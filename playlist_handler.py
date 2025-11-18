"""
재생목록 핸들러 모듈
YouTube 재생목록 감지 및 처리 기능을 제공합니다.
"""

import re
from typing import Optional, List, Dict
import yt_dlp


class PlaylistHandler:
    """YouTube 재생목록 처리 클래스"""

    @staticmethod
    def is_playlist_url(url: str) -> bool:
        """
        URL이 재생목록 URL인지 확인합니다.

        Args:
            url: YouTube URL

        Returns:
            재생목록 URL이면 True, 아니면 False
        """
        playlist_patterns = [
            r'[?&]list=([^&]+)',  # ?list=PLxxx 또는 &list=PLxxx
            r'/playlist\?',       # /playlist?
        ]

        for pattern in playlist_patterns:
            if re.search(pattern, url):
                return True

        return False

    @staticmethod
    def extract_playlist_id(url: str) -> Optional[str]:
        """
        URL에서 재생목록 ID를 추출합니다.

        Args:
            url: YouTube 재생목록 URL

        Returns:
            재생목록 ID 또는 None
        """
        match = re.search(r'[?&]list=([^&]+)', url)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def get_playlist_info(url: str) -> Optional[Dict]:
        """
        재생목록의 정보를 가져옵니다.

        Args:
            url: YouTube 재생목록 URL

        Returns:
            재생목록 정보 딕셔너리 또는 None
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # 메타데이터만 추출 (비디오 다운로드 X)
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if info.get('_type') != 'playlist':
                    return None

                return {
                    'id': info.get('id', 'Unknown'),
                    'title': info.get('title', 'Unknown Playlist'),
                    'uploader': info.get('uploader', 'Unknown Channel'),
                    'video_count': len(info.get('entries', [])),
                    'entries': info.get('entries', [])
                }

        except Exception as e:
            print(f"⚠️  재생목록 정보 추출 오류: {e}")
            return None

    @staticmethod
    def get_video_urls_from_playlist(url: str) -> List[Dict[str, str]]:
        """
        재생목록에서 모든 비디오 URL을 추출합니다.

        Args:
            url: YouTube 재생목록 URL

        Returns:
            비디오 정보 리스트 (각 항목은 {'id', 'url', 'title'} 포함)
        """
        playlist_info = PlaylistHandler.get_playlist_info(url)

        if not playlist_info:
            return []

        videos = []
        for entry in playlist_info['entries']:
            if entry:  # None이 아닌 경우만
                video_id = entry.get('id')
                video_title = entry.get('title', 'Unknown Title')

                if video_id:
                    videos.append({
                        'id': video_id,
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'title': video_title
                    })

        return videos

    @staticmethod
    def get_playlist_metadata(url: str) -> Dict:
        """
        재생목록의 메타데이터를 간단히 가져옵니다.

        Args:
            url: YouTube 재생목록 URL

        Returns:
            재생목록 메타데이터
        """
        playlist_info = PlaylistHandler.get_playlist_info(url)

        if not playlist_info:
            return {
                'title': 'Unknown Playlist',
                'uploader': 'Unknown Channel',
                'video_count': 0
            }

        return {
            'title': playlist_info['title'],
            'uploader': playlist_info['uploader'],
            'video_count': playlist_info['video_count']
        }


def process_playlist_or_video(url: str) -> Dict:
    """
    URL이 재생목록인지 단일 비디오인지 확인하고 처리합니다.

    Args:
        url: YouTube URL

    Returns:
        처리 결과 딕셔너리 {
            'type': 'playlist' 또는 'video',
            'videos': 비디오 정보 리스트,
            'playlist_info': 재생목록 정보 (재생목록인 경우만)
        }
    """
    handler = PlaylistHandler()

    if handler.is_playlist_url(url):
        videos = handler.get_video_urls_from_playlist(url)
        playlist_info = handler.get_playlist_metadata(url)

        return {
            'type': 'playlist',
            'videos': videos,
            'playlist_info': playlist_info
        }
    else:
        # 단일 비디오
        from youtube_api import extract_video_id

        video_id = extract_video_id(url)
        if video_id:
            return {
                'type': 'video',
                'videos': [{
                    'id': video_id,
                    'url': url,
                    'title': 'Video'  # 실제 제목은 나중에 메타데이터에서 가져옴
                }],
                'playlist_info': None
            }
        else:
            return {
                'type': 'unknown',
                'videos': [],
                'playlist_info': None
            }
