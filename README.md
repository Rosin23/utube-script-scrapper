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

## 프로젝트 구조

```
utube-script-scrapper/
├── main.py                 # 메인 실행 파일 (워크플로우 오케스트레이션)
├── youtube_api.py          # YouTube API 연동 모듈
├── formatters.py           # 출력 포맷터 모듈 (전략 패턴)
├── Utube_scrapper.py       # 레거시 호환용 (하위 호환성 유지)
├── requirements.txt        # 의존성 패키지 목록
├── pytest.ini              # pytest 설정 파일
├── tests/                  # 단위 테스트 디렉토리
│   ├── __init__.py
│   ├── test_youtube_api.py
│   └── test_formatters.py
└── README.md
```

### 아키텍처 특징

- **모듈화**: 각 모듈이 단일 책임을 가지도록 설계
- **전략 패턴**: 출력 포맷터를 쉽게 추가/변경 가능
- **테스트 커버리지**: pytest를 사용한 포괄적인 단위 테스트
- **확장성**: 새로운 출력 형식 추가가 용이

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
# 핵심 의존성
pip install yt-dlp youtube-transcript-api

# 테스트 의존성 (개발자용)
pip install pytest pytest-mock pytest-cov
```

## 사용 방법

### 방법 1: 대화형 모드 (권장)

```bash
python main.py
```

실행 후 프롬프트에서:
1. YouTube URL 입력
2. 출력 형식 선택 (1-4)

### 방법 2: 명령줄 인자로 전달

```bash
# URL만 전달 (형식은 대화형으로 선택)
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"

# URL과 형식 모두 전달
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" 1  # TXT
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" 2  # JSON
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" 3  # XML
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" 4  # MD
```

### 방법 3: 레거시 스크립트 사용 (하위 호환성)

```bash
python Utube_scrapper.py "https://www.youtube.com/watch?v=VIDEO_ID" 1
```

## 사용 예시

```bash
# 예시 1: 대화형 모드로 실행
python main.py
# → YouTube URL 입력: https://www.youtube.com/watch?v=dQw4w9WgXcQ
# → 출력 형식 선택: 2 (JSON)

# 예시 2: URL만 전달
python main.py "https://youtu.be/dQw4w9WgXcQ"
# → 출력 형식 선택: 1 (TXT)

# 예시 3: URL과 형식 모두 전달
python main.py "https://youtu.be/dQw4w9WgXcQ" 3
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

## 테스트

이 프로젝트는 pytest를 사용한 포괄적인 단위 테스트를 포함합니다.

### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 상세한 출력과 함께 실행
pytest -v

# 커버리지 리포트와 함께 실행
pytest --cov=. --cov-report=html

# 특정 테스트 파일만 실행
pytest tests/test_youtube_api.py
pytest tests/test_formatters.py
```

### 테스트 구조

- `tests/test_youtube_api.py`: YouTube API 모듈 테스트
  - URL에서 비디오 ID 추출 테스트
  - 타임스탬프 형식 변환 테스트
  - 메타데이터 추출 테스트 (모킹 사용)
  - 자막 추출 테스트 (모킹 사용)

- `tests/test_formatters.py`: 포맷터 모듈 테스트
  - 각 포맷터의 초기화 테스트
  - 파일 생성 및 구조 검증 테스트
  - 유효한 출력 형식 생성 테스트
  - 포맷터 팩토리 함수 테스트

## 개발자 가이드

### 새로운 출력 형식 추가하기

전략 패턴 덕분에 새로운 출력 형식을 쉽게 추가할 수 있습니다:

1. `formatters.py`에 새 포맷터 클래스 생성:
```python
class SrtFormatter(Formatter):
    def __init__(self):
        super().__init__()
        self.file_extension = "srt"
        self.format_name = "SRT 자막"

    def save(self, metadata, transcript, output_file):
        # SRT 형식으로 저장하는 로직 구현
        pass
```

2. `get_available_formatters()` 함수에 추가:
```python
'5': SrtFormatter()
```

3. 테스트 작성:
```python
# tests/test_formatters.py에 테스트 추가
class TestSrtFormatter:
    def test_initialization(self):
        formatter = SrtFormatter()
        assert formatter.get_extension() == "srt"
```

## 요구사항

- Python 3.7 이상
- 인터넷 연결

## 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제공됩니다.

## 주의사항

- YouTube의 이용 약관을 준수하여 사용하세요.
- 저작권이 있는 콘텐츠를 무단으로 배포하지 마세요.
- API 사용 제한이 있을 수 있습니다.
