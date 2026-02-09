from . import BaseProvider
from core.services import register

@register("chat", "completion", "aliyun")
class Aliyun(BaseProvider):
    pass