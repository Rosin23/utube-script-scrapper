#!/usr/bin/env python3
"""
YouTube Video Scraper with Timestamps
유튜브 영상의 제목, 설명, 자막(타임스탬프 포함)을 추출하여 구조화된 텍스트 파일로 저장합니다.
"""

import sys
import re
from datetime import datetime
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


def create_structured_text(metadata: Dict, transcript: List[Dict], output_file: str):
    """
    구조화된 텍스트 파일을 생성합니다.

    Args:
        metadata: 비디오 메타데이터
        transcript: 타임스탬프가 포함된 자막 데이터
        output_file: 출력 파일 경로
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # 헤더
            f.write("=" * 80 + "\n")
            f.write("YouTube Video Transcript\n")
            f.write("=" * 80 + "\n\n")

            # 비디오 정보
            f.write("📹 Video Information\n")
            f.write("-" * 80 + "\n")
            f.write(f"Title: {metadata['title']}\n")
            f.write(f"Channel: {metadata['channel']}\n")
            f.write(f"Upload Date: {metadata['upload_date']}\n")
            f.write(f"Duration: {format_timestamp(metadata['duration'])}\n")
            f.write(f"Views: {metadata['view_count']:,}\n")
            f.write("\n")

            # 설명
            f.write("📝 Description\n")
            f.write("-" * 80 + "\n")
            f.write(f"{metadata['description']}\n")
            f.write("\n")

            # 자막 (타임스탬프 포함)
            if transcript:
                f.write("📜 Transcript with Timestamps\n")
                f.write("=" * 80 + "\n\n")

                for entry in transcript:
                    timestamp = format_timestamp(entry['start'])
                    text = entry['text'].strip()
                    f.write(f"[{timestamp}] {text}\n")

                f.write("\n")
                f.write("=" * 80 + "\n")
                f.write(f"Total transcript entries: {len(transcript)}\n")
            else:
                f.write("📜 Transcript\n")
                f.write("=" * 80 + "\n")
                f.write("No transcript available for this video.\n")

            f.write(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print(f"\n✅ 파일이 성공적으로 생성되었습니다: {output_file}")

    except Exception as e:
        print(f"파일 생성 오류: {e}")
        sys.exit(1)


def main():
    """
    메인 함수
    """
    print("=" * 80)
    print("YouTube Video Scraper with Timestamps")
    print("=" * 80)
    print()

    # YouTube URL 입력
    if len(sys.argv) > 1:
        youtube_url = sys.argv[1]
    else:
        youtube_url = input("YouTube URL을 입력하세요: ").strip()

    if not youtube_url:
        print("❌ 오류: URL이 입력되지 않았습니다.")
        sys.exit(1)

    # 비디오 ID 추출
    video_id = extract_video_id(youtube_url)
    if not video_id:
        print("❌ 오류: 유효한 YouTube URL이 아닙니다.")
        sys.exit(1)

    print(f"🔍 비디오 ID: {video_id}")
    print()

    # 메타데이터 가져오기
    print("📥 비디오 정보를 가져오는 중...")
    metadata = get_video_metadata(youtube_url)
    print(f"✓ 제목: {metadata['title']}")
    print()

    # 자막 가져오기
    print("📥 자막을 가져오는 중...")
    transcript = get_transcript_with_timestamps(video_id)

    if transcript:
        print(f"✓ {len(transcript)}개의 자막 항목을 찾았습니다.")
    else:
        print("⚠️  자막을 찾을 수 없습니다. 메타데이터만 저장됩니다.")
    print()

    # 출력 파일명 생성
    safe_title = re.sub(r'[^\w\s-]', '', metadata['title'])
    safe_title = re.sub(r'[-\s]+', '_', safe_title)
    output_file = f"{safe_title[:50]}_{video_id}.txt"

    # 파일 생성
    print("💾 텍스트 파일을 생성하는 중...")
    create_structured_text(metadata, transcript, output_file)
    print()
    print("=" * 80)
    print("✅ 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()
