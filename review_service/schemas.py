from pydantic import BaseModel, Field

class ReviewCreateRequest(BaseModel):
    product_id: int
    text: str = Field(..., min_length=5, max_length=1000)
    rating: int = Field(..., ge=1, le=5)

class ReviewUpdateRequest(BaseModel):
    text: str
    rating: int
