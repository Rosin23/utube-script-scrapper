#!/bin/bash
#
# cURL Examples for YouTube Script Scraper API
#
# This file contains example cURL commands for all API endpoints.
# Make sure the API server is running before executing these commands.

BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}YouTube Script Scraper API - cURL Examples${NC}\n"

# ============================================================================
# VIDEO ENDPOINTS
# ============================================================================

echo -e "${GREEN}1. Get Video Information${NC}"
curl -X POST "${BASE_URL}/video/info" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "languages": ["en"],
    "prefer_manual": true
  }' | jq '.'

echo -e "\n${GREEN}2. Scrape Video with AI Enhancement${NC}"
curl -X POST "${BASE_URL}/video/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    "enable_summary": true,
    "summary_max_points": 5,
    "enable_translation": true,
    "target_language": "ko",
    "enable_topics": true,
    "num_topics": 5,
    "output_format": "json"
  }' | jq '.'

echo -e "\n${GREEN}3. Get Video Metadata Only${NC}"
curl -X GET "${BASE_URL}/video/metadata?video_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -H "Accept: application/json" | jq '.'

echo -e "\n${GREEN}4. Get Video Transcript Only${NC}"
curl -X GET "${BASE_URL}/video/transcript?video_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&languages=en&languages=ko" \
  -H "Accept: application/json" | jq '.'

# ============================================================================
# PLAYLIST ENDPOINTS
# ============================================================================

echo -e "\n${GREEN}5. Get Playlist Information${NC}"
curl -X POST "${BASE_URL}/playlist/info" \
  -H "Content-Type: application/json" \
  -d '{
    "playlist_url": "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
    "max_videos": 10
  }' | jq '.'

echo -e "\n${GREEN}6. Check if URL is Playlist${NC}"
curl -X GET "${BASE_URL}/playlist/check?url=https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf" \
  -H "Accept: application/json" | jq '.'

echo -e "\n${GREEN}7. Get Playlist Videos Only${NC}"
curl -X GET "${BASE_URL}/playlist/videos?playlist_url=https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf&max_videos=5" \
  -H "Accept: application/json" | jq '.'

# ============================================================================
# AI ENDPOINTS
# ============================================================================

echo -e "\n${GREEN}8. Generate Summary${NC}"
curl -X POST "${BASE_URL}/ai/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Long text to summarize goes here...",
    "max_points": 5,
    "language": "en"
  }' | jq '.'

echo -e "\n${GREEN}9. Translate Text${NC}"
curl -X POST "${BASE_URL}/ai/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_language": "ko",
    "source_language": "en"
  }' | jq '.'

echo -e "\n${GREEN}10. Extract Topics${NC}"
curl -X POST "${BASE_URL}/ai/topics" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Text about machine learning, artificial intelligence, and data science...",
    "num_topics": 5,
    "language": "en"
  }' | jq '.'

echo -e "\n${GREEN}11. AI Enhancement (All Features)${NC}"
curl -X POST "${BASE_URL}/ai/enhance" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Long text to process with all AI features...",
    "enable_summary": true,
    "summary_max_points": 3,
    "enable_translation": true,
    "target_language": "ko",
    "enable_topics": true,
    "num_topics": 5,
    "language": "en"
  }' | jq '.'

echo -e "\n${GREEN}12. Check AI Service Health${NC}"
curl -X GET "${BASE_URL}/ai/health" \
  -H "Accept: application/json" | jq '.'

# ============================================================================
# GENERAL ENDPOINTS
# ============================================================================

echo -e "\n${GREEN}13. Root Endpoint (API Info)${NC}"
curl -X GET "${BASE_URL}/" \
  -H "Accept: application/json" | jq '.'

echo -e "\n${GREEN}14. Health Check${NC}"
curl -X GET "${BASE_URL}/health" \
  -H "Accept: application/json" | jq '.'

echo -e "\n${GREEN}15. Get Tool Schemas (for AI Agents)${NC}"
curl -X GET "${BASE_URL}/tools/schemas" \
  -H "Accept: application/json" | jq '.'

# ============================================================================
# ERROR HANDLING EXAMPLES
# ============================================================================

echo -e "\n${BLUE}Error Handling Examples${NC}\n"

echo -e "${GREEN}16. Invalid URL Error${NC}"
curl -X POST "${BASE_URL}/video/info" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "not-a-valid-url",
    "languages": ["en"]
  }' | jq '.'

echo -e "\n${GREEN}17. AI Service Unavailable (without API key)${NC}"
curl -X POST "${BASE_URL}/ai/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test text",
    "max_points": 3
  }' | jq '.'

# ============================================================================
# ADVANCED USAGE
# ============================================================================

echo -e "\n${BLUE}Advanced Usage Examples${NC}\n"

echo -e "${GREEN}18. Batch Processing Playlist Videos${NC}"
# Get playlist videos
VIDEOS=$(curl -s -X POST "${BASE_URL}/playlist/info" \
  -H "Content-Type: application/json" \
  -d '{
    "playlist_url": "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
    "max_videos": 3
  }' | jq -r '.videos[].url')

# Process each video
for video_url in $VIDEOS; do
  echo "Processing: $video_url"
  curl -s -X POST "${BASE_URL}/video/info" \
    -H "Content-Type: application/json" \
    -d "{\"video_url\": \"$video_url\", \"languages\": [\"en\"]}" \
    | jq '.metadata.title'
done

echo -e "\n${GREEN}19. Save Response to File${NC}"
curl -X POST "${BASE_URL}/video/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "enable_summary": true,
    "output_format": "json"
  }' -o video_output.json

echo "Response saved to video_output.json"

echo -e "\n${GREEN}20. Check Response Status Code${NC}"
curl -X GET "${BASE_URL}/health" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s -o /dev/null

echo -e "\n${BLUE}Examples completed!${NC}"
