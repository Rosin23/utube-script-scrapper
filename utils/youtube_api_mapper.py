"""
YouTube API v3 Field Mapper
Maps between yt-dlp response format and YouTube Data API v3 standard format.

Reference: https://developers.google.com/youtube/v3/docs
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime


class YouTubeAPIMapper:
    """
    YouTube Data API v3 호환 형식으로 변환하는 매퍼 클래스

    yt-dlp와 YouTube Data API v3 간의 필드 매핑을 처리합니다.

    Field Mappings:
    ===============
    Video Resource:
    - upload_date → snippet.publishedAt (ISO 8601)
    - channel → snippet.channelTitle
    - channel_id → snippet.channelId
    - duration → contentDetails.duration (ISO 8601: PT#M#S)
    - view_count → statistics.viewCount (string)
    - like_count → statistics.likeCount (string)
    - comment_count → statistics.commentCount (string)
    - thumbnail → snippet.thumbnails.{size}.url

    Playlist Resource:
    - uploader → snippet.channelTitle
    - uploader_id → snippet.channelId
    - playlist_count → contentDetails.itemCount

    PlaylistItem Resource:
    - id (video) → snippet.resourceId.videoId
    - position → snippet.position (0-based)
    """

    @staticmethod
    def convert_upload_date_to_iso8601(upload_date: str) -> str:
        """
        yt-dlp 형식의 upload_date를 ISO 8601 형식으로 변환합니다.

        Args:
            upload_date: yt-dlp format ('20230101')

        Returns:
            ISO 8601 format ('2023-01-01T00:00:00Z')

        Examples:
            >>> convert_upload_date_to_iso8601('20230115')
            '2023-01-15T00:00:00Z'
        """
        if not upload_date or upload_date == 'Unknown Date':
            return None

        try:
            # Parse yt-dlp format: '20230101'
            if len(upload_date) == 8 and upload_date.isdigit():
                year = upload_date[0:4]
                month = upload_date[4:6]
                day = upload_date[6:8]
                return f"{year}-{month}-{day}T00:00:00Z"
            # Already in ISO format
            elif 'T' in upload_date:
                return upload_date
            else:
                return None
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def convert_duration_to_iso8601(seconds: int) -> str:
        """
        초 단위 duration을 ISO 8601 duration 형식으로 변환합니다.

        Args:
            seconds: Duration in seconds

        Returns:
            ISO 8601 duration (e.g., 'PT15M33S', 'PT1H2M10S')

        Examples:
            >>> convert_duration_to_iso8601(933)
            'PT15M33S'
            >>> convert_duration_to_iso8601(3730)
            'PT1H2M10S'
        """
        if not seconds or seconds == 0:
            return 'PT0S'

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        duration = 'PT'
        if hours > 0:
            duration += f'{hours}H'
        if minutes > 0:
            duration += f'{minutes}M'
        if secs > 0 or (hours == 0 and minutes == 0):
            duration += f'{secs}S'

        return duration

    @staticmethod
    def parse_iso8601_duration(duration: str) -> int:
        """
        ISO 8601 duration을 초 단위로 변환합니다.

        Args:
            duration: ISO 8601 duration (e.g., 'PT15M33S')

        Returns:
            Duration in seconds

        Examples:
            >>> parse_iso8601_duration('PT15M33S')
            933
            >>> parse_iso8601_duration('PT1H2M10S')
            3730
        """
        if not duration or not duration.startswith('PT'):
            return 0

        # Remove 'PT' prefix
        duration = duration[2:]

        hours = 0
        minutes = 0
        seconds = 0

        # Parse hours
        if 'H' in duration:
            hours_match = re.search(r'(\d+)H', duration)
            if hours_match:
                hours = int(hours_match.group(1))

        # Parse minutes
        if 'M' in duration:
            minutes_match = re.search(r'(\d+)M', duration)
            if minutes_match:
                minutes = int(minutes_match.group(1))

        # Parse seconds
        if 'S' in duration:
            seconds_match = re.search(r'(\d+)S', duration)
            if seconds_match:
                seconds = int(seconds_match.group(1))

        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def map_video_to_api_v3(yt_dlp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        yt-dlp video 데이터를 YouTube Data API v3 형식으로 변환합니다.

        Args:
            yt_dlp_data: yt-dlp extract_info() 결과

        Returns:
            YouTube Data API v3 video resource 형식의 딕셔너리

        Reference:
            https://developers.google.com/youtube/v3/docs/videos#resource
        """
        video_id = yt_dlp_data.get('id', '')

        # Build snippet object
        snippet = {
            'publishedAt': YouTubeAPIMapper.convert_upload_date_to_iso8601(
                yt_dlp_data.get('upload_date', 'Unknown Date')
            ),
            'channelId': yt_dlp_data.get('channel_id', ''),
            'title': yt_dlp_data.get('title', 'Unknown Title'),
            'description': yt_dlp_data.get('description', 'No description available'),
            'channelTitle': yt_dlp_data.get('channel', 'Unknown Channel'),
            'categoryId': yt_dlp_data.get('categories', ['0'])[0] if yt_dlp_data.get('categories') else '0',
            'tags': yt_dlp_data.get('tags', []),
            'defaultLanguage': yt_dlp_data.get('language'),
            'defaultAudioLanguage': yt_dlp_data.get('audio_language'),
        }

        # Build thumbnails object
        thumbnails = {}
        if yt_dlp_data.get('thumbnails'):
            for thumb in yt_dlp_data['thumbnails']:
                thumb_id = thumb.get('id', 'default')
                thumbnails[thumb_id] = {
                    'url': thumb.get('url'),
                    'width': thumb.get('width'),
                    'height': thumb.get('height')
                }
        elif yt_dlp_data.get('thumbnail'):
            # Single thumbnail URL
            thumbnails['default'] = {
                'url': yt_dlp_data['thumbnail'],
                'width': None,
                'height': None
            }

        snippet['thumbnails'] = thumbnails

        # Build contentDetails object
        content_details = {
            'duration': YouTubeAPIMapper.convert_duration_to_iso8601(
                yt_dlp_data.get('duration', 0)
            ),
            'dimension': '2d',  # yt-dlp doesn't provide this, default to 2d
            'definition': yt_dlp_data.get('format_note', 'sd').lower(),
            'caption': 'true' if yt_dlp_data.get('subtitles') else 'false',
        }

        # Build statistics object (all values as strings per API spec)
        statistics = {
            'viewCount': str(yt_dlp_data.get('view_count', 0)),
            'likeCount': str(yt_dlp_data.get('like_count', 0)) if yt_dlp_data.get('like_count') is not None else None,
            'commentCount': str(yt_dlp_data.get('comment_count', 0)) if yt_dlp_data.get('comment_count') is not None else None,
        }

        # Remove None values from statistics
        statistics = {k: v for k, v in statistics.items() if v is not None}

        return {
            'kind': 'youtube#video',
            'id': video_id,
            'snippet': snippet,
            'contentDetails': content_details,
            'statistics': statistics
        }

    @staticmethod
    def map_video_from_legacy(legacy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        기존 레거시 형식의 비디오 데이터를 YouTube API v3 형식으로 변환합니다.

        Args:
            legacy_data: 기존 get_video_metadata() 결과

        Returns:
            YouTube Data API v3 형식의 딕셔너리
        """
        snippet = {
            'publishedAt': YouTubeAPIMapper.convert_upload_date_to_iso8601(
                legacy_data.get('upload_date', 'Unknown Date')
            ),
            'channelId': '',  # Not available in legacy format
            'title': legacy_data.get('title', 'Unknown Title'),
            'description': legacy_data.get('description', 'No description available'),
            'channelTitle': legacy_data.get('channel', 'Unknown Channel'),
            'categoryId': '0',
            'tags': [],
        }

        # Handle thumbnails
        thumbnails = {}
        if legacy_data.get('thumbnail_url'):
            thumbnails['default'] = {
                'url': legacy_data['thumbnail_url'],
                'width': None,
                'height': None
            }
        snippet['thumbnails'] = thumbnails

        content_details = {
            'duration': YouTubeAPIMapper.convert_duration_to_iso8601(
                legacy_data.get('duration', 0)
            ),
        }

        statistics = {
            'viewCount': str(legacy_data.get('view_count', 0)),
        }
        if legacy_data.get('like_count') is not None:
            statistics['likeCount'] = str(legacy_data['like_count'])

        return {
            'kind': 'youtube#video',
            'id': legacy_data.get('video_id', ''),
            'snippet': snippet,
            'contentDetails': content_details,
            'statistics': statistics
        }

    @staticmethod
    def map_playlist_to_api_v3(yt_dlp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        yt-dlp playlist 데이터를 YouTube Data API v3 형식으로 변환합니다.

        Args:
            yt_dlp_data: yt-dlp extract_info() 결과 (playlist)

        Returns:
            YouTube Data API v3 playlist resource 형식

        Reference:
            https://developers.google.com/youtube/v3/docs/playlists#resource
        """
        snippet = {
            'publishedAt': None,  # yt-dlp doesn't provide this for playlists
            'channelId': yt_dlp_data.get('uploader_id', ''),
            'title': yt_dlp_data.get('title', 'Unknown Playlist'),
            'description': yt_dlp_data.get('description'),
            'channelTitle': yt_dlp_data.get('uploader', 'Unknown Channel'),
        }

        content_details = {
            'itemCount': yt_dlp_data.get('playlist_count', 0)
        }

        return {
            'kind': 'youtube#playlist',
            'id': yt_dlp_data.get('id', 'Unknown'),
            'snippet': snippet,
            'contentDetails': content_details
        }

    @staticmethod
    def map_playlist_item_to_api_v3(
        video_data: Dict[str, Any],
        playlist_id: str,
        position: int
    ) -> Dict[str, Any]:
        """
        비디오 데이터를 YouTube API v3 playlistItem 형식으로 변환합니다.

        Args:
            video_data: 비디오 정보 딕셔너리 (id, title, url 등)
            playlist_id: 플레이리스트 ID
            position: 플레이리스트 내 위치 (0-based)

        Returns:
            YouTube Data API v3 playlistItem resource 형식

        Reference:
            https://developers.google.com/youtube/v3/docs/playlistItems#resource
        """
        video_id = video_data.get('id', '')

        snippet = {
            'publishedAt': None,  # Not available from yt-dlp flat extraction
            'channelId': '',
            'title': video_data.get('title', 'Unknown Title'),
            'description': '',
            'channelTitle': '',
            'playlistId': playlist_id,
            'position': position,  # 0-based per API spec
            'resourceId': {
                'kind': 'youtube#video',
                'videoId': video_id
            }
        }

        content_details = {
            'videoId': video_id,
            'videoPublishedAt': None
        }

        return {
            'kind': 'youtube#playlistItem',
            'id': f"{playlist_id}_{video_id}",  # Composite ID
            'snippet': snippet,
            'contentDetails': content_details
        }

    @staticmethod
    def convert_api_v3_to_legacy(api_v3_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        YouTube API v3 형식을 기존 레거시 형식으로 변환합니다 (역방향 변환).

        주로 테스트와 호환성을 위한 유틸리티입니다.

        Args:
            api_v3_data: YouTube API v3 형식 데이터

        Returns:
            레거시 형식 딕셔너리
        """
        if api_v3_data.get('kind') == 'youtube#video':
            snippet = api_v3_data.get('snippet', {})
            content_details = api_v3_data.get('contentDetails', {})
            statistics = api_v3_data.get('statistics', {})

            # Convert publishedAt back to upload_date format
            upload_date = 'Unknown Date'
            if snippet.get('publishedAt'):
                try:
                    dt = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                    upload_date = dt.strftime('%Y%m%d')
                except:
                    pass

            # Convert duration back to seconds
            duration = 0
            if content_details.get('duration'):
                duration = YouTubeAPIMapper.parse_iso8601_duration(content_details['duration'])

            # Get thumbnail URL (prefer high quality)
            thumbnail_url = None
            thumbnails = snippet.get('thumbnails', {})
            for quality in ['maxres', 'standard', 'high', 'medium', 'default']:
                if quality in thumbnails and thumbnails[quality].get('url'):
                    thumbnail_url = thumbnails[quality]['url']
                    break

            return {
                'video_id': api_v3_data.get('id', ''),
                'title': snippet.get('title', 'Unknown Title'),
                'description': snippet.get('description', 'No description available'),
                'channel': snippet.get('channelTitle', 'Unknown Channel'),
                'upload_date': upload_date,
                'duration': duration,
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)) if statistics.get('likeCount') else None,
                'thumbnail_url': thumbnail_url
            }

        return api_v3_data
