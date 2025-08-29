#!/bin/bash
# Echo Web IDE 시작 스크립트

echo "🧬 Echo Web IDE 시작 중..."

# 가상환경 활성화
source echo_ide_venv/bin/activate

# 웹 서버 시작
echo "🌐 웹 서버를 localhost:8000에서 시작합니다..."
python3 web_ide_server.py

echo "👋 Echo Web IDE 종료"