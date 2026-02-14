from ..base import Base
from typing import AsyncGenerator

class Base(Base):
    async def generate(self, prompt: str, **kwargs) -> str:
        '''
        生成图片
        '''
        pass

    async def run(
            self, 
            prompt: str, 
            image_height:int, 
            image_width:int,
            image_number:int,
            **kwargs,
    ) -> AsyncGenerator[str, None]:
        '''
        生成图片
        '''
        pass