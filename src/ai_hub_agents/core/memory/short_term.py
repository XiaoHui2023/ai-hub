"""ShortTermMemory — 操作 state 中有界列表字段的短期记忆管理器。

通过 checkpointer 自动持久化，无需额外存储层。
压缩时调用 LLM 将老条目摘要化，保留最近 keep 条。
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    RemoveMessage,
    SystemMessage,
)

logger = logging.getLogger(__name__)


class ShortTermMemory:
    """有界列表字段的短期记忆管理器。

    Args:
        field: 目标 state 字段名（默认 "messages"）。
        threshold: 条目数超过此值时触发压缩。
        keep: 压缩后保留最近多少条原始条目。
    """

    def __init__(
        self,
        field: str = "messages",
        *,
        threshold: int = 20,
        keep: int = 8,
    ) -> None:
        self.field = field
        self.threshold = threshold
        self.keep = keep

    def items(self, state: dict[str, Any]) -> list:
        return state.get(self.field, [])

    def count(self, state: dict[str, Any]) -> int:
        return len(self.items(state))

    def overflow(self, state: dict[str, Any]) -> bool:
        return self.count(state) > self.threshold

    def compress(
        self,
        state: dict[str, Any],
        *,
        llm: BaseChatModel,
        prompt: str,
        summary_field: str,
        format_fn: Callable[[list], str] | None = None,
    ) -> dict[str, Any]:
        """LLM 压缩老条目为摘要，保留最近 keep 条。返回 state patch。

        Args:
            state: 当前图状态。
            llm: 用于压缩的 LLM（建议用轻量模型）。
            prompt: 压缩任务的 system prompt。
            summary_field: 摘要写入的 state 字段名。
            format_fn: 自定义格式化函数，将待压缩条目列表转为字符串。
                       默认适用于 BaseMessage 列表。
        """
        items = self.items(state)
        if len(items) <= self.threshold:
            return {}

        to_compress = items[: -self.keep]
        to_keep = items[-self.keep :]

        if format_fn:
            text = format_fn(to_compress)
        else:
            text = "\n".join(
                f"{m.type}: {m.content}"
                for m in to_compress
                if isinstance(m, BaseMessage) and hasattr(m, "content")
            )

        existing = state.get(summary_field, "")
        if existing:
            text = f"已有摘要：{existing}\n\n新内容：\n{text}"

        response = llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=text),
        ])

        logger.info(
            "[ShortTermMemory] 压缩 %d → %d 条（摘要 %d 字符）",
            len(items),
            self.keep,
            len(response.content),
        )

        if self.field == "messages":
            delete_ops = [
                RemoveMessage(id=m.id)
                for m in to_compress
                if isinstance(m, BaseMessage) and hasattr(m, "id")
            ]
            summary_msg = SystemMessage(
                content=f"[对话摘要] {response.content}"
            )
            return {
                self.field: delete_ops + [summary_msg] + list(to_keep),
                summary_field: response.content,
            }

        return {
            self.field: list(to_keep),
            summary_field: response.content,
        }

    def remove(
        self,
        state: dict[str, Any],
        *,
        indices: list[int] | None = None,
        predicate: Callable[[Any], bool] | None = None,
    ) -> dict[str, Any]:
        """按索引或条件删除条目。返回 state patch。"""
        items = list(self.items(state))
        if indices is not None:
            to_remove = set(indices)
            remaining = [v for i, v in enumerate(items) if i not in to_remove]
        elif predicate is not None:
            remaining = [v for v in items if not predicate(v)]
        else:
            return {}

        removed = len(items) - len(remaining)
        if removed:
            logger.info("[ShortTermMemory] 删除 %d 条", removed)
        return {self.field: remaining}

    def append(self, item: Any) -> dict[str, Any]:
        """追加条目。返回 state patch（利用 LangGraph Annotated reducer）。"""
        return {self.field: [item]}
