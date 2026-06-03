"""
dependencies.py — FastAPI dependencies for authentication.

A dependency is a function that FastAPI calls automatically
before your route handler runs. If it raises an exception,
the route never executes.

Usage in a route:
    @router.get("/protected")
    def protected_route(current_user = Depends(get_current_user)):
        # current_user is the logged-in User object
        # FastAPI called get_current_user() automatically
        # If the token was invalid, this line never runs
"""

import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.crud.users import get_user_by_id
from app.core.security import decode_access_token

logger = logging.getLogger(__name__)

# HTTPBearer extracts the token from the Authorization: Bearer <token> header
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """
    Extract and validate the JWT token from the request header.
    Returns the current User object if valid.
    Raises 401 if token is missing, expired, or invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token. Please login again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    return user