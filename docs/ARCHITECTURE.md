# Architecture Documentation

Comprehensive architectural overview of the YouTube Script Scraper API.

## Table of Contents

- [System Overview](#system-overview)
- [Architectural Patterns](#architectural-patterns)
- [Layer Architecture](#layer-architecture)
- [Component Diagram](#component-diagram)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Design Decisions](#design-decisions)
- [Scalability Considerations](#scalability-considerations)

---

## System Overview

The YouTube Script Scraper API is a **production-ready RESTful API** built with FastAPI that extracts and processes YouTube video data with optional AI enhancements.

###

 Key Characteristics

- **Async/Await**: Non-blocking I/O operations
- **Layered Architecture**: Clear separation of concerns
- **Dependency Injection**: Loose coupling and testability
- **Type Safety**: Pydantic v2 models throughout
- **Extensible**: Easy to add new features

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Applications                   │
│   (Web Browsers, Mobile Apps, AI Agents, Scripts)       │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP/HTTPS
                        ▼
┌─────────────────────────────────────────────────────────┐
│                      FastAPI Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Video     │  │   Playlist   │  │      AI      │  │
│  │   Routers    │  │   Routers    │  │   Routers    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼──────────────────┼──────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                   Service Layer (Core)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   YouTube    │  │      AI      │  │  Formatter   │  │
│  │   Service    │  │   Service    │  │   Service    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘  │
└─────────┼──────────────────┼──────────────────────────────┘
          │                  │
          ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│              External Services & Libraries               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   yt-dlp     │  │    Gemini    │  │   YouTube    │  │
│  │              │  │     API      │  │ Transcript   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Architectural Patterns

### 1. Layered Architecture

The system is organized into distinct layers, each with specific responsibilities:

#### **API Layer** (`api/`)
- **Responsibility**: HTTP request/response handling
- **Components**: Routers, Schemas
- **Technologies**: FastAPI, Pydantic v2

#### **Core Layer** (`core/`)
- **Responsibility**: Business logic
- **Components**: Services
- **Technologies**: Python, yt-dlp, google-generativeai

#### **Tools Layer** (`tools/`)
- **Responsibility**: Agent-compatible tools
- **Components**: Standalone tools with schemas
- **Technologies**: OpenAI function calling format

#### **Utils Layer** (`utils/`)
- **Responsibility**: Configuration and utilities
- **Components**: Settings, Dependencies
- **Technologies**: Pydantic Settings

### 2. Dependency Injection

```python
# utils/dependencies.py
def get_youtube_service() -> YouTubeService:
    return YouTubeService()

# api/routers/video.py
async def get_video_info(
    request: VideoRequest,
    youtube_service: YouTubeServiceDep  # Injected
):
    ...
```

**Benefits:**
- Loose coupling
- Easy testing (mock dependencies)
- Single Responsibility Principle
- Centralized service management

### 3. Strategy Pattern (Formatters)

```python
class Formatter(ABC):
    @abstractmethod
    def save(self, metadata, transcript, output_file):
        pass

class JsonFormatter(Formatter):
    def save(self, metadata, transcript, output_file):
        # JSON-specific implementation
        pass

class TxtFormatter(Formatter):
    def save(self, metadata, transcript, output_file):
        # TXT-specific implementation
        pass
```

**Benefits:**
- Easy to add new formats
- Encapsulated formatting logic
- Open/Closed Principle

### 4. Service Layer Pattern

```python
# Business logic separated from API
class YouTubeService:
    def get_video_info(self, video_url, languages):
        # Reusable business logic
        pass

# Used in both API and CLI
```

**Benefits:**
- Reusable across interfaces
- Business logic isolation
- Easier unit testing

---

## Layer Architecture

### API Layer (`api/`)

```
api/
├── __init__.py
├── routers/              # FastAPI routers
│   ├── video.py          # Video endpoints
│   ├── playlist.py       # Playlist endpoints
│   └── ai.py             # AI endpoints
└── schemas/              # Pydantic models
    ├── video.py          # Video request/response models
    ├── playlist.py       # Playlist models
    └── ai.py             # AI models
```

**Responsibilities:**
- Request validation (Pydantic)
- Response formatting
- HTTP error handling
- OpenAPI documentation generation

**Key Technologies:**
- FastAPI for routing
- Pydantic v2 for validation
- Type hints for IDE support

### Core Layer (`core/`)

```
core/
├── __init__.py
├── youtube_service.py    # YouTube data extraction
├── ai_service.py         # AI operations (Gemini)
└── formatter_service.py  # Output formatting
```

**Responsibilities:**
- YouTube data extraction
- AI processing (summary, translation, topics)
- Output formatting
- Error handling

**Key Technologies:**
- yt-dlp for metadata
- youtube-transcript-api for subtitles
- google-generativeai for AI features

### Tools Layer (`tools/`)

```
tools/
├── __init__.py
├── video_scraper.py      # Video scraping tool
├── summarizer.py         # AI summarization tool
├── translator.py         # Translation tool
└── topic_extractor.py    # Topic extraction tool
```

**Responsibilities:**
- Agent-friendly interfaces
- OpenAI function calling schemas
- Standalone operation
- Error handling

**Key Features:**
- Compatible with Claude Code, OpenAI, LangChain
- Self-contained tools
- Clear input/output contracts

---

## Component Diagram

```
┌─────────────────────────────────────────────┐
│            api_main.py                      │
│  ┌─────────────────────────────────────┐   │
│  │  FastAPI App                        │   │
│  │  - CORS Middleware                  │   │
│  │  - Router Registration              │   │
│  │  - Exception Handlers               │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│         Routers (API Endpoints)             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Video   │  │ Playlist │  │    AI    │  │
│  │  Router  │  │  Router  │  │  Router  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼──────────────┼─────────┘
        │             │              │
        ▼             ▼              ▼
┌─────────────────────────────────────────────┐
│           Services (Business Logic)         │
│  ┌──────────────┐  ┌──────────────────┐    │
│  │   YouTube    │  │       AI         │    │
│  │   Service    │  │     Service      │    │
│  │              │  │   (Gemini API)   │    │
│  └──────┬───────┘  └────────┬─────────┘    │
│         │                    │              │
│         │    ┌───────────────┘              │
│         │    │                              │
│         ▼    ▼                              │
│  ┌──────────────────┐                       │
│  │    Formatter     │                       │
│  │     Service      │                       │
│  └──────────────────┘                       │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│         External Dependencies               │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐    │
│  │ yt-dlp  │  │ Gemini  │  │ YouTube  │    │
│  │         │  │   API   │  │Transcript│    │
│  └─────────┘  └─────────┘  └──────────┘    │
└─────────────────────────────────────────────┘
```

---

## Data Flow

### Video Information Request Flow

```
1. Client Request
   ↓
2. FastAPI Router (video.py)
   └─ Validate with Pydantic schema
   ↓
3. Dependency Injection
   └─ YouTubeService injected
   ↓
4. YouTubeService
   ├─ Extract video ID
   ├─ Get metadata (yt-dlp)
   └─ Get transcript (youtube-transcript-api)
   ↓
5. Response Formatting
   └─ Pydantic model serialization
   ↓
6. Client Response (JSON)
```

### AI Enhancement Flow

```
1. Client Request (video/scrape)
   ↓
2. FastAPI Router
   ↓
3. Service Injection
   ├─ YouTubeService
   ├─ AIService
   └─ FormatterService
   ↓
4. Sequential Processing
   ├─ Get video data (YouTubeService)
   ├─ Generate summary (AIService)
   ├─ Translate text (AIService)
   ├─ Extract topics (AIService)
   └─ Format output (FormatterService)
   ↓
5. Response with AI data
```

---

## Technology Stack

### Core Framework
- **FastAPI 0.109+**: Modern async web framework
- **Uvicorn**: ASGI server
- **Python 3.11+**: Programming language

### Data Validation
- **Pydantic v2**: Data validation and settings
- **Type Hints**: Static type checking

### YouTube Integration
- **yt-dlp**: Video metadata extraction
- **youtube-transcript-api**: Subtitle retrieval

### AI Integration
- **google-generativeai**: Gemini API client
- **Gemini 2.0 Flash**: AI model

### Testing
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **httpx**: Async HTTP client for testing

### Development Tools
- **Black**: Code formatting (if used)
- **mypy**: Static type checking (if used)
- **ruff**: Linting (if used)

---

## Design Decisions

### Why FastAPI?

**Chosen:** FastAPI
**Alternatives:** Flask, Django REST Framework

**Reasons:**
1. **Performance**: Async support, high performance
2. **Type Safety**: Built-in Pydantic integration
3. **Documentation**: Automatic OpenAPI generation
4. **Modern**: Python 3.6+ features, type hints
5. **Testing**: Built-in TestClient

### Why Pydantic v2?

**Chosen:** Pydantic v2
**Alternatives:** dataclasses, attrs

**Reasons:**
1. **Validation**: Automatic data validation
2. **Serialization**: JSON schema generation
3. **Performance**: 5-50x faster than v1
4. **Type Safety**: Runtime type checking
5. **FastAPI Integration**: First-class support

### Why Layered Architecture?

**Chosen:** Layered Architecture
**Alternatives:** Monolithic, Microservices

**Reasons:**
1. **Maintainability**: Clear separation of concerns
2. **Testability**: Easy to test individual layers
3. **Flexibility**: Can swap implementations
4. **Scalability**: Can extract layers to microservices
5. **Clarity**: Easy to understand codebase

### Why Dependency Injection?

**Chosen:** FastAPI Depends
**Alternatives:** Global instances, Manual instantiation

**Reasons:**
1. **Testing**: Easy to mock dependencies
2. **Flexibility**: Can change implementations
3. **Performance**: Automatic caching with lru_cache
4. **Type Safety**: IDE autocomplete support
5. **Best Practice**: Recommended by FastAPI

---

## Scalability Considerations

### Current Architecture

**Suitable for:**
- Small to medium workloads
- Single server deployment
- Development and testing

**Limitations:**
- Single process (can use workers)
- No built-in caching
- No database persistence

### Scaling Strategies

#### Horizontal Scaling

```
┌─────────┐
│ Load    │
│Balancer │
└────┬────┘
     │
     ├─────────┬─────────┐
     ▼         ▼         ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ API     │ │ API     │ │ API     │
│Instance │ │Instance │ │Instance │
└─────────┘ └─────────┘ └─────────┘
```

**Steps:**
1. Deploy multiple instances
2. Use load balancer (Nginx, HAProxy)
3. Share configuration via environment

#### Caching Layer

```
┌─────────┐
│  Redis  │  ← Cache video metadata
└────┬────┘
     │
     ▼
┌─────────┐
│   API   │
└─────────┘
```

**Benefits:**
- Reduce YouTube API calls
- Faster response times
- Lower external API costs

#### Database Integration

```
┌──────────┐
│PostgreSQL│  ← Store processed data
└────┬─────┘
     │
     ▼
┌─────────┐
│   API   │
└─────────┘
```

**Use Cases:**
- Store processed videos
- User management
- Analytics data

### Performance Optimization

1. **Async Processing**: Already implemented with FastAPI
2. **Connection Pooling**: For database connections
3. **Response Caching**: Cache frequently accessed data
4. **CDN**: For static content
5. **Compression**: Enable gzip compression

---

## Security Considerations

### Current Implementation

- **Input Validation**: Pydantic models
- **Error Handling**: No sensitive info in errors
- **CORS**: Configurable origins

### Recommendations

1. **Authentication**: Add API key authentication
2. **Rate Limiting**: Prevent abuse
3. **HTTPS**: Use SSL/TLS in production
4. **Secrets Management**: Use environment variables
5. **Input Sanitization**: Validate all inputs

---

## Future Enhancements

### Planned Features

1. **WebSocket Support**: Real-time progress updates
2. **Database Integration**: PostgreSQL for persistence
3. **Queue System**: Celery for background processing
4. **Caching**: Redis for response caching
5. **Monitoring**: Prometheus metrics
6. **Admin Dashboard**: Web UI for monitoring

### Architectural Changes

1. **Microservices**: Split into smaller services
2. **Event-Driven**: Use message queues
3. **Containerization**: Docker/Kubernetes
4. **API Gateway**: Centralized routing
5. **Service Mesh**: For microservices

---

## See Also

- [API Reference](API_REFERENCE.md)
- [Development Guide](DEVELOPMENT.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Main README](../README.md)
