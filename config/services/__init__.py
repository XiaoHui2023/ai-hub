from pydantic import BaseModel,Field,ConfigDict
from .service import Service
from typing import Optional, Iterator

class Services(BaseModel):
    model_config = ConfigDict(extra="forbid")
    chat: Optional[Service] = Field(default=None,description="对话服务")
    text_to_image: Optional[Service] = Field(default=None,description="文生图服务")
    context: Optional[Service] = Field(default=None,description="上下文服务")
    vision: Optional[Service] = Field(default=None,description="视觉理解服务")
    web_search: Optional[Service] = Field(default=None,description="网络搜索服务")

    def __iter__(self) -> Iterator[tuple[str, Service]]:
        """遍历已配置的 (服务名, Service)"""
        for name in self.__class__.model_fields:
            value = getattr(self, name)
            if value is not None:
                yield name, value

    def __getitem__(self, name: str) -> Service:
        """按名称获取：services["chat"]"""
        if name not in self.__class__.model_fields:
            raise KeyError(f"未知的服务: '{name}'")
        value = getattr(self, name)
        if value is None:
            raise KeyError(f"服务 '{name}' 未配置")
        return value

    def __contains__(self, name: str) -> bool:
        return name in self.__class__.model_fields and getattr(self, name) is not None


__all__ = [
    "Services",
    "Service",
]