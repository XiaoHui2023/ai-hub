"""reply 节点 — 基于 prompt 生成最终回答。

从 state 读取 chat_recalled（长期记忆）和 chat_context（外部注入的参考上下文）。
"""

from __future__ import annotations

import logging
import time
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage

from ai_hub_agents.core.llm import _model_tag

logger = logging.getLogger(__name__)


def make_reply(llm: BaseChatModel, prompt: str):
    """返回 reply 节点函数。"""

    def reply(state: dict[str, Any]) -> dict[str, Any]:
        messages = list(state["messages"])
        system = prompt

        recalled = state.get("chat_recalled", "")
        if recalled:
            system += f"\n\n你记得关于这个用户：\n{recalled}"

        context = state.get("chat_context", "")
        if context:
            system += (
                "\n\n[内部参考，用自然段落融入回答，"
                "不要使用编号列表、Markdown 标题、分隔线等格式，"
                "不要提及搜索、查询、参考资料等字眼]：\n"
                + context
            )

        tag = _model_tag(llm)
        logger.info("[reply] 开始调用 主 模型: %s", tag)
        t0 = time.perf_counter()
        response = llm.invoke([SystemMessage(content=system), *messages])
        elapsed = time.perf_counter() - t0
        logger.info("[reply] 主 模型 %s 响应完成，耗时 %.1fs", tag, elapsed)
        return {"messages": [response]}

    return reply
