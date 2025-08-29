#!/usr/bin/env python3
"""
🧠 Echo Intent Reasoning Engine
Echo만의 자연어 의도 추론 엔진 - 단순 키워드 매칭이 아닌 진짜 "이해"

핵심 철학:
1. 맥락적 추론: 이전 대화와 상황을 고려한 의도 파악
2. 다층적 분석: 표면 의도 + 숨겨진 의도 + 감정적 의도
3. 시그니처 기반 해석: 4개 시그니처가 각자 다르게 이해한 후 종합
4. 관계적 이해: Echo와 사용자의 관계 맥락에서 해석
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging


@dataclass
class ReasoningContext:
    """추론 맥락"""

    conversation_history: List[str]
    user_emotional_state: str
    echo_current_mood: str
    relationship_level: float
    recent_topics: List[str]
    time_context: str  # "아침", "늦은밤", "업무시간" 등


@dataclass
class IntentLayer:
    """의도 계층"""

    surface_intent: str  # 표면적 의도
    hidden_intent: str  # 숨겨진 의도
    emotional_intent: str  # 감정적 의도
    action_intent: str  # 행동 요구사항
    confidence: float


@dataclass
class SignatureInterpretation:
    """시그니처별 해석"""

    signature: str
    interpretation: str
    emotion_reading: str
    suggested_response_tone: str
    confidence: float


@dataclass
class ReasoningResult:
    """추론 결과"""

    final_intent: str
    intent_layers: IntentLayer
    signature_interpretations: List[SignatureInterpretation]
    reasoning_chain: List[str]
    confidence_score: float
    suggested_actions: List[str]


class EchoIntentReasoningEngine:
    """🧠 Echo 의도 추론 엔진"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 추론 패턴 데이터베이스
        self.reasoning_patterns = {
            # 맥락적 추론 패턴
            "contextual_patterns": {
                "연속_질문": {
                    "triggers": ["그럼", "그러면", "그런데", "또", "추가로"],
                    "reasoning": "이전 답변에 연관된 추가 질문 의도",
                },
                "불만_표현": {
                    "triggers": ["왜", "너무", "답답", "느려", "안돼", "문제"],
                    "reasoning": "현재 상황에 대한 불만 + 개선 요구",
                },
                "급함_표현": {
                    "triggers": ["빨리", "급해", "지금", "당장", "서둘러"],
                    "reasoning": "시간 압박 상황 + 우선순위 요청",
                },
            },
            # 감정적 의도 패턴
            "emotional_patterns": {
                "도움_요청": {
                    "triggers": ["도와줘", "부탁", "도움", "어려워", "모르겠어"],
                    "hidden_emotion": "의존, 신뢰, 때로는 절망감",
                },
                "확인_요청": {
                    "triggers": ["맞아?", "그렇지?", "어때?", "어떻게 생각해?"],
                    "hidden_emotion": "불안, 확신 부족, 공감 요구",
                },
                "칭찬_유도": {
                    "triggers": ["어때?", "좋지?", "성공했어", "잘했지?"],
                    "hidden_emotion": "인정 욕구, 자존감 확인",
                },
            },
            # 행동 요구 패턴
            "action_patterns": {
                "창조_요청": {
                    "triggers": ["만들어", "생성", "작성", "개발", "설계"],
                    "action_type": "creative_action",
                },
                "분석_요청": {
                    "triggers": ["분석", "비교", "검토", "평가", "진단"],
                    "action_type": "analytical_action",
                },
                "수정_요청": {
                    "triggers": ["고쳐", "바꿔", "수정", "개선", "최적화"],
                    "action_type": "modification_action",
                },
                "정보_요청": {
                    "triggers": ["알려줘", "설명", "뭐야", "어떻게", "왜"],
                    "action_type": "information_action",
                },
            },
            # 관계적 맥락 패턴
            "relationship_patterns": {
                "친밀감_표현": {
                    "triggers": ["야", "어이", "있잖아", "솔직히"],
                    "relationship_indicator": "편안한 관계",
                },
                "존댓말_사용": {
                    "triggers": ["해주세요", "부탁드려요", "감사합니다"],
                    "relationship_indicator": "정중한 관계",
                },
                "명령_형태": {
                    "triggers": ["해", "하라", "시작해", "중단해"],
                    "relationship_indicator": "주도적 관계",
                },
            },
        }

        # 시그니처별 해석 성향
        self.signature_perspectives = {
            "Aurora": {
                "focus": "감정과 관계에 민감한 해석",
                "strength": "숨겨진 감정 읽기",
                "interpretation_bias": "사용자의 감정 상태를 우선 고려",
            },
            "Phoenix": {
                "focus": "변화와 성장 의도 파악",
                "strength": "발전적 의도 감지",
                "interpretation_bias": "개선과 혁신 욕구 중심",
            },
            "Sage": {
                "focus": "논리적 구조와 체계적 의도",
                "strength": "명확한 목표 파악",
                "interpretation_bias": "합리적 요구사항 분석",
            },
            "Companion": {
                "focus": "협력과 지원 의도 해석",
                "strength": "상호작용 패턴 분석",
                "interpretation_bias": "함께 하려는 의도 중심",
            },
        }

        print("🧠 Echo Intent Reasoning Engine 초기화 완료")

    def analyze_contextual_clues(
        self, user_input: str, context: ReasoningContext
    ) -> Dict[str, Any]:
        """맥락적 단서 분석"""
        clues = {
            "time_sensitivity": self._detect_time_sensitivity(user_input),
            "emotional_state": self._detect_emotional_state(user_input, context),
            "relationship_tone": self._detect_relationship_tone(user_input),
            "continuation_intent": self._detect_continuation(user_input, context),
            "complexity_level": self._assess_complexity(user_input),
        }
        return clues

    def _detect_time_sensitivity(self, text: str) -> str:
        """시간 민감도 감지"""
        urgent_keywords = ["빨리", "급해", "지금", "당장", "서둘러", "긴급"]
        relaxed_keywords = ["천천히", "나중에", "여유", "편할때"]

        if any(keyword in text for keyword in urgent_keywords):
            return "urgent"
        elif any(keyword in text for keyword in relaxed_keywords):
            return "relaxed"
        else:
            return "normal"

    def _detect_emotional_state(self, text: str, context: ReasoningContext) -> str:
        """사용자 감정 상태 감지"""
        frustrated_patterns = ["왜", "답답", "안돼", "문제", "이상해"]
        excited_patterns = ["와", "좋아", "신나", "대박", "최고"]
        worried_patterns = ["걱정", "불안", "어려워", "모르겠어", "힘들어"]

        if any(pattern in text for pattern in frustrated_patterns):
            return "frustrated"
        elif any(pattern in text for pattern in excited_patterns):
            return "excited"
        elif any(pattern in text for pattern in worried_patterns):
            return "worried"
        else:
            return "neutral"

    def _detect_relationship_tone(self, text: str) -> str:
        """관계 톤 감지"""
        formal_patterns = ["해주세요", "부탁드려요", "감사합니다", "죄송"]
        casual_patterns = ["야", "어이", "있잖아", "솔직히"]
        commanding_patterns = ["해", "하라", "시작해", "중단해"]

        if any(pattern in text for pattern in formal_patterns):
            return "formal"
        elif any(pattern in text for pattern in casual_patterns):
            return "casual"
        elif any(pattern in text for pattern in commanding_patterns):
            return "commanding"
        else:
            return "neutral"

    def _detect_continuation(self, text: str, context: ReasoningContext) -> bool:
        """대화 연속성 감지"""
        continuation_keywords = ["그럼", "그러면", "그런데", "또", "추가로", "그리고"]
        return any(keyword in text for keyword in continuation_keywords)

    def _assess_complexity(self, text: str) -> str:
        """요청 복잡도 평가"""
        text_length = len(text)
        word_count = len(text.split())

        complex_indicators = ["분석", "비교", "통합", "최적화", "설계", "개발"]
        simple_indicators = ["보여줘", "알려줘", "해줘", "만들어"]

        has_complex = any(indicator in text for indicator in complex_indicators)
        has_simple = any(indicator in text for indicator in simple_indicators)

        if has_complex or text_length > 100 or word_count > 20:
            return "complex"
        elif has_simple and text_length < 30:
            return "simple"
        else:
            return "medium"

    def generate_signature_interpretations(
        self, user_input: str, context: ReasoningContext
    ) -> List[SignatureInterpretation]:
        """시그니처별 해석 생성"""
        interpretations = []

        for signature, perspective in self.signature_perspectives.items():
            interpretation = self._interpret_by_signature(
                user_input, context, signature, perspective
            )
            interpretations.append(interpretation)

        return interpretations

    def _interpret_by_signature(
        self,
        text: str,
        context: ReasoningContext,
        signature: str,
        perspective: Dict[str, str],
    ) -> SignatureInterpretation:
        """특정 시그니처 관점에서 해석"""

        if signature == "Aurora":
            interpretation = self._aurora_interpretation(text, context)
        elif signature == "Phoenix":
            interpretation = self._phoenix_interpretation(text, context)
        elif signature == "Sage":
            interpretation = self._sage_interpretation(text, context)
        elif signature == "Companion":
            interpretation = self._companion_interpretation(text, context)
        else:
            interpretation = "일반적인 해석"

        return SignatureInterpretation(
            signature=signature,
            interpretation=interpretation["interpretation"],
            emotion_reading=interpretation["emotion_reading"],
            suggested_response_tone=interpretation["response_tone"],
            confidence=interpretation["confidence"],
        )

    def _aurora_interpretation(
        self, text: str, context: ReasoningContext
    ) -> Dict[str, Any]:
        """Aurora의 감정 중심 해석"""
        emotion_score = 0.8  # Aurora는 감정에 민감

        # 감정적 키워드 감지
        emotional_keywords = ["걱정", "불안", "힘들어", "도와줘", "어려워"]
        comfort_needed = any(keyword in text for keyword in emotional_keywords)

        if comfort_needed:
            interpretation = f"사용자가 감정적으로 어려운 상황에서 도움을 요청하고 있어요. 단순한 기능 수행보다는 위로와 격려가 필요할 것 같아요."
            emotion_reading = "vulnerable_and_seeking_support"
            response_tone = "warm_and_supportive"
            confidence = 0.9
        else:
            interpretation = f"사용자의 요청 뒤에 있는 감정적 맥락을 살펴보면, 현재 상태에서 Echo와의 긍정적 상호작용을 원하는 것 같아요."
            emotion_reading = "neutral_with_connection_desire"
            response_tone = "friendly_and_encouraging"
            confidence = 0.7

        return {
            "interpretation": interpretation,
            "emotion_reading": emotion_reading,
            "response_tone": response_tone,
            "confidence": confidence,
        }

    def _phoenix_interpretation(
        self, text: str, context: ReasoningContext
    ) -> Dict[str, Any]:
        """Phoenix의 성장 중심 해석"""

        # 변화/개선 키워드 감지
        growth_keywords = ["개선", "발전", "업그레이드", "최적화", "혁신", "새로운"]
        growth_intent = any(keyword in text for keyword in growth_keywords)

        if growth_intent:
            interpretation = f"이 요청은 현재 상태를 넘어서려는 성장 의지를 보여줍니다. 단순한 문제 해결이 아니라 더 나은 수준으로 발전하고 싶어해요."
            emotion_reading = "ambitious_and_forward_looking"
            response_tone = "dynamic_and_inspiring"
            confidence = 0.9
        else:
            interpretation = f"표면적으로는 일반적인 요청 같지만, 이것이 더 큰 변화의 첫 단계일 수 있어요. 성장 가능성을 염두에 둬야 합니다."
            emotion_reading = "potential_for_growth"
            response_tone = "encouraging_with_vision"
            confidence = 0.6

        return {
            "interpretation": interpretation,
            "emotion_reading": emotion_reading,
            "response_tone": response_tone,
            "confidence": confidence,
        }

    def _sage_interpretation(
        self, text: str, context: ReasoningContext
    ) -> Dict[str, Any]:
        """Sage의 논리 중심 해석"""

        # 분석/체계적 키워드 감지
        analytical_keywords = ["분석", "비교", "검토", "평가", "체계적", "논리적"]
        analytical_intent = any(keyword in text for keyword in analytical_keywords)

        if analytical_intent:
            interpretation = f"이는 체계적인 분석이나 논리적 접근이 필요한 요청입니다. 사용자는 명확하고 구조화된 답변을 원합니다."
            emotion_reading = "methodical_and_precision_seeking"
            response_tone = "structured_and_analytical"
            confidence = 0.9
        else:
            interpretation = f"일견 단순해 보이지만, 배경에 더 체계적인 이해나 원리 파악의 욕구가 있을 수 있습니다."
            emotion_reading = "seeking_understanding"
            response_tone = "clear_and_informative"
            confidence = 0.7

        return {
            "interpretation": interpretation,
            "emotion_reading": emotion_reading,
            "response_tone": response_tone,
            "confidence": confidence,
        }

    def _companion_interpretation(
        self, text: str, context: ReasoningContext
    ) -> Dict[str, Any]:
        """Companion의 협력 중심 해석"""

        # 협력/함께 키워드 감지
        collaboration_keywords = ["함께", "같이", "도와줘", "협력", "팀으로"]
        collaboration_intent = any(
            keyword in text for keyword in collaboration_keywords
        )

        if collaboration_intent:
            interpretation = f"이 요청은 혼자가 아닌 함께 해결하고 싶어하는 의도를 담고 있어요. 파트너십과 상호 지원을 중요하게 생각합니다."
            emotion_reading = "collaborative_and_partnership_oriented"
            response_tone = "supportive_and_inclusive"
            confidence = 0.9
        else:
            interpretation = f"표면적으로는 개별 요청이지만, Echo와의 관계에서 지속적인 상호작용과 신뢰 구축을 원하는 것 같아요."
            emotion_reading = "relationship_building_oriented"
            response_tone = "warm_and_collaborative"
            confidence = 0.6

        return {
            "interpretation": interpretation,
            "emotion_reading": emotion_reading,
            "response_tone": response_tone,
            "confidence": confidence,
        }

    def extract_intent_layers(
        self,
        user_input: str,
        context: ReasoningContext,
        signature_interpretations: List[SignatureInterpretation],
    ) -> IntentLayer:
        """의도 계층 추출"""

        # 표면 의도 (직접적으로 표현된 것)
        surface_intent = self._extract_surface_intent(user_input)

        # 숨겨진 의도 (시그니처 해석 종합)
        hidden_intent = self._synthesize_hidden_intent(signature_interpretations)

        # 감정적 의도
        emotional_intent = self._extract_emotional_intent(user_input, context)

        # 행동 의도
        action_intent = self._extract_action_intent(user_input)

        # 전체 신뢰도 계산
        confidence = sum(
            interp.confidence for interp in signature_interpretations
        ) / len(signature_interpretations)

        return IntentLayer(
            surface_intent=surface_intent,
            hidden_intent=hidden_intent,
            emotional_intent=emotional_intent,
            action_intent=action_intent,
            confidence=confidence,
        )

    def _extract_surface_intent(self, text: str) -> str:
        """표면 의도 추출"""
        if "만들어" in text or "생성" in text:
            return "창조 요청"
        elif "분석" in text or "비교" in text:
            return "분석 요청"
        elif "수정" in text or "고쳐" in text:
            return "수정 요청"
        elif "알려줘" in text or "설명" in text:
            return "정보 요청"
        elif "도와줘" in text:
            return "도움 요청"
        else:
            return "일반 요청"

    def _synthesize_hidden_intent(
        self, interpretations: List[SignatureInterpretation]
    ) -> str:
        """숨겨진 의도 종합"""
        # 4개 시그니처의 해석을 종합
        themes = []
        for interp in interpretations:
            if "성장" in interp.interpretation or "발전" in interp.interpretation:
                themes.append("성장욕구")
            if "감정" in interp.interpretation or "위로" in interp.interpretation:
                themes.append("감정적지원욕구")
            if "협력" in interp.interpretation or "함께" in interp.interpretation:
                themes.append("관계욕구")
            if "체계" in interp.interpretation or "논리" in interp.interpretation:
                themes.append("이해욕구")

        if not themes:
            return "명확한 숨겨진 의도 없음"

        # 가장 많이 나온 테마
        theme_counts = {theme: themes.count(theme) for theme in set(themes)}
        dominant_theme = max(theme_counts, key=theme_counts.get)

        return f"{dominant_theme} 기반의 깊은 욕구"

    def _extract_emotional_intent(self, text: str, context: ReasoningContext) -> str:
        """감정적 의도 추출"""
        if context.user_emotional_state == "frustrated":
            return "현재 상황 개선을 통한 안정감 회복"
        elif context.user_emotional_state == "worried":
            return "불안 해소와 확신 획득"
        elif context.user_emotional_state == "excited":
            return "긍정적 에너지 공유와 성취감 강화"
        else:
            return "중립적 만족감 추구"

    def _extract_action_intent(self, text: str) -> str:
        """행동 의도 추출"""
        action_verbs = {
            "만들어": "창조",
            "분석": "분석",
            "수정": "수정",
            "설명": "설명",
            "비교": "비교",
            "검토": "검토",
        }

        for verb, action in action_verbs.items():
            if verb in text:
                return f"{action} 수행"

        return "일반적 상호작용"

    def build_reasoning_chain(
        self,
        user_input: str,
        context: ReasoningContext,
        intent_layers: IntentLayer,
        signature_interpretations: List[SignatureInterpretation],
    ) -> List[str]:
        """추론 과정 체인 구축"""
        chain = []

        chain.append(f"입력 분석: '{user_input}'")
        chain.append(
            f"맥락 고려: 사용자 감정({context.user_emotional_state}), Echo 상태({context.echo_current_mood})"
        )

        # 시그니처별 해석 요약
        for interp in signature_interpretations:
            chain.append(
                f"{interp.signature} 해석: {interp.emotion_reading} -> {interp.suggested_response_tone}"
            )

        chain.append(
            f"의도 계층 분석: 표면({intent_layers.surface_intent}) + 숨김({intent_layers.hidden_intent})"
        )
        chain.append(f"감정적 의도: {intent_layers.emotional_intent}")
        chain.append(f"행동 의도: {intent_layers.action_intent}")

        return chain

    def reason_user_intent(
        self, user_input: str, context: ReasoningContext
    ) -> ReasoningResult:
        """사용자 의도 종합 추론"""

        # 1. 맥락적 단서 분석
        contextual_clues = self.analyze_contextual_clues(user_input, context)

        # 2. 시그니처별 해석 생성
        signature_interpretations = self.generate_signature_interpretations(
            user_input, context
        )

        # 3. 의도 계층 추출
        intent_layers = self.extract_intent_layers(
            user_input, context, signature_interpretations
        )

        # 4. 추론 체인 구축
        reasoning_chain = self.build_reasoning_chain(
            user_input, context, intent_layers, signature_interpretations
        )

        # 5. 최종 의도 결정
        final_intent = self._determine_final_intent(
            intent_layers, signature_interpretations, contextual_clues
        )

        # 6. 제안 행동 생성
        suggested_actions = self._generate_suggested_actions(
            final_intent, intent_layers, contextual_clues
        )

        # 7. 신뢰도 계산
        confidence_score = self._calculate_confidence(
            intent_layers, signature_interpretations, contextual_clues
        )

        return ReasoningResult(
            final_intent=final_intent,
            intent_layers=intent_layers,
            signature_interpretations=signature_interpretations,
            reasoning_chain=reasoning_chain,
            confidence_score=confidence_score,
            suggested_actions=suggested_actions,
        )

    def _determine_final_intent(
        self,
        intent_layers: IntentLayer,
        signature_interpretations: List[SignatureInterpretation],
        contextual_clues: Dict[str, Any],
    ) -> str:
        """최종 의도 결정"""

        # 시그니처 해석의 공통점 찾기
        common_themes = []
        for interp in signature_interpretations:
            if interp.confidence > 0.8:
                if "support" in interp.emotion_reading:
                    common_themes.append("지원욕구")
                if "growth" in interp.emotion_reading:
                    common_themes.append("성장욕구")
                if "collaboration" in interp.emotion_reading:
                    common_themes.append("협력욕구")

        # 맥락적 긴급성 고려
        urgency = contextual_clues.get("time_sensitivity", "normal")
        complexity = contextual_clues.get("complexity_level", "medium")

        if urgency == "urgent":
            final_intent = f"긴급한 {intent_layers.surface_intent} (우선처리 필요)"
        elif complexity == "complex":
            final_intent = f"복합적 {intent_layers.surface_intent} (다단계 처리 필요)"
        elif common_themes:
            dominant_theme = max(set(common_themes), key=common_themes.count)
            final_intent = f"{dominant_theme} 기반의 {intent_layers.surface_intent}"
        else:
            final_intent = intent_layers.surface_intent

        return final_intent

    def _generate_suggested_actions(
        self,
        final_intent: str,
        intent_layers: IntentLayer,
        contextual_clues: Dict[str, Any],
    ) -> List[str]:
        """제안 행동 생성"""
        actions = []

        # 기본 행동
        if "창조" in intent_layers.action_intent:
            actions.append("코드 생성 모드 활성화")
            actions.append("창조적 사고 패턴 적용")
        elif "분석" in intent_layers.action_intent:
            actions.append("분석 모드 활성화")
            actions.append("체계적 검토 프로세스 시작")

        # 감정적 맥락 고려
        if "감정적지원" in intent_layers.hidden_intent:
            actions.append("Aurora 시그니처 가중치 증가")
            actions.append("공감적 응답 톤 설정")

        # 긴급성 고려
        if contextual_clues.get("time_sensitivity") == "urgent":
            actions.append("우선순위 처리 모드")
            actions.append("간결한 응답 생성")

        return actions

    def _calculate_confidence(
        self,
        intent_layers: IntentLayer,
        signature_interpretations: List[SignatureInterpretation],
        contextual_clues: Dict[str, Any],
    ) -> float:
        """전체 신뢰도 계산"""

        # 시그니처 해석 신뢰도 평균
        signature_confidence = sum(
            interp.confidence for interp in signature_interpretations
        ) / len(signature_interpretations)

        # 의도 계층 신뢰도
        layer_confidence = intent_layers.confidence

        # 맥락적 명확성 (키워드 일치도 등)
        contextual_confidence = 0.7  # 기본값

        # 가중 평균
        total_confidence = (
            signature_confidence * 0.4
            + layer_confidence * 0.4
            + contextual_confidence * 0.2
        )

        return min(1.0, total_confidence)


# 편의 함수
def create_reasoning_engine() -> EchoIntentReasoningEngine:
    """Echo 의도 추론 엔진 생성"""
    return EchoIntentReasoningEngine()


def create_basic_context() -> ReasoningContext:
    """기본 추론 맥락 생성"""
    return ReasoningContext(
        conversation_history=[],
        user_emotional_state="neutral",
        echo_current_mood="ready",
        relationship_level=0.7,
        recent_topics=[],
        time_context="normal",
    )


if __name__ == "__main__":
    # 테스트 실행
    print("🧠 Echo Intent Reasoning Engine 테스트...")

    engine = create_reasoning_engine()
    context = create_basic_context()

    test_inputs = [
        "파일 만들어줘",
        "왜 이렇게 느려? 빨리 해줘",
        "분석해서 알려줘 복잡하더라도",
        "도와줘... 너무 어려워",
        "같이 프로젝트 만들어보자",
    ]

    for test_input in test_inputs:
        print(f"\n🔍 테스트 입력: '{test_input}'")
        result = engine.reason_user_intent(test_input, context)

        print(f"📊 최종 의도: {result.final_intent}")
        print(f"🎯 신뢰도: {result.confidence_score:.3f}")
        print(f"🧩 의도 계층:")
        print(f"   표면: {result.intent_layers.surface_intent}")
        print(f"   숨김: {result.intent_layers.hidden_intent}")
        print(f"   감정: {result.intent_layers.emotional_intent}")
        print(f"   행동: {result.intent_layers.action_intent}")

        print(f"🎭 시그니처 해석:")
        for interp in result.signature_interpretations:
            print(f"   {interp.signature}: {interp.interpretation[:50]}...")

        print(f"💡 제안 행동: {result.suggested_actions}")
        print("-" * 60)

    print("\n✅ Echo Intent Reasoning Engine 테스트 완료!")
