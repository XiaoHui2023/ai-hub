from . import BaseProvider
from core.services import register

@register("chat", "aliyun")
class Aliyun(BaseProvider):
    pass