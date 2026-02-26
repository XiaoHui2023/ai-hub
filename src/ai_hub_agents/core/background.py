from __future__ import annotations

import asyncio
import logging
import queue
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")


class BackgroundAgent(ABC, Generic[T]):
    """后台 hook 式 agent 基类 — 独立线程，累积消费，非阻塞提交。

    主线程通过 emit() 提交任务后立即返回（零阻塞）。
    后台工作线程持续监听队列，有任务就处理。
    如果处理速度慢导致任务堆积，自动调用 merge() 将多个任务
    合并为一批，再交给 process() 一次性处理。

    子类必须实现：
        - process(items: list[T]): 处理一批累积的任务

    子类可覆盖：
        - merge(items: list[T]) -> list[T]: 自定义合并逻辑
        - on_error(exc: Exception, items: list[T]): 错误处理

    类型参数：
        T: 任务载荷类型（如 list[BaseMessage]、str、自定义 dataclass）

    用法::

        class MemoryWorker(BackgroundAgent[list[BaseMessage]]):
            def process(self, items):
                all_msgs = [m for batch in items for m in batch]
                llm.invoke(compress(all_msgs))

            def merge(self, items):
                return [[m for batch in items for m in batch]]

        worker = MemoryWorker(debounce=1.0)
        worker.start()
        worker.emit(messages)   # 非阻塞
        worker.stop()           # 优雅退出
    """

    def __init__(
        self,
        *,
        max_queue: int = 0,
        debounce: float = 0,
        drain_on_stop: bool = True,
        callbacks: list[Any] | None = None,
    ) -> None:
        """
        Args:
            max_queue: 队列容量上限，0 表示无限。
            debounce: 收到首个任务后额外等待的秒数，让更多任务积累。
            drain_on_stop: stop() 时是否处理完队列中剩余的任务。
            callbacks: 可选的 StreamCallback 列表，用于通知后台任务生命周期。
        """
        self._queue: queue.Queue[T] = queue.Queue(maxsize=max_queue)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._debounce = debounce
        self._drain_on_stop = drain_on_stop
        self._callbacks: list[Any] = callbacks or []
        self._logger = logging.getLogger(f"{__name__}.{type(self).__name__}")

    # ── 生命周期 ──────────────────────────────────

    def start(self) -> None:
        """启动后台工作线程（幂等，重复调用无副作用）。"""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name=f"bg-{type(self).__name__}",
        )
        self._thread.start()
        name = getattr(self, "_name", type(self).__name__)
        self._logger.debug("后台 worker '%s' 已启动", name)

    def stop(self, timeout: float | None = None) -> None:
        """优雅停止。drain_on_stop=True 时会处理完剩余任务。"""
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)
            self._thread = None
            self._logger.info("后台 agent 已停止")

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def pending(self) -> int:
        """队列中待处理的任务数。"""
        return self._queue.qsize()

    # ── 提交任务 ──────────────────────────────────

    def emit(self, payload: T) -> None:
        """非阻塞提交任务到队列。"""
        self._queue.put(payload)
        name = getattr(self, "_name", type(self).__name__)
        for cb in self._callbacks:
            cb.on_background_submit(name)

    # ── 内部循环 ──────────────────────────────────

    def _run_loop(self) -> None:
        while not self._stop.is_set():
            batch = self._collect_batch()
            if not batch:
                continue
            self._execute(batch)

        if self._drain_on_stop:
            remaining = self._drain()
            if remaining:
                self._logger.info("停止前处理剩余 %d 项", len(remaining))
                self._execute(remaining)

    def _collect_batch(self) -> list[T]:
        """阻塞等待首个任务，然后 drain 剩余 + debounce。"""
        try:
            first = self._queue.get(timeout=0.5)
        except queue.Empty:
            return []

        if self._debounce > 0:
            time.sleep(self._debounce)

        items = [first]
        items.extend(self._drain())
        return items

    def _drain(self) -> list[T]:
        """非阻塞取出队列中所有剩余项。"""
        items: list[T] = []
        while True:
            try:
                items.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return items

    def _execute(self, items: list[T]) -> None:
        """合并 + 处理 + 错误兜底。"""
        name = getattr(self, "_name", type(self).__name__)
        try:
            merged = self.merge(items)
            self._logger.debug(
                "处理 %d 项（合并前 %d 项）", len(merged), len(items)
            )
            self.process(merged)
            for cb in self._callbacks:
                cb.on_background_done(name, len(merged))
        except Exception as exc:
            for cb in self._callbacks:
                cb.on_background_error(name, str(exc), len(items))
            self.on_error(exc, items)

    # ── 子类接口 ──────────────────────────────────

    @abstractmethod
    def process(self, items: list[T]) -> None:
        """处理一批累积的任务。items 已经过 merge() 合并。"""
        ...

    def merge(self, items: list[T]) -> list[T]:
        """合并策略。默认原样返回，子类可覆盖实现去重/压缩/拼接。"""
        return items

    def on_error(self, exc: Exception, items: list[T]) -> None:
        """处理失败时的回调。默认仅记录日志，子类可覆盖实现重试等。"""
        self._logger.exception("后台处理失败（%d 项丢弃）", len(items))

    # ── Context Manager ──────────────────────────

    def __enter__(self) -> BackgroundAgent[T]:
        self.start()
        return self

    def __exit__(self, *args: object) -> None:
        self.stop()


class FnBackgroundAgent(BackgroundAgent[T]):
    """函数式后台 agent — 无需继承写类，传入函数即可使用。

    用法::

        def do_compress(items: list[dict]) -> None:
            for batch in items:
                llm.invoke(compress(batch["messages"]))

        worker = FnBackgroundAgent(fn=do_compress, name="compress")
        worker.start()
        worker.emit({"messages": msgs})
    """

    def __init__(
        self,
        *,
        fn: Callable[[list[T]], None],
        name: str = "fn-worker",
        merge_fn: Callable[[list[T]], list[T]] | None = None,
        callbacks: list[Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(callbacks=callbacks, **kwargs)
        self._fn = fn
        self._name = name
        self._merge_fn = merge_fn
        self._logger = logging.getLogger(f"{__name__}.{name}")

    def process(self, items: list[T]) -> None:
        self._fn(items)

    def merge(self, items: list[T]) -> list[T]:
        if self._merge_fn is not None:
            return self._merge_fn(items)
        return items


class AsyncBackgroundAgent(ABC, Generic[T]):
    """异步版后台 hook 式 agent — 基于 asyncio.Task。

    与 BackgroundAgent 相同的语义，但运行在 event loop 中，
    适用于 FastAPI / aiohttp 等异步服务场景。
    """

    def __init__(
        self,
        *,
        max_queue: int = 0,
        debounce: float = 0,
    ) -> None:
        self._queue: asyncio.Queue[T] = asyncio.Queue(maxsize=max_queue)
        self._task: asyncio.Task[None] | None = None
        self._debounce = debounce
        self._logger = logging.getLogger(f"{__name__}.{type(self).__name__}")

    async def start(self) -> None:
        """启动后台异步任务（幂等）。"""
        if self._task is not None and not self._task.done():
            return
        self._task = asyncio.create_task(
            self._run_loop(), name=f"bg-{type(self).__name__}"
        )
        self._logger.info("异步后台 agent 已启动")

    async def stop(self) -> None:
        """取消后台任务并等待退出。"""
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            self._logger.info("异步后台 agent 已停止")

    def emit(self, payload: T) -> None:
        """同步提交（适合从 sync callback 中调用）。"""
        self._queue.put_nowait(payload)

    async def emit_async(self, payload: T) -> None:
        """异步提交（队列满时等待）。"""
        await self._queue.put(payload)

    @property
    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    @property
    def pending(self) -> int:
        """队列中待处理的任务数。"""
        return self._queue.qsize()

    async def _run_loop(self) -> None:
        try:
            while True:
                first = await self._queue.get()
                if self._debounce > 0:
                    await asyncio.sleep(self._debounce)

                items = [first]
                while not self._queue.empty():
                    try:
                        items.append(self._queue.get_nowait())
                    except asyncio.QueueEmpty:
                        break

                try:
                    merged = self.merge(items)
                    self._logger.debug(
                        "处理 %d 项（合并前 %d 项）", len(merged), len(items)
                    )
                    await self.process(merged)
                except Exception as exc:
                    self.on_error(exc, items)
        except asyncio.CancelledError:
            raise

    # ── 子类接口 ──────────────────────────────────

    @abstractmethod
    async def process(self, items: list[T]) -> None:
        """处理一批累积的任务。items 已经过 merge() 合并。"""
        ...

    def merge(self, items: list[T]) -> list[T]:
        """合并策略。默认原样返回，子类可覆盖实现去重/压缩/拼接。"""
        return items

    def on_error(self, exc: Exception, items: list[T]) -> None:
        """处理失败时的回调。默认仅记录日志，子类可覆盖实现重试等。"""
        self._logger.exception("异步后台处理失败（%d 项丢弃）", len(items))

    # ── Async Context Manager ────────────────────

    async def __aenter__(self) -> AsyncBackgroundAgent[T]:
        await self.start()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.stop()
