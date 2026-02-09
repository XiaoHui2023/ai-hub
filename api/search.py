from fastapi import Request
from .base_api import BasePayload, BaseRouter
import logging

logger = logging.getLogger(__name__)


class SearchPayload(BasePayload):
    query: str


class SearchRouter(BaseRouter):
    service = "search"
    operation = "query"

    def _setup_routes(self):
        @self.router.post(self.path)
        async def query(request: Request, payload: SearchPayload):
            async def run(op, client_ip):
                result = await op.run(query=payload.query)
                logger.info(f"search response to {client_ip}: {str(result)[:200]}")
                return {"content": result}

            return await self._handle(request, payload, run)
