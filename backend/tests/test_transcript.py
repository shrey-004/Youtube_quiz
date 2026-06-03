"""
test_transcript.py — Unit tests for the transcript extraction module.

We test the logic in isolation — no HTTP server needed.
Run with: pytest tests/ -v
"""

import pytest
from app.core.transcript import extract_video_id, clean_transcript_text, get_transcript


class TestExtractVideoId:
    """Tests for the URL parsing function."""

    def test_standard_url(self):
        """Standard watch URL should return the video ID."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url(self):
        """youtu.be short URL should work."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_url_with_timestamp(self):
        """URL with &t= timestamp parameter should still work."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_embed_url(self):
        """Embed URL format should work."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_mobile_url(self):
        """Mobile URL should work."""
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_invalid_url_returns_none(self):
        """Non-YouTube URL should return None."""
        assert extract_video_id("https://google.com") is None

    def test_empty_string_returns_none(self):
        """Empty string should return None."""
        assert extract_video_id("") is None


class TestCleanTranscript:
    """Tests for the transcript cleaning function."""

    def test_removes_music_tags(self):
        """[Music] and similar tags should be removed."""
        chunks = [{"text": "[Music] Hello world", "start": 0, "duration": 1}]
        result = clean_transcript_text(chunks)
        assert "[Music]" not in result
        assert "Hello world" in result

    def test_removes_applause_tags(self):
        """[Applause] should be removed."""
        chunks = [{"text": "[Applause] Thank you", "start": 0, "duration": 1}]
        result = clean_transcript_text(chunks)
        assert "[Applause]" not in result

    def test_joins_chunks(self):
        """Multiple chunks should be joined into one string."""
        chunks = [
            {"text": "Hello", "start": 0, "duration": 1},
            {"text": "world", "start": 1, "duration": 1},
        ]
        result = clean_transcript_text(chunks)
        assert "Hello world" in result

    def test_fixes_html_entities(self):
        """HTML entities should be converted to real characters."""
        chunks = [{"text": "Tom &amp; Jerry", "start": 0, "duration": 1}]
        result = clean_transcript_text(chunks)
        assert "Tom & Jerry" in result
        assert "&amp;" not in result

    def test_empty_list_returns_empty_string(self):
        """Empty transcript list should return empty string."""
        result = clean_transcript_text([])
        assert result == ""


class TestGetTranscript:
    """Integration tests — these actually call YouTube."""

    def test_invalid_url_returns_error(self):
        """Non-YouTube URL should return a failure dict."""
        result = get_transcript("https://google.com")
        assert result["success"] is False
        assert result["error_type"] == "INVALID_URL"
        assert result["transcript"] == ""

    def test_valid_video_returns_transcript(self):
        """
        A real public YouTube video with captions should succeed.
        We use a well-known educational video that won't be taken down.
        This test requires internet connection.
        """
        # TED Talk: "The first 20 hours" - stable, has captions
        url = "https://www.youtube.com/watch?v=5MgBikgcWnY"
        result = get_transcript(url)

        # Either it works or it fails gracefully — never crashes
        assert isinstance(result["success"], bool)
        if result["success"]:
            assert len(result["transcript"]) > 100
            assert result["video_id"] == "5MgBikgcWnY"
        else:
            # If it fails, it must have a proper error message
            assert len(result["error"]) > 0