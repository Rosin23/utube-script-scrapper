"""
Gemini API 모듈 테스트
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os


class TestGeminiClient:
    """GeminiClient 클래스 테스트"""

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'})
    @patch('gemini_api.genai')
    def test_initialization_with_api_key(self, mock_genai):
        """API 키로 초기화 테스트"""
        from gemini_api import GeminiClient

        client = GeminiClient(api_key='custom-api-key')
        assert client.api_key == 'custom-api-key'
        mock_genai.configure.assert_called_once_with(api_key='custom-api-key')

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'env-api-key'})
    @patch('gemini_api.genai')
    def test_initialization_with_env_var(self, mock_genai):
        """환경변수에서 API 키 로드 테스트"""
        from gemini_api import GeminiClient

        client = GeminiClient()
        assert client.api_key == 'env-api-key'

    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_without_api_key(self):
        """API 키 없이 초기화 시 에러 테스트"""
        from gemini_api import GeminiClient

        with pytest.raises(ValueError, match="Gemini API 키가 필요합니다"):
            GeminiClient()

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    @patch('gemini_api.genai')
    def test_combine_transcript_text(self, mock_genai):
        """자막 텍스트 결합 테스트"""
        from gemini_api import GeminiClient

        client = GeminiClient()
        transcript = [
            {'text': 'Hello', 'start': 0},
            {'text': 'World', 'start': 5},
            {'text': 'Test', 'start': 10}
        ]

        result = client._combine_transcript_text(transcript)
        assert result == 'Hello World Test'

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    @patch('gemini_api.genai')
    def test_generate_summary(self, mock_genai):
        """요약 생성 테스트"""
        from gemini_api import GeminiClient

        # Mock 모델 응답 설정
        mock_response = Mock()
        mock_response.text = "1. 첫 번째 요약\n2. 두 번째 요약"
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient()
        transcript = [{'text': 'Test content', 'start': 0}]

        summary = client.generate_summary(transcript, max_points=2)
        assert summary == "1. 첫 번째 요약\n2. 두 번째 요약"
        mock_model.generate_content.assert_called_once()

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    @patch('gemini_api.genai')
    def test_generate_summary_empty_transcript(self, mock_genai):
        """빈 자막으로 요약 생성 시 None 반환 테스트"""
        from gemini_api import GeminiClient

        client = GeminiClient()
        summary = client.generate_summary([])
        assert summary is None

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    @patch('gemini_api.genai')
    def test_translate_text(self, mock_genai):
        """텍스트 번역 테스트"""
        from gemini_api import GeminiClient

        mock_response = Mock()
        mock_response.text = "Translated text"
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient()
        result = client.translate_text("테스트 텍스트", target_language='en')

        assert result == "Translated text"
        mock_model.generate_content.assert_called_once()

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    @patch('gemini_api.genai')
    def test_translate_text_empty(self, mock_genai):
        """빈 텍스트 번역 시 None 반환 테스트"""
        from gemini_api import GeminiClient

        client = GeminiClient()
        result = client.translate_text("")
        assert result is None

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    @patch('gemini_api.genai')
    def test_extract_key_topics(self, mock_genai):
        """핵심 주제 추출 테스트"""
        from gemini_api import GeminiClient

        mock_response = Mock()
        mock_response.text = "- 주제 1\n- 주제 2\n- 주제 3"
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient()
        transcript = [{'text': 'Test content', 'start': 0}]

        topics = client.extract_key_topics(transcript, num_topics=3)
        assert topics == ['주제 1', '주제 2', '주제 3']

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    @patch('gemini_api.genai')
    def test_extract_key_topics_empty_transcript(self, mock_genai):
        """빈 자막으로 주제 추출 시 None 반환 테스트"""
        from gemini_api import GeminiClient

        client = GeminiClient()
        topics = client.extract_key_topics([])
        assert topics is None


class TestIsGeminiAvailable:
    """is_gemini_available 함수 테스트"""

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_gemini_available(self):
        """API 키가 있을 때 True 반환 테스트"""
        from gemini_api import is_gemini_available

        assert is_gemini_available() is True

    @patch.dict(os.environ, {}, clear=True)
    def test_gemini_not_available(self):
        """API 키가 없을 때 False 반환 테스트"""
        from gemini_api import is_gemini_available

        assert is_gemini_available() is False
