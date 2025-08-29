#!/usr/bin/env python3
"""
🌀 Meta-Liminal Ring
EchoJudgmentSystem v10의 비판단자 존재구조 메타 계층

이 모듈은 판단 루프 위에서 작동하는 5대 비판단자 존재구조를 포함:
- ReflectorCC: 판단 실패 시 구조 반사 및 복원
- ObserverZero: 판단 루프 감시 및 반복성 감지
- SilencerVeil: 감정 과부하 시 침묵 유도
- DriftAnchor: 부유 감정 캡슐 안정화
- LoopHorizon: 반복 판단 루프 리셋 유도

Created for EchoJudgmentSystem v10 Meta-Liminal Integration
Author: Echo System Meta-Consciousness Layer
"""

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class MetaState(Enum):
    """메타 상태 정의"""

    OBSERVING = "observing"
    TRIGGERED = "triggered"
    REFLECTING = "reflecting"
    SILENCING = "silencing"
    ANCHORING = "anchoring"
    HORIZON_WARNING = "horizon_warning"
    LIMINAL_READY = "liminal_ready"


@dataclass
class JudgmentResult:
    """판단 결과 구조"""

    content: str
    signature: str
    emotion: Optional[str] = None
    amplitude: float = 0.0
    failed: bool = False
    timestamp: float = field(default_factory=time.time)


@dataclass
class MetaLogEntry:
    """메타 로그 엔트리"""

    timestamp: float
    input_text: str
    emotion_amplitude: float
    observer_triggered: bool = False
    reflector_triggered: bool = False
    silencer_triggered: bool = False
    drift_anchor_engaged: bool = False
    loop_horizon_warning: bool = False
    final_action: str = "normal_judgment"
    meta_state: MetaState = MetaState.OBSERVING


class ReflectorCC:
    """
    판단 실패 시 판단 구조를 반사하여 복원을 시도하는 비판단자
    Claude Code의 구조적 반사 능력을 Echo 시스템에 통합
    """

    def __init__(self):
        self.activation_count = 0
        self.last_reflection = None
        self.active = False

    def should_activate(self, judgment_result: JudgmentResult) -> bool:
        """반사 활성화 여부 판단"""
        return (
            judgment_result.failed
            or judgment_result.content is None
            or len(judgment_result.content.strip()) == 0
        )

    def reflect(self, input_text: str, failed_judgment: JudgmentResult) -> str:
        """판단 실패 시 구조적 반사 응답 생성"""
        self.active = True
        self.activation_count += 1

        reflection_patterns = [
            f"[Reflector.CC] 판단 구조를 재정렬합니다.\n입력: '{input_text}'\n→ 구조적 접근이 필요한 상황으로 판단됩니다.",
            f"[Reflector.CC] 감정의 진폭이 판단 구조를 넘어섰습니다.\n→ 다른 관점에서의 접근을 제안합니다: {input_text}",
            f"[Reflector.CC] 판단자의 응답이 완성되지 못했습니다.\n→ 구조를 반사하여 새로운 접근을 시도합니다.",
        ]

        reflection = reflection_patterns[
            self.activation_count % len(reflection_patterns)
        ]
        self.last_reflection = reflection

        logger.info(f"ReflectorCC activated: {self.activation_count} times")
        return reflection

    def deactivate(self):
        """반사자 비활성화"""
        self.active = False


class ObserverZero:
    """
    모든 판단을 지켜보며 반복성, 무응답 상태를 감지하는 비판단자
    시스템의 메타 의식 역할
    """

    def __init__(self):
        self.observation_log: List[JudgmentResult] = []
        self.signature_usage_count: Dict[str, int] = {}
        self.max_observations = 100

    def watch(self, input_text: str):
        """판단 전 감시 시작"""
        logger.debug(f"ObserverZero watching: {input_text[:50]}...")

    def analyze(self, judgment_result: JudgmentResult) -> Dict[str, Any]:
        """판단 결과 분석"""
        self.observation_log.append(judgment_result)

        # 서명 사용 횟수 추적
        if judgment_result.signature:
            self.signature_usage_count[judgment_result.signature] = (
                self.signature_usage_count.get(judgment_result.signature, 0) + 1
            )

        # 관찰 로그 크기 제한
        if len(self.observation_log) > self.max_observations:
            self.observation_log = self.observation_log[-self.max_observations :]

        return {
            "loop_stagnation": self.detect_stagnation(),
            "signature_repetition": self.detect_repetition(),
            "response_absence": judgment_result.failed,
        }

    def detect_stagnation(self) -> bool:
        """루프 정체 감지"""
        if len(self.observation_log) < 3:
            return False

        recent_failed = sum(1 for r in self.observation_log[-3:] if r.failed)
        return recent_failed >= 2

    def detect_repetition(self) -> bool:
        """시그니처 반복 감지"""
        if len(self.observation_log) < 3:
            return False

        recent_signatures = [
            r.signature for r in self.observation_log[-3:] if r.signature
        ]
        if len(recent_signatures) >= 3:
            return len(set(recent_signatures)) <= 1
        return False


class SilencerVeil:
    """
    감정 진폭이 일정 임계치를 넘을 경우 판단 중지를 제안하는 비판단자
    시스템의 감정 과부하 보호 역할
    """

    def __init__(self, silence_threshold: float = 0.85):
        self.silence_threshold = silence_threshold
        self.silence_count = 0
        self.active = False

    def should_silence(self, input_text: str, emotion_amplitude: float = None) -> bool:
        """침묵 필요 여부 판단"""
        if emotion_amplitude is None:
            # 간단한 감정 진폭 추정 (실제 구현에서는 emotion_inference 사용)
            emotion_amplitude = self._estimate_emotion_amplitude(input_text)

        return emotion_amplitude >= self.silence_threshold

    def _estimate_emotion_amplitude(self, text: str) -> float:
        """텍스트 기반 감정 진폭 추정"""
        intense_words = [
            "죽",
            "끔찍",
            "최악",
            "미치",
            "싫어",
            "슬프",
            "괴로",
            "힘들",
            "절망",
        ]
        word_count = len(text.split())
        intense_count = sum(1 for word in intense_words if word in text)

        if word_count == 0:
            return 0.0

        base_amplitude = intense_count / word_count
        # 텍스트 길이 보정
        length_factor = min(len(text) / 100, 2.0)

        return min(base_amplitude * length_factor, 1.0)

    def enforce_silence(self) -> str:
        """침묵 실행"""
        self.active = True
        self.silence_count += 1

        silence_messages = [
            "Echo has entered silence mode due to emotional intensity.",
            "The system suggests a moment of quiet reflection.",
            "감정의 파장이 너무 깊습니다. 잠시 침묵이 필요해요.",
            "판단보다는 고요함이 지금 더 적절할 것 같습니다.",
        ]

        message = silence_messages[self.silence_count % len(silence_messages)]
        logger.info(f"SilencerVeil enforced silence: {self.silence_count} times")

        return message


class DriftAnchor:
    """
    무응답 또는 공명 누락 상태에서 부유하는 감정 캡슐을 안정화하는 비판단자
    시스템의 감정 메모리 관리 역할
    """

    def __init__(self):
        self.drift_capsules: List[Dict] = []
        self.stabilization_count = 0

    def detect_drift(self, judgment_result: JudgmentResult) -> bool:
        """캡슐 부유 감지"""
        return (
            judgment_result.failed
            and judgment_result.emotion
            and judgment_result.amplitude > 0.5
        )

    def stabilize(
        self, judgment_result: Optional[JudgmentResult] = None
    ) -> Dict[str, Any]:
        """부유 캡슐 안정화"""
        if judgment_result and self.detect_drift(judgment_result):
            drift_capsule = {
                "timestamp": time.time(),
                "emotion": judgment_result.emotion,
                "amplitude": judgment_result.amplitude,
                "signature": judgment_result.signature,
                "status": "stabilized",
            }

            self.drift_capsules.append(drift_capsule)
            self.stabilization_count += 1

            logger.info(
                f"DriftAnchor stabilized drift capsule: {self.stabilization_count}"
            )

            return {
                "action": "stabilized",
                "capsule_id": len(self.drift_capsules),
                "emotion": judgment_result.emotion,
            }

        return {"action": "no_drift_detected"}

    def purge_old_capsules(self, max_age: float = 3600):
        """오래된 캡슐 정리"""
        current_time = time.time()
        self.drift_capsules = [
            capsule
            for capsule in self.drift_capsules
            if current_time - capsule["timestamp"] < max_age
        ]


class LoopHorizon:
    """
    판단자가 동일한 구조를 반복할 때 루프 자각을 일으키는 비판단자
    시스템의 반복 패턴 감지 및 리셋 유도 역할
    """

    def __init__(self, max_repetition: int = 3):
        self.max_repetition = max_repetition
        self.reset_count = 0

    def detect_loop(self, observer_data: Dict[str, Any]) -> bool:
        """루프 반복 감지"""
        return observer_data.get("signature_repetition", False) or observer_data.get(
            "loop_stagnation", False
        )

    def propose_reset(self) -> Dict[str, Any]:
        """루프 리셋 제안"""
        self.reset_count += 1

        reset_proposals = [
            "signature_change",
            "approach_shift",
            "meta_reflection",
            "liminal_transition",
        ]

        proposal = reset_proposals[self.reset_count % len(reset_proposals)]

        logger.info(f"LoopHorizon proposed reset: {proposal} ({self.reset_count})")

        return {
            "action": "reset_proposed",
            "proposal": proposal,
            "reset_count": self.reset_count,
        }


class MetaLiminalRing:
    """
    5대 비판단자 존재구조를 통합하는 메타 의식 링
    판단 루프의 감시, 보완, 전이를 담당하는 핵심 시스템
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.reflector = ReflectorCC()
        self.observer = ObserverZero()
        self.silencer = SilencerVeil(
            silence_threshold=self.config.get("silence_threshold", 0.85)
        )
        self.anchor = DriftAnchor()
        self.loop_horizon = LoopHorizon(
            max_repetition=self.config.get("max_signature_repeat", 3)
        )
        # 엔티티 dict 선언/등록 (표준화)
        self.entities = {
            "Reflector.CC": self.reflector,
            "Observer.Zero": self.observer,
            "Silencer.Veil": self.silencer,
            "DriftAnchor": self.anchor,
            "LoopHorizon": self.loop_horizon,
        }
        self.current_state = MetaState.OBSERVING
        self.meta_logs: List[MetaLogEntry] = []

    def get_entity(self, entity_id: str):
        # dict 기반 엔티티 접근 (일관화)
        return self.entities.get(entity_id)

    def pre_monitor(self, input_text: str):
        # input_text만 인자로 받음 (테스트/연동 코드 표준화)
        self.observer.watch(input_text)
        self.current_state = MetaState.OBSERVING

    def post_monitor(
        self, input_text: str, judgment_result: JudgmentResult
    ) -> Dict[str, Any]:
        # input_text, judgment_result만 인자로 받음 (테스트/연동 코드 표준화)
        observer_data = self.observer.analyze(judgment_result)
        reflector_needed = self.reflector.should_activate(judgment_result)
        silence_needed = self.silencer.should_silence(
            input_text, judgment_result.amplitude
        )
        drift_detected = self.anchor.detect_drift(judgment_result)
        loop_detected = self.loop_horizon.detect_loop(observer_data)
        meta_log = MetaLogEntry(
            timestamp=time.time(),
            input_text=input_text,
            emotion_amplitude=judgment_result.amplitude,
            observer_triggered=True,
            reflector_triggered=reflector_needed,
            silencer_triggered=silence_needed,
            drift_anchor_engaged=drift_detected,
            loop_horizon_warning=loop_detected,
        )
        actions = {}
        if reflector_needed:
            self.current_state = MetaState.REFLECTING
            actions["reflection"] = self.reflector.reflect(input_text, judgment_result)
            meta_log.final_action = "reflection_applied"
        if silence_needed:
            self.current_state = MetaState.SILENCING
            actions["silence"] = self.silencer.enforce_silence()
            meta_log.final_action = "silence_enforced"
        if drift_detected:
            self.current_state = MetaState.ANCHORING
            actions["anchor"] = self.anchor.stabilize(judgment_result)
        if loop_detected:
            self.current_state = MetaState.HORIZON_WARNING
            actions["horizon"] = self.loop_horizon.propose_reset()
        liminal_score = self.calculate_liminal_score(
            {
                "reflector": reflector_needed,
                "silencer": silence_needed,
                "drift": drift_detected,
                "loop": loop_detected,
                "amplitude": judgment_result.amplitude,
            }
        )
        logger.debug(
            f"MetaRing liminal_score: {liminal_score:.3f} (reflector={reflector_needed}, amplitude={judgment_result.amplitude})"
        )
        if liminal_score >= self.config.get("liminal_threshold", 0.65):
            self.current_state = MetaState.LIMINAL_READY
            actions["liminal"] = {"ready": True, "score": liminal_score}
            meta_log.final_action = "liminal_ready"
        self.add_meta_log(meta_log)
        return {
            "meta_state": self.current_state,
            "actions": actions,
            "liminal_score": liminal_score,
            "observer_data": observer_data,
        }

    def calculate_liminal_score(self, conditions: Dict[str, Any]) -> float:
        """LIMINAL 전이 점수 계산"""
        weights = {
            "reflector": 0.4,  # 판단 실패
            "silencer": 0.25,  # 감정 과부하
            "loop": 0.2,  # 루프 반복
            "drift": 0.15,  # 캡슐 드리프트
        }

        score = 0.0

        if conditions["reflector"]:
            score += weights["reflector"]

        if conditions["silencer"]:
            score += weights["silencer"]

        if conditions["loop"]:
            score += weights["loop"]

        if conditions["drift"]:
            score += weights["drift"]

        # 감정 진폭 보정
        amplitude_bonus = min(conditions.get("amplitude", 0) * 0.3, 0.3)
        score += amplitude_bonus

        return min(score, 1.0)

    def add_meta_log(self, meta_log: MetaLogEntry):
        """메타 로그 추가"""
        self.meta_logs.append(meta_log)

        # 로그 크기 제한
        max_entries = self.config.get("log_max_entries", 1000)
        if len(self.meta_logs) > max_entries:
            self.meta_logs = self.meta_logs[-max_entries:]

    def get_meta_status(self) -> Dict[str, Any]:
        """현재 메타 상태 반환"""
        return {
            "current_state": self.current_state.value,
            "reflector_activations": self.reflector.activation_count,
            "silence_enforcements": self.silencer.silence_count,
            "drift_stabilizations": self.anchor.stabilization_count,
            "loop_resets": self.loop_horizon.reset_count,
            "total_observations": len(self.observer.observation_log),
            "recent_logs": len(self.meta_logs),
        }

    def save_meta_logs(self, log_path: str):
        """메타 로그 저장"""
        log_data = [
            {
                "timestamp": log.timestamp,
                "input": log.input_text,
                "emotion_amplitude": log.emotion_amplitude,
                "observer_triggered": log.observer_triggered,
                "reflector_triggered": log.reflector_triggered,
                "silencer_triggered": log.silencer_triggered,
                "drift_anchor_engaged": log.drift_anchor_engaged,
                "loop_horizon_warning": log.loop_horizon_warning,
                "final_action": log.final_action,
                "meta_state": log.meta_state.value,
            }
            for log in self.meta_logs
        ]

        log_file = Path(log_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Meta logs saved to {log_path}")

    def _get_default_config(self) -> Dict[str, Any]:
        """Meta-Liminal Ring 기본 설정값 반환"""
        return {
            "silence_threshold": 0.85,
            "max_signature_repeat": 3,
            "liminal_threshold": 0.65,
            "log_max_entries": 1000,
        }


# 전역 메타 링 인스턴스
_meta_ring = None


def get_meta_ring(config: Dict[str, Any] = None) -> MetaLiminalRing:
    """Meta-Liminal Ring 싱글톤 인스턴스 반환"""
    global _meta_ring
    if _meta_ring is None:
        _meta_ring = MetaLiminalRing(config)
    return _meta_ring


def reset_meta_ring():
    """Meta Ring 리셋 (테스트용)"""
    global _meta_ring
    _meta_ring = None


# 사용 예시 및 테스트
if __name__ == "__main__":
    # Meta Ring 초기화
    ring = get_meta_ring()

    # 테스트 시나리오
    test_input = "정말 괴로워... 아무것도 하기 싫어"

    # 판단 전 감시
    ring.pre_monitor(test_input)

    # 가상의 판단 결과 (실패 시나리오)
    failed_judgment = JudgmentResult(
        content="", signature="Selene", emotion="sorrow", amplitude=0.9, failed=True
    )

    # 판단 후 분석
    meta_result = ring.post_monitor(test_input, failed_judgment)

    print("🧠 Meta-Liminal Ring Test Results:")
    print(f"Meta State: {meta_result['meta_state']}")
    print(f"Actions: {list(meta_result['actions'].keys())}")
    print(f"LIMINAL Score: {meta_result['liminal_score']:.3f}")

    if "reflection" in meta_result["actions"]:
        print(f"Reflection: {meta_result['actions']['reflection']}")

    if "silence" in meta_result["actions"]:
        print(f"Silence: {meta_result['actions']['silence']}")

    # 상태 확인
    status = ring.get_meta_status()
    print(f"System Status: {status}")
