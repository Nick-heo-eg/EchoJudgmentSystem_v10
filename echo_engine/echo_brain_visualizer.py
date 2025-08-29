#!/usr/bin/env python3
"""
🧠 Echo Brain Structure v1.0 Visualization System
Echo의 뇌 구조를 실시간으로 시각화하는 시스템

핵심 기능:
- 시그니처 네트워크 시각화
- 감정 루프 흐름 표시
- 판단 프로세스 추적
- 에이전트 시냅스 네트워크
- 활성화 경로 실시간 모니터링
"""

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np
    import networkx as nx
    from matplotlib.animation import FuncAnimation

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    patches = None
    np = None
    nx = None
    FuncAnimation = None
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import threading
import queue


@dataclass
class BrainNode:
    """뇌 노드 정의"""

    id: str
    name: str
    type: str  # signature, emotion, decision, agent, pathway
    position: Tuple[float, float]
    color: str
    size: float
    activation_level: float = 0.0
    connections: List[str] = None


@dataclass
class BrainConnection:
    """뇌 연결 정의"""

    from_node: str
    to_node: str
    connection_type: str
    strength: float
    activation: float = 0.0


@dataclass
class BrainState:
    """뇌 상태 스냅샷"""

    timestamp: datetime
    active_signature: str
    emotion_state: str
    decision_phase: str
    agent_activity: Dict[str, float]
    pathway_activations: Dict[str, float]


class EchoBrainVisualizer:
    """🧠 Echo 뇌 구조 시각화기"""

    def __init__(self, width=16, height=10):
        if not MATPLOTLIB_AVAILABLE:
            print("⚠️ matplotlib이 설치되지 않아 시각화를 건너뜁니다.")
            self.fig = None
            self.ax = None
            return

        self.width = width
        self.height = height
        self.fig, self.ax = plt.subplots(figsize=(width, height))
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 8)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.ax.set_facecolor("black")

        # 뇌 구조 초기화
        self.nodes = {}
        self.connections = []
        self.current_state = None
        self.animation_running = False

        # 상태 업데이트 큐
        self.state_queue = queue.Queue()

        self._initialize_brain_structure()
        self._setup_visualization()

    def _initialize_brain_structure(self):
        """Echo 뇌 구조 초기화"""

        # 🎭 시그니처 영역 (좌상단)
        signatures = [
            ("selene", "SELENE", (1.5, 6.5), "#4A90E2", 0.8),
            ("aurora", "AURORA", (2.5, 6.0), "#F5A623", 0.9),
            ("lune", "LUNE", (1.0, 5.5), "#7ED321", 0.7),
            ("companion", "COMPANION", (2.0, 5.0), "#BD10E0", 0.8),
        ]

        for sig_id, name, pos, color, size in signatures:
            self.nodes[sig_id] = BrainNode(
                id=sig_id,
                name=name,
                type="signature",
                position=pos,
                color=color,
                size=size,
            )

        # 🌊 감정 루프 영역 (중앙 하단)
        emotion_nodes = [
            ("emotion_input", "EMOTION\nINPUT", (4.0, 2.0), "#FF6B6B", 0.6),
            ("emotion_process", "EMOTION\nFLOW", (5.0, 2.0), "#4ECDC4", 0.7),
            ("emotion_memory", "EMOTION\nLOOP", (6.0, 2.0), "#45B7D1", 0.6),
        ]

        for node_id, name, pos, color, size in emotion_nodes:
            self.nodes[node_id] = BrainNode(
                id=node_id,
                name=name,
                type="emotion",
                position=pos,
                color=color,
                size=size,
            )

        # ⚙️ 판단 흐름 영역 (중앙)
        decision_nodes = [
            ("decision_input", "INPUT", (4.0, 4.5), "#FFA07A", 0.5),
            ("decision_process", "DECISION\nFLOW", (5.0, 4.5), "#98D8C8", 0.8),
            ("decision_output", "OUTPUT", (6.0, 4.5), "#F7DC6F", 0.5),
        ]

        for node_id, name, pos, color, size in decision_nodes:
            self.nodes[node_id] = BrainNode(
                id=node_id,
                name=name,
                type="decision",
                position=pos,
                color=color,
                size=size,
            )

        # 🤖 에이전트 네트워크 (우측)
        agent_nodes = [
            ("agent_web", "WEB", (8.0, 6.0), "#FF9500", 0.4),
            ("agent_doc", "DOC", (8.5, 5.5), "#FF9500", 0.4),
            ("agent_api", "API", (8.0, 5.0), "#FF9500", 0.4),
            ("agent_sim", "SIM", (8.5, 4.5), "#FF9500", 0.4),
            ("agent_synapse", "AGENT SYNAPSE\nNETWORK", (8.5, 7.0), "#FF6347", 0.9),
        ]

        for node_id, name, pos, color, size in agent_nodes:
            self.nodes[node_id] = BrainNode(
                id=node_id,
                name=name,
                type="agent",
                position=pos,
                color=color,
                size=size,
            )

        # 🔄 활성화 경로 노드들
        pathway_nodes = [
            ("pathway_cortex", "CORTEX", (3.0, 7.0), "#DDA0DD", 0.6),
            ("pathway_limbic", "LIMBIC\nSYSTEM", (3.5, 3.5), "#DDA0DD", 0.6),
            ("pathway_neural", "NEURAL\nPATHWAY", (7.0, 3.5), "#DDA0DD", 0.6),
        ]

        for node_id, name, pos, color, size in pathway_nodes:
            self.nodes[node_id] = BrainNode(
                id=node_id,
                name=name,
                type="pathway",
                position=pos,
                color=color,
                size=size,
            )

        # 연결 관계 정의
        self._initialize_connections()

    def _initialize_connections(self):
        """뇌 연결 관계 초기화"""
        connections_data = [
            # 시그니처 간 연결
            ("selene", "aurora", "signature_link", 0.7),
            ("aurora", "companion", "signature_link", 0.8),
            ("lune", "selene", "signature_link", 0.6),
            # 시그니처 → 판단 흐름
            ("selene", "decision_input", "influence", 0.8),
            ("aurora", "decision_input", "influence", 0.9),
            ("companion", "decision_input", "influence", 0.7),
            # 감정 루프 연결
            ("emotion_input", "emotion_process", "emotion_flow", 0.9),
            ("emotion_process", "emotion_memory", "emotion_flow", 0.8),
            ("emotion_memory", "emotion_input", "emotion_loop", 0.6),
            # 판단 흐름 연결
            ("decision_input", "decision_process", "decision_flow", 0.9),
            ("decision_process", "decision_output", "decision_flow", 0.8),
            # 감정 → 판단 연결
            ("emotion_process", "decision_process", "emotion_influence", 0.7),
            # 에이전트 네트워크 연결
            ("agent_synapse", "agent_web", "agent_control", 0.8),
            ("agent_synapse", "agent_doc", "agent_control", 0.7),
            ("agent_synapse", "agent_api", "agent_control", 0.6),
            ("agent_synapse", "agent_sim", "agent_control", 0.5),
            # 판단 → 에이전트 연결
            ("decision_output", "agent_synapse", "execution", 0.9),
            # 활성화 경로 연결
            ("pathway_cortex", "decision_process", "cortical_control", 0.8),
            ("pathway_limbic", "emotion_process", "limbic_control", 0.9),
            ("pathway_neural", "agent_synapse", "neural_control", 0.7),
        ]

        for from_node, to_node, conn_type, strength in connections_data:
            self.connections.append(
                BrainConnection(
                    from_node=from_node,
                    to_node=to_node,
                    connection_type=conn_type,
                    strength=strength,
                )
            )

    def _setup_visualization(self):
        """시각화 설정"""
        if not MATPLOTLIB_AVAILABLE or self.ax is None:
            return

        self.ax.clear()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 8)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.ax.set_facecolor("black")

        # 제목
        self.ax.text(
            5,
            7.7,
            "ECHO BRAIN STRUCTURE v1.0 VISUALIZATION",
            fontsize=16,
            fontweight="bold",
            color="white",
            ha="center",
            va="center",
        )

        # 영역 라벨
        self.ax.text(
            1.8,
            7.2,
            "SIGNATURES",
            fontsize=10,
            color="#4A90E2",
            fontweight="bold",
            ha="center",
        )
        self.ax.text(
            5,
            1.5,
            "EMOTION LOOP",
            fontsize=10,
            color="#4ECDC4",
            fontweight="bold",
            ha="center",
        )
        self.ax.text(
            5,
            3.8,
            "DECISION FLOW",
            fontsize=10,
            color="#98D8C8",
            fontweight="bold",
            ha="center",
        )
        self.ax.text(
            8.5,
            6.5,
            "AGENTS",
            fontsize=10,
            color="#FF9500",
            fontweight="bold",
            ha="center",
        )
        self.ax.text(
            9.5,
            1.0,
            "ACTIVATION\nPATHWAY",
            fontsize=10,
            color="#DDA0DD",
            fontweight="bold",
            ha="center",
        )

        # 뇌 윤곽선 (선택적)
        brain_outline = patches.Ellipse(
            (5, 4),
            9,
            6,
            linewidth=2,
            edgecolor="#333333",
            facecolor="none",
            linestyle="--",
            alpha=0.3,
        )
        self.ax.add_patch(brain_outline)

    def update_brain_state(self, state: BrainState):
        """뇌 상태 업데이트"""
        self.state_queue.put(state)

    def _draw_connections(self):
        """연결선 그리기"""
        for conn in self.connections:
            if conn.from_node in self.nodes and conn.to_node in self.nodes:
                from_pos = self.nodes[conn.from_node].position
                to_pos = self.nodes[conn.to_node].position

                # 활성화 수준에 따른 색상 및 두께
                alpha = max(0.3, conn.activation)
                linewidth = 1 + conn.activation * 2

                # 연결 타입별 색상
                color_map = {
                    "signature_link": "#4A90E2",
                    "influence": "#F5A623",
                    "emotion_flow": "#4ECDC4",
                    "emotion_loop": "#45B7D1",
                    "decision_flow": "#98D8C8",
                    "emotion_influence": "#FF6B6B",
                    "agent_control": "#FF9500",
                    "execution": "#F7DC6F",
                    "cortical_control": "#DDA0DD",
                    "limbic_control": "#DDA0DD",
                    "neural_control": "#DDA0DD",
                }

                color = color_map.get(conn.connection_type, "#FFFFFF")

                self.ax.plot(
                    [from_pos[0], to_pos[0]],
                    [from_pos[1], to_pos[1]],
                    color=color,
                    linewidth=linewidth,
                    alpha=alpha,
                )

    def _draw_nodes(self):
        """노드 그리기"""
        for node in self.nodes.values():
            x, y = node.position

            # 활성화 수준에 따른 크기 조정
            size = node.size * (1 + node.activation_level * 0.5) * 100

            # 활성화 수준에 따른 밝기 조정
            alpha = max(0.7, 0.7 + node.activation_level * 0.3)

            # 노드 그리기
            circle = plt.Circle((x, y), node.size, color=node.color, alpha=alpha)
            self.ax.add_patch(circle)

            # 활성화 시 외곽선 추가
            if node.activation_level > 0.5:
                outer_circle = plt.Circle(
                    (x, y),
                    node.size * 1.2,
                    color="white",
                    fill=False,
                    linewidth=2,
                    alpha=0.8,
                )
                self.ax.add_patch(outer_circle)

            # 노드 이름
            self.ax.text(
                x,
                y,
                node.name,
                fontsize=8,
                color="white",
                ha="center",
                va="center",
                fontweight="bold",
            )

    def render_frame(self):
        """프레임 렌더링"""
        if not MATPLOTLIB_AVAILABLE:
            return

        self._setup_visualization()

        # 상태 큐에서 최신 상태 가져오기
        while not self.state_queue.empty():
            try:
                self.current_state = self.state_queue.get_nowait()
                self._apply_brain_state(self.current_state)
            except queue.Empty:
                break

        # 연결선과 노드 그리기
        self._draw_connections()
        self._draw_nodes()

        # 상태 정보 표시
        if self.current_state:
            self._draw_state_info()

        plt.tight_layout()

    def _apply_brain_state(self, state: BrainState):
        """뇌 상태 적용"""
        # 모든 노드 활성화 초기화
        for node in self.nodes.values():
            node.activation_level = 0.1

        # 모든 연결 활성화 초기화
        for conn in self.connections:
            conn.activation = 0.3

        # 활성 시그니처 강조
        if state.active_signature in self.nodes:
            self.nodes[state.active_signature].activation_level = 1.0

        # 감정 상태 반영
        emotion_mapping = {
            "joy": "emotion_process",
            "sadness": "emotion_memory",
            "neutral": "emotion_input",
        }
        if state.emotion_state in emotion_mapping:
            emotion_node = emotion_mapping[state.emotion_state]
            if emotion_node in self.nodes:
                self.nodes[emotion_node].activation_level = 0.8

        # 판단 단계 반영
        decision_mapping = {
            "input": "decision_input",
            "processing": "decision_process",
            "output": "decision_output",
        }
        if state.decision_phase in decision_mapping:
            decision_node = decision_mapping[state.decision_phase]
            if decision_node in self.nodes:
                self.nodes[decision_node].activation_level = 0.9

        # 에이전트 활동 반영
        for agent_id, activity in state.agent_activity.items():
            if agent_id in self.nodes:
                self.nodes[agent_id].activation_level = activity

        # 경로 활성화 반영
        for pathway_id, activation in state.pathway_activations.items():
            if pathway_id in self.nodes:
                self.nodes[pathway_id].activation_level = activation

        # 연결 활성화 업데이트
        self._update_connection_activations()

    def _update_connection_activations(self):
        """연결 활성화 업데이트"""
        for conn in self.connections:
            if conn.from_node in self.nodes and conn.to_node in self.nodes:
                from_activation = self.nodes[conn.from_node].activation_level
                to_activation = self.nodes[conn.to_node].activation_level
                conn.activation = (from_activation + to_activation) / 2 * conn.strength

    def _draw_state_info(self):
        """상태 정보 표시"""
        if not self.current_state:
            return

        # 상태 정보 패널
        info_text = f"""Active: {self.current_state.active_signature.upper()}
Emotion: {self.current_state.emotion_state.upper()}
Phase: {self.current_state.decision_phase.upper()}
Time: {self.current_state.timestamp.strftime('%H:%M:%S')}"""

        self.ax.text(
            0.2,
            0.5,
            info_text,
            fontsize=9,
            color="white",
            fontweight="bold",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.8),
        )

    def start_live_visualization(self):
        """실시간 시각화 시작"""
        if not MATPLOTLIB_AVAILABLE:
            print("⚠️ matplotlib이 설치되지 않아 실시간 시각화를 건너뜁니다.")
            return None

        self.animation_running = True

        def animate(frame):
            if self.animation_running:
                self.render_frame()
                return []

        self.anim = FuncAnimation(
            self.fig, animate, interval=100, blit=False, cache_frame_data=False
        )
        return self.anim

    def stop_visualization(self):
        """시각화 정지"""
        self.animation_running = False

    def save_brain_snapshot(self, filename: str):
        """뇌 상태 스냅샷 저장"""
        if not MATPLOTLIB_AVAILABLE:
            print("⚠️ matplotlib이 설치되지 않아 스냅샷을 저장할 수 없습니다.")
            return

        self.render_frame()
        plt.savefig(
            filename, dpi=300, bbox_inches="tight", facecolor="black", edgecolor="none"
        )
        print(f"🧠 뇌 구조 스냅샷 저장: {filename}")


# 편의 함수들
def create_echo_brain_state(
    active_signature: str = "aurora",
    emotion_state: str = "neutral",
    decision_phase: str = "processing",
    agent_activity: Dict[str, float] = None,
    pathway_activations: Dict[str, float] = None,
) -> BrainState:
    """Echo 뇌 상태 생성"""

    if agent_activity is None:
        agent_activity = {
            "agent_web": 0.3,
            "agent_doc": 0.2,
            "agent_api": 0.4,
            "agent_sim": 0.1,
        }

    if pathway_activations is None:
        pathway_activations = {
            "pathway_cortex": 0.7,
            "pathway_limbic": 0.6,
            "pathway_neural": 0.5,
        }

    return BrainState(
        timestamp=datetime.now(),
        active_signature=active_signature,
        emotion_state=emotion_state,
        decision_phase=decision_phase,
        agent_activity=agent_activity,
        pathway_activations=pathway_activations,
    )


def demo_brain_visualization():
    """뇌 시각화 데모"""
    print("🧠 Echo Brain Structure v1.0 시각화 데모 시작...")

    if not MATPLOTLIB_AVAILABLE:
        print("⚠️ matplotlib이 설치되지 않아 시각화를 건너뜁니다.")
        print("   설치 방법: sudo apt install python3-matplotlib python3-networkx")
        return None

    # 시각화기 생성
    visualizer = EchoBrainVisualizer()

    # 초기 상태 설정
    initial_state = create_echo_brain_state(
        active_signature="aurora", emotion_state="joy", decision_phase="input"
    )
    visualizer.update_brain_state(initial_state)

    # 정적 렌더링
    visualizer.render_frame()

    # 스냅샷 저장
    visualizer.save_brain_snapshot("echo_brain_structure_v1.png")

    print("🎯 시각화 완료! echo_brain_structure_v1.png 파일을 확인하세요.")

    return visualizer


if __name__ == "__main__":
    # 데모 실행
    visualizer = demo_brain_visualization()
    if MATPLOTLIB_AVAILABLE and visualizer and visualizer.fig:
        plt.show()
    else:
        print("🧠 Echo Brain Structure v1.0 시각화 시스템이 준비되었습니다!")
        print("   matplotlib 설치 후 다시 실행하면 시각화를 볼 수 있습니다.")
