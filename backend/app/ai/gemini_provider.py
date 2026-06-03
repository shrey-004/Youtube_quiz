"""
gemini_provider.py — Google Gemini implementation of BaseLLMProvider.

Uses the Gemini 1.5 Flash model (free tier):
- 15 requests per minute
- 1 million tokens per day
- No credit card required

The free tier is more than sufficient for development and portfolio demos.
"""

import json
import logging
import time
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator

import google.generativeai as genai

from app.ai.base import BaseLLMProvider
from app.ai.prompts import QUIZ_GENERATION_PROMPT, RETRY_PROMPT, CONNECTION_TEST_PROMPT
from app.config import settings

logger = logging.getLogger(__name__)

# Pydantic models for validating the LLM's JSON output
from pydantic import BaseModel, field_validator
from typing import List


class QuestionSchema(BaseModel):
    """
    Validates a single question from the LLM response.
    If the LLM returns a malformed question, Pydantic catches it here
    instead of letting bad data into the database.
    """
    model_config = ConfigDict(protected_namespaces=())
    question_text: str
    options: List[str]
    correct_answer: str
    difficulty: str
    explanation: str

    @field_validator("options")
    @classmethod
    def must_have_four_options(cls, v):
        if len(v) != 4:
            raise ValueError(f"Each question must have exactly 4 options, got {len(v)}")
        return v

    @field_validator("difficulty")
    @classmethod
    def must_be_valid_difficulty(cls, v):
        valid = {"easy", "medium", "hard"}
        if v.lower() not in valid:
            raise ValueError(f"Difficulty must be one of {valid}, got '{v}'")
        return v.lower()

    @field_validator("correct_answer")
    @classmethod
    def correct_answer_must_be_in_options(cls, v, info):
        # info.data contains the already-validated fields
        if "options" in info.data and v not in info.data["options"]:
            raise ValueError(
                f"correct_answer '{v}' must exactly match one of the options"
            )
        return v


class QuestionsResponseSchema(BaseModel):
    """Validates the full response containing all questions."""
    model_config = ConfigDict(protected_namespaces=())
    questions: List[QuestionSchema]


class GeminiProvider(BaseLLMProvider):
    """
    Gemini 1.5 Flash implementation.
    Flash is the free-tier model — fast and capable for our use case.
    """

    # We use Flash for free tier — Pro would cost money
    MODEL_NAME = "gemini-2.5-flash-lite"
    MAX_RETRIES = 2         # How many times to retry on malformed JSON
    RETRY_DELAY = 2         # Seconds between retries

    def __init__(self):
        """
        Initialize the Gemini client.
        Called once at app startup via dependency injection.
        """
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Generation config controls how the model responds
        self.generation_config = genai.types.GenerationConfig(
            # Temperature 0.3: low randomness for consistent structured output
            # Higher = more creative but less reliable JSON
            temperature=0.3,

            # Max output tokens — 2048 is enough for 10 questions with explanations
            # More tokens = more detail but slower and uses more quota
            max_output_tokens=2048,

            # top_p and top_k control sampling — defaults are fine
            top_p=0.8,
            top_k=40,
        )

        # Safety settings — we're generating educational content
        # so we set these to block only truly harmful content
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        self.model = genai.GenerativeModel(
            model_name=self.MODEL_NAME,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
        )

        logger.info(f"GeminiProvider initialized with model: {self.MODEL_NAME}")

    def test_connection(self) -> bool:
        """
        Send a minimal prompt to verify the API key works.
        Called on startup and by the /health endpoint.
        """
        try:
            response = self.model.generate_content(CONNECTION_TEST_PROMPT)
            result = response.text.strip()
            is_connected = "CONNECTED" in result
            logger.info(f"Gemini connection test: {'passed' if is_connected else 'failed'}")
            return is_connected
        except Exception as e:
            logger.error(f"Gemini connection test failed: {str(e)}")
            return False

    def _parse_llm_response(self, raw_text: str) -> Optional[dict]:
        """
        Parse and validate the LLM's raw text response into a Python dict.

        The LLM sometimes adds markdown code blocks (```json ... ```)
        even when told not to. This method strips those before parsing.

        Args:
            raw_text: Raw string from the LLM

        Returns:
            Parsed and validated dict, or None if parsing fails
        """
        # Strip whitespace
        text = raw_text.strip()

        # Remove markdown code blocks if present
        # The model sometimes wraps JSON in ```json ... ``` despite instructions
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```json or ```) and last line (```)
            text = "\n".join(lines[1:-1]) if len(lines) > 2 else text

        # Remove any remaining backticks
        text = text.strip("`").strip()

        try:
            parsed = json.loads(text)

            # Validate against our Pydantic schema
            validated = QuestionsResponseSchema(**parsed)
            return validated.model_dump()

        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {str(e)}")
            logger.debug(f"Raw text that failed parsing: {text[:500]}")
            return None

        except Exception as e:
            logger.warning(f"Validation error: {str(e)}")
            return None

    def generate_questions(
        self,
        transcript: str,
        video_title: Optional[str] = None,
        num_easy: int = 4,
        num_medium: int = 4,
        num_hard: int = 2,
    ) -> dict:
        """
        Generate quiz questions from a transcript using Gemini.

        Implements retry logic: if the first response is malformed JSON,
        we send a retry prompt up to MAX_RETRIES times before giving up.

        Args:
            transcript: Clean video transcript text
            video_title: Optional video title for context
            num_easy/medium/hard: Number of questions per difficulty

        Returns:
            Standard dict with success, questions, error, model_used
        """
        logger.info(
            f"Generating questions: {num_easy} easy, {num_medium} medium, "
            f"{num_hard} hard. Transcript length: {len(transcript)} chars"
        )

        # Build the initial prompt
        prompt = QUIZ_GENERATION_PROMPT.format(
            transcript=transcript,
            video_title=video_title or "Not provided",
            num_easy=num_easy,
            num_medium=num_medium,
            num_hard=num_hard,
        )

        # Attempt generation with retries
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                logger.info(f"Gemini API call attempt {attempt + 1}/{self.MAX_RETRIES + 1}")

                # Make the API call
                response = self.model.generate_content(prompt)

                # Check if the model refused to respond (safety filter)
                if not response.text:
                    logger.warning("Gemini returned empty response (possible safety block)")
                    return {
                        "success": False,
                        "questions": [],
                        "error": (
                            "AI could not process this content. "
                            "Try a different video."
                        ),
                        "model_used": self.MODEL_NAME,
                        "tokens_used": 0,
                    }

                raw_text = response.text
                logger.debug(f"Raw Gemini response (first 300 chars): {raw_text[:300]}")

                # Try to parse the response
                parsed = self._parse_llm_response(raw_text)

                if parsed:
                    questions = parsed["questions"]
                    total_expected = num_easy + num_medium + num_hard

                    logger.info(
                        f"Successfully generated {len(questions)} questions "
                        f"(expected {total_expected})"
                    )

                    # Count by difficulty for logging
                    by_difficulty = {}
                    for q in questions:
                        diff = q["difficulty"]
                        by_difficulty[diff] = by_difficulty.get(diff, 0) + 1
                    logger.info(f"Question breakdown: {by_difficulty}")

                    return {
                        "success": True,
                        "questions": questions,
                        "error": "",
                        "model_used": self.MODEL_NAME,
                        # Approximate token count
                        "tokens_used": len(prompt.split()) + len(raw_text.split()),
                    }

                # Parsing failed — retry with a simpler prompt
                logger.warning(
                    f"Attempt {attempt + 1} failed to parse JSON. "
                    f"{'Retrying...' if attempt < self.MAX_RETRIES else 'Giving up.'}"
                )

                if attempt < self.MAX_RETRIES:
                    # Use the retry prompt which is shorter and more direct
                    prompt = RETRY_PROMPT.format(
                        transcript=transcript[:5000],  # Shorter for retry
                        num_easy=num_easy,
                        num_medium=num_medium,
                        num_hard=num_hard,
                    )
                    time.sleep(self.RETRY_DELAY)

            except Exception as e:
                error_str = str(e).lower()
                logger.error(f"Gemini API error on attempt {attempt + 1}: {str(e)}")

                # Handle rate limiting specifically
                if ("429" in str(e) or "quota" in error_str or "rate" in error_str) and "404" not in str(e):
                    if attempt < self.MAX_RETRIES:
                        wait_time = (attempt + 1) * 10  # 10s, 20s
                        logger.info(f"Rate limited. Waiting {wait_time}s before retry.")
                        time.sleep(wait_time)
                        continue

                    return {
                        "success": False,
                        "questions": [],
                        "error": (
                            "AI service is temporarily busy. "
                            "Please wait a minute and try again."
                        ),
                        "model_used": self.MODEL_NAME,
                        "tokens_used": 0,
                    }

                # For other errors, don't retry
                return {
                    "success": False,
                    "questions": [],
                    "error": f"AI generation failed: {str(e)}",
                    "model_used": self.MODEL_NAME,
                    "tokens_used": 0,
                }

        # All retries exhausted
        return {
            "success": False,
            "questions": [],
            "error": (
                "AI could not generate properly formatted questions "
                "after multiple attempts. Please try again."
            ),
            "model_used": self.MODEL_NAME,
            "tokens_used": 0,
        }