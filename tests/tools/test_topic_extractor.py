"""
Topic Extractor 도구 테스트
"""

import pytest
from unittest.mock import Mock, patch

from tools.topic_extractor import TopicExtractorTool


class TestTopicExtractorTool:
    """Topic Extractor 도구 테스트"""

    def test_initialization(self):
        """도구 초기화 테스트"""
        tool = TopicExtractorTool()
        assert tool is not None
        assert tool.name == "topic_extractor"
        assert tool.ai_service is not None

    @patch('tools.topic_extractor.AIService')
    def test_run_with_text_success(self, mock_service_class):
        """텍스트로 주제 추출 성공 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.extract_topics_from_text.return_value = ["Topic 1", "Topic 2", "Topic 3"]
        mock_service_class.return_value = mock_service

        tool = TopicExtractorTool()
        result = tool.run(text="Long text content", num_topics=3)

        assert len(result) == 3
        assert result[0] == "Topic 1"
        mock_service.extract_topics_from_text.assert_called_once()

    @patch('tools.topic_extractor.AIService')
    def test_run_with_transcript_success(self, mock_service_class):
        """자막으로 주제 추출 성공 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.extract_topics.return_value = ["주제 1", "주제 2"]
        mock_service_class.return_value = mock_service

        tool = TopicExtractorTool()
        transcript = [{'text': '안녕하세요', 'start': 0}]
        result = tool.run(transcript=transcript, num_topics=2, language="ko")

        assert len(result) == 2
        assert result[0] == "주제 1"
        mock_service.extract_topics.assert_called_once()

    @patch('tools.topic_extractor.AIService')
    def test_run_service_unavailable(self, mock_service_class):
        """AI 서비스 사용 불가능 시 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = False
        mock_service_class.return_value = mock_service

        tool = TopicExtractorTool()
        result = tool.run(text="Text content")

        assert result is None

    @patch('tools.topic_extractor.AIService')
    def test_run_no_input(self, mock_service_class):
        """입력 없이 실행 시 오류 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service_class.return_value = mock_service

        tool = TopicExtractorTool()

        with pytest.raises(ValueError, match="Either 'text' or 'transcript' must be provided"):
            tool.run()

    @patch('tools.topic_extractor.AIService')
    def test_is_available(self, mock_service_class):
        """사용 가능 여부 확인 테스트"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service_class.return_value = mock_service

        tool = TopicExtractorTool()

        assert tool.is_available() is True

    def test_get_tool_schema(self):
        """도구 스키마 가져오기 테스트"""
        schema = TopicExtractorTool.get_tool_schema()

        assert schema['type'] == 'function'
        assert 'function' in schema
        assert schema['function']['name'] == 'topic_extractor'
        assert 'parameters' in schema['function']
        assert 'text' in schema['function']['parameters']['properties']
        assert 'num_topics' in schema['function']['parameters']['properties']
        assert 'language' in schema['function']['parameters']['properties']
