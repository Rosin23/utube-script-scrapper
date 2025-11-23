"""
포맷터 서비스
다양한 출력 형식을 지원하는 서비스 레이어
"""

from typing import Optional, List, Dict
import logging
import os

from legacy.formatters import get_formatter, get_available_formatters, Formatter

logger = logging.getLogger(__name__)


class FormatterService:
    """
    출력 포맷터 서비스

    다양한 형식(TXT, JSON, XML, Markdown)으로 데이터를 저장합니다.
    """

    # 포맷 이름과 선택 번호 매핑
    FORMAT_MAP = {
        'txt': '1',
        'json': '2',
        'xml': '3',
        'markdown': '4',
        'md': '4',
    }

    def __init__(self):
        """서비스 초기화"""
        pass

    @staticmethod
    def get_available_formats() -> List[str]:
        """
        사용 가능한 출력 형식 목록을 반환합니다.

        Returns:
            형식 목록
        """
        return get_available_formatters()

    def get_formatter(self, format_choice: str) -> Formatter:
        """
        지정된 형식에 해당하는 포맷터를 반환합니다.

        Args:
            format_choice: 형식 선택 ('1', '2', '3', '4' 또는 'txt', 'json', 'xml', 'markdown')

        Returns:
            Formatter 인스턴스
        """
        # 문자열 형식을 번호로 변환
        if format_choice.lower() in self.FORMAT_MAP:
            format_choice = self.FORMAT_MAP[format_choice.lower()]

        formatter = get_formatter(format_choice)
        logger.info(f"Using formatter: {formatter.format_name}")
        return formatter

    def save_to_file(
        self,
        metadata: Dict,
        transcript: List[Dict],
        output_file: str,
        format_choice: str = 'json',
        summary: Optional[str] = None,
        translation: Optional[str] = None,
        key_topics: Optional[List[str]] = None
    ) -> str:
        """
        데이터를 지정된 형식으로 파일에 저장합니다.

        Args:
            metadata: 비디오 메타데이터
            transcript: 자막 데이터
            output_file: 출력 파일 경로 (확장자 없이)
            format_choice: 형식 선택
            summary: AI 생성 요약 (선택사항)
            translation: 번역된 텍스트 (선택사항)
            key_topics: 핵심 주제 리스트 (선택사항)

        Returns:
            저장된 파일 경로
        """
        # 포맷터 가져오기
        formatter = self.get_formatter(format_choice)

        # 파일 경로에 확장자 추가
        if not output_file.endswith(f".{formatter.file_extension}"):
            output_file = f"{output_file}.{formatter.file_extension}"

        # 디렉토리 생성
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created directory: {output_dir}")

        # 파일 저장
        try:
            formatter.save(
                metadata=metadata,
                transcript=transcript,
                output_file=output_file,
                summary=summary,
                translation=translation,
                key_topics=key_topics
            )
            logger.info(f"Successfully saved to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Failed to save file {output_file}: {e}")
            raise

    def format_data(
        self,
        metadata: Dict,
        transcript: List[Dict],
        format_choice: str = 'json',
        summary: Optional[str] = None,
        translation: Optional[str] = None,
        key_topics: Optional[List[str]] = None
    ) -> str:
        """
        데이터를 지정된 형식의 문자열로 변환합니다 (파일 저장 없이).

        Args:
            metadata: 비디오 메타데이터
            transcript: 자막 데이터
            format_choice: 형식 선택
            summary: AI 생성 요약 (선택사항)
            translation: 번역된 텍스트 (선택사항)
            key_topics: 핵심 주제 리스트 (선택사항)

        Returns:
            포맷팅된 문자열
        """
        import tempfile
        import os

        # 임시 파일 생성
        formatter = self.get_formatter(format_choice)
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=f'.{formatter.file_extension}',
            delete=False
        ) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # 임시 파일에 저장
            formatter.save(
                metadata=metadata,
                transcript=transcript,
                output_file=tmp_path,
                summary=summary,
                translation=translation,
                key_topics=key_topics
            )

            # 파일 내용 읽기
            with open(tmp_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return content
        finally:
            # 임시 파일 삭제
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
