#!/usr/bin/env python3
"""
YouTube Video Scraper with Multi-Format Support
유튜브 영상의 제목, 설명, 자막(타임스탬프 포함)을 추출하여 구조화된 파일로 저장합니다.
지원 형식: TXT, JSON, XML, Markdown
Phase 2: 재생목록 지원, AI 요약, 다국어 지원
"""

import sys
import re
import argparse
from typing import Optional, List
from youtube_api import extract_video_id, get_video_metadata, get_transcript_with_timestamps
from formatters import get_formatter, get_available_formatters
from playlist_handler import process_playlist_or_video
from gemini_api import GeminiClient, is_gemini_available


def display_banner():
    """프로그램 배너를 출력합니다."""
    print("=" * 80)
    print("YouTube Video Scraper with AI Enhancement (Phase 2)")
    print("=" * 80)
    print()


def parse_arguments():
    """
    명령줄 인자를 파싱합니다.

    Returns:
        파싱된 인자 객체
    """
    parser = argparse.ArgumentParser(
        description='YouTube 비디오/재생목록 스크래퍼 with AI 요약 및 번역',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 단일 비디오 스크래핑
  python main.py https://www.youtube.com/watch?v=VIDEO_ID

  # 재생목록 스크래핑
  python main.py https://www.youtube.com/playlist?list=PLAYLIST_ID

  # AI 요약 포함
  python main.py VIDEO_URL --summary

  # 번역 포함 (영어로)
  python main.py VIDEO_URL --translate en

  # 언어 지정
  python main.py VIDEO_URL --lang ko en

  # 모든 기능 사용
  python main.py VIDEO_URL --summary --translate en --topics 5 --format 2
        """
    )

    parser.add_argument(
        'url',
        nargs='?',
        help='YouTube 비디오 또는 재생목록 URL'
    )

    parser.add_argument(
        'format_choice',
        nargs='?',
        help='출력 형식 (1: TXT, 2: JSON, 3: XML, 4: Markdown)'
    )

    parser.add_argument(
        '--lang',
        nargs='+',
        default=['ko', 'en'],
        help='자막 언어 우선순위 (기본값: ko en)'
    )

    parser.add_argument(
        '--summary',
        action='store_true',
        help='Gemini API를 사용한 AI 요약 생성'
    )

    parser.add_argument(
        '--translate',
        metavar='LANG',
        help='자막을 지정된 언어로 번역 (예: en, ja, zh)'
    )

    parser.add_argument(
        '--topics',
        type=int,
        metavar='N',
        help='핵심 주제 N개 추출'
    )

    parser.add_argument(
        '--format',
        dest='format_flag',
        type=str,
        choices=['1', '2', '3', '4'],
        help='출력 형식 (1: TXT, 2: JSON, 3: XML, 4: Markdown)'
    )

    parser.add_argument(
        '--max-videos',
        type=int,
        default=None,
        metavar='N',
        help='재생목록에서 처리할 최대 비디오 수 (기본값: 전체)'
    )

    return parser.parse_args()


def get_youtube_url(args) -> str:
    """
    YouTube URL을 입력받습니다.

    Args:
        args: 파싱된 명령줄 인자

    Returns:
        YouTube URL

    Raises:
        SystemExit: URL이 입력되지 않은 경우
    """
    if args.url:
        youtube_url = args.url
    else:
        youtube_url = input("YouTube URL을 입력하세요 (비디오 또는 재생목록): ").strip()

    if not youtube_url:
        print("❌ 오류: URL이 입력되지 않았습니다.")
        sys.exit(1)

    return youtube_url


def get_format_choice(args) -> str:
    """
    출력 형식을 선택받습니다.

    Args:
        args: 파싱된 명령줄 인자

    Returns:
        형식 선택 (1-4)

    Raises:
        SystemExit: 잘못된 형식 선택
    """
    # --format 플래그가 있으면 우선 사용
    if args.format_flag:
        return args.format_flag

    # 위치 인자로 제공된 경우
    if args.format_choice:
        return args.format_choice

    # 대화형 모드
    print("\n📄 출력 형식을 선택하세요:")
    formatters = get_available_formatters()
    for key, formatter in formatters.items():
        ext = formatter.get_extension().upper()
        if ext == "TXT":
            print(f"{key}. {ext:<4} - 구조화된 텍스트 파일")
        elif ext == "JSON":
            print(f"{key}. {ext:<4} - JSON 형식")
        elif ext == "XML":
            print(f"{key}. {ext:<4} - XML 형식")
        elif ext == "MD":
            print(f"{key}. {ext:<4} - Markdown 형식")
    print()

    format_choice = input("선택 (1-4): ").strip()

    # 유효성 검증
    if format_choice not in formatters:
        print("❌ 오류: 올바른 형식을 선택해주세요 (1-4).")
        sys.exit(1)

    return format_choice


def generate_safe_filename(title: str, video_id: str, extension: str) -> str:
    """
    안전한 파일명을 생성합니다.

    Args:
        title: 비디오 제목
        video_id: 비디오 ID
        extension: 파일 확장자

    Returns:
        안전한 파일명
    """
    safe_title = re.sub(r'[^\w\s-]', '', title)
    safe_title = re.sub(r'[-\s]+', '_', safe_title)
    return f"{safe_title[:50]}_{video_id}.{extension}"


def process_single_video(
    video_url: str,
    video_id: str,
    formatter,
    args,
    gemini_client: Optional[GeminiClient] = None,
    video_index: Optional[int] = None,
    total_videos: Optional[int] = None
) -> bool:
    """
    단일 비디오를 처리합니다.

    Args:
        video_url: 비디오 URL
        video_id: 비디오 ID
        formatter: 포맷터 객체
        args: 명령줄 인자
        gemini_client: Gemini API 클라이언트 (선택사항)
        video_index: 재생목록 내 비디오 인덱스 (선택사항)
        total_videos: 전체 비디오 수 (선택사항)

    Returns:
        성공 여부
    """
    try:
        # 진행 상황 표시 (재생목록인 경우)
        if video_index is not None and total_videos is not None:
            print(f"\n{'='*80}")
            print(f"비디오 {video_index}/{total_videos} 처리 중...")
            print(f"{'='*80}")

        # 메타데이터 가져오기
        print(f"📥 비디오 정보를 가져오는 중... (ID: {video_id})")
        metadata = get_video_metadata(video_url)
        print(f"✓ 제목: {metadata['title']}")
        print()

        # 자막 가져오기
        print("📥 자막을 가져오는 중...")
        transcript = get_transcript_with_timestamps(video_id, languages=args.lang)

        if transcript:
            print(f"✓ {len(transcript)}개의 자막 항목을 찾았습니다.")
        else:
            print("⚠️  자막을 찾을 수 없습니다. 메타데이터만 저장됩니다.")
        print()

        # AI 기능 처리
        summary = None
        translation = None
        key_topics = None

        if gemini_client and transcript:
            # 요약 생성
            if args.summary:
                print("🤖 AI 요약을 생성하는 중...")
                summary = gemini_client.generate_summary(
                    transcript,
                    max_points=5,
                    language=args.lang[0] if args.lang else 'ko'
                )
                if summary:
                    print("✓ 요약이 생성되었습니다.")
                else:
                    print("⚠️  요약 생성에 실패했습니다.")
                print()

            # 번역
            if args.translate:
                print(f"🌐 {args.translate}로 번역하는 중...")
                translation = gemini_client.translate_transcript(
                    transcript,
                    target_language=args.translate
                )
                if translation:
                    print("✓ 번역이 완료되었습니다.")
                else:
                    print("⚠️  번역에 실패했습니다.")
                print()

            # 핵심 주제 추출
            if args.topics:
                print(f"🔑 핵심 주제 {args.topics}개를 추출하는 중...")
                key_topics = gemini_client.extract_key_topics(
                    transcript,
                    num_topics=args.topics,
                    language=args.lang[0] if args.lang else 'ko'
                )
                if key_topics:
                    print(f"✓ {len(key_topics)}개의 주제가 추출되었습니다.")
                else:
                    print("⚠️  주제 추출에 실패했습니다.")
                print()

        # 출력 파일명 생성
        output_file = generate_safe_filename(
            metadata['title'],
            video_id,
            formatter.get_extension()
        )

        # 파일 생성
        print(f"💾 {formatter.get_name()} 파일을 생성하는 중...")
        formatter.save(
            metadata,
            transcript,
            output_file,
            summary=summary,
            translation=translation,
            key_topics=key_topics
        )

        return True

    except Exception as e:
        print(f"\n❌ 비디오 처리 오류 (ID: {video_id}): {e}")
        return False


def main():
    """메인 함수 - 전체 워크플로우를 오케스트레이션합니다."""

    # 1. 배너 출력
    display_banner()

    try:
        # 2. 명령줄 인자 파싱
        args = parse_arguments()

        # 3. YouTube URL 입력
        youtube_url = get_youtube_url(args)

        # 4. 출력 형식 선택
        format_choice = get_format_choice(args)
        formatter = get_formatter(format_choice)
        print(f"\n✓ {formatter.get_name()} 형식이 선택되었습니다.")
        print()

        # 5. Gemini API 클라이언트 초기화 (필요한 경우)
        gemini_client = None
        if args.summary or args.translate or args.topics:
            if is_gemini_available():
                try:
                    gemini_client = GeminiClient()
                    print("✓ Gemini API가 활성화되었습니다.")
                    print()
                except Exception as e:
                    print(f"⚠️  Gemini API 초기화 실패: {e}")
                    print("   AI 기능이 비활성화됩니다.")
                    print()
            else:
                print("⚠️  GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
                print("   AI 기능을 사용하려면 API 키를 설정하세요.")
                print()

        # 6. 재생목록 또는 단일 비디오 확인
        print("🔍 URL 분석 중...")
        result = process_playlist_or_video(youtube_url)

        if result['type'] == 'playlist':
            # 재생목록 처리
            playlist_info = result['playlist_info']
            videos = result['videos']

            print(f"\n✓ 재생목록이 감지되었습니다!")
            print(f"   제목: {playlist_info['title']}")
            print(f"   채널: {playlist_info['uploader']}")
            print(f"   비디오 수: {playlist_info['video_count']}")
            print()

            # 최대 비디오 수 제한
            if args.max_videos and args.max_videos < len(videos):
                videos = videos[:args.max_videos]
                print(f"⚠️  처리할 비디오를 {args.max_videos}개로 제한합니다.")
                print()

            # 각 비디오 처리
            success_count = 0
            for i, video in enumerate(videos, 1):
                success = process_single_video(
                    video['url'],
                    video['id'],
                    formatter,
                    args,
                    gemini_client,
                    video_index=i,
                    total_videos=len(videos)
                )
                if success:
                    success_count += 1

            # 재생목록 처리 결과
            print("\n" + "=" * 80)
            print("✅ 재생목록 처리 완료!")
            print(f"   성공: {success_count}/{len(videos)}")
            print("=" * 80)

        elif result['type'] == 'video':
            # 단일 비디오 처리
            video = result['videos'][0]
            print(f"\n✓ 단일 비디오가 감지되었습니다.")
            print(f"   비디오 ID: {video['id']}")
            print()

            success = process_single_video(
                video['url'],
                video['id'],
                formatter,
                args,
                gemini_client
            )

            if success:
                print()
                print("=" * 80)
                print("✅ 완료!")
                print("=" * 80)
            else:
                sys.exit(1)

        else:
            print("❌ 오류: 유효한 YouTube URL이 아닙니다.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
