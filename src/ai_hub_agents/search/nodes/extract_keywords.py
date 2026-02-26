"""extract_keywords 节点 — 将用户输入提炼成搜索关键词。"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from ai_hub_agents.core.llm import _model_tag

logger = logging.getLogger(__name__)

KEYWORDS_PROMPT = """你将用户的问题或描述提炼为适合搜索引擎使用的关键词。

要求：
- 根据用户输入提取核心关键词，用空格分隔
- 只输出关键词，不要解释
"""


def make_extract_keywords(llm: BaseChatModel):
    """返回 extract_keywords 节点函数。"""

    def extract_keywords(state: dict[str, Any]) -> dict[str, Any]:
        last_msg = state["messages"][-1]
        user_input = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

        logger.info("[extract_keywords] 使用轻量模型: %s", _model_tag(llm))
        response = llm.invoke([
            SystemMessage(content=KEYWORDS_PROMPT),
            HumanMessage(content=user_input),
        ])
        keywords = response.content.strip()

        logger.info("用户输入: %s -> 搜索关键词: %s", user_input[:50], keywords)
        return {"search_query": keywords, "original_query": user_input}

    return extract_keywords
