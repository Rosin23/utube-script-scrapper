"""
API 라우터 패키지
FastAPI 엔드포인트를 제공합니다.
"""

from .video import router as video_router
from .playlist import router as playlist_router
from .ai import router as ai_router

__all__ = [
    "video_router",
    "playlist_router",
    "ai_router",
]
