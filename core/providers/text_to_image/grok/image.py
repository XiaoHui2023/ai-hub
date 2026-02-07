from .base import Base
from .... import config

class Image(Base):
    def __init__(
            self,
            **kwargs,
    ):
        super().__init__(
            config=config.grok.Image(),
            **kwargs
        )
