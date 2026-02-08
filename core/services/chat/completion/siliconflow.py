from . import BaseProvider
from core.services import register

@register("chat", "siliconflow")
class Siliconflow(BaseProvider):
    pass