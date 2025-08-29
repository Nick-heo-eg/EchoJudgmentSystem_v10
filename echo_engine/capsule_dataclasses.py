from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, field
from echo_engine.capsule_types import CapsuleType, CapsuleComplexity

"""
🎭 Capsule Designer Data Classes
캡슐 설계 시스템의 핵심 데이터 구조들
"""




@dataclass
class CapsuleComponent:
    """캡슐 컴포넌트"""

    component_id: str
    component_type: str  # "signature", "emotion", "cognitive", "consciousness"
    name: str
    weight: float  # 0.0 ~ 1.0
    parameters: Dict[str, Any]
    description: str
    dependencies: List[str] = field(default_factory=list)


@dataclass
class CapsuleBlueprint:
    """캡슐 설계도"""

    capsule_id: str
    name: str
    description: str
    capsule_type: CapsuleType
    complexity: CapsuleComplexity
    components: List[CapsuleComponent]
    blending_rules: Dict[str, Any]
    performance_targets: Dict[str, float]
    metadata: Dict[str, Any]
    created_timestamp: datetime
    last_modified: datetime
    version: str


@dataclass
class CapsuleValidationResult:
    """캡슐 검증 결과"""

    is_valid: bool
    validation_score: float
    component_compatibility: Dict[str, float]
    predicted_performance: Dict[str, float]
    warnings: List[str]
    recommendations: List[str]
    timestamp: datetime


@dataclass
class CapsuleSimulationResult:
    """캡슐 시뮬레이션 결과"""

    simulation_id: str
    capsule_id: str
    scenario_name: str
    performance_metrics: Dict[str, float]
    behavioral_patterns: Dict[str, Any]
    resource_usage: Dict[str, float]
    execution_time_ms: float
    stability_score: float
    adaptability_score: float
    timestamp: datetime


@dataclass
class CapsuleTemplate:
    """캡슐 템플릿"""

    template_id: str
    template_name: str
    category: str
    description: str
    base_components: List[CapsuleComponent]
    customization_options: Dict[str, Any]
    use_cases: List[str]
    difficulty_level: str  # "beginner", "intermediate", "advanced", "expert"
