"""search_urls 节点 — 调用 Provider 搜索，获取 URL 列表。"""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any

from ai_hub_agents.search.providers.base import SearchProvider

logger = logging.getLogger(__name__)


def make_search_urls(provider: SearchProvider, max_results: int):
    """返回 search_urls 节点函数。"""

    def search_urls(state: dict[str, Any]) -> dict[str, Any]:
        last_msg = state["messages"][-1]
        query = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

        logger.info("搜索: %s (provider=%s)", query, provider.name)
        results = provider.search(query, max_results=max_results)
        logger.info("获取到 %d 条搜索结果", len(results))

        return {
            "search_query": query,
            "search_results": [asdict(r) for r in results],
        }

    return search_urls
