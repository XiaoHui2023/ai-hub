from typing import Optional,List,AsyncGenerator
import logging
import json
import requests
from abc import abstractmethod
from openai import OpenAI
import httpx

class BaseService:
    def __init__(
        self,
        base_url:str,
        path:str,
        api_key:str,
        proxy:Optional[str]=None,
        temperature:Optional[float]=None,
        frequency_penalty:Optional[float]=None,
        presence_penalty:Optional[float]=None,
        top_p:Optional[float]=None,
        max_retries:Optional[int]=1,
    ):
        '''
        base_url: 基础URL
        path: 路径
        api_key: 密钥
        proxy: 代理
        temperature: 温度
        frequency_penalty: 频率惩罚
        presence_penalty: 存在惩罚
        top_p: Top-P
        max_retries: 最大重试次数
        '''
        super().__init__()

        self.base_url = base_url
        self.path = path
        self.api_key = api_key
        self.proxy = proxy
        self.temperature = temperature
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.top_p = top_p
        self.max_retries = max_retries

    @abstractmethod
    async def run(self,*args,**kwargs) -> any:
        '''
        运行
        '''
        pass

    @property
    def url(self) -> str:
        '''地址'''
        base = self.base_url.rstrip("/")
        path = self.path.strip("/")
        parts = [base, path]
        return "/".join(p for p in parts if p)

    def create_openai_client(self) -> OpenAI:
        '''
        创建OpenAI客户端
        '''
        if self.proxy:
            proxy_client = httpx.Client(
                proxy=self.proxy
            )
        else:
            proxy_client = None

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.url,
            max_retries=self.max_retries,
            http_client=proxy_client
        )

        return client

    async def _completion_openai(self, messages: List[dict]) -> AsyncGenerator[str, None]:
        '''
        使用OpenAI API完成聊天补全，以异步生成器方式返回

        Args:
            messages: 消息列表

        Yields:
            str: 响应文本块
        '''
        args = {k:v for k,v in {
            "model": self.model,
            "temperature": self.temperature,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "top_p": self.top_p,
        }.items() if v is not None}

        if args:
            info = ''.join([f"\n{k}: {v}" for k,v in args.items()])
        else:
            info = ""

        logging.info(f"OpenAI.completion: {info}\nmessage: {json.dumps(messages,indent=4,ensure_ascii=False)}")

        client = self.create_openai_client()
        stream = client.chat.completions.create(
            messages=messages,
            stream=True,
            **args
        )
        
        buffer = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                buffer += content

        if buffer:
            yield buffer

    def _completion_curl(self,messages:List[dict]) -> str:
        '''
        使用CURL完成聊天补全

        messages: 消息列表
        '''
        api_key = self.api_key
        url = f"{self.base_url}/chat/completions"
        model = self.model
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "messages": messages,
            "model": model,
            "stream": True,
        }

        try:
            response = requests.post(url, headers=headers, json=data, stream=True)

            full_content = ""
            for line in response.iter_lines():
                if line:
                    try:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            line = line[6:]  # 移除 'data: ' 前缀
                            if line.strip() == '[DONE]':
                                break
                            chunk = json.loads(line)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_content += content
                    except Exception as e:
                        logging.exception(f"\n处理流数据时出错: {e}")
                        raise Exception(f"处理流数据时出错")

            rt = full_content
        except Exception as e:
            logging.exception(f"Chat.completion 使用CURL完成聊天补全失败: {e}")
            raise Exception(f"Chat.completion 使用CURL完成聊天补全失败")
        
        return rt