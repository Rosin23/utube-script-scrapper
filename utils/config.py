"""
애플리케이션 설정 관리
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, model_validator


class Settings(BaseSettings):
    """
    애플리케이션 설정

    환경변수에서 설정을 로드합니다.
    .env 파일이 있으면 먼저 .env에서 읽고, 없으면 환경 변수에서 읽습니다.
    """

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API 설정
    api_title: str = "YouTube Script Scraper API"
    api_description: str = "YouTube 비디오 스크래핑 및 AI 기능을 제공하는 RESTful API"
    api_version: str = "3.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Gemini API 설정
    # .env 파일에서 GEMINI_API_KEY 또는 gemini_api_key로 설정 가능
    # 환경 변수에서도 GEMINI_API_KEY 또는 gemini_api_key로 설정 가능
    gemini_api_key: Optional[str] = None
    gemini_model_name: str = "gemini-2.5-flash"
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

    @model_validator(mode="after")
    def load_gemini_api_key(self):
        """
        Gemini API 키를 로드합니다.
        
        우선순위:
        1. .env 파일의 GEMINI_API_KEY 또는 gemini_api_key (이미 Pydantic이 로드함)
        2. 환경 변수 GEMINI_API_KEY
        3. 환경 변수 GOOGLE_API_KEY
        """
        # .env 파일에서 이미 로드된 gemini_api_key가 있으면 사용
        if self.gemini_api_key:
            return self
        
        # 환경 변수에서 찾기 (우선순위: GEMINI_API_KEY > GOOGLE_API_KEY)
        # .env 파일이 없거나 gemini_api_key가 없는 경우에만 실행
        self.gemini_api_key = (
            os.getenv("GEMINI_API_KEY") or 
            os.getenv("GOOGLE_API_KEY")
        )
        
        return self


# 전역 설정 인스턴스
settings = Settings()
