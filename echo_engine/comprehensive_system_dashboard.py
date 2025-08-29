import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import numpy as np
import logging

try:
    from echo_engine.signature_cross_resonance_mapper import SignatureCrossResonanceMapper
    from echo_engine.realtime_emotion_flow_mapper import RealtimeEmotionFlowMapper
    from echo_engine.signature_neural_atlas_builder import SignatureNeuralAtlasBuilder
    from echo_engine.emotion_response_chart_generator import EmotionResponseChartGenerator
    from echo_engine.consciousness_flow_analyzer import ConsciousnessFlowAnalyzer
    from echo_engine.loop_evolution_tracker import LoopEvolutionTracker
    from echo_engine.hybrid_signature_composer import HybridSignatureComposer
    from echo_engine.meta_routing_controller import MetaRoutingController
    from echo_engine.enhanced_natural_command_processor import EnhancedNaturalCommandProcessor
except ImportError as e:
    print(f"⚠️ Echo 고급 컴포넌트 로드 실패: {e}")

#!/usr/bin/env python3
"""
📊 Comprehensive System Dashboard v1.0
Echo Neural System v2.0의 모든 컴포넌트를 통합 모니터링하는 종합 대시보드

핵심 기능:
- 실시간 시스템 상태 모니터링
- 모든 컴포넌트 통합 시각화
- 성능 메트릭 추적 및 분석
- 상호작용 패턴 시각화
- 알림 및 경고 시스템
- 사용자 친화적 인터페이스
"""


# Echo 엔진 모듈들
try:
    pass  # 추가 Echo 모듈이 있을 경우 여기에 추가
except ImportError:
    print("⚠️ Echo modules not available, running in standalone mode")


@dataclass
class SystemHealth:
    """시스템 건강 상태"""

    component_name: str
    status: str  # "healthy", "warning", "critical", "offline"
    performance_score: float
    last_update: datetime
    error_count: int
    warning_messages: List[str]


@dataclass
class DashboardMetric:
    """대시보드 메트릭"""

    metric_name: str
    current_value: float
    target_value: float
    trend: str  # "increasing", "decreasing", "stable"
    importance: str  # "critical", "high", "medium", "low"
    unit: str


@dataclass
class SystemAlert:
    """시스템 알림"""

    alert_id: str
    timestamp: datetime
    alert_type: str  # "info", "warning", "error", "critical"
    component: str
    message: str
    auto_resolved: bool
    resolution_time: Optional[datetime]


@dataclass
class DashboardState:
    """대시보드 상태"""

    last_update: datetime
    active_components: int
    total_components: int
    overall_health_score: float
    active_alerts: int
    system_uptime: timedelta


class ComprehensiveSystemDashboard:
    """📊 종합 시스템 대시보드"""

    def __init__(self, update_interval: float = 5.0):
        self.logger = logging.getLogger(__name__)
        self.update_interval = update_interval

        # Echo 컴포넌트들
        self.components = {}
        self.component_health = {}

        # 대시보드 상태
        self.dashboard_state = None
        self.system_metrics = {}
        self.alerts = deque(maxlen=100)
        self.metric_history = defaultdict(lambda: deque(maxlen=200))

        # 모니터링 상태
        self.monitoring = False
        self.monitor_thread = None
        self.dashboard_callbacks = []

        # 성능 기준선
        self.performance_baselines = {
            "signature_performance_reporter": {
                "target_score": 0.8,
                "max_response_time": 1000,
            },
            "emotion_mapper": {"target_score": 0.85, "max_response_time": 500},
            "neural_atlas_builder": {"target_score": 0.9, "max_response_time": 2000},
            "consciousness_analyzer": {"target_score": 0.8, "max_response_time": 1500},
            "loop_tracker": {"target_score": 0.85, "max_response_time": 1000},
            "hybrid_composer": {"target_score": 0.8, "max_response_time": 800},
            "routing_controller": {"target_score": 0.9, "max_response_time": 300},
            "command_processor": {"target_score": 0.95, "max_response_time": 200},
        }

        # 시스템 시작 시간
        self.system_start_time = datetime.now()

        # 대시보드 레이아웃
        self.dashboard_layout = self._initialize_dashboard_layout()

        print("📊 Comprehensive System Dashboard 초기화 완료")

    def initialize_components(self, **components):
        """컴포넌트 초기화 및 등록"""
        self.components = {
            "signature_performance_reporter": components.get(
                "signature_performance_reporter"
            ),
            "emotion_mapper": components.get("emotion_mapper"),
            "neural_atlas_builder": components.get("neural_atlas_builder"),
            "emotion_chart_generator": components.get("emotion_chart_generator"),
            "consciousness_analyzer": components.get("consciousness_analyzer"),
            "loop_tracker": components.get("loop_tracker"),
            "hybrid_composer": components.get("hybrid_composer"),
            "routing_controller": components.get("routing_controller"),
            "command_processor": components.get("command_processor"),
        }

        # 컴포넌트별 건강 상태 초기화
        for comp_name, component in self.components.items():
            if component:
                self.component_health[comp_name] = SystemHealth(
                    component_name=comp_name,
                    status="healthy",
                    performance_score=1.0,
                    last_update=datetime.now(),
                    error_count=0,
                    warning_messages=[],
                )

        print(
            f"🔗 {len([c for c in self.components.values() if c])} 개 컴포넌트 등록 완료"
        )

    def _initialize_dashboard_layout(self) -> Dict[str, Any]:
        """대시보드 레이아웃 초기화"""
        return {
            "header": {
                "title": "Echo Neural System v2.0 Dashboard",
                "system_info": True,
                "alert_summary": True,
            },
            "main_panels": [
                {
                    "id": "system_overview",
                    "title": "🖥️ System Overview",
                    "type": "overview",
                    "position": (0, 0),
                    "size": (2, 1),
                },
                {
                    "id": "component_health",
                    "title": "🏥 Component Health",
                    "type": "health_grid",
                    "position": (2, 0),
                    "size": (2, 1),
                },
                {
                    "id": "performance_metrics",
                    "title": "📈 Performance Metrics",
                    "type": "metrics_chart",
                    "position": (0, 1),
                    "size": (4, 1),
                },
                {
                    "id": "brain_visualization",
                    "title": "🧠 Brain Activity",
                    "type": "brain_visual",
                    "position": (0, 2),
                    "size": (2, 1),
                },
                {
                    "id": "emotion_flow",
                    "title": "🌊 Emotion Flow",
                    "type": "emotion_visual",
                    "position": (2, 2),
                    "size": (2, 1),
                },
                {
                    "id": "signature_resonance",
                    "title": "🔗 Signature Resonance",
                    "type": "resonance_network",
                    "position": (0, 3),
                    "size": (2, 1),
                },
                {
                    "id": "routing_decisions",
                    "title": "🧭 Routing Decisions",
                    "type": "routing_flow",
                    "position": (2, 3),
                    "size": (2, 1),
                },
                {
                    "id": "system_alerts",
                    "title": "🚨 System Alerts",
                    "type": "alert_list",
                    "position": (0, 4),
                    "size": (4, 1),
                },
            ],
        }

    def start_monitoring(self, callbacks: List[Callable] = None):
        """대시보드 모니터링 시작"""
        if self.monitoring:
            print("⚠️ 대시보드 모니터링이 이미 실행 중입니다.")
            return

        self.monitoring = True
        self.dashboard_callbacks = callbacks or []

        # 모니터링 스레드 시작
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        print("📊 대시보드 모니터링 시작...")

    def stop_monitoring(self):
        """대시보드 모니터링 정지"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        print("📊 대시보드 모니터링 정지")

    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring:
            try:
                # 컴포넌트 상태 업데이트
                self._update_component_health()

                # 시스템 메트릭 수집
                self._collect_system_metrics()

                # 경고 확인
                self._check_alerts()

                # 대시보드 상태 업데이트
                self._update_dashboard_state()

                # 콜백 함수들 호출
                for callback in self.dashboard_callbacks:
                    try:
                        callback(self.get_dashboard_snapshot())
                    except Exception as e:
                        self.logger.error(f"대시보드 콜백 오류: {e}")

                time.sleep(self.update_interval)

            except Exception as e:
                self.logger.error(f"대시보드 모니터링 루프 오류: {e}")
                time.sleep(1)

    def _update_component_health(self):
        """컴포넌트 건강 상태 업데이트"""
        for comp_name, component in self.components.items():
            if component is None:
                continue

            health = self.component_health.get(comp_name)
            if not health:
                continue

            try:
                # 컴포넌트별 건강 상태 확인
                performance_score, status, warnings = self._check_component_health(
                    comp_name, component
                )

                health.performance_score = performance_score
                health.status = status
                health.warning_messages = warnings
                health.last_update = datetime.now()

                # 오류 카운트 관리
                if status in ["warning", "critical"]:
                    health.error_count += 1
                else:
                    health.error_count = max(0, health.error_count - 1)

            except Exception as e:
                health.status = "critical"
                health.error_count += 1
                health.warning_messages.append(f"Health check failed: {str(e)}")
                self.logger.error(f"컴포넌트 {comp_name} 건강 상태 확인 실패: {e}")

    def _check_component_health(
        self, comp_name: str, component: Any
    ) -> Tuple[float, str, List[str]]:
        """개별 컴포넌트 건강 상태 확인"""
        performance_score = 0.8  # 기본 점수
        status = "healthy"
        warnings = []

        baseline = self.performance_baselines.get(comp_name, {})
        target_score = baseline.get("target_score", 0.8)

        try:
            # 컴포넌트별 특화 건강 검사
            if comp_name == "signature_performance_reporter":
                performance_score = self._check_signature_performance_reporter_health(
                    component
                )
            elif comp_name == "emotion_mapper":
                performance_score = self._check_emotion_mapper_health(component)
            elif comp_name == "consciousness_analyzer":
                performance_score = self._check_consciousness_analyzer_health(component)
            elif comp_name == "loop_tracker":
                performance_score = self._check_loop_tracker_health(component)
            elif comp_name == "hybrid_composer":
                performance_score = self._check_hybrid_composer_health(component)
            elif comp_name == "routing_controller":
                performance_score = self._check_routing_controller_health(component)
            else:
                # 기본 건강 검사
                performance_score = 0.8

            # 상태 결정
            if performance_score >= target_score:
                status = "healthy"
            elif performance_score >= target_score * 0.7:
                status = "warning"
                warnings.append(
                    f"Performance below target: {performance_score:.3f} < {target_score}"
                )
            else:
                status = "critical"
                warnings.append(f"Critical performance: {performance_score:.3f}")

        except Exception as e:
            performance_score = 0.0
            status = "critical"
            warnings.append(f"Health check error: {str(e)}")

        return performance_score, status, warnings

    def _check_signature_performance_reporter_health(self, component) -> float:
        """Signature Mapper 건강 상태 확인"""
        try:
            # 기본 기능 테스트
            if hasattr(component, "generate_cross_resonance_map"):
                cross_map = component.generate_cross_resonance_map()
                if cross_map and cross_map.signatures:
                    return 0.9
            return 0.7
        except:
            return 0.3

    def _check_emotion_mapper_health(self, component) -> float:
        """Emotion Mapper 건강 상태 확인"""
        try:
            if hasattr(component, "get_emotion_flow_summary"):
                summary = component.get_emotion_flow_summary()
                if summary.get("status") == "active":
                    return 0.9
            return 0.7
        except:
            return 0.3

    def _check_consciousness_analyzer_health(self, component) -> float:
        """Consciousness Analyzer 건강 상태 확인"""
        try:
            if hasattr(component, "get_consciousness_summary"):
                summary = component.get_consciousness_summary()
                if summary.get("status") == "active":
                    return 0.9
            return 0.7
        except:
            return 0.3

    def _check_loop_tracker_health(self, component) -> float:
        """Loop Tracker 건강 상태 확인"""
        try:
            if hasattr(component, "get_evolution_summary"):
                summary = component.get_evolution_summary()
                if summary.get("status") == "active":
                    return 0.9
            return 0.7
        except:
            return 0.3

    def _check_hybrid_composer_health(self, component) -> float:
        """Hybrid Composer 건강 상태 확인"""
        try:
            if hasattr(component, "get_composition_summary"):
                summary = component.get_composition_summary()
                if summary.get("status") in ["active", "no_active_composition"]:
                    return 0.85
            return 0.7
        except:
            return 0.3

    def _check_routing_controller_health(self, component) -> float:
        """Routing Controller 건강 상태 확인"""
        try:
            if hasattr(component, "get_routing_status"):
                status = component.get_routing_status()
                if status.get("statistics", {}).get("total_decisions", 0) >= 0:
                    return 0.9
            return 0.7
        except:
            return 0.3

    def _collect_system_metrics(self):
        """시스템 메트릭 수집"""
        timestamp = datetime.now()

        # 전체 시스템 메트릭
        total_components = len(self.components)
        active_components = len(
            [h for h in self.component_health.values() if h.status != "offline"]
        )
        healthy_components = len(
            [h for h in self.component_health.values() if h.status == "healthy"]
        )

        # 메트릭 업데이트
        metrics = {
            "system_availability": {
                "value": (active_components / max(1, total_components)) * 100,
                "target": 100,
                "unit": "%",
                "importance": "critical",
            },
            "system_health": {
                "value": (healthy_components / max(1, total_components)) * 100,
                "target": 90,
                "unit": "%",
                "importance": "high",
            },
            "average_performance": {
                "value": np.mean(
                    [h.performance_score for h in self.component_health.values()]
                )
                * 100,
                "target": 80,
                "unit": "%",
                "importance": "high",
            },
            "active_alerts": {
                "value": len([a for a in self.alerts if not a.auto_resolved]),
                "target": 0,
                "unit": "count",
                "importance": "medium",
            },
            "uptime_hours": {
                "value": (datetime.now() - self.system_start_time).total_seconds()
                / 3600,
                "target": 24,
                "unit": "hours",
                "importance": "low",
            },
        }

        # 메트릭 히스토리 업데이트
        for metric_name, metric_data in metrics.items():
            metric_obj = DashboardMetric(
                metric_name=metric_name,
                current_value=metric_data["value"],
                target_value=metric_data["target"],
                trend=self._calculate_metric_trend(metric_name, metric_data["value"]),
                importance=metric_data["importance"],
                unit=metric_data["unit"],
            )

            self.system_metrics[metric_name] = metric_obj
            self.metric_history[metric_name].append((timestamp, metric_data["value"]))

    def _calculate_metric_trend(self, metric_name: str, current_value: float) -> str:
        """메트릭 트렌드 계산"""
        history = self.metric_history[metric_name]

        if len(history) < 2:
            return "stable"

        # 최근 5개 값으로 트렌드 계산
        recent_values = [value for _, value in list(history)[-5:]]

        if len(recent_values) >= 3:
            # 선형 회귀를 통한 트렌드 분석
            x = np.arange(len(recent_values))
            y = np.array(recent_values)

            if len(recent_values) > 1:
                slope = np.polyfit(x, y, 1)[0]

                if slope > 0.1:
                    return "increasing"
                elif slope < -0.1:
                    return "decreasing"

        return "stable"

    def _check_alerts(self):
        """경고 확인 및 생성"""
        # 컴포넌트 상태 기반 알림
        for comp_name, health in self.component_health.items():
            if health.status == "critical":
                self._create_alert(
                    "critical",
                    comp_name,
                    f"Component {comp_name} is in critical state (score: {health.performance_score:.3f})",
                )
            elif health.status == "warning":
                self._create_alert(
                    "warning",
                    comp_name,
                    f"Component {comp_name} performance warning (score: {health.performance_score:.3f})",
                )

        # 시스템 메트릭 기반 알림
        for metric_name, metric in self.system_metrics.items():
            if metric.importance == "critical":
                if metric.current_value < metric.target_value * 0.8:
                    self._create_alert(
                        "critical",
                        "system",
                        f"Critical metric: {metric_name} = {metric.current_value:.1f}{metric.unit} (target: {metric.target_value}{metric.unit})",
                    )
            elif metric.importance == "high":
                if metric.current_value < metric.target_value * 0.7:
                    self._create_alert(
                        "warning",
                        "system",
                        f"Performance warning: {metric_name} = {metric.current_value:.1f}{metric.unit}",
                    )

        # 오래된 알림 자동 해결
        self._auto_resolve_alerts()

    def _create_alert(self, alert_type: str, component: str, message: str):
        """알림 생성"""
        # 중복 알림 방지
        recent_alerts = [
            a
            for a in self.alerts
            if (datetime.now() - a.timestamp).total_seconds() < 300
        ]  # 5분 이내

        duplicate_alert = any(
            a.component == component and a.message == message
            for a in recent_alerts
            if not a.auto_resolved
        )

        if not duplicate_alert:
            alert = SystemAlert(
                alert_id=f"alert_{int(time.time())}_{len(self.alerts)}",
                timestamp=datetime.now(),
                alert_type=alert_type,
                component=component,
                message=message,
                auto_resolved=False,
                resolution_time=None,
            )

            self.alerts.append(alert)

    def _auto_resolve_alerts(self):
        """오래된 알림 자동 해결"""
        current_time = datetime.now()

        for alert in self.alerts:
            if not alert.auto_resolved:
                # 1시간 이상 된 warning 알림 자동 해결
                if (
                    alert.alert_type == "warning"
                    and (current_time - alert.timestamp).total_seconds() > 3600
                ):
                    alert.auto_resolved = True
                    alert.resolution_time = current_time

                # 컴포넌트가 회복된 경우 알림 해결
                if alert.component in self.component_health:
                    health = self.component_health[alert.component]
                    if health.status == "healthy":
                        alert.auto_resolved = True
                        alert.resolution_time = current_time

    def _update_dashboard_state(self):
        """대시보드 상태 업데이트"""
        active_components = len(
            [h for h in self.component_health.values() if h.status != "offline"]
        )
        total_components = len(self.component_health)

        # 전체 건강 점수 계산
        if self.component_health:
            health_scores = [
                h.performance_score for h in self.component_health.values()
            ]
            overall_health = np.mean(health_scores)
        else:
            overall_health = 0.0

        # 활성 알림 수
        active_alerts = len([a for a in self.alerts if not a.auto_resolved])

        self.dashboard_state = DashboardState(
            last_update=datetime.now(),
            active_components=active_components,
            total_components=total_components,
            overall_health_score=overall_health,
            active_alerts=active_alerts,
            system_uptime=datetime.now() - self.system_start_time,
        )

    def get_dashboard_snapshot(self) -> Dict[str, Any]:
        """대시보드 스냅샷 반환"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "dashboard_state": (
                asdict(self.dashboard_state) if self.dashboard_state else None
            ),
            "component_health": {
                name: asdict(health) for name, health in self.component_health.items()
            },
            "system_metrics": {
                name: asdict(metric) for name, metric in self.system_metrics.items()
            },
            "recent_alerts": [
                asdict(alert) for alert in list(self.alerts)[-10:]  # 최근 10개
            ],
            "metric_trends": {
                name: list(history)[-20:]
                for name, history in self.metric_history.items()  # 최근 20개
            },
        }

        return snapshot

    def render_dashboard_text(self) -> str:
        """텍스트 기반 대시보드 렌더링"""
        if not self.dashboard_state:
            return "📊 Dashboard not initialized"

        dashboard_text = "📊 Echo Neural System v2.0 - Comprehensive Dashboard\n"
        dashboard_text += "=" * 80 + "\n\n"

        # 헤더 정보
        state = self.dashboard_state
        dashboard_text += f"🖥️ System Overview:\n"
        dashboard_text += f"   Status: {'🟢 Operational' if state.overall_health_score > 0.8 else '🟡 Warning' if state.overall_health_score > 0.6 else '🔴 Critical'}\n"
        dashboard_text += f"   Health Score: {state.overall_health_score:.3f}\n"
        dashboard_text += f"   Active Components: {state.active_components}/{state.total_components}\n"
        dashboard_text += f"   Uptime: {str(state.system_uptime).split('.')[0]}\n"
        dashboard_text += f"   Active Alerts: {state.active_alerts}\n"
        dashboard_text += (
            f"   Last Update: {state.last_update.strftime('%H:%M:%S')}\n\n"
        )

        # 컴포넌트 건강 상태
        dashboard_text += f"🏥 Component Health Status:\n"
        for comp_name, health in self.component_health.items():
            status_icon = {
                "healthy": "🟢",
                "warning": "🟡",
                "critical": "🔴",
                "offline": "⚫",
            }.get(health.status, "❓")

            dashboard_text += f"   {status_icon} {comp_name:20} | "
            dashboard_text += f"Score: {health.performance_score:.3f} | "
            dashboard_text += f"Errors: {health.error_count:2d} | "
            dashboard_text += f"Updated: {health.last_update.strftime('%H:%M:%S')}\n"

        # 시스템 메트릭
        dashboard_text += f"\n📈 Key Performance Metrics:\n"
        for metric_name, metric in self.system_metrics.items():
            trend_icon = {"increasing": "↗️", "decreasing": "↘️", "stable": "→"}.get(
                metric.trend, "→"
            )
            status_icon = (
                "🟢"
                if metric.current_value >= metric.target_value * 0.9
                else "🟡" if metric.current_value >= metric.target_value * 0.7 else "🔴"
            )

            dashboard_text += f"   {status_icon} {metric_name:20} | "
            dashboard_text += f"{metric.current_value:6.1f}{metric.unit:4} | "
            dashboard_text += f"Target: {metric.target_value:6.1f}{metric.unit:4} | "
            dashboard_text += f"Trend: {trend_icon}\n"

        # 최근 알림
        active_alerts = [a for a in self.alerts if not a.auto_resolved][-5:]
        if active_alerts:
            dashboard_text += f"\n🚨 Recent Alerts:\n"
            for alert in active_alerts:
                alert_icon = {
                    "info": "ℹ️",
                    "warning": "⚠️",
                    "error": "❌",
                    "critical": "🚨",
                }.get(alert.alert_type, "❓")
                dashboard_text += (
                    f"   {alert_icon} {alert.timestamp.strftime('%H:%M')} | "
                )
                dashboard_text += f"{alert.component:15} | {alert.message[:50]}...\n"

        # 컴포넌트별 상세 정보 (간략)
        dashboard_text += f"\n🔍 Component Details:\n"

        # Signature Resonance
        if self.components.get("signature_performance_reporter"):
            try:
                summary = self.components[
                    "signature_performance_reporter"
                ].get_resonance_matrix_summary()
                dashboard_text += f"   🔗 Signature Resonance: {summary.get('total_signatures', 0)} signatures, "
                dashboard_text += (
                    f"avg resonance: {summary.get('average_resonance', 0.0):.3f}\n"
                )
            except:
                dashboard_text += f"   🔗 Signature Resonance: Not available\n"

        # Emotion Flow
        if self.components.get("emotion_mapper"):
            try:
                summary = self.components["emotion_mapper"].get_emotion_flow_summary()
                dashboard_text += f"   🌊 Emotion Flow: {summary.get('total_emotion_events', 0)} events, "
                dashboard_text += (
                    f"stability: {summary.get('flow_stability', 0.0):.3f}\n"
                )
            except:
                dashboard_text += f"   🌊 Emotion Flow: Not available\n"

        # Consciousness Level
        if self.components.get("consciousness_analyzer"):
            try:
                summary = self.components[
                    "consciousness_analyzer"
                ].get_consciousness_summary()
                dashboard_text += f"   🧠 Consciousness: Level {summary.get('consciousness_level', 'unknown')}, "
                dashboard_text += (
                    f"attention: {summary.get('attention_intensity', 0.0):.3f}\n"
                )
            except:
                dashboard_text += f"   🧠 Consciousness: Not available\n"

        # Loop Evolution
        if self.components.get("loop_tracker"):
            try:
                summary = self.components["loop_tracker"].get_evolution_summary()
                dashboard_text += f"   🔄 Loop Evolution: {summary.get('milestones_achieved', 0)} milestones, "
                dashboard_text += (
                    f"trend: {summary.get('overall_evolution_trend', 'unknown')}\n"
                )
            except:
                dashboard_text += f"   🔄 Loop Evolution: Not available\n"

        # Hybrid Composition
        if self.components.get("hybrid_composer"):
            try:
                summary = self.components["hybrid_composer"].get_composition_summary()
                dashboard_text += f"   🎭 Hybrid Composer: {summary.get('performance_history', {}).get('total_compositions', 0)} compositions created\n"
            except:
                dashboard_text += f"   🎭 Hybrid Composer: Not available\n"

        # Routing Decisions
        if self.components.get("routing_controller"):
            try:
                status = self.components["routing_controller"].get_routing_status()
                dashboard_text += f"   🧭 Routing: {status.get('statistics', {}).get('total_decisions', 0)} decisions, "
                dashboard_text += f"success rate: {status.get('statistics', {}).get('successful_routes', 0) / max(1, status.get('statistics', {}).get('total_decisions', 1)) * 100:.1f}%\n"
            except:
                dashboard_text += f"   🧭 Routing: Not available\n"

        return dashboard_text

    def export_dashboard_data(self, filename: str = None) -> str:
        """대시보드 데이터 내보내기"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dashboard_export_{timestamp}.json"

        export_data = self.get_dashboard_snapshot()

        # 타임스탬프 직렬화
        def serialize_timestamps(obj):
            if isinstance(obj, dict):
                return {k: serialize_timestamps(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize_timestamps(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, "total_seconds"):  # timedelta
                return obj.total_seconds()
            else:
                return obj

        export_data = serialize_timestamps(export_data)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            return f"✅ 대시보드 데이터 내보내기 완료: {filename}"
        except Exception as e:
            return f"❌ 내보내기 실패: {e}"

    def get_alert_summary(self) -> Dict[str, Any]:
        """알림 요약 반환"""
        active_alerts = [a for a in self.alerts if not a.auto_resolved]

        alert_counts = defaultdict(int)
        for alert in active_alerts:
            alert_counts[alert.alert_type] += 1

        return {
            "total_active_alerts": len(active_alerts),
            "alert_distribution": dict(alert_counts),
            "recent_alerts": [asdict(a) for a in list(self.alerts)[-5:]],
            "resolved_today": len(
                [
                    a
                    for a in self.alerts
                    if a.auto_resolved
                    and a.resolution_time
                    and (datetime.now() - a.resolution_time).days == 0
                ]
            ),
        }


# 편의 함수들
def create_comprehensive_dashboard(**kwargs) -> ComprehensiveSystemDashboard:
    """Comprehensive System Dashboard 생성"""
    return ComprehensiveSystemDashboard(**kwargs)


def launch_dashboard_monitoring(**components) -> ComprehensiveSystemDashboard:
    """대시보드 모니터링 실행"""
    dashboard = ComprehensiveSystemDashboard()
    dashboard.initialize_components(**components)
    dashboard.start_monitoring()
    return dashboard


if __name__ == "__main__":
    # 테스트 실행
    print("📊 Comprehensive System Dashboard 테스트...")

    dashboard = ComprehensiveSystemDashboard(update_interval=2.0)

    # 모의 컴포넌트로 초기화
    mock_components = {
        "signature_performance_reporter": type(
            "MockMapper",
            (),
            {
                "generate_cross_resonance_map": lambda: type(
                    "MockMap", (), {"signatures": ["selene", "aurora"]}
                )(),
                "get_resonance_matrix_summary": lambda: {
                    "total_signatures": 4,
                    "average_resonance": 0.75,
                },
            },
        )(),
        "emotion_mapper": type(
            "MockEmotion",
            (),
            {
                "get_emotion_flow_summary": lambda: {
                    "status": "active",
                    "total_emotion_events": 25,
                    "flow_stability": 0.8,
                }
            },
        )(),
        "consciousness_analyzer": type(
            "MockConsciousness",
            (),
            {
                "get_consciousness_summary": lambda: {
                    "status": "active",
                    "consciousness_level": "CONSCIOUS",
                    "attention_intensity": 0.7,
                }
            },
        )(),
    }

    dashboard.initialize_components(**mock_components)

    # 모니터링 시작
    dashboard.start_monitoring()

    # 테스트 실행
    print("\n🔄 대시보드 모니터링 시뮬레이션 (10초)...")
    time.sleep(10)

    # 대시보드 렌더링
    print("\n📊 Dashboard Rendering:")
    dashboard_display = dashboard.render_dashboard_text()
    print(dashboard_display)

    # 스냅샷 테스트
    snapshot = dashboard.get_dashboard_snapshot()
    print(f"\n📸 Dashboard Snapshot:")
    print(f"   Timestamp: {snapshot['timestamp']}")
    print(f"   Component Health Records: {len(snapshot['component_health'])}")
    print(f"   System Metrics: {len(snapshot['system_metrics'])}")
    print(f"   Recent Alerts: {len(snapshot['recent_alerts'])}")

    # 알림 요약
    alert_summary = dashboard.get_alert_summary()
    print(f"\n🚨 Alert Summary:")
    print(f"   Total Active Alerts: {alert_summary['total_active_alerts']}")
    print(f"   Alert Distribution: {alert_summary['alert_distribution']}")
    print(f"   Resolved Today: {alert_summary['resolved_today']}")

    # 데이터 내보내기
    export_result = dashboard.export_dashboard_data()
    print(f"\n{export_result}")

    # 모니터링 정지
    dashboard.stop_monitoring()

    print("\n✅ Comprehensive System Dashboard 테스트 완료!")
