from .base_provider import BaseProvider
from pydantic import Field

class BoCha(BaseProvider):
    name = "bocha"
    access_key: str = Field(...,description="访问密钥")
    secret_key: str = Field(...,description="安全密钥")