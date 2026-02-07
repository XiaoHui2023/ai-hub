from ... import models
from typing import List, AsyncGenerator
from ..base import Base as BaseProvider

class Base(BaseProvider):
 
    async def run(self, user: str, assistants: List[str] = None, system: str = None, memory: List[dict] = None, name: str = None, delimiter: str = None) -> AsyncGenerator[str, None]:
        '''
        简单聊天

        Args:
            name: 用户名称
            user: 用户消息
            assistants: 助手消息列表
            system: 系统消息
            memory: 会话记忆
            delimiter: 分隔符，如果提供则按分隔符分块返回，否则累积所有内容后一次性返回

        Yields:
            str: 响应文本块
        '''
        messages = self.order_message(user, assistants, system, memory, name)

        messages = [self.reform_message(message) for message in messages]

        async for chunk in self.completion(messages, delimiter):
            yield chunk

    def order_message(self, user: str, assistants: List[str], system: str, memory: List[dict], name: str) -> List[models.Message]:
        '''
        排序消息

        Args:
            user: 用户消息
            assistants: 助手消息列表
            system: 系统消息
            memory: 会话记忆
            name: 用户名称
        '''
        messages = []
        if memory:
            messages.extend([models.Message(**message) for message in memory])
        if system:
            messages.append(models.Message(role=models.Role.SYSTEM, content=[models.Text(text=system)]))
        if user:
            messages.append(models.Message(role=models.Role.USER, content=[models.Text(text=user)], name=name))
        if assistants:
            messages.extend([models.Message(role=models.Role.ASSISTANT, content=[models.Text(text=assistant)]) for assistant in assistants])

        return messages

    def reform_message(self, message: models.Message) -> dict:
        '''
        重构消息
        '''
        return message.json