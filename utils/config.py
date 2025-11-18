"""
애플리케이션 설정 관리
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    애플리케이션 설정

    환경변수에서 설정을 로드합니다.
    """

    # API 설정
    api_title: str = "YouTube Script Scraper API"
    api_description: str = "YouTube 비디오 스크래핑 및 AI 기능을 제공하는 RESTful API"
    api_version: str = "3.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Gemini API 설정
    gemini_api_key: Optional[str] = None
    gemini_model_name: str = "gemini-2.0-flash-exp"
    gemini_retry_count: int = 3
    gemini_retry_delay: float = 1.0

    # 기본 설정
    default_languages: list = ["ko", "en"]
    default_max_summary_points: int = 5
    default_num_topics: int = 5

    # CORS 설정
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]

    # 로깅 설정
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 환경변수에서 Gemini API 키 로드
        if not self.gemini_api_key:
            self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


# 전역 설정 인스턴스
settings = Settings()
