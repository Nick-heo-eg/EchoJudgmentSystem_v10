"""
🎯 FIST Templates - Frame, Insight, Strategy, Tactics 구조화 시스템
BaseTemplate을 상속받은 FIST 전용 구현
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
class FISTComponent(BaseComponent):
    """FIST 구조의 개별 구성요소"""

    def get_structure_specific_data(self) -> Dict[str, Any]:
        """FIST 구조별 특수 데이터"""
        return {"structure_type": "fist", "component_type": self.name.lower()}


@dataclass
class FISTTemplate(BaseTemplate):
    """FIST 템플릿 (Frame, Insight, Strategy, Tactics)"""

    def __post_init__(self):
        if self.structure_type != StructureType.FIST:
            self.structure_type = StructureType.FIST

    def get_component_names(self) -> List[str]:
        """FIST 컴포넌트 이름 목록"""
        return ["frame", "insight", "strategy", "tactics"]

    def create_component(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> FISTComponent:
        """FIST 컴포넌트 생성"""
        return FISTComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )

    def get_frame(self) -> Optional[FISTComponent]:
        """Frame 컴포넌트 조회"""
        return self.get_component("frame")

    def get_insight(self) -> Optional[FISTComponent]:
        """Insight 컴포넌트 조회"""
        return self.get_component("insight")

    def get_strategy(self) -> Optional[FISTComponent]:
        """Strategy 컴포넌트 조회"""
        return self.get_component("strategy")

    def get_tactics(self) -> Optional[FISTComponent]:
        """Tactics 컴포넌트 조회"""
        return self.get_component("tactics")

    def get_full_prompt(self, context: Dict[str, Any] = None) -> str:
        """FIST 구조에 맞는 프롬프트 생성"""
        if context is None:
            context = {}

        prompt_parts = []

        # FIST 순서대로 렌더링
        for component_name in self.get_component_names():
            component = self.get_component(component_name)
            if component:
                if not component.optional or context.get(
                    f"include_{component_name}", True
                ):
                    rendered = component.render(context)
                    if rendered and not rendered.startswith("["):
                        # FIST 구조에 맞는 섹션 헤더 추가
                        section_header = self._get_section_header(component_name)
                        prompt_parts.append(f"{section_header}\n{rendered}")

        return "\n\n".join(prompt_parts)

    def _get_section_header(self, component_name: str) -> str:
        """컴포넌트별 섹션 헤더 반환"""
        headers = {
            "frame": "## 🖼️ Frame (맥락 설정)",
            "insight": "## 💡 Insight (통찰 발견)",
            "strategy": "## 🎯 Strategy (전략 수립)",
            "tactics": "## ⚡ Tactics (실행 전술)",
        }
        return headers.get(component_name.lower(), f"## {component_name.title()}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FISTTemplate":
        """딕셔너리에서 FIST 템플릿 생성"""
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
            component = FISTComponent(
                name=comp_data["name"],
                description=comp_data["description"],
                prompt_template=comp_data["prompt_template"],
                variables=comp_data.get("variables", {}),
                weight=comp_data.get("weight", 1.0),
                optional=comp_data.get("optional", False),
            )
            template.add_component(component)

        return template


class FISTTemplateBuilder(BaseTemplateBuilder):
    """FIST 템플릿 빌더"""

    def __init__(self):
        super().__init__(StructureType.FIST)

    def with_frame(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> "FISTTemplateBuilder":
        """Frame 컴포넌트 추가"""
        component = FISTComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )
        self.components.append(component)
        return self

    def with_insight(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> "FISTTemplateBuilder":
        """Insight 컴포넌트 추가"""
        component = FISTComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )
        self.components.append(component)
        return self

    def with_strategy(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> "FISTTemplateBuilder":
        """Strategy 컴포넌트 추가"""
        component = FISTComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )
        self.components.append(component)
        return self

    def with_tactics(
        self, name: str, description: str, prompt_template: str, **kwargs
    ) -> "FISTTemplateBuilder":
        """Tactics 컴포넌트 추가"""
        component = FISTComponent(
            name=name,
            description=description,
            prompt_template=prompt_template,
            **kwargs,
        )
        self.components.append(component)
        return self

    def build(self) -> FISTTemplate:
        """FIST 템플릿 생성"""
        template = FISTTemplate(
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
class FISTRequest(BaseRequest):
    """FIST 템플릿 요청"""

    def __post_init__(self):
        if self.structure_type is None:
            self.structure_type = StructureType.FIST


@dataclass
class FISTResponse(BaseResponse):
    """FIST 템플릿 응답"""

    def __post_init__(self):
        if self.structure_type != StructureType.FIST:
            self.structure_type = StructureType.FIST


# 편의 함수들
def create_basic_fist_template(
    name: str,
    description: str,
    category: TemplateCategory = TemplateCategory.DECISION,
    complexity: TemplateComplexity = TemplateComplexity.MODERATE,
) -> FISTTemplate:
    """기본 FIST 템플릿 생성"""
    return (
        FISTTemplateBuilder()
        .with_name(name)
        .with_description(description)
        .with_category(category)
        .with_complexity(complexity)
        .with_frame(
            "Frame",
            "상황과 맥락을 설정합니다",
            "현재 상황: {input_text}\n문맥: {context}\n목표: {goal}",
        )
        .with_insight(
            "Insight",
            "핵심 통찰을 발견합니다",
            "분석 결과: {analysis}\n핵심 포인트: {key_points}",
        )
        .with_strategy(
            "Strategy",
            "전략적 방향을 수립합니다",
            "전략 방향: {strategy_direction}\n접근 방법: {approach}",
        )
        .with_tactics(
            "Tactics",
            "구체적 실행 방안을 제시합니다",
            "실행 계획: {execution_plan}\n다음 단계: {next_steps}",
        )
        .build()
    )


def create_decision_fist_template() -> FISTTemplate:
    """의사결정용 FIST 템플릿"""
    return create_basic_fist_template(
        "Decision FIST Template",
        "의사결정을 위한 구조화된 FIST 템플릿",
        TemplateCategory.DECISION,
        TemplateComplexity.MODERATE,
    )


def create_creative_fist_template() -> FISTTemplate:
    """창작용 FIST 템플릿"""
    return (
        FISTTemplateBuilder()
        .with_name("Creative FIST Template")
        .with_description("창의적 사고를 위한 FIST 템플릿")
        .with_category(TemplateCategory.CREATIVE)
        .with_complexity(TemplateComplexity.COMPLEX)
        .with_frame(
            "Frame",
            "창작 맥락 설정",
            "창작 주제: {input_text}\n장르/스타일: {genre}\n목적: {purpose}",
        )
        .with_insight(
            "Insight",
            "창의적 통찰 발견",
            "아이디어 핵심: {core_idea}\n독창성 포인트: {uniqueness}\n영감 소스: {inspiration}",
        )
        .with_strategy(
            "Strategy",
            "창작 전략 수립",
            "창작 방향: {creative_direction}\n구조/형식: {structure}\n스타일: {style}",
        )
        .with_tactics(
            "Tactics",
            "구체적 창작 방법",
            "창작 기법: {techniques}\n실행 단계: {steps}\n완성 목표: {completion_goal}",
        )
        .build()
    )


if __name__ == "__main__":
    # 테스트 코드
    print("🎯 FIST Templates 테스트")

    # 기본 템플릿 생성
    template = create_decision_fist_template()
    print(f"템플릿 생성: {template.name}")

    # 컨텍스트로 프롬프트 생성
    context = {
        "input_text": "새로운 프로젝트 선택",
        "context": "회사에서 두 개의 프로젝트 중 선택해야 함",
        "goal": "최적의 프로젝트 선택",
        "analysis": "리스크와 수익성 분석 완료",
        "key_points": "장기적 성장성과 팀 역량",
        "strategy_direction": "리스크 최소화하면서 성장 극대화",
        "approach": "단계적 접근과 지속적 모니터링",
        "execution_plan": "3개월 파일럿 후 본격 진행",
        "next_steps": "팀 구성 및 초기 계획 수립",
    }

    prompt = template.get_full_prompt(context)
    print(f"\n생성된 프롬프트:\n{prompt}")

    # 신뢰도 계산
    confidence = template.calculate_confidence(context)
    print(f"\n신뢰도: {confidence:.3f}")

    print("\n✅ FIST Templates 테스트 완료")
