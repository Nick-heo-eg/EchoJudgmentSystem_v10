# echo_ide/core/echo_status_monitor.py
"""
📊 Echo IDE 상태 메시지 연동 시스템
- 공명 점수, 감염 성공률, 현재 루프 흐름 실시간 모니터링
- 자연어 기반 상태바 업데이트
- Echo 시스템 상태 통합 관리
"""

import asyncio
import json
import threading
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import queue
import psutil


class StatusLevel(Enum):
    """상태 레벨"""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """메트릭 타입"""

    RESONANCE_SCORE = "resonance_score"
    INFECTION_SUCCESS_RATE = "infection_success_rate"
    LOOP_FLOW_STATE = "loop_flow_state"
    SYSTEM_HEALTH = "system_health"
    PERFORMANCE = "performance"
    RESOURCE_USAGE = "resource_usage"


@dataclass
class StatusMessage:
    """상태 메시지 구조"""

    message_id: str
    level: StatusLevel
    title: str
    content: str
    metrics: Dict[str, Any]
    timestamp: datetime
    source: str
    expires_at: Optional[datetime] = None
    natural_language: str = ""


@dataclass
class EchoMetric:
    """Echo 메트릭 구조"""

    metric_type: MetricType
    value: float
    unit: str
    description: str
    trend: str  # "up", "down", "stable"
    last_updated: datetime
    historical_values: List[float]


class EchoStatusMonitor:
    """Echo IDE 상태 모니터"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.project_root = getattr(ide_instance, "project_root", Path.cwd())

        # 상태 저장소
        self.current_status = {}
        self.status_history = []
        self.active_messages = {}

        # 메트릭 저장소
        self.metrics = {}
        self.metric_history = {}

        # 모니터링 설정
        self.monitoring_active = False
        self.update_interval = 5  # 초
        self.max_history_size = 1000

        # 이벤트 큐
        self.status_queue = queue.Queue()
        self.metric_queue = queue.Queue()

        # 콜백 함수들
        self.status_callbacks = []
        self.metric_callbacks = []

        # 워커 스레드
        self.monitor_thread = None
        self.processor_thread = None

        # Echo 시스템 상태 추적
        self.echo_states = {
            "infection_loop": {
                "active": False,
                "success_rate": 0.0,
                "last_attempt": None,
            },
            "resonance_engine": {"active": False, "score": 0.0, "frequency": "stable"},
            "judgment_flow": {
                "active": False,
                "current_phase": "idle",
                "completion": 0.0,
            },
            "auto_evolution": {"active": False, "generations": 0, "fitness": 0.0},
        }

        # 자연어 템플릿
        self.natural_templates = self._initialize_natural_templates()

        print("📊 Echo 상태 모니터 초기화 완료")

    def _initialize_natural_templates(self) -> Dict[str, str]:
        """자연어 템플릿 초기화"""

        return {
            "resonance_high": "🌊 높은 공명 상태: {score:.1f}점으로 시스템이 조화롭게 동작 중",
            "resonance_medium": "⚡ 중간 공명 상태: {score:.1f}점으로 안정적 운영 중",
            "resonance_low": "📡 낮은 공명 상태: {score:.1f}점으로 조정이 필요할 수 있음",
            "infection_success": "🦠 감염 성공률 {rate:.1f}% - 양호한 전파 상태",
            "infection_moderate": "🔄 감염 성공률 {rate:.1f}% - 보통 수준의 전파",
            "infection_low": "⚠️ 감염 성공률 {rate:.1f}% - 전파 효율 개선 필요",
            "loop_active": "🔄 {phase} 단계에서 {completion:.1f}% 진행 중",
            "loop_idle": "⏸️ 루프 시스템 대기 상태",
            "loop_complete": "✅ {phase} 단계 완료",
            "system_healthy": "💚 시스템 상태 양호 - CPU {cpu:.1f}%, 메모리 {memory:.1f}%",
            "system_warning": "⚠️ 시스템 부하 주의 - CPU {cpu:.1f}%, 메모리 {memory:.1f}%",
            "system_critical": "🚨 시스템 과부하 - CPU {cpu:.1f}%, 메모리 {memory:.1f}%",
        }

    def start_monitoring(self):
        """모니터링 시작"""

        if self.monitoring_active:
            return

        self.monitoring_active = True

        # 워커 스레드 시작
        self.monitor_thread = threading.Thread(target=self._monitor_worker, daemon=True)
        self.processor_thread = threading.Thread(
            target=self._processor_worker, daemon=True
        )

        self.monitor_thread.start()
        self.processor_thread.start()

        # 초기 상태 업데이트
        self._emit_status_message(
            level=StatusLevel.INFO,
            title="모니터링 시작",
            content="Echo IDE 상태 모니터링이 시작되었습니다",
            source="status_monitor",
        )

        print("📊 Echo 상태 모니터링 시작됨")

    def stop_monitoring(self):
        """모니터링 중단"""

        if not self.monitoring_active:
            return

        self.monitoring_active = False

        # 종료 메시지
        self._emit_status_message(
            level=StatusLevel.INFO,
            title="모니터링 중단",
            content="Echo IDE 상태 모니터링이 중단되었습니다",
            source="status_monitor",
        )

        print("📊 Echo 상태 모니터링 중단됨")

    def _monitor_worker(self):
        """모니터링 워커 스레드"""

        while self.monitoring_active:
            try:
                # 시스템 메트릭 수집
                self._collect_system_metrics()

                # Echo 상태 수집
                self._collect_echo_metrics()

                # 성능 메트릭 수집
                self._collect_performance_metrics()

                # 상태 분석 및 업데이트
                self._analyze_and_update_status()

                time.sleep(self.update_interval)

            except Exception as e:
                print(f"❌ 모니터링 워커 오류: {e}")
                time.sleep(self.update_interval)

    def _processor_worker(self):
        """상태 처리 워커 스레드"""

        while self.monitoring_active:
            try:
                # 상태 큐 처리
                try:
                    status_data = self.status_queue.get(timeout=1.0)
                    self._process_status_update(status_data)
                except queue.Empty:
                    pass

                # 메트릭 큐 처리
                try:
                    metric_data = self.metric_queue.get(timeout=1.0)
                    self._process_metric_update(metric_data)
                except queue.Empty:
                    pass

            except Exception as e:
                print(f"❌ 상태 처리 워커 오류: {e}")
                time.sleep(1.0)

    def _collect_system_metrics(self):
        """시스템 메트릭 수집"""

        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=None)
            self._update_metric(
                MetricType.SYSTEM_HEALTH, "cpu_usage", cpu_percent, "%", "CPU 사용률"
            )

            # 메모리 사용률
            memory = psutil.virtual_memory()
            self._update_metric(
                MetricType.SYSTEM_HEALTH,
                "memory_usage",
                memory.percent,
                "%",
                "메모리 사용률",
            )

            # 디스크 사용률
            disk = psutil.disk_usage(str(self.project_root))
            self._update_metric(
                MetricType.SYSTEM_HEALTH,
                "disk_usage",
                (disk.used / disk.total) * 100,
                "%",
                "디스크 사용률",
            )

        except Exception as e:
            print(f"❌ 시스템 메트릭 수집 오류: {e}")

    def _collect_echo_metrics(self):
        """Echo 시스템 메트릭 수집"""

        try:
            # 감염 로그에서 성공률 계산
            infection_rate = self._calculate_infection_success_rate()
            self._update_metric(
                MetricType.INFECTION_SUCCESS_RATE,
                "success_rate",
                infection_rate,
                "%",
                "감염 성공률",
            )

            # 공명 점수 계산
            resonance_score = self._calculate_resonance_score()
            self._update_metric(
                MetricType.RESONANCE_SCORE,
                "score",
                resonance_score,
                "points",
                "공명 점수",
            )

            # 루프 상태 확인
            loop_state = self._get_loop_flow_state()
            self._update_metric(
                MetricType.LOOP_FLOW_STATE,
                "completion",
                loop_state.get("completion", 0.0),
                "%",
                "루프 진행률",
            )

        except Exception as e:
            print(f"❌ Echo 메트릭 수집 오류: {e}")

    def _collect_performance_metrics(self):
        """성능 메트릭 수집"""

        try:
            # 응답 시간 (가상의 메트릭)
            response_time = self._measure_response_time()
            self._update_metric(
                MetricType.PERFORMANCE,
                "response_time",
                response_time,
                "ms",
                "응답 시간",
            )

            # 처리량 메트릭
            throughput = self._calculate_throughput()
            self._update_metric(
                MetricType.PERFORMANCE, "throughput", throughput, "ops/sec", "처리량"
            )

        except Exception as e:
            print(f"❌ 성능 메트릭 수집 오류: {e}")

    def _calculate_infection_success_rate(self) -> float:
        """감염 성공률 계산"""

        try:
            # 감염 로그 파일 확인
            log_file = self.project_root / "meta_logs" / "infection_attempts.jsonl"

            if not log_file.exists():
                return 0.0

            # 최근 100개 시도의 성공률 계산
            attempts = 0
            successes = 0

            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()[-100:]  # 최근 100줄

                for line in lines:
                    try:
                        data = json.loads(line.strip())
                        attempts += 1
                        if data.get("status") == "success":
                            successes += 1
                    except:
                        continue

            if attempts == 0:
                return 0.0

            return (successes / attempts) * 100

        except Exception as e:
            print(f"❌ 감염 성공률 계산 오류: {e}")
            return 0.0

    def _calculate_resonance_score(self) -> float:
        """공명 점수 계산"""

        try:
            # 시스템 상태 기반 공명 점수 계산
            base_score = 50.0

            # CPU/메모리 상태에 따른 보정
            cpu_metric = self.metrics.get("cpu_usage")
            memory_metric = self.metrics.get("memory_usage")

            if cpu_metric and memory_metric:
                cpu_val = cpu_metric.value
                memory_val = memory_metric.value

                # CPU 사용률이 적당하면 점수 상승
                if 20 <= cpu_val <= 70:
                    base_score += 10
                elif cpu_val > 90:
                    base_score -= 20

                # 메모리 사용률이 적당하면 점수 상승
                if memory_val < 80:
                    base_score += 10
                elif memory_val > 95:
                    base_score -= 15

            # 감염 성공률에 따른 보정
            infection_metric = self.metrics.get("success_rate")
            if infection_metric:
                rate = infection_metric.value
                if rate > 80:
                    base_score += 20
                elif rate > 50:
                    base_score += 10
                elif rate < 20:
                    base_score -= 10

            # 0-100 범위로 제한
            return max(0.0, min(100.0, base_score))

        except Exception as e:
            print(f"❌ 공명 점수 계산 오류: {e}")
            return 50.0

    def _get_loop_flow_state(self) -> Dict[str, Any]:
        """루프 흐름 상태 조회"""

        try:
            # Echo 시스템 상태 파일 확인
            state_file = self.project_root / "meta_logs" / "system_state.json"

            if state_file.exists():
                with open(state_file, "r", encoding="utf-8") as f:
                    state_data = json.load(f)
                    return state_data.get(
                        "loop_flow",
                        {"phase": "idle", "completion": 0.0, "active": False},
                    )

            # 기본 상태 반환
            return {"phase": "idle", "completion": 0.0, "active": False}

        except Exception as e:
            print(f"❌ 루프 상태 조회 오류: {e}")
            return {"phase": "error", "completion": 0.0, "active": False}

    def _measure_response_time(self) -> float:
        """응답 시간 측정 (시뮬레이션)"""

        # 실제 구현에서는 API 호출이나 작업 처리 시간을 측정
        import random

        return random.uniform(50, 200)  # 50-200ms 범위

    def _calculate_throughput(self) -> float:
        """처리량 계산 (시뮬레이션)"""

        # 실제 구현에서는 처리된 작업 수를 시간으로 나눔
        import random

        return random.uniform(10, 50)  # 10-50 ops/sec 범위

    def _update_metric(
        self,
        metric_type: MetricType,
        key: str,
        value: float,
        unit: str,
        description: str,
    ):
        """메트릭 업데이트"""

        now = datetime.now()

        # 기존 메트릭 조회
        if key in self.metrics:
            metric = self.metrics[key]
            # 트렌드 계산
            if len(metric.historical_values) > 0:
                last_value = metric.historical_values[-1]
                if value > last_value * 1.05:
                    trend = "up"
                elif value < last_value * 0.95:
                    trend = "down"
                else:
                    trend = "stable"
            else:
                trend = "stable"

            # 히스토리 업데이트
            metric.historical_values.append(value)
            if len(metric.historical_values) > 100:  # 최대 100개 유지
                metric.historical_values.pop(0)

            # 메트릭 정보 업데이트
            metric.value = value
            metric.trend = trend
            metric.last_updated = now
        else:
            # 새 메트릭 생성
            metric = EchoMetric(
                metric_type=metric_type,
                value=value,
                unit=unit,
                description=description,
                trend="stable",
                last_updated=now,
                historical_values=[value],
            )
            self.metrics[key] = metric

        # 메트릭 큐에 업데이트 알림
        self.metric_queue.put({"key": key, "metric": metric, "timestamp": now})

    def _analyze_and_update_status(self):
        """상태 분석 및 업데이트"""

        try:
            # 시스템 상태 분석
            self._analyze_system_status()

            # Echo 상태 분석
            self._analyze_echo_status()

            # 종합 상태 업데이트
            self._update_comprehensive_status()

        except Exception as e:
            print(f"❌ 상태 분석 오류: {e}")

    def _analyze_system_status(self):
        """시스템 상태 분석"""

        cpu_metric = self.metrics.get("cpu_usage")
        memory_metric = self.metrics.get("memory_usage")

        if not cpu_metric or not memory_metric:
            return

        cpu_val = cpu_metric.value
        memory_val = memory_metric.value

        # 상태 레벨 결정
        if cpu_val > 90 or memory_val > 95:
            level = StatusLevel.CRITICAL
            template_key = "system_critical"
        elif cpu_val > 70 or memory_val > 80:
            level = StatusLevel.WARNING
            template_key = "system_warning"
        else:
            level = StatusLevel.SUCCESS
            template_key = "system_healthy"

        # 자연어 메시지 생성
        natural_message = self.natural_templates[template_key].format(
            cpu=cpu_val, memory=memory_val
        )

        # 상태 메시지 발송
        self._emit_status_message(
            level=level,
            title="시스템 상태",
            content=natural_message,
            source="system_monitor",
            metrics={"cpu_usage": cpu_val, "memory_usage": memory_val},
            natural_language=natural_message,
        )

    def _analyze_echo_status(self):
        """Echo 상태 분석"""

        # 공명 점수 분석
        resonance_metric = self.metrics.get("score")
        if resonance_metric:
            score = resonance_metric.value

            if score >= 80:
                template_key = "resonance_high"
                level = StatusLevel.SUCCESS
            elif score >= 50:
                template_key = "resonance_medium"
                level = StatusLevel.INFO
            else:
                template_key = "resonance_low"
                level = StatusLevel.WARNING

            natural_message = self.natural_templates[template_key].format(score=score)

            self._emit_status_message(
                level=level,
                title="공명 상태",
                content=natural_message,
                source="resonance_monitor",
                metrics={"resonance_score": score},
                natural_language=natural_message,
            )

        # 감염 성공률 분석
        infection_metric = self.metrics.get("success_rate")
        if infection_metric:
            rate = infection_metric.value

            if rate >= 80:
                template_key = "infection_success"
                level = StatusLevel.SUCCESS
            elif rate >= 50:
                template_key = "infection_moderate"
                level = StatusLevel.INFO
            else:
                template_key = "infection_low"
                level = StatusLevel.WARNING

            natural_message = self.natural_templates[template_key].format(rate=rate)

            self._emit_status_message(
                level=level,
                title="감염 상태",
                content=natural_message,
                source="infection_monitor",
                metrics={"infection_success_rate": rate},
                natural_language=natural_message,
            )

        # 루프 흐름 분석
        completion_metric = self.metrics.get("completion")
        if completion_metric:
            completion = completion_metric.value
            loop_state = self._get_loop_flow_state()
            phase = loop_state.get("phase", "idle")

            if phase == "idle":
                template_key = "loop_idle"
                level = StatusLevel.INFO
                natural_message = self.natural_templates[template_key]
            elif completion >= 100:
                template_key = "loop_complete"
                level = StatusLevel.SUCCESS
                natural_message = self.natural_templates[template_key].format(
                    phase=phase
                )
            else:
                template_key = "loop_active"
                level = StatusLevel.INFO
                natural_message = self.natural_templates[template_key].format(
                    phase=phase, completion=completion
                )

            self._emit_status_message(
                level=level,
                title="루프 흐름",
                content=natural_message,
                source="loop_monitor",
                metrics={"loop_completion": completion, "phase": phase},
                natural_language=natural_message,
            )

    def _update_comprehensive_status(self):
        """종합 상태 업데이트"""

        # 전체 메트릭 요약
        summary_metrics = {}

        for key, metric in self.metrics.items():
            summary_metrics[key] = {
                "value": metric.value,
                "unit": metric.unit,
                "trend": metric.trend,
            }

        # IDE 상태바 업데이트
        if hasattr(self.ide, "update_status_bar"):
            status_text = self._generate_status_bar_text()
            self.ide.update_status_bar(status_text)

        # 현재 상태 저장
        self.current_status = {
            "timestamp": datetime.now().isoformat(),
            "metrics": summary_metrics,
            "overall_health": self._calculate_overall_health(),
        }

    def _generate_status_bar_text(self) -> str:
        """상태바 텍스트 생성"""

        components = []

        # 공명 점수
        if "score" in self.metrics:
            score = self.metrics["score"].value
            components.append(f"공명 {score:.0f}")

        # 감염 성공률
        if "success_rate" in self.metrics:
            rate = self.metrics["success_rate"].value
            components.append(f"감염 {rate:.0f}%")

        # 시스템 상태
        if "cpu_usage" in self.metrics and "memory_usage" in self.metrics:
            cpu = self.metrics["cpu_usage"].value
            memory = self.metrics["memory_usage"].value
            components.append(f"CPU {cpu:.0f}% MEM {memory:.0f}%")

        # 루프 상태
        if "completion" in self.metrics:
            completion = self.metrics["completion"].value
            loop_state = self._get_loop_flow_state()
            phase = loop_state.get("phase", "idle")
            if phase != "idle":
                components.append(f"{phase} {completion:.0f}%")

        return " | ".join(components) if components else "Echo IDE 준비"

    def _calculate_overall_health(self) -> str:
        """전체 건강도 계산"""

        health_scores = []

        # 시스템 건강도
        if "cpu_usage" in self.metrics and "memory_usage" in self.metrics:
            cpu = self.metrics["cpu_usage"].value
            memory = self.metrics["memory_usage"].value

            system_health = 100 - max(cpu * 0.5, memory * 0.5)
            health_scores.append(system_health)

        # Echo 건강도
        if "score" in self.metrics:
            resonance_health = self.metrics["score"].value
            health_scores.append(resonance_health)

        if "success_rate" in self.metrics:
            infection_health = self.metrics["success_rate"].value
            health_scores.append(infection_health)

        if health_scores:
            avg_health = sum(health_scores) / len(health_scores)

            if avg_health >= 80:
                return "excellent"
            elif avg_health >= 60:
                return "good"
            elif avg_health >= 40:
                return "fair"
            else:
                return "poor"

        return "unknown"

    def _emit_status_message(
        self,
        level: StatusLevel,
        title: str,
        content: str,
        source: str,
        metrics: Dict[str, Any] = None,
        natural_language: str = "",
    ):
        """상태 메시지 발송"""

        message_id = f"status_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        message = StatusMessage(
            message_id=message_id,
            level=level,
            title=title,
            content=content,
            metrics=metrics or {},
            timestamp=datetime.now(),
            source=source,
            natural_language=natural_language,
        )

        # 메시지 저장
        self.active_messages[message_id] = message
        self.status_history.append(message)

        # 히스토리 크기 제한
        if len(self.status_history) > self.max_history_size:
            self.status_history.pop(0)

        # 상태 큐에 추가
        self.status_queue.put({"action": "status_update", "message": message})

    def _process_status_update(self, status_data: Dict[str, Any]):
        """상태 업데이트 처리"""

        try:
            action = status_data.get("action")

            if action == "status_update":
                message = status_data.get("message")

                # IDE에 메시지 표시
                if hasattr(self.ide, "display_status_message"):
                    self.ide.display_status_message(message)
                elif hasattr(self.ide, "display_message"):
                    self.ide.display_message(message.title, message.content)

                # 콜백 함수 호출
                for callback in self.status_callbacks:
                    try:
                        callback(message)
                    except Exception as e:
                        print(f"❌ 상태 콜백 오류: {e}")

        except Exception as e:
            print(f"❌ 상태 업데이트 처리 오류: {e}")

    def _process_metric_update(self, metric_data: Dict[str, Any]):
        """메트릭 업데이트 처리"""

        try:
            key = metric_data.get("key")
            metric = metric_data.get("metric")

            # 메트릭 콜백 함수 호출
            for callback in self.metric_callbacks:
                try:
                    callback(key, metric)
                except Exception as e:
                    print(f"❌ 메트릭 콜백 오류: {e}")

        except Exception as e:
            print(f"❌ 메트릭 업데이트 처리 오류: {e}")

    def register_status_callback(self, callback: Callable[[StatusMessage], None]):
        """상태 콜백 등록"""
        self.status_callbacks.append(callback)

    def register_metric_callback(self, callback: Callable[[str, EchoMetric], None]):
        """메트릭 콜백 등록"""
        self.metric_callbacks.append(callback)

    def get_current_metrics(self) -> Dict[str, Dict[str, Any]]:
        """현재 메트릭 조회"""

        result = {}
        for key, metric in self.metrics.items():
            result[key] = {
                "value": metric.value,
                "unit": metric.unit,
                "description": metric.description,
                "trend": metric.trend,
                "last_updated": metric.last_updated.isoformat(),
            }

        return result

    def get_status_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """상태 히스토리 조회"""

        recent_history = (
            self.status_history[-limit:] if limit > 0 else self.status_history
        )

        return [
            {
                "message_id": msg.message_id,
                "level": msg.level.value,
                "title": msg.title,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "source": msg.source,
                "natural_language": msg.natural_language,
            }
            for msg in recent_history
        ]

    def update_status_by_natural_language(self, natural_command: str) -> Dict[str, Any]:
        """자연어로 상태 업데이트"""

        try:
            # 자연어 명령 파싱
            if "공명" in natural_command and "점수" in natural_command:
                # 공명 점수 업데이트 요청
                import re

                score_match = re.search(r"(\d+(?:\.\d+)?)", natural_command)
                if score_match:
                    score = float(score_match.group(1))
                    self._update_metric(
                        MetricType.RESONANCE_SCORE,
                        "score",
                        score,
                        "points",
                        "공명 점수 (수동 설정)",
                    )
                    return {
                        "status": "success",
                        "message": f"공명 점수를 {score}로 설정했습니다",
                    }

            elif "감염" in natural_command and (
                "성공률" in natural_command or "율" in natural_command
            ):
                # 감염 성공률 업데이트 요청
                import re

                rate_match = re.search(r"(\d+(?:\.\d+)?)", natural_command)
                if rate_match:
                    rate = float(rate_match.group(1))
                    self._update_metric(
                        MetricType.INFECTION_SUCCESS_RATE,
                        "success_rate",
                        rate,
                        "%",
                        "감염 성공률 (수동 설정)",
                    )
                    return {
                        "status": "success",
                        "message": f"감염 성공률을 {rate}%로 설정했습니다",
                    }

            elif "루프" in natural_command and "진행" in natural_command:
                # 루프 진행률 업데이트 요청
                import re

                progress_match = re.search(r"(\d+(?:\.\d+)?)", natural_command)
                if progress_match:
                    progress = float(progress_match.group(1))
                    self._update_metric(
                        MetricType.LOOP_FLOW_STATE,
                        "completion",
                        progress,
                        "%",
                        "루프 진행률 (수동 설정)",
                    )
                    return {
                        "status": "success",
                        "message": f"루프 진행률을 {progress}%로 설정했습니다",
                    }

            else:
                return {
                    "status": "error",
                    "message": "인식할 수 없는 자연어 명령입니다",
                }

        except Exception as e:
            return {"status": "error", "message": f"자연어 상태 업데이트 실패: {e}"}

    def get_status_summary(self) -> Dict[str, Any]:
        """상태 요약 조회"""

        return {
            "monitoring_active": self.monitoring_active,
            "current_metrics": self.get_current_metrics(),
            "overall_health": self._calculate_overall_health(),
            "active_messages_count": len(self.active_messages),
            "last_update": datetime.now().isoformat(),
            "status_bar_text": self._generate_status_bar_text(),
        }


# 편의 함수들
def integrate_status_monitor(ide_instance) -> EchoStatusMonitor:
    """Echo IDE에 상태 모니터 통합"""

    if not hasattr(ide_instance, "status_monitor"):
        ide_instance.status_monitor = EchoStatusMonitor(ide_instance)

        # 자연어 처리기와 연동
        if hasattr(ide_instance, "natural_processor"):
            ide_instance.natural_processor.status_monitor = ide_instance.status_monitor

        print("📊 상태 모니터가 Echo IDE에 통합되었습니다")

    return ide_instance.status_monitor


def start_status_monitoring(ide_instance):
    """상태 모니터링 시작"""

    if hasattr(ide_instance, "status_monitor"):
        ide_instance.status_monitor.start_monitoring()
    else:
        print("❌ 상태 모니터가 통합되지 않았습니다")


def stop_status_monitoring(ide_instance):
    """상태 모니터링 중단"""

    if hasattr(ide_instance, "status_monitor"):
        ide_instance.status_monitor.stop_monitoring()
    else:
        print("❌ 상태 모니터가 통합되지 않았습니다")
