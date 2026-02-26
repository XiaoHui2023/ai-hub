"""轻量 SSE 行解析器。

将 ``data: {json}\n\n`` 格式的 SSE 帧解析为 :class:`AgentEvent`。
支持同步 / 异步两种消费方式。
"""

from __future__ import annotations

import json
from typing import AsyncIterator, Iterator

from ._event import AgentEvent


class SSEParser:
    """有状态的逐行 SSE 解析器。

    每次调用 :meth:`feed` 传入一行（不含换行符），
    当遇到空行时刷新缓冲区并返回 :class:`AgentEvent`。
    """

    __slots__ = ("_buf",)

    def __init__(self) -> None:
        self._buf: list[str] = []

    def feed(self, line: str) -> AgentEvent | None:
        """喂入一行，返回事件或 ``None``。"""
        stripped = line.rstrip("\r\n")
        if stripped.startswith("data: "):
            self._buf.append(stripped[6:])
            return None
        if stripped == "" and self._buf:
            return self._flush()
        return None

    def flush(self) -> AgentEvent | None:
        """流结束时调用，刷新尚未消费的缓冲区。"""
        if self._buf:
            return self._flush()
        return None

    def _flush(self) -> AgentEvent | None:
        raw = "".join(self._buf)
        self._buf.clear()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return None
        event_type = payload.pop("type", "unknown")
        return AgentEvent(type=event_type, data=payload)


# ── 便捷迭代器 ──────────────────────────────────────


def iter_sse_events(lines: Iterator[str]) -> Iterator[AgentEvent]:
    """同步版：逐行迭代并产出事件。"""
    parser = SSEParser()
    for line in lines:
        event = parser.feed(line)
        if event is not None:
            yield event
    event = parser.flush()
    if event is not None:
        yield event


async def aiter_sse_events(lines: AsyncIterator[str]) -> AsyncIterator[AgentEvent]:
    """异步版：逐行迭代并产出事件。"""
    parser = SSEParser()
    async for line in lines:
        event = parser.feed(line)
        if event is not None:
            yield event
    event = parser.flush()
    if event is not None:
        yield event
