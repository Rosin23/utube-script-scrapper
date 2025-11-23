"""
플레이리스트 관련 API 라우터
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import logging

from api.schemas.playlist import (
    PlaylistRequest,
    PlaylistResponse,
    PlaylistInfo,
    PlaylistVideoInfo
)
from utils.dependencies import YouTubeServiceDep

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/playlist",
    tags=["playlist"],
    responses={404: {"description": "Not found"}},
)


@router.post("/info", response_model=PlaylistResponse)
async def get_playlist_info(
    request: PlaylistRequest,
    youtube_service: YouTubeServiceDep
):
    """
    YouTube 플레이리스트의 정보와 비디오 목록을 가져옵니다.
    """
    try:
        # 플레이리스트 확인
        if not youtube_service.is_playlist_url(request.playlist_url):
            raise ValueError("Provided URL is not a playlist URL")

        # 플레이리스트 정보 가져오기
        playlist_info_raw = youtube_service.get_playlist_info(request.playlist_url)
        if not playlist_info_raw:
            raise ValueError("Failed to get playlist info")

        # 필드명 정규화 및 안전 처리
        playlist_info_dict = {
            'playlist_id': (
                playlist_info_raw.get('playlist_id') or 
                playlist_info_raw.get('id') or 
                'Unknown'
            ),
            'title': playlist_info_raw.get('title') or 'Unknown Playlist',
            'uploader': playlist_info_raw.get('uploader'),
            'video_count': playlist_info_raw.get('video_count', 0),
            'description': playlist_info_raw.get('description')
        }

        # 비디오 목록 가져오기
        videos = youtube_service.get_playlist_videos(
            playlist_url=request.playlist_url,
            max_videos=request.max_videos
        )

        # 비디오 정보 안전 처리
        video_list = []
        for i, v in enumerate(videos, 1):
            if not isinstance(v, dict):
                logger.warning(f"Invalid video entry at index {i}: {v}")
                continue
            
            # position 정보 추출 (0-based)
            position = v.get('position', i - 1)  # position이 없으면 index-1로 계산
            
            video_list.append(
                PlaylistVideoInfo(
                    video_id=v.get('id', ''),
                    url=v.get('url', ''),
                    title=v.get('title', 'Unknown'),
                    index=i,  # 1-based (사용자 친화적)
                    position=position  # 0-based (API 표준)
                )
            )

        # 응답 생성
        return PlaylistResponse(
            playlist_info=PlaylistInfo(**playlist_info_dict),
            videos=video_list,
            total_videos=playlist_info_dict['video_count'],
            returned_videos=len(video_list)
        )

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get playlist info: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get playlist info: {str(e)}"
        )


@router.get("/check")
async def check_playlist_url(
    youtube_service: YouTubeServiceDep,
    url: str = Query(..., description="확인할 YouTube URL")
):
    """
    URL이 플레이리스트 URL인지 확인합니다.

    - **url**: 확인할 YouTube URL
    """
    try:
        is_playlist = youtube_service.is_playlist_url(url)

        result_type = "unknown"
        if is_playlist:
            result_type = "playlist"
        else:
            video_id = youtube_service.extract_video_id(url)
            if video_id:
                result_type = "video"

        return JSONResponse(content={
            "url": url,
            "is_playlist": is_playlist,
            "type": result_type
        })

    except Exception as e:
        logger.error(f"Failed to check URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check URL: {str(e)}")


@router.get("/videos")
async def get_playlist_videos(
    youtube_service: YouTubeServiceDep,
    playlist_url: str = Query(..., description="YouTube 플레이리스트 URL"),
    max_videos: int = Query(None, ge=1, description="최대 비디오 수")
):
    """
    플레이리스트의 비디오 목록만 가져옵니다.

    - **playlist_url**: YouTube 플레이리스트 URL
    - **max_videos**: 최대 비디오 수 (선택)
    """
    try:
        if not youtube_service.is_playlist_url(playlist_url):
            raise ValueError("Provided URL is not a playlist URL")

        videos = youtube_service.get_playlist_videos(
            playlist_url=playlist_url,
            max_videos=max_videos
        )

        return JSONResponse(content={
            "videos": videos,
            "count": len(videos)
        })

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get playlist videos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get playlist videos: {str(e)}"
        )
