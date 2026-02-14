from typing import List
from pydantic import BaseModel,Field,ConfigDict

class Provider(BaseModel):
    model_config = ConfigDict(extra="forbid")
    models: List[str] = Field(default_factory=list,description="模型列表")
    stream: bool = Field(default=True,description="是否支持流式传输")