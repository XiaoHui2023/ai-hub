"""通用 SSE 流式执行。

提供 run_agent_sse() 函数，将任意 BaseAgent 的 invoke() 过程
包装为 SSE StreamingResponse。各 Agent 的业务端点直接调用即可。
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from starlette.responses import StreamingResponse

from ai_hub_agents.core import BaseAgent

from .sse import SSERenderer


async def run_agent_sse(
    agent: BaseAgent,
    message: str,
    state_fields: dict[str, Any] | None = None,
) -> StreamingResponse:
    """将 Agent 执行过程包装为 SSE 流式响应。

    Args:
        agent: 任意 BaseAgent 实例
        message: 用户消息
        state_fields: Agent 特有的状态字段（如 input_file, output_file），
                      原样透传给 agent.invoke()
    """
    renderer = SSERenderer()
    loop = asyncio.get_running_loop()
    renderer.set_loop(loop)

    fields = state_fields or {}

    def _run_sync() -> None:
        agent.invoke(message, callbacks=[renderer], **fields)

    async def _event_stream():
        future = loop.run_in_executor(None, _run_sync)
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

            exc = future.exception() if future.done() else None
            if exc:
                err = json.dumps(
                    {"type": "error", "message": str(exc)},
                    ensure_ascii=False,
                )
                yield f"data: {err}\n\n"

    return StreamingResponse(
        _event_stream(), media_type="text/event-stream"
    )
