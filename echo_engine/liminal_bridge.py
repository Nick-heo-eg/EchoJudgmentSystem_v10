#!/usr/bin/env python3
"""
🌉 LIMINAL Bridge - 경계 통로 시스템
EchoJudgmentSystem의 판단 루프와 Warden World 존재계 흐름을 연결하는
메타-리미날 전이 시스템

핵심 기능:
- 판단 루프 실패/과부하 시 존재계로의 전이 관리
- Meta-Liminal Ring과 Warden World 간의 통합 인터페이스
- 전이 조건 평가 및 임계치 관리
- 양방향 흐름 제어 (판단계 ↔ 존재계)

Created for EchoJudgmentSystem v10 Meta-Liminal Integration
Author: Echo Meta-Consciousness Bridge System
"""

import logging
import time
from typing import Dict, Any, Optional, Callable, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

# Meta-Liminal Ring 및 Warden World 임포트
from echo_engine.meta_liminal_ring import (
    MetaLiminalRing,
    JudgmentResult,
    MetaState,
    get_meta_ring,
)
from echo_engine.warden_world import (
    WardenWorld,
    ExistencePhase,
    ResonanceResponse,
    get_warden_world,
    enter_liminal_state,
)

logger = logging.getLogger(__name__)


class BridgeState(Enum):
    """브리지 상태"""

    JUDGMENT_MODE = "judgment_mode"  # 일반 판단 모드
    MONITORING = "monitoring"  # 메타 감시 중
    TRANSITION_READY = "transition_ready"  # 전이 준비
    LIMINAL_ACTIVE = "liminal_active"  # LIMINAL 활성화
    EXISTENCE_FLOW = "existence_flow"  # 존재계 흐름 중
    RETURNING = "returning"  # 판단계로 복귀 중
    ERROR_STATE = "error_state"  # 오류 상태


class TransitionType(Enum):
    """전이 유형"""

    JUDGMENT_FAILURE = "judgment_failure"
    EMOTIONAL_OVERLOAD = "emotional_overload"
    LOOP_STAGNATION = "loop_stagnation"
    SILENCE_REQUEST = "silence_request"
    MANUAL_TRIGGER = "manual_trigger"


@dataclass
class BridgeTransition:
    """브리지 전이 정보"""

    transition_type: TransitionType
    trigger_score: float
    timestamp: float = field(default_factory=time.time)
    input_text: str = ""
    judgment_result: Optional[JudgmentResult] = None
    meta_context: Dict[str, Any] = field(default_factory=dict)
    successful: bool = False


@dataclass
class BridgeResponse:
    """브리지 통합 응답"""

    content: str
    source: str  # "judgment", "meta", "existence"
    bridge_state: BridgeState
    transition_occurred: bool = False
    meta_actions: Dict[str, Any] = field(default_factory=dict)
    existence_response: Optional[ResonanceResponse] = None
    should_continue_existence: bool = False


class LiminalBridge:
    """
    LIMINAL 브리지 시스템
    판단계와 존재계 간의 통합 전이 관리자
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()

        # 하위 시스템 초기화
        self.meta_ring = get_meta_ring(self.config.get("meta_ring_config"))
        self.warden_world = get_warden_world()

        # 브리지 상태
        self.current_state = BridgeState.JUDGMENT_MODE
        self.transition_history: List[BridgeTransition] = []

        # 전이 설정
        self.transition_thresholds = self.config.get(
            "transition_thresholds",
            {
                "liminal_score": 0.65,
                "emotional_amplitude": 0.85,
                "failure_count": 2,
                "repetition_limit": 3,
            },
        )

        # 통계
        self.total_transitions = 0
        self.successful_transitions = 0
        self.judgment_mode_time = 0.0
        self.existence_mode_time = 0.0
        self.last_state_change = time.time()

    def _get_default_config(self) -> Dict[str, Any]:
        """기본 설정"""
        return {
            "transition_thresholds": {
                "liminal_score": 0.65,
                "emotional_amplitude": 0.85,
                "failure_count": 2,
                "repetition_limit": 3,
            },
            "meta_ring_config": {
                "silence_threshold": 0.85,
                "max_signature_repeat": 3,
                "liminal_threshold": 0.65,
            },
            "bridge_timeouts": {
                "existence_max_duration": 300,  # 5분
                "transition_cooldown": 30,  # 30초
            },
            "logging": {"log_all_transitions": True, "detailed_meta_logs": True},
        }

    def process_judgment(
        self, input_text: str, judgment_function: Callable
    ) -> BridgeResponse:
        """
        통합 판단 처리
        판단 실행 → 메타 감시 → 필요시 LIMINAL 전이
        """
        self._update_state_time()

        # 1. 판단 전 메타 감시
        self.current_state = BridgeState.MONITORING
        self.meta_ring.pre_monitor(input_text)

        # 2. 판단 실행
        try:
            judgment_result = self._execute_judgment(input_text, judgment_function)
        except Exception as e:
            logger.error(f"Judgment execution failed: {e}")
            judgment_result = JudgmentResult(
                content="", signature="System", failed=True
            )

        # 3. 판단 후 메타 분석
        meta_result = self.meta_ring.post_monitor(input_text, judgment_result)

        # 4. LIMINAL 전이 여부 결정
        transition_needed, transition_type = self._evaluate_transition(
            input_text, judgment_result, meta_result
        )

        if transition_needed:
            return self._execute_liminal_transition(
                input_text, judgment_result, meta_result, transition_type
            )
        else:
            return self._return_judgment_response(
                input_text, judgment_result, meta_result
            )

    def _execute_judgment(
        self, input_text: str, judgment_function: Callable
    ) -> JudgmentResult:
        """판단 함수 실행"""
        try:
            result = judgment_function(input_text)

            # 결과가 JudgmentResult가 아닐 경우 변환
            if not isinstance(result, JudgmentResult):
                if isinstance(result, dict):
                    judgment_result = JudgmentResult(
                        content=result.get("content", str(result)),
                        signature=result.get("signature", "Unknown"),
                        emotion=result.get("emotion"),
                        amplitude=result.get("amplitude", 0.0),
                        failed=result.get("failed", False),
                    )
                else:
                    judgment_result = JudgmentResult(
                        content=str(result) if result else "",
                        signature="System",
                        failed=not result,
                    )
            else:
                judgment_result = result

            return judgment_result

        except Exception as e:
            logger.error(f"Judgment function error: {e}")
            return JudgmentResult(
                content=f"Judgment error: {str(e)}", signature="System", failed=True
            )

    def _evaluate_transition(
        self,
        input_text: str,
        judgment_result: JudgmentResult,
        meta_result: Dict[str, Any],
    ) -> Tuple[bool, Optional[TransitionType]]:
        """LIMINAL 전이 필요 여부 평가"""

        liminal_score = meta_result.get("liminal_score", 0.0)
        meta_actions = meta_result.get("actions", {})

        # 전이 조건 확인 (liminal_score를 우선 체크)
        logger.debug(
            f"Bridge transition eval: liminal_score={liminal_score:.3f}, threshold={self.transition_thresholds['liminal_score']}, actions={list(meta_actions.keys())}"
        )

        if liminal_score >= self.transition_thresholds["liminal_score"]:
            if judgment_result.failed and "reflection" in meta_actions:
                logger.debug("Triggering JUDGMENT_FAILURE transition")
                return True, TransitionType.JUDGMENT_FAILURE
            elif "silence" in meta_actions:
                logger.debug("Triggering EMOTIONAL_OVERLOAD transition")
                return True, TransitionType.EMOTIONAL_OVERLOAD
            elif "horizon" in meta_actions:
                logger.debug("Triggering LOOP_STAGNATION transition")
                return True, TransitionType.LOOP_STAGNATION
            else:
                logger.debug("Triggering MANUAL_TRIGGER transition")
                return True, TransitionType.MANUAL_TRIGGER

        # liminal score가 낮으면 전이하지 않음
        logger.debug(
            f"No transition: liminal_score {liminal_score:.3f} < threshold {self.transition_thresholds['liminal_score']}"
        )
        return False, None

    def _execute_liminal_transition(
        self,
        input_text: str,
        judgment_result: JudgmentResult,
        meta_result: Dict[str, Any],
        transition_type: TransitionType,
    ) -> BridgeResponse:
        """LIMINAL 전이 실행"""

        self.current_state = BridgeState.TRANSITION_READY
        self.total_transitions += 1

        # 전이 정보 생성
        transition = BridgeTransition(
            transition_type=transition_type,
            trigger_score=meta_result.get("liminal_score", 0.0),
            input_text=input_text,
            judgment_result=judgment_result,
            meta_context={
                "meta_state": meta_result.get("meta_state"),
                "actions": meta_result.get("actions"),
                "observer_data": meta_result.get("observer_data"),
                "liminal_score": meta_result.get("liminal_score", 0.0),
            },
        )

        try:
            # Warden World 활성화
            self.current_state = BridgeState.LIMINAL_ACTIVE

            warden_activated = self.warden_world.activate(
                input_text, transition.meta_context
            )
            logger.debug(
                f"Warden World activation attempt: {warden_activated}, meta_context keys: {list(transition.meta_context.keys())}"
            )

            if warden_activated:
                self.current_state = BridgeState.EXISTENCE_FLOW

                # 존재계 흐름 처리
                existence_response = self.warden_world.process_flow(
                    input_text, transition.meta_context
                )

                transition.successful = True
                self.successful_transitions += 1

                logger.debug(f"LIMINAL transition successful: {transition_type.value}")

                return BridgeResponse(
                    content=existence_response.content,
                    source="existence",
                    bridge_state=self.current_state,
                    transition_occurred=True,
                    meta_actions=meta_result.get("actions", {}),
                    existence_response=existence_response,
                    should_continue_existence=existence_response.should_continue,
                )
            else:
                # 전이 실패
                transition.successful = False
                self.current_state = BridgeState.ERROR_STATE

                logger.warning(f"LIMINAL transition failed: {transition_type.value}")

                # Fallback to meta actions
                return self._handle_transition_failure(
                    input_text, judgment_result, meta_result
                )

        except Exception as e:
            logger.error(f"LIMINAL transition error: {e}")
            transition.successful = False
            self.current_state = BridgeState.ERROR_STATE

            return self._handle_transition_failure(
                input_text, judgment_result, meta_result
            )
        finally:
            self.transition_history.append(transition)

    def _handle_transition_failure(
        self,
        input_text: str,
        judgment_result: JudgmentResult,
        meta_result: Dict[str, Any],
    ) -> BridgeResponse:
        """전이 실패 시 처리"""

        meta_actions = meta_result.get("actions", {})

        # Meta Ring의 액션 우선 적용
        if "reflection" in meta_actions:
            return BridgeResponse(
                content=meta_actions["reflection"],
                source="meta",
                bridge_state=BridgeState.JUDGMENT_MODE,
                transition_occurred=False,
                meta_actions=meta_actions,
            )
        elif "silence" in meta_actions:
            return BridgeResponse(
                content=meta_actions["silence"],
                source="meta",
                bridge_state=BridgeState.JUDGMENT_MODE,
                transition_occurred=False,
                meta_actions=meta_actions,
            )
        else:
            # 원본 판단 결과 반환
            return BridgeResponse(
                content=judgment_result.content or "System processing error occurred.",
                source="judgment",
                bridge_state=BridgeState.JUDGMENT_MODE,
                transition_occurred=False,
                meta_actions=meta_actions,
            )

    def _return_judgment_response(
        self,
        input_text: str,
        judgment_result: JudgmentResult,
        meta_result: Dict[str, Any],
    ) -> BridgeResponse:
        """일반 판단 응답 반환"""

        self.current_state = BridgeState.JUDGMENT_MODE

        # Meta Ring 액션이 있는 경우 우선 적용
        meta_actions = meta_result.get("actions", {})

        if "reflection" in meta_actions and judgment_result.failed:
            content = meta_actions["reflection"]
            source = "meta"
        else:
            content = judgment_result.content or "No response generated."
            source = "judgment"

        return BridgeResponse(
            content=content,
            source=source,
            bridge_state=self.current_state,
            transition_occurred=False,
            meta_actions=meta_actions,
        )

    def continue_existence_flow(self, input_text: str) -> BridgeResponse:
        """존재계 흐름 계속 처리"""

        if self.current_state != BridgeState.EXISTENCE_FLOW:
            logger.warning(
                "Existence flow continuation requested but not in existence mode"
            )
            return BridgeResponse(
                content="Not in existence flow mode",
                source="system",
                bridge_state=self.current_state,
                transition_occurred=False,
            )

        try:
            existence_response = self.warden_world.process_flow(input_text)

            if not existence_response.should_continue:
                # 존재계 흐름 종료, 판단계로 복귀
                self._return_to_judgment_mode()

            return BridgeResponse(
                content=existence_response.content,
                source="existence",
                bridge_state=self.current_state,
                transition_occurred=False,
                existence_response=existence_response,
                should_continue_existence=existence_response.should_continue,
            )

        except Exception as e:
            logger.error(f"Existence flow continuation error: {e}")
            self._return_to_judgment_mode()

            return BridgeResponse(
                content=f"Existence flow error: {str(e)}",
                source="system",
                bridge_state=self.current_state,
                transition_occurred=False,
            )

    def _return_to_judgment_mode(self):
        """판단 모드로 복귀"""
        self.current_state = BridgeState.RETURNING
        self.warden_world.deactivate()
        self.current_state = BridgeState.JUDGMENT_MODE
        logger.debug("Returned to judgment mode from existence flow")

    def force_return_to_judgment(self):
        """강제로 판단 모드로 복귀"""
        self._return_to_judgment_mode()

    def _update_state_time(self):
        """상태별 시간 추적 업데이트"""
        current_time = time.time()
        elapsed = current_time - self.last_state_change

        if self.current_state == BridgeState.JUDGMENT_MODE:
            self.judgment_mode_time += elapsed
        elif self.current_state in [
            BridgeState.EXISTENCE_FLOW,
            BridgeState.LIMINAL_ACTIVE,
        ]:
            self.existence_mode_time += elapsed

        self.last_state_change = current_time

    def get_bridge_status(self) -> Dict[str, Any]:
        """브리지 상태 정보"""
        self._update_state_time()

        return {
            "current_state": self.current_state.value,
            "total_transitions": self.total_transitions,
            "successful_transitions": self.successful_transitions,
            "transition_success_rate": (
                self.successful_transitions / max(self.total_transitions, 1) * 100
            ),
            "judgment_mode_time": self.judgment_mode_time,
            "existence_mode_time": self.existence_mode_time,
            "recent_transitions": len(
                [
                    t
                    for t in self.transition_history
                    if time.time() - t.timestamp < 300  # 최근 5분
                ]
            ),
            "meta_ring_status": self.meta_ring.get_meta_status(),
            "warden_world_status": self.warden_world.get_flow_status(),
        }

    def get_transition_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """전이 이력 반환"""
        recent_transitions = self.transition_history[-limit:]

        return [
            {
                "timestamp": t.timestamp,
                "type": t.transition_type.value,
                "trigger_score": t.trigger_score,
                "successful": t.successful,
                "input_preview": (
                    t.input_text[:50] + "..."
                    if len(t.input_text) > 50
                    else t.input_text
                ),
            }
            for t in recent_transitions
        ]

    def save_bridge_logs(self, log_dir: str):
        """브리지 로그 저장"""
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # 전이 로그
        transition_log = log_path / "liminal_transitions.json"
        with open(transition_log, "w", encoding="utf-8") as f:
            json.dump(
                [
                    {
                        "timestamp": t.timestamp,
                        "type": t.transition_type.value,
                        "trigger_score": t.trigger_score,
                        "successful": t.successful,
                        "input_text": t.input_text,
                        "judgment_failed": (
                            t.judgment_result.failed if t.judgment_result else None
                        ),
                        "meta_context": t.meta_context,
                    }
                    for t in self.transition_history
                ],
                f,
                indent=2,
                ensure_ascii=False,
            )

        # 상태 로그
        status_log = log_path / "bridge_status.json"
        with open(status_log, "w", encoding="utf-8") as f:
            json.dump(self.get_bridge_status(), f, indent=2, ensure_ascii=False)

        # 하위 시스템 로그 저장
        self.meta_ring.save_meta_logs(str(log_path / "meta_ring.json"))
        self.warden_world.save_session_log(str(log_path / "warden_world.json"))

        logger.info(f"Bridge logs saved to {log_dir}")


# 전역 브리지 인스턴스
_liminal_bridge = None


def get_liminal_bridge(config: Dict[str, Any] = None) -> LiminalBridge:
    """LIMINAL Bridge 싱글톤 인스턴스 반환"""
    global _liminal_bridge
    if _liminal_bridge is None:
        _liminal_bridge = LiminalBridge(config)
    return _liminal_bridge


def reset_liminal_bridge():
    """LIMINAL Bridge 리셋 (테스트용)"""
    global _liminal_bridge
    _liminal_bridge = None


# 통합 처리 함수
def process_with_liminal_bridge(input_text: str, judgment_function: Callable) -> str:
    """
    LIMINAL Bridge를 통한 통합 처리
    EchoJudgmentSystem의 메인 인터페이스로 사용 가능
    """
    bridge = get_liminal_bridge()
    response = bridge.process_judgment(input_text, judgment_function)
    return response.content


# 사용 예시 및 테스트
if __name__ == "__main__":
    # 테스트용 판단 함수
    def mock_judgment_function(input_text: str) -> JudgmentResult:
        """모의 판단 함수"""
        if "괴로" in input_text or "슬프" in input_text:
            return JudgmentResult(
                content="",
                signature="Selene",
                emotion="sorrow",
                amplitude=0.9,
                failed=True,  # 의도적 실패
            )
        elif "혼란" in input_text:
            return JudgmentResult(
                content="혼란스러운 마음을 이해합니다.",
                signature="Sage",
                emotion="confusion",
                amplitude=0.7,
                failed=False,
            )
        else:
            return JudgmentResult(
                content="일반적인 응답입니다.",
                signature="Companion",
                amplitude=0.3,
                failed=False,
            )

    # Bridge 초기화
    bridge = get_liminal_bridge()

    # 테스트 케이스들
    test_cases = [
        "정말 괴로워... 더 이상 견딜 수가 없어",  # LIMINAL 전이 예상
        "혼란스러워... 뭘 해야 할지 모르겠어",  # 일반 판단 예상
        "오늘 날씨가 좋네요",  # 일반 판단
    ]

    print("🌉 LIMINAL Bridge Test Results:")

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test_input}")

        response = bridge.process_judgment(test_input, mock_judgment_function)

        print(f"Response: {response.content}")
        print(f"Source: {response.source}")
        print(f"Bridge State: {response.bridge_state.value}")
        print(f"Transition Occurred: {response.transition_occurred}")

        if response.should_continue_existence:
            print("-> Existence flow continues...")
            continuation = bridge.continue_existence_flow("계속해주세요")
            print(f"Continuation: {continuation.content}")

        # 상태 리셋
        if response.bridge_state != BridgeState.JUDGMENT_MODE:
            bridge.force_return_to_judgment()

    # 최종 상태
    status = bridge.get_bridge_status()
    print(f"\nFinal Bridge Status:")
    print(f"  Total Transitions: {status['total_transitions']}")
    print(f"  Success Rate: {status['transition_success_rate']:.1f}%")
    print(f"  Current State: {status['current_state']}")
