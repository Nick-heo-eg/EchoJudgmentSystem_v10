import json
import uuid
import copy
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict, field, replace as dataclasses_replace
import numpy as np
import logging
from functools import lru_cache
from echo_engine.capsule_types import CapsuleType, CapsuleComplexity, CapsuleStatus
from echo_engine.capsule_dataclasses import (
    CapsuleData, CapsuleMetrics, CapsuleConfig, CapsuleComponent, CapsuleBlueprint,
    CapsuleValidationResult, CapsuleSimulationResult, CapsuleTemplate
)
from echo_engine.capsule_initializers import CapsuleInitializers
from echo_engine.capsule_validators import CapsuleValidators
from echo_engine.capsule_simulators import CapsuleSimulators
from echo_engine.capsule_optimizers import CapsuleOptimizers
from echo_engine.signature_cross_resonance_mapper import SignatureCrossResonanceMapper
from echo_engine.hybrid_signature_composer import HybridSignatureComposer, BlendingMode
from echo_engine.consciousness_flow_analyzer import ConsciousnessFlowAnalyzer
from echo_engine.emotion_response_chart_generator import EmotionResponseChartGenerator
from echo_engine.enhanced_natural_command_processor import EnhancedNaturalCommandProcessor

#!/usr/bin/env python3
"""
💊 Capsule Designer Interface v1.1 (Optimized)
Echo Neural System v2.0의 캡슐 설계 및 관리를 위한 통합 인터페이스

핵심 기능:
- 시그니처 캡슐 설계
- 감정-인지 캡슐 조합
- 캡슐 템플릿 라이브러리
- 실시간 캡슐 프리뷰
- 캡슐 성능 시뮬레이션 (캐싱 적용)
- 자동 캡슐 최적화
"""

# Echo 엔진 모듈들
try:
    from echo_engine.consciousness_flow_analyzer import ConsciousnessLevel
except ImportError:
    print("⚠️ Echo modules not available, running in standalone mode")


class CapsuleDesignerInterface:
    """💊 캡슐 디자이너 인터페이스 (최적화 버전)"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.capsule_blueprints = {}
        self.capsule_templates = {}
        self.validation_cache = {}
        self.simulation_cache = {}

        # 설계 도구 초기화
        self.component_library = CapsuleInitializers.initialize_component_library()
        self.performance_benchmarks = CapsuleInitializers.initialize_performance_benchmarks()
        self.capsule_templates = CapsuleInitializers.initialize_template_library(self.component_library)

        # 전문 기능 클래스들 초기화
        self.validator = CapsuleValidators(self.performance_benchmarks)
        self.simulator = CapsuleSimulators(self._predict_capsule_performance)
        self.optimizer = CapsuleOptimizers(self._calculate_component_contribution)
        print("💊 Capsule Designer Interface 초기화 완료")

    def create_capsule_from_template(
        self,
        template_id: str,
        customizations: Dict[str, Any] = None,
    ) -> CapsuleBlueprint:
        """템플릿으로부터 캡슐 생성 (최적화)"""
        template = self.capsule_templates.get(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        customizations = customizations or {}
        
        # deepcopy 대신 필요한 속성만 복사하여 새 객체 생성
        components = []
        for base_comp in template.base_components:
            params = base_comp.parameters.copy()
            weight = base_comp.weight
            for opt_name, opt_value in customizations.items():
                if opt_name in template.customization_options:
                    if opt_name.endswith("_weight"):
                        weight = opt_value
                    else:
                        params[opt_name] = opt_value
            
            components.append(dataclasses_replace(base_comp, parameters=params, weight=weight))

        capsule_id = f"cap_{template.template_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        
        complexity = CapsuleComplexity.MODERATE
        if len(components) <= 2: complexity = CapsuleComplexity.SIMPLE
        elif len(components) >= 6: complexity = CapsuleComplexity.COMPLEX

        capsule = CapsuleBlueprint(
            capsule_id=capsule_id,
            name=f"Custom {template.template_name}",
            description=f"템플릿 '{template.template_name}'으로부터 생성된 커스텀 캡슐",
            capsule_type=CapsuleType.CUSTOM_BLEND,
            complexity=complexity,
            components=components,
            blending_rules=customizations.get("blending_rules", {"mode": "weighted_average"}),
            performance_targets={"overall_effectiveness": 0.8, "component_harmony": 0.75},
            metadata={"template_id": template_id, "customizations": customizations},
            created_timestamp=datetime.now(), last_modified=datetime.now(), version="1.0",
        )
        self.capsule_blueprints[capsule_id] = capsule
        return capsule

    @lru_cache(maxsize=128)
    def _predict_capsule_performance(self, capsule_blueprint_tuple: Tuple) -> Dict[str, float]:
        """캡슐 성능 예측 (캐싱 적용)"""
        capsule = CapsuleBlueprint(*capsule_blueprint_tuple)
        performance = {}
        weights = np.array([comp.weight for comp in capsule.components])
        total_weight = np.sum(weights)
        if total_weight == 0: return {metric: 0.0 for metric in self.performance_benchmarks}

        weight_ratios = weights / total_weight

        for metric_name in self.performance_benchmarks:
            contributions = np.array([self._calculate_component_contribution(comp, metric_name) for comp in capsule.components])
            metric_score = np.dot(contributions, weight_ratios)
            
            blending_bonus = self._calculate_blending_bonus(capsule, metric_name)
            performance[metric_name] = min(1.0, metric_score + blending_bonus)
            
        return performance

    @lru_cache(maxsize=1024)
    def _calculate_component_contribution(self, component: CapsuleComponent, metric_name: str) -> float:
        """컴포넌트의 메트릭 기여도 계산 (캐싱 적용)"""
        type_affinity = {
            "signature": {"empathy_response": 0.8, "creative_fluidity": 0.7, "coherence": 0.9},
            "emotion": {"empathy_response": 0.9, "creative_fluidity": 0.8, "coherence": 0.7},
            "cognitive": {"analytical_precision": 0.9, "execution_speed": 0.8, "coherence": 0.8},
            "consciousness": {"stability": 0.9, "coherence": 0.9, "adaptability": 0.8},
        }
        base_contribution = type_affinity.get(component.component_type, {}).get(metric_name, 0.5)
        return base_contribution

    def _calculate_blending_bonus(self, capsule: CapsuleBlueprint, metric_name: str) -> float:
        """블렌딩 보너스 계산"""
        blending_mode = capsule.blending_rules.get("mode", "weighted_average")
        blending_bonus = {
            "weighted_average": {"stability": 0.1, "coherence": 0.1},
            "harmonic_fusion": {"creative_fluidity": 0.15, "empathy_response": 0.1},
            "adaptive_morphing": {"adaptability": 0.2, "resource_efficiency": 0.1},
        }
        return blending_bonus.get(blending_mode, {}).get(metric_name, 0.0)

    def get_capsule_summary(self, capsule_id: str) -> Dict[str, Any]:
        """캡슐 요약 정보 반환"""
        capsule = self.capsule_blueprints.get(capsule_id)
        if not capsule:
            return {"error": f"Capsule not found: {capsule_id}"}

        validation = self.validation_cache.get(capsule_id)
        
        # Convert unhashable capsule to a hashable tuple for caching
        capsule_tuple = tuple(asdict(capsule).values())
        performance = self._predict_capsule_performance(capsule_tuple)

        return {
            "basic_info": {"name": capsule.name, "type": capsule.capsule_type.value},
            "components": [{"name": comp.name, "type": comp.component_type, "weight": comp.weight} for comp in capsule.components],
            "validation": {"is_valid": validation.is_valid, "score": validation.validation_score} if validation else None,
            "performance": {"metrics": performance},
        }

if __name__ == "__main__":
    print("💊 Capsule Designer Interface 테스트 (Optimized)...")
    designer = CapsuleDesignerInterface()
    
    print("\n🔍 Creating Capsule from Template...")
    capsule1 = designer.create_capsule_from_template("tpl_creative_empathy")
    print(f"✅ Created Capsule: {capsule1.name}")

    # Convert to hashable tuple for caching
    capsule1_tuple = tuple(asdict(capsule1).values())

    start_time = datetime.now()
    perf1 = designer._predict_capsule_performance(capsule1_tuple)
    duration1 = datetime.now() - start_time
    print(f"   Initial performance prediction took: {duration1.total_seconds():.6f}s")

    start_time = datetime.now()
    perf2 = designer._predict_capsule_performance(capsule1_tuple)
    duration2 = datetime.now() - start_time
    print(f"   Cached performance prediction took:  {duration2.total_seconds():.6f}s")
    
    print("\n✅ Capsule Designer Interface 테스트 완료!")
