"""
Dependencies for FastAPI
공통 의존성 및 서비스 인스턴스를 제공합니다.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from core import YouTubeService, AIService, FormatterService
from utils.config import Settings


@lru_cache()
def get_settings() -> Settings:
    """
    애플리케이션 설정을 반환합니다.

    lru_cache를 사용하여 싱글톤 패턴으로 설정을 관리합니다.
    """
    return Settings()


def get_youtube_service() -> YouTubeService:
    """
    YouTube 서비스 인스턴스를 생성하여 반환합니다.

    Returns:
        YouTubeService 인스턴스
    """
    return YouTubeService()


def get_ai_service(
    settings: Annotated[Settings, Depends(get_settings)]
) -> AIService:
    """
    AI 서비스 인스턴스를 생성하여 반환합니다.

    Args:
        settings: 애플리케이션 설정 (의존성 주입)

    Returns:
        AIService 인스턴스
    """
    return AIService(
        api_key=settings.gemini_api_key,
        model_name=settings.gemini_model_name
    )


def get_formatter_service() -> FormatterService:
    """
    Formatter 서비스 인스턴스를 생성하여 반환합니다.

    Returns:
        FormatterService 인스턴스
    """
    return FormatterService()


# Type aliases for cleaner code
YouTubeServiceDep = Annotated[YouTubeService, Depends(get_youtube_service)]
AIServiceDep = Annotated[AIService, Depends(get_ai_service)]
FormatterServiceDep = Annotated[FormatterService, Depends(get_formatter_service)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
