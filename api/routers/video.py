"""
비디오 관련 API 라우터
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import logging

from api.schemas.video import (
    VideoRequest,
    VideoResponse,
    VideoScrapeRequest,
    VideoScrapeResponse,
    VideoMetadata,
    TranscriptEntry
)
from core import YouTubeService, AIService, FormatterService
from utils import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/video",
    tags=["video"],
    responses={404: {"description": "Not found"}},
)


@router.post("/info", response_model=VideoResponse)
async def get_video_info(request: VideoRequest):
    """
    YouTube 비디오의 메타데이터와 자막을 가져옵니다.

    - **video_url**: YouTube 비디오 URL (필수)
    - **languages**: 자막 언어 우선순위 목록 (선택, 기본값: ["ko", "en"])
    - **prefer_manual**: 수동 생성 자막 선호 여부 (선택, 기본값: True)
    """
    youtube_service = YouTubeService()

    try:
        # 비디오 정보 가져오기
        result = youtube_service.get_video_info(
            video_url=request.video_url,
            languages=request.languages,
            prefer_manual=request.prefer_manual
        )

        # 응답 생성
        return VideoResponse(
            metadata=VideoMetadata(**result['metadata']),
            transcript=[TranscriptEntry(**entry) for entry in result['transcript']],
            transcript_language=request.languages[0] if request.languages else None
        )

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get video info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get video info: {str(e)}")


@router.post("/scrape", response_model=VideoScrapeResponse)
async def scrape_video(request: VideoScrapeRequest):
    """
    YouTube 비디오를 스크래핑하고 AI 기능을 적용합니다.

    - **video_url**: YouTube 비디오 URL (필수)
    - **languages**: 자막 언어 우선순위 목록
    - **enable_summary**: AI 요약 활성화 여부
    - **enable_translation**: 번역 활성화 여부
    - **enable_topics**: 주제 추출 활성화 여부
    - **output_format**: 출력 형식 (txt, json, xml, markdown)
    """
    youtube_service = YouTubeService()
    ai_service = AIService(
        api_key=settings.gemini_api_key,
        model_name=settings.gemini_model_name
    )
    formatter_service = FormatterService()

    try:
        # 1. 비디오 정보 가져오기
        logger.info(f"Scraping video: {request.video_url}")
        video_info = youtube_service.get_video_info(
            video_url=request.video_url,
            languages=request.languages,
            prefer_manual=request.prefer_manual
        )

        metadata = video_info['metadata']
        transcript = video_info['transcript']

        # 2. AI 기능 적용
        summary = None
        translation = None
        topics = None

        if request.enable_summary:
            logger.info("Generating summary...")
            summary = ai_service.generate_summary(
                transcript=transcript,
                max_points=request.summary_max_points,
                language=request.languages[0] if request.languages else 'ko'
            )

        if request.enable_translation and request.target_language:
            logger.info(f"Translating to {request.target_language}...")
            translation = ai_service.translate_transcript(
                transcript=transcript,
                target_language=request.target_language
            )

        if request.enable_topics:
            logger.info("Extracting topics...")
            topics = ai_service.extract_topics(
                transcript=transcript,
                num_topics=request.num_topics,
                language=request.languages[0] if request.languages else 'ko'
            )

        # 3. 파일로 저장 (선택적)
        output_file = None
        if request.output_format:
            video_title = metadata.get('title', 'video').replace('/', '_')
            output_file = formatter_service.save_to_file(
                metadata=metadata,
                transcript=transcript,
                output_file=f"output/{video_title}",
                format_choice=request.output_format,
                summary=summary,
                translation=translation,
                key_topics=topics
            )
            logger.info(f"Saved to file: {output_file}")

        # 4. 응답 생성
        return VideoScrapeResponse(
            metadata=VideoMetadata(**metadata),
            transcript=[TranscriptEntry(**entry) for entry in transcript],
            transcript_language=request.languages[0] if request.languages else None,
            summary=summary,
            translation=translation,
            key_topics=topics,
            output_file=output_file
        )

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to scrape video: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to scrape video: {str(e)}")


@router.get("/metadata")
async def get_video_metadata(
    video_url: str = Query(..., description="YouTube 비디오 URL")
):
    """
    YouTube 비디오의 메타데이터만 가져옵니다 (자막 제외).

    - **video_url**: YouTube 비디오 URL
    """
    youtube_service = YouTubeService()

    try:
        video_id = youtube_service.extract_video_id(video_url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {video_url}")

        metadata = youtube_service.get_video_metadata(video_id)

        return JSONResponse(content=metadata)

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metadata: {str(e)}")


@router.get("/transcript")
async def get_video_transcript(
    video_url: str = Query(..., description="YouTube 비디오 URL"),
    languages: List[str] = Query(default=["ko", "en"], description="자막 언어 우선순위"),
    prefer_manual: bool = Query(default=True, description="수동 생성 자막 선호 여부")
):
    """
    YouTube 비디오의 자막만 가져옵니다 (메타데이터 제외).

    - **video_url**: YouTube 비디오 URL
    - **languages**: 자막 언어 우선순위 목록
    - **prefer_manual**: 수동 생성 자막 선호 여부
    """
    youtube_service = YouTubeService()

    try:
        video_id = youtube_service.extract_video_id(video_url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {video_url}")

        transcript = youtube_service.get_transcript(
            video_id=video_id,
            languages=languages,
            prefer_manual=prefer_manual
        )

        return JSONResponse(content=transcript)

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get transcript: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get transcript: {str(e)}")
