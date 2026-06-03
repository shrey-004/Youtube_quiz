"""
crud/users.py — Database operations for Users.

CRUD = Create, Read, Update, Delete.
These functions are the ONLY place that touches the users table directly.
Routes call these functions — they never write SQL themselves.

This separation means:
- Easy to test (mock the db session)
- Easy to change DB logic without touching routes
- One place to look when debugging data issues
"""

import logging
from sqlalchemy.orm import Session
from app.db.models import User
from app.core.security import hash_password

logger = logging.getLogger(__name__)


def get_user_by_email(db: Session, email: str):
    """Fetch a user by email. Returns None if not found."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    """Fetch a user by username. Returns None if not found."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: str):
    """Fetch a user by their ID. Returns None if not found."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, username: str, password: str):
    """
    Create a new user in the database.
    Password is hashed before storage — never store plain text.

    Args:
        db: Database session
        email: User's email address (must be unique)
        username: Display name (must be unique)
        password: Plain text password (will be hashed)

    Returns:
        The created User object
    """
    hashed = hash_password(password)
    db_user = User(
        email=email,
        username=username,
        hashed_password=hashed,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Reload from DB to get generated ID etc.
    logger.info(f"Created new user: {username} ({email})")
    return db_user


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    """Fetch all users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()