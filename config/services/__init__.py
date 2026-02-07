from pydantic import BaseModel,Field,ConfigDict

class Services(BaseModel):
    model_config = ConfigDict(extra="forbid")