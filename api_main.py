"""
YouTube Script Scraper API (FastAPI)
YouTube 비디오 스크래핑 및 AI 기능을 제공하는 RESTful API

에이전트 프레임워크가 사용할 수 있는 보편적인 도구 API를 제공합니다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn

from api.routers import video_router, playlist_router, ai_router
from utils import settings
from tools import (
    VideoScraperTool,
    SummarizerTool,
    TranslatorTool,
    TopicExtractorTool
)

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# 라우터 등록
app.include_router(video_router)
app.include_router(playlist_router)
app.include_router(ai_router)


@app.get("/")
async def root():
    """
    API 루트 엔드포인트

    API 정보와 사용 가능한 엔드포인트를 반환합니다.
    """
    return JSONResponse(content={
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "endpoints": {
            "video": {
                "info": "/video/info",
                "scrape": "/video/scrape",
                "metadata": "/video/metadata",
                "transcript": "/video/transcript"
            },
            "playlist": {
                "info": "/playlist/info",
                "check": "/playlist/check",
                "videos": "/playlist/videos"
            },
            "ai": {
                "summary": "/ai/summary",
                "translate": "/ai/translate",
                "topics": "/ai/topics",
                "enhance": "/ai/enhance",
                "health": "/ai/health"
            },
            "tools": {
                "schemas": "/tools/schemas"
            }
        }
    })


@app.get("/health")
async def health_check():
    """
    헬스 체크 엔드포인트

    API 서버의 상태를 확인합니다.
    """
    return JSONResponse(content={
        "status": "healthy",
        "version": settings.api_version,
        "service": "YouTube Script Scraper API"
    })


@app.get("/tools/schemas")
async def get_tool_schemas():
    """
    에이전트 프레임워크용 도구 스키마 반환

    OpenAI function calling 형식의 도구 스키마를 제공합니다.
    Claude, GPT, LangChain 등 다양한 에이전트 프레임워크에서 사용 가능합니다.
    """
    schemas = [
        VideoScraperTool.get_tool_schema(),
        SummarizerTool.get_tool_schema(),
        TranslatorTool.get_tool_schema(),
        TopicExtractorTool.get_tool_schema(),
    ]

    return JSONResponse(content={
        "tools": schemas,
        "format": "openai_function_calling",
        "compatible_frameworks": [
            "OpenAI Function Calling",
            "Claude Code Tools",
            "LangChain",
            "AutoGPT",
            "BabyAGI",
            "Custom Agent Frameworks"
        ],
        "usage_example": {
            "description": "에이전트가 이 스키마를 사용하여 도구를 호출할 수 있습니다.",
            "example_call": {
                "tool": "video_scraper",
                "parameters": {
                    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "languages": ["ko", "en"]
                }
            },
            "api_endpoint": "POST /video/info"
        }
    })


@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 이벤트
    """
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"API documentation available at: /docs")
    logger.info(f"Tool schemas available at: /tools/schemas")


@app.on_event("shutdown")
async def shutdown_event():
    """
    애플리케이션 종료 이벤트
    """
    logger.info(f"Shutting down {settings.api_title}")


def start_server(
    host: str = None,
    port: int = None,
    reload: bool = False
):
    """
    API 서버를 시작합니다.

    Args:
        host: 호스트 주소 (기본값: settings.api_host)
        port: 포트 번호 (기본값: settings.api_port)
        reload: 자동 리로드 활성화 (개발 모드)
    """
    uvicorn.run(
        "api_main:app",
        host=host or settings.api_host,
        port=port or settings.api_port,
        reload=reload,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    import sys

    # 명령줄 인자 파싱
    reload_mode = "--reload" in sys.argv or "--dev" in sys.argv

    print("=" * 80)
    print(f"{settings.api_title} v{settings.api_version}")
    print("=" * 80)
    print(f"Starting server at http://{settings.api_host}:{settings.api_port}")
    print(f"API documentation: http://{settings.api_host}:{settings.api_port}/docs")
    print(f"Tool schemas: http://{settings.api_host}:{settings.api_port}/tools/schemas")
    print("=" * 80)
    print()

    start_server(reload=reload_mode)
