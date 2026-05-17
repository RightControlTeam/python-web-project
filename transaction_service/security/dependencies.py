from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from shared.jwt_module import TokenClaims, decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login/")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenClaims:
    return decode_jwt(token)