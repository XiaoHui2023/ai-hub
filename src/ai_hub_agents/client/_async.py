"""异步客户端。"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, AsyncIterator, Callable

import httpx

from ._event import AgentEvent
from ._result import AgentResult
from ._sse import aiter_sse_events


class AsyncAgentClient:
    """异步 Agent 客户端，适用于 Web 后端集成。

    Usage::

        async with AsyncAgentClient("http://localhost:8000") as client:
            result = await client.invoke("你好", thread_id="s1")
            print(result)

            async for event in client.stream("你好"):
                print(event.content, end="")
    """

    def __init__(self, base_url: str, *, timeout: float = 300.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncAgentClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    # ── 公共 API ──────────────────────────────────────

    async def invoke(
        self,
        message: str,
        *,
        thread_id: str | None = None,
        on_event: Callable[[AgentEvent], None] | None = None,
        **files: str | Path,
    ) -> AgentResult:
        """异步阻塞调用，返回最终结果。

        Args:
            message: 用户消息。
            thread_id: 会话 ID（多轮对话）。
            on_event: 可选回调，每个 SSE 事件触发一次（同步函数）。
            **files: 文件字段，值为本地路径。
        """
        result = AgentResult()
        async for event in self.stream(message, thread_id=thread_id, **files):
            if on_event is not None:
                on_event(event)
            _apply_event(event, result)
        return result

    async def stream(
        self,
        message: str,
        *,
        thread_id: str | None = None,
        **files: str | Path,
    ) -> AsyncIterator[AgentEvent]:
        """异步流式调用，逐事件 yield。"""
        kwargs = _build_request(message, thread_id=thread_id, **files)
        async with self._client.stream(
            "POST", f"{self._base_url}/", **kwargs
        ) as resp:
            resp.raise_for_status()
            async for event in aiter_sse_events(resp.aiter_lines()):
                yield event


# ── 内部工具 ──────────────────────────────────────────


def _apply_event(event: AgentEvent, result: AgentResult) -> None:
    if event.is_end:
        result.text = event.content
    elif event.type == "output_file":
        field = event.data.get("field", "")
        b64 = event.data.get("content_base64", "")
        result.files[field] = base64.b64decode(b64)
        result._filenames[field] = event.data.get("filename", "")
    elif event.is_error:
        raise RuntimeError(event.content)


def _build_request(
    message: str,
    *,
    thread_id: str | None = None,
    **files: str | Path,
) -> dict[str, Any]:
    if files:
        form_data: dict[str, str] = {"message": message}
        if thread_id is not None:
            form_data["thread_id"] = thread_id
        file_uploads: dict[str, tuple[str, bytes]] = {}
        for field, path in files.items():
            p = Path(path)
            file_uploads[field] = (p.name, p.read_bytes())
        return {"data": form_data, "files": file_uploads}

    body: dict[str, Any] = {"message": message}
    if thread_id is not None:
        body["thread_id"] = thread_id
    return {"json": body}
