"""同步客户端。"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Callable, Iterator

import httpx

from ._event import AgentEvent
from ._result import AgentResult
from ._sse import iter_sse_events


class AgentClient:
    """同步 Agent 客户端，适用于脚本和测试场景。

    Usage::

        client = AgentClient("http://localhost:8000")
        result = client.invoke("你好", thread_id="s1")
        print(result)

        for event in client.stream("你好"):
            print(event.content, end="")

        client.close()

    也可用作上下文管理器::

        with AgentClient("http://localhost:8000") as client:
            result = client.invoke("你好")
    """

    def __init__(self, base_url: str, *, timeout: float = 300.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> AgentClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    # ── 公共 API ──────────────────────────────────────

    def invoke(
        self,
        message: str,
        *,
        thread_id: str | None = None,
        on_event: Callable[[AgentEvent], None] | None = None,
        **files: str | Path,
    ) -> AgentResult:
        """阻塞调用，返回最终结果。

        Args:
            message: 用户消息。
            thread_id: 会话 ID（多轮对话）。
            on_event: 可选回调，每个 SSE 事件触发一次。
            **files: 文件字段，值为本地路径。
        """
        result = AgentResult()
        for event in self.stream(message, thread_id=thread_id, **files):
            if on_event is not None:
                on_event(event)
            self._apply_event(event, result)
        return result

    def stream(
        self,
        message: str,
        *,
        thread_id: str | None = None,
        **files: str | Path,
    ) -> Iterator[AgentEvent]:
        """流式调用，逐事件 yield。"""
        kwargs = _build_request(message, thread_id=thread_id, **files)
        with self._client.stream("POST", f"{self._base_url}/", **kwargs) as resp:
            resp.raise_for_status()
            yield from iter_sse_events(resp.iter_lines())

    # ── 内部 ──────────────────────────────────────────

    @staticmethod
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


# ── 请求构建 ──────────────────────────────────────────


def _build_request(
    message: str,
    *,
    thread_id: str | None = None,
    **files: str | Path,
) -> dict[str, Any]:
    """根据是否有文件，构建 httpx 请求 kwargs。"""
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
