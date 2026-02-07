from .base import Base
from ... import models

class OpenAI(Base):
    def reform_message(self, message: models.Message) -> dict:
        '''
        重构消息
        '''
        message = super().reform_message(message)
        role = message['role']
        if role == "system":
            role = "developer"
        message['role'] = role

        return message