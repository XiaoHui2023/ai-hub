from .base_provider import BaseProvider
import time
import uuid
import hmac
import base64
from hashlib import sha1

class Liblib(BaseProvider):
    @property
    def param(self) -> str:
        # API访问密钥
        access_key = self.access_key
        secret_key = self.secret_key
        uri = self.api

        # 当前毫秒时间戳
        timestamp = str(int(time.time() * 1000))
        # 随机字符串
        signature_nonce= str(uuid.uuid4())
        # 拼接请求数据
        content = '&'.join((uri, timestamp, signature_nonce))
        
        # 生成签名
        digest = hmac.new(secret_key.encode(), content.encode(), sha1).digest()
        # 移除为了补全base64位数而填充的尾部等号
        sign = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()

        return f"?AccessKey={access_key}&Signature={sign}&Timestamp={timestamp}&SignatureNonce={signature_nonce}"
