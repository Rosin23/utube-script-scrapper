# YouTube API v3 Refactoring Plan

## Overview
This document outlines the comprehensive refactoring needed to align the codebase with YouTube Data API v3 official specifications and best practices.

## References
- [YouTube Data API v3 - Videos Resource](https://developers.google.com/youtube/v3/docs/videos)
- [YouTube Data API v3 - PlaylistItems Resource](https://developers.google.com/youtube/v3/docs/playlistItems)
- [YouTube Data API v3 - Playlists Resource](https://developers.google.com/youtube/v3/docs/playlists)

## Issues Found

### 1. Variable Naming Misalignment (`youtube_api.py`)

**Current vs. YouTube API v3 Standard:**

| Current Field | YouTube API v3 Field | Location | Issue |
|--------------|---------------------|----------|-------|
| `upload_date` | `snippet.publishedAt` | Line 87 | Non-standard naming, should use ISO 8601 datetime |
| `channel` | `snippet.channelTitle` | Line 86 | Non-standard naming |
| `like_count` | `statistics.likeCount` | Line 90 | Naming OK, but missing conversion from string |
| `view_count` | `statistics.viewCount` | Line 89 | Naming OK, but missing conversion from string |
| `thumbnail_url` | `snippet.thumbnails` | Line 91 | Should be object with multiple sizes |
| N/A | `snippet.channelId` | Missing | Critical field for API compatibility |
| N/A | `snippet.tags` | Missing | Important metadata field |
| N/A | `snippet.categoryId` | Missing | Important metadata field |
| N/A | `contentDetails.duration` | Line 88 | Using yt-dlp's integer, API uses ISO 8601 duration |

**yt-dlp vs YouTube API v3 Mapping:**
```python
# yt-dlp provides:
info.get('upload_date')        # Format: '20230101'
info.get('channel')            # Channel name
info.get('duration')           # Integer seconds

# YouTube API v3 provides:
snippet.publishedAt           # ISO 8601: '2023-01-01T10:30:00Z'
snippet.channelTitle          # Channel name
contentDetails.duration       # ISO 8601 duration: 'PT15M33S'
```

### 2. Playlist Handler Issues (`playlist_handler.py`)

**Current vs. YouTube API v3 Standard:**

| Current Field | YouTube API v3 Field | Location | Issue |
|--------------|---------------------|----------|-------|
| `uploader` | `snippet.channelTitle` | Line 95 | Non-standard naming |
| `position` | `snippet.position` | Line 153 | ✓ Correctly 0-based |
| `id` (video) | `snippet.resourceId.videoId` | Line 150 | Missing nested structure |
| N/A | `contentDetails.videoId` | Missing | Alternative video ID location |

**PlaylistItems Structure:**
```python
# Current implementation:
{
    'id': 'video_id',
    'url': 'video_url',
    'title': 'title',
    'position': 0
}

# YouTube API v3 structure:
{
    'snippet': {
        'playlistId': 'playlist_id',
        'position': 0,
        'resourceId': {
            'kind': 'youtube#video',
            'videoId': 'video_id'
        },
        'title': 'title',
        'channelId': 'channel_id',
        'channelTitle': 'channel_name'
    },
    'contentDetails': {
        'videoId': 'video_id',
        'videoPublishedAt': '2023-01-01T10:30:00Z'
    }
}
```

### 3. Schema Documentation

**Issues:**
- Schemas use Python snake_case (good for Python) but don't document mapping to API's camelCase
- Missing field descriptions referencing YouTube API v3 spec
- Missing optional fields that are important for full API compatibility

## Refactoring Strategy

### Phase 1: Add YouTube API v3 Field Mapping Layer

**Goal:** Create a mapping layer that translates between yt-dlp responses and YouTube API v3 standard format.

**Files to modify:**
- `youtube_api.py` - Add mapping functions
- `playlist_handler.py` - Add mapping functions
- New file: `utils/youtube_api_mapper.py` - Centralized mapping logic

**Benefits:**
- Maintains backward compatibility
- Provides YouTube API v3 compliant output option
- Documents field mappings clearly
- Easier to switch from yt-dlp to official YouTube API v3 in the future

### Phase 2: Update Variable Names and Add Missing Fields

**`youtube_api.py` changes:**

```python
def get_video_metadata(url: str, api_v3_format: bool = False) -> Dict[str, str]:
    """
    YouTube 비디오의 메타데이터를 가져옵니다.

    Args:
        url: YouTube 비디오 URL
        api_v3_format: True면 YouTube API v3 호환 형식으로 반환

    Returns:
        비디오 메타데이터 딕셔너리

    Field Mappings (yt-dlp → YouTube API v3):
        - upload_date → snippet.publishedAt
        - channel → snippet.channelTitle
        - duration → contentDetails.duration (converted to ISO 8601)
        - like_count → statistics.likeCount
        - view_count → statistics.viewCount
        - thumbnail → snippet.thumbnails.{size}.url
    """
    # Implementation with optional YouTube API v3 format
```

**New return structure (when `api_v3_format=True`):**
```python
{
    'id': 'video_id',
    'snippet': {
        'publishedAt': '2023-01-01T10:30:00Z',  # ISO 8601 format
        'channelId': 'UC...',
        'channelTitle': 'Channel Name',
        'title': 'Video Title',
        'description': 'Description',
        'thumbnails': {
            'default': {'url': '...', 'width': 120, 'height': 90},
            'medium': {'url': '...', 'width': 320, 'height': 180},
            'high': {'url': '...', 'width': 480, 'height': 360},
            'standard': {'url': '...', 'width': 640, 'height': 480},
            'maxres': {'url': '...', 'width': 1280, 'height': 720}
        },
        'tags': ['tag1', 'tag2'],
        'categoryId': '22'
    },
    'contentDetails': {
        'duration': 'PT15M33S',  # ISO 8601 duration
        'dimension': '2d',
        'definition': 'hd',
        'caption': 'true'
    },
    'statistics': {
        'viewCount': '1000000',  # String as per API spec
        'likeCount': '50000',
        'commentCount': '1200'
    }
}
```

**`playlist_handler.py` changes:**

```python
def get_playlist_info(url: str, api_v3_format: bool = False) -> Optional[Dict]:
    """
    재생목록 정보를 가져옵니다.

    Args:
        url: YouTube 플레이리스트 URL
        api_v3_format: True면 YouTube API v3 호환 형식으로 반환

    Returns:
        플레이리스트 정보 (YouTube API v3 형식 선택 가능)

    Field Mappings:
        - uploader → snippet.channelTitle
        - playlist_id → id
    """
```

### Phase 3: Add API Schema Documentation

**Update all schemas with:**
1. YouTube API v3 field name mappings in docstrings
2. Reference links to official API documentation
3. Examples showing both formats

### Phase 4: Add Logging Documentation System

**New file:** `utils/logging_handler.py`

```python
"""
Logging documentation system for tracking API calls and operations.
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class LogDocumenter:
    """
    로깅 기록을 문서화하는 클래스

    Features:
    - Structured logging to files
    - API call tracking
    - Error documentation
    - Performance metrics
    """

    def __init__(self, log_dir: str = "logs/documented"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def document_api_call(
        self,
        operation: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        duration: float,
        error: Optional[Exception] = None
    ):
        """API 호출을 문서화합니다."""
        pass

    def generate_daily_report(self):
        """일일 로그 리포트를 생성합니다."""
        pass
```

### Phase 5: Update Tests

**Add tests for:**
- YouTube API v3 format conversion
- Field mapping accuracy
- Backward compatibility
- Logging documentation

## Implementation Priority

1. **High Priority:**
   - Add YouTube API v3 field mapper (backward compatible)
   - Add missing critical fields (channelId, tags, categoryId)
   - Add logging documentation system

2. **Medium Priority:**
   - Update schema documentation
   - Add duration ISO 8601 conversion
   - Add thumbnails object structure

3. **Low Priority:**
   - Refactor variable names (maintain backward compatibility)
   - Add comprehensive API v3 format option throughout

## Backward Compatibility Strategy

- Keep existing field names as default
- Add `api_v3_format` flag to enable YouTube API v3 naming
- Provide both formats in responses where needed
- Update documentation to show both formats
- Add deprecation warnings for future migration

## Testing Strategy

```python
def test_youtube_api_v3_format():
    """Test YouTube API v3 format compliance"""
    service = YouTubeService()

    # Test with API v3 format
    result = service.get_video_metadata(
        video_id="test_id",
        api_v3_format=True
    )

    # Verify structure
    assert 'snippet' in result
    assert 'channelTitle' in result['snippet']
    assert 'publishedAt' in result['snippet']
    assert 'contentDetails' in result
    assert 'statistics' in result
```

## Documentation Updates

1. **README.md:**
   - Add section on YouTube API v3 compliance
   - Document field mappings
   - Add migration guide

2. **CLAUDE.md:**
   - Update architecture section with mapper layer
   - Add YouTube API v3 format examples
   - Document logging system

3. **API Documentation:**
   - Update OpenAPI schemas with YouTube API v3 references
   - Add examples showing both formats
   - Link to official YouTube API v3 docs

## Success Criteria

- [ ] All critical YouTube API v3 fields are available
- [ ] Field names match YouTube API v3 specification
- [ ] Backward compatibility maintained
- [ ] Logging documentation system implemented
- [ ] Tests pass with >80% coverage
- [ ] Documentation updated
- [ ] Examples demonstrate both formats

## Timeline

**Phase 1-2:** Core refactoring (immediate)
**Phase 3:** Schema updates (immediate)
**Phase 4:** Logging system (immediate)
**Phase 5:** Testing & documentation (before commit)

## Notes

- yt-dlp is a great tool but doesn't follow YouTube API v3 naming conventions
- We're not replacing yt-dlp, just adding a compatibility layer
- This prepares the codebase for potential future migration to official YouTube Data API v3
- Maintains all existing functionality while improving API compliance
