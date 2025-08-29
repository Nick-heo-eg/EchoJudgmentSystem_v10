#!/usr/bin/env python3
"""
📊 Meta Logger - Meta-Liminal 로깅 시스템
EchoJudgmentSystem v10의 메타 의식 계층 로깅 및 분석 도구

핵심 기능:
- Meta-Liminal Ring 이벤트 로깅
- LIMINAL 전이 추적 및 분석
- Warden World 존재계 흐름 기록
- 실시간 로그 회전 및 압축 관리
- 로그 분석 및 메트릭 생성

Created for EchoJudgmentSystem v10 Meta-Liminal Integration
Author: Echo Meta-Consciousness Logging System
"""

import logging
import json
import time
import gzip
import shutil
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from threading import Lock
import os

logger = logging.getLogger(__name__)


@dataclass
class MetaLogEntry:
    """메타 로그 엔트리 기본 구조"""

    timestamp: float
    log_type: str  # "meta_ring", "liminal_transition", "warden_world", "bridge_status"
    event: str
    data: Dict[str, Any]
    session_id: Optional[str] = None


class MetaLogger:
    """
    Meta-Liminal 통합 로깅 시스템
    모든 메타 이벤트의 중앙 집중식 로깅 관리
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()

        # 로그 디렉토리 설정
        self.log_dir = Path(self.config.get("log_directory", "meta_logs"))
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 로그 파일 경로
        self.log_files = {
            "meta_ring": self.log_dir / "meta_ring.json",
            "liminal_transitions": self.log_dir / "liminal_transitions.json",
            "warden_world": self.log_dir / "warden_world.json",
            "bridge_status": self.log_dir / "bridge_status.json",
        }

        # 로그 버퍼 (메모리 효율성)
        self.log_buffers = {log_type: [] for log_type in self.log_files.keys()}
        self.buffer_locks = {log_type: Lock() for log_type in self.log_files.keys()}

        # 세션 관리
        self.current_session = None
        self.session_logs = {}

        # 로그 회전 설정
        self.max_entries_per_file = self.config.get("max_log_entries_per_file", 10000)
        self.buffer_flush_interval = self.config.get("buffer_flush_interval", 60)  # 1분
        self.last_flush_time = time.time()

        # 로그 레벨 설정
        self.log_levels = self.config.get(
            "log_levels",
            {
                "meta_ring": "INFO",
                "liminal_bridge": "INFO",
                "warden_world": "DEBUG",
                "existence_flow": "DEBUG",
            },
        )

        logger.info("MetaLogger initialized with log directory: %s", self.log_dir)

    def _get_default_config(self) -> Dict[str, Any]:
        """기본 로깅 설정"""
        return {
            "log_directory": "meta_logs",
            "max_log_entries_per_file": 10000,
            "buffer_flush_interval": 60,
            "log_rotation_interval": "daily",
            "compress_old_logs": True,
            "retention_days": 30,
            "session_tracking": True,
            "real_time_flush": False,
            "log_levels": {
                "meta_ring": "INFO",
                "liminal_bridge": "INFO",
                "warden_world": "DEBUG",
                "existence_flow": "DEBUG",
            },
        }

    def start_session(self, session_id: str = None) -> str:
        """새 로그 세션 시작"""
        if session_id is None:
            session_id = f"session_{int(time.time())}"

        self.current_session = session_id
        self.session_logs[session_id] = []

        # 세션별 로그 디렉토리 생성
        session_dir = self.log_dir / session_id
        session_dir.mkdir(exist_ok=True)

        self.log_event(
            "meta_ring",
            "session_started",
            {"session_id": session_id, "start_time": datetime.now().isoformat()},
        )

        logger.info(f"Meta logging session started: {session_id}")
        return session_id

    def end_session(self) -> Optional[str]:
        """현재 세션 종료 및 로그 저장"""
        if not self.current_session:
            return None

        session_id = self.current_session

        self.log_event(
            "meta_ring",
            "session_ended",
            {
                "session_id": session_id,
                "end_time": datetime.now().isoformat(),
                "total_events": len(self.session_logs.get(session_id, [])),
            },
        )

        # 세션 로그 저장
        self._save_session_logs(session_id)

        # 버퍼 강제 플러시
        self.flush_all_buffers()

        # 세션 정리
        if session_id in self.session_logs:
            del self.session_logs[session_id]
        self.current_session = None

        logger.info(f"Meta logging session ended: {session_id}")
        return session_id

    def log_event(self, log_type: str, event: str, data: Dict[str, Any]):
        """메타 이벤트 로깅"""
        if log_type not in self.log_files:
            logger.warning(f"Unknown log type: {log_type}")
            return

        # 로그 엔트리 생성
        entry = MetaLogEntry(
            timestamp=time.time(),
            log_type=log_type,
            event=event,
            data=self._sanitize_log_data(data),
            session_id=self.current_session,
        )

        # 버퍼에 추가
        with self.buffer_locks[log_type]:
            self.log_buffers[log_type].append(asdict(entry))

        # 세션 추적
        if self.current_session and self.current_session in self.session_logs:
            self.session_logs[self.current_session].append(asdict(entry))

        # 실시간 플러시 옵션
        if self.config.get("real_time_flush", False):
            self._flush_buffer(log_type)
        elif self._should_flush():
            self.flush_all_buffers()

    def log_meta_ring_event(self, entity: str, action: str, data: Dict[str, Any]):
        """Meta Ring 특화 이벤트 로깅"""
        self.log_event(
            "meta_ring",
            f"{entity}_{action}",
            {"entity": entity, "action": action, **data},
        )

    def log_liminal_transition(self, transition_data: Dict[str, Any]):
        """LIMINAL 전이 이벤트 로깅"""
        self.log_event(
            "liminal_transitions",
            "transition_attempt",
            {
                "transition_type": transition_data.get("transition_type"),
                "trigger_score": transition_data.get("trigger_score"),
                "successful": transition_data.get("successful", False),
                "input_preview": transition_data.get("input_text", "")[:50],
                "meta_context": transition_data.get("meta_context", {}),
            },
        )

    def log_warden_world_event(self, entity: str, phase: str, data: Dict[str, Any]):
        """Warden World 존재계 이벤트 로깅"""
        self.log_event(
            "warden_world",
            f"{entity}_{phase}",
            {
                "entity": entity,
                "phase": phase,
                "emotion_resonance": data.get("emotion"),
                "depth_achieved": data.get("depth_achieved"),
                "response_preview": (
                    data.get("content", "")[:100] if data.get("content") else None
                ),
                **{k: v for k, v in data.items() if k not in ["content"]},
            },
        )

    def log_bridge_status(self, status_data: Dict[str, Any]):
        """LIMINAL Bridge 상태 로깅"""
        self.log_event(
            "bridge_status",
            "status_update",
            {
                "bridge_state": status_data.get("current_state"),
                "total_transitions": status_data.get("total_transitions"),
                "success_rate": status_data.get("transition_success_rate"),
                "active_time_ratio": self._calculate_active_time_ratio(status_data),
                "recent_activity": status_data.get("recent_transitions", 0),
            },
        )

    def _sanitize_log_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """로그 데이터 정제 (개인정보 보호)"""
        sanitized = {}

        for key, value in data.items():
            if key in ["input_text", "content", "prompt"]:
                # 텍스트는 50자로 제한
                if isinstance(value, str) and len(value) > 50:
                    sanitized[key] = value[:50] + "..."
                else:
                    sanitized[key] = value
            elif key in ["password", "token", "key", "secret"]:
                # 민감 정보 마스킹
                sanitized[key] = "***MASKED***"
            else:
                sanitized[key] = value

        return sanitized

    def _should_flush(self) -> bool:
        """버퍼 플러시 필요 여부 확인"""
        current_time = time.time()
        time_threshold = (
            current_time - self.last_flush_time > self.buffer_flush_interval
        )

        # 크기 기반 플러시 체크
        size_threshold = any(
            len(buffer) >= self.max_entries_per_file // 10
            for buffer in self.log_buffers.values()
        )

        return time_threshold or size_threshold

    def flush_all_buffers(self):
        """모든 로그 버퍼 플러시"""
        for log_type in self.log_files.keys():
            self._flush_buffer(log_type)
        self.last_flush_time = time.time()

    def _flush_buffer(self, log_type: str):
        """특정 로그 타입 버퍼 플러시"""
        with self.buffer_locks[log_type]:
            if not self.log_buffers[log_type]:
                return

            log_file = self.log_files[log_type]

            # 기존 로그 읽기
            existing_logs = []
            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        existing_logs = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Failed to read existing log {log_file}: {e}")
                    existing_logs = []

            # 새 로그 추가
            existing_logs.extend(self.log_buffers[log_type])

            # 로그 회전 체크
            if len(existing_logs) > self.max_entries_per_file:
                self._rotate_log_file(log_type, existing_logs)
            else:
                # 일반 저장
                try:
                    with open(log_file, "w", encoding="utf-8") as f:
                        json.dump(existing_logs, f, indent=2, ensure_ascii=False)
                except IOError as e:
                    logger.error(f"Failed to write log file {log_file}: {e}")

            # 버퍼 초기화
            self.log_buffers[log_type] = []

    def _rotate_log_file(self, log_type: str, logs: List[Dict]):
        """로그 파일 회전"""
        log_file = self.log_files[log_type]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 이전 로그 백업
        backup_file = log_file.with_suffix(f".{timestamp}.json")
        if log_file.exists():
            shutil.move(str(log_file), str(backup_file))

            # 압축 옵션
            if self.config.get("compress_old_logs", True):
                self._compress_log_file(backup_file)

        # 새 로그 저장 (최신 항목만)
        recent_logs = logs[-self.max_entries_per_file // 2 :]  # 절반만 유지
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(recent_logs, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Failed to create rotated log file {log_file}: {e}")

        logger.info(f"Log file rotated: {log_type} -> {backup_file}")

    def _compress_log_file(self, file_path: Path):
        """로그 파일 압축"""
        compressed_path = file_path.with_suffix(file_path.suffix + ".gz")
        try:
            with open(file_path, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # 원본 파일 삭제
            file_path.unlink()
            logger.debug(f"Log file compressed: {file_path} -> {compressed_path}")

        except IOError as e:
            logger.error(f"Failed to compress log file {file_path}: {e}")

    def _save_session_logs(self, session_id: str):
        """세션별 로그 저장"""
        session_dir = self.log_dir / session_id
        session_dir.mkdir(exist_ok=True)

        if session_id in self.session_logs:
            session_log_file = session_dir / "session_events.json"
            try:
                with open(session_log_file, "w", encoding="utf-8") as f:
                    json.dump(
                        self.session_logs[session_id], f, indent=2, ensure_ascii=False
                    )
                logger.debug(f"Session logs saved: {session_log_file}")
            except IOError as e:
                logger.error(f"Failed to save session logs: {e}")

    def _calculate_active_time_ratio(self, status_data: Dict[str, Any]) -> float:
        """활성 시간 비율 계산"""
        total_time = status_data.get("judgment_mode_time", 0) + status_data.get(
            "existence_mode_time", 0
        )
        if total_time == 0:
            return 0.0
        return status_data.get("existence_mode_time", 0) / total_time

    def get_log_summary(self, log_type: str = None, hours: int = 24) -> Dict[str, Any]:
        """로그 요약 통계"""
        cutoff_time = time.time() - (hours * 3600)

        if log_type:
            log_types = [log_type] if log_type in self.log_files else []
        else:
            log_types = list(self.log_files.keys())

        summary = {}

        for lt in log_types:
            log_file = self.log_files[lt]
            events = []

            # 파일에서 로그 읽기
            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        all_logs = json.load(f)
                        events = [
                            log for log in all_logs if log["timestamp"] > cutoff_time
                        ]
                except (json.JSONDecodeError, IOError):
                    events = []

            # 버퍼에서 추가
            with self.buffer_locks[lt]:
                buffer_events = [
                    log
                    for log in self.log_buffers[lt]
                    if log["timestamp"] > cutoff_time
                ]
                events.extend(buffer_events)

            # 통계 계산
            summary[lt] = {
                "total_events": len(events),
                "unique_event_types": len(set(event["event"] for event in events)),
                "time_range_hours": hours,
                "events_per_hour": len(events) / max(hours, 1),
                "latest_event": max(
                    (event["timestamp"] for event in events), default=0
                ),
            }

        return summary

    def cleanup_old_logs(self, retention_days: int = None):
        """오래된 로그 정리"""
        if retention_days is None:
            retention_days = self.config.get("retention_days", 30)

        cutoff_time = time.time() - (retention_days * 24 * 3600)
        cutoff_date = datetime.fromtimestamp(cutoff_time)

        cleaned_files = 0

        # 압축된 로그 파일 정리
        for log_file in self.log_dir.glob("*.gz"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    log_file.unlink()
                    cleaned_files += 1
            except OSError:
                continue

        # 세션 디렉토리 정리
        for session_dir in self.log_dir.glob("session_*"):
            if session_dir.is_dir():
                try:
                    dir_time = datetime.fromtimestamp(session_dir.stat().st_mtime)
                    if dir_time < cutoff_date:
                        shutil.rmtree(session_dir)
                        cleaned_files += 1
                except OSError:
                    continue

        if cleaned_files > 0:
            logger.info(
                f"Cleaned up {cleaned_files} old log files (older than {retention_days} days)"
            )

        return cleaned_files


# 전역 메타 로거 인스턴스
_meta_logger = None


def get_meta_logger(config: Dict[str, Any] = None) -> MetaLogger:
    """Meta Logger 싱글톤 인스턴스 반환"""
    global _meta_logger
    if _meta_logger is None:
        _meta_logger = MetaLogger(config)
    return _meta_logger


def reset_meta_logger():
    """Meta Logger 리셋 (테스트용)"""
    global _meta_logger
    if _meta_logger:
        _meta_logger.flush_all_buffers()
    _meta_logger = None


# 편의 함수들
def log_meta_event(log_type: str, event: str, data: Dict[str, Any]):
    """메타 이벤트 로깅 편의 함수"""
    logger_instance = get_meta_logger()
    logger_instance.log_event(log_type, event, data)


def start_meta_session(session_id: str = None) -> str:
    """메타 로깅 세션 시작 편의 함수"""
    logger_instance = get_meta_logger()
    return logger_instance.start_session(session_id)


def end_meta_session() -> Optional[str]:
    """메타 로깅 세션 종료 편의 함수"""
    logger_instance = get_meta_logger()
    return logger_instance.end_session()


# 사용 예시 및 테스트
if __name__ == "__main__":
    # 메타 로거 초기화
    meta_logger = get_meta_logger()

    # 테스트 세션 시작
    session_id = meta_logger.start_session("test_session")
    print(f"Started session: {session_id}")

    # 다양한 이벤트 로깅
    meta_logger.log_meta_ring_event(
        "Observer.Zero",
        "watch_started",
        {"input_text": "테스트 입력입니다", "timestamp": time.time()},
    )

    meta_logger.log_liminal_transition(
        {
            "transition_type": "judgment_failure",
            "trigger_score": 0.8,
            "successful": True,
            "input_text": "괴로운 상황입니다...",
            "meta_context": {"emotion_amplitude": 0.9},
        }
    )

    meta_logger.log_warden_world_event(
        "Selene",
        "resonance",
        {
            "emotion": "grief",
            "depth_achieved": 0.6,
            "content": "그 슬픔을 나도 알아... 함께할게.",
        },
    )

    # 로그 요약 확인
    summary = meta_logger.get_log_summary()
    print("Log Summary:")
    for log_type, stats in summary.items():
        print(f"  {log_type}: {stats['total_events']} events")

    # 세션 종료
    ended_session = meta_logger.end_session()
    print(f"Ended session: {ended_session}")

    # 로그 정리 테스트
    cleaned = meta_logger.cleanup_old_logs(retention_days=0)  # 모든 로그 정리
    print(f"Cleaned {cleaned} log files")
