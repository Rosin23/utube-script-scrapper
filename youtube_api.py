"""
YouTube API 모듈
YouTube 비디오 메타데이터 및 자막 추출 기능을 제공합니다.
"""

import re
from typing import Optional, Dict, List
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> Optional[str]:
    """
    YouTube URL에서 비디오 ID를 추출합니다.

    Args:
        url: YouTube 비디오 URL

    Returns:
        비디오 ID 또는 None
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
        r'youtube\.com\/v\/([^&\n?#]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def format_timestamp(seconds: float) -> str:
    """
    초를 HH:MM:SS 형식으로 변환합니다.

    Args:
        seconds: 초 단위 시간

    Returns:
        HH:MM:SS 형식의 문자열
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def get_video_metadata(url: str) -> Dict[str, str]:
    """
    YouTube 비디오의 메타데이터를 가져옵니다.

    Args:
        url: YouTube 비디오 URL

    Returns:
        title, description, channel 등의 정보를 담은 딕셔너리
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            return {
                'title': info.get('title', 'Unknown Title'),
                'description': info.get('description', 'No description available'),
                'channel': info.get('channel', 'Unknown Channel'),
                'upload_date': info.get('upload_date', 'Unknown Date'),
                'duration': info.get('duration', 0),
                'view_count': info.get('view_count', 0),
            }
    except Exception as e:
        print(f"메타데이터 추출 오류: {e}")
        return {
            'title': 'Unknown Title',
            'description': 'No description available',
            'channel': 'Unknown Channel',
            'upload_date': 'Unknown Date',
            'duration': 0,
            'view_count': 0,
        }


def get_transcript_with_timestamps(video_id: str, languages: List[str] = ['ko', 'en']) -> List[Dict]:
    """
    YouTube 비디오의 자막을 타임스탬프와 함께 가져옵니다.
    youtube-transcript-api 0.x와 1.x 버전 모두 지원합니다.

    Args:
        video_id: YouTube 비디오 ID
        languages: 선호하는 언어 목록 (기본값: ['ko', 'en'])

    Returns:
        타임스탬프와 텍스트를 담은 딕셔너리 리스트
    """

    # 신버전 (1.x) API 사용 시도 - fetch() 인스턴스 메서드
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=languages)
        # FetchedTranscript 객체를 dict 리스트로 변환
        if hasattr(transcript, 'snippets'):
            return [{'start': s.start, 'duration': s.duration, 'text': s.text}
                   for s in transcript.snippets]
        # 이미 리스트 형태인 경우
        return transcript if isinstance(transcript, list) else []
    except AttributeError:
        # fetch 메서드가 없음 - 구버전 (0.x)일 가능성
        pass
    except Exception as e:
        # 다른 이유로 실패 (자막 없음, 네트워크 오류 등) - 계속 시도
        pass

    # 구버전 (0.x) API 사용 시도 - get_transcript() 정적 메서드
    # 방법 1: 선호하는 언어들을 한 번에 시도
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        return transcript
    except AttributeError:
        # get_transcript 메서드가 없음 - 신버전인데 위에서 실패한 경우
        pass
    except Exception:
        # 자막을 찾을 수 없거나 다른 오류
        pass

    # 방법 2: 각 언어를 개별적으로 시도 (구버전)
    if hasattr(YouTubeTranscriptApi, 'get_transcript'):
        for lang in languages:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                return transcript
            except Exception:
                continue

    # 방법 3: 언어 지정 없이 기본 자막 가져오기 시도 (구버전)
    if hasattr(YouTubeTranscriptApi, 'get_transcript'):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except Exception:
            pass

    # 방법 4: list() 메서드로 사용 가능한 자막 목록 확인 (신버전 1.x)
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        # 수동 생성 자막 우선 시도
        try:
            transcript = transcript_list.find_transcript(languages)
            result = transcript.fetch()
            if hasattr(result, 'snippets'):
                return [{'start': s.start, 'duration': s.duration, 'text': s.text}
                       for s in result.snippets]
            return result if isinstance(result, list) else []
        except:
            pass

        # 사용 가능한 첫 번째 자막 사용
        try:
            available = list(transcript_list)
            if available:
                result = available[0].fetch()
                if hasattr(result, 'snippets'):
                    return [{'start': s.start, 'duration': s.duration, 'text': s.text}
                           for s in result.snippets]
                return result if isinstance(result, list) else []
        except:
            pass
    except AttributeError:
        # list 메서드가 없음
        pass
    except Exception as e:
        print(f"자막 목록 조회 오류: {e}")

    # 방법 5: list_transcripts() 메서드 시도 (구버전 0.x)
    if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # 수동 생성 자막 우선 시도
            try:
                for lang in languages:
                    try:
                        transcript = transcript_list.find_manually_created_transcript([lang])
                        return transcript.fetch()
                    except:
                        continue
            except:
                pass

            # 자동 생성 자막 시도
            try:
                for lang in languages:
                    try:
                        transcript = transcript_list.find_generated_transcript([lang])
                        return transcript.fetch()
                    except:
                        continue
            except:
                pass

            # 사용 가능한 첫 번째 자막 사용
            try:
                available_transcripts = list(transcript_list)
                if available_transcripts:
                    return available_transcripts[0].fetch()
            except:
                pass
        except Exception as e:
            print(f"자막 추출 오류: {e}")

    print("이 비디오에 사용 가능한 자막이 없습니다.")
    return []
