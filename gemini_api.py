"""
Gemini API 모듈
Google Gemini API를 사용한 자막 요약 및 번역 기능을 제공합니다.
"""

import os
from typing import Optional, List, Dict
import google.generativeai as genai


class GeminiClient:
    """Gemini API 클라이언트 클래스"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Gemini API 클라이언트를 초기화합니다.

        Args:
            api_key: Gemini API 키 (None일 경우 환경변수에서 로드)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Gemini API 키가 필요합니다. "
                "환경변수 GEMINI_API_KEY를 설정하거나 api_key 파라미터로 전달하세요."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def _combine_transcript_text(self, transcript: List[Dict]) -> str:
        """
        자막 리스트를 하나의 텍스트로 결합합니다.

        Args:
            transcript: 자막 데이터 리스트

        Returns:
            결합된 텍스트
        """
        return " ".join([entry.get('text', '').strip() for entry in transcript])

    def generate_summary(
        self,
        transcript: List[Dict],
        max_points: int = 5,
        language: str = 'ko'
    ) -> Optional[str]:
        """
        자막을 요약합니다.

        Args:
            transcript: 자막 데이터 리스트
            max_points: 최대 요약 포인트 수
            language: 요약 언어 ('ko', 'en' 등)

        Returns:
            요약 텍스트 또는 None (실패 시)
        """
        if not transcript:
            return None

        try:
            text = self._combine_transcript_text(transcript)

            if language == 'ko':
                prompt = f"""다음 YouTube 비디오 스크립트를 {max_points}개의 핵심 포인트로 요약해주세요.
각 포인트는 간결하고 명확하게 작성해주세요.

스크립트:
{text}

요약 형식:
1. [첫 번째 핵심 포인트]
2. [두 번째 핵심 포인트]
...
"""
            else:
                prompt = f"""Please summarize the following YouTube video script into {max_points} key points.
Each point should be concise and clear.

Script:
{text}

Summary format:
1. [First key point]
2. [Second key point]
...
"""

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            print(f"⚠️  요약 생성 오류: {e}")
            return None

    def translate_text(
        self,
        text: str,
        target_language: str = 'en',
        source_language: Optional[str] = None
    ) -> Optional[str]:
        """
        텍스트를 번역합니다.

        Args:
            text: 번역할 텍스트
            target_language: 대상 언어
            source_language: 소스 언어 (None일 경우 자동 감지)

        Returns:
            번역된 텍스트 또는 None (실패 시)
        """
        if not text:
            return None

        try:
            language_names = {
                'ko': '한국어',
                'en': '영어',
                'ja': '일본어',
                'zh': '중국어',
                'es': '스페인어',
                'fr': '프랑스어',
                'de': '독일어'
            }

            target_lang_name = language_names.get(target_language, target_language)

            if source_language:
                source_lang_name = language_names.get(source_language, source_language)
                prompt = f"다음 {source_lang_name} 텍스트를 {target_lang_name}로 번역해주세요. 번역 결과만 출력하세요:\n\n{text}"
            else:
                prompt = f"다음 텍스트를 {target_lang_name}로 번역해주세요. 번역 결과만 출력하세요:\n\n{text}"

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            print(f"⚠️  번역 오류: {e}")
            return None

    def translate_transcript(
        self,
        transcript: List[Dict],
        target_language: str = 'en'
    ) -> Optional[str]:
        """
        전체 자막을 번역합니다.

        Args:
            transcript: 자막 데이터 리스트
            target_language: 대상 언어

        Returns:
            번역된 전체 텍스트 또는 None (실패 시)
        """
        if not transcript:
            return None

        text = self._combine_transcript_text(transcript)
        return self.translate_text(text, target_language)

    def extract_key_topics(
        self,
        transcript: List[Dict],
        num_topics: int = 5,
        language: str = 'ko'
    ) -> Optional[List[str]]:
        """
        자막에서 핵심 주제를 추출합니다.

        Args:
            transcript: 자막 데이터 리스트
            num_topics: 추출할 주제 수
            language: 출력 언어

        Returns:
            핵심 주제 리스트 또는 None (실패 시)
        """
        if not transcript:
            return None

        try:
            text = self._combine_transcript_text(transcript)

            if language == 'ko':
                prompt = f"""다음 YouTube 비디오 스크립트에서 핵심 주제 {num_topics}가지를 추출해주세요.
각 주제는 짧은 키워드나 구절로 표현해주세요.

스크립트:
{text}

출력 형식 (각 주제를 한 줄씩):
- [주제 1]
- [주제 2]
...
"""
            else:
                prompt = f"""Extract {num_topics} key topics from the following YouTube video script.
Express each topic as a short keyword or phrase.

Script:
{text}

Output format (one topic per line):
- [Topic 1]
- [Topic 2]
...
"""

            response = self.model.generate_content(prompt)
            topics_text = response.text.strip()

            # 각 줄을 파싱하여 리스트로 변환
            topics = []
            for line in topics_text.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    topics.append(line[1:].strip())
                elif line and not line.isspace():
                    topics.append(line)

            return topics[:num_topics] if topics else None

        except Exception as e:
            print(f"⚠️  주제 추출 오류: {e}")
            return None


def is_gemini_available() -> bool:
    """
    Gemini API가 사용 가능한지 확인합니다.

    Returns:
        API 키가 설정되어 있으면 True, 아니면 False
    """
    return bool(os.getenv('GEMINI_API_KEY'))
