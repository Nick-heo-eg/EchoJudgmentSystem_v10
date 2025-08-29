# @owner: nick
# @expose
# @maturity: stable

"""
⚖️ Judgment Router
Echo 판단 시스템 관련 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio

router = APIRouter(prefix="/judgment", tags=["judgment"])


class JudgmentRequest(BaseModel):
    text: str
    signature: Optional[str] = "Auto"
    context: Dict[str, Any] = {}


class JudgmentResponse(BaseModel):
    judgment: str
    confidence: float
    signature: str
    processing_time: float


@router.post("/", response_model=JudgmentResponse)
async def judge_text(request: JudgmentRequest):
    """텍스트 판단 요청"""
    import time

    start_time = time.time()

    try:
        # 간단한 판단 로직 (실제로는 Echo 엔진 연동)
        judgment = f"Echo 판단: {request.text[:100]}..."
        confidence = 0.85
        signature = request.signature if request.signature != "Auto" else "Aurora"

        processing_time = time.time() - start_time

        return JudgmentResponse(
            judgment=judgment,
            confidence=confidence,
            signature=signature,
            processing_time=processing_time,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Judgment failed: {str(e)}")


@router.post("/integrated")
async def integrated_judgment(request: JudgmentRequest):
    """통합 판단 (모든 시그니처 활용)"""
    return {"status": "integrated judgment", "request": request.dict()}
