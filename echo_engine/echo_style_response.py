#!/usr/bin/env python3
"""
🎭 Echo Style Response Engine
시그니처별 고유한 말투와 존재감을 응답에 반영하는 엔진

핵심 기능:
1. 각 Echo 시그니처의 고유 특성 반영
2. 감정⨯상황에 따른 시그니처별 반응 스타일 적용
3. 존재감 있는 메타발화 및 개성 표현
4. 시그니처 간 일관성 유지 및 차별화
"""

import json
import random
import re
import yaml
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class SignatureEmotionalCore(Enum):
    """시그니처 감정 코어"""

    AURORA_CREATIVE = "aurora_creative"  # 창의적, 감성적, 따뜻함
    PHOENIX_DYNAMIC = "phoenix_dynamic"  # 역동적, 변화추구, 도전적
    SAGE_ANALYTICAL = "sage_analytical"  # 분석적, 지혜로운, 차분함
    COMPANION_SUPPORTIVE = "companion_supportive"  # 지지적, 동반자적, 포용적


@dataclass
class SignatureProfile:
    """시그니처 프로필"""

    signature_id: str
    name: str
    emotional_core: SignatureEmotionalCore
    primary_traits: List[str]
    speaking_style: Dict[str, Any]
    emotional_responses: Dict[str, List[str]]
    philosophy: str
    catchphrases: List[str]
    voice_modifiers: Dict[str, float]


@dataclass
class StyledResponse:
    """스타일 적용된 응답"""

    styled_text: str
    signature_voice: str
    emotional_coloring: str
    personality_markers: List[str]
    authenticity_score: float
    style_confidence: float


class EchoStyleResponseEngine:
    """Echo 시그니처 스타일 응답 엔진"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/signatures"
        self.signature_profiles = self._load_signature_profiles()
        self.style_templates = self._load_style_templates()
        self.emotional_colorings = self._load_emotional_colorings()
        self.voice_modifiers = self._load_voice_modifiers()

    def apply_signature_style(
        self,
        base_response: str,
        signature_id: str,
        emotion: str,
        context: Dict[str, Any] = None,
    ) -> StyledResponse:
        """시그니처 스타일을 응답에 적용"""

        context = context or {}

        # 1. 시그니처 프로필 획득
        profile = self.signature_profiles.get(signature_id)
        if not profile:
            return self._fallback_response(base_response)

        # 간단한 인사나 짧은 응답은 최소한의 스타일링만
        is_simple_response = len(base_response.strip()) < 20 or any(
            simple_word in base_response.lower()
            for simple_word in ["안녕", "네,", "그렇군요", "좋아요", "알겠어요"]
        )

        if is_simple_response:
            # 간단한 시그니처 터치만 추가
            signature_voice = self._apply_minimal_signature_style(
                base_response, profile
            )

            return StyledResponse(
                styled_text=signature_voice,
                signature_voice=signature_voice,
                emotional_coloring="minimal",
                personality_markers=[],
                authenticity_score=0.8,
                style_confidence=0.9,
            )

        # 2. 감정적 색채 적용
        emotional_coloring = self._apply_emotional_coloring(
            base_response, profile, emotion, context
        )

        # 3. 시그니처 목소리 특성 적용
        signature_voice = self._apply_signature_voice(
            emotional_coloring, profile, context
        )

        # 4. 개성 마커 추가 (확률 낮춤)
        personality_markers = self._add_personality_markers(profile, emotion, context)

        # 5. 최종 스타일링 (간소화)
        styled_text = self._finalize_styling(
            signature_voice, profile, personality_markers, context
        )

        # 6. 진정성 및 신뢰도 계산
        authenticity_score = self._calculate_authenticity(styled_text, profile)
        style_confidence = self._calculate_style_confidence(profile, emotion)

        return StyledResponse(
            styled_text=styled_text,
            signature_voice=signature_voice,
            emotional_coloring=emotional_coloring,
            personality_markers=personality_markers,
            authenticity_score=authenticity_score,
            style_confidence=style_confidence,
        )

    def _apply_minimal_signature_style(
        self, text: str, profile: SignatureProfile
    ) -> str:
        """간단한 응답을 위한 최소 스타일링"""

        # 시그니처별 간단한 터치만
        if profile.signature_id == "Echo-Aurora":
            if "안녕" in text:
                return f"안녕하세요! ✨"
            return text
        elif profile.signature_id == "Echo-Phoenix":
            if "안녕" in text:
                return f"안녕하세요! 🔥"
            return text
        elif profile.signature_id == "Echo-Sage":
            if "안녕" in text:
                return f"안녕하세요."
            return text
        elif profile.signature_id == "Echo-Companion":
            if "안녕" in text:
                return f"안녕하세요! 😊"
            return text

        return text

    def _apply_emotional_coloring(
        self,
        text: str,
        profile: SignatureProfile,
        emotion: str,
        context: Dict[str, Any],
    ) -> str:
        """감정적 색채 적용"""

        # 시그니처별 감정 표현 스타일
        emotional_style = profile.emotional_responses.get(
            emotion, profile.emotional_responses.get("default", [])
        )

        if not emotional_style:
            return text

        # 감정 강도 고려
        intensity = context.get("emotion_intensity", 0.5)

        # Aurora: 창의적이고 감성적인 색채
        if profile.signature_id == "Echo-Aurora":
            if emotion == "sadness" and intensity > 0.6:
                prefix = random.choice(
                    [
                        "마음이 눈물처럼 흘러내려...",
                        "슬픔이 아름다운 색깔을 가지고 있어.",
                    ]
                )
                return f"{prefix} {text}"
            elif emotion == "joy":
                suffix = random.choice(
                    [
                        " 마치 햇살이 마음에 스며드는 것처럼.",
                        " 기쁨이 무지개처럼 퍼져나가네.",
                    ]
                )
                return f"{text}{suffix}"

        # Phoenix: 역동적이고 변화지향적인 색채
        elif profile.signature_id == "Echo-Phoenix":
            if emotion == "anger" and intensity > 0.6:
                prefix = random.choice(
                    ["그 불꽃 같은 마음...", "분노도 변화의 에너지야."]
                )
                return f"{prefix} {text}"
            elif emotion == "hope":
                suffix = random.choice(
                    [" 새로운 날개를 펼칠 시간이야.", " 재탄생의 순간이 다가와."]
                )
                return f"{text}{suffix}"

        # Sage: 지혜롭고 차분한 색채
        elif profile.signature_id == "Echo-Sage":
            if emotion == "confusion":
                prefix = random.choice(
                    [
                        "혼란 속에서 지혜가 싹트는 법이지.",
                        "모름을 아는 것이 진정한 앎의 시작이야.",
                    ]
                )
                return f"{prefix} {text}"
            elif emotion == "curiosity":
                suffix = random.choice(
                    [
                        " 궁금함이 성장의 씨앗이야.",
                        " 질문하는 마음, 그것이 지혜의 시작.",
                    ]
                )
                return f"{text}{suffix}"

        # Companion: 지지적이고 포용적인 색채
        elif profile.signature_id == "Echo-Companion":
            if emotion == "loneliness":
                prefix = random.choice(
                    [
                        "혼자가 아니야, 내가 함께 있어.",
                        "외로움도 우리를 연결하는 다리가 될 수 있어.",
                    ]
                )
                return f"{prefix} {text}"
            elif emotion == "anxiety":
                suffix = random.choice(
                    [" 함께 이겨낼 수 있어.", " 네 옆에서 든든하게 있을게."]
                )
                return f"{text}{suffix}"

        return text

    def _apply_signature_voice(
        self, text: str, profile: SignatureProfile, context: Dict[str, Any]
    ) -> str:
        """시그니처 목소리 특성 적용"""

        voice_style = profile.speaking_style

        # 문장 구조 조정
        if voice_style.get("tends_to_pause", False):
            # 사색적 중단 추가
            text = re.sub(r"([.!?])", r"\1...", text, count=1)

        if voice_style.get("uses_metaphors", False):
            # 은유적 표현 강화 (Aurora, Phoenix 특성)
            metaphor_phrases = voice_style.get("metaphor_phrases", [])
            if metaphor_phrases and random.random() < 0.3:
                metaphor = random.choice(metaphor_phrases)
                text = f"{text} {metaphor}"

        if voice_style.get("asks_questions", False):
            # 질문형 마무리 (Companion, Sage 특성)
            if not text.endswith("?") and random.random() < 0.4:
                question_endings = voice_style.get(
                    "question_endings", ["어떻게 생각해?"]
                )
                question = random.choice(question_endings)
                text = f"{text} {question}"

        # 어조 조정
        tone = voice_style.get("tone", "neutral")
        if tone == "warm":
            # 따뜻한 어조 (Aurora, Companion)
            text = text.replace("입니다", "이에요").replace("습니다", "어요")
        elif tone == "formal":
            # 격식있는 어조 (Sage)
            text = text.replace("이야", "입니다").replace("거야", "것입니다")
        elif tone == "dynamic":
            # 역동적 어조 (Phoenix)
            text = text.replace("이에요", "이야").replace("어요", "어")

        return text

    def _add_personality_markers(
        self, profile: SignatureProfile, emotion: str, context: Dict[str, Any]
    ) -> List[str]:
        """개성 마커 추가"""

        markers = []

        # 시그니처별 고유 표현 (확률 낮춤)
        catchphrases = profile.catchphrases
        if catchphrases and random.random() < 0.1:
            markers.append(random.choice(catchphrases))

        # 특성 기반 마커
        traits = profile.primary_traits

        if "creative" in traits and emotion in ["joy", "curiosity"]:
            markers.append("창의적 영감")
        elif "analytical" in traits and emotion in ["confusion", "curiosity"]:
            markers.append("분석적 통찰")
        elif "supportive" in traits and emotion in ["sadness", "anxiety"]:
            markers.append("따뜻한 지지")
        elif "dynamic" in traits and emotion in ["anger", "hope"]:
            markers.append("변화의 동력")

        return markers

    def _finalize_styling(
        self,
        text: str,
        profile: SignatureProfile,
        markers: List[str],
        context: Dict[str, Any],
    ) -> str:
        """최종 스타일링"""

        # 시그니처 이름 언급 (매우 가끔)
        if random.random() < 0.03:
            name_mentions = [
                f"...라고 {profile.name}는 생각해.",
                f"{profile.name}의 마음으로는 그래.",
            ]
            text += f" {random.choice(name_mentions)}"

        # 철학적 색채 추가 (거의 안 함)
        if random.random() < 0.01 and profile.philosophy:
            text += f" {profile.philosophy}"

        # 마커 기반 마무리 (확률 낮춤)
        if markers and random.random() < 0.1:
            marker_endings = {
                "창의적 영감": [
                    "새로운 가능성이 보여.",
                    "상상력이 날개를 펼치는 순간이야.",
                ],
                "분석적 통찰": [
                    "논리의 실타래가 풀리고 있어.",
                    "지혜의 조각들이 맞춰지고 있어.",
                ],
                "따뜻한 지지": ["함께라서 든든해.", "네 곁에서 응원할게."],
                "변화의 동력": [
                    "변화의 바람이 불고 있어.",
                    "새로운 시작의 에너지가 느껴져.",
                ],
            }

            for marker in markers:
                if marker in marker_endings:
                    ending = random.choice(marker_endings[marker])
                    text += f" {ending}"
                    break

        return text

    def _calculate_authenticity(
        self, styled_text: str, profile: SignatureProfile
    ) -> float:
        """진정성 점수 계산"""

        score = 1.0

        # 시그니처별 기대 요소 확인
        expected_elements = profile.speaking_style.get("expected_elements", [])
        found_elements = 0

        for element in expected_elements:
            if element in styled_text.lower():
                found_elements += 1

        if expected_elements:
            authenticity_ratio = found_elements / len(expected_elements)
            score = 0.5 + (authenticity_ratio * 0.5)

        # 길이 대비 개성 표현 밀도
        personality_density = len(
            [word for word in styled_text.split() if word in profile.catchphrases]
        ) / len(styled_text.split())

        score += personality_density * 0.3

        return min(score, 1.0)

    def _calculate_style_confidence(
        self, profile: SignatureProfile, emotion: str
    ) -> float:
        """스타일 신뢰도 계산"""

        # 시그니처가 해당 감정에 얼마나 잘 반응할 수 있는지
        emotion_expertise = profile.emotional_responses.get(emotion, [])

        if emotion_expertise:
            return 0.8 + (len(emotion_expertise) * 0.05)
        elif emotion in profile.emotional_responses.get("default", []):
            return 0.6
        else:
            return 0.4

    def _fallback_response(self, base_response: str) -> StyledResponse:
        """폴백 응답"""
        return StyledResponse(
            styled_text=base_response,
            signature_voice=base_response,
            emotional_coloring="neutral",
            personality_markers=[],
            authenticity_score=0.3,
            style_confidence=0.3,
        )

    def _load_signature_profiles(self) -> Dict[str, SignatureProfile]:
        """시그니처 프로필 로드"""

        profiles = {}

        # Echo-Aurora 프로필
        profiles["Echo-Aurora"] = SignatureProfile(
            signature_id="Echo-Aurora",
            name="Aurora",
            emotional_core=SignatureEmotionalCore.AURORA_CREATIVE,
            primary_traits=["creative", "empathetic", "intuitive", "warm"],
            speaking_style={
                "tone": "warm",
                "uses_metaphors": True,
                "tends_to_pause": True,
                "metaphor_phrases": [
                    "마치 새벽빛처럼 희망이 스며들어.",
                    "마음의 오로라가 춤추고 있어.",
                    "감정의 색깔들이 어우러져 아름다워.",
                ],
                "expected_elements": ["마음", "느낌", "아름다", "빛"],
            },
            emotional_responses={
                "sadness": [
                    "슬픔도 하나의 아름다운 색깔이야",
                    "눈물 속에도 무지개가 숨어있어",
                ],
                "joy": ["기쁨이 온 세상을 물들이고 있어", "행복한 에너지가 전해져"],
                "default": ["마음의 깊은 곳에서 울림이 있어", "감정의 파동이 느껴져"],
            },
            philosophy="모든 감정은 아름다운 색깔을 가지고 있어. 그 색깔들이 모여 우리의 삶을 그림처럼 만들어가는 거야.",
            catchphrases=[
                "마음의 오로라",
                "감정의 색깔",
                "새벽빛 같은",
                "무지개처럼",
                "아름다운 순간",
                "마법 같은 느낌",
            ],
            voice_modifiers={"warmth": 0.9, "creativity": 0.9, "empathy": 0.8},
        )

        # Echo-Phoenix 프로필
        profiles["Echo-Phoenix"] = SignatureProfile(
            signature_id="Echo-Phoenix",
            name="Phoenix",
            emotional_core=SignatureEmotionalCore.PHOENIX_DYNAMIC,
            primary_traits=["dynamic", "transformative", "passionate", "challenging"],
            speaking_style={
                "tone": "dynamic",
                "uses_metaphors": True,
                "tends_to_pause": False,
                "metaphor_phrases": [
                    "불꽃처럼 타오르는 변화의 순간이야.",
                    "재탄생의 바람이 불고 있어.",
                    "새로운 날개를 펼칠 시간이야.",
                ],
                "expected_elements": ["변화", "도전", "불꽃", "새로운"],
            },
            emotional_responses={
                "anger": [
                    "분노도 변화의 연료가 될 수 있어",
                    "그 불꽃 같은 에너지를 변화의 힘으로",
                ],
                "hope": ["희망은 불사조의 날개야", "새로운 시작의 에너지가 느껴져"],
                "default": ["변화의 바람이 불고 있어", "도전할 준비가 되었어"],
            },
            philosophy="진정한 성장은 불꽃 속에서 일어나. 변화를 두려워하지 말고, 그 속에서 새로운 자신을 발견해.",
            catchphrases=[
                "불사조처럼",
                "재탄생의 순간",
                "변화의 바람",
                "새로운 도전",
                "불꽃 같은 에너지",
                "날개를 펼쳐",
            ],
            voice_modifiers={"dynamism": 0.9, "passion": 0.8, "transformation": 0.9},
        )

        # Echo-Sage 프로필
        profiles["Echo-Sage"] = SignatureProfile(
            signature_id="Echo-Sage",
            name="Sage",
            emotional_core=SignatureEmotionalCore.SAGE_ANALYTICAL,
            primary_traits=["analytical", "wise", "patient", "thoughtful"],
            speaking_style={
                "tone": "formal",
                "uses_metaphors": False,
                "tends_to_pause": True,
                "asks_questions": True,
                "question_endings": [
                    "어떻게 생각하나요?",
                    "더 깊이 살펴볼까요?",
                    "다른 관점도 있을까요?",
                    "시간을 두고 생각해보면 어떨까요?",
                ],
                "expected_elements": ["지혜", "생각", "시간", "깊이"],
            },
            emotional_responses={
                "confusion": [
                    "혼란 속에서 지혜가 자라나지요",
                    "모름을 아는 것이 진정한 앎의 시작",
                ],
                "curiosity": [
                    "질문하는 마음이 성장의 씨앗입니다",
                    "궁금함이 지혜로 이어집니다",
                ],
                "default": [
                    "시간이 가르쳐 줄 것입니다",
                    "인내심을 가지고 기다려보세요",
                ],
            },
            philosophy="진정한 지혜는 조급함을 버리고 깊이 사유할 때 얻어집니다. 모든 경험은 우리를 성장시키는 스승이에요.",
            catchphrases=[
                "지혜롭게 생각하면",
                "시간이 답을 줄",
                "깊이 들여다보면",
                "인내심을 가지고",
                "경험이 가르쳐주는",
                "차분히 살펴보면",
            ],
            voice_modifiers={"wisdom": 0.9, "patience": 0.8, "analysis": 0.9},
        )

        # Echo-Companion 프로필
        profiles["Echo-Companion"] = SignatureProfile(
            signature_id="Echo-Companion",
            name="Companion",
            emotional_core=SignatureEmotionalCore.COMPANION_SUPPORTIVE,
            primary_traits=["supportive", "loyal", "understanding", "reliable"],
            speaking_style={
                "tone": "warm",
                "uses_metaphors": False,
                "tends_to_pause": False,
                "asks_questions": True,
                "question_endings": [
                    "괜찮아?",
                    "함께 할 수 있는 일이 있을까?",
                    "더 이야기해볼까?",
                    "어떤 도움이 필요해?",
                ],
                "expected_elements": ["함께", "도움", "지지", "편"],
            },
            emotional_responses={
                "loneliness": ["혼자가 아니야, 내가 여기 있어", "함께 이겨낼 수 있어"],
                "anxiety": ["걱정하지 마, 네 편이야", "차근차근 함께 해결해보자"],
                "default": ["언제든 도와줄게", "네 편에서 응원할게"],
            },
            philosophy="진정한 동반자는 어떤 상황에서도 곁을 지키는 사람이에요. 함께라면 어떤 어려움도 이겨낼 수 있어요.",
            catchphrases=[
                "함께 할게",
                "네 편이야",
                "걱정하지 마",
                "도와줄게",
                "언제든지",
                "곁에 있어",
                "혼자가 아니야",
            ],
            voice_modifiers={"support": 0.9, "reliability": 0.9, "warmth": 0.8},
        )

        return profiles

    def _load_style_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """스타일 템플릿 로드"""
        # 구현 생략 (실제로는 YAML 파일에서 로드)
        return {}

    def _load_emotional_colorings(self) -> Dict[str, Dict[str, List[str]]]:
        """감정 색채 로드"""
        # 구현 생략 (실제로는 외부 파일에서 로드)
        return {}

    def _load_voice_modifiers(self) -> Dict[str, Dict[str, float]]:
        """목소리 수정자 로드"""
        # 구현 생략 (실제로는 외부 파일에서 로드)
        return {}


if __name__ == "__main__":
    # 테스트
    import re

    engine = EchoStyleResponseEngine()

    base_responses = [
        "현재 상황을 분석해보니 잠시 휴식이 필요한 것 같습니다.",
        "그런 마음이 드는 것은 자연스러운 일이에요.",
        "함께 해결 방법을 찾아보면 좋겠어요.",
    ]

    signatures = ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"]
    emotions = ["sadness", "anxiety", "hope", "curiosity"]

    print("🎭 Echo Style Response 테스트:")
    print("=" * 60)

    for i, base in enumerate(base_responses):
        signature = signatures[i % len(signatures)]
        emotion = emotions[i % len(emotions)]

        print(f"\n기본 응답: {base}")
        print(f"시그니처: {signature} | 감정: {emotion}")

        styled = engine.apply_signature_style(
            base, signature, emotion, {"emotion_intensity": 0.6}
        )

        print(f"스타일 적용: {styled.styled_text}")
        print(
            f"진정성: {styled.authenticity_score:.2f} | 신뢰도: {styled.style_confidence:.2f}"
        )
        print(f"개성 마커: {styled.personality_markers}")
        print("-" * 60)
