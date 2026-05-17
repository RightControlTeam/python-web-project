from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .token import decode_token
from .login_schemas import TokenClaims

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login/")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenClaims:
    return decode_token(token)