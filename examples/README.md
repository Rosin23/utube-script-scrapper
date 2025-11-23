# API Examples

This directory contains comprehensive examples demonstrating how to use the YouTube Script Scraper API.

## Directory Structure

```
examples/
├── api_responses/              # Example API responses
│   ├── video_info_success.json
│   ├── video_scrape_with_ai.json
│   ├── playlist_info_success.json
│   ├── error_invalid_url.json
│   ├── error_no_transcript.json
│   └── error_ai_service_unavailable.json
├── code_samples/               # Code examples in different languages
│   ├── python_basic_usage.py
│   ├── javascript_fetch_example.js
│   └── curl_examples.sh
└── README.md                   # This file
```

## API Response Examples

### Success Responses

- **`video_info_success.json`**: Example response from `/video/info` endpoint
- **`video_scrape_with_ai.json`**: Complete response with AI enhancements (summary, translation, topics)
- **`playlist_info_success.json`**: Playlist information with video list

### Error Responses

- **`error_invalid_url.json`**: Response when invalid YouTube URL is provided
- **`error_no_transcript.json`**: Response when video has no available transcripts
- **`error_ai_service_unavailable.json`**: Response when AI service is not configured

## Code Samples

### Python Examples (`python_basic_usage.py`)

Complete Python examples using the `requests` library:

```bash
# Install dependencies
pip install requests

# Run examples
python examples/code_samples/python_basic_usage.py
```

**Features:**
- Get video information
- Scrape with AI features
- Process playlists
- Generate summaries
- Translate text
- Extract topics
- Comprehensive error handling

### JavaScript Examples (`javascript_fetch_example.js`)

Modern JavaScript/Node.js examples using fetch API:

```bash
# For Node.js, install node-fetch
npm install node-fetch

# Run examples
node examples/code_samples/javascript_fetch_example.js
```

**Features:**
- Async/await patterns
- Promise-based error handling
- Works in both browser and Node.js
- All API endpoints covered

### cURL Examples (`curl_examples.sh`)

Shell script with cURL commands for all endpoints:

```bash
# Make executable
chmod +x examples/code_samples/curl_examples.sh

# Run all examples
./examples/code_samples/curl_examples.sh

# Or run individual commands
curl -X POST "http://localhost:8000/video/info" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

**Features:**
- All API endpoints
- Error handling examples
- Advanced usage (batch processing, file saving)
- Colored output for readability

## Quick Start

### 1. Start the API Server

```bash
python api_main.py
```

### 2. Run Examples

**Python:**
```bash
python examples/code_samples/python_basic_usage.py
```

**JavaScript:**
```bash
node examples/code_samples/javascript_fetch_example.js
```

**cURL:**
```bash
./examples/code_samples/curl_examples.sh
```

## Common Use Cases

### Extract Video Information

**Python:**
```python
video_data = get_video_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(f"Title: {video_data['metadata']['title']}")
```

**JavaScript:**
```javascript
const videoData = await getVideoInfo('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
console.log(`Title: ${videoData.metadata.title}`);
```

**cURL:**
```bash
curl -X POST "http://localhost:8000/video/info" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### Process Playlist

**Python:**
```python
playlist_data = get_playlist_info(
    "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
    max_videos=10
)
for video in playlist_data['videos']:
    print(f"- {video['title']}")
```

### AI-Powered Summarization

**Python:**
```python
ai_data = scrape_video_with_ai(
    "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    enable_summary=True,
    enable_topics=True
)
print(f"Summary: {ai_data['summary']}")
print(f"Topics: {ai_data['key_topics']}")
```

## Error Handling

All examples include proper error handling. Common errors:

### 400 Bad Request
- Invalid YouTube URL
- Missing required parameters
- Invalid parameter values

### 503 Service Unavailable
- AI service not configured (missing API key)
- Gemini API quota exceeded

### 500 Internal Server Error
- YouTube service unavailable
- Transcript not found
- Processing errors

## Testing Examples

You can use these examples to test the API:

```bash
# Test video endpoint
curl http://localhost:8000/video/metadata?video_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Test health check
curl http://localhost:8000/health

# Test AI service
curl http://localhost:8000/ai/health
```

## Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Main README**: ../README.md
- **Project Documentation**: ../docs/
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Contributing

Found an issue or have a suggestion for examples? Please:
1. Check existing examples
2. Open an issue
3. Submit a pull request

## License

Same as the main project (MIT License).
