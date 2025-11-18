"""
AI 라우터 테스트
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from api_main import app

client = TestClient(app)


class TestAIRouter:
    """AI 라우터 테스트"""

    def test_ai_health_check(self):
        """AI 헬스 체크 테스트"""
        response = client.get("/ai/health")
        assert response.status_code == 200

        data = response.json()
        assert "available" in data
        assert "model" in data

    @patch('api.routers.ai.AIService')
    def test_generate_summary_success(self, mock_service_class):
        """요약 생성 성공 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.generate_summary_from_text.return_value = "This is a summary."
        mock_service_class.return_value = mock_service

        response = client.post(
            "/ai/summary",
            json={
                "text": "Long text to summarize...",
                "max_points": 3,
                "language": "en"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert data["summary"] == "This is a summary."

    @patch('api.routers.ai.AIService')
    def test_translate_text_success(self, mock_service_class):
        """번역 성공 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.translate_text.return_value = "Hello"
        mock_service_class.return_value = mock_service

        response = client.post(
            "/ai/translate",
            json={
                "text": "안녕하세요",
                "target_language": "en"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert data["translated_text"] == "Hello"

    @patch('api.routers.ai.AIService')
    def test_extract_topics_success(self, mock_service_class):
        """주제 추출 성공 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.extract_topics_from_text.return_value = ["Topic 1", "Topic 2"]
        mock_service_class.return_value = mock_service

        response = client.post(
            "/ai/topics",
            json={
                "text": "Text to extract topics from...",
                "num_topics": 2,
                "language": "en"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "topics" in data
        assert len(data["topics"]) == 2
