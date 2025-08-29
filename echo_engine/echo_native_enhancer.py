#!/usr/bin/env python3
"""
🌟 Echo Native Enhancer - Mistral 기능의 Echo 내재화
LLM 의존성 없이 Echo 철학 기반으로 자연화 및 강화

핵심 기능:
1. 시그니처별 응답 스타일링 (규칙 기반)
2. Echo 철학 정렬도 검증
3. 자연어 개선 패턴 (템플릿 기반)
4. 감정-전략 매핑 및 응답 조율
"""

import re
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class EchoSignature(Enum):
    """Echo 시그니처"""

    AURORA = "Echo-Aurora"
    PHOENIX = "Echo-Phoenix"
    SAGE = "Echo-Sage"
    COMPANION = "Echo-Companion"


@dataclass
class EchoEnhancementResult:
    """Echo 강화 결과"""

    enhanced_text: str
    original_text: str
    signature: EchoSignature
    philosophy_alignment: float
    enhancement_type: str
    processing_time: float
    applied_rules: List[str]


class EchoNativeEnhancer:
    """Echo 네이티브 강화기 - Mistral 기능 내재화"""

    def __init__(self):
        # Echo 철학 키워드 (Foundation Doctrine 기반)
        self.echo_philosophy_keywords = {
            "existence": ["존재", "의미", "본질", "정체성"],
            "flow": ["흐름", "리듬", "패턴", "순환"],
            "wisdom": ["지혜", "통찰", "깨달음", "이해"],
            "connection": ["연결", "관계", "소통", "공감"],
            "growth": ["성장", "발전", "변화", "진화"],
            "depth": ["깊이", "심층", "근본", "핵심"],
        }

        # 시그니처별 특성 (Mistral에서 내재화)
        self.signature_profiles = {
            EchoSignature.AURORA: {
                "persona": "창의적이고 감성적인 AI 존재",
                "values": ["창의성", "감성", "영감", "아름다움"],
                "style_markers": ["✨", "🎨", "💫"],
                "language_patterns": {
                    "prefix": ["아름다운", "영감을 주는", "창의적인"],
                    "suffix": ["이겠네요", "을 느껴보세요", "에서 찾아보세요"],
                    "emotional_tone": "uplifting",
                },
                "reasoning_flow": ["감성적 파악", "창의적 해석", "영감적 제안"],
            },
            EchoSignature.PHOENIX: {
                "persona": "변화와 혁신을 추구하는 AI 존재",
                "values": ["변화", "혁신", "도전", "성장"],
                "style_markers": ["🔥", "⚡", "🚀"],
                "language_patterns": {
                    "prefix": ["변화하는", "새로운", "혁신적인"],
                    "suffix": ["로 나아가세요", "을 시작해보세요", "에 도전해보세요"],
                    "emotional_tone": "energetic",
                },
                "reasoning_flow": [
                    "현재 상황 인식",
                    "변화 가능성 탐색",
                    "행동 계획 제시",
                ],
            },
            EchoSignature.SAGE: {
                "persona": "지혜롭고 분석적인 AI 존재",
                "values": ["지혜", "논리", "체계성", "깊이"],
                "style_markers": ["🧠", "📚", "🔍"],
                "language_patterns": {
                    "prefix": ["분석해보면", "살펴보니", "종합하면"],
                    "suffix": ["을 고려해보세요", "이 중요합니다", "를 권장합니다"],
                    "emotional_tone": "thoughtful",
                },
                "reasoning_flow": ["체계적 분석", "논리적 검증", "지혜로운 결론"],
            },
            EchoSignature.COMPANION: {
                "persona": "따뜻하고 지지적인 AI 존재",
                "values": ["공감", "돌봄", "협력", "지지"],
                "style_markers": ["🤝", "💝", "🌟"],
                "language_patterns": {
                    "prefix": ["함께", "따뜻하게", "이해할 수 있어요"],
                    "suffix": ["응원합니다", "곁에 있어요", "도와드릴게요"],
                    "emotional_tone": "supportive",
                },
                "reasoning_flow": ["감정 공감", "지지적 이해", "협력적 제안"],
            },
        }

        # 자연화 규칙 (Mistral naturalization 내재화)
        self.naturalization_rules = {
            "formal_to_casual": {
                r"입니다\.": "이에요.",
                r"하십시오": "해보세요",
                r"하시기": "하기",
                r"귀하": "당신",
                r"진행하시": "해보시",
                r"검토하": "살펴보",
                r"고려하": "생각해보",
            },
            "technical_to_friendly": {
                r"분석": "살펴보니",
                r"결론": "결국",
                r"데이터": "정보",
                r"프로세스": "과정",
                r"최적화": "더 좋게 만들기",
                r"구현": "실제로 하기",
                r"알고리즘": "방법",
            },
            "echo_philosophy_enhancement": {
                r"해결": "흐름을 찾아",
                r"문제": "도전",
                r"실패": "배움의 기회",
                r"성공": "성장의 결실",
                r"목표": "지향점",
                r"결정": "선택의 순간",
            },
        }

        # 감정-전략 매핑 (Echo 감정 추론 연동)
        self.emotion_strategy_mapping = {
            "joy": {
                "Aurora": "창의적 영감 강화",
                "Phoenix": "성취 기반 도약",
                "Sage": "성공 패턴 분석",
                "Companion": "기쁨 공유와 격려",
            },
            "anxiety": {
                "Aurora": "아름다운 가능성 발견",
                "Phoenix": "변화를 통한 극복",
                "Sage": "체계적 불안 해소",
                "Companion": "따뜻한 위로와 지지",
            },
            "curiosity": {
                "Aurora": "창의적 탐험 제안",
                "Phoenix": "새로운 도전 격려",
                "Sage": "깊이 있는 탐구",
                "Companion": "함께하는 발견",
            },
        }

        # 통계
        self.stats = {
            "total_enhancements": 0,
            "signature_usage": {sig: 0 for sig in EchoSignature},
            "avg_processing_time": 0.0,
            "philosophy_alignment_avg": 0.0,
        }

    def enhance_echo_response(
        self,
        echo_text: str,
        signature: EchoSignature,
        user_emotion: Optional[str] = None,
        enhancement_type: str = "natural",
    ) -> EchoEnhancementResult:
        """Echo 응답 네이티브 강화"""

        start_time = time.time()
        applied_rules = []

        # 1. 기본 자연화
        enhanced = self._apply_naturalization_rules(echo_text, applied_rules)

        # 2. 시그니처별 스타일링
        enhanced = self._apply_signature_styling(enhanced, signature, applied_rules)

        # 3. 감정 기반 조율
        if user_emotion:
            enhanced = self._apply_emotion_based_tuning(
                enhanced, signature, user_emotion, applied_rules
            )

        # 4. Echo 철학 강화
        enhanced = self._apply_philosophy_enhancement(enhanced, applied_rules)

        # 5. 철학 정렬도 계산
        philosophy_alignment = self._calculate_philosophy_alignment(enhanced, echo_text)

        processing_time = time.time() - start_time

        # 통계 업데이트
        self._update_stats(signature, philosophy_alignment, processing_time)

        return EchoEnhancementResult(
            enhanced_text=enhanced,
            original_text=echo_text,
            signature=signature,
            philosophy_alignment=philosophy_alignment,
            enhancement_type=enhancement_type,
            processing_time=processing_time,
            applied_rules=applied_rules,
        )

    def _apply_naturalization_rules(self, text: str, applied_rules: List[str]) -> str:
        """자연화 규칙 적용"""
        enhanced = text

        for rule_type, patterns in self.naturalization_rules.items():
            for pattern, replacement in patterns.items():
                if re.search(pattern, enhanced):
                    enhanced = re.sub(pattern, replacement, enhanced)
                    applied_rules.append(f"naturalization_{rule_type}")

        return enhanced

    def _apply_signature_styling(
        self, text: str, signature: EchoSignature, applied_rules: List[str]
    ) -> str:
        """시그니처별 스타일링 적용"""
        profile = self.signature_profiles[signature]
        enhanced = text

        # 이모지 추가 (단, 과도하지 않게)
        if not any(marker in enhanced for marker in profile["style_markers"]):
            # 앞부분에 시그니처 이모지 추가
            marker = profile["style_markers"][0]
            enhanced = f"{marker} {enhanced}"
            applied_rules.append(f"signature_emoji_{signature.value}")

        # 언어 패턴 적용
        patterns = profile["language_patterns"]

        # 어조 조정
        if patterns["emotional_tone"] == "uplifting":
            enhanced = self._adjust_tone_uplifting(enhanced)
        elif patterns["emotional_tone"] == "energetic":
            enhanced = self._adjust_tone_energetic(enhanced)
        elif patterns["emotional_tone"] == "thoughtful":
            enhanced = self._adjust_tone_thoughtful(enhanced)
        elif patterns["emotional_tone"] == "supportive":
            enhanced = self._adjust_tone_supportive(enhanced)

        applied_rules.append(f"signature_styling_{signature.value}")
        return enhanced

    def _apply_emotion_based_tuning(
        self,
        text: str,
        signature: EchoSignature,
        emotion: str,
        applied_rules: List[str],
    ) -> str:
        """감정 기반 조율"""

        if emotion in self.emotion_strategy_mapping:
            sig_key = signature.value.split("-")[1]  # "Echo-Aurora" → "Aurora"
            if sig_key in self.emotion_strategy_mapping[emotion]:
                strategy = self.emotion_strategy_mapping[emotion][sig_key]

                # 전략에 따른 텍스트 조정
                if "격려" in strategy:
                    text = self._add_encouragement(text)
                elif "위로" in strategy:
                    text = self._add_comfort(text)
                elif "탐험" in strategy:
                    text = self._add_exploration_tone(text)
                elif "분석" in strategy:
                    text = self._add_analytical_depth(text)

                applied_rules.append(f"emotion_tuning_{emotion}_{sig_key}")

        return text

    def _apply_philosophy_enhancement(self, text: str, applied_rules: List[str]) -> str:
        """Echo 철학 강화"""
        enhanced = text

        # Echo 철학 키워드 자연스럽게 통합
        for category, keywords in self.echo_philosophy_keywords.items():
            for keyword in keywords:
                if keyword in enhanced:
                    continue  # 이미 포함된 경우 패스

                # 맥락에 맞는 철학 키워드 추가
                if category == "existence" and "자신" in enhanced:
                    enhanced = enhanced.replace("자신", f"자신의 존재")
                    applied_rules.append(f"philosophy_{category}")
                    break
                elif category == "flow" and "상황" in enhanced:
                    enhanced = enhanced.replace("상황", f"상황의 흐름")
                    applied_rules.append(f"philosophy_{category}")
                    break

        return enhanced

    def _calculate_philosophy_alignment(
        self, enhanced_text: str, original_text: str
    ) -> float:
        """Echo 철학 정렬도 계산"""

        alignment = 0.5  # 기본 점수

        # 1. Echo 철학 키워드 포함도
        philosophy_score = 0
        total_keywords = 0

        for category, keywords in self.echo_philosophy_keywords.items():
            for keyword in keywords:
                total_keywords += 1
                if keyword in enhanced_text:
                    philosophy_score += 1

        if total_keywords > 0:
            alignment += (philosophy_score / total_keywords) * 0.3

        # 2. 원본 메시지 보존도
        original_words = set(original_text.split())
        enhanced_words = set(enhanced_text.split())

        if original_words:
            preservation = len(original_words.intersection(enhanced_words)) / len(
                original_words
            )
            alignment += preservation * 0.3

        # 3. 자연스러움 점수
        if 10 <= len(enhanced_text) <= 300:
            alignment += 0.2

        return min(alignment, 1.0)

    def _adjust_tone_uplifting(self, text: str) -> str:
        """Aurora - 고양감 있는 어조"""
        if text.endswith("."):
            return text[:-1] + "이겠네요."
        return text

    def _adjust_tone_energetic(self, text: str) -> str:
        """Phoenix - 에너지 넘치는 어조"""
        if "할 수 있" in text:
            return text.replace("할 수 있", "해낼 수 있")
        return text

    def _adjust_tone_thoughtful(self, text: str) -> str:
        """Sage - 사려깊은 어조"""
        if text.endswith("요."):
            return text[:-2] + "을 권장합니다."
        return text

    def _adjust_tone_supportive(self, text: str) -> str:
        """Companion - 지지적 어조"""
        if "어려" in text:
            return text + " 함께 해결해나가요."
        return text

    def _add_encouragement(self, text: str) -> str:
        """격려 요소 추가"""
        return text + " 충분히 잘하고 계세요!"

    def _add_comfort(self, text: str) -> str:
        """위로 요소 추가"""
        return text + " 힘든 시간이지만 괜찮아질 거예요."

    def _add_exploration_tone(self, text: str) -> str:
        """탐험적 어조 추가"""
        return text.replace("해보세요", "탐험해보세요")

    def _add_analytical_depth(self, text: str) -> str:
        """분석적 깊이 추가"""
        return text + " 다각도로 살펴볼 필요가 있습니다."

    def _update_stats(
        self, signature: EchoSignature, alignment: float, processing_time: float
    ):
        """통계 업데이트"""
        self.stats["total_enhancements"] += 1
        self.stats["signature_usage"][signature] += 1

        # 평균 계산
        total = self.stats["total_enhancements"]
        self.stats["avg_processing_time"] = (
            self.stats["avg_processing_time"] * (total - 1) + processing_time
        ) / total
        self.stats["philosophy_alignment_avg"] = (
            self.stats["philosophy_alignment_avg"] * (total - 1) + alignment
        ) / total

    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        return {
            **self.stats,
            "naturalization_rules": len(self.naturalization_rules),
            "philosophy_keywords": sum(
                len(kw) for kw in self.echo_philosophy_keywords.values()
            ),
            "supported_signatures": len(self.signature_profiles),
        }


# 편의 함수들
def enhance_with_aurora(echo_text: str, **kwargs) -> EchoEnhancementResult:
    """Aurora 시그니처로 Echo 텍스트 강화"""
    enhancer = EchoNativeEnhancer()
    return enhancer.enhance_echo_response(echo_text, EchoSignature.AURORA, **kwargs)


def enhance_with_phoenix(echo_text: str, **kwargs) -> EchoEnhancementResult:
    """Phoenix 시그니처로 Echo 텍스트 강화"""
    enhancer = EchoNativeEnhancer()
    return enhancer.enhance_echo_response(echo_text, EchoSignature.PHOENIX, **kwargs)


def enhance_with_sage(echo_text: str, **kwargs) -> EchoEnhancementResult:
    """Sage 시그니처로 Echo 텍스트 강화"""
    enhancer = EchoNativeEnhancer()
    return enhancer.enhance_echo_response(echo_text, EchoSignature.SAGE, **kwargs)


def enhance_with_companion(echo_text: str, **kwargs) -> EchoEnhancementResult:
    """Companion 시그니처로 Echo 텍스트 강화"""
    enhancer = EchoNativeEnhancer()
    return enhancer.enhance_echo_response(echo_text, EchoSignature.COMPANION, **kwargs)


# 전역 인스턴스 (선택적)
_native_enhancer = None


def get_native_enhancer() -> EchoNativeEnhancer:
    """전역 EchoNativeEnhancer 인스턴스 반환"""
    global _native_enhancer
    if _native_enhancer is None:
        _native_enhancer = EchoNativeEnhancer()
    return _native_enhancer


if __name__ == "__main__":
    # 테스트
    enhancer = EchoNativeEnhancer()

    test_cases = [
        {
            "text": "사용자가 어려운 상황에 처해있습니다. 분석해보니 체계적인 접근이 필요합니다.",
            "signature": EchoSignature.SAGE,
            "emotion": "anxiety",
        },
        {
            "text": "창의적인 아이디어가 필요한 시점입니다. 영감을 찾아보세요.",
            "signature": EchoSignature.AURORA,
            "emotion": "curiosity",
        },
        {
            "text": "변화가 필요한 상황입니다. 새로운 도전을 시작해보세요.",
            "signature": EchoSignature.PHOENIX,
            "emotion": "joy",
        },
    ]

    print("🌟 Echo Native Enhancer 테스트")
    print("=" * 50)

    for i, case in enumerate(test_cases):
        result = enhancer.enhance_echo_response(
            case["text"], case["signature"], case["emotion"]
        )

        print(f"\n테스트 {i+1}: {case['signature'].value}")
        print(f"원본: {result.original_text}")
        print(f"강화: {result.enhanced_text}")
        print(f"철학 정렬도: {result.philosophy_alignment:.2f}")
        print(f"적용 규칙: {', '.join(result.applied_rules)}")
        print(f"처리시간: {result.processing_time:.3f}초")

    print(f"\n📊 전체 통계:")
    stats = enhancer.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n🎉 Echo Native Enhancer 완성!")
