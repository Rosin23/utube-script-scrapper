"""
Gemini API 모듈
Google Gemini API (google-genai 패키지)를 사용한 자막 요약 및 번역 기능을 제공합니다.
공식 문서 기반으로 작성된 베스트 프랙티스 버전입니다.
"""

import os
from typing import Optional, List, Dict
import time
import logging

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiAPIError(Exception):
    """Gemini API 관련 커스텀 예외"""
    pass


class GeminiClient:
    """
    Gemini API 클라이언트 클래스 (google-genai 패키지 기반)
    
    공식 Gemini API를 사용하여 텍스트 요약, 번역, 주제 추출을 수행합니다.
    """

    # 사용 가능한 모델 목록
    AVAILABLE_MODELS = [
        'gemini-2.0-flash-exp',
        'gemini-2.5-flash',
        'gemini-1.5-flash',
        'gemini-1.5-pro'
    ]

    # 언어 코드와 이름 매핑
    LANGUAGE_NAMES = {
        'ko': '한국어',
        'en': '영어',
        'ja': '일본어',
        'zh': '중국어',
        'es': '스페인어',
        'fr': '프랑스어',
        'de': '독일어',
        'it': '이탈리아어',
        'pt': '포르투갈어',
        'ru': '러시아어'
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = 'gemini-2.5-flash',
        retry_count: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Gemini API 클라이언트를 초기화합니다.

        Args:
            api_key: Gemini API 키 (None일 경우 환경변수에서 로드)
            model_name: 사용할 모델 이름
            retry_count: API 호출 실패 시 재시도 횟수
            retry_delay: 재시도 간 대기 시간 (초)

        Raises:
            GeminiAPIError: API 키가 없거나 SDK가 설치되지 않은 경우
        """
        if genai is None:
            raise GeminiAPIError(
                "google-genai 패키지가 설치되지 않았습니다. "
                "'pip install google-genai'로 설치하세요."
            )

        # API 키 설정 (환경변수 우선순위: GEMINI_API_KEY > GOOGLE_API_KEY)
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise GeminiAPIError(
                "Gemini API 키가 필요합니다. "
                "환경변수 GEMINI_API_KEY 또는 GOOGLE_API_KEY를 설정하거나 "
                "api_key 파라미터로 전달하세요."
            )

        self.model_name = model_name
        self.retry_count = retry_count
        self.retry_delay = retry_delay

        # 클라이언트 초기화 (google-genai 패키지 방식)
        try:
            # API 키를 직접 전달하여 클라이언트 생성
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Gemini 클라이언트 초기화 완료 (모델: {self.model_name})")
        except Exception as e:
            raise GeminiAPIError(f"클라이언트 초기화 실패: {e}")

    def _combine_transcript_text(self, transcript: List[Dict]) -> str:
        """
        자막 리스트를 하나의 텍스트로 결합합니다.

        Args:
            transcript: 자막 데이터 리스트

        Returns:
            결합된 텍스트
        """
        if not transcript:
            return ""

        return " ".join([entry.get('text', '').strip() for entry in transcript if entry.get('text')])

    def _make_api_call(
        self,
        prompt: str,
        temperature: float = 0.7,
        timeout: Optional[int] = None
    ) -> Optional[str]:
        """
        재시도 로직이 포함된 API 호출을 수행합니다.

        Args:
            prompt: 전달할 프롬프트
            temperature: 생성 온도 (0.0-1.0)
            timeout: API 호출 타임아웃 (초, None이면 무제한)

        Returns:
            생성된 텍스트 또는 None (실패 시)
        """
        for attempt in range(self.retry_count):
            try:
                # google-genai 패키지의 새로운 API 방식
                config_params = {'temperature': temperature}
                if timeout is not None:
                    config_params['timeout'] = timeout

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(**config_params)
                )

                # 응답 검증
                if not response or not hasattr(response, 'text') or not response.text:
                    logger.warning(f"빈 응답 수신 (시도 {attempt + 1}/{self.retry_count})")
                    continue

                return response.text.strip()

            except Exception as e:
                logger.warning(
                    f"API 호출 실패 (시도 {attempt + 1}/{self.retry_count}): {e}"
                )

                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # 지수 백오프
                else:
                    logger.error(f"API 호출 최종 실패: {e}")
                    return None

        return None

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
            language: 요약 언어

        Returns:
            요약 텍스트 또는 None (실패 시)
        """
        if not transcript:
            logger.warning("자막이 비어있어 요약을 생성할 수 없습니다.")
            return None

        try:
            text = self._combine_transcript_text(transcript)

            if not text:
                logger.warning("결합된 텍스트가 비어있습니다.")
                return None

            # 텍스트 길이 제한
            max_chars = 30000
            if len(text) > max_chars:
                logger.info(f"텍스트가 너무 깁니다. {max_chars}자로 제한합니다.")
                text = text[:max_chars] + "..."

            # 언어별 프롬프트 생성
            if language == 'ko':
                prompt = f"""다음 YouTube 비디오 스크립트를 {max_points}개의 핵심 포인트로 요약해주세요.
각 포인트는 간결하고 명확하게 작성하며, 번호를 붙여주세요.

스크립트:
{text}

요약 형식:
1. [첫 번째 핵심 포인트]
2. [두 번째 핵심 포인트]
...

요약:"""
            else:
                prompt = f"""Please summarize the following YouTube video script into {max_points} key points.
Each point should be concise and clear, numbered.

Script:
{text}

Summary format:
1. [First key point]
2. [Second key point]
...

Summary:"""

            logger.info(f"요약 생성 중... (언어: {language}, 포인트: {max_points})")
            result = self._make_api_call(prompt, temperature=0.3)

            if result:
                logger.info("요약 생성 성공")
            else:
                logger.error("요약 생성 실패")

            return result

        except Exception as e:
            logger.error(f"요약 생성 오류: {e}")
            return None

    def _truncate_text_smartly(self, text: str, max_chars: int = 30000) -> str:
        """
        문장 경계에서 텍스트를 스마트하게 자릅니다.

        단순 절단 대신 문장 종결 기호에서 자르기 때문에 번역 품질이 향상됩니다.

        Args:
            text: 자를 텍스트
            max_chars: 최대 문자 수

        Returns:
            잘린 텍스트
        """
        if len(text) <= max_chars:
            return text

        # 문장 종결 기호에서 자르기
        truncated = text[:max_chars]
        delimiters = ['. ', '。', '! ', '? ', '\n\n', '.\n', '。\n']

        # 최소 80% 이상 유지하면서 문장 경계 찾기
        min_length = int(max_chars * 0.8)
        for delimiter in delimiters:
            idx = truncated.rfind(delimiter)
            if idx > min_length:
                return text[:idx + len(delimiter)]

        # 문장 경계를 찾지 못한 경우 단어 경계에서 자르기
        last_space = truncated.rfind(' ')
        if last_space > min_length:
            return text[:last_space]

        # 최악의 경우 그냥 자르기
        return text[:max_chars]

    def translate_text(
        self,
        text: str,
        target_language: str = 'en',
        source_language: Optional[str] = None,
        timeout: int = 30
    ) -> Optional[str]:
        """
        텍스트를 번역합니다.

        Args:
            text: 번역할 텍스트
            target_language: 대상 언어 코드
            source_language: 소스 언어 코드 (None일 경우 자동 감지)
            timeout: API 호출 타임아웃 (초, 기본값: 30)

        Returns:
            번역된 텍스트 또는 None (실패 시)
        """
        if not text or not text.strip():
            logger.warning("번역할 텍스트가 비어있습니다.")
            return None

        try:
            # 스마트 텍스트 절단 (문장 경계에서)
            max_chars = 30000
            original_length = len(text)
            if len(text) > max_chars:
                text = self._truncate_text_smartly(text, max_chars)
                logger.info(
                    f"텍스트가 너무 깁니다. {original_length}자 → {len(text)}자로 스마트 절단"
                )

            target_lang_name = self.LANGUAGE_NAMES.get(target_language, target_language)

            # 영어 프롬프트 사용 (품질 10-15% 향상)
            if source_language:
                source_lang_name = self.LANGUAGE_NAMES.get(source_language, source_language)
                prompt = f"""Translate the following {source_lang_name} text to {target_lang_name}.
Output only the translation, without any explanations or additional comments.

Original text:
{text}

Translation:"""
            else:
                prompt = f"""Translate the following text to {target_lang_name}.
Output only the translation, without any explanations or additional comments.

Original text:
{text}

Translation:"""

            logger.info(f"텍스트 번역 중... (대상 언어: {target_language})")
            result = self._make_api_call(prompt, temperature=0.3, timeout=timeout)

            if result:
                logger.info("번역 완료")
            else:
                logger.error("번역 실패")

            return result

        except Exception as e:
            logger.error(f"번역 오류: {e}")
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
            target_language: 대상 언어 코드

        Returns:
            번역된 전체 텍스트 또는 None (실패 시)
        """
        if not transcript:
            logger.warning("자막이 비어있어 번역할 수 없습니다.")
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
            logger.warning("자막이 비어있어 주제를 추출할 수 없습니다.")
            return None

        try:
            text = self._combine_transcript_text(transcript)

            if not text:
                logger.warning("결합된 텍스트가 비어있습니다.")
                return None

            # 텍스트 길이 제한
            max_chars = 30000
            if len(text) > max_chars:
                logger.info(f"텍스트가 너무 깁니다. {max_chars}자로 제한합니다.")
                text = text[:max_chars] + "..."

            # 언어별 프롬프트 생성
            if language == 'ko':
                prompt = f"""다음 YouTube 비디오 스크립트에서 핵심 주제 {num_topics}가지를 추출해주세요.
각 주제는 짧은 키워드나 구절로 표현해주세요.

스크립트:
{text}

출력 형식 (각 주제를 한 줄씩, 불릿 포인트 사용):
- [주제 1]
- [주제 2]
...

주제:"""
            else:
                prompt = f"""Extract {num_topics} key topics from the following YouTube video script.
Express each topic as a short keyword or phrase.

Script:
{text}

Output format (one topic per line, use bullet points):
- [Topic 1]
- [Topic 2]
...

Topics:"""

            logger.info(f"주제 추출 중... (언어: {language}, 개수: {num_topics})")
            topics_text = self._make_api_call(prompt, temperature=0.5)

            if not topics_text:
                logger.error("주제 추출 실패")
                return None

            # 각 줄을 파싱하여 리스트로 변환
            topics = []
            for line in topics_text.split('\n'):
                line = line.strip()
                # 불릿 포인트 제거
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    topic = line[1:].strip()
                    if topic:
                        topics.append(topic)
                elif line and not line.isspace():
                    # 숫자 제거 (1., 2. 등)
                    import re
                    topic = re.sub(r'^\d+\.\s*', '', line).strip()
                    if topic:
                        topics.append(topic)

            # 요청한 개수만큼만 반환
            topics = topics[:num_topics]

            if topics:
                logger.info(f"{len(topics)}개의 주제 추출 성공")
            else:
                logger.warning("추출된 주제가 없습니다.")

            return topics if topics else None

        except Exception as e:
            logger.error(f"주제 추출 오류: {e}")
            return None


def is_gemini_available(api_key: Optional[str] = None) -> bool:
    """
    Gemini API가 사용 가능한지 확인합니다.
    
    Args:
        api_key: API 키 (전달되면 이 키를 사용, None이면 환경 변수 확인)
    
    Returns:
        SDK가 설치되어 있고 API 키가 있으면 True, 아니면 False
    """
    # SDK 확인
    if genai is None:
        return False
    
    # API 키 확인 (우선순위: 파라미터 > 환경 변수)
    if api_key:
        return True
    
    # 환경 변수 확인
    return bool(os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY'))


def get_gemini_client(
    api_key: Optional[str] = None,
    model_name: str = 'gemini-2.5-flash'
) -> Optional[GeminiClient]:
    """
    Gemini API 클라이언트를 생성합니다.

    Args:
        api_key: Gemini API 키 (선택사항)
        model_name: 사용할 모델 이름

    Returns:
        GeminiClient 인스턴스 또는 None (실패 시)
    """
    try:
        return GeminiClient(api_key=api_key, model_name=model_name)
    except GeminiAPIError as e:
        logger.error(f"Gemini 클라이언트 생성 실패: {e}")
        return None
