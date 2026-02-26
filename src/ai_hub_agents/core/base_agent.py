from __future__ import annotations

import inspect
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Generator

import frontmatter
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph

from .callbacks import StreamCallback
from .langchain_bridge import LangChainBridge
from .event import (
    Event,
    EventBus,
    NodeCompleteEvent,
    RunCompleteEvent,
    RunContext,
    RunErrorEvent,
    RunStartEvent,
)
from .message_processing import clean_response
from .thread_lock import ThreadLockManager
from .trigger import Trigger

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """所有 Agent 的抽象基类，定义标准集成接口。

    子类需实现:
        - name / description: 类属性
        - State: 内部类，继承 MessagesState 定义图状态
        - get_tools(): 返回该 Agent 拥有的工具列表
        - create(): 构建 Agent 实例（使用 DSL: nodes/flow/route/pipe/compile）

    集成方式:
        - as_tool():  包装为 LangChain Tool，供父 Agent 调用
        - as_node():  包装为 LangGraph 节点，用于组合工作流
        - invoke() / stream(): 直接执行

    排队保护:
        子类设置 sequential_threads = True 后，同一 thread_id
        的并发请求会自动排队，防止 checkpoint 竞态条件。
    """

    class State(MessagesState):
        """子类覆盖此内部类定义自己的 state。"""
        pass

    name: str
    description: str
    sequential_threads: bool = False

    _builders: dict[str, StateGraph] = {}

    def __init__(self, graph: CompiledStateGraph) -> None:
        self._graph = graph
        self._bus = EventBus()
        self._thread_locks: ThreadLockManager | None = None
        if self.sequential_threads:
            self._thread_locks = ThreadLockManager()

    # ── 图构建 DSL ────────────────────────────────────

    @classmethod
    def _get_builder(cls) -> StateGraph:
        key = cls.__qualname__
        if key not in BaseAgent._builders:
            BaseAgent._builders[key] = StateGraph(cls.State)
        return BaseAgent._builders[key]

    @classmethod
    def nodes(cls, mapping: dict[str, Any]) -> None:
        """批量注册节点。首次调用自动创建 builder。"""
        builder = cls._get_builder()
        for name, fn in mapping.items():
            builder.add_node(name, fn)

    @classmethod
    def node(cls, name: str, fn: Any) -> None:
        """注册单个节点。"""
        cls._get_builder().add_node(name, fn)

    @classmethod
    def flow(cls, *path: str) -> None:
        """链式连边。START/END 由调用方显式传入。

        flow(START, "a", "b", END) => edge(START,a) + edge(a,b) + edge(b,END)
        """
        builder = cls._get_builder()
        for a, b in zip(path, path[1:]):
            builder.add_edge(a, b)

    @classmethod
    def route(cls, from_node: str, fn: Callable) -> None:
        """条件分支。"""
        cls._get_builder().add_conditional_edges(from_node, fn)

    @classmethod
    def pipe(cls, src: str, dst: str) -> str:
        """字段映射桥节点。返回自动生成的节点名，可直接用于 flow()。"""
        src_prefix = src.split("_", 1)[0]
        dst_prefix = dst.split("_", 1)[0]
        bridge_name = f"{src_prefix}>{dst_prefix}"

        def _bridge(state: dict) -> dict:
            value = state.get(src, "")
            preview = repr(value[:60]) if isinstance(value, str) else type(value).__name__
            logger.info("[%s] %s → %s (%s)", bridge_name, src, dst, preview)
            return {dst: value}

        cls.node(bridge_name, _bridge)
        return bridge_name

    @classmethod
    def compile(cls, **kwargs: Any) -> BaseAgent:
        """编译图并返回 agent 实例，重置 builder。"""
        key = cls.__qualname__
        builder = BaseAgent._builders.pop(key, None)
        if builder is None:
            raise RuntimeError(f"{cls.__name__}: 没有待编译的图，请先调用 nodes()/node()")
        graph = builder.compile(**kwargs)
        return cls(graph)

    # ── 子类必须实现 ─────────────────────────────────

    @classmethod
    @abstractmethod
    def get_tools(cls, **kwargs: Any) -> list[BaseTool]:
        """返回该 Agent 的工具列表。"""
        ...

    @classmethod
    @abstractmethod
    def create(cls, llm: BaseChatModel, **kwargs: Any) -> BaseAgent:
        """构建 Agent 实例。"""
        ...

    # ── 公共能力 ──────────────────────────────────────

    @classmethod
    def get_prompt(cls) -> str:
        """读取子类所在目录下的 prompt.md（frontmatter 格式）。"""
        md_path = Path(inspect.getfile(cls)).parent / "prompt.md"
        if not md_path.exists():
            raise FileNotFoundError(
                f"{cls.__name__} 的 prompt.md 未找到: {md_path}"
            )
        post = frontmatter.load(str(md_path))
        return post.content

    # ── 事件 / 触发器 ────────────────────────────────

    def trigger(
        self,
        event: str,
        action: Callable[[Event], None],
        condition: Callable[[Event], bool] | None = None,
        name: str = "",
    ) -> None:
        """注册触发器到事件总线。"""
        t = Trigger(event=event, action=action, condition=condition, name=name)
        t.register(self._bus)

    def _get_state(self, thread_id: str | None) -> dict:
        """获取当前 graph 的完整 state。"""
        config = self._build_config(thread_id)
        if config is None:
            return {}
        try:
            snapshot = self._graph.get_state(config)
            return snapshot.values if snapshot else {}
        except Exception:
            return {}

    # ── 集成接口 ──────────────────────────────────────

    @classmethod
    def as_tool(cls, llm: BaseChatModel, **kwargs: Any) -> BaseTool:
        """包装为 LangChain Tool，供父 Agent 调用。"""
        agent = cls.create(llm, **kwargs)

        def _invoke(task: str) -> str:
            return agent.invoke(task)

        return StructuredTool.from_function(
            func=_invoke,
            name=cls.name,
            description=cls.description,
        )

    @classmethod
    def as_node(cls, llm: BaseChatModel, **kwargs: Any) -> Callable:
        """返回可用于 StateGraph.add_node() 的节点函数。"""
        agent = cls.create(llm, **kwargs)

        def _node(state: dict[str, Any]) -> dict[str, Any]:
            return agent._graph.invoke(state)

        return _node

    # ── 直接执行 ──────────────────────────────────────

    def invoke(
        self,
        message: str,
        *,
        thread_id: str | None = None,
        callbacks: list[StreamCallback] | None = None,
        **state_fields: Any,
    ) -> str:
        """执行 Agent，基于 stream 驱动，支持回调。

        Args:
            message: 用户消息
            thread_id: 会话 ID，配合 checkpointer 实现多轮对话
            callbacks: 可选的 StreamCallback 列表，用于监听生命周期事件
            **state_fields: 额外的 state 字段（如 input_file, output_file）
        """
        if self._thread_locks and thread_id:
            return self._invoke_sequential(
                message, thread_id=thread_id, callbacks=callbacks, **state_fields
            )
        return self._invoke_inner(
            message, thread_id=thread_id, callbacks=callbacks, **state_fields
        )

    def _invoke_sequential(
        self,
        message: str,
        *,
        thread_id: str,
        callbacks: list[StreamCallback] | None = None,
        **state_fields: Any,
    ) -> str:
        """排队路径：同一 thread_id 串行执行。"""
        assert self._thread_locks is not None
        cbs = callbacks or []

        locked = self._thread_locks._locks.get(thread_id)
        if locked is not None and locked.locked():
            for cb in cbs:
                cb.on_queue_wait(thread_id)

        with self._thread_locks.acquire(thread_id):
            for cb in cbs:
                cb.on_queue_resume(thread_id)
            return self._invoke_inner(
                message, thread_id=thread_id, callbacks=callbacks, **state_fields
            )

    def _invoke_inner(
        self,
        message: str,
        *,
        thread_id: str | None = None,
        callbacks: list[StreamCallback] | None = None,
        **state_fields: Any,
    ) -> str:
        """实际执行逻辑。"""
        logger.debug("Agent '%s' invoke, message: %.100s", self.name, message)
        input_state: dict[str, Any] = {"messages": [("human", message)]}
        input_state.update(state_fields)
        cbs = callbacks or []
        config = self._build_config(thread_id) or {}
        config.setdefault("callbacks", []).append(LangChainBridge(cbs))

        run_ctx = RunContext(thread_id=thread_id, config=config)
        self._bus.emit(RunStartEvent(ctx=run_ctx))

        for cb in cbs:
            cb.on_stream_start()

        last_content = ""
        for ns, mode, event in self._graph.stream(
            input_state,
            config=config,
            stream_mode=["updates", "messages"],
            subgraphs=True,
        ):
            for cb in cbs:
                cb.on_event(mode, event, ns=ns)

            if mode == "updates":
                prefix = ".".join(ns) + "." if ns else ""
                for node_name, update in event.items():
                    self._bus.emit(NodeCompleteEvent(
                        ctx=run_ctx, node=f"{prefix}{node_name}", update=update or {},
                    ))
                    if not update:
                        continue
                    for msg in update.get("messages", []):
                        if isinstance(msg, AIMessage) and msg.content:
                            last_content = msg.content

        if not last_content:
            raise RuntimeError(f"Agent '{self.name}' 返回了空的 messages")

        result = clean_response(last_content)

        for cb in cbs:
            cb.on_stream_end(result)

        run_ctx.state = self._get_state(thread_id)
        self._bus.emit(RunCompleteEvent(ctx=run_ctx))

        return result

    def stream(
        self,
        message: str,
        *,
        thread_id: str | None = None,
        **state_fields: Any,
    ) -> Generator[tuple[str, Any], None, None]:
        if self._thread_locks and thread_id:
            yield from self._stream_sequential(
                message, thread_id=thread_id, **state_fields
            )
        else:
            yield from self._stream_inner(
                message, thread_id=thread_id, **state_fields
            )

    def _stream_sequential(
        self,
        message: str,
        *,
        thread_id: str,
        **state_fields: Any,
    ) -> Generator[tuple[str, Any], None, None]:
        assert self._thread_locks is not None
        with self._thread_locks.acquire(thread_id):
            yield from self._stream_inner(
                message, thread_id=thread_id, **state_fields
            )

    def _stream_inner(
        self,
        message: str,
        *,
        thread_id: str | None = None,
        **state_fields: Any,
    ) -> Generator[tuple[str, Any], None, None]:
        logger.debug("Agent '%s' stream, message: %.100s", self.name, message)
        input_state: dict[str, Any] = {"messages": [("human", message)]}
        input_state.update(state_fields)
        config = self._build_config(thread_id) or {}

        run_ctx = RunContext(thread_id=thread_id, config=config)
        self._bus.emit(RunStartEvent(ctx=run_ctx))

        for ns, mode, event in self._graph.stream(
            input_state,
            config=config,
            stream_mode=["updates", "messages"],
            subgraphs=True,
        ):
            yield mode, event

            if mode == "updates":
                prefix = ".".join(ns) + "." if ns else ""
                for node_name, update in event.items():
                    self._bus.emit(NodeCompleteEvent(
                        ctx=run_ctx, node=f"{prefix}{node_name}", update=update or {},
                    ))

        run_ctx.state = self._get_state(thread_id)
        self._bus.emit(RunCompleteEvent(ctx=run_ctx))

    # ── 内部工具 ──────────────────────────────────────

    @staticmethod
    def _build_config(thread_id: str | None) -> dict[str, Any] | None:
        if thread_id is None:
            return None
        return {"configurable": {"thread_id": thread_id}}
