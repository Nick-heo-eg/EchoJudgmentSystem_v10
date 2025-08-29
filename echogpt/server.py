#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGPT FastAPI Server
Teacher-Student Online Distillation ChatGPT-style API
"""
import os
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml

# Local imports
from core.config import load_config
from intent.pipeline import init_global_pipeline, get_global_pipeline
from ops.metrics import Metrics

# Conditional imports
try:
    from intent.distill_trainer import DistillTrainer

    TRAINER_AVAILABLE = True
except ImportError:
    TRAINER_AVAILABLE = False
    DistillTrainer = None

try:
    from ops.logger import setup_logger
except ImportError:
    # Fallback logger setup
    def setup_logger(name: str):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)


# 로거 설정
logger = setup_logger("echogpt.server")

# 전역 상태
pipeline = None
trainer = None
cfg = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 라이프사이클 관리"""
    global pipeline, trainer, cfg

    try:
        # 설정 로드
        cfg = load_config("config/echogpt.yaml")
        logger.info("Configuration loaded")

        # Pipeline 초기화
        pipeline = init_global_pipeline(cfg, logger)
        logger.info("Intent Pipeline initialized")

        # Trainer 초기화 (sklearn이 있는 경우만)
        if TRAINER_AVAILABLE and DistillTrainer:
            try:
                trainer = DistillTrainer(cfg, logger)
                logger.info("Distillation Trainer initialized")
            except Exception as e:
                logger.warning(f"Trainer initialization failed: {e}")
                trainer = None
        else:
            logger.info("Distillation Trainer not available (missing dependencies)")
            trainer = None

        yield

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    finally:
        logger.info("Shutting down EchoGPT server")


# FastAPI 앱 생성
app = FastAPI(
    title="EchoGPT API",
    description="Teacher-Student Online Distillation ChatGPT-style API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response 모델
class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "echogpt-1.0"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000
    stream: Optional[bool] = False


class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str


class ChatUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: ChatUsage


class IntentAnalysisRequest(BaseModel):
    text: str
    context: Optional[Dict[str, Any]] = None


class IntentAnalysisResponse(BaseModel):
    intent: str
    confidence: float
    summary: str
    tags: List[str]
    safety: List[str]
    source: str
    latency_ms: int
    model_available: bool


class SystemStatusResponse(BaseModel):
    status: str
    pipeline: Dict[str, Any]
    metrics: Dict[str, Any]
    trainer: Optional[Dict[str, Any]] = None


# API 엔드포인트
@app.get("/")
async def root():
    """헬스 체크"""
    return {"message": "EchoGPT API Server", "version": "1.0.0", "status": "running"}


@app.post("/v1/chat/completions", response_model=ChatResponse)
async def create_chat_completion(request: ChatRequest):
    """ChatGPT 호환 채팅 완료 API"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    try:
        start_time = time.time()

        # 최신 사용자 메시지 추출
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user messages found")

        last_message = user_messages[-1].content

        # Intent 분석
        intent_result = await pipeline.analyze_intent(last_message)

        # 응답 생성 (임시로 간단한 응답)
        response_content = f"Intent: {intent_result.intent} (confidence: {intent_result.confidence:.2f})\n"
        response_content += f"Summary: {intent_result.summary}\n"

        if intent_result.tags:
            response_content += f"Tags: {', '.join(intent_result.tags)}\n"

        # 특정 intent에 따른 맞춤 응답
        if intent_result.intent == "medical_support":
            response_content += "\n의료 정보는 전문의와 상담하시기 바랍니다."
        elif intent_result.intent == "local_search":
            response_content += "\n위치 기반 검색을 도와드릴게요."
        elif intent_result.intent == "emotional_support":
            response_content += "\n괜찮아요. 함께 해결해 나가요."

        # 응답 생성
        completion_time = int(time.time())
        response_id = f"echogpt-{completion_time}-{hash(last_message) % 10000}"

        # 토큰 계산 (간단한 추정)
        prompt_tokens = sum(len(msg.content.split()) for msg in request.messages)
        completion_tokens = len(response_content.split())

        return ChatResponse(
            id=response_id,
            created=completion_time,
            model=request.model or "echogpt-1.0",
            choices=[
                ChatChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=response_content),
                    finish_reason="stop",
                )
            ],
            usage=ChatUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
        )

    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/v1/intent/analyze", response_model=IntentAnalysisResponse)
async def analyze_intent(request: IntentAnalysisRequest):
    """Intent 분석 API"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    try:
        result = await pipeline.analyze_intent(request.text, request.context or {})

        return IntentAnalysisResponse(
            intent=result.intent,
            confidence=result.confidence,
            summary=result.summary,
            tags=result.tags,
            safety=result.safety,
            source=result.source,
            latency_ms=result.latency_ms,
            model_available=result.model_available,
        )

    except Exception as e:
        logger.error(f"Intent analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/v1/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """시스템 상태 조회"""
    try:
        pipeline_status = (
            pipeline.get_pipeline_status()
            if pipeline
            else {"error": "Pipeline not initialized"}
        )

        trainer_status = None
        if trainer:
            trainer_status = trainer.get_training_info()

        return SystemStatusResponse(
            status="healthy" if pipeline else "degraded",
            pipeline=pipeline_status,
            metrics=pipeline_status.get("metrics", {}),
            trainer=trainer_status,
        )

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@app.post("/v1/system/train")
async def trigger_training(background_tasks: BackgroundTasks):
    """온라인 학습 트리거"""
    if not trainer:
        raise HTTPException(status_code=503, detail="Trainer not available")

    # Metrics 인스턴스 가져오기 (pipeline에서 참조)
    pipeline_instance = get_global_pipeline()
    metrics_instance = getattr(pipeline_instance, "metrics", None)

    async def run_training():
        try:
            result = trainer.train_once()
            logger.info(f"Training completed: {result}")

            # F1 점수를 metrics에 기록
            if metrics_instance and result.get("f1_macro") is not None:
                metrics_instance.set_student_f1(result.get("f1_macro"))
                logger.info(
                    f"Updated student F1 estimate: {result.get('f1_macro'):.3f}"
                )

            # 성공적으로 학습되었으면 Student 모델 리로드
            if result.get("trained") and result.get("status") == "hotswapped":
                pipeline.reload_student_model()
                logger.info("Student model hot-swapped successfully")

        except Exception as e:
            logger.error(f"Background training failed: {e}")

    background_tasks.add_task(run_training)
    return {"message": "Training started in background", "status": "accepted"}


@app.post("/v1/system/reload")
async def reload_student_model():
    """Student 모델 리로드"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    try:
        success = pipeline.reload_student_model()
        return {
            "success": success,
            "message": (
                "Student model reloaded successfully" if success else "Reload failed"
            ),
        }
    except Exception as e:
        logger.error(f"Model reload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(e)}")


@app.get("/echo-gpt/metrics-prom")
def get_metrics_prom():
    """Prometheus exposition format metrics"""
    if not pipeline:
        return Response(
            content="# No pipeline available\n", media_type="text/plain; version=0"
        )

    metrics_instance = getattr(pipeline, "metrics", None)
    if not metrics_instance:
        return Response(
            content="# No metrics available\n", media_type="text/plain; version=0"
        )

    try:
        prom_text = metrics_instance.export_prometheus()
        return Response(content=prom_text, media_type="text/plain; version=0")
    except Exception as e:
        logger.error(f"Prometheus export failed: {e}")
        return Response(
            content="# Metrics export error\n", media_type="text/plain; version=0"
        )


# 개발용 헬퍼 엔드포인트
@app.get("/v1/debug/config")
async def get_config():
    """설정 조회 (개발용)"""
    if not cfg:
        raise HTTPException(status_code=503, detail="Configuration not loaded")

    # 민감한 정보 제외
    debug_config = dict(cfg)
    if "teacher" in debug_config:
        debug_config["teacher"] = {**debug_config["teacher"], "api_key": "***masked***"}

    return debug_config


@app.get("/v1/debug/labels")
async def get_intent_labels():
    """Intent 라벨 목록 조회"""
    try:
        labels_file = "config/intent_labels.json"
        if os.path.exists(labels_file):
            import json

            with open(labels_file, encoding="utf-8") as f:
                labels = json.load(f)
            return {"labels": labels, "count": len(labels)}
        else:
            return {"error": "Labels file not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load labels: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    # 개발 모드 설정
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    port = int(os.getenv("PORT", 9001))  # EchoGPT API 포트
    host = os.getenv("HOST", "127.0.0.1")

    logger.info(f"Starting EchoGPT server on {host}:{port}")

    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=True,  # 개발용
        reload_dirs=[".", "intent", "core", "ops"],
    )
