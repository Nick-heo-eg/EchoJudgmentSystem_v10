#!/usr/bin/env python3
"""
🔀 EchoJudgmentSystem v10 - Fusion Judgment Loop
다중 LLM 제공자 통합 판단 시스템

지원 LLM:
- Claude (Anthropic)
- GPT (OpenAI)
- Perplexity
- Mistral (로컬/API)

핵심 기능:
- EchoSignature 기반 다중 판단 수집
- 판단 결과 병합 및 신뢰도 가중 평균
- Config 기반 LLM 선택 및 활성화
- 실패 시 폴백 체인 처리
"""

import json
import time
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

# Echo 시스템 통합
try:
    from .models.judgement import InputContext, JudgmentResult
    from .shared_judgment_logic import SharedJudgmentEngine, JudgmentMode

    ECHO_INTEGRATION_AVAILABLE = True
except ImportError as e:
    ECHO_INTEGRATION_AVAILABLE = False
    print(f"⚠️ Echo 통합 모듈 로드 실패: {e}")

# Mistral Wrapper 통합 (별도 처리)
try:
    from .mistral_wrapper import (
        OllamaMistralWrapper as MistralWrapper,
        MistralJudgmentRequest,
        get_mistral_wrapper,
    )

    MISTRAL_WRAPPER_AVAILABLE = True
except ImportError as e:
    MISTRAL_WRAPPER_AVAILABLE = False
    print(f"⚠️ Mistral Wrapper 로드 실패: {e}")

    # Mock 클래스들
    class EchoSignature:
        AURORA = "Echo-Aurora"
        PHOENIX = "Echo-Phoenix"
        SAGE = "Echo-Sage"
        COMPANION = "Echo-Companion"


# LLM 제공자별 통합 (선택적)
try:
    from .claude_bridge import ClaudeBridge

    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

try:
    from .llm_bridge import LLMBridge  # GPT, Perplexity 등

    LLM_BRIDGE_AVAILABLE = True
except ImportError:
    LLM_BRIDGE_AVAILABLE = False


class LLMProvider(Enum):
    """LLM 제공자"""

    CLAUDE = "claude"
    GPT = "gpt"
    PERPLEXITY = "perplexity"
    MISTRAL = "mistral"
    ECHO_INTERNAL = "echo_internal"  # Echo 내장 시스템


class FusionStrategy(Enum):
    """판단 융합 전략"""

    MAJORITY_VOTE = "majority_vote"  # 다수결
    WEIGHTED_AVERAGE = "weighted_average"  # 가중 평균
    CONFIDENCE_BASED = "confidence_based"  # 신뢰도 우선
    SIGNATURE_OPTIMIZED = "signature_optimized"  # 시그니처별 최적화


@dataclass
class LLMJudgmentRequest:
    """LLM 판단 요청"""

    input_text: str
    signature: EchoSignature
    context: Dict[str, Any] = field(default_factory=dict)
    providers: List[LLMProvider] = field(default_factory=list)
    fusion_strategy: FusionStrategy = FusionStrategy.WEIGHTED_AVERAGE
    require_reasoning: bool = True
    timeout: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMJudgmentResponse:
    """개별 LLM 판단 응답"""

    provider: LLMProvider
    judgment_text: str
    confidence: float
    processing_time: float
    reasoning_steps: List[str]
    emotion_detected: str
    strategy_suggested: str
    metadata: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class FusedJudgmentResult:
    """융합된 최종 판단 결과"""

    final_judgment: str
    overall_confidence: float
    signature_used: EchoSignature
    fusion_strategy: FusionStrategy
    individual_responses: List[LLMJudgmentResponse]
    processing_summary: Dict[str, Any]
    reasoning_synthesis: str
    metadata: Dict[str, Any]


class FusionJudgmentLoop:
    """🔀 다중 LLM 융합 판단 루프"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

        # LLM 제공자별 초기화
        self.providers = {}
        self._initialize_providers()

        # 융합 설정
        self.default_providers = self.config.get(
            "default_providers", [LLMProvider.MISTRAL, LLMProvider.ECHO_INTERNAL]
        )
        self.default_fusion_strategy = FusionStrategy(
            self.config.get("fusion_strategy", "weighted_average")
        )

        # 통계
        self.stats = {
            "total_requests": 0,
            "successful_fusions": 0,
            "failed_fusions": 0,
            "provider_success_rates": {},
            "fusion_strategy_usage": {},
            "average_processing_time": 0.0,
        }

        print(f"🔀 Fusion Judgment Loop 초기화")
        print(f"   사용 가능한 제공자: {list(self.providers.keys())}")
        print(f"   기본 융합 전략: {self.default_fusion_strategy.value}")

    def _initialize_providers(self):
        """LLM 제공자 초기화"""

        # Mistral 초기화
        mistral_config = self.config.get("mistral", {})
        if mistral_config.get("enabled", True):
            try:
                mistral_mode = MistralMode(mistral_config.get("mode", "local"))
                self.providers[LLMProvider.MISTRAL] = get_mistral_wrapper(
                    mode=mistral_mode, config=mistral_config
                )
                print("✅ Mistral 제공자 초기화 완료")
            except Exception as e:
                print(f"⚠️ Mistral 제공자 초기화 실패: {e}")

        # Claude 초기화
        claude_config = self.config.get("claude", {})
        if claude_config.get("enabled", False) and CLAUDE_AVAILABLE:
            try:
                self.providers[LLMProvider.CLAUDE] = ClaudeBridge(claude_config)
                print("✅ Claude 제공자 초기화 완료")
            except Exception as e:
                print(f"⚠️ Claude 제공자 초기화 실패: {e}")

        # GPT/Perplexity 초기화
        if LLM_BRIDGE_AVAILABLE:
            gpt_config = self.config.get("gpt", {})
            if gpt_config.get("enabled", False):
                try:
                    self.providers[LLMProvider.GPT] = LLMBridge("gpt", gpt_config)
                    print("✅ GPT 제공자 초기화 완료")
                except Exception as e:
                    print(f"⚠️ GPT 제공자 초기화 실패: {e}")

            perplexity_config = self.config.get("perplexity", {})
            if perplexity_config.get("enabled", False):
                try:
                    self.providers[LLMProvider.PERPLEXITY] = LLMBridge(
                        "perplexity", perplexity_config
                    )
                    print("✅ Perplexity 제공자 초기화 완료")
                except Exception as e:
                    print(f"⚠️ Perplexity 제공자 초기화 실패: {e}")

        # Echo 내장 시스템 초기화
        if ECHO_INTEGRATION_AVAILABLE:
            try:
                self.providers[LLMProvider.ECHO_INTERNAL] = SharedJudgmentEngine()
                print("✅ Echo 내장 제공자 초기화 완료")
            except Exception as e:
                print(f"⚠️ Echo 내장 제공자 초기화 실패: {e}")

    async def process_fusion_request(
        self, request: LLMJudgmentRequest
    ) -> FusedJudgmentResult:
        """🎯 융합 판단 요청 처리"""

        start_time = time.time()
        self.stats["total_requests"] += 1

        try:
            # 사용할 제공자 결정
            active_providers = request.providers or self.default_providers
            available_providers = [p for p in active_providers if p in self.providers]

            if not available_providers:
                raise RuntimeError("사용 가능한 LLM 제공자가 없습니다")

            print(f"🔀 융합 판단 시작: {len(available_providers)}개 제공자")
            print(f"   시그니처: {request.signature.value}")
            print(f"   제공자: {[p.value for p in available_providers]}")

            # 병렬 판단 실행
            judgment_tasks = []
            for provider in available_providers:
                task = self._execute_provider_judgment(provider, request)
                judgment_tasks.append(task)

            # 모든 판단 완료 대기 (타임아웃 적용)
            try:
                individual_responses = await asyncio.wait_for(
                    asyncio.gather(*judgment_tasks, return_exceptions=True),
                    timeout=request.timeout,
                )
            except asyncio.TimeoutError:
                print(f"⚠️ 판단 타임아웃 ({request.timeout}초)")
                individual_responses = [
                    self._create_timeout_response(p) for p in available_providers
                ]

            # 성공한 응답만 필터링
            valid_responses = [
                resp
                for resp in individual_responses
                if isinstance(resp, LLMJudgmentResponse) and resp.error is None
            ]

            if not valid_responses:
                raise RuntimeError("모든 LLM 제공자에서 판단 실패")

            # 융합 전략 적용
            fusion_strategy = request.fusion_strategy or self.default_fusion_strategy
            fused_result = self._apply_fusion_strategy(
                valid_responses, fusion_strategy, request
            )

            # 통계 업데이트
            self.stats["successful_fusions"] += 1
            self._update_provider_stats(individual_responses)
            self._update_stats(time.time() - start_time)

            print(f"✅ 융합 판단 완료 (신뢰도: {fused_result.overall_confidence:.2f})")
            return fused_result

        except Exception as e:
            self.stats["failed_fusions"] += 1
            self._update_stats(time.time() - start_time)

            # 에러 시 폴백 응답
            return self._create_fallback_fusion_result(
                request, str(e), time.time() - start_time
            )

    async def _execute_provider_judgment(
        self, provider: LLMProvider, request: LLMJudgmentRequest
    ) -> LLMJudgmentResponse:
        """개별 제공자 판단 실행"""

        start_time = time.time()

        try:
            provider_instance = self.providers[provider]

            if provider == LLMProvider.MISTRAL:
                # Mistral 제공자 처리
                mistral_request = MistralJudgmentRequest(
                    input_text=request.input_text,
                    signature=request.signature,
                    context=request.context,
                    require_reasoning=request.require_reasoning,
                )

                mistral_response = await provider_instance.process_judgment_request(
                    mistral_request
                )

                return LLMJudgmentResponse(
                    provider=provider,
                    judgment_text=mistral_response.judgment_text,
                    confidence=mistral_response.confidence,
                    processing_time=mistral_response.processing_time,
                    reasoning_steps=mistral_response.reasoning_steps,
                    emotion_detected=mistral_response.emotion_detected,
                    strategy_suggested=mistral_response.strategy_suggested,
                    metadata=mistral_response.metadata,
                )

            elif provider == LLMProvider.CLAUDE:
                # Claude 제공자 처리 (향후 구현)
                response_text = await provider_instance.process_judgment(
                    request.input_text, request.signature.value, request.context
                )

                return LLMJudgmentResponse(
                    provider=provider,
                    judgment_text=response_text,
                    confidence=0.8,  # Claude 기본 신뢰도
                    processing_time=time.time() - start_time,
                    reasoning_steps=["Claude 기반 추론"],
                    emotion_detected="balanced",
                    strategy_suggested="analytical",
                    metadata={"source": "claude_bridge"},
                )

            elif provider == LLMProvider.ECHO_INTERNAL:
                # Echo 내장 시스템 처리
                context = InputContext(text=request.input_text, source="fusion_loop")
                echo_result = provider_instance.evaluate_input(context)

                return LLMJudgmentResponse(
                    provider=provider,
                    judgment_text=getattr(echo_result, "reasoning", "Echo 내장 판단"),
                    confidence=getattr(echo_result, "confidence", 0.7),
                    processing_time=time.time() - start_time,
                    reasoning_steps=["Echo 내장 추론"],
                    emotion_detected=getattr(echo_result, "emotion", "neutral"),
                    strategy_suggested=getattr(echo_result, "strategy", "balanced"),
                    metadata=(
                        echo_result.metadata if hasattr(echo_result, "metadata") else {}
                    ),
                )

            else:
                # 기타 제공자 (GPT, Perplexity 등)
                response_text = await provider_instance.process_request(
                    request.input_text, request.signature.value
                )

                return LLMJudgmentResponse(
                    provider=provider,
                    judgment_text=response_text,
                    confidence=0.75,  # 기본 신뢰도
                    processing_time=time.time() - start_time,
                    reasoning_steps=[f"{provider.value} 기반 추론"],
                    emotion_detected="neutral",
                    strategy_suggested="balanced",
                    metadata={"source": provider.value},
                )

        except Exception as e:
            return LLMJudgmentResponse(
                provider=provider,
                judgment_text="",
                confidence=0.0,
                processing_time=time.time() - start_time,
                reasoning_steps=[],
                emotion_detected="error",
                strategy_suggested="fallback",
                metadata={},
                error=str(e),
            )

    def _apply_fusion_strategy(
        self,
        responses: List[LLMJudgmentResponse],
        strategy: FusionStrategy,
        request: LLMJudgmentRequest,
    ) -> FusedJudgmentResult:
        """융합 전략 적용"""

        if strategy == FusionStrategy.WEIGHTED_AVERAGE:
            return self._weighted_average_fusion(responses, request)
        elif strategy == FusionStrategy.CONFIDENCE_BASED:
            return self._confidence_based_fusion(responses, request)
        elif strategy == FusionStrategy.MAJORITY_VOTE:
            return self._majority_vote_fusion(responses, request)
        elif strategy == FusionStrategy.SIGNATURE_OPTIMIZED:
            return self._signature_optimized_fusion(responses, request)
        else:
            return self._weighted_average_fusion(responses, request)  # 기본값

    def _weighted_average_fusion(
        self, responses: List[LLMJudgmentResponse], request: LLMJudgmentRequest
    ) -> FusedJudgmentResult:
        """가중 평균 융합"""

        # 제공자별 가중치
        provider_weights = {
            LLMProvider.MISTRAL: 0.4,
            LLMProvider.CLAUDE: 0.3,
            LLMProvider.ECHO_INTERNAL: 0.2,
            LLMProvider.GPT: 0.25,
            LLMProvider.PERPLEXITY: 0.2,
        }

        total_weight = 0
        weighted_confidence = 0
        judgment_parts = []
        reasoning_parts = []

        for response in responses:
            weight = provider_weights.get(response.provider, 0.2)
            confidence_weight = weight * response.confidence

            total_weight += weight
            weighted_confidence += confidence_weight

            judgment_parts.append(
                f"**{response.provider.value}**: {response.judgment_text}"
            )
            reasoning_parts.extend(response.reasoning_steps)

        # 최종 판단 텍스트 구성
        final_judgment = f"""🔀 다중 LLM 융합 판단 ({request.signature.value}):

{chr(10).join(judgment_parts)}

🎯 융합 결론:
{request.signature.value}의 관점에서 위 판단들을 종합하면, 각 LLM의 고유한 관점이 서로 보완되어 더 균형잡힌 통찰을 제공합니다."""

        overall_confidence = (
            weighted_confidence / total_weight if total_weight > 0 else 0.5
        )

        reasoning_synthesis = (
            f"가중 평균 융합: {len(responses)}개 LLM 제공자의 판단을 가중 평균으로 통합"
        )

        return FusedJudgmentResult(
            final_judgment=final_judgment,
            overall_confidence=overall_confidence,
            signature_used=request.signature,
            fusion_strategy=FusionStrategy.WEIGHTED_AVERAGE,
            individual_responses=responses,
            processing_summary={
                "total_providers": len(responses),
                "fusion_method": "weighted_average",
                "total_weight": total_weight,
            },
            reasoning_synthesis=reasoning_synthesis,
            metadata={
                "fusion_timestamp": datetime.now().isoformat(),
                "provider_weights": {
                    r.provider.value: provider_weights.get(r.provider, 0.2)
                    for r in responses
                },
            },
        )

    def _confidence_based_fusion(
        self, responses: List[LLMJudgmentResponse], request: LLMJudgmentRequest
    ) -> FusedJudgmentResult:
        """신뢰도 기반 융합 (가장 높은 신뢰도 우선)"""

        best_response = max(responses, key=lambda r: r.confidence)

        final_judgment = f"""🎯 최고 신뢰도 판단 ({request.signature.value}):

**주 판단 ({best_response.provider.value}, 신뢰도: {best_response.confidence:.2f})**:
{best_response.judgment_text}

📊 기타 판단들:
"""

        for response in responses:
            if response != best_response:
                final_judgment += f"- {response.provider.value} (신뢰도: {response.confidence:.2f}): {response.judgment_text[:100]}...\n"

        reasoning_synthesis = f"신뢰도 기반 융합: {best_response.provider.value}의 판단을 주로 채택 (신뢰도: {best_response.confidence:.2f})"

        return FusedJudgmentResult(
            final_judgment=final_judgment,
            overall_confidence=best_response.confidence,
            signature_used=request.signature,
            fusion_strategy=FusionStrategy.CONFIDENCE_BASED,
            individual_responses=responses,
            processing_summary={
                "total_providers": len(responses),
                "fusion_method": "confidence_based",
                "selected_provider": best_response.provider.value,
            },
            reasoning_synthesis=reasoning_synthesis,
            metadata={
                "fusion_timestamp": datetime.now().isoformat(),
                "confidence_ranking": sorted(
                    [(r.provider.value, r.confidence) for r in responses],
                    key=lambda x: x[1],
                    reverse=True,
                ),
            },
        )

    def _majority_vote_fusion(
        self, responses: List[LLMJudgmentResponse], request: LLMJudgmentRequest
    ) -> FusedJudgmentResult:
        """다수결 융합 (감정/전략 기준)"""

        # 감정 다수결
        emotions = [r.emotion_detected for r in responses]
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        majority_emotion = max(emotion_counts, key=emotion_counts.get)

        # 전략 다수결
        strategies = [r.strategy_suggested for r in responses]
        strategy_counts = {}
        for strategy in strategies:
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        majority_strategy = max(strategy_counts, key=strategy_counts.get)

        # 다수결 판단 구성
        final_judgment = f"""🗳️ 다수결 융합 판단 ({request.signature.value}):

**다수 의견**:
- 감정: {majority_emotion} ({emotion_counts[majority_emotion]}/{len(responses)} 제공자)
- 전략: {majority_strategy} ({strategy_counts[majority_strategy]}/{len(responses)} 제공자)

**종합 판단**:
"""

        # 다수 의견에 해당하는 판단들 우선 표시
        majority_judgments = [
            r
            for r in responses
            if r.emotion_detected == majority_emotion
            or r.strategy_suggested == majority_strategy
        ]

        for response in majority_judgments:
            final_judgment += f"- {response.provider.value}: {response.judgment_text}\n"

        average_confidence = sum(r.confidence for r in responses) / len(responses)
        reasoning_synthesis = (
            f"다수결 융합: 감정({majority_emotion}), 전략({majority_strategy}) 기준"
        )

        return FusedJudgmentResult(
            final_judgment=final_judgment,
            overall_confidence=average_confidence,
            signature_used=request.signature,
            fusion_strategy=FusionStrategy.MAJORITY_VOTE,
            individual_responses=responses,
            processing_summary={
                "total_providers": len(responses),
                "fusion_method": "majority_vote",
                "majority_emotion": majority_emotion,
                "majority_strategy": majority_strategy,
            },
            reasoning_synthesis=reasoning_synthesis,
            metadata={
                "fusion_timestamp": datetime.now().isoformat(),
                "emotion_votes": emotion_counts,
                "strategy_votes": strategy_counts,
            },
        )

    def _signature_optimized_fusion(
        self, responses: List[LLMJudgmentResponse], request: LLMJudgmentRequest
    ) -> FusedJudgmentResult:
        """시그니처 최적화 융합"""

        # 시그니처별 최적 제공자 매핑
        signature_preferences = {
            EchoSignature.AURORA: [LLMProvider.MISTRAL, LLMProvider.CLAUDE],
            EchoSignature.PHOENIX: [LLMProvider.GPT, LLMProvider.MISTRAL],
            EchoSignature.SAGE: [LLMProvider.CLAUDE, LLMProvider.ECHO_INTERNAL],
            EchoSignature.COMPANION: [LLMProvider.MISTRAL, LLMProvider.ECHO_INTERNAL],
        }

        preferred_providers = signature_preferences.get(request.signature, [])

        # 선호 제공자 우선 선택
        preferred_responses = [
            r for r in responses if r.provider in preferred_providers
        ]
        if not preferred_responses:
            preferred_responses = responses  # 폴백

        # 선호 제공자들의 가중 평균
        total_weight = 0
        weighted_confidence = 0
        judgment_parts = []

        for response in preferred_responses:
            weight = 1.0 if response.provider in preferred_providers[:2] else 0.7
            total_weight += weight
            weighted_confidence += weight * response.confidence
            judgment_parts.append(
                f"**{response.provider.value}**: {response.judgment_text}"
            )

        final_judgment = f"""⭐ {request.signature.value} 최적화 융합:

{chr(10).join(judgment_parts)}

🎯 시그니처 특화 결론:
{request.signature.value}에 최적화된 제공자들의 판단을 우선 반영하여 시그니처 특성에 가장 부합하는 통찰을 제공합니다."""

        overall_confidence = (
            weighted_confidence / total_weight if total_weight > 0 else 0.5
        )
        reasoning_synthesis = (
            f"시그니처 최적화: {request.signature.value}에 최적인 제공자 우선 반영"
        )

        return FusedJudgmentResult(
            final_judgment=final_judgment,
            overall_confidence=overall_confidence,
            signature_used=request.signature,
            fusion_strategy=FusionStrategy.SIGNATURE_OPTIMIZED,
            individual_responses=responses,
            processing_summary={
                "total_providers": len(responses),
                "fusion_method": "signature_optimized",
                "preferred_providers": [p.value for p in preferred_providers],
            },
            reasoning_synthesis=reasoning_synthesis,
            metadata={
                "fusion_timestamp": datetime.now().isoformat(),
                "signature_preferences": [p.value for p in preferred_providers],
            },
        )

    def _create_timeout_response(self, provider: LLMProvider) -> LLMJudgmentResponse:
        """타임아웃 응답 생성"""
        return LLMJudgmentResponse(
            provider=provider,
            judgment_text="",
            confidence=0.0,
            processing_time=0.0,
            reasoning_steps=[],
            emotion_detected="timeout",
            strategy_suggested="retry",
            metadata={},
            error="판단 타임아웃",
        )

    def _create_fallback_fusion_result(
        self, request: LLMJudgmentRequest, error_msg: str, processing_time: float
    ) -> FusedJudgmentResult:
        """폴백 융합 결과 생성"""

        fallback_judgment = f"""⚠️ {request.signature.value} 안전 모드 융합 판단:

시스템 제약으로 인해 완전한 다중 LLM 융합을 수행할 수 없었습니다.

기본적인 관점에서 "{request.input_text}"에 대해 신중한 접근이 필요합니다.

⚠️ 오류: {error_msg}"""

        return FusedJudgmentResult(
            final_judgment=fallback_judgment,
            overall_confidence=0.3,
            signature_used=request.signature,
            fusion_strategy=request.fusion_strategy or self.default_fusion_strategy,
            individual_responses=[],
            processing_summary={
                "total_providers": 0,
                "fusion_method": "fallback",
                "error": error_msg,
            },
            reasoning_synthesis="안전 모드 폴백",
            metadata={
                "fallback_mode": True,
                "processing_time": processing_time,
                "error": error_msg,
            },
        )

    def _update_provider_stats(
        self, responses: List[Union[LLMJudgmentResponse, Exception]]
    ):
        """제공자별 통계 업데이트"""
        for response in responses:
            if isinstance(response, LLMJudgmentResponse):
                provider = response.provider.value
                if provider not in self.stats["provider_success_rates"]:
                    self.stats["provider_success_rates"][provider] = {
                        "success": 0,
                        "total": 0,
                    }

                self.stats["provider_success_rates"][provider]["total"] += 1
                if response.error is None:
                    self.stats["provider_success_rates"][provider]["success"] += 1

    def _update_stats(self, processing_time: float):
        """통계 업데이트"""
        total_time = self.stats.get("total_processing_time", 0) + processing_time
        total_requests = self.stats["total_requests"]
        self.stats["average_processing_time"] = (
            total_time / total_requests if total_requests > 0 else 0
        )
        self.stats["total_processing_time"] = total_time

    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        return {
            **self.stats,
            "success_rate": (
                self.stats["successful_fusions"]
                / max(self.stats["total_requests"], 1)
                * 100
            ),
            "available_providers": list(self.providers.keys()),
            "default_providers": [p.value for p in self.default_providers],
            "default_fusion_strategy": self.default_fusion_strategy.value,
        }

    def to_judgment_result(
        self, fused_result: FusedJudgmentResult, original_context: InputContext = None
    ) -> JudgmentResult:
        """Echo JudgmentResult 형식으로 변환"""

        if not ECHO_INTEGRATION_AVAILABLE:
            raise RuntimeError("Echo 통합이 필요하지만 사용할 수 없습니다")

        return JudgmentResult(
            input_text=original_context.text if original_context else "",
            judgment=fused_result.final_judgment,
            confidence=fused_result.overall_confidence,
            reasoning=fused_result.reasoning_synthesis,
            strategy="fusion_integrated",
            emotion="multi_dimensional",
            metadata={
                "source": "fusion_judgment_loop",
                "signature": fused_result.signature_used.value,
                "fusion_strategy": fused_result.fusion_strategy.value,
                "providers_used": [
                    r.provider.value for r in fused_result.individual_responses
                ],
                "processing_summary": fused_result.processing_summary,
                "fusion_metadata": fused_result.metadata,
            },
        )


# 편의 함수들
async def create_fusion_judgment(
    input_text: str,
    signature: EchoSignature = EchoSignature.AURORA,
    providers: List[LLMProvider] = None,
    strategy: FusionStrategy = FusionStrategy.WEIGHTED_AVERAGE,
) -> FusedJudgmentResult:
    """빠른 융합 판단 생성"""

    loop = FusionJudgmentLoop()
    request = LLMJudgmentRequest(
        input_text=input_text,
        signature=signature,
        providers=providers,
        fusion_strategy=strategy,
    )

    return await loop.process_fusion_request(request)


# 전역 융합 루프 인스턴스
_fusion_loop = None


def get_fusion_judgment_loop(config: Dict[str, Any] = None) -> FusionJudgmentLoop:
    """융합 판단 루프 싱글톤 인스턴스"""
    global _fusion_loop
    if _fusion_loop is None:
        _fusion_loop = FusionJudgmentLoop(config)
    return _fusion_loop
