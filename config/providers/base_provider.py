from typing import Optional, List
from pydantic import BaseModel,Field,ConfigDict,PrivateAttr
from .key_pool import KeyPool

class BaseProvider(BaseModel):
    model_config = ConfigDict(extra="forbid")
    base_url: str = Field(...,description="基础URL")
    api_keys: List[str] = Field(default_factory=list,description="API密钥列表")
    proxy: Optional[str] = Field(default=None,description="代理")
    use_proxy: bool = Field(default=False,description="是否使用代理")

    _key_pool: Optional[KeyPool] = PrivateAttr(default=None)

    @property
    def key_pool(self) -> KeyPool:
        """延迟创建的 Key 轮询池"""
        if self._key_pool is None:
            self._key_pool = KeyPool(self.api_keys)
        return self._key_pool

    @property
    def param(self) -> dict:
        """参数"""
        return {}

    @property
    def is_valid(self) -> bool:
        """是否有效"""
        return self.is_key_valid and bool(self.base_url)

    @property
    def is_key_valid(self) -> bool:
        """是否API密钥有效"""
        return bool(self.api_keys)