"""
Summarizer 도구 테스트
"""

import pytest
from unittest.mock import Mock, patch

from tools.summarizer import SummarizerTool


class TestSummarizerTool:
    """Summarizer 도구 테스트"""

    def test_initialization(self):
        """도구 초기화 테스트"""
        tool = SummarizerTool()
        assert tool is not None
        assert tool.name == "summarizer"
        assert tool.ai_service is not None

    @patch('tools.summarizer.AIService')
    def test_run_with_text_success(self, mock_service_class):
        """텍스트로 요약 실행 성공 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.generate_summary_from_text.return_value = "Generated summary"
        mock_service_class.return_value = mock_service

        tool = SummarizerTool()
        result = tool.run(text="Long text to summarize", max_points=3)

        assert result == "Generated summary"
        mock_service.generate_summary_from_text.assert_called_once()

    @patch('tools.summarizer.AIService')
    def test_run_with_transcript_success(self, mock_service_class):
        """자막으로 요약 실행 성공 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.generate_summary.return_value = "Transcript summary"
        mock_service_class.return_value = mock_service

        tool = SummarizerTool()
        transcript = [{'text': 'Hello', 'start': 0}]
        result = tool.run(transcript=transcript, max_points=5)

        assert result == "Transcript summary"
        mock_service.generate_summary.assert_called_once()

    @patch('tools.summarizer.AIService')
    def test_run_service_unavailable(self, mock_service_class):
        """AI 서비스 사용 불가능 시 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = False
        mock_service_class.return_value = mock_service

        tool = SummarizerTool()
        result = tool.run(text="Text to summarize")

        assert result is None

    @patch('tools.summarizer.AIService')
    def test_run_no_input(self, mock_service_class):
        """입력 없이 실행 시 오류 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service_class.return_value = mock_service

        tool = SummarizerTool()

        with pytest.raises(ValueError, match="Either 'text' or 'transcript' must be provided"):
            tool.run()

    @patch('tools.summarizer.AIService')
    def test_is_available(self, mock_service_class):
        """사용 가능 여부 확인 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service_class.return_value = mock_service

        tool = SummarizerTool()

        assert tool.is_available() is True

    def test_get_tool_schema(self):
        """도구 스키마 가져오기 테스트"""
        schema = SummarizerTool.get_tool_schema()

        assert schema['type'] == 'function'
        assert 'function' in schema
        assert schema['function']['name'] == 'summarizer'
        assert 'parameters' in schema['function']
        assert 'text' in schema['function']['parameters']['properties']
        assert 'max_points' in schema['function']['parameters']['properties']
