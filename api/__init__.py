from fastapi import FastAPI
from config import Config
from .chat import create_chat_router
from .search import create_search_router
import uvicorn
import threading


class App:
    def __init__(self, config: Config):
        self._config = config
        self._app = FastAPI()
        self._app.include_router(create_chat_router(config))
        self._app.include_router(create_search_router(config))
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

    def stop(self, timeout: float = 10):
        """停止服务器，等待端口完全释放"""
        if self._server:
            self._server.should_exit = True
        if self._thread:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                raise RuntimeError("服务器未能在超时时间内停止")
            self._thread = None
            self._server = None

    @property
    def is_running(self) -> bool:
        """服务器是否在运行"""
        return self._thread is not None and self._thread.is_alive()


__all__ = [
    "App",
]