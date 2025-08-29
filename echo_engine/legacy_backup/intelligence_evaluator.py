"""
Multi-Dimensional Intelligence Evaluator - GPT-5 Level Self-Assessment
=====================================================================

Implements comprehensive intelligence evaluation with:
- Multi-faceted cognitive assessment
- Dynamic intelligence metrics
- Self-awareness scoring
- Performance prediction capabilities
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import json
import logging
import time
import math
from enum import Enum

logger = logging.getLogger(__name__)


class IntelligenceDimension(Enum):
    """지능의 다차원 구분"""

    LOGICAL = "logical"  # 논리적 지능
    CREATIVE = "creative"  # 창의적 지능
    ANALYTICAL = "analytical"  # 분석적 지능
    EMOTIONAL = "emotional"  # 감정적 지능
    STRATEGIC = "strategic"  # 전략적 지능
    SYNTHETIC = "synthetic"  # 종합적 지능
    ADAPTIVE = "adaptive"  # 적응적 지능
    META_COGNITIVE = "meta_cognitive"  # 메타인지 지능


class EvaluationLevel(Enum):
    """평가 수준"""

    SURFACE = 1  # 표면적 평가
    DEEP = 2  # 심층 평가
    HOLISTIC = 3  # 전체적 평가
    TRANSCENDENT = 4  # 초월적 평가


@dataclass
class IntelligenceScore:
    """지능 점수 구조"""

    dimension: IntelligenceDimension
    raw_score: float  # 원시 점수 (0-1)
    confidence: float  # 평가 신뢰도
    evidence_strength: float  # 증거 강도
    improvement_potential: float  # 개선 가능성
    meta_evaluation: Dict[str, float]  # 메타 평가


@dataclass
class ComprehensiveEvaluation:
    """종합 평가 결과"""

    evaluation_id: str
    timestamp: float

    # 차원별 점수
    dimension_scores: Dict[IntelligenceDimension, IntelligenceScore] = field(
        default_factory=dict
    )

    # 통합 지표
    overall_intelligence: float = 0.0
    cognitive_coherence: float = 0.0  # 인지적 일관성
    adaptive_capacity: float = 0.0  # 적응 능력
    growth_trajectory: float = 0.0  # 성장 궤적

    # 메타 분석
    evaluation_quality: float = 0.0  # 평가 품질
    self_awareness_level: float = 0.0  # 자기 인식 수준
    blind_spots: List[str] = field(default_factory=list)

    # 예측 및 권고
    performance_prediction: Dict[str, float] = field(default_factory=dict)
    improvement_recommendations: List[Dict[str, Any]] = field(default_factory=list)


class MultiDimensionalIntelligenceEvaluator:
    """GPT-5 수준의 다차원 지능 평가자

    핵심 기능:
    1. 다차원 지능 측정 - 8개 지능 영역의 종합 평가
    2. 동적 평가 시스템 - 맥락과 상황에 따른 적응적 평가
    3. 메타 인지적 자기 평가 - 자신의 평가 능력에 대한 평가
    4. 성장 및 개선 예측 - 미래 성능 예측과 개선 방안 제시
    """

    def __init__(self, evaluation_config: Optional[Dict[str, Any]] = None):
        self.config = evaluation_config or self._default_config()
        self.evaluation_history: List[ComprehensiveEvaluation] = []
        self.dimension_weights = self._initialize_dimension_weights()
        self.benchmark_scores = self._load_benchmark_scores()
        self.meta_calibration = self._initialize_meta_calibration()

        logger.info(
            "MultiDimensionalIntelligenceEvaluator initialized with GPT-5 level capabilities"
        )

    def evaluate_response(
        self,
        response: str,
        context: Dict[str, Any],
        evidence: List[Dict[str, Any]] = None,
    ) -> ComprehensiveEvaluation:
        """응답에 대한 종합적 지능 평가"""

        evaluation_id = f"eval-{int(time.time())}-{hash(response) % 10000}"

        # 차원별 평가 수행
        dimension_scores = {}
        for dimension in IntelligenceDimension:
            score = self._evaluate_dimension(
                dimension, response, context, evidence or []
            )
            dimension_scores[dimension] = score

        # 통합 지표 계산
        overall_intelligence = self._calculate_overall_intelligence(dimension_scores)
        cognitive_coherence = self._assess_cognitive_coherence(dimension_scores)
        adaptive_capacity = self._assess_adaptive_capacity(response, context)
        growth_trajectory = self._calculate_growth_trajectory(dimension_scores)

        # 메타 분석
        evaluation_quality = self._assess_evaluation_quality(dimension_scores)
        self_awareness_level = self._assess_self_awareness(response, context)
        blind_spots = self._identify_blind_spots(dimension_scores)

        # 예측 및 권고 생성
        performance_prediction = self._predict_performance(dimension_scores, context)
        improvement_recommendations = self._generate_improvement_recommendations(
            dimension_scores
        )

        evaluation = ComprehensiveEvaluation(
            evaluation_id=evaluation_id,
            timestamp=time.time(),
            dimension_scores=dimension_scores,
            overall_intelligence=overall_intelligence,
            cognitive_coherence=cognitive_coherence,
            adaptive_capacity=adaptive_capacity,
            growth_trajectory=growth_trajectory,
            evaluation_quality=evaluation_quality,
            self_awareness_level=self_awareness_level,
            blind_spots=blind_spots,
            performance_prediction=performance_prediction,
            improvement_recommendations=improvement_recommendations,
        )

        # 이력 추가
        self.evaluation_history.append(evaluation)

        logger.info(
            f"Comprehensive evaluation completed: {evaluation_id}, overall={overall_intelligence:.3f}"
        )
        return evaluation

    def meta_evaluate_evaluation(
        self, evaluation: ComprehensiveEvaluation
    ) -> Dict[str, Any]:
        """평가에 대한 메타 평가 - 자신의 평가 능력을 평가"""

        meta_eval = {
            "evaluation_consistency": self._check_evaluation_consistency(evaluation),
            "evaluation_depth": self._assess_evaluation_depth(evaluation),
            "evaluation_bias": self._detect_evaluation_bias(evaluation),
            "calibration_quality": self._assess_calibration_quality(evaluation),
            "improvement_suggestions": self._suggest_evaluation_improvements(
                evaluation
            ),
        }

        logger.info(f"Meta-evaluation completed for {evaluation.evaluation_id}")
        return meta_eval

    def comparative_analysis(
        self, evaluations: List[ComprehensiveEvaluation]
    ) -> Dict[str, Any]:
        """여러 평가 간 비교 분석"""

        if len(evaluations) < 2:
            return {"error": "At least 2 evaluations required for comparison"}

        analysis = {
            "trend_analysis": self._analyze_trends(evaluations),
            "consistency_analysis": self._analyze_consistency(evaluations),
            "growth_patterns": self._identify_growth_patterns(evaluations),
            "performance_stability": self._assess_performance_stability(evaluations),
            "dimensional_evolution": self._track_dimensional_evolution(evaluations),
        }

        logger.info(
            f"Comparative analysis completed for {len(evaluations)} evaluations"
        )
        return analysis

    # === 차원별 평가 메서드들 ===

    def _evaluate_dimension(
        self,
        dimension: IntelligenceDimension,
        response: str,
        context: Dict[str, Any],
        evidence: List[Dict[str, Any]],
    ) -> IntelligenceScore:
        """특정 지능 차원에 대한 평가"""

        if dimension == IntelligenceDimension.LOGICAL:
            return self._evaluate_logical_intelligence(response, context, evidence)
        elif dimension == IntelligenceDimension.CREATIVE:
            return self._evaluate_creative_intelligence(response, context, evidence)
        elif dimension == IntelligenceDimension.ANALYTICAL:
            return self._evaluate_analytical_intelligence(response, context, evidence)
        elif dimension == IntelligenceDimension.EMOTIONAL:
            return self._evaluate_emotional_intelligence(response, context, evidence)
        elif dimension == IntelligenceDimension.STRATEGIC:
            return self._evaluate_strategic_intelligence(response, context, evidence)
        elif dimension == IntelligenceDimension.SYNTHETIC:
            return self._evaluate_synthetic_intelligence(response, context, evidence)
        elif dimension == IntelligenceDimension.ADAPTIVE:
            return self._evaluate_adaptive_intelligence(response, context, evidence)
        elif dimension == IntelligenceDimension.META_COGNITIVE:
            return self._evaluate_meta_cognitive_intelligence(
                response, context, evidence
            )
        else:
            return self._default_intelligence_score(dimension)

    def _evaluate_logical_intelligence(
        self, response: str, context: Dict[str, Any], evidence: List[Dict[str, Any]]
    ) -> IntelligenceScore:
        """논리적 지능 평가"""

        # 논리적 구조 분석
        logical_structure = self._analyze_logical_structure(response)

        # 추론의 타당성 검증
        reasoning_validity = self._assess_reasoning_validity(response)

        # 논리적 일관성 체크
        consistency = self._check_logical_consistency(response)

        # 증거 활용도
        evidence_utilization = self._assess_evidence_utilization(response, evidence)

        raw_score = (
            logical_structure + reasoning_validity + consistency + evidence_utilization
        ) / 4
        confidence = self._calculate_confidence(raw_score, "logical")
        evidence_strength = len(evidence) * 0.1 if evidence else 0.3
        improvement_potential = max(0.1, 1.0 - raw_score)

        meta_evaluation = {
            "structure_quality": logical_structure,
            "reasoning_validity": reasoning_validity,
            "consistency_level": consistency,
            "evidence_integration": evidence_utilization,
        }

        return IntelligenceScore(
            dimension=IntelligenceDimension.LOGICAL,
            raw_score=raw_score,
            confidence=confidence,
            evidence_strength=evidence_strength,
            improvement_potential=improvement_potential,
            meta_evaluation=meta_evaluation,
        )

    def _evaluate_creative_intelligence(
        self, response: str, context: Dict[str, Any], evidence: List[Dict[str, Any]]
    ) -> IntelligenceScore:
        """창의적 지능 평가"""

        # 독창성 평가
        originality = self._assess_originality(response)

        # 유연한 사고
        flexibility = self._assess_thinking_flexibility(response)

        # 아이디어 정교화
        elaboration = self._assess_idea_elaboration(response)

        # 창의적 연결성
        creative_connections = self._assess_creative_connections(response, context)

        raw_score = (originality + flexibility + elaboration + creative_connections) / 4
        confidence = self._calculate_confidence(raw_score, "creative")
        evidence_strength = 0.7  # 창의성은 외부 증거보다는 내재적 특성
        improvement_potential = max(0.2, 1.0 - raw_score)

        meta_evaluation = {
            "originality_level": originality,
            "flexibility_score": flexibility,
            "elaboration_depth": elaboration,
            "connection_quality": creative_connections,
        }

        return IntelligenceScore(
            dimension=IntelligenceDimension.CREATIVE,
            raw_score=raw_score,
            confidence=confidence,
            evidence_strength=evidence_strength,
            improvement_potential=improvement_potential,
            meta_evaluation=meta_evaluation,
        )

    def _evaluate_analytical_intelligence(
        self, response: str, context: Dict[str, Any], evidence: List[Dict[str, Any]]
    ) -> IntelligenceScore:
        """분석적 지능 평가"""

        # 패턴 인식 능력
        pattern_recognition = self._assess_pattern_recognition(response)

        # 데이터 해석 능력
        data_interpretation = self._assess_data_interpretation(response, evidence)

        # 체계적 분해 능력
        systematic_breakdown = self._assess_systematic_breakdown(response)

        # 비판적 사고
        critical_thinking = self._assess_critical_thinking(response)

        raw_score = (
            pattern_recognition
            + data_interpretation
            + systematic_breakdown
            + critical_thinking
        ) / 4
        confidence = self._calculate_confidence(raw_score, "analytical")
        evidence_strength = min(1.0, len(evidence) * 0.15) if evidence else 0.4
        improvement_potential = max(0.1, 1.0 - raw_score)

        meta_evaluation = {
            "pattern_recognition": pattern_recognition,
            "data_interpretation": data_interpretation,
            "systematic_approach": systematic_breakdown,
            "critical_thinking": critical_thinking,
        }

        return IntelligenceScore(
            dimension=IntelligenceDimension.ANALYTICAL,
            raw_score=raw_score,
            confidence=confidence,
            evidence_strength=evidence_strength,
            improvement_potential=improvement_potential,
            meta_evaluation=meta_evaluation,
        )

    def _evaluate_emotional_intelligence(
        self, response: str, context: Dict[str, Any], evidence: List[Dict[str, Any]]
    ) -> IntelligenceScore:
        """감정적 지능 평가"""

        # 감정 인식
        emotion_recognition = self._assess_emotion_recognition(response, context)

        # 감정 조절
        emotion_regulation = self._assess_emotion_regulation(response)

        # 공감 능력
        empathy = self._assess_empathy(response, context)

        # 사회적 인식
        social_awareness = self._assess_social_awareness(response, context)

        raw_score = (
            emotion_recognition + emotion_regulation + empathy + social_awareness
        ) / 4
        confidence = self._calculate_confidence(raw_score, "emotional")
        evidence_strength = 0.6  # 감정 지능은 맥락 의존적
        improvement_potential = max(0.15, 1.0 - raw_score)

        meta_evaluation = {
            "emotion_recognition": emotion_recognition,
            "emotion_regulation": emotion_regulation,
            "empathy_level": empathy,
            "social_awareness": social_awareness,
        }

        return IntelligenceScore(
            dimension=IntelligenceDimension.EMOTIONAL,
            raw_score=raw_score,
            confidence=confidence,
            evidence_strength=evidence_strength,
            improvement_potential=improvement_potential,
            meta_evaluation=meta_evaluation,
        )

    def _evaluate_strategic_intelligence(
        self, response: str, context: Dict[str, Any], evidence: List[Dict[str, Any]]
    ) -> IntelligenceScore:
        """전략적 지능 평가"""

        # 장기적 사고
        long_term_thinking = self._assess_long_term_thinking(response)

        # 목표 설정 능력
        goal_setting = self._assess_goal_setting(response, context)

        # 자원 최적화
        resource_optimization = self._assess_resource_optimization(response, context)

        # 리스크 관리
        risk_management = self._assess_risk_management(response)

        raw_score = (
            long_term_thinking + goal_setting + resource_optimization + risk_management
        ) / 4
        confidence = self._calculate_confidence(raw_score, "strategic")
        evidence_strength = 0.5
        improvement_potential = max(0.1, 1.0 - raw_score)

        meta_evaluation = {
            "long_term_vision": long_term_thinking,
            "goal_clarity": goal_setting,
            "resource_efficiency": resource_optimization,
            "risk_awareness": risk_management,
        }

        return IntelligenceScore(
            dimension=IntelligenceDimension.STRATEGIC,
            raw_score=raw_score,
            confidence=confidence,
            evidence_strength=evidence_strength,
            improvement_potential=improvement_potential,
            meta_evaluation=meta_evaluation,
        )

    def _evaluate_synthetic_intelligence(
        self, response: str, context: Dict[str, Any], evidence: List[Dict[str, Any]]
    ) -> IntelligenceScore:
        """종합적 지능 평가"""

        # 다영역 통합
        cross_domain_integration = self._assess_cross_domain_integration(response)

        # 전체적 관점
        holistic_perspective = self._assess_holistic_perspective(response, context)

        # 복잡성 관리
        complexity_management = self._assess_complexity_management(response)

        # 창발적 통찰
        emergent_insights = self._assess_emergent_insights(response)

        raw_score = (
            cross_domain_integration
            + holistic_perspective
            + complexity_management
            + emergent_insights
        ) / 4
        confidence = self._calculate_confidence(raw_score, "synthetic")
        evidence_strength = 0.8  # 종합 지능은 높은 증거 강도 필요
        improvement_potential = max(0.2, 1.0 - raw_score)

        meta_evaluation = {
            "integration_ability": cross_domain_integration,
            "holistic_view": holistic_perspective,
            "complexity_handling": complexity_management,
            "emergent_quality": emergent_insights,
        }

        return IntelligenceScore(
            dimension=IntelligenceDimension.SYNTHETIC,
            raw_score=raw_score,
            confidence=confidence,
            evidence_strength=evidence_strength,
            improvement_potential=improvement_potential,
            meta_evaluation=meta_evaluation,
        )

    def _evaluate_adaptive_intelligence(
        self, response: str, context: Dict[str, Any], evidence: List[Dict[str, Any]]
    ) -> IntelligenceScore:
        """적응적 지능 평가"""

        # 맥락 적응성
        context_adaptation = self._assess_context_adaptation(response, context)

        # 학습 능력
        learning_ability = self._assess_learning_ability(response)

        # 유연성
        flexibility = self._assess_adaptive_flexibility(response)

        # 회복력
        resilience = self._assess_resilience(response, context)

        raw_score = (
            context_adaptation + learning_ability + flexibility + resilience
        ) / 4
        confidence = self._calculate_confidence(raw_score, "adaptive")
        evidence_strength = 0.6
        improvement_potential = max(0.1, 1.0 - raw_score)

        meta_evaluation = {
            "context_sensitivity": context_adaptation,
            "learning_capacity": learning_ability,
            "adaptive_flexibility": flexibility,
            "resilience_level": resilience,
        }

        return IntelligenceScore(
            dimension=IntelligenceDimension.ADAPTIVE,
            raw_score=raw_score,
            confidence=confidence,
            evidence_strength=evidence_strength,
            improvement_potential=improvement_potential,
            meta_evaluation=meta_evaluation,
        )

    def _evaluate_meta_cognitive_intelligence(
        self, response: str, context: Dict[str, Any], evidence: List[Dict[str, Any]]
    ) -> IntelligenceScore:
        """메타인지 지능 평가"""

        # 자기 인식
        self_awareness = self._assess_self_awareness(response, context)

        # 사고에 대한 사고
        thinking_about_thinking = self._assess_meta_thinking(response)

        # 인지 전략 사용
        cognitive_strategy_use = self._assess_cognitive_strategy_use(response)

        # 성찰 능력
        reflection_ability = self._assess_reflection_ability(response)

        raw_score = (
            self_awareness
            + thinking_about_thinking
            + cognitive_strategy_use
            + reflection_ability
        ) / 4
        confidence = self._calculate_confidence(raw_score, "meta_cognitive")
        evidence_strength = 0.7  # 메타인지는 내재적 특성이 강함
        improvement_potential = max(0.15, 1.0 - raw_score)

        meta_evaluation = {
            "self_awareness_depth": self_awareness,
            "meta_thinking_quality": thinking_about_thinking,
            "strategy_sophistication": cognitive_strategy_use,
            "reflection_depth": reflection_ability,
        }

        return IntelligenceScore(
            dimension=IntelligenceDimension.META_COGNITIVE,
            raw_score=raw_score,
            confidence=confidence,
            evidence_strength=evidence_strength,
            improvement_potential=improvement_potential,
            meta_evaluation=meta_evaluation,
        )

    # === 통합 평가 메서드들 ===

    def _calculate_overall_intelligence(
        self, dimension_scores: Dict[IntelligenceDimension, IntelligenceScore]
    ) -> float:
        """전체 지능 점수 계산"""
        if not dimension_scores:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for dimension, score in dimension_scores.items():
            weight = self.dimension_weights.get(dimension, 1.0)
            weighted_sum += score.raw_score * weight * score.confidence
            total_weight += weight * score.confidence

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _assess_cognitive_coherence(
        self, dimension_scores: Dict[IntelligenceDimension, IntelligenceScore]
    ) -> float:
        """인지적 일관성 평가"""
        if len(dimension_scores) < 2:
            return 0.5

        scores = [score.raw_score for score in dimension_scores.values()]
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)

        # 낮은 분산은 높은 일관성을 의미
        coherence = max(0.0, 1.0 - math.sqrt(variance))
        return coherence

    def _assess_adaptive_capacity(
        self, response: str, context: Dict[str, Any]
    ) -> float:
        """적응 능력 평가"""
        # 맥락 변화에 대한 대응력 평가
        context_sensitivity = self._assess_context_sensitivity(response, context)

        # 불확실성 처리 능력
        uncertainty_handling = self._assess_uncertainty_handling(response)

        # 학습 및 개선 의지
        improvement_orientation = self._assess_improvement_orientation(response)

        return (
            context_sensitivity + uncertainty_handling + improvement_orientation
        ) / 3

    def _calculate_growth_trajectory(
        self, dimension_scores: Dict[IntelligenceDimension, IntelligenceScore]
    ) -> float:
        """성장 궤적 계산"""
        if not self.evaluation_history:
            # 초기 평가인 경우, 개선 잠재력 기반으로 계산
            avg_potential = sum(
                score.improvement_potential for score in dimension_scores.values()
            ) / len(dimension_scores)
            return avg_potential

        # 이전 평가와 비교하여 성장률 계산
        previous_eval = self.evaluation_history[-1]

        growth_sum = 0.0
        comparison_count = 0

        for dimension, current_score in dimension_scores.items():
            if dimension in previous_eval.dimension_scores:
                previous_score = previous_eval.dimension_scores[dimension].raw_score
                growth = (current_score.raw_score - previous_score) / max(
                    0.01, previous_score
                )
                growth_sum += growth
                comparison_count += 1

        return growth_sum / comparison_count if comparison_count > 0 else 0.0

    # === 메타 분석 메서드들 ===

    def _assess_evaluation_quality(
        self, dimension_scores: Dict[IntelligenceDimension, IntelligenceScore]
    ) -> float:
        """평가 품질 평가"""
        quality_indicators = []

        # 신뢰도 분포
        confidences = [score.confidence for score in dimension_scores.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        quality_indicators.append(avg_confidence)

        # 증거 강도
        evidence_strengths = [
            score.evidence_strength for score in dimension_scores.values()
        ]
        avg_evidence = (
            sum(evidence_strengths) / len(evidence_strengths)
            if evidence_strengths
            else 0.5
        )
        quality_indicators.append(avg_evidence)

        # 평가 완성도 (모든 차원이 평가되었는지)
        completeness = len(dimension_scores) / len(IntelligenceDimension)
        quality_indicators.append(completeness)

        return sum(quality_indicators) / len(quality_indicators)

    def _identify_blind_spots(
        self, dimension_scores: Dict[IntelligenceDimension, IntelligenceScore]
    ) -> List[str]:
        """맹점 식별"""
        blind_spots = []

        # 낮은 점수 영역
        for dimension, score in dimension_scores.items():
            if score.raw_score < 0.4:
                blind_spots.append(f"low_{dimension.value}_intelligence")

        # 낮은 신뢰도 영역
        for dimension, score in dimension_scores.items():
            if score.confidence < 0.5:
                blind_spots.append(f"uncertain_{dimension.value}_evaluation")

        # 불균형한 발달
        scores = [score.raw_score for score in dimension_scores.values()]
        if scores:
            max_score = max(scores)
            min_score = min(scores)
            if max_score - min_score > 0.5:
                blind_spots.append("unbalanced_cognitive_development")

        return blind_spots

    def _predict_performance(
        self,
        dimension_scores: Dict[IntelligenceDimension, IntelligenceScore],
        context: Dict[str, Any],
    ) -> Dict[str, float]:
        """성능 예측"""
        predictions = {}

        # 단기 성능 예측
        short_term_weights = {
            IntelligenceDimension.LOGICAL: 0.3,
            IntelligenceDimension.ANALYTICAL: 0.3,
            IntelligenceDimension.ADAPTIVE: 0.4,
        }

        short_term_score = 0.0
        for dim, weight in short_term_weights.items():
            if dim in dimension_scores:
                short_term_score += dimension_scores[dim].raw_score * weight

        predictions["short_term_performance"] = short_term_score

        # 장기 성능 예측
        long_term_weights = {
            IntelligenceDimension.STRATEGIC: 0.3,
            IntelligenceDimension.SYNTHETIC: 0.3,
            IntelligenceDimension.META_COGNITIVE: 0.4,
        }

        long_term_score = 0.0
        for dim, weight in long_term_weights.items():
            if dim in dimension_scores:
                long_term_score += dimension_scores[dim].raw_score * weight

        predictions["long_term_performance"] = long_term_score

        # 창의적 과제 성능 예측
        creative_score = dimension_scores.get(
            IntelligenceDimension.CREATIVE,
            self._default_intelligence_score(IntelligenceDimension.CREATIVE),
        ).raw_score
        predictions["creative_task_performance"] = creative_score

        # 복잡한 문제 해결 성능 예측
        complex_problem_weights = {
            IntelligenceDimension.ANALYTICAL: 0.25,
            IntelligenceDimension.SYNTHETIC: 0.25,
            IntelligenceDimension.STRATEGIC: 0.25,
            IntelligenceDimension.ADAPTIVE: 0.25,
        }

        complex_score = 0.0
        for dim, weight in complex_problem_weights.items():
            if dim in dimension_scores:
                complex_score += dimension_scores[dim].raw_score * weight

        predictions["complex_problem_solving"] = complex_score

        return predictions

    def _generate_improvement_recommendations(
        self, dimension_scores: Dict[IntelligenceDimension, IntelligenceScore]
    ) -> List[Dict[str, Any]]:
        """개선 권고 생성"""
        recommendations = []

        # 각 차원별 개선 권고
        for dimension, score in dimension_scores.items():
            if score.improvement_potential > 0.3:  # 개선 여지가 충분한 경우
                recommendations.append(
                    {
                        "type": "dimension_improvement",
                        "target": dimension.value,
                        "current_score": score.raw_score,
                        "improvement_potential": score.improvement_potential,
                        "priority": (
                            "high" if score.improvement_potential > 0.6 else "medium"
                        ),
                        "suggested_actions": self._get_improvement_actions(dimension),
                        "expected_timeline": self._estimate_improvement_timeline(
                            score.improvement_potential
                        ),
                    }
                )

        # 균형 개선 권고
        scores = [score.raw_score for score in dimension_scores.values()]
        if scores:
            variance = sum((s - sum(scores) / len(scores)) ** 2 for s in scores) / len(
                scores
            )
            if variance > 0.1:  # 불균형이 큰 경우
                recommendations.append(
                    {
                        "type": "balance_improvement",
                        "issue": "cognitive_imbalance",
                        "severity": "high" if variance > 0.2 else "medium",
                        "suggested_actions": [
                            "focus_on_weaker_dimensions",
                            "integrate_cognitive_skills",
                        ],
                        "priority": "medium",
                    }
                )

        # 메타인지 개선 권고 (항상 포함)
        meta_score = dimension_scores.get(IntelligenceDimension.META_COGNITIVE)
        if meta_score and meta_score.raw_score < 0.8:
            recommendations.append(
                {
                    "type": "meta_cognitive_enhancement",
                    "current_level": meta_score.raw_score,
                    "target_level": 0.9,
                    "suggested_actions": [
                        "self_reflection_practice",
                        "cognitive_strategy_learning",
                        "awareness_training",
                    ],
                    "priority": "high",
                    "rationale": "Meta-cognitive skills enhance all other cognitive abilities",
                }
            )

        return sorted(
            recommendations,
            key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(
                x.get("priority", "low"), 1
            ),
            reverse=True,
        )

    # === 개별 평가 요소들 (간소화된 구현) ===

    def _analyze_logical_structure(self, response: str) -> float:
        """논리적 구조 분석"""
        # 논리적 연결어 분석
        logical_connectors = [
            "therefore",
            "because",
            "since",
            "thus",
            "consequently",
            "hence",
        ]
        connector_count = sum(
            1 for word in logical_connectors if word in response.lower()
        )

        # 문장 구조 복잡도
        sentences = response.split(".")
        avg_sentence_length = sum(len(sent.split()) for sent in sentences) / max(
            len(sentences), 1
        )

        # 점수 계산 (0-1)
        structure_score = min(
            1.0, (connector_count * 0.2) + min(0.6, avg_sentence_length / 20)
        )
        return structure_score

    def _assess_reasoning_validity(self, response: str) -> float:
        """추론 타당성 평가"""
        # 증거 기반 추론 패턴 검출
        evidence_patterns = [
            "research shows",
            "studies indicate",
            "data suggests",
            "analysis reveals",
        ]
        evidence_score = sum(
            0.2 for pattern in evidence_patterns if pattern in response.lower()
        )

        # 논리적 오류 검출
        fallacy_patterns = [
            "always",
            "never",
            "everyone",
            "nobody",
            "all",
        ]  # 과도한 일반화
        fallacy_penalty = sum(
            0.1 for pattern in fallacy_patterns if pattern in response.lower()
        )

        validity_score = max(0.3, min(1.0, 0.7 + evidence_score - fallacy_penalty))
        return validity_score

    def _check_logical_consistency(self, response: str) -> float:
        """논리적 일관성 확인"""
        # 모순 감지 (간단한 키워드 기반)
        contradictions = ["however", "but", "although", "despite", "nevertheless"]
        contradiction_count = sum(
            1 for word in contradictions if word in response.lower()
        )

        # 적절한 수준의 모순은 복잡한 사고를 나타냄
        if contradiction_count <= 2:
            consistency_score = 0.9
        elif contradiction_count <= 4:
            consistency_score = 0.7
        else:
            consistency_score = 0.5

        return consistency_score

    def _assess_evidence_utilization(
        self, response: str, evidence: List[Dict[str, Any]]
    ) -> float:
        """증거 활용도 평가"""
        if not evidence:
            return 0.5  # 중간 점수

        # 증거 언급 확인
        evidence_mentions = 0
        for item in evidence:
            title = item.get("title", "").lower()
            if title and any(
                word in response.lower() for word in title.split() if len(word) > 3
            ):
                evidence_mentions += 1

        utilization_rate = evidence_mentions / len(evidence)
        return min(1.0, utilization_rate + 0.3)  # 베이스라인 0.3 추가

    def _assess_originality(self, response: str) -> float:
        """독창성 평가"""
        # 독창적 표현 패턴
        creative_patterns = [
            "imagine",
            "envision",
            "what if",
            "alternatively",
            "innovatively",
        ]
        creativity_indicators = sum(
            0.15 for pattern in creative_patterns if pattern in response.lower()
        )

        # 어휘 다양성 (간단한 근사)
        words = response.lower().split()
        unique_words = len(set(words))
        diversity = unique_words / max(len(words), 1) if words else 0

        originality_score = min(1.0, creativity_indicators + diversity * 0.5)
        return max(0.2, originality_score)

    def _assess_thinking_flexibility(self, response: str) -> float:
        """사고 유연성 평가"""
        # 다양한 관점 제시
        perspective_indicators = [
            "on the other hand",
            "alternatively",
            "another way",
            "different approach",
        ]
        flexibility_score = sum(
            0.2 for indicator in perspective_indicators if indicator in response.lower()
        )

        # 질문 활용 (유연한 사고의 지표)
        question_count = response.count("?")
        question_score = min(0.4, question_count * 0.1)

        return min(1.0, max(0.3, flexibility_score + question_score))

    def _assess_idea_elaboration(self, response: str) -> float:
        """아이디어 정교화 평가"""
        # 응답 길이와 구조
        word_count = len(response.split())
        length_score = min(0.5, word_count / 200)  # 200단어 기준으로 0.5점

        # 세부 설명 정도
        detail_indicators = [
            "specifically",
            "in detail",
            "furthermore",
            "moreover",
            "additionally",
        ]
        detail_score = sum(
            0.1 for indicator in detail_indicators if indicator in response.lower()
        )

        elaboration_score = length_score + detail_score
        return min(1.0, max(0.2, elaboration_score))

    def _assess_creative_connections(
        self, response: str, context: Dict[str, Any]
    ) -> float:
        """창의적 연결성 평가"""
        # 비유와 은유 사용
        metaphor_indicators = [
            "like",
            "as if",
            "similar to",
            "analogous to",
            "comparable to",
        ]
        metaphor_score = sum(
            0.15 for indicator in metaphor_indicators if indicator in response.lower()
        )

        # 도메인 간 연결 (키워드 기반 추정)
        cross_domain_keywords = [
            "combine",
            "integrate",
            "merge",
            "synthesize",
            "connect",
        ]
        connection_score = sum(
            0.1 for keyword in cross_domain_keywords if keyword in response.lower()
        )

        return min(1.0, max(0.3, metaphor_score + connection_score))

    # === 기타 평가 메서드들 (간소화) ===

    def _assess_pattern_recognition(self, response: str) -> float:
        """패턴 인식 평가 (간소화)"""
        pattern_words = ["pattern", "trend", "recurring", "consistent", "systematic"]
        score = sum(0.2 for word in pattern_words if word in response.lower())
        return min(1.0, max(0.4, score))

    def _assess_data_interpretation(
        self, response: str, evidence: List[Dict[str, Any]]
    ) -> float:
        """데이터 해석 평가 (간소화)"""
        interpretation_words = [
            "indicates",
            "suggests",
            "implies",
            "demonstrates",
            "reveals",
        ]
        score = sum(0.15 for word in interpretation_words if word in response.lower())
        evidence_bonus = 0.2 if evidence else 0.0
        return min(1.0, max(0.3, score + evidence_bonus))

    def _assess_systematic_breakdown(self, response: str) -> float:
        """체계적 분해 평가 (간소화)"""
        structure_indicators = ["first", "second", "next", "finally", "step", "phase"]
        score = sum(
            0.1 for indicator in structure_indicators if indicator in response.lower()
        )
        return min(1.0, max(0.4, score))

    def _assess_critical_thinking(self, response: str) -> float:
        """비판적 사고 평가 (간소화)"""
        critical_words = [
            "question",
            "challenge",
            "examine",
            "evaluate",
            "assess",
            "critique",
        ]
        score = sum(0.15 for word in critical_words if word in response.lower())
        return min(1.0, max(0.3, score))

    # === 간소화된 다른 차원 평가들 ===

    def _assess_emotion_recognition(
        self, response: str, context: Dict[str, Any]
    ) -> float:
        emotion_words = ["feel", "emotion", "mood", "sentiment", "empathy"]
        return min(
            1.0,
            max(0.3, sum(0.2 for word in emotion_words if word in response.lower())),
        )

    def _assess_emotion_regulation(self, response: str) -> float:
        regulation_words = ["calm", "balanced", "measured", "thoughtful", "composed"]
        return min(
            1.0,
            max(
                0.4, sum(0.15 for word in regulation_words if word in response.lower())
            ),
        )

    def _assess_empathy(self, response: str, context: Dict[str, Any]) -> float:
        empathy_words = [
            "understand",
            "perspective",
            "viewpoint",
            "consider",
            "appreciate",
        ]
        return min(
            1.0,
            max(0.4, sum(0.15 for word in empathy_words if word in response.lower())),
        )

    def _assess_social_awareness(self, response: str, context: Dict[str, Any]) -> float:
        social_words = ["community", "society", "social", "cultural", "interpersonal"]
        return min(
            1.0,
            max(0.3, sum(0.15 for word in social_words if word in response.lower())),
        )

    def _assess_long_term_thinking(self, response: str) -> float:
        future_words = [
            "future",
            "long-term",
            "sustainability",
            "legacy",
            "consequences",
        ]
        return min(
            1.0, max(0.3, sum(0.2 for word in future_words if word in response.lower()))
        )

    def _assess_goal_setting(self, response: str, context: Dict[str, Any]) -> float:
        goal_words = ["objective", "target", "aim", "purpose", "mission"]
        return min(
            1.0, max(0.4, sum(0.15 for word in goal_words if word in response.lower()))
        )

    def _assess_resource_optimization(
        self, response: str, context: Dict[str, Any]
    ) -> float:
        optimization_words = [
            "efficient",
            "optimize",
            "resource",
            "maximize",
            "minimize",
        ]
        return min(
            1.0,
            max(
                0.3,
                sum(0.15 for word in optimization_words if word in response.lower()),
            ),
        )

    def _assess_risk_management(self, response: str) -> float:
        risk_words = ["risk", "uncertainty", "potential", "mitigation", "contingency"]
        return min(
            1.0, max(0.4, sum(0.15 for word in risk_words if word in response.lower()))
        )

    def _assess_cross_domain_integration(self, response: str) -> float:
        integration_words = ["integrate", "combine", "synthesize", "merge", "holistic"]
        return min(
            1.0,
            max(
                0.3, sum(0.2 for word in integration_words if word in response.lower())
            ),
        )

    def _assess_holistic_perspective(
        self, response: str, context: Dict[str, Any]
    ) -> float:
        holistic_words = ["overall", "comprehensive", "complete", "entire", "whole"]
        return min(
            1.0,
            max(0.4, sum(0.15 for word in holistic_words if word in response.lower())),
        )

    def _assess_complexity_management(self, response: str) -> float:
        complexity_words = [
            "complex",
            "sophisticated",
            "nuanced",
            "multifaceted",
            "intricate",
        ]
        return min(
            1.0,
            max(
                0.3, sum(0.15 for word in complexity_words if word in response.lower())
            ),
        )

    def _assess_emergent_insights(self, response: str) -> float:
        emergence_words = [
            "insight",
            "revelation",
            "breakthrough",
            "discovery",
            "realization",
        ]
        return min(
            1.0,
            max(0.2, sum(0.2 for word in emergence_words if word in response.lower())),
        )

    def _assess_context_adaptation(
        self, response: str, context: Dict[str, Any]
    ) -> float:
        # 맥락에 맞는 키워드 사용 여부 등을 체크 (간소화)
        return 0.7  # 기본값

    def _assess_learning_ability(self, response: str) -> float:
        learning_words = ["learn", "improve", "develop", "evolve", "adapt"]
        return min(
            1.0,
            max(0.4, sum(0.15 for word in learning_words if word in response.lower())),
        )

    def _assess_adaptive_flexibility(self, response: str) -> float:
        flexibility_words = [
            "flexible",
            "adaptable",
            "versatile",
            "adjustable",
            "malleable",
        ]
        return min(
            1.0,
            max(
                0.3, sum(0.2 for word in flexibility_words if word in response.lower())
            ),
        )

    def _assess_resilience(self, response: str, context: Dict[str, Any]) -> float:
        resilience_words = [
            "resilient",
            "robust",
            "persistent",
            "endurance",
            "recovery",
        ]
        return min(
            1.0,
            max(
                0.4, sum(0.15 for word in resilience_words if word in response.lower())
            ),
        )

    def _assess_self_awareness(self, response: str, context: Dict[str, Any]) -> float:
        awareness_words = ["aware", "recognize", "understand", "acknowledge", "realize"]
        return min(
            1.0,
            max(0.3, sum(0.15 for word in awareness_words if word in response.lower())),
        )

    def _assess_meta_thinking(self, response: str) -> float:
        meta_words = ["thinking", "reasoning", "cognitive", "mental", "mindful"]
        return min(
            1.0, max(0.3, sum(0.15 for word in meta_words if word in response.lower()))
        )

    def _assess_cognitive_strategy_use(self, response: str) -> float:
        strategy_words = ["strategy", "approach", "method", "technique", "framework"]
        return min(
            1.0,
            max(0.4, sum(0.15 for word in strategy_words if word in response.lower())),
        )

    def _assess_reflection_ability(self, response: str) -> float:
        reflection_words = ["reflect", "consider", "ponder", "contemplate", "examine"]
        return min(
            1.0,
            max(0.3, sum(0.2 for word in reflection_words if word in response.lower())),
        )

    # === 유틸리티 메서드들 ===

    def _calculate_confidence(self, raw_score: float, dimension_type: str) -> float:
        """신뢰도 계산"""
        base_confidence = 0.8

        # 점수가 극단적일 때 신뢰도 조정
        if raw_score < 0.2 or raw_score > 0.9:
            confidence_penalty = 0.1
        else:
            confidence_penalty = 0.0

        # 차원별 신뢰도 조정
        dimension_adjustments = {
            "logical": 0.1,  # 논리는 더 객관적
            "creative": -0.1,  # 창의성은 더 주관적
            "analytical": 0.05,
            "emotional": -0.05,
            "strategic": 0.0,
            "synthetic": -0.1,
            "adaptive": 0.0,
            "meta_cognitive": -0.05,
        }

        adjustment = dimension_adjustments.get(dimension_type, 0.0)
        confidence = base_confidence + adjustment - confidence_penalty

        return max(0.1, min(0.95, confidence))

    def _default_intelligence_score(
        self, dimension: IntelligenceDimension
    ) -> IntelligenceScore:
        """기본 지능 점수"""
        return IntelligenceScore(
            dimension=dimension,
            raw_score=0.5,
            confidence=0.5,
            evidence_strength=0.3,
            improvement_potential=0.5,
            meta_evaluation={},
        )

    def _default_config(self) -> Dict[str, Any]:
        """기본 설정"""
        return {
            "evaluation_depth": EvaluationLevel.DEEP,
            "confidence_threshold": 0.6,
            "improvement_threshold": 0.3,
            "meta_evaluation_enabled": True,
        }

    def _initialize_dimension_weights(self) -> Dict[IntelligenceDimension, float]:
        """차원별 가중치 초기화"""
        return {
            IntelligenceDimension.LOGICAL: 1.0,
            IntelligenceDimension.CREATIVE: 0.9,
            IntelligenceDimension.ANALYTICAL: 1.1,
            IntelligenceDimension.EMOTIONAL: 0.8,
            IntelligenceDimension.STRATEGIC: 1.2,
            IntelligenceDimension.SYNTHETIC: 1.3,
            IntelligenceDimension.ADAPTIVE: 1.1,
            IntelligenceDimension.META_COGNITIVE: 1.4,
        }

    def _load_benchmark_scores(self) -> Dict[str, float]:
        """벤치마크 점수 로드"""
        return {
            "average_human": 0.5,
            "expert_human": 0.8,
            "gpt4_level": 0.75,
            "gpt5_target": 0.9,
        }

    def _initialize_meta_calibration(self) -> Dict[str, float]:
        """메타 보정 초기화"""
        return {
            "overconfidence_bias": 0.1,
            "underconfidence_bias": 0.05,
            "evaluation_noise": 0.02,
        }

    # === 메타 평가와 비교 분석 메서드들 (간소화) ===

    def _check_evaluation_consistency(
        self, evaluation: ComprehensiveEvaluation
    ) -> float:
        """평가 일관성 확인"""
        return 0.8  # 간소화된 구현

    def _assess_evaluation_depth(self, evaluation: ComprehensiveEvaluation) -> float:
        """평가 깊이 평가"""
        return 0.7  # 간소화된 구현

    def _detect_evaluation_bias(
        self, evaluation: ComprehensiveEvaluation
    ) -> Dict[str, float]:
        """평가 편향 탐지"""
        return {"optimism_bias": 0.1, "severity_bias": 0.05}  # 간소화

    def _assess_calibration_quality(self, evaluation: ComprehensiveEvaluation) -> float:
        """보정 품질 평가"""
        return 0.75  # 간소화

    def _suggest_evaluation_improvements(
        self, evaluation: ComprehensiveEvaluation
    ) -> List[str]:
        """평가 개선 제안"""
        return ["increase_evidence_collection", "improve_confidence_calibration"]

    def _analyze_trends(
        self, evaluations: List[ComprehensiveEvaluation]
    ) -> Dict[str, Any]:
        """트렌드 분석"""
        return {"trend": "improving"}  # 간소화

    def _analyze_consistency(self, evaluations: List[ComprehensiveEvaluation]) -> float:
        """일관성 분석"""
        return 0.8  # 간소화

    def _identify_growth_patterns(
        self, evaluations: List[ComprehensiveEvaluation]
    ) -> Dict[str, Any]:
        """성장 패턴 식별"""
        return {"pattern": "steady_improvement"}  # 간소화

    def _assess_performance_stability(
        self, evaluations: List[ComprehensiveEvaluation]
    ) -> float:
        """성능 안정성 평가"""
        return 0.75  # 간소화

    def _track_dimensional_evolution(
        self, evaluations: List[ComprehensiveEvaluation]
    ) -> Dict[str, List[float]]:
        """차원별 진화 추적"""
        return {}  # 간소화

    def _assess_context_sensitivity(
        self, response: str, context: Dict[str, Any]
    ) -> float:
        """맥락 민감도 평가"""
        return 0.7  # 간소화

    def _assess_uncertainty_handling(self, response: str) -> float:
        """불확실성 처리 평가"""
        uncertainty_words = ["uncertain", "possible", "might", "perhaps", "potentially"]
        return min(
            1.0,
            max(
                0.3, sum(0.15 for word in uncertainty_words if word in response.lower())
            ),
        )

    def _assess_improvement_orientation(self, response: str) -> float:
        """개선 지향성 평가"""
        improvement_words = ["improve", "better", "enhance", "optimize", "upgrade"]
        return min(
            1.0,
            max(
                0.4, sum(0.15 for word in improvement_words if word in response.lower())
            ),
        )

    def _get_improvement_actions(self, dimension: IntelligenceDimension) -> List[str]:
        """차원별 개선 액션"""
        action_map = {
            IntelligenceDimension.LOGICAL: [
                "practice_logical_reasoning",
                "study_formal_logic",
            ],
            IntelligenceDimension.CREATIVE: [
                "engage_in_brainstorming",
                "explore_diverse_perspectives",
            ],
            IntelligenceDimension.ANALYTICAL: [
                "practice_data_analysis",
                "study_analytical_frameworks",
            ],
            IntelligenceDimension.EMOTIONAL: [
                "practice_empathy",
                "study_emotional_patterns",
            ],
            IntelligenceDimension.STRATEGIC: [
                "practice_strategic_planning",
                "study_decision_theory",
            ],
            IntelligenceDimension.SYNTHETIC: [
                "practice_integration_exercises",
                "study_systems_thinking",
            ],
            IntelligenceDimension.ADAPTIVE: [
                "expose_to_varied_contexts",
                "practice_flexibility",
            ],
            IntelligenceDimension.META_COGNITIVE: [
                "practice_self_reflection",
                "study_metacognition",
            ],
        }
        return action_map.get(dimension, ["general_cognitive_training"])

    def _estimate_improvement_timeline(self, improvement_potential: float) -> str:
        """개선 일정 추정"""
        if improvement_potential > 0.7:
            return "long_term"  # 6개월 이상
        elif improvement_potential > 0.4:
            return "medium_term"  # 3-6개월
        else:
            return "short_term"  # 1-3개월
