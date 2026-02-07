from typing import Optional, List
from pydantic import BaseModel,Field,ConfigDict

class BaseProvider(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(...,description="名称")
    base_url: str = Field(...,description="基础URL")
    api_keys: List[str] = Field(default_factory=list,description="API密钥列表")
    proxy: Optional[str] = Field(default=None,description="代理")
    use_proxy: bool = Field(default=False,description="是否使用代理")

    @property
    def is_valid(self) -> bool:
        return bool(self.api_keys) and bool(self.base_url)