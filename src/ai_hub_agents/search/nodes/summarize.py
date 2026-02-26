"""summarize 节点 — 使用 LLM 对抓取内容进行精简总结。"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import frontmatter
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from ai_hub_agents.core.llm import _model_tag

logger = logging.getLogger(__name__)


def _load_prompt() -> str:
    """加载 search 模块的 prompt.md。"""
    md_path = Path(__file__).parent.parent / "prompt.md"
    post = frontmatter.load(str(md_path))
    return post.content


def make_summarize(llm: BaseChatModel):
    """返回 summarize 节点函数。"""
    system_prompt = _load_prompt()

    def summarize(state: dict[str, Any]) -> dict[str, Any]:
        fetched: list[dict] = state.get("search_fetched", [])
        query: str = state.get("search_query", "")

        if not fetched:
            return {"search_summary": "", "messages": [AIMessage(content="未能获取到搜索内容。")]}

        parts: list[str] = []
        for item in fetched:
            parts.append(f"### 来源: {item['url']}\n\n{item['markdown']}")
        combined = "\n\n---\n\n".join(parts)

        user_content = f"用户问题：{query}\n\n搜索到的内容：\n\n{combined}"

        logger.info("[summarize] 使用 轻量 模型: %s", _model_tag(llm))
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content),
        ])

        return {
            "search_summary": response.content,
            "messages": [AIMessage(content=response.content)],
        }

    return summarize
