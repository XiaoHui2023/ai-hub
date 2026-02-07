from .aliyun import Aliyun
from .grok import Grok
from .openai import Openai
from .bocha import BoCha
from .liblib import Liblib
from .qanything import QAnything
from .siliconflow import Siliconflow
from pydantic import BaseModel,Field,ConfigDict,field_validator
from typing import List
from .base_provider import BaseProvider

REGRISTRIES: List[type[BaseProvider]] = []

def parse_provider(data: dict) -> BaseProvider:
    """根据 name 自动选择正确的类"""
    name = data.get("name")
    cls = _REGISTRY.get(name, BaseProvider)  # 没注册的一律用 BaseProvider
    return cls(**data)

class Providers(BaseModel):
    model_config = ConfigDict(extra="forbid")
    aliyun: Aliyun = Field(default=None)
    grok: Grok = Field(default=None)
    openai: Openai = Field(default=None)
    bocha: BoCha = Field(default=None)
    liblib: Liblib = Field(default=None)
    qanything: QAnything = Field(default=None)
    siliconflow: Siliconflow = Field(default=None)

    @field_validator("items", mode="before")
    @classmethod
    def _parse(cls, v):
        return [parse_provider(item) if isinstance(item, dict) else item for item in v]


    @property
    def providers(self) -> List[BaseProvider]:
        """获取所有提供商"""
        return [provider for provider in self.__class__.model_fields.values() if provider is not None]

    @property
    def valid_providers(self) -> List[BaseProvider]:
        """获取所有有效的提供商"""
        return [provider for provider in self.providers if provider.is_valid]