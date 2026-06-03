"""
scorer.py — Quiz scoring and results calculation engine.

This module takes a list of questions and a list of user answers,
then calculates a complete result breakdown.

It is pure Python — no database, no HTTP, no AI.
This makes it trivially testable and reusable.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def calculate_score(
    questions: List[dict],
    user_answers: Dict[str, str],
) -> dict:
    """
    Score a quiz attempt.

    Args:
        questions: List of question dicts (from quiz generator).
                   Each must have: id, question_text, options,
                   correct_answer, difficulty, explanation
        user_answers: Dict mapping question_id → selected_answer
                      Example: {"uuid-1": "Paris", "uuid-2": "Berlin"}

    Returns:
        Complete result dict with score, breakdown, and per-question detail.

    Example:
        questions = [{"id": "abc", "correct_answer": "Paris", ...}]
        user_answers = {"abc": "Paris"}
        result = calculate_score(questions, user_answers)
        # result["score"] == 1
        # result["accuracy"] == 100.0
    """
    if not questions:
        return {
            "success": False,
            "error": "No questions provided.",
        }

    total = len(questions)
    correct_count = 0
    skipped_count = 0

    # Per-question detailed results
    question_results = []

    # Per-difficulty tracking
    difficulty_stats = {
        "easy":   {"total": 0, "correct": 0},
        "medium": {"total": 0, "correct": 0},
        "hard":   {"total": 0, "correct": 0},
    }

    for question in questions:
        q_id = question["id"]
        correct_answer = question["correct_answer"]
        difficulty = question.get("difficulty", "medium").lower()
        user_answer = user_answers.get(q_id, None)

        # Track difficulty stats
        if difficulty in difficulty_stats:
            difficulty_stats[difficulty]["total"] += 1

        # Determine if answer is correct
        if user_answer is None or user_answer.strip() == "":
            # Question was skipped — counts as wrong
            is_correct = False
            skipped_count += 1
        else:
            # Case-insensitive, whitespace-stripped comparison
            # Prevents "Paris " vs "Paris" from being marked wrong
            is_correct = (
                user_answer.strip().lower() == correct_answer.strip().lower()
            )

        if is_correct:
            correct_count += 1
            if difficulty in difficulty_stats:
                difficulty_stats[difficulty]["correct"] += 1

        question_results.append({
            "question_id": q_id,
            "question_text": question["question_text"],
            "options": question["options"],
            "correct_answer": correct_answer,
            "user_answer": user_answer,
            "is_correct": is_correct,
            "was_skipped": user_answer is None,
            "difficulty": difficulty,
            "explanation": question.get("explanation", ""),
        })

    # Calculate accuracy — avoid division by zero
    accuracy = round((correct_count / total) * 100, 1) if total > 0 else 0.0

    wrong_count = total - correct_count

    # Calculate per-difficulty accuracy
    difficulty_breakdown = {}
    for diff, stats in difficulty_stats.items():
        if stats["total"] > 0:
            diff_accuracy = round(
                (stats["correct"] / stats["total"]) * 100, 1
            )
        else:
            diff_accuracy = 0.0

        difficulty_breakdown[diff] = {
            "total": stats["total"],
            "correct": stats["correct"],
            "wrong": stats["total"] - stats["correct"],
            "accuracy": diff_accuracy,
        }

    # Performance grade based on accuracy
    grade = _calculate_grade(accuracy)

    # Performance message for the UI
    performance_message = _get_performance_message(accuracy, total, correct_count)

    logger.info(
        f"Scoring complete: {correct_count}/{total} correct, "
        f"accuracy: {accuracy}%, grade: {grade}"
    )

    return {
        "success": True,
        "error": "",

        # Summary stats
        "score": correct_count,
        "total_questions": total,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "skipped_count": skipped_count,
        "accuracy": accuracy,
        "grade": grade,
        "performance_message": performance_message,

        # Per-difficulty breakdown
        "difficulty_breakdown": difficulty_breakdown,

        # Full per-question detail (for results page)
        "question_results": question_results,
    }


def _calculate_grade(accuracy: float) -> str:
    """
    Convert accuracy percentage to a letter grade.

    Standard grading scale used in most universities.
    """
    if accuracy >= 90:
        return "A"
    elif accuracy >= 80:
        return "B"
    elif accuracy >= 70:
        return "C"
    elif accuracy >= 60:
        return "D"
    else:
        return "F"


def _get_performance_message(
    accuracy: float,
    total: int,
    correct: int,
) -> str:
    """
    Return an encouraging, contextual performance message.
    Used on the results page to give the user feedback.
    """
    if accuracy == 100:
        return f"Perfect score! You answered all {total} questions correctly."
    elif accuracy >= 80:
        return (
            f"Great job! You got {correct} out of {total} correct. "
            f"You have a strong understanding of this topic."
        )
    elif accuracy >= 60:
        return (
            f"Good effort! You got {correct} out of {total} correct. "
            f"Review the explanations for the questions you missed."
        )
    elif accuracy >= 40:
        return (
            f"You got {correct} out of {total} correct. "
            f"Consider rewatching the video and trying again."
        )
    else:
        return (
            f"You got {correct} out of {total} correct. "
            f"Don't worry — review the explanations and try again!"
        )