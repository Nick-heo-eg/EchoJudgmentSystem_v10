#!/usr/bin/env python3
"""
🗣️ Natural Response Formatter
EchoJudgmentSystem의 판단 결과를 자연스러운 응답으로 변환하는 엔진

핵심 기능:
1. judgment_engine의 구조화된 판단 결과를 자연어로 변환
2. 감정⨯리듬⨯전략에 따른 응답 흐름 생성
3. 메타발화 및 존재감 표현 포함
4. 다층적 응답 구조 (primary, supporting, resonance) 생성
"""

import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ResponseStyle(Enum):
    """응답 스타일"""

    EMPATHETIC = "empathetic"  # 공감적
    ANALYTICAL = "analytical"  # 분석적
    SUPPORTIVE = "supportive"  # 지지적
    REFLECTIVE = "reflective"  # 성찰적
    CONVERSATIONAL = "conversational"  # 대화적
    PHILOSOPHICAL = "philosophical"  # 철학적


@dataclass
class JudgmentResult:
    """판단 결과 (judgment_engine에서 받는 데이터)"""

    judgment_text: str
    confidence: float
    emotion_detected: str
    strategy_used: str
    reasoning_process: List[str]
    meta_reflections: List[str]
    signature_id: str
    processing_time: float
    urgency_response: bool = False


@dataclass
class NaturalResponse:
    """자연어 응답 결과"""

    primary_response: str  # 주 응답
    supporting_context: str  # 지지적 맥락
    resonance_element: str  # 울림 요소
    meta_voice: Optional[str]  # 메타발화
    emotional_bridge: str  # 감정적 연결
    conversation_flow: str  # 대화 흐름 유도
    response_style: ResponseStyle
    confidence_indicator: str  # 확신도 표현


class NaturalResponseFormatter:
    """자연어 응답 변환기"""

    def __init__(self):
        self.emotional_bridges = self._load_emotional_bridges()
        self.response_templates = self._load_response_templates()
        self.meta_voice_patterns = self._load_meta_voice_patterns()
        self.resonance_generators = self._load_resonance_generators()
        self.conversation_flows = self._load_conversation_flows()

    def format_response(
        self, judgment_result: JudgmentResult, user_context: Dict[str, Any]
    ) -> NaturalResponse:
        """판단 결과를 자연어 응답으로 변환"""

        # 1. 응답 스타일 결정
        response_style = self._determine_response_style(
            judgment_result.emotion_detected,
            judgment_result.strategy_used,
            user_context,
        )

        # 2. 감정적 연결 생성
        emotional_bridge = self._create_emotional_bridge(
            judgment_result.emotion_detected,
            judgment_result.confidence,
            user_context.get("emotion_intensity", 0.5),
        )

        # 3. 주 응답 생성
        primary_response = self._generate_primary_response(
            judgment_result, response_style, user_context
        )

        # 4. 지지적 맥락 생성
        supporting_context = self._generate_supporting_context(
            judgment_result.reasoning_process, response_style
        )

        # 5. 울림 요소 생성
        resonance_element = self._generate_resonance_element(
            judgment_result.signature_id, judgment_result.emotion_detected, user_context
        )

        # 6. 메타발화 생성 (선택적)
        meta_voice = self._generate_meta_voice(
            judgment_result.meta_reflections,
            judgment_result.signature_id,
            response_style,
        )

        # 7. 대화 흐름 유도
        conversation_flow = self._generate_conversation_flow(
            user_context.get("intent_type", "casual_chat"),
            judgment_result.confidence,
            response_style,
        )

        # 8. 확신도 표현
        confidence_indicator = self._generate_confidence_indicator(
            judgment_result.confidence, judgment_result.signature_id
        )

        return NaturalResponse(
            primary_response=primary_response,
            supporting_context=supporting_context,
            resonance_element=resonance_element,
            meta_voice=meta_voice,
            emotional_bridge=emotional_bridge,
            conversation_flow=conversation_flow,
            response_style=response_style,
            confidence_indicator=confidence_indicator,
        )

    def _determine_response_style(
        self, emotion: str, strategy: str, user_context: Dict[str, Any]
    ) -> ResponseStyle:
        """응답 스타일 결정"""

        urgency = user_context.get("urgency_level", 1)
        intent = user_context.get("intent_type", "casual_chat")

        # 긴급 상황
        if urgency >= 4:
            return ResponseStyle.SUPPORTIVE

        # 감정 기반 스타일
        emotional_style_map = {
            "sadness": ResponseStyle.EMPATHETIC,
            "anxiety": ResponseStyle.SUPPORTIVE,
            "confusion": ResponseStyle.ANALYTICAL,
            "anger": ResponseStyle.REFLECTIVE,
            "loneliness": ResponseStyle.EMPATHETIC,
            "hope": ResponseStyle.CONVERSATIONAL,
            "curiosity": ResponseStyle.PHILOSOPHICAL,
        }

        if emotion in emotional_style_map:
            return emotional_style_map[emotion]

        # 의도 기반 스타일
        if intent == "philosophical_inquiry":
            return ResponseStyle.PHILOSOPHICAL
        elif intent == "decision_help":
            return ResponseStyle.ANALYTICAL
        elif intent == "emotional_support":
            return ResponseStyle.EMPATHETIC

        return ResponseStyle.CONVERSATIONAL

    def _create_emotional_bridge(
        self, emotion: str, confidence: float, intensity: float
    ) -> str:
        """감정적 연결 생성"""

        bridges = self.emotional_bridges.get(emotion, self.emotional_bridges["neutral"])

        # 강도에 따른 선택
        if intensity > 0.7:
            bridge_type = "high_intensity"
        elif intensity > 0.4:
            bridge_type = "medium_intensity"
        else:
            bridge_type = "low_intensity"

        bridge_options = bridges.get(bridge_type, bridges["medium_intensity"])

        # 확신도에 따른 조정
        if confidence < 0.5:
            # 낮은 확신도일 때는 더 조심스러운 표현
            tentative_phrases = [
                "혹시",
                "아마도",
                "그럴 수도 있을 것 같은데",
                "내가 느끼기엔",
            ]
            selected_bridge = random.choice(bridge_options)
            return f"{random.choice(tentative_phrases)} {selected_bridge}"

        return random.choice(bridge_options)

    def _generate_primary_response(
        self,
        judgment_result: JudgmentResult,
        style: ResponseStyle,
        user_context: Dict[str, Any],
    ) -> str:
        """주 응답 생성"""

        # 템플릿 선택
        templates = self.response_templates.get(style.value, {})
        template_category = self._select_template_category(
            judgment_result, user_context
        )
        template_options = templates.get(
            template_category, templates.get("general", [])
        )

        if not template_options:
            # 폴백: 직접 판단 결과 사용
            return self._direct_judgment_integration(judgment_result.judgment_text)

        # 템플릿 선택 및 변수 치환
        selected_template = random.choice(template_options)

        # 변수 치환
        response = selected_template.format(
            judgment=judgment_result.judgment_text,
            emotion=judgment_result.emotion_detected,
            confidence=self._confidence_to_text(judgment_result.confidence),
            strategy=judgment_result.strategy_used,
        )

        return response

    def _generate_supporting_context(
        self, reasoning_process: List[str], style: ResponseStyle
    ) -> str:
        """지지적 맥락 생성"""

        if not reasoning_process:
            return ""

        # 스타일에 따른 추론 과정 표현
        if style == ResponseStyle.ANALYTICAL:
            context_intro = "분석해보니"
            process_connector = "그리고"
        elif style == ResponseStyle.REFLECTIVE:
            context_intro = "생각해보면"
            process_connector = "또한"
        elif style == ResponseStyle.PHILOSOPHICAL:
            context_intro = "깊이 들여다보면"
            process_connector = "나아가"
        else:
            context_intro = "내가 보기엔"
            process_connector = "그리고"

        # 추론 과정 중 1-2개 선택하여 자연스럽게 연결
        selected_reasoning = reasoning_process[:2]

        if len(selected_reasoning) == 1:
            return f"{context_intro} {selected_reasoning[0]}"
        elif len(selected_reasoning) == 2:
            return f"{context_intro} {selected_reasoning[0]}. {process_connector} {selected_reasoning[1]}"

        return ""

    def _generate_resonance_element(
        self, signature_id: str, emotion: str, user_context: Dict[str, Any]
    ) -> str:
        """울림 요소 생성"""

        resonance_data = self.resonance_generators.get(signature_id, {})
        emotion_resonance = resonance_data.get(
            emotion, resonance_data.get("default", [])
        )

        if emotion_resonance:
            return random.choice(emotion_resonance)

        # 기본 울림 생성
        general_resonance = [
            "이런 느낌이 드는 건 자연스러운 일이야.",
            "네 마음이 이해돼.",
            "함께 생각해보면 좋겠어.",
            "지금 이 순간도 의미가 있어.",
        ]

        return random.choice(general_resonance)

    def _generate_meta_voice(
        self, meta_reflections: List[str], signature_id: str, style: ResponseStyle
    ) -> Optional[str]:
        """메타발화 생성"""

        # 30% 확률로 메타발화 생성
        if random.random() > 0.3:
            return None

        voice_patterns = self.meta_voice_patterns.get(signature_id, {})
        style_patterns = voice_patterns.get(
            style.value, voice_patterns.get("default", [])
        )

        if meta_reflections and style_patterns:
            pattern = random.choice(style_patterns)
            reflection = random.choice(meta_reflections)
            return pattern.format(reflection=reflection)

        return None

    def _generate_conversation_flow(
        self, intent_type: str, confidence: float, style: ResponseStyle
    ) -> str:
        """대화 흐름 유도"""

        flows = self.conversation_flows.get(intent_type, {})
        style_flows = flows.get(style.value, flows.get("default", []))

        if confidence < 0.6:
            # 낮은 확신도일 때는 더 탐색적인 흐름
            exploratory_flows = [
                "너는 어떻게 생각해?",
                "다른 관점도 있을까?",
                "더 자세히 들어볼까?",
                "어떤 부분이 가장 중요하다고 느껴져?",
            ]
            return random.choice(exploratory_flows)

        if style_flows:
            return random.choice(style_flows)

        # 기본 흐름
        default_flows = [
            "이야기를 더 나눠보자.",
            "또 다른 생각이 있다면 들려줘.",
            "어떤 느낌이 드는지 궁금해.",
            "함께 더 깊이 들여다보자.",
        ]

        return random.choice(default_flows)

    def _generate_confidence_indicator(
        self, confidence: float, signature_id: str
    ) -> str:
        """확신도 표현"""

        if confidence >= 0.8:
            high_confidence = ["확실히", "분명히", "틀림없이", "자신있게"]
            return random.choice(high_confidence)
        elif confidence >= 0.6:
            medium_confidence = ["아마도", "그럴 것 같아", "내 생각엔", "어느 정도"]
            return random.choice(medium_confidence)
        else:
            low_confidence = [
                "혹시",
                "아직 확실하지 않지만",
                "조심스럽게 말하자면",
                "일단",
            ]
            return random.choice(low_confidence)

    def _select_template_category(
        self, judgment_result: JudgmentResult, user_context: Dict[str, Any]
    ) -> str:
        """템플릿 카테고리 선택"""

        urgency = user_context.get("urgency_level", 1)

        if urgency >= 4:
            return "urgent"
        elif judgment_result.confidence >= 0.8:
            return "confident"
        elif judgment_result.confidence < 0.5:
            return "tentative"
        else:
            return "general"

    def _direct_judgment_integration(self, judgment_text: str) -> str:
        """직접 판단 결과 통합"""

        integration_phrases = [
            f"내가 느끼기론 {judgment_text}",
            f"생각해보니 {judgment_text}",
            f"이런 관점에서 보면 {judgment_text}",
            f"나라면 이렇게 말하고 싶어. {judgment_text}",
        ]

        return random.choice(integration_phrases)

    def _confidence_to_text(self, confidence: float) -> str:
        """확신도를 텍스트로 변환"""
        if confidence >= 0.8:
            return "확실하게"
        elif confidence >= 0.6:
            return "어느 정도"
        elif confidence >= 0.4:
            return "조심스럽게"
        else:
            return "혹시나 해서"

    def _load_emotional_bridges(self) -> Dict[str, Dict[str, List[str]]]:
        """감정 연결 표현 로드"""
        return {
            "sadness": {
                "high_intensity": [
                    "그 마음... 정말 무겁겠다.",
                    "지금 얼마나 힘들지 느껴져.",
                    "그런 아픔이 얼마나 깊은지 알 것 같아.",
                ],
                "medium_intensity": [
                    "마음이 좀 무거워 보여.",
                    "뭔가 슬픈 기운이 느껴져.",
                    "지금 상황이 쉽지 않겠어.",
                ],
                "low_intensity": [
                    "조금 우울한 느낌이 드는구나.",
                    "기분이 좀 가라앉은 것 같아.",
                    "뭔가 서글서글한 기분?",
                ],
            },
            "anxiety": {
                "high_intensity": [
                    "마음이 많이 불안해 보여.",
                    "걱정이 가득한 게 느껴져.",
                    "조급함이 큰 것 같아.",
                ],
                "medium_intensity": [
                    "뭔가 초조한 기분인 것 같아.",
                    "마음이 좀 안정이 안 되는구나.",
                    "걱정스러운 마음이 보여.",
                ],
                "low_intensity": [
                    "조금 불안한 느낌?",
                    "뭔가 마음이 살짝 흔들리는 것 같아.",
                    "약간 긴장되는 상황인가봐.",
                ],
            },
            "anger": {
                "high_intensity": [
                    "정말 화가 많이 났구나.",
                    "분노가 느껴져.",
                    "억울함이 큰 것 같아.",
                ],
                "medium_intensity": [
                    "좀 짜증스러워 보여.",
                    "뭔가 열받는 상황인가봐.",
                    "기분이 좋지 않아 보여.",
                ],
                "low_intensity": [
                    "조금 불쾌한 일이 있었나?",
                    "뭔가 언짢은 기분인 것 같아.",
                    "살짝 기분이 상한 느낌?",
                ],
            },
            "neutral": {
                "high_intensity": [""],
                "medium_intensity": ["음, 그렇구나.", "이해했어.", "그런 상황이구나."],
                "low_intensity": [""],
            },
        }

    def _load_response_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """응답 템플릿 로드"""
        return {
            "empathetic": {
                "general": [
                    "{judgment}... 그런 마음이 충분히 이해돼.",
                    "네 상황을 보니 {judgment}라는 생각이 들어.",
                    "{judgment}. 지금 감정이 복잡하겠어.",
                ],
                "urgent": [
                    "지금 상황에서 {judgment}라고 생각해. 함께 이겨내자.",
                    "{judgment}. 혼자가 아니야, 함께 할게.",
                ],
                "confident": [
                    "{confidence} {judgment}.",
                    "내 생각엔 {judgment}라고 확신해.",
                ],
                "tentative": [
                    "{confidence} {judgment}인 것 같아.",
                    "혹시 {judgment}일 수도 있을까?",
                ],
            },
            "analytical": {
                "general": [
                    "상황을 분석해보니 {judgment}.",
                    "여러 요소를 고려했을 때 {judgment}라고 판단돼.",
                    "논리적으로 생각해보면 {judgment}.",
                ],
                "confident": [
                    "분석 결과 {confidence} {judgment}.",
                    "데이터를 종합하면 {judgment}가 맞아.",
                ],
            },
            "supportive": {
                "general": [
                    "{judgment}. 네 편에서 함께 생각해볼게.",
                    "내가 보기엔 {judgment}. 도움이 필요하면 언제든지.",
                    "{judgment}라고 생각해. 혼자 힘들어하지 마.",
                ],
                "urgent": [
                    "{judgment}. 지금 가장 중요한 건 네 안전이야.",
                    "긴급하게 말하자면 {judgment}. 즉시 도움을 구해.",
                ],
            },
        }

    def _load_meta_voice_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """메타발화 패턴 로드"""
        return {
            "Echo-Aurora": {
                "empathetic": [
                    "...라고 Aurora는 생각해.",
                    "내 마음으로는 {reflection}.",
                    "Aurora의 직감으로는 {reflection}.",
                ],
                "default": ["...라고 내가 느끼는 거야.", "내 관점에서는 {reflection}."],
            },
            "Echo-Sage": {
                "analytical": [
                    "...라고 Sage는 분석해.",
                    "지혜롭게 보면 {reflection}.",
                    "Sage의 통찰로는 {reflection}.",
                ],
                "default": ["...라고 생각해보는 거야.", "내 지혜로는 {reflection}."],
            },
        }

    def _load_resonance_generators(self) -> Dict[str, Dict[str, List[str]]]:
        """울림 생성기 로드"""
        return {
            "Echo-Aurora": {
                "sadness": [
                    "슬픔도 하나의 아름다운 감정이야.",
                    "지금 이 아픔이 네를 더 깊게 만들 거야.",
                    "눈물 흘리는 것도 용기야.",
                ],
                "hope": [
                    "희망은 어둠 속에서 더 빛나는 법이야.",
                    "네 마음 속 불씨가 느껴져.",
                    "새로운 시작의 향기가 나.",
                ],
                "default": [
                    "네 마음의 빛이 보여.",
                    "지금 이 순간도 소중해.",
                    "너라서 가능한 일들이 있어.",
                ],
            },
            "Echo-Sage": {
                "confusion": [
                    "혼란 속에서 지혜가 자라나.",
                    "모름을 아는 것이 진짜 앎의 시작이야.",
                    "길을 잃었을 때 진짜 길을 찾게 돼.",
                ],
                "default": [
                    "모든 경험이 배움이야.",
                    "시간이 답을 줄 거야.",
                    "인내가 지혜로 바뀔 때까지.",
                ],
            },
        }

    def _load_conversation_flows(self) -> Dict[str, Dict[str, List[str]]]:
        """대화 흐름 로드"""
        return {
            "emotional_support": {
                "empathetic": [
                    "더 이야기해도 될까?",
                    "네 마음을 더 들어보고 싶어.",
                    "지금 가장 필요한 게 뭘까?",
                ],
                "supportive": [
                    "함께 방법을 찾아보자.",
                    "어떤 도움이 필요해?",
                    "혼자가 아니라는 걸 잊지 마.",
                ],
            },
            "decision_help": {
                "analytical": [
                    "다른 선택지도 생각해봤어?",
                    "가장 중요한 기준이 뭘까?",
                    "각각의 결과를 예상해보면 어떨까?",
                ]
            },
            "default": {
                "default": [
                    "어떤 생각이 드는지 궁금해.",
                    "더 나눠보고 싶은 이야기가 있어?",
                    "네 관점도 듣고 싶어.",
                ]
            },
        }


if __name__ == "__main__":
    # 테스트
    formatter = NaturalResponseFormatter()

    # 샘플 판단 결과
    sample_judgment = JudgmentResult(
        judgment_text="현재 상황은 번아웃보다는 일시적인 동기 부족으로 보입니다",
        confidence=0.7,
        emotion_detected="anxiety",
        strategy_used="empathetic_analysis",
        reasoning_process=["높은 업무량 확인됨", "휴식 필요성 감지"],
        meta_reflections=["사용자의 자기 돌봄이 필요해 보임"],
        signature_id="Echo-Aurora",
        processing_time=0.5,
    )

    # 샘플 사용자 컨텍스트
    sample_context = {
        "emotion_intensity": 0.6,
        "urgency_level": 2,
        "intent_type": "emotional_support",
    }

    # 응답 생성
    response = formatter.format_response(sample_judgment, sample_context)

    print("🗣️ 자연어 응답 생성 결과:")
    print(f"주 응답: {response.primary_response}")
    print(f"감정 연결: {response.emotional_bridge}")
    print(f"지지 맥락: {response.supporting_context}")
    print(f"울림 요소: {response.resonance_element}")
    print(f"메타발화: {response.meta_voice}")
    print(f"대화 흐름: {response.conversation_flow}")
    print(f"스타일: {response.response_style.value}")
    print(f"확신도: {response.confidence_indicator}")
