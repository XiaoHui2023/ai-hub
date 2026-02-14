from .. import Message,Role
from ... import models as Data
from typing import List, AsyncGenerator
from ..base import Base

class Base(Base):
    async def run(self, image_path: str,query:str) -> AsyncGenerator[str, None]:
        '''
        视觉理解

        Args:
            image_path: 图片路径
            query: 查询内容

        Yields:
            str: 响应文本块
        '''
        messages = self.order_message(image_path,query)

        async for chunk in self.completion(messages):
            yield chunk

    def order_message(self, image_path: str,query:str) -> List[Message]:
        '''
        排序消息

        Args:
            image_path: 图片路径
            query: 查询内容
        '''
        messages = []
        messages.append(Message(role=Role.USER, content=[Data.Image(file_path=image_path)]))
        messages.append(Message(role=Role.USER, content=[Data.Text(text=query)]))

        return messages
