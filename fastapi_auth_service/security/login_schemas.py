from pydantic import BaseModel

class LoginRequesst(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenClaims(BaseModel):
    sub: str
    exp: int
