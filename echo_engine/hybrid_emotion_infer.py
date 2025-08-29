#!/usr/bin/env python3
"""
🎭 Hybrid Emotion Infer - KoSimCSE 기반 soft 감정 추론

기존 keyword 방식과 KoSimCSE 임베딩 기반 soft 추론을 병합하여
GPT 수준의 미묘한 감정 인식 능력을 구현합니다.

기존 emotion_infer.py는 유지하고, v2 확장 모듈로 개발됩니다.
"""

import time
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re

try:
    # KoSimCSE 임베딩 (선택적 import)
    from sentence_transformers import SentenceTransformer

    KOSIMCSE_AVAILABLE = True
except ImportError:
    KOSIMCSE_AVAILABLE = False

# 기존 모듈과의 호환성을 위한 import
try:
    from echo_engine.emotion_infer import infer_emotion as legacy_infer_emotion
    from echo_engine.emotion_infer import EmotionInferenceResult

    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False

    # 폴백용 EmotionInferenceResult 정의
    @dataclass
    class EmotionInferenceResult:
        primary_emotion: str
        confidence: float
        intensity: float
        secondary_emotions: List[str]
        foundation_doctrine_compliance: bool = True


class EmotionConfidenceLevel(Enum):
    """감정 확신도 레벨"""

    VERY_HIGH = "very_high"  # 0.9+
    HIGH = "high"  # 0.7-0.9
    MODERATE = "moderate"  # 0.5-0.7
    LOW = "low"  # 0.3-0.5
    VERY_LOW = "very_low"  # 0.0-0.3


@dataclass
class HybridEmotionResult:
    """하이브리드 감정 추론 결과"""

    primary_emotion: str
    confidence: float
    intensity: float
    confidence_level: EmotionConfidenceLevel
    secondary_emotions: List[str]
    emotion_vector: Optional[np.ndarray] = None
    keyword_signals: List[str] = None
    semantic_signals: List[str] = None
    hybrid_method_used: str = "combined"
    processing_time: float = 0.0


class HybridEmotionInfer:
    """🎭 하이브리드 감정 추론기"""

    def __init__(self):
        self.version = "2.0.0-hybrid"

        # KoSimCSE 모델 (사용 가능한 경우)
        self.kosimcse_model = None
        if KOSIMCSE_AVAILABLE:
            try:
                self.kosimcse_model = SentenceTransformer(
                    "BM-K/KoSimCSE-roberta-multitask"
                )
                print("✅ KoSimCSE 모델 로드 완료")
            except Exception as e:
                print(f"⚠️ KoSimCSE 모델 로드 실패: {e}")
                KOSIMCSE_AVAILABLE = False

        # 감정별 임베딩 레퍼런스 (KoSimCSE 기반)
        self.emotion_references = self._build_emotion_references()

        # 키워드 기반 감정 시그널 (기존 방식 강화)
        self.emotion_keywords = {
            "joy": {
                "strong": [
                    "기쁘",
                    "행복",
                    "즐거",
                    "신나",
                    "좋아",
                    "사랑",
                    "완벽",
                    "최고",
                ],
                "moderate": ["만족", "괜찮", "나쁘지않", "그럭저럭", "보통"],
                "subtle": ["그래", "응", "알겠", "음"],
            },
            "sadness": {
                "strong": ["슬프", "우울", "힘들", "속상", "눈물", "아프", "절망"],
                "moderate": ["아쉽", "외로", "허무", "그저그런"],
                "subtle": ["음", "그냥", "모르겠"],
            },
            "anger": {
                "strong": ["화", "짜증", "빡", "분노", "열받", "미치", "싫"],
                "moderate": ["답답", "억울", "불만", "짜증"],
                "subtle": ["에이", "아", "뭐야"],
            },
            "fear": {
                "strong": ["무서", "두려", "불안", "걱정", "위험", "긴장"],
                "moderate": ["초조", "스트레스", "조심", "경계"],
                "subtle": ["혹시", "만약", "아마"],
            },
            "surprise": {
                "strong": ["놀라", "깜짝", "와", "헉", "어", "정말"],
                "moderate": ["신기", "의외", "예상외", "생각못한"],
                "subtle": ["아", "오", "음"],
            },
        }

        # 통계
        self.inference_stats = {
            "total_inferences": 0,
            "hybrid_successes": 0,
            "keyword_fallbacks": 0,
            "legacy_fallbacks": 0,
            "average_confidence": 0.0,
            "average_processing_time": 0.0,
        }

        print(f"🎭 Hybrid Emotion Infer v{self.version} 초기화 완료")
        print(f"   KoSimCSE 가용: {'✅' if KOSIMCSE_AVAILABLE else '❌'}")
        print(f"   Legacy 호환: {'✅' if LEGACY_AVAILABLE else '❌'}")

    def _build_emotion_references(self) -> Dict[str, List[str]]:
        """감정별 레퍼런스 문장 구성"""
        return {
            "joy": [
                "정말 기쁘고 행복해요",
                "너무 좋아서 웃음이 나와요",
                "마음이 따뜻하고 만족스러워요",
                "즐겁고 신나는 기분이에요",
            ],
            "sadness": [
                "마음이 슬프고 우울해요",
                "눈물이 날 것 같아요",
                "외롭고 허무한 기분이에요",
                "힘들고 지쳐있어요",
            ],
            "anger": [
                "정말 화가 나고 짜증나요",
                "분노가 치밀어 올라요",
                "답답하고 열받아요",
                "억울하고 불만스러워요",
            ],
            "fear": [
                "무섭고 두려워요",
                "불안하고 걱정돼요",
                "긴장되고 조심스러워요",
                "위험할 것 같아요",
            ],
            "surprise": [
                "정말 놀랍고 신기해요",
                "예상하지 못했어요",
                "깜짝 놀랐어요",
                "의외의 일이에요",
            ],
            "neutral": [
                "평범하고 보통이에요",
                "특별할 것 없어요",
                "그냥 그래요",
                "차분하고 안정적이에요",
            ],
        }

    def infer(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> HybridEmotionResult:
        """🎯 하이브리드 감정 추론 메인 함수"""
        start_time = time.time()
        self.inference_stats["total_inferences"] += 1

        # 1단계: 키워드 기반 기본 추론
        keyword_emotion, keyword_confidence, keyword_signals = self._keyword_inference(
            text
        )

        # 2단계: 의미론적 추론 (KoSimCSE 기반)
        semantic_emotion, semantic_confidence, semantic_signals = (
            self._semantic_inference(text)
        )

        # 3단계: 하이브리드 조합
        final_emotion, final_confidence, method_used = self._combine_inferences(
            keyword_emotion, keyword_confidence, semantic_emotion, semantic_confidence
        )

        # 4단계: 보조 감정 탐지
        secondary_emotions = self._detect_secondary_emotions(text, final_emotion)

        # 5단계: 강도 및 확신도 레벨 계산
        intensity = self._calculate_intensity(text, final_emotion, final_confidence)
        confidence_level = self._determine_confidence_level(final_confidence)

        processing_time = time.time() - start_time

        # 결과 구성
        result = HybridEmotionResult(
            primary_emotion=final_emotion,
            confidence=final_confidence,
            intensity=intensity,
            confidence_level=confidence_level,
            secondary_emotions=secondary_emotions,
            keyword_signals=keyword_signals,
            semantic_signals=semantic_signals,
            hybrid_method_used=method_used,
            processing_time=processing_time,
        )

        # 통계 업데이트
        self._update_stats(result)

        return result

    def _keyword_inference(self, text: str) -> Tuple[str, float, List[str]]:
        """키워드 기반 감정 추론"""
        text_lower = text.lower()
        emotion_scores = {}
        detected_signals = []

        for emotion, intensity_keywords in self.emotion_keywords.items():
            score = 0.0

            # 강도별 키워드 매칭
            for signal in intensity_keywords["strong"]:
                if signal in text_lower:
                    score += 1.0
                    detected_signals.append(f"strong:{signal}")

            for signal in intensity_keywords["moderate"]:
                if signal in text_lower:
                    score += 0.6
                    detected_signals.append(f"moderate:{signal}")

            for signal in intensity_keywords["subtle"]:
                if signal in text_lower:
                    score += 0.3
                    detected_signals.append(f"subtle:{signal}")

            if score > 0:
                emotion_scores[emotion] = score

        # 최고 점수 감정 선택
        if emotion_scores:
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            max_score = emotion_scores[primary_emotion]
            # 정규화된 신뢰도 (0.3-0.8 범위)
            confidence = min(0.8, 0.3 + (max_score / 3.0) * 0.5)
            return primary_emotion, confidence, detected_signals

        return "neutral", 0.5, []

    def _semantic_inference(self, text: str) -> Tuple[str, float, List[str]]:
        """의미론적 감정 추론 (KoSimCSE 기반)"""
        if not KOSIMCSE_AVAILABLE or not self.kosimcse_model:
            return "neutral", 0.0, ["kosimcse_unavailable"]

        try:
            # 입력 텍스트 임베딩
            text_embedding = self.kosimcse_model.encode([text])[0]

            emotion_similarities = {}
            semantic_signals = []

            # 각 감정 레퍼런스와 유사도 계산
            for emotion, references in self.emotion_references.items():
                ref_embeddings = self.kosimcse_model.encode(references)

                # 코사인 유사도 계산
                similarities = []
                for ref_embedding in ref_embeddings:
                    similarity = np.dot(text_embedding, ref_embedding) / (
                        np.linalg.norm(text_embedding) * np.linalg.norm(ref_embedding)
                    )
                    similarities.append(similarity)

                # 최대 유사도
                max_similarity = max(similarities)
                emotion_similarities[emotion] = max_similarity

                if max_similarity > 0.5:  # 임계값
                    semantic_signals.append(f"semantic:{emotion}:{max_similarity:.3f}")

            # 최고 유사도 감정 선택
            if emotion_similarities:
                primary_emotion = max(emotion_similarities.items(), key=lambda x: x[1])[
                    0
                ]
                confidence = emotion_similarities[primary_emotion]

                # 신뢰도 보정 (0.4-0.9 범위)
                confidence = max(0.4, min(0.9, confidence))

                return primary_emotion, confidence, semantic_signals

        except Exception as e:
            semantic_signals.append(f"semantic_error:{str(e)}")

        return "neutral", 0.0, semantic_signals

    def _combine_inferences(
        self,
        keyword_emotion: str,
        keyword_confidence: float,
        semantic_emotion: str,
        semantic_confidence: float,
    ) -> Tuple[str, float, str]:
        """키워드와 의미론적 추론 결과 조합"""

        # 의미론적 추론이 불가능한 경우
        if semantic_confidence == 0.0:
            self.inference_stats["keyword_fallbacks"] += 1
            return keyword_emotion, keyword_confidence, "keyword_only"

        # 두 방법이 같은 감정을 감지한 경우
        if keyword_emotion == semantic_emotion:
            # 신뢰도 가중 평균 (의미론적에 더 높은 가중치)
            combined_confidence = keyword_confidence * 0.3 + semantic_confidence * 0.7
            self.inference_stats["hybrid_successes"] += 1
            return keyword_emotion, combined_confidence, "hybrid_agreement"

        # 두 방법이 다른 감정을 감지한 경우
        if semantic_confidence > keyword_confidence + 0.2:
            # 의미론적 추론 우선
            return semantic_emotion, semantic_confidence * 0.9, "semantic_priority"
        elif keyword_confidence > semantic_confidence + 0.2:
            # 키워드 추론 우선
            return keyword_emotion, keyword_confidence * 0.9, "keyword_priority"
        else:
            # 신뢰도 기반 선택
            if semantic_confidence >= keyword_confidence:
                return semantic_emotion, semantic_confidence * 0.8, "semantic_selected"
            else:
                return keyword_emotion, keyword_confidence * 0.8, "keyword_selected"

    def _detect_secondary_emotions(self, text: str, primary_emotion: str) -> List[str]:
        """보조 감정 탐지"""
        secondary = []
        text_lower = text.lower()

        for emotion, intensity_keywords in self.emotion_keywords.items():
            if emotion == primary_emotion:
                continue

            # 보조 감정 점수 계산
            score = 0
            for signal in intensity_keywords["strong"]:
                if signal in text_lower:
                    score += 1
            for signal in intensity_keywords["moderate"]:
                if signal in text_lower:
                    score += 0.5

            if score >= 0.5:  # 임계값
                secondary.append(emotion)

        return secondary[:2]  # 최대 2개까지

    def _calculate_intensity(self, text: str, emotion: str, confidence: float) -> float:
        """감정 강도 계산"""
        base_intensity = confidence

        # 감탄사나 강조 표현으로 강도 조정
        intensity_modifiers = {
            "very_high": ["정말", "너무", "완전", "엄청", "진짜", "대박", "최고"],
            "high": ["많이", "꽤", "상당히", "제법"],
            "low": ["조금", "약간", "살짝", "그럭저럭"],
        }

        text_lower = text.lower()

        for level, modifiers in intensity_modifiers.items():
            for modifier in modifiers:
                if modifier in text_lower:
                    if level == "very_high":
                        base_intensity = min(1.0, base_intensity * 1.3)
                    elif level == "high":
                        base_intensity = min(1.0, base_intensity * 1.15)
                    elif level == "low":
                        base_intensity = max(0.1, base_intensity * 0.8)
                    break

        return base_intensity

    def _determine_confidence_level(self, confidence: float) -> EmotionConfidenceLevel:
        """확신도 레벨 결정"""
        if confidence >= 0.9:
            return EmotionConfidenceLevel.VERY_HIGH
        elif confidence >= 0.7:
            return EmotionConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return EmotionConfidenceLevel.MODERATE
        elif confidence >= 0.3:
            return EmotionConfidenceLevel.LOW
        else:
            return EmotionConfidenceLevel.VERY_LOW

    def _update_stats(self, result: HybridEmotionResult):
        """통계 업데이트"""
        total = self.inference_stats["total_inferences"]
        current_avg_conf = self.inference_stats["average_confidence"]
        current_avg_time = self.inference_stats["average_processing_time"]

        # 평균 신뢰도 업데이트
        if total == 1:
            self.inference_stats["average_confidence"] = result.confidence
            self.inference_stats["average_processing_time"] = result.processing_time
        else:
            new_avg_conf = (current_avg_conf * (total - 1) + result.confidence) / total
            new_avg_time = (
                current_avg_time * (total - 1) + result.processing_time
            ) / total
            self.inference_stats["average_confidence"] = new_avg_conf
            self.inference_stats["average_processing_time"] = new_avg_time

    def to_legacy_format(self, result: HybridEmotionResult) -> EmotionInferenceResult:
        """기존 EmotionInferenceResult 형식으로 변환"""
        return EmotionInferenceResult(
            primary_emotion=result.primary_emotion,
            confidence=result.confidence,
            intensity=result.intensity,
            secondary_emotions=result.secondary_emotions,
            foundation_doctrine_compliance=True,
        )

    def get_inference_stats(self) -> Dict[str, Any]:
        """추론 통계 반환"""
        total = max(self.inference_stats["total_inferences"], 1)

        return {
            **self.inference_stats,
            "hybrid_success_rate": (self.inference_stats["hybrid_successes"] / total)
            * 100,
            "keyword_fallback_rate": (self.inference_stats["keyword_fallbacks"] / total)
            * 100,
            "kosimcse_available": KOSIMCSE_AVAILABLE,
            "legacy_compatible": LEGACY_AVAILABLE,
        }


# 전역 인스턴스
_hybrid_emotion_infer: Optional[HybridEmotionInfer] = None


def get_hybrid_emotion_infer() -> HybridEmotionInfer:
    """하이브리드 감정 추론기 인스턴스 반환"""
    global _hybrid_emotion_infer
    if _hybrid_emotion_infer is None:
        _hybrid_emotion_infer = HybridEmotionInfer()
    return _hybrid_emotion_infer


def hybrid_infer_emotion(
    text: str, context: Optional[Dict[str, Any]] = None
) -> HybridEmotionResult:
    """🎯 하이브리드 감정 추론 진입점"""
    infer_engine = get_hybrid_emotion_infer()
    return infer_engine.infer(text, context)


def hybrid_infer_emotion_legacy(
    text: str, context: Optional[Dict[str, Any]] = None
) -> EmotionInferenceResult:
    """기존 호환성을 위한 legacy 형식 반환"""
    infer_engine = get_hybrid_emotion_infer()
    hybrid_result = infer_engine.infer(text, context)
    return infer_engine.to_legacy_format(hybrid_result)


if __name__ == "__main__":
    # 하이브리드 감정 추론기 테스트
    print("🧪 Hybrid Emotion Infer 테스트")

    test_cases = [
        "오늘 정말 기분이 좋아요! 너무 행복해서 웃음이 나와요",
        "요즘 마음이 좀 우울하고 힘들어요... 눈물이 날 것 같아요",
        "진짜 화가 나서 미치겠어요! 답답하고 열받아요",
        "혹시 무언가 잘못될까봐 걱정되고 불안해요",
        "와! 정말 놀라운 소식이네요. 예상하지 못했어요",
        "그냥 평범한 하루예요. 특별할 것 없어요",
        "조금 슬프기도 하고 기쁘기도 한 복잡한 마음이에요",
    ]

    infer_engine = get_hybrid_emotion_infer()

    for i, test_text in enumerate(test_cases, 1):
        print(f"\n🎯 테스트 {i}: {test_text}")

        result = infer_engine.infer(test_text)

        print(f"   감정: {result.primary_emotion} (신뢰도: {result.confidence:.3f})")
        print(f"   강도: {result.intensity:.3f}")
        print(f"   확신도 레벨: {result.confidence_level.value}")
        print(f"   보조 감정: {result.secondary_emotions}")
        print(f"   추론 방법: {result.hybrid_method_used}")
        print(f"   처리 시간: {result.processing_time:.4f}초")

        if result.keyword_signals:
            print(f"   키워드 시그널: {result.keyword_signals[:3]}")
        if result.semantic_signals:
            print(f"   의미 시그널: {result.semantic_signals[:2]}")

    # 통계 출력
    print(f"\n📊 추론 통계:")
    stats = infer_engine.get_inference_stats()
    print(f"   총 추론: {stats['total_inferences']}")
    print(f"   하이브리드 성공률: {stats['hybrid_success_rate']:.1f}%")
    print(f"   평균 신뢰도: {stats['average_confidence']:.3f}")
    print(f"   평균 처리시간: {stats['average_processing_time']:.4f}초")
