# api/server.py
from fastapi import FastAPI
from api.routers.meta_liminal import router as meta_liminal_router
from api.routers.capsule_router import router as capsule_router

# from api.routers.judgment import router as judgment_router  # 기존
from echo_engine.signature.echo_signature_network import init_signatures

app = FastAPI(title="EchoJudgmentSystem API", version="1.0.0")
init_signatures()

# app.include_router(judgment_router, prefix="/judgment")
app.include_router(meta_liminal_router)  # prefix 포함됨
app.include_router(capsule_router)  # 캡슐 시스템 API

# uvicorn api.server:app --host 127.0.0.1 --port 8000
