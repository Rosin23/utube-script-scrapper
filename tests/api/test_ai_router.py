"""
AI 라우터 테스트
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

from api_main import app
from utils.dependencies import get_ai_service, get_settings

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

    def test_generate_summary_success(self):
        """요약 생성 성공 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.generate_summary_from_text.return_value = "This is a summary."

        app.dependency_overrides[get_ai_service] = lambda: mock_service

        response = client.post(
            "/ai/summary",
            json={
                "text": "Long text to summarize...",
                "max_points": 3,
                "language": "en"
            }
        )

        app.dependency_overrides = {}

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert data["summary"] == "This is a summary."

    def test_translate_text_success(self):
        """번역 성공 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.translate_text.return_value = "Hello"

        app.dependency_overrides[get_ai_service] = lambda: mock_service

        response = client.post(
            "/ai/translate",
            json={
                "text": "안녕하세요",
                "target_language": "en"
            }
        )

        app.dependency_overrides = {}

        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert data["translated_text"] == "Hello"

    def test_extract_topics_success(self):
        """주제 추출 성공 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.extract_topics_from_text.return_value = ["Topic 1", "Topic 2"]

        app.dependency_overrides[get_ai_service] = lambda: mock_service

        response = client.post(
            "/ai/topics",
            json={
                "text": "Text to extract topics from...",
                "num_topics": 2,
                "language": "en"
            }
        )

        app.dependency_overrides = {}

        assert response.status_code == 200
        data = response.json()
        assert "topics" in data
        assert len(data["topics"]) == 2

    def test_generate_summary_service_unavailable(self):
        """AI 서비스 사용 불가능 시 요약 실패 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = False

        app.dependency_overrides[get_ai_service] = lambda: mock_service

        response = client.post(
            "/ai/summary",
            json={
                "text": "Text to summarize",
                "max_points": 3
            }
        )

        app.dependency_overrides = {}

        assert response.status_code == 503

    def test_translate_text_service_unavailable(self):
        """AI 서비스 사용 불가능 시 번역 실패 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = False

        app.dependency_overrides[get_ai_service] = lambda: mock_service

        response = client.post(
            "/ai/translate",
            json={
                "text": "Text to translate",
                "target_language": "ko"
            }
        )

        app.dependency_overrides = {}

        assert response.status_code == 503

    def test_extract_topics_service_unavailable(self):
        """AI 서비스 사용 불가능 시 주제 추출 실패 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = False

        app.dependency_overrides[get_ai_service] = lambda: mock_service

        response = client.post(
            "/ai/topics",
            json={
                "text": "Text to analyze",
                "num_topics": 3
            }
        )

        app.dependency_overrides = {}

        assert response.status_code == 503

    def test_enhance_text_all_features(self):
        """모든 AI 기능 적용 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True

        # enhance_transcript 메서드의 반환값 설정
        mock_service.enhance_transcript.return_value = {
            'summary': "Test summary",
            'translation': "Translated text",
            'topics': ["Topic 1", "Topic 2"],
            'processing_time': 1.5
        }

        app.dependency_overrides[get_ai_service] = lambda: mock_service

        response = client.post(
            "/ai/enhance",
            json={
                "text": "Text to enhance",
                "enable_summary": True,
                "summary_max_points": 3,
                "enable_translation": True,
                "target_language": "ko",
                "enable_topics": True,
                "num_topics": 2
            }
        )

        app.dependency_overrides = {}

        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "Test summary"
        assert data["translation"] == "Translated text"
        assert len(data["topics"]) == 2
        assert "processing_time" in data

    def test_enhance_text_service_unavailable(self):
        """AI 서비스 사용 불가능 시 향상 실패 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = False

        app.dependency_overrides[get_ai_service] = lambda: mock_service

        response = client.post(
            "/ai/enhance",
            json={
                "text": "Text to enhance",
                "enable_summary": True
            }
        )

        app.dependency_overrides = {}

        assert response.status_code == 503
