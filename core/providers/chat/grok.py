from .base import Base
from ... import models
from typing import List

class Grok(Base):
    def order_message(self, user: str, assistants: List[str], system: str, memory: List[dict], name: str) -> List['models.Message']:
        '''
        assistant会被当成用户对话，因此应该用SYSTEM
        SYSTEM放在早期会被覆盖掉，因此应该放到最后
        '''
        messages = []
        if memory:
            messages.extend([models.Message(**message) for message in memory])
        if user:
            messages.append(models.Message(role=models.Role.USER, content=user, name=name))
        if assistants:
            messages.extend([models.Message(role=models.Role.SYSTEM, content=assistant) for assistant in assistants])
        if system:
            messages.append(models.Message(role=models.Role.SYSTEM, content=system))

        return messages