from pydantic import BaseModel, Field
from typing import Literal

class Config(BaseModel):
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