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

    @patch('api.routers.video.YouTubeService')
    def test_post_video_info_success(self, mock_service_class):
        """비디오 정보 POST 엔드포인트 성공 테스트"""
        mock_service = Mock()
        mock_service.get_video_info.return_value = {
            'metadata': {
                'video_id': 'test123',
                'title': 'Test Video',
                'channel': 'Test Channel',
                'upload_date': '20230101',
                'duration': 120
            },
            'transcript': [
                {'start': 0.0, 'duration': 3.0, 'text': 'Hello', 'timestamp': '00:00:00'}
            ],
            'video_id': 'test123'
        }
        mock_service_class.return_value = mock_service

        response = client.post(
            "/video/info",
            json={
                "video_url": "https://www.youtube.com/watch?v=test123",
                "languages": ["ko", "en"],
                "prefer_manual": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert 'metadata' in data
        assert 'transcript' in data
        assert data['metadata']['video_id'] == 'test123'

    @patch('api.routers.video.YouTubeService')
    def test_post_video_info_invalid_url(self, mock_service_class):
        """유효하지 않은 URL로 비디오 정보 POST 실패 테스트"""
        mock_service = Mock()
        mock_service.get_video_info.side_effect = ValueError("Invalid YouTube URL")
        mock_service_class.return_value = mock_service

        response = client.post(
            "/video/info",
            json={
                "video_url": "invalid_url",
                "languages": ["ko"]
            }
        )

        assert response.status_code == 400

    @patch('api.routers.video.YouTubeService')
    @patch('api.routers.video.AIService')
    def test_scrape_video_with_summary(self, mock_ai_class, mock_yt_class):
        """요약 포함 비디오 스크래핑 테스트"""
        mock_yt = Mock()
        mock_yt.get_video_info.return_value = {
            'metadata': {'video_id': 'test123', 'title': 'Test'},
            'transcript': [{'start': 0, 'text': 'Hello'}],
            'video_id': 'test123'
        }
        mock_yt_class.return_value = mock_yt

        mock_ai = Mock()
        mock_ai.generate_summary.return_value = "Test summary"
        mock_ai_class.return_value = mock_ai

        response = client.post(
            "/video/scrape",
            json={
                "video_url": "https://www.youtube.com/watch?v=test123",
                "enable_summary": True,
                "summary_max_points": 5
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert 'summary' in data
        assert data['summary'] == "Test summary"

    @patch('api.routers.video.YouTubeService')
    @patch('api.routers.video.AIService')
    def test_scrape_video_with_translation(self, mock_ai_class, mock_yt_class):
        """번역 포함 비디오 스크래핑 테스트"""
        mock_yt = Mock()
        mock_yt.get_video_info.return_value = {
            'metadata': {'video_id': 'test123', 'title': 'Test'},
            'transcript': [{'start': 0, 'text': 'Hello'}],
            'video_id': 'test123'
        }
        mock_yt_class.return_value = mock_yt

        mock_ai = Mock()
        mock_ai.translate_transcript.return_value = "Translated text"
        mock_ai_class.return_value = mock_ai

        response = client.post(
            "/video/scrape",
            json={
                "video_url": "https://www.youtube.com/watch?v=test123",
                "enable_translation": True,
                "target_language": "ko"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert 'translation' in data
        assert data['translation'] == "Translated text"

    @patch('api.routers.video.YouTubeService')
    @patch('api.routers.video.AIService')
    def test_scrape_video_with_topics(self, mock_ai_class, mock_yt_class):
        """주제 추출 포함 비디오 스크래핑 테스트"""
        mock_yt = Mock()
        mock_yt.get_video_info.return_value = {
            'metadata': {'video_id': 'test123', 'title': 'Test'},
            'transcript': [{'start': 0, 'text': 'Hello'}],
            'video_id': 'test123'
        }
        mock_yt_class.return_value = mock_yt

        mock_ai = Mock()
        mock_ai.extract_topics.return_value = ["Topic 1", "Topic 2"]
        mock_ai_class.return_value = mock_ai

        response = client.post(
            "/video/scrape",
            json={
                "video_url": "https://www.youtube.com/watch?v=test123",
                "enable_topics": True,
                "num_topics": 2
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert 'key_topics' in data
        assert len(data['key_topics']) == 2
