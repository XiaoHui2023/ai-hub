from .base_agent import BaseAgent
from core.services import register

@register("search", "query", "bocha", "web-search")
class WebSearch(BaseAgent):
    def __init__(
            self,
            **kwargs,
    ):
        super().__init__(
            path="web-search",
            **kwargs
        )
    
    def get_body(self, query: str) -> dict:
        return {
            "query": query,
            "freshness": self.freshness,
            "summary": self.summary,
            "count": self.count,
        }
        
    def parse_response(self,response:dict) -> dict:
        try:
            response = response["data"]["webPages"]["value"]

            response = [{k:v for k,v in value.items() if k in ["name","summary","datePublished","dateLastCrawled"]} for value in response]
        except:
            raise Exception(f'Failed to parse response: {response}')

        return response

