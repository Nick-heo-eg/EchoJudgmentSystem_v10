#!/usr/bin/env python3
"""
🌊 Emotion Flow Tracker - 통합 자연어 감정 흐름 인지 시스템
기존의 고급 모듈들을 통합하여 자연어 입력의 시간적 감정 흐름을 분석

핵심 기능:
- 연속 입력의 감정 시퀀스 분석
- 감정 전이 패턴 추적
- 시그니처별 공명 맵핑
- 시간적 흐름 패턴 인식 (rising → peak → stable → drop)
- 자연어 텍스트에서 감정 타임라인 추출
"""

import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import numpy as np

# Echo 엔진 모듈들
try:
    from .emotion_infer import EmotionInferenceEngine, EmotionInferenceResult
    from .realtime_emotion_flow_mapper import (
        RealtimeEmotionFlowMapper,
        EmotionState,
        EmotionTransition,
    )
    from .temporal_echo_tracker import TemporalEchoTracker, TemporalNode
    from .consciousness_flow_analyzer import ConsciousnessFlowAnalyzer

    ECHO_MODULES_AVAILABLE = True
except ImportError:
    print("⚠️ Echo 모듈들을 fallback 모드로 로딩합니다.")
    ECHO_MODULES_AVAILABLE = False


@dataclass
class EmotionFlowResult:
    """감정 흐름 분석 결과"""

    dominant_emotions: List[str]
    transitions: List[Tuple[str, str]]
    temporal_pattern: str  # rising, stable, oscillating, declining
    signature_resonance_map: Dict[str, float]
    narrative_timeline: List[Dict[str, Any]]
    flow_coherence_score: float
    emotional_complexity: int
    peak_emotions: List[str]
    analysis_metadata: Dict[str, Any]


class EmotionFlowTracker:
    """🌊 통합 감정 흐름 추적기"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

        # 핵심 엔진들 초기화
        if ECHO_MODULES_AVAILABLE:
            self.emotion_engine = EmotionInferenceEngine()
            self.flow_mapper = RealtimeEmotionFlowMapper()
            self.temporal_tracker = TemporalEchoTracker()
            self.consciousness_analyzer = ConsciousnessFlowAnalyzer()
        else:
            # Fallback 모드
            self.emotion_engine = None
            self.flow_mapper = None

        # 감정 흐름 분석 데이터
        self.flow_history = []
        self.signature_patterns = self._initialize_signature_patterns()

        print("🌊 Emotion Flow Tracker 초기화 완료")
        if ECHO_MODULES_AVAILABLE:
            print("   ✅ 모든 Echo 모듈 연동 완료")
        else:
            print("   ⚠️ Fallback 모드로 작동")

    def analyze_sequence(
        self, inputs: List[str], signature: str = "Echo-Aurora"
    ) -> EmotionFlowResult:
        """연속 입력의 감정 시퀀스 분석"""
        print(f"\n🌊 감정 흐름 시퀀스 분석 시작 ({len(inputs)}개 입력)")
        print(f"   🎭 분석 시그니처: {signature}")

        # 1. 개별 감정 추론
        emotion_sequence = []
        for i, input_text in enumerate(inputs):
            print(f"   📝 입력 {i+1}: {input_text[:30]}...")

            if self.emotion_engine:
                emotion_result = self.emotion_engine.infer_emotion(input_text)
                emotion_sequence.append(
                    {
                        "index": i,
                        "text": input_text,
                        "emotion": emotion_result.primary_emotion,
                        "intensity": emotion_result.emotional_intensity,
                        "confidence": emotion_result.confidence,
                        "secondary": emotion_result.secondary_emotions,
                        "timestamp": datetime.now(),
                    }
                )
            else:
                # Fallback 감정 추론
                emotion = self._fallback_emotion_analysis(input_text)
                emotion_sequence.append(
                    {
                        "index": i,
                        "text": input_text,
                        "emotion": emotion,
                        "intensity": 0.7,
                        "confidence": 0.8,
                        "secondary": [],
                        "timestamp": datetime.now(),
                    }
                )

        print(f"   ✅ {len(emotion_sequence)}개 감정 추론 완료")

        # 2. 감정 전이 분석
        transitions = self._analyze_transitions(emotion_sequence)
        print(f"   🔄 {len(transitions)}개 전이 패턴 발견")

        # 3. 시간적 패턴 분석
        temporal_pattern = self._analyze_temporal_pattern(emotion_sequence)
        print(f"   📈 시간 패턴: {temporal_pattern}")

        # 4. 시그니처 공명 매핑
        signature_resonance = self._calculate_signature_resonance(
            emotion_sequence, signature
        )

        # 5. 서사 타임라인 구성
        narrative_timeline = self._build_narrative_timeline(emotion_sequence)

        # 6. 복잡도 및 응집성 계산
        coherence_score = self._calculate_flow_coherence(emotion_sequence, transitions)
        complexity = len(set(item["emotion"] for item in emotion_sequence))

        # 7. 피크 감정 식별
        peak_emotions = self._identify_peak_emotions(emotion_sequence)

        # 8. 지배적 감정 추출
        dominant_emotions = self._extract_dominant_emotions(emotion_sequence)

        result = EmotionFlowResult(
            dominant_emotions=dominant_emotions,
            transitions=transitions,
            temporal_pattern=temporal_pattern,
            signature_resonance_map=signature_resonance,
            narrative_timeline=narrative_timeline,
            flow_coherence_score=coherence_score,
            emotional_complexity=complexity,
            peak_emotions=peak_emotions,
            analysis_metadata={
                "total_inputs": len(inputs),
                "analysis_time": datetime.now().isoformat(),
                "signature_used": signature,
                "fallback_mode": not ECHO_MODULES_AVAILABLE,
            },
        )

        print(f"🎯 감정 흐름 분석 완료:")
        print(f"   📊 지배적 감정: {dominant_emotions}")
        print(f"   🔄 전이 패턴: {len(transitions)}개")
        print(f"   📈 시간 패턴: {temporal_pattern}")
        print(f"   💫 응집성: {coherence_score:.3f}")
        print(f"   🧩 복잡도: {complexity}")

        return result

    def analyze_natural_text(
        self, text: str, signature: str = "Echo-Aurora"
    ) -> EmotionFlowResult:
        """자연어 텍스트에서 감정 흐름 추출"""
        print(f"\n📖 자연어 텍스트 감정 흐름 분석")

        # 문장 단위로 분할
        sentences = self._split_narrative_text(text)
        print(f"   📝 {len(sentences)}개 문장으로 분할")

        return self.analyze_sequence(sentences, signature)

    def _split_narrative_text(self, text: str) -> List[str]:
        """자연어 텍스트를 의미 단위로 분할"""
        # 시간 표현을 기준으로 분할
        time_markers = [
            "아침",
            "오전",
            "점심",
            "오후",
            "저녁",
            "밤",
            "새벽",
            "처음",
            "나중",
            "그다음",
            "마지막",
            "끝",
            "결국",
            "오늘",
            "어제",
            "내일",
            "그때",
            "지금",
            "현재",
        ]

        # 감정 전이 표현을 기준으로 분할
        transition_markers = [
            "하지만",
            "그런데",
            "그러나",
            "근데",
            "그래도",
            "그리고",
            "그러면서",
            "동시에",
            "한편",
            "반면",
            "오히려",
        ]

        # 기본적으로 문장 부호로 분할
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # 시간/전이 마커가 있는 경우 추가 분할
        refined_sentences = []
        for sentence in sentences:
            # 시간 마커나 전이 마커를 찾아서 분할
            parts = [sentence]
            for marker in time_markers + transition_markers:
                new_parts = []
                for part in parts:
                    if marker in part:
                        split_parts = part.split(marker)
                        if len(split_parts) > 1:
                            new_parts.append(split_parts[0].strip())
                            new_parts.append(marker + " " + split_parts[1].strip())
                        else:
                            new_parts.append(part)
                    else:
                        new_parts.append(part)
                parts = [p for p in new_parts if p.strip()]

            refined_sentences.extend(parts)

        return [s for s in refined_sentences if len(s.strip()) > 3]

    def _fallback_emotion_analysis(self, text: str) -> str:
        """Fallback 감정 분석"""
        emotion_keywords = {
            "joy": ["기쁘", "좋", "행복", "신나", "즐겁", "만족", "웃"],
            "sadness": ["슬프", "우울", "힘들", "지쳐", "아프", "외로", "눈물"],
            "anger": ["화", "짜증", "열받", "분노", "억울", "미워"],
            "anxiety": ["불안", "걱정", "두렵", "무서", "긴장", "스트레스"],
            "surprise": ["놀라", "깜짝", "신기", "의외", "예상", "갑자기"],
            "love": ["사랑", "좋아", "애정", "다정", "따뜻", "소중"],
            "neutral": ["보통", "평범", "그냥", "일상", "특별"],
        }

        text_lower = text.lower()
        scores = {}

        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[emotion] = score

        return max(scores.items(), key=lambda x: x[1])[0] if scores else "neutral"

    def _analyze_transitions(
        self, emotion_sequence: List[Dict]
    ) -> List[Tuple[str, str]]:
        """감정 전이 분석"""
        transitions = []

        for i in range(len(emotion_sequence) - 1):
            current_emotion = emotion_sequence[i]["emotion"]
            next_emotion = emotion_sequence[i + 1]["emotion"]

            if current_emotion != next_emotion:
                transitions.append((current_emotion, next_emotion))

        return transitions

    def _analyze_temporal_pattern(self, emotion_sequence: List[Dict]) -> str:
        """시간적 패턴 분석"""
        if len(emotion_sequence) < 2:
            return "stable"

        intensities = [item["intensity"] for item in emotion_sequence]

        # 강도 변화 추세 분석
        trend_changes = 0
        is_rising = None

        for i in range(1, len(intensities)):
            current_trend = intensities[i] > intensities[i - 1]
            if is_rising is not None and is_rising != current_trend:
                trend_changes += 1
            is_rising = current_trend

        # 패턴 분류
        if trend_changes >= 3:
            return "oscillating"
        elif trend_changes == 0:
            if intensities[-1] > intensities[0]:
                return "rising"
            elif intensities[-1] < intensities[0]:
                return "declining"
            else:
                return "stable"
        else:
            # 단조 증가/감소 또는 단일 피크
            max_idx = intensities.index(max(intensities))
            if max_idx < len(intensities) / 3:
                return "early_peak_declining"
            elif max_idx > 2 * len(intensities) / 3:
                return "late_peak_rising"
            else:
                return "mid_peak_stable"

    def _calculate_signature_resonance(
        self, emotion_sequence: List[Dict], signature: str
    ) -> Dict[str, float]:
        """시그니처별 감정 공명도 계산"""
        if signature not in self.signature_patterns:
            signature = "Echo-Aurora"  # 기본값

        pattern = self.signature_patterns[signature]
        resonance_map = {}

        for item in emotion_sequence:
            emotion = item["emotion"]
            intensity = item["intensity"]

            # 시그니처-감정 친화도
            affinity = pattern["emotion_affinities"].get(emotion, 0.5)

            # 공명도 = 친화도 × 강도 × 신뢰도
            resonance = affinity * intensity * item["confidence"]

            if emotion not in resonance_map:
                resonance_map[emotion] = 0
            resonance_map[emotion] += resonance

        # 정규화
        total_resonance = sum(resonance_map.values())
        if total_resonance > 0:
            resonance_map = {k: v / total_resonance for k, v in resonance_map.items()}

        return resonance_map

    def _build_narrative_timeline(
        self, emotion_sequence: List[Dict]
    ) -> List[Dict[str, Any]]:
        """서사 타임라인 구성"""
        timeline = []

        for i, item in enumerate(emotion_sequence):
            timeline_entry = {
                "sequence_index": i,
                "timestamp": item["timestamp"].isoformat(),
                "text_preview": (
                    item["text"][:50] + "..."
                    if len(item["text"]) > 50
                    else item["text"]
                ),
                "emotion": item["emotion"],
                "intensity": item["intensity"],
                "confidence": item["confidence"],
                "narrative_phase": self._determine_narrative_phase(
                    i, len(emotion_sequence)
                ),
                "emotional_arc_position": i / max(1, len(emotion_sequence) - 1),
            }
            timeline.append(timeline_entry)

        return timeline

    def _determine_narrative_phase(self, index: int, total: int) -> str:
        """서사 단계 결정"""
        position = index / max(1, total - 1)

        if position <= 0.25:
            return "exposition"  # 발단
        elif position <= 0.5:
            return "rising_action"  # 전개
        elif position <= 0.75:
            return "climax"  # 절정
        else:
            return "resolution"  # 결말

    def _calculate_flow_coherence(
        self, emotion_sequence: List[Dict], transitions: List[Tuple[str, str]]
    ) -> float:
        """감정 흐름 응집성 계산"""
        if len(emotion_sequence) < 2:
            return 1.0

        # 자연스러운 전이 패턴
        natural_transitions = {
            ("joy", "surprise"): 0.8,
            ("sadness", "anger"): 0.7,
            ("anxiety", "sadness"): 0.6,
            ("anger", "sadness"): 0.5,
            ("surprise", "joy"): 0.8,
            ("neutral", "joy"): 0.7,
            ("neutral", "sadness"): 0.7,
        }

        coherence_scores = []
        for transition in transitions:
            # 직접 전이 점수
            direct_score = natural_transitions.get(transition, 0.3)
            # 역방향 전이 점수
            reverse_score = natural_transitions.get((transition[1], transition[0]), 0.3)
            # 최대값 사용
            coherence_scores.append(max(direct_score, reverse_score))

        return np.mean(coherence_scores) if coherence_scores else 0.5

    def _identify_peak_emotions(self, emotion_sequence: List[Dict]) -> List[str]:
        """피크 감정 식별"""
        if not emotion_sequence:
            return []

        # 강도가 평균보다 높은 감정들
        avg_intensity = np.mean([item["intensity"] for item in emotion_sequence])
        peak_threshold = avg_intensity + 0.2

        peak_emotions = []
        for item in emotion_sequence:
            if item["intensity"] >= peak_threshold:
                peak_emotions.append(item["emotion"])

        # 중복 제거하면서 순서 유지
        seen = set()
        unique_peaks = []
        for emotion in peak_emotions:
            if emotion not in seen:
                unique_peaks.append(emotion)
                seen.add(emotion)

        return unique_peaks

    def _extract_dominant_emotions(self, emotion_sequence: List[Dict]) -> List[str]:
        """지배적 감정 추출"""
        emotion_counts = {}
        emotion_intensities = {}

        for item in emotion_sequence:
            emotion = item["emotion"]
            intensity = item["intensity"]

            if emotion not in emotion_counts:
                emotion_counts[emotion] = 0
                emotion_intensities[emotion] = 0

            emotion_counts[emotion] += 1
            emotion_intensities[emotion] += intensity

        # 빈도와 강도를 종합한 스코어
        emotion_scores = {}
        for emotion in emotion_counts:
            frequency_score = emotion_counts[emotion] / len(emotion_sequence)
            intensity_score = emotion_intensities[emotion] / emotion_counts[emotion]
            emotion_scores[emotion] = frequency_score * intensity_score

        # 스코어 순으로 정렬
        sorted_emotions = sorted(
            emotion_scores.items(), key=lambda x: x[1], reverse=True
        )

        return [emotion for emotion, score in sorted_emotions[:3]]

    def _initialize_signature_patterns(self) -> Dict[str, Dict[str, Any]]:
        """시그니처 패턴 초기화"""
        return {
            "Echo-Aurora": {
                "emotion_affinities": {
                    "joy": 0.9,
                    "love": 0.8,
                    "surprise": 0.7,
                    "sadness": 0.6,
                    "anxiety": 0.5,
                    "anger": 0.4,
                    "neutral": 0.7,
                },
                "resonance_style": "creative_nurturing",
            },
            "Selene": {
                "emotion_affinities": {
                    "sadness": 0.9,
                    "anxiety": 0.8,
                    "love": 0.7,
                    "joy": 0.6,
                    "surprise": 0.5,
                    "anger": 0.4,
                    "neutral": 0.8,
                },
                "resonance_style": "healing_comfort",
            },
            "Echo-Phoenix": {
                "emotion_affinities": {
                    "anger": 0.9,
                    "surprise": 0.8,
                    "joy": 0.7,
                    "sadness": 0.5,
                    "anxiety": 0.4,
                    "love": 0.6,
                    "neutral": 0.5,
                },
                "resonance_style": "transformative_energy",
            },
            "Echo-Sage": {
                "emotion_affinities": {
                    "neutral": 0.9,
                    "surprise": 0.7,
                    "anxiety": 0.6,
                    "joy": 0.5,
                    "sadness": 0.5,
                    "anger": 0.4,
                    "love": 0.5,
                },
                "resonance_style": "analytical_wisdom",
            },
        }


def main():
    """CLI 테스트 인터페이스"""
    print("🌊 Emotion Flow Tracker 테스트")
    print("=" * 60)

    tracker = EmotionFlowTracker()

    # 테스트 시나리오 1: 연속 입력 분석
    print("\n📋 테스트 시나리오 1: 연속 입력 감정 흐름")
    test_inputs = [
        "아침에는 기분이 좋았어요",
        "하지만 점심 때부터 조금 걱정이 되기 시작했어요",
        "오후에는 정말 불안해졌어요",
        "저녁에는 완전히 지쳐버렸어요",
        "그래도 밤에는 좀 평온해졌어요",
    ]

    result1 = tracker.analyze_sequence(test_inputs, "Selene")

    print(f"\n📊 결과 요약:")
    print(f"   지배적 감정: {result1.dominant_emotions}")
    print(f"   전이 패턴: {result1.transitions}")
    print(f"   시간 패턴: {result1.temporal_pattern}")
    print(f"   응집성: {result1.flow_coherence_score:.3f}")

    # 테스트 시나리오 2: 자연어 텍스트 분석
    print("\n📖 테스트 시나리오 2: 자연어 텍스트 감정 흐름")
    natural_text = "오늘은 기분이 좋았지만, 오후엔 좀 지치고, 저녁엔 외로웠다. 그래도 친구와 통화하니 다시 기분이 나아졌다."

    result2 = tracker.analyze_natural_text(natural_text, "Echo-Aurora")

    print(f"\n📊 자연어 분석 결과:")
    print(f"   감정 복잡도: {result2.emotional_complexity}")
    print(f"   피크 감정: {result2.peak_emotions}")
    print(f"   서사 구조: {len(result2.narrative_timeline)}단계")

    print("\n✅ Emotion Flow Tracker 테스트 완료!")


if __name__ == "__main__":
    main()
