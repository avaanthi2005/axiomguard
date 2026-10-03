from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.security import decode_access_token
from database.db import get_user_by_id

# tokenUrl just points Swagger UI at the login endpoint — doesn't affect behavior
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Use this on routes that REQUIRE login (e.g. /api/history)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = get_user_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    return user


def get_current_user_optional(token: str = Depends(oauth2_scheme)) -> Optional[dict]:
    """Use this on routes that work with OR without login
    (e.g. scan/phish/guard — so the Chrome extension keeps working)."""
    if not token:
        return None

    payload = decode_access_token(token)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    return get_user_by_id(int(user_id))
