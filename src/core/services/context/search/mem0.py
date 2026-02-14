from core.services import BaseOperation,register
from mem0 import MemoryClient

@register("context", "search", "mem0")
class Mem0(BaseOperation):
    async def run(self, query: str, user_id: str, tag: str) -> dict:
        client = MemoryClient(api_key=self.api_key)
        filters = {
        "OR":[
            {
                "user_id":f"{user_id}&{tag}"
            }
        ]
        }
        response = client.search(query, version="v2", filters=filters)
        result = '\n'.join([item["memory"] for item in response["results"]])
        return result