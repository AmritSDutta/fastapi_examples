from pydantic import BaseModel, conlist, Field


class PredictRequest(BaseModel):
    features: conlist(float, min_length=4, max_length=4) = Field(...,
                                                                 title='Feature Vector',
                                                                 description='Exactly 4 numerical data used.',
                                                                 examples=[5.1, 3.5, 1.4, 0.2])


class PredictResponse(BaseModel):
    prediction: int
