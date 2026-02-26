"""compress 后台 worker — 压缩过长的消息历史（短期记忆）。"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel

from ai_hub_agents.core import FnBackgroundAgent
from ai_hub_agents.core.event import RunContext
from ai_hub_agents.core.llm import _model_tag
from ai_hub_agents.core.memory import ShortTermMemory

logger = logging.getLogger(__name__)

_COMPRESS_PROMPT = """\
将以下对话历史压缩为一段简洁的摘要，保留关键信息和上下文。
如果已有之前的摘要，将新对话内容合并进去。
只输出摘要文本，不要加任何前缀。"""


def create_compress_worker(
    stm: ShortTermMemory,
    lite: BaseChatModel,
    checkpointer: Any,
    callbacks: list | None = None,
) -> FnBackgroundAgent | None:
    if checkpointer is None:
        return None

    def do_compress(items: list[RunContext]) -> None:
        for ctx in items:
            if not stm.overflow(ctx.state):
                continue
            logger.info("[compress] 使用 轻量 模型: %s", _model_tag(lite))
            patch = stm.compress(
                ctx.state,
                llm=lite,
                prompt=_COMPRESS_PROMPT,
                summary_field="chat_summary",
            )
            if patch:
                logger.info("[compress] 压缩完成，thread=%s", ctx.thread_id)

    worker = FnBackgroundAgent(fn=do_compress, name="compress", debounce=0, callbacks=callbacks)
    worker.start()
    return worker
