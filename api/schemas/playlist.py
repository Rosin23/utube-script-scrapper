"""
플레이리스트 관련 Pydantic 스키마

YouTube Data API v3 Field Mappings:
====================================

Playlist Resource:
- playlist_id → id
- title → snippet.title
- uploader → snippet.channelTitle
- uploader_id/channel_id → snippet.channelId
- video_count → contentDetails.itemCount
- description → snippet.description

PlaylistItem Resource:
- video_id (in dict) → snippet.resourceId.videoId
- position → snippet.position (0-based)
- playlistId → snippet.playlistId

Reference:
- Playlists: https://developers.google.com/youtube/v3/docs/playlists
- PlaylistItems: https://developers.google.com/youtube/v3/docs/playlistItems
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict


class PlaylistRequest(BaseModel):
    """플레이리스트 정보 요청 스키마"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "playlist_url": "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
                "max_videos": 10
            }
        }
    )

    playlist_url: str = Field(..., description="YouTube 플레이리스트 URL")
    max_videos: Optional[int] = Field(
        None,
        ge=1,
        description="처리할 최대 비디오 수 (제한 없음: None)"
    )


class PlaylistVideoInfo(BaseModel):
    """
    플레이리스트 내 비디오 정보 스키마

    YouTube Data API v3 Mapping (PlaylistItem):
    - video_id → snippet.resourceId.videoId OR contentDetails.videoId
    - url → Constructed from video_id
    - title → snippet.title
    - position → snippet.position (0-based per API spec)

    Note: index is 1-based for user display, position is 0-based per YouTube API v3 spec.

    Reference: https://developers.google.com/youtube/v3/docs/playlistItems#resource
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "title": "Sample Video",
                "index": 1,
                "position": 0  # 0-based position (YouTube API v3 표준)
            }
        }
    )

    video_id: str = Field(
        ...,
        description="비디오 ID (YouTube API v3: snippet.resourceId.videoId)"
    )
    url: str = Field(..., description="비디오 URL (Constructed from video_id)")
    title: str = Field(..., description="비디오 제목 (YouTube API v3: snippet.title)")
    index: Optional[int] = Field(
        None,
        description="플레이리스트 내 순서 (1-based, 사용자 친화적 표시용)"
    )
    position: Optional[int] = Field(
        None,
        description="플레이리스트 내 위치 (0-based, YouTube API v3 표준: snippet.position)"
    )


class PlaylistInfo(BaseModel):
    """
    플레이리스트 메타데이터 스키마

    YouTube Data API v3 Mapping:
    - playlist_id → id
    - title → snippet.title
    - uploader → snippet.channelTitle
    - uploader_id/channel_id → snippet.channelId
    - video_count → contentDetails.itemCount
    - description → snippet.description

    Reference: https://developers.google.com/youtube/v3/docs/playlists#resource
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "playlist_id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
                "title": "Sample Playlist",
                "uploader": "Sample Channel",
                "uploader_id": "UC1234567890",
                "video_count": 50,
                "description": "This is a sample playlist"
            }
        }
    )

    playlist_id: str = Field(
        ...,
        description="플레이리스트 ID (YouTube API v3: id)"
    )
    title: str = Field(
        ...,
        description="플레이리스트 제목 (YouTube API v3: snippet.title)"
    )
    uploader: Optional[str] = Field(
        None,
        description="업로더 이름 (YouTube API v3: snippet.channelTitle)"
    )
    uploader_id: Optional[str] = Field(
        None,
        description="업로더 ID (YouTube API v3: snippet.channelId)"
    )
    video_count: int = Field(
        ...,
        description="총 비디오 수 (YouTube API v3: contentDetails.itemCount)"
    )
    description: Optional[str] = Field(
        None,
        description="플레이리스트 설명 (YouTube API v3: snippet.description)"
    )


class PlaylistResponse(BaseModel):
    """플레이리스트 응답 스키마"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "playlist_info": {
                    "playlist_id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
                    "title": "Sample Playlist",
                    "uploader": "Sample Channel",
                    "video_count": 50
                },
                "videos": [
                    {
                        "video_id": "dQw4w9WgXcQ",
                        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        "title": "Sample Video",
                        "index": 1
                    }
                ],
                "total_videos": 50,
                "returned_videos": 10
            }
        }
    )

    playlist_info: PlaylistInfo
    videos: List[PlaylistVideoInfo]
    total_videos: int = Field(..., description="전체 비디오 수")
    returned_videos: int = Field(..., description="반환된 비디오 수")
