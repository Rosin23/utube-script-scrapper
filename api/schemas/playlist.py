"""
플레이리스트 관련 Pydantic 스키마
"""

from typing import Optional, List
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
    """플레이리스트 내 비디오 정보 스키마"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "title": "Sample Video",
                "index": 1
            }
        }
    )

    video_id: str = Field(..., description="비디오 ID")
    url: str = Field(..., description="비디오 URL")
    title: str = Field(..., description="비디오 제목")
    index: Optional[int] = Field(None, description="플레이리스트 내 순서")


class PlaylistInfo(BaseModel):
    """플레이리스트 메타데이터 스키마"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "playlist_id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
                "title": "Sample Playlist",
                "uploader": "Sample Channel",
                "video_count": 50,
                "description": "This is a sample playlist"
            }
        }
    )

    playlist_id: str = Field(..., description="플레이리스트 ID")
    title: str = Field(..., description="플레이리스트 제목")
    uploader: Optional[str] = Field(None, description="업로더 이름")
    video_count: int = Field(..., description="총 비디오 수")
    description: Optional[str] = Field(None, description="플레이리스트 설명")


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
