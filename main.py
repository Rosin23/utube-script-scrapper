#!/usr/bin/env python3
"""
YouTube Video Scraper with Multi-Format Support
유튜브 영상의 제목, 설명, 자막(타임스탬프 포함)을 추출하여 구조화된 파일로 저장합니다.
지원 형식: TXT, JSON, XML, Markdown
"""

import sys
import re
from youtube_api import extract_video_id, get_video_metadata, get_transcript_with_timestamps
from formatters import get_formatter, get_available_formatters


def display_banner():
    """프로그램 배너를 출력합니다."""
    print("=" * 80)
    print("YouTube Video Scraper with Multi-Format Support")
    print("=" * 80)
    print()


def get_youtube_url() -> str:
    """
    YouTube URL을 입력받습니다.

    Returns:
        YouTube URL

    Raises:
        SystemExit: URL이 입력되지 않은 경우
    """
    if len(sys.argv) > 1:
        youtube_url = sys.argv[1]
    else:
        youtube_url = input("YouTube URL을 입력하세요: ").strip()

    if not youtube_url:
        print("❌ 오류: URL이 입력되지 않았습니다.")
        sys.exit(1)

    return youtube_url


def get_format_choice() -> str:
    """
    출력 형식을 선택받습니다.

    Returns:
        형식 선택 (1-4)

    Raises:
        SystemExit: 잘못된 형식 선택
    """
    print("\n📄 출력 형식을 선택하세요:")

    # 사용 가능한 포맷터 표시
    formatters = get_available_formatters()
    for key, formatter in formatters.items():
        ext = formatter.get_extension().upper()
        name = formatter.get_name()
        if ext == "TXT":
            print(f"{key}. {ext:<4} - 구조화된 텍스트 파일")
        elif ext == "JSON":
            print(f"{key}. {ext:<4} - JSON 형식")
        elif ext == "XML":
            print(f"{key}. {ext:<4} - XML 형식")
        elif ext == "MD":
            print(f"{key}. {ext:<4} - Markdown 형식")
    print()

    # 명령줄 인자로 형식이 제공된 경우
    if len(sys.argv) > 2:
        format_choice = sys.argv[2]
    else:
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


def main():
    """메인 함수 - 전체 워크플로우를 오케스트레이션합니다."""

    # 1. 배너 출력
    display_banner()

    try:
        # 2. YouTube URL 입력
        youtube_url = get_youtube_url()

        # 3. 출력 형식 선택
        format_choice = get_format_choice()

        # 4. 포맷터 가져오기
        formatter = get_formatter(format_choice)
        print(f"\n✓ {formatter.get_name()} 형식이 선택되었습니다.")
        print()

        # 5. 비디오 ID 추출
        video_id = extract_video_id(youtube_url)
        if not video_id:
            print("❌ 오류: 유효한 YouTube URL이 아닙니다.")
            sys.exit(1)

        print(f"🔍 비디오 ID: {video_id}")
        print()

        # 6. 메타데이터 가져오기
        print("📥 비디오 정보를 가져오는 중...")
        metadata = get_video_metadata(youtube_url)
        print(f"✓ 제목: {metadata['title']}")
        print()

        # 7. 자막 가져오기
        print("📥 자막을 가져오는 중...")
        transcript = get_transcript_with_timestamps(video_id)

        if transcript:
            print(f"✓ {len(transcript)}개의 자막 항목을 찾았습니다.")
        else:
            print("⚠️  자막을 찾을 수 없습니다. 메타데이터만 저장됩니다.")
        print()

        # 8. 출력 파일명 생성
        output_file = generate_safe_filename(
            metadata['title'],
            video_id,
            formatter.get_extension()
        )

        # 9. 파일 생성
        print(f"💾 {formatter.get_name()} 파일을 생성하는 중...")
        formatter.save(metadata, transcript, output_file)

        # 10. 완료
        print()
        print("=" * 80)
        print("✅ 완료!")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
