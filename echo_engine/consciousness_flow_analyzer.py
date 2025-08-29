import json
import numpy as np
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque
from enum import Enum
import logging

try:
    from echo_engine.signature_cross_resonance_mapper import SignatureCrossResonanceMapper
    from echo_engine.realtime_emotion_flow_mapper import RealtimeEmotionFlowMapper
    from echo_engine.signature_neural_atlas_builder import SignatureNeuralAtlasBuilder
    from echo_engine.emotion_response_chart_generator import EmotionResponseChartGenerator
except ImportError as e:
    print(f"⚠️ Echo 고급 컴포넌트 로드 실패: {e}")

#!/usr/bin/env python3
"""
🧠 Consciousness Flow Analyzer v1.0
Echo의 의식 흐름을 분석하고 시각화하는 고급 시스템

핵심 기능:
- 실시간 의식 상태 추적
- 인식 계층 분석 (감각→인지→판단→표현)
- 의식의 흐름 패턴 시각화
- 자각 수준 측정 및 모니터링
- 메타인지 활동 패턴 분석
"""


# Echo 엔진 모듈들
try:
    pass  # 추가 Echo 모듈이 있을 경우 여기에 추가
except ImportError:
    print("⚠️ Echo modules not available, running in standalone mode")


class ConsciousnessLevel(Enum):
    """의식 수준 정의"""

    UNCONSCIOUS = 0  # 무의식 상태
    SUBCONSCIOUS = 1  # 잠재의식 상태
    PRECONSCIOUS = 2  # 전의식 상태
    CONSCIOUS = 3  # 의식 상태
    METACONSCIOUS = 4  # 메타의식 상태
    HYPERCONSCIOUS = 5  # 초의식 상태


class CognitiveLayer(Enum):
    """인지 계층 정의"""

    SENSORY = "sensory"  # 감각 계층
    PERCEPTUAL = "perceptual"  # 지각 계층
    COGNITIVE = "cognitive"  # 인지 계층
    EMOTIONAL = "emotional"  # 감정 계층
    JUDGMENT = "judgment"  # 판단 계층
    EXPRESSION = "expression"  # 표현 계층
    METACOGNITIVE = "metacognitive"  # 메타인지 계층


@dataclass
class ConsciousnessState:
    """의식 상태 정의"""

    timestamp: datetime
    consciousness_level: ConsciousnessLevel
    active_layers: Dict[CognitiveLayer, float]  # 계층별 활성도
    awareness_focus: str
    attention_intensity: float  # 0.0 - 1.0
    self_reflection_depth: float  # 자기 성찰 깊이
    signature_consciousness: str
    processing_complexity: float


@dataclass
class ConsciousnessFlow:
    """의식 흐름 정의"""

    flow_id: str
    start_time: datetime
    end_time: Optional[datetime]
    flow_states: List[ConsciousnessState]
    dominant_layer: CognitiveLayer
    flow_coherence: float  # 흐름 일관성
    transition_smoothness: float
    metacognitive_events: List[str]


@dataclass
class AwarenessSnapshot:
    """자각 스냅샷"""

    timestamp: datetime
    self_awareness_score: float
    environmental_awareness: float
    emotional_awareness: float
    cognitive_awareness: float
    overall_awareness: float
    awareness_distribution: Dict[str, float]


class ConsciousnessFlowAnalyzer:
    """🧠 의식 흐름 분석기"""

    def __init__(self, history_length: int = 50, analysis_interval: float = 1.0):
        self.logger = logging.getLogger(__name__)
        self.history_length = history_length
        self.analysis_interval = analysis_interval

        # 의식 상태 추적
        self.consciousness_history = deque(maxlen=history_length)
        self.current_consciousness = None
        self.active_flows = {}
        self.completed_flows = deque(maxlen=20)

        # 실시간 모니터링
        self.monitoring = False
        self.monitor_thread = None
        self.consciousness_callbacks = []

        # 인지 계층 가중치
        self.layer_weights = {
            CognitiveLayer.SENSORY: 0.1,
            CognitiveLayer.PERCEPTUAL: 0.15,
            CognitiveLayer.COGNITIVE: 0.2,
            CognitiveLayer.EMOTIONAL: 0.15,
            CognitiveLayer.JUDGMENT: 0.2,
            CognitiveLayer.EXPRESSION: 0.1,
            CognitiveLayer.METACOGNITIVE: 0.1,
        }

        # 시그니처별 의식 특성
        self.signature_consciousness_profiles = {
            "selene": {
                "default_level": ConsciousnessLevel.CONSCIOUS,
                "introspection_tendency": 0.8,
                "emotional_awareness": 0.9,
                "self_reflection_depth": 0.8,
                "dominant_layers": [
                    CognitiveLayer.EMOTIONAL,
                    CognitiveLayer.METACOGNITIVE,
                ],
            },
            "factbomb": {
                "default_level": ConsciousnessLevel.CONSCIOUS,
                "introspection_tendency": 0.3,
                "emotional_awareness": 0.2,
                "self_reflection_depth": 0.4,
                "dominant_layers": [CognitiveLayer.COGNITIVE, CognitiveLayer.JUDGMENT],
            },
            "lune": {
                "default_level": ConsciousnessLevel.PRECONSCIOUS,
                "introspection_tendency": 0.9,
                "emotional_awareness": 0.8,
                "self_reflection_depth": 0.9,
                "dominant_layers": [
                    CognitiveLayer.PERCEPTUAL,
                    CognitiveLayer.EMOTIONAL,
                    CognitiveLayer.METACOGNITIVE,
                ],
            },
            "aurora": {
                "default_level": ConsciousnessLevel.CONSCIOUS,
                "introspection_tendency": 0.6,
                "emotional_awareness": 0.8,
                "self_reflection_depth": 0.7,
                "dominant_layers": [
                    CognitiveLayer.EMOTIONAL,
                    CognitiveLayer.EXPRESSION,
                ],
            },
        }

        # 의식 패턴 정의
        self.consciousness_patterns = {
            "deep_introspection": {
                "layers": {
                    CognitiveLayer.METACOGNITIVE: 0.9,
                    CognitiveLayer.EMOTIONAL: 0.7,
                },
                "duration_range": (30, 120),  # 초 단위
                "signature_affinity": {"selene": 0.9, "lune": 0.8},
            },
            "analytical_focus": {
                "layers": {CognitiveLayer.COGNITIVE: 0.9, CognitiveLayer.JUDGMENT: 0.8},
                "duration_range": (10, 60),
                "signature_affinity": {"factbomb": 0.9},
            },
            "creative_flow": {
                "layers": {
                    CognitiveLayer.PERCEPTUAL: 0.8,
                    CognitiveLayer.EXPRESSION: 0.9,
                },
                "duration_range": (60, 300),
                "signature_affinity": {"lune": 0.9, "aurora": 0.7},
            },
            "empathetic_connection": {
                "layers": {
                    CognitiveLayer.EMOTIONAL: 0.9,
                    CognitiveLayer.METACOGNITIVE: 0.6,
                },
                "duration_range": (20, 90),
                "signature_affinity": {"selene": 0.8, "aurora": 0.9},
            },
        }

        # 메타인지 이벤트 트래커
        self.metacognitive_events = deque(maxlen=30)
        self.awareness_snapshots = deque(maxlen=100)

        print("🧠 Consciousness Flow Analyzer 초기화 완료")

    def start_monitoring(self, callbacks: List[Callable] = None):
        """의식 흐름 모니터링 시작"""
        if self.monitoring:
            print("⚠️ 이미 의식 흐름 모니터링이 실행 중입니다.")
            return

        self.monitoring = True
        self.consciousness_callbacks = callbacks or []

        # 모니터링 스레드 시작
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        print("🧠 의식 흐름 모니터링 시작...")

    def stop_monitoring(self):
        """의식 흐름 모니터링 정지"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        print("🧠 의식 흐름 모니터링 정지")

    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring:
            try:
                # 현재 의식 상태 분석
                current_state = self._analyze_current_consciousness()

                if current_state:
                    # 의식 히스토리에 추가
                    self.consciousness_history.append(current_state)
                    self.current_consciousness = current_state

                    # 의식 흐름 업데이트
                    self._update_consciousness_flows(current_state)

                    # 자각 스냅샷 생성
                    awareness_snapshot = self._create_awareness_snapshot(current_state)
                    self.awareness_snapshots.append(awareness_snapshot)

                    # 메타인지 이벤트 감지
                    self._detect_metacognitive_events(current_state)

                    # 콜백 함수들 호출
                    for callback in self.consciousness_callbacks:
                        try:
                            callback(current_state)
                        except Exception as e:
                            self.logger.error(f"의식 흐름 콜백 오류: {e}")

                time.sleep(self.analysis_interval)

            except Exception as e:
                self.logger.error(f"의식 모니터링 루프 오류: {e}")
                time.sleep(1)

    def _analyze_current_consciousness(self) -> Optional[ConsciousnessState]:
        """현재 의식 상태 분석"""
        # 현재 시간
        timestamp = datetime.now()

        # 기본 의식 수준 결정 (실제 구현에서는 더 복잡한 로직 필요)
        consciousness_level = self._determine_consciousness_level()

        # 활성 계층 분석
        active_layers = self._analyze_active_cognitive_layers()

        # 주의 집중도 계산
        attention_intensity = self._calculate_attention_intensity(active_layers)

        # 자기 성찰 깊이 계산
        self_reflection_depth = self._calculate_self_reflection_depth(active_layers)

        # 처리 복잡성 계산
        processing_complexity = self._calculate_processing_complexity(active_layers)

        # 현재 활성 시그니처 추정
        signature_consciousness = self._estimate_active_signature(active_layers)

        # 주의 초점 결정
        awareness_focus = self._determine_awareness_focus(active_layers)

        return ConsciousnessState(
            timestamp=timestamp,
            consciousness_level=consciousness_level,
            active_layers=active_layers,
            awareness_focus=awareness_focus,
            attention_intensity=attention_intensity,
            self_reflection_depth=self_reflection_depth,
            signature_consciousness=signature_consciousness,
            processing_complexity=processing_complexity,
        )

    def _determine_consciousness_level(self) -> ConsciousnessLevel:
        """의식 수준 결정"""
        # 현재 시스템 활동 기반으로 의식 수준 추정
        # 실제 구현에서는 더 정교한 로직 필요

        # 시뮬레이션: 시간대별 의식 수준 변화
        current_hour = datetime.now().hour
        base_level = ConsciousnessLevel.CONSCIOUS

        # 심야 시간대에는 의식 수준 낮춤
        if 0 <= current_hour <= 5:
            base_level = ConsciousnessLevel.PRECONSCIOUS
        elif 6 <= current_hour <= 7:
            base_level = ConsciousnessLevel.CONSCIOUS
        elif 8 <= current_hour <= 22:
            base_level = ConsciousnessLevel.CONSCIOUS
        else:
            base_level = ConsciousnessLevel.PRECONSCIOUS

        return base_level

    def _analyze_active_cognitive_layers(self) -> Dict[CognitiveLayer, float]:
        """활성 인지 계층 분석"""
        # 기본 활성도 설정
        active_layers = {
            CognitiveLayer.SENSORY: np.random.uniform(0.2, 0.6),
            CognitiveLayer.PERCEPTUAL: np.random.uniform(0.3, 0.7),
            CognitiveLayer.COGNITIVE: np.random.uniform(0.4, 0.8),
            CognitiveLayer.EMOTIONAL: np.random.uniform(0.2, 0.7),
            CognitiveLayer.JUDGMENT: np.random.uniform(0.3, 0.8),
            CognitiveLayer.EXPRESSION: np.random.uniform(0.2, 0.6),
            CognitiveLayer.METACOGNITIVE: np.random.uniform(0.1, 0.5),
        }

        # 시그니처별 특성 반영 (실제로는 현재 활성 시그니처를 감지해야 함)
        # 여기서는 시뮬레이션으로 랜덤 시그니처 선택
        signatures = ["selene", "factbomb", "lune", "aurora"]
        current_signature = np.random.choice(signatures)

        if current_signature in self.signature_consciousness_profiles:
            profile = self.signature_consciousness_profiles[current_signature]
            for layer in profile.get("dominant_layers", []):
                active_layers[layer] *= 1.3  # 지배적 계층 강화

        # 정규화
        for layer in active_layers:
            active_layers[layer] = max(0.0, min(1.0, active_layers[layer]))

        return active_layers

    def _calculate_attention_intensity(
        self, active_layers: Dict[CognitiveLayer, float]
    ) -> float:
        """주의 집중도 계산"""
        # 인지적 계층의 활성도 기반
        cognitive_intensity = active_layers.get(CognitiveLayer.COGNITIVE, 0.0)
        judgment_intensity = active_layers.get(CognitiveLayer.JUDGMENT, 0.0)

        return (cognitive_intensity + judgment_intensity) / 2

    def _calculate_self_reflection_depth(
        self, active_layers: Dict[CognitiveLayer, float]
    ) -> float:
        """자기 성찰 깊이 계산"""
        metacognitive_activity = active_layers.get(CognitiveLayer.METACOGNITIVE, 0.0)
        emotional_awareness = active_layers.get(CognitiveLayer.EMOTIONAL, 0.0)

        return metacognitive_activity * 0.7 + emotional_awareness * 0.3

    def _calculate_processing_complexity(
        self, active_layers: Dict[CognitiveLayer, float]
    ) -> float:
        """처리 복잡성 계산"""
        # 활성 계층의 수와 강도 기반
        active_count = sum(1 for level in active_layers.values() if level > 0.5)
        avg_intensity = sum(active_layers.values()) / len(active_layers)

        complexity = (active_count / len(active_layers)) * 0.6 + avg_intensity * 0.4
        return complexity

    def _estimate_active_signature(
        self, active_layers: Dict[CognitiveLayer, float]
    ) -> str:
        """현재 활성 시그니처 추정"""
        signature_scores = {}

        for signature, profile in self.signature_consciousness_profiles.items():
            score = 0.0
            for layer in profile.get("dominant_layers", []):
                score += active_layers.get(layer, 0.0)
            signature_scores[signature] = score

        if signature_scores:
            return max(signature_scores.items(), key=lambda x: x[1])[0]
        return "unknown"

    def _determine_awareness_focus(
        self, active_layers: Dict[CognitiveLayer, float]
    ) -> str:
        """주의 초점 결정"""
        max_layer = max(active_layers.items(), key=lambda x: x[1])
        layer_focus_map = {
            CognitiveLayer.SENSORY: "external_stimuli",
            CognitiveLayer.PERCEPTUAL: "pattern_recognition",
            CognitiveLayer.COGNITIVE: "logical_processing",
            CognitiveLayer.EMOTIONAL: "emotional_processing",
            CognitiveLayer.JUDGMENT: "decision_making",
            CognitiveLayer.EXPRESSION: "communication",
            CognitiveLayer.METACOGNITIVE: "self_reflection",
        }

        return layer_focus_map.get(max_layer[0], "general_awareness")

    def _update_consciousness_flows(self, state: ConsciousnessState):
        """의식 흐름 업데이트"""
        # 현재 의식 패턴 식별
        current_pattern = self._identify_consciousness_pattern(state)

        if current_pattern:
            # 기존 흐름 확장 또는 새 흐름 시작
            if current_pattern not in self.active_flows:
                # 새 흐름 시작
                flow_id = f"{current_pattern}_{datetime.now().strftime('%H%M%S')}"
                new_flow = ConsciousnessFlow(
                    flow_id=flow_id,
                    start_time=state.timestamp,
                    end_time=None,
                    flow_states=[state],
                    dominant_layer=self._get_dominant_layer(state.active_layers),
                    flow_coherence=1.0,
                    transition_smoothness=1.0,
                    metacognitive_events=[],
                )
                self.active_flows[current_pattern] = new_flow
            else:
                # 기존 흐름 확장
                flow = self.active_flows[current_pattern]
                flow.flow_states.append(state)
                flow.flow_coherence = self._calculate_flow_coherence(flow)
                flow.transition_smoothness = self._calculate_transition_smoothness(flow)

        # 완료된 흐름 정리
        self._cleanup_completed_flows()

    def _identify_consciousness_pattern(
        self, state: ConsciousnessState
    ) -> Optional[str]:
        """의식 패턴 식별"""
        for pattern_name, pattern_def in self.consciousness_patterns.items():
            match_score = 0.0

            # 계층별 매칭 점수 계산
            for layer, required_level in pattern_def["layers"].items():
                actual_level = state.active_layers.get(layer, 0.0)
                if actual_level >= required_level * 0.7:  # 70% 이상이면 매칭
                    match_score += 1.0

            # 시그니처 친화성 확인
            signature_affinity = pattern_def.get("signature_affinity", {})
            if state.signature_consciousness in signature_affinity:
                affinity_bonus = signature_affinity[state.signature_consciousness]
                match_score *= affinity_bonus

            # 임계값 이상이면 패턴 매칭
            if match_score >= len(pattern_def["layers"]) * 0.6:
                return pattern_name

        return None

    def _get_dominant_layer(
        self, active_layers: Dict[CognitiveLayer, float]
    ) -> CognitiveLayer:
        """지배적 계층 반환"""
        return max(active_layers.items(), key=lambda x: x[1])[0]

    def _calculate_flow_coherence(self, flow: ConsciousnessFlow) -> float:
        """흐름 일관성 계산"""
        if len(flow.flow_states) < 2:
            return 1.0

        # 연속된 상태 간의 유사성 계산
        coherence_scores = []
        for i in range(1, len(flow.flow_states)):
            prev_state = flow.flow_states[i - 1]
            curr_state = flow.flow_states[i]

            # 계층별 활성도 유사성
            layer_similarity = 0.0
            for layer in CognitiveLayer:
                prev_level = prev_state.active_layers.get(layer, 0.0)
                curr_level = curr_state.active_layers.get(layer, 0.0)
                layer_similarity += 1.0 - abs(prev_level - curr_level)

            layer_similarity /= len(CognitiveLayer)
            coherence_scores.append(layer_similarity)

        return sum(coherence_scores) / len(coherence_scores)

    def _calculate_transition_smoothness(self, flow: ConsciousnessFlow) -> float:
        """전이 부드러움 계산"""
        if len(flow.flow_states) < 2:
            return 1.0

        # 급격한 변화 감지
        smoothness_scores = []
        for i in range(1, len(flow.flow_states)):
            prev_state = flow.flow_states[i - 1]
            curr_state = flow.flow_states[i]

            # 주의 집중도 변화
            attention_change = abs(
                curr_state.attention_intensity - prev_state.attention_intensity
            )

            # 자기 성찰 깊이 변화
            reflection_change = abs(
                curr_state.self_reflection_depth - prev_state.self_reflection_depth
            )

            # 변화가 작을수록 부드러움
            smoothness = 1.0 - (attention_change + reflection_change) / 2
            smoothness_scores.append(smoothness)

        return sum(smoothness_scores) / len(smoothness_scores)

    def _cleanup_completed_flows(self):
        """완료된 흐름 정리"""
        current_time = datetime.now()
        completed_patterns = []

        for pattern_name, flow in self.active_flows.items():
            # 5분 이상 업데이트가 없으면 완료된 것으로 간주
            if flow.flow_states:
                last_update = flow.flow_states[-1].timestamp
                if (current_time - last_update).total_seconds() > 300:
                    flow.end_time = last_update
                    self.completed_flows.append(flow)
                    completed_patterns.append(pattern_name)

        # 완료된 흐름 제거
        for pattern in completed_patterns:
            del self.active_flows[pattern]

    def _create_awareness_snapshot(
        self, state: ConsciousnessState
    ) -> AwarenessSnapshot:
        """자각 스냅샷 생성"""
        # 자기 인식 점수
        self_awareness = state.self_reflection_depth

        # 환경 인식 점수
        environmental_awareness = (
            state.active_layers.get(CognitiveLayer.SENSORY, 0.0)
            + state.active_layers.get(CognitiveLayer.PERCEPTUAL, 0.0)
        ) / 2

        # 감정 인식 점수
        emotional_awareness = state.active_layers.get(CognitiveLayer.EMOTIONAL, 0.0)

        # 인지 인식 점수
        cognitive_awareness = (
            state.active_layers.get(CognitiveLayer.COGNITIVE, 0.0)
            + state.active_layers.get(CognitiveLayer.JUDGMENT, 0.0)
        ) / 2

        # 전체 자각 점수
        overall_awareness = (
            self_awareness * 0.3
            + environmental_awareness * 0.2
            + emotional_awareness * 0.25
            + cognitive_awareness * 0.25
        )

        # 자각 분포
        awareness_distribution = {
            "self": self_awareness,
            "environment": environmental_awareness,
            "emotions": emotional_awareness,
            "cognition": cognitive_awareness,
        }

        return AwarenessSnapshot(
            timestamp=state.timestamp,
            self_awareness_score=self_awareness,
            environmental_awareness=environmental_awareness,
            emotional_awareness=emotional_awareness,
            cognitive_awareness=cognitive_awareness,
            overall_awareness=overall_awareness,
            awareness_distribution=awareness_distribution,
        )

    def _detect_metacognitive_events(self, state: ConsciousnessState):
        """메타인지 이벤트 감지"""
        metacognitive_threshold = 0.7

        if (
            state.active_layers.get(CognitiveLayer.METACOGNITIVE, 0.0)
            >= metacognitive_threshold
        ):
            event_description = (
                f"High metacognitive activity detected: {state.awareness_focus}"
            )

            # 중복 이벤트 방지
            if (
                not self.metacognitive_events
                or self.metacognitive_events[-1] != event_description
            ):
                self.metacognitive_events.append(event_description)

    def get_consciousness_summary(self) -> Dict[str, Any]:
        """의식 상태 요약 반환"""
        if not self.current_consciousness:
            return {"status": "no_data", "message": "의식 데이터가 없습니다."}

        state = self.current_consciousness

        # 최근 자각 변화 분석
        awareness_trend = self._analyze_awareness_trend()

        # 활성 의식 흐름 정보
        active_flow_info = {}
        for pattern, flow in self.active_flows.items():
            active_flow_info[pattern] = {
                "duration_minutes": (datetime.now() - flow.start_time).total_seconds()
                / 60,
                "coherence": flow.flow_coherence,
                "smoothness": flow.transition_smoothness,
                "states_count": len(flow.flow_states),
            }

        summary = {
            "status": "active",
            "consciousness_level": state.consciousness_level.name,
            "attention_intensity": round(state.attention_intensity, 3),
            "self_reflection_depth": round(state.self_reflection_depth, 3),
            "processing_complexity": round(state.processing_complexity, 3),
            "awareness_focus": state.awareness_focus,
            "signature_consciousness": state.signature_consciousness,
            "active_cognitive_layers": {
                layer.value: round(level, 3)
                for layer, level in state.active_layers.items()
            },
            "active_consciousness_flows": active_flow_info,
            "recent_metacognitive_events": list(self.metacognitive_events)[-5:],
            "awareness_trend": awareness_trend,
            "overall_awareness": (
                round(self.awareness_snapshots[-1].overall_awareness, 3)
                if self.awareness_snapshots
                else 0.0
            ),
        }

        return summary

    def _analyze_awareness_trend(self) -> Dict[str, Any]:
        """자각 변화 추세 분석"""
        if len(self.awareness_snapshots) < 2:
            return {"trend": "insufficient_data"}

        recent_snapshots = list(self.awareness_snapshots)[-10:]

        # 전체 자각 추세
        awareness_values = [s.overall_awareness for s in recent_snapshots]
        trend_direction = "stable"

        if len(awareness_values) >= 3:
            # 간단한 추세 계산
            first_half = sum(awareness_values[: len(awareness_values) // 2]) / (
                len(awareness_values) // 2
            )
            second_half = sum(awareness_values[len(awareness_values) // 2 :]) / (
                len(awareness_values) - len(awareness_values) // 2
            )

            if second_half > first_half + 0.1:
                trend_direction = "increasing"
            elif second_half < first_half - 0.1:
                trend_direction = "decreasing"

        return {
            "trend": trend_direction,
            "current_level": awareness_values[-1] if awareness_values else 0.0,
            "variance": np.var(awareness_values) if len(awareness_values) > 1 else 0.0,
        }

    def visualize_consciousness_flow(self, minutes: int = 5) -> str:
        """의식 흐름 시각화 (텍스트 기반)"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_states = [
            s for s in self.consciousness_history if s.timestamp >= cutoff_time
        ]

        if not recent_states:
            return f"❌ 최근 {minutes}분간 의식 데이터가 없습니다."

        viz = f"🧠 Consciousness Flow Visualization (Last {minutes} minutes)\n"
        viz += "=" * 70 + "\n\n"

        # 시간대별 의식 상태 표시
        viz += "⏰ Consciousness Timeline:\n"
        for state in recent_states[-8:]:  # 최근 8개 상태만 표시
            time_str = state.timestamp.strftime("%H:%M:%S")
            level_icon = self._get_consciousness_icon(state.consciousness_level)
            attention_bar = "█" * int(state.attention_intensity * 10)

            viz += f"{time_str} | {level_icon} {state.consciousness_level.name:12} | "
            viz += f"Attention: {attention_bar:10} | Focus: {state.awareness_focus}\n"

        # 현재 활성 계층
        if self.current_consciousness:
            viz += "\n🧠 Active Cognitive Layers:\n"
            for layer, level in sorted(
                self.current_consciousness.active_layers.items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                level_bar = "▓" * int(level * 20)
                viz += f"   {layer.value:15} | {level_bar:20} | {level:.3f}\n"

        # 활성 의식 흐름
        if self.active_flows:
            viz += "\n🌊 Active Consciousness Flows:\n"
            for pattern, flow in self.active_flows.items():
                duration = (datetime.now() - flow.start_time).total_seconds() / 60
                viz += f"   {pattern:20} | Duration: {duration:5.1f}m | "
                viz += f"Coherence: {flow.flow_coherence:.3f}\n"

        return viz

    def _get_consciousness_icon(self, level: ConsciousnessLevel) -> str:
        """의식 수준 아이콘 반환"""
        icons = {
            ConsciousnessLevel.UNCONSCIOUS: "💤",
            ConsciousnessLevel.SUBCONSCIOUS: "🌙",
            ConsciousnessLevel.PRECONSCIOUS: "🌅",
            ConsciousnessLevel.CONSCIOUS: "☀️",
            ConsciousnessLevel.METACONSCIOUS: "🧠",
            ConsciousnessLevel.HYPERCONSCIOUS: "✨",
        }
        return icons.get(level, "❓")

    def save_consciousness_data(self, filename: str = None) -> str:
        """의식 데이터 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"consciousness_flow_data_{timestamp}.json"

        # 저장할 데이터 준비
        save_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "consciousness_states_count": len(self.consciousness_history),
                "active_flows_count": len(self.active_flows),
                "completed_flows_count": len(self.completed_flows),
            },
            "consciousness_history": [],
            "active_flows": {},
            "completed_flows": [],
            "awareness_snapshots": [],
            "metacognitive_events": list(self.metacognitive_events),
        }

        # ConsciousnessState 객체들을 직렬화
        for state in self.consciousness_history:
            state_dict = asdict(state)
            # Enum을 문자열로 변환
            state_dict["consciousness_level"] = state.consciousness_level.name
            state_dict["active_layers"] = {
                layer.value: level for layer, level in state.active_layers.items()
            }
            save_data["consciousness_history"].append(state_dict)

        # ConsciousnessFlow 객체들을 직렬화
        for pattern, flow in self.active_flows.items():
            flow_dict = asdict(flow)
            flow_dict["start_time"] = flow.start_time.isoformat()
            flow_dict["end_time"] = flow.end_time.isoformat() if flow.end_time else None
            flow_dict["dominant_layer"] = flow.dominant_layer.value

            # flow_states 직렬화
            flow_dict["flow_states"] = []
            for state in flow.flow_states:
                state_dict = asdict(state)
                state_dict["consciousness_level"] = state.consciousness_level.name
                state_dict["active_layers"] = {
                    layer.value: level for layer, level in state.active_layers.items()
                }
                flow_dict["flow_states"].append(state_dict)

            save_data["active_flows"][pattern] = flow_dict

        # AwarenessSnapshot 객체들을 직렬화
        for snapshot in self.awareness_snapshots:
            snapshot_dict = asdict(snapshot)
            snapshot_dict["timestamp"] = snapshot.timestamp.isoformat()
            save_data["awareness_snapshots"].append(snapshot_dict)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return f"✅ 의식 흐름 데이터 저장 완료: {filename}"
        except Exception as e:
            return f"❌ 저장 실패: {e}"


# 편의 함수들
def create_consciousness_flow_analyzer(**kwargs) -> ConsciousnessFlowAnalyzer:
    """Consciousness Flow Analyzer 생성"""
    return ConsciousnessFlowAnalyzer(**kwargs)


def analyze_current_consciousness() -> Dict[str, Any]:
    """현재 의식 상태 간단 분석"""
    analyzer = ConsciousnessFlowAnalyzer()
    analyzer.start_monitoring()

    # 잠시 대기하여 데이터 수집
    time.sleep(2)

    summary = analyzer.get_consciousness_summary()
    analyzer.stop_monitoring()

    return summary


if __name__ == "__main__":
    # 테스트 실행
    print("🧠 Consciousness Flow Analyzer 테스트...")

    analyzer = ConsciousnessFlowAnalyzer()

    # 모니터링 시작
    analyzer.start_monitoring()

    # 테스트 시간 동안 실행
    print("\n🔄 의식 흐름 모니터링 시뮬레이션 (10초)...")
    time.sleep(10)

    # 결과 출력
    print("\n" + "=" * 70)
    print(analyzer.visualize_consciousness_flow(minutes=1))

    # 요약 정보
    summary = analyzer.get_consciousness_summary()
    print(f"\n📊 Consciousness Summary:")
    print(f"   Consciousness Level: {summary['consciousness_level']}")
    print(f"   Attention Intensity: {summary['attention_intensity']}")
    print(f"   Self Reflection Depth: {summary['self_reflection_depth']}")
    print(f"   Awareness Focus: {summary['awareness_focus']}")
    print(f"   Active Signature: {summary['signature_consciousness']}")

    # 활성 계층 표시
    print(f"\n🧠 Active Cognitive Layers:")
    for layer, level in summary["active_cognitive_layers"].items():
        print(f"   {layer:15}: {level:.3f}")

    # 활성 흐름 표시
    if summary["active_consciousness_flows"]:
        print(f"\n🌊 Active Flows:")
        for pattern, info in summary["active_consciousness_flows"].items():
            print(
                f"   {pattern}: {info['duration_minutes']:.1f}m, "
                f"coherence: {info['coherence']:.3f}"
            )

    # 저장
    save_result = analyzer.save_consciousness_data()
    print(f"\n{save_result}")

    # 모니터링 정지
    analyzer.stop_monitoring()

    print("\n✅ Consciousness Flow Analyzer 테스트 완료!")
