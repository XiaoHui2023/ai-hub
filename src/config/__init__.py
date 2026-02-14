from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from .providers import *
from .services import *

class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")
    providers: Providers = Field(default_factory=Providers)
    services: Services = Field(default_factory=Services)
    ip: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    log: Optional[str] = Field(default=None)
    proxy: Optional[str] = Field(default=None,description="代理")

__all__ = [
    "Config",
]