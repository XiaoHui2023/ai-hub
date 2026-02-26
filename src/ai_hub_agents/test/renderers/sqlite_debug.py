"""SQLite Debug 渲染器，将每次 LLM 调用的完整上下文持久化到 SQLite。"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from langchain_core.messages import AIMessage, BaseMessage, messages_to_dict

from ai_hub_agents.core.callbacks import StreamCallback


class SqliteDebugRenderer(StreamCallback):
    """将每次 LLM 调用的完整上下文写入 SQLite，不做任何文本输出。

    利用事件缓冲策略解决"LLM 回调时还不知道节点名"的问题：

    - ``on_llm_start`` → 缓存 messages
    - ``on_llm_end``   → 把 AI 回复追加到缓存
    - ``on_node``      → 此时才有节点名，将缓存写入 SQLite 并清空

    如果某个节点没有 LLM 调用，``on_node`` 时缓存为 None，直接跳过。

    ``thread_id`` 通过 ``on_queue_wait`` / ``on_queue_resume`` 自动捕获，
    无需在构造函数中指定。

    使用方法::

        renderer = SqliteDebugRenderer(db_path="debug.db")
        result = agent.invoke("你好", thread_id="test-001", callbacks=[renderer])

        # 事后用 DB Browser for SQLite 打开，或代码查询：
        import sqlite3, json
        conn = sqlite3.connect("debug.db")
        for row in conn.execute(
            "SELECT node_path, call_seq, messages FROM llm_calls WHERE thread_id=?",
            ("test-001",),
        ):
            print(f"=== {row[0]} #{row[1]} ===")
            for msg in json.loads(row[2]):
                print(f"  [{msg['type']}] {msg['data']['content'][:100]}")
    """

    def __init__(self, db_path: str = "llm_debug.db") -> None:
        self._db_path = db_path
        self._call_seq = 0
        self._thread_id: str = "unknown"
        self._pending_messages: list[BaseMessage] | None = None
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS llm_calls (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT    NOT NULL,
                    node_path TEXT    NOT NULL,
                    call_seq  INTEGER NOT NULL,
                    timestamp TEXT    NOT NULL,
                    messages  TEXT    NOT NULL
                )
            """)

    # ── 排队钩子 → 自动捕获 thread_id ──────────────

    def on_queue_wait(self, thread_id: str) -> None:
        self._thread_id = thread_id

    def on_queue_resume(self, thread_id: str) -> None:
        self._thread_id = thread_id

    # ── LLM 生命周期 ────────────────────────────

    def on_llm_start(self, messages: list[BaseMessage]) -> None:
        self._pending_messages = list(messages)

    def on_llm_end(self, response: AIMessage) -> None:
        if self._pending_messages is not None:
            self._pending_messages.append(response)

    # ── 节点完成 → 写入 SQLite ──────────────────

    def on_node(self, name: str) -> None:
        if self._pending_messages is None:
            return
        self._call_seq += 1
        self._write(name, self._pending_messages)
        self._pending_messages = None

    def _write(self, node_path: str, messages: list[BaseMessage]) -> None:
        serialized = json.dumps(
            messages_to_dict(messages),
            ensure_ascii=False,
            indent=2,
        )
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT INTO llm_calls "
                "(thread_id, node_path, call_seq, timestamp, messages) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    self._thread_id,
                    node_path,
                    self._call_seq,
                    datetime.now(timezone.utc).isoformat(),
                    serialized,
                ),
            )
