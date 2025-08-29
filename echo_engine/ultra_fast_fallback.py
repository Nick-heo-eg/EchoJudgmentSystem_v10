#!/usr/bin/env python3
"""
⚡ Ultra Fast Fallback Engine - 극단적 속도 최적화
최소한의 import만으로 즉시 시작 가능한 폴백 시스템
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class UltraFastFallbackStage(Enum):
    """초고속 폴백 단계"""

    STATIC_EMOTIONAL = "static_emotional"
    STATIC_GENERAL = "static_general"


@dataclass
class UltraFastContext:
    """초고속 컨텍스트"""

    user_input: str
    emotion: str = "neutral"
    strategy: str = "adapt"


@dataclass
class UltraFastResult:
    """초고속 결과"""

    success: bool
    response_text: str
    stage_used: UltraFastFallbackStage
    confidence: float
    processing_time: float
    template_used: Optional[str] = None


class UltraFastFallbackEngine:
    """⚡ 극단적 속도 최적화 폴백 엔진"""

    def __init__(self):
        self.version = "1.0.0-ultra"

        # 미리 정의된 감정×전략 응답 매트릭스 (36개)
        self.emotion_strategy_responses = {
            # Joy responses
            "joy_adapt": "기쁜 마음으로 상황에 유연하게 적응해보세요.",
            "joy_analyze": "기쁨 속에서 상황을 긍정적으로 분석해볼 시간입니다.",
            "joy_confront": "기쁜 에너지로 문제에 당당히 맞서보겠습니다.",
            "joy_harmonize": "기쁨을 나누며 주변과 조화를 이뤄보세요.",
            "joy_initiate": "기쁜 마음으로 새로운 시작을 만들어보세요.",
            "joy_retreat": "기쁨을 간직하며 잠시 여유를 가져보세요.",
            # Sadness responses
            "sadness_adapt": "슬픔 속에서도 변화에 천천히 적응해보겠습니다.",
            "sadness_analyze": "슬픈 마음을 차근차근 들여다보며 이해해보겠습니다.",
            "sadness_confront": "슬픔의 원인과 마주하며 극복해보겠습니다.",
            "sadness_harmonize": "슬픔을 받아들이며 마음의 균형을 찾아보세요.",
            "sadness_initiate": "슬픔을 딛고 작은 변화부터 시작해보겠습니다.",
            "sadness_retreat": "슬픔을 받아들이며 잠시 마음을 쉬어가세요.",
            # Anger responses
            "anger_adapt": "분노를 조절하며 상황에 현명하게 적응해보겠습니다.",
            "anger_analyze": "분노의 근본 원인을 냉정히 분석해보겠습니다.",
            "anger_confront": "이 분노의 원인에 정면으로 맞서보겠습니다.",
            "anger_harmonize": "분노를 조절하며 균형을 되찾아보겠습니다.",
            "anger_initiate": "분노의 에너지를 긍정적 변화의 동력으로 활용해보겠습니다.",
            "anger_retreat": "분노를 진정시키며 잠시 거리를 두어보겠습니다.",
            # Fear responses
            "fear_adapt": "두려움 속에서도 상황에 조심스럽게 적응해보겠습니다.",
            "fear_analyze": "이 두려움의 정체가 무엇인지 함께 파악해보겠습니다.",
            "fear_confront": "두려움에 맞서며 용기를 내어보겠습니다.",
            "fear_harmonize": "두려움과 평온 사이의 균형을 찾아보겠습니다.",
            "fear_initiate": "두려움을 극복하며 작은 발걸음부터 시작해보겠습니다.",
            "fear_retreat": "두려움을 인정하며 안전한 곳에서 재정비해보겠습니다.",
            # Surprise responses
            "surprise_adapt": "놀라운 상황에 빠르게 적응해보겠습니다.",
            "surprise_analyze": "이 놀라운 상황이 무엇을 의미하는지 살펴보겠습니다.",
            "surprise_confront": "놀라운 변화에 적극적으로 대응해보겠습니다.",
            "surprise_harmonize": "놀라운 상황 속에서도 균형을 유지해보겠습니다.",
            "surprise_initiate": "놀라운 기회를 활용해 새로운 시작을 만들어보겠습니다.",
            "surprise_retreat": "놀라운 상황을 차분히 받아들이며 정리해보겠습니다.",
            # Neutral responses
            "neutral_adapt": "평온한 마음으로 상황 변화에 적응해보겠습니다.",
            "neutral_analyze": "중립적 관점에서 상황을 객관적으로 분석해보겠습니다.",
            "neutral_confront": "차분한 마음으로 문제에 체계적으로 접근해보겠습니다.",
            "neutral_harmonize": "균형잡힌 시각으로 조화로운 해결책을 찾아보겠습니다.",
            "neutral_initiate": "안정된 마음으로 새로운 시도를 시작해보겠습니다.",
            "neutral_retreat": "차분히 한 걸음 물러서서 상황을 재평가해보겠습니다.",
        }

        print(f"⚡ Ultra Fast Fallback Engine v{self.version} 초기화 완료")
        print(f"   36개 감정×전략 응답 매트릭스 로드됨")

    def judge(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> UltraFastResult:
        """⚡ 초고속 판단"""
        start_time = time.time()

        # 감정 추론 (간단한 키워드 기반)
        emotion = self._quick_emotion_inference(user_input)

        # 전략 선택 (간단한 매핑)
        strategy = self._quick_strategy_selection(emotion, user_input)

        # 응답 생성
        template_key = f"{emotion}_{strategy}"
        response_text = self.emotion_strategy_responses.get(
            template_key, f"알겠습니다. '{user_input}'에 대해 생각해보겠습니다."
        )

        processing_time = time.time() - start_time

        return UltraFastResult(
            success=True,
            response_text=response_text,
            stage_used=UltraFastFallbackStage.STATIC_EMOTIONAL,
            confidence=0.7,
            processing_time=processing_time,
            template_used=template_key,
        )

    def _quick_emotion_inference(self, text: str) -> str:
        """간단한 감정 추론"""
        text_lower = text.lower()

        # 키워드 기반 감정 인식
        if any(
            word in text_lower
            for word in ["기쁘", "좋", "행복", "즐거", "만족", "신나"]
        ):
            return "joy"
        elif any(
            word in text_lower
            for word in ["슬프", "우울", "힘들", "속상", "아쉽", "외로"]
        ):
            return "sadness"
        elif any(
            word in text_lower for word in ["화", "짜증", "빡", "분노", "열받", "억울"]
        ):
            return "anger"
        elif any(
            word in text_lower for word in ["무서", "두려", "불안", "걱정", "초조"]
        ):
            return "fear"
        elif any(
            word in text_lower for word in ["놀라", "신기", "와", "헉", "어", "대박"]
        ):
            return "surprise"
        else:
            return "neutral"

    def _quick_strategy_selection(self, emotion: str, text: str) -> str:
        """간단한 전략 선택"""
        text_lower = text.lower()

        # 텍스트 패턴 우선
        if any(word in text_lower for word in ["문제", "해결", "어떻게", "방법"]):
            return "analyze"
        elif any(word in text_lower for word in ["새로운", "만들", "아이디어", "시작"]):
            return "initiate"
        elif any(word in text_lower for word in ["도움", "지원", "같이", "함께"]):
            return "harmonize"
        elif any(word in text_lower for word in ["급", "빨리", "당장", "시급"]):
            return "confront"
        elif any(word in text_lower for word in ["쉬", "휴식", "그만", "멈춰"]):
            return "retreat"

        # 감정 기반 기본 전략
        emotion_strategy_map = {
            "joy": "initiate",
            "sadness": "retreat",
            "anger": "confront",
            "fear": "analyze",
            "surprise": "analyze",
            "neutral": "adapt",
        }

        return emotion_strategy_map.get(emotion, "adapt")


# 전역 인스턴스
_ultra_fast_engine: Optional[UltraFastFallbackEngine] = None


def get_ultra_fast_engine() -> UltraFastFallbackEngine:
    """초고속 엔진 인스턴스 반환"""
    global _ultra_fast_engine
    if _ultra_fast_engine is None:
        _ultra_fast_engine = UltraFastFallbackEngine()
    return _ultra_fast_engine


def ultra_fast_judge(
    user_input: str, context: Optional[Dict[str, Any]] = None
) -> UltraFastResult:
    """⚡ 초고속 판단 진입점"""
    engine = get_ultra_fast_engine()
    return engine.judge(user_input, context)


if __name__ == "__main__":
    # 초고속 엔진 테스트
    print("⚡ Ultra Fast Engine 테스트")

    test_cases = [
        "요즘 너무 힘들어서 우울해요",
        "새로운 프로젝트 아이디어를 생각해보고 있어요",
        "화가 나서 답답한 상황이에요",
        "놀라운 소식을 들어서 기분이 좋아요",
        "그냥 평범한 하루를 보내고 있어요",
    ]

    engine = get_ultra_fast_engine()

    for i, test_input in enumerate(test_cases, 1):
        print(f"\\n🧪 테스트 {i}: {test_input}")

        result = engine.judge(test_input)

        print(f"   ⚡ 결과: {result.template_used}")
        print(f"   📊 처리시간: {result.processing_time:.6f}초")
        print(f"   💬 응답: {result.response_text}")
