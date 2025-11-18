"""
Formatters 모듈 단위 테스트
"""

import pytest
import json
import xml.etree.ElementTree as ET
import os
from formatters import (
    TxtFormatter,
    JsonFormatter,
    XmlFormatter,
    MarkdownFormatter,
    get_formatter,
    get_available_formatters
)


@pytest.fixture
def sample_metadata():
    """테스트용 샘플 메타데이터"""
    return {
        'title': 'Test Video Title',
        'channel': 'Test Channel',
        'upload_date': '20240101',
        'duration': 630,
        'view_count': 1000000,
        'description': 'This is a test description.'
    }


@pytest.fixture
def sample_transcript():
    """테스트용 샘플 자막"""
    return [
        {'start': 0.0, 'duration': 2.5, 'text': 'First subtitle'},
        {'start': 2.5, 'duration': 3.0, 'text': 'Second subtitle'},
        {'start': 5.5, 'duration': 2.0, 'text': 'Third subtitle'}
    ]


@pytest.fixture
def temp_output_file(tmp_path):
    """임시 출력 파일 경로"""
    def _get_file(extension):
        return str(tmp_path / f"test_output.{extension}")
    return _get_file


class TestTxtFormatter:
    """TxtFormatter 클래스 테스트"""

    def test_initialization(self):
        """초기화 테스트"""
        formatter = TxtFormatter()
        assert formatter.get_extension() == "txt"
        assert formatter.get_name() == "텍스트"

    def test_save_creates_file(self, sample_metadata, sample_transcript, temp_output_file):
        """파일 생성 테스트"""
        formatter = TxtFormatter()
        output_file = temp_output_file('txt')

        formatter.save(sample_metadata, sample_transcript, output_file)

        assert os.path.exists(output_file)

    def test_save_content_structure(self, sample_metadata, sample_transcript, temp_output_file):
        """파일 내용 구조 테스트"""
        formatter = TxtFormatter()
        output_file = temp_output_file('txt')

        formatter.save(sample_metadata, sample_transcript, output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 주요 섹션이 포함되어 있는지 확인
        assert 'YouTube Video Transcript' in content
        assert 'Video Information' in content
        assert 'Description' in content
        assert 'Transcript with Timestamps' in content
        assert 'Test Video Title' in content
        assert 'Test Channel' in content
        assert 'First subtitle' in content

    def test_save_with_empty_transcript(self, sample_metadata, temp_output_file):
        """빈 자막으로 저장 테스트"""
        formatter = TxtFormatter()
        output_file = temp_output_file('txt')

        formatter.save(sample_metadata, [], output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'No transcript available' in content


class TestJsonFormatter:
    """JsonFormatter 클래스 테스트"""

    def test_initialization(self):
        """초기화 테스트"""
        formatter = JsonFormatter()
        assert formatter.get_extension() == "json"
        assert formatter.get_name() == "JSON"

    def test_save_creates_valid_json(self, sample_metadata, sample_transcript, temp_output_file):
        """유효한 JSON 파일 생성 테스트"""
        formatter = JsonFormatter()
        output_file = temp_output_file('json')

        formatter.save(sample_metadata, sample_transcript, output_file)

        # JSON 파일이 유효한지 확인
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert 'video_info' in data
        assert 'description' in data
        assert 'transcript' in data
        assert 'metadata' in data

    def test_save_json_structure(self, sample_metadata, sample_transcript, temp_output_file):
        """JSON 구조 테스트"""
        formatter = JsonFormatter()
        output_file = temp_output_file('json')

        formatter.save(sample_metadata, sample_transcript, output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # video_info 검증
        assert data['video_info']['title'] == 'Test Video Title'
        assert data['video_info']['channel'] == 'Test Channel'
        assert data['video_info']['duration'] == 630

        # transcript 검증
        assert len(data['transcript']) == 3
        assert data['transcript'][0]['text'] == 'First subtitle'

        # metadata 검증
        assert data['metadata']['total_entries'] == 3


class TestXmlFormatter:
    """XmlFormatter 클래스 테스트"""

    def test_initialization(self):
        """초기화 테스트"""
        formatter = XmlFormatter()
        assert formatter.get_extension() == "xml"
        assert formatter.get_name() == "XML"

    def test_save_creates_valid_xml(self, sample_metadata, sample_transcript, temp_output_file):
        """유효한 XML 파일 생성 테스트"""
        formatter = XmlFormatter()
        output_file = temp_output_file('xml')

        formatter.save(sample_metadata, sample_transcript, output_file)

        # XML 파일이 유효한지 확인
        tree = ET.parse(output_file)
        root = tree.getroot()

        assert root.tag == 'youtube_transcript'

    def test_save_xml_structure(self, sample_metadata, sample_transcript, temp_output_file):
        """XML 구조 테스트"""
        formatter = XmlFormatter()
        output_file = temp_output_file('xml')

        formatter.save(sample_metadata, sample_transcript, output_file)

        tree = ET.parse(output_file)
        root = tree.getroot()

        # video_info 검증
        video_info = root.find('video_info')
        assert video_info is not None
        assert video_info.find('title').text == 'Test Video Title'
        assert video_info.find('channel').text == 'Test Channel'

        # transcript 검증
        transcript = root.find('transcript')
        entries = transcript.findall('entry')
        assert len(entries) == 3
        assert entries[0].find('text').text == 'First subtitle'

        # metadata 검증
        metadata = root.find('metadata')
        assert metadata.find('total_entries').text == '3'


class TestMarkdownFormatter:
    """MarkdownFormatter 클래스 테스트"""

    def test_initialization(self):
        """초기화 테스트"""
        formatter = MarkdownFormatter()
        assert formatter.get_extension() == "md"
        assert formatter.get_name() == "Markdown"

    def test_save_creates_file(self, sample_metadata, sample_transcript, temp_output_file):
        """파일 생성 테스트"""
        formatter = MarkdownFormatter()
        output_file = temp_output_file('md')

        formatter.save(sample_metadata, sample_transcript, output_file)

        assert os.path.exists(output_file)

    def test_save_markdown_structure(self, sample_metadata, sample_transcript, temp_output_file):
        """Markdown 구조 테스트"""
        formatter = MarkdownFormatter()
        output_file = temp_output_file('md')

        formatter.save(sample_metadata, sample_transcript, output_file)

        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Markdown 헤더 확인
        assert '# Test Video Title' in content
        assert '## 📹 Video Information' in content
        assert '## 📝 Description' in content
        assert '## 📜 Transcript' in content

        # 표 형식 확인
        assert '| Timestamp | Text |' in content
        assert '|-----------|------|' in content

        # 내용 확인
        assert 'Test Channel' in content
        assert 'First subtitle' in content


class TestFormatterFactory:
    """포맷터 팩토리 함수 테스트"""

    def test_get_formatter_txt(self):
        """TXT 포맷터 가져오기 테스트"""
        formatter = get_formatter('1')
        assert isinstance(formatter, TxtFormatter)

    def test_get_formatter_json(self):
        """JSON 포맷터 가져오기 테스트"""
        formatter = get_formatter('2')
        assert isinstance(formatter, JsonFormatter)

    def test_get_formatter_xml(self):
        """XML 포맷터 가져오기 테스트"""
        formatter = get_formatter('3')
        assert isinstance(formatter, XmlFormatter)

    def test_get_formatter_markdown(self):
        """Markdown 포맷터 가져오기 테스트"""
        formatter = get_formatter('4')
        assert isinstance(formatter, MarkdownFormatter)

    def test_get_formatter_invalid(self):
        """잘못된 선택 테스트"""
        with pytest.raises(ValueError):
            get_formatter('5')

    def test_get_available_formatters(self):
        """사용 가능한 포맷터 목록 테스트"""
        formatters = get_available_formatters()

        assert '1' in formatters
        assert '2' in formatters
        assert '3' in formatters
        assert '4' in formatters
        assert len(formatters) == 4

        assert isinstance(formatters['1'], TxtFormatter)
        assert isinstance(formatters['2'], JsonFormatter)
        assert isinstance(formatters['3'], XmlFormatter)
        assert isinstance(formatters['4'], MarkdownFormatter)
