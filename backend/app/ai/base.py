"""
base.py — Abstract base class for all LLM providers.

This defines the CONTRACT that every AI provider must follow.
Whether we use Gemini, OpenAI, or anything else, the rest of
the app only talks to this interface — never to the provider directly.

This means swapping providers = changing ONE line, not rewriting the app.
This is the Open/Closed Principle: open for extension, closed for modification.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    Any class that inherits this MUST implement generate_questions().
    If it doesn't, Python raises a TypeError at startup — catching
    the mistake early rather than at runtime.
    """

    @abstractmethod
    def generate_questions(
        self,
        transcript: str,
        video_title: Optional[str] = None,
        num_easy: int = 4,
        num_medium: int = 4,
        num_hard: int = 2,
    ) -> dict:
        """
        Generate quiz questions from a transcript.

        Args:
            transcript: Clean text from the YouTube video
            video_title: Optional title for better context
            num_easy: Number of easy questions to generate
            num_medium: Number of medium questions to generate
            num_hard: Number of hard questions to generate

        Returns:
            dict with keys:
                success (bool): Whether generation succeeded
                questions (list): List of question dicts
                error (str): Error message if success is False
                model_used (str): Which model was used
                tokens_used (int): Approximate tokens consumed
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if the API key and connection are working.
        Returns True if the provider is available, False otherwise.
        Used for health checks and startup validation.
        """
        pass