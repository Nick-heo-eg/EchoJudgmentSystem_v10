import copy
from datetime import datetime
from typing import Dict, List, Any
from echo_engine.capsule_dataclasses import CapsuleBlueprint

"""
🎭 Capsule Optimizers
캡슐 최적화 로직들
"""




class CapsuleOptimizers:
    """캡슐 최적화 관련 로직들"""

    def __init__(self, component_contribution_calculator):
        self.component_contribution_calculator = component_contribution_calculator

    def optimize_capsule(
        self, capsule: CapsuleBlueprint, optimization_goals: Dict[str, float] = None
    ) -> CapsuleBlueprint:
        """캡슐 최적화"""
        optimization_goals = optimization_goals or {"overall_effectiveness": 0.85}

        # 최적화된 캡슐 생성
        optimized_capsule = copy.deepcopy(capsule)
        optimized_capsule.capsule_id = f"{capsule.capsule_id}_optimized"
        optimized_capsule.name = f"{capsule.name} (Optimized)"
        optimized_capsule.last_modified = datetime.now()
        optimized_capsule.version = f"{capsule.version}.opt"
        optimized_capsule.metadata["optimization_goals"] = optimization_goals
        optimized_capsule.metadata["optimized_from"] = capsule.capsule_id

        # 가중치 최적화
        self._optimize_component_weights(optimized_capsule, optimization_goals)

        # 블렌딩 규칙 최적화
        self._optimize_blending_rules(optimized_capsule, optimization_goals)

        # 성능 목표 업데이트
        optimized_capsule.performance_targets.update(optimization_goals)

        return optimized_capsule

    def _optimize_component_weights(
        self, capsule: CapsuleBlueprint, goals: Dict[str, float]
    ):
        """컴포넌트 가중치 최적화"""
        # 간단한 가중치 조정 알고리즘
        for goal_metric, target_value in goals.items():
            for component in capsule.components:
                contribution = self.component_contribution_calculator(
                    component, goal_metric
                )
                if contribution > 0.7 and component.weight < 0.9:
                    component.weight = min(1.0, component.weight + 0.1)
                elif contribution < 0.5 and component.weight > 0.3:
                    component.weight = max(0.1, component.weight - 0.1)

    def _optimize_blending_rules(
        self, capsule: CapsuleBlueprint, goals: Dict[str, float]
    ):
        """블렌딩 규칙 최적화"""
        # 목표에 따른 블렌딩 모드 조정
        if "adaptability" in goals and goals["adaptability"] > 0.8:
            capsule.blending_rules["mode"] = "adaptive_morphing"
            capsule.blending_rules["adaptation_rate"] = 0.5
        elif "stability" in goals and goals["stability"] > 0.8:
            capsule.blending_rules["mode"] = "weighted_average"
            capsule.blending_rules["stability_priority"] = 0.9
        elif "creative_fluidity" in goals and goals["creative_fluidity"] > 0.8:
            capsule.blending_rules["mode"] = "harmonic_fusion"
