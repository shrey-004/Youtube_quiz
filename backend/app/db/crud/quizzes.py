"""
crud/quizzes.py — Database operations for Videos, Quizzes, and Questions.
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Video, Quiz, Question

logger = logging.getLogger(__name__)


# ─── VIDEO OPERATIONS ────────────────────────────────────────────────────────

def get_video_by_youtube_id(db: Session, video_id: str) -> Optional[Video]:
    """Check if we already have this video's transcript cached."""
    return db.query(Video).filter(Video.video_id == video_id).first()


def create_video(
    db: Session,
    youtube_url: str,
    video_id: str,
    transcript: str,
    language: str = "en",
    char_count: int = 0,
) -> Video:
    """Store a new video and its transcript."""
    db_video = Video(
        youtube_url=youtube_url,
        video_id=video_id,
        transcript=transcript,
        transcript_language=language,
        char_count=char_count,
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    logger.info(f"Stored video: {video_id}")
    return db_video


# ─── QUIZ OPERATIONS ─────────────────────────────────────────────────────────

def create_quiz_with_questions(
    db: Session,
    video_id: str,
    user_id: str,
    questions: List[dict],
    model_used: str = "",
) -> Quiz:
    """
    Create a quiz and all its questions in one transaction.

    We use a transaction here — either ALL questions are saved,
    or NONE are. This prevents partial quizzes in the database.
    """
    # Create the quiz record
    db_quiz = Quiz(
        video_id=video_id,
        created_by=user_id,
        status="ready",
        total_questions=len(questions),
        model_used=model_used,
    )
    db.add(db_quiz)
    db.flush()  # Get the quiz ID without committing yet

    # Create all question records
    for q in questions:
        db_question = Question(
            quiz_id=db_quiz.id,
            question_number=q["question_number"],
            question_text=q["question_text"],
            options=q["options"],
            correct_answer=q["correct_answer"],
            difficulty=q["difficulty"],
            explanation=q["explanation"],
        )
        db.add(db_question)

    # Commit everything at once — atomic transaction
    db.commit()
    db.refresh(db_quiz)
    logger.info(
        f"Created quiz {db_quiz.id} with {len(questions)} questions"
    )
    return db_quiz


def get_quiz_by_id(db: Session, quiz_id: str) -> Optional[Quiz]:
    """Fetch a quiz with all its questions."""
    return db.query(Quiz).filter(Quiz.id == quiz_id).first()


def get_quizzes_by_user(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 20,
) -> List[Quiz]:
    """Fetch all quizzes created by a user, newest first."""
    return (
        db.query(Quiz)
        .filter(Quiz.created_by == user_id)
        .order_by(Quiz.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )