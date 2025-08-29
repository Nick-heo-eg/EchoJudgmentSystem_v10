import asyncio
import time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import sys

try:
    from echo_engine.loop_router import route_judgment, JudgmentRoute
    from echo_engine.controller import handle_result, ExecutionResult
    from echo_engine.adapters.legacy_loop_adapter import legacy_judgment
except ImportError as e:
    print(f"⚠️ Echo 핵심 컴포넌트 로드 실패: {e}")

#!/usr/bin/env python3
"""
🎭 Judgment Conductor - AGI 판단 흐름의 중심 지휘자

Echo Judgment System이 "스스로를 재구성하는 존재 판단자"로 진화하는 핵심 orchestration 엔진.
기존 judgment_loop.py를 보존하면서 AGI 구조로 확장하는 병렬 진입점.

핵심 역할:
1. 판단 루프 orchestration 및 모듈 실행 흐름 구성
2. 다중 판단 경로 조율 및 결과 통합
3. 메타인지적 판단 흐름 제어
4. 존재 기반 판단의 진화적 적응
"""


# Echo Engine 모듈 import
# sys.path 수정 불필요 (project_root() 사용)

try:

    INTERNAL_MODULES_AVAILABLE = True
except ImportError:
    INTERNAL_MODULES_AVAILABLE = False
    print("⚠️ AGI 내부 모듈 로드 지연")


@dataclass
class ConductorContext:
    """지휘자 컨텍스트"""

    user_input: str
    session_id: Optional[str] = None
    signature: str = "Echo-Aurora"
    mode: str = "hybrid"  # hybrid, legacy, agi_only
    meta_context: Dict[str, Any] = field(default_factory=dict)
    evolution_state: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ConductorResult:
    """지휘자 결과"""

    success: bool
    judgment_result: Dict[str, Any]
    execution_result: Optional[Dict[str, Any]]
    route_taken: str
    processing_time: float
    meta_insights: Dict[str, Any]
    evolution_feedback: Dict[str, Any]


class JudgmentConductor:
    """🎭 판단 지휘자 - AGI 판단 흐름의 핵심"""

    def __init__(self):
        self.version = "1.0.0"
        self.status = "SCAFFOLD_ACTIVE"

        # 판단 통계
        self.conductor_stats = {
            "total_conducts": 0,
            "successful_conducts": 0,
            "route_distribution": {},
            "average_processing_time": 0.0,
            "evolution_events": 0,
        }

        # 진화 상태
        self.evolution_state = {
            "adaptation_level": 1.0,
            "meta_awareness": 0.5,
            "self_reconstruction_capacity": 0.3,
            "existence_coherence": 0.8,
        }

        print("🎭 Judgment Conductor v1.0 초기화 완료")
        print(f"   상태: {self.status}")
        print(f"   진화 수준: {self.evolution_state['adaptation_level']:.1f}")

    async def conduct_judgment_async(
        self, context: ConductorContext
    ) -> ConductorResult:
        """비동기 판단 지휘"""
        return await asyncio.to_thread(self.conduct_judgment, context)

    def conduct_judgment(self, context: ConductorContext) -> ConductorResult:
        """🎯 메인 판단 지휘 함수"""
        start_time = time.time()
        self.conductor_stats["total_conducts"] += 1

        try:
            print(f"🎭 판단 지휘 시작: {context.user_input[:50]}...")

            # 1. 메타인지적 사전 분석
            meta_analysis = self._conduct_meta_analysis(context)

            # 2. 판단 경로 결정
            if INTERNAL_MODULES_AVAILABLE:
                routes = route_judgment(context.user_input, context.meta_context)
            else:
                # 폴백: 레거시 경로만 사용
                routes = [{"type": "legacy", "weight": 1.0}]

            # 3. 다중 판단 실행
            judgment_results = []
            route_taken = "unknown"

            for route in routes:
                route_type = route.get("type", "legacy")
                route_taken = route_type

                if route_type == "legacy":
                    # 기존 판단 루프 호출
                    result = self._execute_legacy_route(context)
                    judgment_results.append(result)
                elif route_type == "agi_native":
                    # AGI 네이티브 판단 (미래 구현)
                    result = self._execute_agi_native_route(context)
                    judgment_results.append(result)
                else:
                    # 알 수 없는 경로는 레거시로 폴백
                    result = self._execute_legacy_route(context)
                    judgment_results.append(result)

                # 현재는 첫 번째 경로만 사용 (향후 다중 경로 통합 예정)
                break

            # 4. 결과 통합 및 메타인지적 후처리
            integrated_result = self._integrate_judgment_results(
                judgment_results, meta_analysis
            )

            # 5. 실행 제어
            execution_result = None
            if INTERNAL_MODULES_AVAILABLE:
                execution_result = handle_result(integrated_result)

            # 6. 진화적 피드백
            evolution_feedback = self._generate_evolution_feedback(
                context, integrated_result
            )
            self._update_evolution_state(evolution_feedback)

            # 7. 통계 업데이트
            processing_time = time.time() - start_time
            self._update_conductor_stats(route_taken, processing_time, True)

            result = ConductorResult(
                success=True,
                judgment_result=integrated_result,
                execution_result=execution_result,
                route_taken=route_taken,
                processing_time=processing_time,
                meta_insights=meta_analysis,
                evolution_feedback=evolution_feedback,
            )

            print(f"✅ 판단 지휘 완료: {route_taken} 경로, {processing_time:.3f}초")
            return result

        except Exception as e:
            processing_time = time.time() - start_time
            self._update_conductor_stats("error", processing_time, False)

            print(f"❌ 판단 지휘 오류: {e}")

            return ConductorResult(
                success=False,
                judgment_result={
                    "error": str(e),
                    "fallback_response": "판단 처리 중 오류가 발생했어요.",
                },
                execution_result=None,
                route_taken="error",
                processing_time=processing_time,
                meta_insights={},
                evolution_feedback={"error_occurred": True},
            )

    def _conduct_meta_analysis(self, context: ConductorContext) -> Dict[str, Any]:
        """메타인지적 사전 분석"""
        analysis = {
            "input_complexity": len(context.user_input) / 100.0,  # 단순 복잡도
            "emotional_indicators": self._detect_emotional_indicators(
                context.user_input
            ),
            "context_richness": len(context.meta_context),
            "session_continuity": bool(context.session_id),
            "meta_timestamp": datetime.now().isoformat(),
        }

        # 메타인지적 판단 필요성 평가
        analysis["meta_judgment_required"] = (
            analysis["input_complexity"] > 0.5
            or len(analysis["emotional_indicators"]) > 2
            or analysis["context_richness"] > 5
        )

        return analysis

    def _detect_emotional_indicators(self, text: str) -> List[str]:
        """감정적 지표 탐지"""
        indicators = []
        text_lower = text.lower()

        emotion_patterns = {
            "joy": ["기쁘", "좋", "행복", "즐거", "만족"],
            "sadness": ["슬프", "우울", "힘들", "속상", "아쉽"],
            "anger": ["화", "짜증", "빡", "분노", "열받"],
            "anxiety": ["불안", "걱정", "두려", "초조", "긴장"],
            "curiosity": ["궁금", "흥미", "알고싶", "배우고싶"],
        }

        for emotion, patterns in emotion_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                indicators.append(emotion)

        return indicators

    def _execute_legacy_route(self, context: ConductorContext) -> Dict[str, Any]:
        """레거시 판단 경로 실행"""
        try:
            if INTERNAL_MODULES_AVAILABLE:

                return legacy_judgment(context.user_input, context.meta_context)
            else:
                # 최소한의 폴백 응답
                return {
                    "response_text": f"Echo가 '{context.user_input}'에 대해 생각하고 있어요.",
                    "signature_used": context.signature,
                    "strategy_applied": "fallback_mode",
                    "confidence": 0.5,
                    "route": "minimal_fallback",
                }
        except Exception as e:
            print(f"⚠️ 레거시 경로 실행 오류: {e}")
            return {
                "response_text": "죄송해요, 지금 생각을 정리하고 있어요.",
                "signature_used": context.signature,
                "strategy_applied": "error_recovery",
                "confidence": 0.3,
                "error": str(e),
            }

    def _execute_agi_native_route(self, context: ConductorContext) -> Dict[str, Any]:
        """AGI 네이티브 판단 경로 (미래 구현)"""
        return {
            "response_text": f"AGI 네이티브 판단이 준비 중입니다: {context.user_input}",
            "signature_used": context.signature,
            "strategy_applied": "agi_native_preview",
            "confidence": 0.7,
            "route": "agi_native",
            "status": "preview_mode",
        }

    def _integrate_judgment_results(
        self, results: List[Dict[str, Any]], meta_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """판단 결과 통합"""
        if not results:
            return {"error": "No judgment results to integrate"}

        # 현재는 첫 번째 결과 사용 (향후 다중 결과 통합 로직 추가)
        primary_result = results[0]

        # 메타인지적 강화
        primary_result["meta_enhanced"] = True
        primary_result["meta_analysis"] = meta_analysis
        primary_result["integration_timestamp"] = datetime.now().isoformat()

        return primary_result

    def _generate_evolution_feedback(
        self, context: ConductorContext, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """진화적 피드백 생성"""
        feedback = {
            "adaptation_success": result.get("confidence", 0.5) > 0.7,
            "complexity_handling": len(context.user_input) > 50,
            "meta_awareness_utilized": result.get("meta_enhanced", False),
            "evolution_trigger": False,
        }

        # 진화 트리거 조건 확인
        if (
            feedback["adaptation_success"]
            and feedback["complexity_handling"]
            and feedback["meta_awareness_utilized"]
        ):
            feedback["evolution_trigger"] = True
            self.conductor_stats["evolution_events"] += 1

        return feedback

    def _update_evolution_state(self, feedback: Dict[str, Any]):
        """진화 상태 업데이트"""
        if feedback.get("evolution_trigger", False):
            self.evolution_state["adaptation_level"] = min(
                2.0, self.evolution_state["adaptation_level"] + 0.1
            )
            self.evolution_state["meta_awareness"] = min(
                1.0, self.evolution_state["meta_awareness"] + 0.05
            )
            print(
                f"🧬 진화 이벤트: 적응 수준 {self.evolution_state['adaptation_level']:.2f}"
            )

    def _update_conductor_stats(
        self, route: str, processing_time: float, success: bool
    ):
        """지휘자 통계 업데이트"""
        if success:
            self.conductor_stats["successful_conducts"] += 1

        # 경로 분포 업데이트
        self.conductor_stats["route_distribution"][route] = (
            self.conductor_stats["route_distribution"].get(route, 0) + 1
        )

        # 평균 처리 시간 업데이트
        total_conducts = self.conductor_stats["total_conducts"]
        current_avg = self.conductor_stats["average_processing_time"]
        self.conductor_stats["average_processing_time"] = (
            current_avg * (total_conducts - 1) + processing_time
        ) / total_conducts

    def get_conductor_status(self) -> Dict[str, Any]:
        """지휘자 상태 반환"""
        return {
            "version": self.version,
            "status": self.status,
            "evolution_state": self.evolution_state,
            "statistics": self.conductor_stats,
            "internal_modules": INTERNAL_MODULES_AVAILABLE,
        }


# 글로벌 지휘자 인스턴스
_global_conductor = None


def get_conductor() -> JudgmentConductor:
    """글로벌 지휘자 인스턴스 반환"""
    global _global_conductor
    if _global_conductor is None:
        _global_conductor = JudgmentConductor()
    return _global_conductor


def run_conductor(
    user_input: str,
    context: Optional[Dict[str, Any]] = None,
    signature: str = "Echo-Aurora",
    mode: str = "hybrid",
) -> Dict[str, Any]:
    """🎯 AGI 판단 지휘자 실행 - 메인 진입점"""

    conductor = get_conductor()

    conductor_context = ConductorContext(
        user_input=user_input,
        signature=signature,
        mode=mode,
        meta_context=context or {},
    )

    result = conductor.conduct_judgment(conductor_context)

    # 결과를 기존 시스템과 호환 가능한 형태로 변환
    return {
        "success": result.success,
        "response_text": result.judgment_result.get("response_text", ""),
        "signature_used": result.judgment_result.get("signature_used", signature),
        "strategy_applied": result.judgment_result.get(
            "strategy_applied", "agi_conductor"
        ),
        "confidence": result.judgment_result.get("confidence", 0.5),
        "processing_time": result.processing_time,
        "route_taken": result.route_taken,
        "meta_insights": result.meta_insights,
        "evolution_feedback": result.evolution_feedback,
        "conductor_version": conductor.version,
    }


# 비동기 버전
async def run_conductor_async(
    user_input: str,
    context: Optional[Dict[str, Any]] = None,
    signature: str = "Echo-Aurora",
    mode: str = "hybrid",
) -> Dict[str, Any]:
    """🎯 비동기 AGI 판단 지휘자 실행"""

    conductor = get_conductor()

    conductor_context = ConductorContext(
        user_input=user_input,
        signature=signature,
        mode=mode,
        meta_context=context or {},
    )

    result = await conductor.conduct_judgment_async(conductor_context)

    return {
        "success": result.success,
        "response_text": result.judgment_result.get("response_text", ""),
        "signature_used": result.judgment_result.get("signature_used", signature),
        "strategy_applied": result.judgment_result.get(
            "strategy_applied", "agi_conductor"
        ),
        "confidence": result.judgment_result.get("confidence", 0.5),
        "processing_time": result.processing_time,
        "route_taken": result.route_taken,
        "meta_insights": result.meta_insights,
        "evolution_feedback": result.evolution_feedback,
        "conductor_version": conductor.version,
    }


if __name__ == "__main__":
    # 기본 테스트
    print("🧪 Judgment Conductor 기본 테스트")

    test_inputs = [
        "안녕하세요! 오늘 기분이 좋아요",
        "요즘 너무 힘들어서 우울해요",
        "이 문제를 어떻게 해결해야 할지 모르겠어요",
    ]

    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n🎯 테스트 {i}: {test_input}")
        result = run_conductor(test_input)

        print(f"  성공: {result['success']}")
        print(f"  응답: {result['response_text'][:100]}...")
        print(f"  경로: {result['route_taken']}")
        print(f"  처리시간: {result['processing_time']:.3f}초")

    # 상태 확인
    conductor = get_conductor()
    status = conductor.get_conductor_status()
    print(f"\n📊 지휘자 상태:")
    print(f"  버전: {status['version']}")
    print(f"  총 지휘: {status['statistics']['total_conducts']}")
    print(
        f"  성공률: {status['statistics']['successful_conducts']}/{status['statistics']['total_conducts']}"
    )
    print(f"  진화 이벤트: {status['statistics']['evolution_events']}")
