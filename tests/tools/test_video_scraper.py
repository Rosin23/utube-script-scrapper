"""
비디오 스크래퍼 도구 테스트
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from tools.video_scraper import VideoScraperTool


class TestVideoScraperTool:
    """비디오 스크래퍼 도구 테스트"""

    def test_initialization(self):
        """도구 초기화 테스트"""
        tool = VideoScraperTool()
        assert tool is not None
        assert tool.name == "video_scraper"
        assert tool.youtube_service is not None

    @patch('tools.video_scraper.YouTubeService')
    def test_run_success(self, mock_service_class):
        """도구 실행 성공 테스트"""
        mock_service = Mock()
        mock_service.get_video_info.return_value = {
            'metadata': {'video_id': 'test123', 'title': 'Test Video'},
            'transcript': [{'start': 0.0, 'text': 'Hello'}],
            'video_id': 'test123'
        }
        mock_service_class.return_value = mock_service

        tool = VideoScraperTool()
        result = tool.run(video_url="https://www.youtube.com/watch?v=test123")

        assert 'metadata' in result
        assert 'transcript' in result
        assert result['video_id'] == 'test123'

    def test_run_no_url(self):
        """URL 없이 실행 시 오류 테스트"""
        tool = VideoScraperTool()

        with pytest.raises(ValueError, match="video_url is required"):
            tool.run(video_url="")

    @patch('tools.video_scraper.YouTubeService')
    def test_get_metadata_only(self, mock_service_class):
        """메타데이터만 가져오기 테스트"""
        mock_service = Mock()
        mock_service.extract_video_id.return_value = "test123"
        mock_service.get_video_metadata.return_value = {
            'video_id': 'test123',
            'title': 'Test Video'
        }
        mock_service_class.return_value = mock_service

        tool = VideoScraperTool()
        metadata = tool.get_metadata_only("https://www.youtube.com/watch?v=test123")

        assert metadata['video_id'] == 'test123'
        mock_service.get_video_metadata.assert_called_once_with('test123')

    @patch('tools.video_scraper.YouTubeService')
    def test_get_transcript_only(self, mock_service_class):
        """자막만 가져오기 테스트"""
        mock_service = Mock()
        mock_service.extract_video_id.return_value = "test123"
        mock_service.get_transcript.return_value = [
            {'start': 0.0, 'text': 'Hello'}
        ]
        mock_service_class.return_value = mock_service

        tool = VideoScraperTool()
        transcript = tool.get_transcript_only("https://www.youtube.com/watch?v=test123")

        assert len(transcript) == 1
        assert transcript[0]['text'] == 'Hello'

    def test_get_tool_schema(self):
        """도구 스키마 가져오기 테스트"""
        schema = VideoScraperTool.get_tool_schema()

        assert schema['type'] == 'function'
        assert 'function' in schema
        assert schema['function']['name'] == 'video_scraper'
        assert 'parameters' in schema['function']
        assert 'video_url' in schema['function']['parameters']['properties']
