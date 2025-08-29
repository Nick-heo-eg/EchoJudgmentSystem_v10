"""
🎯 DIR Structure Templates - Direction, Intention, Realization
방향성과 목적 지향적 사고를 위한 DIR 구조 템플릿 시스템
BaseTemplate을 상속받은 DIR 전용 구현
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import math

from .base_template import (
    BaseComponent,
    BaseTemplate,
    BaseRequest,
    BaseResponse,
    BaseTemplateBuilder,
    StructureType,
    TemplateCategory,
    TemplateComplexity,
)


@dataclass
class DIRComponent(BaseComponent):
    """DIR 구조의 개별 구성요소"""

    directionality_vector: Optional[Dict[str, float]] = None  # DIR 특유의 방향성 벡터

    def __post_init__(self):
        if self.directionality_vector is None:
            self.directionality_vector = {"x": 0.0, "y": 0.0, "z": 0.0}

    def get_structure_specific_data(self) -> Dict[str, Any]:
        """DIR 구조별 특수 데이터"""
        return {
            "structure_type": "dir",
            "component_type": self.name.lower(),
            "directionality_vector": self.directionality_vector,
            "vector_magnitude": self.calculate_vector_magnitude(),
        }

    def render(self, context: Dict[str, Any]) -> str:
        """방향성 벡터 정보를 포함한 렌더링"""
        try:
            # 방향성 벡터 정보를 컨텍스트에 추가
            enhanced_context = {
                **context,
                **self.variables,
                "directionality_vector": self.directionality_vector,
                "vector_magnitude": self.calculate_vector_magnitude(),
            }

            rendered = self.prompt_template.format(**enhanced_context)
            return rendered.strip()
        except KeyError as e:
            return f"[DIR 템플릿 오류: {e} 변수 누락]"
        except Exception as e:
            return f"[DIR 렌더링 오류: {str(e)}]"

    def calculate_vector_magnitude(self) -> float:
        """방향성 벡터의 크기 계산"""
        if not self.directionality_vector:
            return 0.0

        x = self.directionality_vector.get("x", 0.0)
        y = self.directionality_vector.get("y", 0.0)
        z = self.directionality_vector.get("z", 0.0)

        return math.sqrt(x**2 + y**2 + z**2)

    def set_directionality_vector(self, x: float, y: float, z: float):
        """방향성 벡터 설정"""
        self.directionality_vector = {"x": x, "y": y, "z": z}


@dataclass
class DIRTemplate(BaseTemplate):
    """DIR 템플릿 (Direction, Intention, Realization)"""

    # DIR 특유 설정
    vector_alignment_threshold: float = 0.8  # 방향성 벡터 정렬 임계값
    goal_orientation_weight: float = 0.7  # 목표 지향성 가중치

    def __post_init__(self):
        if self.structure_type != StructureType.DIR:
            self.structure_type = StructureType.DIR

    def get_component_names(self) -> List[str]:
        """DIR 컴포넌트 이름 목록"""
        return ["direction", "intention", "realization"]

    def create_component(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> DIRComponent:
        """DIR 컴포넌트 생성"""
        return DIRComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )

    def get_direction(self) -> Optional[DIRComponent]:
        """Direction 컴포넌트 조회"""
        return self.get_component("direction")

    def get_intention(self) -> Optional[DIRComponent]:
        """Intention 컴포넌트 조회"""
        return self.get_component("intention")

    def get_realization(self) -> Optional[DIRComponent]:
        """Realization 컴포넌트 조회"""
        return self.get_component("realization")

    def get_full_prompt(self, context: Dict[str, Any] = None) -> str:
        """DIR 구조에 맞는 프롬프트 생성"""
        if context is None:
            context = {}

        prompt_parts = []

        # DIR 순서대로 렌더링
        for component_name in self.get_component_names():
            component = self.get_component(component_name)
            if component:
                if not component.optional or context.get(
                    f"include_{component_name}", True
                ):
                    rendered = component.render(context)
                    if rendered and not rendered.startswith("["):
                        # DIR 구조에 맞는 섹션 헤더 추가
                        section_header = self._get_section_header(component_name)
                        prompt_parts.append(f"{section_header}\n{rendered}")

        return "\n\n".join(prompt_parts)

    def _get_section_header(self, component_name: str) -> str:
        """컴포넌트별 섹션 헤더 반환"""
        headers = {
            "direction": "## 🧭 Direction (방향성)",
            "intention": "## 🎯 Intention (의도)",
            "realization": "## ⚡ Realization (실현)",
        }
        return headers.get(component_name.lower(), f"## {component_name.title()}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DIRTemplate":
        """딕셔너리에서 DIR 템플릿 생성"""
        template = cls(
            template_id=data["template_id"],
            name=data["name"],
            description=data["description"],
            structure_type=StructureType(data["structure_type"]),
            category=TemplateCategory(data["category"]),
            complexity=TemplateComplexity(data["complexity"]),
            metadata=data.get("metadata", {}),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if "created_at" in data
                else datetime.now()
            ),
            vector_alignment_threshold=data.get("settings", {}).get(
                "vector_alignment_threshold", 0.8
            ),
            goal_orientation_weight=data.get("settings", {}).get(
                "goal_orientation_weight", 0.7
            ),
        )

        # 컴포넌트 복원
        for comp_data in data.get("components", []):
            component = DIRComponent(
                name=comp_data["name"],
                description=comp_data["description"],
                prompt_template=comp_data["prompt_template"],
                variables=comp_data.get("variables", {}),
                weight=comp_data.get("weight", 1.0),
                optional=comp_data.get("optional", False),
                directionality_vector=comp_data.get("directionality_vector"),
            )
            template.add_component(component)

        return template


class DIRTemplateBuilder(BaseTemplateBuilder):
    """DIR 템플릿 빌더"""

    def __init__(self):
        super().__init__(StructureType.DIR)

    def with_direction(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> "DIRTemplateBuilder":
        """Direction 컴포넌트 추가"""
        component = DIRComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )
        self.components.append(component)
        return self

    def with_intention(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> "DIRTemplateBuilder":
        """Intention 컴포넌트 추가"""
        component = DIRComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )
        self.components.append(component)
        return self

    def with_realization(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> "DIRTemplateBuilder":
        """Realization 컴포넌트 추가"""
        component = DIRComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )
        self.components.append(component)
        return self

    def build(self) -> DIRTemplate:
        """DIR 템플릿 생성"""
        template = DIRTemplate(
            template_id=self.template_id,
            name=self.name,
            description=self.description,
            structure_type=self.structure_type,
            category=self.category,
            complexity=self.complexity,
            metadata=self.metadata,
        )

        # 컴포넌트 추가
        for component in self.components:
            template.add_component(component)

        return template


@dataclass
class DIRRequest(BaseRequest):
    """DIR 템플릿 요청"""

    def __post_init__(self):
        if self.structure_type is None:
            self.structure_type = StructureType.DIR


@dataclass
class DIRResponse(BaseResponse):
    """DIR 템플릿 응답"""

    def __post_init__(self):
        if self.structure_type != StructureType.DIR:
            self.structure_type = StructureType.DIR


# 편의 함수들
def create_goal_dir_template() -> DIRTemplate:
    """목표 달성용 DIR 템플릿"""
    return (
        DIRTemplateBuilder()
        .with_name("Goal Achievement DIR Template")
        .with_description("목표 달성을 위한 DIR 템플릿")
        .with_category(TemplateCategory.STRATEGIC)
        .with_complexity(TemplateComplexity.MODERATE)
        .with_direction(
            "Direction",
            "목표 방향성을 설정합니다",
            "목표: {input_text}\n방향성: {goal_direction}\n우선순위: {priorities}",
        )
        .with_intention(
            "Intention",
            "달성 의도를 명확화합니다",
            "달성 의도: {achievement_intention}\n동기: {motivation}\n기대 효과: {expected_outcomes}",
        )
        .with_realization(
            "Realization",
            "구체적 실현 방안을 수립합니다",
            "실행 계획: {execution_plan}\n필요 자원: {required_resources}\n마일스톤: {milestones}",
        )
        .build()
    )


def create_problem_solving_dir_template() -> DIRTemplate:
    """문제 해결용 DIR 템플릿"""
    return (
        DIRTemplateBuilder()
        .with_name("Problem Solving DIR Template")
        .with_description("문제 해결을 위한 DIR 템플릿")
        .with_category(TemplateCategory.PROBLEM_SOLVING)
        .with_complexity(TemplateComplexity.COMPLEX)
        .with_direction(
            "Direction",
            "문제 해결 방향을 설정합니다",
            "문제: {input_text}\n해결 방향: {solution_direction}\n접근 방식: {approach_method}",
        )
        .with_intention(
            "Intention",
            "해결 의도와 목적을 명확화합니다",
            "해결 의도: {solving_intention}\n목적: {purpose}\n성공 기준: {success_criteria}",
        )
        .with_realization(
            "Realization",
            "해결 방안의 실현 계획을 수립합니다",
            "해결 방안: {solution_plan}\n실행 단계: {implementation_steps}\n검증 방법: {validation_methods}",
        )
        .build()
    )


if __name__ == "__main__":
    # 테스트 코드
    print("🎯 DIR Templates 테스트")

    # 목표 달성용 템플릿 생성
    template = create_goal_dir_template()
    print(f"템플릿 생성: {template.name}")

    # 컨텍스트로 프롬프트 생성
    context = {
        "input_text": "새로운 기술 스택 마스터하기",
        "goal_direction": "실무 활용 가능한 수준까지 학습",
        "priorities": "핵심 기능 우선, 심화 학습은 후순위",
        "achievement_intention": "프로젝트에 즉시 적용 가능한 실력 확보",
        "motivation": "기술적 성장과 업무 효율성 향상",
        "expected_outcomes": "새로운 프로젝트 기회 확보",
        "execution_plan": "3개월 집중 학습 후 토이 프로젝트 진행",
        "required_resources": "온라인 강의, 실습 환경, 멘토링",
        "milestones": "1개월: 기초, 2개월: 중급, 3개월: 프로젝트 완성",
    }

    prompt = template.get_full_prompt(context)
    print(f"\n생성된 프롬프트:\n{prompt}")

    # 신뢰도 계산
    confidence = template.calculate_confidence(context)
    print(f"\n신뢰도: {confidence:.3f}")

    print("\n✅ DIR Templates 테스트 완료")
