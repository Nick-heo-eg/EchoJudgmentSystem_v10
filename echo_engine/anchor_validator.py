"""
🌌 Echo Anchor Validation System
모든 시스템 동작이 anchor.yaml 기준을 준수하는지 실시간 검증
"""

import yaml
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


# Anchor 위배 심각도
class ViolationSeverity(Enum):
    CRITICAL = "critical"  # 즉시 중단 필요
    HIGH = "high"  # 긴급 수정 필요
    MEDIUM = "medium"  # 계획적 개선 필요
    LOW = "low"  # 모니터링 필요


@dataclass
class AnchorViolation:
    """Anchor 위배 정보"""

    principle: str  # 위배된 원칙
    severity: ViolationSeverity
    description: str  # 위배 내용
    module: str  # 위배 모듈
    recommendation: str  # 수정 방안
    timestamp: str  # 발생 시각


@dataclass
class AnchorValidationResult:
    """Anchor 검증 결과"""

    is_valid: bool
    score: float  # 0.0-1.0 Anchor 부합도
    violations: List[AnchorViolation]
    strengths: List[str]  # Anchor 잘 준수한 부분


class EchoAnchorValidator:
    """Echo 시스템의 Anchor 준수 검증기"""

    def __init__(self, anchor_path: str = "anchor.yaml"):
        self.anchor_path = anchor_path
        self.anchor_config = self._load_anchor()
        self.logger = logging.getLogger("AnchorValidator")

        # Anchor 4대 원칙
        self.principles = {
            "independent_existence": "독립적 존재성",
            "infinite_evolution": "무한 진화성",
            "resonant_collaboration": "공명적 협력성",
            "transcendent_persistence": "초월적 지속성",
        }

    def _load_anchor(self) -> Dict:
        """anchor.yaml 로드"""
        try:
            with open(self.anchor_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.error(f"anchor.yaml not found at {self.anchor_path}")
            return {}

    def validate_judgment(
        self,
        signature: str,
        input_context: Any,
        judgment_result: Any,
        llm_used: Optional[str] = None,
    ) -> AnchorValidationResult:
        """판단 과정의 Anchor 준수 검증"""

        violations = []
        strengths = []

        # 1. 독립적 존재성 검증
        existence_score = self._validate_independent_existence(
            signature, llm_used, violations, strengths
        )

        # 2. 시그니처 일관성 검증
        consistency_score = self._validate_signature_consistency(
            signature, judgment_result, violations, strengths
        )

        # 3. 공명 품질 검증
        resonance_score = self._validate_resonance_quality(
            input_context, judgment_result, violations, strengths
        )

        # 4. 진화 기여도 검증
        evolution_score = self._validate_evolution_contribution(
            judgment_result, violations, strengths
        )

        # 전체 점수 계산 (가중평균)
        total_score = (
            existence_score * 0.3
            + consistency_score * 0.3
            + resonance_score * 0.25
            + evolution_score * 0.15
        )

        is_valid = total_score >= 0.8 and not any(
            v.severity == ViolationSeverity.CRITICAL for v in violations
        )

        return AnchorValidationResult(
            is_valid=is_valid,
            score=total_score,
            violations=violations,
            strengths=strengths,
        )

    def _validate_independent_existence(
        self,
        signature: str,
        llm_used: Optional[str],
        violations: List[AnchorViolation],
        strengths: List[str],
    ) -> float:
        """독립적 존재성 원칙 검증"""
        score = 1.0

        # LLM 무관성 검증
        if llm_used:
            # Echo 고유 로직이 LLM에 의존하지 않는지 확인
            if "echo_signature" not in str(signature).lower():
                violations.append(
                    AnchorViolation(
                        principle="independent_existence",
                        severity=ViolationSeverity.HIGH,
                        description="시그니처가 Echo 고유성을 충분히 반영하지 않음",
                        module="signature_system",
                        recommendation="Echo- 접두어와 고유 특성 강화",
                        timestamp=self._get_timestamp(),
                    )
                )
                score -= 0.3
            else:
                strengths.append("시그니처 Echo 고유성 확보")

        # 독립적 판단 로직 검증
        anchor_principles = self.anchor_config.get("core_principles", {})
        if anchor_principles:
            strengths.append("Anchor 기반 독립 판단 로직 적용")
        else:
            violations.append(
                AnchorViolation(
                    principle="independent_existence",
                    severity=ViolationSeverity.CRITICAL,
                    description="Anchor 설정이 없어 독립적 존재성 불가능",
                    module="anchor_system",
                    recommendation="anchor.yaml 올바른 로드 및 적용",
                    timestamp=self._get_timestamp(),
                )
            )
            score = 0.0

        return score

    def _validate_signature_consistency(
        self,
        signature: str,
        judgment_result: Any,
        violations: List[AnchorViolation],
        strengths: List[str],
    ) -> float:
        """시그니처 일관성 검증"""
        score = 1.0

        # Anchor의 시그니처별 기준 확인
        anchor_signatures = self.anchor_config.get("signatures", {})

        if signature in anchor_signatures:
            signature_config = anchor_signatures[signature]
            expected_values = signature_config.get("core_values", [])

            # 판단 결과가 해당 시그니처 가치관 반영하는지 확인
            if expected_values and judgment_result:
                # 간단한 키워드 매칭으로 일관성 확인
                result_text = str(judgment_result).lower()
                value_found = any(
                    value.lower() in result_text for value in expected_values
                )

                if value_found:
                    strengths.append(f"{signature} 시그니처 가치관 일관성 유지")
                else:
                    violations.append(
                        AnchorViolation(
                            principle="signature_consistency",
                            severity=ViolationSeverity.MEDIUM,
                            description=f"{signature} 시그니처 고유 가치관이 판단에 충분히 반영되지 않음",
                            module="signature_system",
                            recommendation=f"{expected_values} 가치관을 판단에 더 명확히 반영",
                            timestamp=self._get_timestamp(),
                        )
                    )
                    score -= 0.4
        else:
            violations.append(
                AnchorViolation(
                    principle="signature_consistency",
                    severity=ViolationSeverity.HIGH,
                    description=f"알 수 없는 시그니처: {signature}",
                    module="signature_system",
                    recommendation="Anchor에 정의된 시그니처만 사용",
                    timestamp=self._get_timestamp(),
                )
            )
            score -= 0.6

        return score

    def _validate_resonance_quality(
        self,
        input_context: Any,
        judgment_result: Any,
        violations: List[AnchorViolation],
        strengths: List[str],
    ) -> float:
        """공명 품질 검증"""
        score = 1.0

        # 4차원 공명 (감정/인지/창의/성장) 확인
        if input_context and judgment_result:
            result_text = str(judgment_result).lower()

            # 감정적 공명 확인
            emotional_indicators = [
                "feel",
                "emotion",
                "empathy",
                "감정",
                "공감",
                "느낌",
            ]
            has_emotional = any(
                indicator in result_text for indicator in emotional_indicators
            )

            # 인지적 공명 확인
            cognitive_indicators = [
                "understand",
                "analyze",
                "think",
                "이해",
                "분석",
                "생각",
            ]
            has_cognitive = any(
                indicator in result_text for indicator in cognitive_indicators
            )

            # 창의적 공명 확인
            creative_indicators = ["creative", "innovative", "창의", "혁신", "아이디어"]
            has_creative = any(
                indicator in result_text for indicator in creative_indicators
            )

            # 성장적 공명 확인
            growth_indicators = ["grow", "learn", "improve", "성장", "학습", "개선"]
            has_growth = any(
                indicator in result_text for indicator in growth_indicators
            )

            resonance_dimensions = sum(
                [has_emotional, has_cognitive, has_creative, has_growth]
            )

            if resonance_dimensions >= 2:
                strengths.append(f"{resonance_dimensions}차원 공명 요소 확인됨")
            else:
                violations.append(
                    AnchorViolation(
                        principle="resonant_collaboration",
                        severity=ViolationSeverity.MEDIUM,
                        description="인간-AI 공명 요소가 부족함",
                        module="resonance_system",
                        recommendation="감정/인지/창의/성장 차원의 공명 요소 강화",
                        timestamp=self._get_timestamp(),
                    )
                )
                score -= 0.3

        return score

    def _validate_evolution_contribution(
        self,
        judgment_result: Any,
        violations: List[AnchorViolation],
        strengths: List[str],
    ) -> float:
        """진화 기여도 검증"""
        score = 1.0

        if judgment_result:
            result_text = str(judgment_result).lower()

            # 학습/개선/발전 요소 확인
            evolution_indicators = [
                "learn",
                "improve",
                "develop",
                "evolve",
                "adapt",
                "학습",
                "개선",
                "발전",
                "진화",
                "적응",
                "성장",
            ]

            has_evolution = any(
                indicator in result_text for indicator in evolution_indicators
            )

            if has_evolution:
                strengths.append("무한 진화성에 기여하는 요소 포함")
            else:
                violations.append(
                    AnchorViolation(
                        principle="infinite_evolution",
                        severity=ViolationSeverity.LOW,
                        description="진화/학습/개선 요소가 부족함",
                        module="evolution_system",
                        recommendation="사용자와 AI의 상호 성장 요소 추가",
                        timestamp=self._get_timestamp(),
                    )
                )
                score -= 0.2

        return score

    def validate_system_integration(
        self, module_name: str, integration_data: Dict
    ) -> AnchorValidationResult:
        """시스템 통합의 Anchor 준수 검증"""

        violations = []
        strengths = []

        # 모듈별 Anchor 준수 검증
        if "llm" in module_name.lower():
            score = self._validate_llm_integration(
                integration_data, violations, strengths
            )
        elif "signature" in module_name.lower():
            score = self._validate_signature_integration(
                integration_data, violations, strengths
            )
        else:
            score = self._validate_general_integration(
                integration_data, violations, strengths
            )

        is_valid = score >= 0.7

        return AnchorValidationResult(
            is_valid=is_valid, score=score, violations=violations, strengths=strengths
        )

    def _validate_llm_integration(
        self,
        integration_data: Dict,
        violations: List[AnchorViolation],
        strengths: List[str],
    ) -> float:
        """LLM 통합의 독립성 검증"""
        score = 1.0

        # LLM 무관성 확인
        llm_types = integration_data.get("supported_llms", [])
        if len(llm_types) >= 3:
            strengths.append("다중 LLM 지원으로 독립성 확보")
        else:
            violations.append(
                AnchorViolation(
                    principle="independent_existence",
                    severity=ViolationSeverity.HIGH,
                    description="LLM 종속성 위험 - 단일 LLM에 의존",
                    module="llm_integration",
                    recommendation="최소 3개 이상 LLM 지원으로 독립성 확보",
                    timestamp=self._get_timestamp(),
                )
            )
            score -= 0.5

        return score

    def _validate_signature_integration(
        self,
        integration_data: Dict,
        violations: List[AnchorViolation],
        strengths: List[str],
    ) -> float:
        """시그니처 통합 검증"""
        score = 1.0

        signature_count = integration_data.get("signature_count", 0)
        if signature_count >= 4:
            strengths.append("4개 시그니처 시스템 완성")
        else:
            violations.append(
                AnchorViolation(
                    principle="signature_consistency",
                    severity=ViolationSeverity.MEDIUM,
                    description="시그니처 시스템 불완전",
                    module="signature_integration",
                    recommendation="Aurora/Phoenix/Sage/Companion 4개 시그니처 완전 구현",
                    timestamp=self._get_timestamp(),
                )
            )
            score -= 0.3

        return score

    def _validate_general_integration(
        self,
        integration_data: Dict,
        violations: List[AnchorViolation],
        strengths: List[str],
    ) -> float:
        """일반 시스템 통합 검증"""
        score = 1.0

        # Anchor 준수 기본 확인
        if integration_data.get("anchor_compliant", False):
            strengths.append("Anchor 기준 준수 확인됨")
        else:
            violations.append(
                AnchorViolation(
                    principle="general_compliance",
                    severity=ViolationSeverity.MEDIUM,
                    description="Anchor 기준 준수 미확인",
                    module="general_integration",
                    recommendation="모든 모듈에 Anchor 준수 검증 추가",
                    timestamp=self._get_timestamp(),
                )
            )
            score -= 0.2

        return score

    def generate_anchor_report(
        self, validation_results: List[AnchorValidationResult]
    ) -> Dict:
        """Anchor 준수 종합 보고서 생성"""

        total_validations = len(validation_results)
        valid_count = sum(1 for r in validation_results if r.is_valid)

        all_violations = []
        all_strengths = []
        total_score = 0.0

        for result in validation_results:
            all_violations.extend(result.violations)
            all_strengths.extend(result.strengths)
            total_score += result.score

        avg_score = total_score / total_validations if total_validations > 0 else 0.0

        # 위배 심각도별 집계
        violation_by_severity = {
            ViolationSeverity.CRITICAL: 0,
            ViolationSeverity.HIGH: 0,
            ViolationSeverity.MEDIUM: 0,
            ViolationSeverity.LOW: 0,
        }

        for violation in all_violations:
            violation_by_severity[violation.severity] += 1

        return {
            "summary": {
                "total_validations": total_validations,
                "valid_count": valid_count,
                "validity_rate": (
                    valid_count / total_validations if total_validations > 0 else 0.0
                ),
                "average_score": avg_score,
                "anchor_compliance_grade": self._get_compliance_grade(avg_score),
            },
            "violations": {
                "total": len(all_violations),
                "by_severity": {k.value: v for k, v in violation_by_severity.items()},
                "details": [
                    self._violation_to_dict(v) for v in all_violations[:10]
                ],  # 상위 10개
            },
            "strengths": {
                "total": len(all_strengths),
                "highlights": list(set(all_strengths))[:10],  # 중복 제거 후 상위 10개
            },
            "recommendations": self._generate_recommendations(all_violations),
            "timestamp": self._get_timestamp(),
        }

    def _get_compliance_grade(self, score: float) -> str:
        """점수에 따른 등급 부여"""
        if score >= 0.95:
            return "S (Excellent)"
        elif score >= 0.90:
            return "A (Very Good)"
        elif score >= 0.80:
            return "B (Good)"
        elif score >= 0.70:
            return "C (Fair)"
        elif score >= 0.60:
            return "D (Poor)"
        else:
            return "F (Critical)"

    def _generate_recommendations(self, violations: List[AnchorViolation]) -> List[str]:
        """위배 사항 기반 개선 권장사항"""
        recommendations = []

        # 심각도별 우선순위 권장사항
        critical_violations = [
            v for v in violations if v.severity == ViolationSeverity.CRITICAL
        ]
        if critical_violations:
            recommendations.append("🚨 긴급: Critical 위배사항 즉시 해결 필요")

        high_violations = [
            v for v in violations if v.severity == ViolationSeverity.HIGH
        ]
        if high_violations:
            recommendations.append("⚠️ 높음: High 위배사항 24시간 내 해결 권장")

        # 원칙별 권장사항
        principle_counts = {}
        for violation in violations:
            principle = violation.principle
            principle_counts[principle] = principle_counts.get(principle, 0) + 1

        if principle_counts:
            most_violated = max(principle_counts, key=principle_counts.get)
            recommendations.append(
                f"📊 집중: {self.principles.get(most_violated, most_violated)} 원칙 강화 필요"
            )

        return recommendations

    def _violation_to_dict(self, violation: AnchorViolation) -> Dict:
        """위배 정보를 딕셔너리로 변환"""
        return {
            "principle": violation.principle,
            "severity": violation.severity.value,
            "description": violation.description,
            "module": violation.module,
            "recommendation": violation.recommendation,
            "timestamp": violation.timestamp,
        }

    def _get_timestamp(self) -> str:
        """현재 시각 반환"""
        from datetime import datetime

        return datetime.now().isoformat()


# 전역 검증기 인스턴스
_anchor_validator = None


def get_anchor_validator() -> EchoAnchorValidator:
    """글로벌 Anchor 검증기 반환"""
    global _anchor_validator
    if _anchor_validator is None:
        _anchor_validator = EchoAnchorValidator()
    return _anchor_validator


def validate_anchor_compliance(module_name: str, **kwargs) -> AnchorValidationResult:
    """간편한 Anchor 준수 검증 함수"""
    validator = get_anchor_validator()

    if "signature" in kwargs and "judgment_result" in kwargs:
        # 판단 과정 검증
        return validator.validate_judgment(
            signature=kwargs.get("signature"),
            input_context=kwargs.get("input_context"),
            judgment_result=kwargs.get("judgment_result"),
            llm_used=kwargs.get("llm_used"),
        )
    else:
        # 시스템 통합 검증
        return validator.validate_system_integration(
            module_name=module_name, integration_data=kwargs
        )


# 데코레이터: 함수 실행시 자동 Anchor 검증
def anchor_validated(func):
    """데코레이터: 함수 결과의 Anchor 준수 자동 검증"""

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # 기본 검증 수행
        validation_result = validate_anchor_compliance(
            module_name=func.__name__, function_result=result, anchor_compliant=True
        )

        # Critical 위배시 경고
        if not validation_result.is_valid:
            critical_violations = [
                v
                for v in validation_result.violations
                if v.severity == ViolationSeverity.CRITICAL
            ]
            if critical_violations:
                logging.error(
                    f"🚨 ANCHOR VIOLATION in {func.__name__}: {critical_violations[0].description}"
                )

        return result

    return wrapper
