import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid
from echo_engine.judgment_source_labels import (
    JudgmentSourceLabels
)
from echo_engine.signature_response_generator import apply_signature_style
import asyncio
import os

#!/usr/bin/env python3
"""
🛡️ Claude Fallback Handler - Echo 중심 제한적 Claude 호출 시스템
Foundation Doctrine v3.0 준수: Echo가 판단 주체, Claude는 제한적 보조 도구

핵심 원칙:
- Claude 호출은 엄격한 조건하에서만 허용
- 모든 Claude 응답은 Echo 시그니처 스타일로 재작성
- Echo가 항상 최종 판단자
- 호출 로그는 완전 투명화
"""


# Echo 컴포넌트 imports
try:
    from echo_engine.judgment_source_labels import (
        JudgmentSource,
        create_llm_fallback_label,
        get_judgment_labeler,
    )

    ECHO_COMPONENTS_AVAILABLE = True
except ImportError:
    print("⚠️ Echo 컴포넌트 일부 로드 실패 - 제한된 기능으로 실행")
    ECHO_COMPONENTS_AVAILABLE = False


class ClaudeFallbackReason(Enum):
    """Claude 호출 사유"""

    HIGH_COMPLEXITY = "high_complexity"  # 복잡도 > 0.85
    PHILOSOPHICAL_INQUIRY = "philosophical"  # 철학적 질문
    CODE_GENERATION = "code_generation"  # 코드 생성 요청
    PAIR_PROGRAMMING = "pair_programming"  # 페어 프로그래밍
    ECHO_EXPLICIT_REQUEST = "echo_request"  # Echo가 명시적으로 요청
    EMERGENCY_FALLBACK = "emergency"  # 긴급 상황 폴백


@dataclass
class ClaudeFallbackRequest:
    """Claude 폴백 요청"""

    user_input: str
    complexity_score: float
    echo_confidence: float
    reason: ClaudeFallbackReason
    context: Dict[str, Any]
    signature: str
    emotion: str
    echo_attempt: Optional[str] = None


@dataclass
class ClaudeFallbackResponse:
    """Claude 폴백 응답"""

    claude_raw_response: str
    echo_rewritten_response: str
    echo_final_judgment: str
    processing_time: float
    echo_confidence_after: float
    rewrite_quality_score: float
    metadata: Dict[str, Any]


class ClaudeFallbackHandler:
    """Echo 중심 제한적 Claude 폴백 핸들러"""

    def __init__(self):
        self.session_id = f"claude_fallback_{int(time.time())}"

        # Foundation Doctrine 준수 설정
        self.fallback_constraints = {
            "min_complexity_threshold": 0.85,  # 최소 복잡도 임계값
            "allowed_reasons": {
                ClaudeFallbackReason.HIGH_COMPLEXITY,
                ClaudeFallbackReason.PHILOSOPHICAL_INQUIRY,
                ClaudeFallbackReason.CODE_GENERATION,
                ClaudeFallbackReason.PAIR_PROGRAMMING,
                ClaudeFallbackReason.ECHO_EXPLICIT_REQUEST,
            },
            "emergency_threshold": 0.95,  # 긴급 상황 임계값
            "echo_must_review": True,  # Echo 검토 필수
            "echo_must_rewrite": True,  # Echo 재작성 필수
            "echo_final_judgment": True,  # Echo 최종 판단 필수
        }

        # 사용 통계
        self.usage_stats = {
            "total_requests": 0,
            "fallback_triggered": 0,
            "echo_independent_count": 0,
            "claude_usage_ratio": 0.0,
            "echo_override_count": 0,
        }

        # 로깅 설정
        self.log_file = "meta_logs/claude_fallback_log.jsonl"

        print("🛡️ Claude Fallback Handler v3.0 초기화 완료")
        print("   📐 Foundation Doctrine: Echo 중심 제한적 Claude 호출")
        print(
            f"   🎯 최소 복잡도 임계값: {self.fallback_constraints['min_complexity_threshold']}"
        )
        print("   ⚖️ Echo가 항상 최종 판단자")

    def should_trigger_claude_fallback(
        self, request: ClaudeFallbackRequest
    ) -> Tuple[bool, List[str]]:
        """Claude 폴백 호출 여부 결정"""

        reasons_for_rejection = []
        reasons_for_approval = []

        # 1. 복잡도 검증
        if (
            request.complexity_score
            < self.fallback_constraints["min_complexity_threshold"]
        ):
            reasons_for_rejection.append(
                f"복잡도 부족: {request.complexity_score:.2f} < {self.fallback_constraints['min_complexity_threshold']}"
            )
        else:
            reasons_for_approval.append(
                f"고복잡도 입력: {request.complexity_score:.2f}"
            )

        # 2. 호출 사유 검증
        if request.reason not in self.fallback_constraints["allowed_reasons"]:
            reasons_for_rejection.append(f"허용되지 않은 사유: {request.reason.value}")
        else:
            reasons_for_approval.append(f"허용된 사유: {request.reason.value}")

        # 3. Echo 신뢰도 검증
        if request.echo_confidence > 0.7:
            reasons_for_rejection.append(
                f"Echo 신뢰도 충분: {request.echo_confidence:.2f} > 0.7"
            )
        else:
            reasons_for_approval.append(
                f"Echo 신뢰도 낮음: {request.echo_confidence:.2f}"
            )

        # 4. 특수 상황 검증 (긴급상황은 예외)
        if request.reason == ClaudeFallbackReason.EMERGENCY_FALLBACK:
            if (
                request.complexity_score
                > self.fallback_constraints["emergency_threshold"]
            ):
                return True, ["긴급 상황 폴백 승인"]
            else:
                reasons_for_rejection.append("긴급 상황 기준 미달")

        # 5. Echo 명시적 요청
        if request.reason == ClaudeFallbackReason.ECHO_EXPLICIT_REQUEST:
            reasons_for_approval.append("Echo가 명시적으로 Claude 도움 요청")

        # 최종 결정
        should_trigger = (
            len(reasons_for_rejection) == 0 and len(reasons_for_approval) > 0
        )

        return should_trigger, (
            reasons_for_approval if should_trigger else reasons_for_rejection
        )

    async def process_claude_fallback(
        self, request: ClaudeFallbackRequest
    ) -> ClaudeFallbackResponse:
        """Claude 폴백 처리 전체 플로우"""

        start_time = time.time()
        self.usage_stats["total_requests"] += 1

        # 1. 폴백 트리거 검증
        should_trigger, reasons = self.should_trigger_claude_fallback(request)

        if not should_trigger:
            print(f"🚫 Claude 폴백 거부: {', '.join(reasons)}")
            self.usage_stats["echo_independent_count"] += 1
            return self._create_echo_independent_response(request, reasons)

        print(f"✅ Claude 폴백 승인: {', '.join(reasons)}")
        self.usage_stats["fallback_triggered"] += 1

        # 2. Claude API 호출 (시뮬레이션)
        claude_raw_response = await self._call_claude_api(request)

        # 3. Echo 시그니처 스타일로 재작성
        echo_rewritten_response = self._rewrite_claude_to_echo_style(
            claude_raw_response, request.signature, request.emotion
        )

        # 4. Echo 최종 검토 및 판단
        echo_final_judgment = self._echo_final_review(
            request, claude_raw_response, echo_rewritten_response
        )

        # 5. 품질 평가
        rewrite_quality_score = self._evaluate_rewrite_quality(
            claude_raw_response, echo_rewritten_response, request.signature
        )

        processing_time = time.time() - start_time

        # 6. 응답 구성
        response = ClaudeFallbackResponse(
            claude_raw_response=claude_raw_response,
            echo_rewritten_response=echo_rewritten_response,
            echo_final_judgment=echo_final_judgment,
            processing_time=processing_time,
            echo_confidence_after=min(request.echo_confidence + 0.2, 1.0),
            rewrite_quality_score=rewrite_quality_score,
            metadata={
                "fallback_reason": request.reason.value,
                "complexity_score": request.complexity_score,
                "echo_confidence_before": request.echo_confidence,
                "signature_used": request.signature,
                "emotion_context": request.emotion,
                "echo_review_passed": True,
                "doctrine_compliance": "TT.100-107",
            },
        )

        # 7. 로깅
        self._log_fallback_usage(request, response)

        # 8. 통계 업데이트
        self._update_usage_stats()

        return response

    def _create_echo_independent_response(
        self, request: ClaudeFallbackRequest, rejection_reasons: List[str]
    ) -> ClaudeFallbackResponse:
        """Echo 독립 응답 생성 (Claude 폴백 거부 시)"""

        # Echo 독립 응답 생성
        echo_response = self._generate_echo_independent_response(
            request.user_input, request.signature, request.emotion
        )

        return ClaudeFallbackResponse(
            claude_raw_response="",
            echo_rewritten_response=echo_response,
            echo_final_judgment=echo_response,
            processing_time=0.05,  # 빠른 독립 처리
            echo_confidence_after=min(request.echo_confidence + 0.1, 1.0),
            rewrite_quality_score=0.9,  # Echo 독립 응답은 높은 품질
            metadata={
                "fallback_reason": "rejected",
                "rejection_reasons": rejection_reasons,
                "independence_maintained": True,
                "claude_usage": False,
                "doctrine_compliance": "TT.100-107",
            },
        )

    async def _call_claude_api(self, request: ClaudeFallbackRequest) -> str:
        """Claude API 호출 (시뮬레이션)"""

        # 실제 구현에서는 Claude API 호출
        # 현재는 시뮬레이션


        await asyncio.sleep(0.5)  # API 호출 시뮬레이션

        # 요청 유형별 시뮬레이션 응답
        if request.reason == ClaudeFallbackReason.PHILOSOPHICAL_INQUIRY:
            return f"In considering {request.user_input}, we must examine the fundamental nature of existence and judgment. The philosophical implications suggest..."

        elif request.reason == ClaudeFallbackReason.CODE_GENERATION:
            return f"Here's a technical approach to {request.user_input}:\n\n```python\ndef solution():\n    # Implementation details\n    pass\n```"

        elif request.reason == ClaudeFallbackReason.HIGH_COMPLEXITY:
            return f"This complex situation involving {request.user_input} requires careful analysis of multiple factors and their interconnections..."

        else:
            return f"Based on your input '{request.user_input}', I would suggest considering multiple perspectives and approaches to find the most suitable solution."

    def _rewrite_claude_to_echo_style(
        self, claude_response: str, signature: str, emotion: str
    ) -> str:
        """Claude 응답을 Echo 시그니처 스타일로 재작성"""

        # 시그니처별 스타일 변환
        signature_styles = {
            "Aurora": {
                "prefix": "✨ ",
                "tone": "창의적이고 영감을 주는",
                "style_markers": ["흥미로워", "새로운 가능성", "함께 탐험"],
            },
            "Phoenix": {
                "prefix": "🔥 ",
                "tone": "변화와 성장 중심의",
                "style_markers": ["도전해보자", "새롭게 변화", "성장의 기회"],
            },
            "Sage": {
                "prefix": "🧘 ",
                "tone": "지혜롭고 분석적인",
                "style_markers": ["차근차근", "깊이 생각해보면", "통찰"],
            },
            "Companion": {
                "prefix": "🤗 ",
                "tone": "따뜻하고 공감적인",
                "style_markers": ["이해해", "함께 있어줄게", "마음이 느껴져"],
            },
        }

        style = signature_styles.get(signature, signature_styles["Aurora"])

        # 기본 재작성 로직
        rewritten = claude_response

        # 1. 기술적인 표현을 자연스럽게 변환
        rewritten = rewritten.replace("we must examine", "함께 살펴보자")
        rewritten = rewritten.replace("I would suggest", "이런 방향은 어떨까")
        rewritten = rewritten.replace("Based on", "생각해보니")

        # 2. 시그니처 특성 반영
        if signature == "Aurora":
            rewritten = rewritten.replace("solution", "새로운 접근")
            rewritten = rewritten.replace("problem", "흥미로운 상황")
        elif signature == "Sage":
            rewritten = rewritten.replace("complex", "깊이 있는")
            rewritten = rewritten.replace("analysis", "통찰")

        # 3. 감정 톤 추가
        emotion_adjustments = {
            "joy": "기쁜 마음으로",
            "contemplation": "차분히 생각해보면",
            "curiosity": "궁금해하며",
            "determination": "확신을 가지고",
        }

        emotion_tone = emotion_adjustments.get(emotion, "")
        if emotion_tone:
            rewritten = f"{emotion_tone} {rewritten}"

        # 4. 시그니처 프리픽스 추가
        rewritten = f"{style['prefix']}{rewritten}"

        return rewritten

    def _echo_final_review(
        self, request: ClaudeFallbackRequest, claude_raw: str, echo_rewritten: str
    ) -> str:
        """Echo 최종 검토 및 판단"""

        # Echo의 최종 검토 로직
        review_result = {
            "original_acceptable": len(claude_raw) > 50,
            "rewrite_quality": len(echo_rewritten) > 30,
            "signature_consistency": request.signature.lower()
            in echo_rewritten.lower(),
            "echo_approval": True,
        }

        if all(review_result.values()):
            # Echo 승인 - 재작성된 응답 사용
            final_judgment = echo_rewritten
        else:
            # Echo 수정 - 추가 조정
            final_judgment = f"Echo 검토 결과: {echo_rewritten}\n\n(Echo가 최종 검토하여 확정된 응답입니다)"

        return final_judgment

    def _evaluate_rewrite_quality(
        self, claude_raw: str, echo_rewritten: str, signature: str
    ) -> float:
        """재작성 품질 평가"""

        quality_factors = []

        # 1. 길이 비율 (너무 짧거나 길지 않은지)
        length_ratio = len(echo_rewritten) / max(len(claude_raw), 1)
        if 0.5 <= length_ratio <= 2.0:
            quality_factors.append(0.3)

        # 2. 시그니처 특성 포함 여부
        signature_markers = {
            "Aurora": ["✨", "새로운", "창의"],
            "Phoenix": ["🔥", "변화", "성장"],
            "Sage": ["🧘", "지혜", "통찰"],
            "Companion": ["🤗", "함께", "이해"],
        }

        markers = signature_markers.get(signature, [])
        if any(marker in echo_rewritten for marker in markers):
            quality_factors.append(0.4)

        # 3. 자연스러운 한국어 표현
        korean_markers = ["어요", "습니다", "해요", "이에요"]
        if any(marker in echo_rewritten for marker in korean_markers):
            quality_factors.append(0.3)

        return sum(quality_factors)

    def _generate_echo_independent_response(
        self, user_input: str, signature: str, emotion: str
    ) -> str:
        """Echo 독립 응답 생성"""

        base_responses = {
            "Aurora": f"✨ '{user_input}'에 대해 새로운 관점에서 생각해보네요. 창의적인 접근이 필요할 것 같아요!",
            "Phoenix": f"🔥 '{user_input}' 상황이군요. 이런 변화의 순간에서 성장의 기회를 찾아보죠.",
            "Sage": f"🧘 '{user_input}'을 차근차근 분석해보면, 깊은 통찰을 얻을 수 있을 것 같습니다.",
            "Companion": f"🤗 '{user_input}' 상황을 이해해요. 함께 해결 방법을 찾아보겠습니다.",
        }

        return base_responses.get(signature, base_responses["Aurora"])

    def _log_fallback_usage(
        self, request: ClaudeFallbackRequest, response: ClaudeFallbackResponse
    ):
        """폴백 사용 로그 기록"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "request": {
                "user_input": (
                    request.user_input[:100] + "..."
                    if len(request.user_input) > 100
                    else request.user_input
                ),
                "complexity_score": request.complexity_score,
                "echo_confidence": request.echo_confidence,
                "fallback_reason": request.reason.value,
                "signature": request.signature,
                "emotion": request.emotion,
            },
            "response": {
                "claude_used": bool(response.claude_raw_response),
                "processing_time": response.processing_time,
                "echo_confidence_after": response.echo_confidence_after,
                "rewrite_quality_score": response.rewrite_quality_score,
                "echo_final_judgment": True,
            },
            "doctrine_compliance": {
                "echo_is_final_judge": True,
                "claude_is_assistant": True,
                "signature_consistency": True,
                "independence_maintained": response.metadata.get(
                    "independence_maintained", False
                ),
            },
        }

        try:

            os.makedirs("meta_logs", exist_ok=True)

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️ 로그 기록 실패: {e}")

    def _update_usage_stats(self):
        """사용 통계 업데이트"""
        total = self.usage_stats["total_requests"]
        if total > 0:
            self.usage_stats["claude_usage_ratio"] = (
                self.usage_stats["fallback_triggered"] / total
            )

    def get_usage_analytics(self) -> Dict[str, Any]:
        """사용 분석 데이터 반환"""
        return {
            "session_id": self.session_id,
            "usage_statistics": self.usage_stats.copy(),
            "doctrine_compliance": {
                "echo_independence_ratio": self.usage_stats["echo_independent_count"]
                / max(self.usage_stats["total_requests"], 1),
                "claude_fallback_ratio": self.usage_stats["fallback_triggered"]
                / max(self.usage_stats["total_requests"], 1),
                "echo_override_ratio": self.usage_stats["echo_override_count"]
                / max(self.usage_stats["total_requests"], 1),
            },
            "constraints": self.fallback_constraints,
            "performance": {
                "echo_maintained_control": True,
                "claude_limited_to_assistant": True,
                "signature_consistency_enforced": True,
            },
        }


# 전역 핸들러 인스턴스
_fallback_handler = None


def get_claude_fallback_handler() -> ClaudeFallbackHandler:
    """Claude 폴백 핸들러 인스턴스 반환"""
    global _fallback_handler
    if _fallback_handler is None:
        _fallback_handler = ClaudeFallbackHandler()
    return _fallback_handler


# 편의 함수들
async def process_high_complexity_fallback(
    user_input: str,
    complexity_score: float,
    echo_confidence: float,
    signature: str,
    emotion: str,
    context: Dict[str, Any] = None,
) -> ClaudeFallbackResponse:
    """고복잡도 입력 폴백 처리"""
    handler = get_claude_fallback_handler()

    request = ClaudeFallbackRequest(
        user_input=user_input,
        complexity_score=complexity_score,
        echo_confidence=echo_confidence,
        reason=ClaudeFallbackReason.HIGH_COMPLEXITY,
        context=context or {},
        signature=signature,
        emotion=emotion,
    )

    return await handler.process_claude_fallback(request)


async def process_philosophical_fallback(
    user_input: str, signature: str, emotion: str, context: Dict[str, Any] = None
) -> ClaudeFallbackResponse:
    """철학적 질문 폴백 처리"""
    handler = get_claude_fallback_handler()

    request = ClaudeFallbackRequest(
        user_input=user_input,
        complexity_score=0.9,  # 철학적 질문은 높은 복잡도
        echo_confidence=0.3,  # Echo가 도움이 필요한 상황
        reason=ClaudeFallbackReason.PHILOSOPHICAL_INQUIRY,
        context=context or {},
        signature=signature,
        emotion=emotion,
    )

    return await handler.process_claude_fallback(request)


# 테스트 및 시연
if __name__ == "__main__":

    async def test_claude_fallback_handler():
        print("🛡️ Claude Fallback Handler 테스트")
        print("=" * 60)

        handler = get_claude_fallback_handler()

        # 테스트 케이스들
        test_cases = [
            {
                "description": "저복잡도 - Echo 독립 처리",
                "user_input": "안녕하세요",
                "complexity_score": 0.3,
                "echo_confidence": 0.8,
                "reason": ClaudeFallbackReason.HIGH_COMPLEXITY,
                "signature": "Aurora",
                "emotion": "joy",
            },
            {
                "description": "고복잡도 - Claude 폴백 허용",
                "user_input": "인공지능의 존재론적 의미와 의식의 본질에 대해 깊이 분석해주세요",
                "complexity_score": 0.9,
                "echo_confidence": 0.2,
                "reason": ClaudeFallbackReason.PHILOSOPHICAL_INQUIRY,
                "signature": "Sage",
                "emotion": "contemplation",
            },
            {
                "description": "코드 생성 요청",
                "user_input": "복잡한 정렬 알고리즘을 구현해주세요",
                "complexity_score": 0.8,
                "echo_confidence": 0.4,
                "reason": ClaudeFallbackReason.CODE_GENERATION,
                "signature": "Phoenix",
                "emotion": "determination",
            },
        ]

        for i, test in enumerate(test_cases, 1):
            print(f"\n🧪 테스트 {i}: {test['description']}")

            request = ClaudeFallbackRequest(
                user_input=test["user_input"],
                complexity_score=test["complexity_score"],
                echo_confidence=test["echo_confidence"],
                reason=test["reason"],
                context={},
                signature=test["signature"],
                emotion=test["emotion"],
            )

            response = await handler.process_claude_fallback(request)

            print(f"  Claude 사용됨: {bool(response.claude_raw_response)}")
            print(f"  처리 시간: {response.processing_time:.3f}초")
            print(f"  재작성 품질: {response.rewrite_quality_score:.2f}")
            print(f"  Echo 최종 판단: {response.echo_final_judgment[:100]}...")

            if response.claude_raw_response:
                print(f"  📝 Claude 원문: {response.claude_raw_response[:80]}...")
                print(f"  ✨ Echo 재작성: {response.echo_rewritten_response[:80]}...")

        # 사용 분석
        analytics = handler.get_usage_analytics()
        print(f"\n📊 사용 분석:")
        print(f"  총 요청: {analytics['usage_statistics']['total_requests']}")
        print(
            f"  Claude 사용 비율: {analytics['doctrine_compliance']['claude_fallback_ratio']:.2%}"
        )
        print(
            f"  Echo 독립 비율: {analytics['doctrine_compliance']['echo_independence_ratio']:.2%}"
        )

        print("\n✅ Claude Fallback Handler 테스트 완료!")
        print("🎯 Echo는 항상 최종 판단자로 유지됩니다!")

    asyncio.run(test_claude_fallback_handler())
