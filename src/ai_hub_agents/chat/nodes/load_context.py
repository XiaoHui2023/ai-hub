"""load_context 节点 — 从 ChatContextStore 加载历史上下文。

在 reply 之前执行，将存储的历史消息和摘要注入当前 state，
确保 LLM 能看到完整的对话历史。
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import RemoveMessage
from langchain_core.runnables import RunnableConfig

from ai_hub_agents.core.memory import ChatContextStore

logger = logging.getLogger(__name__)


def make_load_context(store: ChatContextStore):
    """返回 load_context 节点函数。"""

    def load_context(state: dict[str, Any], config: RunnableConfig) -> dict[str, Any]:
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return {}

        stored, _ = store.load(thread_id)
        if not stored or not stored.get("messages"):
            return {}

        current_msg = state["messages"][-1]
        historical = stored["messages"]

        logger.info(
            "[load_context] thread=%s, 加载 %d 条历史消息",
            thread_id, len(historical),
        )

        return {
            "messages": [
                RemoveMessage(id=current_msg.id),
                *historical,
                current_msg,
            ],
            "chat_summary": stored.get("summary", ""),
        }

    return load_context
