"""
test_scorer.py — Unit tests for the scoring engine.

These tests run instantly — no network, no AI, no database.
Pure logic testing.
"""

import pytest
from app.core.scorer import calculate_score, _calculate_grade


# Reusable sample questions for all tests
SAMPLE_QUESTIONS = [
    {
        "id": "q1",
        "question_text": "What is the capital of France?",
        "options": ["Berlin", "Paris", "Madrid", "Rome"],
        "correct_answer": "Paris",
        "difficulty": "easy",
        "explanation": "Paris is the capital city of France.",
    },
    {
        "id": "q2",
        "question_text": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "correct_answer": "4",
        "difficulty": "easy",
        "explanation": "Basic arithmetic: 2 + 2 = 4.",
    },
    {
        "id": "q3",
        "question_text": "What is machine learning?",
        "options": [
            "A type of computer hardware",
            "A subset of AI that learns from data",
            "A programming language",
            "A database system",
        ],
        "correct_answer": "A subset of AI that learns from data",
        "difficulty": "medium",
        "explanation": "Machine learning is a subset of AI.",
    },
]


class TestCalculateScore:

    def test_perfect_score(self):
        """All correct answers should give 100% accuracy."""
        answers = {
            "q1": "Paris",
            "q2": "4",
            "q3": "A subset of AI that learns from data",
        }
        result = calculate_score(SAMPLE_QUESTIONS, answers)

        assert result["success"] is True
        assert result["score"] == 3
        assert result["correct_count"] == 3
        assert result["wrong_count"] == 0
        assert result["accuracy"] == 100.0
        assert result["grade"] == "A"

    def test_zero_score(self):
        """All wrong answers should give 0% accuracy."""
        answers = {
            "q1": "Berlin",
            "q2": "3",
            "q3": "A type of computer hardware",
        }
        result = calculate_score(SAMPLE_QUESTIONS, answers)

        assert result["score"] == 0
        assert result["accuracy"] == 0.0
        assert result["grade"] == "F"
        assert result["wrong_count"] == 3

    def test_partial_score(self):
        """Mix of right and wrong should calculate correctly."""
        answers = {
            "q1": "Paris",    # correct
            "q2": "3",        # wrong
            "q3": "A subset of AI that learns from data",  # correct
        }
        result = calculate_score(SAMPLE_QUESTIONS, answers)

        assert result["correct_count"] == 2
        assert result["wrong_count"] == 1
        assert result["accuracy"] == round((2/3) * 100, 1)

    def test_skipped_question_counts_as_wrong(self):
        """A question with no answer should count as wrong."""
        answers = {
            "q1": "Paris",
            # q2 skipped
            "q3": "A subset of AI that learns from data",
        }
        result = calculate_score(SAMPLE_QUESTIONS, answers)

        assert result["skipped_count"] == 1
        assert result["correct_count"] == 2
        assert result["wrong_count"] == 1

    def test_empty_answers_all_skipped(self):
        """Submitting no answers should give zero score."""
        result = calculate_score(SAMPLE_QUESTIONS, {})

        assert result["score"] == 0
        assert result["skipped_count"] == 3
        assert result["accuracy"] == 0.0

    def test_case_insensitive_matching(self):
        """Answers should match regardless of case."""
        answers = {
            "q1": "paris",   # lowercase should still match "Paris"
            "q2": "4",
            "q3": "A subset of AI that learns from data",
        }
        result = calculate_score(SAMPLE_QUESTIONS, answers)
        assert result["correct_count"] == 3

    def test_whitespace_trimmed(self):
        """Extra whitespace around answer should not affect result."""
        answers = {
            "q1": "  Paris  ",
            "q2": "4",
            "q3": "A subset of AI that learns from data",
        }
        result = calculate_score(SAMPLE_QUESTIONS, answers)
        assert result["correct_count"] == 3

    def test_empty_questions_returns_error(self):
        """Empty question list should return failure."""
        result = calculate_score([], {"q1": "Paris"})
        assert result["success"] is False

    def test_question_results_have_correct_structure(self):
        """Each question result must have all required fields."""
        answers = {"q1": "Paris", "q2": "4", "q3": "Berlin"}
        result = calculate_score(SAMPLE_QUESTIONS, answers)

        for qr in result["question_results"]:
            assert "question_id" in qr
            assert "question_text" in qr
            assert "correct_answer" in qr
            assert "user_answer" in qr
            assert "is_correct" in qr
            assert "difficulty" in qr
            assert "explanation" in qr

    def test_difficulty_breakdown_calculated(self):
        """Difficulty breakdown should reflect correct answers per level."""
        answers = {
            "q1": "Paris",  # easy - correct
            "q2": "3",      # easy - wrong
            "q3": "A subset of AI that learns from data",  # medium - correct
        }
        result = calculate_score(SAMPLE_QUESTIONS, answers)

        assert result["difficulty_breakdown"]["easy"]["total"] == 2
        assert result["difficulty_breakdown"]["easy"]["correct"] == 1
        assert result["difficulty_breakdown"]["medium"]["correct"] == 1


class TestCalculateGrade:

    def test_grade_boundaries(self):
        assert _calculate_grade(95) == "A"
        assert _calculate_grade(90) == "A"
        assert _calculate_grade(89) == "B"
        assert _calculate_grade(80) == "B"
        assert _calculate_grade(79) == "C"
        assert _calculate_grade(70) == "C"
        assert _calculate_grade(69) == "D"
        assert _calculate_grade(60) == "D"
        assert _calculate_grade(59) == "F"
        assert _calculate_grade(0)  == "F"