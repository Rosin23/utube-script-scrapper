# CLAUDE.md - AI Assistant Guide

This document provides comprehensive guidance for AI assistants working with the `utube-script-scrapper` codebase.

## Table of Contents
- [Repository Overview](#repository-overview)
- [Architecture & Design Patterns](#architecture--design-patterns)
- [Module Reference](#module-reference)
- [Development Workflow](#development-workflow)
- [Testing Conventions](#testing-conventions)
- [Git Workflow](#git-workflow)
- [Code Style & Conventions](#code-style--conventions)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)

---

## Repository Overview

### Purpose
A Python-based YouTube video/playlist scraper that extracts metadata, descriptions, and timestamped transcripts with AI-powered enhancements (summarization, translation, topic extraction).

### Key Features (Phase 2)
1. **YouTube Playlist Support**: Automatic detection and batch processing of playlists using yt-dlp
2. **AI Summarization**: Gemini API integration for automatic transcript summarization
3. **Multi-language Support**: User-configurable subtitle language preferences
4. **Translation**: AI-powered transcript translation to target languages
5. **Topic Extraction**: Automatic extraction of key topics from video content
6. **Multi-format Output**: TXT, JSON, XML, Markdown formatters

### Technology Stack
- **Python 3.11+**
- **Core Libraries**: yt-dlp, youtube-transcript-api
- **AI Integration**: google-generativeai (Gemini API v1beta)
- **Testing**: pytest, pytest-mock, pytest-cov
- **Design Patterns**: Strategy Pattern, Dependency Injection

---

## Architecture & Design Patterns

### Project Structure
```
utube-script-scrapper/
├── main.py                      # Entry point with argparse CLI (439 lines)
├── youtube_api.py               # YouTube API integration (234 lines)
├── formatters.py                # Output formatters - Strategy Pattern (402 lines)
├── playlist_handler.py          # Playlist detection & processing (191 lines)
├── gemini_api.py                # Gemini API v1beta integration (454 lines)
├── Utube_scrapper.py            # Legacy compatibility script (535 lines)
├── requirements.txt             # Python dependencies
├── pytest.ini                   # pytest configuration
├── tests/                       # Unit tests directory
│   ├── __init__.py
│   ├── test_youtube_api.py      # YouTube API tests
│   ├── test_formatters.py       # Formatter tests
│   ├── test_playlist_handler.py # Playlist handler tests
│   └── test_gemini_api.py       # Gemini API tests (34 tests, 88% coverage)
├── README.md                    # User documentation
├── ISSUE_TRANSCRIPT_API_FIX.md  # Known issues & troubleshooting
└── CLAUDE.md                    # This file
```

### Design Patterns

#### 1. Strategy Pattern (Formatters)
**Location**: `formatters.py`

The formatter system uses the Strategy Pattern to allow interchangeable output formats:

```python
# Abstract base class
class Formatter(ABC):
    @abstractmethod
    def save(self, metadata, transcript, output_file, summary=None,
             translation=None, key_topics=None) -> None:
        pass

# Concrete implementations
class TxtFormatter(Formatter): ...
class JsonFormatter(Formatter): ...
class XmlFormatter(Formatter): ...
class MarkdownFormatter(Formatter): ...

# Factory function
def get_formatter(choice: str) -> Formatter:
    formatters = {
        '1': TxtFormatter,
        '2': JsonFormatter,
        '3': XmlFormatter,
        '4': MarkdownFormatter,
    }
    return formatters.get(choice, TxtFormatter)()
```

**Benefits**:
- Easy to add new output formats without modifying existing code (OCP)
- Each formatter encapsulates its own logic (SRP)
- Client code works with the abstract interface

#### 2. Dependency Injection
**Location**: Throughout the codebase

Modules are loosely coupled through function parameters rather than hard-coded dependencies:

```python
# Good: Dependencies are injected
def process_video(video_url, gemini_client=None, formatter=None):
    ...

# Tests can easily inject mocks
def test_process_video():
    mock_client = Mock()
    process_video(url, gemini_client=mock_client)
```

#### 3. API Client Pattern
**Location**: `gemini_api.py`

The Gemini API integration uses a client class with retry logic and error handling:

```python
class GeminiClient:
    def __init__(self, api_key, model_name, retry_count=3, retry_delay=1.0):
        # Client initialization with genai.Client() (v1beta API)

    def _make_api_call(self, prompt, temperature=0.7):
        # Retry logic with exponential backoff

    def generate_summary(self, transcript, max_points=5, language='ko'):
        # High-level API methods
```

### Clean Code Principles

The codebase follows SOLID principles:

1. **Single Responsibility Principle (SRP)**
   - Each module has one clear purpose
   - `youtube_api.py`: YouTube data extraction
   - `gemini_api.py`: AI operations
   - `formatters.py`: Output formatting
   - `playlist_handler.py`: Playlist processing

2. **Open-Closed Principle (OCP)**
   - New formatters can be added without modifying existing code
   - Strategy Pattern enables extension

3. **Dependency Inversion Principle (DIP)**
   - High-level modules depend on abstractions (Formatter ABC)
   - Loose coupling through dependency injection

4. **DRY (Don't Repeat Yourself)**
   - Shared functionality extracted to utility functions
   - Reusable components across modules

---

## Module Reference

### main.py (439 lines)
**Purpose**: Entry point with comprehensive CLI using argparse

**Key Functions**:
- `parse_arguments()`: CLI argument parsing with argparse
- `display_banner()`: Program banner display
- `get_output_filename()`: Output filename generation
- `process_single_video()`: Single video processing logic
- `main()`: Main execution flow

**CLI Arguments**:
```bash
# Positional
url                  # YouTube video or playlist URL
format_choice        # Output format (1-4)

# Optional
--lang LANG [LANG ...]   # Subtitle language priority (default: ko en)
--summary                # Enable AI summarization
--translate LANG         # Translate to target language
--topics N               # Extract N key topics
--format {1,2,3,4}       # Output format (alternative to positional)
--max-videos N           # Limit playlist processing
```

**Example Usage**:
```bash
# Single video with summary
python main.py VIDEO_URL --summary

# Playlist with all AI features
python main.py PLAYLIST_URL --summary --translate en --topics 5 --format 2
```

### youtube_api.py (234 lines)
**Purpose**: YouTube data extraction using yt-dlp and youtube-transcript-api

**Key Functions**:
- `extract_video_id(url: str) -> Optional[str]`: Extract video ID from various URL formats
- `get_video_metadata(video_id: str) -> Dict`: Fetch video metadata using yt-dlp
- `get_transcript_with_timestamps(video_id, languages, prefer_manual) -> List[Dict]`: Fetch timestamped transcripts
- `format_timestamp(seconds: float) -> str`: Convert seconds to HH:MM:SS format

**Important Notes**:
- Uses `youtube-transcript-api` for transcript extraction
- Supports multiple language preferences (fallback chain)
- Compatible with both 0.x and 1.x versions of youtube-transcript-api
- See `ISSUE_TRANSCRIPT_API_FIX.md` for known issues

### formatters.py (402 lines)
**Purpose**: Output formatting using Strategy Pattern

**Class Hierarchy**:
```
Formatter (ABC)
├── TxtFormatter      # Structured text format
├── JsonFormatter     # JSON format
├── XmlFormatter      # XML format
└── MarkdownFormatter # Markdown format
```

**All Formatters Support**:
- Video metadata (title, channel, views, date, etc.)
- Timestamped transcripts
- AI-generated summary (optional)
- Translation (optional)
- Key topics (optional)

**Adding New Formatters**:
1. Create class inheriting from `Formatter`
2. Implement `save()` method with signature:
   ```python
   def save(self, metadata, transcript, output_file,
            summary=None, translation=None, key_topics=None) -> None:
   ```
3. Add to factory function `get_formatter()`

### playlist_handler.py (191 lines)
**Purpose**: Playlist detection and video URL extraction

**Key Functions**:
- `PlaylistHandler.is_playlist_url(url) -> bool`: Detect playlist URLs
- `PlaylistHandler.extract_playlist_id(url) -> Optional[str]`: Extract playlist ID
- `PlaylistHandler.get_playlist_info(url) -> Optional[Dict]`: Fetch playlist metadata
- `PlaylistHandler.get_video_urls_from_playlist(url) -> List[Dict]`: Extract all video URLs
- `process_playlist_or_video(url) -> Dict`: Unified processor for playlists/videos

**Return Format**:
```python
{
    'type': 'playlist' | 'video' | 'unknown',
    'videos': [{'id': str, 'url': str, 'title': str}, ...],
    'playlist_info': {'title': str, 'uploader': str, 'video_count': int} | None
}
```

### gemini_api.py (454 lines)
**Purpose**: Gemini API v1beta integration for AI features

**CRITICAL**: Uses official Gemini API v1beta style
```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=prompt,
    config=types.GenerateContentConfig(temperature=0.7)
)
```

**Key Class**: `GeminiClient`

**Methods**:
- `__init__(api_key, model_name, retry_count, retry_delay)`: Initialize client
- `_make_api_call(prompt, temperature) -> str`: Low-level API call with retry logic
- `generate_summary(transcript, max_points, language) -> str`: Generate summary
- `translate_text(text, target_language, source_language) -> str`: Translate text
- `translate_transcript(transcript, target_language) -> str`: Translate full transcript
- `extract_key_topics(transcript, num_topics, language) -> List[str]`: Extract topics

**Environment Variables**:
- `GEMINI_API_KEY` (primary)
- `GOOGLE_API_KEY` (fallback)

**Supported Models**:
- `gemini-2.0-flash-exp` (default)
- `gemini-2.5-flash`
- `gemini-1.5-flash`
- `gemini-1.5-pro`

**Error Handling**:
- Custom exception: `GeminiAPIError`
- Exponential backoff retry (3 attempts by default)
- Logging for debugging
- Text length validation (30,000 char limit)

---

## Development Workflow

### Phase-Based Development

The project follows a phased development approach:

**Phase 1** (Completed):
- Basic YouTube scraping
- Multi-format output (TXT, JSON, XML, Markdown)
- Modular architecture
- Comprehensive testing

**Phase 2** (Current - Completed):
- Playlist support
- AI summarization (Gemini API)
- Multi-language subtitle support
- Translation capabilities
- Topic extraction
- Refactored to official Gemini API v1beta

**Future Phases**:
- Web interface
- Batch processing
- Additional AI models

### Branch Naming Convention

```
claude/<feature-description>-<session-id>
```

Examples:
- `claude/phase-2-core-features-01QUjqhTGM1GiY4RQGsY92bk`
- `claude/add-multi-format-conversion`

**IMPORTANT**: Session ID suffix is required for push operations (403 forbidden without it).

### Development Steps

1. **Planning**: Use TodoWrite tool for multi-step tasks
2. **Implementation**: Write code following existing patterns
3. **Testing**: Achieve 80%+ coverage target
4. **Documentation**: Update README.md and docstrings
5. **Commit**: Clear, descriptive commit messages
6. **Push**: Use `git push -u origin <branch-name>` with retry logic

---

## Testing Conventions

### Test Structure

**Location**: `tests/` directory

**Configuration**: `pytest.ini`
```ini
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### Test Organization

Each test file follows this structure:
```python
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock external dependencies BEFORE importing module
mock_external = MagicMock()
sys.modules['external_lib'] = mock_external

# Now import the module under test
from module import ClassName, function

class TestClassName:
    """ClassName 테스트"""

    def test_method_success(self):
        """성공 케이스 테스트"""
        ...

    def test_method_failure(self):
        """실패 케이스 테스트"""
        ...
```

### Gemini API Testing Pattern

**CRITICAL**: The Gemini API uses a new pattern that requires special mocking:

```python
# tests/test_gemini_api.py
import sys
from unittest.mock import MagicMock

# Mock the new API structure BEFORE importing
mock_genai_module = MagicMock()
mock_types_module = MagicMock()
mock_google = MagicMock()
mock_google.genai = mock_genai_module
mock_genai_module.types = mock_types_module

sys.modules['google'] = mock_google
sys.modules['google.genai'] = mock_genai_module
sys.modules['google.genai.types'] = mock_types_module

# Now safe to import
from gemini_api import GeminiClient

# In tests, mock the client
mock_client = Mock()
mock_genai_module.Client.return_value = mock_client
mock_client.models.generate_content.return_value = mock_response
```

### Coverage Requirements

**Target**: 80%+ coverage for all new modules

**Running Tests**:
```bash
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ -v --cov=. --cov-report=term-missing

# Specific module
python -m pytest tests/test_gemini_api.py -v --cov=gemini_api --cov-report=term-missing
```

**Current Coverage** (as of last test):
- `gemini_api.py`: 88% ✅
- `playlist_handler.py`: 92% ✅
- `formatters.py`: 77%
- Overall: 63% (including legacy code)

### Test Naming Conventions

```python
def test_<method_name>_<scenario>():
    """<Korean description>"""
```

Examples:
- `test_initialization_with_api_key()`: "API 키로 초기화 테스트"
- `test_make_api_call_retry()`: "API 호출 재시도 테스트"
- `test_generate_summary_empty_transcript()`: "빈 자막으로 요약 생성 시 None 반환 테스트"

### Mocking Best Practices

1. **Mock external dependencies early** (before imports)
2. **Use `patch.dict(os.environ, ...)` for environment variables**
3. **Reset side_effects after tests** to avoid interference
4. **Use descriptive mock return values** for clarity

Example:
```python
@patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
def test_something(self):
    mock_client = Mock()
    mock_client.models.generate_content.return_value = Mock(text="Result")
    ...
    # Clean up
    mock_client.models.generate_content.side_effect = None
```

---

## Git Workflow

### Commit Message Format

```
<Type>: <Short description>

<Detailed description>
- Bullet point 1
- Bullet point 2
- ...
```

**Types**:
- `Refactor`: Code restructuring
- `Implement`: New feature implementation
- `Fix`: Bug fixes
- `Update`: Documentation or minor updates
- `Add`: Adding new files or functionality

**Example**:
```
Refactor gemini_api.py to use official Gemini API v1beta style

- Changed from google.generativeai to google.genai and google.genai.types imports
- Updated client initialization to use genai.Client() instead of genai.GenerativeModel()
- Modified API calls to use client.models.generate_content() pattern
- Updated config to use types.GenerateContentConfig()
- All gemini_api tests passing with 88% coverage (exceeds 80% target)
```

### Git Operations with Retry Logic

**Push Operations**:
```bash
# CRITICAL: Branch must start with 'claude/' and end with session ID
git push -u origin claude/feature-name-SESSION_ID
```

**Retry Logic** (for network failures):
- Retry up to 4 times
- Exponential backoff: 2s, 4s, 8s, 16s
- Apply to: `git push`, `git fetch`, `git pull`

**Never**:
- Push to main/master without explicit permission
- Use `git push --force` to main/master
- Skip hooks (--no-verify) unless explicitly requested
- Commit changes without user request

### Branch Operations

```bash
# Create and switch to new branch
git checkout -b claude/feature-name-SESSION_ID

# Stage files
git add file1.py file2.py

# Commit with heredoc for formatting
git commit -m "$(cat <<'EOF'
Commit message here.

- Detail 1
- Detail 2
EOF
)"

# Push with upstream tracking
git push -u origin claude/feature-name-SESSION_ID
```

---

## Code Style & Conventions

### Python Style

**General**:
- PEP 8 compliant
- Type hints throughout
- Docstrings for all public functions/classes
- Korean comments for Korean-speaking team, English for public APIs

**Example**:
```python
def get_video_metadata(video_id: str) -> Dict:
    """
    비디오 메타데이터를 가져옵니다.

    Args:
        video_id: YouTube 비디오 ID

    Returns:
        메타데이터 딕셔너리

    Raises:
        Exception: 메타데이터 추출 실패 시
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    ...
```

### Docstrings

**Module Level**:
```python
"""
모듈 설명
추가 설명이 필요한 경우 여기에 작성합니다.
"""
```

**Function/Method Level**:
```python
def function_name(param1: Type1, param2: Type2 = default) -> ReturnType:
    """
    함수의 목적을 한 줄로 설명합니다.

    Args:
        param1: 첫 번째 파라미터 설명
        param2: 두 번째 파라미터 설명 (기본값: default)

    Returns:
        반환값 설명

    Raises:
        ExceptionType: 예외 발생 조건
    """
```

### Error Handling

1. **Custom Exceptions** for domain-specific errors:
   ```python
   class GeminiAPIError(Exception):
       """Gemini API 관련 커스텀 예외"""
       pass
   ```

2. **Logging** instead of print statements (in production code):
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info("Processing video...")
   logger.error(f"Failed to process: {e}")
   ```

3. **Graceful degradation** for optional features:
   ```python
   try:
       summary = gemini_client.generate_summary(transcript)
   except GeminiAPIError as e:
       logger.warning(f"Summary generation failed: {e}")
       summary = None  # Continue without summary
   ```

### Import Organization

```python
# Standard library
import sys
import os
from typing import Optional, List, Dict

# Third-party
import pytest
from unittest.mock import Mock, patch

# Local modules
from youtube_api import extract_video_id
from formatters import get_formatter
from gemini_api import GeminiClient
```

---

## Common Tasks

### Adding a New Output Formatter

1. **Create formatter class** in `formatters.py`:
   ```python
   class CsvFormatter(Formatter):
       def __init__(self):
           super().__init__()
           self.file_extension = "csv"
           self.format_name = "CSV"

       def save(self, metadata, transcript, output_file,
                summary=None, translation=None, key_topics=None) -> None:
           # Implementation
           pass
   ```

2. **Add to factory**:
   ```python
   def get_formatter(choice: str) -> Formatter:
       formatters = {
           '1': TxtFormatter,
           '2': JsonFormatter,
           '3': XmlFormatter,
           '4': MarkdownFormatter,
           '5': CsvFormatter,  # NEW
       }
       return formatters.get(choice, TxtFormatter)()
   ```

3. **Update available formatters**:
   ```python
   def get_available_formatters() -> List[str]:
       return [
           "1. 텍스트 (TXT)",
           "2. JSON",
           "3. XML",
           "4. Markdown (MD)",
           "5. CSV",  # NEW
       ]
   ```

4. **Write tests** in `tests/test_formatters.py`:
   ```python
   class TestCsvFormatter:
       def test_initialization(self):
           formatter = CsvFormatter()
           assert formatter.file_extension == "csv"

       def test_save_creates_valid_csv(self, tmp_path):
           # Test implementation
           pass
   ```

### Adding Gemini API Functionality

1. **Add method to `GeminiClient` class**:
   ```python
   def new_ai_feature(self, transcript: List[Dict],
                      param: str = 'default') -> Optional[str]:
       """
       새로운 AI 기능 설명

       Args:
           transcript: 자막 데이터
           param: 파라미터 설명

       Returns:
           결과 문자열 또는 None
       """
       # Validate input
       combined_text = self._combine_transcript_text(transcript)
       if not combined_text:
           return None

       # Create prompt
       prompt = f"Your prompt here: {combined_text}"

       # Make API call
       return self._make_api_call(prompt, temperature=0.7)
   ```

2. **Add tests**:
   ```python
   @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
   def test_new_ai_feature_success(self):
       mock_response = Mock()
       mock_response.text = "AI response"
       mock_client = Mock()
       mock_client.models.generate_content.return_value = mock_response
       mock_genai_module.Client.return_value = mock_client

       client = GeminiClient()
       result = client.new_ai_feature(transcript)

       assert result == "AI response"
   ```

3. **Integrate in `main.py`** if needed

### Updating Dependencies

1. **Update `requirements.txt`**:
   ```
   new-package>=1.0.0
   ```

2. **Install and test**:
   ```bash
   pip install -r requirements.txt
   python -m pytest tests/ -v
   ```

3. **Document in README.md** if user-facing

---

## Troubleshooting

### Common Issues

#### 1. Gemini API Import Errors

**Problem**: `ModuleNotFoundError: No module named 'google.genai'`

**Solution**: Install correct package:
```bash
pip install google-generativeai>=0.3.0
```

**Important**: The package name is `google-generativeai` but imports use `from google import genai`

#### 2. Test Import Failures

**Problem**: Tests fail with `pyo3_runtime.PanicException`

**Solution**: Mock the modules BEFORE importing:
```python
# At top of test file, before imports
mock_genai_module = MagicMock()
sys.modules['google.genai'] = mock_genai_module
```

#### 3. YouTube Transcript API Issues

**Problem**: Transcript extraction fails

**Solution**: See `ISSUE_TRANSCRIPT_API_FIX.md` for:
- Version compatibility (0.x vs 1.x)
- Language code issues
- Manual vs auto-generated subtitle preferences

#### 4. Coverage Not Meeting 80%

**Steps**:
1. Run coverage report to identify gaps:
   ```bash
   python -m pytest tests/test_module.py --cov=module --cov-report=term-missing
   ```
2. Look at "Missing" column for uncovered lines
3. Add tests for:
   - Error handling paths
   - Edge cases (empty input, None values)
   - Conditional branches

### Debugging Tips

1. **Enable logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Use pytest verbose mode**:
   ```bash
   python -m pytest tests/ -vv
   ```

3. **Run single test**:
   ```bash
   python -m pytest tests/test_file.py::TestClass::test_method -v
   ```

4. **Check test output**:
   ```bash
   python -m pytest tests/ -v --tb=short  # Short traceback
   python -m pytest tests/ -v --tb=long   # Full traceback
   ```

---

## Best Practices for AI Assistants

### When Working with This Codebase

1. **Always read existing code** before making changes
   - Use Read tool to understand current implementation
   - Check for similar patterns in codebase

2. **Follow existing patterns**
   - Use Strategy Pattern for formatters
   - Use dependency injection for testability
   - Follow naming conventions (Korean comments + English code)

3. **Test-Driven Development**
   - Write tests for new features
   - Target 80%+ coverage
   - Use mocking for external dependencies

4. **Document changes**
   - Update docstrings
   - Update README.md for user-facing features
   - Update this CLAUDE.md for architecture changes

5. **Use TodoWrite for complex tasks**
   - Break down multi-step tasks
   - Track progress (pending, in_progress, completed)
   - Mark tasks complete immediately after finishing

6. **Git workflow**
   - Commit with clear, descriptive messages
   - Use heredoc for multi-line commit messages
   - Push with retry logic for network failures
   - Never force push to main/master

7. **Handle API changes carefully**
   - Read official documentation when provided
   - Update mocks to match new API patterns
   - Test thoroughly after refactoring

### Code Review Checklist

Before committing, verify:

- [ ] Code follows existing patterns
- [ ] Type hints added for all functions
- [ ] Docstrings present and accurate
- [ ] Tests written and passing
- [ ] Coverage ≥ 80% for new code
- [ ] No security vulnerabilities (SQL injection, XSS, etc.)
- [ ] Error handling implemented
- [ ] Logging instead of print statements
- [ ] README.md updated if needed
- [ ] Commit message is clear and descriptive

---

## Version History

### Current State (2025-11-18)

**Latest Commit**: `3fb94d7` - Refactor gemini_api.py to use official Gemini API v1beta style

**Key Modules**:
- `main.py`: 439 lines - Phase 2 CLI with argparse
- `gemini_api.py`: 454 lines - Gemini API v1beta integration (88% coverage)
- `formatters.py`: 402 lines - Strategy Pattern formatters (77% coverage)
- `youtube_api.py`: 234 lines - YouTube API integration
- `playlist_handler.py`: 191 lines - Playlist handling (92% coverage)

**Branch**: `claude/phase-2-core-features-01QUjqhTGM1GiY4RQGsY92bk`

**Test Coverage**: 46 tests passing for Phase 2 modules

---

## Contact & Resources

- **Repository**: https://github.com/Rosin23/utube-script-scrapper
- **Issues**: See ISSUE_TRANSCRIPT_API_FIX.md
- **User Guide**: README.md

---

*This document is maintained by AI assistants and should be updated when significant architectural changes are made.*
