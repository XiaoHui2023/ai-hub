from . import BaseProvider
from core.services import register

@register("chat", "completion", "siliconflow")
class Siliconflow(BaseProvider):
    pass