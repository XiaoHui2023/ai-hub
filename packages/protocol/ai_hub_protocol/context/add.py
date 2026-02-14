from ..base import BaseRequest, BaseResponse


class Request(BaseRequest):
    content: str
    user_id: str
    tag: str


class Response(BaseResponse):
    content: str | list | dict
