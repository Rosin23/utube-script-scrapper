"""
주제 추출 도구
텍스트나 자막에서 핵심 주제를 AI로 추출하는 독립적인 도구
"""

from typing import Dict, List, Optional
import logging

from core import AIService

logger = logging.getLogger(__name__)


class TopicExtractorTool:
    """
    AI 주제 추출 도구

    에이전트가 텍스트나 자막에서 핵심 주제를 추출할 수 있도록 하는 도구입니다.

    사용 예시:
        tool = TopicExtractorTool()
        topics = tool.run(
            text="긴 텍스트 내용...",
            num_topics=5
        )
    """

    name: str = "topic_extractor"
    description: str = (
        "텍스트나 자막에서 핵심 주제를 AI로 추출합니다. "
        "내용을 분석하여 주요 토픽들을 리스트로 반환합니다."
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
        num_topics: int = 5,
        language: str = 'ko'
    ) -> Optional[List[str]]:
        """
        텍스트 또는 자막에서 핵심 주제를 추출합니다.

        Args:
            text: 분석할 텍스트 (text 또는 transcript 중 하나 필수)
            transcript: 분석할 자막 데이터
            num_topics: 추출할 주제 수 (1-20)
            language: 주제 언어 코드

        Returns:
            추출된 주제 리스트 또는 None

        Raises:
            ValueError: text와 transcript가 모두 없을 때

        Example:
            >>> tool = TopicExtractorTool()
            >>> topics = tool.run(text="텍스트 내용...", num_topics=3)
            >>> print(topics)
            ['주제 1', '주제 2', '주제 3']
        """
        if not self.ai_service.is_available():
            logger.warning("AI service not available")
            return None

        if text is None and transcript is None:
            raise ValueError("Either 'text' or 'transcript' must be provided")

        try:
            # 텍스트가 제공된 경우
            if text:
                logger.info(f"Extracting topics from text ({len(text)} chars)")
                return self.ai_service.extract_topics_from_text(
                    text=text,
                    num_topics=num_topics,
                    language=language
                )

            # 자막이 제공된 경우
            if transcript:
                logger.info(
                    f"Extracting topics from transcript ({len(transcript)} entries)"
                )
                return self.ai_service.extract_topics(
                    transcript=transcript,
                    num_topics=num_topics,
                    language=language
                )

        except Exception as e:
            logger.error(f"Failed to extract topics: {e}")
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
                "name": "topic_extractor",
                "description": (
                    "텍스트나 자막에서 핵심 주제를 AI로 추출합니다. "
                    "내용을 분석하여 주요 토픽들을 리스트로 반환합니다."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "분석할 텍스트"
                        },
                        "num_topics": {
                            "type": "integer",
                            "description": "추출할 주제 수 (1-20)",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20
                        },
                        "language": {
                            "type": "string",
                            "description": "주제 언어 코드 (ko, en, ja, zh 등)",
                            "default": "ko"
                        }
                    },
                    "required": ["text"]
                }
            }
        }
