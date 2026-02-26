"""Bocha Web Search Provider — 博查搜索 API。"""

from __future__ import annotations

import logging
import os

import requests

from . import register
from .base import SearchProvider, SearchResult

logger = logging.getLogger(__name__)

BOCHA_API_URL = "https://api.bochaai.com/v1/web-search"


@register
class BochaSearchProvider(SearchProvider):
    name = "bocha"

    def __init__(self) -> None:
        self._api_key = os.environ["BOCHA_API_KEY"]

    def search(self, query: str, max_results: int) -> list[SearchResult]:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "query": query,
            "count": max_results,
            "summary": True,
        }
        resp = requests.post(BOCHA_API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        logger.debug("Bocha 原始响应: %s", data)

        if isinstance(data.get("code"), int) and data["code"] != 200:
            logger.warning("Bocha API 错误 (code=%s): %s", data.get("code"), data.get("msg") or data.get("message", ""))
            return []

        results: list[SearchResult] = []
        web_pages = data.get("data", {}).get("webPages", data.get("webPages", {}))
        for item in web_pages.get("value", []):
            results.append(
                SearchResult(
                    url=item["url"],
                    title=item.get("name", ""),
                    published_date=item.get("datePublished"),
                )
            )
        return results

    @classmethod
    def is_available(cls) -> bool:
        return bool(os.environ.get("BOCHA_API_KEY"))
