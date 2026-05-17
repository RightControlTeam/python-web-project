import jwt
from jwt import decode, PyJWTError
from config import settings
from pydantic import BaseModel

class TokenClaims(BaseModel):
    sub: str
    exp: int

def decode_jwt(token: str) -> TokenClaims | None:
    try:
        claims = decode(
            token,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM,
        )
        return TokenClaims(**claims)
    except PyJWTError:
        return None

def create_jwt(claims: TokenClaims | None) -> str | None:
    if not claims:
        return None
    return jwt.encode(
        claims.model_dump(),
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM
    )
