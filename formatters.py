"""
출력 포맷터 모듈
전략 패턴(Strategy Pattern)을 사용하여 다양한 출력 형식을 지원합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from youtube_api import format_timestamp


class Formatter(ABC):
    """
    출력 포맷터 추상 클래스
    모든 포맷터는 이 클래스를 상속받아 save() 메서드를 구현해야 합니다.
    """

    def __init__(self):
        """포맷터 초기화"""
        self.file_extension = ""
        self.format_name = ""

    @abstractmethod
    def save(
        self,
        metadata: Dict,
        transcript: List[Dict],
        output_file: str,
        summary: Optional[str] = None,
        translation: Optional[str] = None,
        key_topics: Optional[List[str]] = None
    ) -> None:
        """
        데이터를 지정된 형식으로 저장합니다.

        Args:
            metadata: 비디오 메타데이터
            transcript: 타임스탬프가 포함된 자막 데이터
            output_file: 출력 파일 경로
            summary: AI 생성 요약 (선택사항)
            translation: 번역된 텍스트 (선택사항)
            key_topics: 핵심 주제 리스트 (선택사항)
        """
        pass

    def get_extension(self) -> str:
        """파일 확장자를 반환합니다."""
        return self.file_extension

    def get_name(self) -> str:
        """포맷 이름을 반환합니다."""
        return self.format_name


class TxtFormatter(Formatter):
    """구조화된 텍스트 파일 포맷터"""

    def __init__(self):
        super().__init__()
        self.file_extension = "txt"
        self.format_name = "텍스트"

    def save(
        self,
        metadata: Dict,
        transcript: List[Dict],
        output_file: str,
        summary: Optional[str] = None,
        translation: Optional[str] = None,
        key_topics: Optional[List[str]] = None
    ) -> None:
        """텍스트 파일로 저장합니다."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # 헤더
                f.write("=" * 80 + "\n")
                f.write("YouTube Video Transcript\n")
                f.write("=" * 80 + "\n\n")

                # 비디오 정보
                f.write("📹 Video Information\n")
                f.write("-" * 80 + "\n")
                f.write(f"Title: {metadata['title']}\n")
                f.write(f"Channel: {metadata['channel']}\n")
                f.write(f"Upload Date: {metadata['upload_date']}\n")
                f.write(f"Duration: {format_timestamp(metadata['duration'])}\n")
                f.write(f"Views: {metadata['view_count']:,}\n")
                f.write("\n")

                # 설명
                f.write("📝 Description\n")
                f.write("-" * 80 + "\n")
                f.write(f"{metadata['description']}\n")
                f.write("\n")

                # AI 생성 요약 (있는 경우)
                if summary:
                    f.write("🤖 AI Summary\n")
                    f.write("-" * 80 + "\n")
                    f.write(f"{summary}\n")
                    f.write("\n")

                # 핵심 주제 (있는 경우)
                if key_topics:
                    f.write("🔑 Key Topics\n")
                    f.write("-" * 80 + "\n")
                    for topic in key_topics:
                        f.write(f"• {topic}\n")
                    f.write("\n")

                # 번역 (있는 경우)
                if translation:
                    f.write("🌐 Translation\n")
                    f.write("-" * 80 + "\n")
                    f.write(f"{translation}\n")
                    f.write("\n")

                # 자막 (타임스탬프 포함)
                if transcript:
                    f.write("📜 Transcript with Timestamps\n")
                    f.write("=" * 80 + "\n\n")

                    for entry in transcript:
                        timestamp = format_timestamp(entry['start'])
                        text = entry['text'].strip()
                        f.write(f"[{timestamp}] {text}\n")

                    f.write("\n")
                    f.write("=" * 80 + "\n")
                    f.write(f"Total transcript entries: {len(transcript)}\n")
                else:
                    f.write("📜 Transcript\n")
                    f.write("=" * 80 + "\n")
                    f.write("No transcript available for this video.\n")

                f.write(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            print(f"\n✅ 파일이 성공적으로 생성되었습니다: {output_file}")

        except Exception as e:
            raise IOError(f"파일 생성 오류: {e}")


class JsonFormatter(Formatter):
    """JSON 파일 포맷터"""

    def __init__(self):
        super().__init__()
        self.file_extension = "json"
        self.format_name = "JSON"

    def save(
        self,
        metadata: Dict,
        transcript: List[Dict],
        output_file: str,
        summary: Optional[str] = None,
        translation: Optional[str] = None,
        key_topics: Optional[List[str]] = None
    ) -> None:
        """JSON 파일로 저장합니다."""
        try:
            # JSON 구조 생성
            data = {
                "video_info": {
                    "title": metadata['title'],
                    "channel": metadata['channel'],
                    "upload_date": metadata['upload_date'],
                    "duration": metadata['duration'],
                    "duration_formatted": format_timestamp(metadata['duration']),
                    "view_count": metadata['view_count']
                },
                "description": metadata['description'],
                "transcript": [
                    {
                        "timestamp": format_timestamp(entry['start']),
                        "start_seconds": entry['start'],
                        "duration": entry['duration'],
                        "text": entry['text'].strip()
                    }
                    for entry in transcript
                ],
                "metadata": {
                    "total_entries": len(transcript),
                    "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }

            # AI 기능 추가
            if summary:
                data["ai_summary"] = summary
            if key_topics:
                data["key_topics"] = key_topics
            if translation:
                data["translation"] = translation

            # JSON 파일 저장
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"\n✅ JSON 파일이 성공적으로 생성되었습니다: {output_file}")

        except Exception as e:
            raise IOError(f"JSON 파일 생성 오류: {e}")


class XmlFormatter(Formatter):
    """XML 파일 포맷터"""

    def __init__(self):
        super().__init__()
        self.file_extension = "xml"
        self.format_name = "XML"

    def save(
        self,
        metadata: Dict,
        transcript: List[Dict],
        output_file: str,
        summary: Optional[str] = None,
        translation: Optional[str] = None,
        key_topics: Optional[List[str]] = None
    ) -> None:
        """XML 파일로 저장합니다."""
        try:
            # 루트 엘리먼트 생성
            root = ET.Element('youtube_transcript')

            # 비디오 정보
            video_info = ET.SubElement(root, 'video_info')
            ET.SubElement(video_info, 'title').text = metadata['title']
            ET.SubElement(video_info, 'channel').text = metadata['channel']
            ET.SubElement(video_info, 'upload_date').text = metadata['upload_date']
            ET.SubElement(video_info, 'duration').text = str(metadata['duration'])
            ET.SubElement(video_info, 'duration_formatted').text = format_timestamp(metadata['duration'])
            ET.SubElement(video_info, 'view_count').text = str(metadata['view_count'])

            # 설명
            description = ET.SubElement(root, 'description')
            description.text = metadata['description']

            # AI 기능 (있는 경우)
            if summary:
                ai_summary = ET.SubElement(root, 'ai_summary')
                ai_summary.text = summary

            if key_topics:
                topics_element = ET.SubElement(root, 'key_topics')
                for topic in key_topics:
                    topic_element = ET.SubElement(topics_element, 'topic')
                    topic_element.text = topic

            if translation:
                translation_element = ET.SubElement(root, 'translation')
                translation_element.text = translation

            # 자막
            transcript_element = ET.SubElement(root, 'transcript')
            for entry in transcript:
                entry_element = ET.SubElement(transcript_element, 'entry')
                ET.SubElement(entry_element, 'timestamp').text = format_timestamp(entry['start'])
                ET.SubElement(entry_element, 'start_seconds').text = str(entry['start'])
                ET.SubElement(entry_element, 'duration').text = str(entry['duration'])
                ET.SubElement(entry_element, 'text').text = entry['text'].strip()

            # 메타데이터
            metadata_element = ET.SubElement(root, 'metadata')
            ET.SubElement(metadata_element, 'total_entries').text = str(len(transcript))
            ET.SubElement(metadata_element, 'generated_at').text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # XML 트리 생성 및 저장
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ")  # Pretty print
            tree.write(output_file, encoding='utf-8', xml_declaration=True)

            print(f"\n✅ XML 파일이 성공적으로 생성되었습니다: {output_file}")

        except Exception as e:
            raise IOError(f"XML 파일 생성 오류: {e}")


class MarkdownFormatter(Formatter):
    """Markdown 파일 포맷터"""

    def __init__(self):
        super().__init__()
        self.file_extension = "md"
        self.format_name = "Markdown"

    def save(
        self,
        metadata: Dict,
        transcript: List[Dict],
        output_file: str,
        summary: Optional[str] = None,
        translation: Optional[str] = None,
        key_topics: Optional[List[str]] = None
    ) -> None:
        """Markdown 파일로 저장합니다."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # 제목
                f.write(f"# {metadata['title']}\n\n")

                # 비디오 정보
                f.write("## 📹 Video Information\n\n")
                f.write(f"- **Title**: {metadata['title']}\n")
                f.write(f"- **Channel**: {metadata['channel']}\n")
                f.write(f"- **Upload Date**: {metadata['upload_date']}\n")
                f.write(f"- **Duration**: {format_timestamp(metadata['duration'])}\n")
                f.write(f"- **Views**: {metadata['view_count']:,}\n\n")

                # 설명
                f.write("## 📝 Description\n\n")
                f.write(f"{metadata['description']}\n\n")

                # AI 생성 요약 (있는 경우)
                if summary:
                    f.write("## 🤖 AI Summary\n\n")
                    f.write(f"{summary}\n\n")

                # 핵심 주제 (있는 경우)
                if key_topics:
                    f.write("## 🔑 Key Topics\n\n")
                    for topic in key_topics:
                        f.write(f"- {topic}\n")
                    f.write("\n")

                # 번역 (있는 경우)
                if translation:
                    f.write("## 🌐 Translation\n\n")
                    f.write(f"{translation}\n\n")

                # 자막
                if transcript:
                    f.write("## 📜 Transcript\n\n")
                    f.write("| Timestamp | Text |\n")
                    f.write("|-----------|------|\n")

                    for entry in transcript:
                        timestamp = format_timestamp(entry['start'])
                        text = entry['text'].strip().replace('\n', ' ').replace('|', '\\|')
                        f.write(f"| `{timestamp}` | {text} |\n")

                    f.write(f"\n**Total transcript entries**: {len(transcript)}\n\n")
                else:
                    f.write("## 📜 Transcript\n\n")
                    f.write("No transcript available for this video.\n\n")

                # 메타데이터
                f.write("---\n\n")
                f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

            print(f"\n✅ Markdown 파일이 성공적으로 생성되었습니다: {output_file}")

        except Exception as e:
            raise IOError(f"Markdown 파일 생성 오류: {e}")


# 포맷터 팩토리 함수
def get_formatter(format_choice: str) -> Formatter:
    """
    선택한 형식에 해당하는 포맷터를 반환합니다.

    Args:
        format_choice: 형식 선택 (1-4)

    Returns:
        Formatter 인스턴스

    Raises:
        ValueError: 잘못된 형식 선택
    """
    formatters = {
        '1': TxtFormatter(),
        '2': JsonFormatter(),
        '3': XmlFormatter(),
        '4': MarkdownFormatter()
    }

    if format_choice not in formatters:
        raise ValueError(f"잘못된 형식 선택: {format_choice}. 1-4 중 선택해주세요.")

    return formatters[format_choice]


# 사용 가능한 포맷터 목록 가져오기
def get_available_formatters() -> Dict[str, Formatter]:
    """
    사용 가능한 모든 포맷터의 딕셔너리를 반환합니다.

    Returns:
        포맷터 딕셔너리 {선택번호: Formatter 인스턴스}
    """
    return {
        '1': TxtFormatter(),
        '2': JsonFormatter(),
        '3': XmlFormatter(),
        '4': MarkdownFormatter()
    }
