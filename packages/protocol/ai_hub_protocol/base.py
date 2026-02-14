from pydantic import BaseModel, ConfigDict, Field


class BaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str = Field(..., description="提供商")
    model: str = Field("", description="模型")
    stream: bool = Field(default=False, description="是否流式")


class BaseResponse(BaseModel):
    content: str | list | dict
