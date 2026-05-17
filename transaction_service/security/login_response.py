from datetime import datetime, timedelta, UTC

from shared.config import settings
from .login_schemas import LoginResponse
from shared.jwt_module import create_jwt, TokenClaims


def generate_login_response(user_id: int) -> LoginResponse:
    exp_time_delta: timedelta = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    exp_time: datetime = datetime.now(UTC) + exp_time_delta
    exp_time_int: int = int(exp_time.timestamp())

    claims = TokenClaims(
        sub = str(user_id),
        exp = exp_time_int,
    )

    token: str = create_jwt(claims)

    return LoginResponse(
        access_token= token,
        token_type = "Bearer",
        expires_in = settings.JWT_EXPIRE_MINUTES * 60,
    )