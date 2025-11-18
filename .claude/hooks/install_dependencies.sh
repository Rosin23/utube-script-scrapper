#!/bin/bash

echo "============================================="
echo "Installing YouTube Scraper Dependencies..."
echo "============================================="

# 1. 기본 스크래퍼 의존성 설치
pip install -r requirements.txt

# 2. AI 요약/분석을 위한 Gemini API 라이브러리 설치
pip install google-generativeai

# 3. 'API-First' 아키텍처를 위한 Web Framework 설치
# (모든 에이전트 프레임워크가 접근할 수 있도록 HTTP API 제공)
pip install fastapi uvicorn

echo "============================================="
echo "Starting API Service..."
echo "============================================="

# api_main.py가 존재하면 백그라운드에서 실행 (포트 8080)
# 에이전트가 이 파일을 나중에 생성할 수도 있으므로 체크 후 실행
if [ -f "api_main.py" ]; then
    echo "Found api_main.py. Starting uvicorn server on port 8080..."
    # nohup을 사용하여 세션이 끊겨도 프로세스 유지, 로그는 api.log에 저장
    nohup uvicorn api_main:app --host 0.0.0.0 --port 8080 > api.log 2>&1 &
    echo "✅ API Server is running in background."
else
    echo "ℹ️ api_main.py not found. Skipping server start."
    echo "   (The agent may create this file later and start it manually)"
fi

echo "============================================="
echo "Environment Setup Complete."
echo "============================================="
exit 0