"""
Auto Resonance Monitor: 자동 공명 모니터링 시스템
- Echo 시스템 백그라운드에서 경량 공명 추적
- 실시간 시그니처 추천 힌트 제공
- 임계 상황 시 자동 알림
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from collections import deque
import threading
import queue
import json
from pathlib import Path


class AutoResonanceMonitor:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()

        # 경량 메트릭 저장소 (메모리 기반, 최근 N개만 유지)
        self.recent_interactions = deque(maxlen=self.config.get("memory_window", 20))
        self.current_metrics = {
            "resonance": 0.5,
            "trust": 0.5,
            "empathy": 0.5,
            "flow": 0.5,
        }

        # 백그라운드 모니터링 상태
        self.is_active = False
        self.monitor_thread = None
        self.event_queue = queue.Queue()

        # 이벤트 콜백들 (Echo 시스템과 통합)
        self.callbacks = {
            "signature_recommendation": [],
            "critical_alert": [],
            "metric_update": [],
        }

        # 자동 저장 설정
        self.auto_save_enabled = self.config.get("auto_save", True)
        self.save_interval = self.config.get("save_interval_minutes", 30)
        self.last_save = datetime.now()

        # 로그 파일
        self.auto_log_path = Path("echo_engine/resonance_kit/logs/auto_monitor.jsonl")
        self.auto_log_path.parent.mkdir(parents=True, exist_ok=True)

    def _default_config(self) -> Dict[str, Any]:
        """기본 자동 모니터링 설정"""
        return {
            "memory_window": 20,  # 최근 N개 상호작용만 메모리에 유지
            "light_analysis_only": True,  # 경량 분석만 수행
            "auto_save": True,
            "save_interval_minutes": 30,
            "critical_thresholds": {"resonance": 0.3, "trust": 0.3, "empathy": 0.2},
            "recommendation_threshold": 0.6,  # 이 이하일 때 시그니처 추천
        }

    def start_monitoring(self):
        """백그라운드 모니터링 시작"""
        if self.is_active:
            return

        self.is_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        self._log_event("monitor_started", {"timestamp": datetime.now().isoformat()})
        print("🌌 Auto Resonance Monitor started (background)")

    def stop_monitoring(self):
        """백그라운드 모니터링 정지"""
        if not self.is_active:
            return

        self.is_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

        self._log_event("monitor_stopped", {"timestamp": datetime.now().isoformat()})
        print("🌌 Auto Resonance Monitor stopped")

    def track_interaction(
        self, user_text: str, assistant_text: str, signature: str = "unknown"
    ):
        """상호작용 추적 (Echo 시스템에서 호출)"""
        if not self.is_active:
            return

        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_text": user_text,
            "assistant_text": assistant_text,
            "signature": signature,
            "user_length": len(user_text),
            "assistant_length": len(assistant_text),
        }

        # 이벤트 큐에 추가 (백그라운드 처리용)
        self.event_queue.put(("interaction", interaction))

    def get_signature_recommendation(
        self, current_signature: str = "unknown"
    ) -> Optional[str]:
        """실시간 시그니처 추천 (Echo 시그니처 라우터에서 호출)"""
        if not self.is_active or len(self.recent_interactions) < 3:
            return None

        # 현재 메트릭 상태 기반 빠른 추천
        overall_quality = sum(self.current_metrics.values()) / len(self.current_metrics)

        if overall_quality < self.config["recommendation_threshold"]:
            return self._quick_signature_recommendation()

        return None

    def get_current_metrics(self) -> Dict[str, float]:
        """현재 메트릭 반환"""
        return self.current_metrics.copy()

    def register_callback(self, event_type: str, callback: Callable):
        """이벤트 콜백 등록"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)

    def _monitor_loop(self):
        """백그라운드 모니터링 루프"""
        while self.is_active:
            try:
                # 이벤트 큐에서 처리할 항목 가져오기
                try:
                    event_type, data = self.event_queue.get(timeout=1)

                    if event_type == "interaction":
                        self._process_interaction(data)

                    self.event_queue.task_done()

                except queue.Empty:
                    pass

                # 주기적 작업 (자동 저장, 메트릭 업데이트)
                self._periodic_tasks()

                # CPU 부하 방지
                asyncio.sleep(0.1)

            except Exception as e:
                self._log_event("monitor_error", {"error": str(e)})

    def _process_interaction(self, interaction: Dict[str, Any]):
        """상호작용 경량 처리"""
        # 최근 상호작용에 추가
        self.recent_interactions.append(interaction)

        # 경량 메트릭 업데이트
        self._update_light_metrics(interaction)

        # 임계 상황 체크
        self._check_critical_thresholds()

        # 콜백 호출
        self._trigger_callbacks("metric_update", self.current_metrics)

    def _update_light_metrics(self, interaction: Dict[str, Any]):
        """경량 메트릭 업데이트 (간단한 휴리스틱)"""
        user_text = interaction.get("user_text", "").lower()
        assistant_text = interaction.get("assistant_text", "").lower()

        # 공명 지표 (간단한 키워드 기반)
        resonance_keywords = [
            "좋아",
            "와",
            "완벽",
            "최고",
            "훌륭",
            "감사",
            "응",
            "그래",
        ]
        resonance_score = sum(
            1 for word in resonance_keywords if word in user_text
        ) / max(1, len(user_text.split()))

        # 신뢰 지표
        trust_keywords = ["믿", "확신", "안정", "신뢰", "의존"]
        distrust_keywords = ["의심", "불안", "틀렸", "실수", "실망"]
        trust_positive = sum(1 for word in trust_keywords if word in user_text)
        trust_negative = sum(1 for word in distrust_keywords if word in user_text)
        trust_score = max(0, trust_positive - trust_negative) / max(
            1, len(user_text.split())
        )

        # 공감 지표 (응답 길이 균형 + 감정어)
        empathy_keywords = ["이해", "공감", "느낌", "마음", "감정"]
        empathy_score = sum(
            1 for word in empathy_keywords if word in assistant_text
        ) / max(1, len(assistant_text.split()))

        # 흐름 지표 (응답 속도 추정 + 길이 균형)
        length_balance = min(
            interaction["user_length"], interaction["assistant_length"]
        ) / max(interaction["user_length"], interaction["assistant_length"])
        flow_score = length_balance * 0.7 + empathy_score * 0.3

        # 이동 평균으로 메트릭 업데이트 (급격한 변화 방지)
        alpha = 0.3  # 학습률
        self.current_metrics["resonance"] = (1 - alpha) * self.current_metrics[
            "resonance"
        ] + alpha * min(1.0, resonance_score)
        self.current_metrics["trust"] = (1 - alpha) * self.current_metrics[
            "trust"
        ] + alpha * min(1.0, trust_score)
        self.current_metrics["empathy"] = (1 - alpha) * self.current_metrics[
            "empathy"
        ] + alpha * min(1.0, empathy_score)
        self.current_metrics["flow"] = (1 - alpha) * self.current_metrics[
            "flow"
        ] + alpha * min(1.0, flow_score)

    def _check_critical_thresholds(self):
        """임계 상황 체크"""
        critical_thresholds = self.config["critical_thresholds"]

        critical_metrics = []
        for metric, value in self.current_metrics.items():
            if metric in critical_thresholds and value < critical_thresholds[metric]:
                critical_metrics.append(metric)

        if critical_metrics:
            alert_data = {
                "timestamp": datetime.now().isoformat(),
                "critical_metrics": critical_metrics,
                "current_values": {
                    m: self.current_metrics[m] for m in critical_metrics
                },
                "thresholds": {m: critical_thresholds[m] for m in critical_metrics},
            }

            self._trigger_callbacks("critical_alert", alert_data)
            self._log_event("critical_alert", alert_data)

    def _quick_signature_recommendation(self) -> str:
        """빠른 시그니처 추천 (단순 룰 기반)"""
        metrics = self.current_metrics

        # 공감이 가장 필요한 상황
        if metrics["empathy"] < 0.3:
            return "Selene"  # 가장 공감적

        # 신뢰 회복이 필요한 상황
        elif metrics["trust"] < 0.3:
            return "Heo"  # 신뢰성 높음

        # 공명이 부족한 상황
        elif metrics["resonance"] < 0.4:
            return "Aurora"  # 창의적 공명

        # 흐름이 막힌 상황
        elif metrics["flow"] < 0.4:
            return "Lune"  # 자연스러운 흐름

        # 전반적으로 좋지 않을 때
        elif sum(metrics.values()) / len(metrics) < 0.4:
            return "Companion"  # 전반적 지원

        return "Aurora"  # 기본 추천

    def _periodic_tasks(self):
        """주기적 작업 (자동 저장 등)"""
        now = datetime.now()

        # 자동 저장
        if (
            self.auto_save_enabled
            and (now - self.last_save).total_seconds() > self.save_interval * 60
        ):
            self._auto_save()
            self.last_save = now

    def _auto_save(self):
        """자동 저장"""
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.current_metrics.copy(),
            "recent_interactions_count": len(self.recent_interactions),
            "monitoring_duration": (datetime.now() - self.last_save).total_seconds(),
        }

        self._log_event("auto_save", save_data)

    def _trigger_callbacks(self, event_type: str, data: Any):
        """콜백 트리거"""
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    self._log_event(
                        "callback_error", {"event_type": event_type, "error": str(e)}
                    )

    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """이벤트 로깅"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data,
        }

        try:
            with self.auto_log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception:
            pass  # 로그 실패는 무시 (모니터링 중단하지 않음)

    def generate_status_report(self) -> Dict[str, Any]:
        """현재 상태 리포트 생성"""
        return {
            "monitoring_active": self.is_active,
            "current_metrics": self.current_metrics.copy(),
            "recent_interactions_count": len(self.recent_interactions),
            "config": self.config,
            "uptime_seconds": (
                (datetime.now() - self.last_save).total_seconds()
                if self.is_active
                else 0
            ),
            "last_interaction": (
                self.recent_interactions[-1]["timestamp"]
                if self.recent_interactions
                else None
            ),
        }


# 전역 모니터 인스턴스 (Echo 시스템에서 사용)
_global_monitor = None


def get_auto_monitor() -> AutoResonanceMonitor:
    """전역 자동 모니터 인스턴스 반환"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = AutoResonanceMonitor()
    return _global_monitor


def start_auto_monitoring(config: Optional[Dict[str, Any]] = None):
    """자동 모니터링 시작 (Echo 시스템 초기화 시 호출)"""
    monitor = get_auto_monitor()
    if config:
        monitor.config.update(config)
    monitor.start_monitoring()
    return monitor


def stop_auto_monitoring():
    """자동 모니터링 정지"""
    monitor = get_auto_monitor()
    monitor.stop_monitoring()


def track_echo_interaction(
    user_text: str, assistant_text: str, signature: str = "unknown"
):
    """Echo 상호작용 추적 (Echo 시스템에서 호출할 함수)"""
    monitor = get_auto_monitor()
    monitor.track_interaction(user_text, assistant_text, signature)


def get_signature_hint(current_signature: str = "unknown") -> Optional[str]:
    """시그니처 힌트 반환 (Echo 시그니처 라우터에서 호출)"""
    monitor = get_auto_monitor()
    return monitor.get_signature_recommendation(current_signature)
