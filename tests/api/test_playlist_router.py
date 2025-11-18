"""
Playlist 라우터 테스트
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from api_main import app

client = TestClient(app)


class TestPlaylistRouter:
    """Playlist 라우터 테스트"""

    @patch('api.routers.playlist.YouTubeService')
    def test_check_playlist_url_is_playlist(self, mock_service_class):
        """플레이리스트 URL 확인 테스트 - 플레이리스트인 경우"""
        mock_service = Mock()
        mock_service.is_playlist_url.return_value = True
        mock_service_class.return_value = mock_service

        response = client.get(
            "/playlist/check",
            params={"url": "https://www.youtube.com/playlist?list=PLtest"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['is_playlist'] is True
        assert data['type'] == 'playlist'

    @patch('api.routers.playlist.YouTubeService')
    def test_check_playlist_url_is_video(self, mock_service_class):
        """플레이리스트 URL 확인 테스트 - 비디오인 경우"""
        mock_service = Mock()
        mock_service.is_playlist_url.return_value = False
        mock_service.extract_video_id.return_value = "test123"
        mock_service_class.return_value = mock_service

        response = client.get(
            "/playlist/check",
            params={"url": "https://www.youtube.com/watch?v=test123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['is_playlist'] is False
        assert data['type'] == 'video'

    @patch('api.routers.playlist.YouTubeService')
    def test_get_playlist_videos_success(self, mock_service_class):
        """플레이리스트 비디오 목록 가져오기 성공 테스트"""
        mock_service = Mock()
        mock_service.is_playlist_url.return_value = True
        mock_service.get_playlist_videos.return_value = [
            {'id': 'video1', 'url': 'url1', 'title': 'Video 1'},
            {'id': 'video2', 'url': 'url2', 'title': 'Video 2'}
        ]
        mock_service_class.return_value = mock_service

        response = client.get(
            "/playlist/videos",
            params={"playlist_url": "https://www.youtube.com/playlist?list=PLtest"}
        )

        assert response.status_code == 200
        data = response.json()
        assert 'videos' in data
        assert len(data['videos']) == 2
        assert data['count'] == 2

    @patch('api.routers.playlist.YouTubeService')
    def test_get_playlist_videos_not_playlist(self, mock_service_class):
        """플레이리스트가 아닌 URL로 비디오 목록 가져오기 실패 테스트"""
        mock_service = Mock()
        mock_service.is_playlist_url.return_value = False
        mock_service_class.return_value = mock_service

        response = client.get(
            "/playlist/videos",
            params={"playlist_url": "https://www.youtube.com/watch?v=test123"}
        )

        assert response.status_code == 400

    @patch('api.routers.playlist.YouTubeService')
    def test_get_playlist_videos_with_limit(self, mock_service_class):
        """최대 비디오 수 제한하여 가져오기 테스트"""
        mock_service = Mock()
        mock_service.is_playlist_url.return_value = True
        mock_service.get_playlist_videos.return_value = [
            {'id': f'video{i}', 'url': f'url{i}', 'title': f'Video {i}'}
            for i in range(5)
        ]
        mock_service_class.return_value = mock_service

        response = client.get(
            "/playlist/videos",
            params={
                "playlist_url": "https://www.youtube.com/playlist?list=PLtest",
                "max_videos": 5
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data['videos']) == 5
