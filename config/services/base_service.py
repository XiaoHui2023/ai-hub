from typing import List
from pydantic import BaseModel,Field,ConfigDict

class BaseService(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(...,description="名称")