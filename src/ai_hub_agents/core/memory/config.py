"""记忆基础设施 — checkpointer / store 工厂函数。

纯基础设施层，不持有 LLM。LLM 选择是调用方的责任。
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def create_checkpointer() -> Any:
    """根据环境变量创建 checkpointer。

    支持的 CHECKPOINT_BACKEND:
        - "sqlite"（默认）：使用 SQLite 文件存储
        - "postgres"：使用 PostgreSQL
        - "memory"：纯内存（重启即丢）
    """
    backend = os.environ.get("CHECKPOINT_BACKEND", "sqlite").lower()

    if backend == "memory":
        from langgraph.checkpoint.memory import MemorySaver

        logger.info("使用 MemorySaver（内存）作为 checkpointer")
        return MemorySaver()

    if backend == "sqlite":
        import sqlite3

        try:
            from langgraph.checkpoint.sqlite import SqliteSaver
        except ImportError:
            raise ImportError(
                "需要安装 langgraph-checkpoint-sqlite: "
                "pip install 'ai-hub-agents[memory]'"
            )
        db_path = os.environ.get("CHECKPOINT_SQLITE_PATH", "checkpoints.db")
        logger.info("使用 SqliteSaver（%s）作为 checkpointer", db_path)
        conn = sqlite3.connect(db_path, check_same_thread=False)
        return SqliteSaver(conn)

    if backend == "postgres":
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
        except ImportError:
            raise ImportError(
                "需要安装 langgraph-checkpoint-postgres: "
                "pip install 'ai-hub-agents[memory-postgres]'"
            )
        from psycopg import Connection
        from psycopg.rows import dict_row

        url = os.environ.get("CHECKPOINT_POSTGRES_URL", "")
        if not url:
            raise ValueError("CHECKPOINT_BACKEND=postgres 时必须设置 CHECKPOINT_POSTGRES_URL")
        conn = Connection.connect(
            url, autocommit=True, prepare_threshold=0, row_factory=dict_row
        )
        logger.info("使用 PostgresSaver 作为 checkpointer")
        return PostgresSaver(conn)

    raise ValueError(f"不支持的 CHECKPOINT_BACKEND: {backend}")


def _build_index_config() -> dict[str, Any] | None:
    """根据 EMBEDDING_* 环境变量构建 Store 语义索引配置。"""
    model = os.environ.get("EMBEDDING_MODEL")
    if not model:
        return None

    from langchain_openai import OpenAIEmbeddings

    api_key = os.environ.get("EMBEDDING_API_KEY") or os.environ.get("API_KEY", "")
    base_url = os.environ.get("EMBEDDING_BASE_URL") or os.environ.get("API_BASE_URL")

    embeddings = OpenAIEmbeddings(
        model=model,
        api_key=api_key,
        base_url=base_url,
        check_embedding_ctx_length=False,
    )
    return {"embed": embeddings, "dims": 1024, "fields": ["content"]}


def create_store() -> Any | None:
    """根据环境变量创建 Store。

    支持的 STORE_BACKEND:
        - "memory"（默认）：InMemoryStore，需配置 EMBEDDING_MODEL 才有意义
        - "postgres"：PostgresStore，持久化 + pgvector 语义搜索
    """
    backend = os.environ.get("STORE_BACKEND", "memory").lower()
    index_config = _build_index_config()

    if backend == "memory":
        if not index_config:
            logger.info("未配置 EMBEDDING_MODEL，跳过 store 创建")
            return None
        from langgraph.store.memory import InMemoryStore

        store = InMemoryStore(index=index_config)
        logger.info("使用 InMemoryStore（embedding=%s）作为 store", os.environ["EMBEDDING_MODEL"])
        return store

    if backend == "postgres":
        try:
            from langgraph.store.postgres import PostgresStore
        except ImportError:
            raise ImportError(
                "需要安装 langgraph-checkpoint-postgres 及 psycopg: "
                "pip install 'ai-hub-agents[memory-postgres]'"
            )
        from psycopg import Connection
        from psycopg.rows import dict_row

        url = os.environ.get("STORE_POSTGRES_URL") or os.environ.get("CHECKPOINT_POSTGRES_URL", "")
        if not url:
            raise ValueError(
                "STORE_BACKEND=postgres 时必须设置 STORE_POSTGRES_URL 或 CHECKPOINT_POSTGRES_URL"
            )
        conn = Connection.connect(
            url, autocommit=True, prepare_threshold=0, row_factory=dict_row
        )
        store_kwargs: dict[str, Any] = {}
        if index_config:
            store_kwargs["index"] = index_config
        store = PostgresStore(conn, **store_kwargs)
        store.setup()
        logger.info("使用 PostgresStore 作为 store（embedding=%s）", os.environ.get("EMBEDDING_MODEL", "无"))
        return store

    raise ValueError(f"不支持的 STORE_BACKEND: {backend}")
