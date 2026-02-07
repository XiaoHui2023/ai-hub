from .... import config
from ..base import Base
import requests
import asyncio

class Base(Base):
    def __init__(
            self,
            model: str,
            **kwargs,
    ):
        super().__init__(
            config=config.bocha.BoCha(model=model),
            **kwargs
        )
    
    async def run(self,data) -> dict:
        url = f'{self.config.base_url}/{self.config.model}'
        
        response = await asyncio.to_thread(requests.post,
            url=url,
            json=data,
            headers={
                'Authorization': f'Bearer {self.config.api_key}',
                'Content-Type': 'application/json'
            }
        )
        
        # 检查响应状态
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'{response.status_code} {response.text}')

   