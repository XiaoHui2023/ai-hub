from .base import Base
from .... import config

class QwenVlPlus(Base):
    def __init__(
            self,
            **kwargs,
    ):
        super().__init__(
            config=config.aliyun.QwenVlPlus(),
            **kwargs
        )
