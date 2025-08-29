#!/usr/bin/env python3
"""
🎯 LLM Router - 지능적 모델 라우팅 시스템
Echo 판단 복잡도와 시스템 상황에 따라 최적의 LLM 선택 및 라우팅

핵심 기능:
1. 복잡도 기반 Echo ↔ Mistral ↔ External LLM 라우팅
2. 실시간 모델 상태 모니터링 및 로드밸런싱
3. 폴백 체인을 통한 안정성 보장
4. 비용 효율적 모델 선택 최적화
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

# Echo 시스템 컴포넌트들
try:
    from .mistral_wrapper import OllamaMistralWrapper as MistralWrapper
    from .llm_bridge import LLMBridge, CooperationMode, LLMProvider
    from .echo_selector import EchoSelector, ProcessingMode, ComplexityLevel

    ECHO_COMPONENTS_AVAILABLE = True
except ImportError:
    print("⚠️ Echo 컴포넌트 일부 로드 실패")
    ECHO_COMPONENTS_AVAILABLE = False


class ModelType(Enum):
    """모델 타입"""

    ECHO_NATIVE = "echo_native"  # 순수 Echo 시스템
    MISTRAL_LOCAL = "mistral_local"  # 로컬 Mistral
    EXTERNAL_API = "external_api"  # 외부 API (GPT, Claude)
    HYBRID_ECHO_MISTRAL = "hybrid_echo_mistral"  # Echo + Mistral
    HYBRID_ECHO_API = "hybrid_echo_api"  # Echo + External
    ADAPTIVE = "adaptive"  # 상황별 적응


class RouterDecision(Enum):
    """라우터 결정"""

    ROUTE_TO_ECHO = "route_to_echo"
    ROUTE_TO_MISTRAL = "route_to_mistral"
    ROUTE_TO_API = "route_to_api"
    ROUTE_TO_HYBRID = "route_to_hybrid"
    ROUTE_TO_FALLBACK = "route_to_fallback"


@dataclass
class RoutingRequest:
    """라우팅 요청"""

    user_input: str
    complexity_score: float
    urgency_level: int
    echo_analysis: Optional[str] = None
    user_context: Dict[str, Any] = None
    preferred_quality: str = "balanced"  # "speed", "quality", "balanced"
    max_cost: float = 0.01
    offline_only: bool = False


@dataclass
class RoutingResult:
    """라우팅 결과"""

    selected_model: ModelType
    decision_reasoning: List[str]
    response_text: str
    processing_time: float
    cost_estimate: float
    quality_score: float
    confidence: float
    fallback_used: bool
    model_health: Dict[str, Any]


@dataclass
class ModelHealth:
    """모델 건강 상태"""

    model_type: ModelType
    available: bool
    response_time_avg: float
    error_rate: float
    memory_usage: float
    queue_length: int
    last_check: datetime


class LLMRouter:
    """지능적 LLM 라우팅 시스템"""

    def __init__(self, config_path: str = "config/llm_router_config.yaml"):
        self.config_path = config_path

        # 모델 인스턴스들
        self.mistral_wrapper: Optional[MistralWrapper] = None
        self.llm_bridge: Optional[LLMBridge] = None
        self.echo_selector: Optional[EchoSelector] = None

        # 모델 건강 상태 모니터링
        self.model_health: Dict[ModelType, ModelHealth] = {}

        # 라우팅 통계
        self.routing_stats = {
            "total_requests": 0,
            "model_usage": {model.value: 0 for model in ModelType},
            "avg_response_times": {model.value: [] for model in ModelType},
            "success_rates": {model.value: [] for model in ModelType},
            "cost_tracking": 0.0,
        }

        # 라우팅 규칙 및 설정
        self.routing_rules = self._load_routing_rules()
        self.fallback_chain = self._setup_fallback_chain()

        # 비동기 초기화는 lazy로 변경 (첫 호출 시 실행)
        self._initialized = False

        print("🎯 LLM Router 초기화 완료")

    async def _ensure_initialized(self):
        """컴포넌트들이 초기화되었는지 확인하고, 필요시 초기화"""
        if self._initialized:
            return
        await self._initialize_components()
        self._initialized = True

    async def _initialize_components(self):
        """컴포넌트들 비동기 초기화"""
        try:
            # config/system.yaml에서 설정 로드
            config = self._load_system_config()

            # Mistral 래퍼 초기화
            if config.get("llm", {}).get("mistral", {}).get("enabled", True):
                mistral_config = config.get("llm", {}).get("mistral", {})
                self.mistral_wrapper = MistralWrapper(
                    model_path=mistral_config.get(
                        "model_path", "models/Mistral-7B-Instruct-v0.2"
                    ),
                    device=mistral_config.get("device", "auto"),
                    load_in_8bit=mistral_config.get("load_in_8bit", True),
                    config=mistral_config,
                )

            # LLM 브리지 초기화 (Claude 등)
            try:
                self.llm_bridge = LLMBridge()
            except ImportError:
                print("⚠️ LLMBridge 컴포넌트를 찾을 수 없음 - 외부 API 기능 비활성화")
                self.llm_bridge = None

            # Echo 선택기 초기화
            try:
                self.echo_selector = EchoSelector()
            except ImportError:
                print(
                    "⚠️ EchoSelector 컴포넌트를 찾을 수 없음 - Echo 네이티브 기능 제한"
                )
                self.echo_selector = None

            # 초기 건강 상태 체크
            await self._update_all_model_health()

            print("✅ LLM Router 컴포넌트 초기화 완료")

        except Exception as e:
            print(f"⚠️ 컴포넌트 초기화 실패: {e}")

    async def route_request(self, request: RoutingRequest) -> RoutingResult:
        """요청을 최적 모델로 라우팅"""

        # Lazy initialization 확인
        await self._ensure_initialized()

        start_time = time.time()
        self.routing_stats["total_requests"] += 1

        # 1. 모델 건강 상태 확인
        await self._update_critical_model_health()

        # 2. 라우팅 결정
        decision, reasoning = await self._make_routing_decision(request)

        # 3. 선택된 모델로 요청 처리
        try:
            response_text, quality_score, cost = await self._execute_routing(
                decision, request
            )
            fallback_used = False

        except Exception as e:
            print(f"⚠️ 주 모델 실패: {e}")
            # 폴백 체인 실행
            response_text, quality_score, cost, fallback_used = (
                await self._execute_fallback(request)
            )
            reasoning.append(f"폴백 모드 사용: {e}")

        # 4. 결과 정리 및 통계 업데이트
        processing_time = time.time() - start_time
        confidence = self._calculate_routing_confidence(
            decision, request, quality_score
        )

        result = RoutingResult(
            selected_model=self._decision_to_model_type(decision),
            decision_reasoning=reasoning,
            response_text=response_text,
            processing_time=processing_time,
            cost_estimate=cost,
            quality_score=quality_score,
            confidence=confidence,
            fallback_used=fallback_used,
            model_health=self._get_current_health_summary(),
        )

        # 통계 업데이트
        self._update_routing_stats(result)

        return result

    async def _make_routing_decision(
        self, request: RoutingRequest
    ) -> Tuple[RouterDecision, List[str]]:
        """라우팅 결정 로직"""

        reasoning = []

        # 1. 오프라인 전용 모드 체크
        if request.offline_only:
            if self._is_model_available(ModelType.MISTRAL_LOCAL):
                reasoning.append("오프라인 모드 - Mistral 로컬 선택")
                return RouterDecision.ROUTE_TO_MISTRAL, reasoning
            else:
                reasoning.append("오프라인 모드 - Echo 네이티브로 폴백")
                return RouterDecision.ROUTE_TO_ECHO, reasoning

        # 2. 긴급도 기반 판단
        if request.urgency_level >= 4:
            # 긴급 상황 - 속도 우선
            if self._is_model_available(ModelType.ECHO_NATIVE):
                reasoning.append("긴급 상황 - Echo 네이티브 우선")
                return RouterDecision.ROUTE_TO_ECHO, reasoning
            elif self._is_model_available(ModelType.MISTRAL_LOCAL):
                reasoning.append("긴급 상황 - Mistral 로컬 사용")
                return RouterDecision.ROUTE_TO_MISTRAL, reasoning

        # 3. 복잡도 기반 판단
        if request.complexity_score < 0.3:
            # 단순한 요청 - Echo 또는 빠른 LLM
            reasoning.append("낮은 복잡도 - 빠른 처리 모델 선택")
            if self._is_model_available(ModelType.ECHO_NATIVE):
                return RouterDecision.ROUTE_TO_ECHO, reasoning

        elif request.complexity_score > 0.7:
            # 복잡한 요청 - 하이브리드 또는 고품질 모델
            reasoning.append("높은 복잡도 - 고품질 모델 필요")

            if request.preferred_quality == "quality":
                if self._is_model_available(
                    ModelType.EXTERNAL_API
                ) and self._check_cost_constraint(
                    ModelType.EXTERNAL_API, request.max_cost
                ):
                    reasoning.append("품질 우선 - 외부 API 사용")
                    return RouterDecision.ROUTE_TO_API, reasoning

            # 하이브리드 모드 시도
            if self._is_model_available(
                ModelType.ECHO_NATIVE
            ) and self._is_model_available(ModelType.MISTRAL_LOCAL):
                reasoning.append("하이브리드 모드 - Echo + Mistral")
                return RouterDecision.ROUTE_TO_HYBRID, reasoning

        # 4. 품질 선호도 기반 판단
        if request.preferred_quality == "speed":
            # 속도 우선
            if self._is_model_available(ModelType.ECHO_NATIVE):
                reasoning.append("속도 우선 - Echo 네이티브")
                return RouterDecision.ROUTE_TO_ECHO, reasoning

        elif request.preferred_quality == "quality":
            # 품질 우선
            if self._is_model_available(
                ModelType.EXTERNAL_API
            ) and self._check_cost_constraint(ModelType.EXTERNAL_API, request.max_cost):
                reasoning.append("품질 우선 - 외부 API")
                return RouterDecision.ROUTE_TO_API, reasoning

        # 5. 기본 라우팅 - 균형 모드
        reasoning.append("기본 라우팅 - 균형 모드")

        if self._is_model_available(ModelType.MISTRAL_LOCAL):
            reasoning.append("Mistral 로컬 사용 가능")
            return RouterDecision.ROUTE_TO_MISTRAL, reasoning
        elif self._is_model_available(ModelType.ECHO_NATIVE):
            reasoning.append("Echo 네이티브로 폴백")
            return RouterDecision.ROUTE_TO_ECHO, reasoning
        else:
            reasoning.append("모든 모델 실패 - 폴백 체인 실행")
            return RouterDecision.ROUTE_TO_FALLBACK, reasoning

    async def _execute_routing(
        self, decision: RouterDecision, request: RoutingRequest
    ) -> Tuple[str, float, float]:
        """라우팅 결정 실행"""

        if decision == RouterDecision.ROUTE_TO_ECHO:
            return await self._route_to_echo(request)

        elif decision == RouterDecision.ROUTE_TO_MISTRAL:
            return await self._route_to_mistral(request)

        elif decision == RouterDecision.ROUTE_TO_API:
            return await self._route_to_api(request)

        elif decision == RouterDecision.ROUTE_TO_HYBRID:
            return await self._route_to_hybrid(request)

        else:  # ROUTE_TO_FALLBACK
            return await self._route_to_fallback(request)

    async def _route_to_echo(self, request: RoutingRequest) -> Tuple[str, float, float]:
        """Echo 네이티브 라우팅"""

        # Echo 시스템을 통한 순수 판단
        if request.echo_analysis:
            response_text = request.echo_analysis
        else:
            # 간소화된 Echo 응답 시뮬레이션
            if request.urgency_level >= 3:
                response_text = "상황을 신중히 고려해보겠습니다."
            else:
                response_text = "말씀해주신 내용을 이해했습니다."

        quality_score = 0.8  # Echo의 일관된 품질
        cost = 0.0  # 내부 처리 비용 없음

        return response_text, quality_score, cost

    async def _route_to_mistral(
        self, request: RoutingRequest
    ) -> Tuple[str, float, float]:
        """Mistral 로컬 라우팅"""

        if not self.mistral_wrapper:
            raise RuntimeError("Mistral wrapper not available")

        # 요청 컨텍스트 준비
        user_context = request.user_context or {}
        user_context.update(
            {
                "urgency_level": request.urgency_level,
                "complexity_score": request.complexity_score,
            }
        )

        if request.echo_analysis:
            # Echo 분석이 있으면 보조 모드
            result = await self.mistral_wrapper.assist_echo_judgment(
                request.echo_analysis, user_context, MistralMode.ECHO_ASSIST
            )
        else:
            # 독립적 협력 판단
            result = await self.mistral_wrapper.cooperative_judgment(request.user_input)

        return result.text, result.confidence, 0.001  # 로컬 처리 최소 비용

    async def _route_to_api(self, request: RoutingRequest) -> Tuple[str, float, float]:
        """외부 API 라우팅"""

        if not self.llm_bridge:
            raise RuntimeError("LLM bridge not available")

        # LLM 브리지를 통한 외부 API 호출
        cooperation_result = await self.llm_bridge.cooperate_with_echo(
            request.echo_analysis or "사용자 요청 처리",
            CooperationMode.ECHO_THEN_LLM,
            request.user_context,
        )

        return (
            cooperation_result.final_response,
            cooperation_result.quality_metrics.get("overall_quality", 0.8),
            sum(cooperation_result.cost_breakdown.values()),
        )

    async def _route_to_hybrid(
        self, request: RoutingRequest
    ) -> Tuple[str, float, float]:
        """하이브리드 라우팅 (Echo + Mistral)"""

        # Echo 분석 먼저 수행
        echo_response, echo_quality, echo_cost = await self._route_to_echo(request)

        # Mistral로 개선
        enhanced_request = RoutingRequest(
            user_input=request.user_input,
            complexity_score=request.complexity_score,
            urgency_level=request.urgency_level,
            echo_analysis=echo_response,
            user_context=request.user_context,
        )

        mistral_response, mistral_quality, mistral_cost = await self._route_to_mistral(
            enhanced_request
        )

        # 두 결과의 가중 평균
        combined_quality = echo_quality * 0.4 + mistral_quality * 0.6
        total_cost = echo_cost + mistral_cost

        return mistral_response, combined_quality, total_cost

    async def _route_to_fallback(
        self, request: RoutingRequest
    ) -> Tuple[str, float, float]:
        """폴백 라우팅"""

        # 최소한의 응답 제공
        fallback_responses = [
            "현재 시스템을 정비 중입니다. 잠시 후 다시 시도해주세요.",
            "요청을 처리하는 중 문제가 발생했습니다.",
            "Echo 시스템이 최선을 다해 응답하겠습니다.",
        ]

        response_text = fallback_responses[
            request.urgency_level % len(fallback_responses)
        ]
        quality_score = 0.3  # 낮은 품질
        cost = 0.0

        return response_text, quality_score, cost

    async def _execute_fallback(
        self, request: RoutingRequest
    ) -> Tuple[str, float, float, bool]:
        """폴백 체인 실행"""

        for fallback_model in self.fallback_chain:
            try:
                if fallback_model == ModelType.ECHO_NATIVE:
                    response, quality, cost = await self._route_to_echo(request)
                    return response, quality, cost, True

                elif (
                    fallback_model == ModelType.MISTRAL_LOCAL
                    and self._is_model_available(ModelType.MISTRAL_LOCAL)
                ):
                    response, quality, cost = await self._route_to_mistral(request)
                    return response, quality, cost, True

            except Exception as e:
                print(f"⚠️ 폴백 모델 {fallback_model.value} 실패: {e}")
                continue

        # 모든 폴백 실패 시 최종 응답
        response, quality, cost = await self._route_to_fallback(request)
        return response, quality, cost, True

    def _is_model_available(self, model_type: ModelType) -> bool:
        """모델 사용 가능 여부 확인"""

        if model_type == ModelType.ECHO_NATIVE:
            return True  # Echo는 항상 사용 가능

        elif model_type == ModelType.MISTRAL_LOCAL:
            return (
                self.mistral_wrapper is not None and self.mistral_wrapper.model_loaded
            )

        elif model_type == ModelType.EXTERNAL_API:
            return self.llm_bridge is not None

        health = self.model_health.get(model_type)
        return health is not None and health.available

    def _check_cost_constraint(self, model_type: ModelType, max_cost: float) -> bool:
        """비용 제약 확인"""

        estimated_costs = {
            ModelType.ECHO_NATIVE: 0.0,
            ModelType.MISTRAL_LOCAL: 0.001,
            ModelType.EXTERNAL_API: 0.02,
            ModelType.HYBRID_ECHO_MISTRAL: 0.001,
            ModelType.HYBRID_ECHO_API: 0.02,
        }

        estimated_cost = estimated_costs.get(model_type, 0.01)
        return estimated_cost <= max_cost

    def _decision_to_model_type(self, decision: RouterDecision) -> ModelType:
        """결정을 모델 타입으로 변환"""

        mapping = {
            RouterDecision.ROUTE_TO_ECHO: ModelType.ECHO_NATIVE,
            RouterDecision.ROUTE_TO_MISTRAL: ModelType.MISTRAL_LOCAL,
            RouterDecision.ROUTE_TO_API: ModelType.EXTERNAL_API,
            RouterDecision.ROUTE_TO_HYBRID: ModelType.HYBRID_ECHO_MISTRAL,
            RouterDecision.ROUTE_TO_FALLBACK: ModelType.ECHO_NATIVE,
        }

        return mapping.get(decision, ModelType.ADAPTIVE)

    def _calculate_routing_confidence(
        self, decision: RouterDecision, request: RoutingRequest, quality_score: float
    ) -> float:
        """라우팅 신뢰도 계산"""

        base_confidence = 0.7

        # 모델 건강 상태 기반 조정
        model_type = self._decision_to_model_type(decision)
        if self._is_model_available(model_type):
            base_confidence += 0.1

        # 복잡도와 모델 매칭 적절성
        if request.complexity_score < 0.3 and decision == RouterDecision.ROUTE_TO_ECHO:
            base_confidence += 0.1
        elif (
            request.complexity_score > 0.7
            and decision == RouterDecision.ROUTE_TO_HYBRID
        ):
            base_confidence += 0.1

        # 품질 점수 반영
        base_confidence += (quality_score - 0.5) * 0.2

        return min(base_confidence, 1.0)

    async def _update_all_model_health(self):
        """모든 모델 건강 상태 업데이트"""

        for model_type in ModelType:
            await self._update_model_health(model_type)

    async def _update_critical_model_health(self):
        """중요 모델들의 건강 상태만 빠르게 업데이트"""

        critical_models = [
            ModelType.ECHO_NATIVE,
            ModelType.MISTRAL_LOCAL,
            ModelType.EXTERNAL_API,
        ]

        for model_type in critical_models:
            await self._update_model_health(model_type)

    async def _update_model_health(self, model_type: ModelType):
        """특정 모델의 건강 상태 업데이트"""

        try:
            start_time = time.time()

            if model_type == ModelType.ECHO_NATIVE:
                # Echo는 항상 사용 가능
                available = True
                response_time = 0.1
                error_rate = 0.01
                memory_usage = 0.1
                queue_length = 0

            elif model_type == ModelType.MISTRAL_LOCAL:
                available = (
                    self.mistral_wrapper is not None
                    and self.mistral_wrapper.model_loaded
                )
                if available:
                    status = self.mistral_wrapper.get_model_status()
                    response_time = status.get("avg_processing_time", 1.0)
                    error_rate = status.get("error_count", 0) / max(
                        status.get("total_requests", 1), 1
                    )
                    memory_usage = status.get("memory_usage_gb", 0)
                    queue_length = 0
                else:
                    response_time = float("inf")
                    error_rate = 1.0
                    memory_usage = 0
                    queue_length = 0

            elif model_type == ModelType.EXTERNAL_API:
                available = self.llm_bridge is not None
                response_time = 2.0  # 외부 API는 일반적으로 느림
                error_rate = 0.05
                memory_usage = 0  # 외부 서비스
                queue_length = 0

            else:
                # 기타 모델들
                available = False
                response_time = float("inf")
                error_rate = 1.0
                memory_usage = 0
                queue_length = 0

            self.model_health[model_type] = ModelHealth(
                model_type=model_type,
                available=available,
                response_time_avg=response_time,
                error_rate=error_rate,
                memory_usage=memory_usage,
                queue_length=queue_length,
                last_check=datetime.now(),
            )

        except Exception as e:
            print(f"⚠️ {model_type.value} 건강 상태 업데이트 실패: {e}")

            # 실패한 모델은 사용 불가로 표시
            self.model_health[model_type] = ModelHealth(
                model_type=model_type,
                available=False,
                response_time_avg=float("inf"),
                error_rate=1.0,
                memory_usage=0,
                queue_length=0,
                last_check=datetime.now(),
            )

    def _get_current_health_summary(self) -> Dict[str, Any]:
        """현재 모델 건강 상태 요약"""

        summary = {}
        for model_type, health in self.model_health.items():
            summary[model_type.value] = {
                "available": health.available,
                "response_time": health.response_time_avg,
                "error_rate": health.error_rate,
                "last_check": (
                    health.last_check.isoformat() if health.last_check else None
                ),
            }

        return summary

    def _update_routing_stats(self, result: RoutingResult):
        """라우팅 통계 업데이트"""

        model_key = result.selected_model.value

        # 모델 사용 카운트
        self.routing_stats["model_usage"][model_key] += 1

        # 응답 시간 기록
        self.routing_stats["avg_response_times"][model_key].append(
            result.processing_time
        )
        if len(self.routing_stats["avg_response_times"][model_key]) > 100:
            self.routing_stats["avg_response_times"][model_key] = self.routing_stats[
                "avg_response_times"
            ][model_key][-100:]

        # 성공률 기록
        success = 1.0 if result.quality_score > 0.5 else 0.0
        self.routing_stats["success_rates"][model_key].append(success)
        if len(self.routing_stats["success_rates"][model_key]) > 100:
            self.routing_stats["success_rates"][model_key] = self.routing_stats[
                "success_rates"
            ][model_key][-100:]

        # 비용 추적
        self.routing_stats["cost_tracking"] += result.cost_estimate

    def _load_routing_rules(self) -> Dict[str, Any]:
        """라우팅 규칙 로드"""

        # 기본 라우팅 규칙
        return {
            "complexity_thresholds": {"simple": 0.3, "moderate": 0.5, "complex": 0.7},
            "urgency_mappings": {
                1: "echo_native",
                2: "mistral_local",
                3: "mistral_local",
                4: "echo_native",  # 긴급시 빠른 응답
                5: "echo_native",
            },
            "quality_preferences": {
                "speed": ["echo_native", "mistral_local"],
                "balanced": ["mistral_local", "hybrid_echo_mistral"],
                "quality": ["external_api", "hybrid_echo_api"],
            },
        }

    def _setup_fallback_chain(self) -> List[ModelType]:
        """폴백 체인 설정"""

        return [
            ModelType.ECHO_NATIVE,  # 1차 폴백 (항상 사용 가능)
            ModelType.MISTRAL_LOCAL,  # 2차 폴백 (로컬 모델)
            ModelType.EXTERNAL_API,  # 3차 폴백 (외부 API)
        ]

    def _load_system_config(self) -> Dict[str, Any]:
        """시스템 설정 로드"""
        try:
            import yaml

            config_path = Path("config/system.yaml")
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ 시스템 설정 로드 실패: {e}")

        # 기본 설정 반환
        return {
            "llm": {
                "primary_mode": "mistral",
                "mistral": {
                    "enabled": True,
                    "model_path": "models/Mistral-7B-Instruct-v0.2",
                    "device": "auto",
                    "load_in_8bit": True,
                    "temperature": 0.7,
                    "max_tokens": 512,
                },
            }
        }

    def get_routing_analytics(self) -> Dict[str, Any]:
        """라우팅 분석 데이터 반환"""

        analytics = {
            "total_requests": self.routing_stats["total_requests"],
            "model_distribution": self.routing_stats["model_usage"],
            "total_cost": self.routing_stats["cost_tracking"],
            "model_performance": {},
            "health_summary": self._get_current_health_summary(),
        }

        # 모델별 성능 계산
        for model_key in ModelType:
            model_value = model_key.value

            response_times = self.routing_stats["avg_response_times"][model_value]
            success_rates = self.routing_stats["success_rates"][model_value]

            analytics["model_performance"][model_value] = {
                "avg_response_time": sum(response_times) / max(len(response_times), 1),
                "success_rate": sum(success_rates) / max(len(success_rates), 1),
                "usage_count": self.routing_stats["model_usage"][model_value],
            }

        return analytics

    async def health_check(self) -> Dict[str, Any]:
        """전체 시스템 건강 상태 확인"""

        await self._update_all_model_health()

        return {
            "router_status": "healthy",
            "models_available": sum(
                1 for health in self.model_health.values() if health.available
            ),
            "total_models": len(self.model_health),
            "model_details": self._get_current_health_summary(),
            "routing_stats": self.routing_stats,
            "last_check": datetime.now().isoformat(),
        }


# 사용 예시 및 테스트
if __name__ == "__main__":

    async def test_llm_router():
        print("🎯 LLM Router 테스트")
        print("=" * 60)

        router = LLMRouter()

        # 초기화 대기
        await asyncio.sleep(2)

        # 건강 상태 확인
        health = await router.health_check()
        print(
            f"사용 가능한 모델: {health['models_available']}/{health['total_models']}"
        )

        # 다양한 라우팅 시나리오 테스트
        test_cases = [
            {
                "user_input": "안녕하세요",
                "complexity_score": 0.1,
                "urgency_level": 1,
                "preferred_quality": "speed",
                "description": "간단한 인사 - 속도 우선",
            },
            {
                "user_input": "인생의 의미에 대해 깊이 고민하고 있습니다",
                "complexity_score": 0.8,
                "urgency_level": 2,
                "preferred_quality": "quality",
                "max_cost": 0.05,
                "description": "복잡한 철학적 질문 - 품질 우선",
            },
            {
                "user_input": "급한 결정을 내려야 합니다!",
                "complexity_score": 0.6,
                "urgency_level": 4,
                "preferred_quality": "speed",
                "description": "긴급 상황 - 속도 최우선",
            },
            {
                "user_input": "AI와 인간의 협력에 대한 견해",
                "complexity_score": 0.7,
                "urgency_level": 2,
                "preferred_quality": "balanced",
                "offline_only": True,
                "description": "오프라인 모드 - 로컬 처리만",
            },
        ]

        for i, case in enumerate(test_cases):
            print(f"\n--- 테스트 {i+1}: {case['description']} ---")

            request = RoutingRequest(
                user_input=case["user_input"],
                complexity_score=case["complexity_score"],
                urgency_level=case["urgency_level"],
                preferred_quality=case.get("preferred_quality", "balanced"),
                max_cost=case.get("max_cost", 0.01),
                offline_only=case.get("offline_only", False),
            )

            try:
                result = await router.route_request(request)

                print(f"선택된 모델: {result.selected_model.value}")
                print(f"응답: {result.response_text[:100]}...")
                print(f"처리시간: {result.processing_time:.3f}초")
                print(f"품질 점수: {result.quality_score:.2f}")
                print(f"신뢰도: {result.confidence:.2f}")
                print(f"비용: ${result.cost_estimate:.4f}")
                print(f"폴백 사용: {result.fallback_used}")

                if result.decision_reasoning:
                    print("결정 과정:")
                    for reason in result.decision_reasoning:
                        print(f"  • {reason}")

            except Exception as e:
                print(f"❌ 테스트 실패: {e}")

            print("-" * 40)

        # 최종 분석
        analytics = router.get_routing_analytics()
        print(f"\n📊 라우팅 분석:")
        print(f"총 요청: {analytics['total_requests']}")
        print(f"총 비용: ${analytics['total_cost']:.4f}")
        print("모델별 사용 분포:", analytics["model_distribution"])

        print("\n🎉 LLM Router 테스트 완료!")

    asyncio.run(test_llm_router())
