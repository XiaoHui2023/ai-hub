from fastapi import FastAPI
from config import Config
from .chat import create_chat_router
import uvicorn
import threading


class App:
    def __init__(self, config: Config):
        self._config = config
        self._app = FastAPI()
        self._app.include_router(create_chat_router(config))
        self._server: uvicorn.Server | None = None
        self._thread: threading.Thread | None = None

    def start(self):
        """在后台线程中启动服务器"""
        self._server = uvicorn.Server(
            uvicorn.Config(
                self._app,
                host=self._config.ip,
                port=self._config.port,
                log_config=None,
            )
        )
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()

    def stop(self):
        """停止服务器"""
        if self._server:
            self._server.should_exit = True
        if self._thread:
            self._thread.join(timeout=5)

    @property
    def is_running(self) -> bool:
        """服务器是否在运行"""
        return self._thread is not None and self._thread.is_alive()


__all__ = [
    "App",
]