from typing import List

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


class Topic(BaseModel):
    name: str
    confidence: float


class ClassificationResult(BaseModel):
    result: List[Topic]

    @property
    def sorted_result(self) -> List[Topic]:
        return sorted(self.result, key=lambda t: t.confidence, reverse=True)


class PassageRequest(BaseModel):
    passage: str = Field(
        ...,
        max_length=1000,
        min_length=1,
        description="Input passage to classify (max 1000 characters)."
    )
