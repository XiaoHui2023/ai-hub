"""Thread ID 排队锁管理器。

提供按 key（通常是 thread_id）分桶的锁，确保同一 thread_id
的请求串行执行，防止并发读写 checkpoint 导致的竞态条件。

两种实现：
  - ThreadLockManager: 基于 threading.Lock，用于同步调用场景（脚本/测试）
  - AsyncThreadLockManager: 基于 asyncio.Lock，用于异步服务端场景

两者均带引用计数，锁归零后自动清理防内存泄漏。
"""

from __future__ import annotations

import asyncio
import threading
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncIterator, Iterator


class ThreadLockManager:
    """同步锁管理器 — 按 key 分桶的 threading.Lock。"""

    def __init__(self) -> None:
        self._guard = threading.Lock()
        self._locks: dict[str, threading.Lock] = {}
        self._refs: dict[str, int] = {}

    @contextmanager
    def acquire(self, key: str) -> Iterator[None]:
        lock = self._get_lock(key)
        lock.acquire()
        try:
            yield
        finally:
            lock.release()
            self._release_lock(key)

    def _get_lock(self, key: str) -> threading.Lock:
        with self._guard:
            if key not in self._locks:
                self._locks[key] = threading.Lock()
                self._refs[key] = 0
            self._refs[key] += 1
            return self._locks[key]

    def _release_lock(self, key: str) -> None:
        with self._guard:
            self._refs[key] -= 1
            if self._refs[key] <= 0:
                del self._locks[key]
                del self._refs[key]


class AsyncThreadLockManager:
    """异步锁管理器 — 按 key 分桶的 asyncio.Lock。"""

    def __init__(self) -> None:
        self._guard = asyncio.Lock()
        self._locks: dict[str, asyncio.Lock] = {}
        self._refs: dict[str, int] = {}

    @asynccontextmanager
    async def acquire(self, key: str) -> AsyncIterator[None]:
        lock = await self._get_lock(key)
        await lock.acquire()
        try:
            yield
        finally:
            lock.release()
            await self._release_lock(key)

    async def _get_lock(self, key: str) -> asyncio.Lock:
        async with self._guard:
            if key not in self._locks:
                self._locks[key] = asyncio.Lock()
                self._refs[key] = 0
            self._refs[key] += 1
            return self._locks[key]

    async def _release_lock(self, key: str) -> None:
        async with self._guard:
            self._refs[key] -= 1
            if self._refs[key] <= 0:
                del self._locks[key]
                del self._refs[key]
