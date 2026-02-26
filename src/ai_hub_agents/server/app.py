"""通用 Agent HTTP 服务。

两种使用方式：

1. 一键启动::

       serve(XlsxAgent, llm, port=8000)

2. 自定义集成::

       app = create_app([XlsxAgent], llm)
"""

from __future__ import annotations

import asyncio
import base64
import json
import tempfile
from pathlib import Path
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

from ai_hub_agents.core import BaseAgent
from ai_hub_agents.core.fields import get_file_fields, get_output_extensions
from ai_hub_agents.core.thread_lock import AsyncThreadLockManager

from .sse import SSERenderer


# ── 公共 API ─────────────────────────────────────


def serve(
    agents: list[type[BaseAgent]] | type[BaseAgent],
    llm: Any,
    *,
    host: str = "0.0.0.0",
    port: int = 8000,
    **kwargs: Any,
) -> None:
    """一键启动 Agent HTTP 服务。

    自动为每个 Agent 生成 POST /<name> 路由（SSE 流式响应）。
    额外的 ``kwargs`` 会透传给 ``agent_cls.create()``。
    """
    import uvicorn

    app = create_app(agents, llm, **kwargs)
    uvicorn.run(app, host=host, port=port)


def create_app(
    agents: list[type[BaseAgent]] | type[BaseAgent],
    llm: Any,
    **kwargs: Any,
) -> Starlette:
    """创建 Starlette 应用，可挂载到自定义 ASGI 服务器。

    当只注册一个 Agent 时，自动在 ``POST /`` 根路径额外挂载，
    客户端可省略 Agent 名称。额外的 ``kwargs`` 会透传给 ``agent_cls.create()``。
    """
    if not isinstance(agents, list):
        agents = [agents]

    routes: list[Route] = []
    for cls in agents:
        routes.append(_build_route(cls, llm, **kwargs))

    if len(agents) == 1:
        root_endpoint = routes[0].endpoint
        routes.append(Route("/", root_endpoint, methods=["POST"]))

    return Starlette(routes=routes)


# ── 内部实现 ─────────────────────────────────────


async def _stream_agent(
    agent: BaseAgent,
    message: str,
    fields: dict[str, Any],
    renderer: SSERenderer,
    loop: asyncio.AbstractEventLoop,
    *,
    thread_id: str | None = None,
):
    """核心 SSE 生成器：执行 Agent 并 yield SSE data 帧。"""

    def _run() -> None:
        agent.invoke(message, thread_id=thread_id, callbacks=[renderer], **fields)

    future = loop.run_in_executor(None, _run)
    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    renderer.queue.get(), timeout=0.5
                )
                yield f"data: {data}\n\n"
            except asyncio.TimeoutError:
                if future.done():
                    break
    finally:
        while not renderer.queue.empty():
            data = renderer.queue.get_nowait()
            yield f"data: {data}\n\n"

        if future.done():
            exc = future.exception()
            if exc:
                yield _sse_frame({"type": "error", "message": str(exc)})


def _build_route(agent_cls: type[BaseAgent], llm: Any, **kwargs: Any) -> Route:
    """为一个 Agent 自动生成路由。"""
    schema = getattr(agent_cls, "state_schema", None)
    input_fields, output_fields = get_file_fields(schema)
    ext_map = get_output_extensions(schema, output_fields)
    has_files = bool(input_fields or output_fields)

    holder: dict[str, BaseAgent] = {}
    async_locks: AsyncThreadLockManager | None = (
        AsyncThreadLockManager() if agent_cls.sequential_threads else None
    )

    def _get_agent() -> BaseAgent:
        if "i" not in holder:
            holder["i"] = agent_cls.create(llm, **kwargs)
        return holder["i"]

    async def endpoint(request: Request) -> StreamingResponse:
        agent = _get_agent()
        state_fields: dict[str, Any] = {}
        thread_id: str | None = None

        if has_files:
            form = await request.form()
            message = str(form.get("message", ""))
            if not message:
                return JSONResponse(
                    {"error": "缺少 message 字段"}, status_code=400
                )
        else:
            body = await request.json()
            message = body.get("message", "")
            thread_id = body.get("thread_id")
            if not message:
                return JSONResponse(
                    {"error": "缺少 message 字段"}, status_code=400
                )

        renderer = SSERenderer()
        loop = asyncio.get_running_loop()
        renderer.set_loop(loop)

        async def _stream():
            if async_locks and thread_id:
                async with async_locks.acquire(thread_id):
                    renderer._send({"type": "queue_resume"})
                    async for chunk in _stream_core():
                        yield chunk
            else:
                async for chunk in _stream_core():
                    yield chunk

        async def _stream_core():
            with tempfile.TemporaryDirectory(prefix="ai_hub_") as tmpdir:
                tmp = Path(tmpdir)

                if has_files:
                    for field in input_fields:
                        upload = form.get(field)
                        if upload is not None:
                            fp = tmp / upload.filename
                            fp.write_bytes(await upload.read())
                            state_fields[field] = str(fp)

                    for field in output_fields:
                        ext = ext_map.get(field, "")
                        state_fields[field] = str(tmp / f"{field}{ext}")

                async for chunk in _stream_agent(
                    agent, message, state_fields, renderer, loop,
                    thread_id=thread_id,
                ):
                    yield chunk

                if output_fields:
                    for field in output_fields:
                        p = Path(state_fields.get(field, ""))
                        if p.exists():
                            content = base64.b64encode(
                                p.read_bytes()
                            ).decode()
                            yield _sse_frame({
                                "type": "output_file",
                                "field": field,
                                "filename": p.name,
                                "content_base64": content,
                            })

        return StreamingResponse(_stream(), media_type="text/event-stream")

    return Route(f"/{agent_cls.name}", endpoint, methods=["POST"])


def _sse_frame(data: dict[str, Any]) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
