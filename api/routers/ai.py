"""
AI 기능 관련 API 라우터
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
import time

from api.schemas.ai import (
    SummaryRequest,
    SummaryResponse,
    TranslationRequest,
    TranslationResponse,
    TopicExtractionRequest,
    TopicExtractionResponse,
    AIEnhancementRequest,
    AIEnhancementResponse
)
from core import AIService
from utils import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    responses={404: {"description": "Not found"}},
)


def get_ai_service() -> AIService:
    """AI 서비스 인스턴스를 생성합니다."""
    return AIService(
        api_key=settings.gemini_api_key,
        model_name=settings.gemini_model_name
    )


@router.post("/summary", response_model=SummaryResponse)
async def generate_summary(request: SummaryRequest):
    """
    텍스트 요약을 생성합니다.

    - **text**: 요약할 텍스트 (필수)
    - **max_points**: 최대 요약 포인트 수 (1-10, 기본값: 5)
    - **language**: 요약 언어 코드 (기본값: ko)
    """
    ai_service = get_ai_service()

    if not ai_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="AI service is not available. Please check API key configuration."
        )

    try:
        logger.info(f"Generating summary for text ({len(request.text)} chars)")

        summary = ai_service.generate_summary_from_text(
            text=request.text,
            max_points=request.max_points,
            language=request.language
        )

        if not summary:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate summary"
            )

        return SummaryResponse(
            summary=summary,
            original_length=len(request.text),
            summary_length=len(summary),
            language=request.language
        )

    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}"
        )


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    텍스트를 번역합니다.

    - **text**: 번역할 텍스트 (필수)
    - **target_language**: 대상 언어 코드 (필수)
    - **source_language**: 원본 언어 코드 (선택, 자동 감지)
    """
    ai_service = get_ai_service()

    if not ai_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="AI service is not available. Please check API key configuration."
        )

    try:
        logger.info(
            f"Translating text ({len(request.text)} chars) "
            f"to {request.target_language}"
        )

        translated = ai_service.translate_text(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language
        )

        if not translated:
            raise HTTPException(
                status_code=500,
                detail="Failed to translate text"
            )

        return TranslationResponse(
            translated_text=translated,
            source_language=request.source_language,
            target_language=request.target_language,
            original_length=len(request.text),
            translated_length=len(translated)
        )

    except Exception as e:
        logger.error(f"Failed to translate text: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to translate text: {str(e)}"
        )


@router.post("/topics", response_model=TopicExtractionResponse)
async def extract_topics(request: TopicExtractionRequest):
    """
    텍스트에서 핵심 주제를 추출합니다.

    - **text**: 분석할 텍스트 (필수)
    - **num_topics**: 추출할 주제 수 (1-20, 기본값: 5)
    - **language**: 주제 언어 코드 (기본값: ko)
    """
    ai_service = get_ai_service()

    if not ai_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="AI service is not available. Please check API key configuration."
        )

    try:
        logger.info(
            f"Extracting topics from text ({len(request.text)} chars)"
        )

        topics = ai_service.extract_topics_from_text(
            text=request.text,
            num_topics=request.num_topics,
            language=request.language
        )

        if not topics:
            raise HTTPException(
                status_code=500,
                detail="Failed to extract topics"
            )

        return TopicExtractionResponse(
            topics=topics,
            num_topics=len(topics),
            language=request.language
        )

    except Exception as e:
        logger.error(f"Failed to extract topics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract topics: {str(e)}"
        )


@router.post("/enhance", response_model=AIEnhancementResponse)
async def enhance_text(request: AIEnhancementRequest):
    """
    텍스트에 AI 기능을 종합적으로 적용합니다 (요약, 번역, 주제 추출).

    - **text**: 처리할 텍스트 (필수)
    - **enable_summary**: 요약 활성화
    - **enable_translation**: 번역 활성화
    - **enable_topics**: 주제 추출 활성화
    """
    ai_service = get_ai_service()

    if not ai_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="AI service is not available. Please check API key configuration."
        )

    try:
        logger.info(f"Enhancing text with AI ({len(request.text)} chars)")

        start_time = time.time()

        # 텍스트를 자막 형식으로 변환
        transcript = [{'text': request.text, 'start': 0, 'duration': 0}]

        # AI 기능 적용
        result = ai_service.enhance_transcript(
            transcript=transcript,
            enable_summary=request.enable_summary,
            summary_max_points=request.summary_max_points,
            enable_translation=request.enable_translation,
            target_language=request.target_language,
            enable_topics=request.enable_topics,
            num_topics=request.num_topics,
            language=request.language
        )

        processing_time = time.time() - start_time

        return AIEnhancementResponse(
            summary=result['summary'],
            translation=result['translation'],
            topics=result['topics'],
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"Failed to enhance text: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enhance text: {str(e)}"
        )


@router.get("/health")
async def check_ai_health():
    """
    AI 서비스의 상태를 확인합니다.
    """
    ai_service = get_ai_service()

    return JSONResponse(content={
        "available": ai_service.is_available(),
        "model": settings.gemini_model_name,
        "api_key_configured": bool(settings.gemini_api_key)
    })
