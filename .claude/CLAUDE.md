# CLAUDE.md - AI Assistant Guide

This document provides comprehensive guidance for AI assistants working with the `utube-script-scrapper` codebase.

## Table of Contents
- [Repository Overview](#repository-overview)
- [Architecture & Design Patterns](#architecture--design-patterns)
- [Module Reference](#module-reference)
- [API Reference](#api-reference)
- [Tools for Agent Frameworks](#tools-for-agent-frameworks)
- [Development Workflow](#development-workflow)
- [Testing Conventions](#testing-conventions)
- [Git Workflow](#git-workflow)
- [Code Style & Conventions](#code-style--conventions)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)

---

## Repository Overview

### Purpose
A FastAPI-based YouTube video/playlist scraper API that provides universal tools for AI agent frameworks. Offers metadata extraction, transcripts, and AI-powered enhancements (summarization, translation, topic extraction).

### Key Features (Phase 3 - FastAPI Architecture)
1. **RESTful API**: FastAPI-based API for universal access by any agent framework
2. **Agent-Friendly Tools**: Decoupled tools with OpenAI function calling compatible schemas
3. **YouTube Playlist Support**: Automatic detection and batch processing
4. **AI Summarization**: Gemini API integration for automatic transcript summarization
5. **Multi-language Support**: User-configurable subtitle language preferences
6. **Translation**: AI-powered transcript translation
7. **Topic Extraction**: Automatic extraction of key topics
8. **Multi-format Output**: TXT, JSON, XML, Markdown formatters
9. **OpenAPI Documentation**: Auto-generated API docs at `/docs`

### Technology Stack
- **Python 3.11+**
- **FastAPI**: Modern async web framework
- **Uvicorn**: ASGI server
- **Pydantic v2**: Data validation and settings
- **Core Libraries**: yt-dlp, youtube-transcript-api
- **AI Integration**: google-generativeai (Gemini API v1beta)
- **Testing**: pytest, pytest-mock, pytest-cov, httpx
- **Design Patterns**: Layered Architecture, Strategy Pattern, Dependency Injection

---

## Architecture & Design Patterns

### Project Structure (Phase 3)
```
utube-script-scrapper/
├── api_main.py                      # FastAPI application entry point (210 lines)
├── api/                             # API layer
│   ├── __init__.py
│   ├── routers/                     # FastAPI routers
│   │   ├── __init__.py
│   │   ├── video.py                 # Video endpoints (226 lines)
│   │   ├── playlist.py              # Playlist endpoints (145 lines)
│   │   └── ai.py                    # AI endpoints (242 lines)
│   └── schemas/                     # Pydantic schemas
│       ├── __init__.py
│       ├── video.py                 # Video models (190 lines)
│       ├── playlist.py              # Playlist models (68 lines)
│       └── ai.py                    # AI models (145 lines)
├── core/                            # Core business logic layer
│   ├── __init__.py
│   ├── youtube_service.py           # YouTube data service (227 lines)
│   ├── ai_service.py                # AI service (320 lines)
│   └── formatter_service.py         # Formatter service (172 lines)
├── tools/                           # Agent-friendly tools
│   ├── __init__.py
│   ├── video_scraper.py             # Video scraping tool (165 lines)
│   ├── summarizer.py                # Summarization tool (115 lines)
│   ├── translator.py                # Translation tool (127 lines)
│   └── topic_extractor.py           # Topic extraction tool (117 lines)
├── utils/                           # Utilities
│   ├── __init__.py
│   └── config.py                    # Settings management (59 lines)
├── tests/                           # Comprehensive tests
│   ├── api/                         # API tests
│   ├── core/                        # Core service tests
│   └── tools/                       # Tool tests
├── main.py                          # CLI entry point (legacy, 439 lines)
├── youtube_api.py                   # Legacy YouTube API (234 lines)
├── gemini_api.py                    # Legacy Gemini API (454 lines)
├── formatters.py                    # Legacy formatters (402 lines)
├── playlist_handler.py              # Legacy playlist handler (191 lines)
├── requirements.txt                 # Python dependencies
└── README.md                        # User documentation
```

### Architectural Layers

#### 1. API Layer (`api/`)
**Purpose**: RESTful API endpoints using FastAPI

- **Routers** (`api/routers/`): Endpoint definitions
  - `video.py`: Video scraping endpoints
  - `playlist.py`: Playlist processing endpoints
  - `ai.py`: AI enhancement endpoints

- **Schemas** (`api/schemas/`): Pydantic v2 models for validation
  - Input/output validation
  - Automatic OpenAPI schema generation
  - Type safety

**Example**:
```python
from fastapi import APIRouter
from api.schemas.video import VideoRequest, VideoResponse

router = APIRouter(prefix="/video", tags=["video"])

@router.post("/info", response_model=VideoResponse)
async def get_video_info(request: VideoRequest):
    # Implementation
    pass
```

#### 2. Core Layer (`core/`)
**Purpose**: Business logic and service orchestration

- **YouTubeService**: YouTube data extraction
- **AIService**: AI operations (summary, translation, topics)
- **FormatterService**: Output formatting

**Benefits**:
- Decoupled from API layer
- Reusable in CLI and API contexts
- Easier to test
- Clear separation of concerns

**Example**:
```python
from core import YouTubeService

service = YouTubeService()
video_info = service.get_video_info(
    video_url="https://youtube.com/watch?v=...",
    languages=["ko", "en"]
)
```

#### 3. Tools Layer (`tools/`)
**Purpose**: Agent framework compatible tools

Each tool provides:
- Clear input/output interface
- OpenAI function calling schema
- Independent operation
- Error handling

**Compatible Frameworks**:
- OpenAI Function Calling
- Claude Code Tools
- LangChain
- AutoGPT
- BabyAGI
- Custom agent frameworks

**Example**:
```python
from tools import VideoScraperTool

tool = VideoScraperTool()
result = tool.run(video_url="https://youtube.com/watch?v=...")
schema = VideoScraperTool.get_tool_schema()  # For agent frameworks
```

#### 4. Utils Layer (`utils/`)
**Purpose**: Configuration and utilities

- Environment-based configuration
- Pydantic Settings
- Centralized settings management

### Design Patterns

#### 1. Layered Architecture
**Implementation**:
```
User/Agent → API Layer → Core Layer → External Services
                ↓
            Tools Layer (standalone)
```

**Benefits**:
- Clear separation of concerns
- Each layer has specific responsibilities
- Easy to modify individual layers
- Better testability

#### 2. Strategy Pattern (Formatters)
**Location**: `formatters.py` (legacy), `core/formatter_service.py`

Continued from Phase 2 implementation with service wrapper.

#### 3. Dependency Injection
**Throughout the codebase**

Services and tools accept dependencies as parameters:
```python
class AIService:
    def __init__(self, api_key=None, model_name="gemini-2.0-flash-exp"):
        # Inject configuration
        pass
```

#### 4. Service Layer Pattern
**Location**: `core/` directory

Business logic encapsulated in service classes:
- Separates API concerns from business logic
- Reusable across different interfaces (API, CLI)
- Easier unit testing

---

## Module Reference

### api_main.py (210 lines)
**Purpose**: FastAPI application entry point

**Key Components**:
- FastAPI app initialization
- CORS middleware configuration
- Router registration
- Health check endpoints
- Tool schema endpoints

**Running the API**:
```bash
# Development mode with auto-reload
python api_main.py --reload

# Production mode
python api_main.py

# Custom host/port
uvicorn api_main:app --host 0.0.0.0 --port 8000
```

**Endpoints**:
- `GET /`: API information
- `GET /health`: Health check
- `GET /tools/schemas`: Agent framework tool schemas
- `GET /docs`: Interactive API documentation
- `GET /openapi.json`: OpenAPI specification

### api/routers/

#### video.py (226 lines)
**Endpoints**:
- `POST /video/info`: Get video metadata and transcript
- `POST /video/scrape`: Full scraping with AI enhancements
- `GET /video/metadata`: Metadata only
- `GET /video/transcript`: Transcript only

#### playlist.py (145 lines)
**Endpoints**:
- `POST /playlist/info`: Get playlist info and videos
- `GET /playlist/check`: Check if URL is playlist
- `GET /playlist/videos`: Get video list only

#### ai.py (242 lines)
**Endpoints**:
- `POST /ai/summary`: Generate text summary
- `POST /ai/translate`: Translate text
- `POST /ai/topics`: Extract topics
- `POST /ai/enhance`: Apply all AI features
- `GET /ai/health`: Check AI service status

### api/schemas/

#### video.py (190 lines)
**Models**:
- `VideoRequest`: Video info request
- `VideoResponse`: Video info response
- `VideoMetadata`: Video metadata
- `TranscriptEntry`: Single transcript entry
- `VideoScrapeRequest`: Full scraping request
- `VideoScrapeResponse`: Full scraping response

#### playlist.py (68 lines)
**Models**:
- `PlaylistRequest`: Playlist request
- `PlaylistResponse`: Playlist response
- `PlaylistInfo`: Playlist metadata
- `PlaylistVideoInfo`: Video in playlist

#### ai.py (145 lines)
**Models**:
- `SummaryRequest/Response`: Summarization
- `TranslationRequest/Response`: Translation
- `TopicExtractionRequest/Response`: Topic extraction
- `AIEnhancementRequest/Response`: Combined AI features

### core/

#### youtube_service.py (227 lines)
**Purpose**: YouTube data extraction service

**Key Methods**:
- `extract_video_id(url)`: Extract video ID from URL
- `get_video_metadata(video_id)`: Get metadata
- `get_transcript(video_id, languages)`: Get transcript
- `get_video_info(url)`: Get full video info
- `get_playlist_info(url)`: Get playlist info
- `get_playlist_videos(url)`: Get playlist videos

#### ai_service.py (320 lines)
**Purpose**: AI operations service

**Key Methods**:
- `generate_summary(transcript, max_points, language)`: Generate summary
- `translate_text(text, target_language)`: Translate text
- `extract_topics(transcript, num_topics)`: Extract topics
- `enhance_transcript(...)`: Apply all AI features

#### formatter_service.py (172 lines)
**Purpose**: Output formatting service

**Key Methods**:
- `get_formatter(format_choice)`: Get formatter instance
- `save_to_file(metadata, transcript, ...)`: Save to file
- `format_data(...)`: Format as string

### tools/

#### video_scraper.py (165 lines)
**Purpose**: Video scraping tool for agents

**Methods**:
- `run(video_url, languages)`: Scrape video
- `get_metadata_only(url)`: Metadata only
- `get_transcript_only(url)`: Transcript only
- `get_tool_schema()`: Schema for agents

#### summarizer.py (115 lines)
**Purpose**: Text summarization tool

**Methods**:
- `run(text, max_points, language)`: Generate summary
- `is_available()`: Check if AI is available
- `get_tool_schema()`: Schema for agents

#### translator.py (127 lines)
**Purpose**: Translation tool

**Methods**:
- `run(text, target_language)`: Translate text
- `get_supported_languages()`: Language list
- `get_tool_schema()`: Schema for agents

#### topic_extractor.py (117 lines)
**Purpose**: Topic extraction tool

**Methods**:
- `run(text, num_topics, language)`: Extract topics
- `is_available()`: Check if AI is available
- `get_tool_schema()`: Schema for agents

---

## API Reference

### Starting the API Server

```bash
# Development with auto-reload
python api_main.py --reload

# Production
python api_main.py

# Using uvicorn directly
uvicorn api_main:app --host 0.0.0.0 --port 8000 --reload
```

### API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Example API Calls

#### Get Video Info
```bash
curl -X POST "http://localhost:8000/video/info" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "languages": ["ko", "en"],
    "prefer_manual": true
  }'
```

#### Scrape Video with AI
```bash
curl -X POST "http://localhost:8000/video/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "enable_summary": true,
    "summary_max_points": 5,
    "enable_translation": true,
    "target_language": "en",
    "enable_topics": true,
    "num_topics": 5
  }'
```

#### Generate Summary
```bash
curl -X POST "http://localhost:8000/ai/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Long text to summarize...",
    "max_points": 5,
    "language": "ko"
  }'
```

---

## Tools for Agent Frameworks

### Getting Tool Schemas

```bash
curl http://localhost:8000/tools/schemas
```

Returns OpenAI function calling compatible schemas for all tools.

### Using Tools in Agent Code

#### OpenAI Function Calling
```python
import openai
import requests

# Get tool schemas
response = requests.get("http://localhost:8000/tools/schemas")
tools = response.json()["tools"]

# Use with OpenAI
completion = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Scrape this YouTube video..."}],
    tools=tools
)
```

#### Claude Code
```python
# Claude can directly call the API endpoints
# The tools are exposed as RESTful endpoints
```

#### LangChain
```python
from langchain.tools import StructuredTool
from tools import VideoScraperTool

tool = VideoScraperTool()

langchain_tool = StructuredTool.from_function(
    func=tool.run,
    name=tool.name,
    description=tool.description
)
```

### Available Tools

1. **video_scraper**: Scrape YouTube videos
2. **summarizer**: Generate AI summaries
3. **translator**: Translate text
4. **topic_extractor**: Extract key topics

Each tool provides:
- Clear function signature
- Input validation
- Error handling
- OpenAI-compatible schema

---

## Development Workflow

### Phase-Based Development

**Phase 1** (Completed):
- Basic YouTube scraping
- Multi-format output
- Modular architecture

**Phase 2** (Completed):
- Playlist support
- AI features (Gemini API)
- CLI with argparse

**Phase 3** (Current - Completed):
- FastAPI architecture
- RESTful API
- Agent-friendly tools
- Service layer pattern
- Comprehensive testing

### Branch Naming Convention

```
feature/<feature-description>-<session-id>
```

Examples:
- `feature/fastapi-architecture-01EZhV9Zf6MNs7x4swCvdvAC`
- `feature/add-caching-layer-ABC123XYZ`

**IMPORTANT**: Session ID suffix is required for push operations.

### Development Steps

1. **Planning**: Use TodoWrite tool for multi-step tasks
2. **Implementation**: Follow layered architecture
3. **Testing**: Write tests for each layer
4. **Documentation**: Update CLAUDE.md and docstrings
5. **Commit**: Clear, descriptive commit messages
6. **Push**: Use `git push -u origin <branch-name>` with retry logic

---

## Testing Conventions

### Test Structure

**Location**: `tests/` directory

```
tests/
├── api/                # API endpoint tests
│   ├── test_main.py
│   ├── test_video_router.py
│   ├── test_playlist_router.py
│   └── test_ai_router.py
├── core/               # Service layer tests
│   ├── test_youtube_service.py
│   ├── test_ai_service.py
│   └── test_formatter_service.py
└── tools/              # Tool tests
    ├── test_video_scraper.py
    ├── test_summarizer.py
    ├── test_translator.py
    └── test_topic_extractor.py
```

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ -v --cov=api --cov=core --cov=tools --cov=api_main --cov-report=term-missing

# Specific module
python -m pytest tests/api/test_main.py -v

# FastAPI specific
python -m pytest tests/api/ -v
```

### FastAPI Testing Pattern

```python
from fastapi.testclient import TestClient
from api_main import app

client = TestClient(app)

def test_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Coverage Requirements

**Target**: 80%+ coverage for new modules

**Current Status** (Phase 3):
- API schemas: 100%
- API main: 66%
- Core services: 22-56%
- Tools: 43-44%
- API routers: 25-61%

**Note**: Legacy modules maintain existing coverage.

---

## Git Workflow

### Commit Message Format

```
<Type>: <Short description>

<Detailed description>
- Bullet point 1
- Bullet point 2
```

**Types**:
- `Refactor`: Code restructuring
- `Implement`: New feature
- `Fix`: Bug fixes
- `Update`: Documentation or minor updates
- `Add`: New files or functionality

**Example**:
```
Refactor: Implement FastAPI architecture with agent-friendly tools

- Created layered architecture (API, Core, Tools, Utils)
- Implemented FastAPI with Pydantic v2 schemas
- Added OpenAI function calling compatible tool schemas
- Created comprehensive test suite
- Updated documentation for Phase 3 architecture
```

### Git Operations with Retry Logic

**Push Operations**:
```bash
# CRITICAL: Branch must start with 'feature/' and end with session ID
git push -u origin feature/fastapi-architecture-SESSION_ID
```

**Retry Logic** (for network failures):
- Retry up to 4 times
- Exponential backoff: 2s, 4s, 8s, 16s
- Apply to: `git push`, `git fetch`, `git pull`

---

## Code Style & Conventions

### Python Style

- PEP 8 compliant
- Type hints throughout
- Pydantic v2 for data validation
- Async/await for FastAPI endpoints
- Docstrings for all public functions/classes

### FastAPI Conventions

```python
from fastapi import APIRouter, HTTPException
from api.schemas.video import VideoRequest, VideoResponse

router = APIRouter(prefix="/video", tags=["video"])

@router.post("/info", response_model=VideoResponse)
async def get_video_info(request: VideoRequest):
    """
    Endpoint description.

    - **param1**: Description
    - **param2**: Description
    """
    try:
        # Implementation
        pass
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Pydantic Models

```python
from pydantic import BaseModel, Field

class VideoRequest(BaseModel):
    video_url: str = Field(..., description="YouTube video URL")
    languages: List[str] = Field(default=["ko", "en"], description="Language priority")

    class Config:
        json_schema_extra = {
            "example": {
                "video_url": "https://youtube.com/watch?v=...",
                "languages": ["ko", "en"]
            }
        }
```

---

## Common Tasks

### Adding a New API Endpoint

1. **Create schema** in `api/schemas/`:
```python
class NewRequest(BaseModel):
    param: str = Field(..., description="Description")
```

2. **Add router endpoint** in `api/routers/`:
```python
@router.post("/new-endpoint", response_model=NewResponse)
async def new_endpoint(request: NewRequest):
    # Implementation
    pass
```

3. **Write tests** in `tests/api/`:
```python
def test_new_endpoint():
    response = client.post("/new-endpoint", json={...})
    assert response.status_code == 200
```

### Adding a New Agent Tool

1. **Create tool class** in `tools/`:
```python
class NewTool:
    name = "new_tool"
    description = "Tool description"

    def run(self, **kwargs):
        # Implementation
        pass

    @staticmethod
    def get_tool_schema():
        return {...}  # OpenAI function calling schema
```

2. **Add to tools/__init__.py**

3. **Write tests**

4. **Register in api_main.py** (tool schemas endpoint)

### Configuring Environment

Create `.env` file:
```bash
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_NAME=gemini-2.0-flash-exp
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

---

## Troubleshooting

### Common Issues

#### 1. FastAPI Import Errors

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
pip install -r requirements.txt
```

#### 2. Pydantic Validation Errors

**Problem**: Request validation fails

**Solution**: Check request payload matches schema. View `/docs` for schema details.

#### 3. CORS Issues

**Problem**: Browser blocks API requests

**Solution**: Configure CORS in `utils/config.py`:
```python
cors_origins = ["http://localhost:3000", "..."]
```

#### 4. AI Service Unavailable

**Problem**: AI endpoints return 503

**Solution**: Check `GEMINI_API_KEY` environment variable:
```bash
export GEMINI_API_KEY=your_key
# or add to .env file
```

### Debugging Tips

1. **Check API logs**: FastAPI provides detailed request logs

2. **Use interactive docs**: Visit `/docs` to test endpoints

3. **Check health endpoints**:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/ai/health
```

4. **Enable debug logging**:
```python
# In api_main.py or .env
LOG_LEVEL=DEBUG
```

---

## Best Practices for AI Assistants

### When Working with This Codebase

1. **Understand the layered architecture**
   - API layer: Endpoints and validation
   - Core layer: Business logic
   - Tools layer: Agent-compatible interfaces
   - Each layer has specific responsibilities

2. **Follow FastAPI conventions**
   - Use Pydantic models for validation
   - Include docstrings with parameter descriptions
   - Handle errors with HTTPException
   - Write async functions for endpoints

3. **Maintain backward compatibility**
   - Legacy CLI (`main.py`) still works
   - Legacy modules can coexist with new architecture
   - API provides same functionality via HTTP

4. **Test thoroughly**
   - Write tests for each layer
   - Use FastAPI TestClient for API tests
   - Mock external dependencies
   - Aim for 80%+ coverage

5. **Document changes**
   - Update docstrings
   - Update CLAUDE.md for architecture changes
   - Update README.md for user-facing changes
   - Include examples in schemas

### Code Review Checklist

Before committing, verify:

- [ ] Code follows layered architecture
- [ ] Pydantic models have examples
- [ ] API endpoints have proper error handling
- [ ] Tests written and passing
- [ ] Type hints present
- [ ] Docstrings complete
- [ ] No security vulnerabilities
- [ ] CLAUDE.md updated if needed
- [ ] OpenAPI docs look correct (`/docs`)

---

## Version History

### Phase 3 (2025-11-18) - Current

**Latest Changes**: FastAPI architecture implementation

**Key Additions**:
- `api_main.py`: FastAPI application (210 lines)
- `api/` directory: Routers and schemas
- `core/` directory: Service layer
- `tools/` directory: Agent-friendly tools
- `utils/` directory: Configuration
- Comprehensive test suite
- OpenAPI documentation
- Agent framework compatibility

**Branch**: `feature/refactor-fastapi-architecture-01EZhV9Zf6MNs7x4swCvdvAC`

**Test Coverage**: 22 passing tests, API fully functional

### Previous Phases

See git history for Phase 1 and Phase 2 details.

---

## Contact & Resources

- **Repository**: https://github.com/Rosin23/utube-script-scrapper
- **API Documentation**: http://localhost:8000/docs (when running)
- **Tool Schemas**: http://localhost:8000/tools/schemas
- **Issues**: See ISSUE_TRANSCRIPT_API_FIX.md
- **User Guide**: README.md

---

*This document is maintained by AI assistants and should be updated when significant architectural changes are made.*
