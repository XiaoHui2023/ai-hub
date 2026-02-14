from abc import ABC, abstractmethod
from typing import Optional, Callable, TypeVar
from urllib.parse import urlencode
from openai import AsyncOpenAI, AuthenticationError, PermissionDeniedError, RateLimitError
from config.providers.key_pool import KeyPool
import httpx
import logging
import requests
import asyncio

logger = logging.getLogger(__name__)
T = TypeVar("T")

class BaseOperation(ABC):
    def __init__(
            self,
            base_url:str,
            path:Optional[str]=None,
            params:Optional[dict]=None,
            api_key:Optional[str]=None,
            key_pool:Optional[KeyPool]=None,
            headers:Optional[dict]=None,
            proxy:Optional[str]=None,
            max_retries:Optional[int]=1,
            stream:bool=False,
            model:Optional[str]=None,
        ):
        """
        base_url: 基础URL
        path: 路径
        params: 参数
        api_key: 密钥
        key_pool: Key 轮询池（优先于 api_key）
        headers: 请求头（由 provider config 计算）
        proxy: 代理
        max_retries: 最大重试次数
        stream: 是否启用流式传输
        model: 模型
        """
        super().__init__()

        self.base_url = base_url
        self.path = path
        self.params = params
        self._key_pool = key_pool
        self.api_key = api_key
        self.headers = headers
        self.proxy = proxy
        self.max_retries = max_retries
        self.stream = stream
        self.model = model

    async def run(self, *args, **kwargs) -> any:
        """运行"""
        body = self.get_body(*args,**kwargs)
        response = await self._request(self.full_url, body)
        return self.parse_response(response)

    def _switch_api_key(self) -> bool:
        """切换到下一个 API key，返回是否成功切换"""
        if not self._key_pool:
            return False
        old_key = self.api_key
        if old_key:
            self._key_pool.report_failure(old_key)
        new_key = self._key_pool.next()
        if new_key and new_key != old_key:
            self.api_key = new_key
            return True
        return False

    async def _call_with_key_retry(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        带 key 自动切换的重试调用

        在遇到认证失败、权限拒绝、速率限制等错误时，
        自动切换到下一个 key 并重试。
        """
        max_attempts = max(len(self._key_pool), 1) if self._key_pool else 1
        last_error = None

        for attempt in range(max_attempts):
            try:
                return await func(*args, **kwargs)
            except (AuthenticationError, PermissionDeniedError, RateLimitError) as e:
                last_error = e
                logger.warning(
                    f"API key 调用失败 (第{attempt + 1}次): {type(e).__name__}: {e}"
                )
                if not self._switch_api_key():
                    break

        raise last_error
    
    def get_body(self, *args, **kwargs) -> dict:
        """请求体"""
        raise NotImplementedError("get_body method not implemented")

    def parse_response(self,response:dict) -> dict:
        """解析响应"""
        raise NotImplementedError("parse_response method not implemented")

    @property
    def full_url(self) -> str:
        """完整请求地址"""
        base = self.base_url.rstrip("/")
        path = self.path.strip("/")
        url = "/".join(p for p in [base, path] if p)
        if self.params:
            url += f"?{urlencode(self.params)}"
        return url

    def _create_openai_client(self) -> AsyncOpenAI:
        """
        创建异步 OpenAI 客户端（使用当前 api_key）
        """
        if self.proxy:
            http_client = httpx.AsyncClient(proxy=self.proxy)
        else:
            http_client = None

        return AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            max_retries=self.max_retries,
            http_client=http_client,
        )

        
    async def _request(self,url:str,data:dict) -> dict:
        """请求"""
        response = await asyncio.to_thread(requests.post,
            url=url,
            json=data,
            headers=self.headers,
        )
        import pprint
        print("url: ", url)
        pprint.pprint(self.headers)
        pprint.pprint(data)
        pprint.pprint(response.json())
        
        # 检查响应状态
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'{response.status_code} {response.text}')

   