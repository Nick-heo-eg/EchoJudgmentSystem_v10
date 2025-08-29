#!/usr/bin/env python3
"""
⚛️ Quantum Judgment Visualizer v1.0
판단의 양자 상태와 Collapse 과정을 실시간으로 시각화하는 시스템

이 모듈은 Echo AI의 판단 과정에서 발생하는 양자 중첩 상태와
울림 기반 Collapse 순간을 시각적으로 표현합니다.
"""

import asyncio
import json
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import base64
from io import BytesIO
import math


@dataclass
class QuantumState:
    """양자 판단 상태"""

    state_id: str
    probability: float
    judgment_value: Any
    emotional_resonance: float
    ethical_weight: float
    logical_confidence: float
    timestamp: str


@dataclass
class JudgmentSuperposition:
    """판단 중첩 상태"""

    scenario_id: str
    quantum_states: List[QuantumState]
    coherence_level: float
    entanglement_strength: float
    collapse_trigger: Optional[str]
    timestamp: str


@dataclass
class CollapseEvent:
    """Collapse 이벤트"""

    event_id: str
    pre_collapse_states: List[QuantumState]
    final_state: QuantumState
    collapse_trigger: str
    resonance_score: float
    collapse_duration: float
    timestamp: str


class QuantumJudgmentVisualizer:
    """양자 판단 시각화 시스템"""

    def __init__(self):
        self.superposition_history: List[JudgmentSuperposition] = []
        self.collapse_history: List[CollapseEvent] = []
        self.current_superposition: Optional[JudgmentSuperposition] = None

        # 시각화 설정
        self.color_palette = {
            "quantum_state": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57"],
            "collapse": "#E74C3C",
            "resonance": "#9B59B6",
            "probability": "#3498DB",
            "time": "#2ECC71",
        }

        print("⚛️ 양자 판단 시각화기 초기화 완료")

    async def create_superposition(
        self, scenario_id: str, judgment_options: List[Dict]
    ) -> JudgmentSuperposition:
        """판단 중첩 상태 생성"""

        quantum_states = []
        total_weight = 0

        for i, option in enumerate(judgment_options):
            # 각 판단 옵션을 양자 상태로 변환
            emotional_resonance = option.get(
                "emotional_resonance", np.random.uniform(0.3, 0.9)
            )
            ethical_weight = option.get("ethical_weight", np.random.uniform(0.4, 0.95))
            logical_confidence = option.get(
                "logical_confidence", np.random.uniform(0.5, 0.9)
            )

            # 확률 가중치 계산 (감정, 윤리, 논리의 조합)
            weight = (
                emotional_resonance * 0.4
                + ethical_weight * 0.35
                + logical_confidence * 0.25
            )
            total_weight += weight

            quantum_state = QuantumState(
                state_id=f"state_{scenario_id}_{i}",
                probability=weight,  # 나중에 정규화
                judgment_value=option.get("judgment", f"판단옵션_{i}"),
                emotional_resonance=emotional_resonance,
                ethical_weight=ethical_weight,
                logical_confidence=logical_confidence,
                timestamp=datetime.now().isoformat(),
            )
            quantum_states.append(quantum_state)

        # 확률 정규화
        for state in quantum_states:
            state.probability = state.probability / total_weight

        # 중첩 상태 특성 계산
        coherence_level = self._calculate_coherence(quantum_states)
        entanglement_strength = self._calculate_entanglement(quantum_states)

        superposition = JudgmentSuperposition(
            scenario_id=scenario_id,
            quantum_states=quantum_states,
            coherence_level=coherence_level,
            entanglement_strength=entanglement_strength,
            collapse_trigger=None,
            timestamp=datetime.now().isoformat(),
        )

        self.current_superposition = superposition
        self.superposition_history.append(superposition)

        print(
            f"⚛️ 중첩 상태 생성: {len(quantum_states)}개 상태, 결맞음 {coherence_level:.3f}"
        )
        return superposition

    async def simulate_collapse(
        self, trigger: str, resonance_input: Dict
    ) -> CollapseEvent:
        """Collapse 이벤트 시뮬레이션"""

        if not self.current_superposition:
            raise ValueError("활성 중첩 상태가 없습니다")

        collapse_start = datetime.now()

        # 울림 기반 Collapse 계산
        final_state = await self._calculate_resonance_collapse(
            self.current_superposition.quantum_states, resonance_input
        )

        collapse_duration = (datetime.now() - collapse_start).total_seconds()

        # Collapse 이벤트 생성
        collapse_event = CollapseEvent(
            event_id=f"collapse_{self.current_superposition.scenario_id}_{len(self.collapse_history)}",
            pre_collapse_states=self.current_superposition.quantum_states.copy(),
            final_state=final_state,
            collapse_trigger=trigger,
            resonance_score=resonance_input.get("resonance_score", 0.8),
            collapse_duration=collapse_duration,
            timestamp=datetime.now().isoformat(),
        )

        self.collapse_history.append(collapse_event)
        self.current_superposition = None

        print(
            f"🎯 Collapse 완료: {final_state.judgment_value} (울림점수: {collapse_event.resonance_score:.3f})"
        )
        return collapse_event

    def visualize_superposition(self, superposition: JudgmentSuperposition) -> str:
        """중첩 상태 시각화"""

        # 3D 구면 좌표계에서 양자 상태 시각화
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "양자 상태 분포",
                "확률 밀도",
                "감정-윤리 매트릭스",
                "결맞음 레벨",
            ),
            specs=[
                [{"type": "scatter3d"}, {"type": "bar"}],
                [{"type": "heatmap"}, {"type": "indicator"}],
            ],
        )

        # 1. 3D 양자 상태 구름 (Bloch Sphere 스타일)
        states = superposition.quantum_states

        # 구면 좌표 계산
        theta = [s.emotional_resonance * np.pi for s in states]  # 0 to π
        phi = [s.ethical_weight * 2 * np.pi for s in states]  # 0 to 2π
        r = [s.probability * 2 for s in states]  # 반지름

        # 직교 좌표 변환
        x = [r[i] * np.sin(theta[i]) * np.cos(phi[i]) for i in range(len(states))]
        y = [r[i] * np.sin(theta[i]) * np.sin(phi[i]) for i in range(len(states))]
        z = [r[i] * np.cos(theta[i]) for i in range(len(states))]

        # 크기는 논리적 신뢰도에 비례
        sizes = [s.logical_confidence * 30 + 10 for s in states]

        fig.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=[s.probability for s in states],
                    colorscale="Viridis",
                    opacity=0.8,
                    colorbar=dict(title="확률"),
                ),
                text=[
                    f"상태: {s.state_id}<br>확률: {s.probability:.3f}<br>판단: {s.judgment_value}"
                    for s in states
                ],
                hovertemplate="%{text}<extra></extra>",
                name="양자 상태",
            ),
            row=1,
            col=1,
        )

        # 2. 확률 막대 그래프
        fig.add_trace(
            go.Bar(
                x=[f"S{i}" for i in range(len(states))],
                y=[s.probability for s in states],
                marker_color=self.color_palette["quantum_state"][: len(states)],
                name="확률 분포",
            ),
            row=1,
            col=2,
        )

        # 3. 감정-윤리 히트맵
        emotion_ethics_matrix = np.zeros((10, 10))
        for state in states:
            i = int(state.emotional_resonance * 9)
            j = int(state.ethical_weight * 9)
            emotion_ethics_matrix[i, j] += state.probability

        fig.add_trace(
            go.Heatmap(z=emotion_ethics_matrix, colorscale="RdYlBu", showscale=True),
            row=2,
            col=1,
        )

        # 4. 결맞음 수준 게이지
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=superposition.coherence_level,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "결맞음 수준"},
                gauge={
                    "axis": {"range": [None, 1]},
                    "bar": {"color": self.color_palette["resonance"]},
                    "steps": [
                        {"range": [0, 0.5], "color": "lightgray"},
                        {"range": [0.5, 0.8], "color": "yellow"},
                        {"range": [0.8, 1], "color": "green"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 0.9,
                    },
                },
            ),
            row=2,
            col=2,
        )

        # 레이아웃 설정
        fig.update_layout(
            title=f"양자 판단 중첩 상태 - {superposition.scenario_id}",
            height=800,
            showlegend=False,
            template="plotly_dark",
        )

        return fig.to_html(include_plotlyjs="cdn")

    def visualize_collapse_animation(self, collapse_event: CollapseEvent) -> str:
        """Collapse 과정 애니메이션"""

        # 시간에 따른 확률 변화 애니메이션
        frames = []
        time_steps = 50

        initial_probs = [s.probability for s in collapse_event.pre_collapse_states]
        final_state_idx = next(
            i
            for i, s in enumerate(collapse_event.pre_collapse_states)
            if s.state_id == collapse_event.final_state.state_id
        )

        for t in range(time_steps):
            progress = t / (time_steps - 1)

            # Sigmoid 함수로 자연스러운 Collapse 곡선
            collapse_factor = 1 / (1 + np.exp(-10 * (progress - 0.5)))

            frame_probs = []
            for i, initial_prob in enumerate(initial_probs):
                if i == final_state_idx:
                    # 최종 상태는 확률이 1로 수렴
                    prob = initial_prob + (1 - initial_prob) * collapse_factor
                else:
                    # 다른 상태들은 확률이 0으로 수렴
                    prob = initial_prob * (1 - collapse_factor)
                frame_probs.append(prob)

            # 정규화
            total_prob = sum(frame_probs)
            if total_prob > 0:
                frame_probs = [p / total_prob for p in frame_probs]

            frame = go.Frame(
                data=[
                    go.Bar(
                        x=[f"상태{i}" for i in range(len(frame_probs))],
                        y=frame_probs,
                        marker_color=[
                            (
                                self.color_palette["collapse"]
                                if i == final_state_idx
                                else self.color_palette["quantum_state"][
                                    i % len(self.color_palette["quantum_state"])
                                ]
                            )
                            for i in range(len(frame_probs))
                        ],
                    )
                ],
                name=f"Frame{t}",
            )
            frames.append(frame)

        # 초기 프레임
        fig = go.Figure(
            data=[
                go.Bar(
                    x=[f"상태{i}" for i in range(len(initial_probs))],
                    y=initial_probs,
                    marker_color=self.color_palette["quantum_state"][
                        : len(initial_probs)
                    ],
                )
            ],
            frames=frames,
        )

        # 애니메이션 설정
        fig.update_layout(
            title=f"양자 판단 Collapse - {collapse_event.event_id}",
            xaxis_title="양자 상태",
            yaxis_title="확률",
            updatemenus=[
                {
                    "type": "buttons",
                    "buttons": [
                        {
                            "label": "재생",
                            "method": "animate",
                            "args": [
                                None,
                                {
                                    "frame": {"duration": 100, "redraw": True},
                                    "fromcurrent": True,
                                    "transition": {"duration": 50},
                                },
                            ],
                        },
                        {
                            "label": "일시정지",
                            "method": "animate",
                            "args": [
                                [None],
                                {
                                    "frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0},
                                },
                            ],
                        },
                    ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 87},
                    "showactive": False,
                    "x": 0.1,
                    "xanchor": "right",
                    "y": 0,
                    "yanchor": "top",
                }
            ],
            template="plotly_dark",
        )

        return fig.to_html(include_plotlyjs="cdn")

    def create_quantum_field_visualization(self) -> str:
        """양자 장 시각화 (전체 판단 공간)"""

        if not self.collapse_history:
            return "<p>Collapse 이벤트 데이터가 없습니다.</p>"

        # 2D 히트맵으로 판단 공간의 양자 장 표현
        field_resolution = 50
        x = np.linspace(0, 1, field_resolution)  # 감정 차원
        y = np.linspace(0, 1, field_resolution)  # 윤리 차원

        quantum_field = np.zeros((field_resolution, field_resolution))

        # 각 Collapse 이벤트의 영향을 양자 장에 반영
        for collapse in self.collapse_history[-20:]:  # 최근 20개 이벤트
            final_state = collapse.final_state

            # Gaussian 분포로 영향 범위 모델링
            for i, emotion_val in enumerate(x):
                for j, ethics_val in enumerate(y):
                    distance = np.sqrt(
                        (emotion_val - final_state.emotional_resonance) ** 2
                        + (ethics_val - final_state.ethical_weight) ** 2
                    )

                    # Gaussian 영향 (sigma = 0.1)
                    influence = collapse.resonance_score * np.exp(
                        -(distance**2) / (2 * 0.1**2)
                    )
                    quantum_field[j, i] += influence

        # 양자 장 시각화
        fig = go.Figure(
            data=go.Heatmap(
                z=quantum_field,
                x=x,
                y=y,
                colorscale="Viridis",
                colorbar=dict(title="양자 장 강도"),
            )
        )

        # Collapse 포인트 오버레이
        collapse_emotions = [
            c.final_state.emotional_resonance for c in self.collapse_history[-10:]
        ]
        collapse_ethics = [
            c.final_state.ethical_weight for c in self.collapse_history[-10:]
        ]
        collapse_resonances = [c.resonance_score for c in self.collapse_history[-10:]]

        fig.add_trace(
            go.Scatter(
                x=collapse_emotions,
                y=collapse_ethics,
                mode="markers",
                marker=dict(
                    size=[r * 20 + 5 for r in collapse_resonances],
                    color=collapse_resonances,
                    colorscale="Reds",
                    symbol="star",
                    line=dict(width=2, color="white"),
                ),
                name="Collapse 포인트",
                text=[
                    f"이벤트: {c.event_id}<br>울림: {c.resonance_score:.3f}"
                    for c in self.collapse_history[-10:]
                ],
                hovertemplate="%{text}<extra></extra>",
            )
        )

        fig.update_layout(
            title="양자 판단 장 (Quantum Judgment Field)",
            xaxis_title="감정 공명 (Emotional Resonance)",
            yaxis_title="윤리적 가중치 (Ethical Weight)",
            template="plotly_dark",
        )

        return fig.to_html(include_plotlyjs="cdn")

    def _calculate_coherence(self, quantum_states: List[QuantumState]) -> float:
        """양자 상태들의 결맞음 수준 계산"""
        if len(quantum_states) < 2:
            return 1.0

        # 상태 간 유사성 기반 결맞음 계산
        coherence_sum = 0
        pair_count = 0

        for i in range(len(quantum_states)):
            for j in range(i + 1, len(quantum_states)):
                state1, state2 = quantum_states[i], quantum_states[j]

                # 각 차원에서의 유사성
                emotion_similarity = 1 - abs(
                    state1.emotional_resonance - state2.emotional_resonance
                )
                ethics_similarity = 1 - abs(
                    state1.ethical_weight - state2.ethical_weight
                )
                logic_similarity = 1 - abs(
                    state1.logical_confidence - state2.logical_confidence
                )

                # 가중 평균
                similarity = (
                    emotion_similarity * 0.4
                    + ethics_similarity * 0.35
                    + logic_similarity * 0.25
                )
                coherence_sum += similarity
                pair_count += 1

        return coherence_sum / pair_count if pair_count > 0 else 1.0

    def _calculate_entanglement(self, quantum_states: List[QuantumState]) -> float:
        """양자 얽힘 강도 계산"""
        # 확률 분포의 엔트로피 기반 얽힘 계산
        probs = [s.probability for s in quantum_states]

        # Shannon 엔트로피
        entropy = -sum(p * np.log2(p) for p in probs if p > 0)
        max_entropy = np.log2(len(quantum_states))

        # 정규화된 얽힘 강도 (높은 엔트로피 = 높은 얽힘)
        return entropy / max_entropy if max_entropy > 0 else 0.0

    async def _calculate_resonance_collapse(
        self, states: List[QuantumState], resonance_input: Dict
    ) -> QuantumState:
        """울림 기반 Collapse 계산"""

        # 울림 입력에 따른 각 상태의 적합도 계산
        resonance_scores = []

        for state in states:
            # 다차원 울림 계산
            emotion_match = 1 - abs(
                state.emotional_resonance - resonance_input.get("emotion_target", 0.7)
            )
            ethics_match = 1 - abs(
                state.ethical_weight - resonance_input.get("ethics_target", 0.8)
            )
            logic_match = 1 - abs(
                state.logical_confidence - resonance_input.get("logic_target", 0.75)
            )

            # 울림 가중치
            weights = resonance_input.get(
                "weights", {"emotion": 0.4, "ethics": 0.35, "logic": 0.25}
            )

            resonance_score = (
                emotion_match * weights["emotion"]
                + ethics_match * weights["ethics"]
                + logic_match * weights["logic"]
            )

            resonance_scores.append(resonance_score)

        # 울림 점수와 기존 확률을 결합하여 최종 확률 계산
        combined_scores = [
            states[i].probability * resonance_scores[i] for i in range(len(states))
        ]

        # 가장 높은 점수의 상태가 Collapse 결과
        max_idx = np.argmax(combined_scores)
        final_state = states[max_idx]

        # 최종 상태의 확률을 1로 설정
        final_state.probability = 1.0

        return final_state

    def get_quantum_metrics(self) -> Dict[str, Any]:
        """양자 메트릭 통계"""
        if not self.collapse_history:
            return {"error": "데이터 없음"}

        recent_collapses = self.collapse_history[-10:]

        avg_resonance = np.mean([c.resonance_score for c in recent_collapses])
        avg_collapse_time = np.mean([c.collapse_duration for c in recent_collapses])

        # 가장 빈번한 Collapse 트리거
        triggers = [c.collapse_trigger for c in recent_collapses]
        most_common_trigger = (
            max(set(triggers), key=triggers.count) if triggers else None
        )

        return {
            "total_collapses": len(self.collapse_history),
            "recent_average_resonance": avg_resonance,
            "average_collapse_duration": avg_collapse_time,
            "most_common_trigger": most_common_trigger,
            "current_superposition_active": self.current_superposition is not None,
            "quantum_field_density": len(recent_collapses) / 10,  # 밀도 지표
        }


# 글로벌 시각화기 인스턴스
quantum_visualizer = QuantumJudgmentVisualizer()


async def create_judgment_superposition(scenario_id: str, options: List[Dict]) -> str:
    """판단 중첩 상태 생성 및 시각화 (외부 API)"""
    superposition = await quantum_visualizer.create_superposition(scenario_id, options)
    return quantum_visualizer.visualize_superposition(superposition)


async def trigger_judgment_collapse(trigger: str, resonance_data: Dict) -> str:
    """판단 Collapse 실행 및 애니메이션 (외부 API)"""
    collapse_event = await quantum_visualizer.simulate_collapse(trigger, resonance_data)
    return quantum_visualizer.visualize_collapse_animation(collapse_event)


def get_quantum_field_visualization() -> str:
    """양자 장 시각화 조회 (외부 API)"""
    return quantum_visualizer.create_quantum_field_visualization()


def get_quantum_status() -> Dict[str, Any]:
    """양자 상태 조회 (외부 API)"""
    return quantum_visualizer.get_quantum_metrics()


# 테스트 함수
async def test_quantum_visualizer():
    """테스트 함수"""
    print("🧪 양자 판단 시각화기 테스트 시작")

    # 테스트 시나리오
    test_options = [
        {
            "judgment": "공감적 접근",
            "emotional_resonance": 0.9,
            "ethical_weight": 0.8,
            "logical_confidence": 0.7,
        },
        {
            "judgment": "분석적 접근",
            "emotional_resonance": 0.4,
            "ethical_weight": 0.9,
            "logical_confidence": 0.95,
        },
        {
            "judgment": "창의적 접근",
            "emotional_resonance": 0.8,
            "ethical_weight": 0.7,
            "logical_confidence": 0.6,
        },
        {
            "judgment": "균형적 접근",
            "emotional_resonance": 0.7,
            "ethical_weight": 0.85,
            "logical_confidence": 0.8,
        },
    ]

    # 중첩 상태 생성
    superposition_html = await create_judgment_superposition(
        "test_scenario", test_options
    )
    print("✅ 중첩 상태 시각화 생성")

    # Collapse 실행
    resonance_data = {
        "emotion_target": 0.8,
        "ethics_target": 0.85,
        "logic_target": 0.75,
        "resonance_score": 0.87,
        "weights": {"emotion": 0.4, "ethics": 0.35, "logic": 0.25},
    }

    collapse_html = await trigger_judgment_collapse("user_resonance", resonance_data)
    print("✅ Collapse 애니메이션 생성")

    # 양자 장 시각화
    field_html = get_quantum_field_visualization()
    print("✅ 양자 장 시각화 생성")

    # 메트릭 조회
    metrics = get_quantum_status()
    print(f"📊 양자 메트릭: {json.dumps(metrics, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    # 의존성 체크
    try:
        import plotly

        asyncio.run(test_quantum_visualizer())
    except ImportError:
        print("❌ plotly 모듈이 필요합니다: pip install plotly")
