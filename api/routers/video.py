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
from utils.dependencies import (
    YouTubeServiceDep,
    AIServiceDep,
    FormatterServiceDep
)
from utils.metadata import normalize_metadata, validate_metadata

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/video",
    tags=["video"],
    responses={404: {"description": "Not found"}},
)


@router.post("/info", response_model=VideoResponse)
async def get_video_info(
    request: VideoRequest,
    youtube_service: YouTubeServiceDep
):
    """
    YouTube 비디오의 메타데이터와 자막을 가져옵니다.

    - **video_url**: YouTube 비디오 URL (필수)
    - **languages**: 자막 언어 우선순위 목록 (선택, 기본값: ["ko", "en"])
    - **prefer_manual**: 수동 생성 자막 선호 여부 (선택, 기본값: True)
    """
    try:
        # 비디오 정보 가져오기
        result = youtube_service.get_video_info(
            video_url=request.video_url,
            languages=request.languages,
            prefer_manual=request.prefer_manual
        )

        # 응답 생성
        metadata_dict = normalize_metadata(
            result['metadata'],
            video_id=result.get('video_id', '')
        )

        return VideoResponse(
            metadata=validate_metadata(metadata_dict),
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
async def scrape_video(
    request: VideoScrapeRequest,
    youtube_service: YouTubeServiceDep,
    ai_service: AIServiceDep,
    formatter_service: FormatterServiceDep
):
    """
    YouTube 비디오를 스크래핑하고 AI 기능을 적용합니다.

    - **video_url**: YouTube 비디오 URL (필수)
    - **languages**: 자막 언어 우선순위 목록
    - **enable_summary**: AI 요약 활성화 여부
    - **enable_translation**: 번역 활성화 여부
    - **enable_topics**: 주제 추출 활성화 여부
    - **output_format**: 출력 형식 (txt, json, xml, markdown)
    """
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

        # AI 서비스 사용 가능 여부 확인
        ai_available = ai_service.is_available()
        if not ai_available and (request.enable_summary or request.enable_translation or request.enable_topics):
            logger.warning(
                "AI features were requested but AI service is not available. "
                "Please check your Gemini API key configuration."
            )

        # languages 안전 처리
        default_language = 'ko'
        if request.languages and len(request.languages) > 0:
            default_language = request.languages[0]

        if request.enable_summary and ai_available:
            logger.info("Generating summary...")
            try:
                summary = ai_service.generate_summary(
                    transcript=transcript,
                    max_points=request.summary_max_points,
                    language=default_language
                )
            except Exception as e:
                logger.error(f"Failed to generate summary: {e}")
                summary = None

        if request.enable_translation and request.target_language and ai_available:
            logger.info(f"Translating to {request.target_language}...")
            try:
                translation = ai_service.translate_transcript(
                    transcript=transcript,
                    target_language=request.target_language
                )
            except Exception as e:
                logger.error(f"Failed to translate: {e}")
                translation = None

        if request.enable_topics and ai_available:
            logger.info("Extracting topics...")
            try:
                topics = ai_service.extract_topics(
                    transcript=transcript,
                    num_topics=request.num_topics,
                    language=default_language
                )
            except Exception as e:
                logger.error(f"Failed to extract topics: {e}")
                topics = None

        # 3. 파일로 저장 (선택적)
        output_file = None
        if request.output_format:
            try:
                # 안전한 파일명 생성
                video_title = metadata.get('title', 'video')
                if not video_title or video_title.strip() == '':
                    video_title = 'video'
                
                import re
                safe_title = re.sub(r'[<>:"/\\|?*]', '_', video_title)
                safe_title = safe_title.strip()[:100]
                
                video_id = video_info.get('video_id', '')
                if video_id:
                    safe_title = f"{safe_title}_{video_id}"
                
                output_file = formatter_service.save_to_file(
                    metadata=metadata,
                    transcript=transcript,
                    output_file=f"output/{safe_title}",
                    format_choice=request.output_format,
                    summary=summary,
                    translation=translation,
                    key_topics=topics
                )
                logger.info(f"Saved to file: {output_file}")
            except Exception as e:
                logger.error(f"Failed to save file: {e}")
                # 파일 저장 실패해도 응답은 계속 진행
                output_file = None

        # 4. 응답 생성
        metadata_dict = normalize_metadata(
            video_info['metadata'],
            video_id=video_info.get('video_id', '')
        )

        return VideoScrapeResponse(
            metadata=validate_metadata(metadata_dict),
            transcript=[TranscriptEntry(**entry) for entry in transcript],
            transcript_language=default_language,
            summary=summary,
            translation=translation,
            key_topics=topics,
            output_file=output_file
        )

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to scrape video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to scrape video: {str(e)}")


@router.get("/metadata")
async def get_video_metadata(
    youtube_service: YouTubeServiceDep,
    video_url: str = Query(..., description="YouTube 비디오 URL")
):
    """
    YouTube 비디오의 메타데이터만 가져옵니다 (자막 제외).

    - **video_url**: YouTube 비디오 URL
    """
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
    youtube_service: YouTubeServiceDep,
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
