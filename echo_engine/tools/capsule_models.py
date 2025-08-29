"""
🎭 Capsule System Models
실행 가능한 캡슐 시스템의 핵심 모델들
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class CapsuleType(str, Enum):
    EMOTION = "emotion"
    SIGNATURE = "signature"
    COGNITIVE = "cognitive"
    HYBRID = "hybrid"


class ExecutionContext(BaseModel):
    """실행 컨텍스트"""

    text: Optional[str] = None
    emotion: Optional[str] = None
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    context: Dict[str, Any] = Field(default_factory=dict)


class CapsuleRule(BaseModel):
    """캡슐 규칙"""

    condition: str  # 조건 표현식
    action: str  # 수행할 액션
    priority: int = Field(default=1, ge=1, le=10)
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class CapsuleTemplate(BaseModel):
    """캡슐 템플릿"""

    name: str
    description: str
    base_emotion: Optional[str] = None
    default_rules: List[CapsuleRule] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class CapsuleSpec(BaseModel):
    """캡슐 사양"""

    name: str
    version: str = "1.0.0"
    type: CapsuleType
    description: str

    # 실행 설정
    template: Optional[str] = None
    rules: List[CapsuleRule] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)

    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.now)
    author: str = "Echo System"
    tags: List[str] = Field(default_factory=list)


class SimulationResult(BaseModel):
    """시뮬레이션 결과"""

    capsule_name: str
    input_context: ExecutionContext

    # 결과
    triggered_rules: List[str] = Field(default_factory=list)
    output_actions: List[str] = Field(default_factory=list)
    emotional_state: Dict[str, float] = Field(default_factory=dict)

    # 메트릭
    execution_time_ms: float
    confidence_score: float = Field(ge=0.0, le=1.0)

    timestamp: datetime = Field(default_factory=datetime.now)


class CapsuleRegistry(BaseModel):
    """캡슐 레지스트리"""

    capsules: Dict[str, CapsuleSpec] = Field(default_factory=dict)
    templates: Dict[str, CapsuleTemplate] = Field(default_factory=dict)

    def register_capsule(self, capsule: CapsuleSpec) -> None:
        """캡슐 등록"""
        self.capsules[capsule.name] = capsule

    def get_capsule(self, name: str) -> Optional[CapsuleSpec]:
        """캡슐 조회"""
        return self.capsules.get(name)

    def list_capsules(
        self, type_filter: Optional[CapsuleType] = None
    ) -> List[CapsuleSpec]:
        """캡슐 목록"""
        capsules = list(self.capsules.values())
        if type_filter:
            capsules = [c for c in capsules if c.type == type_filter]
        return capsules
