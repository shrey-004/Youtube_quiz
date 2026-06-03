"""
security.py — Password hashing and JWT token management.

Two responsibilities:
1. Password security: hash passwords with bcrypt before storing,
   verify submitted passwords against stored hashes.
2. JWT tokens: create signed tokens on login, decode and verify
   tokens on every protected request.

WHY JWT?
When a user logs in, we give them a token — like a signed hall pass.
On every future request, they show this pass. We verify our signature
on it — no database lookup needed. This is stateless and scales well.

WHY BCRYPT?
Bcrypt is intentionally slow — it takes ~100ms to hash a password.
This makes brute-force attacks impractical. Never use MD5 or SHA for passwords.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

logger = logging.getLogger(__name__)

# CryptContext handles password hashing
# bcrypt is the industry standard for password storage
# deprecated="auto" means old hash formats are automatically upgraded
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    Call this before storing a password in the database.

    Example:
        hashed = hash_password("mypassword123")
        # hashed = "$2b$12$..." (bcrypt hash, safe to store)
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if a plain text password matches a stored bcrypt hash.
    Call this during login to verify the user's submitted password.

    Example:
        is_valid = verify_password("mypassword123", stored_hash)
        # True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    The token contains a payload (data dict) that we can read later
    without a database lookup. We sign it with our SECRET_KEY so
    we can detect if anyone tampers with it.

    Args:
        data: Dict to encode in the token, typically {"sub": user_id}
        expires_delta: How long until the token expires

    Returns:
        Signed JWT token string
    """
    to_encode = data.copy()

    # Set expiry time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    # Sign the token with our secret key
    # Anyone who reads this token can see the payload (it's base64 encoded)
    # But they can't MODIFY it without the secret key — that's the security
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.

    Returns the payload dict if token is valid and not expired.
    Returns None if token is invalid, expired, or tampered with.

    Example:
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
        else:
            # Token is invalid — reject the request
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode failed: {str(e)}")
        return None