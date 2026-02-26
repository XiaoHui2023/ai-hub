"""Stream 生命周期回调。

提供 StreamCallback 基类，BaseAgent 在 stream 过程中调用其三个入口方法：
  - on_stream_start()
  - on_event(mode, event)
  - on_stream_end(result)

on_event 的默认实现会把 LangGraph 原始事件路由到细粒度钩子，
子类只需覆盖感兴趣的钩子即可。
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, ToolMessage


class StreamCallback:
    """Stream 生命周期回调基类。

    BaseAgent 仅调用 on_stream_start / on_event / on_stream_end，
    不关心细粒度钩子的存在。事件分发逻辑完全封装在本类中。
    """

    # ── BaseAgent 直接调用的入口 ───────────────────

    def on_stream_start(self) -> None:
        """stream 开始前调用。"""

    def on_stream_end(self, result: str) -> None:
        """stream 结束后调用。result 为最终清洗后的文本。"""

    def on_event(self, mode: str, event: Any, *, ns: tuple[str, ...] = ()) -> None:
        """处理原始 stream 事件，默认分发到细粒度钩子。

        - messages 模式：处理 ToolMessage（每个工具完成时立即触发）
        - updates 模式：处理 AIMessage（tool_calls 和文本回复）

        Args:
            ns: 子图命名空间路径，用于给节点名加前缀（如 ``("search",)``）。

        高级用户可覆盖此方法直接处理原始事件。
        """
        if mode == "messages":
            msg, _metadata = event
            if isinstance(msg, ToolMessage):
                if getattr(msg, "status", None) == "error":
                    self.on_tool_error(msg.name, str(msg.content))
                else:
                    self.on_tool_result(msg.name, str(msg.content))
        elif mode == "updates":
            prefix = ".".join(ns) + "." if ns else ""
            for node_name, update in event.items():
                self.on_node(f"{prefix}{node_name}")
                if not update:
                    continue
                for msg in update.get("messages", []):
                    if isinstance(msg, AIMessage):
                        if msg.tool_calls:
                            for tc in msg.tool_calls:
                                self.on_tool_call(tc["name"], tc["args"])
                        elif msg.content:
                            self.on_ai_message(msg)

    # ── 排队钩子 ──────────────────────────────────

    def on_queue_wait(self, thread_id: str) -> None:
        """进入排队等待时触发（同一 thread_id 有请求正在执行）。"""

    def on_queue_resume(self, thread_id: str) -> None:
        """获得锁、即将开始执行时触发。"""

    # ── 细粒度钩子（子类按需覆盖） ────────────────

    def on_node(self, name: str) -> None:
        """节点完成时触发。"""

    def on_ai_message(self, message: AIMessage) -> None:
        """AI 产生了文本回复。"""

    def on_tool_call(self, name: str, args: dict[str, Any]) -> None:
        """AI 请求调用工具。"""

    def on_tool_result(self, name: str, content: str) -> None:
        """工具返回了结果。"""

    def on_tool_error(self, name: str, content: str) -> None:
        """工具执行失败。"""

    # ── 后台任务钩子 ──────────────────────────────

    def on_background_submit(self, worker_name: str) -> None:
        """后台 worker 收到任务提交。"""

    def on_background_done(self, worker_name: str, item_count: int) -> None:
        """后台 worker 完成一批任务处理。"""

    def on_background_error(self, worker_name: str, error: str, item_count: int) -> None:
        """后台 worker 处理失败。"""
