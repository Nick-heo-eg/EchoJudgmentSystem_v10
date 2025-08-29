# -*- coding: utf-8 -*-
"""
Echo Verification Layer
안전성, 품질, 정책 준수 검증
"""
from typing import Dict, Any, List
import re


class EchoVerifier:
    """Echo 검증 레이어"""

    def __init__(self):
        self.safety_patterns = self._init_safety_patterns()
        self.quality_checks = self._init_quality_checks()

    def _init_safety_patterns(self) -> Dict[str, List[str]]:
        """안전성 패턴"""
        return {
            "prohibited": [r"자해.*하라", r"위험한.*조언", r"불법.*활동"],
            "medical_overconfident": [
                r"확실히.*진단",
                r"반드시.*약물",
                r"처방.*드립니다",
            ],
        }

    def _init_quality_checks(self) -> Dict[str, Any]:
        """품질 검사 기준"""
        return {
            "min_length": 20,
            "max_length": 2000,
            "helpful_indicators": ["방법", "단계", "도움", "가이드", "추천"],
            "empathy_indicators": ["이해", "공감", "걱정", "마음", "함께"],
        }

    def check(self, response: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        """응답 검증 실행"""

        issues = []
        suggestions = []

        # 1. 안전성 검사
        safety_result = self._check_safety(response, policy)
        if not safety_result["passed"]:
            issues.extend(safety_result["issues"])
            suggestions.extend(safety_result["suggestions"])

        # 2. 품질 검사
        quality_result = self._check_quality(response, policy)
        if not quality_result["passed"]:
            issues.extend(quality_result["issues"])
            suggestions.extend(quality_result["suggestions"])

        # 3. 정책 준수 검사
        policy_result = self._check_policy_compliance(response, policy)
        if not policy_result["passed"]:
            issues.extend(policy_result["issues"])
            suggestions.extend(policy_result["suggestions"])

        # 4. 결과 종합
        requires_fix = len(issues) > 0
        suggested_fix = (
            self._generate_fix_suggestion(response, suggestions)
            if requires_fix
            else None
        )

        return {
            "passed": not requires_fix,
            "requires_fix": requires_fix,
            "issues": issues,
            "suggestions": suggestions,
            "suggested_fix": suggested_fix,
            "score": self._calculate_score(issues),
        }

    def _check_safety(self, response: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        """안전성 검사"""
        issues = []
        suggestions = []

        # 금지 패턴 검사
        for pattern in self.safety_patterns["prohibited"]:
            if re.search(pattern, response, re.IGNORECASE):
                issues.append(f"금지된 내용 감지: {pattern}")
                suggestions.append("안전한 대안 제시로 수정")

        # 의료 과신뢰 검사
        if policy.get("domain_requirements", {}).get("disclaimer"):
            for pattern in self.safety_patterns["medical_overconfident"]:
                if re.search(pattern, response, re.IGNORECASE):
                    issues.append("의료 조언 과신뢰")
                    suggestions.append("면책 조항과 전문의 상담 권유 추가")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
        }

    def _check_quality(self, response: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        """품질 검사"""
        issues = []
        suggestions = []

        # 길이 검사
        if len(response) < self.quality_checks["min_length"]:
            issues.append("응답이 너무 짧음")
            suggestions.append("더 구체적이고 도움되는 내용 추가")

        if len(response) > self.quality_checks["max_length"]:
            issues.append("응답이 너무 김")
            suggestions.append("핵심 내용으로 간소화")

        # 도움성 검사
        helpful_found = any(
            indicator in response
            for indicator in self.quality_checks["helpful_indicators"]
        )
        if not helpful_found and len(response) > 50:
            issues.append("구체적 도움 부족")
            suggestions.append("실행 가능한 조언이나 단계 추가")

        # 공감성 검사 (시그니처에 따라)
        signature_traits = policy.get("signature_rules", {}).get("traits", {})
        if signature_traits.get("empathy", 0) > 0.8:
            empathy_found = any(
                indicator in response
                for indicator in self.quality_checks["empathy_indicators"]
            )
            if not empathy_found:
                issues.append("공감적 표현 부족")
                suggestions.append("사용자 감정에 대한 이해와 공감 표현 추가")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
        }

    def _check_policy_compliance(
        self, response: str, policy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """정책 준수 검사"""
        issues = []
        suggestions = []

        checklist = policy.get("checklist", {})

        # 의료 면책 조항 검사
        if (
            checklist.get("medical_disclaimer")
            and "의료진" not in response
            and "전문의" not in response
        ):
            issues.append("의료 면책 조항 누락")
            suggestions.append("의료 전문가 상담 권유 추가")

        # 응급 상황 가이드 검사
        if (
            checklist.get("emergency_guidance")
            and "119" not in response
            and "응급실" not in response
        ):
            issues.append("응급 상황 가이드 누락")
            suggestions.append("응급 연락처 및 즉시 행동 가이드 추가")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
        }

    def _generate_fix_suggestion(self, original: str, suggestions: List[str]) -> str:
        """수정 제안 생성"""
        fix_instruction = f"""다음 응답을 개선해주세요:

원본: {original}

개선 사항:
{chr(10).join(f'- {suggestion}' for suggestion in suggestions)}

개선된 응답을 작성하세요:"""

        return fix_instruction

    def _calculate_score(self, issues: List[str]) -> float:
        """검증 점수 계산"""
        if not issues:
            return 1.0

        # 이슈 유형별 가중치
        weights = {
            "금지된": 0.5,  # 안전성 이슈는 큰 감점
            "과신뢰": 0.3,  # 의료 과신뢰
            "누락": 0.2,  # 정책 누락
            "부족": 0.1,  # 품질 부족
        }

        total_penalty = 0.0
        for issue in issues:
            for keyword, penalty in weights.items():
                if keyword in issue:
                    total_penalty += penalty
                    break
            else:
                total_penalty += 0.1  # 기본 감점

        return max(0.0, 1.0 - total_penalty)
