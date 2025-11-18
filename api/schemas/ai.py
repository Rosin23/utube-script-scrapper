"""
AI 기능 관련 Pydantic 스키마
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SummaryRequest(BaseModel):
    """요약 생성 요청 스키마"""
    text: str = Field(..., description="요약할 텍스트")
    max_points: int = Field(
        default=5,
        ge=1,
        le=10,
        description="요약 포인트 수 (1-10)"
    )
    language: str = Field(
        default="ko",
        description="요약 언어 코드"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "This is a long text that needs to be summarized...",
                "max_points": 5,
                "language": "ko"
            }
        }


class SummaryResponse(BaseModel):
    """요약 생성 응답 스키마"""
    summary: str = Field(..., description="생성된 요약")
    original_length: int = Field(..., description="원본 텍스트 길이")
    summary_length: int = Field(..., description="요약 텍스트 길이")
    language: str = Field(..., description="요약 언어")

    class Config:
        json_schema_extra = {
            "example": {
                "summary": "1. Point one\n2. Point two\n3. Point three",
                "original_length": 5000,
                "summary_length": 200,
                "language": "ko"
            }
        }


class TranslationRequest(BaseModel):
    """번역 요청 스키마"""
    text: str = Field(..., description="번역할 텍스트")
    target_language: str = Field(..., description="대상 언어 코드")
    source_language: Optional[str] = Field(
        None,
        description="원본 언어 코드 (자동 감지: None)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "안녕하세요, 반갑습니다.",
                "target_language": "en",
                "source_language": "ko"
            }
        }


class TranslationResponse(BaseModel):
    """번역 응답 스키마"""
    translated_text: str = Field(..., description="번역된 텍스트")
    source_language: Optional[str] = Field(None, description="원본 언어")
    target_language: str = Field(..., description="대상 언어")
    original_length: int = Field(..., description="원본 텍스트 길이")
    translated_length: int = Field(..., description="번역 텍스트 길이")

    class Config:
        json_schema_extra = {
            "example": {
                "translated_text": "Hello, nice to meet you.",
                "source_language": "ko",
                "target_language": "en",
                "original_length": 15,
                "translated_length": 25
            }
        }


class TopicExtractionRequest(BaseModel):
    """주제 추출 요청 스키마"""
    text: str = Field(..., description="주제를 추출할 텍스트")
    num_topics: int = Field(
        default=5,
        ge=1,
        le=20,
        description="추출할 주제 수 (1-20)"
    )
    language: str = Field(
        default="ko",
        description="주제 언어 코드"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "This is a text about various topics...",
                "num_topics": 5,
                "language": "ko"
            }
        }


class TopicExtractionResponse(BaseModel):
    """주제 추출 응답 스키마"""
    topics: List[str] = Field(..., description="추출된 주제 리스트")
    num_topics: int = Field(..., description="추출된 주제 수")
    language: str = Field(..., description="주제 언어")

    class Config:
        json_schema_extra = {
            "example": {
                "topics": ["Topic 1", "Topic 2", "Topic 3"],
                "num_topics": 3,
                "language": "ko"
            }
        }


class AIEnhancementRequest(BaseModel):
    """AI 종합 기능 요청 스키마"""
    text: str = Field(..., description="처리할 텍스트")
    enable_summary: bool = Field(default=False, description="요약 활성화")
    summary_max_points: int = Field(default=5, ge=1, le=10, description="요약 포인트 수")
    enable_translation: bool = Field(default=False, description="번역 활성화")
    target_language: Optional[str] = Field(None, description="번역 대상 언어")
    enable_topics: bool = Field(default=False, description="주제 추출 활성화")
    num_topics: int = Field(default=5, ge=1, le=20, description="추출할 주제 수")
    language: str = Field(default="ko", description="기본 언어 코드")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Sample text for AI processing...",
                "enable_summary": True,
                "summary_max_points": 5,
                "enable_translation": True,
                "target_language": "en",
                "enable_topics": True,
                "num_topics": 5,
                "language": "ko"
            }
        }


class AIEnhancementResponse(BaseModel):
    """AI 종합 기능 응답 스키마"""
    summary: Optional[str] = Field(None, description="생성된 요약")
    translation: Optional[str] = Field(None, description="번역된 텍스트")
    topics: Optional[List[str]] = Field(None, description="추출된 주제 리스트")
    processing_time: Optional[float] = Field(None, description="처리 시간 (초)")

    class Config:
        json_schema_extra = {
            "example": {
                "summary": "1. Summary point one\n2. Summary point two",
                "translation": "Translated text here...",
                "topics": ["Topic 1", "Topic 2", "Topic 3"],
                "processing_time": 2.5
            }
        }
