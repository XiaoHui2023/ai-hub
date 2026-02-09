from core.services import BaseOperation

class BaseAgent(BaseOperation):
    def __init__(
            self,
            freshness:str="noLimit",
            summary:bool=True,
            count:int=50,
            **kwargs,
    ):
        super().__init__(
            **kwargs
        )
        self.freshness = freshness
        self.summary = summary
        self.count = count