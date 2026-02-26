"""compress 后台 worker — 异步压缩过长的消息历史（短期记忆）。

从 ChatContextStore 加载最新数据，压缩老消息为摘要，
通过 CAS（save_if_version）写回，防止覆盖并发写入的新数据。
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from ai_hub_agents.core import FnBackgroundAgent
from ai_hub_agents.core.event import RunContext
from ai_hub_agents.core.llm import _model_tag
from ai_hub_agents.core.memory import ChatContextStore, ShortTermMemory

logger = logging.getLogger(__name__)

_COMPRESS_PROMPT = """\
将以下对话历史压缩为一段简洁的摘要，保留关键信息和上下文。
如果已有之前的摘要，将新对话内容合并进去。
只输出摘要文本，不要加任何前缀。"""


def create_compress_worker(
    stm: ShortTermMemory,
    lite: BaseChatModel,
    context_store: ChatContextStore,
    callbacks: list | None = None,
) -> FnBackgroundAgent | None:
    if context_store is None:
        return None

    def do_compress(items: list[RunContext]) -> None:
        seen: set[str | None] = set()
        for ctx in items:
            if ctx.thread_id in seen:
                continue
            seen.add(ctx.thread_id)

            if not ctx.thread_id:
                continue

            stored, version = context_store.load(ctx.thread_id)
            if not stored:
                continue

            messages = stored["messages"]
            if len(messages) <= stm.threshold:
                continue

            to_compress = messages[: -stm.keep]
            to_keep = messages[-stm.keep :]

            text = "\n".join(
                f"{m.type}: {m.content}"
                for m in to_compress
                if hasattr(m, "content")
            )

            existing_summary = stored.get("summary", "")
            if existing_summary:
                text = f"已有摘要：{existing_summary}\n\n新内容：\n{text}"

            logger.info("[compress] 使用 轻量 模型: %s", _model_tag(lite))
            response = lite.invoke([
                SystemMessage(content=_COMPRESS_PROMPT),
                HumanMessage(content=text),
            ])

            new_summary = response.content
            summary_msg = SystemMessage(content=f"[对话摘要] {new_summary}")
            new_messages = [summary_msg, *to_keep]

            if context_store.save_if_version(
                ctx.thread_id, new_messages, new_summary, version
            ):
                logger.info(
                    "[compress] 压缩完成 thread=%s, %d → %d 条",
                    ctx.thread_id, len(messages), len(new_messages),
                )

    worker = FnBackgroundAgent(
        fn=do_compress, name="compress", debounce=0, callbacks=callbacks,
    )
    worker.start()
    return worker
