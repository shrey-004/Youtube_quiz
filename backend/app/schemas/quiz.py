"""
schemas/quiz.py — Request and response shapes for quizzes and attempts.
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class QuestionOut(BaseModel):
    """A question as returned to the frontend."""
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    question_number: int
    question_text: str
    options: List[str]
    difficulty: str
    # NOTE: correct_answer is NOT included here
    # We never send the answer to the frontend before submission
    # That would make cheating trivial


class QuestionWithAnswer(BaseModel):
    """Question including the answer — only sent after submission."""
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    question_number: int
    question_text: str
    options: List[str]
    correct_answer: str
    difficulty: str
    explanation: str


class QuizOut(BaseModel):
    """A quiz as returned after generation."""
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    video_id: str
    total_questions: int
    status: str
    created_at: datetime
    questions: List[QuestionOut]


class GenerateFromURLRequest(BaseModel):
    """Request to generate a quiz from a YouTube URL."""
    url: str
    num_easy: int = 4
    num_medium: int = 4
    num_hard: int = 2


class AnswerSubmission(BaseModel):
    """One answer in the submission."""
    question_id: str
    selected_answer: str


class SubmitAttemptRequest(BaseModel):
    """Submit all answers for a quiz."""
    quiz_id: str
    answers: List[AnswerSubmission]


class AttemptOut(BaseModel):
    """Attempt summary for the history page."""
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    quiz_id: str
    score: int
    total_questions: int
    correct_count: int
    wrong_count: int
    accuracy: float
    grade: str
    attempted_at: datetime


class AttemptResultOut(BaseModel):
    """Full result including per-question breakdown."""
    model_config = ConfigDict(protected_namespaces=())

    attempt_id: str
    score: int
    total_questions: int
    correct_count: int
    wrong_count: int
    skipped_count: int
    accuracy: float
    grade: str
    performance_message: str
    difficulty_breakdown: dict
    question_results: List[dict]