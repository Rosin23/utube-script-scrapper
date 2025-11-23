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
            재생목록 정보 딕셔너리 (PlaylistInfo 스키마와 일치)
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

                # entries 안전 처리
                entries = info.get('entries', [])
                if entries is None:
                    entries = []
                elif not isinstance(entries, list):
                    # entries가 리스트가 아닌 경우 (드물지만 가능)
                    print(f"Unexpected entries type: {type(entries)}")
                    entries = []
                
                # video_count 계산 개선
                video_count = info.get('playlist_count')
                if video_count is None:
                    # entries에서 유효한 항목 수 계산
                    valid_entries = [e for e in entries if e is not None]
                    video_count = len(valid_entries)
                
                return {
                    'playlist_id': info.get('id', 'Unknown'),  # 필드명 변경
                    'title': info.get('title', 'Unknown Playlist'),
                    'uploader': info.get('uploader', 'Unknown Channel'),
                    'video_count': video_count,  # 개선된 계산
                    'description': info.get('description'),  # description 추가
                    'entries': entries  # 내부 사용용 (필요시)
                }

        except Exception as e:
            print(f"⚠️  재생목록 정보 추출 오류: {e}")
            return None

    @staticmethod
    def get_video_urls_from_playlist(url: str, playlist_info: Optional[Dict] = None) -> List[Dict[str, str]]:
        """
        재생목록에서 모든 비디오 URL을 추출합니다.
        """
        if playlist_info is None:
            playlist_info = PlaylistHandler.get_playlist_info(url)

        if not playlist_info:
            return []

        videos = []
        entries = playlist_info.get('entries', []) or []
        
        for position, entry in enumerate(entries):
            if not entry:  # None 체크
                continue
            
            video_id = None
            video_title = 'Unknown Title'
            video_url = None
            
            # entry 타입에 따라 처리
            if isinstance(entry, dict):
                # 딕셔너리인 경우 (일반적인 경우)
                video_id = entry.get('id')
                video_title = entry.get('title', 'Unknown Title')
                # URL이 있으면 사용, 없으면 생성
                video_url = entry.get('url') or (
                    f"https://www.youtube.com/watch?v={video_id}" if video_id else None
                )
            elif isinstance(entry, str):
                # 문자열인 경우 (URL 또는 video_id)
                # URL에서 video_id 추출 시도
                from youtube_api import extract_video_id
                video_id = extract_video_id(entry) or entry
                video_url = entry if entry.startswith('http') else f"https://www.youtube.com/watch?v={entry}"
                video_title = 'Unknown Title'  # URL만 있으면 제목을 알 수 없음
            else:
                # 예상치 못한 타입
                print(f"Unexpected entry type: {type(entry)}, value: {entry}")
                continue

            if video_id:
                videos.append({
                    'id': video_id,
                    'url': video_url or f"https://www.youtube.com/watch?v={video_id}",
                    'title': video_title,
                    'position': position  # 0-based position 추가 (API 문서와 일치)
                })

        return videos

    @staticmethod
    def get_playlist_metadata(url: str) -> Dict:
        """
        재생목록의 메타데이터를 간단히 가져옵니다.

        Args:
            url: YouTube 재생목록 URL

        Returns:
            재생목록 메타데이터 (PlaylistInfo 스키마와 호환)
        """
        playlist_info = PlaylistHandler.get_playlist_info(url)

        if not playlist_info:
            return {
                'playlist_id': 'Unknown',
                'title': 'Unknown Playlist',
                'uploader': 'Unknown Channel',
                'video_count': 0,
                'description': None
            }

        return {
            'playlist_id': playlist_info.get('playlist_id', 'Unknown'),
            'title': playlist_info.get('title', 'Unknown Playlist'),
            'uploader': playlist_info.get('uploader', 'Unknown Channel'),
            'video_count': playlist_info.get('video_count', 0),
            'description': playlist_info.get('description')
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
        # 한 번만 호출하여 재사용
        playlist_info = handler.get_playlist_info(url)
        
        if not playlist_info:
            return {
                'type': 'unknown',
                'videos': [],
                'playlist_info': None
            }
        
        # 가져온 정보를 재사용하여 비디오 목록 추출
        videos = handler.get_video_urls_from_playlist(url, playlist_info=playlist_info)
        
        # 메타데이터는 이미 가져온 정보에서 생성
        playlist_metadata = {
            'playlist_id': playlist_info.get('playlist_id', 'Unknown'),
            'title': playlist_info.get('title', 'Unknown Playlist'),
            'uploader': playlist_info.get('uploader', 'Unknown Channel'),
            'video_count': playlist_info.get('video_count', 0),
            'description': playlist_info.get('description')
        }

        return {
            'type': 'playlist',
            'videos': videos,
            'playlist_info': playlist_metadata
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
                    'title': 'Video'
                }],
                'playlist_info': None
            }
        else:
            return {
                'type': 'unknown',
                'videos': [],
                'playlist_info': None
            }
