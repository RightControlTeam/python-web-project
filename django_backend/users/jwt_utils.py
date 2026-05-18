import jwt
from datetime import datetime, timedelta, UTC
from django.conf import settings

def generate_token(user_id: int) -> str:
    """Генерирует JWT токен"""
    exp = datetime.now(UTC) + timedelta(minutes=settings.JWT_EXP_MINS)
    payload = {'sub': str(user_id), 'exp': exp}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """Декодирует JWT токен"""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])