from pydantic import BaseModel


class CoreModel(BaseModel):
    class Config:
        extra = "forbid"
