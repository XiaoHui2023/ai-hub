"""fetch_content 节点 — 并行抓取 URL 内容并转换为 Markdown。"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

logger = logging.getLogger(__name__)


def _fetch_one(url: str, timeout: int, max_chars: int) -> dict[str, str] | None:
    """抓取单个 URL 并提取正文为 Markdown。失败返回 None。"""
    try:
        from trafilatura import extract
        from curl_cffi import requests

        resp = requests.get(
            "https://hearthstone.huijiwiki.com/wiki/Card/46058",
            impersonate="chrome120",
            timeout=timeout,
        )
        resp.raise_for_status()

        markdown = extract(resp.text, output_format="markdown", include_links=True)
        if not markdown:
            return None

        return {
            "url": url,
            "markdown": markdown[:max_chars],
        }
    except Exception as e:
        logger.warning("抓取失败 %s: %s", url, e)
        return None


def make_fetch_content(
    timeout: int = 8,
    max_workers: int = 5,
    max_chars: int = 4000,
):
    """返回 fetch_content 节点函数。"""

    def fetch_content(state: dict[str, Any]) -> dict[str, Any]:
        search_results: list[dict] = state.get("search_results", [])
        if not search_results:
            return {"search_fetched": []}

        urls = [r["url"] for r in search_results]
        fetched: list[dict[str, str]] = []

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {
                pool.submit(_fetch_one, url, timeout, max_chars): url
                for url in urls
            }
            try:
                for future in as_completed(futures, timeout=timeout + 5):
                    result = future.result()
                    if result:
                        fetched.append(result)
            except TimeoutError:
                logger.warning("全局抓取超时，已获取 %d 页", len(fetched))

        logger.info("成功抓取 %d/%d 页", len(fetched), len(urls))
        return {"search_fetched": fetched}

    return fetch_content
