from typing import Optional, Iterator
from pydantic import BaseModel,Field,ConfigDict
from .provider import Provider

class Service(BaseModel):
    model_config = ConfigDict(extra="forbid")
    aliyun: Optional[Provider] = Field(default=None,description="阿里云")
    grok: Optional[Provider] = Field(default=None,description="Grok")
    openai: Optional[Provider] = Field(default=None,description="OpenAI")
    bocha: Optional[Provider] = Field(default=None,description="博查")
    liblib: Optional[Provider] = Field(default=None,description="Liblib")
    qanything: Optional[Provider] = Field(default=None,description="QAnything")
    siliconflow: Optional[Provider] = Field(default=None,description="硅基流动")

    def __iter__(self) -> Iterator[tuple[str, Provider]]:
        """遍历已配置的 (provider名, Provider)"""
        for name in self.__class__.model_fields:
            value = getattr(self, name)
            if value is not None:
                yield name, value

    @property
    def configured_names(self) -> list[str]:
        """该服务下已配置的 provider 名称"""
        return [name for name in self.__class__.model_fields if getattr(self, name) is not None]

    def __getitem__(self, name: str) -> Provider:
        """按 provider 名获取：service["aliyun"]"""
        if name not in self.__class__.model_fields:
            raise KeyError(f"未知的 provider: '{name}'")
        value = getattr(self, name)
        if value is None:
            raise KeyError(f"provider '{name}' 未配置")
        return value

    def __contains__(self, name: str) -> bool:
        return name in self.__class__.model_fields and getattr(self, name) is not None