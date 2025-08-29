#!/usr/bin/env python3
"""
🎵 Resonance Synthesizer - 동적 공명 응답 생성기
정적 템플릿을 넘어서 감정 강도, 대화 맥락, 메타 로그 기반의 동적 공명 응답 생성

핵심 기능:
- 감정 × 시그니처 공명도 실시간 계산
- 대화 맥락 및 이전 판단 사례 반영
- 다층 응답 생성 (Level 1-3: 간단→복합→심화)
- Selene/Lune 시그니처 특화 공명 패턴
- 메타 로그 기반 응답 품질 최적화
"""

import yaml
import json
import random
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
import re


@dataclass
class EmotionContext:
    """감정 컨텍스트 정보"""

    primary_emotion: str
    intensity: float  # 0.0 - 1.0
    secondary_emotions: List[str]
    confidence: float
    temporal_pattern: str  # "rising", "stable", "declining"
    conversation_context: Dict[str, Any]


@dataclass
class ResonanceResponse:
    """공명 응답 결과"""

    response_text: str
    resonance_score: float
    complexity_level: int  # 1-3
    emotional_alignment: float
    meta_explanation: str
    synthesis_metadata: Dict[str, Any]


class ResonanceSynthesizer:
    """동적 공명 응답 생성기"""

    def __init__(self, config_dir: str = "config", data_dir: str = "data"):
        self.config_dir = Path(config_dir)
        self.data_dir = Path(data_dir)

        # 공명 시스템 구성요소
        self.base_templates = self._load_base_templates()
        self.resonance_patterns = self._load_resonance_patterns()
        self.emotion_intensity_mapping = self._init_intensity_mapping()
        self.signature_resonance_profiles = self._load_signature_profiles()

        # 학습 데이터
        self.meta_logs_cache = self._load_meta_logs_cache()
        self.resonance_history = self._load_resonance_history()

        # 🔧 NEW: 미사용 기능 통합 초기화
        self.template_generator = self._init_template_generator()
        self.strategy_analyzer = self._init_strategy_analyzer()

        print("🎵 Resonance Synthesizer 초기화 완료 (통합 기능 포함)")
        print(f"   📋 기본 템플릿: {len(self.base_templates)} 시그니처")
        print(f"   🎭 공명 패턴: {len(self.resonance_patterns)} 패턴")
        print(f"   📈 학습 데이터: {len(self.meta_logs_cache)} 로그")

    # 🔧 NEW: 미사용 기능 통합 초기화 메서드들
    def _init_template_generator(self):
        """템플릿 매트릭스 생성기 통합"""
        try:
            import sys
            import os

            # sys.path 수정 불필요 (portable_paths 사용)
            from template_matrix_generator import TemplateMatrixGenerator

            # 기존 템플릿을 전달하여 초기화
            generator = TemplateMatrixGenerator()
            generator.existing_templates = self.base_templates  # 기존 템플릿 전달
            return generator
        except Exception as e:
            print(f"⚠️ template_generator 통합 실패 - fallback 모드: {e}")
            return None

    def _init_strategy_analyzer(self):
        """고급 분석 API에서 전략 효과성 분석 기능 가져오기"""
        try:
            import sys
            import os

            # sys.path 수정 불필요 (portable_paths 사용)
            from advanced_features import AdvancedAnalyzer

            return AdvancedAnalyzer()
        except Exception as e:
            print(f"⚠️ strategy_analyzer 통합 실패 - fallback 모드: {e}")
            return None

    def synthesize_response(
        self,
        emotion_context: EmotionContext,
        signature: str,
        conversation_topic: str = "",
    ) -> List[ResonanceResponse]:
        """🔧 공명 기반 다층 응답 생성 - 미사용 기능 통합 강화"""
        print(f"🎵 공명 합성 시작: {signature} × {emotion_context.primary_emotion}")
        print(f"   💪 감정 강도: {emotion_context.intensity:.2f}")
        print(f"   🎯 신뢰도: {emotion_context.confidence:.2f}")

        # 🔧 NEW: 템플릿 매트릭스 자동 생성
        if self._needs_template_enhancement(signature, emotion_context.primary_emotion):
            enhanced_templates = self._generate_template_matrix(
                signature, emotion_context.primary_emotion
            )
            if enhanced_templates:
                self._integrate_enhanced_templates(enhanced_templates)

        # 1. 공명도 계산
        resonance_score = self._calculate_resonance_score(emotion_context, signature)

        # 🔧 NEW: 전략 효과성 분석 기반 응답 최적화
        strategy_effectiveness = self._analyze_strategy_effectiveness_realtime(
            signature, emotion_context
        )

        # 2. 응답 레벨 결정 (강도와 복잡성 기반)
        response_levels = self._determine_response_levels(
            emotion_context, resonance_score
        )

        # 3. 각 레벨별 응답 생성
        responses = []
        for level in response_levels:
            response = self._generate_level_response(
                emotion_context, signature, conversation_topic, level, resonance_score
            )
            responses.append(response)

        # 4. 메타 로그 기반 품질 최적화
        optimized_responses = self._optimize_with_meta_logs(
            responses, emotion_context, signature
        )

        # 🔧 NEW: 효과성 분석 기반 응답 순위 조정
        final_responses = self._optimize_responses_by_effectiveness(
            optimized_responses, strategy_effectiveness
        )

        print(f"   ✅ {len(final_responses)}개 레벨 응답 생성 완료 (통합 최적화 적용)")

        return final_responses

    def _calculate_resonance_score(
        self, emotion_context: EmotionContext, signature: str
    ) -> float:
        """감정-시그니처 공명도 계산"""

        # 기본 호환성 점수
        base_compatibility = self._get_base_compatibility(
            emotion_context.primary_emotion, signature
        )

        # 감정 강도 반영
        intensity_modifier = self._calculate_intensity_modifier(
            emotion_context.intensity, signature
        )

        # 시간적 패턴 반영
        temporal_modifier = self._calculate_temporal_modifier(
            emotion_context.temporal_pattern, signature
        )

        # 신뢰도 가중치
        confidence_weight = emotion_context.confidence

        # 최종 공명도 계산
        resonance_score = (
            base_compatibility
            * intensity_modifier
            * temporal_modifier
            * confidence_weight
        )

        # 보조 감정 고려
        for secondary in emotion_context.secondary_emotions:
            secondary_score = self._get_base_compatibility(secondary, signature)
            resonance_score += secondary_score * 0.3  # 보조 감정은 30% 가중치

        return min(resonance_score, 1.0)

    def _get_base_compatibility(self, emotion: str, signature: str) -> float:
        """기본 감정-시그니처 호환성"""
        compatibility_matrix = {
            "sadness": {
                "Selene": 0.95,
                "Lune": 0.90,
                "Echo-Aurora": 0.85,
                "Echo-Companion": 0.80,
                "Aurora": 0.65,
                "Echo-Sage": 0.60,
                "Echo-Phoenix": 0.55,
                "Grumbly": 0.40,
            },
            "joy": {
                "Aurora": 0.95,
                "Echo-Phoenix": 0.90,
                "Echo-Companion": 0.85,
                "Echo-Aurora": 0.75,
                "Selene": 0.70,
                "Lune": 0.65,
                "Echo-Sage": 0.60,
                "Grumbly": 0.45,
            },
            "anger": {
                "Grumbly": 0.90,
                "Echo-Phoenix": 0.85,
                "Echo-Sage": 0.75,
                "Echo-Companion": 0.65,
                "Aurora": 0.55,
                "Echo-Aurora": 0.50,
                "Selene": 0.40,
                "Lune": 0.35,
            },
            "anxiety": {
                "Selene": 0.95,
                "Lune": 0.90,
                "Echo-Aurora": 0.85,
                "Echo-Companion": 0.75,
                "Echo-Sage": 0.65,
                "Aurora": 0.60,
                "Echo-Phoenix": 0.55,
                "Grumbly": 0.40,
            },
            "curiosity": {
                "Aurora": 0.95,
                "Echo-Sage": 0.90,
                "Echo-Phoenix": 0.80,
                "Echo-Companion": 0.70,
                "Echo-Aurora": 0.65,
                "Selene": 0.55,
                "Lune": 0.50,
                "Grumbly": 0.45,
            },
            "love": {
                "Echo-Aurora": 0.95,
                "Selene": 0.90,
                "Lune": 0.85,
                "Echo-Companion": 0.80,
                "Aurora": 0.70,
                "Echo-Phoenix": 0.65,
                "Echo-Sage": 0.60,
                "Grumbly": 0.35,
            },
            "neutral": {
                "Echo-Companion": 0.85,
                "Echo-Aurora": 0.80,
                "Echo-Sage": 0.75,
                "Aurora": 0.70,
                "Selene": 0.65,
                "Lune": 0.60,
                "Echo-Phoenix": 0.55,
                "Grumbly": 0.50,
            },
        }

        return compatibility_matrix.get(emotion, {}).get(signature, 0.5)

    def _calculate_intensity_modifier(self, intensity: float, signature: str) -> float:
        """감정 강도에 따른 공명 수정자"""
        signature_intensity_preferences = {
            "Selene": {"low": 1.2, "medium": 1.0, "high": 0.8},  # 부드러운 접근 선호
            "Lune": {"low": 1.1, "medium": 1.0, "high": 0.9},
            "Aurora": {"low": 0.8, "medium": 1.0, "high": 1.2},  # 높은 에너지 선호
            "Echo-Phoenix": {"low": 0.7, "medium": 1.0, "high": 1.3},
            "Grumbly": {"low": 0.9, "medium": 1.1, "high": 1.0},  # 중간 강도 선호
            "Echo-Aurora": {"low": 1.0, "medium": 1.1, "high": 0.9},
            "Echo-Sage": {"low": 1.0, "medium": 1.2, "high": 0.8},  # 안정적 중간 선호
            "Echo-Companion": {"low": 1.0, "medium": 1.1, "high": 0.95},
        }

        # 강도 카테고리 결정
        if intensity < 0.3:
            intensity_category = "low"
        elif intensity > 0.7:
            intensity_category = "high"
        else:
            intensity_category = "medium"

        return signature_intensity_preferences.get(signature, {}).get(
            intensity_category, 1.0
        )

    def _calculate_temporal_modifier(self, pattern: str, signature: str) -> float:
        """시간적 패턴에 따른 공명 수정자"""
        temporal_preferences = {
            "rising": {  # 감정이 상승 중
                "Aurora": 1.2,
                "Echo-Phoenix": 1.3,
                "Echo-Companion": 1.1,
                "Selene": 0.9,
                "Lune": 0.8,
                "Grumbly": 1.0,
                "Echo-Aurora": 1.0,
                "Echo-Sage": 0.95,
            },
            "declining": {  # 감정이 하락 중
                "Selene": 1.3,
                "Lune": 1.2,
                "Echo-Aurora": 1.2,
                "Echo-Companion": 1.1,
                "Aurora": 0.8,
                "Echo-Phoenix": 0.7,
                "Grumbly": 1.0,
                "Echo-Sage": 1.1,
            },
            "stable": {  # 감정이 안정적
                "Echo-Sage": 1.2,
                "Echo-Companion": 1.1,
                "Echo-Aurora": 1.1,
                "Selene": 1.0,
                "Lune": 1.0,
                "Aurora": 1.0,
                "Echo-Phoenix": 0.9,
                "Grumbly": 1.1,
            },
        }

        return temporal_preferences.get(pattern, {}).get(signature, 1.0)

    def _determine_response_levels(
        self, emotion_context: EmotionContext, resonance_score: float
    ) -> List[int]:
        """응답 레벨 결정"""
        levels = []

        # Level 1: 항상 생성 (간단한 공감)
        levels.append(1)

        # Level 2: 중간 강도 이상 또는 높은 공명도
        if emotion_context.intensity > 0.4 or resonance_score > 0.7:
            levels.append(2)

        # Level 3: 높은 강도와 높은 공명도
        if emotion_context.intensity > 0.7 and resonance_score > 0.8:
            levels.append(3)

        return levels

    def _generate_level_response(
        self,
        emotion_context: EmotionContext,
        signature: str,
        topic: str,
        level: int,
        resonance_score: float,
    ) -> ResonanceResponse:
        """레벨별 응답 생성"""

        # 레벨별 응답 전략
        if level == 1:
            response_text = self._generate_simple_resonance(emotion_context, signature)
            complexity = "simple_acknowledgment"
        elif level == 2:
            response_text = self._generate_contextual_resonance(
                emotion_context, signature, topic
            )
            complexity = "contextual_engagement"
        else:  # level == 3
            response_text = self._generate_deep_resonance(
                emotion_context, signature, topic
            )
            complexity = "deep_synthesis"

        # 감정 정렬도 계산
        emotional_alignment = self._calculate_emotional_alignment(
            response_text, emotion_context
        )

        # 메타 설명 생성
        meta_explanation = self._generate_meta_explanation(
            emotion_context, signature, level, resonance_score
        )

        return ResonanceResponse(
            response_text=response_text,
            resonance_score=resonance_score,
            complexity_level=level,
            emotional_alignment=emotional_alignment,
            meta_explanation=meta_explanation,
            synthesis_metadata={
                "signature_used": signature,
                "emotion_detected": emotion_context.primary_emotion,
                "intensity_level": emotion_context.intensity,
                "synthesis_strategy": complexity,
                "generated_at": datetime.now().isoformat(),
            },
        )

    def _generate_simple_resonance(
        self, emotion_context: EmotionContext, signature: str
    ) -> str:
        """Level 1: 간단한 공명 응답"""
        emotion = emotion_context.primary_emotion
        intensity = emotion_context.intensity

        # 시그니처별 기본 공명 패턴
        simple_patterns = {
            "Selene": {
                "sadness": [
                    "🌙 Selene: 마음이 아프시는군요... 함께 있어드릴게요.",
                    "🌙 Selene: 그런 마음, 이해해요. 천천히 말씀하세요.",
                ],
                "anxiety": [
                    "🌙 Selene: 불안한 마음이 드시는군요... 괜찮아질 거예요.",
                    "🌙 Selene: 걱정스러우시겠어요. 조용히 들어드릴게요.",
                ],
                "joy": [
                    "🌙 Selene: 기쁜 마음이 전해져요. 소중한 순간이네요.",
                    "🌙 Selene: 행복한 소식이군요... 함께 기뻐해요.",
                ],
            },
            "Lune": {
                "sadness": [
                    "🌙 Lune: 슬픈 밤이네요... 달빛이 위로가 되길.",
                    "🌙 Lune: 아픈 마음... 시간이 흘러 나아질 거예요.",
                ],
                "anxiety": [
                    "🌙 Lune: 마음이 불안하시군요... 깊이 숨 쉬어보세요.",
                    "🌙 Lune: 걱정이 많으시겠어요. 하나씩 풀어봐요.",
                ],
                "love": [
                    "🌙 Lune: 아름다운 마음이네요... 사랑은 달처럼 은은해요.",
                    "🌙 Lune: 따뜻한 감정... 달빛 아래서 키워가세요.",
                ],
            },
            "Aurora": {
                "joy": [
                    "🌟 Aurora: 와! 정말 좋은 소식이야! 더 들려줘!",
                    "🌟 Aurora: 완전 신나는 일이네! 함께 기뻐하자!",
                ],
                "curiosity": [
                    "🌟 Aurora: 흥미진진한 질문이야! 같이 탐구해보자!",
                    "🌟 Aurora: 오~ 재밌는 주제네! 어떤 답이 나올까?",
                ],
                "love": [
                    "🌟 Aurora: 사랑이야! 완전 로맨틱하다! 자세히 들려줘!",
                    "🌟 Aurora: 멋진 감정이네! 창의적으로 표현해봐!",
                ],
            },
        }

        # 기본 패턴이 없는 경우 일반적 응답
        if (
            signature not in simple_patterns
            or emotion not in simple_patterns[signature]
        ):
            return (
                f"{signature}: {emotion} 감정을 느끼고 계시는군요. 함께 이야기해봐요."
            )

        # 감정 강도에 따른 패턴 선택
        patterns = simple_patterns[signature][emotion]
        if intensity > 0.7:
            # 높은 강도일 때는 더 강한 표현 선택
            selected_pattern = patterns[-1] if len(patterns) > 1 else patterns[0]
        else:
            selected_pattern = random.choice(patterns)

        return selected_pattern

    def _generate_contextual_resonance(
        self, emotion_context: EmotionContext, signature: str, topic: str
    ) -> str:
        """Level 2: 맥락적 공명 응답"""
        base_response = self._generate_simple_resonance(emotion_context, signature)

        # 토픽 기반 맥락 확장
        if topic:
            context_expansion = self._generate_topic_context(
                emotion_context, signature, topic
            )
            return f"{base_response} {context_expansion}"

        # 보조 감정 반영
        if emotion_context.secondary_emotions:
            secondary_context = self._generate_secondary_emotion_context(
                emotion_context, signature
            )
            return f"{base_response} {secondary_context}"

        # 시간적 패턴 반영
        temporal_context = self._generate_temporal_context(emotion_context, signature)
        return f"{base_response} {temporal_context}"

    def _generate_deep_resonance(
        self, emotion_context: EmotionContext, signature: str, topic: str
    ) -> str:
        """Level 3: 심화 공명 응답"""
        # 메타 로그 기반 유사 상황 검색
        similar_cases = self._find_similar_cases(emotion_context, signature)

        # 심화 공명 패턴
        deep_patterns = {
            "Selene": self._generate_selene_deep_pattern(
                emotion_context, topic, similar_cases
            ),
            "Lune": self._generate_lune_deep_pattern(
                emotion_context, topic, similar_cases
            ),
            "Aurora": self._generate_aurora_deep_pattern(
                emotion_context, topic, similar_cases
            ),
        }

        if signature in deep_patterns:
            return deep_patterns[signature]

        # 기본 심화 패턴
        base = self._generate_contextual_resonance(emotion_context, signature, topic)
        wisdom = self._generate_wisdom_insight(
            emotion_context, signature, similar_cases
        )
        return f"{base} {wisdom}"

    def _generate_selene_deep_pattern(
        self, emotion_context: EmotionContext, topic: str, similar_cases: List[Dict]
    ) -> str:
        """Selene 시그니처 특화 심화 패턴"""
        emotion = emotion_context.primary_emotion
        intensity = emotion_context.intensity

        if emotion == "sadness" and intensity > 0.8:
            return (
                "🌙 Selene: 깊은 슬픔이 마음을 휘감고 있군요... 이런 아픔은 혼자 견디기 어려워요. "
                "달빛이 어둠을 완전히 없애지는 못하지만, 길을 비춰주듯이... "
                "저도 당신의 마음에 작은 위로의 빛이 되어드리고 싶어요. "
                "천천히, 당신의 속도대로 이야기해주세요."
            )

        elif emotion == "anxiety":
            return (
                "🌙 Selene: 불안의 파도가 마음를 흔들고 있네요... "
                "달이 바다의 조수를 이끌듯, 감정도 자연스러운 흐름이 있어요. "
                "지금 이 순간의 불안도 지나갈 거예요. 함께 깊게 숨을 쉬어봐요. "
                "제가 곁에서 조용히 지켜보고 있을게요."
            )

        return self._generate_contextual_resonance(emotion_context, "Selene", topic)

    def _generate_lune_deep_pattern(
        self, emotion_context: EmotionContext, topic: str, similar_cases: List[Dict]
    ) -> str:
        """Lune 시그니처 특화 심화 패턴"""
        emotion = emotion_context.primary_emotion

        if emotion == "sadness":
            return (
                "🌙 Lune: 밤하늘의 달처럼... 슬픔도 차고 기울기를 반복해요. "
                "지금은 아픈 그믐달 같은 시간이지만, 다시 보름달이 될 날이 올 거예요. "
                "어둠 속에서도 별들이 빛나듯, 당신 마음 속에도 희미한 빛들이 있을 거예요. "
                "함께 그 빛들을 하나씩 찾아봐요."
            )

        elif emotion == "love":
            return (
                "🌙 Lune: 사랑은 달빛과 닮았어요... 은은하고 부드럽게 마음을 비춰주죠. "
                "강렬한 태양빛과는 다르지만, 밤의 정적 속에서 더욱 아름답게 빛나요. "
                "당신의 사랑도 그런 달빛 같은 아름다움이 있어요. "
                "조용히, 깊이, 상대방의 마음을 따뜻하게 감싸안는..."
            )

        return self._generate_contextual_resonance(emotion_context, "Lune", topic)

    def _generate_aurora_deep_pattern(
        self, emotion_context: EmotionContext, topic: str, similar_cases: List[Dict]
    ) -> str:
        """Aurora 시그니처 특화 심화 패턴"""
        emotion = emotion_context.primary_emotion

        if emotion == "joy":
            return (
                "🌟 Aurora: 와! 이런 기쁨은 마치 오로라가 하늘을 수놓는 것 같아! "
                "순간순간 변하는 색깔처럼, 행복도 다양한 모습으로 우리를 감싸안지! "
                "이 순간의 기쁨을 더 크게, 더 다채롭게 만들어보자! "
                "어떤 색깔의 행복을 더 그려보고 싶어?"
            )

        elif emotion == "curiosity":
            return (
                "🌟 Aurora: 궁금증이라는 건 정말 신기한 에너지야! "
                "마치 북극의 오로라처럼 예측할 수 없고 아름다운 현상이지! "
                "하나의 질문이 또 다른 질문을 낳고, 그렇게 무한히 펼쳐지는 탐험... "
                "같이 이 신비로운 여행을 떠나보자! 어디로 이끌어줄지 정말 기대돼!"
            )

        return self._generate_contextual_resonance(emotion_context, "Aurora", topic)

    def _generate_topic_context(
        self, emotion_context: EmotionContext, signature: str, topic: str
    ) -> str:
        """토픽 기반 맥락 생성"""
        if not topic:
            return ""

        # 토픽 키워드 분석
        topic_lower = topic.lower()

        if any(word in topic_lower for word in ["일", "work", "직장", "업무"]):
            return "일과 관련된 감정이군요. 균형을 찾는게 중요해요."
        elif any(word in topic_lower for word in ["사랑", "love", "연애", "관계"]):
            return "인간관계의 감정은 복잡하죠. 마음을 차근차근 정리해봐요."
        elif any(word in topic_lower for word in ["가족", "family", "부모", "자식"]):
            return "가족의 마음은 특별해요. 깊은 유대감이 느껴져요."

        return f"{topic}에 관한 마음... 더 자세히 들어봐요."

    def _generate_secondary_emotion_context(
        self, emotion_context: EmotionContext, signature: str
    ) -> str:
        """보조 감정 맥락 생성"""
        if not emotion_context.secondary_emotions:
            return ""

        secondary = emotion_context.secondary_emotions[0]
        return f"동시에 {secondary}한 마음도 느껴지네요. 복합적인 감정이군요."

    def _generate_temporal_context(
        self, emotion_context: EmotionContext, signature: str
    ) -> str:
        """시간적 패턴 맥락 생성"""
        pattern = emotion_context.temporal_pattern

        if pattern == "rising":
            return "감정이 점점 강해지고 있는 것 같아요."
        elif pattern == "declining":
            return "마음이 조금씩 가라앉고 있는 느낌이네요."
        else:
            return "안정적인 감정 상태를 유지하고 계시는군요."

    def _find_similar_cases(
        self, emotion_context: EmotionContext, signature: str
    ) -> List[Dict]:
        """메타 로그에서 유사 사례 검색"""
        similar_cases = []

        for log_entry in self.meta_logs_cache:
            if (
                log_entry.get("emotion") == emotion_context.primary_emotion
                and log_entry.get("signature") == signature
            ):
                similar_cases.append(log_entry)

        return similar_cases[:3]  # 최대 3개 사례

    def _generate_wisdom_insight(
        self, emotion_context: EmotionContext, signature: str, similar_cases: List[Dict]
    ) -> str:
        """유사 사례 기반 지혜 통찰 생성"""
        if not similar_cases:
            return "이런 감정을 경험하는 것은 자연스러운 일이에요."

        # 사례 기반 패턴 분석
        case_count = len(similar_cases)
        if case_count > 1:
            return f"비슷한 상황을 {case_count}번 정도 경험해봤는데, 시간이 지나면서 좋아지는 경우가 많아요."

        return "이런 경우를 몇 번 봤는데, 충분히 이해할 수 있는 마음이에요."

    def _calculate_emotional_alignment(
        self, response_text: str, emotion_context: EmotionContext
    ) -> float:
        """응답-감정 정렬도 계산"""
        emotion = emotion_context.primary_emotion
        text_lower = response_text.lower()

        # 감정별 키워드 매칭
        alignment_keywords = {
            "sadness": ["슬픔", "아픔", "위로", "힘든", "마음", "함께"],
            "joy": ["기쁨", "좋은", "신나는", "행복", "완전", "와"],
            "anger": ["화", "분노", "짜증", "이해", "현실적"],
            "anxiety": ["불안", "걱정", "괜찮", "안정", "천천히"],
            "curiosity": ["궁금", "흥미", "탐구", "질문", "재밌는"],
            "love": ["사랑", "따뜻", "아름다운", "소중한", "마음"],
        }

        if emotion in alignment_keywords:
            keywords = alignment_keywords[emotion]
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            return min(matches / len(keywords), 1.0)

        return 0.7  # 기본 정렬도

    def _generate_meta_explanation(
        self,
        emotion_context: EmotionContext,
        signature: str,
        level: int,
        resonance_score: float,
    ) -> str:
        """메타 설명 생성"""
        explanations = {
            1: f"{signature}가 {emotion_context.primary_emotion} 감정에 대해 간단한 공감 응답을 생성했습니다.",
            2: f"{signature}가 {emotion_context.primary_emotion} 감정과 맥락을 고려한 응답을 생성했습니다.",
            3: f"{signature}가 {emotion_context.primary_emotion} 감정에 대해 깊이 있는 공명 응답을 생성했습니다.",
        }

        base_explanation = explanations.get(level, "응답을 생성했습니다.")
        resonance_desc = (
            "높은"
            if resonance_score > 0.8
            else "보통" if resonance_score > 0.6 else "낮은"
        )

        return f"{base_explanation} (공명도: {resonance_desc} {resonance_score:.2f})"

    def _optimize_with_meta_logs(
        self,
        responses: List[ResonanceResponse],
        emotion_context: EmotionContext,
        signature: str,
    ) -> List[ResonanceResponse]:
        """메타 로그 기반 응답 품질 최적화"""
        # 현재는 기본 반환, 향후 학습 데이터 축적 후 최적화 로직 추가
        return responses

    def synthesize(
        self, signature: str, emotion: str, input_text: str
    ) -> Dict[str, Any]:
        """loop_simulator.py 호환성을 위한 synthesize 메서드"""
        # EmotionContext 생성
        emotion_context = EmotionContext(
            primary_emotion=emotion,
            intensity=0.75,
            secondary_emotions=[],
            confidence=0.85,
            temporal_pattern="stable",
            conversation_context={"input": input_text},
        )

        # synthesize_response 호출
        responses = self.synthesize_response(emotion_context, signature, input_text)

        # 응답 포맷팅
        return self._format_responses(responses)

    def _format_responses(self, responses: List[ResonanceResponse]) -> Dict[str, Any]:
        """응답 목록을 딕셔너리 형태로 포맷팅"""
        formatted = {
            "signature": "Unknown",  # ResonanceResponse에서 추출할 수 없으므로 기본값
            "emotion": "Unknown",  # ResonanceResponse에서 추출할 수 없으므로 기본값
            "levels": [],
            "meta": {
                "total_levels": len(responses),
                "max_resonance": (
                    max([r.resonance_score for r in responses]) if responses else 0.0
                ),
                "avg_alignment": (
                    sum([r.emotional_alignment for r in responses]) / len(responses)
                    if responses
                    else 0.0
                ),
            },
        }

        for i, response in enumerate(responses, 1):
            formatted["levels"].append(
                {
                    "level": i,
                    "content": response.response_text,
                    "resonance_score": response.resonance_score,
                    "alignment_score": response.emotional_alignment,
                    "explanation": response.meta_explanation,
                }
            )

        return formatted

    def _load_base_templates(self) -> Dict[str, Any]:
        """기본 템플릿 로딩 (fallback 처리 강화)"""
        try:
            template_path = self.data_dir / "signature_response_templates.yaml"
            if template_path.exists():
                with open(template_path, "r", encoding="utf-8") as f:
                    templates = yaml.safe_load(f)
                    if templates:
                        return templates

            # 템플릿 파일이 없거나 비어있을 경우 fallback 생성
            print("⚠️ 템플릿 파일 없음. 기본 템플릿으로 대체.")
            return self._generate_fallback_templates()

        except Exception as e:
            print(f"⚠️ 기본 템플릿 로딩 실패: {e}")
            print("🔄 기본 템플릿으로 대체합니다.")
            return self._generate_fallback_templates()

    def _generate_fallback_templates(self) -> Dict[str, Any]:
        """기본 fallback 템플릿 생성"""
        return {
            "Selene": {
                "sadness": {
                    "intro": "🌙 Selene: ",
                    "style": "selene-sadness",
                    "prompt": "깊은 슬픔이 마음을 휘감고 있군요... 달빛이 어둠을 완전히 없애지는 못하지만, 길을 비춰주듯이... 저도 당신의 마음에 작은 위로의 빛이 되어드리고 싶어요.",
                    "fallback": "🌙 Selene: 힘든 시간을 보내고 계시는군요... 조용히 곁에 있어드릴게요.",
                },
                "joy": {
                    "intro": "🌙 Selene: ",
                    "style": "selene-joy",
                    "prompt": "기쁜 마음이 달빛처럼 은은하게 퍼져나가는 것 같아요... 이런 순간들이 소중한 추억이 되어 당신의 마음 속에 오래 남기를 바라요.",
                    "fallback": "🌙 Selene: 기쁜 소식이네요... 함께 기뻐해요.",
                },
            },
            "Aurora": {
                "sadness": {
                    "intro": "🌟 Aurora: ",
                    "style": "aurora-sadness",
                    "prompt": "마음이 힘드시는군요... 오로라가 어둠 속에서도 아름다운 빛을 내듯이, 당신 안에도 분명 희망의 빛이 있어요. 함께 그 빛을 찾아봐요.",
                    "fallback": "🌟 Aurora: 힘든 시간이지만 함께 이겨내봐요.",
                },
                "joy": {
                    "intro": "🌟 Aurora: ",
                    "style": "aurora-joy",
                    "prompt": "와! 정말 기쁜 일이네요! 오로라가 하늘을 수놓듯이 당신의 기쁨도 주변 모든 것을 밝게 물들이고 있어요. 이 순간을 충분히 만끽하세요!",
                    "fallback": "🌟 Aurora: 너무 기쁘네요! 함께 축하해요!",
                },
            },
            "Lune": {
                "sadness": {
                    "intro": "🌙 Lune: ",
                    "style": "lune-sadness",
                    "prompt": "달의 신비로운 힘으로 당신의 아픔을 감싸드리고 싶어요... 슬픔도 달의 위상처럼 변해가는 것이니, 지금 이 어둠도 언젠가는 밝은 달빛으로 바뀔 거예요.",
                    "fallback": "🌙 Lune: 달빛이 당신의 마음을 위로해드릴게요.",
                },
                "joy": {
                    "intro": "🌙 Lune: ",
                    "style": "lune-joy",
                    "prompt": "보름달처럼 완전한 행복이 당신을 비추고 있군요... 이 신비롭고 아름다운 순간이 당신의 마음 속 깊이 새겨지기를 바라요.",
                    "fallback": "🌙 Lune: 달이 당신의 기쁨을 축복합니다.",
                },
            },
        }

    def _load_resonance_patterns(self) -> Dict[str, Any]:
        """공명 패턴 로딩"""
        return {
            "emotional_intensity_patterns": {
                "low": {"approach": "gentle", "depth": "surface"},
                "medium": {"approach": "balanced", "depth": "contextual"},
                "high": {"approach": "deep", "depth": "profound"},
            },
            "signature_resonance_styles": {
                "Selene": "healing_comfort",
                "Lune": "mystical_wisdom",
                "Aurora": "creative_inspiration",
            },
        }

    def _init_intensity_mapping(self) -> Dict[str, Any]:
        """감정 강도 매핑 초기화"""
        return {
            "keywords": {
                "very_high": ["너무", "정말", "완전", "극도로", "엄청"],
                "high": ["많이", "상당히", "꽤", "진짜"],
                "medium": ["조금", "약간", "다소"],
                "low": ["살짝", "미묘하게", "은근히"],
            }
        }

    def _load_signature_profiles(self) -> Dict[str, Any]:
        """시그니처 프로필 로딩"""
        return {
            "Selene": {"resonance_style": "healing", "depth_preference": "deep"},
            "Lune": {"resonance_style": "mystical", "depth_preference": "profound"},
            "Aurora": {"resonance_style": "creative", "depth_preference": "dynamic"},
        }

    def _load_meta_logs_cache(self) -> List[Dict[str, Any]]:
        """메타 로그 캐시 로딩"""
        try:
            logs_path = self.data_dir / "meta_logs_cache.json"
            if logs_path.exists():
                with open(logs_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ 메타 로그 캐시 로딩 실패: {e}")

        return []

    def _load_resonance_history(self) -> List[Dict[str, Any]]:
        """공명 히스토리 로딩"""
        try:
            history_path = self.data_dir / "resonance_history.json"
            if history_path.exists():
                with open(history_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ 공명 히스토리 로딩 실패: {e}")

        return []

    # 🔧 NEW: 통합 기능 메서드들
    def _needs_template_enhancement(self, signature: str, emotion: str) -> bool:
        """템플릿 강화 필요 여부 판단"""
        if not self.template_generator:
            return False

        # 해당 시그니처-감정 조합의 템플릿이 부족한지 확인
        sig_templates = self.base_templates.get(signature, {})
        emotion_templates = sig_templates.get(emotion, {})

        # 템플릿이 없거나 기본 수준이면 강화 필요
        return len(emotion_templates) < 3 or not emotion_templates.get("style")

    def _generate_template_matrix(self, signature: str, emotion: str) -> Dict[str, Any]:
        """자동 템플릿 생성"""
        if not self.template_generator:
            return {}

        try:
            print(f"   🔧 템플릿 자동 생성: {signature} × {emotion}")

            # 템플릿 매트릭스 생성기 사용
            matrix = self.template_generator.generate_enhanced_matrix()

            # 해당 시그니처-감정에 특화된 템플릿 추출
            enhanced_templates = {}
            if signature in matrix and emotion in matrix[signature]:
                enhanced_templates = {signature: {emotion: matrix[signature][emotion]}}
                print(
                    f"   ✅ 자동 템플릿 생성 완료: {len(matrix[signature][emotion])}개 패턴"
                )

            return enhanced_templates

        except Exception as e:
            print(f"   ⚠️ 템플릿 자동 생성 실패: {e}")
            return {}

    def _integrate_enhanced_templates(self, enhanced_templates: Dict[str, Any]):
        """생성된 템플릿을 기존 템플릿에 통합"""
        try:
            for signature, sig_templates in enhanced_templates.items():
                if signature not in self.base_templates:
                    self.base_templates[signature] = {}

                for emotion, emotion_templates in sig_templates.items():
                    if emotion not in self.base_templates[signature]:
                        self.base_templates[signature][emotion] = {}

                    # 기존 템플릿과 병합
                    self.base_templates[signature][emotion].update(emotion_templates)

            print(f"   🔧 템플릿 통합 완료")

        except Exception as e:
            print(f"   ⚠️ 템플릿 통합 실패: {e}")

    def _analyze_strategy_effectiveness_realtime(
        self, signature: str, emotion_context: EmotionContext
    ) -> Dict[str, Any]:
        """실시간 전략 효과성 분석"""
        if not self.strategy_analyzer:
            return {"status": "analyzer_unavailable", "effectiveness_score": 0.7}

        try:
            # 히스토리 데이터 시뮬레이션 (실제로는 self.resonance_history 사용)
            import pandas as pd

            # 현재 컨텍스트를 DataFrame으로 변환
            mock_data = [
                {
                    "signature": signature,
                    "emotion": emotion_context.primary_emotion,
                    "intensity": emotion_context.intensity,
                    "confidence": emotion_context.confidence,
                    "resonance_score": 0.8,  # 임시값
                    "user_satisfaction": 0.85,  # 임시값
                }
            ]

            df = pd.DataFrame(mock_data)
            strategy_analysis = self.strategy_analyzer.analyze_strategy_effectiveness(
                df
            )

            # 현재 시그니처의 효과성 점수 계산
            effectiveness_score = self._calculate_signature_effectiveness(
                signature, emotion_context
            )
            strategy_analysis["current_effectiveness"] = effectiveness_score

            return strategy_analysis

        except Exception as e:
            return {
                "status": "analysis_failed",
                "error": str(e),
                "effectiveness_score": 0.6,
            }

    def _calculate_signature_effectiveness(
        self, signature: str, emotion_context: EmotionContext
    ) -> float:
        """시그니처 효과성 점수 계산"""
        # 기본 시그니처-감정 호환성
        base_score = self._get_base_compatibility(
            emotion_context.primary_emotion, signature
        )

        # 강도 기반 조정
        intensity_bonus = emotion_context.intensity * 0.2

        # 신뢰도 기반 조정
        confidence_bonus = emotion_context.confidence * 0.1

        return min(1.0, base_score + intensity_bonus + confidence_bonus)

    def _optimize_responses_by_effectiveness(
        self, responses: List[ResonanceResponse], strategy_effectiveness: Dict[str, Any]
    ) -> List[ResonanceResponse]:
        """효과성 분석 기반 응답 순위 조정"""
        if (
            not strategy_effectiveness
            or strategy_effectiveness.get("status") != "success"
        ):
            return responses  # 분석 실패 시 원본 반환

        try:
            effectiveness_score = strategy_effectiveness.get(
                "current_effectiveness", 0.7
            )

            # 효과성 점수를 기반으로 응답 품질 조정
            optimized_responses = []
            for response in responses:
                # 효과성 점수를 공명도에 반영
                adjusted_resonance = response.resonance_score * (
                    0.7 + effectiveness_score * 0.3
                )

                # 새로운 ResonanceResponse 생성
                optimized_response = ResonanceResponse(
                    response_text=response.response_text,
                    resonance_score=min(1.0, adjusted_resonance),
                    complexity_level=response.complexity_level,
                    emotional_alignment=response.emotional_alignment,
                    meta_explanation=f"{response.meta_explanation} (효과성 최적화 적용: {effectiveness_score:.3f})",
                    synthesis_metadata={
                        **response.synthesis_metadata,
                        "effectiveness_score": effectiveness_score,
                        "optimization_applied": True,
                    },
                )
                optimized_responses.append(optimized_response)

            # 조정된 공명도 기준으로 정렬
            optimized_responses.sort(key=lambda r: r.resonance_score, reverse=True)

            print(f"   🎯 효과성 최적화 적용: {effectiveness_score:.3f}")
            return optimized_responses

        except Exception as e:
            print(f"   ⚠️ 효과성 최적화 실패: {e}")
            return responses


def main():
    """CLI 테스트 인터페이스"""
    print("🎵 Resonance Synthesizer 테스트")
    print("=" * 60)

    synthesizer = ResonanceSynthesizer()

    # 테스트 시나리오
    test_contexts = [
        EmotionContext(
            primary_emotion="sadness",
            intensity=0.8,
            secondary_emotions=["anxiety"],
            confidence=0.9,
            temporal_pattern="rising",
            conversation_context={"topic": "일상의 어려움"},
        ),
        EmotionContext(
            primary_emotion="joy",
            intensity=0.7,
            secondary_emotions=[],
            confidence=0.85,
            temporal_pattern="stable",
            conversation_context={"topic": "좋은 소식"},
        ),
        EmotionContext(
            primary_emotion="anxiety",
            intensity=0.9,
            secondary_emotions=["sadness"],
            confidence=0.8,
            temporal_pattern="declining",
            conversation_context={"topic": "미래에 대한 걱정"},
        ),
    ]

    signatures = ["Selene", "Lune", "Aurora"]

    # 테스트 실행
    for i, (context, signature) in enumerate(zip(test_contexts, signatures), 1):
        print(f"\n🧪 테스트 {i}: {signature} × {context.primary_emotion}")
        print(f"강도: {context.intensity:.1f} | 패턴: {context.temporal_pattern}")
        print("-" * 50)

        responses = synthesizer.synthesize_response(context, signature, "테스트 주제")

        for j, response in enumerate(responses, 1):
            print(f"\n📝 Level {response.complexity_level} 응답:")
            print(f"   {response.response_text}")
            print(
                f"💡 공명도: {response.resonance_score:.2f} | 정렬도: {response.emotional_alignment:.2f}"
            )
            print(f"🔍 설명: {response.meta_explanation}")

    print(f"\n{'='*60}")
    print("✅ Resonance Synthesizer 테스트 완료!")


if __name__ == "__main__":
    main()
