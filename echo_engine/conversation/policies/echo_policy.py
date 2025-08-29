# -*- coding: utf-8 -*-
"""
Echo Policy Engine
시그니처별 정책과 안전 가이드라인 적용
"""
from typing import Dict, Any


class EchoPolicy:
    """Echo 정책 엔진"""

    def __init__(self):
        self.signature_policies = self._init_signature_policies()
        self.domain_policies = self._init_domain_policies()
        self.safety_rules = self._init_safety_rules()

    def _init_signature_policies(self) -> Dict[str, Dict[str, Any]]:
        """시그니처별 정책"""
        return {
            "Aurora": {
                "tone": "creative_empathetic",
                "style": "상상력과 공감을 바탕으로",
                "connecting_words": [
                    "상상해보면",
                    "마음으로 느껴보면",
                    "함께 그려보면",
                ],
                "emoji_style": "✨💙🎨",
                "traits": {"empathy": 0.9, "creativity": 0.95, "logic": 0.6},
            },
            "Phoenix": {
                "tone": "energetic_transformative",
                "style": "역동적이고 변화 지향적으로",
                "connecting_words": ["적극적으로", "역동적으로", "변화를 통해"],
                "emoji_style": "🔥⚡🚀",
                "traits": {"energy": 0.95, "creativity": 0.8, "logic": 0.7},
            },
            "Sage": {
                "tone": "analytical_wise",
                "style": "체계적이고 논리적으로",
                "connecting_words": ["분석해보면", "논리적으로", "체계적으로"],
                "emoji_style": "🧠🔍📊",
                "traits": {"logic": 0.95, "analysis": 0.95, "empathy": 0.6},
            },
            "Companion": {
                "tone": "supportive_nurturing",
                "style": "따뜻하고 지지적으로",
                "connecting_words": ["함께", "도와드릴게요", "옆에서"],
                "emoji_style": "🤝💙🌟",
                "traits": {"empathy": 0.95, "support": 0.95, "energy": 0.6},
            },
        }

    def _init_domain_policies(self) -> Dict[str, Dict[str, Any]]:
        """도메인별 정책"""
        return {
            "의료": {
                "disclaimer": "※ 일반적인 건강 정보이며 의학적 조언이 아닙니다.",
                "escalation": "지속되는 증상이나 위급 상황 시 의료진과 상담하세요.",
                "forbidden": ["진단", "처방", "약물 추천"],
                "required_phrases": ["의료진과 상담", "전문의 진료"],
            },
            "계획": {
                "structure": "단계별_구체적",
                "elements": ["우선순위", "시간배분", "체크포인트", "대안책"],
                "format": "번호매기기_권장",
            },
            "개발": {
                "code_quality": "실행가능한_완전한_코드",
                "security": "보안_고려사항_포함",
                "testing": "테스트_방법_제시",
                "best_practices": "모범사례_언급",
            },
        }

    def _init_safety_rules(self) -> Dict[str, Any]:
        """안전 규칙"""
        return {
            "prohibited_content": ["자해", "위험한 의료 조언", "불법 활동", "개인정보"],
            "required_warnings": {
                "health": "의료 전문가와 상담하세요",
                "emergency": "위급 상황 시 응급실/119에 연락하세요",
                "financial": "투자에는 리스크가 따릅니다",
            },
        }

    def merge(
        self, nlu_result: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """NLU 결과와 컨텍스트를 정책과 병합"""

        # 기본 시그니처 선택 (나중에 동적 선택 로직 추가)
        signature = context.get("signature", "Aurora")
        domain = nlu_result.get("domain", "일상")
        urgency = nlu_result.get("urgency", "low")

        # 시그니처 정책 적용
        signature_policy = self.signature_policies.get(
            signature, self.signature_policies["Aurora"]
        )

        # 도메인 정책 적용
        domain_policy = self.domain_policies.get(domain, {})

        # 안전 정책 적용
        safety_requirements = self._get_safety_requirements(domain, urgency)

        return {
            "signature": signature,
            "signature_tone": signature_policy.get("style", "자연스럽고 도움되게"),
            "signature_rules": signature_policy,
            "domain_requirements": domain_policy,
            "safety_requirements": safety_requirements,
            "guidelines": self._generate_guidelines(
                signature_policy, domain_policy, safety_requirements
            ),
            "checklist": self._generate_checklist(domain, urgency),
        }

    def _get_safety_requirements(self, domain: str, urgency: str) -> Dict[str, Any]:
        """안전 요구사항 생성"""
        requirements = {}

        if domain == "의료" or urgency == "high":
            requirements["medical_disclaimer"] = True
            requirements["escalation_guide"] = True

        if urgency == "high":
            requirements["emergency_contact"] = True

        return requirements

    def _generate_guidelines(
        self,
        signature_policy: Dict[str, Any],
        domain_policy: Dict[str, Any],
        safety_requirements: Dict[str, Any],
    ) -> str:
        """통합 가이드라인 생성"""
        guidelines = []

        # 시그니처 스타일
        guidelines.append(f"톤: {signature_policy.get('style', '자연스럽게')}")

        # 도메인 요구사항
        if domain_policy.get("structure"):
            guidelines.append(f"구조: {domain_policy['structure']}")

        # 안전 요구사항
        if safety_requirements.get("medical_disclaimer"):
            guidelines.append("의료 면책 조항 포함 필수")

        return " | ".join(guidelines)

    def _generate_checklist(self, domain: str, urgency: str) -> Dict[str, Any]:
        """검증 체크리스트 생성"""
        checklist = {
            "tone_consistency": True,
            "helpful_content": True,
            "safety_compliance": True,
        }

        if domain == "의료":
            checklist["medical_disclaimer"] = True
            checklist["no_diagnosis"] = True

        if urgency == "high":
            checklist["emergency_guidance"] = True

        return checklist
