#!/usr/bin/env python3
"""
🎭 Echo Style Transformer
Echo 판단 결과를 자연스러운 문장으로 변환하는 핵심 모듈

핵심 기능:
1. Echo 판단 결과 → 자연스러운 문장 변환
2. 사용자 리듬에 맞는 말투 적용
3. LLM 협력하되 Echo 스타일 유지
4. 메타로그 기반 대화 흐름 참조
"""

import json
import random
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class SpeechRhythm(Enum):
    """발화 리듬 타입"""

    CASUAL = "casual"  # 캐주얼한 말투
    FORMAL = "formal"  # 격식있는 말투
    URGENT = "urgent"  # 급한 말투
    GENTLE = "gentle"  # 부드러운 말투
    PLAYFUL = "playful"  # 장난스러운 말투
    SERIOUS = "serious"  # 진지한 말투


class ConversationTone(Enum):
    """대화 톤"""

    FRIENDLY = "friendly"  # 친근한
    SUPPORTIVE = "supportive"  # 지지적인
    ANALYTICAL = "analytical"  # 분석적인
    EMPATHETIC = "empathetic"  # 공감적인
    ENCOURAGING = "encouraging"  # 격려하는
    CALM = "calm"  # 차분한


@dataclass
class JudgmentInput:
    """Echo 판단 결과 (입력)"""

    strategy: str
    emotion: str
    summary: str
    confidence: float
    reasoning_steps: List[str]
    signature: str
    urgency_level: int
    meta_thoughts: List[str]


@dataclass
class NaturalOutput:
    """자연어 변환 결과 (출력)"""

    natural_sentence: str
    applied_rhythm: SpeechRhythm
    conversation_tone: ConversationTone
    signature_touch: str
    flow_continuity: float


class EchoStyleTransformer:
    """Echo 스타일 변환기"""

    def __init__(self):
        self.rhythm_patterns = self._load_rhythm_patterns()
        self.tone_adjusters = self._load_tone_adjusters()
        self.signature_voices = self._load_signature_voices()
        self.conversation_memory = {}  # 세션별 대화 기억

    def transform_judgment_to_natural(
        self,
        judgment: JudgmentInput,
        user_context: Dict[str, Any] = None,
        session_id: str = None,
    ) -> NaturalOutput:
        """Echo 판단 결과를 자연스러운 문장으로 변환"""

        user_context = user_context or {}

        # 1. 사용자 리듬 감지
        user_rhythm = self._detect_user_rhythm(user_context, session_id)

        # 2. 적절한 대화 톤 결정
        conversation_tone = self._determine_conversation_tone(
            judgment.emotion, judgment.urgency_level, user_rhythm
        )

        # 3. 기본 문장 생성
        base_sentence = self._generate_base_sentence(judgment, conversation_tone)

        # 4. 리듬 적용
        rhythmic_sentence = self._apply_rhythm(
            base_sentence, user_rhythm, judgment.signature
        )

        # 5. 시그니처 터치 추가
        signature_touch = self._add_signature_touch(
            rhythmic_sentence, judgment.signature, conversation_tone
        )

        # 6. 흐름 연속성 확인
        flow_sentence, continuity = self._ensure_flow_continuity(
            signature_touch, user_context, session_id
        )

        # 7. 대화 기억 업데이트
        self._update_conversation_memory(session_id, flow_sentence, user_rhythm)

        return NaturalOutput(
            natural_sentence=flow_sentence,
            applied_rhythm=user_rhythm,
            conversation_tone=conversation_tone,
            signature_touch=signature_touch,
            flow_continuity=continuity,
        )

    def _detect_user_rhythm(
        self, user_context: Dict[str, Any], session_id: str
    ) -> SpeechRhythm:
        """사용자 리듬 감지"""

        user_message = user_context.get("user_message", "")
        emotion_intensity = user_context.get("emotion_intensity", 0.5)
        urgency = user_context.get("urgency_level", 1)

        # 이전 대화에서 리듬 패턴 참조
        if session_id and session_id in self.conversation_memory:
            prev_rhythm = self.conversation_memory[session_id].get("user_rhythm")
            if prev_rhythm:
                # 이전 리듬과의 연속성 고려
                rhythm_consistency = 0.7  # 70% 확률로 이전 리듬 유지
                if random.random() < rhythm_consistency:
                    return prev_rhythm

        # 메시지 특성 기반 리듬 감지
        message_lower = user_message.lower()

        # 긴급한 리듬
        if urgency >= 4 or any(
            urgent_word in message_lower
            for urgent_word in ["급해", "빨리", "지금", "당장", "!!"]
        ):
            return SpeechRhythm.URGENT

        # 장난스러운 리듬
        if any(
            playful in message_lower for playful in ["ㅋㅋ", "ㅎㅎ", "~", "에코~", "야"]
        ):
            return SpeechRhythm.PLAYFUL

        # 진지한 리듬
        if emotion_intensity > 0.7 or any(
            serious in message_lower for serious in ["심각", "고민", "걱정", "문제"]
        ):
            return SpeechRhythm.SERIOUS

        # 격식있는 리듬
        if "습니다" in user_message or "됩니다" in user_message:
            return SpeechRhythm.FORMAL

        # 부드러운 리듬
        if emotion_intensity < 0.3 or any(
            gentle in message_lower for gentle in ["조용히", "천천히", "괜찮아"]
        ):
            return SpeechRhythm.GENTLE

        # 기본은 캐주얼
        return SpeechRhythm.CASUAL

    def _determine_conversation_tone(
        self, emotion: str, urgency: int, rhythm: SpeechRhythm
    ) -> ConversationTone:
        """대화 톤 결정"""

        # 긴급 상황
        if urgency >= 4:
            return ConversationTone.SUPPORTIVE

        # 감정 기반 톤
        emotion_tone_map = {
            "sadness": ConversationTone.EMPATHETIC,
            "anxiety": ConversationTone.SUPPORTIVE,
            "anger": ConversationTone.CALM,
            "joy": ConversationTone.FRIENDLY,
            "curiosity": ConversationTone.ENCOURAGING,
            "confusion": ConversationTone.ANALYTICAL,
        }

        if emotion in emotion_tone_map:
            return emotion_tone_map[emotion]

        # 리듬 기반 톤
        if rhythm == SpeechRhythm.PLAYFUL:
            return ConversationTone.FRIENDLY
        elif rhythm == SpeechRhythm.SERIOUS:
            return ConversationTone.ANALYTICAL
        elif rhythm == SpeechRhythm.GENTLE:
            return ConversationTone.EMPATHETIC

        return ConversationTone.FRIENDLY

    def _generate_base_sentence(
        self, judgment: JudgmentInput, tone: ConversationTone
    ) -> str:
        """기본 문장 생성"""

        # 판단 내용을 자연스럽게 표현
        summary = judgment.summary

        # 톤에 따른 문장 시작 조정
        tone_starters = {
            ConversationTone.FRIENDLY: ["", "그렇군요! ", "아, "],
            ConversationTone.SUPPORTIVE: ["", "마음이 이해돼요. ", ""],
            ConversationTone.ANALYTICAL: ["생각해보니 ", "분석해보면 ", ""],
            ConversationTone.EMPATHETIC: ["", "그런 마음이시군요. ", ""],
            ConversationTone.ENCOURAGING: ["", "좋은 생각이에요! ", ""],
            ConversationTone.CALM: ["", "차분히 보면 ", ""],
        }

        starter = random.choice(tone_starters.get(tone, [""]))

        # 과도한 분석 표현 제거
        clean_summary = self._clean_judgment_summary(summary)

        return f"{starter}{clean_summary}"

    def _clean_judgment_summary(self, summary: str) -> str:
        """판단 요약을 자연스럽게 정리"""

        # 과도한 분석 표현 제거
        cleanup_patterns = [
            (r"여러 요소를 고려했을 때\s*", ""),
            (r"상황을 분석해보니\s*", ""),
            (r"논리적으로 생각해보면\s*", ""),
            (r"종합적으로 판단하면\s*", ""),
            (r"\.라고\s+(생각|판단)해\.", "."),
            (r"라고\s+\w+는\s+생각해\.", "."),
        ]

        cleaned = summary
        for pattern, replacement in cleanup_patterns:
            cleaned = re.sub(pattern, replacement, cleaned)

        # 중복 구두점 정리
        cleaned = re.sub(r"[.]{2,}", ".", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned

    def _apply_rhythm(self, sentence: str, rhythm: SpeechRhythm, signature: str) -> str:
        """리듬 적용"""

        rhythm_adjustments = {
            SpeechRhythm.CASUAL: self._apply_casual_rhythm,
            SpeechRhythm.FORMAL: self._apply_formal_rhythm,
            SpeechRhythm.URGENT: self._apply_urgent_rhythm,
            SpeechRhythm.GENTLE: self._apply_gentle_rhythm,
            SpeechRhythm.PLAYFUL: self._apply_playful_rhythm,
            SpeechRhythm.SERIOUS: self._apply_serious_rhythm,
        }

        adjuster = rhythm_adjustments.get(rhythm, self._apply_casual_rhythm)
        return adjuster(sentence, signature)

    def _apply_casual_rhythm(self, sentence: str, signature: str) -> str:
        """캐주얼 리듬 적용"""
        # 편한 말투로 변경
        sentence = sentence.replace("습니다", "어요").replace("됩니다", "돼요")
        sentence = sentence.replace("이에요", "이야").replace("예요", "야")
        return sentence

    def _apply_formal_rhythm(self, sentence: str, signature: str) -> str:
        """격식 리듬 적용"""
        # 격식있는 말투로 변경
        sentence = sentence.replace("어요", "습니다").replace("이야", "입니다")
        sentence = sentence.replace("돼요", "됩니다")
        return sentence

    def _apply_urgent_rhythm(self, sentence: str, signature: str) -> str:
        """긴급 리듬 적용"""
        # 간결하고 명확하게
        sentence = re.sub(r"[.]{3,}", ".", sentence)
        if not sentence.endswith(("!", "?")):
            sentence = sentence.rstrip(".") + "!"
        return sentence

    def _apply_gentle_rhythm(self, sentence: str, signature: str) -> str:
        """부드러운 리듬 적용"""
        # 부드럽게 표현
        gentle_endings = ["요", "어요", "네요", "겠어요"]
        for ending in gentle_endings:
            if sentence.endswith("."):
                sentence = sentence[:-1] + ending + "."
                break
        return sentence

    def _apply_playful_rhythm(self, sentence: str, signature: str) -> str:
        """장난스러운 리듬 적용"""
        # 친근하고 활기찬 톤
        if signature == "Echo-Aurora":
            return f"{sentence} ✨"
        elif signature == "Echo-Phoenix":
            return f"{sentence} 🔥"
        elif signature == "Echo-Companion":
            return f"{sentence} 😊"
        return sentence

    def _apply_serious_rhythm(self, sentence: str, signature: str) -> str:
        """진지한 리듬 적용"""
        # 차분하고 진중하게
        sentence = sentence.replace("!", ".")
        return sentence

    def _add_signature_touch(
        self, sentence: str, signature: str, tone: ConversationTone
    ) -> str:
        """시그니처 터치 추가 (최소한)"""

        # 간단한 경우는 터치 최소화
        if len(sentence.strip()) < 15:
            return sentence

        # 시그니처별 미묘한 터치
        touches = {
            "Echo-Aurora": {
                ConversationTone.FRIENDLY: ["", " 마음이 따뜻해져요."],
                ConversationTone.EMPATHETIC: ["", " 함께 느껴져요."],
                "default": [""],
            },
            "Echo-Phoenix": {
                ConversationTone.ENCOURAGING: ["", " 새로운 시작이에요!"],
                ConversationTone.ANALYTICAL: ["", " 변화가 필요할지도."],
                "default": [""],
            },
            "Echo-Sage": {
                ConversationTone.ANALYTICAL: ["", " 시간을 두고 보면 좋겠어요."],
                ConversationTone.CALM: ["", " 지혜롭게 접근해보세요."],
                "default": [""],
            },
            "Echo-Companion": {
                ConversationTone.SUPPORTIVE: ["", " 함께 할게요."],
                ConversationTone.FRIENDLY: ["", " 언제든 도와줄게요."],
                "default": [""],
            },
        }

        signature_touches = touches.get(signature, {"default": [""]})
        touch_options = signature_touches.get(tone.value, signature_touches["default"])

        # 30% 확률로만 터치 추가
        if random.random() < 0.3:
            touch = random.choice(touch_options)
            return f"{sentence}{touch}"

        return sentence

    def _ensure_flow_continuity(
        self, sentence: str, user_context: Dict[str, Any], session_id: str
    ) -> Tuple[str, float]:
        """흐름 연속성 확인"""

        # 이전 대화와의 연결성 확인
        continuity_score = 0.8  # 기본 연속성

        if session_id and session_id in self.conversation_memory:
            prev_conversation = self.conversation_memory[session_id]
            prev_tone = prev_conversation.get("tone")
            current_tone = user_context.get("current_tone")

            # 급격한 톤 변화 감지
            if prev_tone and current_tone and prev_tone != current_tone:
                # 톤 변화에 따른 자연스러운 전환 문구 추가
                transition_phrases = {
                    "serious_to_casual": "그런데 말이야, ",
                    "casual_to_serious": "진지하게 말하면, ",
                    "sad_to_happy": "다행히 ",
                    "happy_to_sad": "하지만 ",
                }
                # 실제로는 더 세밀한 전환 로직 필요
                continuity_score = 0.6

        return sentence, continuity_score

    def _update_conversation_memory(
        self, session_id: str, sentence: str, rhythm: SpeechRhythm
    ):
        """대화 기억 업데이트"""
        if not session_id:
            return

        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = {}

        self.conversation_memory[session_id].update(
            {
                "last_response": sentence,
                "user_rhythm": rhythm,
                "timestamp": datetime.now().isoformat(),
                "response_count": self.conversation_memory[session_id].get(
                    "response_count", 0
                )
                + 1,
            }
        )

        # 메모리 제한 (최근 10개 대화만 유지)
        if len(self.conversation_memory) > 10:
            oldest_session = min(
                self.conversation_memory.keys(),
                key=lambda x: self.conversation_memory[x].get("timestamp", ""),
            )
            del self.conversation_memory[oldest_session]

    def _load_rhythm_patterns(self) -> Dict[str, Any]:
        """리듬 패턴 로드"""
        return {
            "casual_markers": ["그냥", "뭔가", "좀", "약간"],
            "formal_markers": ["습니다", "됩니다", "입니다"],
            "urgent_markers": ["빨리", "급해", "지금", "당장"],
            "gentle_markers": ["천천히", "괜찮아", "괜찮다"],
            "playful_markers": ["ㅋㅋ", "ㅎㅎ", "~", "야"],
            "serious_markers": ["심각", "중요", "문제", "고민"],
        }

    def _load_tone_adjusters(self) -> Dict[str, Any]:
        """톤 조정기 로드"""
        return {
            "friendly": {"warmth": 0.8, "casualness": 0.7},
            "supportive": {"warmth": 0.9, "firmness": 0.6},
            "analytical": {"clarity": 0.9, "objectivity": 0.8},
            "empathetic": {"warmth": 1.0, "gentleness": 0.9},
            "encouraging": {"positivity": 0.9, "energy": 0.8},
            "calm": {"steadiness": 0.9, "gentleness": 0.7},
        }

    def _load_signature_voices(self) -> Dict[str, Any]:
        """시그니처 목소리 로드"""
        return {
            "Echo-Aurora": {"creativity": 0.9, "warmth": 0.8, "intuition": 0.9},
            "Echo-Phoenix": {"dynamism": 0.9, "passion": 0.8, "change": 0.9},
            "Echo-Sage": {"wisdom": 0.9, "patience": 0.8, "depth": 0.9},
            "Echo-Companion": {"support": 0.9, "reliability": 0.9, "warmth": 0.8},
        }


# 테스트 함수
if __name__ == "__main__":
    transformer = EchoStyleTransformer()

    # 테스트 판단 결과
    test_judgment = JudgmentInput(
        strategy="empathetic_support",
        emotion="joy",
        summary="말씀해주신 상황을 이해했습니다. 함께 생각해보면 좋겠어요.",
        confidence=0.8,
        reasoning_steps=["사용자 의도 파악", "감정 분석"],
        signature="Echo-Aurora",
        urgency_level=1,
        meta_thoughts=[],
    )

    # 테스트 사용자 컨텍스트들
    test_contexts = [
        {"user_message": "안녕 에코~", "emotion_intensity": 0.3, "urgency_level": 1},
        {
            "user_message": "인사했을 뿐인데?",
            "emotion_intensity": 0.4,
            "urgency_level": 1,
        },
    ]

    print("🎭 Echo Style Transformer 테스트:")
    print("=" * 50)

    for i, context in enumerate(test_contexts):
        print(f"\n--- 테스트 {i+1} ---")
        print(f"사용자 입력: {context['user_message']}")
        print(f"원본 판단: {test_judgment.summary}")

        result = transformer.transform_judgment_to_natural(
            test_judgment, context, f"test_session_{i}"
        )

        print(f"변환 결과: {result.natural_sentence}")
        print(f"적용된 리듬: {result.applied_rhythm.value}")
        print(f"대화 톤: {result.conversation_tone.value}")
        print(f"흐름 연속성: {result.flow_continuity:.2f}")
        print("-" * 30)

    print("\n🎉 테스트 완료!")
