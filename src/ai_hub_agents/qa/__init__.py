"""QaAgent — 搜索增强问答，委托 ChatAgent 生成回复。

流程：router → [SEARCH] search → pipe → chat → END
             → [CHAT]                  chat → END

QaAgent 是无状态编排层：
  - 无 checkpointer / store（记忆由 ChatAgent 子图管理）
  - SearchAgent 的输出通过 pipe 桥接到 ChatAgent 的 chat_context 字段
  - 不再有冗余的 summarize（SearchAgent 内部已总结）
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, MessagesState

from ai_hub_agents.chat import ChatAgent
from ai_hub_agents.core import BaseAgent
from ai_hub_agents.core.llm import resolve_lite_llm

from .nodes import make_router

logger = logging.getLogger(__name__)


class QaAgent(BaseAgent):
    """搜索增强问答助手，需要搜索时先检索再回答，否则直接对话。"""

    class State(MessagesState):
        qa_needs_search: bool
        qa_search_results: str
        chat_context: str

    name = "qa"
    description = "搜索增强问答助手，支持实时搜索和多轮对话记忆。"

    @classmethod
    def get_tools(cls, **kwargs: Any) -> list[BaseTool]:
        return []

    @classmethod
    def create(
        cls,
        llm: BaseChatModel,
        *,
        provider_name: str | None = None,
        **kwargs: Any,
    ) -> QaAgent:
        chat_agent = ChatAgent.create(llm, **kwargs)
        lite = resolve_lite_llm(llm)
        bridge = cls.pipe("qa_search_results", "chat_context")

        cls.nodes({
            "router": make_router(lite),
            "search": _make_search(llm, provider_name=provider_name),
            "chat": chat_agent._graph,
        })

        cls.flow(START, "router")
        cls.route("router", _route_after_router)
        cls.flow("search", bridge, "chat", END)

        return cls.compile()


# ── 内部辅助 ──────────────────────────────────────


def _route_after_router(state: dict[str, Any]) -> str:
    """条件路由：需要搜索 → search，否则 → chat。"""
    if state.get("qa_needs_search", False):
        return "search"
    return "chat"


def _make_search(
    llm: BaseChatModel,
    *,
    provider_name: str | None = None,
):
    """创建 search 节点，委托 SearchAgent 完成搜索+总结。"""

    def search(state: dict[str, Any]) -> dict[str, Any]:
        try:
            from ai_hub_agents.search import SearchAgent

            agent = SearchAgent.create(llm, provider_name=provider_name)
            last_msg = state["messages"][-1]
            content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
            results = agent.invoke(content)
            return {"qa_search_results": results}
        except Exception:
            logger.warning("搜索失败，跳过", exc_info=True)
            return {"qa_search_results": ""}

    return search
