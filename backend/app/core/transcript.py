"""
transcript.py — YouTube transcript extraction module.
Written for youtube-transcript-api version 1.2.4
In this version, YouTubeTranscriptApi must be instantiated first.
Usage: api = YouTubeTranscriptApi(); api.fetch(video_id)
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

MAX_TRANSCRIPT_LENGTH = 15000


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract the YouTube video ID from various URL formats.
    Handles: watch?v=, youtu.be/, embed/, mobile URLs
    """
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"(?:embed\/)([0-9A-Za-z_-]{11})",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            logger.info(f"Extracted video ID: {video_id} from URL: {url}")
            return video_id

    logger.warning(f"Could not extract video ID from URL: {url}")
    return None


def clean_transcript_text(transcript_data) -> str:
    """
    Convert raw transcript data into clean readable text.
    Handles both list-of-dicts and object formats.
    """
    if not transcript_data:
        return ""

    # Build raw text — handle both dict and object style items
    parts = []
    for item in transcript_data:
        try:
            # Dict style: item["text"]
            parts.append(item["text"])
        except (KeyError, TypeError):
            try:
                # Object style: item.text
                parts.append(item.text)
            except AttributeError:
                parts.append(str(item))

    raw_text = " ".join(parts)

    # Clean noise
    cleaning_steps = [
        (r"\[.*?\]", ""),      # Remove [Music], [Applause] etc.
        (r"♪.*?♪", ""),        # Remove music notes
        (r"&amp;", "&"),        # Fix HTML entities
        (r"&quot;", '"'),
        (r"&apos;", "'"),
        (r"&#39;", "'"),
        (r"\n+", " "),          # Replace newlines with spaces
        (r" {2,}", " "),        # Collapse multiple spaces
    ]

    cleaned = raw_text
    for pattern, replacement in cleaning_steps:
        cleaned = re.sub(pattern, replacement, cleaned)

    return cleaned.strip()


def get_transcript(url: str) -> dict:
    """
    Main function — given a YouTube URL, return the clean transcript.
    Works with youtube-transcript-api 1.2.4 where the class
    must be instantiated before calling fetch() or list().
    """
    logger.info(f"Starting transcript extraction for: {url}")

    # Step 1: Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        return {
            "success": False,
            "transcript": "",
            "video_id": "",
            "language": "",
            "char_count": 0,
            "was_truncated": False,
            "error": "Invalid YouTube URL. Please check the URL and try again.",
            "error_type": "INVALID_URL",
        }

    # Step 2: Fetch transcript
    # In version 1.2.4, YouTubeTranscriptApi is instantiated first
    # then fetch(video_id) or list(video_id) is called on the instance
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        # Create an instance — this is new in 1.2.4
        ytt_api = YouTubeTranscriptApi()

        # Try English first
        try:
            transcript_data = ytt_api.fetch(
                video_id,
                languages=["en", "en-US", "en-GB", "en-IN"]
            )
            language = "en"
            logger.info(f"Found English transcript for {video_id}")

        except Exception as lang_error:
            logger.warning(
                f"English not found for {video_id}, trying any language. "
                f"Reason: {str(lang_error)}"
            )
            # Fallback: fetch without specifying language
            transcript_data = ytt_api.fetch(video_id)
            language = "auto"
            logger.info(f"Using auto-detected language for {video_id}")

    except Exception as e:
        error_str = str(e).lower()
        logger.error(
            f"Error fetching transcript for {video_id}: {str(e)}"
        )

        # Detect error type from message content
        if "disabled" in error_str:
            return {
                "success": False,
                "transcript": "",
                "video_id": video_id,
                "language": "",
                "char_count": 0,
                "was_truncated": False,
                "error": (
                    "This video has captions disabled. "
                    "Try a video with the CC button visible."
                ),
                "error_type": "TRANSCRIPTS_DISABLED",
            }

        if "unavailable" in error_str or "private" in error_str:
            return {
                "success": False,
                "transcript": "",
                "video_id": video_id,
                "language": "",
                "char_count": 0,
                "was_truncated": False,
                "error": (
                    "This video is unavailable. "
                    "It may be private, age-restricted, or deleted."
                ),
                "error_type": "VIDEO_UNAVAILABLE",
            }

        if "no transcript" in error_str or "could not retrieve" in error_str:
            return {
                "success": False,
                "transcript": "",
                "video_id": video_id,
                "language": "",
                "char_count": 0,
                "was_truncated": False,
                "error": (
                    "No transcript found for this video. "
                    "It may not have captions available."
                ),
                "error_type": "NO_TRANSCRIPT",
            }

        return {
            "success": False,
            "transcript": "",
            "video_id": video_id,
            "language": "",
            "char_count": 0,
            "was_truncated": False,
            "error": f"Could not extract transcript: {str(e)}",
            "error_type": "UNEXPECTED_ERROR",
        }

    # Step 3: Clean the text
    clean_text = clean_transcript_text(transcript_data)

    if not clean_text:
        return {
            "success": False,
            "transcript": "",
            "video_id": video_id,
            "language": language,
            "char_count": 0,
            "was_truncated": False,
            "error": "Transcript was empty after cleaning.",
            "error_type": "EMPTY_TRANSCRIPT",
        }

    # Step 4: Truncate if too long
    was_truncated = False
    if len(clean_text) > MAX_TRANSCRIPT_LENGTH:
        clean_text = clean_text[:MAX_TRANSCRIPT_LENGTH]
        # Cut at last complete sentence
        last_period = clean_text.rfind(".")
        if last_period > MAX_TRANSCRIPT_LENGTH * 0.8:
            clean_text = clean_text[:last_period + 1]
        was_truncated = True
        logger.info(f"Transcript truncated to {MAX_TRANSCRIPT_LENGTH} chars")

    logger.info(
        f"Successfully extracted: {len(clean_text)} chars, "
        f"language: {language}, truncated: {was_truncated}"
    )

    return {
        "success": True,
        "transcript": clean_text,
        "video_id": video_id,
        "language": language,
        "char_count": len(clean_text),
        "was_truncated": was_truncated,
        "error": "",
        "error_type": "",
    }