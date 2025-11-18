#!/bin/bash
    
    echo "============================================="
    echo "Installing YouTube Scrapper Dependencies..."
    echo "============================================="
    
    # requirements.txt에 명시된 핵심 의존성 설치
    pip install -r requirements.txt
    
    # Phase 2/3에서 제안된 AI 요약/번역 기능을 위한 라이브러리 추가
    # (Gemini API 사용)
    pip install google-generativeai
    
    echo "============================================="
    echo "All dependencies installed. Environment is ready."
    echo "============================================="
    exit 0