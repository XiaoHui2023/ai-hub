from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from config import Config
from factory import create_operation
from .base_api import BaseAPI
from models.message import Message
import logging
import json

logger = logging.getLogger(__name__)


class Chat(BaseAPI):
    messages: List[Message]
    temperature: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    top_p: Optional[float] = None


def create_chat_router(config: Config) -> APIRouter:
    router = APIRouter()

    @router.post("/chat")
    async def chat(request: Request, payload: Chat):
        client_ip = request.client.host
        logger.info(f"chat from {client_ip}: {payload.model_dump_json(exclude_none=True)}")

        try:
            op = create_operation(
                cfg=config,
                service="chat",
                provider=payload.provider,
                model=payload.model,
                stream=payload.stream,
            )

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
                    stream_chunks(op, run_kwargs, client_ip),
                    media_type="text/event-stream",
                )
            else:
                result = ""
                async for chunk in op.run(**run_kwargs):
                    result += chunk

                logger.info(f"chat response to {client_ip}: {result[:200]}")
                return {"content": result}

        except (KeyError, ValueError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception(f"chat error from {client_ip}: {e}")
            raise HTTPException(status_code=500, detail=f"调用失败: {e}")

    return router


async def stream_chunks(op, run_kwargs: dict, client_ip: str):
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
