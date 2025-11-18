"""
요약 생성 도구
텍스트나 자막을 AI로 요약하는 독립적인 도구
"""

from typing import Dict, List, Optional
import logging

from core import AIService

logger = logging.getLogger(__name__)


class SummarizerTool:
    """
    AI 요약 생성 도구

    에이전트가 텍스트나 자막을 요약할 수 있도록 하는 도구입니다.

    사용 예시:
        tool = SummarizerTool()
        summary = tool.run(
            text="긴 텍스트 내용...",
            max_points=5,
            language="ko"
        )
    """

    name: str = "summarizer"
    description: str = (
        "텍스트나 자막을 AI로 요약합니다. "
        "긴 내용을 주요 포인트로 압축하여 이해하기 쉽게 만듭니다."
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
        text: Optional[str] = None,
        transcript: Optional[List[Dict]] = None,
        max_points: int = 5,
        language: str = 'ko'
    ) -> Optional[str]:
        """
        텍스트 또는 자막을 요약합니다.

        Args:
            text: 요약할 텍스트 (text 또는 transcript 중 하나 필수)
            transcript: 요약할 자막 데이터
            max_points: 최대 요약 포인트 수 (1-10)
            language: 요약 언어 코드

        Returns:
            생성된 요약 문자열 또는 None

        Raises:
            ValueError: text와 transcript가 모두 없을 때

        Example:
            >>> tool = SummarizerTool()
            >>> summary = tool.run(text="긴 텍스트...", max_points=3)
            >>> print(summary)
        """
        if not self.ai_service.is_available():
            logger.warning("AI service not available")
            return None

        if text is None and transcript is None:
            raise ValueError("Either 'text' or 'transcript' must be provided")

        try:
            # 텍스트가 제공된 경우
            if text:
                logger.info(f"Summarizing text ({len(text)} chars)")
                return self.ai_service.generate_summary_from_text(
                    text=text,
                    max_points=max_points,
                    language=language
                )

            # 자막이 제공된 경우
            if transcript:
                logger.info(f"Summarizing transcript ({len(transcript)} entries)")
                return self.ai_service.generate_summary(
                    transcript=transcript,
                    max_points=max_points,
                    language=language
                )

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return None

    def is_available(self) -> bool:
        """
        AI 서비스 사용 가능 여부를 확인합니다.

        Returns:
            사용 가능하면 True
        """
        return self.ai_service.is_available()

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
                "name": "summarizer",
                "description": (
                    "텍스트나 자막을 AI로 요약합니다. "
                    "긴 내용을 주요 포인트로 압축하여 반환합니다."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "요약할 텍스트"
                        },
                        "max_points": {
                            "type": "integer",
                            "description": "최대 요약 포인트 수 (1-10)",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 10
                        },
                        "language": {
                            "type": "string",
                            "description": "요약 언어 코드 (ko, en, ja, zh 등)",
                            "default": "ko"
                        }
                    },
                    "required": ["text"]
                }
            }
        }
