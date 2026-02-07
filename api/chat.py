from typing import List, Optional
from pydantic import BaseModel
import json

class Chat(BaseModel):
    provider: str = "default"
    model: str = "default"
    system: Optional[str] = None
    assistants: Optional[List[str]] = None
    memory: Optional[List[dict]] = None
    user: Optional[str] = None
    name: Optional[str] = None
    temperature: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    top_p: Optional[float] = None
    
    @property
    def json(self) -> dict:
        return {
            "provider": self.provider,
            "model": self.model,
        }

    @property
    def text(self) -> str:
        return json.dumps({k:v for k,v in self.json.items() if v not in [None,'default',[]]},indent=4,ensure_ascii=False)