"""
비디오 스크래퍼 도구
YouTube 비디오에서 메타데이터와 자막을 추출하는 독립적인 도구
"""

from typing import Dict, List, Optional
import logging

from core import YouTubeService

logger = logging.getLogger(__name__)


class VideoScraperTool:
    """
    YouTube 비디오 스크래핑 도구

    에이전트가 YouTube 비디오에서 정보를 추출할 수 있도록 하는 도구입니다.

    사용 예시:
        tool = VideoScraperTool()
        result = tool.run(
            video_url="https://www.youtube.com/watch?v=VIDEO_ID",
            languages=["ko", "en"]
        )
    """

    name: str = "video_scraper"
    description: str = (
        "YouTube 비디오에서 메타데이터와 자막을 추출합니다. "
        "비디오 URL을 입력하면 제목, 설명, 조회수, 타임스탬프가 포함된 자막 등을 반환합니다."
    )

    def __init__(self):
        """도구 초기화"""
        self.youtube_service = YouTubeService()

    def run(
        self,
        video_url: str,
        languages: Optional[List[str]] = None,
        prefer_manual: bool = True
    ) -> Dict:
        """
        비디오 스크래핑을 실행합니다.

        Args:
            video_url: YouTube 비디오 URL (필수)
            languages: 자막 언어 우선순위 목록 (기본값: ["ko", "en"])
            prefer_manual: 수동 생성 자막 선호 여부 (기본값: True)

        Returns:
            다음 키를 포함한 딕셔너리:
            - metadata: 비디오 메타데이터 (제목, 채널, 조회수 등)
            - transcript: 타임스탬프가 포함된 자막 리스트
            - video_id: YouTube 비디오 ID

        Raises:
            ValueError: 유효하지 않은 URL
            Exception: 스크래핑 실패 시

        Example:
            >>> tool = VideoScraperTool()
            >>> result = tool.run("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            >>> print(result['metadata']['title'])
            >>> print(len(result['transcript']))
        """
        if not video_url:
            raise ValueError("video_url is required")

        if languages is None:
            languages = ["ko", "en"]

        logger.info(f"Scraping video: {video_url}")

        try:
            result = self.youtube_service.get_video_info(
                video_url=video_url,
                languages=languages,
                prefer_manual=prefer_manual
            )

            logger.info(
                f"Successfully scraped video: {result['metadata']['title']}"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to scrape video {video_url}: {e}")
            raise

    def get_metadata_only(self, video_url: str) -> Dict:
        """
        비디오 메타데이터만 추출합니다 (자막 제외).

        Args:
            video_url: YouTube 비디오 URL

        Returns:
            메타데이터 딕셔너리

        Raises:
            ValueError: 유효하지 않은 URL
        """
        video_id = self.youtube_service.extract_video_id(video_url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {video_url}")

        return self.youtube_service.get_video_metadata(video_id)

    def get_transcript_only(
        self,
        video_url: str,
        languages: Optional[List[str]] = None,
        prefer_manual: bool = True
    ) -> List[Dict]:
        """
        비디오 자막만 추출합니다 (메타데이터 제외).

        Args:
            video_url: YouTube 비디오 URL
            languages: 자막 언어 우선순위 목록
            prefer_manual: 수동 생성 자막 선호 여부

        Returns:
            자막 리스트

        Raises:
            ValueError: 유효하지 않은 URL
        """
        if languages is None:
            languages = ["ko", "en"]

        video_id = self.youtube_service.extract_video_id(video_url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {video_url}")

        return self.youtube_service.get_transcript(
            video_id=video_id,
            languages=languages,
            prefer_manual=prefer_manual
        )

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
                "name": "video_scraper",
                "description": (
                    "YouTube 비디오에서 메타데이터와 자막을 추출합니다. "
                    "비디오 제목, 설명, 조회수, 타임스탬프가 포함된 자막 등을 반환합니다."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_url": {
                            "type": "string",
                            "description": "YouTube 비디오 URL"
                        },
                        "languages": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "자막 언어 우선순위 목록 (예: ['ko', 'en'])",
                            "default": ["ko", "en"]
                        },
                        "prefer_manual": {
                            "type": "boolean",
                            "description": "수동 생성 자막 선호 여부",
                            "default": True
                        }
                    },
                    "required": ["video_url"]
                }
            }
        }
