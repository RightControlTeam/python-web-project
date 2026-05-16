from datetime import datetime, timedelta, UTC
from jwt import encode, decode, PyJWTError
from fastapi import HTTPException

from shared.config import settings
from .login_schemas import TokenClaims, LoginResponse


def generate_login_response(user_id: int) -> LoginResponse:
    exp_time_delta: timedelta = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    exp_time: datetime = datetime.now(UTC) + exp_time_delta
    exp_time_int: int = int(exp_time.timestamp())

    claims = TokenClaims(
        sub = str(user_id),
        exp = exp_time_int,
    )

    token: str = encode(
        claims.model_dump(),
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return LoginResponse(
        access_token= token,
        token_type = "Bearer",
        expires_in = settings.JWT_EXPIRE_MINUTES * 60,
    )

def decode_token(token: str) -> TokenClaims:
    try:
        claims: dict = decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=settings.JWT_ALGORITHM
        )
        return TokenClaims(**claims)
    except PyJWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}",
        )