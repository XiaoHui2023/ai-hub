from typing import List, Optional
from fastapi import Request
from .base_api import BasePayload, BaseRouter
from models.message import Message
import logging

logger = logging.getLogger(__name__)


class ContextAddPayload(BasePayload):
    content: str
    user_id: str
    tag: str


class ContextSearchPayload(BasePayload):
    query: str
    user_id: str
    tag: str


class ContextAddRouter(BaseRouter):
    service = "context"
    operation = "add"

    def _setup_routes(self):
        @self.router.post(self.path)
        async def add(request: Request, payload: ContextAddPayload):
            async def run(op, client_ip):
                result = await op.run(
                    content=payload.content,
                    user_id=payload.user_id,
                    tag=payload.tag,
                )
                logger.info(f"context/add response to {client_ip}: {str(result)[:200]}")
                return {"content": result}

            return await self._handle(request, payload, run)


class ContextSearchRouter(BaseRouter):
    service = "context"
    operation = "search"

    def _setup_routes(self):
        @self.router.post(self.path)
        async def search(request: Request, payload: ContextSearchPayload):
            async def run(op, client_ip):
                result = await op.run(
                    query=payload.query,
                    user_id=payload.user_id,
                    tag=payload.tag,
                )
                logger.info(f"context/search response to {client_ip}: {str(result)[:200]}")
                return {"content": result}

            return await self._handle(request, payload, run)
