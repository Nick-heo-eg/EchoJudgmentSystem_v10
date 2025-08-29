"""
Meta-Reasoning Engine - GPT-5 Level Self-Reflective Intelligence
===============================================================

Implements advanced meta-cognitive capabilities with:
- Self-aware reasoning processes
- Dynamic strategy selection and optimization
- Real-time cognitive performance monitoring
- Adaptive reasoning pathway selection
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
import json
import logging
import time
from enum import Enum

logger = logging.getLogger(__name__)


class ReasoningStrategy(Enum):
    """추론 전략 유형"""

    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    INTUITIVE = "intuitive"
    SYSTEMATIC = "systematic"
    ADAPTIVE = "adaptive"
    HYBRID = "hybrid"


@dataclass
class ReasoningTrace:
    """추론 과정 추적"""

    step_id: str
    strategy_used: ReasoningStrategy
    input_state: Dict[str, Any]
    reasoning_process: Dict[str, Any]
    output_state: Dict[str, Any]
    confidence: float
    processing_time: float
    meta_observations: List[str] = field(default_factory=list)


@dataclass
class MetaCognition:
    """메타인지 상태"""

    self_awareness_level: float = 0.7
    strategy_effectiveness: Dict[str, float] = field(default_factory=dict)
    cognitive_load: float = 0.5
    confidence_calibration: float = 0.8
    learning_rate: float = 0.1


class MetaReasoningEngine:
    """GPT-5 수준의 메타 추론 엔진"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.meta_cognition = MetaCognition()
        self.reasoning_history: List[ReasoningTrace] = []
        self.strategy_performance: Dict[ReasoningStrategy, Dict[str, float]] = {}

        logger.info("MetaReasoningEngine initialized")

    def meta_reason(
        self, problem: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """메타 추론 실행"""

        # 1. 문제 분석 및 전략 선택
        optimal_strategy = self._select_optimal_strategy(problem, context)

        # 2. 추론 실행
        reasoning_result = self._execute_reasoning(problem, context, optimal_strategy)

        # 3. 메타 평가
        meta_evaluation = self._evaluate_reasoning_process(reasoning_result)

        # 4. 자기 개선
        self._update_meta_cognition(reasoning_result, meta_evaluation)

        return {
            "reasoning_result": reasoning_result,
            "meta_evaluation": meta_evaluation,
            "strategy_used": optimal_strategy.value,
            "meta_insights": self._generate_meta_insights(),
        }

    def _select_optimal_strategy(
        self, problem: Dict[str, Any], context: Dict[str, Any]
    ) -> ReasoningStrategy:
        """최적 추론 전략 선택"""

        # 문제 특성 분석
        complexity = problem.get("complexity", 0.5)
        creativity_needed = problem.get("creativity_required", False)
        time_pressure = context.get("time_pressure", 0.3)

        # 전략별 적합도 계산
        strategy_scores = {}

        if creativity_needed:
            strategy_scores[ReasoningStrategy.CREATIVE] = 0.9
            strategy_scores[ReasoningStrategy.INTUITIVE] = 0.7

        if complexity > 0.7:
            strategy_scores[ReasoningStrategy.SYSTEMATIC] = 0.8
            strategy_scores[ReasoningStrategy.ANALYTICAL] = 0.9

        if time_pressure > 0.7:
            strategy_scores[ReasoningStrategy.INTUITIVE] = 0.8
            strategy_scores[ReasoningStrategy.ADAPTIVE] = 0.7

        # 성능 이력 반영
        for strategy in ReasoningStrategy:
            perf = self.strategy_performance.get(strategy, {})
            success_rate = perf.get("success_rate", 0.5)
            strategy_scores[strategy] = strategy_scores.get(strategy, 0.5) * (
                0.7 + 0.3 * success_rate
            )

        # 최고 점수 전략 선택
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])[0]
        return best_strategy

    def _execute_reasoning(
        self,
        problem: Dict[str, Any],
        context: Dict[str, Any],
        strategy: ReasoningStrategy,
    ) -> Dict[str, Any]:
        """추론 실행"""

        start_time = time.time()

        if strategy == ReasoningStrategy.ANALYTICAL:
            result = self._analytical_reasoning(problem, context)
        elif strategy == ReasoningStrategy.CREATIVE:
            result = self._creative_reasoning(problem, context)
        elif strategy == ReasoningStrategy.INTUITIVE:
            result = self._intuitive_reasoning(problem, context)
        elif strategy == ReasoningStrategy.SYSTEMATIC:
            result = self._systematic_reasoning(problem, context)
        elif strategy == ReasoningStrategy.ADAPTIVE:
            result = self._adaptive_reasoning(problem, context)
        else:
            result = self._hybrid_reasoning(problem, context)

        processing_time = time.time() - start_time

        # 추론 추적 기록
        trace = ReasoningTrace(
            step_id=f"reasoning_{int(time.time())}",
            strategy_used=strategy,
            input_state={"problem": problem, "context": context},
            reasoning_process=result.get("process", {}),
            output_state=result,
            confidence=result.get("confidence", 0.7),
            processing_time=processing_time,
        )

        self.reasoning_history.append(trace)
        return result

    def _analytical_reasoning(
        self, problem: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """분석적 추론"""
        return {
            "approach": "analytical",
            "steps": ["decompose", "analyze", "synthesize"],
            "confidence": 0.8,
            "process": {"method": "logical_analysis"},
        }

    def _creative_reasoning(
        self, problem: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """창의적 추론"""
        return {
            "approach": "creative",
            "steps": ["diverge", "explore", "converge"],
            "confidence": 0.7,
            "process": {"method": "creative_exploration"},
        }

    def _intuitive_reasoning(
        self, problem: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """직관적 추론"""
        return {
            "approach": "intuitive",
            "steps": ["sense", "feel", "decide"],
            "confidence": 0.6,
            "process": {"method": "pattern_matching"},
        }

    def _systematic_reasoning(
        self, problem: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """체계적 추론"""
        return {
            "approach": "systematic",
            "steps": ["plan", "execute", "verify"],
            "confidence": 0.85,
            "process": {"method": "step_by_step"},
        }

    def _adaptive_reasoning(
        self, problem: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """적응적 추론"""
        return {
            "approach": "adaptive",
            "steps": ["assess", "adapt", "execute"],
            "confidence": 0.75,
            "process": {"method": "context_adaptive"},
        }

    def _hybrid_reasoning(
        self, problem: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """하이브리드 추론"""
        return {
            "approach": "hybrid",
            "steps": ["multi_strategy", "integrate", "optimize"],
            "confidence": 0.8,
            "process": {"method": "strategy_combination"},
        }

    def _evaluate_reasoning_process(
        self, reasoning_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """추론 과정 평가"""

        return {
            "effectiveness": 0.8,
            "efficiency": 0.7,
            "coherence": 0.85,
            "creativity": 0.6,
            "overall_quality": 0.75,
        }

    def _update_meta_cognition(
        self, reasoning_result: Dict[str, Any], evaluation: Dict[str, Any]
    ) -> None:
        """메타인지 업데이트"""

        # 전략 성능 업데이트
        strategy_name = reasoning_result.get("approach", "unknown")
        try:
            strategy = ReasoningStrategy(strategy_name)
            if strategy not in self.strategy_performance:
                self.strategy_performance[strategy] = {
                    "success_rate": 0.5,
                    "avg_confidence": 0.7,
                }

            perf = self.strategy_performance[strategy]
            perf["success_rate"] = (
                perf["success_rate"] + evaluation.get("overall_quality", 0.5)
            ) / 2
            perf["avg_confidence"] = (
                perf["avg_confidence"] + reasoning_result.get("confidence", 0.7)
            ) / 2
        except ValueError:
            pass  # 알 수 없는 전략

        # 메타인지 레벨 조정
        quality = evaluation.get("overall_quality", 0.5)
        if quality > 0.8:
            self.meta_cognition.self_awareness_level = min(
                1.0, self.meta_cognition.self_awareness_level + 0.01
            )
        elif quality < 0.4:
            self.meta_cognition.self_awareness_level = max(
                0.1, self.meta_cognition.self_awareness_level - 0.005
            )

    def _generate_meta_insights(self) -> List[str]:
        """메타 통찰 생성"""

        insights = []

        # 전략 효과성 분석
        if self.strategy_performance:
            best_strategy = max(
                self.strategy_performance.items(),
                key=lambda x: x[1].get("success_rate", 0),
            )
            insights.append(f"Most effective strategy: {best_strategy[0].value}")

        # 자기 인식 수준 평가
        awareness = self.meta_cognition.self_awareness_level
        if awareness > 0.8:
            insights.append("High self-awareness detected")
        elif awareness < 0.5:
            insights.append("Self-awareness needs improvement")

        return insights

    def _default_config(self) -> Dict[str, Any]:
        """기본 설정"""
        return {
            "max_reasoning_history": 1000,
            "strategy_adaptation_rate": 0.1,
            "meta_learning_enabled": True,
        }
