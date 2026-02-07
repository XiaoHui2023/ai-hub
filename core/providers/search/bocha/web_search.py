from typing import Dict,Any
from .base import Base

class WebSearch(Base):
    def __init__(
            self,
            **kwargs,
    ):
        super().__init__(
            model="web-search",
            **kwargs
        )
    
    async def run(self,query:str,freshness:str="noLimit",summary:bool=True,count:int=50,page:int=1) -> Dict[str,Any]:
        '''
        网络搜索

        query: 搜索关键词
        freshness: 新鲜度
        summary: 摘要
        count: 数量
        page: 页码
        '''
        data = {
            "query": query,
            "freshness": freshness,
            "summary": summary,
            "count": count,
            "page" : page
        }
        
        rt = await super().run(data)

        try:
            rt = rt["data"]["webPages"]["value"]

            rt = [{k:v for k,v in value.items() if k in ["name","snippet","summary","datePublished","dateLastCrawled"]} for value in rt]
        except:
            raise Exception(f'Failed to parse response: {rt}')

        return rt

