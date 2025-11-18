"""
YouTube API 모듈 단위 테스트
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from youtube_api import (
    extract_video_id,
    format_timestamp,
    get_video_metadata,
    get_transcript_with_timestamps
)


class TestExtractVideoId:
    """extract_video_id 함수 테스트"""

    def test_extract_from_watch_url(self):
        """youtube.com/watch?v=VIDEO_ID 형식 테스트"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_extract_from_short_url(self):
        """youtu.be/VIDEO_ID 형식 테스트"""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_extract_from_embed_url(self):
        """youtube.com/embed/VIDEO_ID 형식 테스트"""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_extract_from_v_url(self):
        """youtube.com/v/VIDEO_ID 형식 테스트"""
        url = "https://www.youtube.com/v/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_extract_with_additional_params(self):
        """추가 파라미터가 있는 URL 테스트"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_extract_invalid_url(self):
        """잘못된 URL 테스트"""
        url = "https://www.google.com"
        assert extract_video_id(url) is None

    def test_extract_empty_url(self):
        """빈 URL 테스트"""
        url = ""
        assert extract_video_id(url) is None


class TestFormatTimestamp:
    """format_timestamp 함수 테스트"""

    def test_format_seconds_only(self):
        """초만 있는 경우 테스트"""
        assert format_timestamp(45) == "00:45"

    def test_format_minutes_and_seconds(self):
        """분과 초가 있는 경우 테스트"""
        assert format_timestamp(125) == "02:05"

    def test_format_hours_minutes_seconds(self):
        """시, 분, 초가 있는 경우 테스트"""
        assert format_timestamp(3661) == "01:01:01"

    def test_format_zero_seconds(self):
        """0초 테스트"""
        assert format_timestamp(0) == "00:00"

    def test_format_large_value(self):
        """큰 값 테스트"""
        assert format_timestamp(7200) == "02:00:00"

    def test_format_decimal_seconds(self):
        """소수점이 있는 초 테스트"""
        assert format_timestamp(125.5) == "02:05"


class TestGetVideoMetadata:
    """get_video_metadata 함수 테스트"""

    @patch('youtube_api.yt_dlp.YoutubeDL')
    def test_get_metadata_success(self, mock_ytdl):
        """메타데이터 추출 성공 테스트"""
        # Mock 설정
        mock_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_instance
        mock_instance.extract_info.return_value = {
            'title': 'Test Video',
            'description': 'Test Description',
            'channel': 'Test Channel',
            'upload_date': '20240101',
            'duration': 630,
            'view_count': 1000000
        }

        # 테스트 실행
        metadata = get_video_metadata("https://www.youtube.com/watch?v=test")

        # 검증
        assert metadata['title'] == 'Test Video'
        assert metadata['description'] == 'Test Description'
        assert metadata['channel'] == 'Test Channel'
        assert metadata['upload_date'] == '20240101'
        assert metadata['duration'] == 630
        assert metadata['view_count'] == 1000000

    @patch('youtube_api.yt_dlp.YoutubeDL')
    def test_get_metadata_missing_fields(self, mock_ytdl):
        """일부 필드가 없는 경우 테스트"""
        # Mock 설정
        mock_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_instance
        mock_instance.extract_info.return_value = {}

        # 테스트 실행
        metadata = get_video_metadata("https://www.youtube.com/watch?v=test")

        # 검증 - 기본값이 설정되어야 함
        assert metadata['title'] == 'Unknown Title'
        assert metadata['description'] == 'No description available'
        assert metadata['channel'] == 'Unknown Channel'
        assert metadata['upload_date'] == 'Unknown Date'
        assert metadata['duration'] == 0
        assert metadata['view_count'] == 0

    @patch('youtube_api.yt_dlp.YoutubeDL')
    def test_get_metadata_exception(self, mock_ytdl):
        """예외 발생 시 테스트"""
        # Mock 설정
        mock_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_instance
        mock_instance.extract_info.side_effect = Exception("Network error")

        # 테스트 실행
        metadata = get_video_metadata("https://www.youtube.com/watch?v=test")

        # 검증 - 기본값이 반환되어야 함
        assert metadata['title'] == 'Unknown Title'
        assert metadata['channel'] == 'Unknown Channel'


class TestGetTranscriptWithTimestamps:
    """get_transcript_with_timestamps 함수 테스트"""

    @patch('youtube_api.YouTubeTranscriptApi')
    def test_get_transcript_success_old_api(self, mock_api):
        """구버전 API로 자막 추출 성공 테스트"""
        # Mock 설정
        mock_api.get_transcript.return_value = [
            {'start': 0.0, 'duration': 2.5, 'text': 'Hello'},
            {'start': 2.5, 'duration': 3.0, 'text': 'World'}
        ]

        # 테스트 실행
        transcript = get_transcript_with_timestamps('test_video_id')

        # 검증
        assert len(transcript) == 2
        assert transcript[0]['text'] == 'Hello'
        assert transcript[1]['text'] == 'World'

    @patch('youtube_api.YouTubeTranscriptApi')
    def test_get_transcript_no_available(self, mock_api):
        """자막이 없는 경우 테스트"""
        # Mock 설정 - 모든 메서드가 실패하도록
        mock_api.get_transcript.side_effect = Exception("No transcript")

        # 테스트 실행
        transcript = get_transcript_with_timestamps('test_video_id')

        # 검증 - 빈 리스트가 반환되어야 함
        assert transcript == []

    @patch('youtube_api.YouTubeTranscriptApi')
    def test_get_transcript_with_language_preference(self, mock_api):
        """언어 선호도를 사용한 자막 추출 테스트"""
        # Mock 설정
        mock_api.get_transcript.return_value = [
            {'start': 0.0, 'duration': 2.5, 'text': '안녕하세요'}
        ]

        # 테스트 실행
        transcript = get_transcript_with_timestamps('test_video_id', languages=['ko', 'en'])

        # 검증
        assert len(transcript) == 1
        assert transcript[0]['text'] == '안녕하세요'
