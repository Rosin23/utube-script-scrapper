"""
재생목록 핸들러 모듈 테스트
"""

import pytest
from unittest.mock import Mock, patch
from legacy.playlist_handler import PlaylistHandler, process_playlist_or_video


class TestPlaylistHandler:
    """PlaylistHandler 클래스 테스트"""

    def test_is_playlist_url_valid_playlist(self):
        """유효한 재생목록 URL 감지 테스트"""
        urls = [
            "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
            "https://www.youtube.com/watch?v=VIDEO_ID&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
            "https://youtube.com/playlist?list=PLtest123"
        ]

        for url in urls:
            assert PlaylistHandler.is_playlist_url(url) is True

    def test_is_playlist_url_single_video(self):
        """단일 비디오 URL이 재생목록이 아님을 확인하는 테스트"""
        urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ"
        ]

        for url in urls:
            assert PlaylistHandler.is_playlist_url(url) is False

    def test_extract_playlist_id(self):
        """재생목록 ID 추출 테스트"""
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        playlist_id = PlaylistHandler.extract_playlist_id(url)
        assert playlist_id == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"

    def test_extract_playlist_id_from_watch_url(self):
        """watch URL에서 재생목록 ID 추출 테스트"""
        url = "https://www.youtube.com/watch?v=VIDEO_ID&list=PLtest123"
        playlist_id = PlaylistHandler.extract_playlist_id(url)
        assert playlist_id == "PLtest123"

    def test_extract_playlist_id_no_playlist(self):
        """재생목록 ID가 없는 URL에서 None 반환 테스트"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        playlist_id = PlaylistHandler.extract_playlist_id(url)
        assert playlist_id is None

    @patch('playlist_handler.yt_dlp.YoutubeDL')
    def test_get_playlist_info(self, mock_ydl_class):
        """재생목록 정보 가져오기 테스트"""
        # Mock 데이터 설정
        mock_info = {
            '_type': 'playlist',
            'id': 'PLtest123',
            'title': 'Test Playlist',
            'uploader': 'Test Channel',
            'entries': [
                {'id': 'video1', 'title': 'Video 1'},
                {'id': 'video2', 'title': 'Video 2'}
            ]
        }

        mock_ydl = Mock()
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        url = "https://www.youtube.com/playlist?list=PLtest123"
        result = PlaylistHandler.get_playlist_info(url)

        assert result['id'] == 'PLtest123'
        assert result['title'] == 'Test Playlist'
        assert result['uploader'] == 'Test Channel'
        assert result['video_count'] == 2
        assert len(result['entries']) == 2

    @patch('playlist_handler.yt_dlp.YoutubeDL')
    def test_get_playlist_info_not_playlist(self, mock_ydl_class):
        """재생목록이 아닌 URL로 None 반환 테스트"""
        mock_info = {'_type': 'video'}

        mock_ydl = Mock()
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        url = "https://www.youtube.com/watch?v=VIDEO_ID"
        result = PlaylistHandler.get_playlist_info(url)

        assert result is None

    @patch('playlist_handler.yt_dlp.YoutubeDL')
    def test_get_video_urls_from_playlist(self, mock_ydl_class):
        """재생목록에서 비디오 URL 추출 테스트"""
        mock_info = {
            '_type': 'playlist',
            'id': 'PLtest123',
            'title': 'Test Playlist',
            'uploader': 'Test Channel',
            'entries': [
                {'id': 'video1', 'title': 'Video 1'},
                {'id': 'video2', 'title': 'Video 2'},
                None,  # None 항목도 처리해야 함
                {'id': 'video3', 'title': 'Video 3'}
            ]
        }

        mock_ydl = Mock()
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        url = "https://www.youtube.com/playlist?list=PLtest123"
        videos = PlaylistHandler.get_video_urls_from_playlist(url)

        assert len(videos) == 3  # None은 제외됨
        assert videos[0]['id'] == 'video1'
        assert videos[0]['url'] == 'https://www.youtube.com/watch?v=video1'
        assert videos[0]['title'] == 'Video 1'

    @patch('playlist_handler.yt_dlp.YoutubeDL')
    def test_get_playlist_metadata(self, mock_ydl_class):
        """재생목록 메타데이터 가져오기 테스트"""
        mock_info = {
            '_type': 'playlist',
            'id': 'PLtest123',
            'title': 'Test Playlist',
            'uploader': 'Test Channel',
            'entries': [
                {'id': 'video1'},
                {'id': 'video2'}
            ]
        }

        mock_ydl = Mock()
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        url = "https://www.youtube.com/playlist?list=PLtest123"
        metadata = PlaylistHandler.get_playlist_metadata(url)

        assert metadata['title'] == 'Test Playlist'
        assert metadata['uploader'] == 'Test Channel'
        assert metadata['video_count'] == 2


class TestProcessPlaylistOrVideo:
    """process_playlist_or_video 함수 테스트"""

    @patch('playlist_handler.PlaylistHandler')
    def test_process_playlist(self, mock_handler_class):
        """재생목록 URL 처리 테스트"""
        mock_handler = Mock()
        mock_handler.is_playlist_url.return_value = True
        mock_handler.get_video_urls_from_playlist.return_value = [
            {'id': 'video1', 'url': 'url1', 'title': 'Video 1'}
        ]
        mock_handler.get_playlist_metadata.return_value = {
            'title': 'Test Playlist',
            'uploader': 'Test Channel',
            'video_count': 1
        }
        mock_handler_class.return_value = mock_handler

        url = "https://www.youtube.com/playlist?list=PLtest123"
        result = process_playlist_or_video(url)

        assert result['type'] == 'playlist'
        assert len(result['videos']) == 1
        assert result['playlist_info']['title'] == 'Test Playlist'

    @patch('playlist_handler.PlaylistHandler')
    @patch('youtube_api.extract_video_id')
    def test_process_single_video(self, mock_extract_id, mock_handler_class):
        """단일 비디오 URL 처리 테스트"""
        mock_handler = Mock()
        mock_handler.is_playlist_url.return_value = False
        mock_handler_class.return_value = mock_handler
        mock_extract_id.return_value = 'VIDEO_ID'

        url = "https://www.youtube.com/watch?v=VIDEO_ID"
        result = process_playlist_or_video(url)

        assert result['type'] == 'video'
        assert len(result['videos']) == 1
        assert result['videos'][0]['id'] == 'VIDEO_ID'
        assert result['playlist_info'] is None

    @patch('playlist_handler.PlaylistHandler')
    @patch('youtube_api.extract_video_id')
    def test_process_unknown_url(self, mock_extract_id, mock_handler_class):
        """잘못된 URL 처리 테스트"""
        mock_handler = Mock()
        mock_handler.is_playlist_url.return_value = False
        mock_handler_class.return_value = mock_handler
        mock_extract_id.return_value = None

        url = "https://invalid-url.com"
        result = process_playlist_or_video(url)

        assert result['type'] == 'unknown'
        assert len(result['videos']) == 0
        assert result['playlist_info'] is None
