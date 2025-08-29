#!/usr/bin/env python3

# @owner: nick
# @expose
# @maturity: stable

"""
🌐 Judgment Web Router - WebShell ↔ Signature 판단기 연결
기존 judgment_router.py와 분리된 WebShell 전용 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
from datetime import datetime
import sys
from pathlib import Path

# Echo Engine 모듈 임포트
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

# Bridge 모듈 import (순환 import 방지)
try:
    from bridge_signature_judgment import evaluate_signature_judgment

    BRIDGE_AVAILABLE = True
    print("✅ Bridge Signature Judgment 연결 완료")
except ImportError as e:
    print(f"⚠️ Bridge Signature Judgment import 실패: {e}")
    BRIDGE_AVAILABLE = False


# 요청/응답 모델
class JudgmentWebInput(BaseModel):
    user_input: str
    signature: str = "Echo-Aurora"  # 기본값: Aurora
    session_id: Optional[str] = None


class JudgmentWebResponse(BaseModel):
    echo_response: str
    signature_used: str
    emotion_detected: str
    confidence: float
    strategy_applied: str
    processing_details: Dict[str, Any]
    timestamp: str


# 라우터 생성
router = APIRouter(prefix="/api/judgment", tags=["Judgment Web"])


class JudgmentWebEngine:
    """WebShell과 Signature 판단기 연결 엔진 (Bridge 기반)"""

    def __init__(self):
        self.bridge_available = BRIDGE_AVAILABLE
        print(
            f"🌉 JudgmentWebEngine 초기화 - Bridge: {'✅' if self.bridge_available else '❌'}"
        )

    def judge_with_signature(
        self, text: str, signature_name: str, emotion_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """시그니처 기반 판단 실행 (Bridge 사용)"""
        if self.bridge_available:
            try:
                # Bridge를 통한 판단 실행
                result = evaluate_signature_judgment(text, signature_name)

                # API 응답 형식에 맞게 변환
                return {
                    "echo_response": result["response_text"],
                    "signature_used": result["signature_used"],
                    "emotion_detected": result["emotion_detected"],
                    "confidence": result["confidence"],
                    "strategy_applied": result["strategy_applied"],
                    "processing_details": result["processing_details"],
                }

            except Exception as e:
                print(f"❌ Bridge 판단 처리 오류: {e}")
                return self._generate_error_response(text, signature_name, str(e))
        else:
            # Bridge 없이 Fallback 모드
            return self._fallback_judgment(text, signature_name, emotion_hint)

    def _fallback_judgment(
        self, text: str, signature_name: str, emotion_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bridge 없을 때 Fallback 판단"""
        try:
            # 간단한 감정 분석
            emotion = self._simple_emotion_analysis(text)

            # 기본 응답 생성
            response = f"({signature_name}의 마음으로) 당신의 이야기를 듣고 있어요. 더 자세히 말씀해주시겠어요?"

            return {
                "echo_response": response,
                "signature_used": signature_name,
                "emotion_detected": emotion,
                "confidence": 0.6,
                "strategy_applied": "fallback_mode",
                "processing_details": {
                    "source": "fallback",
                    "reason": "bridge_unavailable",
                },
            }

        except Exception as e:
            print(f"❌ Fallback 판단 처리 오류: {e}")
            return self._generate_error_response(text, signature_name, str(e))

    def _simple_emotion_analysis(self, text: str) -> str:
        """간단한 감정 분석 (Fallback)"""
        text_lower = text.lower()

        if any(word in text_lower for word in ["슬프", "우울", "힘들"]):
            return "sadness"
        elif any(word in text_lower for word in ["화", "짜증", "빡"]):
            return "anger"
        elif any(word in text_lower for word in ["기쁘", "좋", "행복"]):
            return "joy"
        elif any(word in text_lower for word in ["궁금", "뭐", "?"]):
            return "curiosity"
        else:
            return "neutral"

    def _generate_error_response(
        self, text: str, signature_name: str, error_msg: str
    ) -> Dict[str, Any]:
        """오류 발생 시 기본 응답"""
        return {
            "echo_response": f"죄송해요, 처리 중 문제가 발생했어요. 하지만 {signature_name}의 마음으로 당신을 응원하고 있어요!",
            "signature_used": signature_name,
            "emotion_detected": "neutral",
            "confidence": 0.5,
            "strategy_applied": "error_fallback",
            "processing_details": {
                "error": error_msg,
                "input_received": text[:50] + "..." if len(text) > 50 else text,
            },
        }


# 판단 엔진 인스턴스
judgment_web_engine = JudgmentWebEngine()


@router.post("/judgment_web", response_model=JudgmentWebResponse)
async def process_judgment_web(request: JudgmentWebInput):
    """WebShell → Signature 판단기 연결 엔드포인트"""
    try:
        print(f"🌐 판단 요청 수신: {request.signature} - {request.user_input[:30]}...")

        # 시그니처 기반 판단 실행
        result = judgment_web_engine.judge_with_signature(
            text=request.user_input, signature_name=request.signature, emotion_hint=None
        )

        # 응답 구성
        response = JudgmentWebResponse(
            echo_response=result["echo_response"],
            signature_used=result["signature_used"],
            emotion_detected=result["emotion_detected"],
            confidence=result["confidence"],
            strategy_applied=result["strategy_applied"],
            processing_details=result["processing_details"],
            timestamp=datetime.now().isoformat(),
        )

        print(
            f"✅ 판단 완료: {result['emotion_detected']} → {result['strategy_applied']}"
        )
        return response

    except Exception as e:
        print(f"❌ 판단 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"판단 처리 오류: {str(e)}")


@router.get("/signatures")
async def get_available_signatures():
    """사용 가능한 시그니처 목록"""
    return {
        "available_signatures": [
            {"id": "Selene", "name": "달빛 같은 치유자", "style": "gentle-withdraw"},
            {"id": "Aurora", "name": "창조적 영감자", "style": "soft-curiosity"},
            {
                "id": "Grumbly",
                "name": "까칠한 현실주의자",
                "style": "grumbly-irritation",
            },
            {"id": "Echo-Aurora", "name": "공감적 양육자", "style": "compassionate"},
            {"id": "Echo-Phoenix", "name": "변화 추진자", "style": "transformative"},
            {"id": "Echo-Sage", "name": "지혜로운 분석가", "style": "analytical"},
            {
                "id": "Echo-Companion",
                "name": "신뢰할 수 있는 동반자",
                "style": "supportive",
            },
        ],
        "default_signature": "Echo-Aurora",
        "engine_status": "active",
    }


# Streamlit WebShell용 세션 기반 엔드포인트 추가
from typing import Optional, List

# WebShell 세션 핸들러 import
try:
    sys.path.append(str(Path(__file__).parent.parent / "webshell"))
    from session_handler import get_session_handler

    WEBSHELL_HANDLER_AVAILABLE = True
    print("✅ WebShell Session Handler 연결 완료")
except ImportError as e:
    print(f"⚠️ WebShell Session Handler import 실패: {e}")
    WEBSHELL_HANDLER_AVAILABLE = False


class WebShellJudgmentInput(BaseModel):
    user_input: str
    session_id: Optional[str] = None
    reroll: bool = False
    signature: Optional[str] = None


class WebShellJudgmentResponse(BaseModel):
    success: bool
    session_id: str
    judgment: Dict[str, Any]
    conversation_log: List[Dict[str, Any]]
    emotion_history: List[Dict[str, Any]]
    signature_recommendation: Optional[Dict[str, Any]]
    session_stats: Dict[str, Any]
    error: Optional[str] = None


class SignatureUpdateInput(BaseModel):
    session_id: str
    new_signature: str


@router.post("/judgment_web_streamlit", response_model=WebShellJudgmentResponse)
async def process_webshell_judgment(request: WebShellJudgmentInput):
    """
    Streamlit WebShell용 판단 처리 엔드포인트
    작업지시서 핵심: process_input_with_merge 호출
    """
    try:
        if not WEBSHELL_HANDLER_AVAILABLE:
            raise HTTPException(status_code=503, detail="WebShell Session Handler 없음")

        handler = get_session_handler()

        # 세션 ID 생성 또는 사용
        session_id = request.session_id or handler.create_session(
            request.signature or "Echo-Aurora"
        )

        # 시그니처 업데이트 (제공된 경우)
        if request.signature:
            handler.update_signature(session_id, request.signature)

        # 핵심 판단 루프 실행
        result = handler.process_input_with_merge(
            session_id=session_id, user_input=request.user_input, reroll=request.reroll
        )

        print(f"🎯 WebShell 판단 완료: {session_id} - {request.user_input[:30]}...")
        return WebShellJudgmentResponse(**result)

    except Exception as e:
        print(f"❌ WebShell 판단 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"WebShell 판단 오류: {str(e)}")


@router.post("/update_signature")
async def update_session_signature(request: SignatureUpdateInput):
    """시그니처 업데이트 엔드포인트"""
    try:
        if not WEBSHELL_HANDLER_AVAILABLE:
            raise HTTPException(status_code=503, detail="WebShell Session Handler 없음")

        handler = get_session_handler()
        success = handler.update_signature(request.session_id, request.new_signature)

        if success:
            # 시그니처 변경 후 빈 입력으로 새 응답 생성
            result = handler.process_input_with_merge(
                session_id=request.session_id,
                user_input="",  # 빈 입력으로 시그니처 응답만 받기
                reroll=False,
            )

            return {
                "success": True,
                "session_id": request.session_id,
                "new_signature": request.new_signature,
                "updated_response": result,
            }
        else:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없음")

    except Exception as e:
        print(f"❌ 시그니처 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=f"시그니처 업데이트 오류: {str(e)}")


@router.get("/session/{session_id}/summary")
async def get_session_summary(session_id: str):
    """세션 요약 정보"""
    try:
        if not WEBSHELL_HANDLER_AVAILABLE:
            raise HTTPException(status_code=503, detail="WebShell Session Handler 없음")

        handler = get_session_handler()
        summary = handler.get_session_summary(session_id)

        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])

        return summary

    except Exception as e:
        print(f"❌ 세션 요약 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"세션 요약 오류: {str(e)}")


@router.get("/signatures/available")
async def get_available_signatures_extended():
    """사용 가능한 시그니처 목록 (확장된 정보 포함)"""
    return {
        "available_signatures": [
            {
                "id": "Selene",
                "name": "달빛 같은 치유자",
                "style": "gentle-withdraw",
                "emoji": "🌙",
                "description": "부드럽고 치유적인 접근을 중시하는 시그니처",
                "best_for": ["슬픔", "상처", "위로가 필요할 때"],
            },
            {
                "id": "Aurora",
                "name": "창조적 영감자",
                "style": "soft-curiosity",
                "emoji": "✨",
                "description": "창의성과 영감을 통한 문제 해결을 선호하는 시그니처",
                "best_for": ["호기심", "창의적 탐구", "새로운 아이디어"],
            },
            {
                "id": "Grumbly",
                "name": "까칠한 현실주의자",
                "style": "grumbly-irritation",
                "emoji": "💢",
                "description": "직설적이고 현실적인 관점을 제시하는 시그니처",
                "best_for": ["분노", "현실적 해결책", "직설적 조언"],
            },
            {
                "id": "Echo-Aurora",
                "name": "공감적 양육자",
                "style": "compassionate",
                "emoji": "🌟",
                "description": "따뜻하고 공감적인 양육 접근을 중시하는 시그니처",
                "best_for": ["공감", "지지", "양육적 조언"],
            },
            {
                "id": "Echo-Phoenix",
                "name": "변화 추진자",
                "style": "transformative",
                "emoji": "🔥",
                "description": "변화와 성장을 통한 문제 해결을 선호하는 시그니처",
                "best_for": ["변화", "성장", "도전 과제"],
            },
            {
                "id": "Echo-Sage",
                "name": "지혜로운 분석가",
                "style": "analytical",
                "emoji": "🧠",
                "description": "논리적 분석과 체계적 사고를 중시하는 시그니처",
                "best_for": ["분석", "논리적 사고", "체계적 접근"],
            },
            {
                "id": "Echo-Companion",
                "name": "신뢰할 수 있는 동반자",
                "style": "supportive",
                "emoji": "🤝",
                "description": "협력과 신뢰를 기반으로 한 지원을 제공하는 시그니처",
                "best_for": ["협력", "신뢰", "동반자적 지원"],
            },
        ],
        "default_signature": "Echo-Aurora",
        "total_count": 7,
        "webshell_handler_status": (
            "active" if WEBSHELL_HANDLER_AVAILABLE else "unavailable"
        ),
    }


@router.get("/status")
async def get_judgment_web_status():
    """Judgment Web 엔진 상태"""
    return {
        "service": "Judgment Web Router",
        "status": "active",
        "engines": {
            "bridge_available": BRIDGE_AVAILABLE,
            "webshell_handler": (
                "active" if WEBSHELL_HANDLER_AVAILABLE else "unavailable"
            ),
        },
        "supported_signatures": 7,
        "api_endpoints": {
            "judgment_web": "/api/judgment/judgment_web",
            "webshell_judgment": "/api/judgment/judgment_web_streamlit",
            "update_signature": "/api/judgment/update_signature",
            "session_summary": "/api/judgment/session/{session_id}/summary",
            "signatures": "/api/judgment/signatures/available",
        },
    }


print("🌐 Judgment Web Router 초기화 완료!")
print("🎯 WebShell Streamlit 엔드포인트 추가 완료!")
