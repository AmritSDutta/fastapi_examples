from pydantic import BaseModel, Field


class ValidatorResponse(BaseModel):
    isStatisticalQuery: bool = False
    confidence: float = 0.0
    reason: str
