"""
schemas/auth.py — Request and response shapes for authentication.

Pydantic schemas are different from SQLAlchemy models:
- SQLAlchemy models = database table structure
- Pydantic schemas = API request/response structure

We never expose SQLAlchemy models directly to the API —
that would leak internal details like hashed_password.
Schemas control exactly what comes in and goes out.
"""

from pydantic import BaseModel, EmailStr, field_validator
import re


class RegisterRequest(BaseModel):
    email: EmailStr          # Pydantic validates email format automatically
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 50:
            raise ValueError("Username must be under 50 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, and underscores"
            )
        return v

    @field_validator("password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool

    # This tells Pydantic to read data from SQLAlchemy model attributes
    model_config = {"from_attributes": True}