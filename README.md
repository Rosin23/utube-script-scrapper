# YouTube Scraper with Timestamps & AI Enhancement (Phase 2)

YouTube 비디오/재생목록의 제목, 설명, 자막(타임스탬프 포함)을 추출하여 구조화된 파일로 저장하는 Python 스크립트입니다.

## 새로운 기능 (Phase 2) 🚀

- **🎬 재생목록 지원**: 재생목록 URL을 입력하면 모든 비디오를 자동으로 처리
- **🤖 AI 요약**: Gemini API를 활용한 자동 스크립트 요약
- **🌐 다국어 번역**: AI 기반 자막 번역
- **🔑 핵심 주제 추출**: 비디오의 주요 토픽 자동 추출
- **🌍 다국어 자막 지원**: 사용자 지정 언어 우선순위 설정

## 기능

### 기본 기능
- YouTube 비디오 메타데이터 추출 (제목, 채널명, 업로드 날짜, 조회수 등)
- 비디오 설명(Description) 추출
- 자막/스크립트 추출 (타임스탬프 포함)
- **다중 출력 형식 지원**:
  - **TXT** - 구조화된 텍스트 파일
  - **JSON** - 프로그래밍 친화적인 JSON 형식
  - **XML** - 구조화된 XML 형식
  - **Markdown** - 가독성 높은 마크다운 형식

### Phase 2 고급 기능
- **재생목록 처리**: URL이 재생목록이면 모든 비디오를 순차 처리
- **AI 요약**: Gemini API로 비디오 내용을 핵심 포인트로 요약
- **번역**: 자막을 다른 언어로 자동 번역
- **주제 추출**: 비디오의 핵심 주제 자동 추출
- **사용자 지정 언어**: 선호하는 자막 언어 우선순위 설정

## 프로젝트 구조

```
utube-script-scrapper/
├── main.py                      # 메인 실행 파일 (Phase 2 통합)
├── youtube_api.py               # YouTube API 연동 모듈
├── formatters.py                # 출력 포맷터 모듈 (전략 패턴)
├── playlist_handler.py          # 재생목록 처리 모듈 (NEW)
├── gemini_api.py                # Gemini API 연동 모듈 (NEW)
├── Utube_scrapper.py            # 레거시 호환용
├── requirements.txt             # 의존성 패키지 목록
├── pytest.ini                   # pytest 설정 파일
├── tests/                       # 단위 테스트 디렉토리
│   ├── __init__.py
│   ├── test_youtube_api.py
│   ├── test_formatters.py
│   ├── test_playlist_handler.py # NEW
│   └── test_gemini_api.py       # NEW
└── README.md
```

### 아키텍처 특징

- **모듈화**: 각 모듈이 단일 책임을 가지도록 설계 (SRP)
- **전략 패턴**: 출력 포맷터를 쉽게 추가/변경 가능
- **의존성 주입**: 느슨한 결합으로 테스트와 확장 용이
- **테스트 커버리지**: pytest를 사용한 포괄적인 단위 테스트
- **확장성**: 새로운 기능 추가가 용이한 구조

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

# AI 기능 (선택사항)
pip install google-generativeai

# 테스트 의존성 (개발자용)
pip install pytest pytest-mock pytest-cov
```

### 3. Gemini API 설정 (AI 기능 사용 시)

AI 요약, 번역, 주제 추출 기능을 사용하려면 Gemini API 키가 필요합니다.

1. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 API 키 발급
2. 환경변수 설정:

```bash
# Linux/Mac
export GEMINI_API_KEY="your-api-key-here"

# Windows (PowerShell)
$env:GEMINI_API_KEY="your-api-key-here"

# Windows (CMD)
set GEMINI_API_KEY=your-api-key-here
```

또는 `.bashrc`, `.zshrc` 등에 추가하여 영구 설정:

```bash
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## 사용 방법

### 방법 1: 기본 사용 (단일 비디오)

```bash
# 대화형 모드
python main.py

# URL과 함께 실행
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"

# 출력 형식까지 지정
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --format 2
```

### 방법 2: 재생목록 처리

```bash
# 재생목록 전체 처리
python main.py "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# 처리할 비디오 수 제한 (처음 5개만)
python main.py "PLAYLIST_URL" --max-videos 5
```

### 방법 3: AI 기능 사용

```bash
# AI 요약 생성
python main.py "VIDEO_URL" --summary

# 영어로 번역
python main.py "VIDEO_URL" --translate en

# 핵심 주제 5개 추출
python main.py "VIDEO_URL" --topics 5

# 모든 AI 기능 사용
python main.py "VIDEO_URL" --summary --translate en --topics 5
```

### 방법 4: 자막 언어 지정

```bash
# 한국어 우선, 영어 차선
python main.py "VIDEO_URL" --lang ko en

# 일본어 우선
python main.py "VIDEO_URL" --lang ja

# 영어와 스페인어
python main.py "VIDEO_URL" --lang en es
```

### 방법 5: 종합 예제

```bash
# 재생목록의 처음 3개 비디오를 JSON으로 저장하고, AI 요약 및 영어 번역 포함
python main.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" \
  --format 2 \
  --max-videos 3 \
  --summary \
  --translate en \
  --topics 3 \
  --lang ko en
```

## 명령줄 옵션

```
usage: main.py [-h] [--lang LANG [LANG ...]] [--summary] [--translate LANG]
               [--topics N] [--format {1,2,3,4}] [--max-videos N]
               [url] [format_choice]

YouTube 비디오/재생목록 스크래퍼 with AI 요약 및 번역

positional arguments:
  url                   YouTube 비디오 또는 재생목록 URL
  format_choice         출력 형식 (1: TXT, 2: JSON, 3: XML, 4: Markdown)

optional arguments:
  -h, --help            도움말 메시지 표시
  --lang LANG [LANG ...]
                        자막 언어 우선순위 (기본값: ko en)
  --summary             Gemini API를 사용한 AI 요약 생성
  --translate LANG      자막을 지정된 언어로 번역 (예: en, ja, zh)
  --topics N            핵심 주제 N개 추출
  --format {1,2,3,4}    출력 형식 (1: TXT, 2: JSON, 3: XML, 4: Markdown)
  --max-videos N        재생목록에서 처리할 최대 비디오 수 (기본값: 전체)
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

🤖 AI Summary (새로운 기능!)
--------------------------------------------------------------------------------
1. 첫 번째 핵심 포인트
2. 두 번째 핵심 포인트
3. 세 번째 핵심 포인트

🔑 Key Topics (새로운 기능!)
--------------------------------------------------------------------------------
• 주제 1
• 주제 2
• 주제 3

🌐 Translation (새로운 기능!)
--------------------------------------------------------------------------------
번역된 전체 내용...

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
  "ai_summary": "1. 첫 번째 요약\n2. 두 번째 요약...",
  "key_topics": ["주제1", "주제2", "주제3"],
  "translation": "번역된 전체 내용...",
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
  <ai_summary>AI 생성 요약...</ai_summary>
  <key_topics>
    <topic>주제 1</topic>
    <topic>주제 2</topic>
  </key_topics>
  <translation>번역된 내용...</translation>
  <transcript>
    <entry>
      <timestamp>00:00</timestamp>
      <start_seconds>0.0</start_seconds>
      <duration>2.5</duration>
      <text>첫 번째 자막 내용</text>
    </entry>
  </transcript>
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

## 🤖 AI Summary

1. 첫 번째 핵심 포인트
2. 두 번째 핵심 포인트

## 🔑 Key Topics

- 주제 1
- 주제 2
- 주제 3

## 🌐 Translation

번역된 전체 내용...

## 📜 Transcript

| Timestamp | Text |
|-----------|------|
| `00:00` | 첫 번째 자막 내용 |
| `00:15` | 두 번째 자막 내용 |
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

### 단일 비디오
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`

### 재생목록
- `https://www.youtube.com/playlist?list=PLAYLIST_ID`
- `https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID`

## 자막 언어 우선순위

기본값: 한국어 (ko) → 영어 (en)

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
pytest tests/test_playlist_handler.py
pytest tests/test_gemini_api.py
```

### 테스트 구조

- `tests/test_youtube_api.py`: YouTube API 모듈 테스트
- `tests/test_formatters.py`: 포맷터 모듈 테스트
- `tests/test_playlist_handler.py`: 재생목록 핸들러 테스트 (NEW)
- `tests/test_gemini_api.py`: Gemini API 모듈 테스트 (NEW)

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

    def save(self, metadata, transcript, output_file, summary=None,
             translation=None, key_topics=None):
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

### Clean Code 원칙

이 프로젝트는 다음 원칙을 따릅니다:

1. **단일 책임 원칙 (SRP)**: 각 모듈과 클래스는 하나의 책임만 가짐
2. **개방-폐쇄 원칙 (OCP)**: 확장에는 열려있고 수정에는 닫혀있음
3. **의존성 역전 원칙 (DIP)**: 추상화에 의존, 구체화에 의존하지 않음
4. **Don't Repeat Yourself (DRY)**: 코드 중복 최소화
5. **명확한 네이밍**: 함수와 변수명이 의도를 명확히 표현

## 실전 예제

### 예제 1: 교육 콘텐츠 분석

```bash
# 강의 재생목록을 스크랩하고 AI 요약으로 학습 노트 생성
python main.py "https://www.youtube.com/playlist?list=PLEducation123" \
  --summary \
  --topics 10 \
  --format 4 \
  --max-videos 10
```

### 예제 2: 다국어 콘텐츠 번역

```bash
# 한국어 비디오를 영어로 번역
python main.py "https://www.youtube.com/watch?v=KoreanVideo" \
  --translate en \
  --lang ko \
  --format 2
```

### 예제 3: 컨퍼런스 토크 요약

```bash
# 컨퍼런스 발표 영상의 핵심만 추출
python main.py "https://www.youtube.com/watch?v=ConferenceTalk" \
  --summary \
  --topics 5 \
  --format 4
```

## 요구사항

- Python 3.7 이상
- 인터넷 연결
- Gemini API 키 (AI 기능 사용 시)

## 문제 해결

### Q: "자막을 찾을 수 없습니다" 오류가 발생합니다.

A: 해당 비디오에 자막이 없거나, 언어 설정을 조정해보세요:
```bash
python main.py "VIDEO_URL" --lang en
```

### Q: Gemini API 오류가 발생합니다.

A:
1. API 키가 올바르게 설정되었는지 확인
2. API 할당량을 초과하지 않았는지 확인
3. 인터넷 연결 상태 확인

### Q: 재생목록 처리 중 일부 비디오가 실패합니다.

A: 정상 동작입니다. 자막이 없거나 접근 불가능한 비디오는 건너뛰고 계속 진행됩니다.

## 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제공됩니다.

## 주의사항

- YouTube의 이용 약관을 준수하여 사용하세요.
- 저작권이 있는 콘텐츠를 무단으로 배포하지 마세요.
- API 사용 제한이 있을 수 있습니다.
- Gemini API는 유료 서비스이며, 무료 할당량이 제한적일 수 있습니다.

## 기여

버그 리포트, 기능 제안, Pull Request를 환영합니다!

## 변경 이력

### Phase 2 (현재)
- ✅ YouTube 재생목록 지원 추가
- ✅ Gemini API 통합 (AI 요약, 번역, 주제 추출)
- ✅ 다국어 자막 지원 개선
- ✅ CLI 인자 파싱 개선
- ✅ 포괄적인 테스트 추가

### Phase 1
- ✅ 기본 스크래핑 기능
- ✅ 다중 출력 형식 (TXT, JSON, XML, Markdown)
- ✅ 모듈화 아키텍처
- ✅ 단위 테스트
