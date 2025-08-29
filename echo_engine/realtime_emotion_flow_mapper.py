#!/usr/bin/env python3
"""
🌊 Real-time Emotion Flow Mapper v1.0
실시간 감정 흐름을 매핑하고 시각화하는 시스템

핵심 기능:
- 실시간 감정 상태 추적
- 감정 흐름 경로 매핑
- 감정 전이 패턴 분석
- 시그니처별 감정 반응 모니터링
- 감정 히트맵 생성
"""

import time
import json
import threading
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque
import numpy as np
import logging

# Echo 엔진 모듈들
try:
    from .echo_brain_monitor import get_brain_monitor, update_echo_brain_emotion
    from .signature_cross_resonance_mapper import SignatureCrossResonanceMapper
except ImportError:
    print("⚠️ Echo Brain modules not available, running in standalone mode")
    get_brain_monitor = None


@dataclass
class EmotionState:
    """감정 상태 정의"""

    timestamp: datetime
    emotion_type: str
    intensity: float  # 0.0 - 1.0
    source: str  # "user_input", "system_response", "signature_activation"
    signature_context: str
    triggers: List[str]
    duration_ms: int


@dataclass
class EmotionTransition:
    """감정 전이 정의"""

    from_emotion: str
    to_emotion: str
    transition_time: float  # seconds
    intensity_change: float
    trigger_event: str
    signature_involved: str
    smoothness_score: float  # 0.0 - 1.0


@dataclass
class EmotionFlowSnapshot:
    """감정 흐름 스냅샷"""

    timestamp: datetime
    active_emotions: Dict[str, float]
    dominant_emotion: str
    emotion_velocity: Dict[str, float]  # 감정 변화 속도
    signature_influence: Dict[str, float]
    flow_stability: float


class RealtimeEmotionFlowMapper:
    """🌊 실시간 감정 흐름 매퍼"""

    def __init__(self, history_length: int = 100, update_interval: float = 0.1):
        self.logger = logging.getLogger(__name__)
        self.history_length = history_length
        self.update_interval = update_interval

        # 감정 추적 상태
        self.emotion_history = deque(maxlen=history_length)
        self.transition_history = deque(maxlen=history_length)
        self.current_emotions = {}
        self.emotion_velocity = {}

        # 실시간 모니터링
        self.monitoring = False
        self.monitor_thread = None
        self.emotion_queue = queue.Queue()
        self.flow_callbacks = []

        # 감정 정의
        self.emotion_categories = {
            "positive": [
                "joy",
                "happiness",
                "excitement",
                "contentment",
                "love",
                "hope",
            ],
            "negative": [
                "sadness",
                "anger",
                "fear",
                "anxiety",
                "disappointment",
                "frustration",
            ],
            "neutral": ["calm", "neutral", "focused", "contemplative"],
            "complex": ["bittersweet", "nostalgic", "melancholic", "ambivalent"],
        }

        # 시그니처별 감정 프로파일
        self.signature_emotion_profiles = {
            "selene": {
                "preferred_emotions": [
                    "melancholic",
                    "gentle",
                    "empathetic",
                    "contemplative",
                ],
                "emotion_sensitivity": 0.9,
                "transition_style": "gradual",
            },
            "factbomb": {
                "preferred_emotions": [
                    "focused",
                    "determined",
                    "analytical",
                    "neutral",
                ],
                "emotion_sensitivity": 0.3,
                "transition_style": "sharp",
            },
            "lune": {
                "preferred_emotions": ["dreamy", "nostalgic", "poetic", "bittersweet"],
                "emotion_sensitivity": 0.8,
                "transition_style": "flowing",
            },
            "aurora": {
                "preferred_emotions": ["hopeful", "nurturing", "encouraging", "warm"],
                "emotion_sensitivity": 0.8,
                "transition_style": "warm",
            },
        }

        # 감정 전이 규칙
        self.transition_rules = {
            "natural_flows": {
                "sadness": ["melancholic", "contemplative", "calm"],
                "anger": ["frustration", "determination", "focused"],
                "joy": ["contentment", "excitement", "love"],
                "fear": ["anxiety", "cautious", "alert"],
            },
            "signature_preferences": {
                "selene": {"sadness": 0.9, "melancholic": 0.8, "gentle": 0.8},
                "factbomb": {"focused": 0.9, "determined": 0.8, "analytical": 0.9},
                "lune": {"dreamy": 0.9, "nostalgic": 0.8, "poetic": 0.7},
                "aurora": {"hopeful": 0.9, "nurturing": 0.8, "encouraging": 0.8},
            },
        }

        # 감정 히트맵 데이터
        self.emotion_heatmap = {}
        self.signature_activity_map = {}

        print("🌊 Real-time Emotion Flow Mapper 초기화 완료")

    def start_monitoring(self, callbacks: List[Callable] = None):
        """실시간 감정 모니터링 시작"""
        if self.monitoring:
            print("⚠️ 이미 감정 모니터링이 실행 중입니다.")
            return

        self.monitoring = True
        self.flow_callbacks = callbacks or []

        # 모니터링 스레드 시작
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        print("🌊 실시간 감정 흐름 모니터링 시작...")

    def stop_monitoring(self):
        """감정 모니터링 정지"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        print("🌊 감정 흐름 모니터링 정지")

    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring:
            try:
                # 감정 큐에서 새 감정 상태 처리
                self._process_emotion_queue()

                # 현재 감정 흐름 분석
                flow_snapshot = self._analyze_current_flow()

                # 콜백 함수들 호출
                for callback in self.flow_callbacks:
                    try:
                        callback(flow_snapshot)
                    except Exception as e:
                        self.logger.error(f"감정 흐름 콜백 오류: {e}")

                # 감정 히트맵 업데이트
                self._update_emotion_heatmap(flow_snapshot)

                time.sleep(self.update_interval)

            except Exception as e:
                self.logger.error(f"감정 모니터링 루프 오류: {e}")
                time.sleep(1)

    def add_emotion_event(
        self,
        emotion_type: str,
        intensity: float,
        source: str = "user_input",
        signature_context: str = "unknown",
        triggers: List[str] = None,
    ):
        """감정 이벤트 추가"""
        emotion_state = EmotionState(
            timestamp=datetime.now(),
            emotion_type=emotion_type,
            intensity=intensity,
            source=source,
            signature_context=signature_context,
            triggers=triggers or [],
            duration_ms=int(time.time() * 1000),
        )

        self.emotion_queue.put(emotion_state)

        # Echo Brain Monitor 연동
        if get_brain_monitor:
            try:
                update_echo_brain_emotion(emotion_type, intensity)
            except Exception as e:
                self.logger.warning(f"Echo Brain Monitor 업데이트 실패: {e}")

    def _process_emotion_queue(self):
        """감정 큐 처리"""
        processed_count = 0
        while not self.emotion_queue.empty() and processed_count < 10:
            try:
                emotion_state = self.emotion_queue.get_nowait()
                self._process_emotion_state(emotion_state)
                processed_count += 1
            except queue.Empty:
                break

    def _process_emotion_state(self, emotion_state: EmotionState):
        """감정 상태 처리"""
        # 감정 히스토리에 추가
        self.emotion_history.append(emotion_state)

        # 이전 감정과의 전이 분석
        if len(self.emotion_history) >= 2:
            previous_emotion = self.emotion_history[-2]
            transition = self._analyze_transition(previous_emotion, emotion_state)
            if transition:
                self.transition_history.append(transition)

        # 현재 감정 상태 업데이트
        self._update_current_emotions(emotion_state)

        # 감정 속도 계산
        self._calculate_emotion_velocity(emotion_state)

        # 시그니처 영향도 업데이트
        self._update_signature_influence(emotion_state)

    def _analyze_transition(
        self, from_emotion: EmotionState, to_emotion: EmotionState
    ) -> Optional[EmotionTransition]:
        """감정 전이 분석"""
        if from_emotion.emotion_type == to_emotion.emotion_type:
            return None  # 같은 감정은 전이로 보지 않음

        transition_time = (
            to_emotion.timestamp - from_emotion.timestamp
        ).total_seconds()
        intensity_change = to_emotion.intensity - from_emotion.intensity

        # 전이 부드러움 점수 계산
        smoothness_score = self._calculate_transition_smoothness(
            from_emotion.emotion_type,
            to_emotion.emotion_type,
            transition_time,
            intensity_change,
        )

        return EmotionTransition(
            from_emotion=from_emotion.emotion_type,
            to_emotion=to_emotion.emotion_type,
            transition_time=transition_time,
            intensity_change=intensity_change,
            trigger_event=to_emotion.source,
            signature_involved=to_emotion.signature_context,
            smoothness_score=smoothness_score,
        )

    def _calculate_transition_smoothness(
        self,
        from_emotion: str,
        to_emotion: str,
        transition_time: float,
        intensity_change: float,
    ) -> float:
        """전이 부드러움 점수 계산"""
        # 자연스러운 감정 흐름 확인
        natural_flows = self.transition_rules.get("natural_flows", {})
        if from_emotion in natural_flows and to_emotion in natural_flows[from_emotion]:
            natural_score = 0.8
        else:
            natural_score = 0.4

        # 전이 시간 점수 (너무 빠르거나 느리면 부자연스러움)
        optimal_time = 2.0  # 2초가 최적
        time_score = max(0.0, 1.0 - abs(transition_time - optimal_time) / 5.0)

        # 강도 변화 점수 (급격한 변화는 부자연스러움)
        intensity_score = max(0.0, 1.0 - abs(intensity_change) * 0.5)

        return natural_score * 0.5 + time_score * 0.3 + intensity_score * 0.2

    def _update_current_emotions(self, emotion_state: EmotionState):
        """현재 감정 상태 업데이트"""
        # 감정 감쇠 적용 (시간이 지나면 감정 강도 감소)
        current_time = emotion_state.timestamp
        decay_rate = 0.1  # 초당 10% 감쇠

        # 기존 감정들 감쇠
        for emotion_type in list(self.current_emotions.keys()):
            if emotion_type != emotion_state.emotion_type:
                # 감쇠 적용
                self.current_emotions[emotion_type] *= (
                    1.0 - decay_rate * self.update_interval
                )

                # 너무 약해진 감정 제거
                if self.current_emotions[emotion_type] < 0.05:
                    del self.current_emotions[emotion_type]

        # 새 감정 추가/업데이트
        self.current_emotions[emotion_state.emotion_type] = emotion_state.intensity

    def _calculate_emotion_velocity(self, emotion_state: EmotionState):
        """감정 변화 속도 계산"""
        if len(self.emotion_history) < 2:
            return

        previous_state = self.emotion_history[-2]
        time_diff = (emotion_state.timestamp - previous_state.timestamp).total_seconds()

        if time_diff > 0:
            # 이전 상태에서 같은 감정의 강도
            prev_intensity = 0.0
            if (
                hasattr(previous_state, "emotion_type")
                and previous_state.emotion_type == emotion_state.emotion_type
            ):
                prev_intensity = previous_state.intensity

            # 속도 계산 (강도 변화 / 시간)
            velocity = (emotion_state.intensity - prev_intensity) / time_diff
            self.emotion_velocity[emotion_state.emotion_type] = velocity

    def _update_signature_influence(self, emotion_state: EmotionState):
        """시그니처 영향도 업데이트"""
        signature = emotion_state.signature_context
        if signature == "unknown":
            return

        if signature not in self.signature_activity_map:
            self.signature_activity_map[signature] = {
                "emotion_activations": {},
                "total_activations": 0,
                "last_activation": emotion_state.timestamp,
            }

        # 시그니처의 감정 활성화 기록
        sig_map = self.signature_activity_map[signature]
        emotion_type = emotion_state.emotion_type

        if emotion_type not in sig_map["emotion_activations"]:
            sig_map["emotion_activations"][emotion_type] = 0

        sig_map["emotion_activations"][emotion_type] += emotion_state.intensity
        sig_map["total_activations"] += 1
        sig_map["last_activation"] = emotion_state.timestamp

    def _analyze_current_flow(self) -> EmotionFlowSnapshot:
        """현재 감정 흐름 분석"""
        timestamp = datetime.now()

        # 지배적 감정 결정
        dominant_emotion = "neutral"
        if self.current_emotions:
            dominant_emotion = max(self.current_emotions.items(), key=lambda x: x[1])[0]

        # 흐름 안정성 계산
        flow_stability = self._calculate_flow_stability()

        # 시그니처 영향도 계산
        signature_influence = self._calculate_signature_influence()

        return EmotionFlowSnapshot(
            timestamp=timestamp,
            active_emotions=self.current_emotions.copy(),
            dominant_emotion=dominant_emotion,
            emotion_velocity=self.emotion_velocity.copy(),
            signature_influence=signature_influence,
            flow_stability=flow_stability,
        )

    def _calculate_flow_stability(self) -> float:
        """감정 흐름 안정성 계산"""
        if len(self.transition_history) < 3:
            return 0.8  # 기본 안정성

        # 최근 전이들의 부드러움 점수 평균
        recent_transitions = list(self.transition_history)[-5:]
        smoothness_scores = [t.smoothness_score for t in recent_transitions]

        return sum(smoothness_scores) / len(smoothness_scores)

    def _calculate_signature_influence(self) -> Dict[str, float]:
        """시그니처 영향도 계산"""
        influence = {}
        total_activations = sum(
            sig_data["total_activations"]
            for sig_data in self.signature_activity_map.values()
        )

        if total_activations == 0:
            return influence

        for signature, sig_data in self.signature_activity_map.items():
            # 최근 활성화 가중치
            time_weight = self._calculate_time_weight(sig_data["last_activation"])

            # 활성화 비율
            activation_ratio = sig_data["total_activations"] / total_activations

            influence[signature] = activation_ratio * time_weight

        return influence

    def _calculate_time_weight(self, last_activation: datetime) -> float:
        """시간 가중치 계산 (최근일수록 높은 가중치)"""
        time_diff = (datetime.now() - last_activation).total_seconds()
        # 10분 이내면 최대 가중치, 그 이후 지수적 감소
        return max(0.1, np.exp(-time_diff / 600))

    def _update_emotion_heatmap(self, flow_snapshot: EmotionFlowSnapshot):
        """감정 히트맵 업데이트"""
        timestamp_key = flow_snapshot.timestamp.strftime("%Y%m%d_%H%M")

        if timestamp_key not in self.emotion_heatmap:
            self.emotion_heatmap[timestamp_key] = {}

        # 현재 감정들을 히트맵에 누적
        for emotion, intensity in flow_snapshot.active_emotions.items():
            if emotion not in self.emotion_heatmap[timestamp_key]:
                self.emotion_heatmap[timestamp_key][emotion] = 0.0

            self.emotion_heatmap[timestamp_key][emotion] += intensity

        # 오래된 데이터 정리 (24시간 이상된 데이터 제거)
        cutoff_time = datetime.now() - timedelta(hours=24)
        cutoff_key = cutoff_time.strftime("%Y%m%d_%H%M")

        keys_to_remove = [
            key for key in self.emotion_heatmap.keys() if key < cutoff_key
        ]
        for key in keys_to_remove:
            del self.emotion_heatmap[key]

    def get_emotion_flow_summary(self) -> Dict[str, Any]:
        """감정 흐름 요약 반환"""
        if not self.emotion_history:
            return {"status": "no_data", "message": "감정 데이터가 없습니다."}

        # 최근 감정 분석
        recent_emotions = list(self.emotion_history)[-10:]
        emotion_counts = {}
        total_intensity = 0.0

        for emotion_state in recent_emotions:
            emotion_type = emotion_state.emotion_type
            emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1
            total_intensity += emotion_state.intensity

        # 가장 빈번한 감정
        most_frequent = (
            max(emotion_counts.items(), key=lambda x: x[1])
            if emotion_counts
            else ("neutral", 0)
        )

        # 평균 감정 강도
        avg_intensity = (
            total_intensity / len(recent_emotions) if recent_emotions else 0.0
        )

        # 전이 분석
        transition_analysis = self._analyze_transition_patterns()

        summary = {
            "status": "active",
            "current_emotions": self.current_emotions,
            "dominant_emotion": (
                max(self.current_emotions.items(), key=lambda x: x[1])[0]
                if self.current_emotions
                else "neutral"
            ),
            "most_frequent_emotion": most_frequent[0],
            "average_intensity": round(avg_intensity, 3),
            "emotion_velocity": self.emotion_velocity,
            "flow_stability": self._calculate_flow_stability(),
            "signature_influence": self._calculate_signature_influence(),
            "transition_patterns": transition_analysis,
            "total_emotion_events": len(self.emotion_history),
            "total_transitions": len(self.transition_history),
        }

        return summary

    def _analyze_transition_patterns(self) -> Dict[str, Any]:
        """전이 패턴 분석"""
        if not self.transition_history:
            return {}

        # 전이 빈도 분석
        transition_counts = {}
        smoothness_scores = []

        for transition in self.transition_history:
            key = f"{transition.from_emotion} → {transition.to_emotion}"
            transition_counts[key] = transition_counts.get(key, 0) + 1
            smoothness_scores.append(transition.smoothness_score)

        # 가장 빈번한 전이
        most_common_transition = (
            max(transition_counts.items(), key=lambda x: x[1])
            if transition_counts
            else ("없음", 0)
        )

        # 평균 전이 부드러움
        avg_smoothness = (
            sum(smoothness_scores) / len(smoothness_scores)
            if smoothness_scores
            else 0.0
        )

        return {
            "most_common_transition": most_common_transition[0],
            "transition_frequency": most_common_transition[1],
            "average_smoothness": round(avg_smoothness, 3),
            "total_unique_transitions": len(transition_counts),
        }

    def get_emotion_heatmap(self, hours: int = 1) -> Dict[str, Any]:
        """감정 히트맵 반환"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_key = cutoff_time.strftime("%Y%m%d_%H%M")

        # 지정된 시간 범위의 데이터만 필터링
        filtered_heatmap = {
            key: data for key, data in self.emotion_heatmap.items() if key >= cutoff_key
        }

        # 감정별 총합 계산
        emotion_totals = {}
        for time_data in filtered_heatmap.values():
            for emotion, intensity in time_data.items():
                emotion_totals[emotion] = emotion_totals.get(emotion, 0.0) + intensity

        return {
            "time_range_hours": hours,
            "heatmap_data": filtered_heatmap,
            "emotion_totals": emotion_totals,
            "dominant_emotion": (
                max(emotion_totals.items(), key=lambda x: x[1])[0]
                if emotion_totals
                else "neutral"
            ),
        }

    def visualize_emotion_flow(self, minutes: int = 10) -> str:
        """감정 흐름 시각화 (텍스트 기반)"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_emotions = [
            e for e in self.emotion_history if e.timestamp >= cutoff_time
        ]

        if not recent_emotions:
            return f"❌ 최근 {minutes}분간 감정 데이터가 없습니다."

        viz = f"🌊 Emotion Flow Visualization (Last {minutes} minutes)\n"
        viz += "=" * 60 + "\n\n"

        # 시간대별 감정 표시
        for emotion_state in recent_emotions[-10:]:  # 최근 10개만 표시
            time_str = emotion_state.timestamp.strftime("%H:%M:%S")
            intensity_bar = "█" * int(emotion_state.intensity * 10)

            viz += f"{time_str} | {emotion_state.emotion_type:12} | "
            viz += f"{intensity_bar:10} | {emotion_state.intensity:.2f} | "
            viz += f"{emotion_state.signature_context}\n"

        # 현재 활성 감정
        viz += "\n🎯 Current Active Emotions:\n"
        for emotion, intensity in sorted(
            self.current_emotions.items(), key=lambda x: x[1], reverse=True
        ):
            intensity_bar = "▓" * int(intensity * 20)
            viz += f"   {emotion:12} | {intensity_bar:20} | {intensity:.3f}\n"

        # 감정 속도
        if self.emotion_velocity:
            viz += "\n⚡ Emotion Velocity:\n"
            for emotion, velocity in self.emotion_velocity.items():
                direction = "↗" if velocity > 0 else "↘" if velocity < 0 else "→"
                viz += f"   {emotion:12} | {direction} {abs(velocity):.3f}/s\n"

        return viz

    def save_emotion_flow_data(self, filename: str = None) -> str:
        """감정 흐름 데이터 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"emotion_flow_data_{timestamp}.json"

        # 저장할 데이터 준비
        save_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "history_length": len(self.emotion_history),
                "transition_count": len(self.transition_history),
            },
            "emotion_history": [asdict(e) for e in self.emotion_history],
            "transition_history": [asdict(t) for t in self.transition_history],
            "current_emotions": self.current_emotions,
            "emotion_velocity": self.emotion_velocity,
            "signature_activity_map": {},
            "emotion_heatmap": self.emotion_heatmap,
        }

        # 시그니처 활동 맵 직렬화
        for signature, data in self.signature_activity_map.items():
            save_data["signature_activity_map"][signature] = {
                "emotion_activations": data["emotion_activations"],
                "total_activations": data["total_activations"],
                "last_activation": data["last_activation"].isoformat(),
            }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return f"✅ 감정 흐름 데이터 저장 완료: {filename}"
        except Exception as e:
            return f"❌ 저장 실패: {e}"


# 편의 함수들
def create_emotion_flow_mapper(**kwargs) -> RealtimeEmotionFlowMapper:
    """Emotion Flow Mapper 생성"""
    return RealtimeEmotionFlowMapper(**kwargs)


def track_emotion_event(
    emotion_type: str, intensity: float, signature: str = "unknown"
):
    """전역 감정 이벤트 추적 (싱글톤 패턴)"""
    global _global_emotion_mapper
    if "_global_emotion_mapper" not in globals():
        _global_emotion_mapper = RealtimeEmotionFlowMapper()
        _global_emotion_mapper.start_monitoring()

    _global_emotion_mapper.add_emotion_event(
        emotion_type=emotion_type, intensity=intensity, signature_context=signature
    )


if __name__ == "__main__":
    # 테스트 실행
    print("🌊 Real-time Emotion Flow Mapper 테스트...")

    mapper = RealtimeEmotionFlowMapper()

    # 모니터링 시작
    mapper.start_monitoring()

    # 테스트 감정 이벤트들 추가
    test_emotions = [
        ("sadness", 0.7, "selene"),
        ("melancholic", 0.6, "selene"),
        ("contemplative", 0.5, "selene"),
        ("analytical", 0.8, "factbomb"),
        ("focused", 0.9, "factbomb"),
        ("dreamy", 0.6, "lune"),
        ("nostalgic", 0.7, "lune"),
        ("hopeful", 0.8, "aurora"),
    ]

    print("\n🎭 감정 이벤트 시퀀스 시뮬레이션...")
    for emotion, intensity, signature in test_emotions:
        mapper.add_emotion_event(emotion, intensity, signature_context=signature)
        time.sleep(0.5)  # 0.5초 간격으로 감정 이벤트 발생
        print(f"   {signature}: {emotion} ({intensity})")

    # 잠시 대기 후 분석
    time.sleep(2)

    # 결과 출력
    print("\n" + "=" * 60)
    print(mapper.visualize_emotion_flow(minutes=1))

    # 요약 정보
    summary = mapper.get_emotion_flow_summary()
    print(f"\n📊 Flow Summary:")
    print(f"   Dominant Emotion: {summary['dominant_emotion']}")
    print(f"   Flow Stability: {summary['flow_stability']:.3f}")
    print(f"   Total Events: {summary['total_emotion_events']}")

    # 히트맵
    heatmap = mapper.get_emotion_heatmap(hours=1)
    print(f"\n🔥 Emotion Heatmap:")
    for emotion, total in sorted(
        heatmap["emotion_totals"].items(), key=lambda x: x[1], reverse=True
    ):
        print(f"   {emotion:12}: {total:.2f}")

    # 저장
    save_result = mapper.save_emotion_flow_data()
    print(f"\n{save_result}")

    # 모니터링 정지
    mapper.stop_monitoring()

    print("\n✅ Real-time Emotion Flow Mapper 테스트 완료!")
