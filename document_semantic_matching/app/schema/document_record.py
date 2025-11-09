
from pydantic import BaseModel, constr, Field, conint


class SearchRequest(BaseModel):
    search_term: constr(max_length=100) = Field(
        ...,
        example="aromatic, fruity with apple notes",
        description="Search term (max 100 characters)"
    )
    limit: conint(le=5) = Field(
        3,
        example=3,
        description="Number of results to return (max 5)"
    )


class DocumentRecord(BaseModel):
    name: str
    description: str

    class Config:
        extra = "forbid"
