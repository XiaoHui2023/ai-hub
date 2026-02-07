from .base import Base
from .... import config

class DeepSeekV3(Base):
    def __init__(
            self,
            **kwargs,
    ):
        super().__init__(
            config=config.siliconflow.DeepSeekV3(),
            **kwargs
        )
