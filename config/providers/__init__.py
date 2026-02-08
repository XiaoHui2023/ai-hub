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

    @property
    def providers(self) -> dict[str, Optional[BaseProvider]]:
        """所有声明的 provider"""
        return {name: getattr(self, name) for name in self.__class__.model_fields}

    @property
    def configured_providers(self) -> dict[str, Optional[BaseProvider]]:
        """所有已配置的 provider"""
        return {k: v for k, v in self.providers.items() if v is not None and v.is_valid}

    def __iter__(self) -> Iterator[BaseProvider]:
        """遍历所有已配置的 provider"""
        for provider in self.configured_providers.values():
            yield provider

    @property
    def configured_names(self) -> list[str]:
        """所有已配置的 provider 名称"""
        return list(self.configured_providers.keys())

    def __getitem__(self, name: str) -> BaseProvider:
        """按名称获取 provider：providers["grok"]"""
        if name not in self.configured_providers:
            raise KeyError(f"未知的 provider: '{name}'")
        return self.configured_providers[name]

    def __contains__(self, name: str) -> bool:
        """检查 provider 是否已配置：'grok' in providers"""
        return name in self.configured_providers

    def __len__(self) -> int:
        """已配置的 provider 数量"""
        return sum(1 for _ in self)

__all__ = [
    "Providers",
    "BaseProvider",
]