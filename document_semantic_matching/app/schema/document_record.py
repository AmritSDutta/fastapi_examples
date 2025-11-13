from typing import List

from pydantic import BaseModel, constr, Field, conint, ConfigDict


class SearchRequest(BaseModel):
    search_term: constr(max_length=100) = Field(
        ...,
        json_schema_extra={"example": "foo"},
        description="Search term (max 100 characters)"
    )
    limit: conint(le=5) = Field(
        3,
        json_schema_extra={"example": 3},
        description="Number of results to return (max 5)"
    )


class DocumentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    description: str


class Topic(BaseModel):
    name: str
    confidence: float


class ClassificationResult(BaseModel):
    result: List[Topic]

    @property
    def sorted_result(self) -> List[Topic]:
        return sorted(self.result, key=lambda t: t.confidence, reverse=True)


class PassageRequest(BaseModel):
    passage: str = 'python is silly ata sometime'
