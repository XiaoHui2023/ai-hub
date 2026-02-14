from abc import ABC, abstractmethod
from fastapi import APIRouter, HTTPException, Request
from config import Config
from ai_hub_protocol import BaseRequest
from factory import create_operation
import logging

logger = logging.getLogger(__name__)


class BaseRouter(ABC):
    """API 路由基类，封装公共的请求处理流程"""
    service: str
    operation: str

    def __init__(self, config: Config):
        self.config = config
        self.router = APIRouter()
        self.path = f"/{self.service}/{self.operation}"
        self._setup_routes()

    @abstractmethod
    def _setup_routes(self):
        """子类注册具体路由"""
        pass

    def _create_op(self, payload: BaseRequest, **kwargs):
        """根据 payload 创建 operation 实例"""
        return create_operation(
            cfg=self.config,
            service=self.service,
            operation=self.operation,
            provider=payload.provider,
            model=payload.model,
            stream=payload.stream,
            **kwargs,
        )

    async def _handle(self, request: Request, payload: BaseRequest, callback):
        """
        通用请求处理：日志 + 创建 op + 错误处理

        callback: async (op, client_ip) -> Response
        """
        client_ip = request.client.host
        logger.info(f"{self.service} from {client_ip}: {payload.model_dump_json(exclude_none=True)}")

        try:
            op = self._create_op(payload)
            return await callback(op, client_ip)
        except (KeyError, ValueError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception(f"{self.service} error from {client_ip}: {e}")
            raise HTTPException(status_code=500, detail=f"调用失败: {e}")
