"""
🎯 FIST Templates Core - 핵심 클래스 및 데이터 구조
Frame, Insight, Strategy, Tactics 구조화된 프롬프트 시스템의 핵심 구현
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
import json
import uuid


class FISTStructureType(Enum):
    """FIST 구조 유형"""

    FIST = "fist"  # Frame, Insight, Strategy, Tactics
    RISE = "rise"  # Reflect, Improve, Synthesize, Evolve
    DIR = "dir"  # Directionality


class TemplateCategory(Enum):
    """템플릿 카테고리"""

    DECISION = "decision"
    EVALUATION = "evaluation"
    CREATIVE = "creative"
    EMOTIONAL = "emotional"
    STRATEGIC = "strategic"
    ANALYTICAL = "analytical"
    PROBLEM_SOLVING = "problem_solving"
    PREDICTION = "prediction"


class TemplateComplexity(Enum):
    """템플릿 복잡도"""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"


@dataclass
class FISTComponent:
    """FIST 구조의 개별 구성요소"""

    name: str
    description: str
    prompt_template: str
    variables: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    optional: bool = False

    def render(self, context: Dict[str, Any]) -> str:
        """컨텍스트를 사용하여 프롬프트 렌더링"""
        try:
            # 🔧 패치: 템플릿 변수 검증 및 기본값 설정
            safe_context = self._ensure_template_variables(context)

            # 템플릿 변수 치환
            rendered = self.prompt_template.format(**safe_context, **self.variables)
            return rendered
        except KeyError as e:
            # graceful fallback - 누락된 변수에 기본값 설정
            print(f"[DEBUG] 템플릿 변수 누락 감지: {e}, 기본값으로 대체")
            fallback_context = self._create_fallback_context(context, str(e))
            try:
                rendered = self.prompt_template.format(
                    **fallback_context, **self.variables
                )
                return rendered
            except Exception as fallback_error:
                raise ValueError(
                    f"템플릿 변수 누락 및 폴백 실패: {e} -> {fallback_error}"
                )
        except Exception as e:
            raise ValueError(f"템플릿 렌더링 실패: {e}")

    def _ensure_template_variables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """템플릿 변수 검증 및 기본값 설정"""
        safe_context = context.copy()

        # 일반적으로 사용되는 템플릿 변수들
        default_variables = {
            "key_people": "관련 인물 미지정",
            "situation": "상황 미지정",
            "focus": "초점 미지정",
            "insights": "통찰 미지정",
            "strategic_direction": "전략적 방향 미지정",
            "implementation": "구현 방안 미지정",
            "risk_factors": "위험 요소 미지정",
            "decision_criteria": "판단 기준 미지정",
            "target_audience": "대상 집단 미지정",
            "context_summary": "컨텍스트 요약 미지정",
            "stakeholders": "이해관계자 미지정",
            "objectives": "목표 미지정",
            "constraints": "제약 조건 미지정",
            # 🔧 패차: relationship 관련 변수 추가
            "relationship_type": "관계 유형 미지정",
            "relationship_importance": "관계 중요도 미지정",
            # 추가 자주 사용되는 변수들
            "timeline": "시간계획 미지정",
            "resources": "자원 현황 미지정",
            "success_metrics": "성공 지표 미지정",
            "communication_plan": "소통 계획 미지정",
            "governance": "거버넌스 미지정",
        }

        for key, default_value in default_variables.items():
            if key not in safe_context or safe_context[key] is None:
                safe_context[key] = default_value

        # 🔧 패치: 복합 템플릿 변수 의존성 보정
        safe_context = self._repair_missing_variables(safe_context)

        return safe_context

    def _repair_missing_variables(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """복합 템플릿 변수 의존성 보정"""
        # 연관 변수 쌍 정의
        fallback_pairs = [
            ("relationship_type", "relationship_importance"),
            ("objectives", "strategic_direction"),
            ("focus", "context_summary"),
            ("key_people", "stakeholders"),
            ("situation", "context_summary"),
            ("implementation", "strategic_direction"),
            ("risk_factors", "decision_criteria"),
            ("timeline", "implementation"),
            ("resources", "constraints"),
            ("success_metrics", "objectives"),
        ]

        for key, backup_key in fallback_pairs:
            # key는 없지만 backup_key는 있는 경우
            if key not in variables and backup_key in variables:
                variables[key] = f"{key} 미지정 (관련: {backup_key})"
                print(f"[DEBUG] 복합 변수 보정: {key} ← {backup_key}")

            # backup_key는 없지만 key는 있는 경우
            elif backup_key not in variables and key in variables:
                variables[backup_key] = f"{backup_key} 미지정 (관련: {key})"
                print(f"[DEBUG] 복합 변수 보정: {backup_key} ← {key}")

        return variables

    def _create_fallback_context(
        self, context: Dict[str, Any], missing_key: str
    ) -> Dict[str, Any]:
        """폴백 컨텍스트 생성"""
        fallback_context = context.copy()

        # KeyError 메시지에서 실제 키 추출 (예: "'key_people'" -> "key_people")
        clean_key = missing_key.strip("'\"")
        fallback_context[clean_key] = f"{clean_key} 미지정"

        return fallback_context


@dataclass
class FISTTemplate:
    """FIST 템플릿 정의"""

    template_id: str
    name: str
    description: str
    category: TemplateCategory
    complexity: TemplateComplexity
    structure_type: FISTStructureType

    # FIST 구조 구성요소들
    frame: FISTComponent
    insight: FISTComponent
    strategy: FISTComponent
    tactics: FISTComponent

    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    author: str = "EchoJudgmentSystem"
    tags: List[str] = field(default_factory=list)

    # 성능 지표
    usage_count: int = 0
    success_rate: float = 0.0
    average_confidence: float = 0.0

    # 설정
    max_tokens: int = 1000
    temperature: float = 0.3
    requires_context: bool = True

    def __post_init__(self):
        if not self.template_id:
            self.template_id = str(uuid.uuid4())[:8]

    def get_full_prompt(self, context: Dict[str, Any]) -> str:
        """완전한 FIST 프롬프트 생성"""
        components = []

        # Frame 섹션
        if not self.frame.optional:
            components.append(f"## Frame (맥락 설정)\n{self.frame.render(context)}")

        # Insight 섹션
        if not self.insight.optional:
            components.append(
                f"## Insight (분석 및 이해)\n{self.insight.render(context)}"
            )

        # Strategy 섹션
        if not self.strategy.optional:
            components.append(
                f"## Strategy (접근 전략)\n{self.strategy.render(context)}"
            )

        # Tactics 섹션
        if not self.tactics.optional:
            components.append(
                f"## Tactics (구체적 실행)\n{self.tactics.render(context)}"
            )

        return "\n\n".join(components)

    def validate_template(self) -> Dict[str, Any]:
        """템플릿 유효성 검증"""
        validation_result = {"is_valid": True, "errors": [], "warnings": []}

        # 필수 구성요소 검증
        components = [self.frame, self.insight, self.strategy, self.tactics]
        for component in components:
            if not component.prompt_template:
                validation_result["errors"].append(
                    f"{component.name} 프롬프트가 비어있습니다"
                )
                validation_result["is_valid"] = False

        # 변수 일관성 검증
        all_variables = set()
        for component in components:
            # 템플릿에서 사용된 변수 추출
            import re

            variables_in_template = re.findall(r"\{(\w+)\}", component.prompt_template)
            all_variables.update(variables_in_template)

        # 템플릿 복잡도 검증
        total_length = sum(len(comp.prompt_template) for comp in components)
        if total_length > 2000 and self.complexity == TemplateComplexity.SIMPLE:
            validation_result["warnings"].append(
                "템플릿 길이가 Simple 복잡도에 비해 깁니다"
            )

        return validation_result

    def to_dict(self) -> Dict[str, Any]:
        """템플릿을 딕셔너리로 변환"""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "complexity": self.complexity.value,
            "structure_type": self.structure_type.value,
            "components": {
                "frame": {
                    "name": self.frame.name,
                    "description": self.frame.description,
                    "prompt_template": self.frame.prompt_template,
                    "weight": self.frame.weight,
                },
                "insight": {
                    "name": self.insight.name,
                    "description": self.insight.description,
                    "prompt_template": self.insight.prompt_template,
                    "weight": self.insight.weight,
                },
                "strategy": {
                    "name": self.strategy.name,
                    "description": self.strategy.description,
                    "prompt_template": self.strategy.prompt_template,
                    "weight": self.strategy.weight,
                },
                "tactics": {
                    "name": self.tactics.name,
                    "description": self.tactics.description,
                    "prompt_template": self.tactics.prompt_template,
                    "weight": self.tactics.weight,
                },
            },
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "version": self.version,
                "author": self.author,
                "tags": self.tags,
                "usage_count": self.usage_count,
                "success_rate": self.success_rate,
                "average_confidence": self.average_confidence,
            },
            "settings": {
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "requires_context": self.requires_context,
            },
        }


@dataclass
class RISETemplate:
    """RISE 구조 템플릿 (Reflect, Improve, Synthesize, Evolve)"""

    template_id: str
    name: str
    description: str
    category: TemplateCategory

    # RISE 구조 구성요소들
    reflect: FISTComponent
    improve: FISTComponent
    synthesize: FISTComponent
    evolve: FISTComponent

    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"

    def get_full_prompt(self, context: Dict[str, Any]) -> str:
        """완전한 RISE 프롬프트 생성"""
        components = [
            f"## Reflect (회고 분석)\n{self.reflect.render(context)}",
            f"## Improve (개선 방안)\n{self.improve.render(context)}",
            f"## Synthesize (통합 관점)\n{self.synthesize.render(context)}",
            f"## Evolve (진화 계획)\n{self.evolve.render(context)}",
        ]

        return "\n\n".join(components)


@dataclass
class DIRTemplate:
    """DIR 구조 템플릿 (Directionality - 방향성 기반)"""

    template_id: str
    name: str
    description: str
    category: TemplateCategory

    # DIR 구조 구성요소들
    direction: FISTComponent
    intention: FISTComponent
    realization: FISTComponent

    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"

    def get_full_prompt(self, context: Dict[str, Any]) -> str:
        """완전한 DIR 프롬프트 생성"""
        components = [
            f"## Direction (방향성)\n{self.direction.render(context)}",
            f"## Intention (의도)\n{self.intention.render(context)}",
            f"## Realization (실현)\n{self.realization.render(context)}",
        ]

        return "\n\n".join(components)


@dataclass
class FISTRequest:
    """FIST 처리 요청"""

    input_text: str
    category: TemplateCategory
    structure_type: FISTStructureType = FISTStructureType.FIST

    # 선택적 설정
    complexity: Optional[TemplateComplexity] = None
    template_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    # 처리 설정
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

    # 메타데이터
    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=datetime.now)

    def add_context(self, key: str, value: Any) -> None:
        """컨텍스트 추가"""
        self.context[key] = value

    def get_context_with_input(self) -> Dict[str, Any]:
        """입력 텍스트를 포함한 전체 컨텍스트 반환"""
        return {
            "input_text": self.input_text,
            "category": self.category.value,
            "structure_type": self.structure_type.value,
            "request_id": self.request_id,
            "timestamp": self.timestamp.isoformat(),
            **self.context,
        }


@dataclass
class FISTResponse:
    """FIST 처리 응답"""

    request_id: str
    template_id: str

    # 구조화된 응답
    frame_result: str
    insight_result: str
    strategy_result: str
    tactics_result: str

    # 종합 결과
    comprehensive_judgment: str
    confidence: float

    # 처리 정보
    processing_time: float
    template_used: str
    structure_type: FISTStructureType

    # 메타데이터
    timestamp: datetime = field(default_factory=datetime.now)
    alternatives: List[str] = field(default_factory=list)
    reasoning_trace: List[str] = field(default_factory=list)

    def get_structured_output(self) -> Dict[str, Any]:
        """구조화된 출력 반환"""
        return {
            "frame": self.frame_result,
            "insight": self.insight_result,
            "strategy": self.strategy_result,
            "tactics": self.tactics_result,
            "comprehensive": self.comprehensive_judgment,
            "confidence": self.confidence,
            "processing_time": self.processing_time,
            "template_used": self.template_used,
            "structure_type": self.structure_type.value,
            "alternatives": self.alternatives,
            "reasoning_trace": self.reasoning_trace,
        }

    def to_claude_format(self) -> Dict[str, Any]:
        """Claude 응답 형식으로 변환"""
        return {
            "judgment": self.comprehensive_judgment,
            "confidence": self.confidence,
            "reasoning": " → ".join(self.reasoning_trace),
            "emotion_detected": "analyzed",  # FIST 구조에서는 분석된 상태
            "strategy_suggested": "structured",  # FIST 구조 기반 전략
            "alternatives": self.alternatives,
            "processing_time": self.processing_time,
            "fist_structure": {
                "frame": self.frame_result,
                "insight": self.insight_result,
                "strategy": self.strategy_result,
                "tactics": self.tactics_result,
            },
        }


# 템플릿 빌더 클래스
class FISTTemplateBuilder:
    """FIST 템플릿 빌더 (Builder Pattern)"""

    def __init__(self):
        self.reset()

    def reset(self):
        """빌더 초기화"""
        self._template_id = None
        self._name = None
        self._description = None
        self._category = None
        self._complexity = TemplateComplexity.MODERATE
        self._structure_type = FISTStructureType.FIST
        self._components = {}
        self._metadata = {}
        self._settings = {}
        return self

    def with_id(self, template_id: str):
        """템플릿 ID 설정"""
        self._template_id = template_id
        return self

    def with_name(self, name: str):
        """템플릿 이름 설정"""
        self._name = name
        return self

    def with_description(self, description: str):
        """템플릿 설명 설정"""
        self._description = description
        return self

    def with_category(self, category: TemplateCategory):
        """템플릿 카테고리 설정"""
        self._category = category
        return self

    def with_complexity(self, complexity: TemplateComplexity):
        """템플릿 복잡도 설정"""
        self._complexity = complexity
        return self

    def with_frame(
        self, name: str, description: str, prompt_template: str, weight: float = 1.0
    ):
        """Frame 구성요소 설정"""
        self._components["frame"] = FISTComponent(
            name, description, prompt_template, weight=weight
        )
        return self

    def with_insight(
        self, name: str, description: str, prompt_template: str, weight: float = 1.0
    ):
        """Insight 구성요소 설정"""
        self._components["insight"] = FISTComponent(
            name, description, prompt_template, weight=weight
        )
        return self

    def with_strategy(
        self, name: str, description: str, prompt_template: str, weight: float = 1.0
    ):
        """Strategy 구성요소 설정"""
        self._components["strategy"] = FISTComponent(
            name, description, prompt_template, weight=weight
        )
        return self

    def with_tactics(
        self, name: str, description: str, prompt_template: str, weight: float = 1.0
    ):
        """Tactics 구성요소 설정"""
        self._components["tactics"] = FISTComponent(
            name, description, prompt_template, weight=weight
        )
        return self

    def build(self) -> FISTTemplate:
        """FIST 템플릿 빌드"""
        if not all([self._name, self._description, self._category]):
            raise ValueError("필수 템플릿 정보가 누락되었습니다")

        if not all(
            key in self._components
            for key in ["frame", "insight", "strategy", "tactics"]
        ):
            raise ValueError("FIST 구성요소가 모두 설정되지 않았습니다")

        template = FISTTemplate(
            template_id=self._template_id or str(uuid.uuid4())[:8],
            name=self._name,
            description=self._description,
            category=self._category,
            complexity=self._complexity,
            structure_type=self._structure_type,
            frame=self._components["frame"],
            insight=self._components["insight"],
            strategy=self._components["strategy"],
            tactics=self._components["tactics"],
        )

        # 템플릿 검증
        validation = template.validate_template()
        if not validation["is_valid"]:
            raise ValueError(f"템플릿 검증 실패: {validation['errors']}")

        return template


# 편의 함수들
def create_simple_fist_template(
    name: str,
    category: TemplateCategory,
    frame_prompt: str,
    insight_prompt: str,
    strategy_prompt: str,
    tactics_prompt: str,
) -> FISTTemplate:
    """간단한 FIST 템플릿 생성"""
    builder = FISTTemplateBuilder()
    return (
        builder.with_name(name)
        .with_description(f"Simple {category.value} template")
        .with_category(category)
        .with_complexity(TemplateComplexity.SIMPLE)
        .with_frame("Frame", "Context setting", frame_prompt)
        .with_insight("Insight", "Analysis", insight_prompt)
        .with_strategy("Strategy", "Approach", strategy_prompt)
        .with_tactics("Tactics", "Implementation", tactics_prompt)
        .build()
    )


def load_template_from_dict(template_data: Dict[str, Any]) -> FISTTemplate:
    """딕셔너리에서 템플릿 로드"""
    components = template_data["components"]

    return FISTTemplate(
        template_id=template_data["template_id"],
        name=template_data["name"],
        description=template_data["description"],
        category=TemplateCategory(template_data["category"]),
        complexity=TemplateComplexity(template_data["complexity"]),
        structure_type=FISTStructureType(template_data["structure_type"]),
        frame=FISTComponent(
            name=components["frame"]["name"],
            description=components["frame"]["description"],
            prompt_template=components["frame"]["prompt_template"],
            weight=components["frame"]["weight"],
        ),
        insight=FISTComponent(
            name=components["insight"]["name"],
            description=components["insight"]["description"],
            prompt_template=components["insight"]["prompt_template"],
            weight=components["insight"]["weight"],
        ),
        strategy=FISTComponent(
            name=components["strategy"]["name"],
            description=components["strategy"]["description"],
            prompt_template=components["strategy"]["prompt_template"],
            weight=components["strategy"]["weight"],
        ),
        tactics=FISTComponent(
            name=components["tactics"]["name"],
            description=components["tactics"]["description"],
            prompt_template=components["tactics"]["prompt_template"],
            weight=components["tactics"]["weight"],
        ),
    )
