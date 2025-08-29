from datetime import datetime
from typing import Dict, Any
import numpy as np
from echo_engine.capsule_types import CapsuleComplexity
from echo_engine.capsule_dataclasses import CapsuleBlueprint, CapsuleSimulationResult

"""
🎭 Capsule Simulators
캡슐 시뮬레이션 및 성능 분석 로직들
"""




class CapsuleSimulators:
    """캡슐 시뮬레이션 관련 로직들"""

    def __init__(self, performance_predictor):
        self.performance_predictor = performance_predictor

    def simulate_capsule_performance(
        self,
        capsule: CapsuleBlueprint,
        scenario_name: str = "default",
        simulation_params: Dict[str, Any] = None,
    ) -> CapsuleSimulationResult:
        """캡슐 성능 시뮬레이션"""
        simulation_params = simulation_params or {}

        start_time = datetime.now()
        simulation_id = f"sim_{capsule.capsule_id}_{int(start_time.timestamp())}"

        # 성능 메트릭 시뮬레이션
        performance_metrics = self.performance_predictor(capsule)

        # 행동 패턴 시뮬레이션
        behavioral_patterns = self._simulate_behavioral_patterns(capsule, scenario_name)

        # 리소스 사용량 시뮬레이션
        resource_usage = self._simulate_resource_usage(capsule)

        # 안정성 점수 계산
        stability_score = self._calculate_stability_score(capsule, performance_metrics)

        # 적응성 점수 계산
        adaptability_score = self._calculate_adaptability_score(
            capsule, behavioral_patterns
        )

        execution_time = (datetime.now() - start_time).total_seconds() * 1000

        return CapsuleSimulationResult(
            simulation_id=simulation_id,
            capsule_id=capsule.capsule_id,
            scenario_name=scenario_name,
            performance_metrics=performance_metrics,
            behavioral_patterns=behavioral_patterns,
            resource_usage=resource_usage,
            execution_time_ms=execution_time,
            stability_score=stability_score,
            adaptability_score=adaptability_score,
            timestamp=datetime.now(),
        )

    def _simulate_behavioral_patterns(
        self, capsule: CapsuleBlueprint, scenario: str
    ) -> Dict[str, Any]:
        """행동 패턴 시뮬레이션"""
        patterns = {
            "response_style": "balanced",
            "decision_making": "analytical",
            "interaction_preference": "collaborative",
            "adaptation_strategy": "gradual",
            "creative_approach": "systematic",
        }

        # 컴포넌트 영향 적용
        for component in capsule.components:
            if component.component_type == "signature":
                if "aurora" in component.component_id:
                    patterns["response_style"] = "empathetic"
                    patterns["interaction_preference"] = "nurturing"
                elif "phoenix" in component.component_id:
                    patterns["adaptation_strategy"] = "transformative"
                    patterns["creative_approach"] = "innovative"
                elif "sage" in component.component_id:
                    patterns["decision_making"] = "wisdom_based"
                    patterns["response_style"] = "analytical"

            elif component.component_type == "emotion":
                if "empathy" in component.name.lower():
                    patterns["interaction_preference"] = "empathetic"
                elif "creativity" in component.name.lower():
                    patterns["creative_approach"] = "intuitive"

            elif component.component_type == "cognitive":
                patterns["decision_making"] = "systematic"
                patterns["response_style"] = "logical"

        return patterns

    def _simulate_resource_usage(self, capsule: CapsuleBlueprint) -> Dict[str, float]:
        """리소스 사용량 시뮬레이션"""
        base_usage = {"memory": 0.5, "processing": 0.4, "network": 0.3, "storage": 0.2}

        # 복잡도에 따른 리소스 사용량 증가
        complexity_multiplier = {
            CapsuleComplexity.SIMPLE: 0.8,
            CapsuleComplexity.MODERATE: 1.0,
            CapsuleComplexity.COMPLEX: 1.3,
            CapsuleComplexity.ADVANCED: 1.6,
        }.get(capsule.complexity, 1.0)

        # 컴포넌트 수에 따른 추가 사용량
        component_factor = 1.0 + (len(capsule.components) - 1) * 0.1

        usage = {}
        for resource, base_value in base_usage.items():
            usage[resource] = min(
                1.0, base_value * complexity_multiplier * component_factor
            )

        return usage

    def _calculate_stability_score(
        self, capsule: CapsuleBlueprint, performance: Dict[str, float]
    ) -> float:
        """안정성 점수 계산"""
        # 성능 메트릭의 표준편차로 안정성 측정
        performance_values = list(performance.values())
        if not performance_values:
            return 0.5

        std_dev = np.std(performance_values)
        stability = max(0.0, 1.0 - std_dev)

        # 블렌딩 모드에 따른 조정
        blending_stability = capsule.blending_rules.get("stability_priority", 0.7)

        return (stability + blending_stability) / 2

    def _calculate_adaptability_score(
        self, capsule: CapsuleBlueprint, patterns: Dict[str, Any]
    ) -> float:
        """적응성 점수 계산"""
        adaptability = 0.6  # 기본 점수

        # 적응 관련 패턴 확인
        if patterns.get("adaptation_strategy") == "transformative":
            adaptability += 0.2
        elif patterns.get("adaptation_strategy") == "gradual":
            adaptability += 0.1

        # 창조성 접근법에 따른 보정
        if patterns.get("creative_approach") == "innovative":
            adaptability += 0.1

        # 의사결정 스타일에 따른 보정
        if patterns.get("decision_making") == "flexible":
            adaptability += 0.1

        return min(1.0, adaptability)
