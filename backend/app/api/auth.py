"""
auth.py — Registration and login endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.crud.users import (
    get_user_by_email,
    get_user_by_username,
    create_user,
)
from app.core.security import verify_password, create_access_token
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.

    Checks:
    - Email not already registered
    - Username not already taken
    - Password meets minimum requirements (validated by Pydantic)
    """
    # Check email uniqueness
    if get_user_by_email(db, request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Check username uniqueness
    if get_user_by_username(db, request.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken.",
        )

    user = create_user(
        db=db,
        email=request.email,
        username=request.username,
        password=request.password,
    )

    logger.info(f"New user registered: {user.username}")
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive JWT token",
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT access token.

    The token must be included in the Authorization header
    of all protected requests:
        Authorization: Bearer <token>
    """
    # Find user by email
    user = get_user_by_email(db, request.email)

    # Deliberately vague error — don't tell attackers if email exists
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    # Create JWT token with user ID as the subject
    token = create_access_token(data={"sub": user.id})

    logger.info(f"User logged in: {user.username}")

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
    )