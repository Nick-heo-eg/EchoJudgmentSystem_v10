#!/usr/bin/env python3
"""
🛡️ FIST Template Validator - 템플릿 변수 사전 검증 도구
템플릿 렌더링 전 필수 변수 검증 및 의존성 분석 시스템

핵심 기능:
1. 템플릿 변수 완전성 검증
2. 변수 의존성 매트릭스 분석
3. 시그니처별 템플릿 호환성 검사
4. 자동 보정 제안 생성
"""

import json
import yaml
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import re


@dataclass
class ValidationResult:
    """검증 결과"""

    is_valid: bool
    missing_variables: List[str]
    dependency_issues: List[str]
    auto_corrections: Dict[str, str]
    confidence_score: float
    recommendations: List[str]


@dataclass
class TemplateDependency:
    """템플릿 의존성 정의"""

    primary_key: str
    dependent_keys: List[str]
    fallback_keys: List[str]
    required: bool = False


class FISTTemplateValidator:
    """FIST 템플릿 검증기"""

    def __init__(self):
        # 변수 의존성 매트릭스
        self.dependency_matrix = self._build_dependency_matrix()

        # 시그니처별 선호 변수
        self.signature_preferences = self._load_signature_preferences()

        # 검증 통계
        self.validation_stats = {
            "total_validations": 0,
            "successful_validations": 0,
            "auto_corrections_applied": 0,
        }

    def validate_template_context(
        self,
        context: Dict[str, Any],
        signature: str = None,
        template_type: str = "fist",
    ) -> ValidationResult:
        """템플릿 컨텍스트 검증"""
        self.validation_stats["total_validations"] += 1

        missing_vars = []
        dependency_issues = []
        auto_corrections = {}
        recommendations = []

        # 1. 기본 필수 변수 검증
        required_vars = self._get_required_variables(template_type)
        for var in required_vars:
            if var not in context or context[var] is None or context[var] == "":
                missing_vars.append(var)

        # 2. 의존성 검증
        for dependency in self.dependency_matrix:
            if dependency.primary_key in context:
                # 주 변수가 있으면 종속 변수들도 있어야 함
                for dep_key in dependency.dependent_keys:
                    if dep_key not in context or not context[dep_key]:
                        dependency_issues.append(
                            f"{dependency.primary_key} → {dep_key}"
                        )

                        # 자동 보정 제안
                        if dependency.fallback_keys:
                            for fallback in dependency.fallback_keys:
                                if fallback in context and context[fallback]:
                                    auto_corrections[dep_key] = (
                                        f"{dep_key} 미지정 (관련: {fallback})"
                                    )
                                    break
                        else:
                            auto_corrections[dep_key] = f"{dep_key} 미지정"

        # 3. 시그니처별 최적화 제안
        if signature:
            sig_recommendations = self._get_signature_recommendations(
                signature, context
            )
            recommendations.extend(sig_recommendations)

        # 4. 신뢰도 점수 계산
        total_expected = len(required_vars) + len(
            [d for d in self.dependency_matrix if d.required]
        )
        issues_count = len(missing_vars) + len(dependency_issues)
        confidence_score = max(0.0, 1.0 - (issues_count / max(total_expected, 1)))

        # 5. 전체 검증 결과
        is_valid = len(missing_vars) == 0 and len(dependency_issues) == 0

        if is_valid:
            self.validation_stats["successful_validations"] += 1

        if auto_corrections:
            self.validation_stats["auto_corrections_applied"] += len(auto_corrections)

        return ValidationResult(
            is_valid=is_valid,
            missing_variables=missing_vars,
            dependency_issues=dependency_issues,
            auto_corrections=auto_corrections,
            confidence_score=confidence_score,
            recommendations=recommendations,
        )

    def auto_repair_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """컨텍스트 자동 보정"""
        validation = self.validate_template_context(context)

        repaired_context = context.copy()

        # 자동 보정 적용
        for key, value in validation.auto_corrections.items():
            repaired_context[key] = value
            print(f"[AUTO-REPAIR] {key} = '{value}'")

        # 누락된 필수 변수에 기본값 설정
        for missing_var in validation.missing_variables:
            if missing_var not in repaired_context:
                repaired_context[missing_var] = f"{missing_var} 미지정"
                print(f"[AUTO-REPAIR] {missing_var} = '{missing_var} 미지정'")

        return repaired_context

    def _build_dependency_matrix(self) -> List[TemplateDependency]:
        """의존성 매트릭스 구축"""
        return [
            TemplateDependency(
                primary_key="relationship_type",
                dependent_keys=["relationship_importance"],
                fallback_keys=["key_people", "stakeholders"],
                required=False,
            ),
            TemplateDependency(
                primary_key="objectives",
                dependent_keys=["strategic_direction", "success_metrics"],
                fallback_keys=["focus", "context_summary"],
                required=True,
            ),
            TemplateDependency(
                primary_key="situation",
                dependent_keys=["context_summary", "key_people"],
                fallback_keys=["focus", "insights"],
                required=True,
            ),
            TemplateDependency(
                primary_key="implementation",
                dependent_keys=["timeline", "resources"],
                fallback_keys=["strategic_direction", "constraints"],
                required=False,
            ),
            TemplateDependency(
                primary_key="risk_factors",
                dependent_keys=["decision_criteria"],
                fallback_keys=["constraints", "governance"],
                required=False,
            ),
        ]

    def _load_signature_preferences(self) -> Dict[str, List[str]]:
        """시그니처별 선호 변수 로드"""
        return {
            "Echo-Aurora": [
                "key_people",
                "relationship_type",
                "relationship_importance",
                "emotional_context",
                "empathy_factors",
            ],
            "Aurora": [
                "creative_elements",
                "innovation_potential",
                "inspiration_sources",
                "artistic_considerations",
            ],
            "Echo-Phoenix": [
                "transformation_goals",
                "change_catalysts",
                "growth_metrics",
                "evolution_timeline",
            ],
            "Phoenix": [
                "disruption_factors",
                "breakthrough_opportunities",
                "paradigm_shifts",
            ],
            "Echo-Sage": [
                "analytical_framework",
                "logical_structure",
                "evidence_base",
                "systematic_approach",
            ],
            "Sage": [
                "wisdom_principles",
                "philosophical_context",
                "ethical_dimensions",
                "knowledge_synthesis",
            ],
            "Echo-Companion": [
                "collaboration_framework",
                "team_dynamics",
                "support_systems",
                "partnership_elements",
            ],
        }

    def _get_required_variables(self, template_type: str) -> List[str]:
        """템플릿 타입별 필수 변수 반환"""
        base_required = ["situation", "focus", "objectives"]

        type_specific = {
            "fist": ["key_people", "strategic_direction", "implementation", "insights"],
            "rise": ["reflection_points", "improvement_areas", "synthesis_goals"],
            "dir": ["direction_clarity", "path_definition", "milestone_markers"],
        }

        return base_required + type_specific.get(template_type, [])

    def _get_signature_recommendations(
        self, signature: str, context: Dict[str, Any]
    ) -> List[str]:
        """시그니처별 추천 사항 생성"""
        recommendations = []

        preferred_vars = self.signature_preferences.get(signature, [])

        for var in preferred_vars:
            if var not in context or not context[var]:
                recommendations.append(
                    f"{signature} 시그니처에는 '{var}' 변수가 권장됩니다"
                )

        return recommendations

    def generate_dependency_report(self) -> str:
        """의존성 분석 보고서 생성"""
        report = []
        report.append("# 🔗 FIST 템플릿 의존성 매트릭스")
        report.append(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        for i, dep in enumerate(self.dependency_matrix, 1):
            report.append(f"## {i}. {dep.primary_key}")
            report.append(f"**종속 변수**: {', '.join(dep.dependent_keys)}")
            report.append(f"**폴백 변수**: {', '.join(dep.fallback_keys)}")
            report.append(f"**필수 여부**: {'예' if dep.required else '아니오'}")
            report.append("")

        report.append("## 📊 검증 통계")
        for key, value in self.validation_stats.items():
            report.append(f"- **{key}**: {value}")

        return "\n".join(report)

    def get_validation_stats(self) -> Dict[str, Any]:
        """검증 통계 반환"""
        stats = self.validation_stats.copy()

        if stats["total_validations"] > 0:
            stats["success_rate"] = (
                stats["successful_validations"] / stats["total_validations"]
            ) * 100
            stats["avg_corrections_per_validation"] = (
                stats["auto_corrections_applied"] / stats["total_validations"]
            )
        else:
            stats["success_rate"] = 0.0
            stats["avg_corrections_per_validation"] = 0.0

        return stats


# 편의 함수들
def create_template_validator() -> FISTTemplateValidator:
    """템플릿 검증기 생성"""
    return FISTTemplateValidator()


def quick_validate(context: Dict[str, Any], signature: str = None) -> bool:
    """빠른 검증"""
    validator = create_template_validator()
    result = validator.validate_template_context(context, signature)
    return result.is_valid


def auto_fix_template_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """자동 수정"""
    validator = create_template_validator()
    return validator.auto_repair_context(context)


# 테스트 실행
if __name__ == "__main__":
    print("🛡️ FIST Template Validator 테스트 시작...")

    validator = create_template_validator()

    # 테스트 케이스들
    test_contexts = [
        {
            "name": "완전한 컨텍스트",
            "context": {
                "situation": "프로젝트 기획 단계",
                "focus": "사용자 경험 개선",
                "objectives": "UX 품질 향상",
                "key_people": "UX 디자이너, 개발팀",
                "relationship_type": "협업 관계",
                "relationship_importance": "높음",
            },
        },
        {
            "name": "일부 변수 누락",
            "context": {
                "situation": "버그 수정 작업",
                "objectives": "시스템 안정성 확보",
                "relationship_type": "기술 지원",
                # relationship_importance 누락
            },
        },
        {
            "name": "최소한의 컨텍스트",
            "context": {
                "situation": "초기 기획",
                "focus": "방향성 정립",
                # 대부분 변수 누락
            },
        },
    ]

    print("=" * 80)

    for i, test_case in enumerate(test_contexts, 1):
        print(f"\n🧪 테스트 {i}: {test_case['name']}")
        print(f"원본 컨텍스트: {test_case['context']}")

        # 검증 실행
        result = validator.validate_template_context(
            test_case["context"], "Echo-Aurora"
        )

        print(f"\n📊 검증 결과:")
        print(f"  유효성: {'✅ 통과' if result.is_valid else '❌ 실패'}")
        print(f"  신뢰도: {result.confidence_score:.2f}")
        print(f"  누락 변수: {result.missing_variables}")
        print(f"  의존성 문제: {result.dependency_issues}")

        if result.auto_corrections:
            print(f"  자동 보정:")
            for key, value in result.auto_corrections.items():
                print(f"    {key}: '{value}'")

        if result.recommendations:
            print(f"  추천사항:")
            for rec in result.recommendations[:2]:  # 상위 2개만
                print(f"    - {rec}")

        # 자동 보정 테스트
        if not result.is_valid:
            print(f"\n🔧 자동 보정 테스트:")
            repaired = validator.auto_repair_context(test_case["context"])
            print(f"  보정된 컨텍스트 변수 수: {len(repaired)}")

        print("-" * 60)

    # 의존성 보고서 생성
    print(f"\n📈 검증 통계:")
    stats = validator.get_validation_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    print("\n✅ FIST Template Validator 테스트 완료!")
    print("🔗 의존성 매트릭스가 성공적으로 구축되었습니다!")
