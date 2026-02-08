from fastapi import APIRouter, HTTPException, Request
from config import Config
from factory import create_operation
from .base_api import BaseAPI
import logging

logger = logging.getLogger(__name__)


class Search(BaseAPI):
    query: str

def create_search_router(config: Config) -> APIRouter:
    router = APIRouter()

    @router.post("/search")
    async def search(request: Request, payload: Search):
        client_ip = request.client.host
        logger.info(f"search from {client_ip}: {payload.model_dump_json(exclude_none=True)}")

        try:
            op = create_operation(
                cfg=config,
                service="search",
                provider=payload.provider,
                model=payload.model,
            )

            result = await op.run(query=payload.query)

            logger.info(f"search response to {client_ip}: {str(result)[:200]}")
            return {"content": result}

        except (KeyError, ValueError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception(f"search error from {client_ip}: {e}")
            raise HTTPException(status_code=500, detail=f"调用失败: {e}")

    return router
