"""
models.py — SQLAlchemy ORM models.

Each class here maps to one table in PostgreSQL.
SQLAlchemy translates between Python objects and SQL rows automatically.

Naming conventions:
- Table names: plural, lowercase (users, quizzes, questions)
- Column names: lowercase with underscores (created_at, video_id)
- Primary keys: always UUID, never auto-increment integers
  (UUIDs are safer for distributed systems and don't leak row counts)
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Float,
    Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


def generate_uuid():
    """Generate a new UUID string. Used as default for primary keys."""
    return str(uuid.uuid4())


class User(Base):
    """
    Stores registered users.
    Passwords are NEVER stored in plain text — only bcrypt hashes.
    """
    __tablename__ = "users"

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid,
        index=True,
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships — SQLAlchemy will automatically fetch related records
    # back_populates creates a two-way link between models
    quizzes = relationship("Quiz", back_populates="creator")
    attempts = relationship("Attempt", back_populates="user")

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"


class Video(Base):
    """
    Stores YouTube video metadata and transcripts.

    We cache transcripts here so if two users submit the same URL,
    we don't re-fetch and re-generate — we reuse the existing record.
    This saves Gemini API quota and speeds up response time.
    """
    __tablename__ = "videos"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    youtube_url = Column(String(500), nullable=False)
    video_id = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=True)
    transcript = Column(Text, nullable=False)
    transcript_language = Column(String(10), default="en")
    char_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One video can have many quizzes (different users generating from same video)
    quizzes = relationship("Quiz", back_populates="video")

    def __repr__(self):
        return f"<Video {self.video_id}>"


class Quiz(Base):
    """
    Represents a generated quiz.

    A Quiz belongs to one Video and one User (who generated it).
    It contains many Questions.
    Users can make many Attempts at the same Quiz.

    status field tracks the generation lifecycle:
    - 'generating': AI is working on it
    - 'ready': Questions generated and validated
    - 'failed': Generation failed
    """
    __tablename__ = "quizzes"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="ready")  # generating, ready, failed
    total_questions = Column(Integer, default=0)
    model_used = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="quizzes")
    creator = relationship("User", back_populates="quizzes")
    questions = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan",  # Delete questions when quiz is deleted
    )
    attempts = relationship("Attempt", back_populates="quiz")

    def __repr__(self):
        return f"<Quiz {self.id} ({self.status})>"


class Question(Base):
    """
    A single multiple-choice question within a Quiz.

    Options are stored as JSON — a list of 4 strings.
    This is simpler than a separate options table since
    options are always exactly 4 and never queried individually.
    """
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    quiz_id = Column(String(36), ForeignKey("quizzes.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)       # ["opt1", "opt2", "opt3", "opt4"]
    correct_answer = Column(Text, nullable=False)
    difficulty = Column(String(10), nullable=False)  # easy, medium, hard
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answer_logs = relationship("AnswerLog", back_populates="question")

    def __repr__(self):
        return f"<Question {self.question_number} ({self.difficulty})>"


class Attempt(Base):
    """
    Records one user's attempt at a Quiz.

    A user can attempt the same quiz multiple times.
    Each attempt gets its own row with its own score.
    This enables tracking improvement over time.
    """
    __tablename__ = "attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    quiz_id = Column(String(36), ForeignKey("quizzes.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    score = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    wrong_count = Column(Integer, default=0)
    skipped_count = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    grade = Column(String(2), default="F")
    attempted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="attempts")
    answer_logs = relationship(
        "AnswerLog",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Attempt {self.id} score={self.score}/{self.total_questions}>"


class AnswerLog(Base):
    """
    Records the user's answer for each individual question in an attempt.

    This is what powers the detailed results page —
    "You got question 3 wrong, here's the correct answer and explanation."
    """
    __tablename__ = "answer_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    attempt_id = Column(String(36), ForeignKey("attempts.id"), nullable=False)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    user_answer = Column(Text, nullable=True)   # None if question was skipped
    is_correct = Column(Boolean, default=False)
    was_skipped = Column(Boolean, default=False)

    # Relationships
    attempt = relationship("Attempt", back_populates="answer_logs")
    question = relationship("Question", back_populates="answer_logs")

    def __repr__(self):
        return f"<AnswerLog q={self.question_id} correct={self.is_correct}>"