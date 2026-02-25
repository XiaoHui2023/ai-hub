from fastapi import Request
from .base_router import BaseRouter
import ai_hub_protocol as protocol
import logging

logger = logging.getLogger(__name__)


class ContextAddRouter(BaseRouter):
    service = "context"
    operation = "add"

    def _setup_routes(self):
        @self.router.post(self.path)
        async def do_add(request: Request, payload: protocol.context.add.Request):
            async def run(op, client_ip):
                result = await op.run(
                    content=payload.content,
                    user_id=payload.user_id,
                    tag=payload.tag,
                )
                logger.info(f"context/add response to {client_ip}: {str(result)[:200]}")
                return protocol.context.add.Response(content=result).model_dump()

            return await self._handle(request, payload, run)


class ContextSearchRouter(BaseRouter):
    service = "context"
    operation = "search"

    def _setup_routes(self):
        @self.router.post(self.path)
        async def do_search(request: Request, payload: protocol.context.search.Request):
            async def run(op, client_ip):
                result = await op.run(
                    query=payload.query,
                    user_id=payload.user_id,
                    tag=payload.tag,
                )
                logger.info(f"context/search response to {client_ip}: {str(result)[:200]}")
                return protocol.context.search.Response(content=result).model_dump()

            return await self._handle(request, payload, run)
