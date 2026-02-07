from ... import config
from typing import List
from ..base import Base
import json
import requests
import logging

class QAnything(Base):
    def __init__(
            self,
            **kwargs,
    ):
        super().__init__(
            config=config.qanything.QAnything4oMini(),
            **kwargs
        )

    @property
    def headers(self) -> dict:
        '''
        请求头
        '''
        return {
            "Authorization": self.config.api_key,
            "Content-Type": "application/json",
        }

    async def get_kb_list(self) -> List[dict]:
        '''
        获取知识库列表
        '''
        url = f"{self.config.base_url}/kb_list"
        response = requests.get(url, headers=self.headers)
        json_data = response.json()
        result = json_data['result']
        kb_list = [{'id':item['kbId'],'name':item['kbName']} for item in result]
        return kb_list
    
    async def get_kb_id(self,name:str) -> str:
        '''
        获取知识库ID
        '''
        kb_list = await self.get_kb_list()
        kb_id = next((item['id'] for item in kb_list if item['name'] == name), None)
        return kb_id
    
    async def chat_stream(self,kbId:str,query:str) -> str:
        '''
        聊天流式接口
        '''
        url = f"{self.config.base_url}/chat_stream"

        data = {
            "question": query,
            "kbIds": [kbId],
            "prompt": "",
            "history": [],
            "model": self.config.model,
            "maxToken": "1024",
            "hybridSearch": "false",
            "networking": "false",
            "sourceNeeded": "false"
        }
        response = requests.post(url, headers=self.headers, json=data,stream=True)
        return self.stream_to_string(response)
    

    async def deduplicate(self,content:str) -> str:
        '''
        去重
        '''
        l = len(content)
        left = content[:l//2]
        right = content[l//2:]
        if left == right:
            return left
        else:
            return content
    
    async def execute(self,knowledge_base_name:str,query:str) -> str:
        '''
        执行
        '''
        kbId = await self.get_kb_id(knowledge_base_name)
        if not kbId:
            logging.error(f"知识库{knowledge_base_name}不存在")
            return ""
        response = await self.chat_stream(kbId,query)
        response = await self.deduplicate(response)
        return response
 
    async def run(self,*args,**kwargs) -> str:
        '''
        运行
        '''
        return await self.run_async(self.execute,*args,**kwargs)