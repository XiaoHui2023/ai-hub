"""LangChain 原生回调 → StreamCallback 桥接。

通过实现 ``BaseCallbackHandler``，将 LangChain 的
``on_chat_model_start`` / ``on_llm_end`` 事件
转发到 :class:`StreamCallback` 的 ``on_llm_start`` / ``on_llm_end`` 钩子，
使两套回调系统无缝衔接。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult

if TYPE_CHECKING:
    from uuid import UUID

    from .callbacks import StreamCallback


class LangChainBridge(BaseCallbackHandler):
    """把 LangChain 原生回调桥接到 StreamCallback 体系。"""

    def __init__(self, stream_callbacks: list[StreamCallback]) -> None:
        self._cbs = stream_callbacks

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        flat = messages[0] if messages else []
        for cb in self._cbs:
            cb.on_llm_start(flat)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        ai_msg = (
            response.generations[0][0].message
            if response.generations and response.generations[0]
            else None
        )
        if ai_msg is None:
            return
        for cb in self._cbs:
            cb.on_llm_end(ai_msg)
