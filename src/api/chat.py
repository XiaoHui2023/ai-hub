from fastapi import Request
from fastapi.responses import StreamingResponse
from .base_api import BaseRouter
from protocol.chat import completion
import logging
import json

logger = logging.getLogger(__name__)


class ChatRouter(BaseRouter):
    service = "chat"
    operation = "completion"

    def _setup_routes(self):
        @self.router.post(self.path)
        async def chat(request: Request, payload: completion.Request):
            async def run(op, client_ip):
                run_kwargs = dict(
                    messages=payload.messages,
                    model=payload.model,
                    temperature=payload.temperature,
                    frequency_penalty=payload.frequency_penalty,
                    presence_penalty=payload.presence_penalty,
                    top_p=payload.top_p,
                )

                if payload.stream:
                    return StreamingResponse(
                        _stream_chunks(op, run_kwargs, client_ip),
                        media_type="text/event-stream",
                    )
                else:
                    result = ""
                    async for chunk in op.run(**run_kwargs):
                        result += chunk
                    logger.info(f"chat response to {client_ip}: {result[:200]}")
                    return {"content": result}

            return await self._handle(request, payload, run)


async def _stream_chunks(op, run_kwargs: dict, client_ip: str):
    """SSE 格式逐块推送"""
    result = ""
    try:
        async for chunk in op.run(**run_kwargs):
            result += chunk
            yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.exception(f"chat stream error from {client_ip}: {e}")
        yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
    finally:
        if result:
            logger.info(f"chat response to {client_ip}: {result[:200]}")
