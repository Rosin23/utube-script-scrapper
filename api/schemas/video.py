"""
비디오 관련 Pydantic 스키마

YouTube Data API v3 Field Mappings:
====================================

Legacy Format → YouTube API v3:
- video_id → id
- upload_date → snippet.publishedAt (ISO 8601)
- channel → snippet.channelTitle
- channel_id → snippet.channelId
- duration → contentDetails.duration (ISO 8601)
- view_count → statistics.viewCount (string)
- like_count → statistics.likeCount (string)
- thumbnail_url → snippet.thumbnails.{quality}.url
- tags → snippet.tags
- categories → snippet.categoryId

Reference:
- Videos Resource: https://developers.google.com/youtube/v3/docs/videos
- Video Snippet: https://developers.google.com/youtube/v3/docs/videos#snippet
- ContentDetails: https://developers.google.com/youtube/v3/docs/videos#contentDetails
- Statistics: https://developers.google.com/youtube/v3/docs/videos#statistics
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class VideoRequest(BaseModel):
    """비디오 정보 요청 스키마"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "languages": ["ko", "en"],
                "prefer_manual": True
            }
        }
    )

    video_url: str = Field(..., description="YouTube 비디오 URL")
    languages: List[str] = Field(
        default=["ko", "en"],
        description="자막 언어 우선순위 목록"
    )
    prefer_manual: bool = Field(
        default=True,
        description="수동 생성 자막 선호 여부"
    )


class TranscriptEntry(BaseModel):
    """자막 엔트리 스키마"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start": 0.0,
                "duration": 3.5,
                "text": "안녕하세요",
                "timestamp": "00:00:00"
            }
        }
    )

    start: float = Field(..., description="시작 시간 (초)")
    duration: float = Field(..., description="지속 시간 (초)")
    text: str = Field(..., description="자막 텍스트")
    timestamp: Optional[str] = Field(None, description="HH:MM:SS 형식의 타임스탬프")


class VideoMetadata(BaseModel):
    """
    비디오 메타데이터 스키마

    YouTube Data API v3 Mapping:
    - video_id → id
    - title → snippet.title
    - channel → snippet.channelTitle
    - channel_id → snippet.channelId
    - upload_date → snippet.publishedAt (yt-dlp format: YYYYMMDD)
    - duration → contentDetails.duration (seconds, not ISO 8601 in legacy format)
    - view_count → statistics.viewCount (integer in legacy format)
    - like_count → statistics.likeCount (integer in legacy format)
    - comment_count → statistics.commentCount
    - tags → snippet.tags
    - categories → snippet.categoryId

    Note: Legacy format uses different data types than YouTube API v3.
    Use api_v3_format=True in API calls to get YouTube API v3 compliant responses.

    Reference: https://developers.google.com/youtube/v3/docs/videos#resource
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "title": "Sample Video Title",
                "channel": "Sample Channel",
                "channel_id": "UC1234567890",
                "upload_date": "20230101",
                "duration": 212,
                "view_count": 1000000,
                "like_count": 50000,
                "comment_count": 1200,
                "description": "Sample description",
                "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
                "tags": ["music", "video"],
                "categories": ["10"]
            }
        }
    )

    video_id: str = Field(..., description="YouTube 비디오 ID (YouTube API v3: id)")
    title: str = Field(..., description="비디오 제목 (YouTube API v3: snippet.title)")
    channel: str = Field(..., description="채널 이름 (YouTube API v3: snippet.channelTitle)")
    channel_id: Optional[str] = Field(None, description="채널 ID (YouTube API v3: snippet.channelId)")
    upload_date: Optional[str] = Field(
        None,
        description="업로드 날짜 (yt-dlp format: YYYYMMDD, YouTube API v3: snippet.publishedAt in ISO 8601)"
    )
    duration: Optional[int] = Field(
        None,
        description="비디오 길이 (초). YouTube API v3에서는 ISO 8601 duration (PT#M#S) 형식"
    )
    view_count: Optional[int] = Field(
        None,
        description="조회수 (YouTube API v3: statistics.viewCount as string)"
    )
    like_count: Optional[int] = Field(
        None,
        description="좋아요 수 (YouTube API v3: statistics.likeCount as string)"
    )
    comment_count: Optional[int] = Field(
        None,
        description="댓글 수 (YouTube API v3: statistics.commentCount as string)"
    )
    description: Optional[str] = Field(
        None,
        description="비디오 설명 (YouTube API v3: snippet.description)"
    )
    thumbnail_url: Optional[str] = Field(
        None,
        description="썸네일 URL (YouTube API v3: snippet.thumbnails.{quality}.url)"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="태그 목록 (YouTube API v3: snippet.tags)"
    )
    categories: Optional[List[str]] = Field(
        None,
        description="카테고리 ID 목록 (YouTube API v3: snippet.categoryId)"
    )


class VideoResponse(BaseModel):
    """비디오 정보 응답 스키마"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metadata": {
                    "video_id": "dQw4w9WgXcQ",
                    "title": "Sample Video",
                    "channel": "Sample Channel",
                    "duration": 212,
                    "view_count": 1000000
                },
                "transcript": [
                    {
                        "start": 0.0,
                        "duration": 3.5,
                        "text": "안녕하세요",
                        "timestamp": "00:00:00"
                    }
                ],
                "transcript_language": "ko"
            }
        }
    )

    metadata: VideoMetadata
    transcript: List[TranscriptEntry]
    transcript_language: Optional[str] = Field(None, description="자막 언어 코드")


class VideoScrapeRequest(BaseModel):
    """비디오 스크래핑 요청 스키마 (AI 기능 포함)"""
    video_url: str = Field(..., description="YouTube 비디오 URL")
    languages: List[str] = Field(
        default=["ko", "en"],
        description="자막 언어 우선순위 목록"
    )
    prefer_manual: bool = Field(
        default=True,
        description="수동 생성 자막 선호 여부"
    )
    enable_summary: bool = Field(
        default=False,
        description="AI 요약 활성화 여부"
    )
    summary_max_points: int = Field(
        default=5,
        ge=1,
        le=10,
        description="요약 포인트 수 (1-10)"
    )
    enable_translation: bool = Field(
        default=False,
        description="번역 활성화 여부"
    )
    target_language: Optional[str] = Field(
        None,
        description="번역 대상 언어 코드"
    )
    enable_topics: bool = Field(
        default=False,
        description="주제 추출 활성화 여부"
    )
    num_topics: int = Field(
        default=5,
        ge=1,
        le=20,
        description="추출할 주제 수 (1-20)"
    )
    output_format: str = Field(
        default="json",
        description="출력 형식 (txt, json, xml, markdown)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "languages": ["ko", "en"],
                "prefer_manual": True,
                "enable_summary": True,
                "summary_max_points": 5,
                "enable_translation": True,
                "target_language": "en",
                "enable_topics": True,
                "num_topics": 5,
                "output_format": "json"
            }
        }
    )


class VideoScrapeResponse(BaseModel):
    """비디오 스크래핑 응답 스키마"""
    metadata: VideoMetadata
    transcript: List[TranscriptEntry]
    transcript_language: Optional[str] = None
    summary: Optional[str] = None
    translation: Optional[str] = None
    key_topics: Optional[List[str]] = None
    output_file: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metadata": {
                    "video_id": "dQw4w9WgXcQ",
                    "title": "Sample Video",
                    "channel": "Sample Channel"
                },
                "transcript": [
                    {
                        "start": 0.0,
                        "duration": 3.5,
                        "text": "안녕하세요",
                        "timestamp": "00:00:00"
                    }
                ],
                "transcript_language": "ko",
                "summary": "This is a summary...",
                "translation": "This is a translation...",
                "key_topics": ["Topic 1", "Topic 2"],
                "output_file": "output.json"
            }
        }
    )
