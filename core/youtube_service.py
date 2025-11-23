"""
YouTube 서비스
YouTube 데이터 추출 및 처리를 위한 서비스 레이어

YouTube Data API v3 Support:
- 모든 메서드는 api_v3_format 파라미터 지원
- YouTube Data API v3 표준 형식으로 응답 가능
- 필드 매핑 및 변환은 youtube_api_mapper 사용

Reference: https://developers.google.com/youtube/v3/docs
"""

from typing import Optional, List, Dict
import logging

from youtube_api import (
    extract_video_id,
    get_video_metadata,
    get_transcript_with_timestamps,
    format_timestamp
)
from playlist_handler import PlaylistHandler, process_playlist_or_video
from utils.youtube_api_mapper import YouTubeAPIMapper

logger = logging.getLogger(__name__)


class YouTubeService:
    """
    YouTube 데이터 추출 서비스

    비디오 및 플레이리스트 메타데이터, 자막 추출 기능을 제공합니다.
    """

    def __init__(self):
        """서비스 초기화"""
        self.playlist_handler = PlaylistHandler()

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        URL에서 비디오 ID를 추출합니다.

        Args:
            url: YouTube 비디오 URL

        Returns:
            비디오 ID 또는 None
        """
        return extract_video_id(url)

    def get_video_metadata(self, video_id: str, api_v3_format: bool = False) -> Dict:
        """
        비디오 메타데이터를 가져옵니다.

        Args:
            video_id: YouTube 비디오 ID
            api_v3_format: True이면 YouTube Data API v3 호환 형식으로 반환

        Returns:
            메타데이터 딕셔너리 (VideoMetadata 스키마와 일치)

        Reference:
            https://developers.google.com/youtube/v3/docs/videos#resource
        """
        try:
            # video_id를 URL로 변환
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            metadata = get_video_metadata(video_url, api_v3_format=api_v3_format)

            # Legacy format: video_id가 없으면 추가
            if not api_v3_format:
                if 'video_id' not in metadata or not metadata['video_id']:
                    metadata['video_id'] = video_id

            logger.info(f"Successfully retrieved metadata for video {video_id}")
            return metadata
        except Exception as e:
            logger.error(f"Failed to get metadata for video {video_id}: {e}")
            raise

    def get_transcript(
        self,
        video_id: str,
        languages: List[str] = None,
        prefer_manual: bool = True
    ) -> List[Dict]:
        """
        비디오 자막을 가져옵니다.

        Args:
            video_id: YouTube 비디오 ID
            languages: 자막 언어 우선순위 목록
            prefer_manual: 수동 생성 자막 선호 여부

        Returns:
            타임스탬프가 포함된 자막 리스트

        Raises:
            Exception: 자막 추출 실패 시
        """
        if languages is None:
            languages = ["ko", "en"]

        try:
            transcript = get_transcript_with_timestamps(
                video_id,
                languages=languages,
                prefer_manual=prefer_manual
            )

            # 타임스탬프 포맷팅 추가
            for entry in transcript:
                if 'timestamp' not in entry or entry['timestamp'] is None:
                    entry['timestamp'] = format_timestamp(entry['start'])

            logger.info(f"Successfully retrieved transcript for video {video_id}")
            return transcript
        except Exception as e:
            logger.error(f"Failed to get transcript for video {video_id}: {e}")
            raise

    def get_video_info(
        self,
        video_url: str,
        languages: List[str] = None,
        prefer_manual: bool = True,
        api_v3_format: bool = False
    ) -> Dict:
        """
        비디오의 전체 정보를 가져옵니다 (메타데이터 + 자막).

        Args:
            video_url: YouTube 비디오 URL
            languages: 자막 언어 우선순위 목록
            prefer_manual: 수동 생성 자막 선호 여부
            api_v3_format: True이면 YouTube Data API v3 호환 형식으로 반환

        Returns:
            메타데이터와 자막을 포함한 딕셔너리

        Raises:
            ValueError: 유효하지 않은 URL
            Exception: 데이터 추출 실패 시
        """
        if languages is None:
            languages = ["ko", "en"]

        # 비디오 ID 추출
        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {video_url}")

        # 메타데이터 및 자막 가져오기
        metadata = self.get_video_metadata(video_id, api_v3_format=api_v3_format)
        transcript = self.get_transcript(video_id, languages, prefer_manual)

        return {
            'metadata': metadata,
            'transcript': transcript,
            'video_id': video_id
        }

    def is_playlist_url(self, url: str) -> bool:
        """
        URL이 플레이리스트 URL인지 확인합니다.

        Args:
            url: YouTube URL

        Returns:
            플레이리스트 URL이면 True
        """
        return self.playlist_handler.is_playlist_url(url)

    def get_playlist_info(self, playlist_url: str, api_v3_format: bool = False) -> Optional[Dict]:
        """
        플레이리스트 정보를 가져옵니다.

        Args:
            playlist_url: YouTube 플레이리스트 URL
            api_v3_format: True이면 YouTube Data API v3 호환 형식으로 반환

        Returns:
            플레이리스트 정보 딕셔너리 또는 None

        Reference:
            https://developers.google.com/youtube/v3/docs/playlists#resource
        """
        try:
            info = self.playlist_handler.get_playlist_info(playlist_url, api_v3_format=api_v3_format)
            logger.info(f"Successfully retrieved playlist info for {playlist_url}")
            return info
        except Exception as e:
            logger.error(f"Failed to get playlist info: {e}")
            return None

    def get_playlist_videos(
        self,
        playlist_url: str,
        max_videos: Optional[int] = None,
        api_v3_format: bool = False
    ) -> List[Dict]:
        """
        플레이리스트의 비디오 목록을 가져옵니다.

        Args:
            playlist_url: YouTube 플레이리스트 URL
            max_videos: 최대 비디오 수 제한
            api_v3_format: True이면 YouTube Data API v3 호환 형식으로 반환

        Returns:
            비디오 정보 리스트

        Raises:
            Exception: 플레이리스트 추출 실패 시

        Reference:
            https://developers.google.com/youtube/v3/docs/playlistItems#resource
        """
        try:
            videos = self.playlist_handler.get_video_urls_from_playlist(
                playlist_url,
                api_v3_format=api_v3_format
            )

            if max_videos and max_videos > 0:
                videos = videos[:max_videos]

            logger.info(f"Retrieved {len(videos)} videos from playlist")
            return videos
        except Exception as e:
            logger.error(f"Failed to get playlist videos: {e}")
            raise

    def process_url(self, url: str) -> Dict:
        """
        URL을 분석하여 비디오 또는 플레이리스트 정보를 반환합니다.

        Args:
            url: YouTube URL

        Returns:
            타입, 비디오 목록, 플레이리스트 정보를 포함한 딕셔너리
        """
        try:
            result = process_playlist_or_video(url)
            logger.info(f"Processed URL type: {result['type']}")
            return result
        except Exception as e:
            logger.error(f"Failed to process URL {url}: {e}")
            raise
