"""
🌟 RISE Structure Templates - Reflect, Improve, Synthesize, Evolve
진화적 사고와 지속적 개선을 위한 RISE 구조 템플릿 시스템
BaseTemplate을 상속받은 RISE 전용 구현
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

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
class RISEComponent(BaseComponent):
    """RISE 구조의 개별 구성요소"""

    def get_structure_specific_data(self) -> Dict[str, Any]:
        """RISE 구조별 특수 데이터"""
        return {
            "structure_type": "rise",
            "component_type": self.name.lower(),
            "evolution_stage": self.name.lower(),
        }


@dataclass
class RISETemplate(BaseTemplate):
    """RISE 템플릿 (Reflect, Improve, Synthesize, Evolve)"""

    def __post_init__(self):
        if self.structure_type != StructureType.RISE:
            self.structure_type = StructureType.RISE

    def get_component_names(self) -> List[str]:
        """RISE 컴포넌트 이름 목록"""
        return ["reflect", "improve", "synthesize", "evolve"]

    def create_component(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> RISEComponent:
        """RISE 컴포넌트 생성"""
        return RISEComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )

    def get_reflect(self) -> Optional[RISEComponent]:
        """Reflect 컴포넌트 조회"""
        return self.get_component("reflect")

    def get_improve(self) -> Optional[RISEComponent]:
        """Improve 컴포넌트 조회"""
        return self.get_component("improve")

    def get_synthesize(self) -> Optional[RISEComponent]:
        """Synthesize 컴포넌트 조회"""
        return self.get_component("synthesize")

    def get_evolve(self) -> Optional[RISEComponent]:
        """Evolve 컴포넌트 조회"""
        return self.get_component("evolve")

    def get_full_prompt(self, context: Dict[str, Any] = None) -> str:
        """RISE 구조에 맞는 프롬프트 생성"""
        if context is None:
            context = {}

        prompt_parts = []

        # RISE 순서대로 렌더링
        for component_name in self.get_component_names():
            component = self.get_component(component_name)
            if component:
                if not component.optional or context.get(
                    f"include_{component_name}", True
                ):
                    rendered = component.render(context)
                    if rendered and not rendered.startswith("["):
                        # RISE 구조에 맞는 섹션 헤더 추가
                        section_header = self._get_section_header(component_name)
                        prompt_parts.append(f"{section_header}\n{rendered}")

        return "\n\n".join(prompt_parts)

    def _get_section_header(self, component_name: str) -> str:
        """컴포넌트별 섹션 헤더 반환"""
        headers = {
            "reflect": "## 🔍 Reflect (성찰)",
            "improve": "## 📈 Improve (개선)",
            "synthesize": "## 🔗 Synthesize (통합)",
            "evolve": "## 🌱 Evolve (진화)",
        }
        return headers.get(component_name.lower(), f"## {component_name.title()}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RISETemplate":
        """딕셔너리에서 RISE 템플릿 생성"""
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
        )

        # 컴포넌트 복원
        for comp_data in data.get("components", []):
            component = RISEComponent(
                name=comp_data["name"],
                description=comp_data["description"],
                prompt_template=comp_data["prompt_template"],
                variables=comp_data.get("variables", {}),
                weight=comp_data.get("weight", 1.0),
                optional=comp_data.get("optional", False),
            )
            template.add_component(component)

        return template


class RISETemplateBuilder(BaseTemplateBuilder):
    """RISE 템플릿 빌더"""

    def __init__(self):
        super().__init__(StructureType.RISE)

    def with_reflect(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> "RISETemplateBuilder":
        """Reflect 컴포넌트 추가"""
        component = RISEComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )
        self.components.append(component)
        return self

    def with_improve(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> "RISETemplateBuilder":
        """Improve 컴포넌트 추가"""
        component = RISEComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )
        self.components.append(component)
        return self

    def with_synthesize(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> "RISETemplateBuilder":
        """Synthesize 컴포넌트 추가"""
        component = RISEComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )
        self.components.append(component)
        return self

    def with_evolve(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> "RISETemplateBuilder":
        """Evolve 컴포넌트 추가"""
        component = RISEComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )
        self.components.append(component)
        return self

    def build(self) -> RISETemplate:
        """RISE 템플릿 생성"""
        template = RISETemplate(
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
class RISERequest(BaseRequest):
    """RISE 템플릿 요청"""

    def __post_init__(self):
        if self.structure_type is None:
            self.structure_type = StructureType.RISE


@dataclass
class RISEResponse(BaseResponse):
    """RISE 템플릿 응답"""

    def __post_init__(self):
        if self.structure_type != StructureType.RISE:
            self.structure_type = StructureType.RISE


# 편의 함수들
def create_learning_rise_template() -> RISETemplate:
    """학습용 RISE 템플릿"""
    return (
        RISETemplateBuilder()
        .with_name("Learning RISE Template")
        .with_description("학습과 개선을 위한 RISE 템플릿")
        .with_category(TemplateCategory.ANALYTICAL)
        .with_complexity(TemplateComplexity.MODERATE)
        .with_reflect(
            "Reflect",
            "현재 상황과 경험을 성찰합니다",
            "현재 상황: {input_text}\n경험한 것: {experience}\n느낀 점: {feelings}",
        )
        .with_improve(
            "Improve",
            "개선 방안을 모색합니다",
            "개선 필요점: {improvement_needs}\n개선 방향: {improvement_direction}\n구체적 방법: {methods}",
        )
        .with_synthesize(
            "Synthesize",
            "정보를 통합하고 패턴을 찾습니다",
            "핵심 패턴: {patterns}\n통합 인사이트: {insights}\n연결고리: {connections}",
        )
        .with_evolve(
            "Evolve",
            "진화된 접근법을 개발합니다",
            "진화 방향: {evolution_direction}\n새로운 접근: {new_approach}\n다음 단계: {next_steps}",
        )
        .build()
    )


def create_project_rise_template() -> RISETemplate:
    """프로젝트용 RISE 템플릿"""
    return (
        RISETemplateBuilder()
        .with_name("Project RISE Template")
        .with_description("프로젝트 발전을 위한 RISE 템플릿")
        .with_category(TemplateCategory.STRATEGIC)
        .with_complexity(TemplateComplexity.COMPLEX)
        .with_reflect(
            "Reflect",
            "프로젝트 현황을 성찰합니다",
            "프로젝트 상태: {input_text}\n진행 현황: {progress}\n성과와 문제점: {achievements_issues}",
        )
        .with_improve(
            "Improve",
            "프로젝트 개선방안을 수립합니다",
            "개선 영역: {improvement_areas}\n최적화 방법: {optimization}\n리소스 효율화: {resource_efficiency}",
        )
        .with_synthesize(
            "Synthesize",
            "프로젝트 요소들을 통합합니다",
            "핵심 목표 재정의: {goal_refinement}\n통합 전략: {integration_strategy}\n시너지 포인트: {synergy_points}",
        )
        .with_evolve(
            "Evolve",
            "프로젝트의 진화 방향을 설정합니다",
            "진화 목표: {evolution_goals}\n혁신 방안: {innovation_plans}\n장기 비전: {long_term_vision}",
        )
        .build()
    )


if __name__ == "__main__":
    # 테스트 코드
    print("🌟 RISE Templates 테스트")

    # 학습용 템플릿 생성
    template = create_learning_rise_template()
    print(f"템플릿 생성: {template.name}")

    # 컨텍스트로 프롬프트 생성
    context = {
        "input_text": "새로운 프로그래밍 언어 학습",
        "experience": "Python 기초 문법 학습 완료",
        "feelings": "어렵지만 흥미로움",
        "improvement_needs": "실전 프로젝트 경험 부족",
        "improvement_direction": "실습 중심 학습",
        "methods": "토이 프로젝트 진행",
        "patterns": "이론→실습→피드백 사이클",
        "insights": "반복 학습의 중요성",
        "connections": "기존 지식과의 연계",
        "evolution_direction": "심화 학습과 응용",
        "new_approach": "프로젝트 기반 학습",
        "next_steps": "웹 앱 개발 프로젝트 시작",
    }

    prompt = template.get_full_prompt(context)
    print(f"\n생성된 프롬프트:\n{prompt}")

    # 신뢰도 계산
    confidence = template.calculate_confidence(context)
    print(f"\n신뢰도: {confidence:.3f}")

    print("\n✅ RISE Templates 테스트 완료")
