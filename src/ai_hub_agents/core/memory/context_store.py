"""ChatContextStore — 按 thread_id 持久化会话上下文。

独立于 LangGraph checkpointer，由 ChatAgent 的 load_context / save_context
节点直接读写。支持乐观并发控制（版本号 CAS），防止异步压缩覆盖新数据。

存储后端默认复用 CHECKPOINT_BACKEND / CHECKPOINT_SQLITE_PATH 环境变量。
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from typing import Any

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

logger = logging.getLogger(__name__)

_TYPE_MAP: dict[str, type[BaseMessage]] = {
    "human": HumanMessage,
    "ai": AIMessage,
    "system": SystemMessage,
}


def _serialize_messages(messages: list[BaseMessage]) -> str:
    result = []
    for m in messages:
        if isinstance(m, BaseMessage) and hasattr(m, "content"):
            data: dict[str, Any] = {"type": m.type, "content": m.content}
            if hasattr(m, "id") and m.id:
                data["id"] = m.id
            result.append(data)
    return json.dumps(result, ensure_ascii=False)


def _deserialize_messages(raw: str) -> list[BaseMessage]:
    data = json.loads(raw)
    messages: list[BaseMessage] = []
    for d in data:
        cls = _TYPE_MAP.get(d.get("type", ""), HumanMessage)
        kwargs: dict[str, Any] = {"content": d["content"]}
        if d.get("id"):
            kwargs["id"] = d["id"]
        messages.append(cls(**kwargs))
    return messages


class ChatContextStore:
    """SQLite-backed conversation context store with optimistic concurrency.

    每条记录包含:
      - thread_id (PK)
      - messages_json: 序列化的消息列表
      - summary: 压缩摘要
      - version: 乐观并发版本号
      - updated_at: 最后更新时间戳
    """

    def __init__(self, db_path: str | None = None) -> None:
        path = db_path or os.environ.get("CHECKPOINT_SQLITE_PATH", "checkpoints.db")
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_table()
        logger.info("ChatContextStore 初始化完成（%s）", path)

    def _init_table(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_contexts (
                thread_id   TEXT PRIMARY KEY,
                messages_json TEXT NOT NULL DEFAULT '[]',
                summary     TEXT NOT NULL DEFAULT '',
                version     INTEGER NOT NULL DEFAULT 0,
                updated_at  REAL NOT NULL
            )
        """)
        self._conn.commit()

    def load(self, thread_id: str) -> tuple[dict[str, Any] | None, int]:
        """加载指定 thread 的上下文。

        Returns:
            (data, version) — data = {"messages": [...], "summary": "..."}
            如果 thread 不存在，返回 (None, 0)。
        """
        row = self._conn.execute(
            "SELECT messages_json, summary, version FROM chat_contexts WHERE thread_id = ?",
            (thread_id,),
        ).fetchone()
        if row is None:
            return None, 0
        messages = _deserialize_messages(row["messages_json"])
        return {"messages": messages, "summary": row["summary"]}, row["version"]

    def save(self, thread_id: str, messages: list[BaseMessage], summary: str) -> int:
        """无条件保存，返回新版本号。"""
        messages_json = _serialize_messages(messages)
        now = time.time()
        self._conn.execute(
            """
            INSERT INTO chat_contexts (thread_id, messages_json, summary, version, updated_at)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(thread_id) DO UPDATE SET
                messages_json = excluded.messages_json,
                summary       = excluded.summary,
                version       = version + 1,
                updated_at    = excluded.updated_at
            """,
            (thread_id, messages_json, summary, now),
        )
        self._conn.commit()
        row = self._conn.execute(
            "SELECT version FROM chat_contexts WHERE thread_id = ?",
            (thread_id,),
        ).fetchone()
        new_ver = row["version"] if row else 1
        logger.debug(
            "[ChatContextStore] save thread=%s, msgs=%d, ver=%d",
            thread_id, len(messages), new_ver,
        )
        return new_ver

    def save_if_version(
        self,
        thread_id: str,
        messages: list[BaseMessage],
        summary: str,
        expected_version: int,
    ) -> bool:
        """CAS 写入：仅当存储版本 == expected_version 时更新。

        用于异步压缩场景——如果在压缩期间有新消息写入（版本已变），
        则放弃本次写入，避免覆盖新数据。
        """
        messages_json = _serialize_messages(messages)
        now = time.time()
        cursor = self._conn.execute(
            """
            UPDATE chat_contexts
            SET messages_json = ?, summary = ?, version = version + 1, updated_at = ?
            WHERE thread_id = ? AND version = ?
            """,
            (messages_json, summary, now, thread_id, expected_version),
        )
        self._conn.commit()
        ok = cursor.rowcount > 0
        if ok:
            logger.debug(
                "[ChatContextStore] CAS save OK thread=%s, msgs=%d, ver=%d→%d",
                thread_id, len(messages), expected_version, expected_version + 1,
            )
        else:
            logger.info(
                "[ChatContextStore] CAS save 版本冲突，跳过 thread=%s (expected ver=%d)",
                thread_id, expected_version,
            )
        return ok
