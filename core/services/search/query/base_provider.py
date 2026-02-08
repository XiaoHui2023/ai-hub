from typing import AsyncGenerator
from core.services import BaseOperation

class BaseProvider(BaseOperation):
    async def run(self, **kwargs) -> AsyncGenerator[str, None]:
        pass