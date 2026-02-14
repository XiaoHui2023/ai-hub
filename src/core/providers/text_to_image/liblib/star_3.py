from .... import config
from .base import Base

class Star3(Base):
    def __init__(
            self,
            **kwargs,
    ):
        super().__init__(
            config=config.liblib.Star3TextToImage(),
            **kwargs
        )
