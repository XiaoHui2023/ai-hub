from core.services import BaseOperation,register
from mem0 import MemoryClient

@register("context", "add", "mem0")
class Mem0(BaseOperation):
    async def run(self, content: str, user_id: str, tag: str) -> dict:
        client = MemoryClient(api_key=self.api_key)
        messages = [
            {"role": "user", "content": content},
        ]
        client.add(messages, user_id=f"{user_id}&{tag}", version="v2")
        return {}