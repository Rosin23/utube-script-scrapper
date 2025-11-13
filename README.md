# YouTube Scraper with Timestamps

YouTube 비디오의 제목, 설명, 자막(타임스탬프 포함)을 추출하여 구조화된 텍스트 파일로 저장하는 Python 스크립트입니다.

## 기능

- YouTube 비디오 메타데이터 추출 (제목, 채널명, 업로드 날짜, 조회수 등)
- 비디오 설명(Description) 추출
- 자막/스크립트 추출 (타임스탬프 포함)
- 구조화된 텍스트 파일(.txt) 생성
- 한국어 및 영어 자막 자동 감지
- 수동 생성 자막 우선 사용, 없을 경우 자동 생성 자막 사용

## 설치 방법

### 1. 저장소 클론

```bash
git clone <repository-url>
cd utube-script-scrapper
```

### 2. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

또는 개별적으로 설치:

```bash
pip install yt-dlp youtube-transcript-api
```

## 사용 방법

### 방법 1: 명령줄 인자로 URL 전달

```bash
python Utube_scrapper.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 방법 2: 대화형 모드

```bash
python Utube_scrapper.py
```

실행 후 프롬프트에서 YouTube URL을 입력합니다.

## 사용 예시

```bash
# 예시 1: 직접 URL 입력
python Utube_scrapper.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 예시 2: 짧은 URL 형식
python Utube_scrapper.py "https://youtu.be/dQw4w9WgXcQ"
```

## 출력 파일 형식

스크립트는 다음과 같은 구조의 텍스트 파일을 생성합니다:

```
================================================================================
YouTube Video Transcript
================================================================================

📹 Video Information
--------------------------------------------------------------------------------
Title: 비디오 제목
Channel: 채널명
Upload Date: 20240101
Duration: 10:30
Views: 1,234,567

📝 Description
--------------------------------------------------------------------------------
비디오 설명 내용...

📜 Transcript with Timestamps
================================================================================

[00:00] 첫 번째 자막 내용
[00:15] 두 번째 자막 내용
[01:30] 세 번째 자막 내용
...

================================================================================
Total transcript entries: 150

Generated on: 2024-01-01 12:00:00
```

## 출력 파일명

출력 파일은 다음과 같은 형식으로 자동 생성됩니다:
```
{비디오_제목}_{비디오_ID}.txt
```

예시: `My_Awesome_Video_dQw4w9WgXcQ.txt`

## 지원하는 URL 형식

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`

## 자막 언어 우선순위

1. 한국어 (ko) - 수동 생성 자막
2. 영어 (en) - 수동 생성 자막
3. 한국어 (ko) - 자동 생성 자막
4. 영어 (en) - 자동 생성 자막
5. 기타 사용 가능한 첫 번째 자막

## 문제 해결

### 자막이 추출되지 않는 경우

- 해당 비디오에 자막이 활성화되어 있는지 확인하세요.
- 일부 비디오는 자막이 제공되지 않을 수 있습니다.
- 이 경우에도 비디오 메타데이터는 정상적으로 저장됩니다.

### 네트워크 오류

- 인터넷 연결을 확인하세요.
- YouTube 서버가 일시적으로 응답하지 않을 수 있습니다. 잠시 후 다시 시도하세요.

### Python 버전

- Python 3.7 이상이 필요합니다.

## 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제공됩니다.

## 주의사항

- YouTube의 이용 약관을 준수하여 사용하세요.
- 저작권이 있는 콘텐츠를 무단으로 배포하지 마세요.
- API 사용 제한이 있을 수 있습니다.
