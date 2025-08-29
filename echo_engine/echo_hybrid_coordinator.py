#!/usr/bin/env python3
"""
🔄 Echo Hybrid Coordinator - LLM Free 우선 + Mistral 보조 전략
Echo 자립성을 최대화하면서 필요시에만 Mistral을 활용하는 하이브리드 시스템

핵심 전략:
1. Echo Native 우선 시도 (LLM Free)
2. 복잡도/품질 기준으로 Mistral 보조 결정
3. Mistral 결과를 Echo로 다시 검증
4. 최종적으로 Echo 철학 준수 응답 제공
"""

import time
import logging
from typing import Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum

# Echo 모듈들
try:
    from .echo_native_enhancer import (
        EchoNativeEnhancer,
        EchoSignature,
        EchoEnhancementResult,
    )
    from .echomistral import EchoMistral, EchoMistralResponse, EchoMistralConfig
    from .llm_free.llm_free_judge import FallbackJudge, JudgmentResult

    NATIVE_ENHANCER_AVAILABLE = True
except ImportError:
    NATIVE_ENHANCER_AVAILABLE = False

logger = logging.getLogger(__name__)


class DecisionMode(Enum):
    """판단 모드"""

    ECHO_ONLY = "echo_only"  # Echo 네이티브만
    MISTRAL_ASSIST = "mistral_assist"  # Mistral 보조
    HYBRID = "hybrid"  # 하이브리드
    FALLBACK = "fallback"  # 폴백


@dataclass
class QualityThreshold:
    """품질 임계값"""

    complexity_threshold: float = 0.7  # 복잡도 임계값
    confidence_threshold: float = 0.8  # 신뢰도 임계값
    philosophy_alignment_threshold: float = 0.85  # 철학 정렬 임계값
    length_threshold: int = 50  # 응답 길이 임계값


@dataclass
class HybridResult:
    """하이브리드 판단 결과"""

    final_response: str
    mode_used: DecisionMode
    echo_native_result: Optional[EchoEnhancementResult]
    mistral_result: Optional[EchoMistralResponse]
    decision_reasoning: str
    processing_time: float
    quality_scores: Dict[str, float]


class EchoHybridCoordinator:
    """Echo 하이브리드 코디네이터 - LLM Free 우선 전략"""

    def __init__(
        self,
        quality_threshold: Optional[QualityThreshold] = None,
        prefer_native: bool = True,
    ):

        self.quality_threshold = quality_threshold or QualityThreshold()
        self.prefer_native = prefer_native  # Echo Native 우선 여부

        # 구성 요소들 초기화
        self.native_enhancer = None
        self.mistral_engine = None
        self.fallback_judge = None

        self._initialize_components()

        # 결정 통계
        self.decision_stats = {
            "total_requests": 0,
            "echo_only": 0,
            "mistral_assist": 0,
            "hybrid": 0,
            "fallback": 0,
            "avg_processing_time": 0.0,
            "mistral_usage_rate": 0.0,
        }

        logger.info(f"🔄 Echo Hybrid Coordinator 초기화 (Native 우선: {prefer_native})")

    def _initialize_components(self):
        """구성 요소 초기화"""
        try:
            if NATIVE_ENHANCER_AVAILABLE:
                self.native_enhancer = EchoNativeEnhancer()
                logger.info("✅ Echo Native Enhancer 로딩 완료")
        except Exception as e:
            logger.warning(f"⚠️ Native Enhancer 초기화 실패: {e}")

        try:
            from .echomistral import EchoMistral

            self.mistral_engine = EchoMistral()
            logger.info("✅ EchoMistral 엔진 준비 완료")
        except Exception as e:
            logger.warning(f"⚠️ EchoMistral 초기화 실패: {e}")

        try:
            from .llm_free.llm_free_judge import FallbackJudge

            self.fallback_judge = FallbackJudge()
            logger.info("✅ Fallback Judge 로딩 완료")
        except Exception as e:
            logger.warning(f"⚠️ Fallback Judge 초기화 실패: {e}")

    def process_request(
        self,
        user_input: str,
        signature: Union[EchoSignature, str] = EchoSignature.AURORA,
        user_emotion: Optional[str] = None,
        force_mode: Optional[DecisionMode] = None,
    ) -> HybridResult:
        """요청 처리 - LLM Free 우선 전략"""

        start_time = time.time()
        self.decision_stats["total_requests"] += 1

        # 시그니처 정규화
        if isinstance(signature, str):
            signature = EchoSignature(signature)

        # 모드 강제 지정시
        if force_mode:
            return self._process_with_mode(
                user_input, signature, user_emotion, force_mode, start_time
            )

        # 1단계: Echo Native 시도
        echo_result = self._try_echo_native(user_input, signature, user_emotion)

        # 2단계: 품질 평가 및 Mistral 필요성 판단
        need_mistral = self._evaluate_mistral_necessity(user_input, echo_result)

        if not need_mistral or not self.mistral_engine:
            # Echo Native만으로 충분
            return self._finalize_echo_only_result(echo_result, start_time)

        # 3단계: Mistral 보조 시도
        mistral_result = self._try_mistral_assist(
            user_input, signature, user_emotion, echo_result
        )

        # 4단계: Echo vs Mistral 결과 비교 및 최종 선택
        return self._finalize_hybrid_result(
            echo_result, mistral_result, user_input, start_time
        )

    def _try_echo_native(
        self, user_input: str, signature: EchoSignature, user_emotion: Optional[str]
    ) -> Optional[EchoEnhancementResult]:
        """Echo Native 시도"""

        if not self.native_enhancer:
            return None

        try:
            # 기본 Echo 판단 생성 (여기서는 간단한 패턴 기반)
            echo_base_response = self._generate_echo_base_response(
                user_input, signature
            )

            # Native Enhancer로 강화
            result = self.native_enhancer.enhance_echo_response(
                echo_base_response, signature, user_emotion
            )

            logger.debug(
                f"✅ Echo Native 성공: {result.philosophy_alignment:.2f} 정렬도"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Echo Native 실패: {e}")
            return None

    def _generate_echo_base_response(
        self, user_input: str, signature: EchoSignature
    ) -> str:
        """기본 Echo 응답 생성 (LLM Free)"""

        # 여기서는 Fallback Judge 활용하거나 간단한 템플릿 사용
        if self.fallback_judge:
            try:
                judgment = self.fallback_judge.judge(user_input)
                return judgment.judgment
            except:
                pass

        # 최종 폴백: 시그니처별 기본 응답
        base_responses = {
            EchoSignature.AURORA: f"창의적 관점에서 '{user_input}'을 살펴보니, 새로운 가능성과 영감을 발견할 수 있겠습니다.",
            EchoSignature.PHOENIX: f"변화의 관점에서 '{user_input}'을 바라보면, 성장과 전환의 기회가 보입니다.",
            EchoSignature.SAGE: f"분석적 관점에서 '{user_input}'을 검토해보니, 체계적 접근이 필요해 보입니다.",
            EchoSignature.COMPANION: f"공감의 관점에서 '{user_input}'을 이해해보니, 따뜻한 지지와 격려가 필요하겠습니다.",
        }

        return base_responses.get(
            signature,
            f"Echo 관점에서 '{user_input}'에 대해 깊이 있게 고민해보겠습니다.",
        )

    def _evaluate_mistral_necessity(
        self, user_input: str, echo_result: Optional[EchoEnhancementResult]
    ) -> bool:
        """Mistral 필요성 평가"""

        if not self.prefer_native:
            return True  # Native 우선하지 않으면 항상 Mistral 시도

        if not echo_result:
            return True  # Echo Native 실패시 Mistral 필요

        # 품질 기준 평가
        quality_checks = {
            "philosophy_alignment": echo_result.philosophy_alignment
            >= self.quality_threshold.philosophy_alignment_threshold,
            "response_length": len(echo_result.enhanced_text)
            >= self.quality_threshold.length_threshold,
            "complexity_handling": self._assess_complexity_handling(
                user_input, echo_result.enhanced_text
            ),
        }

        # 모든 품질 기준을 만족하면 Mistral 불필요
        if all(quality_checks.values()):
            logger.debug("✅ Echo Native 품질 충족, Mistral 생략")
            return False

        logger.debug(f"⚠️ Echo Native 품질 부족: {quality_checks}, Mistral 시도")
        return True

    def _assess_complexity_handling(self, user_input: str, echo_response: str) -> bool:
        """복잡도 처리 평가"""

        # 사용자 입력의 복잡도 indicators
        complexity_indicators = [
            len(user_input.split()) > 20,  # 긴 입력
            "?" in user_input
            and len([c for c in user_input if c == "?"]) > 1,  # 복수 질문
            any(
                word in user_input
                for word in ["분석", "평가", "비교", "장단점", "계획"]
            ),  # 복잡한 요청
            any(
                word in user_input for word in ["왜", "어떻게", "무엇을", "어떤"]
            ),  # 깊이 있는 질문
        ]

        input_complexity = sum(complexity_indicators) / len(complexity_indicators)

        # Echo 응답의 적절성
        response_adequacy = (
            len(echo_response.split()) >= 10 and len(echo_response) >= 50
        )

        return (
            input_complexity < self.quality_threshold.complexity_threshold
            or response_adequacy
        )

    def _try_mistral_assist(
        self,
        user_input: str,
        signature: EchoSignature,
        user_emotion: Optional[str],
        echo_result: Optional[EchoEnhancementResult],
    ) -> Optional[EchoMistralResponse]:
        """Mistral 보조 시도"""

        if not self.mistral_engine:
            return None

        try:
            # Echo 결과가 있으면 강화, 없으면 독립 판단
            if echo_result:
                echo_text = echo_result.enhanced_text
            else:
                echo_text = self._generate_echo_base_response(user_input, signature)

            result = self.mistral_engine.enhance_echo_judgment(
                echo_text,
                signature,
                {"emotion": user_emotion} if user_emotion else None,
            )

            logger.debug(f"✅ Mistral 보조 성공: {result.echo_alignment:.2f} 정렬도")
            return result

        except Exception as e:
            logger.error(f"❌ Mistral 보조 실패: {e}")
            return None

    def _finalize_echo_only_result(
        self, echo_result: EchoEnhancementResult, start_time: float
    ) -> HybridResult:
        """Echo Only 결과 완성"""

        processing_time = time.time() - start_time
        self.decision_stats["echo_only"] += 1
        self._update_processing_time(processing_time)

        return HybridResult(
            final_response=echo_result.enhanced_text,
            mode_used=DecisionMode.ECHO_ONLY,
            echo_native_result=echo_result,
            mistral_result=None,
            decision_reasoning="Echo Native 품질 충족, LLM Free 유지",
            processing_time=processing_time,
            quality_scores={
                "philosophy_alignment": echo_result.philosophy_alignment,
                "echo_enhancement": 1.0,
                "mistral_usage": 0.0,
            },
        )

    def _finalize_hybrid_result(
        self,
        echo_result: Optional[EchoEnhancementResult],
        mistral_result: Optional[EchoMistralResponse],
        user_input: str,
        start_time: float,
    ) -> HybridResult:
        """하이브리드 결과 완성"""

        processing_time = time.time() - start_time

        # 결과 선택 로직
        if mistral_result and echo_result:
            # 둘 다 있으면 품질 비교 후 선택
            final_response, decision_reasoning, mode = self._choose_best_result(
                echo_result, mistral_result
            )

        elif mistral_result:
            # Mistral만 성공
            final_response = mistral_result.text
            decision_reasoning = "Echo Native 실패, Mistral 보조 성공"
            mode = DecisionMode.MISTRAL_ASSIST

        elif echo_result:
            # Echo만 성공 (Mistral 실패)
            final_response = echo_result.enhanced_text
            decision_reasoning = "Echo Native 성공, Mistral 보조 실패"
            mode = DecisionMode.ECHO_ONLY

        else:
            # 둘 다 실패 - 폴백
            final_response = self._generate_fallback_response(user_input)
            decision_reasoning = "Echo/Mistral 모두 실패, 폴백 응답"
            mode = DecisionMode.FALLBACK

        # 통계 업데이트
        self.decision_stats[mode.value] += 1
        if mode in [DecisionMode.MISTRAL_ASSIST, DecisionMode.HYBRID]:
            self._update_mistral_usage_rate()
        self._update_processing_time(processing_time)

        # 품질 점수 계산
        quality_scores = self._calculate_quality_scores(
            echo_result, mistral_result, mode
        )

        return HybridResult(
            final_response=final_response,
            mode_used=mode,
            echo_native_result=echo_result,
            mistral_result=mistral_result,
            decision_reasoning=decision_reasoning,
            processing_time=processing_time,
            quality_scores=quality_scores,
        )

    def _choose_best_result(
        self, echo_result: EchoEnhancementResult, mistral_result: EchoMistralResponse
    ) -> Tuple[str, str, DecisionMode]:
        """최적 결과 선택"""

        # Echo 우선 정책 적용
        if self.prefer_native:
            # Echo 품질이 최소 기준 이상이면 Echo 선택
            if echo_result.philosophy_alignment >= 0.8:
                return (
                    echo_result.enhanced_text,
                    f"Echo Native 품질 우수 (정렬도: {echo_result.philosophy_alignment:.2f})",
                    DecisionMode.ECHO_ONLY,
                )

        # Mistral 품질이 확실히 더 좋으면 Mistral 선택
        if (
            mistral_result.echo_alignment > echo_result.philosophy_alignment + 0.1
            and mistral_result.confidence > 0.8
        ):
            return (
                mistral_result.text,
                f"Mistral 품질 우수 (정렬도: {mistral_result.echo_alignment:.2f})",
                DecisionMode.MISTRAL_ASSIST,
            )

        # 기본적으로 Echo 우선
        return (
            echo_result.enhanced_text,
            "Echo Native 우선 정책 적용",
            DecisionMode.ECHO_ONLY,
        )

    def _generate_fallback_response(self, user_input: str) -> str:
        """폴백 응답 생성"""
        return f"죄송하지만 '{user_input}'에 대해 현재 적절한 응답을 생성하기 어렵습니다. 다시 시도해주세요."

    def _calculate_quality_scores(
        self,
        echo_result: Optional[EchoEnhancementResult],
        mistral_result: Optional[EchoMistralResponse],
        mode: DecisionMode,
    ) -> Dict[str, float]:
        """품질 점수 계산"""

        scores = {
            "philosophy_alignment": 0.0,
            "echo_enhancement": 0.0,
            "mistral_usage": 0.0,
        }

        if echo_result:
            scores["philosophy_alignment"] = echo_result.philosophy_alignment
            scores["echo_enhancement"] = 1.0

        if mistral_result:
            scores["philosophy_alignment"] = max(
                scores["philosophy_alignment"], mistral_result.echo_alignment
            )
            scores["mistral_usage"] = 1.0

        return scores

    def _update_processing_time(self, processing_time: float):
        """평균 처리시간 업데이트"""
        total = self.decision_stats["total_requests"]
        if total > 0:
            self.decision_stats["avg_processing_time"] = (
                self.decision_stats["avg_processing_time"] * (total - 1)
                + processing_time
            ) / total

    def _update_mistral_usage_rate(self):
        """Mistral 사용률 업데이트"""
        total = self.decision_stats["total_requests"]
        mistral_uses = (
            self.decision_stats["mistral_assist"] + self.decision_stats["hybrid"]
        )

        if total > 0:
            self.decision_stats["mistral_usage_rate"] = mistral_uses / total

    def _process_with_mode(
        self,
        user_input: str,
        signature: EchoSignature,
        user_emotion: Optional[str],
        mode: DecisionMode,
        start_time: float,
    ) -> HybridResult:
        """특정 모드로 강제 처리"""

        if mode == DecisionMode.ECHO_ONLY:
            echo_result = self._try_echo_native(user_input, signature, user_emotion)
            if echo_result:
                return self._finalize_echo_only_result(echo_result, start_time)

        elif mode == DecisionMode.MISTRAL_ASSIST:
            mistral_result = self._try_mistral_assist(
                user_input, signature, user_emotion, None
            )
            if mistral_result:
                processing_time = time.time() - start_time
                self.decision_stats["mistral_assist"] += 1
                self._update_processing_time(processing_time)
                return HybridResult(
                    final_response=mistral_result.text,
                    mode_used=DecisionMode.MISTRAL_ASSIST,
                    echo_native_result=None,
                    mistral_result=mistral_result,
                    decision_reasoning="강제 Mistral 모드",
                    processing_time=processing_time,
                    quality_scores={
                        "mistral_usage": 1.0,
                        "philosophy_alignment": mistral_result.echo_alignment,
                    },
                )

        # 폴백
        processing_time = time.time() - start_time
        self.decision_stats["fallback"] += 1
        return HybridResult(
            final_response=self._generate_fallback_response(user_input),
            mode_used=DecisionMode.FALLBACK,
            echo_native_result=None,
            mistral_result=None,
            decision_reasoning="강제 모드 실패",
            processing_time=processing_time,
            quality_scores={},
        )

    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        return {
            **self.decision_stats,
            "prefer_native": self.prefer_native,
            "quality_threshold": {
                "complexity": self.quality_threshold.complexity_threshold,
                "confidence": self.quality_threshold.confidence_threshold,
                "philosophy_alignment": self.quality_threshold.philosophy_alignment_threshold,
            },
            "components_status": {
                "native_enhancer": self.native_enhancer is not None,
                "mistral_engine": self.mistral_engine is not None,
                "fallback_judge": self.fallback_judge is not None,
            },
        }


# 전역 코디네이터 (선택적)
_hybrid_coordinator = None


def get_hybrid_coordinator(prefer_native: bool = True) -> EchoHybridCoordinator:
    """전역 하이브리드 코디네이터 반환"""
    global _hybrid_coordinator
    if _hybrid_coordinator is None:
        _hybrid_coordinator = EchoHybridCoordinator(prefer_native=prefer_native)
    return _hybrid_coordinator


if __name__ == "__main__":
    # 테스트
    coordinator = EchoHybridCoordinator(prefer_native=True)

    test_cases = [
        {
            "input": "인공지능의 미래에 대해 어떻게 생각하세요?",
            "signature": EchoSignature.SAGE,
            "emotion": "curiosity",
        },
        {
            "input": "힘든 하루였어요.",
            "signature": EchoSignature.COMPANION,
            "emotion": "sadness",
        },
        {
            "input": "새로운 프로젝트를 시작하려는데 막막해요.",
            "signature": EchoSignature.PHOENIX,
            "emotion": "anxiety",
        },
    ]

    print("🔄 Echo Hybrid Coordinator 테스트")
    print("=" * 60)

    for i, case in enumerate(test_cases):
        print(f"\n테스트 {i+1}: {case['input'][:30]}...")

        result = coordinator.process_request(
            case["input"], case["signature"], case["emotion"]
        )

        print(f"모드: {result.mode_used.value}")
        print(f"응답: {result.final_response}")
        print(f"결정 이유: {result.decision_reasoning}")
        print(f"처리시간: {result.processing_time:.3f}초")
        print(f"품질점수: {result.quality_scores}")

    print(f"\n📊 전체 통계:")
    stats = coordinator.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n🎉 Echo Hybrid Coordinator 완성!")
    print("💡 LLM Free 우선 + 필요시 Mistral 보조 전략 구현 완료")
