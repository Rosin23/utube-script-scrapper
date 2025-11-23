"""
API 스키마 패키지
Pydantic 모델을 사용한 입출력 검증을 제공합니다.
"""

from .video import (
    VideoRequest,
    VideoMetadata,
    TranscriptEntry,
    VideoResponse,
    VideoScrapeRequest,
    VideoScrapeResponse
)
from .playlist import (
    PlaylistRequest,
    PlaylistInfo,
    PlaylistVideoInfo,
    PlaylistResponse
)
from .ai import (
    SummaryRequest,
    SummaryResponse,
    TranslationRequest,
    TranslationResponse,
    TopicExtractionRequest,
    TopicExtractionResponse,
    AIEnhancementRequest,
    AIEnhancementResponse
)

__all__ = [
    # Video schemas
    "VideoRequest",
    "VideoMetadata",
    "TranscriptEntry",
    "VideoResponse",
    "VideoScrapeRequest",
    "VideoScrapeResponse",
    # Playlist schemas
    "PlaylistRequest",
    "PlaylistInfo",
    "PlaylistVideoInfo",
    "PlaylistResponse",
    # AI schemas
    "SummaryRequest",
    "SummaryResponse",
    "TranslationRequest",
    "TranslationResponse",
    "TopicExtractionRequest",
    "TopicExtractionResponse",
    "AIEnhancementRequest",
    "AIEnhancementResponse",
]
