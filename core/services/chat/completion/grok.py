from . import BaseProvider
from core.services import register
from models import Message
from typing import List

@register("chat", "grok")
class Grok(BaseProvider):
    def _normalize_messages(self, messages: List[Message]) -> List[Message]:
        """
        assistant会被当成用户对话，因此应该用SYSTEM
        SYSTEM放在早期会被覆盖掉，因此应该放到最后
        """
        # assistant → system
        normalized = []
        for msg in messages:
            if msg.role == "assistant":
                normalized.append(Message(role="system", content=msg.content, name=msg.name))
            else:
                normalized.append(msg)

        # system 消息移到最后
        non_system = [m for m in normalized if m.role != "system"]
        system = [m for m in normalized if m.role == "system"]

        return non_system + system