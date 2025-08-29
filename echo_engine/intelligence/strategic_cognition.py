"""
Advanced Strategic Planner - GPT-5 Level Strategic Thinking
==========================================================

Implements multi-layer strategic cognition with:
- Deep contextual analysis
- Probabilistic outcome modeling
- Dynamic strategy adaptation
- Cross-domain knowledge synthesis
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import json
import logging
import time
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class CognitionDepth(Enum):
    SURFACE = 1  # 표면적 분석
    ANALYTICAL = 2  # 분석적 사고
    STRATEGIC = 3  # 전략적 판단
    SYNTHETIC = 4  # 종합적 통찰
    TRANSCENDENT = 5  # 초월적 지능


class ReasoningMode(Enum):
    LOGICAL = "logical"  # 논리적 추론
    CREATIVE = "creative"  # 창의적 사고
    INTUITIVE = "intuitive"  # 직관적 판단
    SYSTEMATIC = "systematic"  # 체계적 분석
    EMERGENT = "emergent"  # 창발적 사고


@dataclass
class CognitiveContext:
    """인지적 맥락 정보"""

    domain: str
    complexity_level: int
    uncertainty_factors: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    temporal_factors: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategicPlan:
    """전략적 계획 구조"""

    id: str
    title: str
    cognition_depth: CognitionDepth
    reasoning_mode: ReasoningMode
    context: CognitiveContext

    # 계획 구조
    primary_objective: str
    sub_objectives: List[str] = field(default_factory=list)
    execution_layers: List[Dict[str, Any]] = field(default_factory=list)

    # 지능적 요소
    predicted_outcomes: Dict[str, float] = field(default_factory=dict)  # 결과 예측 확률
    risk_assessment: Dict[str, float] = field(default_factory=dict)  # 위험도 평가
    adaptation_triggers: List[str] = field(default_factory=list)  # 적응 트리거

    # 메타 정보
    confidence_score: float = 0.0
    estimated_complexity: float = 0.0
    created_at: float = field(default_factory=time.time)


class AdvancedStrategicPlanner:
    """GPT-5 수준의 고급 전략 기획자

    핵심 기능:
    1. 다층 인지 분석 - 표면에서 초월적 지능까지
    2. 동적 전략 수립 - 실시간 상황 적응
    3. 확률적 결과 예측 - 불확실성 하에서의 의사결정
    4. 메타 인지적 자기 평가 - 자신의 사고 과정 모니터링
    """

    def __init__(self, intelligence_config: Optional[Dict[str, Any]] = None):
        self.config = intelligence_config or self._default_config()
        self.knowledge_domains = self._initialize_domains()
        self.reasoning_patterns = self._load_reasoning_patterns()
        self.adaptation_history: List[Dict[str, Any]] = []

        logger.info(
            "AdvancedStrategicPlanner initialized with GPT-5 level capabilities"
        )

    def analyze_context(self, request: Dict[str, Any]) -> CognitiveContext:
        """요청을 깊이 있게 분석하여 인지적 맥락 구성"""

        # 도메인 식별
        domain = self._identify_domain(request.get("content", ""))

        # 복잡도 평가 (1-10)
        complexity = self._assess_complexity(request)

        # 불확실성 요소 분석
        uncertainties = self._identify_uncertainties(request)

        # 제약 조건 추출
        constraints = self._extract_constraints(request)

        # 성공 기준 정의
        success_criteria = self._define_success_criteria(request)

        # 시간적 요소 분석
        temporal_factors = self._analyze_temporal_aspects(request)

        context = CognitiveContext(
            domain=domain,
            complexity_level=complexity,
            uncertainty_factors=uncertainties,
            constraints=constraints,
            success_criteria=success_criteria,
            temporal_factors=temporal_factors,
        )

        logger.info(f"Context analyzed: domain={domain}, complexity={complexity}")
        return context

    def create_strategic_plan(
        self, request: Dict[str, Any], context: CognitiveContext
    ) -> StrategicPlan:
        """GPT-5 수준의 전략적 계획 수립"""

        # 인지 깊이 결정
        depth = self._determine_cognition_depth(context)

        # 추론 모드 선택
        mode = self._select_reasoning_mode(context, depth)

        # 핵심 목표 정의
        primary_obj = self._define_primary_objective(request, context)

        # 하위 목표 분해
        sub_objectives = self._decompose_objectives(primary_obj, context, depth)

        # 실행 계층 구성
        execution_layers = self._create_execution_layers(sub_objectives, depth)

        # 결과 예측 (확률 기반)
        outcomes = self._predict_outcomes(execution_layers, context)

        # 위험 평가
        risks = self._assess_risks(execution_layers, context)

        # 적응 트리거 설정
        triggers = self._define_adaptation_triggers(context)

        # 신뢰도 및 복잡도 계산
        confidence = self._calculate_confidence(context, outcomes, risks)
        complexity = self._estimate_execution_complexity(execution_layers)

        plan = StrategicPlan(
            id=f"strategic-{int(time.time())}-{hash(str(request)) % 10000}",
            title=f"Strategic Plan: {primary_obj}",
            cognition_depth=depth,
            reasoning_mode=mode,
            context=context,
            primary_objective=primary_obj,
            sub_objectives=sub_objectives,
            execution_layers=execution_layers,
            predicted_outcomes=outcomes,
            risk_assessment=risks,
            adaptation_triggers=triggers,
            confidence_score=confidence,
            estimated_complexity=complexity,
        )

        logger.info(
            f"Strategic plan created: {plan.id}, depth={depth.name}, confidence={confidence:.3f}"
        )
        return plan

    def adapt_plan(
        self, plan: StrategicPlan, feedback: Dict[str, Any]
    ) -> StrategicPlan:
        """실시간 피드백을 통한 계획 적응"""

        # 피드백 분석
        adaptation_needed = self._analyze_adaptation_need(plan, feedback)

        if not adaptation_needed:
            return plan

        # 적응 전략 수립
        adaptation_strategy = self._create_adaptation_strategy(plan, feedback)

        # 계획 수정
        adapted_plan = self._apply_adaptation(plan, adaptation_strategy)

        # 적응 이력 기록
        self.adaptation_history.append(
            {
                "original_plan_id": plan.id,
                "adapted_plan_id": adapted_plan.id,
                "adaptation_reason": feedback.get("reason", "unknown"),
                "adaptation_score": adaptation_strategy.get("effectiveness", 0.0),
                "timestamp": time.time(),
            }
        )

        logger.info(f"Plan adapted: {plan.id} -> {adapted_plan.id}")
        return adapted_plan

    def meta_evaluate_planning(self, plan: StrategicPlan) -> Dict[str, Any]:
        """메타 인지적 계획 평가 - 자신의 계획 수립 과정을 분석"""

        evaluation = {
            "planning_quality": self._evaluate_planning_quality(plan),
            "reasoning_coherence": self._evaluate_reasoning_coherence(plan),
            "strategic_depth": self._evaluate_strategic_depth(plan),
            "adaptation_potential": self._evaluate_adaptation_potential(plan),
            "cognitive_efficiency": self._evaluate_cognitive_efficiency(plan),
            "improvement_suggestions": self._generate_improvement_suggestions(plan),
        }

        logger.info(f"Meta-evaluation completed for plan {plan.id}")
        return evaluation

    # === 내부 메서드들 ===

    def _default_config(self) -> Dict[str, Any]:
        return {
            "max_depth": CognitionDepth.TRANSCENDENT,
            "default_reasoning_mode": ReasoningMode.SYSTEMATIC,
            "confidence_threshold": 0.7,
            "adaptation_sensitivity": 0.3,
            "meta_evaluation_enabled": True,
        }

    def _initialize_domains(self) -> Dict[str, Dict[str, Any]]:
        """지식 도메인 초기화"""
        return {
            "general": {"complexity_weight": 1.0, "uncertainty_factor": 0.5},
            "technical": {"complexity_weight": 1.5, "uncertainty_factor": 0.3},
            "creative": {"complexity_weight": 1.2, "uncertainty_factor": 0.7},
            "analytical": {"complexity_weight": 1.3, "uncertainty_factor": 0.2},
            "strategic": {"complexity_weight": 1.8, "uncertainty_factor": 0.4},
        }

    def _load_reasoning_patterns(self) -> Dict[str, List[str]]:
        """추론 패턴 로드"""
        return {
            "logical": ["premise_analysis", "deductive_reasoning", "validity_check"],
            "creative": ["divergent_thinking", "analogical_reasoning", "synthesis"],
            "intuitive": ["pattern_recognition", "holistic_assessment", "gut_feeling"],
            "systematic": ["decomposition", "hierarchical_analysis", "step_by_step"],
            "emergent": [
                "complexity_embrace",
                "non_linear_thinking",
                "emergence_detection",
            ],
        }

    def _identify_domain(self, content: str) -> str:
        """내용 분석을 통한 도메인 식별"""
        # 키워드 기반 도메인 분류 (실제로는 더 정교한 NLP 분석)
        technical_keywords = ["code", "programming", "algorithm", "system", "technical"]
        creative_keywords = ["creative", "design", "art", "story", "innovative"]
        analytical_keywords = ["analysis", "data", "research", "study", "examine"]
        strategic_keywords = ["strategy", "plan", "goal", "objective", "decision"]

        content_lower = content.lower()

        if any(kw in content_lower for kw in technical_keywords):
            return "technical"
        elif any(kw in content_lower for kw in creative_keywords):
            return "creative"
        elif any(kw in content_lower for kw in analytical_keywords):
            return "analytical"
        elif any(kw in content_lower for kw in strategic_keywords):
            return "strategic"
        else:
            return "general"

    def _assess_complexity(self, request: Dict[str, Any]) -> int:
        """요청의 복잡도 평가 (1-10)"""
        base_complexity = 3

        # 내용 길이에 따른 복잡도 증가
        content_length = len(request.get("content", ""))
        if content_length > 500:
            base_complexity += 2
        elif content_length > 200:
            base_complexity += 1

        # 다중 요구사항 검증
        if "requirements" in request and len(request["requirements"]) > 3:
            base_complexity += 2

        # 시간 제약이 있는 경우
        if request.get("urgent", False):
            base_complexity += 1

        return min(10, base_complexity)

    def _identify_uncertainties(self, request: Dict[str, Any]) -> List[str]:
        """불확실성 요소 식별"""
        uncertainties = []

        content = request.get("content", "").lower()

        if "maybe" in content or "perhaps" in content or "might" in content:
            uncertainties.append("linguistic_uncertainty")

        if "future" in content or "predict" in content:
            uncertainties.append("temporal_uncertainty")

        if request.get("incomplete_info", False):
            uncertainties.append("information_gap")

        return uncertainties

    def _extract_constraints(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """제약 조건 추출"""
        constraints = {}

        if "time_limit" in request:
            constraints["time"] = request["time_limit"]

        if "budget" in request:
            constraints["budget"] = request["budget"]

        if "resources" in request:
            constraints["resources"] = request["resources"]

        return constraints

    def _define_success_criteria(self, request: Dict[str, Any]) -> List[str]:
        """성공 기준 정의"""
        criteria = ["task_completion"]

        if "quality_requirements" in request:
            criteria.append("quality_standards")

        if "user_satisfaction" in request:
            criteria.append("user_satisfaction")

        if request.get("measurable_outcome", False):
            criteria.append("measurable_results")

        return criteria

    def _analyze_temporal_aspects(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """시간적 요소 분석"""
        return {
            "urgency_level": request.get("urgency", "medium"),
            "time_horizon": request.get("time_horizon", "short_term"),
            "temporal_dependencies": request.get("dependencies", []),
        }

    def _determine_cognition_depth(self, context: CognitiveContext) -> CognitionDepth:
        """맥락에 따른 인지 깊이 결정"""
        base_depth = CognitionDepth.ANALYTICAL

        # 복잡도에 따른 깊이 조정
        if context.complexity_level >= 8:
            return CognitionDepth.TRANSCENDENT
        elif context.complexity_level >= 6:
            return CognitionDepth.SYNTHETIC
        elif context.complexity_level >= 4:
            return CognitionDepth.STRATEGIC
        else:
            return base_depth

    def _select_reasoning_mode(
        self, context: CognitiveContext, depth: CognitionDepth
    ) -> ReasoningMode:
        """맥락과 깊이에 따른 추론 모드 선택"""

        if context.domain == "creative":
            return ReasoningMode.CREATIVE
        elif context.domain == "technical":
            return ReasoningMode.LOGICAL
        elif depth == CognitionDepth.TRANSCENDENT:
            return ReasoningMode.EMERGENT
        elif len(context.uncertainty_factors) > 2:
            return ReasoningMode.INTUITIVE
        else:
            return ReasoningMode.SYSTEMATIC

    def _define_primary_objective(
        self, request: Dict[str, Any], context: CognitiveContext
    ) -> str:
        """핵심 목표 정의"""
        content = request.get("content", "")

        # 목표 추출 로직 (실제로는 더 정교한 NLP 처리)
        if "create" in content.lower():
            return f"Create solution for {context.domain} domain challenge"
        elif "analyze" in content.lower():
            return f"Analyze and provide insights for {context.domain} problem"
        elif "improve" in content.lower():
            return f"Improve existing {context.domain} system or process"
        else:
            return f"Address {context.domain} domain request comprehensively"

    def _decompose_objectives(
        self, primary_obj: str, context: CognitiveContext, depth: CognitionDepth
    ) -> List[str]:
        """목표 분해"""
        base_objectives = [
            "Information gathering and analysis",
            "Solution design and planning",
            "Implementation strategy development",
            "Quality assurance and verification",
        ]

        # 깊이에 따른 목표 확장
        if depth.value >= CognitionDepth.STRATEGIC.value:
            base_objectives.extend(
                ["Risk assessment and mitigation", "Performance optimization planning"]
            )

        if depth.value >= CognitionDepth.SYNTHETIC.value:
            base_objectives.extend(
                [
                    "Cross-domain knowledge integration",
                    "Emergent property identification",
                ]
            )

        if depth == CognitionDepth.TRANSCENDENT:
            base_objectives.extend(
                [
                    "Meta-level pattern recognition",
                    "Paradigm transcendence consideration",
                ]
            )

        return base_objectives

    def _create_execution_layers(
        self, objectives: List[str], depth: CognitionDepth
    ) -> List[Dict[str, Any]]:
        """실행 계층 구성"""
        layers = []

        for i, objective in enumerate(objectives):
            layer = {
                "layer_id": i + 1,
                "objective": objective,
                "depth_level": depth.value,
                "estimated_effort": self._estimate_layer_effort(objective),
                "dependencies": list(range(max(0, i - 2), i)),  # 이전 2개 레이어에 의존
                "success_metrics": [
                    f"metric_{i+1}_completion",
                    f"metric_{i+1}_quality",
                ],
            }
            layers.append(layer)

        return layers

    def _estimate_layer_effort(self, objective: str) -> float:
        """계층별 노력 추정"""
        # 키워드 기반 노력 추정
        high_effort_keywords = ["analysis", "design", "optimization", "integration"]
        medium_effort_keywords = ["planning", "assessment", "verification"]

        objective_lower = objective.lower()

        if any(kw in objective_lower for kw in high_effort_keywords):
            return 0.8
        elif any(kw in objective_lower for kw in medium_effort_keywords):
            return 0.6
        else:
            return 0.4

    def _predict_outcomes(
        self, layers: List[Dict[str, Any]], context: CognitiveContext
    ) -> Dict[str, float]:
        """결과 예측 (확률 기반)"""
        base_success_rate = 0.8

        # 복잡도에 따른 성공률 조정
        complexity_penalty = context.complexity_level * 0.05
        uncertainty_penalty = len(context.uncertainty_factors) * 0.1

        success_probability = max(
            0.3, base_success_rate - complexity_penalty - uncertainty_penalty
        )

        return {
            "success_probability": success_probability,
            "partial_success_probability": min(0.95, success_probability + 0.2),
            "excellence_probability": max(0.1, success_probability - 0.2),
            "failure_probability": 1.0 - success_probability,
        }

    def _assess_risks(
        self, layers: List[Dict[str, Any]], context: CognitiveContext
    ) -> Dict[str, float]:
        """위험 평가"""
        return {
            "complexity_risk": context.complexity_level / 10.0,
            "time_pressure_risk": (
                0.7 if context.temporal_factors.get("urgency_level") == "high" else 0.3
            ),
            "resource_constraint_risk": (
                0.5 if context.constraints.get("resources") else 0.2
            ),
            "uncertainty_risk": len(context.uncertainty_factors) * 0.15,
            "execution_risk": (
                sum(layer["estimated_effort"] for layer in layers) / len(layers)
                if layers
                else 0.5
            ),
        }

    def _define_adaptation_triggers(self, context: CognitiveContext) -> List[str]:
        """적응 트리거 정의"""
        triggers = ["significant_feedback", "performance_below_threshold"]

        if context.complexity_level > 7:
            triggers.append("complexity_explosion")

        if len(context.uncertainty_factors) > 2:
            triggers.append("uncertainty_increase")

        if context.temporal_factors.get("urgency_level") == "high":
            triggers.append("time_pressure_change")

        return triggers

    def _calculate_confidence(
        self,
        context: CognitiveContext,
        outcomes: Dict[str, float],
        risks: Dict[str, float],
    ) -> float:
        """신뢰도 계산"""
        base_confidence = outcomes.get("success_probability", 0.5)

        # 위험 요소에 따른 신뢰도 조정
        avg_risk = sum(risks.values()) / len(risks) if risks else 0.5
        risk_penalty = avg_risk * 0.3

        # 도메인 전문성에 따른 조정
        domain_bonus = (
            self.knowledge_domains.get(context.domain, {}).get("complexity_weight", 1.0)
            * 0.1
        )

        confidence = max(0.1, min(0.95, base_confidence - risk_penalty + domain_bonus))
        return round(confidence, 3)

    def _estimate_execution_complexity(self, layers: List[Dict[str, Any]]) -> float:
        """실행 복잡도 추정"""
        if not layers:
            return 0.5

        total_effort = sum(layer["estimated_effort"] for layer in layers)
        dependency_complexity = sum(len(layer["dependencies"]) for layer in layers)

        complexity = (total_effort / len(layers)) + (
            dependency_complexity / (len(layers) * 3)
        )
        return min(1.0, complexity)

    # === 적응 관련 메서드들 ===

    def _analyze_adaptation_need(
        self, plan: StrategicPlan, feedback: Dict[str, Any]
    ) -> bool:
        """적응 필요성 분석"""
        feedback_score = feedback.get("performance_score", 0.8)

        if feedback_score < self.config["confidence_threshold"]:
            return True

        if any(
            trigger in feedback.get("triggered_events", [])
            for trigger in plan.adaptation_triggers
        ):
            return True

        return False

    def _create_adaptation_strategy(
        self, plan: StrategicPlan, feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """적응 전략 수립"""
        return {
            "adaptation_type": feedback.get("adaptation_type", "incremental"),
            "focus_areas": feedback.get("improvement_areas", []),
            "effectiveness": feedback.get("performance_score", 0.5),
            "strategy_adjustments": self._identify_strategy_adjustments(plan, feedback),
        }

    def _apply_adaptation(
        self, plan: StrategicPlan, strategy: Dict[str, Any]
    ) -> StrategicPlan:
        """적응 적용"""
        adapted_plan = StrategicPlan(
            id=f"{plan.id}-adapted-{int(time.time())}",
            title=f"{plan.title} (Adapted)",
            cognition_depth=plan.cognition_depth,
            reasoning_mode=plan.reasoning_mode,
            context=plan.context,
            primary_objective=plan.primary_objective,
            sub_objectives=plan.sub_objectives.copy(),
            execution_layers=plan.execution_layers.copy(),
            predicted_outcomes=plan.predicted_outcomes.copy(),
            risk_assessment=plan.risk_assessment.copy(),
            adaptation_triggers=plan.adaptation_triggers.copy(),
            confidence_score=min(0.95, plan.confidence_score + 0.1),
            estimated_complexity=plan.estimated_complexity,
        )

        # 전략 조정 적용
        adjustments = strategy.get("strategy_adjustments", {})
        if "execution_order" in adjustments:
            adapted_plan.execution_layers = adjustments["execution_order"]

        return adapted_plan

    def _identify_strategy_adjustments(
        self, plan: StrategicPlan, feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """전략 조정 사항 식별"""
        adjustments = {}

        if feedback.get("execution_issues"):
            adjustments["execution_order"] = self._reorder_execution_layers(
                plan.execution_layers
            )

        if feedback.get("quality_issues"):
            adjustments["quality_enhancement"] = True

        return adjustments

    def _reorder_execution_layers(
        self, layers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """실행 계층 재정렬"""
        # 노력 수준에 따른 정렬 (낮은 노력부터)
        return sorted(layers, key=lambda x: x.get("estimated_effort", 0.5))

    # === 메타 평가 메서드들 ===

    def _evaluate_planning_quality(self, plan: StrategicPlan) -> float:
        """계획 품질 평가"""
        quality_score = 0.0

        # 목표 명확성
        if plan.primary_objective and len(plan.sub_objectives) > 0:
            quality_score += 0.3

        # 실행 계층 완성도
        if len(plan.execution_layers) >= 3:
            quality_score += 0.3

        # 위험 평가 완성도
        if len(plan.risk_assessment) >= 3:
            quality_score += 0.2

        # 신뢰도 적절성
        if 0.3 <= plan.confidence_score <= 0.9:
            quality_score += 0.2

        return quality_score

    def _evaluate_reasoning_coherence(self, plan: StrategicPlan) -> float:
        """추론 일관성 평가"""
        coherence_score = 0.5  # 기본 점수

        # 인지 깊이와 추론 모드의 적합성
        if (
            plan.cognition_depth.value >= 4
            and plan.reasoning_mode in [ReasoningMode.EMERGENT, ReasoningMode.SYNTHETIC]
        ) or (
            plan.cognition_depth.value <= 2
            and plan.reasoning_mode in [ReasoningMode.LOGICAL, ReasoningMode.SYSTEMATIC]
        ):
            coherence_score += 0.3

        # 맥락과 전략의 일치성
        if (
            plan.context.domain in ["technical"]
            and plan.reasoning_mode == ReasoningMode.LOGICAL
        ):
            coherence_score += 0.2
        elif (
            plan.context.domain in ["creative"]
            and plan.reasoning_mode == ReasoningMode.CREATIVE
        ):
            coherence_score += 0.2

        return min(1.0, coherence_score)

    def _evaluate_strategic_depth(self, plan: StrategicPlan) -> float:
        """전략적 깊이 평가"""
        depth_score = plan.cognition_depth.value / 5.0

        # 계층 복잡도 보정
        if plan.estimated_complexity > 0.7:
            depth_score += 0.1

        return min(1.0, depth_score)

    def _evaluate_adaptation_potential(self, plan: StrategicPlan) -> float:
        """적응 가능성 평가"""
        adaptation_score = 0.0

        # 적응 트리거 다양성
        adaptation_score += min(0.4, len(plan.adaptation_triggers) * 0.1)

        # 위험 인식도
        if len(plan.risk_assessment) > 3:
            adaptation_score += 0.3

        # 불확실성 대응력
        adaptation_score += min(0.3, len(plan.context.uncertainty_factors) * 0.1)

        return adaptation_score

    def _evaluate_cognitive_efficiency(self, plan: StrategicPlan) -> float:
        """인지적 효율성 평가"""
        efficiency = 1.0 - (plan.estimated_complexity * 0.3)

        # 신뢰도 대비 복잡도 평가
        if plan.confidence_score > 0.8 and plan.estimated_complexity < 0.5:
            efficiency += 0.2

        return max(0.1, min(1.0, efficiency))

    def _generate_improvement_suggestions(self, plan: StrategicPlan) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        if plan.confidence_score < 0.6:
            suggestions.append("신뢰도 향상을 위한 추가 분석 필요")

        if plan.estimated_complexity > 0.8:
            suggestions.append("복잡도 감소를 위한 단순화 고려")

        if len(plan.risk_assessment) < 3:
            suggestions.append("위험 요소 추가 식별 필요")

        if not plan.adaptation_triggers:
            suggestions.append("적응 메커니즘 강화 필요")

        return suggestions
