from fastapi import FastAPI, HTTPException, Request
from config import InputModels
from . import core
from .chat import Chat
import uvicorn
import logging

class App:
    def __init__(self,config:InputModels):
        self._config = config
        self.app = FastAPI()

        # 在实例化后注册路由
        self.app.add_api_route("/chat", self.chat, methods=["POST"])


    @property
    def config(self) -> InputModels:
        try:
            return self._config.reload()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"加载配置失败: {e}")

    def run(self):
        uvicorn.run(self.app, host=self.config.ip, port=self.config.port)

    async def chat(self, request: Request, payload: Chat):
        # 获取客户端IP地址
        client_ip = request.client.host
        info = f"chat from IP: {client_ip}\npayload: {payload.text}"
        
        try:
            response = await core.Chat(self.config, payload).run()
            logging.info(f"{info}\nresponse: {response}")
            return response
        except Exception as e:
            logging.exception(f"{info}\nerror: {e}")
            raise


__all__ = [
    "App",
]