from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(
            self,
            base_url:str,
            endpoint:str,
            freshness:str="noLimit",
            summary:bool=True,
            count:int=2,
    ):
        self.base_url = base_url
        self.endpoint = endpoint
        self.freshness = freshness
        self.summary = summary
        self.count = count
    
    @property
    def full_url(self) -> str:
        """完整的URL"""
        return f'{self.base_url.rstrip("/")}/{self.endpoint.strip("/")}'
    
    @abstractmethod
    def get_body(self, query: str) -> dict:
        """请求体"""
        pass

    @abstractmethod
    def parse_response(self,response:dict) -> dict:
        """解析响应"""
        pass