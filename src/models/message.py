from pydantic import BaseModel
from typing import Literal, Optional

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    name: Optional[str] = None