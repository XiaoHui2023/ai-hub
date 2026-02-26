"""save_context 节点 — 持久化当前上下文并触发后台任务。

在 reply 之后执行。职责：
1. 将当前 messages + summary 写入 ChatContextStore
2. 检测溢出 → 提交异步压缩
3. 提交异步长期记忆提取
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig

from ai_hub_agents.core.event import RunContext
from ai_hub_agents.core.memory import ChatContextStore, ShortTermMemory

logger = logging.getLogger(__name__)


def make_save_context(
    store: ChatContextStore,
    stm: ShortTermMemory,
    compress_worker: Any | None = None,
    extract_worker: Any | None = None,
):
    """返回 save_context 节点函数。"""

    def save_context(state: dict[str, Any], config: RunnableConfig) -> dict[str, Any]:
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return {}

        messages = [m for m in state.get("messages", []) if isinstance(m, BaseMessage)]
        summary = state.get("chat_summary", "")

        store.save(thread_id, messages, summary)

        logger.info(
            "[save_context] thread=%s, 已保存 %d 条消息",
            thread_id, len(messages),
        )

        ctx = RunContext(thread_id=thread_id, config=config)
        ctx.state = state

        if compress_worker and stm.overflow(state):
            logger.info("[save_context] 消息溢出，提交异步压缩")
            compress_worker.emit(ctx)

        if extract_worker:
            extract_worker.emit(ctx)

        return {}

    return save_context
