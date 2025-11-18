"""
FastAPI 메인 애플리케이션 테스트
"""

import pytest
from fastapi.testclient import TestClient

from api_main import app

client = TestClient(app)


class TestMainAPI:
    """메인 API 테스트"""

    def test_root_endpoint(self):
        """루트 엔드포인트 테스트"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data

    def test_health_check(self):
        """헬스 체크 테스트"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_tool_schemas_endpoint(self):
        """도구 스키마 엔드포인트 테스트"""
        response = client.get("/tools/schemas")
        assert response.status_code == 200

        data = response.json()
        assert "tools" in data
        assert "format" in data
        assert data["format"] == "openai_function_calling"
        assert len(data["tools"]) > 0

    def test_openapi_schema(self):
        """OpenAPI 스키마 테스트"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_docs_endpoint(self):
        """API 문서 엔드포인트 테스트"""
        response = client.get("/docs")
        assert response.status_code == 200
