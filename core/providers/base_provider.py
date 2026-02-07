from abc import abstractmethod
from typing import List,AsyncGenerator,Dict,Tuple,Awaitable,Optional
import logging
import requests
import json
import config

class BaseProvider:
    def __init__(
            self,
            cfg: config.Provider,
        ):
        '''
        cfg: 配置
        '''
        super().__init__()

        self.cfg = cfg


    @abstractmethod
    async def run(self,*args,**kwargs) -> any:
        '''
        运行
        '''
        pass


    async def completion(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        '''
        完成聊天补全

        Args:
            messages: 消息列表

        Yields:
            str: 响应文本块
        '''
        async for chunk in self._completion_openai(messages):
            yield chunk
