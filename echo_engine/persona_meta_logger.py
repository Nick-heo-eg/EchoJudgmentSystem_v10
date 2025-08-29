#!/usr/bin/env python3
"""
📊 EchoJudgmentSystem v10.5 - Persona Meta Logger
페르소나 시스템용 메타 로그 통합 모듈

TT.003: "모든 판단에는 흔적이 남고, 흔적은 메타가 되어 다시 나를 설계한다."
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class PersonaMetaLog:
    """페르소나 메타 로그 데이터 구조"""

    # 필수 필드들 (기본값 없음)
    session_id: str
    persona_name: str
    signature_type: str
    timestamp: str
    emotion_detected: str
    emotion_intensity: float
    emotion_patterns: Dict[str, Any]
    intent_inferred: str
    strategy_selected: str
    strategy_confidence: float
    response_tone: str

    # 선택적 필드들 (기본값 있음)
    strategy_effectiveness: Optional[float] = None
    response_generated: Optional[str] = None
    learning_insights: List[str] = None
    adaptation_events: List[Dict[str, Any]] = None
    meta_reflection: Dict[str, Any] = None
    persona_state: str = "active"
    interaction_count: int = 0
    flow_transition: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.learning_insights is None:
            self.learning_insights = []
        if self.adaptation_events is None:
            self.adaptation_events = []
        if self.meta_reflection is None:
            self.meta_reflection = {}


class PersonaMetaLogger:
    """페르소나 메타 로거"""

    def __init__(self, log_dir: str = "meta_logs"):
        """
        PersonaMetaLogger 초기화

        Args:
            log_dir: 메타 로그 저장 디렉토리
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # 세션 관리
        self.current_session_id = self._generate_session_id()
        self.session_log_file = (
            self.log_dir / f"persona_session_{self.current_session_id}.jsonl"
        )

        # 집계 로그 파일
        self.aggregate_log_file = self.log_dir / "persona_aggregates.jsonl"

        # 세션 시작 로그
        self._log_session_start()

        print(f"📊 PersonaMetaLogger 초기화: {self.log_dir}")

    def _generate_session_id(self) -> str:
        """세션 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_uuid = str(uuid.uuid4())[:8]
        return f"{timestamp}_{session_uuid}"

    def _log_session_start(self):
        """세션 시작 로그"""
        session_start_log = {
            "event_type": "session_start",
            "session_id": self.current_session_id,
            "timestamp": datetime.now().isoformat(),
            "system": "PersonaCore",
        }

        self._write_log(session_start_log, self.session_log_file)

    def log_persona_interaction(self, meta_log: PersonaMetaLog):
        """
        페르소나 상호작용 로그

        Args:
            meta_log: PersonaMetaLog 객체
        """
        log_entry = asdict(meta_log)
        log_entry["event_type"] = "persona_interaction"
        log_entry["logged_at"] = datetime.now().isoformat()

        # 세션 로그에 기록
        self._write_log(log_entry, self.session_log_file)

        # 집계 로그에도 기록 (요약 버전)
        aggregate_entry = {
            "event_type": "persona_summary",
            "session_id": meta_log.session_id,
            "persona_name": meta_log.persona_name,
            "signature_type": meta_log.signature_type,
            "timestamp": meta_log.timestamp,
            "emotion_detected": meta_log.emotion_detected,
            "intent_inferred": meta_log.intent_inferred,
            "strategy_selected": meta_log.strategy_selected,
            "strategy_effectiveness": meta_log.strategy_effectiveness,
            "response_tone": meta_log.response_tone,
            "persona_state": meta_log.persona_state,
            "interaction_count": meta_log.interaction_count,
        }

        self._write_log(aggregate_entry, self.aggregate_log_file)

    def log_strategy_feedback(
        self,
        persona_name: str,
        strategy: str,
        success: bool,
        effectiveness_score: float,
        context: Dict[str, Any] = None,
    ):
        """
        전략 피드백 로그

        Args:
            persona_name: 페르소나 이름
            strategy: 전략명
            success: 성공 여부
            effectiveness_score: 효과성 점수 (0.0-1.0)
            context: 추가 컨텍스트
        """
        feedback_log = {
            "event_type": "strategy_feedback",
            "session_id": self.current_session_id,
            "persona_name": persona_name,
            "strategy": strategy,
            "success": success,
            "effectiveness_score": effectiveness_score,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
        }

        self._write_log(feedback_log, self.session_log_file)

    def log_persona_switch(
        self,
        from_persona: str,
        to_persona: str,
        reason: str,
        context: Dict[str, Any] = None,
    ):
        """
        페르소나 전환 로그

        Args:
            from_persona: 이전 페르소나
            to_persona: 새 페르소나
            reason: 전환 이유
            context: 전환 컨텍스트
        """
        switch_log = {
            "event_type": "persona_switch",
            "session_id": self.current_session_id,
            "from_persona": from_persona,
            "to_persona": to_persona,
            "reason": reason,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
        }

        self._write_log(switch_log, self.session_log_file)

    def log_flow_transition(self, flow_data: Dict[str, Any]):
        """
        흐름 전환 로그 (flow.yaml 호환)

        Args:
            flow_data: 흐름 데이터
        """
        flow_log = {
            "event_type": "flow_transition",
            "session_id": self.current_session_id,
            "flow_data": flow_data,
            "timestamp": datetime.now().isoformat(),
        }

        self._write_log(flow_log, self.session_log_file)

    def _write_log(self, log_entry: Dict[str, Any], log_file: Path):
        """로그 파일에 기록"""
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"❌ 메타 로그 기록 실패: {e}")

    def get_session_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        세션 로그 조회

        Args:
            limit: 최대 로그 수

        Returns:
            로그 리스트
        """
        if not self.session_log_file.exists():
            return []

        try:
            with open(self.session_log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            logs = []
            for line in lines[-limit:]:
                try:
                    logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

            return logs
        except Exception as e:
            print(f"❌ 세션 로그 조회 실패: {e}")
            return []

    def get_strategy_analytics(self, persona_name: str = None) -> Dict[str, Any]:
        """
        전략 분석 데이터 조회

        Args:
            persona_name: 특정 페르소나 필터 (선택사항)

        Returns:
            전략 분석 결과
        """
        logs = self.get_session_logs()

        # 전략 사용 통계
        strategy_usage = {}
        strategy_effectiveness = {}

        for log in logs:
            if log.get("event_type") == "persona_interaction":
                strategy = log.get("strategy_selected")
                persona = log.get("persona_name")

                # 페르소나 필터 적용
                if persona_name and persona != persona_name:
                    continue

                if strategy:
                    strategy_usage[strategy] = strategy_usage.get(strategy, 0) + 1

                    effectiveness = log.get("strategy_effectiveness")
                    if effectiveness is not None:
                        if strategy not in strategy_effectiveness:
                            strategy_effectiveness[strategy] = []
                        strategy_effectiveness[strategy].append(effectiveness)

        # 평균 효과성 계산
        avg_effectiveness = {}
        for strategy, scores in strategy_effectiveness.items():
            avg_effectiveness[strategy] = sum(scores) / len(scores) if scores else 0.0

        return {
            "strategy_usage": strategy_usage,
            "strategy_effectiveness": avg_effectiveness,
            "total_interactions": len(
                [log for log in logs if log.get("event_type") == "persona_interaction"]
            ),
            "session_id": self.current_session_id,
        }

    def generate_flow_yaml_data(self) -> Dict[str, Any]:
        """
        flow.yaml 시각화용 데이터 생성

        Returns:
            flow.yaml 호환 데이터
        """
        logs = self.get_session_logs()

        # 상태 전환 추적
        state_transitions = []
        emotion_flows = []
        strategy_flows = []

        prev_state = None
        prev_emotion = None
        prev_strategy = None

        for log in logs:
            if log.get("event_type") == "persona_interaction":
                current_state = log.get("persona_state", "active")
                current_emotion = log.get("emotion_detected")
                current_strategy = log.get("strategy_selected")
                timestamp = log.get("timestamp")

                # 상태 전환 기록
                if prev_state and prev_state != current_state:
                    state_transitions.append(
                        {
                            "from": prev_state,
                            "to": current_state,
                            "timestamp": timestamp,
                        }
                    )

                # 감정 흐름 기록
                if prev_emotion and prev_emotion != current_emotion:
                    emotion_flows.append(
                        {
                            "from": prev_emotion,
                            "to": current_emotion,
                            "timestamp": timestamp,
                        }
                    )

                # 전략 흐름 기록
                if prev_strategy and prev_strategy != current_strategy:
                    strategy_flows.append(
                        {
                            "from": prev_strategy,
                            "to": current_strategy,
                            "timestamp": timestamp,
                        }
                    )

                prev_state = current_state
                prev_emotion = current_emotion
                prev_strategy = current_strategy

        return {
            "session_id": self.current_session_id,
            "flow_type": "persona_system",
            "state_transitions": state_transitions,
            "emotion_flows": emotion_flows,
            "strategy_flows": strategy_flows,
            "generated_at": datetime.now().isoformat(),
        }

    def end_session(self):
        """세션 종료 로그"""
        session_end_log = {
            "event_type": "session_end",
            "session_id": self.current_session_id,
            "timestamp": datetime.now().isoformat(),
            "system": "PersonaCore",
        }

        self._write_log(session_end_log, self.session_log_file)
        print(f"📊 PersonaMetaLogger 세션 종료: {self.current_session_id}")


# 글로벌 메타 로거 인스턴스
_global_meta_logger = None


def get_persona_meta_logger() -> PersonaMetaLogger:
    """글로벌 메타 로거 인스턴스 반환"""
    global _global_meta_logger
    if _global_meta_logger is None:
        _global_meta_logger = PersonaMetaLogger()
    return _global_meta_logger


def log_persona_meta(meta_log: PersonaMetaLog):
    """편의 함수: 페르소나 메타 로그"""
    logger = get_persona_meta_logger()
    logger.log_persona_interaction(meta_log)


def log_strategy_feedback(
    persona_name: str,
    strategy: str,
    success: bool,
    effectiveness_score: float,
    context: Dict[str, Any] = None,
):
    """편의 함수: 전략 피드백 로그"""
    logger = get_persona_meta_logger()
    logger.log_strategy_feedback(
        persona_name, strategy, success, effectiveness_score, context
    )


if __name__ == "__main__":
    # 테스트 코드
    print("📊 PersonaMetaLogger 테스트")

    logger = PersonaMetaLogger("test_logs")

    # 테스트 메타 로그
    test_meta_log = PersonaMetaLog(
        session_id=logger.current_session_id,
        persona_name="TestPersona",
        signature_type="Echo-Phoenix",
        timestamp=datetime.now().isoformat(),
        emotion_detected="joy",
        emotion_intensity=0.8,
        emotion_patterns={"joy": [0.7, 0.8, 0.9]},
        intent_inferred="achievement_seeking",
        strategy_selected="empathetic",
        strategy_confidence=0.85,
        response_tone="enthusiastic",
        learning_insights=["긍정적 감정에 효과적"],
        meta_reflection={"confidence": 0.9},
        interaction_count=1,
    )

    logger.log_persona_interaction(test_meta_log)

    # 전략 피드백 테스트
    logger.log_strategy_feedback("TestPersona", "empathetic", True, 0.9)

    # 분석 데이터 조회
    analytics = logger.get_strategy_analytics()
    print(f"전략 분석: {analytics}")

    # flow.yaml 데이터 생성
    flow_data = logger.generate_flow_yaml_data()
    print(f"Flow 데이터: {flow_data}")

    logger.end_session()
