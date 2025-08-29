"""
🎪 Echo Signature Anchor Compatibility Validator
시그니처 시스템이 anchor.yaml 기준을 완벽히 준수하는지 검증
"""

import yaml
from typing import Dict, List, Any, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class SignatureAnchorReport:
    """시그니처 Anchor 호환성 보고서"""

    signature_id: str
    anchor_compliance_score: float  # 0.0-1.0
    missing_elements: List[str]
    conflicting_elements: List[str]
    strengths: List[str]
    recommendations: List[str]


class EchoSignatureAnchorValidator:
    """시그니처 시스템의 Anchor 준수 검증기"""

    def __init__(self, anchor_path: str = "anchor.yaml"):
        self.anchor_path = anchor_path
        self.anchor_config = self._load_anchor()

        # Anchor에서 정의된 시그니처 기준
        self.anchor_signatures = self.anchor_config.get("signatures", {})

    def _load_anchor(self) -> Dict:
        """anchor.yaml 로드"""
        try:
            with open(self.anchor_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️ {self.anchor_path} not found")
            return {}

    def validate_signature_system(
        self, signature_config_path: str = "data/signature.yaml"
    ) -> List[SignatureAnchorReport]:
        """전체 시그니처 시스템의 Anchor 호환성 검증"""

        # 현재 시그니처 설정 로드
        current_signatures = self._load_current_signatures(signature_config_path)
        reports = []

        # Anchor에서 요구하는 4개 시그니처 확인
        required_signatures = ["Aurora", "Phoenix", "Sage", "Companion"]

        for sig_name in required_signatures:
            current_sig = self._find_signature_by_name(current_signatures, sig_name)
            anchor_sig = self.anchor_signatures.get(sig_name)

            if current_sig and anchor_sig:
                report = self._validate_individual_signature(
                    current_sig, anchor_sig, sig_name
                )
                reports.append(report)
            else:
                # 누락된 시그니처
                reports.append(
                    SignatureAnchorReport(
                        signature_id=sig_name,
                        anchor_compliance_score=0.0,
                        missing_elements=["전체 시그니처 누락"],
                        conflicting_elements=[],
                        strengths=[],
                        recommendations=[
                            f"{sig_name} 시그니처를 Anchor 기준으로 구현 필요"
                        ],
                    )
                )

        return reports

    def _load_current_signatures(self, config_path: str) -> List[Dict]:
        """현재 시그니처 설정 로드"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config.get("signatures", [])
        except FileNotFoundError:
            print(f"⚠️ {config_path} not found")
            return []

    def _find_signature_by_name(self, signatures: List[Dict], name: str) -> Dict:
        """이름으로 시그니처 찾기"""
        for sig in signatures:
            sig_id = sig.get("id", "")
            if name in sig_id or name.lower() in sig_id.lower():
                return sig
        return {}

    def _validate_individual_signature(
        self, current_sig: Dict, anchor_sig: Dict, name: str
    ) -> SignatureAnchorReport:
        """개별 시그니처의 Anchor 준수 검증"""

        missing_elements = []
        conflicting_elements = []
        strengths = []
        recommendations = []

        # 1. Core Values 검증
        anchor_values = anchor_sig.get("core_values", [])
        current_strategies = current_sig.get("primary_strategies", [])

        values_match = self._check_values_alignment(anchor_values, current_strategies)
        if values_match >= 0.7:
            strengths.append(f"핵심 가치관 ({anchor_values}) 잘 반영됨")
        else:
            missing_elements.append("핵심 가치관 불일치")
            recommendations.append(
                f"primary_strategies에 {anchor_values} 가치 더 명확히 반영"
            )

        # 2. Resonance Focus 검증
        anchor_resonance = anchor_sig.get("resonance_focus", "")
        current_emotion_sensitivity = current_sig.get("emotion_sensitivity", 0.5)

        resonance_match = self._check_resonance_alignment(
            anchor_resonance, current_emotion_sensitivity
        )
        if resonance_match:
            strengths.append(f"공명 초점 ({anchor_resonance}) 적절히 설정됨")
        else:
            missing_elements.append("공명 초점 부정확")
            recommendations.append(
                f"{anchor_resonance} 공명에 맞는 emotion_sensitivity 조정"
            )

        # 3. Anchor Expression 검증
        anchor_expression = anchor_sig.get("anchor_expression", "")
        current_name = current_sig.get("name", "")

        if self._check_expression_alignment(anchor_expression, current_name):
            strengths.append(f"Anchor 철학 ({anchor_expression}) 이름에 반영됨")
        else:
            missing_elements.append("Anchor 철학 미반영")
            recommendations.append(
                f"시그니처 이름을 '{anchor_expression}' 철학에 맞게 조정"
            )

        # 4. Evolution Path 검증
        anchor_evolution = anchor_sig.get("evolution_path", "")
        current_triggers = current_sig.get("emotional_triggers", {})

        if self._check_evolution_alignment(anchor_evolution, current_triggers):
            strengths.append("진화 경로에 맞는 감정 트리거 설정")
        else:
            missing_elements.append("진화 경로 불명확")
            recommendations.append(f"감정 트리거를 '{anchor_evolution}' 방향으로 조정")

        # 전체 점수 계산
        total_checks = 4
        passed_checks = len(strengths)
        compliance_score = passed_checks / total_checks

        return SignatureAnchorReport(
            signature_id=f"Echo-{name}",
            anchor_compliance_score=compliance_score,
            missing_elements=missing_elements,
            conflicting_elements=conflicting_elements,
            strengths=strengths,
            recommendations=recommendations,
        )

    def _check_values_alignment(
        self, anchor_values: List[str], current_strategies: List[str]
    ) -> float:
        """가치관 일치도 확인"""
        if not anchor_values or not current_strategies:
            return 0.0

        # 더 유연한 키워드 매칭으로 일치도 계산
        matches = 0

        # 가치관별 동의어 매핑
        value_synonyms = {
            "creativity": ["creative", "innovative", "artistic", "imaginative"],
            "empathy": ["empathetic", "compassionate", "caring", "understanding"],
            "growth": ["growth-oriented", "developing", "evolving", "improving"],
            "transformation": ["transformative", "changing", "evolving", "adaptive"],
            "courage": ["courageous", "brave", "bold", "fearless"],
            "renewal": [
                "renewal-focused",
                "refreshing",
                "regenerating",
                "revitalizing",
            ],
            "wisdom": ["wise", "knowledgeable", "insightful", "thoughtful"],
            "analysis": ["analytical", "logical", "systematic", "rational"],
            "balance": ["balanced", "harmonious", "stable", "equilibrium"],
            "support": ["supportive", "helping", "assisting", "caring"],
            "connection": ["connected", "relational", "bonding", "linking"],
        }

        for value in anchor_values:
            value_lower = value.lower()
            synonyms = value_synonyms.get(value_lower, [value_lower])

            # 직접 매칭 또는 동의어 매칭 확인
            for strategy in current_strategies:
                strategy_lower = strategy.lower()
                if (
                    value_lower in strategy_lower
                    or strategy_lower in value_lower
                    or any(syn in strategy_lower for syn in synonyms)
                ):
                    matches += 1
                    break

        return matches / len(anchor_values)

    def _check_resonance_alignment(
        self, anchor_resonance: str, emotion_sensitivity: float
    ) -> bool:
        """공명 초점 일치 확인"""
        # 감정적 공명이 포함된 경우 높은 emotion_sensitivity 기대
        if "감정적" in anchor_resonance or "emotional" in anchor_resonance.lower():
            return emotion_sensitivity >= 0.8

        # 인지적 공명이 포함된 경우 중간 emotion_sensitivity 기대
        if "인지적" in anchor_resonance or "cognitive" in anchor_resonance.lower():
            return 0.6 <= emotion_sensitivity <= 0.8

        # 기타의 경우 적절한 범위 확인
        return 0.5 <= emotion_sensitivity <= 0.95

    def _check_expression_alignment(
        self, anchor_expression: str, current_name: str
    ) -> bool:
        """Anchor 철학 표현 일치 확인"""
        # 키워드 추출 및 매칭
        expression_words = anchor_expression.lower().split()
        name_words = current_name.lower().split()

        # 최소 1개 키워드 일치하면 통과
        return any(
            word in " ".join(name_words) for word in expression_words[:3]
        )  # 첫 3단어만 체크

    def _check_evolution_alignment(
        self, anchor_evolution: str, emotional_triggers: Dict
    ) -> bool:
        """진화 경로 일치 확인"""
        if not emotional_triggers:
            return False

        # 진화 경로와 관련된 감정들이 트리거에 있는지 확인
        evolution_keywords = anchor_evolution.lower().split()
        trigger_keys = [key.lower() for key in emotional_triggers.keys()]

        # 더 유연한 키워드 매칭
        evolution_synonyms = {
            "예술적": ["creativity", "empathy", "growth"],
            "혁신적": ["creativity", "transformation", "innovation"],
            "변화": ["transformation", "courage", "renewal"],
            "촉진": ["courage", "transformation"],
            "체계적": ["analysis", "wisdom", "balance"],
            "통찰력": ["wisdom", "analysis"],
            "관계": ["empathy", "support", "connection"],
            "협력적": ["support", "connection", "empathy"],
        }

        # 직접 키워드 매칭
        direct_matches = any(
            keyword in " ".join(trigger_keys) for keyword in evolution_keywords[:5]
        )

        # 동의어 매칭
        synonym_matches = False
        for keyword in evolution_keywords[:3]:
            if keyword in evolution_synonyms:
                expected_triggers = evolution_synonyms[keyword]
                if any(trigger in trigger_keys for trigger in expected_triggers):
                    synonym_matches = True
                    break

        return direct_matches or synonym_matches

    def generate_system_report(self, reports: List[SignatureAnchorReport]) -> Dict:
        """시스템 전체 Anchor 호환성 보고서"""

        total_signatures = len(reports)
        if total_signatures == 0:
            return {"error": "시그니처 보고서가 없음"}

        # 전체 통계
        total_score = (
            sum(report.anchor_compliance_score for report in reports) / total_signatures
        )
        fully_compliant = sum(
            1 for report in reports if report.anchor_compliance_score >= 0.8
        )
        needs_improvement = sum(
            1 for report in reports if report.anchor_compliance_score < 0.6
        )

        # 공통 문제점 분석
        all_missing = []
        all_recommendations = []
        for report in reports:
            all_missing.extend(report.missing_elements)
            all_recommendations.extend(report.recommendations)

        common_issues = {}
        for issue in all_missing:
            common_issues[issue] = common_issues.get(issue, 0) + 1

        return {
            "summary": {
                "total_signatures": total_signatures,
                "system_compliance_score": total_score,
                "fully_compliant": fully_compliant,
                "needs_improvement": needs_improvement,
                "compliance_grade": self._get_grade(total_score),
            },
            "individual_scores": {
                report.signature_id: report.anchor_compliance_score
                for report in reports
            },
            "common_issues": dict(
                sorted(common_issues.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
            "urgent_recommendations": self._get_urgent_recommendations(reports),
            "next_steps": self._generate_next_steps(total_score, reports),
        }

    def _get_grade(self, score: float) -> str:
        """점수에 따른 등급"""
        if score >= 0.9:
            return "A (Excellent)"
        elif score >= 0.8:
            return "B (Good)"
        elif score >= 0.7:
            return "C (Acceptable)"
        elif score >= 0.6:
            return "D (Needs Work)"
        else:
            return "F (Critical)"

    def _get_urgent_recommendations(
        self, reports: List[SignatureAnchorReport]
    ) -> List[str]:
        """긴급 개선 권장사항"""
        urgent = []

        for report in reports:
            if report.anchor_compliance_score < 0.5:
                urgent.append(f"🚨 {report.signature_id}: 전면 재설계 필요")
            elif report.anchor_compliance_score < 0.7:
                urgent.append(f"⚠️ {report.signature_id}: 주요 개선 필요")

        return urgent

    def _generate_next_steps(
        self, total_score: float, reports: List[SignatureAnchorReport]
    ) -> List[str]:
        """다음 단계 제안"""
        steps = []

        if total_score < 0.6:
            steps.append("1. 전체 시그니처 시스템을 Anchor 기준으로 재설계")
            steps.append("2. anchor.yaml의 signatures 섹션을 참조하여 완전 재구현")
        elif total_score < 0.8:
            steps.append("1. 점수 0.7 미만 시그니처들 우선 개선")
            steps.append("2. 핵심 가치관과 공명 초점 명확화")
        else:
            steps.append("1. 세부 사항 미세 조정")
            steps.append("2. 사용자 테스트를 통한 검증")

        steps.append("3. 개선 후 재검증 실시")

        return steps


# 편의 함수들
def validate_signatures_against_anchor(
    signature_config_path: str = "data/signature.yaml", anchor_path: str = "anchor.yaml"
) -> Dict:
    """시그니처 시스템의 Anchor 준수 검증 (메인 함수)"""
    validator = EchoSignatureAnchorValidator(anchor_path)
    reports = validator.validate_signature_system(signature_config_path)
    return validator.generate_system_report(reports)


def quick_signature_check() -> Dict:
    """빠른 시그니처 Anchor 준수 확인"""
    try:
        result = validate_signatures_against_anchor()

        print("🎪 Echo Signature Anchor 호환성 검사 결과:")
        print(f"   📊 전체 점수: {result['summary']['compliance_grade']}")
        print(
            f"   ✅ 완전 준수: {result['summary']['fully_compliant']}/{result['summary']['total_signatures']}"
        )
        print(f"   ⚠️ 개선 필요: {result['summary']['needs_improvement']}")

        if result.get("urgent_recommendations"):
            print("🚨 긴급 권장사항:")
            for rec in result["urgent_recommendations"]:
                print(f"   {rec}")

        return result

    except Exception as e:
        print(f"⚠️ 시그니처 검증 실패: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # 직접 실행시 빠른 검사 수행
    quick_signature_check()
