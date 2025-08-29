"""
🎯 Base Template Abstraction - 통합 템플릿 시스템
FIST, RISE, DIR 구조를 위한 공통 기반 클래스 및 추상화 계층
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Type
from enum import Enum
from datetime import datetime
import json
import uuid


class StructureType(Enum):
    """구조 유형 (FIST, RISE, DIR 등)"""

    FIST = "fist"  # Frame, Insight, Strategy, Tactics
    RISE = "rise"  # Reflect, Improve, Synthesize, Evolve
    DIR = "dir"  # Direction, Intention, Realization


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
class BaseComponent(ABC):
    """모든 템플릿 구성요소의 기본 클래스"""

    name: str
    description: str
    prompt_template: str
    variables: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    optional: bool = False

    def render(self, context: Dict[str, Any]) -> str:
        """컨텍스트를 사용하여 프롬프트 렌더링"""
        try:
            # 기본 변수와 컨텍스트 병합
            merged_context = {**self.variables, **context}
            rendered = self.prompt_template.format(**merged_context)
            return rendered.strip()
        except KeyError as e:
            return f"[템플릿 오류: {e} 변수 누락]"
        except Exception as e:
            return f"[렌더링 오류: {str(e)}]"

    @abstractmethod
    def get_structure_specific_data(self) -> Dict[str, Any]:
        """구조별 특수 데이터 반환"""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """컴포넌트를 딕셔너리로 변환"""
        return {
            "name": self.name,
            "description": self.description,
            "prompt_template": self.prompt_template,
            "variables": self.variables,
            "weight": self.weight,
            "optional": self.optional,
            **self.get_structure_specific_data(),
        }


@dataclass
class BaseTemplate(ABC):
    """모든 템플릿의 기본 클래스"""

    template_id: str
    name: str
    description: str
    structure_type: StructureType
    category: TemplateCategory
    complexity: TemplateComplexity
    components: List[BaseComponent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    @abstractmethod
    def get_component_names(self) -> List[str]:
        """해당 구조의 컴포넌트 이름 목록 반환"""
        pass

    @abstractmethod
    def create_component(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> BaseComponent:
        """구조별 컴포넌트 생성"""
        pass

    def add_component(self, component: BaseComponent) -> "BaseTemplate":
        """컴포넌트 추가"""
        self.components.append(component)
        return self

    def get_component(self, name: str) -> Optional[BaseComponent]:
        """이름으로 컴포넌트 조회"""
        for component in self.components:
            if component.name.lower() == name.lower():
                return component
        return None

    def get_full_prompt(self, context: Dict[str, Any] = None) -> str:
        """전체 프롬프트 생성"""
        if context is None:
            context = {}

        prompt_parts = []
        for component in self.components:
            if not component.optional or context.get(
                f"include_{component.name.lower()}", True
            ):
                rendered = component.render(context)
                if rendered and not rendered.startswith("["):  # 오류가 아닌 경우
                    prompt_parts.append(rendered)

        return "\n\n".join(prompt_parts)

    def calculate_confidence(self, context: Dict[str, Any] = None) -> float:
        """템플릿 적용 신뢰도 계산"""
        if not self.components:
            return 0.0

        total_weight = sum(comp.weight for comp in self.components if not comp.optional)
        if total_weight == 0:
            return 0.0

        # 필수 컴포넌트가 모두 렌더링 가능한지 확인
        valid_components = 0
        for component in self.components:
            if not component.optional:
                rendered = component.render(context or {})
                if not rendered.startswith("["):  # 오류가 아닌 경우
                    valid_components += component.weight

        return min(1.0, valid_components / total_weight)

    def to_dict(self) -> Dict[str, Any]:
        """템플릿을 딕셔너리로 변환"""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "structure_type": self.structure_type.value,
            "category": self.category.value,
            "complexity": self.complexity.value,
            "components": [comp.to_dict() for comp in self.components],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseTemplate":
        """딕셔너리에서 템플릿 생성"""
        # 구조별 템플릿 클래스 매핑
        from .fist_templates import FISTTemplate
        from .rise_templates import RISETemplate
        from .dir_templates import DIRTemplate

        structure_type = StructureType(data["structure_type"])
        template_classes = {
            StructureType.FIST: FISTTemplate,
            StructureType.RISE: RISETemplate,
            StructureType.DIR: DIRTemplate,
        }

        template_class = template_classes.get(structure_type)
        if not template_class:
            raise ValueError(f"Unknown structure type: {structure_type}")

        return template_class.from_dict(data)


@dataclass
class BaseRequest:
    """템플릿 요청 기본 클래스"""

    input_text: str
    context: Dict[str, Any] = field(default_factory=dict)
    category: Optional[TemplateCategory] = None
    complexity: Optional[TemplateComplexity] = None
    structure_type: Optional[StructureType] = None
    template_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """요청을 딕셔너리로 변환"""
        return {
            "input_text": self.input_text,
            "context": self.context,
            "category": self.category.value if self.category else None,
            "complexity": self.complexity.value if self.complexity else None,
            "structure_type": (
                self.structure_type.value if self.structure_type else None
            ),
            "template_id": self.template_id,
            "metadata": self.metadata,
        }


@dataclass
class BaseResponse:
    """템플릿 응답 기본 클래스"""

    template_id: str
    structure_type: StructureType
    generated_prompt: str
    confidence: float
    processing_time: float
    components_used: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """응답을 딕셔너리로 변환"""
        return {
            "template_id": self.template_id,
            "structure_type": self.structure_type.value,
            "generated_prompt": self.generated_prompt,
            "confidence": self.confidence,
            "processing_time": self.processing_time,
            "components_used": self.components_used,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


class BaseTemplateBuilder(ABC):
    """템플릿 빌더 기본 클래스"""

    def __init__(self, structure_type: StructureType):
        self.structure_type = structure_type
        self.template_id = str(uuid.uuid4())
        self.name = ""
        self.description = ""
        self.category = TemplateCategory.DECISION
        self.complexity = TemplateComplexity.MODERATE
        self.components = []
        self.metadata = {}

    def with_id(self, template_id: str) -> "BaseTemplateBuilder":
        """템플릿 ID 설정"""
        self.template_id = template_id
        return self

    def with_name(self, name: str) -> "BaseTemplateBuilder":
        """템플릿 이름 설정"""
        self.name = name
        return self

    def with_description(self, description: str) -> "BaseTemplateBuilder":
        """템플릿 설명 설정"""
        self.description = description
        return self

    def with_category(self, category: TemplateCategory) -> "BaseTemplateBuilder":
        """템플릿 카테고리 설정"""
        self.category = category
        return self

    def with_complexity(self, complexity: TemplateComplexity) -> "BaseTemplateBuilder":
        """템플릿 복잡도 설정"""
        self.complexity = complexity
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> "BaseTemplateBuilder":
        """메타데이터 설정"""
        self.metadata.update(metadata)
        return self

    @abstractmethod
    def build(self) -> BaseTemplate:
        """템플릿 생성"""
        pass


class TemplateEngine(ABC):
    """템플릿 엔진 기본 클래스"""

    def __init__(self):
        self.templates: Dict[str, BaseTemplate] = {}
        self.template_cache: Dict[str, BaseResponse] = {}

    @abstractmethod
    def load_templates(self, templates_dir: str) -> int:
        """템플릿 디렉토리에서 템플릿 로드"""
        pass

    def register_template(self, template: BaseTemplate) -> None:
        """템플릿 등록"""
        self.templates[template.template_id] = template

    def get_template(self, template_id: str) -> Optional[BaseTemplate]:
        """템플릿 조회"""
        return self.templates.get(template_id)

    def find_templates(
        self,
        structure_type: Optional[StructureType] = None,
        category: Optional[TemplateCategory] = None,
        complexity: Optional[TemplateComplexity] = None,
    ) -> List[BaseTemplate]:
        """조건에 맞는 템플릿 찾기"""
        results = []
        for template in self.templates.values():
            if structure_type and template.structure_type != structure_type:
                continue
            if category and template.category != category:
                continue
            if complexity and template.complexity != complexity:
                continue
            results.append(template)
        return results

    @abstractmethod
    def process_request(self, request: BaseRequest) -> BaseResponse:
        """요청 처리"""
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """템플릿 엔진 통계"""
        total_templates = len(self.templates)
        by_structure = {}
        by_category = {}
        by_complexity = {}

        for template in self.templates.values():
            # 구조별 통계
            structure = template.structure_type.value
            by_structure[structure] = by_structure.get(structure, 0) + 1

            # 카테고리별 통계
            category = template.category.value
            by_category[category] = by_category.get(category, 0) + 1

            # 복잡도별 통계
            complexity = template.complexity.value
            by_complexity[complexity] = by_complexity.get(complexity, 0) + 1

        return {
            "total_templates": total_templates,
            "by_structure": by_structure,
            "by_category": by_category,
            "by_complexity": by_complexity,
            "cache_size": len(self.template_cache),
        }
