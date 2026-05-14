from pydantic import BaseModel

class ReviewCreateRequest(BaseModel):
    product_id: int
    text: str
    rating: int

class ReviewUpdateRequest(BaseModel):
    text: str
    rating: int