from datetime import datetime
from typing import Dict, List, Any
import numpy as np
from echo_engine.capsule_dataclasses import (
    CapsuleData, CapsuleMetrics, CapsuleConfig
)

"""
🎭 Capsule Validators
캡슐 검증 및 성능 예측 로직들
"""

# Note: CapsuleComponent, CapsuleBlueprint, CapsuleValidationResult imports removed
# as they are not defined elsewhere


class CapsuleValidators:
    """캡슐 검증 관련 로직들"""

    def __init__(self, performance_benchmarks: Dict[str, Dict[str, float]]):
        self.performance_benchmarks = performance_benchmarks

    def validate_capsule(
        self, capsule: CapsuleBlueprint, force_revalidate: bool = False
    ) -> CapsuleValidationResult:
        """캡슐 검증"""
        # 검증 수행
        is_valid = True
        validation_score = 0.0
        component_compatibility = {}
        predicted_performance = {}
        warnings = []
        recommendations = []

        # 컴포넌트 호환성 검사
        for component in capsule.components:
            compatibility_score = self._check_component_compatibility(
                component, capsule.components
            )
            component_compatibility[component.component_id] = compatibility_score

            if compatibility_score < 0.6:
                is_valid = False
                warnings.append(
                    f"컴포넌트 '{component.name}'의 호환성이 낮습니다 (점수: {compatibility_score:.3f})"
                )

        # 가중치 검사
        total_weight = sum(comp.weight for comp in capsule.components)
        if total_weight < 0.5 or total_weight > len(capsule.components) * 1.2:
            warnings.append(
                f"컴포넌트 가중치 합계가 비정상적입니다: {total_weight:.3f}"
            )

        # 복잡도 검사
        if capsule.complexity.value == "advanced" and len(capsule.components) < 8:
            warnings.append("고급 복잡도에 비해 컴포넌트 수가 적습니다")
            recommendations.append("더 많은 컴포넌트를 추가하거나 복잡도를 조정하세요")

        # 성능 예측
        predicted_performance = self._predict_capsule_performance(capsule)

        # 전체 검증 점수 계산
        compatibility_avg = (
            np.mean(list(component_compatibility.values()))
            if component_compatibility
            else 0.5
        )
        performance_avg = (
            np.mean(list(predicted_performance.values()))
            if predicted_performance
            else 0.5
        )
        structure_score = (
            0.8 if len(warnings) == 0 else max(0.3, 0.8 - len(warnings) * 0.1)
        )

        validation_score = (
            compatibility_avg * 0.4 + performance_avg * 0.4 + structure_score * 0.2
        )

        if validation_score < 0.6:
            is_valid = False

        # 추천사항 생성
        if validation_score < 0.7:
            recommendations.append("컴포넌트 간 균형을 재조정해보세요")
        if compatibility_avg < 0.7:
            recommendations.append("호환성이 낮은 컴포넌트를 교체 또는 조정하세요")
        if performance_avg < 0.7:
            recommendations.append("성능 목표치를 재설정하거나 컴포넌트를 최적화하세요")

        return CapsuleValidationResult(
            is_valid=is_valid,
            validation_score=validation_score,
            component_compatibility=component_compatibility,
            predicted_performance=predicted_performance,
            warnings=warnings,
            recommendations=recommendations,
            timestamp=datetime.now(),
        )

    def _check_component_compatibility(
        self, component: CapsuleComponent, all_components: List[CapsuleComponent]
    ) -> float:
        """컴포넌트 호환성 검사"""
        compatibility_score = 0.8  # 기본 점수

        # 같은 타입 컴포넌트들과의 호환성
        same_type_components = [
            c
            for c in all_components
            if c.component_type == component.component_type
            and c.component_id != component.component_id
        ]

        if len(same_type_components) > 2:
            compatibility_score -= 0.1  # 같은 타입이 너무 많으면 감점

        # 가중치 균형성 검사
        if component.weight > 1.0 or component.weight < 0.1:
            compatibility_score -= 0.2

        # 의존성 검사
        for dependency in component.dependencies:
            if not any(c.component_id == dependency for c in all_components):
                compatibility_score -= 0.3  # 의존성이 만족되지 않으면 큰 감점

        # 파라미터 일관성 검사
        param_consistency = self._check_parameter_consistency(component, all_components)
        compatibility_score = (compatibility_score + param_consistency) / 2

        return max(0.0, min(1.0, compatibility_score))

    def _check_parameter_consistency(
        self, component: CapsuleComponent, all_components: List[CapsuleComponent]
    ) -> float:
        """파라미터 일관성 검사"""
        consistency_score = 0.8

        # 파라미터 값 범위 검사
        for param_name, param_value in component.parameters.items():
            if isinstance(param_value, (int, float)):
                if param_value < 0 or param_value > 1:
                    consistency_score -= 0.1

        return max(0.0, min(1.0, consistency_score))

    def _predict_capsule_performance(
        self, capsule: CapsuleBlueprint
    ) -> Dict[str, float]:
        """캡슐 성능 예측"""
        performance = {}

        # 컴포넌트별 기여도 계산
        total_weight = sum(comp.weight for comp in capsule.components)

        for metric_name, benchmark in self.performance_benchmarks.items():
            metric_score = 0.0

            for component in capsule.components:
                # 컴포넌트 타입별 메트릭 기여도
                contribution = self._calculate_component_contribution(
                    component, metric_name
                )
                weight_ratio = component.weight / max(1.0, total_weight)
                metric_score += contribution * weight_ratio

            # 블렌딩 효과 적용
            blending_bonus = self._calculate_blending_bonus(capsule, metric_name)
            metric_score = min(1.0, metric_score + blending_bonus)

            performance[metric_name] = metric_score

        return performance

    def _calculate_component_contribution(
        self, component: CapsuleComponent, metric_name: str
    ) -> float:
        """컴포넌트의 메트릭 기여도 계산"""
        # 컴포넌트 타입별 메트릭 친화성
        type_affinity = {
            "signature": {
                "empathy_response": 0.8,
                "creative_fluidity": 0.7,
                "coherence": 0.9,
                "analytical_precision": 0.6,
                "execution_speed": 0.7,
                "adaptability": 0.8,
                "stability": 0.8,
                "resource_efficiency": 0.7,
            },
            "emotion": {
                "empathy_response": 0.9,
                "creative_fluidity": 0.8,
                "coherence": 0.7,
                "analytical_precision": 0.5,
                "execution_speed": 0.6,
                "adaptability": 0.9,
                "stability": 0.6,
                "resource_efficiency": 0.8,
            },
            "cognitive": {
                "empathy_response": 0.5,
                "creative_fluidity": 0.6,
                "coherence": 0.8,
                "analytical_precision": 0.9,
                "execution_speed": 0.8,
                "adaptability": 0.7,
                "stability": 0.8,
                "resource_efficiency": 0.9,
            },
            "consciousness": {
                "empathy_response": 0.7,
                "creative_fluidity": 0.7,
                "coherence": 0.9,
                "analytical_precision": 0.7,
                "execution_speed": 0.6,
                "adaptability": 0.8,
                "stability": 0.9,
                "resource_efficiency": 0.7,
            },
        }

        base_contribution = type_affinity.get(component.component_type, {}).get(
            metric_name, 0.5
        )

        # 컴포넌트 파라미터로 조정
        param_boost = 0.0
        relevant_params = self._get_relevant_parameters(component, metric_name)
        if relevant_params:
            param_boost = np.mean(relevant_params) * 0.2

        return min(1.0, base_contribution + param_boost)

    def _get_relevant_parameters(
        self, component: CapsuleComponent, metric_name: str
    ) -> List[float]:
        """메트릭과 관련된 파라미터 추출"""
        param_mapping = {
            "empathy_response": [
                "empathy",
                "sensitivity",
                "understanding",
                "resonance",
            ],
            "creative_fluidity": ["creativity", "inspiration", "openness", "fluidity"],
            "analytical_precision": ["logic", "systematic", "precision", "analysis"],
            "execution_speed": ["efficiency", "speed", "optimization"],
            "adaptability": ["flexibility", "adaptation", "transformation"],
            "stability": ["stability", "persistence", "consistency"],
            "coherence": ["coherence", "integration", "harmony"],
        }

        relevant_param_names = param_mapping.get(metric_name, [])
        relevant_values = []

        for param_name, param_value in component.parameters.items():
            if any(keyword in param_name.lower() for keyword in relevant_param_names):
                if isinstance(param_value, (int, float)):
                    relevant_values.append(param_value)

        return relevant_values

    def _calculate_blending_bonus(
        self, capsule: CapsuleBlueprint, metric_name: str
    ) -> float:
        """블렌딩 보너스 계산"""
        blending_mode = capsule.blending_rules.get("mode", "weighted_average")

        # 블렌딩 모드별 메트릭 보너스
        blending_bonus = {
            "weighted_average": {"stability": 0.1, "coherence": 0.1},
            "dominant_overlay": {"execution_speed": 0.1, "analytical_precision": 0.1},
            "contextual_switching": {"adaptability": 0.15, "creative_fluidity": 0.1},
            "harmonic_fusion": {"creative_fluidity": 0.15, "empathy_response": 0.1},
            "adaptive_morphing": {"adaptability": 0.2, "resource_efficiency": 0.1},
        }

        return blending_bonus.get(blending_mode, {}).get(metric_name, 0.0)
