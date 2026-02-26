"""recall 节点 — 从长期记忆中召回相关信息。"""

import logging
from typing import Any

from langchain_core.runnables import RunnableConfig

from ai_hub_agents.core.memory import LongTermMemory

logger = logging.getLogger(__name__)


def make_recall(ltm: LongTermMemory | None):
    def recall(state: dict[str, Any], *, config: RunnableConfig | None = None) -> dict[str, Any]:
        if ltm is None:
            return {"chat_recalled": ""}

        messages = state.get("messages", [])
        if not messages:
            return {"chat_recalled": ""}

        last_msg = messages[-1]
        query = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

        thread_id = "default"
        if config and "configurable" in config:
            thread_id = config["configurable"].get("thread_id", "default")

        contents = ltm.search(query, thread_id=thread_id)
        recalled = "\n".join(contents) if contents else ""
        return {"chat_recalled": recalled}

    return recall
