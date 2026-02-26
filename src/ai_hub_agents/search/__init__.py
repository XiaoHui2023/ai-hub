"""SearchAgent — 搜索互联网信息，抓取内容并提炼总结。

流程：search_urls → fetch_content → summarize
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, MessagesState

from ai_hub_agents.core import BaseAgent
from ai_hub_agents.core.llm import resolve_lite_llm

from .nodes import make_fetch_content, make_search_urls, make_summarize
from .providers import resolve_provider

logger = logging.getLogger(__name__)


class SearchAgent(BaseAgent):
    """搜索互联网信息，获取实时内容并提炼总结。"""

    class State(MessagesState):
        search_query: str
        search_results: list[dict]
        search_fetched: list[dict]
        search_summary: str

    name = "search"
    description = "搜索互联网信息，获取实时内容并提炼总结。"

    @classmethod
    def get_tools(cls, **kwargs: Any) -> list[BaseTool]:
        return []

    @classmethod
    def create(
        cls,
        llm: BaseChatModel,
        *,
        provider_name: str | None = None,
        max_results: int = 5,
        **kwargs: Any,
    ) -> SearchAgent:
        provider = resolve_provider(provider_name)
        lite = resolve_lite_llm(llm)

        cls.nodes({
            "search_urls": make_search_urls(provider, max_results=max_results),
            "fetch_content": make_fetch_content(),
            "summarize": make_summarize(lite),
        })
        cls.flow(START, "search_urls", "fetch_content", "summarize", END)

        return cls.compile()
