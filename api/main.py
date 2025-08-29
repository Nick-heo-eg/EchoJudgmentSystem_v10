from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .router import router
from .batch_router import get_advanced_routers
from .judgment_web_router import router as judgment_web_router

app = FastAPI(
    title="EchoJudgmentSystem API",
    description="판단⨯전략⨯감정⨯보상 루프 기반 로컬 API 서버",
    version="2.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기본 라우터
app.include_router(router)

# WebShell 연동 라우터
app.include_router(judgment_web_router)

# 고급 기능 라우터들
for advanced_router in get_advanced_routers():
    app.include_router(advanced_router)


@app.get("/")
async def root():
    return {
        "message": "EchoJudgmentSystem API v2.0",
        "features": [
            "기본 판단 시스템",
            "WebShell 연동 판단 시스템",
            "배치 처리",
            "고급 분석",
            "실시간 모니터링",
            "학습 시스템",
        ],
    }
