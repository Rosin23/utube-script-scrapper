"""
Legacy Module

Contains legacy implementation files that have been moved from the project root.
These modules are still actively used by the core layer but have been organized
into a dedicated directory for better project structure.

Files:
- cli.py: Command-line interface (formerly main.py)
- youtube_api.py: YouTube data extraction
- gemini_api.py: Gemini AI API client
- formatters.py: Output formatters
- playlist_handler.py: Playlist processing

Note: This is part of the Phase 4 refactoring to clean up project structure
while maintaining backward compatibility.
"""

# Re-export commonly used items for easier imports
from .youtube_api import (
    extract_video_id,
    get_video_metadata,
    get_transcript_with_timestamps,
    format_timestamp,
    is_yt_dlp_available,
    is_youtube_transcript_api_available
)

from .gemini_api import (
    GeminiClient,
    GeminiAPIError,
    is_gemini_available,
    get_gemini_client
)

from .formatters import (
    Formatter,
    get_formatter,
    get_available_formatters
)

from .playlist_handler import (
    PlaylistHandler,
    process_playlist_or_video
)

__all__ = [
    # YouTube API
    'extract_video_id',
    'get_video_metadata',
    'get_transcript_with_timestamps',
    'format_timestamp',
    'is_yt_dlp_available',
    'is_youtube_transcript_api_available',
    # Gemini API
    'GeminiClient',
    'GeminiAPIError',
    'is_gemini_available',
    'get_gemini_client',
    # Formatters
    'Formatter',
    'get_formatter',
    'get_available_formatters',
    # Playlist Handler
    'PlaylistHandler',
    'process_playlist_or_video',
]
