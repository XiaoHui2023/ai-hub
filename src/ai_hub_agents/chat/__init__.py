"""ChatAgent — 纯对话引擎，支持短期/长期记忆。

主流程：intent_router → [RECALL] recall → reply → END
                       → [DIRECT]        reply → END

后台任务通过触发器在 run 完成后自动提交。
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
    LongTermMemory,
    ShortTermMemory,
    create_checkpointer,
    create_store,
)

from .backgrounds import create_compress_worker, create_extract_worker
from .nodes import make_intent_router, make_recall, make_reply, route_after_intent

logger = logging.getLogger(__name__)


class ChatAgent(BaseAgent):
    """纯对话聊天助手，支持短期/长期记忆。"""

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
        platform_mode = kwargs.pop("platform_mode", False)
        prompt = cls.get_prompt()
        lite = resolve_lite_llm(llm)

        try:
            checkpointer = create_checkpointer()
        except Exception:
            logger.debug("未配置 checkpointer，跳过")
            checkpointer = None

        store = create_store()
        stm = ShortTermMemory("messages", threshold=20, keep=8)
        ltm = LongTermMemory("user_prefs", store=store) if store else None

        cls.nodes({
            "intent_router": make_intent_router(lite),
            "recall": make_recall(ltm),
            "reply": make_reply(llm, prompt),
        })
        cls.flow(START, "intent_router")
        cls.route("intent_router", route_after_intent)
        cls.flow("recall", "reply", END)

        if platform_mode:
            agent = cls.compile()
        else:
            agent = cls.compile(checkpointer=checkpointer, store=store)

        # ── 后台 + 触发器 ──
        bg_callbacks = kwargs.get("callbacks")
        compress = create_compress_worker(stm, lite, checkpointer, callbacks=bg_callbacks)

        # 为后台 extract worker 创建独立的 store 连接，
        # 避免与主线程共享同一个 psycopg.Connection（非线程安全）
        bg_store = create_store() if store else None
        bg_ltm = LongTermMemory("user_prefs", store=bg_store) if bg_store else None
        extract = create_extract_worker(bg_ltm, lite, callbacks=bg_callbacks)

        if compress:
            agent.trigger(
                "run_complete",
                action=lambda e: compress.emit(e.ctx),
                condition=lambda e: stm.overflow(e.ctx.state),
                name="compress",
            )
        if extract:
            agent.trigger(
                "run_complete",
                action=lambda e: extract.emit(e.ctx),
                name="extract",
            )

        return agent
