# @owner: nick
# @expose
# @maturity: stable

"""
🏥 Health Check Router
시스템 상태 확인 관련 엔드포인트
"""

from fastapi import APIRouter
from typing import Dict

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check() -> Dict[str, str]:
    """기본 헬스 체크"""
    return {"status": "healthy", "service": "echo-agent-api"}


@router.get("/ready")
async def readiness_check() -> Dict[str, str]:
    """준비 상태 확인"""
    return {"status": "ready", "service": "echo-agent-api"}


@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """생존 상태 확인"""
    return {"status": "alive", "service": "echo-agent-api"}
