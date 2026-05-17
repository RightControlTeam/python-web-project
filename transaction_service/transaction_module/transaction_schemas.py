from pydantic import BaseModel

class CreateTransactionRequest(BaseModel):
    user_id: int
    order_id: int
    cost: int