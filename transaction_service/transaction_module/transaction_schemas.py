from pydantic import BaseModel

class CreateTransactionRequest(BaseModel):
    order_id: int
    cost: int

class TransactionResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    cost: int
    is_success: bool