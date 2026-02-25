import json
import asyncio

class SSEStreamRenderer(StreamCallback):
    """将 Agent 事件转为 SSE JSON，推入 asyncio.Queue。"""

    def __init__(self):
        self.queue: asyncio.Queue[str] = asyncio.Queue()

    def _send(self, data: dict):
        self.queue.put_nowait(json.dumps(data, ensure_ascii=False))

    def on_stream_start(self):
        self._send({"type": "stream_start"})

    def on_tool_call(self, name, args):
        self._send({
            "type": "tool_call",
            "name": name,
            "label": TOOL_LABELS.get(name, name),
            "args": _safe_summary(args),
        })

    def on_tool_result(self, name, content):
        self._send({
            "type": "tool_result",
            "name": name,
            "summary": content[:500],
            "success": True,
        })

    def on_tool_error(self, name, content):
        self._send({
            "type": "tool_error",
            "name": name,
            "summary": content[:500],
            "success": False,
        })

    def on_ai_message(self, message):
        self._send({
            "type": "ai_message",
            "content": message.content,
        })

    def on_stream_end(self, result):
        # file_id 由外部注入
        self._send({"type": "stream_end"})