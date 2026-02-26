"""extract 后台 worker — 提取用户偏好/事实写入长期记忆。"""

from __future__ import annotations

import json
import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from ai_hub_agents.core import FnBackgroundAgent
from ai_hub_agents.core.event import RunContext
from ai_hub_agents.core.llm import _model_tag
from ai_hub_agents.core.memory import LongTermMemory

logger = logging.getLogger(__name__)

_EXTRACT_SYSTEM = """\
从以下对话中提取值得长期记住的信息，包括但不限于：
- 用户的偏好、习惯、个人事实（如姓名、职业、所在地等）
- 用户明确要求记住的任何信息（如"帮我记住……"、"记一下……"）
- 用户提到的与自身相关的重要事实或关系

每条信息用一行表示，以 JSON 数组格式输出，每个元素是一个字符串。
如果没有值得记录的信息，输出空数组 []。
只输出 JSON，不要其他文字。"""


def create_extract_worker(
    ltm: LongTermMemory | None,
    lite: BaseChatModel,
    callbacks: list | None = None,
) -> FnBackgroundAgent | None:
    if ltm is None:
        return None

    def do_extract(items: list[RunContext]) -> None:
        for ctx in items:
            messages = ctx.state.get("messages", [])
            recent = messages[-6:] if len(messages) > 6 else messages
            if not recent:
                continue

            conversation = "\n".join(
                f"{m.type}: {m.content}"
                for m in recent
                if hasattr(m, "content")
            )

            logger.info("[extract] 使用 轻量 模型: %s", _model_tag(lite))
            response = lite.invoke([
                SystemMessage(content=_EXTRACT_SYSTEM),
                HumanMessage(content=conversation),
            ])

            try:
                facts = json.loads(response.content.strip())
            except (json.JSONDecodeError, TypeError):
                continue

            if not isinstance(facts, list) or not facts:
                continue

            for fact in facts:
                if isinstance(fact, str) and fact.strip():
                    ltm.put(fact.strip(), thread_id=ctx.thread_id)

    worker = FnBackgroundAgent(fn=do_extract, name="extract", debounce=0, callbacks=callbacks)
    worker.start()
    return worker
