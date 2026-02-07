from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from . import providers

class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")
    providers: List[providers.Providers] = Field(default_factory=list)
    ip: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    log: Optional[str] = Field(default=None)
    proxy: Optional[str] = Field(default=None,description="代理")

__all__ = [
    "providers",
    "Config",
]