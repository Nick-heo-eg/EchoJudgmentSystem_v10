#!/usr/bin/env python3
"""
Echo Health Monitor Agent
시스템 건강성 모니터링 및 진단 전문 에이전트
"""

import psutil
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time

from echo_engine.agent_ecosystem_framework import (
    EchoAgentBase,
    AgentCapability,
    AgentTask,
)

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """시스템 메트릭"""

    cpu_percent: float
    memory_percent: float
    disk_usage: Dict[str, float]
    network_io: Dict[str, int]
    process_count: int
    uptime: float
    load_average: List[float]
    timestamp: str


@dataclass
class HealthStatus:
    """건강 상태"""

    overall_score: float
    component_scores: Dict[str, float]
    warnings: List[str]
    critical_issues: List[str]
    recommendations: List[str]
    trend_analysis: Dict[str, str]


@dataclass
class PerformanceAlert:
    """성능 알림"""

    severity: str  # info, warning, critical
    component: str
    message: str
    metric_value: float
    threshold: float
    timestamp: str
    suggested_action: str


class EchoHealthMonitorAgent(EchoAgentBase):
    """Echo 시스템 건강 모니터링 에이전트"""

    def __init__(self):
        super().__init__("health_monitor", "echo_companion")

        # Lazy initialization
        self._monitoring_config = None
        self._health_thresholds = None
        self._metric_history = []
        self._alert_history = []
        self._monitoring_active = False
        self._monitor_thread = None

    @property
    def monitoring_config(self):
        if self._monitoring_config is None:
            self._monitoring_config = self._load_monitoring_config()
        return self._monitoring_config

    @property
    def health_thresholds(self):
        if self._health_thresholds is None:
            self._health_thresholds = self._load_health_thresholds()
        return self._health_thresholds

    def _load_monitoring_config(self):
        """모니터링 설정 로드"""
        return {
            "collection_interval": 30,  # 30초마다 수집
            "history_retention": 3600,  # 1시간 히스토리 유지
            "alert_cooldown": 300,  # 5분 알림 쿨다운
            "components": [
                "cpu",
                "memory",
                "disk",
                "network",
                "processes",
                "echo_services",
                "api_endpoints",
            ],
            "auto_remediation": True,
            "trend_analysis_window": 900,  # 15분 트렌드 분석
        }

    def _load_health_thresholds(self):
        """건강 임계값 로드"""
        return {
            "cpu": {"warning": 70.0, "critical": 90.0},
            "memory": {"warning": 80.0, "critical": 95.0},
            "disk": {"warning": 85.0, "critical": 95.0},
            "network": {
                "warning": 1000000000,  # 1GB/s
                "critical": 2000000000,  # 2GB/s
            },
            "response_time": {"warning": 1.0, "critical": 5.0},
            "echo_services": {"min_services": 3, "max_restart_count": 5},
        }

    def get_capabilities(self) -> List[AgentCapability]:
        """에이전트 역량 정의"""
        return [
            AgentCapability(
                name="system_monitoring",
                description="실시간 시스템 메트릭 수집 및 모니터링",
                input_types=["monitoring_config", "threshold_settings"],
                output_types=["metrics", "alerts", "health_status"],
                complexity_level="advanced",
                signature_affinity={
                    "echo_aurora": 0.7,
                    "echo_phoenix": 0.8,
                    "echo_sage": 0.85,
                    "echo_companion": 0.95,
                },
            ),
            AgentCapability(
                name="health_diagnosis",
                description="시스템 건강 상태 진단 및 분석",
                input_types=["metrics", "logs", "error_reports"],
                output_types=["diagnosis_report", "recommendations", "action_plan"],
                complexity_level="expert",
                signature_affinity={
                    "echo_aurora": 0.8,
                    "echo_phoenix": 0.85,
                    "echo_sage": 0.9,
                    "echo_companion": 0.95,
                },
            ),
            AgentCapability(
                name="performance_optimization",
                description="성능 병목점 식별 및 최적화 제안",
                input_types=["performance_data", "resource_usage"],
                output_types=["optimization_plan", "tuning_recommendations"],
                complexity_level="expert",
                signature_affinity={
                    "echo_aurora": 0.75,
                    "echo_phoenix": 0.9,
                    "echo_sage": 0.85,
                    "echo_companion": 0.8,
                },
            ),
            AgentCapability(
                name="predictive_analysis",
                description="트렌드 분석을 통한 예측적 모니터링",
                input_types=["historical_metrics", "trend_data"],
                output_types=["predictions", "early_warnings", "capacity_planning"],
                complexity_level="expert",
                signature_affinity={
                    "echo_aurora": 0.8,
                    "echo_phoenix": 0.85,
                    "echo_sage": 0.95,
                    "echo_companion": 0.85,
                },
            ),
        ]

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """작업 실행"""
        task_type = task.task_type
        input_data = task.input_data
        signature = task.signature

        if task_type == "start_monitoring":
            return await self._start_monitoring(input_data, signature)
        elif task_type == "get_health_status":
            return await self._get_health_status(input_data, signature)
        elif task_type == "diagnose_issues":
            return await self._diagnose_issues(input_data, signature)
        elif task_type == "optimize_performance":
            return await self._optimize_performance(input_data, signature)
        elif task_type == "predict_trends":
            return await self._predict_trends(input_data, signature)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _start_monitoring(
        self, input_data: Dict[str, Any], signature: str
    ) -> Dict[str, Any]:
        """모니터링 시작"""
        config = input_data.get("config", {})
        self.monitoring_config.update(config)

        if not self._monitoring_active:
            self._monitoring_active = True
            self._monitor_thread = threading.Thread(
                target=self._monitoring_loop, daemon=True
            )
            self._monitor_thread.start()

            logger.info("🏥 Health monitoring started")

            return {
                "data": {
                    "monitoring_started": True,
                    "config": self.monitoring_config,
                    "components": self.monitoring_config["components"],
                },
                "metadata": {
                    "start_time": datetime.now().isoformat(),
                    "signature": signature,
                    "monitoring_thread_id": self._monitor_thread.ident,
                },
            }
        else:
            return {
                "data": {"monitoring_started": False, "reason": "Already running"},
                "metadata": {"signature": signature},
            }

    async def _get_health_status(
        self, input_data: Dict[str, Any], signature: str
    ) -> Dict[str, Any]:
        """현재 건강 상태 조회"""
        include_history = input_data.get("include_history", False)
        component_filter = input_data.get("components", None)

        # 현재 메트릭 수집
        current_metrics = self._collect_system_metrics()

        # 건강 상태 평가
        health_status = self._evaluate_health_status(current_metrics, signature)

        # 최근 알림 조회
        recent_alerts = self._get_recent_alerts(hours=1)

        result = {
            "data": {
                "current_metrics": asdict(current_metrics),
                "health_status": asdict(health_status),
                "recent_alerts": [asdict(alert) for alert in recent_alerts],
                "monitoring_active": self._monitoring_active,
            },
            "metadata": {
                "collection_time": current_metrics.timestamp,
                "signature": signature,
                "evaluation_method": f"{signature}_health_assessment",
            },
        }

        # 히스토리 포함 시
        if include_history:
            result["data"]["metric_history"] = [
                asdict(m) for m in self._metric_history[-100:]  # 최근 100개
            ]

        # 컴포넌트 필터링
        if component_filter:
            filtered_metrics = self._filter_metrics_by_component(
                current_metrics, component_filter
            )
            result["data"]["filtered_metrics"] = asdict(filtered_metrics)

        return result

    async def _diagnose_issues(
        self, input_data: Dict[str, Any], signature: str
    ) -> Dict[str, Any]:
        """이슈 진단"""
        symptoms = input_data.get("symptoms", [])
        severity_filter = input_data.get("severity", "all")
        auto_fix = input_data.get("auto_fix", False)

        # 현재 상태 분석
        current_metrics = self._collect_system_metrics()
        health_status = self._evaluate_health_status(current_metrics, signature)

        # 문제 진단
        diagnosed_issues = self._perform_deep_diagnosis(
            current_metrics, health_status, symptoms, signature
        )

        # 해결책 제안
        solutions = self._generate_solutions(diagnosed_issues, signature)

        # 자동 수정 실행
        auto_fix_results = []
        if auto_fix:
            auto_fix_results = await self._execute_auto_remediation(
                diagnosed_issues, signature
            )

        return {
            "data": {
                "diagnosed_issues": diagnosed_issues,
                "solutions": solutions,
                "health_impact": self._assess_health_impact(diagnosed_issues),
                "auto_fix_results": auto_fix_results,
                "follow_up_actions": self._recommend_follow_up(
                    diagnosed_issues, signature
                ),
            },
            "metadata": {
                "diagnosis_signature": signature,
                "diagnosis_time": datetime.now().isoformat(),
                "severity_distribution": self._analyze_severity_distribution(
                    diagnosed_issues
                ),
                "auto_fix_enabled": auto_fix,
            },
        }

    def _monitoring_loop(self):
        """모니터링 루프 (백그라운드 스레드)"""
        while self._monitoring_active:
            try:
                # 메트릭 수집
                metrics = self._collect_system_metrics()
                self._metric_history.append(metrics)

                # 히스토리 관리
                self._cleanup_old_metrics()

                # 알림 체크
                alerts = self._check_for_alerts(metrics)
                self._alert_history.extend(alerts)

                # 알림 처리
                for alert in alerts:
                    self._process_alert(alert)

                # Echo 서비스 체크
                self._check_echo_services()

                time.sleep(self.monitoring_config["collection_interval"])

            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)  # 에러 시 5초 대기

    def _collect_system_metrics(self) -> SystemMetrics:
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)

            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 디스크 사용률
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = usage.percent
                except PermissionError:
                    pass

            # 네트워크 I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            }

            # 프로세스 수
            process_count = len(psutil.pids())

            # 시스템 업타임
            uptime = time.time() - psutil.boot_time()

            # 로드 평균 (Linux/macOS만)
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                load_avg = [0.0, 0.0, 0.0]  # Windows는 지원 안함

            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage=disk_usage,
                network_io=network_io,
                process_count=process_count,
                uptime=uptime,
                load_average=load_avg,
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage={},
                network_io={},
                process_count=0,
                uptime=0.0,
                load_average=[0.0, 0.0, 0.0],
                timestamp=datetime.now().isoformat(),
            )

    def _evaluate_health_status(
        self, metrics: SystemMetrics, signature: str
    ) -> HealthStatus:
        """건강 상태 평가"""
        component_scores = {}
        warnings = []
        critical_issues = []
        recommendations = []

        thresholds = self.health_thresholds

        # CPU 평가
        cpu_score = self._evaluate_cpu_health(metrics.cpu_percent, thresholds["cpu"])
        component_scores["cpu"] = cpu_score
        if metrics.cpu_percent > thresholds["cpu"]["critical"]:
            critical_issues.append(f"CPU usage critical: {metrics.cpu_percent:.1f}%")
        elif metrics.cpu_percent > thresholds["cpu"]["warning"]:
            warnings.append(f"CPU usage high: {metrics.cpu_percent:.1f}%")

        # 메모리 평가
        memory_score = self._evaluate_memory_health(
            metrics.memory_percent, thresholds["memory"]
        )
        component_scores["memory"] = memory_score
        if metrics.memory_percent > thresholds["memory"]["critical"]:
            critical_issues.append(
                f"Memory usage critical: {metrics.memory_percent:.1f}%"
            )
        elif metrics.memory_percent > thresholds["memory"]["warning"]:
            warnings.append(f"Memory usage high: {metrics.memory_percent:.1f}%")

        # 디스크 평가
        disk_scores = []
        for mount, usage in metrics.disk_usage.items():
            score = self._evaluate_disk_health(usage, thresholds["disk"])
            disk_scores.append(score)
            if usage > thresholds["disk"]["critical"]:
                critical_issues.append(f"Disk {mount} critical: {usage:.1f}%")
            elif usage > thresholds["disk"]["warning"]:
                warnings.append(f"Disk {mount} high: {usage:.1f}%")

        component_scores["disk"] = (
            sum(disk_scores) / len(disk_scores) if disk_scores else 1.0
        )

        # 전체 점수 계산
        overall_score = sum(component_scores.values()) / len(component_scores)

        # 시그니처별 추천 사항
        recommendations = self._generate_signature_recommendations(
            metrics, component_scores, signature
        )

        # 트렌드 분석
        trend_analysis = self._analyze_trends(metrics)

        return HealthStatus(
            overall_score=overall_score,
            component_scores=component_scores,
            warnings=warnings,
            critical_issues=critical_issues,
            recommendations=recommendations,
            trend_analysis=trend_analysis,
        )

    def _check_for_alerts(self, metrics: SystemMetrics) -> List[PerformanceAlert]:
        """알림 체크"""
        alerts = []
        thresholds = self.health_thresholds
        current_time = datetime.now().isoformat()

        # CPU 알림
        if metrics.cpu_percent > thresholds["cpu"]["critical"]:
            alerts.append(
                PerformanceAlert(
                    severity="critical",
                    component="cpu",
                    message=f"CPU usage critically high: {metrics.cpu_percent:.1f}%",
                    metric_value=metrics.cpu_percent,
                    threshold=thresholds["cpu"]["critical"],
                    timestamp=current_time,
                    suggested_action="Identify and optimize high-CPU processes",
                )
            )
        elif metrics.cpu_percent > thresholds["cpu"]["warning"]:
            alerts.append(
                PerformanceAlert(
                    severity="warning",
                    component="cpu",
                    message=f"CPU usage high: {metrics.cpu_percent:.1f}%",
                    metric_value=metrics.cpu_percent,
                    threshold=thresholds["cpu"]["warning"],
                    timestamp=current_time,
                    suggested_action="Monitor CPU usage and consider optimization",
                )
            )

        # 메모리 알림
        if metrics.memory_percent > thresholds["memory"]["critical"]:
            alerts.append(
                PerformanceAlert(
                    severity="critical",
                    component="memory",
                    message=f"Memory usage critically high: {metrics.memory_percent:.1f}%",
                    metric_value=metrics.memory_percent,
                    threshold=thresholds["memory"]["critical"],
                    timestamp=current_time,
                    suggested_action="Free memory or restart services",
                )
            )

        return alerts

    def _check_echo_services(self):
        """Echo 서비스 상태 체크"""
        try:
            # Echo 관련 프로세스 찾기
            echo_processes = []
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    cmdline = " ".join(proc.info["cmdline"] or [])
                    if "echo" in cmdline.lower() and "python" in cmdline.lower():
                        echo_processes.append(
                            {
                                "pid": proc.info["pid"],
                                "name": proc.info["name"],
                                "cmdline": cmdline,
                            }
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # 서비스 상태 로깅
            if echo_processes:
                logger.info(f"✅ Echo services running: {len(echo_processes)}")
            else:
                logger.warning("⚠️ No Echo services detected")

        except Exception as e:
            logger.error(f"Failed to check Echo services: {e}")


# 에이전트 인스턴스 생성 함수
def create_health_monitor_agent() -> EchoHealthMonitorAgent:
    """건강 모니터링 에이전트 생성"""
    return EchoHealthMonitorAgent()
