from typing import List, Literal, Optional

from pydantic import BaseModel

from ..base import BaseRequest, BaseResponse


class Message(BaseModel):
    """聊天消息模型"""

    role: Literal["user", "assistant", "system"]
    content: str
    name: Optional[str] = None


class Request(BaseRequest):
    messages: List[Message]
    temperature: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    top_p: Optional[float] = None


class Response(BaseResponse):
    content: str
