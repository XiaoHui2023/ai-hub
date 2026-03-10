from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal
from pathlib import Path
import yaml

def find_env_file() -> Path | None:
    """从当前文件所在目录开始，逐层向上查找 .env"""
    start = Path(__file__).resolve().parent
    for parent in [start, *start.parents]:
        env_file = parent / ".env"
        if env_file.is_file():
            return env_file
    return None

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_env_file(),
        env_file_encoding="utf-8",
    )
    # llm
    llm_api_key: str = ""
    """LLM API 密钥"""
    llm_base_url: str = ""
    """LLM 基础 URL"""
    llm_model: str = ""
    """LLM 模型"""

    # bootstrap
    log_dir: str|None = Field(default=None)
    """日志目录"""
    log_level: Literal['info', 'debug', 'warning', 'error', 'critical']='info'
    """日志级别"""
    data_dir: str = "data"
    """数据目录"""
    mcp_path: str = "mcp.json"
    """MCP 路径"""
    memory_file_name: str = "memory.json"
    """记忆文件名"""
    prompt_path: str = "prompt.md"
    """提示词路径"""
    max_context_length: int = 50
    """最大上下文长度"""

    # server
    host: str = "0.0.0.0"
    """主机"""
    port: int = 8000
    """端口"""
    reload: bool = False
    """是否热重载"""
    app_queue_timeout: float = 300.0
    """APP 队列超时时间"""
    app_exec_timeout: float = 120.0
    """APP 执行超时时间"""

settings = Settings()

def load_settings(input_yaml:str|None):
    """加载配置文件"""
    global settings

    if input_yaml:
        with open(input_yaml) as f:
            local_overrides = yaml.safe_load(f)
        for key, value in local_overrides.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

__all__ = [
    "settings",
    "load_settings",
]