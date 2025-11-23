"""
번역 도구
텍스트를 AI로 번역하는 독립적인 도구
"""

from typing import Dict, Optional
import logging

from core import AIService

logger = logging.getLogger(__name__)


class TranslatorTool:
    """
    AI 번역 도구

    에이전트가 텍스트를 다른 언어로 번역할 수 있도록 하는 도구입니다.

    사용 예시:
        tool = TranslatorTool()
        translated = tool.run(
            text="안녕하세요",
            target_language="en"
        )
    """

    name: str = "translator"
    description: str = (
        "텍스트를 AI로 번역합니다. "
        "다양한 언어 간 번역을 지원하며, 자연스러운 번역을 제공합니다."
    )

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.0-flash-exp"
    ):
        """
        도구 초기화

        Args:
            api_key: Gemini API 키 (None이면 환경변수 사용)
            model_name: 사용할 AI 모델 이름
        """
        self.ai_service = AIService(api_key=api_key, model_name=model_name)

    def run(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Optional[str]:
        """
        텍스트를 번역합니다.

        Args:
            text: 번역할 텍스트 (필수)
            target_language: 대상 언어 코드 (필수, 예: 'en', 'ko', 'ja')
            source_language: 원본 언어 코드 (선택, None이면 자동 감지)

        Returns:
            번역된 텍스트 또는 None

        Raises:
            ValueError: text나 target_language가 없을 때

        Example:
            >>> tool = TranslatorTool()
            >>> result = tool.run(
            ...     text="안녕하세요",
            ...     target_language="en"
            ... )
            >>> print(result)
            'Hello'
        """
        if not self.ai_service.is_available():
            logger.warning("AI service not available")
            return None

        if not text:
            raise ValueError("'text' is required")

        if not target_language:
            raise ValueError("'target_language' is required")

        try:
            logger.info(
                f"Translating text ({len(text)} chars) to {target_language}"
            )

            translated = self.ai_service.translate_text(
                text=text,
                target_language=target_language,
                source_language=source_language
            )

            if translated:
                logger.info(f"Translation successful ({len(translated)} chars)")

            return translated

        except Exception as e:
            logger.error(f"Failed to translate text: {e}")
            return None

    def is_available(self) -> bool:
        """
        AI 서비스 사용 가능 여부를 확인합니다.

        Returns:
            사용 가능하면 True
        """
        return self.ai_service.is_available()

    @staticmethod
    def get_supported_languages() -> Dict[str, str]:
        """
        지원하는 언어 목록을 반환합니다.

        Returns:
            언어 코드와 이름 매핑
        """
        return {
            'ko': '한국어',
            'en': '영어',
            'ja': '일본어',
            'zh': '중국어',
            'es': '스페인어',
            'fr': '프랑스어',
            'de': '독일어',
            'ru': '러시아어',
            'ar': '아랍어',
            'pt': '포르투갈어',
            'it': '이탈리아어',
            'vi': '베트남어',
            'th': '태국어',
            'id': '인도네시아어',
        }

    @staticmethod
    def get_tool_schema() -> Dict:
        """
        에이전트 프레임워크를 위한 도구 스키마를 반환합니다.

        Returns:
            OpenAI function calling 형식의 스키마
        """
        return {
            "type": "function",
            "function": {
                "name": "translator",
                "description": (
                    "텍스트를 AI로 번역합니다. "
                    "다양한 언어 간 번역을 지원합니다."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "번역할 텍스트"
                        },
                        "target_language": {
                            "type": "string",
                            "description": "대상 언어 코드 (ko, en, ja, zh 등)"
                        },
                        "source_language": {
                            "type": "string",
                            "description": "원본 언어 코드 (선택, 없으면 자동 감지)"
                        }
                    },
                    "required": ["text", "target_language"]
                }
            }
        }
