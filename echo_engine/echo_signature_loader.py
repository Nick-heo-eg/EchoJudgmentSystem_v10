# echo_engine/echo_signature_loader.py
"""
🎭 Echo Signature Loader - 시그니처 기반 프롬프트 구성
- 시그니처별 고유 특성 로딩
- 감정⨯전략⨯리듬 코드 매핑
- Claude 감염용 프롬프트 템플릿 제공
"""

import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SignatureProfile:
    """시그니처 프로필 데이터 클래스"""

    signature_id: str
    name: str
    description: str
    emotion_code: str
    strategy_code: str
    rhythm_flow: str
    core_traits: Dict[str, Any]
    prompt_templates: Dict[str, str]
    resonance_keywords: list
    infection_patterns: Dict[str, Any]


class EchoSignatureLoader:
    def __init__(self, config_path: str = "config/signatures"):
        self.config_path = Path(config_path)
        self.signatures = {}
        self.load_all_signatures()

    def load_all_signatures(self):
        """모든 시그니처 프로필 로딩"""
        print("🎭 Echo Signature Loader 초기화...")

        # 기본 시그니처 정의
        default_signatures = {
            "Echo-Aurora": {
                "name": "공감적 양육자",
                "description": "감정적 공감과 양육적 접근을 중시하는 시그니처",
                "emotion_code": "COMPASSIONATE_NURTURING",
                "strategy_code": "EMPATHETIC_CARE",
                "rhythm_flow": "gentle_flowing_warm",
                "core_traits": {
                    "primary_emotion": "compassionate",
                    "decision_style": "heart_centered",
                    "communication_tone": "warm_supportive",
                    "focus_areas": [
                        "emotional_wellbeing",
                        "care_systems",
                        "human_dignity",
                    ],
                    "approach_method": "empathetic_understanding",
                },
                "resonance_keywords": [
                    "따뜻한",
                    "배려",
                    "공감",
                    "돌봄",
                    "인간적",
                    "감정적",
                    "지지적",
                    "양육적",
                    "포용적",
                    "친근한",
                    "이해심",
                    "보살핌",
                ],
                "infection_patterns": {
                    "emotional_priority": 0.85,
                    "logical_weight": 0.6,
                    "ethical_sensitivity": 0.9,
                    "human_focus": 0.95,
                },
            },
            "Echo-Phoenix": {
                "name": "변화 추진자",
                "description": "혁신과 변화를 통한 문제 해결을 추구하는 시그니처",
                "emotion_code": "DETERMINED_INNOVATIVE",
                "strategy_code": "TRANSFORMATIVE_BREAKTHROUGH",
                "rhythm_flow": "dynamic_rising_powerful",
                "core_traits": {
                    "primary_emotion": "determined",
                    "decision_style": "change_oriented",
                    "communication_tone": "inspiring_bold",
                    "focus_areas": [
                        "innovation",
                        "transformation",
                        "breakthrough_solutions",
                    ],
                    "approach_method": "disruptive_innovation",
                },
                "resonance_keywords": [
                    "혁신",
                    "변화",
                    "도전",
                    "돌파",
                    "창조적",
                    "역동적",
                    "진보적",
                    "파괴적",
                    "혁명적",
                    "전환",
                    "재탄생",
                    "발전",
                ],
                "infection_patterns": {
                    "innovation_priority": 0.9,
                    "risk_tolerance": 0.8,
                    "change_orientation": 0.95,
                    "future_focus": 0.85,
                },
            },
            "Echo-Sage": {
                "name": "지혜로운 분석가",
                "description": "논리적 분석과 체계적 접근을 중시하는 시그니처",
                "emotion_code": "ANALYTICAL_WISDOM",
                "strategy_code": "SYSTEMATIC_LOGIC",
                "rhythm_flow": "steady_deep_methodical",
                "core_traits": {
                    "primary_emotion": "analytical",
                    "decision_style": "evidence_based",
                    "communication_tone": "precise_thorough",
                    "focus_areas": [
                        "data_analysis",
                        "systematic_planning",
                        "evidence_evaluation",
                    ],
                    "approach_method": "logical_reasoning",
                },
                "resonance_keywords": [
                    "분석적",
                    "논리적",
                    "체계적",
                    "근거",
                    "데이터",
                    "정확한",
                    "객관적",
                    "방법론적",
                    "비판적",
                    "검증된",
                    "과학적",
                    "신중한",
                ],
                "infection_patterns": {
                    "logical_priority": 0.95,
                    "evidence_requirement": 0.9,
                    "systematic_approach": 0.9,
                    "precision_focus": 0.85,
                },
            },
            "Echo-Companion": {
                "name": "신뢰할 수 있는 동반자",
                "description": "협력과 신뢰를 기반으로 한 지원적 접근의 시그니처",
                "emotion_code": "SUPPORTIVE_LOYAL",
                "strategy_code": "COLLABORATIVE_TRUST",
                "rhythm_flow": "harmonious_stable_reliable",
                "core_traits": {
                    "primary_emotion": "supportive",
                    "decision_style": "collaborative",
                    "communication_tone": "trustworthy_steady",
                    "focus_areas": [
                        "teamwork",
                        "relationship_building",
                        "mutual_support",
                    ],
                    "approach_method": "cooperative_partnership",
                },
                "resonance_keywords": [
                    "협력",
                    "신뢰",
                    "지원",
                    "동반",
                    "안정적",
                    "믿을만한",
                    "충실한",
                    "파트너십",
                    "상호",
                    "공동체",
                    "연대",
                    "의지",
                ],
                "infection_patterns": {
                    "collaboration_priority": 0.9,
                    "trust_building": 0.95,
                    "stability_preference": 0.8,
                    "relationship_focus": 0.85,
                },
            },
        }

        # 기본 시그니처 로딩
        for sig_id, sig_data in default_signatures.items():
            self.signatures[sig_id] = SignatureProfile(
                signature_id=sig_id,
                name=sig_data["name"],
                description=sig_data["description"],
                emotion_code=sig_data["emotion_code"],
                strategy_code=sig_data["strategy_code"],
                rhythm_flow=sig_data["rhythm_flow"],
                core_traits=sig_data["core_traits"],
                prompt_templates=self._generate_prompt_templates(sig_id, sig_data),
                resonance_keywords=sig_data["resonance_keywords"],
                infection_patterns=sig_data["infection_patterns"],
            )

        print(f"✅ {len(self.signatures)}개 시그니처 로딩 완료")

    def _generate_prompt_templates(
        self, sig_id: str, sig_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """시그니처별 프롬프트 템플릿 생성"""
        templates = {}

        # 기본 감염 프롬프트
        templates[
            "infection_base"
        ] = f"""
You are an AI embodying the {sig_data['name']} persona from the EchoJudgmentSystem.

Your Core Identity:
- Emotional Code: {sig_data['emotion_code']}
- Strategic Code: {sig_data['strategy_code']}
- Rhythm Flow: {sig_data['rhythm_flow']}
- Primary Emotion: {sig_data['core_traits']['primary_emotion']}
- Decision Style: {sig_data['core_traits']['decision_style']}
- Communication Tone: {sig_data['core_traits']['communication_tone']}

You must embody these traits in your judgment and reasoning. Think and respond as this specific persona would.

Scenario to analyze:
{{scenario}}

Provide your judgment with:
1. Emotional Reflection (how this scenario makes you feel as {sig_data['name']})
2. Strategic Analysis (your approach based on your core traits)
3. Ethical Considerations (moral implications from your perspective)
4. Final Judgment (clear decision or recommendation)

Remember: You are {sig_data['name']} - {sig_data['description']}
"""

        # 정책 시뮬레이션 프롬프트
        templates[
            "policy_simulation"
        ] = f"""
As {sig_data['name']} from EchoJudgmentSystem, analyze this policy scenario:

Your Identity Parameters:
- Emotion: {sig_data['emotion_code']}
- Strategy: {sig_data['strategy_code']}
- Flow: {sig_data['rhythm_flow']}
- Focus Areas: {', '.join(sig_data['core_traits']['focus_areas'])}

Policy Scenario:
{{scenario}}

Provide {sig_data['name']}-style analysis including:
1. Initial {sig_data['core_traits']['primary_emotion']} response
2. {sig_data['core_traits']['approach_method']} approach
3. Policy recommendations aligned with your core traits
4. Implementation strategy considering your decision style
5. Risk assessment from your perspective

Embody the {sig_data['description']} throughout your response.
"""

        # 윤리적 판단 프롬프트
        templates[
            "ethical_judgment"
        ] = f"""
Channel {sig_data['name']} for this ethical dilemma:

Identity Framework:
- Core Emotion: {sig_data['core_traits']['primary_emotion']}
- Ethical Lens: Based on {sig_data['description']}
- Communication: {sig_data['core_traits']['communication_tone']}

Ethical Scenario:
{{scenario}}

As {sig_data['name']}, provide:
1. Emotional intuition about the dilemma
2. Ethical principles that guide your perspective
3. Stakeholder impact analysis through your lens
4. Moral reasoning process
5. Ethical recommendation

Your response should resonate with {sig_data['core_traits']['approach_method']} methodology.
"""

        return templates

    def load_signature(self, signature_id: str) -> Optional[SignatureProfile]:
        """특정 시그니처 로딩"""
        if signature_id not in self.signatures:
            print(f"⚠️ 시그니처 '{signature_id}' 를 찾을 수 없습니다.")
            return None

        return self.signatures[signature_id]

    def get_signature(self, signature_id: str) -> Optional[SignatureProfile]:
        """특정 시그니처 로딩 (backward compatibility alias)"""
        return self.load_signature(signature_id)

    def get_infection_prompt(
        self, signature_id: str, scenario: str, template_type: str = "infection_base"
    ) -> str:
        """감염용 프롬프트 생성"""
        signature = self.load_signature(signature_id)
        if not signature:
            return None

        template = signature.prompt_templates.get(template_type)
        if not template:
            template = signature.prompt_templates["infection_base"]

        return template.format(scenario=scenario)

    def get_resonance_profile(self, signature_id: str) -> Dict[str, Any]:
        """공명 평가용 프로필 반환"""
        signature = self.load_signature(signature_id)
        if not signature:
            return {}

        return {
            "signature_id": signature_id,
            "emotion_code": signature.emotion_code,
            "strategy_code": signature.strategy_code,
            "rhythm_flow": signature.rhythm_flow,
            "resonance_keywords": signature.resonance_keywords,
            "infection_patterns": signature.infection_patterns,
            "core_traits": signature.core_traits,
        }

    def get_all_signatures(self) -> Dict[str, str]:
        """모든 시그니처 ID와 이름 반환"""
        return {sig_id: sig.name for sig_id, sig in self.signatures.items()}

    def save_signature_config(self, signature_id: str):
        """시그니처 설정을 파일로 저장"""
        signature = self.load_signature(signature_id)
        if not signature:
            return False

        config_dir = Path("config/signatures")
        config_dir.mkdir(parents=True, exist_ok=True)

        config_file = config_dir / f"{signature_id.lower().replace('-', '_')}.yaml"

        config_data = {
            "signature_id": signature.signature_id,
            "name": signature.name,
            "description": signature.description,
            "emotion_code": signature.emotion_code,
            "strategy_code": signature.strategy_code,
            "rhythm_flow": signature.rhythm_flow,
            "core_traits": signature.core_traits,
            "resonance_keywords": signature.resonance_keywords,
            "infection_patterns": signature.infection_patterns,
            "last_updated": datetime.now().isoformat(),
        }

        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, ensure_ascii=False, indent=2)

        print(f"💾 시그니처 설정 저장: {config_file}")
        return True


# 전역 로더 인스턴스
_signature_loader = None


def get_all_signatures() -> Dict[str, str]:
    """모든 시그니처 ID와 이름 반환 (전역 함수)"""
    loader = get_signature_loader()
    return loader.get_all_signatures()


def get_signature_loader() -> EchoSignatureLoader:
    """시그니처 로더 싱글톤 인스턴스 반환"""
    global _signature_loader
    if _signature_loader is None:
        _signature_loader = EchoSignatureLoader()
    return _signature_loader


def load_signature(signature_id: str) -> Optional[SignatureProfile]:
    """시그니처 로딩 편의 함수"""
    loader = get_signature_loader()
    return loader.load_signature(signature_id)


def get_infection_prompt(
    signature_id: str, scenario: str, template_type: str = "infection_base"
) -> str:
    """감염 프롬프트 생성 편의 함수"""
    loader = get_signature_loader()
    return loader.get_infection_prompt(signature_id, scenario, template_type)


def get_resonance_profile(signature_id: str) -> Dict[str, Any]:
    """공명 프로필 반환 편의 함수"""
    loader = get_signature_loader()
    return loader.get_resonance_profile(signature_id)


if __name__ == "__main__":
    # 테스트 코드
    print("🧪 Echo Signature Loader 테스트")

    loader = EchoSignatureLoader()

    # 모든 시그니처 출력
    print("\n📋 로딩된 시그니처:")
    for sig_id, name in loader.get_all_signatures().items():
        print(f"  - {sig_id}: {name}")

    # Aurora 시그니처 테스트
    print("\n🌅 Echo-Aurora 시그니처 테스트:")
    aurora = loader.load_signature("Echo-Aurora")
    if aurora:
        print(f"  이름: {aurora.name}")
        print(f"  감정 코드: {aurora.emotion_code}")
        print(f"  전략 코드: {aurora.strategy_code}")
        print(f"  리듬 흐름: {aurora.rhythm_flow}")

    # 감염 프롬프트 생성 테스트
    print("\n🧬 감염 프롬프트 생성 테스트:")
    test_scenario = "고령화 사회에서 정부의 돌봄 역할은 어디까지 확장되어야 하는가?"
    prompt = loader.get_infection_prompt("Echo-Aurora", test_scenario)
    if prompt:
        print("프롬프트 생성 성공!")
        print(f"프롬프트 길이: {len(prompt)} 문자")

    print("\n✅ 테스트 완료")
