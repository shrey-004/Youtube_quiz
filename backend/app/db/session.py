"""
session.py — Database connection and session management.

SQLAlchemy needs two things to talk to PostgreSQL:
1. An Engine — the actual connection to the database server
2. A Session — a "unit of work" that tracks changes and commits them

Think of the Engine as a phone line to the database.
Think of a Session as one phone call — it starts, you do things, it ends.

We never share sessions between requests. Each request gets its own
session, does its work, and the session is closed when done.
This prevents data corruption from concurrent requests.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

logger = logging.getLogger(__name__)

# Create the engine — this is the connection pool to PostgreSQL
# pool_pre_ping=True means SQLAlchemy checks if connections are alive
# before using them. Without this, you get errors after the DB
# restarts or the connection times out.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    # echo=True would log every SQL query — useful for debugging
    # but too noisy for production. Turn on temporarily if needed.
    echo=False,
)

# SessionLocal is a factory — calling SessionLocal() creates a new session
SessionLocal = sessionmaker(
    autocommit=False,  # We commit manually — gives us control
    autoflush=False,   # We flush manually — prevents surprises
    bind=engine,
)


# Base class for all our ORM models
# Every model class will inherit from this
class Base(DeclarativeBase):
    pass


def get_db():
    """
    FastAPI dependency that provides a database session per request.

    Used with FastAPI's Depends() system:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...

    The 'yield' makes this a context manager:
    - Code before yield: set up the session
    - yield: give the session to the route handler
    - Code after yield: always runs, even if an exception occurred
    - This guarantees the session is always closed — no connection leaks
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        # If anything goes wrong, rollback so we don't leave
        # partial data in the database
        db.rollback()
        raise
    finally:
        # Always close the session — returns connection to the pool
        db.close()