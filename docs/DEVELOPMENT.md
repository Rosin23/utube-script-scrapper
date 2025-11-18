# Development Guide

Complete guide for developers contributing to the YouTube Script Scraper API.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Adding New Features](#adding-new-features)
- [Debugging](#debugging)
- [Git Workflow](#git-workflow)
- [CI/CD](#cicd)

---

## Development Environment Setup

### Prerequisites

- **Python 3.11+**
- **pip** (Python package manager)
- **git**
- **vscode** or your preferred IDE (recommended)

### Step 1: Clone Repository

```bash
git clone https://github.com/Rosin23/utube-script-scrapper.git
cd utube-script-scrapper
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Install development dependencies (if separate file exists)
pip install pytest pytest-cov pytest-mock httpx black mypy ruff
```

### Step 4: Configure Environment

```bash
# Create .env file
cp .env.example .env  # If example exists

# Or create manually
cat > .env << EOF
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL_NAME=gemini-2.0-flash-exp
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=DEBUG
EOF
```

### Step 5: Verify Setup

```bash
# Run tests
python -m pytest tests/ -v

# Start development server
python api_main.py --reload

# Visit http://localhost:8000/docs
```

---

## Project Structure

```
utube-script-scrapper/
├── api_main.py                 # FastAPI entry point
├── api/                        # API layer
│   ├── routers/                # FastAPI routers
│   │   ├── video.py
│   │   ├── playlist.py
│   │   └── ai.py
│   └── schemas/                # Pydantic models
│       ├── video.py
│       ├── playlist.py
│       └── ai.py
├── core/                       # Business logic
│   ├── youtube_service.py
│   ├── ai_service.py
│   └── formatter_service.py
├── tools/                      # Agent tools
│   ├── video_scraper.py
│   ├── summarizer.py
│   ├── translator.py
│   └── topic_extractor.py
├── utils/                      # Utilities
│   ├── config.py               # Settings
│   └── dependencies.py         # DI functions
├── tests/                      # Test suite
│   ├── api/
│   ├── core/
│   └── tools/
├── examples/                   # Usage examples
├── docs/                       # Documentation
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

### Key Files

| File | Purpose |
|------|---------|
| `api_main.py` | FastAPI application entry point |
| `api/routers/*.py` | API endpoint definitions |
| `api/schemas/*.py` | Request/response models |
| `core/*_service.py` | Business logic implementation |
| `tools/*.py` | Agent-compatible tools |
| `utils/dependencies.py` | Dependency injection setup |
| `tests/` | Comprehensive test suite |

---

## Coding Standards

### Python Style Guide

Follow **PEP 8** conventions:

```python
# Good
def get_video_info(video_url: str) -> Dict[str, Any]:
    """Get video information from YouTube."""
    pass

# Bad
def GetVideoInfo(videoUrl):
    pass
```

### Type Hints

Always use type hints:

```python
from typing import List, Dict, Optional, Any

def process_videos(
    urls: List[str],
    enable_summary: bool = False
) -> List[Dict[str, Any]]:
    """Process multiple videos."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def scrape_video(
    video_url: str,
    languages: List[str] = None
) -> Dict[str, Any]:
    """
    Scrape YouTube video with optional AI enhancement.

    Args:
        video_url: YouTube video URL
        languages: Preferred subtitle languages

    Returns:
        Dictionary containing metadata and transcript

    Raises:
        ValueError: If URL is invalid
        HTTPException: If YouTube service fails
    """
    pass
```

### Async/Await

Use async for I/O operations:

```python
# Good (FastAPI endpoints)
async def get_video_info(
    request: VideoRequest,
    youtube_service: YouTubeServiceDep
):
    result = youtube_service.get_video_info(request.video_url)
    return result

# Note: Service methods can be sync or async
# FastAPI handles both
```

### Error Handling

Use FastAPI's HTTPException:

```python
from fastapi import HTTPException

try:
    result = youtube_service.get_video_info(url)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Failed: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

---

## Testing

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=api --cov=core --cov=tools --cov-report=term-missing

# Specific test file
python -m pytest tests/api/test_video_router.py -v

# Specific test class
python -m pytest tests/api/test_video_router.py::TestVideoRouter -v

# Specific test method
python -m pytest tests/api/test_video_router.py::TestVideoRouter::test_get_video_info -v

# Generate HTML coverage report
python -m pytest tests/ --cov=api --cov=core --cov-report=html
# Open htmlcov/index.html in browser
```

### Writing Tests

#### API Endpoint Tests

```python
from fastapi.testclient import TestClient
from unittest.mock import Mock
from api_main import app
from utils.dependencies import get_youtube_service

client = TestClient(app)

def test_get_video_info():
    # Create mock service
    mock_service = Mock()
    mock_service.get_video_info.return_value = {
        'metadata': {'title': 'Test Video'},
        'transcript': []
    }

    # Override dependency
    app.dependency_overrides[get_youtube_service] = lambda: mock_service

    # Make request
    response = client.post(
        "/video/info",
        json={"video_url": "https://youtube.com/watch?v=test"}
    )

    # Clean up
    app.dependency_overrides = {}

    # Assertions
    assert response.status_code == 200
    assert response.json()['metadata']['title'] == 'Test Video'
```

#### Service Tests

```python
from unittest.mock import Mock, patch
from core.youtube_service import YouTubeService

@patch('core.youtube_service.yt_dlp')
def test_get_video_metadata(mock_ytdlp):
    # Setup mock
    mock_ytdlp.YoutubeDL.return_value.__enter__.return_value.extract_info.return_value = {
        'title': 'Test Video',
        'uploader': 'Test Channel'
    }

    # Test
    service = YouTubeService()
    metadata = service.get_video_metadata('test_id')

    # Assert
    assert metadata['title'] == 'Test Video'
    assert metadata['uploader'] == 'Test Channel'
```

### Test Coverage Goals

- **API Layer**: 80%+ coverage
- **Core Layer**: 80%+ coverage
- **Tools Layer**: 80%+ coverage
- **Overall**: 81%+ coverage (current)

---

## Adding New Features

### Adding a New API Endpoint

#### Step 1: Create Pydantic Schema

```python
# api/schemas/new_feature.py
from pydantic import BaseModel, Field

class NewFeatureRequest(BaseModel):
    param1: str = Field(..., description="Parameter 1")
    param2: int = Field(default=5, description="Parameter 2")

class NewFeatureResponse(BaseModel):
    result: str
    status: str
```

#### Step 2: Create Service Method

```python
# core/new_service.py
class NewService:
    def process_feature(self, param1: str, param2: int) -> dict:
        """Process new feature."""
        # Implementation
        return {'result': 'success', 'status': 'ok'}
```

#### Step 3: Create Router Endpoint

```python
# api/routers/new_router.py
from fastapi import APIRouter, HTTPException
from api.schemas.new_feature import NewFeatureRequest, NewFeatureResponse
from core.new_service import NewService

router = APIRouter(prefix="/new", tags=["new"])

@router.post("/process", response_model=NewFeatureResponse)
async def process_new_feature(request: NewFeatureRequest):
    """Process new feature."""
    try:
        service = NewService()
        result = service.process_feature(request.param1, request.param2)
        return NewFeatureResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Step 4: Register Router

```python
# api_main.py
from api.routers import new_router

app.include_router(new_router.router)
```

#### Step 5: Write Tests

```python
# tests/api/test_new_router.py
def test_process_new_feature():
    response = client.post(
        "/new/process",
        json={"param1": "test", "param2": 10}
    )
    assert response.status_code == 200
```

### Adding a New Output Format

#### Step 1: Create Formatter Class

```python
# formatters.py
class SrtFormatter(Formatter):
    def __init__(self):
        super().__init__()
        self.file_extension = "srt"
        self.format_name = "SRT Subtitle"

    def save(self, metadata, transcript, output_file, **kwargs):
        """Save as SRT format."""
        srt_content = self._generate_srt(transcript)
        with open(f"{output_file}.{self.file_extension}", 'w') as f:
            f.write(srt_content)

    def _generate_srt(self, transcript):
        # SRT format generation
        pass
```

#### Step 2: Register Formatter

```python
# formatters.py
def get_available_formatters():
    return {
        '1': TxtFormatter(),
        '2': JsonFormatter(),
        '3': XmlFormatter(),
        '4': MarkdownFormatter(),
        '5': SrtFormatter()  # New
    }
```

### Adding a New AI Feature

```python
# core/ai_service.py
def extract_entities(self, text: str) -> List[str]:
    """Extract named entities from text."""
    if not self.is_available():
        return []

    prompt = f"Extract named entities from: {text}"
    response = self.client.generate_content(prompt)
    return self._parse_entities(response.text)
```

---

## Debugging

### Development Server with Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with reload
python api_main.py --reload
```

### VSCode Debug Configuration

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "api_main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false
    },
    {
      "name": "Pytest Current File",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "${file}",
        "-v"
      ],
      "console": "integratedTerminal"
    }
  ]
}
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Different log levels
logger.debug("Debug information")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

### Interactive API Docs for Testing

Visit `http://localhost:8000/docs` for:
- Interactive endpoint testing
- Request/response schemas
- Try it out feature

---

## Git Workflow

### Branch Naming Convention

```
feature/<feature-name>-<session-id>
bugfix/<bug-description>
hotfix/<critical-fix>
```

### Commit Message Format

```
<Type>: <Short description>

<Detailed description>
- Bullet point 1
- Bullet point 2

Closes #issue-number
```

**Types:**
- `Feature`: New feature
- `Fix`: Bug fix
- `Refactor`: Code refactoring
- `Test`: Adding tests
- `Docs`: Documentation
- `Style`: Code style changes
- `Perf`: Performance improvements

### Example Commit

```bash
git commit -m "Feature: Add video metadata caching

- Implement Redis caching for video metadata
- Add cache invalidation after 1 hour
- Update tests for caching behavior

Closes #123"
```

### Pull Request Process

1. Create feature branch
2. Implement changes
3. Write/update tests
4. Update documentation
5. Run tests locally
6. Create pull request
7. Address review comments
8. Merge after approval

---

## CI/CD

### GitHub Actions (Example)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=api --cov=core --cov=tools
```

### Pre-commit Hooks (Optional)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

---

## Best Practices

1. **Write Tests First**: TDD approach
2. **Keep Functions Small**: Single responsibility
3. **Use Type Hints**: Better IDE support
4. **Document Everything**: Docstrings and comments
5. **Handle Errors**: Proper exception handling
6. **Log Appropriately**: Debug, info, error levels
7. **Code Review**: Always get reviews
8. **Update Docs**: Keep documentation current

---

## Common Tasks

### Adding a Dependency

```bash
# Install package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Or manually add to requirements.txt
echo "package-name==1.0.0" >> requirements.txt
```

### Running Code Quality Checks

```bash
# Black (formatting)
black .

# Flake8 (linting)
flake8 .

# mypy (type checking)
mypy api/ core/ tools/

# Ruff (fast linting)
ruff check .
```

### Database Migrations (if implemented)

```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Troubleshooting

### Import Errors

```bash
# Ensure you're in the project root
cd /path/to/utube-script-scrapper

# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Test Failures

```bash
# Run specific failing test
python -m pytest tests/path/to/test.py::test_name -v

# See full error output
python -m pytest tests/ -vv

# Drop into debugger on failure
python -m pytest tests/ --pdb
```

### API Not Starting

```bash
# Check if port is already in use
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Use different port
uvicorn api_main:app --port 8001
```

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Pydantic Docs**: https://docs.pydantic.dev
- **pytest Docs**: https://docs.pytest.org
- **Python Style Guide**: https://pep8.org

---

## See Also

- [Architecture Documentation](ARCHITECTURE.md)
- [API Reference](API_REFERENCE.md)
- [Deployment Guide](DEPLOYMENT.md)
