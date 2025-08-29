#!/usr/bin/env python3
"""
🧭 Meta Routing Controller v1.0
판단⨯감정⨯시그니처 간 지능형 자동 전환 및 라우팅 시스템

핵심 기능:
- 실시간 컨텍스트 분석 기반 라우팅
- 다차원 의사결정 트리 구성
- 적응적 라우팅 규칙 학습
- 시그니처 간 seamless 전환
- 메타인지 기반 최적화
"""

import json
import numpy as np
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import logging

# Echo 엔진 모듈들
try:
    from .signature_cross_resonance_mapper import SignatureCrossResonanceMapper
    from .realtime_emotion_flow_mapper import RealtimeEmotionFlowMapper, EmotionState
    from .consciousness_flow_analyzer import (
        ConsciousnessFlowAnalyzer,
        ConsciousnessLevel,
    )
    from .hybrid_signature_composer import (
        HybridSignatureComposer,
        ContextType,
        BlendingMode,
    )
    from .loop_evolution_tracker import LoopEvolutionTracker
except ImportError:
    print("⚠️ Echo modules not available, running in standalone mode")


class RoutingDecisionType(Enum):
    """라우팅 결정 타입"""

    SIGNATURE_SELECTION = "signature_selection"  # 단일 시그니처 선택
    HYBRID_COMPOSITION = "hybrid_composition"  # 하이브리드 구성
    LOOP_OPTIMIZATION = "loop_optimization"  # 루프 최적화
    CONTEXT_ADAPTATION = "context_adaptation"  # 컨텍스트 적응
    EMERGENCY_FALLBACK = "emergency_fallback"  # 비상 대체


class RoutingPriority(Enum):
    """라우팅 우선순위"""

    CRITICAL = 1  # 긴급 처리 필요
    HIGH = 2  # 높은 우선순위
    NORMAL = 3  # 일반 우선순위
    LOW = 4  # 낮은 우선순위
    BACKGROUND = 5  # 백그라운드 처리


@dataclass
class RoutingContext:
    """라우팅 컨텍스트"""

    context_id: str
    timestamp: datetime
    input_type: str  # "text", "emotion", "task", "system"
    input_content: Any
    user_intent: str
    emotion_state: Dict[str, float]
    complexity_level: float
    urgency_level: float
    user_history: Dict[str, Any]
    environmental_factors: Dict[str, Any]


@dataclass
class RoutingDecision:
    """라우팅 결정"""

    decision_id: str
    timestamp: datetime
    decision_type: RoutingDecisionType
    routing_target: str  # 대상 시그니처 또는 구성
    confidence_score: float
    reasoning_chain: List[str]
    alternative_options: List[Dict[str, Any]]
    execution_priority: RoutingPriority
    expected_performance: float


@dataclass
class RoutingRule:
    """라우팅 규칙"""

    rule_id: str
    rule_name: str
    condition_pattern: Dict[str, Any]
    routing_action: Dict[str, Any]
    priority: int
    success_rate: float
    usage_count: int
    last_updated: datetime
    adaptive_weights: Dict[str, float]


@dataclass
class RoutingPerformance:
    """라우팅 성능"""

    timestamp: datetime
    decision_id: str
    actual_performance: float
    user_satisfaction: float
    execution_time_ms: float
    accuracy_score: float
    efficiency_score: float
    adaptability_score: float


class MetaRoutingController:
    """🧭 메타 라우팅 컨트롤러"""

    def __init__(self, learning_rate: float = 0.1):
        self.logger = logging.getLogger(__name__)
        self.learning_rate = learning_rate

        # 핵심 컴포넌트들
        self.signature_performance_reporter = None
        self.emotion_mapper = None
        self.consciousness_analyzer = None
        self.hybrid_composer = None
        self.loop_tracker = None

        # 라우팅 상태
        self.active_routing_context = None
        self.routing_history = deque(maxlen=100)
        self.performance_history = deque(maxlen=200)
        self.routing_rules = {}

        # 학습 데이터
        self.decision_patterns = defaultdict(list)
        self.success_patterns = defaultdict(float)
        self.context_signatures = defaultdict(str)

        # 실시간 모니터링
        self.monitoring = False
        self.monitor_thread = None
        self.routing_callbacks = []

        # 기본 라우팅 규칙 정의
        self._initialize_default_routing_rules()

        # 성능 메트릭
        self.routing_statistics = {
            "total_decisions": 0,
            "successful_routes": 0,
            "fallback_activations": 0,
            "average_confidence": 0.0,
            "average_performance": 0.0,
        }

        print("🧭 Meta Routing Controller 초기화 완료")

    def initialize_components(
        self,
        signature_performance_reporter: SignatureCrossResonanceMapper = None,
        emotion_mapper: RealtimeEmotionFlowMapper = None,
        consciousness_analyzer: ConsciousnessFlowAnalyzer = None,
        hybrid_composer: HybridSignatureComposer = None,
        loop_tracker: LoopEvolutionTracker = None,
    ):
        """컴포넌트 초기화"""
        self.signature_performance_reporter = (
            signature_performance_reporter or SignatureCrossResonanceMapper()
        )
        self.emotion_mapper = emotion_mapper or RealtimeEmotionFlowMapper()
        self.consciousness_analyzer = (
            consciousness_analyzer or ConsciousnessFlowAnalyzer()
        )
        self.hybrid_composer = hybrid_composer or HybridSignatureComposer()
        self.loop_tracker = loop_tracker or LoopEvolutionTracker()

        print("🔗 Meta Routing Controller 컴포넌트 연결 완료")

    def _initialize_default_routing_rules(self):
        """기본 라우팅 규칙 초기화"""

        # 감정 기반 라우팅 규칙
        self.routing_rules["high_emotion_selene"] = RoutingRule(
            rule_id="high_emotion_selene",
            rule_name="High Emotion -> Selene",
            condition_pattern={
                "emotion_intensity": {"min": 0.7},
                "emotion_types": ["sadness", "melancholy", "vulnerability"],
            },
            routing_action={"target": "selene", "confidence_boost": 0.2},
            priority=2,
            success_rate=0.85,
            usage_count=0,
            last_updated=datetime.now(),
            adaptive_weights={"emotion": 0.8, "context": 0.2},
        )

        # 논리적 분석 기반 라우팅
        self.routing_rules["analytical_factbomb"] = RoutingRule(
            rule_id="analytical_factbomb",
            rule_name="Analytical Task -> FactBomb",
            condition_pattern={
                "complexity_level": {"min": 0.6},
                "task_type": ["analysis", "calculation", "fact_checking"],
            },
            routing_action={"target": "factbomb", "confidence_boost": 0.3},
            priority=1,
            success_rate=0.9,
            usage_count=0,
            last_updated=datetime.now(),
            adaptive_weights={"complexity": 0.7, "accuracy": 0.3},
        )

        # 창조적 작업 라우팅
        self.routing_rules["creative_lune"] = RoutingRule(
            rule_id="creative_lune",
            rule_name="Creative Task -> Lune",
            condition_pattern={
                "creativity_required": {"min": 0.6},
                "task_type": ["creative", "artistic", "poetic"],
            },
            routing_action={"target": "lune", "confidence_boost": 0.25},
            priority=2,
            success_rate=0.8,
            usage_count=0,
            last_updated=datetime.now(),
            adaptive_weights={"creativity": 0.9, "emotion": 0.1},
        )

        # 지원적 상황 라우팅
        self.routing_rules["supportive_aurora"] = RoutingRule(
            rule_id="supportive_aurora",
            rule_name="Supportive Context -> Aurora",
            condition_pattern={
                "support_needed": {"min": 0.6},
                "emotion_types": ["hope", "encouragement", "growth"],
            },
            routing_action={"target": "aurora", "confidence_boost": 0.2},
            priority=2,
            success_rate=0.82,
            usage_count=0,
            last_updated=datetime.now(),
            adaptive_weights={"support": 0.7, "emotion": 0.3},
        )

        # 복합 상황 하이브리드 라우팅
        self.routing_rules["complex_hybrid"] = RoutingRule(
            rule_id="complex_hybrid",
            rule_name="Complex Situation -> Hybrid",
            condition_pattern={
                "complexity_level": {"min": 0.8},
                "multiple_requirements": True,
            },
            routing_action={
                "target": "hybrid_composition",
                "blending_mode": "adaptive_morphing",
            },
            priority=1,
            success_rate=0.75,
            usage_count=0,
            last_updated=datetime.now(),
            adaptive_weights={"complexity": 0.5, "versatility": 0.5},
        )

    def start_monitoring(self, callbacks: List[Callable] = None):
        """라우팅 모니터링 시작"""
        if self.monitoring:
            print("⚠️ 이미 메타 라우팅 모니터링이 실행 중입니다.")
            return

        self.monitoring = True
        self.routing_callbacks = callbacks or []

        # 모니터링 스레드 시작
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        print("🧭 메타 라우팅 모니터링 시작...")

    def stop_monitoring(self):
        """라우팅 모니터링 정지"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        print("🧭 메타 라우팅 모니터링 정지")

    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring:
            try:
                # 컨텍스트 상태 분석
                if self.active_routing_context:
                    self._analyze_routing_context(self.active_routing_context)

                # 성능 지표 업데이트
                self._update_performance_metrics()

                # 적응적 규칙 조정
                self._adapt_routing_rules()

                # 콜백 함수들 호출
                for callback in self.routing_callbacks:
                    try:
                        callback(self.get_routing_status())
                    except Exception as e:
                        self.logger.error(f"라우팅 콜백 오류: {e}")

                time.sleep(1.0)  # 1초마다 모니터링

            except Exception as e:
                self.logger.error(f"라우팅 모니터링 루프 오류: {e}")
                time.sleep(1)

    def route_request(
        self,
        input_data: Any,
        input_type: str = "text",
        user_context: Dict[str, Any] = None,
    ) -> RoutingDecision:
        """요청 라우팅"""

        # 라우팅 컨텍스트 생성
        routing_context = self._create_routing_context(
            input_data, input_type, user_context
        )
        self.active_routing_context = routing_context

        # 컨텍스트 분석
        context_analysis = self._analyze_routing_context(routing_context)

        # 라우팅 옵션 생성
        routing_options = self._generate_routing_options(
            routing_context, context_analysis
        )

        # 최적 라우팅 결정
        best_decision = self._select_best_routing(routing_options, routing_context)

        # 결정 기록
        self.routing_history.append(best_decision)
        self.routing_statistics["total_decisions"] += 1

        # 학습 데이터 수집
        self._collect_learning_data(routing_context, best_decision)

        return best_decision

    def _create_routing_context(
        self, input_data: Any, input_type: str, user_context: Dict[str, Any] = None
    ) -> RoutingContext:
        """라우팅 컨텍스트 생성"""

        # 사용자 의도 추론
        user_intent = self._infer_user_intent(input_data, input_type)

        # 감정 상태 분석
        emotion_state = self._analyze_emotion_state(input_data, user_context)

        # 복잡성 수준 계산
        complexity_level = self._calculate_complexity_level(input_data, user_intent)

        # 긴급성 수준 계산
        urgency_level = self._calculate_urgency_level(input_data, user_context)

        # 환경적 요인 분석
        environmental_factors = self._analyze_environmental_factors(user_context)

        context = RoutingContext(
            context_id=f"ctx_{int(time.time())}_{len(self.routing_history)}",
            timestamp=datetime.now(),
            input_type=input_type,
            input_content=input_data,
            user_intent=user_intent,
            emotion_state=emotion_state,
            complexity_level=complexity_level,
            urgency_level=urgency_level,
            user_history=user_context or {},
            environmental_factors=environmental_factors,
        )

        return context

    def _infer_user_intent(self, input_data: Any, input_type: str) -> str:
        """사용자 의도 추론"""
        if input_type == "text" and isinstance(input_data, str):
            # 간단한 키워드 기반 의도 분류
            text_lower = input_data.lower()

            if any(
                word in text_lower for word in ["analyze", "calculate", "fact", "data"]
            ):
                return "analytical"
            elif any(
                word in text_lower for word in ["help", "support", "encourage", "guide"]
            ):
                return "supportive"
            elif any(
                word in text_lower for word in ["create", "write", "imagine", "dream"]
            ):
                return "creative"
            elif any(
                word in text_lower for word in ["feel", "emotion", "sad", "happy"]
            ):
                return "emotional"
            elif any(
                word in text_lower for word in ["solve", "problem", "issue", "fix"]
            ):
                return "problem_solving"
            else:
                return "conversational"

        return "general"

    def _analyze_emotion_state(
        self, input_data: Any, user_context: Dict[str, Any] = None
    ) -> Dict[str, float]:
        """감정 상태 분석"""
        emotion_state = {
            "intensity": 0.5,
            "valence": 0.5,  # positive/negative
            "arousal": 0.5,  # calm/excited
            "dominance": 0.5,  # submissive/dominant
        }

        if isinstance(input_data, str):
            text = input_data.lower()

            # 간단한 감정 분석
            positive_words = ["happy", "good", "great", "love", "joy", "excited"]
            negative_words = ["sad", "bad", "terrible", "hate", "angry", "frustrated"]
            high_arousal_words = ["excited", "angry", "anxious", "energetic"]

            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)
            arousal_count = sum(1 for word in high_arousal_words if word in text)

            # 감정 강도
            emotion_state["intensity"] = min(
                1.0, (positive_count + negative_count) * 0.2 + 0.3
            )

            # 감정 극성
            if positive_count > negative_count:
                emotion_state["valence"] = 0.6 + positive_count * 0.1
            elif negative_count > positive_count:
                emotion_state["valence"] = 0.4 - negative_count * 0.1

            # 각성 수준
            emotion_state["arousal"] = 0.5 + arousal_count * 0.1

            # 정규화
            for key in emotion_state:
                emotion_state[key] = max(0.0, min(1.0, emotion_state[key]))

        return emotion_state

    def _calculate_complexity_level(self, input_data: Any, user_intent: str) -> float:
        """복잡성 수준 계산"""
        base_complexity = 0.3

        if isinstance(input_data, str):
            text = input_data

            # 텍스트 길이 기반
            length_factor = min(1.0, len(text) / 500.0)

            # 복잡한 키워드 기반
            complex_words = [
                "analyze",
                "optimize",
                "integrate",
                "synthesize",
                "evaluate",
            ]
            complex_count = sum(
                1 for word in complex_words if word.lower() in text.lower()
            )

            # 의도별 기본 복잡성
            intent_complexity = {
                "analytical": 0.8,
                "problem_solving": 0.7,
                "creative": 0.6,
                "supportive": 0.4,
                "emotional": 0.3,
                "conversational": 0.2,
            }.get(user_intent, 0.3)

            complexity = (
                base_complexity * 0.3
                + length_factor * 0.2
                + complex_count * 0.1
                + intent_complexity * 0.4
            )

            return max(0.0, min(1.0, complexity))

        return base_complexity

    def _calculate_urgency_level(
        self, input_data: Any, user_context: Dict[str, Any] = None
    ) -> float:
        """긴급성 수준 계산"""
        urgency = 0.3  # 기본 긴급성

        if isinstance(input_data, str):
            text = input_data.lower()

            # 긴급성 키워드
            urgent_words = [
                "urgent",
                "emergency",
                "asap",
                "immediately",
                "quick",
                "fast",
            ]
            urgent_count = sum(1 for word in urgent_words if word in text)

            urgency += urgent_count * 0.2

        # 사용자 컨텍스트에서 긴급성 정보
        if user_context:
            urgency += user_context.get("urgency_modifier", 0.0)

        return max(0.0, min(1.0, urgency))

    def _analyze_environmental_factors(
        self, user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """환경적 요인 분석"""
        factors = {
            "time_of_day": datetime.now().hour,
            "system_load": 0.5,  # 시스템 부하 (실제로는 측정 필요)
            "user_mood": 0.5,  # 사용자 기분 (실제로는 추적 필요)
            "session_length": 1,  # 세션 길이 (분)
        }

        if user_context:
            factors.update(user_context.get("environmental", {}))

        return factors

    def _analyze_routing_context(self, context: RoutingContext) -> Dict[str, Any]:
        """라우팅 컨텍스트 분석"""
        analysis = {
            "primary_dimension": self._identify_primary_dimension(context),
            "secondary_dimensions": self._identify_secondary_dimensions(context),
            "conflict_indicators": self._detect_conflicts(context),
            "optimization_opportunities": self._identify_optimizations(context),
            "risk_factors": self._assess_risks(context),
        }

        return analysis

    def _identify_primary_dimension(self, context: RoutingContext) -> str:
        """주요 차원 식별"""
        dimensions = {
            "emotion": context.emotion_state["intensity"],
            "complexity": context.complexity_level,
            "urgency": context.urgency_level,
            "creativity": 0.8 if context.user_intent == "creative" else 0.2,
            "analysis": 0.8 if context.user_intent == "analytical" else 0.2,
            "support": 0.8 if context.user_intent == "supportive" else 0.2,
        }

        return max(dimensions.items(), key=lambda x: x[1])[0]

    def _identify_secondary_dimensions(self, context: RoutingContext) -> List[str]:
        """보조 차원들 식별"""
        dimensions = {
            "emotion": context.emotion_state["intensity"],
            "complexity": context.complexity_level,
            "urgency": context.urgency_level,
        }

        # 상위 30% 이상인 차원들을 보조 차원으로 식별
        threshold = 0.3
        secondary = [dim for dim, value in dimensions.items() if value >= threshold]

        return secondary[:3]  # 최대 3개까지

    def _detect_conflicts(self, context: RoutingContext) -> List[str]:
        """충돌 요소 감지"""
        conflicts = []

        # 고복잡성 + 고긴급성 충돌
        if context.complexity_level > 0.7 and context.urgency_level > 0.7:
            conflicts.append("complexity_urgency_conflict")

        # 감정적 요구 + 분석적 요구 충돌
        if (
            context.emotion_state["intensity"] > 0.7
            and context.user_intent == "analytical"
        ):
            conflicts.append("emotion_analysis_conflict")

        # 창조적 요구 + 사실 중심 요구 충돌
        if (
            context.user_intent == "creative"
            and "fact" in str(context.input_content).lower()
        ):
            conflicts.append("creativity_facts_conflict")

        return conflicts

    def _identify_optimizations(self, context: RoutingContext) -> List[str]:
        """최적화 기회 식별"""
        optimizations = []

        # 하이브리드 구성 기회
        if len(self._identify_secondary_dimensions(context)) >= 2:
            optimizations.append("hybrid_composition_opportunity")

        # 캐시 활용 기회
        if context.user_intent in ["analytical", "factual"]:
            optimizations.append("caching_opportunity")

        # 병렬 처리 기회
        if context.complexity_level > 0.6:
            optimizations.append("parallel_processing_opportunity")

        return optimizations

    def _assess_risks(self, context: RoutingContext) -> List[str]:
        """위험 요소 평가"""
        risks = []

        # 높은 감정 강도로 인한 편향 위험
        if context.emotion_state["intensity"] > 0.8:
            risks.append("emotional_bias_risk")

        # 높은 복잡성으로 인한 처리 지연 위험
        if context.complexity_level > 0.8:
            risks.append("processing_delay_risk")

        # 높은 긴급성으로 인한 품질 저하 위험
        if context.urgency_level > 0.8:
            risks.append("quality_degradation_risk")

        return risks

    def _generate_routing_options(
        self, context: RoutingContext, analysis: Dict[str, Any]
    ) -> List[RoutingDecision]:
        """라우팅 옵션 생성"""
        options = []

        # 규칙 기반 옵션들
        for rule_id, rule in self.routing_rules.items():
            if self._rule_matches_context(rule, context):
                decision = self._create_decision_from_rule(rule, context, analysis)
                options.append(decision)

        # 학습 기반 옵션들
        learned_options = self._generate_learned_options(context, analysis)
        options.extend(learned_options)

        # 비상 대체 옵션
        fallback_option = self._create_fallback_option(context)
        options.append(fallback_option)

        return options

    def _rule_matches_context(self, rule: RoutingRule, context: RoutingContext) -> bool:
        """규칙이 컨텍스트와 매치되는지 확인"""
        pattern = rule.condition_pattern

        # 감정 강도 조건
        if "emotion_intensity" in pattern:
            intensity_req = pattern["emotion_intensity"]
            if "min" in intensity_req:
                if context.emotion_state["intensity"] < intensity_req["min"]:
                    return False

        # 복잡성 수준 조건
        if "complexity_level" in pattern:
            complexity_req = pattern["complexity_level"]
            if "min" in complexity_req:
                if context.complexity_level < complexity_req["min"]:
                    return False

        # 작업 타입 조건
        if "task_type" in pattern:
            if context.user_intent not in pattern["task_type"]:
                return False

        # 감정 타입 조건
        if "emotion_types" in pattern:
            # 간단한 감정 타입 매칭 (실제로는 더 정교한 감정 분석 필요)
            required_emotions = pattern["emotion_types"]
            text = str(context.input_content).lower()

            emotion_found = any(emotion in text for emotion in required_emotions)
            if not emotion_found:
                return False

        return True

    def _create_decision_from_rule(
        self, rule: RoutingRule, context: RoutingContext, analysis: Dict[str, Any]
    ) -> RoutingDecision:
        """규칙으로부터 결정 생성"""
        action = rule.routing_action

        # 기본 신뢰도 계산
        base_confidence = rule.success_rate
        confidence_boost = action.get("confidence_boost", 0.0)
        final_confidence = min(1.0, base_confidence + confidence_boost)

        # 결정 타입 결정
        if action["target"] == "hybrid_composition":
            decision_type = RoutingDecisionType.HYBRID_COMPOSITION
        else:
            decision_type = RoutingDecisionType.SIGNATURE_SELECTION

        # 추론 체인 생성
        reasoning_chain = [
            f"Rule '{rule.rule_name}' matched",
            f"Context analysis: {analysis['primary_dimension']}",
            f"Confidence: {final_confidence:.3f}",
        ]

        decision = RoutingDecision(
            decision_id=f"decision_{int(time.time())}_{rule.rule_id}",
            timestamp=datetime.now(),
            decision_type=decision_type,
            routing_target=action["target"],
            confidence_score=final_confidence,
            reasoning_chain=reasoning_chain,
            alternative_options=[],
            execution_priority=RoutingPriority.NORMAL,
            expected_performance=rule.success_rate,
        )

        return decision

    def _generate_learned_options(
        self, context: RoutingContext, analysis: Dict[str, Any]
    ) -> List[RoutingDecision]:
        """학습 기반 옵션 생성"""
        options = []

        # 유사한 과거 컨텍스트 검색
        similar_contexts = self._find_similar_contexts(context)

        for similar_ctx, performance in similar_contexts:
            if performance > 0.7:  # 성공적이었던 경우만
                # 유사한 라우팅 결정 생성
                learned_decision = self._create_learned_decision(
                    context, similar_ctx, performance
                )
                options.append(learned_decision)

        return options[:2]  # 최대 2개의 학습 기반 옵션

    def _find_similar_contexts(
        self, context: RoutingContext
    ) -> List[Tuple[RoutingContext, float]]:
        """유사한 컨텍스트 검색"""
        similar_contexts = []

        for past_decision in self.routing_history:
            # 간단한 유사도 계산 (실제로는 더 정교한 벡터 유사도 필요)
            similarity = self._calculate_context_similarity(context, past_decision)

            if similarity > 0.6:  # 60% 이상 유사한 경우
                # 해당 결정의 성능 찾기
                performance = self._get_decision_performance(past_decision.decision_id)
                similar_contexts.append((context, performance))

        return sorted(similar_contexts, key=lambda x: x[1], reverse=True)[:5]

    def _calculate_context_similarity(
        self, ctx1: RoutingContext, decision: RoutingDecision
    ) -> float:
        """컨텍스트 유사도 계산"""
        # 간단한 유사도 계산
        similarity_factors = []

        # 의도 유사도
        # (실제 구현에서는 decision에서 원본 컨텍스트를 추출해야 함)
        # 여기서는 간단한 휴리스틱 사용
        similarity_factors.append(0.7)  # 기본 유사도

        return np.mean(similarity_factors)

    def _get_decision_performance(self, decision_id: str) -> float:
        """결정의 성능 가져오기"""
        for perf in self.performance_history:
            if perf.decision_id == decision_id:
                return perf.actual_performance

        return 0.5  # 기본값

    def _create_learned_decision(
        self,
        context: RoutingContext,
        similar_context: RoutingContext,
        performance: float,
    ) -> RoutingDecision:
        """학습 기반 결정 생성"""
        decision = RoutingDecision(
            decision_id=f"learned_{int(time.time())}",
            timestamp=datetime.now(),
            decision_type=RoutingDecisionType.SIGNATURE_SELECTION,
            routing_target="selene",  # 학습된 타겟 (실제로는 과거 데이터에서 추출)
            confidence_score=performance * 0.8,  # 학습 기반이므로 약간 할인
            reasoning_chain=[
                "Based on similar past context",
                f"Historical performance: {performance:.3f}",
                "Learned pattern applied",
            ],
            alternative_options=[],
            execution_priority=RoutingPriority.NORMAL,
            expected_performance=performance,
        )

        return decision

    def _create_fallback_option(self, context: RoutingContext) -> RoutingDecision:
        """비상 대체 옵션 생성"""
        # 안전한 기본 시그니처 선택 (Aurora - 가장 균형잡힌 시그니처)
        fallback_decision = RoutingDecision(
            decision_id=f"fallback_{int(time.time())}",
            timestamp=datetime.now(),
            decision_type=RoutingDecisionType.EMERGENCY_FALLBACK,
            routing_target="aurora",
            confidence_score=0.6,  # 중간 정도의 신뢰도
            reasoning_chain=[
                "Fallback option activated",
                "No specific rule matched",
                "Using balanced Aurora signature",
            ],
            alternative_options=[],
            execution_priority=RoutingPriority.LOW,
            expected_performance=0.7,
        )

        return fallback_decision

    def _select_best_routing(
        self, options: List[RoutingDecision], context: RoutingContext
    ) -> RoutingDecision:
        """최적 라우팅 선택"""
        if not options:
            return self._create_fallback_option(context)

        # 다중 기준 평가
        for option in options:
            score = (
                option.confidence_score * 0.4
                + option.expected_performance * 0.3
                + (1.0 / option.execution_priority.value)
                * 0.2  # 높은 우선순위일수록 높은 점수
                + self._calculate_contextual_fitness(option, context) * 0.1
            )
            option.overall_score = score

        # 최고 점수 옵션 선택
        best_option = max(options, key=lambda x: getattr(x, "overall_score", 0))

        # 대안 옵션들 설정
        alternatives = sorted(
            [opt for opt in options if opt != best_option],
            key=lambda x: getattr(x, "overall_score", 0),
            reverse=True,
        )[:3]

        best_option.alternative_options = [
            {
                "target": alt.routing_target,
                "confidence": alt.confidence_score,
                "type": alt.decision_type.value,
            }
            for alt in alternatives
        ]

        return best_option

    def _calculate_contextual_fitness(
        self, decision: RoutingDecision, context: RoutingContext
    ) -> float:
        """컨텍스트 적합성 계산"""
        # 시그니처별 컨텍스트 적합성
        fitness_map = {
            "selene": {
                "emotional": 0.9,
                "supportive": 0.8,
                "creative": 0.6,
                "analytical": 0.3,
            },
            "factbomb": {
                "analytical": 0.9,
                "problem_solving": 0.8,
                "emotional": 0.2,
                "creative": 0.3,
            },
            "lune": {
                "creative": 0.9,
                "emotional": 0.7,
                "supportive": 0.6,
                "analytical": 0.4,
            },
            "aurora": {
                "supportive": 0.9,
                "emotional": 0.8,
                "conversational": 0.8,
                "analytical": 0.6,
            },
        }

        target = decision.routing_target
        if target in fitness_map:
            return fitness_map[target].get(context.user_intent, 0.5)

        return 0.5  # 기본 적합성

    def _collect_learning_data(
        self, context: RoutingContext, decision: RoutingDecision
    ):
        """학습 데이터 수집"""
        learning_data = {
            "context_intent": context.user_intent,
            "complexity": context.complexity_level,
            "emotion_intensity": context.emotion_state["intensity"],
            "decision_target": decision.routing_target,
            "confidence": decision.confidence_score,
            "timestamp": datetime.now(),
        }

        # 패턴별 데이터 저장
        pattern_key = f"{context.user_intent}_{decision.routing_target}"
        self.decision_patterns[pattern_key].append(learning_data)

        # 최근 20개 데이터만 유지
        if len(self.decision_patterns[pattern_key]) > 20:
            self.decision_patterns[pattern_key] = self.decision_patterns[pattern_key][
                -20:
            ]

    def record_routing_performance(
        self,
        decision_id: str,
        actual_performance: float,
        user_satisfaction: float = 0.8,
        execution_time_ms: float = 0.0,
    ):
        """라우팅 성능 기록"""
        performance = RoutingPerformance(
            timestamp=datetime.now(),
            decision_id=decision_id,
            actual_performance=actual_performance,
            user_satisfaction=user_satisfaction,
            execution_time_ms=execution_time_ms,
            accuracy_score=actual_performance,  # 간단화
            efficiency_score=max(0.0, 1.0 - execution_time_ms / 5000.0),  # 5초 기준
            adaptability_score=user_satisfaction,
        )

        self.performance_history.append(performance)

        # 성공률 업데이트
        if actual_performance > 0.7:
            self.routing_statistics["successful_routes"] += 1

        # 규칙 성능 업데이트
        self._update_rule_performance(decision_id, actual_performance)

    def _update_rule_performance(self, decision_id: str, performance: float):
        """규칙 성능 업데이트"""
        # 결정 ID에서 규칙 ID 추출
        for rule_id, rule in self.routing_rules.items():
            if rule_id in decision_id:
                # 성공률 업데이트 (지수 평활법 사용)
                alpha = self.learning_rate
                rule.success_rate = (
                    1 - alpha
                ) * rule.success_rate + alpha * performance
                rule.usage_count += 1
                rule.last_updated = datetime.now()
                break

    def _update_performance_metrics(self):
        """성능 메트릭 업데이트"""
        if not self.performance_history:
            return

        recent_performances = list(self.performance_history)[-10:]

        self.routing_statistics["average_performance"] = np.mean(
            [p.actual_performance for p in recent_performances]
        )

        # 신뢰도 업데이트
        recent_decisions = list(self.routing_history)[-10:]
        if recent_decisions:
            self.routing_statistics["average_confidence"] = np.mean(
                [d.confidence_score for d in recent_decisions]
            )

    def _adapt_routing_rules(self):
        """적응적 라우팅 규칙 조정"""
        # 성능이 낮은 규칙들 조정
        for rule_id, rule in self.routing_rules.items():
            if rule.usage_count >= 5 and rule.success_rate < 0.6:
                # 가중치 조정
                for weight_key in rule.adaptive_weights:
                    rule.adaptive_weights[weight_key] *= 0.95  # 5% 감소

                # 우선순위 낮춤
                rule.priority = min(5, rule.priority + 1)

    def get_routing_status(self) -> Dict[str, Any]:
        """라우팅 상태 반환"""
        status = {
            "active_context": {
                "id": (
                    self.active_routing_context.context_id
                    if self.active_routing_context
                    else None
                ),
                "intent": (
                    self.active_routing_context.user_intent
                    if self.active_routing_context
                    else None
                ),
                "complexity": (
                    self.active_routing_context.complexity_level
                    if self.active_routing_context
                    else 0.0
                ),
            },
            "statistics": self.routing_statistics.copy(),
            "recent_decisions": [
                {
                    "id": d.decision_id,
                    "target": d.routing_target,
                    "confidence": d.confidence_score,
                    "type": d.decision_type.value,
                }
                for d in list(self.routing_history)[-5:]
            ],
            "rule_performance": {
                rule_id: {
                    "success_rate": rule.success_rate,
                    "usage_count": rule.usage_count,
                    "priority": rule.priority,
                }
                for rule_id, rule in self.routing_rules.items()
            },
        }

        return status

    def visualize_routing_flow(self, hours: int = 1) -> str:
        """라우팅 흐름 시각화 (텍스트 기반)"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_decisions = [
            d for d in self.routing_history if d.timestamp >= cutoff_time
        ]

        if not recent_decisions:
            return f"❌ 최근 {hours}시간간 라우팅 데이터가 없습니다."

        viz = f"🧭 Meta Routing Flow (Last {hours} hour{'s' if hours > 1 else ''})\n"
        viz += "=" * 70 + "\n\n"

        # 라우팅 결정 타임라인
        viz += "📋 Routing Decisions Timeline:\n"
        for decision in recent_decisions[-8:]:  # 최근 8개만
            time_str = decision.timestamp.strftime("%H:%M:%S")
            confidence_bar = "█" * int(decision.confidence_score * 10)

            viz += f"{time_str} | {decision.routing_target:12} | "
            viz += f"{confidence_bar:10} | {decision.confidence_score:.3f} | "
            viz += f"{decision.decision_type.value}\n"

        # 라우팅 대상 분포
        target_counts = defaultdict(int)
        for decision in recent_decisions:
            target_counts[decision.routing_target] += 1

        viz += "\n🎯 Routing Target Distribution:\n"
        total_decisions = len(recent_decisions)
        for target, count in sorted(
            target_counts.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / total_decisions) * 100
            bar = "▓" * int(percentage / 5)
            viz += f"   {target:15} | {bar:20} | {count:2d} ({percentage:5.1f}%)\n"

        # 평균 성능 지표
        avg_confidence = np.mean([d.confidence_score for d in recent_decisions])
        viz += f"\n📊 Performance Metrics:\n"
        viz += f"   Average Confidence: {avg_confidence:.3f}\n"
        viz += f"   Total Decisions: {len(recent_decisions)}\n"
        viz += f"   Success Rate: {self.routing_statistics['successful_routes'] / max(1, self.routing_statistics['total_decisions']) * 100:.1f}%\n"

        return viz

    def save_routing_data(self, filename: str = None) -> str:
        """라우팅 데이터 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meta_routing_data_{timestamp}.json"

        # 저장할 데이터 준비
        save_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_decisions": len(self.routing_history),
                "total_performance_records": len(self.performance_history),
            },
            "routing_rules": {},
            "routing_history": [],
            "performance_history": [],
            "decision_patterns": {},
            "routing_statistics": self.routing_statistics,
            "success_patterns": dict(self.success_patterns),
        }

        # RoutingRule 객체들을 직렬화
        for rule_id, rule in self.routing_rules.items():
            rule_dict = asdict(rule)
            rule_dict["last_updated"] = rule.last_updated.isoformat()
            save_data["routing_rules"][rule_id] = rule_dict

        # RoutingDecision 객체들을 직렬화
        for decision in self.routing_history:
            decision_dict = asdict(decision)
            decision_dict["timestamp"] = decision.timestamp.isoformat()
            decision_dict["decision_type"] = decision.decision_type.value
            decision_dict["execution_priority"] = decision.execution_priority.value
            save_data["routing_history"].append(decision_dict)

        # RoutingPerformance 객체들을 직렬화
        for performance in self.performance_history:
            perf_dict = asdict(performance)
            perf_dict["timestamp"] = performance.timestamp.isoformat()
            save_data["performance_history"].append(perf_dict)

        # 결정 패턴 직렬화
        for pattern_key, pattern_data in self.decision_patterns.items():
            save_data["decision_patterns"][pattern_key] = []
            for data_point in pattern_data:
                data_copy = data_point.copy()
                data_copy["timestamp"] = data_point["timestamp"].isoformat()
                save_data["decision_patterns"][pattern_key].append(data_copy)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return f"✅ 메타 라우팅 데이터 저장 완료: {filename}"
        except Exception as e:
            return f"❌ 저장 실패: {e}"


# 편의 함수들
def create_meta_routing_controller(**kwargs) -> MetaRoutingController:
    """Meta Routing Controller 생성"""
    return MetaRoutingController(**kwargs)


def quick_route_request(input_text: str, intent: str = None) -> Dict[str, Any]:
    """빠른 라우팅 요청"""
    controller = MetaRoutingController()

    # 사용자 컨텍스트 구성
    user_context = {"intent_hint": intent} if intent else {}

    decision = controller.route_request(input_text, "text", user_context)

    return {
        "routing_target": decision.routing_target,
        "confidence": decision.confidence_score,
        "decision_type": decision.decision_type.value,
        "reasoning": decision.reasoning_chain,
    }


if __name__ == "__main__":
    # 테스트 실행
    print("🧭 Meta Routing Controller 테스트...")

    controller = MetaRoutingController()
    controller.initialize_components()

    # 다양한 입력에 대한 라우팅 테스트
    test_inputs = [
        ("I'm feeling really sad and need someone to talk to", "emotional"),
        ("Can you analyze this data and find patterns?", "analytical"),
        ("Help me write a creative story about the moon", "creative"),
        ("I need support with my personal growth", "supportive"),
        ("Let's have a casual conversation", "conversational"),
    ]

    print("\n🔄 다양한 입력에 대한 라우팅 테스트...")
    for input_text, expected_intent in test_inputs:
        decision = controller.route_request(input_text, "text")

        print(f"\n📋 Input: {input_text[:50]}...")
        print(f"   Detected Intent: {expected_intent}")
        print(f"   Routing Target: {decision.routing_target}")
        print(f"   Decision Type: {decision.decision_type.value}")
        print(f"   Confidence: {decision.confidence_score:.3f}")
        print(f"   Reasoning: {' → '.join(decision.reasoning_chain)}")

        # 성능 기록 (시뮬레이션)
        simulated_performance = np.random.uniform(0.6, 0.9)
        controller.record_routing_performance(
            decision.decision_id,
            simulated_performance,
            user_satisfaction=np.random.uniform(0.7, 0.95),
        )

    # 라우팅 상태 확인
    status = controller.get_routing_status()
    print(f"\n📊 Routing Status:")
    print(f"   Total Decisions: {status['statistics']['total_decisions']}")
    print(f"   Successful Routes: {status['statistics']['successful_routes']}")
    print(f"   Average Confidence: {status['statistics']['average_confidence']:.3f}")
    print(f"   Average Performance: {status['statistics']['average_performance']:.3f}")

    # 규칙 성능 표시
    print(f"\n📏 Rule Performance:")
    for rule_id, rule_perf in status["rule_performance"].items():
        print(
            f"   {rule_id:20}: Success {rule_perf['success_rate']:.3f}, "
            f"Usage {rule_perf['usage_count']}, Priority {rule_perf['priority']}"
        )

    # 라우팅 흐름 시각화
    print("\n🧭 Routing Flow Visualization:")
    flow_viz = controller.visualize_routing_flow(hours=1)
    print(flow_viz)

    # 저장 테스트
    save_result = controller.save_routing_data()
    print(f"\n{save_result}")

    print("\n✅ Meta Routing Controller 테스트 완료!")
