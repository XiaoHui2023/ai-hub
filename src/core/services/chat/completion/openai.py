from . import BaseProvider
from models import Message
from typing import List
from core.services import register

@register("chat", "completion", "openai")
class OpenAI(BaseProvider):
    def _normalize_messages(self, messages: List[Message]) -> List[Message]:
        """OpenAI 已将 system 角色更名为 developer"""
        normalized = []
        for msg in messages:
            if msg.role == "system":
                normalized.append(Message(role="developer", content=msg.content, name=msg.name))
            else:
                normalized.append(msg)
        return normalized