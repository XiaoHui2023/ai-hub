from ..base import Base
import logging
import asyncio
from typing import AsyncGenerator

class Base(Base):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    async def generate(self,prompt:str) -> str:
        '''
        生成图片

        prompt: 提示词
        '''
        client = self.create_client()
        try:
            response = await asyncio.to_thread(client.images.generate,
                model=self.config.model,
                prompt=prompt,
                response_format="b64_json"
            )

            return response.data[0].b64_json
        
        except Exception as e:
            logging.exception(f"image.generate 异常: {e}\nprompt = {prompt}")
            raise e
    
    async def run(self,prompt:str) -> AsyncGenerator[str,None]:
        '''
        生成图片

        prompt: 提示词
        '''

        rt = await self.generate(prompt)

        yield rt