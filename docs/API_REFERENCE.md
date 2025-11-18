# API Reference

Complete reference documentation for the YouTube Script Scraper API.

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Request/Response Format](#requestresponse-format)
- [Video Endpoints](#video-endpoints)
- [Playlist Endpoints](#playlist-endpoints)
- [AI Endpoints](#ai-endpoints)
- [Utility Endpoints](#utility-endpoints)
- [Error Codes](#error-codes)
- [Rate Limiting](#rate-limiting)

---

## Base URL

```
http://localhost:8000
```

For production deployments, replace with your actual domain.

## Authentication

### Basic Endpoints
No authentication required for basic video/playlist scraping endpoints.

### AI Endpoints
Requires Gemini API key configured via environment variables:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

## Request/Response Format

### Content Type
All requests must include:
```
Content-Type: application/json
```

### Response Format
All responses are in JSON format unless otherwise specified.

### Common Response Fields

```json
{
  "metadata": {
    "video_id": "string",
    "title": "string",
    "channel": "string",
    "upload_date": "string (YYYYMMDD)",
    "duration": "integer (seconds)",
    "view_count": "integer",
    "like_count": "integer",
    "description": "string",
    "thumbnail_url": "string (URL)"
  },
  "transcript": [
    {
      "start": "float",
      "duration": "float",
      "text": "string",
      "timestamp": "string (HH:MM:SS)"
    }
  ]
}
```

---

## Video Endpoints

### POST /video/info

Get video metadata and transcript.

#### Request Body

```json
{
  "video_url": "string (required)",
  "languages": ["string"] (optional, default: ["ko", "en"]),
  "prefer_manual": boolean (optional, default: true)
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `video_url` | string | Yes | - | YouTube video URL |
| `languages` | array[string] | No | `["ko", "en"]` | Preferred subtitle languages in priority order |
| `prefer_manual` | boolean | No | `true` | Prefer manually created subtitles over auto-generated |

#### Response 200

```json
{
  "metadata": {
    "video_id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "channel": "Rick Astley",
    "upload_date": "20091024",
    "duration": 212,
    "view_count": 1400000000,
    "like_count": 15000000,
    "description": "The official video...",
    "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
  },
  "transcript": [
    {
      "start": 0.0,
      "duration": 2.88,
      "text": "♪ We're no strangers to love ♪",
      "timestamp": "00:00:00"
    }
  ],
  "transcript_language": "en"
}
```

#### cURL Example

```bash
curl -X POST "http://localhost:8000/video/info" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "languages": ["en"],
    "prefer_manual": true
  }'
```

---

### POST /video/scrape

Scrape video with optional AI enhancements.

#### Request Body

```json
{
  "video_url": "string (required)",
  "languages": ["string"] (optional),
  "prefer_manual": boolean (optional),
  "enable_summary": boolean (optional, default: false),
  "summary_max_points": integer (optional, default: 5, range: 1-10),
  "enable_translation": boolean (optional, default: false),
  "target_language": "string (optional)",
  "enable_topics": boolean (optional, default: false),
  "num_topics": integer (optional, default: 5, range: 1-20),
  "output_format": "string (optional, values: txt|json|xml|markdown)"
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `video_url` | string | Yes | - | YouTube video URL |
| `enable_summary` | boolean | No | `false` | Enable AI-powered summarization |
| `summary_max_points` | integer | No | `5` | Number of summary points (1-10) |
| `enable_translation` | boolean | No | `false` | Enable translation |
| `target_language` | string | Conditional | - | Target language code (required if translation enabled) |
| `enable_topics` | boolean | No | `false` | Enable topic extraction |
| `num_topics` | integer | No | `5` | Number of topics to extract (1-20) |
| `output_format` | string | No | - | Save to file in specified format |

#### Response 200

```json
{
  "metadata": { ... },
  "transcript": [ ... ],
  "transcript_language": "en",
  "summary": "1. First key point\n2. Second key point...",
  "translation": "Translated full text...",
  "key_topics": ["Topic 1", "Topic 2", "Topic 3"],
  "output_file": "output/Video_Title.json"
}
```

#### cURL Example

```bash
curl -X POST "http://localhost:8000/video/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    "enable_summary": true,
    "summary_max_points": 5,
    "enable_translation": true,
    "target_language": "ko",
    "enable_topics": true,
    "num_topics": 5
  }'
```

---

### GET /video/metadata

Get only video metadata (no transcript).

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_url` | string | Yes | YouTube video URL |

#### Response 200

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "Rick Astley",
  "upload_date": "20091024",
  "duration": 212,
  "view_count": 1400000000,
  "like_count": 15000000,
  "description": "The official video...",
  "thumbnail_url": "https://i.ytimg.com/vi/..."
}
```

#### cURL Example

```bash
curl "http://localhost:8000/video/metadata?video_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

---

### GET /video/transcript

Get only video transcript (no metadata).

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `video_url` | string | Yes | - | YouTube video URL |
| `languages` | array[string] | No | `["ko", "en"]` | Preferred languages |
| `prefer_manual` | boolean | No | `true` | Prefer manual subtitles |

#### Response 200

```json
[
  {
    "start": 0.0,
    "duration": 2.88,
    "text": "♪ We're no strangers to love ♪",
    "timestamp": "00:00:00"
  }
]
```

#### cURL Example

```bash
curl "http://localhost:8000/video/transcript?video_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&languages=en"
```

---

## Playlist Endpoints

### POST /playlist/info

Get playlist information and video list.

#### Request Body

```json
{
  "playlist_url": "string (required)",
  "max_videos": integer (optional, null = all videos)
}
```

#### Response 200

```json
{
  "playlist_info": {
    "playlist_id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
    "title": "Python Tutorial for Beginners",
    "uploader": "Programming with Mosh",
    "video_count": 45,
    "description": "Learn Python programming..."
  },
  "videos": [
    {
      "video_id": "kqtD5dpn9C8",
      "url": "https://www.youtube.com/watch?v=kqtD5dpn9C8",
      "title": "Python Tutorial - Python for Beginners",
      "index": 1
    }
  ],
  "total_videos": 45,
  "returned_videos": 10
}
```

---

### GET /playlist/check

Check if URL is a playlist or video.

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | YouTube URL to check |

#### Response 200

```json
{
  "url": "https://www.youtube.com/playlist?list=PLtest",
  "is_playlist": true,
  "type": "playlist"
}
```

---

### GET /playlist/videos

Get only playlist videos (no metadata).

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `playlist_url` | string | Yes | YouTube playlist URL |
| `max_videos` | integer | No | Maximum videos to return |

#### Response 200

```json
{
  "videos": [
    {
      "id": "video1",
      "url": "https://www.youtube.com/watch?v=...",
      "title": "Video Title"
    }
  ],
  "count": 10
}
```

---

## AI Endpoints

### POST /ai/summary

Generate AI-powered summary of text.

#### Request Body

```json
{
  "text": "string (required)",
  "max_points": integer (optional, default: 5, range: 1-10),
  "language": "string (optional, default: ko)"
}
```

#### Response 200

```json
{
  "summary": "1. First key point\n2. Second key point\n3. Third key point",
  "original_length": 1500,
  "summary_length": 200,
  "language": "ko"
}
```

---

### POST /ai/translate

Translate text to target language.

#### Request Body

```json
{
  "text": "string (required)",
  "target_language": "string (required)",
  "source_language": "string (optional, auto-detect if not provided)"
}
```

#### Response 200

```json
{
  "translated_text": "Translated content...",
  "source_language": "en",
  "target_language": "ko",
  "original_length": 100,
  "translated_length": 120
}
```

---

### POST /ai/topics

Extract key topics from text.

#### Request Body

```json
{
  "text": "string (required)",
  "num_topics": integer (optional, default: 5, range: 1-20),
  "language": "string (optional, default: ko)"
}
```

#### Response 200

```json
{
  "topics": ["Topic 1", "Topic 2", "Topic 3"],
  "num_topics": 3,
  "language": "ko"
}
```

---

### POST /ai/enhance

Apply all AI features to text.

#### Request Body

```json
{
  "text": "string (required)",
  "enable_summary": boolean (optional, default: false),
  "summary_max_points": integer (optional),
  "enable_translation": boolean (optional, default: false),
  "target_language": "string (optional)",
  "enable_topics": boolean (optional, default: false),
  "num_topics": integer (optional),
  "language": "string (optional)"
}
```

#### Response 200

```json
{
  "summary": "AI-generated summary...",
  "translation": "Translated text...",
  "topics": ["Topic 1", "Topic 2"],
  "processing_time": 2.5
}
```

---

### GET /ai/health

Check AI service availability.

#### Response 200

```json
{
  "available": true,
  "model": "gemini-2.0-flash-exp",
  "api_key_configured": true
}
```

---

## Utility Endpoints

### GET /

Get API information.

#### Response 200

```json
{
  "name": "YouTube Script Scraper API",
  "version": "3.0.0",
  "description": "FastAPI-based YouTube scraper with AI",
  "docs": "/docs",
  "redoc": "/redoc",
  "openapi": "/openapi.json",
  "endpoints": { ... }
}
```

---

### GET /health

Health check endpoint.

#### Response 200

```json
{
  "status": "healthy",
  "timestamp": "2025-11-18T12:00:00Z"
}
```

---

### GET /tools/schemas

Get OpenAI function calling compatible tool schemas.

#### Response 200

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "video_scraper",
        "description": "Scrape YouTube videos...",
        "parameters": { ... }
      }
    }
  ]
}
```

---

## Error Codes

### 400 Bad Request

Invalid request parameters.

```json
{
  "detail": "Invalid YouTube URL: not-a-valid-url"
}
```

### 404 Not Found

Resource not found.

```json
{
  "detail": "Not Found"
}
```

### 503 Service Unavailable

AI service not available.

```json
{
  "detail": "AI service is not available. Please check API key configuration."
}
```

### 500 Internal Server Error

Server processing error.

```json
{
  "detail": "Failed to get video info: YouTube service error"
}
```

---

## Rate Limiting

### YouTube API
- No built-in rate limiting
- Subject to YouTube's rate limits
- Recommended: 1 request per second

### Gemini API
- Free tier: 60 requests per minute
- Paid tier: Higher limits based on plan
- Check status: `GET /ai/health`

---

## Best Practices

1. **Error Handling**: Always check HTTP status codes
2. **Retry Logic**: Implement exponential backoff for failed requests
3. **Caching**: Cache video metadata to reduce API calls
4. **Batch Processing**: Use playlist endpoints for multiple videos
5. **AI Usage**: Enable AI features only when needed to conserve quota

---

## Interactive Documentation

For interactive API documentation, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## See Also

- [Architecture Documentation](ARCHITECTURE.md)
- [Development Guide](DEVELOPMENT.md)
- [API Examples](../examples/README.md)
