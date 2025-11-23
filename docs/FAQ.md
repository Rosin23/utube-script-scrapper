# Frequently Asked Questions (FAQ)

Common questions and answers about the YouTube Script Scraper API.

## Table of Contents

- [General Questions](#general-questions)
- [Installation & Setup](#installation--setup)
- [API Usage](#api-usage)
- [AI Features](#ai-features)
- [Troubleshooting](#troubleshooting)
- [Performance](#performance)
- [Development](#development)

---

## General Questions

### What is YouTube Script Scraper API?

A FastAPI-based RESTful API that extracts metadata, transcripts, and descriptions from YouTube videos and playlists, with optional AI-powered enhancements (summarization, translation, topic extraction).

### What can I do with this API?

- Extract video metadata (title, channel, views, etc.)
- Get timestamped transcripts/subtitles
- Process entire playlists
- Generate AI summaries
- Translate transcripts to any language
- Extract key topics
- Export data in multiple formats (JSON, TXT, XML, Markdown)

### Is this API free to use?

Yes, the API itself is open source and free. However:
- YouTube data extraction is free (subject to YouTube's terms)
- AI features require a Gemini API key (has free tier with limits)

### Does it work with private/unlisted videos?

- **Public videos**: Yes ✅
- **Unlisted videos**: Yes (if you have the link) ✅
- **Private videos**: No ❌

### What languages are supported for subtitles?

All languages supported by YouTube, including:
- Korean (ko)
- English (en)
- Japanese (ja)
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- And many more...

---

## Installation & Setup

### What Python version do I need?

Python 3.11 or higher is required.

```bash
python --version  # Should show 3.11+
```

### How do I install dependencies?

```bash
pip install -r requirements.txt
```

### Do I need a YouTube API key?

No! The API uses `yt-dlp` which doesn't require YouTube API credentials.

### How do I get a Gemini API key?

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add to your `.env` file:
   ```
   GEMINI_API_KEY=your-key-here
   ```

### What if I don't have a Gemini API key?

You can still use all basic features:
- Video metadata extraction
- Transcript retrieval
- Playlist processing
- Multiple output formats

AI features (summary, translation, topics) won't work without the API key.

---

## API Usage

### How do I start the API server?

```bash
python api_main.py
```

The API will be available at `http://localhost:8000`

### Where can I find API documentation?

- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **This repository**: `docs/API_REFERENCE.md`

### How do I call the API from Python?

```python
import requests

response = requests.post(
    "http://localhost:8000/video/info",
    json={"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
)
data = response.json()
```

### How do I call the API from JavaScript?

```javascript
const response = await fetch('http://localhost:8000/video/info', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    video_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
  })
});
const data = await response.json();
```

### Can I use cURL?

Yes! See `examples/code_samples/curl_examples.sh` for comprehensive examples.

```bash
curl -X POST "http://localhost:8000/video/info" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### What video URL formats are supported?

- Standard: `https://www.youtube.com/watch?v=VIDEO_ID`
- Short: `https://youtu.be/VIDEO_ID`
- Embed: `https://www.youtube.com/embed/VIDEO_ID`
- With playlist: `https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID`

### How do I process a playlist?

```bash
curl -X POST "http://localhost:8000/playlist/info" \
  -H "Content-Type: application/json" \
  -d '{
    "playlist_url": "https://www.youtube.com/playlist?list=PLAYLIST_ID",
    "max_videos": 10
  }'
```

---

## AI Features

### What AI features are available?

1. **Summarization**: Generate key points summary
2. **Translation**: Translate to any language
3. **Topic Extraction**: Identify main topics

### How much does Gemini API cost?

**Free Tier**:
- 60 requests per minute
- 1,500 requests per day
- Free for testing and development

**Paid Tiers**: Check [Google AI Pricing](https://ai.google.dev/pricing)

### Can I use a different AI model?

Currently, only Gemini is supported. Future versions may support:
- OpenAI GPT
- Anthropic Claude
- Local LLMs

### How accurate is the AI summary?

Accuracy depends on:
- Video content quality
- Transcript quality
- Language (works best with English and Korean)
- Typical accuracy: 85-95%

### Can I adjust summary length?

Yes! Use the `summary_max_points` parameter:

```json
{
  "enable_summary": true,
  "summary_max_points": 3  // 1-10 points
}
```

### What languages can AI features handle?

**Summarization**: Best with English and Korean, works with most languages
**Translation**: Supports 100+ languages
**Topic Extraction**: Works with any language

---

## Troubleshooting

### "No transcript found" error

**Causes**:
1. Video has no subtitles
2. Subtitles disabled by uploader
3. Wrong language code

**Solutions**:
```bash
# Try different languages
curl -X POST "http://localhost:8000/video/info" \
  -d '{"video_url": "...", "languages": ["en", "auto"]}'

# Check available languages
curl "http://localhost:8000/video/metadata?video_url=..."
```

### "Invalid YouTube URL" error

**Check**:
- URL format is correct
- Video ID is valid
- Video is public/unlisted (not private)

### "AI service is not available" (503 error)

**Causes**:
1. Gemini API key not configured
2. Invalid API key
3. API quota exceeded

**Solutions**:
```bash
# Check API key
echo $GEMINI_API_KEY

# Check AI service status
curl http://localhost:8000/ai/health

# Set API key
export GEMINI_API_KEY="your-key-here"
```

### API not starting / Port already in use

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
python api_main.py --port 8001
```

### CORS errors in browser

**Solution**:
Add your domain to CORS origins in `.env`:
```
CORS_ORIGINS=["http://localhost:3000", "http://your-domain.com"]
```

### Slow API responses

**Causes**:
1. Large playlists
2. AI processing
3. Network latency

**Solutions**:
- Limit playlist videos: `max_videos=10`
- Cache frequently accessed data
- Use async requests
- Disable unnecessary AI features

---

## Performance

### How fast is the API?

**Typical response times**:
- Video metadata: 1-2 seconds
- Transcript: 2-3 seconds
- AI summary: 3-5 seconds
- Full scrape with AI: 5-10 seconds

### Can I process videos in parallel?

Yes! Send multiple requests concurrently:

```python
import asyncio
import aiohttp

async def process_videos(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_video(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

### What are the rate limits?

**YouTube**: No built-in limits, but recommended 1 req/sec
**Gemini API**: 60 requests/minute (free tier)

### How can I improve performance?

1. **Cache responses**: Store frequently accessed data
2. **Use Redis**: For distributed caching
3. **Batch processing**: Process multiple videos together
4. **Disable AI**: If not needed
5. **Use playlists**: More efficient than individual requests

---

## Development

### How do I run tests?

```bash
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=api --cov=core --cov=tools
```

### How do I add a new endpoint?

See [Development Guide](DEVELOPMENT.md#adding-new-features)

### Can I contribute?

Yes! See [Contributing Guidelines](../README.md#contributing)

### How do I report a bug?

1. Check existing issues
2. Create new issue with:
   - Description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details

### Is there a Docker image?

Not yet, but planned for future release.

### Can I deploy to production?

Yes! See [Deployment Guide](DEPLOYMENT.md)

---

## Integration

### Can I use this with AI agent frameworks?

Yes! Compatible with:
- **OpenAI Function Calling**
- **Claude Code**
- **LangChain**
- **AutoGPT**
- **Custom agents**

Get tool schemas:
```bash
curl http://localhost:8000/tools/schemas
```

### How do I integrate with my app?

**Option 1**: Direct API calls (REST)
**Option 2**: Use client libraries (Python, JavaScript)
**Option 3**: Use as microservice

### Can I use this in a serverless environment?

Yes, with modifications:
- Use AWS Lambda + API Gateway
- Use Google Cloud Functions
- Use Azure Functions

See [Deployment Guide](DEPLOYMENT.md) for details.

---

## Security

### Is the API secure?

**Current**:
- Input validation (Pydantic)
- Error handling
- No authentication

**Recommended for production**:
- Add API key authentication
- Enable HTTPS
- Add rate limiting
- Use secrets management

### Should I expose this API publicly?

**Development**: Local only
**Production**: Add authentication and rate limiting

### How do I secure my Gemini API key?

- Use environment variables
- Never commit to git
- Use secrets management (AWS Secrets Manager, etc.)
- Rotate keys regularly

---

## Billing & Costs

### How much does it cost to run?

**Infrastructure**:
- Small server: $5-20/month
- Larger deployment: $50-200/month

**API Costs**:
- YouTube data extraction: Free
- Gemini API: Free tier available, then pay-per-use

### Can I track API usage?

Planned feature. Currently:
- Check server logs
- Use Gemini API dashboard for AI usage

---

## Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Examples**: `examples/` directory
- **Architecture**: `docs/ARCHITECTURE.md`
- **Development Guide**: `docs/DEVELOPMENT.md`
- **GitHub Issues**: https://github.com/Rosin23/utube-script-scrapper/issues

---

## Still Have Questions?

1. Check [API Reference](API_REFERENCE.md)
2. Search [GitHub Issues](https://github.com/Rosin23/utube-script-scrapper/issues)
3. Create a new issue with the `question` label
4. Contact maintainers

---

*Last updated: 2025-11-18*
