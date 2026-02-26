"""intent_router 节点 — 判断是否需要召回长期记忆。"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from ai_hub_agents.core.llm import _model_tag

logger = logging.getLogger(__name__)

_INTENT_SYSTEM = """\
判断用户最新消息是否需要调取长期记忆来回答。仅回复一个词：RECALL 或 DIRECT。
- RECALL：涉及用户个人信息、偏好、历史事实、之前聊过的内容，或用户要求记住/回忆某些信息。
- DIRECT：简单问候、闲聊、客观知识、不需要个性化记忆的问题。"""


def make_intent_router(lite: BaseChatModel):
    def intent_router(state: dict[str, Any]) -> dict[str, Any]:
        last_msg = state["messages"][-1]
        content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        logger.info("[intent_router] 使用 轻量 模型: %s", _model_tag(lite))
        response = lite.invoke([
            SystemMessage(content=_INTENT_SYSTEM),
            HumanMessage(content=content),
        ])
        needs_recall = "RECALL" in response.content.strip().upper()
        return {"chat_needs_recall": needs_recall}

    return intent_router


def route_after_intent(state: dict[str, Any]) -> str:
    if state.get("chat_needs_recall", False):
        return "recall"
    return "reply"
