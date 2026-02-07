from .base import Base
from .... import config

class DeepSeekVl2(Base):
    def __init__(
            self,
            **kwargs,
    ):
        super().__init__(
            config=config.siliconflow.DeepSeekVl2(),
            **kwargs
        )
