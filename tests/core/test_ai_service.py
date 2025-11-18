"""
AI 서비스 테스트
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from core.ai_service import AIService


class TestAIService:
    """AI 서비스 테스트"""

    @patch('core.ai_service.is_gemini_available')
    @patch('core.ai_service.GeminiClient')
    def test_initialization_success(self, mock_client_class, mock_available):
        """AI 서비스 초기화 성공 테스트"""
        mock_available.return_value = True
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        service = AIService(api_key="test_key")

        assert service.available is True
        assert service.client is not None

    @patch('core.ai_service.is_gemini_available')
    def test_initialization_unavailable(self, mock_available):
        """Gemini 사용 불가능 시 초기화 테스트"""
        mock_available.return_value = False

        service = AIService()

        assert service.available is False
        assert service.client is None

    @patch('core.ai_service.is_gemini_available')
    @patch('core.ai_service.GeminiClient')
    def test_is_available(self, mock_client_class, mock_available):
        """사용 가능 여부 확인 테스트"""
        mock_available.return_value = True
        mock_client_class.return_value = Mock()

        service = AIService()

        assert service.is_available() is True

    @patch('core.ai_service.is_gemini_available')
    @patch('core.ai_service.GeminiClient')
    def test_generate_summary_success(self, mock_client_class, mock_available):
        """요약 생성 성공 테스트"""
        mock_available.return_value = True
        mock_client = Mock()
        mock_client.generate_summary.return_value = "Test summary"
        mock_client_class.return_value = mock_client

        service = AIService()
        transcript = [{'text': 'Hello', 'start': 0}]
        summary = service.generate_summary(transcript, max_points=3)

        assert summary == "Test summary"
        mock_client.generate_summary.assert_called_once()

    @patch('core.ai_service.is_gemini_available')
    def test_generate_summary_unavailable(self, mock_available):
        """AI 서비스 사용 불가능 시 요약 생성 테스트"""
        mock_available.return_value = False

        service = AIService()
        transcript = [{'text': 'Hello', 'start': 0}]
        summary = service.generate_summary(transcript)

        assert summary is None

    @patch('core.ai_service.is_gemini_available')
    @patch('core.ai_service.GeminiClient')
    def test_generate_summary_from_text(self, mock_client_class, mock_available):
        """텍스트에서 요약 생성 테스트"""
        mock_available.return_value = True
        mock_client = Mock()
        mock_client.generate_summary.return_value = "Summary from text"
        mock_client_class.return_value = mock_client

        service = AIService()
        summary = service.generate_summary_from_text("Long text here", max_points=5)

        assert summary == "Summary from text"

    @patch('core.ai_service.is_gemini_available')
    @patch('core.ai_service.GeminiClient')
    def test_translate_text_success(self, mock_client_class, mock_available):
        """텍스트 번역 성공 테스트"""
        mock_available.return_value = True
        mock_client = Mock()
        mock_client.translate_text.return_value = "Translated text"
        mock_client_class.return_value = mock_client

        service = AIService()
        translated = service.translate_text("원본 텍스트", "en")

        assert translated == "Translated text"
        mock_client.translate_text.assert_called_once()

    @patch('core.ai_service.is_gemini_available')
    def test_translate_text_unavailable(self, mock_available):
        """AI 서비스 사용 불가능 시 번역 테스트"""
        mock_available.return_value = False

        service = AIService()
        translated = service.translate_text("text", "en")

        assert translated is None

    @patch('core.ai_service.is_gemini_available')
    @patch('core.ai_service.GeminiClient')
    def test_translate_transcript(self, mock_client_class, mock_available):
        """자막 번역 테스트"""
        mock_available.return_value = True
        mock_client = Mock()
        mock_client.translate_transcript.return_value = "Translated transcript"
        mock_client_class.return_value = mock_client

        service = AIService()
        transcript = [{'text': 'Hello', 'start': 0}]
        translated = service.translate_transcript(transcript, "ko")

        assert translated == "Translated transcript"

    @patch('core.ai_service.is_gemini_available')
    @patch('core.ai_service.GeminiClient')
    def test_extract_topics_success(self, mock_client_class, mock_available):
        """주제 추출 성공 테스트"""
        mock_available.return_value = True
        mock_client = Mock()
        mock_client.extract_key_topics.return_value = ["Topic 1", "Topic 2"]
        mock_client_class.return_value = mock_client

        service = AIService()
        transcript = [{'text': 'Hello', 'start': 0}]
        topics = service.extract_topics(transcript, num_topics=2)

        assert len(topics) == 2
        assert topics[0] == "Topic 1"

    @patch('core.ai_service.is_gemini_available')
    def test_extract_topics_unavailable(self, mock_available):
        """AI 서비스 사용 불가능 시 주제 추출 테스트"""
        mock_available.return_value = False

        service = AIService()
        topics = service.extract_topics([{'text': 'Hello', 'start': 0}])

        assert topics is None

    @patch('core.ai_service.is_gemini_available')
    @patch('core.ai_service.GeminiClient')
    def test_extract_topics_from_text(self, mock_client_class, mock_available):
        """텍스트에서 주제 추출 테스트"""
        mock_available.return_value = True
        mock_client = Mock()
        mock_client.extract_key_topics.return_value = ["Topic A", "Topic B", "Topic C"]
        mock_client_class.return_value = mock_client

        service = AIService()
        topics = service.extract_topics_from_text("Text content", num_topics=3)

        assert len(topics) == 3

    @patch('core.ai_service.is_gemini_available')
    @patch('core.ai_service.GeminiClient')
    def test_enhance_transcript_all_features(self, mock_client_class, mock_available):
        """모든 AI 기능 적용 테스트"""
        mock_available.return_value = True
        mock_client = Mock()
        mock_client.generate_summary.return_value = "Summary"
        mock_client.translate_transcript.return_value = "Translation"
        mock_client.extract_key_topics.return_value = ["Topic 1"]
        mock_client_class.return_value = mock_client

        service = AIService()
        transcript = [{'text': 'Hello', 'start': 0}]
        result = service.enhance_transcript(
            transcript=transcript,
            enable_summary=True,
            enable_translation=True,
            target_language="en",
            enable_topics=True
        )

        assert result['summary'] == "Summary"
        assert result['translation'] == "Translation"
        assert len(result['topics']) == 1
        assert 'processing_time' in result

    @patch('core.ai_service.is_gemini_available')
    @patch('core.ai_service.GeminiClient')
    def test_enhance_transcript_partial_features(self, mock_client_class, mock_available):
        """일부 AI 기능만 적용 테스트"""
        mock_available.return_value = True
        mock_client = Mock()
        mock_client.generate_summary.return_value = "Summary only"
        mock_client_class.return_value = mock_client

        service = AIService()
        transcript = [{'text': 'Hello', 'start': 0}]
        result = service.enhance_transcript(
            transcript=transcript,
            enable_summary=True,
            enable_translation=False,
            enable_topics=False
        )

        assert result['summary'] == "Summary only"
        assert result['translation'] is None
        assert result['topics'] is None
