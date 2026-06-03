"""
videos.py — API endpoints for video URL submission and transcript extraction.

This file handles HTTP concerns only:
- Validate the incoming request
- Call the core transcript module
- Return the right HTTP response

It does NOT contain transcript logic — that lives in core/transcript.py
"""

import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl, field_validator
from app.core.quiz_generator import generate_quiz

from app.core.transcript import get_transcript

logger = logging.getLogger(__name__)

# APIRouter lets us group related endpoints
# We'll include this router in main.py with a prefix of "/api/videos"
router = APIRouter(prefix="/api/videos", tags=["videos"])


class VideoURLRequest(BaseModel):
    """
    Pydantic model for the incoming request body.
    Pydantic automatically validates types and formats.
    """
    url: str  # We validate it ourselves for better error messages

    @field_validator("url")
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        """
        Ensure the URL looks like a YouTube URL before we process it.
        This saves an API call if the user clearly typed the wrong thing.
        """
        youtube_domains = [
            "youtube.com",
            "youtu.be",
            "www.youtube.com",
            "m.youtube.com",
        ]
        if not any(domain in v for domain in youtube_domains):
            raise ValueError(
                "URL must be a YouTube link "
                "(e.g. https://www.youtube.com/watch?v=...)"
            )
        return v


class VideoURLResponse(BaseModel):
    """Shape of the response we send back to the frontend."""
    success: bool
    video_id: str
    transcript_preview: str  # First 200 chars — frontend shows a preview
    char_count: int
    language: str
    was_truncated: bool
    message: str


@router.post(
    "/extract",
    response_model=VideoURLResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract transcript from a YouTube video",
)
async def extract_transcript(request: VideoURLRequest):
    """
    Accept a YouTube URL and return the extracted transcript.

    This endpoint:
    1. Validates the URL format
    2. Extracts the video ID
    3. Fetches the transcript
    4. Returns a preview + metadata

    The full transcript is not returned here to keep the response small.
    The quiz generation happens in a separate endpoint.
    """
    logger.info(f"Transcript extraction requested for: {request.url}")

    result = get_transcript(request.url)

    if not result["success"]:
        # Map our internal error types to appropriate HTTP status codes
        # 422: the request was valid but we couldn't process it
        # 400: bad input from the user
        error_status_map = {
            "INVALID_URL": status.HTTP_400_BAD_REQUEST,
            "TRANSCRIPTS_DISABLED": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VIDEO_UNAVAILABLE": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "NO_TRANSCRIPT": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "UNEXPECTED_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
        status_code = error_status_map.get(
            result["error_type"],
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        raise HTTPException(
            status_code=status_code,
            detail=result["error"]
        )

    return VideoURLResponse(
        success=True,
        video_id=result["video_id"],
        # Show first 200 chars as a preview so user can verify
        transcript_preview=result["transcript"][:200] + "..."
        if len(result["transcript"]) > 200
        else result["transcript"],
        char_count=result["char_count"],
        language=result["language"],
        was_truncated=result.get("was_truncated", False),
        message="Transcript extracted successfully. Ready to generate quiz.",
    )

class FullQuizRequest(BaseModel):
    """Request to go from YouTube URL directly to a complete quiz."""
    url: str
    num_easy: int = 4
    num_medium: int = 4
    num_hard: int = 2

    @field_validator("url")
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        youtube_domains = [
            "youtube.com", "youtu.be",
            "www.youtube.com", "m.youtube.com",
        ]
        if not any(domain in v for domain in youtube_domains):
            raise ValueError(
                "URL must be a YouTube link"
            )
        return v


class FullQuizResponse(BaseModel):
    """Complete quiz ready for the user to attempt."""
    success: bool
    video_id: str
    transcript_char_count: int
    total_questions: int
    questions: list
    message: str


@router.post(
    "/generate-quiz",
    response_model=FullQuizResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract transcript and generate quiz in one step",
)
async def generate_quiz_from_url(request: FullQuizRequest):
    """
    The main endpoint users will call.

    Single request → complete quiz.

    Steps internally:
    1. Validate YouTube URL
    2. Extract transcript
    3. Generate questions with Gemini
    4. Validate questions
    5. Return complete quiz

    Expect 15-30 seconds response time (AI generation takes time).
    """
    logger.info(f"Full quiz generation requested for: {request.url}")

    # Step 1: Extract transcript
    from app.core.transcript import get_transcript
    transcript_result = get_transcript(request.url)

    if not transcript_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=transcript_result["error"],
        )

    transcript = transcript_result["transcript"]
    video_id = transcript_result["video_id"]

    logger.info(
        f"Transcript extracted: {transcript_result['char_count']} chars. "
        f"Now generating questions..."
    )

    # Step 2: Generate and validate questions
    quiz_result = generate_quiz(
        transcript=transcript,
        video_title=None,
        num_easy=request.num_easy,
        num_medium=request.num_medium,
        num_hard=request.num_hard,
    )

    if not quiz_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=quiz_result["error"],
        )

    quiz_data = quiz_result["quiz_data"]

    logger.info(
        f"Full quiz ready: {quiz_data['total_questions']} questions "
        f"for video {video_id}"
    )

    return FullQuizResponse(
        success=True,
        video_id=video_id,
        transcript_char_count=transcript_result["char_count"],
        total_questions=quiz_data["total_questions"],
        questions=quiz_data["questions"],
        message=(
            f"Quiz ready! {quiz_data['total_questions']} questions "
            f"generated from your video."
        ),
    )