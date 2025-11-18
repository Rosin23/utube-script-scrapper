# YouTube Script Scraper API

<div align="center">

**A modern FastAPI-based YouTube video/playlist scraper with AI-powered enhancements**

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-00a393.svg)](https://fastapi.tiangolo.com)
[![Test Coverage](https://img.shields.io/badge/coverage-81%25-brightgreen.svg)](https://github.com/Rosin23/utube-script-scrapper)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[Features](#features) •
[Quick Start](#quick-start) •
[API Documentation](#api-documentation) •
[Usage Examples](#usage-examples) •
[Contributing](#contributing)

</div>

---

## 🎯 Overview

YouTube Script Scraper API is a **production-ready RESTful API** that extracts video metadata, transcripts, and descriptions from YouTube videos and playlists. Built with **FastAPI** and following modern architectural patterns, it provides:

- 🚀 **High-performance async API** with automatic OpenAPI documentation
- 🤖 **AI-powered features** using Google's Gemini API (summarization, translation, topic extraction)
- 🛠️ **Agent-friendly tools** compatible with Claude Code, OpenAI, LangChain, and other AI frameworks
- 📦 **Multiple output formats** (JSON, TXT, XML, Markdown)
- 🎬 **Playlist support** with batch processing
- 🌍 **Multi-language subtitle support** with customizable priorities
- ✅ **81% test coverage** with comprehensive unit and integration tests

---

## ✨ Features

### Core API Features

| Feature | Description |
|---------|-------------|
| **Video Metadata Extraction** | Title, channel, upload date, duration, views, description |
| **Transcript Retrieval** | Timestamped subtitles with fallback language support |
| **Playlist Processing** | Automatic detection and batch processing of playlists |
| **Multi-format Output** | JSON, TXT, XML, Markdown with consistent structure |

### AI-Powered Enhancements (Optional)

| Feature | Description |
|---------|-------------|
| **🤖 Smart Summarization** | Gemini API-powered content summaries (1-10 key points) |
| **🌐 Translation** | Automatic transcript translation to any language |
| **🔑 Topic Extraction** | AI-identified key topics and themes |
| **⚡ Batch Enhancement** | Apply all AI features in a single request |

### Developer Features

| Feature | Description |
|---------|-------------|
| **OpenAPI/Swagger UI** | Interactive API documentation at `/docs` |
| **Dependency Injection** | Clean, testable FastAPI architecture |
| **Agent Tool Schemas** | OpenAI function calling compatible schemas |
| **CORS Support** | Configurable cross-origin resource sharing |
| **Health Checks** | Monitor API and AI service status |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **pip** (Python package manager)
- **Gemini API Key** (optional, for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rosin23/utube-script-scrapper.git
   cd utube-script-scrapper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional, for AI features)
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your-api-key-here" > .env

   # Or export directly
   export GEMINI_API_KEY="your-api-key-here"
   ```

4. **Start the API server**
   ```bash
   python api_main.py
   ```

   The API will be available at: **http://localhost:8000**

### Verify Installation

Open your browser and navigate to:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📖 API Documentation

### Base URL

```
http://localhost:8000
```

### Authentication

No authentication required for basic features. AI features require a valid Gemini API key configured via environment variables.

### Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/video/info` | POST | Get video metadata and transcript |
| `/video/scrape` | POST | Scrape video with AI enhancements |
| `/video/metadata` | GET | Get metadata only |
| `/video/transcript` | GET | Get transcript only |
| `/playlist/info` | POST | Get playlist info and videos |
| `/playlist/check` | GET | Check if URL is a playlist |
| `/playlist/videos` | GET | Get playlist videos list |
| `/ai/summary` | POST | Generate text summary |
| `/ai/translate` | POST | Translate text |
| `/ai/topics` | POST | Extract topics |
| `/ai/enhance` | POST | Apply all AI features |
| `/ai/health` | GET | Check AI service status |
| `/tools/schemas` | GET | Get agent tool schemas |

### Quick Examples

#### Get Video Information

```bash
curl -X POST "http://localhost:8000/video/info" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "languages": ["ko", "en"],
    "prefer_manual": true
  }'
```

#### Scrape with AI Enhancement

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
    "num_topics": 5,
    "output_format": "json"
  }'
```

#### Get Playlist Information

```bash
curl -X POST "http://localhost:8000/playlist/info" \
  -H "Content-Type: application/json" \
  -d '{
    "playlist_url": "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
    "max_videos": 10
  }'
```

For complete API documentation, visit: **http://localhost:8000/docs**

---

## 💡 Usage Examples

### Example 1: Educational Content Analysis

Extract and summarize lecture videos from a playlist:

```python
import requests

response = requests.post(
    "http://localhost:8000/playlist/info",
    json={
        "playlist_url": "https://www.youtube.com/playlist?list=PLEducation123",
        "max_videos": 10
    }
)

for video in response.json()["videos"]:
    # Scrape each video with AI summary
    video_response = requests.post(
        "http://localhost:8000/video/scrape",
        json={
            "video_url": video["url"],
            "enable_summary": True,
            "summary_max_points": 5,
            "output_format": "markdown"
        }
    )
    print(video_response.json()["summary"])
```

### Example 2: Multi-language Translation

Translate Korean video content to English:

```python
import requests

response = requests.post(
    "http://localhost:8000/video/scrape",
    json={
        "video_url": "https://www.youtube.com/watch?v=KoreanVideo",
        "languages": ["ko"],
        "enable_translation": True,
        "target_language": "en",
        "output_format": "json"
    }
)

translation = response.json()["translation"]
print(translation)
```

### Example 3: Topic Analysis

Analyze video content for key topics:

```python
import requests

response = requests.post(
    "http://localhost:8000/ai/topics",
    json={
        "text": "Long video transcript text...",
        "num_topics": 10,
        "language": "en"
    }
)

topics = response.json()["topics"]
for topic in topics:
    print(f"• {topic}")
```

### Example 4: Using with AI Agent Frameworks

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

Claude Code can directly interact with the API endpoints using the tool schemas.

---

## 🏗️ Architecture

### Project Structure

```
utube-script-scrapper/
├── api_main.py                      # FastAPI application entry point
├── api/                             # API layer
│   ├── routers/                     # FastAPI routers
│   │   ├── video.py                 # Video endpoints
│   │   ├── playlist.py              # Playlist endpoints
│   │   └── ai.py                    # AI endpoints
│   └── schemas/                     # Pydantic v2 models
│       ├── video.py                 # Video schemas
│       ├── playlist.py              # Playlist schemas
│       └── ai.py                    # AI schemas
├── core/                            # Business logic layer
│   ├── youtube_service.py           # YouTube data service
│   ├── ai_service.py                # AI service (Gemini)
│   └── formatter_service.py         # Output formatting
├── tools/                           # Agent-friendly tools
│   ├── video_scraper.py             # Video scraping tool
│   ├── summarizer.py                # Summarization tool
│   ├── translator.py                # Translation tool
│   └── topic_extractor.py           # Topic extraction tool
├── utils/                           # Utilities
│   ├── config.py                    # Settings management
│   └── dependencies.py              # FastAPI dependencies
├── tests/                           # Comprehensive tests (81% coverage)
│   ├── api/                         # API endpoint tests
│   ├── core/                        # Service layer tests
│   └── tools/                       # Tool tests
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

### Design Patterns

- **Layered Architecture**: Clear separation between API, business logic, and tools
- **Dependency Injection**: FastAPI's dependency system for loose coupling
- **Strategy Pattern**: Pluggable formatters for different output formats
- **Service Layer**: Reusable business logic across API and CLI
- **Factory Pattern**: Tool creation and schema generation

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Web Framework** | FastAPI 0.109+ |
| **ASGI Server** | Uvicorn |
| **Data Validation** | Pydantic v2 |
| **YouTube API** | yt-dlp, youtube-transcript-api |
| **AI Integration** | google-generativeai (Gemini) |
| **Testing** | pytest, pytest-cov, httpx |
| **Python Version** | 3.11+ |

---

## 🧪 Testing

The project maintains **81% test coverage** with comprehensive unit and integration tests.

### Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ -v --cov=api --cov=core --cov=tools --cov=api_main --cov-report=term-missing

# Run specific test file
python -m pytest tests/api/test_video_router.py -v

# Generate HTML coverage report
python -m pytest tests/ --cov=api --cov=core --cov=tools --cov-report=html
```

### Test Structure

```
tests/
├── api/                             # API endpoint tests (27 tests)
│   ├── test_main.py                 # Main API tests
│   ├── test_video_router.py         # Video router tests
│   ├── test_playlist_router.py      # Playlist router tests
│   └── test_ai_router.py            # AI router tests
├── core/                            # Service layer tests (21 tests)
│   ├── test_youtube_service.py      # YouTube service tests
│   ├── test_ai_service.py           # AI service tests
│   └── test_formatter_service.py    # Formatter tests
└── tools/                           # Tool tests (29 tests)
    ├── test_video_scraper.py        # Video scraper tests
    ├── test_summarizer.py           # Summarizer tests
    ├── test_translator.py           # Translator tests
    └── test_topic_extractor.py      # Topic extractor tests
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# AI Features (Optional)
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL_NAME=gemini-2.0-flash-exp

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO

# CORS (Optional)
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
```

### Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` file

---

## 📊 Response Formats

### Video Information Response

```json
{
  "metadata": {
    "video_id": "dQw4w9WgXcQ",
    "title": "Sample Video Title",
    "channel": "Sample Channel",
    "upload_date": "20230101",
    "duration": 212,
    "view_count": 1000000,
    "like_count": 50000,
    "description": "Video description...",
    "thumbnail_url": "https://i.ytimg.com/vi/..."
  },
  "transcript": [
    {
      "start": 0.0,
      "duration": 3.5,
      "text": "Hello and welcome",
      "timestamp": "00:00:00"
    }
  ],
  "transcript_language": "en"
}
```

### Scrape with AI Response

```json
{
  "metadata": { ... },
  "transcript": [ ... ],
  "transcript_language": "en",
  "summary": "1. First key point\n2. Second key point\n3. Third key point",
  "translation": "Translated full text...",
  "key_topics": ["Topic 1", "Topic 2", "Topic 3"],
  "output_file": "output/Video_Title.json"
}
```

### Playlist Response

```json
{
  "playlist_info": {
    "playlist_id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
    "title": "Sample Playlist",
    "uploader": "Channel Name",
    "video_count": 50,
    "description": "Playlist description"
  },
  "videos": [
    {
      "video_id": "dQw4w9WgXcQ",
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "title": "Video Title",
      "index": 1
    }
  ],
  "total_videos": 50,
  "returned_videos": 10
}
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/utube-script-scrapper.git

# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Check code coverage
python -m pytest tests/ --cov=api --cov=core --cov=tools --cov-report=html
```

### Code Style

- Follow **PEP 8** conventions
- Use **type hints** throughout
- Write **docstrings** for all public functions
- Maintain **80%+ test coverage**
- Use **async/await** for I/O operations

---

## 🐛 Troubleshooting

### Common Issues

#### "Transcript not found" Error

**Problem**: Video doesn't have subtitles in the requested language.

**Solution**: Try different language combinations:
```bash
curl -X POST "http://localhost:8000/video/info" \
  -d '{"video_url": "...", "languages": ["en", "auto"]}'
```

#### AI Service Returns 503

**Problem**: Gemini API key not configured or invalid.

**Solution**:
1. Check your API key is set: `echo $GEMINI_API_KEY`
2. Verify the key at [Google AI Studio](https://makersuite.google.com)
3. Check API quota limits

#### CORS Errors in Browser

**Problem**: Cross-origin requests blocked.

**Solution**: Configure CORS origins in `.env`:
```env
CORS_ORIGINS=["http://localhost:3000", "http://your-domain.com"]
```

#### Port Already in Use

**Problem**: Port 8000 is already occupied.

**Solution**: Use a different port:
```bash
uvicorn api_main:app --port 8001
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

- **Comply with YouTube's Terms of Service** when using this tool
- **Respect copyright** - do not redistribute copyrighted content
- **Rate limiting** may apply to YouTube and Gemini APIs
- **Educational and personal use** - not for commercial scraping at scale

---

## 🗺️ Roadmap

- [ ] WebSocket support for real-time progress updates
- [ ] Database integration for caching results
- [ ] Admin dashboard for monitoring
- [ ] Docker containerization
- [ ] Kubernetes deployment configs
- [ ] GraphQL API support
- [ ] More AI model integrations (OpenAI, Anthropic)
- [ ] Video download capabilities
- [ ] Batch processing queue system

---

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Pydantic Documentation**: https://docs.pydantic.dev
- **YouTube Data API**: https://developers.google.com/youtube
- **Gemini API**: https://ai.google.dev/docs
- **Project Issues**: https://github.com/Rosin23/utube-script-scrapper/issues

---

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **yt-dlp** - YouTube data extraction
- **Google Gemini** - AI capabilities
- **Pydantic** - Data validation
- **pytest** - Testing framework

---

<div align="center">

**Made with ❤️ by [Rosin23](https://github.com/Rosin23)**

If you find this project useful, please consider giving it a ⭐️

[Report Bug](https://github.com/Rosin23/utube-script-scrapper/issues) •
[Request Feature](https://github.com/Rosin23/utube-script-scrapper/issues) •
[Documentation](http://localhost:8000/docs)

</div>
