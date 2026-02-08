from .liblib import LibLib
from pydantic import BaseModel,Field,ConfigDict
from typing import Optional, Iterator
from .base_provider import BaseProvider

class Providers(BaseModel):
    model_config = ConfigDict(extra="forbid")

    aliyun: Optional[BaseProvider] = Field(default=None)
    grok: Optional[BaseProvider] = Field(default=None)
    openai: Optional[BaseProvider] = Field(default=None)
    bocha: Optional[BaseProvider] = Field(default=None)
    liblib: Optional[LibLib] = Field(default=None)
    qanything: Optional[BaseProvider] = Field(default=None)
    siliconflow: Optional[BaseProvider] = Field(default=None)

    def __iter__(self) -> Iterator[BaseProvider]:
        """遍历所有已配置的 provider"""
        for name in self.__class__.model_fields:
            value = getattr(self, name)
            if value is not None:
                yield value

    @property
    def configured_names(self) -> list[str]:
        """所有已配置的 provider 名称"""
        return [name for name in self.__class__.model_fields if getattr(self, name) is not None]

    def __getitem__(self, name: str) -> BaseProvider:
        """按名称获取 provider：providers["grok"]"""
        if name not in self.__class__.model_fields:
            raise KeyError(f"未知的 provider: '{name}'")
        value = getattr(self, name)
        if value is None:
            raise KeyError(f"provider '{name}' 未配置")
        return value

    def __contains__(self, name: str) -> bool:
        """检查 provider 是否已配置：'grok' in providers"""
        return name in self.__class__.model_fields and getattr(self, name) is not None

    def __len__(self) -> int:
        """已配置的 provider 数量"""
        return sum(1 for _ in self)

__all__ = [
    "Providers",
    "BaseProvider",
]