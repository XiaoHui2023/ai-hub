"""ChatAgent — 纯对话引擎，支持短期/长期记忆。

主流程：load_context → intent_router → [RECALL] recall → reply → save_context → END
                                       → [DIRECT]        reply → save_context → END

记忆完全自管理：
  - load_context / save_context 节点读写 ChatContextStore（独立于 LangGraph checkpointer）
  - 异步压缩由 save_context 检测溢出后提交后台 worker
  - 无论作为独立 agent 还是子图，记忆行为一致，上层无需关心
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, MessagesState

from ai_hub_agents.core import BaseAgent
from ai_hub_agents.core.llm import resolve_lite_llm
from ai_hub_agents.core.memory import (
    ChatContextStore,
    LongTermMemory,
    ShortTermMemory,
    create_store,
)

from .backgrounds import create_compress_worker, create_extract_worker
from .nodes import (
    make_intent_router,
    make_load_context,
    make_recall,
    make_reply,
    make_save_context,
    route_after_intent,
)

logger = logging.getLogger(__name__)


class ChatAgent(BaseAgent):
    """纯对话聊天助手，支持自管理的短期/长期记忆。"""

    class State(MessagesState):
        chat_recalled: str
        chat_context: str
        chat_summary: str
        chat_needs_recall: bool

    name = "chat"
    description = "自然对话聊天助手，支持记忆管理。"
    sequential_threads = True

    @classmethod
    def get_tools(cls, **kwargs: Any) -> list[BaseTool]:
        return []

    @classmethod
    def create(cls, llm: BaseChatModel, **kwargs: Any) -> ChatAgent:
        prompt = cls.get_prompt()
        lite = resolve_lite_llm(llm)

        context_store = ChatContextStore()
        store = create_store()
        stm = ShortTermMemory("messages", threshold=20, keep=8)
        ltm = LongTermMemory("user_prefs", store=store) if store else None

        # ── 后台 workers ──
        bg_callbacks = kwargs.get("callbacks")
        compress = create_compress_worker(stm, lite, context_store, callbacks=bg_callbacks)

        bg_store = create_store() if store else None
        bg_ltm = LongTermMemory("user_prefs", store=bg_store) if bg_store else None
        extract = create_extract_worker(bg_ltm, lite, callbacks=bg_callbacks)

        # ── 图构建 ──
        cls.nodes({
            "load_context": make_load_context(context_store),
            "intent_router": make_intent_router(lite),
            "recall": make_recall(ltm),
            "reply": make_reply(llm, prompt),
            "save_context": make_save_context(context_store, stm, compress, extract),
        })

        cls.flow(START, "load_context", "intent_router")
        cls.route("intent_router", route_after_intent)
        cls.flow("recall", "reply")
        cls.flow("reply", "save_context", END)

        return cls.compile()
