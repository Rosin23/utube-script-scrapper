"""
Translator 도구 테스트
"""

import pytest
from unittest.mock import Mock, patch

from tools.translator import TranslatorTool


class TestTranslatorTool:
    """Translator 도구 테스트"""

    def test_initialization(self):
        """도구 초기화 테스트"""
        tool = TranslatorTool()
        assert tool is not None
        assert tool.name == "translator"
        assert tool.ai_service is not None

    @patch('tools.translator.AIService')
    def test_run_success(self, mock_service_class):
        """번역 실행 성공 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.translate_text.return_value = "Translated text"
        mock_service_class.return_value = mock_service

        tool = TranslatorTool()
        result = tool.run(text="안녕하세요", target_language="en")

        assert result == "Translated text"
        mock_service.translate_text.assert_called_once()

    @patch('tools.translator.AIService')
    def test_run_with_source_language(self, mock_service_class):
        """원본 언어 지정하여 번역 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.translate_text.return_value = "Hello"
        mock_service_class.return_value = mock_service

        tool = TranslatorTool()
        result = tool.run(
            text="안녕하세요",
            target_language="en",
            source_language="ko"
        )

        assert result == "Hello"

    @patch('tools.translator.AIService')
    def test_run_service_unavailable(self, mock_service_class):
        """AI 서비스 사용 불가능 시 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = False
        mock_service_class.return_value = mock_service

        tool = TranslatorTool()
        result = tool.run(text="Text", target_language="en")

        assert result is None

    @patch('tools.translator.AIService')
    def test_run_no_text(self, mock_service_class):
        """텍스트 없이 실행 시 오류 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service_class.return_value = mock_service

        tool = TranslatorTool()

        with pytest.raises(ValueError, match="'text' is required"):
            tool.run(text="", target_language="en")

    @patch('tools.translator.AIService')
    def test_run_no_target_language(self, mock_service_class):
        """대상 언어 없이 실행 시 오류 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service_class.return_value = mock_service

        tool = TranslatorTool()

        with pytest.raises(ValueError, match="'target_language' is required"):
            tool.run(text="Hello", target_language="")

    @patch('tools.translator.AIService')
    def test_is_available(self, mock_service_class):
        """사용 가능 여부 확인 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service_class.return_value = mock_service

        tool = TranslatorTool()

        assert tool.is_available() is True

    def test_get_supported_languages(self):
        """지원 언어 목록 가져오기 테스트"""
        languages = TranslatorTool.get_supported_languages()

        assert isinstance(languages, dict)
        assert 'ko' in languages
        assert 'en' in languages
        assert languages['ko'] == '한국어'
        assert languages['en'] == '영어'

    def test_get_tool_schema(self):
        """도구 스키마 가져오기 테스트"""
        schema = TranslatorTool.get_tool_schema()

        assert schema['type'] == 'function'
        assert 'function' in schema
        assert schema['function']['name'] == 'translator'
        assert 'parameters' in schema['function']
        assert 'text' in schema['function']['parameters']['properties']
        assert 'target_language' in schema['function']['parameters']['properties']
        assert 'source_language' in schema['function']['parameters']['properties']
