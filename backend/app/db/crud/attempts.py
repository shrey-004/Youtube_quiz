"""
crud/attempts.py — Database operations for Attempts and AnswerLogs.
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Attempt, AnswerLog

logger = logging.getLogger(__name__)


def create_attempt(
    db: Session,
    quiz_id: str,
    user_id: str,
    score_data: dict,
) -> Attempt:
    """
    Save a completed quiz attempt and all answer logs.

    score_data is the dict returned by calculate_score() in scorer.py.
    We store both the summary (on Attempt) and the per-question detail
    (on AnswerLog) so the results page has everything it needs.
    """
    # Create the attempt summary
    db_attempt = Attempt(
        quiz_id=quiz_id,
        user_id=user_id,
        score=score_data["score"],
        total_questions=score_data["total_questions"],
        correct_count=score_data["correct_count"],
        wrong_count=score_data["wrong_count"],
        skipped_count=score_data["skipped_count"],
        accuracy=score_data["accuracy"],
        grade=score_data["grade"],
    )
    db.add(db_attempt)
    db.flush()  # Get the attempt ID

    # Create one AnswerLog per question
    for qr in score_data["question_results"]:
        db_log = AnswerLog(
            attempt_id=db_attempt.id,
            question_id=qr["question_id"],
            user_answer=qr.get("user_answer"),
            is_correct=qr["is_correct"],
            was_skipped=qr.get("was_skipped", False),
        )
        db.add(db_log)

    db.commit()
    db.refresh(db_attempt)
    logger.info(
        f"Saved attempt {db_attempt.id}: "
        f"{db_attempt.score}/{db_attempt.total_questions}"
    )
    return db_attempt


def get_attempts_by_user(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 20,
) -> List[Attempt]:
    """Fetch all attempts by a user, newest first."""
    return (
        db.query(Attempt)
        .filter(Attempt.user_id == user_id)
        .order_by(Attempt.attempted_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_attempt_by_id(
    db: Session,
    attempt_id: str,
) -> Optional[Attempt]:
    """Fetch a single attempt with all its answer logs."""
    return db.query(Attempt).filter(Attempt.id == attempt_id).first()