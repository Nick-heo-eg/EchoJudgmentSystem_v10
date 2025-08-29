"""
🎯 FIST Templates - Frame, Insight, Strategy, Tactics 구조화된 프롬프트 시스템
EchoJudgmentSystem v10 확장 모듈 (BaseTemplate 기반 통합 구조)

FIST 구조:
- Frame: 문제 정의 및 맥락 설정
- Insight: 분석 및 이해 도출
- Strategy: 접근 방법 및 전략 수립
- Tactics: 구체적 실행 방안 제시

확장 구조:
- RISE: Reflect, Improve, Synthesize, Evolve
- DIR: Direction, Intention, Realization (방향성 기반 추론)
"""

# Core template system
from .fist_core import (
    FISTStructureType,
    TemplateCategory,
    TemplateComplexity,
    FISTComponent,
    FISTTemplate,
    FISTRequest,
    FISTResponse,
    FISTTemplateBuilder,
)

# Base template system (if available)
try:
    from .base_template import (
        BaseTemplate,
        BaseComponent,
        BaseRequest,
        BaseResponse,
        BaseTemplateBuilder,
        TemplateEngine,
        StructureType,
    )
except ImportError:
    # 폴백: core 클래스들을 사용
    BaseTemplate = FISTTemplate
    BaseComponent = FISTComponent
    BaseRequest = FISTRequest
    BaseResponse = FISTResponse
    BaseTemplateBuilder = FISTTemplateBuilder
    TemplateEngine = None
    StructureType = FISTStructureType

# FIST template system
from .fist_templates import (
    FISTTemplate,
    FISTComponent,
    FISTRequest,
    FISTResponse,
    FISTTemplateBuilder,
    create_basic_fist_template,
    create_decision_fist_template,
    create_creative_fist_template,
)

# RISE template system
from .rise_templates import (
    RISETemplate,
    RISEComponent,
    RISERequest,
    RISEResponse,
    RISETemplateBuilder,
    create_learning_rise_template,
    create_project_rise_template,
)

# DIR template system
from .dir_templates import (
    DIRTemplate,
    DIRComponent,
    DIRRequest,
    DIRResponse,
    DIRTemplateBuilder,
    create_goal_dir_template,
    create_problem_solving_dir_template,
)

# Template engine (if exists)
try:
    from .template_engine import FISTTemplateEngine, TemplateRenderer
except ImportError:
    FISTTemplateEngine = None
    TemplateRenderer = None

# Template selector (if exists)
try:
    from .template_selector import (
        TemplateSelectionStrategy,
        select_optimal_template,
        analyze_template_performance,
    )
except ImportError:
    TemplateSelectionStrategy = None
    select_optimal_template = None
    analyze_template_performance = None

__version__ = "2.0.0"  # Updated for BaseTemplate integration
__author__ = "EchoJudgmentSystem Team"


# 편의 함수들
def quick_fist_judgment(text: str, category: str = "decision") -> dict:
    """빠른 FIST 판단 실행"""
    template = create_decision_fist_template()
    context = {"input_text": text}

    return {
        "prompt": template.get_full_prompt(context),
        "confidence": template.calculate_confidence(context),
        "template_id": template.template_id,
        "structure_type": "fist",
    }


def quick_rise_learning(text: str) -> dict:
    """빠른 RISE 학습 분석"""
    template = create_learning_rise_template()
    context = {"input_text": text}

    return {
        "prompt": template.get_full_prompt(context),
        "confidence": template.calculate_confidence(context),
        "template_id": template.template_id,
        "structure_type": "rise",
    }


def quick_dir_goal(text: str) -> dict:
    """빠른 DIR 목표 달성 분석"""
    template = create_goal_dir_template()
    context = {"input_text": text}

    return {
        "prompt": template.get_full_prompt(context),
        "confidence": template.calculate_confidence(context),
        "template_id": template.template_id,
        "structure_type": "dir",
    }


def get_all_template_types() -> dict:
    """모든 템플릿 유형 정보 반환"""
    return {
        "structure_types": [t.value for t in StructureType],
        "categories": [c.value for c in TemplateCategory],
        "complexities": [x.value for x in TemplateComplexity],
        "available_builders": {
            "fist": "FISTTemplateBuilder",
            "rise": "RISETemplateBuilder",
            "dir": "DIRTemplateBuilder",
        },
        "factory_functions": {
            "fist": [
                "create_basic_fist_template",
                "create_decision_fist_template",
                "create_creative_fist_template",
            ],
            "rise": ["create_learning_rise_template", "create_project_rise_template"],
            "dir": ["create_goal_dir_template", "create_problem_solving_dir_template"],
        },
    }


# 모듈 메타데이터
__all__ = [
    # Base system
    "BaseTemplate",
    "BaseComponent",
    "BaseRequest",
    "BaseResponse",
    "BaseTemplateBuilder",
    "TemplateEngine",
    "StructureType",
    "TemplateCategory",
    "TemplateComplexity",
    "FISTStructureType",
    # FIST system
    "FISTTemplate",
    "FISTComponent",
    "FISTRequest",
    "FISTResponse",
    "FISTTemplateBuilder",
    "create_basic_fist_template",
    "create_decision_fist_template",
    "create_creative_fist_template",
    # RISE system
    "RISETemplate",
    "RISEComponent",
    "RISERequest",
    "RISEResponse",
    "RISETemplateBuilder",
    "create_learning_rise_template",
    "create_project_rise_template",
    # DIR system
    "DIRTemplate",
    "DIRComponent",
    "DIRRequest",
    "DIRResponse",
    "DIRTemplateBuilder",
    "create_goal_dir_template",
    "create_problem_solving_dir_template",
    # Legacy compatibility (if available)
    "FISTTemplateEngine",
    "TemplateRenderer",
    "TemplateSelectionStrategy",
    "select_optimal_template",
    "analyze_template_performance",
    # Convenience functions
    "quick_fist_judgment",
    "quick_rise_learning",
    "quick_dir_goal",
    "get_all_template_types",
]
