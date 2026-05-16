from jwt import decode, PyJWTError
from config import settings

def decode_jwt(token: str) -> dict | None:
    try:
        return decode(
            token,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM,
        )
    except PyJWTError:
        return None
