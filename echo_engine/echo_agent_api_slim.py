#!/usr/bin/env python3
"""
🌐 EchoAgent API Server (Slim Version)
- 기존 대용량 파일을 라우터별로 분리한 경량화 버전
- 모듈화된 구조로 유지보수성 향상
"""

# compat_aliases 지연 로더 설치
try:
    from .compat_aliases import install_compat_aliases

    install_compat_aliases()
except Exception:
    pass  # 헬스 측정/빌드에서 실패해도 진행

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 라우터 임포트
from echo_engine.routers import health, judgment, agents

# 환경 설정
FAST_BOOT = os.getenv("ECHO_FAST_BOOT", "0") == "1"

# FastAPI 앱 생성
app = FastAPI(
    title="Echo Agent API (Slim)",
    description="Echo Judgment System API - Modularized Version",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health.router)
app.include_router(judgment.router)
app.include_router(agents.router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "Echo Agent API (Slim)",
        "version": "2.0.0",
        "status": "healthy",
        "description": "Modularized Echo Judgment System API",
    }


@app.get("/status")
async def system_status():
    """시스템 상태"""
    return {
        "status": "operational",
        "mode": "slim",
        "routers": ["health", "judgment", "agents"],
        "fast_boot": FAST_BOOT,
    }


def main():
    """서버 실행"""
    port = int(os.getenv("ECHO_API_PORT", "9000"))
    host = os.getenv("ECHO_API_HOST", "0.0.0.0")

    print(f"🚀 Echo Agent API (Slim) 시작")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Docs: http://{host}:{port}/docs")

    uvicorn.run(
        "echo_engine.echo_agent_api_slim:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
