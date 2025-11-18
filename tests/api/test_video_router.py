"""
비디오 라우터 테스트
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from api_main import app

client = TestClient(app)


class TestVideoRouter:
    """비디오 라우터 테스트"""

    @patch('api.routers.video.YouTubeService')
    def test_get_video_metadata_success(self, mock_service_class):
        """비디오 메타데이터 가져오기 성공 테스트"""
        mock_service = Mock()
        mock_service.extract_video_id.return_value = "test123"
        mock_service.get_video_metadata.return_value = {
            'video_id': 'test123',
            'title': 'Test Video',
            'channel': 'Test Channel'
        }
        mock_service_class.return_value = mock_service

        response = client.get(
            "/video/metadata",
            params={"video_url": "https://www.youtube.com/watch?v=test123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['video_id'] == 'test123'
        assert data['title'] == 'Test Video'

    @patch('api.routers.video.YouTubeService')
    def test_get_video_metadata_invalid_url(self, mock_service_class):
        """유효하지 않은 URL로 메타데이터 가져오기 실패 테스트"""
        mock_service = Mock()
        mock_service.extract_video_id.return_value = None
        mock_service_class.return_value = mock_service

        response = client.get(
            "/video/metadata",
            params={"video_url": "invalid_url"}
        )

        assert response.status_code == 400

    @patch('api.routers.video.YouTubeService')
    def test_get_video_transcript_success(self, mock_service_class):
        """비디오 자막 가져오기 성공 테스트"""
        mock_service = Mock()
        mock_service.extract_video_id.return_value = "test123"
        mock_service.get_transcript.return_value = [
            {'start': 0.0, 'duration': 3.0, 'text': 'Hello', 'timestamp': '00:00:00'}
        ]
        mock_service_class.return_value = mock_service

        response = client.get(
            "/video/transcript",
            params={
                "video_url": "https://www.youtube.com/watch?v=test123",
                "languages": ["ko", "en"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['text'] == 'Hello'
