"""
quizzes.py — Complete quiz API with database persistence and authentication.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from app.db.session import get_db
from app.db.models import User, Question
from app.db.crud.quizzes import (
    get_video_by_youtube_id,
    create_video,
    create_quiz_with_questions,
    get_quiz_by_id,
    get_quizzes_by_user,
)
from app.db.crud.attempts import (
    create_attempt,
    get_attempts_by_user,
    get_attempt_by_id,
)
from app.core.transcript import get_transcript
from app.core.quiz_generator import generate_quiz
from app.core.scorer import calculate_score
from app.core.dependencies import get_current_user
from app.schemas.quiz import (
    GenerateFromURLRequest,
    QuizOut,
    QuestionOut,
    SubmitAttemptRequest,
    AttemptOut,
    AttemptResultOut,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


@router.post(
    "/generate",
    status_code=status.HTTP_201_CREATED,
    summary="Generate a quiz from a YouTube URL (requires login)",
)
def generate_quiz_from_url(
    request: GenerateFromURLRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Full pipeline: YouTube URL → transcript → AI questions → saved quiz.

    Requires authentication. The quiz is saved to the database
    and associated with the logged-in user.

    Returns the quiz ID and questions (without correct answers).
    """
    logger.info(
        f"User {current_user.username} generating quiz for: {request.url}"
    )

    # Step 1: Extract video ID from URL
    from app.core.transcript import extract_video_id
    video_id = extract_video_id(request.url)
    if not video_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid YouTube URL.",
        )

    # Step 2: Check if we already have this transcript cached
    db_video = get_video_by_youtube_id(db, video_id)

    if db_video:
        logger.info(f"Using cached transcript for video: {video_id}")
        transcript = db_video.transcript
        db_video_id = db_video.id
    else:
        # Fetch and store the transcript
        transcript_result = get_transcript(request.url)
        if not transcript_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=transcript_result["error"],
            )

        db_video = create_video(
            db=db,
            youtube_url=request.url,
            video_id=video_id,
            transcript=transcript_result["transcript"],
            language=transcript_result["language"],
            char_count=transcript_result["char_count"],
        )
        transcript = transcript_result["transcript"]
        db_video_id = db_video.id

    # Step 3: Generate questions with AI
    quiz_result = generate_quiz(
        transcript=transcript,
        num_easy=request.num_easy,
        num_medium=request.num_medium,
        num_hard=request.num_hard,
    )

    if not quiz_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=quiz_result["error"],
        )

    # Step 4: Save quiz and questions to database
    db_quiz = create_quiz_with_questions(
        db=db,
        video_id=db_video_id,
        user_id=current_user.id,
        questions=quiz_result["quiz_data"]["questions"],
        model_used=quiz_result["quiz_data"]["model_used"],
    )

    # Step 5: Return quiz without correct answers
    questions_out = [
        {
            "id": q.id,
            "question_number": q.question_number,
            "question_text": q.question_text,
            "options": q.options,
            "difficulty": q.difficulty,
        }
        for q in db_quiz.questions
    ]

    return {
        "quiz_id": db_quiz.id,
        "video_id": video_id,
        "total_questions": db_quiz.total_questions,
        "questions": questions_out,
        "message": f"Quiz ready! {db_quiz.total_questions} questions generated.",
    }


@router.post(
    "/{quiz_id}/submit",
    response_model=AttemptResultOut,
    summary="Submit answers and get scored results",
)
def submit_quiz_attempt(
    quiz_id: str,
    request: SubmitAttemptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit answers for a quiz and receive full scored results.

    Saves the attempt to the database so it appears in history.
    Returns score, grade, accuracy, and per-question explanations.
    """
    # Fetch the quiz from the database
    db_quiz = get_quiz_by_id(db, quiz_id)
    if not db_quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found.",
        )

    # Build questions list in the format calculate_score() expects
    questions_for_scoring = [
        {
            "id": q.id,
            "question_text": q.question_text,
            "options": q.options,
            "correct_answer": q.correct_answer,
            "difficulty": q.difficulty,
            "explanation": q.explanation,
        }
        for q in db_quiz.questions
    ]

    # Convert answers to dict
    answers_dict = {
        ans.question_id: ans.selected_answer
        for ans in request.answers
    }

    # Calculate score
    score_data = calculate_score(
        questions=questions_for_scoring,
        user_answers=answers_dict,
    )

    if not score_data["success"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=score_data["error"],
        )

    # Save the attempt to database
    db_attempt = create_attempt(
        db=db,
        quiz_id=quiz_id,
        user_id=current_user.id,
        score_data=score_data,
    )

    logger.info(
        f"User {current_user.username} scored "
        f"{score_data['correct_count']}/{score_data['total_questions']} "
        f"({score_data['accuracy']}%) on quiz {quiz_id}"
    )

    return AttemptResultOut(
        attempt_id=db_attempt.id,
        **score_data,
    )


@router.get(
    "/my-quizzes",
    summary="Get all quizzes created by the logged-in user",
)
def get_my_quizzes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns all quizzes the current user has generated."""
    quizzes = get_quizzes_by_user(db, current_user.id)
    return {
        "quizzes": [
            {
                "quiz_id": q.id,
                "video_id": q.video.video_id if q.video else None,
                "total_questions": q.total_questions,
                "created_at": q.created_at.isoformat(),
                "attempt_count": len(q.attempts),
            }
            for q in quizzes
        ]
    }


@router.get(
    "/my-attempts",
    summary="Get quiz attempt history for the logged-in user",
)
def get_my_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns all quiz attempts with scores — the history page data."""
    attempts = get_attempts_by_user(db, current_user.id)
    return {
        "attempts": [
            {
                "attempt_id": a.id,
                "quiz_id": a.quiz_id,
                "score": a.score,
                "total_questions": a.total_questions,
                "accuracy": a.accuracy,
                "grade": a.grade,
                "attempted_at": a.attempted_at.isoformat(),
            }
            for a in attempts
        ]
    }