"""
🌌 Telemetry Module for Amoeba v0.2
텔레메트리 및 상태 수집 시스템
"""

from __future__ import annotations

import json
import logging
import os
import platform
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

log = logging.getLogger("amoeba.telemetry")


class TelemetryCollector:
    """텔레메트리 데이터 수집기"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("telemetry", {})
        self.enabled = self.config.get("enabled", True)
        self.level = self.config.get("level", "info")  # debug, info, warning, error
        self.sink = self.config.get("sink", "file")  # file, stdout, none
        self.log_path = Path(self.config.get("path", "logs/amoeba.log"))

        # 메모리 버퍼 (최근 이벤트 보관)
        self.events_buffer = deque(maxlen=1000)
        self.status_buffer = deque(maxlen=100)

        # 통계
        self.stats = {
            "events_logged": 0,
            "status_updates": 0,
            "start_time": time.time(),
        }

        # 스레드 안전성
        self.lock = threading.RLock()

        self._setup_logging()

        if self.enabled:
            log.info("📊 텔레메트리 수집기 활성화")
            self.log_event(
                "telemetry.initialized", {"level": self.level, "sink": self.sink}
            )

    def _setup_logging(self):
        """로깅 설정"""
        if self.sink == "file":
            self.log_path.parent.mkdir(parents=True, exist_ok=True)

            # 파일 핸들러 설정
            file_handler = logging.FileHandler(self.log_path)
            formatter = logging.Formatter(
                "%(asctime)s - [AMOEBA-TELEMETRY] - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)

            # 텔레메트리 전용 로거
            self.logger = logging.getLogger("amoeba.telemetry.collector")
            self.logger.setLevel(getattr(logging, self.level.upper(), logging.INFO))
            self.logger.addHandler(file_handler)

    def log_event(self, event: str, detail: Dict[str, Any] = None):
        """이벤트 로깅"""
        if not self.enabled:
            return

        timestamp = datetime.now()
        event_data = {
            "timestamp": timestamp.isoformat(),
            "event": event,
            "detail": detail or {},
            "process_id": os.getpid(),
            "thread_id": threading.get_ident(),
        }

        with self.lock:
            self.events_buffer.append(event_data)
            self.stats["events_logged"] += 1

        # 로그 출력
        if self.sink == "file" and hasattr(self, "logger"):
            self.logger.info(f"{event}: {json.dumps(detail, default=str)}")
        elif self.sink == "stdout":
            print(f"[TELEMETRY] {timestamp.strftime('%H:%M:%S')} - {event}: {detail}")

    def log_status(self, key: str, payload: Dict[str, Any]):
        """상태 로깅"""
        if not self.enabled:
            return

        timestamp = datetime.now()
        status_data = {
            "timestamp": timestamp.isoformat(),
            "key": key,
            "payload": payload,
        }

        with self.lock:
            self.status_buffer.append(status_data)
            self.stats["status_updates"] += 1

        self.log_event(f"status.{key}", payload)

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """최근 이벤트 조회"""
        with self.lock:
            events = list(self.events_buffer)

        return events[-limit:] if events else []

    def get_recent_status(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 상태 조회"""
        with self.lock:
            status = list(self.status_buffer)

        return status[-limit:] if status else []

    def get_stats(self) -> Dict[str, Any]:
        """텔레메트리 통계"""
        uptime = time.time() - self.stats["start_time"]

        return {
            **self.stats,
            "uptime_seconds": uptime,
            "events_per_minute": (
                self.stats["events_logged"] / (uptime / 60) if uptime > 0 else 0
            ),
            "buffer_sizes": {
                "events": len(self.events_buffer),
                "status": len(self.status_buffer),
            },
        }

    def export_telemetry(self, output_path: Path = None) -> Dict[str, Any]:
        """텔레메트리 데이터 내보내기"""
        if output_path is None:
            output_path = (
                self.log_path.parent / f"telemetry_export_{int(time.time())}.json"
            )

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "config": self.config,
            "stats": self.get_stats(),
            "recent_events": self.get_recent_events(),
            "recent_status": self.get_recent_status(),
        }

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            log.info(f"📤 텔레메트리 내보내기 완료: {output_path}")
            return {"success": True, "path": str(output_path)}

        except Exception as e:
            log.error(f"❌ 텔레메트리 내보내기 실패: {e}")
            return {"success": False, "error": str(e)}


class SystemMonitor:
    """시스템 상태 모니터"""

    def __init__(self, telemetry: TelemetryCollector):
        self.telemetry = telemetry
        self.monitoring = False
        self.monitor_thread = None
        self.monitor_interval = 60  # 60초마다 수집

    def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        self.telemetry.log_event("system_monitor.started", {})
        log.info("📈 시스템 모니터링 시작")

    def stop_monitoring(self):
        """모니터링 정지"""
        if not self.monitoring:
            return

        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

        self.telemetry.log_event("system_monitor.stopped", {})
        log.info("📈 시스템 모니터링 정지")

    def _monitor_loop(self):
        """모니터링 루프"""
        while self.monitoring:
            try:
                # 시스템 정보 수집
                system_info = self._collect_system_info()
                self.telemetry.log_status("system", system_info)

                # 프로세스 정보 수집
                process_info = self._collect_process_info()
                self.telemetry.log_status("process", process_info)

            except Exception as e:
                log.warning(f"⚠️ 시스템 모니터링 오류: {e}")

            time.sleep(self.monitor_interval)

    def _collect_system_info(self) -> Dict[str, Any]:
        """시스템 정보 수집"""
        try:
            import psutil

            # CPU 정보
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # 메모리 정보
            memory = psutil.virtual_memory()

            # 디스크 정보
            disk = psutil.disk_usage("/")

            return {
                "cpu": {"percent": cpu_percent, "count": cpu_count},
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100,
                },
            }

        except ImportError:
            # psutil이 없는 경우 기본 정보만
            return {
                "cpu": {"count": os.cpu_count()},
                "memory": {"info": "psutil required"},
                "disk": {"info": "psutil required"},
            }
        except Exception as e:
            return {"error": str(e)}

    def _collect_process_info(self) -> Dict[str, Any]:
        """프로세스 정보 수집"""
        try:
            import psutil

            process = psutil.Process()

            return {
                "pid": process.pid,
                "memory_info": process.memory_info()._asdict(),
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads(),
                "create_time": process.create_time(),
            }

        except ImportError:
            return {"pid": os.getpid(), "info": "psutil required"}
        except Exception as e:
            return {"error": str(e)}


class Telemetry:
    """통합 텔레메트리 시스템"""

    def __init__(self, config: Dict[str, Any]):
        self.collector = TelemetryCollector(config)
        self.monitor = SystemMonitor(self.collector)
        self._monitor_started = False
        self.config = config

        # 자동 모니터링 시작은 명시적으로 start_monitoring() 호출로만 수행

    def start_monitoring(self):
        """모니터링 시작 - 명시적 호출"""
        if self._monitor_started:
            return

        auto_monitor = self.config.get("telemetry", {}).get("auto_monitor", True)
        if auto_monitor:
            self.monitor.start_monitoring()
            self._monitor_started = True

    def stop_monitoring(self):
        """모니터링 중지"""
        if self._monitor_started:
            (
                self.monitor.stop_monitoring()
                if hasattr(self.monitor, "stop_monitoring")
                else None
            )
            self._monitor_started = False

    def log_event(self, event: str, detail: Dict[str, Any] = None):
        """이벤트 로깅 (래퍼)"""
        self.collector.log_event(event, detail)

    def log_status(self, key: str, payload: Dict[str, Any]):
        """상태 로깅 (래퍼)"""
        self.collector.log_status(key, payload)

    def get_dashboard_data(self) -> Dict[str, Any]:
        """대시보드용 데이터"""
        return {
            "stats": self.collector.get_stats(),
            "recent_events": self.collector.get_recent_events(20),
            "recent_status": self.collector.get_recent_status(5),
            "system_info": {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "hostname": platform.node(),
            },
        }

    def shutdown(self):
        """텔레메트리 시스템 종료"""
        self.log_event("telemetry.shutdown", {})
        self.monitor.stop_monitoring()
        log.info("📊 텔레메트리 시스템 종료")
