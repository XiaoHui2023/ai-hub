from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Generator

import frontmatter
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.graph.state import CompiledStateGraph


class BaseAgent(ABC):
    """所有 Agent 的抽象基类，定义标准集成接口。

    子类需实现:
        - name / description: 类属性
        - get_tools(): 返回该 Agent 拥有的工具列表
        - create(): 构建 Agent 实例

    集成方式:
        - as_tool():  包装为 LangChain Tool，供父 Agent 调用
        - as_node():  包装为 LangGraph 节点，用于组合工作流
        - invoke() / stream(): 直接执行
    """

    name: str
    description: str

    def __init__(self, graph: CompiledStateGraph) -> None:
        self._graph = graph

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

    def invoke(self, message: str) -> str:
        result = self._graph.invoke({"messages": [("human", message)]})
        return result["messages"][-1].content

    def stream(
        self, message: str
    ) -> Generator[tuple[str, Any], None, None]:
        for mode, event in self._graph.stream(
            {"messages": [("human", message)]},
            stream_mode=["updates", "messages"],
        ):
            yield mode, event
