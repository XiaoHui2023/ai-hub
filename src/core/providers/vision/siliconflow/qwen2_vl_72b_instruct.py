from .base import Base
from .... import config

class Qwen2Vl72bInstruct(Base):
    def __init__(
            self,
            **kwargs,
    ):
        super().__init__(
            config=config.siliconflow.Qwen2Vl72bInstruct(),
            **kwargs
        )
