# YouTube Scraper with Timestamps

YouTube 비디오의 제목, 설명, 자막(타임스탬프 포함)을 추출하여 구조화된 파일로 저장하는 Python 스크립트입니다.

## 기능

- YouTube 비디오 메타데이터 추출 (제목, 채널명, 업로드 날짜, 조회수 등)
- 비디오 설명(Description) 추출
- 자막/스크립트 추출 (타임스탬프 포함)
- **다중 출력 형식 지원**:
  - **TXT** - 구조화된 텍스트 파일
  - **JSON** - 프로그래밍 친화적인 JSON 형식
  - **XML** - 구조화된 XML 형식
  - **Markdown** - 가독성 높은 마크다운 형식
- 한국어 및 영어 자막 자동 감지
- 수동 생성 자막 우선 사용, 없을 경우 자동 생성 자막 사용

## 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/Rosin23/utube-script-scrapper.git

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

### 방법 1: 대화형 모드 (권장)

```bash
python Utube_scrapper.py
```

실행 후 프롬프트에서:
1. YouTube URL 입력
2. 출력 형식 선택 (1-4)

### 방법 2: 명령줄 인자로 전달

```bash
# URL만 전달 (형식은 대화형으로 선택)
python Utube_scrapper.py "https://www.youtube.com/watch?v=VIDEO_ID"

# URL과 형식 모두 전달
python Utube_scrapper.py "https://www.youtube.com/watch?v=VIDEO_ID" 1  # TXT
python Utube_scrapper.py "https://www.youtube.com/watch?v=VIDEO_ID" 2  # JSON
python Utube_scrapper.py "https://www.youtube.com/watch?v=VIDEO_ID" 3  # XML
python Utube_scrapper.py "https://www.youtube.com/watch?v=VIDEO_ID" 4  # MD
```

## 사용 예시

```bash
# 예시 1: 대화형 모드로 실행
python Utube_scrapper.py
# → YouTube URL 입력: https://www.youtube.com/watch?v=dQw4w9WgXcQ
# → 출력 형식 선택: 2 (JSON)

# 예시 2: URL만 전달
python Utube_scrapper.py "https://youtu.be/dQw4w9WgXcQ"
# → 출력 형식 선택: 1 (TXT)

# 예시 3: URL과 형식 모두 전달
python Utube_scrapper.py "https://youtu.be/dQw4w9WgXcQ" 3
# → XML 파일 생성
```

## 출력 파일 형식

### 1. TXT 형식 (구조화된 텍스트)

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
```

### 2. JSON 형식

```json
{
  "video_info": {
    "title": "비디오 제목",
    "channel": "채널명",
    "upload_date": "20240101",
    "duration": 630,
    "duration_formatted": "10:30",
    "view_count": 1234567
  },
  "description": "비디오 설명 내용...",
  "transcript": [
    {
      "timestamp": "00:00",
      "start_seconds": 0.0,
      "duration": 2.5,
      "text": "첫 번째 자막 내용"
    }
  ],
  "metadata": {
    "total_entries": 150,
    "generated_at": "2024-01-01 12:00:00"
  }
}
```

### 3. XML 형식

```xml
<?xml version='1.0' encoding='utf-8'?>
<youtube_transcript>
  <video_info>
    <title>비디오 제목</title>
    <channel>채널명</channel>
    <upload_date>20240101</upload_date>
    <duration>630</duration>
    <duration_formatted>10:30</duration_formatted>
    <view_count>1234567</view_count>
  </video_info>
  <description>비디오 설명 내용...</description>
  <transcript>
    <entry>
      <timestamp>00:00</timestamp>
      <start_seconds>0.0</start_seconds>
      <duration>2.5</duration>
      <text>첫 번째 자막 내용</text>
    </entry>
  </transcript>
  <metadata>
    <total_entries>150</total_entries>
    <generated_at>2024-01-01 12:00:00</generated_at>
  </metadata>
</youtube_transcript>
```

### 4. Markdown 형식

```markdown
# 비디오 제목

## 📹 Video Information

- **Title**: 비디오 제목
- **Channel**: 채널명
- **Upload Date**: 20240101
- **Duration**: 10:30
- **Views**: 1,234,567

## 📝 Description

비디오 설명 내용...

## 📜 Transcript

| Timestamp | Text |
|-----------|------|
| `00:00` | 첫 번째 자막 내용 |
| `00:15` | 두 번째 자막 내용 |
| `01:30` | 세 번째 자막 내용 |
```

## 출력 파일명

출력 파일은 다음과 같은 형식으로 자동 생성됩니다:
```
{비디오_제목}_{비디오_ID}.{확장자}
```

예시:
- `My_Awesome_Video_dQw4w9WgXcQ.txt`
- `My_Awesome_Video_dQw4w9WgXcQ.json`
- `My_Awesome_Video_dQw4w9WgXcQ.xml`
- `My_Awesome_Video_dQw4w9WgXcQ.md`

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

## 요구사항

- Python 3.7 이상
- 인터넷 연결

## 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제공됩니다.

## 주의사항

- YouTube의 이용 약관을 준수하여 사용하세요.
- 저작권이 있는 콘텐츠를 무단으로 배포하지 마세요.
- API 사용 제한이 있을 수 있습니다.
