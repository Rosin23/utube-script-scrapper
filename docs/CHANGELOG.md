# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- WebSocket support for real-time progress updates
- Database integration (PostgreSQL)
- Admin dashboard
- Docker containerization
- Kubernetes deployment configs
- GraphQL API support
- Additional AI model integrations (OpenAI, Claude)

---

## [3.0.0] - 2025-11-18

### Added - Phase 3: FastAPI Architecture

#### Core Features
- **FastAPI Application**: Complete RESTful API implementation
- **Layered Architecture**: API, Core, Tools, Utils layers
- **Dependency Injection**: FastAPI Depends() for all services
- **Pydantic v2**: Complete migration to Pydantic v2 models
- **OpenAPI Documentation**: Auto-generated at `/docs` and `/redoc`
- **Agent Tool Schemas**: OpenAI function calling compatible schemas
- **CORS Support**: Configurable cross-origin resource sharing
- **Health Checks**: API and AI service health endpoints

#### API Endpoints
- `POST /video/info` - Get video metadata and transcript
- `POST /video/scrape` - Full video scraping with AI
- `GET /video/metadata` - Metadata only
- `GET /video/transcript` - Transcript only
- `POST /playlist/info` - Playlist information
- `GET /playlist/check` - Check if URL is playlist
- `GET /playlist/videos` - Get playlist videos
- `POST /ai/summary` - Generate summary
- `POST /ai/translate` - Translate text
- `POST /ai/topics` - Extract topics
- `POST /ai/enhance` - Apply all AI features
- `GET /ai/health` - AI service status
- `GET /tools/schemas` - Tool schemas for agents

#### Architecture
- **Service Layer**: YouTubeService, AIService, FormatterService
- **Router Layer**: Organized by feature (video, playlist, AI)
- **Schema Layer**: Pydantic models for validation
- **Dependency Layer**: Centralized dependency injection

#### Testing
- **81% Test Coverage**: Exceeding 80% goal
- **137 Passing Tests**: Comprehensive test suite
- **FastAPI TestClient**: Modern testing approach
- **Dependency Overrides**: Clean test isolation

#### Documentation
- Comprehensive README with badges
- API Reference documentation
- Architecture documentation
- Development guide
- FAQ section
- Code examples (Python, JavaScript, cURL)
- Response examples

### Changed
- **Pydantic Models**: Migrated from `class Config` to `ConfigDict`
- **Router Structure**: Organized into separate modules
- **Service Instantiation**: From manual to dependency injection
- **Error Handling**: Unified HTTPException usage
- **Test Strategy**: From @patch to dependency_overrides

### Improved
- **Type Safety**: Full type hints throughout
- **Async Support**: Proper async/await patterns
- **Error Messages**: More descriptive error responses
- **Code Organization**: Clear separation of concerns
- **Maintainability**: Easier to extend and test

---

## [2.0.0] - 2024-XX-XX

### Added - Phase 2: AI Features & Playlist Support

#### AI Integration
- **Gemini API Integration**: Google's Gemini 2.0 Flash model
- **AI Summarization**: Automatic content summarization
- **Translation**: Multi-language translation support
- **Topic Extraction**: Key topic identification
- **Configurable AI**: Adjustable summary length and topics

#### Playlist Support
- **Playlist Detection**: Automatic URL type detection
- **Batch Processing**: Process multiple videos from playlist
- **Video Limit**: Control number of videos to process
- **Playlist Metadata**: Extract playlist information

#### CLI Enhancements
- **argparse Integration**: Proper command-line argument parsing
- **AI Options**: `--summary`, `--translate`, `--topics` flags
- **Language Selection**: `--lang` for subtitle preferences
- **Playlist Control**: `--max-videos` for limiting batch size

#### Core Features
- **Enhanced Output**: AI features in all output formats
- **Error Handling**: Improved error messages
- **Logging**: Better logging throughout

### Changed
- **CLI Interface**: From interactive to argument-based
- **Configuration**: Environment variable support
- **Documentation**: Updated for AI features

---

## [1.0.0] - 2024-XX-XX

### Added - Phase 1: Core Functionality

#### Basic Features
- **Video Metadata Extraction**: Title, channel, date, views
- **Transcript Retrieval**: Timestamped subtitles
- **Multiple Output Formats**:
  - TXT: Structured text format
  - JSON: Machine-readable format
  - XML: Structured XML format
  - Markdown: Human-readable format

#### Architecture
- **Modular Design**: Separated concerns
- **Strategy Pattern**: Pluggable formatters
- **Service Classes**: YouTubeAPI class
- **Error Handling**: Comprehensive exception handling

#### Technical
- **yt-dlp Integration**: Video metadata extraction
- **youtube-transcript-api**: Subtitle retrieval
- **Multi-language Support**: Korean, English priority
- **Timestamp Formatting**: HH:MM:SS format

#### Testing
- **pytest Framework**: Unit testing setup
- **Test Coverage**: Basic test coverage
- **Mock Testing**: External API mocking

#### Documentation
- **README**: Basic usage instructions
- **Code Comments**: Inline documentation
- **Examples**: Usage examples

---

## Version History Summary

| Version | Date | Key Features |
|---------|------|--------------|
| **3.0.0** | 2025-11-18 | FastAPI, REST API, Dependency Injection, 81% coverage |
| **2.0.0** | 2024-XX-XX | AI features, Playlist support, CLI improvements |
| **1.0.0** | 2024-XX-XX | Core functionality, Multiple formats, Basic testing |

---

## Breaking Changes

### 3.0.0
- **API-First Design**: Primary interface now REST API (CLI still available)
- **Import Changes**: Core classes moved to `core/` directory
- **Configuration**: Environment variables preferred over arguments

### 2.0.0
- **CLI Arguments**: Changed from interactive to argument-based
- **Python Version**: Minimum Python 3.7 → 3.11
- **Dependencies**: Added google-generativeai

---

## Upgrade Guide

### From 2.0.0 to 3.0.0

**Installation**:
```bash
pip install -r requirements.txt
```

**Start API Server**:
```bash
# Old (CLI):
python main.py "VIDEO_URL"

# New (API):
python api_main.py
# Then make API calls
```

**Code Changes**:
```python
# Old:
from youtube_api import get_video_metadata

# New:
import requests
response = requests.post(
    "http://localhost:8000/video/info",
    json={"video_url": "..."}
)
```

### From 1.0.0 to 2.0.0

**Installation**:
```bash
pip install google-generativeai
```

**Configuration**:
```bash
export GEMINI_API_KEY="your-key"
```

**Usage Changes**:
```bash
# Old:
python Utube_scrapper.py

# New:
python main.py --summary --translate en
```

---

## Deprecation Notices

### Deprecated in 3.0.0
- **Direct CLI Usage**: Use `main.py` instead of importing classes
- **Global Configuration**: Use environment variables

### Removed in 3.0.0
- None (backward compatible)

### Deprecated in 2.0.0
- **Interactive Mode**: Use CLI arguments instead

---

## Contributors

- [@Rosin23](https://github.com/Rosin23) - Project creator and maintainer

---

## Links

- [Repository](https://github.com/Rosin23/utube-script-scrapper)
- [Issue Tracker](https://github.com/Rosin23/utube-script-scrapper/issues)
- [Documentation](https://github.com/Rosin23/utube-script-scrapper/blob/main/README.md)

---

*For detailed API changes, see [API Reference](API_REFERENCE.md)*
*For migration guides, see [Development Guide](DEVELOPMENT.md)*
