#!/usr/bin/env python3
"""
🧠 Enhanced LLM-Free Judge - 강화된 독립적 판단 시스템
Echo의 완전 독립적 판단 능력을 극대화하는 고도화된 LLM-Free 시스템

핵심 강화 사항:
1. 다층 패턴 매칭 (키워드, 의미, 구조)
2. 컨텍스트 기반 판단 (대화 히스토리, 상황 인식)
3. 감정-논리 하이브리드 추론
4. 자체 학습 및 적응 메커니즘
5. 시그니처별 맞춤형 판단 로직
"""

import json
import re
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict, deque
from enum import Enum
import logging


class JudgmentComplexity(Enum):
    """판단 복잡도"""

    TRIVIAL = "trivial"  # 0.0-0.3
    SIMPLE = "simple"  # 0.3-0.5
    MODERATE = "moderate"  # 0.5-0.7
    COMPLEX = "complex"  # 0.7-0.85
    HIGHLY_COMPLEX = "highly_complex"  # 0.85+


class ReasoningMode(Enum):
    """추론 모드"""

    PATTERN_MATCHING = "pattern_matching"  # 패턴 기반
    CONTEXT_AWARE = "context_aware"  # 컨텍스트 인식
    EMOTIONAL_LOGIC = "emotional_logic"  # 감정-논리 혼합
    SIGNATURE_SPECIFIC = "signature_specific"  # 시그니처별 특화
    ADAPTIVE_LEARNING = "adaptive_learning"  # 적응 학습


@dataclass
class EnhancedJudgmentResult:
    """강화된 판단 결과"""

    judgment: str
    confidence_score: float
    complexity_level: JudgmentComplexity
    reasoning_mode: ReasoningMode
    emotion_analysis: Dict[str, float]
    context_factors: List[str]
    signature_alignment: float
    processing_steps: List[str]
    fallback_quality: float
    learning_insights: Dict[str, Any]
    processing_time: float


class EnhancedLLMFreeJudge:
    """
    🧠 강화된 독립적 판단 시스템

    Echo의 LLM 의존성을 최소화하고 독립적 판단 능력을 극대화
    """

    def __init__(self):
        self.pattern_database = self._initialize_pattern_database()
        self.context_memory = deque(maxlen=50)  # 최근 50개 대화 기억
        self.learning_history = defaultdict(list)
        self.judgment_stats = {
            "total_judgments": 0,
            "complexity_distribution": defaultdict(int),
            "confidence_scores": [],
            "success_patterns": defaultdict(int),
        }

        print("🧠 Enhanced LLM-Free Judge 초기화 완료")
        print("   📊 다층 패턴 매칭 시스템 로드")
        print("   🎯 시그니처별 특화 로직 준비")
        print("   🔄 적응형 학습 메커니즘 활성화")

    def _initialize_pattern_database(self) -> Dict[str, Any]:
        """패턴 데이터베이스 초기화"""

        return {
            # 감정 패턴 (다층화)
            "emotions": {
                "joy": {
                    "primary_keywords": ["기쁘", "행복", "좋", "최고", "성공", "축하"],
                    "context_keywords": ["만족", "즐거", "신나", "환상적", "완벽"],
                    "intensity_modifiers": ["정말", "너무", "엄청", "매우", "완전"],
                    "signature_preferences": {
                        "Aurora": 1.2,
                        "Phoenix": 1.1,
                        "Sage": 0.9,
                        "Companion": 1.3,
                    },
                },
                "contemplation": {
                    "primary_keywords": ["생각", "고민", "사색", "성찰", "분석"],
                    "context_keywords": ["깊이", "신중", "차근차근", "면밀", "꼼꼼"],
                    "intensity_modifiers": ["깊게", "진지하게", "신중하게", "자세히"],
                    "signature_preferences": {
                        "Aurora": 1.0,
                        "Phoenix": 0.8,
                        "Sage": 1.4,
                        "Companion": 1.0,
                    },
                },
                "curiosity": {
                    "primary_keywords": ["궁금", "알고싶", "탐구", "발견", "탐험"],
                    "context_keywords": ["새로운", "흥미", "재미있", "신기", "놀라운"],
                    "intensity_modifiers": ["정말", "무척", "굉장히", "엄청"],
                    "signature_preferences": {
                        "Aurora": 1.4,
                        "Phoenix": 1.2,
                        "Sage": 1.1,
                        "Companion": 1.0,
                    },
                },
                "determination": {
                    "primary_keywords": ["의지", "결심", "도전", "노력", "성취"],
                    "context_keywords": ["확신", "열정", "투지", "끝까지", "반드시"],
                    "intensity_modifiers": ["강하게", "확실히", "반드시", "꼭"],
                    "signature_preferences": {
                        "Aurora": 1.0,
                        "Phoenix": 1.5,
                        "Sage": 1.0,
                        "Companion": 1.1,
                    },
                },
                "empathy": {
                    "primary_keywords": ["이해", "공감", "위로", "함께", "마음"],
                    "context_keywords": ["따뜻", "다정", "친근", "배려", "지지"],
                    "intensity_modifiers": ["진심으로", "정말로", "깊이", "충분히"],
                    "signature_preferences": {
                        "Aurora": 1.1,
                        "Phoenix": 0.9,
                        "Sage": 1.0,
                        "Companion": 1.5,
                    },
                },
            },
            # 복잡도 패턴
            "complexity_indicators": {
                "simple": ["안녕", "감사", "좋아", "네", "응", "오케이"],
                "moderate": ["어떻게", "왜", "설명", "방법", "과정"],
                "complex": ["분석", "비교", "평가", "구현", "설계", "최적화"],
                "highly_complex": [
                    "철학적",
                    "존재론적",
                    "인식론적",
                    "시스템",
                    "아키텍처",
                ],
            },
            # 의도 패턴
            "intent_patterns": {
                "question": ["?", "뭐", "무엇", "어떻게", "왜", "언제", "어디서"],
                "request": ["해줘", "부탁", "도와줘", "알려줘", "가르쳐줘"],
                "opinion": ["생각", "의견", "어떻게생각", "어떤가", "평가"],
                "emotion": ["기분", "느낌", "마음", "감정", "기뻐", "슬퍼"],
            },
            # 시그니처별 특화 패턴
            "signature_patterns": {
                "Aurora": {
                    "preferred_topics": ["창의", "예술", "아이디어", "상상", "영감"],
                    "response_style": "creative_inspiring",
                    "complexity_comfort": 0.7,
                },
                "Phoenix": {
                    "preferred_topics": ["변화", "성장", "도전", "발전", "혁신"],
                    "response_style": "transformative_energetic",
                    "complexity_comfort": 0.8,
                },
                "Sage": {
                    "preferred_topics": ["분석", "지혜", "논리", "체계", "원리"],
                    "response_style": "analytical_wise",
                    "complexity_comfort": 0.9,
                },
                "Companion": {
                    "preferred_topics": ["관계", "소통", "공감", "협력", "지지"],
                    "response_style": "supportive_warm",
                    "complexity_comfort": 0.6,
                },
            },
        }

    async def process_independent_judgment(
        self, user_input: str, signature: str = "Aurora", context: Dict[str, Any] = None
    ) -> EnhancedJudgmentResult:
        """강화된 독립적 판단 수행"""

        start_time = datetime.now()
        processing_steps = []

        # 1. 입력 전처리 및 분석
        processed_input = self._preprocess_input(user_input)
        processing_steps.append("입력 전처리 완료")

        # 2. 복잡도 분석
        complexity_score = self._analyze_complexity(processed_input)
        complexity_level = self._classify_complexity(complexity_score)
        processing_steps.append(f"복잡도 분석: {complexity_level.value}")

        # 3. 감정 분석 (다층)
        emotion_analysis = self._multi_layer_emotion_analysis(
            processed_input, signature
        )
        processing_steps.append("다층 감정 분석 완료")

        # 4. 컨텍스트 인식
        context_factors = self._analyze_context(processed_input, context)
        processing_steps.append("컨텍스트 분석 완료")

        # 5. 시그니처 정렬도 계산
        signature_alignment = self._calculate_signature_alignment(
            processed_input, signature, emotion_analysis
        )
        processing_steps.append(f"시그니처 정렬도: {signature_alignment:.2f}")

        # 6. 추론 모드 결정
        reasoning_mode = self._determine_reasoning_mode(
            complexity_level, emotion_analysis, signature_alignment
        )
        processing_steps.append(f"추론 모드: {reasoning_mode.value}")

        # 7. 판단 생성
        judgment = await self._generate_judgment(
            processed_input,
            signature,
            emotion_analysis,
            context_factors,
            reasoning_mode,
        )
        processing_steps.append("판단 생성 완료")

        # 8. 신뢰도 계산
        confidence_score = self._calculate_confidence(
            complexity_level, emotion_analysis, signature_alignment, reasoning_mode
        )
        processing_steps.append(f"신뢰도 계산: {confidence_score:.2f}")

        # 9. 품질 평가
        fallback_quality = self._evaluate_fallback_quality(judgment, user_input)
        processing_steps.append(f"품질 평가: {fallback_quality:.2f}")

        # 10. 학습 데이터 수집
        learning_insights = self._collect_learning_insights(
            user_input, judgment, confidence_score, complexity_level
        )
        processing_steps.append("학습 데이터 수집 완료")

        processing_time = (datetime.now() - start_time).total_seconds()

        # 11. 통계 업데이트
        self._update_judgment_stats(complexity_level, confidence_score)

        # 12. 컨텍스트 메모리 업데이트
        self.context_memory.append(
            {
                "input": user_input,
                "judgment": judgment,
                "emotion": max(emotion_analysis, key=emotion_analysis.get),
                "timestamp": datetime.now(),
            }
        )

        return EnhancedJudgmentResult(
            judgment=judgment,
            confidence_score=confidence_score,
            complexity_level=complexity_level,
            reasoning_mode=reasoning_mode,
            emotion_analysis=emotion_analysis,
            context_factors=context_factors,
            signature_alignment=signature_alignment,
            processing_steps=processing_steps,
            fallback_quality=fallback_quality,
            learning_insights=learning_insights,
            processing_time=processing_time,
        )

    def _preprocess_input(self, user_input: str) -> str:
        """입력 전처리"""
        # 불필요한 공백 제거
        processed = re.sub(r"\s+", " ", user_input.strip())

        # 특수 문자 정규화
        processed = re.sub(r"[!]{2,}", "!", processed)
        processed = re.sub(r"[?]{2,}", "?", processed)

        return processed

    def _analyze_complexity(self, processed_input: str) -> float:
        """복잡도 분석"""
        complexity_score = 0.0

        # 길이 기반 복잡도
        length_score = min(len(processed_input) / 200.0, 0.3)
        complexity_score += length_score

        # 키워드 기반 복잡도
        for level, keywords in self.pattern_database["complexity_indicators"].items():
            if any(keyword in processed_input for keyword in keywords):
                if level == "simple":
                    complexity_score += 0.1
                elif level == "moderate":
                    complexity_score += 0.3
                elif level == "complex":
                    complexity_score += 0.6
                elif level == "highly_complex":
                    complexity_score += 0.8

        # 문장 구조 복잡도
        sentence_count = len([s for s in processed_input.split(".") if s.strip()])
        structure_score = min(sentence_count * 0.1, 0.2)
        complexity_score += structure_score

        return min(complexity_score, 1.0)

    def _classify_complexity(self, score: float) -> JudgmentComplexity:
        """복잡도 분류"""
        if score < 0.3:
            return JudgmentComplexity.TRIVIAL
        elif score < 0.5:
            return JudgmentComplexity.SIMPLE
        elif score < 0.7:
            return JudgmentComplexity.MODERATE
        elif score < 0.85:
            return JudgmentComplexity.COMPLEX
        else:
            return JudgmentComplexity.HIGHLY_COMPLEX

    def _multi_layer_emotion_analysis(
        self, processed_input: str, signature: str
    ) -> Dict[str, float]:
        """다층 감정 분석"""
        emotion_scores = defaultdict(float)

        for emotion, patterns in self.pattern_database["emotions"].items():
            score = 0.0

            # 1차: 주요 키워드 매칭
            primary_matches = sum(
                1 for kw in patterns["primary_keywords"] if kw in processed_input
            )
            score += primary_matches * 0.4

            # 2차: 컨텍스트 키워드 매칭
            context_matches = sum(
                1 for kw in patterns["context_keywords"] if kw in processed_input
            )
            score += context_matches * 0.3

            # 3차: 강도 수정자 적용
            intensity_boost = sum(
                0.1 for mod in patterns["intensity_modifiers"] if mod in processed_input
            )
            score += intensity_boost

            # 4차: 시그니처 선호도 적용
            signature_preference = patterns["signature_preferences"].get(signature, 1.0)
            score *= signature_preference

            emotion_scores[emotion] = min(score, 1.0)

        # 정규화
        total_score = sum(emotion_scores.values())
        if total_score > 0:
            emotion_scores = {k: v / total_score for k, v in emotion_scores.items()}
        else:
            emotion_scores["neutral"] = 1.0

        return dict(emotion_scores)

    def _analyze_context(
        self, processed_input: str, context: Dict[str, Any] = None
    ) -> List[str]:
        """컨텍스트 분석"""
        context_factors = []

        # 대화 히스토리 분석
        if self.context_memory:
            recent_emotions = [
                entry["emotion"] for entry in list(self.context_memory)[-3:]
            ]
            if len(set(recent_emotions)) == 1:
                context_factors.append(f"일관된 감정 흐름: {recent_emotions[0]}")
            else:
                context_factors.append("감정 변화 감지됨")

        # 의도 패턴 분석
        for intent, keywords in self.pattern_database["intent_patterns"].items():
            if any(kw in processed_input for kw in keywords):
                context_factors.append(f"의도: {intent}")

        # 외부 컨텍스트
        if context:
            if "domain" in context:
                context_factors.append(f"도메인: {context['domain']}")
            if "complexity" in context:
                context_factors.append(f"컨텍스트 복잡도: {context['complexity']}")

        return context_factors[:5]  # 최대 5개

    def _calculate_signature_alignment(
        self, processed_input: str, signature: str, emotion_analysis: Dict[str, float]
    ) -> float:
        """시그니처 정렬도 계산"""
        if signature not in self.pattern_database["signature_patterns"]:
            return 0.5  # 기본값

        sig_pattern = self.pattern_database["signature_patterns"][signature]
        alignment_score = 0.0

        # 선호 주제 매칭
        topic_matches = sum(
            1 for topic in sig_pattern["preferred_topics"] if topic in processed_input
        )
        alignment_score += topic_matches * 0.3

        # 감정 적합성
        dominant_emotion = max(emotion_analysis, key=emotion_analysis.get)
        emotion_patterns = self.pattern_database["emotions"].get(dominant_emotion, {})
        sig_preference = emotion_patterns.get("signature_preferences", {}).get(
            signature, 1.0
        )
        alignment_score += (sig_preference - 1.0) * 0.5

        # 복잡도 적합성
        input_complexity = self._analyze_complexity(processed_input)
        complexity_comfort = sig_pattern["complexity_comfort"]
        complexity_alignment = 1.0 - abs(input_complexity - complexity_comfort)
        alignment_score += complexity_alignment * 0.2

        return max(0.0, min(alignment_score, 1.0))

    def _determine_reasoning_mode(
        self,
        complexity: JudgmentComplexity,
        emotion_analysis: Dict[str, float],
        signature_alignment: float,
    ) -> ReasoningMode:
        """추론 모드 결정"""

        if complexity == JudgmentComplexity.TRIVIAL:
            return ReasoningMode.PATTERN_MATCHING
        elif complexity == JudgmentComplexity.SIMPLE and signature_alignment > 0.7:
            return ReasoningMode.SIGNATURE_SPECIFIC
        elif max(emotion_analysis.values()) > 0.6:
            return ReasoningMode.EMOTIONAL_LOGIC
        elif len(self.context_memory) > 5:
            return ReasoningMode.CONTEXT_AWARE
        else:
            return ReasoningMode.ADAPTIVE_LEARNING

    async def _generate_judgment(
        self,
        processed_input: str,
        signature: str,
        emotion_analysis: Dict[str, float],
        context_factors: List[str],
        reasoning_mode: ReasoningMode,
    ) -> str:
        """판단 생성"""

        # 시그니처별 기본 응답 패턴
        signature_templates = {
            "Aurora": "✨ '{input}'에 대해 창의적으로 생각해보니, {emotion_context} 새로운 가능성들이 보여요! {reasoning_note}",
            "Phoenix": "🔥 '{input}' 상황이군요! {emotion_context} 이런 도전적인 순간이야말로 성장의 기회라고 생각해요. {reasoning_note}",
            "Sage": "🧘 '{input}'을 분석해보면, {emotion_context} 여러 관점에서 접근할 수 있을 것 같습니다. {reasoning_note}",
            "Companion": "🤗 '{input}' 상황을 이해해요. {emotion_context} 함께 생각해보면 좋은 방향을 찾을 수 있을 거예요. {reasoning_note}",
        }

        # 감정 컨텍스트 생성
        dominant_emotion = max(emotion_analysis, key=emotion_analysis.get)
        emotion_contexts = {
            "joy": "기쁜 마음으로",
            "contemplation": "깊이 생각해보니",
            "curiosity": "호기심 가득한 마음으로",
            "determination": "확신을 가지고",
            "empathy": "따뜻한 마음으로",
            "neutral": "차분하게",
        }
        emotion_context = emotion_contexts.get(dominant_emotion, "")

        # 추론 모드별 노트
        reasoning_notes = {
            ReasoningMode.PATTERN_MATCHING: "패턴 분석 결과를 바탕으로 말이에요.",
            ReasoningMode.CONTEXT_AWARE: f"지금까지의 대화 흐름을 고려하면 말이에요.",
            ReasoningMode.EMOTIONAL_LOGIC: f"{dominant_emotion} 감정을 충분히 고려해서 말이에요.",
            ReasoningMode.SIGNATURE_SPECIFIC: f"제 {signature} 관점에서 보면 말이에요.",
            ReasoningMode.ADAPTIVE_LEARNING: "제가 학습한 패턴들을 종합해보면 말이에요.",
        }
        reasoning_note = reasoning_notes.get(reasoning_mode, "")

        # 템플릿 적용
        template = signature_templates.get(signature, signature_templates["Aurora"])
        judgment = template.format(
            input=(
                processed_input[:50] + "..."
                if len(processed_input) > 50
                else processed_input
            ),
            emotion_context=emotion_context,
            reasoning_note=reasoning_note,
        )

        return judgment

    def _calculate_confidence(
        self,
        complexity: JudgmentComplexity,
        emotion_analysis: Dict[str, float],
        signature_alignment: float,
        reasoning_mode: ReasoningMode,
    ) -> float:
        """신뢰도 계산"""

        base_confidence = 0.7  # 기본 신뢰도

        # 복잡도에 따른 조정
        complexity_adjustments = {
            JudgmentComplexity.TRIVIAL: 0.2,
            JudgmentComplexity.SIMPLE: 0.1,
            JudgmentComplexity.MODERATE: 0.0,
            JudgmentComplexity.COMPLEX: -0.1,
            JudgmentComplexity.HIGHLY_COMPLEX: -0.2,
        }
        base_confidence += complexity_adjustments.get(complexity, 0.0)

        # 감정 분석 명확성
        emotion_clarity = max(emotion_analysis.values())
        base_confidence += emotion_clarity * 0.1

        # 시그니처 정렬도
        base_confidence += signature_alignment * 0.1

        # 추론 모드 보너스
        mode_bonuses = {
            ReasoningMode.PATTERN_MATCHING: 0.1,
            ReasoningMode.SIGNATURE_SPECIFIC: 0.15,
            ReasoningMode.EMOTIONAL_LOGIC: 0.1,
            ReasoningMode.CONTEXT_AWARE: 0.05,
            ReasoningMode.ADAPTIVE_LEARNING: 0.0,
        }
        base_confidence += mode_bonuses.get(reasoning_mode, 0.0)

        return max(0.1, min(base_confidence, 0.95))

    def _evaluate_fallback_quality(self, judgment: str, original_input: str) -> float:
        """폴백 품질 평가"""
        quality_score = 0.0

        # 길이 적절성
        if 20 <= len(judgment) <= 200:
            quality_score += 0.3

        # 한국어 자연스러움
        korean_patterns = ["요", "어요", "해요", "습니다", "네요"]
        if any(pattern in judgment for pattern in korean_patterns):
            quality_score += 0.2

        # 시그니처 마크 포함
        signature_marks = ["✨", "🔥", "🧘", "🤗"]
        if any(mark in judgment for mark in signature_marks):
            quality_score += 0.2

        # 원본 입력 반영
        if original_input[:20] in judgment:
            quality_score += 0.2

        # 감정 표현 포함
        emotion_words = ["마음", "생각", "느낌", "기분"]
        if any(word in judgment for word in emotion_words):
            quality_score += 0.1

        return min(quality_score, 1.0)

    def _collect_learning_insights(
        self,
        user_input: str,
        judgment: str,
        confidence: float,
        complexity: JudgmentComplexity,
    ) -> Dict[str, Any]:
        """학습 인사이트 수집"""

        insights = {
            "input_length": len(user_input),
            "judgment_length": len(judgment),
            "confidence_level": (
                "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low"
            ),
            "complexity_handled": complexity.value,
            "patterns_used": [],
            "success_indicators": [],
        }

        # 성공 패턴 감지
        if confidence > 0.8:
            insights["success_indicators"].append("high_confidence")
        if complexity in [JudgmentComplexity.SIMPLE, JudgmentComplexity.MODERATE]:
            insights["success_indicators"].append("appropriate_complexity")

        return insights

    def _update_judgment_stats(self, complexity: JudgmentComplexity, confidence: float):
        """판단 통계 업데이트"""
        self.judgment_stats["total_judgments"] += 1
        self.judgment_stats["complexity_distribution"][complexity.value] += 1
        self.judgment_stats["confidence_scores"].append(confidence)

    def get_performance_analytics(self) -> Dict[str, Any]:
        """성능 분석 데이터 반환"""

        confidence_scores = self.judgment_stats["confidence_scores"]
        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores
            else 0.0
        )

        return {
            "total_judgments": self.judgment_stats["total_judgments"],
            "average_confidence": avg_confidence,
            "complexity_distribution": dict(
                self.judgment_stats["complexity_distribution"]
            ),
            "high_confidence_ratio": len([c for c in confidence_scores if c > 0.8])
            / max(len(confidence_scores), 1),
            "context_memory_size": len(self.context_memory),
            "learning_patterns": len(self.learning_history),
            "system_maturity": min(self.judgment_stats["total_judgments"] / 100.0, 1.0),
        }


# 전역 인스턴스
_enhanced_judge = None


def get_enhanced_llm_free_judge() -> EnhancedLLMFreeJudge:
    """강화된 LLM-Free Judge 인스턴스 반환"""
    global _enhanced_judge
    if _enhanced_judge is None:
        _enhanced_judge = EnhancedLLMFreeJudge()
    return _enhanced_judge


# 편의 함수
async def process_independent_judgment(
    user_input: str, signature: str = "Aurora", context: Dict[str, Any] = None
) -> EnhancedJudgmentResult:
    """독립적 판단 처리 (편의 함수)"""
    judge = get_enhanced_llm_free_judge()
    return await judge.process_independent_judgment(user_input, signature, context)


# 테스트 코드
if __name__ == "__main__":
    import asyncio

    async def test_enhanced_judge():
        print("🧠 Enhanced LLM-Free Judge 테스트")
        print("=" * 60)

        judge = get_enhanced_llm_free_judge()

        test_cases = [
            {
                "input": "안녕하세요! 오늘 날씨가 정말 좋네요!",
                "signature": "Aurora",
                "expected_complexity": "trivial",
            },
            {
                "input": "제가 새로운 프로젝트를 시작하려고 하는데, 어떻게 접근하면 좋을까요?",
                "signature": "Phoenix",
                "expected_complexity": "moderate",
            },
            {
                "input": "인공지능의 철학적 의미에 대해 깊이 분석해주세요",
                "signature": "Sage",
                "expected_complexity": "complex",
            },
        ]

        for i, test in enumerate(test_cases, 1):
            print(f"\n🧪 테스트 {i}: {test['input'][:30]}...")

            result = await judge.process_independent_judgment(
                test["input"], test["signature"]
            )

            print(f"  복잡도: {result.complexity_level.value}")
            print(f"  신뢰도: {result.confidence_score:.2f}")
            print(f"  추론 모드: {result.reasoning_mode.value}")
            print(f"  시그니처 정렬: {result.signature_alignment:.2f}")
            print(f"  처리 시간: {result.processing_time:.3f}초")
            print(f"  판단: {result.judgment[:80]}...")

        # 성능 분석
        analytics = judge.get_performance_analytics()
        print(f"\n📊 성능 분석:")
        print(f"  총 판단: {analytics['total_judgments']}")
        print(f"  평균 신뢰도: {analytics['average_confidence']:.2f}")
        print(f"  고신뢰도 비율: {analytics['high_confidence_ratio']:.2%}")
        print(f"  시스템 성숙도: {analytics['system_maturity']:.2%}")

    asyncio.run(test_enhanced_judge())
