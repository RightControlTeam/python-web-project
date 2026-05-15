from pydantic import BaseModel

class UserRequest(BaseModel):
    username: str
    password: str

class UserUpdateRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

class OrderCancelNotification(BaseModel):
    username: str
    order_id: int

class CartNotification(BaseModel):
    username: str
    product_name: str