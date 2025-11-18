"""
Python Examples for YouTube Script Scraper API

This file demonstrates basic usage of the API with Python's requests library.
"""

import requests
import json
from typing import Dict, List, Any


# API Base URL
BASE_URL = "http://localhost:8000"


def get_video_info(video_url: str, languages: List[str] = None) -> Dict[str, Any]:
    """
    Get video metadata and transcript.

    Args:
        video_url: YouTube video URL
        languages: List of preferred subtitle languages (default: ["ko", "en"])

    Returns:
        Dictionary containing metadata and transcript
    """
    if languages is None:
        languages = ["ko", "en"]

    response = requests.post(
        f"{BASE_URL}/video/info",
        json={
            "video_url": video_url,
            "languages": languages,
            "prefer_manual": True
        }
    )

    response.raise_for_status()
    return response.json()


def scrape_video_with_ai(
    video_url: str,
    enable_summary: bool = True,
    enable_translation: bool = False,
    target_language: str = "en",
    enable_topics: bool = True,
    num_topics: int = 5
) -> Dict[str, Any]:
    """
    Scrape video with AI enhancements.

    Args:
        video_url: YouTube video URL
        enable_summary: Enable AI summarization
        enable_translation: Enable translation
        target_language: Target language for translation
        enable_topics: Enable topic extraction
        num_topics: Number of topics to extract

    Returns:
        Dictionary containing video data with AI enhancements
    """
    response = requests.post(
        f"{BASE_URL}/video/scrape",
        json={
            "video_url": video_url,
            "enable_summary": enable_summary,
            "summary_max_points": 5,
            "enable_translation": enable_translation,
            "target_language": target_language,
            "enable_topics": enable_topics,
            "num_topics": num_topics,
            "output_format": "json"
        }
    )

    response.raise_for_status()
    return response.json()


def get_playlist_info(playlist_url: str, max_videos: int = None) -> Dict[str, Any]:
    """
    Get playlist information and video list.

    Args:
        playlist_url: YouTube playlist URL
        max_videos: Maximum number of videos to retrieve (None = all)

    Returns:
        Dictionary containing playlist info and videos
    """
    payload = {"playlist_url": playlist_url}
    if max_videos is not None:
        payload["max_videos"] = max_videos

    response = requests.post(
        f"{BASE_URL}/playlist/info",
        json=payload
    )

    response.raise_for_status()
    return response.json()


def generate_summary(text: str, max_points: int = 5, language: str = "ko") -> str:
    """
    Generate AI summary of text.

    Args:
        text: Text to summarize
        max_points: Maximum number of summary points
        language: Summary language

    Returns:
        Summary text
    """
    response = requests.post(
        f"{BASE_URL}/ai/summary",
        json={
            "text": text,
            "max_points": max_points,
            "language": language
        }
    )

    response.raise_for_status()
    return response.json()["summary"]


def translate_text(text: str, target_language: str, source_language: str = None) -> str:
    """
    Translate text to target language.

    Args:
        text: Text to translate
        target_language: Target language code
        source_language: Source language code (auto-detect if None)

    Returns:
        Translated text
    """
    payload = {
        "text": text,
        "target_language": target_language
    }
    if source_language:
        payload["source_language"] = source_language

    response = requests.post(
        f"{BASE_URL}/ai/translate",
        json=payload
    )

    response.raise_for_status()
    return response.json()["translated_text"]


def extract_topics(text: str, num_topics: int = 5, language: str = "en") -> List[str]:
    """
    Extract key topics from text.

    Args:
        text: Text to analyze
        num_topics: Number of topics to extract
        language: Topic language

    Returns:
        List of topics
    """
    response = requests.post(
        f"{BASE_URL}/ai/topics",
        json={
            "text": text,
            "num_topics": num_topics,
            "language": language
        }
    )

    response.raise_for_status()
    return response.json()["topics"]


# Example Usage
if __name__ == "__main__":
    # Example 1: Get basic video information
    print("Example 1: Getting video information...")
    try:
        video_data = get_video_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print(f"Title: {video_data['metadata']['title']}")
        print(f"Channel: {video_data['metadata']['channel']}")
        print(f"Transcript entries: {len(video_data['transcript'])}")
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json()}")

    # Example 2: Scrape video with AI features
    print("\nExample 2: Scraping video with AI...")
    try:
        ai_data = scrape_video_with_ai(
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            enable_summary=True,
            enable_topics=True
        )
        print(f"Summary: {ai_data['summary'][:100]}...")
        print(f"Topics: {ai_data['key_topics']}")
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json()}")

    # Example 3: Get playlist information
    print("\nExample 3: Getting playlist information...")
    try:
        playlist_data = get_playlist_info(
            "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
            max_videos=5
        )
        print(f"Playlist: {playlist_data['playlist_info']['title']}")
        print(f"Total videos: {playlist_data['total_videos']}")
        print(f"Returned: {playlist_data['returned_videos']}")
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json()}")

    # Example 4: Generate summary
    print("\nExample 4: Generating summary...")
    try:
        long_text = "Your long text here..."
        summary = generate_summary(long_text, max_points=3)
        print(f"Summary: {summary}")
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json()}")

    # Example 5: Translate text
    print("\nExample 5: Translating text...")
    try:
        korean_text = "안녕하세요"
        english_translation = translate_text(korean_text, "en")
        print(f"Translation: {english_translation}")
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json()}")

    # Example 6: Extract topics
    print("\nExample 6: Extracting topics...")
    try:
        sample_text = "Sample text about machine learning and AI..."
        topics = extract_topics(sample_text, num_topics=3)
        print(f"Topics: {topics}")
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.json()}")
