"""
quiz_generator.py — Orchestrates the full quiz generation pipeline.

This module:
1. Takes a transcript
2. Calls the AI provider
3. Post-processes and enriches the questions
4. Returns quiz-ready data

It's separate from the AI provider so the provider can be swapped
without changing the orchestration logic.
"""

import logging
import uuid
from typing import Optional

from app.ai.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)

# Create one provider instance shared across all requests
# This avoids re-initializing the Gemini client on every request
_provider = None


def get_provider() -> GeminiProvider:
    """
    Returns the singleton AI provider instance.
    Creates it on first call (lazy initialization).
    This is the Singleton pattern — one instance for the whole app.
    """
    global _provider
    if _provider is None:
        logger.info("Initializing AI provider (first request)")
        _provider = GeminiProvider()
    return _provider


def generate_quiz(
    transcript: str,
    video_title: Optional[str] = None,
    num_easy: int = 4,
    num_medium: int = 4,
    num_hard: int = 2,
) -> dict:
    """
    Full pipeline: transcript → validated quiz questions.

    Args:
        transcript: Clean video transcript
        video_title: Optional title for context
        num_easy/medium/hard: Questions per difficulty level

    Returns:
        dict with:
            success (bool)
            quiz_data (dict): Complete quiz with metadata
            error (str): Error message if failed
    """
    logger.info(
        f"Starting quiz generation for transcript "
        f"({len(transcript)} chars)"
    )

    # Validate inputs
    if not transcript or len(transcript.strip()) < 100:
        return {
            "success": False,
            "quiz_data": {},
            "error": (
                "Transcript is too short to generate meaningful questions. "
                "Please try a longer video (at least 2 minutes)."
            ),
        }

    total_questions = num_easy + num_medium + num_hard
    if total_questions < 1 or total_questions > 20:
        return {
            "success": False,
            "quiz_data": {},
            "error": "Total questions must be between 1 and 20.",
        }

    # Call the AI provider
    provider = get_provider()
    result = provider.generate_questions(
        transcript=transcript,
        video_title=video_title,
        num_easy=num_easy,
        num_medium=num_medium,
        num_hard=num_hard,
    )

    if not result["success"]:
        return {
            "success": False,
            "quiz_data": {},
            "error": result["error"],
        }

    questions = result["questions"]

    # Enrich each question with a unique ID
    # We generate IDs here so the frontend can reference specific questions
    enriched_questions = []
    for i, q in enumerate(questions):
        enriched_questions.append({
            "id": str(uuid.uuid4()),
            "question_number": i + 1,
            "question_text": q["question_text"],
            "options": q["options"],
            "correct_answer": q["correct_answer"],
            "difficulty": q["difficulty"],
            "explanation": q["explanation"],
        })

    # Build the complete quiz object
    quiz_data = {
        "total_questions": len(enriched_questions),
        "questions_by_difficulty": {
            "easy": [q for q in enriched_questions if q["difficulty"] == "easy"],
            "medium": [q for q in enriched_questions if q["difficulty"] == "medium"],
            "hard": [q for q in enriched_questions if q["difficulty"] == "hard"],
        },
        "questions": enriched_questions,
        "model_used": result["model_used"],
    }

    logger.info(
        f"Quiz generation complete: {len(enriched_questions)} questions, "
        f"model: {result['model_used']}"
    )

    validation = validate_questions(result["questions"])

    if not validation["valid"]:
        logger.error(
            f"Quiz failed validation: {validation['error']}. "
            f"Removed: {validation['removed_count']} questions."
        )
        return {
            "success": False,
            "quiz_data": {},
            "error": validation["error"],
        }

    # Log any non-fatal warnings
    for warning in validation["warnings"]:
        logger.warning(f"Quiz warning: {warning}")

    # Use validated (possibly cleaned) questions
    questions = validation["questions"]

    # Enrich each question with a unique ID
    enriched_questions = []
    for i, q in enumerate(questions):
        enriched_questions.append({
            "id": str(uuid.uuid4()),
            "question_number": i + 1,
            "question_text": q["question_text"],
            "options": q["options"],
            "correct_answer": q["correct_answer"],
            "difficulty": q["difficulty"],
            "explanation": q["explanation"],
        })

    quiz_data = {
        "total_questions": len(enriched_questions),
        "questions_by_difficulty": {
            "easy":   [q for q in enriched_questions if q["difficulty"] == "easy"],
            "medium": [q for q in enriched_questions if q["difficulty"] == "medium"],
            "hard":   [q for q in enriched_questions if q["difficulty"] == "hard"],
        },
        "questions": enriched_questions,
        "model_used": result["model_used"],
        "validation_warnings": validation["warnings"],
    }

    logger.info(
        f"Quiz generation complete: {len(enriched_questions)} questions"
    )

    return {
        "success": True,
        "quiz_data": quiz_data,
        "error": "",
    }


def validate_questions(questions: list) -> dict:
    """
    Quality-check generated questions before sending to the user.

    Catches common LLM failure modes:
    - correct_answer not matching any option exactly
    - Duplicate questions
    - Questions that are too short to be meaningful
    - All questions at the same difficulty

    Args:
        questions: List of question dicts from generate_quiz()

    Returns:
        dict with:
            valid (bool): Whether all questions passed validation
            questions (list): Cleaned/filtered valid questions
            removed_count (int): How many questions were removed
            warnings (list): Non-fatal issues found
    """
    valid_questions = []
    warnings = []
    removed_count = 0

    seen_question_texts = set()

    for i, q in enumerate(questions):
        question_num = i + 1
        issues = []

        # Check 1: correct_answer must exactly match one of the options
        if q["correct_answer"] not in q["options"]:
            issues.append(
                f"Q{question_num}: correct_answer does not match any option"
            )
            logger.warning(
                f"Removing Q{question_num} — correct_answer mismatch: "
                f"'{q['correct_answer']}' not in {q['options']}"
            )
            removed_count += 1
            continue  # Skip this question entirely

        # Check 2: Question must have exactly 4 options
        if len(q["options"]) != 4:
            issues.append(f"Q{question_num}: has {len(q['options'])} options instead of 4")
            removed_count += 1
            continue

        # Check 3: Question text must be meaningful (not too short)
        if len(q["question_text"].strip()) < 15:
            issues.append(f"Q{question_num}: question text too short")
            removed_count += 1
            continue

        # Check 4: No duplicate options within a question
        if len(set(q["options"])) != 4:
            issues.append(f"Q{question_num}: contains duplicate options")
            removed_count += 1
            continue

        # Check 5: Detect duplicate questions (same text)
        normalized = q["question_text"].strip().lower()
        if normalized in seen_question_texts:
            warnings.append(f"Q{question_num}: duplicate question detected and removed")
            removed_count += 1
            continue
        seen_question_texts.add(normalized)

        # Check 6: Difficulty must be valid
        if q.get("difficulty", "").lower() not in {"easy", "medium", "hard"}:
            # Fix it rather than remove it — default to medium
            q["difficulty"] = "medium"
            warnings.append(f"Q{question_num}: invalid difficulty, defaulted to medium")

        # Passed all checks
        valid_questions.append(q)

    # Check 7: Warn if difficulty distribution is heavily skewed
    difficulties = [q["difficulty"] for q in valid_questions]
    if valid_questions:
        most_common_diff = max(set(difficulties), key=difficulties.count)
        most_common_count = difficulties.count(most_common_diff)
        if most_common_count == len(valid_questions) and len(valid_questions) > 1:
            warnings.append(
                f"All questions are '{most_common_diff}' difficulty — "
                f"consider adjusting num_easy/medium/hard"
            )

    has_enough = len(valid_questions) >= 3

    logger.info(
        f"Validation complete: {len(valid_questions)} valid, "
        f"{removed_count} removed, {len(warnings)} warnings"
    )

    return {
        "valid": has_enough,
        "questions": valid_questions,
        "removed_count": removed_count,
        "warnings": warnings,
        "error": (
            "Too many questions failed validation. Please try again."
            if not has_enough
            else ""
        ),
    }