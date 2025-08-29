#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGPT API Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class ChatIn(BaseModel):
    """Chat input request"""

    text: str
    session_id: Optional[str] = None
    mode: Optional[str] = None  # cloud_mimic, local_first


class ToolCall(BaseModel):
    """Tool execution call"""

    tool: str
    args: Dict[str, Any]
    timeout_ms: Optional[int] = 2500


class IntentResult(BaseModel):
    """Intent analysis result"""

    intent: str
    confidence: float
    summary: str
    tags: List[str] = []
    safety: List[str] = []


class EchoReply(BaseModel):
    """EchoGPT response"""

    lead: str  # 상황-공감-행동 3박자 리드
    actions: List[str] = []  # 액션 리스트
    cards: List[Dict[str, Any]] = []  # 도구 결과 카드
    citations: List[Dict[str, Any]] = []  # 인용 정보
    trace_id: str  # 추적 ID
    route: str  # 선택된 라우트
    intent: IntentResult  # Intent 분석 결과
    processing_time_ms: int  # 처리 시간


class MetricsSnapshot(BaseModel):
    """Metrics snapshot"""

    count: int
    avg_ttl_ms: int
    intent_agree_rate: float
    tool_success_rate: float
    uptime_seconds: int
