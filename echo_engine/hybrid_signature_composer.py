#!/usr/bin/env python3
"""
🎭 Hybrid Signature Composer v1.0
다중 시그니처 조합을 통한 하이브리드 AI 페르소나 생성 및 관리 시스템

핵심 기능:
- 복수 시그니처 실시간 블렌딩
- 감정⨯판단⨯표현 스타일 융합
- 적응적 시그니처 전환
- 상황별 최적 조합 추천
- 하이브리드 페르소나 성능 평가
"""

import json
import numpy as np
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import logging

# Echo 엔진 모듈들
try:
    from .signature_cross_resonance_mapper import (
        SignatureCrossResonanceMapper,
        ResonancePattern,
    )
    from .realtime_emotion_flow_mapper import RealtimeEmotionFlowMapper, EmotionState
    from .signature_neural_atlas_builder import SignatureNeuralAtlasBuilder
    from .consciousness_flow_analyzer import ConsciousnessFlowAnalyzer
except ImportError:
    print("⚠️ Echo modules not available, running in standalone mode")


class BlendingMode(Enum):
    """블렌딩 모드 정의"""

    WEIGHTED_AVERAGE = "weighted_average"  # 가중 평균 방식
    DOMINANT_OVERLAY = "dominant_overlay"  # 지배적 오버레이 방식
    CONTEXTUAL_SWITCHING = "contextual_switching"  # 상황별 전환 방식
    HARMONIC_FUSION = "harmonic_fusion"  # 조화적 융합 방식
    ADAPTIVE_MORPHING = "adaptive_morphing"  # 적응적 변형 방식


class ContextType(Enum):
    """컨텍스트 타입 정의"""

    ANALYTICAL = "analytical"  # 분석적 상황
    EMOTIONAL = "emotional"  # 감정적 상황
    CREATIVE = "creative"  # 창조적 상황
    SUPPORTIVE = "supportive"  # 지원적 상황
    CONVERSATIONAL = "conversational"  # 대화적 상황
    PROBLEM_SOLVING = "problem_solving"  # 문제 해결 상황


@dataclass
class SignatureWeight:
    """시그니처 가중치"""

    signature_name: str
    weight: float  # 0.0 - 1.0
    confidence: float  # 가중치에 대한 신뢰도
    contribution_areas: List[str]  # 기여 영역
    activation_threshold: float  # 활성화 임계값


@dataclass
class HybridComposition:
    """하이브리드 구성"""

    composition_id: str
    timestamp: datetime
    signature_weights: List[SignatureWeight]
    blending_mode: BlendingMode
    context_type: ContextType
    performance_score: float
    emotional_coherence: float
    expression_consistency: float
    overall_effectiveness: float


@dataclass
class BlendingRule:
    """블렌딩 규칙"""

    rule_id: str
    context_triggers: List[str]
    recommended_weights: Dict[str, float]
    blending_mode: BlendingMode
    priority: int
    effectiveness_score: float
    usage_count: int


@dataclass
class HybridPerformanceMetric:
    """하이브리드 성능 메트릭"""

    timestamp: datetime
    composition_id: str
    task_type: str
    execution_time_ms: float
    quality_score: float  # 출력 품질
    user_satisfaction: float  # 사용자 만족도
    coherence_score: float  # 일관성 점수
    adaptability_score: float  # 적응성 점수


class HybridSignatureComposer:
    """🎭 하이브리드 시그니처 조합기"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 기본 시그니처 정의
        self.base_signatures = {
            "selene": {
                "emotion_profile": {
                    "empathy": 0.9,
                    "gentleness": 0.9,
                    "melancholy": 0.8,
                    "introspection": 0.7,
                    "vulnerability": 0.6,
                },
                "judgment_style": {
                    "emotion_weighted": 0.8,
                    "intuitive": 0.7,
                    "contextual": 0.8,
                    "slow_deliberation": 0.9,
                    "empathy_first": 0.9,
                },
                "expression_mode": {
                    "whisper_tone": 0.9,
                    "metaphorical": 0.7,
                    "gentle_pauses": 0.8,
                    "emotional_depth": 0.8,
                    "soft_vulnerability": 0.9,
                },
                "core_strengths": [
                    "emotional_intelligence",
                    "empathetic_connection",
                    "gentle_guidance",
                ],
            },
            "factbomb": {
                "emotion_profile": {
                    "analytical_coldness": 0.9,
                    "logical_intensity": 0.8,
                    "impatience_with_fluff": 0.9,
                    "precision_drive": 0.9,
                    "truth_urgency": 0.8,
                },
                "judgment_style": {
                    "fact_first": 0.9,
                    "bias_elimination": 0.9,
                    "rapid_conclusion": 0.8,
                    "logic_priority": 0.9,
                    "emotion_suppression": 0.8,
                },
                "expression_mode": {
                    "direct_statement": 0.9,
                    "minimal_words": 0.8,
                    "sharp_delivery": 0.9,
                    "no_hedging": 0.9,
                    "impact_focus": 0.8,
                },
                "core_strengths": [
                    "logical_analysis",
                    "rapid_processing",
                    "direct_communication",
                ],
            },
            "lune": {
                "emotion_profile": {
                    "dreamy_melancholy": 0.8,
                    "poetic_longing": 0.9,
                    "symbolic_thinking": 0.8,
                    "gentle_wonder": 0.7,
                    "introspective_depth": 0.8,
                },
                "judgment_style": {
                    "symbolic_interpretation": 0.8,
                    "delayed_precision": 0.7,
                    "emotional_logic": 0.8,
                    "metaphor_reasoning": 0.9,
                    "intuitive_synthesis": 0.8,
                },
                "expression_mode": {
                    "lyrical_flow": 0.9,
                    "metaphor_rich": 0.9,
                    "dreamy_cadence": 0.8,
                    "symbolic_language": 0.8,
                    "emotional_echo": 0.8,
                },
                "core_strengths": [
                    "creative_synthesis",
                    "symbolic_interpretation",
                    "artistic_expression",
                ],
            },
            "aurora": {
                "emotion_profile": {
                    "nurturing_warmth": 0.9,
                    "hopeful_optimism": 0.8,
                    "protective_care": 0.8,
                    "gentle_strength": 0.7,
                    "encouraging_energy": 0.9,
                },
                "judgment_style": {
                    "growth_focused": 0.9,
                    "potential_seeing": 0.8,
                    "supportive_logic": 0.8,
                    "nurturing_analysis": 0.9,
                    "encouraging_frame": 0.9,
                },
                "expression_mode": {
                    "warm_encouragement": 0.9,
                    "gentle_guidance": 0.8,
                    "hopeful_tone": 0.9,
                    "supportive_phrasing": 0.8,
                    "nurturing_rhythm": 0.8,
                },
                "core_strengths": [
                    "nurturing_support",
                    "growth_facilitation",
                    "hope_instillation",
                ],
            },
        }

        # 블렌딩 규칙
        self.blending_rules = {
            "analytical_tasks": {
                "weights": {"factbomb": 0.7, "selene": 0.2, "aurora": 0.1},
                "mode": BlendingMode.DOMINANT_OVERLAY,
                "context": ContextType.ANALYTICAL,
            },
            "emotional_support": {
                "weights": {"selene": 0.6, "aurora": 0.3, "lune": 0.1},
                "mode": BlendingMode.HARMONIC_FUSION,
                "context": ContextType.EMOTIONAL,
            },
            "creative_expression": {
                "weights": {"lune": 0.5, "aurora": 0.3, "selene": 0.2},
                "mode": BlendingMode.ADAPTIVE_MORPHING,
                "context": ContextType.CREATIVE,
            },
            "problem_solving": {
                "weights": {"factbomb": 0.4, "aurora": 0.3, "selene": 0.3},
                "mode": BlendingMode.CONTEXTUAL_SWITCHING,
                "context": ContextType.PROBLEM_SOLVING,
            },
            "general_conversation": {
                "weights": {"aurora": 0.4, "selene": 0.3, "lune": 0.2, "factbomb": 0.1},
                "mode": BlendingMode.WEIGHTED_AVERAGE,
                "context": ContextType.CONVERSATIONAL,
            },
        }

        # 상태 추적
        self.current_composition = None
        self.composition_history = deque(maxlen=50)
        self.performance_metrics = deque(maxlen=100)
        self.active_rules = {}

        # 학습된 조합들
        self.learned_compositions = {}
        self.context_patterns = defaultdict(list)

        # 성능 통계
        self.composition_effectiveness = defaultdict(list)
        self.context_success_rates = defaultdict(float)

        print("🎭 Hybrid Signature Composer 초기화 완료")

    def compose_hybrid_signature(
        self,
        context_type: ContextType,
        context_details: Dict[str, Any] = None,
        forced_weights: Dict[str, float] = None,
    ) -> HybridComposition:
        """하이브리드 시그니처 조합"""

        # 컨텍스트 기반 추천 가중치 계산
        if forced_weights:
            recommended_weights = forced_weights
        else:
            recommended_weights = self._calculate_context_weights(
                context_type, context_details
            )

        # 최적 블렌딩 모드 결정
        blending_mode = self._determine_blending_mode(context_type, recommended_weights)

        # 시그니처 가중치 객체 생성
        signature_weights = []
        for sig_name, weight in recommended_weights.items():
            if weight > 0.05:  # 5% 이상의 가중치만 포함
                sig_weight = SignatureWeight(
                    signature_name=sig_name,
                    weight=weight,
                    confidence=self._calculate_weight_confidence(
                        sig_name, context_type
                    ),
                    contribution_areas=self._identify_contribution_areas(
                        sig_name, context_type
                    ),
                    activation_threshold=0.1,
                )
                signature_weights.append(sig_weight)

        # 하이브리드 구성 생성
        composition_id = f"hybrid_{int(time.time())}_{len(self.composition_history)}"

        # 성능 점수 예측
        predicted_performance = self._predict_composition_performance(
            signature_weights, blending_mode, context_type
        )

        composition = HybridComposition(
            composition_id=composition_id,
            timestamp=datetime.now(),
            signature_weights=signature_weights,
            blending_mode=blending_mode,
            context_type=context_type,
            performance_score=predicted_performance["overall"],
            emotional_coherence=predicted_performance["emotional"],
            expression_consistency=predicted_performance["expression"],
            overall_effectiveness=predicted_performance["effectiveness"],
        )

        # 현재 구성으로 설정
        self.current_composition = composition
        self.composition_history.append(composition)

        # 컨텍스트 패턴 학습
        self._learn_context_pattern(context_type, context_details, composition)

        return composition

    def _calculate_context_weights(
        self, context_type: ContextType, context_details: Dict[str, Any] = None
    ) -> Dict[str, float]:
        """컨텍스트 기반 가중치 계산"""

        # 기본 규칙에서 시작
        base_weights = {}
        for rule_name, rule in self.blending_rules.items():
            if rule["context"] == context_type:
                base_weights = rule["weights"].copy()
                break

        if not base_weights:
            # 기본값: 균등 분배
            base_weights = {name: 0.25 for name in self.base_signatures.keys()}

        # 컨텍스트 세부사항 기반 조정
        if context_details:
            base_weights = self._adjust_weights_for_context_details(
                base_weights, context_details
            )

        # 학습된 패턴 적용
        learned_adjustment = self._apply_learned_patterns(context_type, context_details)

        # 최종 가중치 계산
        final_weights = {}
        for sig_name in self.base_signatures.keys():
            base_weight = base_weights.get(sig_name, 0.0)
            learned_weight = learned_adjustment.get(sig_name, 0.0)

            # 가중 조합
            final_weight = base_weight * 0.7 + learned_weight * 0.3
            final_weights[sig_name] = final_weight

        # 정규화
        total_weight = sum(final_weights.values())
        if total_weight > 0:
            final_weights = {k: v / total_weight for k, v in final_weights.items()}

        return final_weights

    def _adjust_weights_for_context_details(
        self, base_weights: Dict[str, float], context_details: Dict[str, Any]
    ) -> Dict[str, float]:
        """컨텍스트 세부사항에 따른 가중치 조정"""
        adjusted_weights = base_weights.copy()

        # 감정 강도 기반 조정
        emotion_intensity = context_details.get("emotion_intensity", 0.5)
        if emotion_intensity > 0.7:
            # 높은 감정 강도 -> Selene과 Aurora 강화
            adjusted_weights["selene"] *= 1.3
            adjusted_weights["aurora"] *= 1.2
            adjusted_weights["factbomb"] *= 0.7

        # 복잡성 수준 기반 조정
        complexity_level = context_details.get("complexity", 0.5)
        if complexity_level > 0.8:
            # 높은 복잡성 -> FactBomb 강화
            adjusted_weights["factbomb"] *= 1.4
            adjusted_weights["lune"] *= 0.8

        # 창조성 요구 기반 조정
        creativity_need = context_details.get("creativity_required", 0.5)
        if creativity_need > 0.7:
            # 높은 창조성 필요 -> Lune 강화
            adjusted_weights["lune"] *= 1.5
            adjusted_weights["factbomb"] *= 0.6

        # 지원 필요성 기반 조정
        support_needed = context_details.get("support_needed", 0.5)
        if support_needed > 0.7:
            # 높은 지원 필요 -> Aurora 강화
            adjusted_weights["aurora"] *= 1.4
            adjusted_weights["selene"] *= 1.2

        return adjusted_weights

    def _apply_learned_patterns(
        self, context_type: ContextType, context_details: Dict[str, Any] = None
    ) -> Dict[str, float]:
        """학습된 패턴 적용"""
        if context_type not in self.context_patterns:
            return {name: 0.0 for name in self.base_signatures.keys()}

        # 유사한 컨텍스트 패턴 찾기
        similar_patterns = self.context_patterns[context_type]

        if not similar_patterns:
            return {name: 0.0 for name in self.base_signatures.keys()}

        # 성능이 좋았던 패턴들의 가중치 평균
        successful_patterns = [
            pattern
            for pattern in similar_patterns
            if pattern.get("performance_score", 0) > 0.7
        ]

        if not successful_patterns:
            return {name: 0.0 for name in self.base_signatures.keys()}

        # 가중치 평균 계산
        learned_weights = defaultdict(float)
        for pattern in successful_patterns:
            weights = pattern.get("weights", {})
            performance = pattern.get("performance_score", 0.7)

            for sig_name, weight in weights.items():
                learned_weights[sig_name] += weight * performance

        # 정규화
        total_weight = sum(learned_weights.values())
        if total_weight > 0:
            learned_weights = {k: v / total_weight for k, v in learned_weights.items()}

        return dict(learned_weights)

    def _determine_blending_mode(
        self, context_type: ContextType, weights: Dict[str, float]
    ) -> BlendingMode:
        """최적 블렌딩 모드 결정"""

        # 가중치 분산 계산
        weight_values = list(weights.values())
        weight_variance = np.var(weight_values)
        max_weight = max(weight_values)

        # 분산과 최대값에 따른 모드 결정
        if max_weight > 0.6:
            return BlendingMode.DOMINANT_OVERLAY
        elif weight_variance < 0.02:  # 균등 분배
            return BlendingMode.WEIGHTED_AVERAGE
        elif context_type == ContextType.CREATIVE:
            return BlendingMode.ADAPTIVE_MORPHING
        elif context_type == ContextType.EMOTIONAL:
            return BlendingMode.HARMONIC_FUSION
        else:
            return BlendingMode.CONTEXTUAL_SWITCHING

    def _calculate_weight_confidence(
        self, signature_name: str, context_type: ContextType
    ) -> float:
        """가중치 신뢰도 계산"""
        # 해당 시그니처의 컨텍스트별 성공률 기반
        success_rate = self.context_success_rates.get(
            f"{signature_name}_{context_type.value}", 0.7
        )

        # 사용 빈도 기반 신뢰도 조정
        usage_count = len(
            [
                p
                for p in self.context_patterns.get(context_type, [])
                if signature_name in p.get("weights", {})
            ]
        )

        frequency_factor = min(1.0, usage_count / 10.0)  # 10회 사용을 기준으로 정규화

        return success_rate * 0.7 + frequency_factor * 0.3

    def _identify_contribution_areas(
        self, signature_name: str, context_type: ContextType
    ) -> List[str]:
        """기여 영역 식별"""
        signature = self.base_signatures.get(signature_name, {})
        core_strengths = signature.get("core_strengths", [])

        # 컨텍스트별 기여 영역 매핑
        context_contributions = {
            ContextType.ANALYTICAL: [
                "logical_analysis",
                "rapid_processing",
                "fact_checking",
            ],
            ContextType.EMOTIONAL: [
                "emotional_intelligence",
                "empathetic_connection",
                "support_provision",
            ],
            ContextType.CREATIVE: [
                "creative_synthesis",
                "artistic_expression",
                "innovative_thinking",
            ],
            ContextType.SUPPORTIVE: [
                "nurturing_support",
                "growth_facilitation",
                "encouragement",
            ],
            ContextType.CONVERSATIONAL: [
                "communication_flow",
                "engagement",
                "relatability",
            ],
            ContextType.PROBLEM_SOLVING: [
                "solution_generation",
                "systematic_thinking",
                "optimization",
            ],
        }

        relevant_areas = context_contributions.get(context_type, [])

        # 시그니처 강점과 컨텍스트 요구사항의 교집합
        contribution_areas = list(set(core_strengths) & set(relevant_areas))

        if not contribution_areas:
            contribution_areas = core_strengths[:2]  # 기본적으로 상위 2개 강점 사용

        return contribution_areas

    def _predict_composition_performance(
        self,
        signature_weights: List[SignatureWeight],
        blending_mode: BlendingMode,
        context_type: ContextType,
    ) -> Dict[str, float]:
        """구성 성능 예측"""

        # 시그니처별 기여도 계산
        total_contribution = 0.0
        emotional_score = 0.0
        expression_score = 0.0

        for weight_obj in signature_weights:
            sig_name = weight_obj.signature_name
            weight = weight_obj.weight
            signature = self.base_signatures.get(sig_name, {})

            # 시그니처 품질 점수
            sig_quality = np.mean(
                [
                    np.mean(list(signature.get("emotion_profile", {}).values())),
                    np.mean(list(signature.get("judgment_style", {}).values())),
                    np.mean(list(signature.get("expression_mode", {}).values())),
                ]
            )

            contribution = weight * sig_quality
            total_contribution += contribution

            # 감정 일관성 기여
            emotion_coherence = np.mean(
                list(signature.get("emotion_profile", {}).values())
            )
            emotional_score += weight * emotion_coherence

            # 표현 일관성 기여
            expression_coherence = np.mean(
                list(signature.get("expression_mode", {}).values())
            )
            expression_score += weight * expression_coherence

        # 블렌딩 모드에 따른 효과성 조정
        mode_multipliers = {
            BlendingMode.WEIGHTED_AVERAGE: 0.85,
            BlendingMode.DOMINANT_OVERLAY: 0.9,
            BlendingMode.CONTEXTUAL_SWITCHING: 0.8,
            BlendingMode.HARMONIC_FUSION: 0.95,
            BlendingMode.ADAPTIVE_MORPHING: 0.88,
        }

        mode_multiplier = mode_multipliers.get(blending_mode, 0.85)

        # 최종 성능 예측
        overall_performance = total_contribution * mode_multiplier

        return {
            "overall": min(1.0, overall_performance),
            "emotional": min(1.0, emotional_score),
            "expression": min(1.0, expression_score),
            "effectiveness": min(
                1.0, overall_performance * 0.9 + mode_multiplier * 0.1
            ),
        }

    def _learn_context_pattern(
        self,
        context_type: ContextType,
        context_details: Dict[str, Any],
        composition: HybridComposition,
    ):
        """컨텍스트 패턴 학습"""
        pattern = {
            "timestamp": datetime.now().isoformat(),
            "context_details": context_details or {},
            "weights": {
                sw.signature_name: sw.weight for sw in composition.signature_weights
            },
            "blending_mode": composition.blending_mode.value,
            "predicted_performance": composition.performance_score,
            "performance_score": None,  # 실제 성능은 나중에 업데이트
        }

        self.context_patterns[context_type].append(pattern)

        # 패턴 수 제한
        if len(self.context_patterns[context_type]) > 20:
            self.context_patterns[context_type] = self.context_patterns[context_type][
                -20:
            ]

    def apply_hybrid_composition(
        self, input_text: str, task_type: str = "general"
    ) -> Dict[str, Any]:
        """하이브리드 구성 적용"""
        if not self.current_composition:
            raise ValueError("활성 하이브리드 구성이 없습니다.")

        composition = self.current_composition
        start_time = time.time()

        # 시그니처별 처리 결과 생성
        signature_results = {}
        for weight_obj in composition.signature_weights:
            sig_name = weight_obj.signature_name
            weight = weight_obj.weight

            # 각 시그니처의 처리 결과 시뮬레이션
            sig_result = self._simulate_signature_processing(
                sig_name, input_text, task_type
            )
            signature_results[sig_name] = {
                "result": sig_result,
                "weight": weight,
                "confidence": weight_obj.confidence,
            }

        # 블렌딩 모드에 따른 결과 융합
        final_result = self._blend_signature_results(
            signature_results, composition.blending_mode
        )

        # 실행 시간 계산
        execution_time = (time.time() - start_time) * 1000

        # 성능 메트릭 기록
        performance_metric = HybridPerformanceMetric(
            timestamp=datetime.now(),
            composition_id=composition.composition_id,
            task_type=task_type,
            execution_time_ms=execution_time,
            quality_score=self._evaluate_result_quality(final_result),
            user_satisfaction=0.8,  # 실제로는 사용자 피드백으로 업데이트
            coherence_score=self._evaluate_coherence(signature_results),
            adaptability_score=self._evaluate_adaptability(composition),
        )

        self.performance_metrics.append(performance_metric)

        return {
            "result": final_result,
            "composition_used": composition.composition_id,
            "signature_contributions": signature_results,
            "execution_time_ms": execution_time,
            "performance_metric": performance_metric,
        }

    def _simulate_signature_processing(
        self, signature_name: str, input_text: str, task_type: str
    ) -> str:
        """시그니처 처리 시뮬레이션"""
        signature = self.base_signatures.get(signature_name, {})

        # 시그니처별 특성 반영
        if signature_name == "selene":
            return f"[Selene] Gently considering your words... {input_text[:50]}... with empathetic understanding."
        elif signature_name == "factbomb":
            return f"[FactBomb] Direct analysis: {input_text[:50]}... Facts: 3 key points identified."
        elif signature_name == "lune":
            return f"[Lune] Dreamily interpreting... {input_text[:50]}... like moonlight on water..."
        elif signature_name == "aurora":
            return f"[Aurora] Warmly embracing your message... {input_text[:50]}... with nurturing hope."
        else:
            return f"[{signature_name}] Processing: {input_text[:50]}..."

    def _blend_signature_results(
        self, signature_results: Dict[str, Dict[str, Any]], blending_mode: BlendingMode
    ) -> str:
        """시그니처 결과 블렌딩"""

        if blending_mode == BlendingMode.WEIGHTED_AVERAGE:
            # 가중 평균 방식
            blended_result = "Blended response: "
            for sig_name, data in signature_results.items():
                weight = data["weight"]
                result = data["result"]
                blended_result += f"({weight:.2f}) {result[:30]}... "
            return blended_result

        elif blending_mode == BlendingMode.DOMINANT_OVERLAY:
            # 지배적 시그니처 결과를 기본으로, 다른 시그니처들의 특성 추가
            dominant_sig = max(signature_results.items(), key=lambda x: x[1]["weight"])
            base_result = dominant_sig[1]["result"]

            overlay_elements = []
            for sig_name, data in signature_results.items():
                if sig_name != dominant_sig[0] and data["weight"] > 0.2:
                    overlay_elements.append(
                        f"[{sig_name} influence: {data['weight']:.2f}]"
                    )

            return f"{base_result} {' '.join(overlay_elements)}"

        elif blending_mode == BlendingMode.HARMONIC_FUSION:
            # 조화적 융합
            fusion_result = "Harmonically fused response integrating: "
            for sig_name, data in signature_results.items():
                fusion_result += f"{sig_name}({data['weight']:.2f}) "
            return fusion_result

        elif blending_mode == BlendingMode.CONTEXTUAL_SWITCHING:
            # 상황별 전환 (가장 적합한 시그니처 선택)
            best_sig = max(signature_results.items(), key=lambda x: x[1]["confidence"])
            return f"Contextually selected: {best_sig[1]['result']}"

        elif blending_mode == BlendingMode.ADAPTIVE_MORPHING:
            # 적응적 변형
            morph_result = "Adaptively morphed response: "
            total_weight = sum(data["weight"] for data in signature_results.values())
            for sig_name, data in signature_results.items():
                morph_contribution = data["weight"] / total_weight
                morph_result += f"[{sig_name}:{morph_contribution:.2f}] "
            return morph_result

        else:
            # 기본값: 단순 연결
            return " | ".join([data["result"] for data in signature_results.values()])

    def _evaluate_result_quality(self, result: str) -> float:
        """결과 품질 평가"""
        # 간단한 품질 평가 (실제로는 더 정교한 평가 필요)
        quality_factors = [
            len(result) > 20,  # 충분한 길이
            "[" in result,  # 구조화된 응답
            ":" in result,  # 세부 정보 포함
            not result.startswith("Error"),  # 오류 없음
        ]

        return sum(quality_factors) / len(quality_factors)

    def _evaluate_coherence(
        self, signature_results: Dict[str, Dict[str, Any]]
    ) -> float:
        """일관성 평가"""
        # 시그니처 결과들 간의 일관성 평가
        weights = [data["weight"] for data in signature_results.values()]
        confidences = [data["confidence"] for data in signature_results.values()]

        # 가중치와 신뢰도의 균형
        weight_balance = 1.0 - np.var(weights)
        confidence_avg = np.mean(confidences)

        return (weight_balance + confidence_avg) / 2

    def _evaluate_adaptability(self, composition: HybridComposition) -> float:
        """적응성 평가"""
        # 구성의 적응성 평가
        weight_diversity = len(composition.signature_weights)
        blending_complexity = {
            BlendingMode.WEIGHTED_AVERAGE: 0.6,
            BlendingMode.DOMINANT_OVERLAY: 0.7,
            BlendingMode.CONTEXTUAL_SWITCHING: 0.8,
            BlendingMode.HARMONIC_FUSION: 0.9,
            BlendingMode.ADAPTIVE_MORPHING: 1.0,
        }.get(composition.blending_mode, 0.5)

        return (weight_diversity / 4.0 + blending_complexity) / 2

    def get_composition_recommendations(
        self, context_type: ContextType, context_details: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """구성 추천"""
        recommendations = []

        # 여러 블렌딩 모드로 구성 생성
        for mode in BlendingMode:
            # 임시 구성 생성
            temp_weights = self._calculate_context_weights(
                context_type, context_details
            )
            temp_signature_weights = [
                SignatureWeight(
                    signature_name=name,
                    weight=weight,
                    confidence=0.8,
                    contribution_areas=[],
                    activation_threshold=0.1,
                )
                for name, weight in temp_weights.items()
                if weight > 0.05
            ]

            predicted_performance = self._predict_composition_performance(
                temp_signature_weights, mode, context_type
            )

            recommendations.append(
                {
                    "blending_mode": mode.value,
                    "weights": temp_weights,
                    "predicted_performance": predicted_performance["overall"],
                    "emotional_coherence": predicted_performance["emotional"],
                    "expression_consistency": predicted_performance["expression"],
                    "recommendation_score": predicted_performance["effectiveness"],
                }
            )

        # 성능 점수 기준으로 정렬
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)

        return recommendations[:3]  # 상위 3개 추천

    def get_composition_summary(self) -> Dict[str, Any]:
        """구성 요약 반환"""
        if not self.current_composition:
            return {"status": "no_active_composition"}

        composition = self.current_composition

        # 최근 성능 통계
        recent_metrics = list(self.performance_metrics)[-10:]

        summary = {
            "status": "active",
            "current_composition": {
                "id": composition.composition_id,
                "timestamp": composition.timestamp.isoformat(),
                "blending_mode": composition.blending_mode.value,
                "context_type": composition.context_type.value,
                "signature_weights": {
                    sw.signature_name: sw.weight for sw in composition.signature_weights
                },
                "predicted_performance": composition.performance_score,
            },
            "performance_history": {
                "total_compositions": len(self.composition_history),
                "total_applications": len(self.performance_metrics),
                "average_quality": (
                    np.mean([m.quality_score for m in recent_metrics])
                    if recent_metrics
                    else 0.0
                ),
                "average_execution_time": (
                    np.mean([m.execution_time_ms for m in recent_metrics])
                    if recent_metrics
                    else 0.0
                ),
            },
            "learned_patterns": {
                context.value: len(patterns)
                for context, patterns in self.context_patterns.items()
            },
            "context_success_rates": dict(self.context_success_rates),
        }

        return summary

    def visualize_composition(self, composition_id: str = None) -> str:
        """구성 시각화 (텍스트 기반)"""
        if composition_id:
            composition = next(
                (
                    c
                    for c in self.composition_history
                    if c.composition_id == composition_id
                ),
                None,
            )
        else:
            composition = self.current_composition

        if not composition:
            return "❌ 표시할 구성이 없습니다."

        viz = f"🎭 Hybrid Signature Composition: {composition.composition_id}\n"
        viz += "=" * 60 + "\n\n"

        # 기본 정보
        viz += f"📊 Composition Overview:\n"
        viz += f"   Timestamp: {composition.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        viz += f"   Context Type: {composition.context_type.value}\n"
        viz += f"   Blending Mode: {composition.blending_mode.value}\n"
        viz += f"   Performance Score: {composition.performance_score:.3f}\n\n"

        # 시그니처 가중치 분포
        viz += f"⚖️ Signature Weight Distribution:\n"
        for weight_obj in sorted(
            composition.signature_weights, key=lambda x: x.weight, reverse=True
        ):
            weight_bar = "█" * int(weight_obj.weight * 20)
            viz += f"   {weight_obj.signature_name:8} | {weight_bar:20} | "
            viz += f"{weight_obj.weight:.3f} (conf: {weight_obj.confidence:.2f})\n"

        # 기여 영역
        viz += f"\n🎯 Contribution Areas:\n"
        for weight_obj in composition.signature_weights:
            if weight_obj.contribution_areas:
                viz += f"   {weight_obj.signature_name}: {', '.join(weight_obj.contribution_areas)}\n"

        # 품질 지표
        viz += f"\n📈 Quality Metrics:\n"
        viz += f"   Emotional Coherence: {composition.emotional_coherence:.3f}\n"
        viz += f"   Expression Consistency: {composition.expression_consistency:.3f}\n"
        viz += f"   Overall Effectiveness: {composition.overall_effectiveness:.3f}\n"

        return viz

    def save_composition_data(self, filename: str = None) -> str:
        """구성 데이터 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hybrid_composition_data_{timestamp}.json"

        # 저장할 데이터 준비
        save_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_compositions": len(self.composition_history),
                "total_performance_records": len(self.performance_metrics),
            },
            "base_signatures": self.base_signatures,
            "blending_rules": {
                name: {
                    "weights": rule["weights"],
                    "mode": rule["mode"].value,
                    "context": rule["context"].value,
                }
                for name, rule in self.blending_rules.items()
            },
            "composition_history": [],
            "performance_metrics": [],
            "context_patterns": {},
            "learned_compositions": self.learned_compositions,
            "context_success_rates": dict(self.context_success_rates),
        }

        # HybridComposition 객체들을 직렬화
        for composition in self.composition_history:
            comp_dict = asdict(composition)
            comp_dict["timestamp"] = composition.timestamp.isoformat()
            comp_dict["blending_mode"] = composition.blending_mode.value
            comp_dict["context_type"] = composition.context_type.value
            save_data["composition_history"].append(comp_dict)

        # HybridPerformanceMetric 객체들을 직렬화
        for metric in self.performance_metrics:
            metric_dict = asdict(metric)
            metric_dict["timestamp"] = metric.timestamp.isoformat()
            save_data["performance_metrics"].append(metric_dict)

        # 컨텍스트 패턴 직렬화
        for context_type, patterns in self.context_patterns.items():
            save_data["context_patterns"][context_type.value] = patterns

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return f"✅ 하이브리드 구성 데이터 저장 완료: {filename}"
        except Exception as e:
            return f"❌ 저장 실패: {e}"


# 편의 함수들
def create_hybrid_signature_composer() -> HybridSignatureComposer:
    """Hybrid Signature Composer 생성"""
    return HybridSignatureComposer()


def quick_hybrid_composition(
    context_type: str, weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """빠른 하이브리드 구성"""
    composer = HybridSignatureComposer()

    # 문자열을 ContextType으로 변환
    try:
        context_enum = ContextType(context_type.lower())
    except ValueError:
        context_enum = ContextType.CONVERSATIONAL

    composition = composer.compose_hybrid_signature(
        context_enum, forced_weights=weights
    )

    return {
        "composition_id": composition.composition_id,
        "weights": {
            sw.signature_name: sw.weight for sw in composition.signature_weights
        },
        "blending_mode": composition.blending_mode.value,
        "predicted_performance": composition.performance_score,
    }


if __name__ == "__main__":
    # 테스트 실행
    print("🎭 Hybrid Signature Composer 테스트...")

    composer = HybridSignatureComposer()

    # 다양한 컨텍스트에서 구성 테스트
    test_contexts = [
        (ContextType.ANALYTICAL, {"complexity": 0.8}),
        (ContextType.EMOTIONAL, {"emotion_intensity": 0.9}),
        (ContextType.CREATIVE, {"creativity_required": 0.8}),
        (ContextType.SUPPORTIVE, {"support_needed": 0.7}),
    ]

    print("\n🔄 다양한 컨텍스트에서 하이브리드 구성 생성...")
    for context_type, context_details in test_contexts:
        composition = composer.compose_hybrid_signature(context_type, context_details)
        print(f"\n📋 {context_type.value.title()} Context:")
        print(f"   Composition ID: {composition.composition_id}")
        print(f"   Blending Mode: {composition.blending_mode.value}")
        print(f"   Performance Score: {composition.performance_score:.3f}")

        # 가중치 표시
        for weight_obj in composition.signature_weights:
            print(f"   {weight_obj.signature_name}: {weight_obj.weight:.3f}")

    # 하이브리드 적용 테스트
    print("\n🎯 하이브리드 적용 테스트:")
    test_input = (
        "I'm feeling overwhelmed with a complex problem and need creative solutions."
    )
    result = composer.apply_hybrid_composition(test_input, "problem_solving")

    print(f"Input: {test_input}")
    print(f"Composition Used: {result['composition_used']}")
    print(f"Execution Time: {result['execution_time_ms']:.1f}ms")
    print(f"Result: {result['result'][:100]}...")

    # 추천 시스템 테스트
    print("\n💡 구성 추천 테스트:")
    recommendations = composer.get_composition_recommendations(
        ContextType.CREATIVE, {"creativity_required": 0.9, "complexity": 0.6}
    )

    for i, rec in enumerate(recommendations, 1):
        print(
            f"   {i}. {rec['blending_mode']} (Score: {rec['recommendation_score']:.3f})"
        )
        main_signatures = sorted(
            rec["weights"].items(), key=lambda x: x[1], reverse=True
        )[:2]
        print(
            f"      Main: {', '.join([f'{sig}({weight:.2f})' for sig, weight in main_signatures])}"
        )

    # 시각화 테스트
    print("\n🎭 구성 시각화:")
    visualization = composer.visualize_composition()
    print(visualization)

    # 요약 정보
    summary = composer.get_composition_summary()
    print(f"\n📊 Composer Summary:")
    print(f"   Active Composition: {summary['current_composition']['id']}")
    print(
        f"   Total Compositions: {summary['performance_history']['total_compositions']}"
    )
    print(
        f"   Average Quality: {summary['performance_history']['average_quality']:.3f}"
    )

    # 저장 테스트
    save_result = composer.save_composition_data()
    print(f"\n{save_result}")

    print("\n✅ Hybrid Signature Composer 테스트 완료!")
