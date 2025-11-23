"""
AI 서비스
Gemini API를 사용한 AI 기능을 제공하는 서비스 레이어
"""

from typing import Optional, List, Dict
import logging
import time
import os

from legacy.gemini_api import GeminiClient, is_gemini_available, GeminiAPIError
from utils.config import settings

# google-genai 패키지 import 확인
try:
    from google import genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)


class AIService:
    """
    AI 기능 서비스

    Gemini API를 사용하여 요약, 번역, 주제 추출 기능을 제공합니다.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        retry_count: int = 3,
        retry_delay: float = 1.0
    ):
        """
        AI 서비스 초기화
        
        Args:
            api_key: Gemini API 키 (None이면 Settings에서 로드)
            model_name: 사용할 모델 이름 (None이면 Settings에서 로드)
            retry_count: 재시도 횟수
            retry_delay: 재시도 지연 시간 (초)
        """
        self.client = None
        self.available = False
        
        # SDK 확인
        if genai is None:
            logger.warning(
                "google-genai 패키지가 설치되지 않았습니다. "
                "'pip install google-genai'로 설치하세요."
            )
            return
        
        # API 키 확인 (우선순위: 파라미터 > Settings > 환경 변수)
        effective_api_key = (
            api_key or 
            settings.gemini_api_key or 
            os.getenv('GEMINI_API_KEY') or 
            os.getenv('GOOGLE_API_KEY')
        )
        
        if not effective_api_key:
            logger.warning(
                "Gemini API 키가 설정되지 않았습니다. "
                ".env 파일에 GEMINI_API_KEY를 설정하거나 "
                "환경 변수로 설정하세요."
            )
            return
        
        # 모델 이름 확인
        effective_model_name = model_name or settings.gemini_model_name
        
        # 클라이언트 초기화 시도
        try:
            self.client = GeminiClient(
                api_key=effective_api_key,
                model_name=effective_model_name,
                retry_count=retry_count,
                retry_delay=retry_delay
            )
            self.available = True
            logger.info(f"AI service initialized with model: {effective_model_name}")
        except GeminiAPIError as e:
            logger.warning(f"Failed to initialize AI service: {e}")
            self.available = False
        except Exception as e:
            logger.warning(f"Failed to initialize AI service (unexpected error): {e}")
            self.available = False

    def is_available(self) -> bool:
        """
        AI 서비스 사용 가능 여부를 반환합니다.

        Returns:
            사용 가능하면 True
        """
        return self.available and self.client is not None

    def generate_summary(
        self,
        transcript: List[Dict],
        max_points: int = 5,
        language: str = 'ko'
    ) -> Optional[str]:
        """
        자막에서 요약을 생성합니다.

        Args:
            transcript: 자막 데이터 리스트
            max_points: 최대 요약 포인트 수
            language: 요약 언어

        Returns:
            생성된 요약 문자열 또는 None
        """
        if not self.is_available():
            logger.warning("AI service not available for summary generation")
            return None

        try:
            summary = self.client.generate_summary(
                transcript=transcript,
                max_points=max_points,
                language=language
            )
            logger.info("Successfully generated summary")
            return summary
        except GeminiAPIError as e:
            logger.error(f"Failed to generate summary: {e}")
            return None

    def generate_summary_from_text(
        self,
        text: str,
        max_points: int = 5,
        language: str = 'ko'
    ) -> Optional[str]:
        """
        텍스트에서 요약을 생성합니다.

        Args:
            text: 요약할 텍스트
            max_points: 최대 요약 포인트 수
            language: 요약 언어

        Returns:
            생성된 요약 문자열 또는 None
        """
        if not self.is_available():
            logger.warning("AI service not available for summary generation")
            return None

        # 텍스트를 자막 형식으로 변환
        transcript = [{'text': text, 'start': 0, 'duration': 0}]
        return self.generate_summary(transcript, max_points, language)

    def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Optional[str]:
        """
        텍스트를 번역합니다.

        Args:
            text: 번역할 텍스트
            target_language: 대상 언어 코드
            source_language: 원본 언어 코드 (None이면 자동 감지)

        Returns:
            번역된 텍스트 또는 None
        """
        if not self.is_available():
            logger.warning("AI service not available for translation")
            return None

        try:
            translated = self.client.translate_text(
                text=text,
                target_language=target_language,
                source_language=source_language
            )
            logger.info(f"Successfully translated text to {target_language}")
            return translated
        except GeminiAPIError as e:
            logger.error(f"Failed to translate text: {e}")
            return None

    def translate_transcript(
        self,
        transcript: List[Dict],
        target_language: str,
        source_language: Optional[str] = None
    ) -> Optional[str]:
        """
        자막 전체를 번역합니다.

        Args:
            transcript: 자막 데이터 리스트
            target_language: 대상 언어 코드
            source_language: 원본 언어 코드

        Returns:
            번역된 텍스트 또는 None
        """
        if not self.is_available():
            logger.warning("AI service not available for transcript translation")
            return None

        try:
            translated = self.client.translate_transcript(
                transcript=transcript,
                target_language=target_language,
                source_language=source_language
            )
            logger.info(f"Successfully translated transcript to {target_language}")
            return translated
        except GeminiAPIError as e:
            logger.error(f"Failed to translate transcript: {e}")
            return None

    def extract_topics(
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
            language: 주제 언어

        Returns:
            주제 리스트 또는 None
        """
        if not self.is_available():
            logger.warning("AI service not available for topic extraction")
            return None

        try:
            topics = self.client.extract_key_topics(
                transcript=transcript,
                num_topics=num_topics,
                language=language
            )
            logger.info(f"Successfully extracted {len(topics) if topics else 0} topics")
            return topics
        except GeminiAPIError as e:
            logger.error(f"Failed to extract topics: {e}")
            return None

    def extract_topics_from_text(
        self,
        text: str,
        num_topics: int = 5,
        language: str = 'ko'
    ) -> Optional[List[str]]:
        """
        텍스트에서 핵심 주제를 추출합니다.

        Args:
            text: 분석할 텍스트
            num_topics: 추출할 주제 수
            language: 주제 언어

        Returns:
            주제 리스트 또는 None
        """
        if not self.is_available():
            logger.warning("AI service not available for topic extraction")
            return None

        # 텍스트를 자막 형식으로 변환
        transcript = [{'text': text, 'start': 0, 'duration': 0}]
        return self.extract_topics(transcript, num_topics, language)

    def enhance_transcript(
        self,
        transcript: List[Dict],
        enable_summary: bool = False,
        summary_max_points: int = 5,
        enable_translation: bool = False,
        target_language: Optional[str] = None,
        enable_topics: bool = False,
        num_topics: int = 5,
        language: str = 'ko'
    ) -> Dict:
        """
        자막을 AI로 향상시킵니다 (요약, 번역, 주제 추출).

        Args:
            transcript: 자막 데이터 리스트
            enable_summary: 요약 활성화
            summary_max_points: 요약 포인트 수
            enable_translation: 번역 활성화
            target_language: 번역 대상 언어
            enable_topics: 주제 추출 활성화
            num_topics: 추출할 주제 수
            language: 기본 언어

        Returns:
            향상된 데이터를 포함한 딕셔너리
        """
        result = {
            'summary': None,
            'translation': None,
            'topics': None,
            'processing_time': 0.0
        }

        if not self.is_available():
            logger.warning("AI service not available for enhancement")
            return result

        start_time = time.time()

        # 요약 생성
        if enable_summary:
            result['summary'] = self.generate_summary(
                transcript=transcript,
                max_points=summary_max_points,
                language=language
            )

        # 번역
        if enable_translation and target_language:
            result['translation'] = self.translate_transcript(
                transcript=transcript,
                target_language=target_language
            )

        # 주제 추출
        if enable_topics:
            result['topics'] = self.extract_topics(
                transcript=transcript,
                num_topics=num_topics,
                language=language
            )

        result['processing_time'] = time.time() - start_time
        logger.info(f"Enhancement completed in {result['processing_time']:.2f}s")

        return result
