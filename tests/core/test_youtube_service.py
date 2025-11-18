"""
YouTube 서비스 테스트
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from core.youtube_service import YouTubeService


class TestYouTubeService:
    """YouTube 서비스 테스트"""

    def test_initialization(self):
        """서비스 초기화 테스트"""
        service = YouTubeService()
        assert service is not None
        assert service.playlist_handler is not None

    @patch('core.youtube_service.extract_video_id')
    def test_extract_video_id_success(self, mock_extract):
        """비디오 ID 추출 성공 테스트"""
        mock_extract.return_value = "dQw4w9WgXcQ"
        service = YouTubeService()

        video_id = service.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        assert video_id == "dQw4w9WgXcQ"
        mock_extract.assert_called_once()

    @patch('core.youtube_service.get_video_metadata')
    def test_get_video_metadata_success(self, mock_metadata):
        """비디오 메타데이터 가져오기 성공 테스트"""
        mock_metadata.return_value = {
            'video_id': 'test123',
            'title': 'Test Video',
            'channel': 'Test Channel'
        }
        service = YouTubeService()

        metadata = service.get_video_metadata('test123')

        assert metadata['video_id'] == 'test123'
        assert metadata['title'] == 'Test Video'
        mock_metadata.assert_called_once_with('test123')

    @patch('core.youtube_service.get_transcript_with_timestamps')
    @patch('core.youtube_service.format_timestamp')
    def test_get_transcript_success(self, mock_format, mock_transcript):
        """자막 가져오기 성공 테스트"""
        mock_transcript.return_value = [
            {'start': 0.0, 'duration': 3.0, 'text': 'Hello'}
        ]
        mock_format.return_value = "00:00:00"
        service = YouTubeService()

        transcript = service.get_transcript('test123', languages=['en'])

        assert len(transcript) == 1
        assert transcript[0]['text'] == 'Hello'
        assert 'timestamp' in transcript[0]

    @patch('core.youtube_service.extract_video_id')
    @patch('core.youtube_service.get_video_metadata')
    @patch('core.youtube_service.get_transcript_with_timestamps')
    def test_get_video_info_success(self, mock_transcript, mock_metadata, mock_extract):
        """비디오 전체 정보 가져오기 성공 테스트"""
        mock_extract.return_value = "test123"
        mock_metadata.return_value = {'video_id': 'test123', 'title': 'Test'}
        mock_transcript.return_value = [
            {'start': 0.0, 'duration': 3.0, 'text': 'Hello', 'timestamp': '00:00:00'}
        ]
        service = YouTubeService()

        result = service.get_video_info("https://www.youtube.com/watch?v=test123")

        assert 'metadata' in result
        assert 'transcript' in result
        assert 'video_id' in result
        assert result['video_id'] == 'test123'

    @patch('core.youtube_service.extract_video_id')
    def test_get_video_info_invalid_url(self, mock_extract):
        """유효하지 않은 URL로 비디오 정보 가져오기 실패 테스트"""
        mock_extract.return_value = None
        service = YouTubeService()

        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            service.get_video_info("invalid_url")

    def test_is_playlist_url(self):
        """플레이리스트 URL 확인 테스트"""
        service = YouTubeService()

        # 플레이리스트 URL
        assert service.is_playlist_url(
            "https://www.youtube.com/playlist?list=PLtest"
        )

        # 비디오 URL
        assert not service.is_playlist_url(
            "https://www.youtube.com/watch?v=test123"
        )

    @patch('core.youtube_service.PlaylistHandler')
    def test_get_playlist_info_success(self, mock_handler_class):
        """플레이리스트 정보 가져오기 성공 테스트"""
        mock_handler = Mock()
        mock_handler.get_playlist_info.return_value = {
            'title': 'Test Playlist',
            'video_count': 10
        }
        mock_handler_class.return_value = mock_handler

        service = YouTubeService()
        info = service.get_playlist_info("https://www.youtube.com/playlist?list=PLtest")

        assert info is not None
        assert info['title'] == 'Test Playlist'
        assert info['video_count'] == 10

    @patch('core.youtube_service.PlaylistHandler')
    def test_get_playlist_videos_success(self, mock_handler_class):
        """플레이리스트 비디오 목록 가져오기 성공 테스트"""
        mock_handler = Mock()
        mock_handler.get_video_urls_from_playlist.return_value = [
            {'id': 'video1', 'url': 'url1', 'title': 'Video 1'},
            {'id': 'video2', 'url': 'url2', 'title': 'Video 2'},
            {'id': 'video3', 'url': 'url3', 'title': 'Video 3'},
        ]
        mock_handler_class.return_value = mock_handler

        service = YouTubeService()
        videos = service.get_playlist_videos(
            "https://www.youtube.com/playlist?list=PLtest",
            max_videos=2
        )

        assert len(videos) == 2
        assert videos[0]['id'] == 'video1'
