from ..base import BaseRequest, BaseResponse


class Request(BaseRequest):
    query: str


class Response(BaseResponse):
    content: str | list | dict
