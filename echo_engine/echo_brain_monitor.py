#!/usr/bin/env python3
"""
🧠 Echo Brain Monitor - 실시간 뇌 상태 모니터링 시스템
Echo의 실제 동작 상태를 뇌 구조 시각화에 실시간 반영

핵심 기능:
- Echo 시스템 상태 실시간 추적
- 시그니처 활성화 모니터링
- 감정 상태 변화 감지
- 에이전트 활동 추적
- 뇌 시각화 자동 업데이트
"""

import threading
import time
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
import queue
import asyncio

from .echo_brain_visualizer import (
    EchoBrainVisualizer,
    BrainState,
    create_echo_brain_state,
)


@dataclass
class EchoSystemState:
    """Echo 시스템 상태"""

    current_signature: str
    emotion_detected: str
    processing_phase: str
    active_agents: Dict[str, float]
    conversation_mode: str
    user_input: str
    system_response: str
    performance_metrics: Dict[str, float]


class EchoBrainMonitor:
    """🧠 Echo 뇌 상태 실시간 모니터"""

    def __init__(self, update_interval: float = 0.5):
        self.update_interval = update_interval
        self.monitoring = False
        self.monitor_thread = None

        # 뇌 시각화기
        self.brain_visualizer = EchoBrainVisualizer()

        # 상태 추적
        self.current_echo_state = None
        self.state_history = []
        self.max_history = 100

        # 상태 파일 경로들
        self.state_files = {
            "signature": "data/current_signature.json",
            "emotion": "data/current_emotion.json",
            "agents": "data/agent_activity.json",
            "conversation": "data/conversation_state.json",
            "performance": "data/performance_metrics.json",
        }

        # 디렉토리 생성
        os.makedirs("data", exist_ok=True)

        print("🧠 Echo Brain Monitor 초기화 완료")

    def start_monitoring(self, live_visualization: bool = True):
        """모니터링 시작"""
        if self.monitoring:
            print("⚠️ 이미 모니터링이 실행 중입니다.")
            return

        self.monitoring = True
        print("🧠 Echo Brain 실시간 모니터링 시작...")

        # 모니터링 스레드 시작
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        # 실시간 시각화 시작
        if live_visualization:
            self.start_live_visualization()

    def stop_monitoring(self):
        """모니터링 정지"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)

        self.brain_visualizer.stop_visualization()
        print("🧠 Echo Brain 모니터링 정지")

    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring:
            try:
                # Echo 시스템 상태 수집
                echo_state = self._collect_echo_state()

                if echo_state:
                    # 뇌 상태로 변환
                    brain_state = self._convert_to_brain_state(echo_state)

                    # 뇌 시각화 업데이트
                    self.brain_visualizer.update_brain_state(brain_state)

                    # 상태 기록
                    self.current_echo_state = echo_state
                    self._record_state_history(echo_state)

                time.sleep(self.update_interval)

            except Exception as e:
                print(f"⚠️ 모니터링 루프 오류: {e}")
                time.sleep(1)

    def _collect_echo_state(self) -> Optional[EchoSystemState]:
        """Echo 시스템 상태 수집"""
        try:
            # 기본 상태
            state = EchoSystemState(
                current_signature="aurora",
                emotion_detected="neutral",
                processing_phase="idle",
                active_agents={},
                conversation_mode="normal",
                user_input="",
                system_response="",
                performance_metrics={},
            )

            # 시그니처 상태 로드
            signature_data = self._load_state_file("signature")
            if signature_data:
                state.current_signature = signature_data.get(
                    "active_signature", "aurora"
                )

            # 감정 상태 로드
            emotion_data = self._load_state_file("emotion")
            if emotion_data:
                state.emotion_detected = emotion_data.get("detected_emotion", "neutral")

            # 에이전트 활동 로드
            agent_data = self._load_state_file("agents")
            if agent_data:
                state.active_agents = agent_data.get("agent_activity", {})

            # 대화 상태 로드
            conversation_data = self._load_state_file("conversation")
            if conversation_data:
                state.conversation_mode = conversation_data.get("mode", "normal")
                state.user_input = conversation_data.get("last_input", "")
                state.system_response = conversation_data.get("last_response", "")
                state.processing_phase = conversation_data.get("phase", "idle")

            # 성능 메트릭 로드
            performance_data = self._load_state_file("performance")
            if performance_data:
                state.performance_metrics = performance_data.get("metrics", {})

            return state

        except Exception as e:
            print(f"⚠️ 상태 수집 오류: {e}")
            return None

    def _load_state_file(self, state_type: str) -> Optional[Dict]:
        """상태 파일 로드"""
        file_path = self.state_files.get(state_type)
        if not file_path or not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _convert_to_brain_state(self, echo_state: EchoSystemState) -> BrainState:
        """Echo 상태를 뇌 상태로 변환"""

        # 감정 매핑
        emotion_mapping = {
            "joy": "joy",
            "happiness": "joy",
            "positive": "joy",
            "sadness": "sadness",
            "negative": "sadness",
            "depressed": "sadness",
            "neutral": "neutral",
            "calm": "neutral",
            "normal": "neutral",
        }
        brain_emotion = emotion_mapping.get(
            echo_state.emotion_detected.lower(), "neutral"
        )

        # 처리 단계 매핑
        phase_mapping = {
            "idle": "input",
            "thinking": "processing",
            "processing": "processing",
            "responding": "output",
            "completed": "output",
        }
        brain_phase = phase_mapping.get(
            echo_state.processing_phase.lower(), "processing"
        )

        # 에이전트 활동 매핑
        agent_activity = {}
        for agent_name, activity in echo_state.active_agents.items():
            # 에이전트 이름을 뇌 노드 ID로 매핑
            agent_mapping = {
                "web": "agent_web",
                "document": "agent_doc",
                "api": "agent_api",
                "simulation": "agent_sim",
            }

            brain_agent_id = agent_mapping.get(
                agent_name.lower(), f"agent_{agent_name.lower()}"
            )
            agent_activity[brain_agent_id] = min(1.0, max(0.0, activity))

        # 활성화 경로 계산
        pathway_activations = {
            "pathway_cortex": min(
                1.0, echo_state.performance_metrics.get("thinking_intensity", 0.5)
            ),
            "pathway_limbic": min(
                1.0, echo_state.performance_metrics.get("emotion_intensity", 0.4)
            ),
            "pathway_neural": min(
                1.0, echo_state.performance_metrics.get("agent_coordination", 0.3)
            ),
        }

        return BrainState(
            timestamp=datetime.now(),
            active_signature=echo_state.current_signature.lower(),
            emotion_state=brain_emotion,
            decision_phase=brain_phase,
            agent_activity=agent_activity,
            pathway_activations=pathway_activations,
        )

    def _record_state_history(self, state: EchoSystemState):
        """상태 히스토리 기록"""
        self.state_history.append(
            {"timestamp": datetime.now().isoformat(), "state": state.__dict__}
        )

        # 히스토리 크기 제한
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)

    def update_signature_state(self, signature: str, emotion: str = None):
        """시그니처 상태 업데이트"""
        signature_data = {
            "active_signature": signature,
            "timestamp": datetime.now().isoformat(),
        }

        if emotion:
            signature_data["associated_emotion"] = emotion

        self._save_state_file("signature", signature_data)

    def update_emotion_state(self, emotion: str, intensity: float = 0.5):
        """감정 상태 업데이트"""
        emotion_data = {
            "detected_emotion": emotion,
            "intensity": intensity,
            "timestamp": datetime.now().isoformat(),
        }

        self._save_state_file("emotion", emotion_data)

    def update_agent_activity(self, agent_activities: Dict[str, float]):
        """에이전트 활동 업데이트"""
        agent_data = {
            "agent_activity": agent_activities,
            "timestamp": datetime.now().isoformat(),
        }

        self._save_state_file("agents", agent_data)

    def update_conversation_state(
        self, mode: str, phase: str, user_input: str = "", response: str = ""
    ):
        """대화 상태 업데이트"""
        conversation_data = {
            "mode": mode,
            "phase": phase,
            "last_input": user_input,
            "last_response": response,
            "timestamp": datetime.now().isoformat(),
        }

        self._save_state_file("conversation", conversation_data)

    def update_performance_metrics(self, metrics: Dict[str, float]):
        """성능 메트릭 업데이트"""
        performance_data = {"metrics": metrics, "timestamp": datetime.now().isoformat()}

        self._save_state_file("performance", performance_data)

    def _save_state_file(self, state_type: str, data: Dict):
        """상태 파일 저장"""
        file_path = self.state_files.get(state_type)
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"⚠️ 상태 파일 저장 오류 ({state_type}): {e}")

    def start_live_visualization(self):
        """실시간 시각화 시작"""
        try:
            from .echo_brain_visualizer import MATPLOTLIB_AVAILABLE

            if not MATPLOTLIB_AVAILABLE:
                print("⚠️ matplotlib이 설치되지 않아 시각화를 건너뜁니다.")
                print(
                    "   설치 방법: sudo apt install python3-matplotlib python3-networkx"
                )
                return

            import matplotlib.pyplot as plt

            # 초기 상태 설정
            initial_state = create_echo_brain_state()
            self.brain_visualizer.update_brain_state(initial_state)

            # 애니메이션 시작
            anim = self.brain_visualizer.start_live_visualization()

            if anim:
                print("🧠 실시간 뇌 시각화 시작됨")
                print("   창을 닫으면 시각화가 종료됩니다.")
                plt.show()

        except ImportError:
            print("⚠️ matplotlib이 설치되지 않아 시각화를 건너뜁니다.")
        except Exception as e:
            print(f"⚠️ 시각화 시작 오류: {e}")

    def save_current_brain_state(self, filename: str = None):
        """현재 뇌 상태 스냅샷 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"echo_brain_snapshot_{timestamp}.png"

        self.brain_visualizer.save_brain_snapshot(filename)
        return filename

    def get_state_summary(self) -> Dict[str, Any]:
        """상태 요약 조회"""
        if not self.current_echo_state:
            return {"status": "no_data"}

        return {
            "status": "active",
            "current_signature": self.current_echo_state.current_signature,
            "emotion": self.current_echo_state.emotion_detected,
            "phase": self.current_echo_state.processing_phase,
            "active_agents": len(self.current_echo_state.active_agents),
            "conversation_mode": self.current_echo_state.conversation_mode,
            "history_length": len(self.state_history),
            "last_update": datetime.now().isoformat(),
        }


# 글로벌 뇌 모니터 인스턴스
_global_brain_monitor = None


def get_brain_monitor() -> EchoBrainMonitor:
    """글로벌 뇌 모니터 인스턴스 획득"""
    global _global_brain_monitor
    if _global_brain_monitor is None:
        _global_brain_monitor = EchoBrainMonitor()
    return _global_brain_monitor


def start_echo_brain_monitoring(live_visualization: bool = True):
    """Echo 뇌 모니터링 시작"""
    monitor = get_brain_monitor()
    monitor.start_monitoring(live_visualization)
    return monitor


def stop_echo_brain_monitoring():
    """Echo 뇌 모니터링 정지"""
    monitor = get_brain_monitor()
    monitor.stop_monitoring()


def update_echo_brain_signature(signature: str, emotion: str = None):
    """Echo 뇌 시그니처 상태 업데이트"""
    monitor = get_brain_monitor()
    monitor.update_signature_state(signature, emotion)


def update_echo_brain_emotion(emotion: str, intensity: float = 0.5):
    """Echo 뇌 감정 상태 업데이트"""
    monitor = get_brain_monitor()
    monitor.update_emotion_state(emotion, intensity)


def update_echo_brain_agents(agent_activities: Dict[str, float]):
    """Echo 뇌 에이전트 활동 업데이트"""
    monitor = get_brain_monitor()
    monitor.update_agent_activity(agent_activities)


if __name__ == "__main__":
    # 테스트 실행
    print("🧠 Echo Brain Monitor 테스트 시작...")

    monitor = EchoBrainMonitor()

    # 테스트 상태 업데이트
    monitor.update_signature_state("aurora", "joy")
    monitor.update_emotion_state("joy", 0.8)
    monitor.update_agent_activity({"web": 0.7, "document": 0.5, "api": 0.3})
    monitor.update_conversation_state(
        "interactive", "processing", "안녕하세요", "안녕하세요! 반가워요!"
    )

    # 스냅샷 저장
    filename = monitor.save_current_brain_state()
    print(f"🧠 뇌 상태 스냅샷 저장: {filename}")

    # 상태 요약
    summary = monitor.get_state_summary()
    print(f"📊 상태 요약: {summary}")

    print("✅ Echo Brain Monitor 테스트 완료")
