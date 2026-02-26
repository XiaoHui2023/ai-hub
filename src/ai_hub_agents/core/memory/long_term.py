"""LongTermMemory — 带衰减模型的语义记忆仓库。

操作 LangGraph Store 中的语义仓库。每条记忆带有强度/时间戳元数据，
支持自然衰减和检索强化。

衰减公式：有效强度 = strength × e^(-decay_rate × hours_since_last_access)

默认 decay_rate=0.005 时的衰减曲线：
  1 小时 → 0.995 | 1 天 → 0.887 | 1 周 → 0.434 | 1 月 → 0.027
"""

from __future__ import annotations

import json
import logging
import math
import time
import uuid
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

_CONSOLIDATE_SYSTEM = """\
以下是关于同一用户的多条记忆。请整合为更精炼的记忆列表：
- 合并高度相似的条目
- 解决矛盾（保留最新/更具体的信息）
- 删除已过时或无意义的条目

输出 JSON 数组，每个元素是一个字符串。只输出 JSON，不要其他文字。"""


class LongTermMemory:
    """带自然衰减的语义记忆仓库。

    Args:
        namespace: store 中的命名空间前缀。
        store: LangGraph Store 实例。
        decay_rate: 衰减速率（每小时），默认 0.005。
        reinforce_delta: 检索命中时强度回升量，默认 0.2。
        strength_threshold: 有效强度低于此值的记忆可被 prune 清理。
        similarity_threshold: put() 时去重的相似度阈值。
    """

    def __init__(
        self,
        namespace: str,
        store: Any,
        *,
        decay_rate: float = 0.005,
        reinforce_delta: float = 0.2,
        strength_threshold: float = 0.05,
        similarity_threshold: float = 0.85,
    ) -> None:
        self.namespace = namespace
        self.store = store
        self.decay_rate = decay_rate
        self.reinforce_delta = reinforce_delta
        self.strength_threshold = strength_threshold
        self.similarity_threshold = similarity_threshold

    def _ns(self, thread_id: str) -> tuple[str, str]:
        return (self.namespace, thread_id)

    def _effective_strength(self, item_value: dict[str, Any]) -> float:
        """计算衰减后的有效强度。"""
        strength = item_value.get("strength", 1.0)
        last_accessed = item_value.get("last_accessed", item_value.get("created_at", time.time()))
        hours = (time.time() - last_accessed) / 3600
        return strength * math.exp(-self.decay_rate * hours)

    def put(self, content: str, *, thread_id: str) -> None:
        """添加记忆。自动去重：高度相似的合并并强化已有条目。"""
        ns = self._ns(thread_id)

        try:
            existing = self.store.search(ns, query=content, limit=3)
        except Exception:
            existing = []

        for item in existing:
            if not item.value:
                continue
            old_content = item.value.get("content", "")
            if self._text_similar(content, old_content):
                item.value["strength"] = min(1.0, item.value.get("strength", 1.0) + self.reinforce_delta)
                item.value["last_accessed"] = time.time()
                item.value["access_count"] = item.value.get("access_count", 0) + 1
                self.store.put(ns, key=item.key, value=item.value)
                logger.info("[LongTermMemory] 合并强化已有记忆: %.40s", old_content)
                return

        now = time.time()
        value = {
            "content": content,
            "strength": 1.0,
            "created_at": now,
            "last_accessed": now,
            "access_count": 0,
        }
        self.store.put(ns, key=str(uuid.uuid4()), value=value)
        logger.info("[LongTermMemory] 新增记忆: %.60s", content)

    def search(self, query: str, *, thread_id: str, limit: int = 5) -> list[str]:
        """语义检索。按衰减后有效强度排序。命中时自动强化。"""
        ns = self._ns(thread_id)
        try:
            results = self.store.search(ns, query=query, limit=limit * 2)
        except Exception:
            logger.debug("[LongTermMemory] store.search 失败", exc_info=True)
            return []

        if not results:
            return []

        scored = []
        for item in results:
            if not item.value:
                continue
            eff = self._effective_strength(item.value)
            if eff >= self.strength_threshold:
                scored.append((eff, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:limit]

        contents = []
        for _score, item in top:
            item.value["last_accessed"] = time.time()
            item.value["access_count"] = item.value.get("access_count", 0) + 1
            item.value["strength"] = min(
                1.0, item.value.get("strength", 0.5) + self.reinforce_delta
            )
            self.store.put(ns, key=item.key, value=item.value)
            contents.append(item.value.get("content", ""))

        if contents:
            logger.info("[LongTermMemory] 检索到 %d 条相关记忆", len(contents))
        return contents

    def prune(self, *, thread_id: str) -> int:
        """清理有效强度低于阈值的记忆。返回清理数量。"""
        ns = self._ns(thread_id)
        try:
            all_items = self.store.search(ns, query="", limit=1000)
        except Exception:
            return 0

        pruned = 0
        for item in all_items:
            if not item.value:
                continue
            eff = self._effective_strength(item.value)
            if eff < self.strength_threshold:
                self.store.delete(ns, key=item.key)
                pruned += 1

        if pruned:
            logger.info("[LongTermMemory] 清理了 %d 条衰减记忆", pruned)
        return pruned

    def consolidate(self, *, thread_id: str, llm: BaseChatModel, prompt: str | None = None) -> None:
        """LLM 整合相似/矛盾的记忆。适合后台定期执行。"""
        ns = self._ns(thread_id)
        try:
            all_items = self.store.search(ns, query="", limit=200)
        except Exception:
            return

        if len(all_items) < 3:
            return

        contents = [
            item.value.get("content", "")
            for item in all_items
            if item.value and item.value.get("content")
        ]
        if not contents:
            return

        sys_prompt = prompt or _CONSOLIDATE_SYSTEM
        response = llm.invoke([
            SystemMessage(content=sys_prompt),
            HumanMessage(content="\n".join(f"- {c}" for c in contents)),
        ])

        try:
            consolidated = json.loads(response.content.strip())
        except (json.JSONDecodeError, TypeError):
            logger.warning("[LongTermMemory] consolidate 解析失败")
            return

        if not isinstance(consolidated, list) or not consolidated:
            return

        for item in all_items:
            self.store.delete(ns, key=item.key)

        now = time.time()
        for content in consolidated:
            if isinstance(content, str) and content.strip():
                self.store.put(
                    ns,
                    key=str(uuid.uuid4()),
                    value={
                        "content": content.strip(),
                        "strength": 1.0,
                        "created_at": now,
                        "last_accessed": now,
                        "access_count": 0,
                    },
                )

        logger.info(
            "[LongTermMemory] 整合 %d → %d 条记忆",
            len(contents),
            len(consolidated),
        )

    @staticmethod
    def _text_similar(a: str, b: str) -> bool:
        """简单的文本相似度判断（基于字符级 Jaccard）。

        仅用于 put() 时的快速去重，不替代语义检索。
        """
        if not a or not b:
            return False
        set_a = set(a)
        set_b = set(b)
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return (intersection / union) > 0.85 if union else False
