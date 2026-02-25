"""SSE 流式渲染器。

将 Agent 的 StreamCallback 生命周期事件序列化为 JSON，
通过 asyncio.Queue 桥接到异步 SSE 响应流。

因为 BaseAgent.invoke() 是同步方法（在线程池中执行），
而 SSE 响应需要 async generator，所以用 call_soon_threadsafe
跨线程安全地推送事件。
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from langchain_core.messages import AIMessage

from ai_hub_agents.core.callbacks import StreamCallback


class SSERenderer(StreamCallback):
    """StreamCallback → asyncio.Queue 桥接。

    每个事件序列化为 JSON 字符串推入 queue，
    由 run_agent_sse() 消费并输出为 SSE data 帧。
    所有字段原样保留，不做截断或摘要，前端自行渲染。
    """

    def __init__(self) -> None:
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """绑定事件循环，必须在 async 上下文中调用。"""
        self._loop = loop

    def _send(self, data: dict[str, Any]) -> None:
        payload = json.dumps(data, ensure_ascii=False, default=str)
        if self._loop is not None and self._loop.is_running():
            self._loop.call_soon_threadsafe(self.queue.put_nowait, payload)
        else:
            self.queue.put_nowait(payload)

    # ── 生命周期钩子 ─────────────────────────────

    def on_stream_start(self) -> None:
        self._send({"type": "stream_start"})

    def on_tool_call(self, name: str, args: dict[str, Any]) -> None:
        self._send({"type": "tool_call", "name": name, "args": args})

    def on_tool_result(self, name: str, content: str) -> None:
        self._send({
            "type": "tool_result",
            "name": name,
            "content": content,
            "success": True,
        })

    def on_tool_error(self, name: str, content: str) -> None:
        self._send({
            "type": "tool_error",
            "name": name,
            "content": content,
            "success": False,
        })

    def on_ai_message(self, message: AIMessage) -> None:
        self._send({"type": "ai_message", "content": message.content})

    def on_stream_end(self, result: str) -> None:
        self._send({"type": "stream_end", "result": result})
