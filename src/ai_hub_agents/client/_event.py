"""SSE 事件数据类。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentEvent:
    """单个 SSE 事件的结构化表示。

    Attributes:
        type: 事件类型，如 ``stream_start``、``ai_message``、``error`` 等。
        data: 去掉 ``type`` 后的原始 JSON 负载。
    """

    type: str
    data: dict[str, Any] = field(default_factory=dict)

    # ── 快捷访问 ──────────────────────────────────────

    @property
    def content(self) -> str:
        """文本内容（兼容 ai_message / stream_end / error）。"""
        return (
            self.data.get("content", "")
            or self.data.get("result", "")
            or self.data.get("message", "")
        )

    @property
    def name(self) -> str:
        """工具名称（tool_call / tool_result / tool_error）。"""
        return self.data.get("name", "")

    @property
    def args(self) -> dict[str, Any]:
        """工具调用参数（tool_call）。"""
        return self.data.get("args", {})

    @property
    def success(self) -> bool:
        """工具是否成功（tool_result / tool_error）。"""
        return self.data.get("success", True)

    @property
    def is_error(self) -> bool:
        return self.type == "error"

    @property
    def is_end(self) -> bool:
        return self.type == "stream_end"

    @property
    def is_queued(self) -> bool:
        return self.type == "queue_wait"
