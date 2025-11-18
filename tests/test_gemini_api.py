"""
Gemini API 모듈 테스트
Coverage 80% 이상을 목표로 한 포괄적인 테스트
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# google.genai 모듈을 mock으로 대체 (새 API 스타일)
mock_genai_module = MagicMock()
mock_types_module = MagicMock()
mock_google = MagicMock()
mock_google.genai = mock_genai_module
mock_genai_module.types = mock_types_module

sys.modules['google'] = mock_google
sys.modules['google.genai'] = mock_genai_module
sys.modules['google.genai.types'] = mock_types_module


# 이제 안전하게 gemini_api import 가능
import gemini_api
from gemini_api import GeminiAPIError, GeminiClient, is_gemini_available, get_gemini_client


class TestGeminiAPIError:
    """GeminiAPIError 예외 테스트"""

    def test_exception_creation(self):
        """예외 생성 테스트"""
        error = GeminiAPIError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)


class TestGeminiClient:
    """GeminiClient 클래스 테스트"""

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-api-key'})
    def test_initialization_with_api_key(self):
        """API 키로 초기화 테스트"""
        mock_client = Mock()
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient(api_key='custom-api-key')

        assert client.api_key == 'custom-api-key'
        assert client.model_name == 'gemini-2.0-flash-exp'
        assert client.retry_count == 3
        assert client.retry_delay == 1.0
        assert os.environ['GOOGLE_API_KEY'] == 'custom-api-key'

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'env-api-key'})
    def test_initialization_with_env_var(self):
        """환경변수에서 API 키 로드 테스트"""
        mock_client = Mock()
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()

        assert client.api_key == 'env-api-key'

    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_without_api_key(self):
        """API 키 없이 초기화 시 에러 테스트"""
        with pytest.raises(GeminiAPIError, match="Gemini API 키가 필요합니다"):
            GeminiClient()

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_initialization_with_custom_params(self):
        """커스텀 파라미터로 초기화 테스트"""
        mock_client = Mock()
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient(
            api_key='custom-key',
            model_name='gemini-1.5-flash',
            retry_count=5,
            retry_delay=2.0
        )

        assert client.api_key == 'custom-key'
        assert client.model_name == 'gemini-1.5-flash'
        assert client.retry_count == 5
        assert client.retry_delay == 2.0

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_initialization_model_failure(self):
        """클라이언트 초기화 실패 테스트"""
        mock_genai_module.Client.side_effect = Exception("Client init failed")

        with pytest.raises(GeminiAPIError, match="클라이언트 초기화 실패"):
            GeminiClient()

        # side_effect 리셋
        mock_genai_module.Client.side_effect = None

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_combine_transcript_text(self):
        """자막 텍스트 결합 테스트"""
        mock_client = Mock()
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()

        # 정상적인 자막
        transcript = [
            {'text': 'Hello', 'start': 0},
            {'text': 'World', 'start': 5},
            {'text': 'Test', 'start': 10}
        ]
        result = client._combine_transcript_text(transcript)
        assert result == 'Hello World Test'

        # 빈 자막
        assert client._combine_transcript_text([]) == ""

        # text 필드가 없는 항목
        transcript_with_empty = [
            {'text': 'Hello', 'start': 0},
            {'start': 5},
            {'text': '', 'start': 10},
            {'text': 'World', 'start': 15}
        ]
        result = client._combine_transcript_text(transcript_with_empty)
        assert result == 'Hello World'

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_make_api_call_success(self):
        """API 호출 성공 테스트"""
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        result = client._make_api_call("test prompt")

        assert result == "Test response"

    @patch('gemini_api.time.sleep')
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_make_api_call_retry(self, mock_sleep):
        """API 호출 재시도 테스트"""
        mock_response = Mock()
        mock_response.text = "Success"
        mock_client = Mock()
        # 첫 두 번은 실패, 세 번째는 성공
        mock_client.models.generate_content.side_effect = [
            Exception("Fail 1"),
            Exception("Fail 2"),
            mock_response
        ]
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        result = client._make_api_call("test prompt")

        assert result == "Success"
        assert mock_client.models.generate_content.call_count == 3

        # side_effect 리셋
        mock_client.models.generate_content.side_effect = None

    @patch('gemini_api.time.sleep')
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_make_api_call_all_retries_fail(self, mock_sleep):
        """모든 재시도 실패 테스트"""
        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        result = client._make_api_call("test prompt")

        assert result is None
        assert mock_client.models.generate_content.call_count == 3

        # side_effect 리셋
        mock_client.models.generate_content.side_effect = None

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_make_api_call_empty_response(self):
        """빈 응답 처리 테스트"""
        mock_response = Mock()
        mock_response.text = ""
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        result = client._make_api_call("test prompt")

        assert result is None

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_generate_summary_success(self):
        """요약 생성 성공 테스트"""
        mock_response = Mock()
        mock_response.text = "1. 첫 번째 요약\n2. 두 번째 요약"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        transcript = [{'text': 'Test content', 'start': 0}]

        summary = client.generate_summary(transcript, max_points=2, language='ko')

        assert summary == "1. 첫 번째 요약\n2. 두 번째 요약"

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_generate_summary_english(self):
        """영어 요약 생성 테스트"""
        mock_response = Mock()
        mock_response.text = "1. First point\n2. Second point"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        transcript = [{'text': 'Test content', 'start': 0}]

        summary = client.generate_summary(transcript, max_points=2, language='en')

        assert summary == "1. First point\n2. Second point"

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_generate_summary_empty_transcript(self):
        """빈 자막으로 요약 생성 시 None 반환 테스트"""
        mock_client = Mock()
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        summary = client.generate_summary([])

        assert summary is None

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_generate_summary_text_only_transcript(self):
        """텍스트 없는 자막으로 요약 생성 테스트"""
        mock_client = Mock()
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        transcript = [{'text': '', 'start': 0}, {'start': 5}]
        summary = client.generate_summary(transcript)

        assert summary is None

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_generate_summary_long_text(self):
        """긴 텍스트 요약 생성 테스트"""
        mock_response = Mock()
        mock_response.text = "Summary"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        # 30000자 이상의 긴 텍스트
        long_text = "A" * 31000
        transcript = [{'text': long_text, 'start': 0}]

        summary = client.generate_summary(transcript)

        assert summary == "Summary"

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_translate_text_success(self):
        """텍스트 번역 성공 테스트"""
        mock_response = Mock()
        mock_response.text = "Translated text"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        result = client.translate_text("테스트 텍스트", target_language='en')

        assert result == "Translated text"

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_translate_text_with_source_language(self):
        """소스 언어 지정 번역 테스트"""
        mock_response = Mock()
        mock_response.text = "Translated"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        result = client.translate_text("테스트", target_language='en', source_language='ko')

        assert result == "Translated"

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_translate_text_empty(self):
        """빈 텍스트 번역 시 None 반환 테스트"""
        mock_client = Mock()
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()

        assert client.translate_text("") is None
        assert client.translate_text("   ") is None

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_translate_text_long_text(self):
        """긴 텍스트 번역 테스트"""
        mock_response = Mock()
        mock_response.text = "Translated"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        long_text = "A" * 31000
        result = client.translate_text(long_text, target_language='en')

        assert result == "Translated"

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_translate_transcript_success(self):
        """자막 번역 성공 테스트"""
        mock_response = Mock()
        mock_response.text = "Translated transcript"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        transcript = [{'text': 'Hello', 'start': 0}, {'text': 'World', 'start': 5}]

        result = client.translate_transcript(transcript, target_language='ko')

        assert result == "Translated transcript"

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_translate_transcript_empty(self):
        """빈 자막 번역 시 None 반환 테스트"""
        mock_client = Mock()
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        assert client.translate_transcript([]) is None

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_extract_key_topics_success(self):
        """핵심 주제 추출 성공 테스트"""
        mock_response = Mock()
        mock_response.text = "- 주제 1\n- 주제 2\n- 주제 3"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        transcript = [{'text': 'Test content', 'start': 0}]

        topics = client.extract_key_topics(transcript, num_topics=3, language='ko')

        assert topics == ['주제 1', '주제 2', '주제 3']

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_extract_key_topics_numbered_format(self):
        """번호 형식 주제 추출 테스트"""
        mock_response = Mock()
        mock_response.text = "1. Topic 1\n2. Topic 2\n3. Topic 3"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        transcript = [{'text': 'Test', 'start': 0}]

        topics = client.extract_key_topics(transcript, num_topics=3)

        assert topics == ['Topic 1', 'Topic 2', 'Topic 3']

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_extract_key_topics_mixed_format(self):
        """혼합 형식 주제 추출 테스트"""
        mock_response = Mock()
        mock_response.text = "• Topic 1\n* Topic 2\n- Topic 3\n4. Topic 4"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        transcript = [{'text': 'Test', 'start': 0}]

        topics = client.extract_key_topics(transcript, num_topics=5)

        assert topics == ['Topic 1', 'Topic 2', 'Topic 3', 'Topic 4']

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_extract_key_topics_limit(self):
        """주제 개수 제한 테스트"""
        mock_response = Mock()
        mock_response.text = "- Topic 1\n- Topic 2\n- Topic 3\n- Topic 4\n- Topic 5"
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        transcript = [{'text': 'Test', 'start': 0}]

        topics = client.extract_key_topics(transcript, num_topics=3)

        assert len(topics) == 3
        assert topics == ['Topic 1', 'Topic 2', 'Topic 3']

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_extract_key_topics_empty_transcript(self):
        """빈 자막으로 주제 추출 시 None 반환 테스트"""
        mock_client = Mock()
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        topics = client.extract_key_topics([])

        assert topics is None

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_extract_key_topics_empty_text(self):
        """빈 텍스트 주제 추출 테스트"""
        mock_client = Mock()
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient()
        transcript = [{'text': '', 'start': 0}]
        topics = client.extract_key_topics(transcript)

        assert topics is None

    @patch('gemini_api.time.sleep')
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_extract_key_topics_api_failure(self, mock_sleep):
        """API 실패 시 None 반환 테스트"""
        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        mock_genai_module.Client.return_value = mock_client

        client = GeminiClient(retry_count=1)
        transcript = [{'text': 'Test', 'start': 0}]
        topics = client.extract_key_topics(transcript)

        assert topics is None

        # side_effect 리셋
        mock_client.models.generate_content.side_effect = None


class TestIsGeminiAvailable:
    """is_gemini_available 함수 테스트"""

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_gemini_available(self):
        """API 키가 있을 때 True 반환 테스트"""
        assert is_gemini_available() is True

    @patch.dict(os.environ, {}, clear=True)
    def test_gemini_not_available(self):
        """API 키가 없을 때 False 반환 테스트"""
        assert is_gemini_available() is False


class TestGetGeminiClient:
    """get_gemini_client 함수 테스트"""

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_get_client_success(self):
        """클라이언트 생성 성공 테스트"""
        mock_client = Mock()
        mock_genai_module.Client.return_value = mock_client

        client = get_gemini_client()

        assert client is not None
        assert client.api_key == 'test-key'

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_get_client_with_custom_model(self):
        """커스텀 모델로 클라이언트 생성 테스트"""
        mock_client = Mock()
        mock_genai_module.Client.return_value = mock_client

        client = get_gemini_client(model_name='gemini-1.5-pro')

        assert client is not None
        assert client.model_name == 'gemini-1.5-pro'

    @patch.dict(os.environ, {}, clear=True)
    def test_get_client_failure(self):
        """클라이언트 생성 실패 테스트"""
        client = get_gemini_client()

        assert client is None
