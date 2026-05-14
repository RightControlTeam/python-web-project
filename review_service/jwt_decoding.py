from jwt import decode, PyJWTError
from os import environ

def decode_jwt(token: str) -> dict | None:
    try:
        return decode(
            token,
            environ.get("JWT_SECRET_KEY"),
            environ.get("JWT_ALGORITHM")
        )
    except PyJWTError:
        return None
