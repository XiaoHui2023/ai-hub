from typing import List
from pydantic import BaseModel,Field,ConfigDict

class Provider(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: str = Field(...,description="提供商")
    models: List[str] = Field(default_factory=list,description="模型列表")