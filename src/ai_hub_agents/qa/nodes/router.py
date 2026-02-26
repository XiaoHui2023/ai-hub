"""router 节点 — 判断用户消息是否需要搜索。"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from ai_hub_agents.core.llm import _model_tag

logger = logging.getLogger(__name__)

_SYSTEM = """\
判断用户的最新消息是否需要搜索互联网来回答。仅回复一个词：SEARCH 或 CHAT。
- SEARCH：需要搜索实时信息、新闻、事实、数据等。
- CHAT：闲聊、打招呼、主观讨论、情感交流、常识性问题等。"""


def make_router(llm: BaseChatModel):
    """返回 router 节点函数。"""

    def router(state: dict[str, Any]) -> dict[str, Any]:
        last_msg = state["messages"][-1]
        content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        logger.info("[router] 使用 轻量 模型: %s", _model_tag(llm))
        response = llm.invoke([
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=content),
        ])
        needs_search = "SEARCH" in response.content.strip().upper()
        return {"qa_needs_search": needs_search}

    return router
