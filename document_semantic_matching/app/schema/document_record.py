
from pydantic import BaseModel


class DocumentRecord(BaseModel):
    name: str
    description: str

    class Config:
        extra = "forbid"
