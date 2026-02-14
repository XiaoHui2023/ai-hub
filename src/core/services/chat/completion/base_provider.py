from models import Message
from typing import List, AsyncGenerator
from core.services import BaseOperation

class BaseProvider(BaseOperation):
    async def run(self, messages: List[Message], **kwargs) -> AsyncGenerator[str, None]:
        messages = self._normalize_messages(messages)

        async for chunk in self._openai_completion(**{"messages": messages} | kwargs):
            yield chunk

    def _normalize_messages(self, messages: List[Message]) -> List[Message]:
        """规范消息"""
        return messages

    async def _openai_completion(self, **kwargs) -> AsyncGenerator[str, None]:
        """使用OpenAI API完成聊天补全，以异步生成器方式返回"""
        kwargs = {k:v for k,v in kwargs.items() if v is not None and v != ""}

        async def _do_call():
            client = self._create_openai_client()
            return await client.chat.completions.create(stream=self.stream, **kwargs)

        response = await self._call_with_key_retry(_do_call)

        if self.stream:
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        else:
            if response.choices and response.choices[0].message.content:
                yield response.choices[0].message.content