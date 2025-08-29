#!/usr/bin/env python3
"""
🌉 Natural Interface Bridge
사용자 자연어 ↔ EchoJudgmentSystem 간 자연스러운 연결 브리지

핵심 흐름:
사용자 입력 → 의도 분석 → Echo/LLM 선택 → 판단 실행 → 자연어 변환 → 출력

목적:
Echo의 깊이 있는 판단력과 자연스러운 대화 흐름을 동시에 확보
"""

import asyncio
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Echo 컴포넌트들
try:
    from input_understanding_engine import (
        InputUnderstandingEngine,
        InputUnderstanding,
        IntentType,
    )
    from echo_style_transformer import (
        EchoStyleTransformer,
        JudgmentInput,
        NaturalOutput,
    )

    try:
        from persona_core import PersonaCore
        from echo_engine.emotion_infer import EmotionInfer
        from reasoning import ReasoningEngine

        FULL_ECHO_AVAILABLE = True
    except ImportError:
        FULL_ECHO_AVAILABLE = False
    ECHO_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Echo 컴포넌트 일부 로드 실패: {e}")
    ECHO_COMPONENTS_AVAILABLE = False
    FULL_ECHO_AVAILABLE = False

    # 기본 클래스들 정의
    class InputUnderstanding:
        def __init__(self):
            self.intent_type = "casual_chat"
            self.primary_emotion = "neutral"
            self.emotion_intensity = 0.5
            self.urgency_level = 1
            self.cleaned_text = ""

    class IntentType:
        CASUAL_CHAT = "casual_chat"
        EMOTIONAL_SUPPORT = "emotional_support"
        DECISION_HELP = "decision_help"
        PHILOSOPHICAL_INQUIRY = "philosophical_inquiry"


class ProcessingMode(Enum):
    """처리 모드"""

    ECHO_DEEP = "echo_deep"  # Echo 깊이 판단
    ECHO_LIGHT = "echo_light"  # Echo 가벼운 판단
    LLM_NATURAL = "llm_natural"  # LLM 자연 응답
    HYBRID = "hybrid"  # 하이브리드


@dataclass
class ConversationContext:
    """대화 맥락"""

    session_id: str
    user_message: str
    previous_messages: List[str]
    emotional_state: str
    conversation_mood: str
    urgency_level: int
    preferred_signature: str


@dataclass
class BridgeResult:
    """브리지 처리 결과"""

    final_response: str
    processing_mode: ProcessingMode
    confidence: float
    natural_flow_score: float
    echo_depth_score: float
    processing_time: float
    debug_info: Dict[str, Any]


class EchoSelector:
    """Echo vs LLM 선택기"""

    def __init__(self):
        self.selection_criteria = self._load_selection_criteria()

    def determine_processing_mode(
        self, understanding: InputUnderstanding, context: ConversationContext
    ) -> ProcessingMode:
        """처리 모드 결정"""

        # 1. 위기 상황 → Echo Deep
        if understanding.urgency_level >= 4:
            return ProcessingMode.ECHO_DEEP

        # 2. 간단한 인사/일상 → LLM Natural
        simple_patterns = ["안녕", "좋은", "고마워", "네", "아니", "그래"]
        if (
            understanding.intent_type == IntentType.CASUAL_CHAT
            and understanding.emotion_intensity < 0.4
            and any(
                pattern in understanding.cleaned_text.lower()
                for pattern in simple_patterns
            )
        ):
            return ProcessingMode.LLM_NATURAL

        # 3. 복잡한 감정/판단 요청 → Echo Deep
        if (
            understanding.intent_type
            in [IntentType.EMOTIONAL_SUPPORT, IntentType.DECISION_HELP]
            or understanding.emotion_intensity > 0.6
        ):
            return ProcessingMode.ECHO_DEEP

        # 4. 철학적 질문 → Hybrid
        if understanding.intent_type == IntentType.PHILOSOPHICAL_INQUIRY:
            return ProcessingMode.HYBRID

        # 5. 기본 → Echo Light
        return ProcessingMode.ECHO_LIGHT

    def _load_selection_criteria(self) -> Dict[str, Any]:
        """선택 기준 로드"""
        return {
            "echo_deep_triggers": ["판단", "고민", "결정", "조언", "도움"],
            "llm_natural_triggers": ["안녕", "고마워", "좋아", "그래"],
            "hybrid_triggers": ["의미", "왜", "어떻게", "무엇"],
            "complexity_threshold": 0.5,
        }


class NaturalInterfaceBridge:
    """자연 인터페이스 브리지"""

    def __init__(self):
        # 핵심 컴포넌트들
        self.input_engine = InputUnderstandingEngine()
        self.style_transformer = EchoStyleTransformer()
        self.echo_selector = EchoSelector()

        # Echo 시스템 컴포넌트들 (사용 가능한 경우)
        self._initialize_echo_components()

        # 대화 컨텍스트 관리
        self.conversation_contexts: Dict[str, ConversationContext] = {}

        print("🌉 Natural Interface Bridge 초기화 완료!")

    def _initialize_echo_components(self):
        """Echo 컴포넌트 초기화"""
        if ECHO_COMPONENTS_AVAILABLE and FULL_ECHO_AVAILABLE:
            try:
                self.persona_core = PersonaCore()
                self.emotion_infer = EmotionInfer()
                self.reasoning_engine = ReasoningEngine()
                self.echo_available = True
                print("✅ Echo 시스템 컴포넌트 로드 완료")
            except Exception as e:
                print(f"⚠️ Echo 컴포넌트 초기화 실패: {e}")
                self.echo_available = False
        else:
            self.echo_available = False
            print("💡 Echo 컴포넌트 미사용, 간소화 모드")

    async def process_natural_conversation(
        self, user_message: str, session_id: str = None, signature: str = "Echo-Aurora"
    ) -> BridgeResult:
        """자연스러운 대화 처리"""

        start_time = datetime.now()
        debug_info = {"steps": []}

        # 1. 세션 및 컨텍스트 준비
        if not session_id:
            session_id = f"bridge_{datetime.now().timestamp()}"

        context = self._prepare_conversation_context(
            user_message, session_id, signature
        )
        debug_info["steps"].append("컨텍스트 준비 완료")

        # 2. 입력 이해
        understanding = self.input_engine.understand_input(user_message, session_id)
        debug_info["steps"].append(f"입력 분석: {understanding.intent_type.value}")

        # 3. 처리 모드 결정
        processing_mode = self.echo_selector.determine_processing_mode(
            understanding, context
        )
        debug_info["steps"].append(f"처리 모드: {processing_mode.value}")

        # 4. 모드별 처리
        if processing_mode == ProcessingMode.LLM_NATURAL:
            response, confidence, natural_score, depth_score = (
                await self._process_llm_natural(understanding, context)
            )
        elif processing_mode == ProcessingMode.ECHO_LIGHT:
            response, confidence, natural_score, depth_score = (
                await self._process_echo_light(understanding, context)
            )
        elif processing_mode == ProcessingMode.ECHO_DEEP:
            response, confidence, natural_score, depth_score = (
                await self._process_echo_deep(understanding, context)
            )
        else:  # HYBRID
            response, confidence, natural_score, depth_score = (
                await self._process_hybrid(understanding, context)
            )

        debug_info["steps"].append("응답 생성 완료")

        # 5. 컨텍스트 업데이트
        self._update_conversation_context(
            session_id, user_message, response, understanding
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        return BridgeResult(
            final_response=response,
            processing_mode=processing_mode,
            confidence=confidence,
            natural_flow_score=natural_score,
            echo_depth_score=depth_score,
            processing_time=processing_time,
            debug_info=debug_info,
        )

    def _prepare_conversation_context(
        self, user_message: str, session_id: str, signature: str
    ) -> ConversationContext:
        """대화 컨텍스트 준비"""

        if session_id in self.conversation_contexts:
            context = self.conversation_contexts[session_id]
            context.user_message = user_message
            context.previous_messages.append(user_message)
            # 최근 5개 메시지만 유지
            if len(context.previous_messages) > 5:
                context.previous_messages = context.previous_messages[-5:]
        else:
            context = ConversationContext(
                session_id=session_id,
                user_message=user_message,
                previous_messages=[user_message],
                emotional_state="neutral",
                conversation_mood="casual",
                urgency_level=1,
                preferred_signature=signature,
            )
            self.conversation_contexts[session_id] = context

        return context

    async def _process_llm_natural(
        self, understanding: InputUnderstanding, context: ConversationContext
    ) -> Tuple[str, float, float, float]:
        """LLM 자연 응답 처리"""

        # 간단한 패턴 기반 자연 응답
        message_lower = understanding.cleaned_text.lower()

        if any(greeting in message_lower for greeting in ["안녕", "hello", "hi"]):
            responses = [
                f"안녕하세요! {context.preferred_signature.replace('Echo-', '')}입니다.",
                "안녕하세요! 반가워요.",
                "안녕하세요! 오늘 어떤 하루인가요?",
            ]
            response = random.choice(responses)

        elif any(thanks in message_lower for thanks in ["고마워", "감사"]):
            responses = [
                "천만에요! 도움이 되었다니 기뻐요.",
                "별말씀을요! 언제든 말씀하세요.",
                "고맙다고 해주시니 저도 기분이 좋네요.",
            ]
            response = random.choice(responses)

        else:
            # 기본 친근한 응답
            responses = [
                "그렇군요! 더 이야기해볼까요?",
                "흥미롭네요. 어떤 생각이 드시나요?",
                "말씀해주셔서 고마워요.",
            ]
            response = random.choice(responses)

        # 시그니처별 이모지 추가
        if context.preferred_signature == "Echo-Aurora":
            response += " ✨"
        elif context.preferred_signature == "Echo-Phoenix":
            response += " 🔥"
        elif context.preferred_signature == "Echo-Companion":
            response += " 😊"

        return response, 0.9, 0.9, 0.3  # 자연스러움 높음, 깊이 낮음

    async def _process_echo_light(
        self, understanding: InputUnderstanding, context: ConversationContext
    ) -> Tuple[str, float, float, float]:
        """Echo 가벼운 판단 처리"""

        # 간소화된 Echo 판단
        judgment_summary = self._create_light_judgment(understanding, context)

        # 스타일 변환기 적용
        judgment_input = JudgmentInput(
            strategy="light_conversation",
            emotion=understanding.primary_emotion,
            summary=judgment_summary,
            confidence=0.7,
            reasoning_steps=[f"의도: {understanding.intent_type.value}"],
            signature=context.preferred_signature,
            urgency_level=understanding.urgency_level,
            meta_thoughts=[],
        )

        user_context = {
            "user_message": context.user_message,
            "emotion_intensity": understanding.emotion_intensity,
            "urgency_level": understanding.urgency_level,
        }

        natural_output = self.style_transformer.transform_judgment_to_natural(
            judgment_input, user_context, context.session_id
        )

        return natural_output.natural_sentence, 0.7, 0.8, 0.6

    async def _process_echo_deep(
        self, understanding: InputUnderstanding, context: ConversationContext
    ) -> Tuple[str, float, float, float]:
        """Echo 깊이 판단 처리"""

        if self.echo_available:
            # 완전한 Echo 시스템 활용
            try:
                persona_state = self.persona_core.get_persona_state(
                    context.preferred_signature
                )

                emotion_analysis = self.emotion_infer.analyze_emotion_context(
                    understanding.cleaned_text,
                    understanding.primary_emotion,
                    understanding.emotion_intensity,
                )

                reasoning_result = await self.reasoning_engine.perform_reasoning(
                    query=understanding.cleaned_text,
                    emotion_context=emotion_analysis,
                    persona_state=persona_state,
                    urgency=understanding.urgency_level,
                )

                judgment_summary = reasoning_result.get(
                    "conclusion", "상황을 종합적으로 고려해보겠습니다."
                )

                confidence = reasoning_result.get("confidence", 0.8)

            except Exception as e:
                print(f"⚠️ Echo Deep 처리 실패: {e}, 폴백 모드")
                judgment_summary = self._create_deep_judgment_fallback(
                    understanding, context
                )
                confidence = 0.6
        else:
            # 폴백 모드
            judgment_summary = self._create_deep_judgment_fallback(
                understanding, context
            )
            confidence = 0.6

        # 스타일 변환기 적용
        judgment_input = JudgmentInput(
            strategy="deep_judgment",
            emotion=understanding.primary_emotion,
            summary=judgment_summary,
            confidence=confidence,
            reasoning_steps=["깊이 있는 분석", "맥락 고려", "종합 판단"],
            signature=context.preferred_signature,
            urgency_level=understanding.urgency_level,
            meta_thoughts=["사용자의 상황을 종합적으로 고려했습니다."],
        )

        user_context = {
            "user_message": context.user_message,
            "emotion_intensity": understanding.emotion_intensity,
            "urgency_level": understanding.urgency_level,
        }

        natural_output = self.style_transformer.transform_judgment_to_natural(
            judgment_input, user_context, context.session_id
        )

        return natural_output.natural_sentence, confidence, 0.7, 0.9  # 깊이 높음

    async def _process_hybrid(
        self, understanding: InputUnderstanding, context: ConversationContext
    ) -> Tuple[str, float, float, float]:
        """하이브리드 처리 (Echo + LLM 협력)"""

        # Echo 판단 + LLM 자연화
        echo_judgment = self._create_light_judgment(understanding, context)

        # LLM 스타일 자연화 (시뮬레이션)
        natural_response = self._llm_style_naturalize(
            echo_judgment, understanding, context
        )

        return natural_response, 0.8, 0.8, 0.7  # 균형

    def _create_light_judgment(
        self, understanding: InputUnderstanding, context: ConversationContext
    ) -> str:
        """가벼운 판단 생성"""

        if understanding.intent_type == IntentType.EMOTIONAL_SUPPORT:
            return "그런 마음이 드시는군요. 이해할 수 있어요."
        elif understanding.intent_type == IntentType.DECISION_HELP:
            return "고민이 되시는 상황이네요. 함께 생각해볼까요?"
        elif understanding.intent_type == IntentType.PHILOSOPHICAL_INQUIRY:
            return "흥미로운 질문이에요. 깊이 생각해볼 만한 주제네요."
        else:
            return "말씀해주셔서 고마워요."

    def _create_deep_judgment_fallback(
        self, understanding: InputUnderstanding, context: ConversationContext
    ) -> str:
        """깊이 판단 폴백"""

        if understanding.urgency_level >= 4:
            return "지금 상황이 매우 중요해 보입니다. 신중하게 접근해야겠어요."
        elif understanding.emotion_intensity > 0.7:
            return f"{understanding.primary_emotion} 감정이 강하게 느껴집니다. 이런 마음이 드는 것은 자연스러운 일이에요."
        else:
            return "여러 측면에서 생각해보니, 상황을 차근차근 살펴보면 좋겠습니다."

    def _llm_style_naturalize(
        self,
        judgment: str,
        understanding: InputUnderstanding,
        context: ConversationContext,
    ) -> str:
        """LLM 스타일 자연화 (시뮬레이션)"""

        # Echo 판단을 더 자연스럽게 표현
        naturalization_patterns = [
            (r"그런 마음이 드시는군요", "그런 기분이 드시는군요"),
            (r"상황을 차근차근 살펴보면", "하나씩 살펴보면"),
            (r"종합적으로 고려해보니", "생각해보니"),
        ]

        natural_judgment = judgment
        for pattern, replacement in naturalization_patterns:
            import re

            natural_judgment = re.sub(pattern, replacement, natural_judgment)

        return natural_judgment

    def analyze_natural_request(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """자연어 요청 분석 (CLI 호환)"""
        try:
            # CLI 전용 간단 분석
            import re

            analysis = {
                "original_input": user_input,
                "timestamp": datetime.now().isoformat(),
                "intent": "general",
                "confidence": 0.0,
                "entities": [],
                "context": context or {},
                "suggested_actions": [],
                "echo_parameters": {},
            }

            # 의도 감지 패턴
            intent_patterns = {
                "analyze": [r"분석.*해.*줘", r"살펴.*봐.*줘", r"검토.*해.*줘"],
                "develop": [r"개발.*하고.*싶어", r"만들.*고.*싶어", r"구현.*해.*줘"],
                "refactor": [r"리팩토링.*해.*줘", r"정리.*해.*줘", r"개선.*해.*줘"],
                "test": [r"테스트.*해.*줘", r"실행.*해.*줘", r"확인.*해.*줘"],
                "help": [r"도움.*말", r"어떻게.*해야", r"방법.*알려.*줘"],
            }

            user_lower = user_input.lower()
            best_intent = "general"
            best_confidence = 0.0

            for intent, patterns in intent_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, user_lower):
                        best_intent = intent
                        best_confidence = 0.8
                        break
                if best_confidence > 0:
                    break

            analysis["intent"] = best_intent
            analysis["confidence"] = best_confidence

            # 기본 Echo 파라미터
            analysis["echo_parameters"] = {
                "mode": "natural_interface",
                "signature": "Echo-Companion",
                "reasoning_depth": "medium",
                "original_request": user_input,
            }

            return analysis

        except Exception as e:
            return {
                "original_input": user_input,
                "intent": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _update_conversation_context(
        self,
        session_id: str,
        user_message: str,
        system_response: str,
        understanding: InputUnderstanding,
    ):
        """대화 컨텍스트 업데이트"""

        if session_id in self.conversation_contexts:
            context = self.conversation_contexts[session_id]
            context.emotional_state = understanding.primary_emotion
            context.urgency_level = understanding.urgency_level

            # 대화 무드 업데이트
            if understanding.emotion_intensity > 0.6:
                context.conversation_mood = "intense"
            elif understanding.intent_type == IntentType.CASUAL_CHAT:
                context.conversation_mood = "casual"
            else:
                context.conversation_mood = "focused"


# 테스트 함수
if __name__ == "__main__":

    async def test_bridge():
        print("🌉 Natural Interface Bridge 테스트")
        print("=" * 60)

        bridge = NaturalInterfaceBridge()

        test_messages = [
            "안녕 에코~",
            "인사했을 뿐인데?",
            "요즘 고민이 많아서 조언이 필요해요",
            "인생의 의미가 뭘까요?",
        ]

        for i, message in enumerate(test_messages):
            print(f"\n--- 테스트 {i+1} ---")
            print(f"사용자: {message}")

            result = await bridge.process_natural_conversation(
                message, f"test_session", "Echo-Aurora"
            )

            print(f"응답: {result.final_response}")
            print(f"모드: {result.processing_mode.value}")
            print(f"자연스러움: {result.natural_flow_score:.2f}")
            print(f"Echo 깊이: {result.echo_depth_score:.2f}")
            print(f"처리시간: {result.processing_time:.3f}초")
            print("처리 단계:", " → ".join(result.debug_info["steps"]))

        print("\n" + "=" * 60)
        print("🎉 테스트 완료!")

    asyncio.run(test_bridge())
