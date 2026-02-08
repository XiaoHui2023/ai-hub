from .base_agent import BaseAgent

class WebSearch(BaseAgent):
    def __init__(
            self,
            **kwargs,
    ):
        super().__init__(
            endpoint="web-search",
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

            response = [{k:v for k,v in value.items() if k in ["name","snippet","summary","datePublished","dateLastCrawled"]} for value in response]
        except:
            raise Exception(f'Failed to parse response: {response}')

        return response

