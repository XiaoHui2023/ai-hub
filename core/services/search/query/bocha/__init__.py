from core.services.search.query import BaseProvider
from core.services import register
from .web_search import WebSearch
from .ai_search import AISearch
from .base_agent import BaseAgent

@register("search", "bocha")
class Bocha(BaseProvider):
    def __init__(
            self,
            **kwargs,
    ):
        super().__init__(
            **kwargs
        )
        self.metadata = {k:v for k,v in kwargs.items() if k in ["base_url", "endpoint"]}
        self._agents: dict[str, BaseAgent] = {
            "web-search": WebSearch(**self.metadata),
            "ai-search": AISearch(**self.metadata),
        }

    async def run(self, query: str):
        agent = self._agents.get(self.model)
        if agent is None:
            raise ValueError(f"不支持的模型: '{self.model}'，支持的模型: {list(self._agents.keys())}")

        body = agent.get_body(query)
        response = await self._request(agent.full_url, body)
        return agent.parse_response(response)