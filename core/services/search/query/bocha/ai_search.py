from .base_agent import BaseAgent
from core.services import register
import json

@register("search", "query", "bocha", "ai-search")
class AISearch(BaseAgent):
    def __init__(
            self,
            answer:bool=False,
            stream:bool=False,
            **kwargs,
    ):
        super().__init__(
            path="ai-search",
            **kwargs
        )
        self.answer = answer
        self.stream = stream

    def get_body(self, query: str) -> dict:
        return {
            "query": query,
            "freshness": self.freshness,
            "answer": self.answer,
            "count": self.count,
            "stream" : self.stream
        }
        
    def parse_response(self,response:dict) -> dict:
        try:
            response = response["messages"]
            response = [json.loads(x["content"]) for x in response if x["content_type"] not in ["video","image"]]
            response = [x["value"] for x in response][0]
            response = [{k: v for k, v in x.items() if k in ["name","summary","datePublished","dateLastCrawled"]} for x in response]
        except:
            raise Exception(f'Failed to parse response: {response}')

        return response