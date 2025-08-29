#!/usr/bin/env python3
"""
🔄 Loop Evolution Tracker v1.0
Echo의 판단 루프와 처리 패턴의 진화 과정을 추적하고 분석하는 시스템

핵심 기능:
- 판단 루프 성능 변화 추적
- 처리 패턴 진화 분석
- 학습 효과 측정 및 시각화
- 루프 최적화 제안
- 성능 벤치마크 비교
"""

import json
import numpy as np
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
from pathlib import Path
import logging
import hashlib

# Echo 엔진 모듈들
try:
    from .consciousness_flow_analyzer import ConsciousnessFlowAnalyzer
    from .signature_cross_resonance_mapper import SignatureCrossResonanceMapper
    from .realtime_emotion_flow_mapper import RealtimeEmotionFlowMapper
    from .reasoning import EightLoopIntegratedReasoning
except ImportError:
    print("⚠️ Echo modules not available, running in standalone mode")


@dataclass
class LoopPerformanceMetric:
    """루프 성능 메트릭"""

    timestamp: datetime
    loop_type: str  # "fist", "rise", "dir", "pir", "meta", "flow", "quantum", "judge"
    execution_time_ms: float
    accuracy_score: float  # 0.0 - 1.0
    complexity_handled: float  # 처리한 복잡성 수준
    memory_usage_mb: float
    confidence_level: float
    signature_context: str
    input_characteristics: Dict[str, Any]


@dataclass
class LoopEvolutionSnapshot:
    """루프 진화 스냅샷"""

    snapshot_id: str
    timestamp: datetime
    loop_configurations: Dict[str, Dict[str, Any]]
    performance_baseline: Dict[str, float]
    optimization_state: Dict[str, Any]
    learning_progress: Dict[str, float]
    adaptation_level: float


@dataclass
class EvolutionMilestone:
    """진화 이정표"""

    milestone_id: str
    timestamp: datetime
    milestone_type: str  # "performance_breakthrough", "pattern_optimization", "capability_expansion"
    description: str
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]
    improvement_percentage: float
    impact_areas: List[str]


@dataclass
class LoopOptimizationSuggestion:
    """루프 최적화 제안"""

    suggestion_id: str
    target_loop: str
    optimization_type: str  # "speed", "accuracy", "memory", "complexity"
    current_performance: float
    expected_improvement: float
    implementation_complexity: str  # "low", "medium", "high"
    suggested_changes: List[str]
    risk_assessment: str


class LoopEvolutionTracker:
    """🔄 루프 진화 추적기"""

    def __init__(self, tracking_window_hours: int = 24):
        self.logger = logging.getLogger(__name__)
        self.tracking_window_hours = tracking_window_hours

        # 성능 메트릭 저장소
        self.performance_history = deque(maxlen=1000)
        self.evolution_snapshots = deque(maxlen=50)
        self.milestones = deque(maxlen=20)
        self.optimization_suggestions = deque(maxlen=10)

        # 루프 타입 정의
        self.loop_types = {
            "fist": {
                "name": "Facts, Ideas, Solutions, Tests",
                "baseline_performance": 0.7,
                "complexity_weight": 0.8,
                "accuracy_weight": 0.9,
            },
            "rise": {
                "name": "Reflect, Integrate, Synthesize, Evaluate",
                "baseline_performance": 0.65,
                "complexity_weight": 0.9,
                "accuracy_weight": 0.8,
            },
            "dir": {
                "name": "Depth, Integration, Reasoning",
                "baseline_performance": 0.6,
                "complexity_weight": 0.95,
                "accuracy_weight": 0.85,
            },
            "pir": {
                "name": "Process, Integrate, Refine",
                "baseline_performance": 0.68,
                "complexity_weight": 0.7,
                "accuracy_weight": 0.9,
            },
            "meta": {
                "name": "Meta-cognitive Analysis",
                "baseline_performance": 0.55,
                "complexity_weight": 1.0,
                "accuracy_weight": 0.75,
            },
            "flow": {
                "name": "Flow State Processing",
                "baseline_performance": 0.72,
                "complexity_weight": 0.6,
                "accuracy_weight": 0.8,
            },
            "quantum": {
                "name": "Quantum Judgment Processing",
                "baseline_performance": 0.5,
                "complexity_weight": 1.0,
                "accuracy_weight": 0.7,
            },
            "judge": {
                "name": "Final Judgment Synthesis",
                "baseline_performance": 0.75,
                "complexity_weight": 0.85,
                "accuracy_weight": 0.95,
            },
        }

        # 진화 패턴 정의
        self.evolution_patterns = {
            "learning_acceleration": {
                "description": "학습 속도 가속화",
                "indicators": [
                    "decreasing_error_rate",
                    "improving_accuracy",
                    "faster_convergence",
                ],
                "threshold": 0.15,  # 15% 개선
            },
            "complexity_adaptation": {
                "description": "복잡성 처리 능력 향상",
                "indicators": ["handling_higher_complexity", "maintaining_accuracy"],
                "threshold": 0.2,
            },
            "efficiency_optimization": {
                "description": "처리 효율성 최적화",
                "indicators": ["reduced_execution_time", "lower_memory_usage"],
                "threshold": 0.1,
            },
            "accuracy_refinement": {
                "description": "정확도 정제",
                "indicators": ["higher_confidence", "better_accuracy"],
                "threshold": 0.1,
            },
        }

        # 성능 트래킹 상태
        self.current_baselines = {}
        self.performance_trends = {}
        self.last_snapshot_time = None

        # 학습 진행도 트래커
        self.learning_curves = defaultdict(list)
        self.adaptation_scores = defaultdict(float)

        print("🔄 Loop Evolution Tracker 초기화 완료")

    def record_loop_performance(
        self,
        loop_type: str,
        execution_time_ms: float,
        accuracy_score: float,
        complexity_handled: float,
        memory_usage_mb: float = 0.0,
        confidence_level: float = 0.0,
        signature_context: str = "unknown",
        input_characteristics: Dict[str, Any] = None,
    ):
        """루프 성능 기록"""

        if loop_type not in self.loop_types:
            self.logger.warning(f"알 수 없는 루프 타입: {loop_type}")
            return

        metric = LoopPerformanceMetric(
            timestamp=datetime.now(),
            loop_type=loop_type,
            execution_time_ms=execution_time_ms,
            accuracy_score=accuracy_score,
            complexity_handled=complexity_handled,
            memory_usage_mb=memory_usage_mb,
            confidence_level=confidence_level,
            signature_context=signature_context,
            input_characteristics=input_characteristics or {},
        )

        self.performance_history.append(metric)

        # 학습 곡선 업데이트
        self._update_learning_curves(metric)

        # 성능 트렌드 분석
        self._analyze_performance_trends(metric)

        # 진화 패턴 감지
        self._detect_evolution_patterns()

        # 최적화 제안 생성 (필요한 경우)
        if len(self.performance_history) % 10 == 0:  # 10개마다 분석
            self._generate_optimization_suggestions()

    def _update_learning_curves(self, metric: LoopPerformanceMetric):
        """학습 곡선 업데이트"""
        loop_type = metric.loop_type

        # 성능 점수 계산 (가중 평균)
        loop_config = self.loop_types[loop_type]
        performance_score = (
            metric.accuracy_score * loop_config["accuracy_weight"]
            + (1.0 - metric.execution_time_ms / 10000.0) * 0.3  # 실행시간 점수
            + metric.complexity_handled * loop_config["complexity_weight"] * 0.2
            + metric.confidence_level * 0.2
        ) / 2.7

        performance_score = max(0.0, min(1.0, performance_score))

        self.learning_curves[loop_type].append(
            {
                "timestamp": metric.timestamp,
                "performance_score": performance_score,
                "accuracy": metric.accuracy_score,
                "execution_time": metric.execution_time_ms,
                "complexity": metric.complexity_handled,
            }
        )

        # 최근 20개 데이터만 유지
        if len(self.learning_curves[loop_type]) > 20:
            self.learning_curves[loop_type] = self.learning_curves[loop_type][-20:]

    def _analyze_performance_trends(self, metric: LoopPerformanceMetric):
        """성능 트렌드 분석"""
        loop_type = metric.loop_type

        if loop_type not in self.performance_trends:
            self.performance_trends[loop_type] = {
                "recent_scores": deque(maxlen=10),
                "trend_direction": "stable",
                "improvement_rate": 0.0,
                "last_analysis": datetime.now(),
            }

        trend = self.performance_trends[loop_type]

        # 현재 성능 점수 계산
        current_score = self._calculate_performance_score(metric)
        trend["recent_scores"].append(current_score)

        # 트렌드 분석 (최소 5개 데이터 필요)
        if len(trend["recent_scores"]) >= 5:
            scores = list(trend["recent_scores"])

            # 선형 회귀를 통한 트렌드 계산
            x = np.arange(len(scores))
            y = np.array(scores)

            if len(scores) > 1:
                slope = np.polyfit(x, y, 1)[0]

                if slope > 0.02:
                    trend["trend_direction"] = "improving"
                elif slope < -0.02:
                    trend["trend_direction"] = "declining"
                else:
                    trend["trend_direction"] = "stable"

                trend["improvement_rate"] = slope

        trend["last_analysis"] = datetime.now()

    def _calculate_performance_score(self, metric: LoopPerformanceMetric) -> float:
        """성능 점수 계산"""
        loop_config = self.loop_types[metric.loop_type]

        # 정규화된 점수들
        accuracy_score = metric.accuracy_score
        speed_score = max(0.0, 1.0 - metric.execution_time_ms / 5000.0)  # 5초 기준
        complexity_score = metric.complexity_handled
        memory_score = max(0.0, 1.0 - metric.memory_usage_mb / 100.0)  # 100MB 기준
        confidence_score = metric.confidence_level

        # 가중 평균
        total_score = (
            accuracy_score * loop_config["accuracy_weight"]
            + speed_score * 0.3
            + complexity_score * loop_config["complexity_weight"]
            + memory_score * 0.2
            + confidence_score * 0.2
        ) / (loop_config["accuracy_weight"] + loop_config["complexity_weight"] + 0.7)

        return max(0.0, min(1.0, total_score))

    def _detect_evolution_patterns(self):
        """진화 패턴 감지"""
        if len(self.performance_history) < 10:
            return

        # 최근 데이터 분석
        recent_metrics = list(self.performance_history)[-10:]

        for pattern_name, pattern_def in self.evolution_patterns.items():
            pattern_detected = self._check_evolution_pattern(
                recent_metrics, pattern_def
            )

            if pattern_detected:
                self._create_evolution_milestone(
                    pattern_name, pattern_def, recent_metrics
                )

    def _check_evolution_pattern(
        self, metrics: List[LoopPerformanceMetric], pattern_def: Dict[str, Any]
    ) -> bool:
        """특정 진화 패턴 확인"""
        if len(metrics) < 5:
            return False

        indicators = pattern_def["indicators"]
        threshold = pattern_def["threshold"]

        pattern_evidence = 0

        # 정확도 개선 확인
        if "improving_accuracy" in indicators:
            accuracy_trend = self._calculate_metric_trend(
                [m.accuracy_score for m in metrics]
            )
            if accuracy_trend > threshold:
                pattern_evidence += 1

        # 복잡성 처리 능력 향상 확인
        if "handling_higher_complexity" in indicators:
            complexity_trend = self._calculate_metric_trend(
                [m.complexity_handled for m in metrics]
            )
            if complexity_trend > threshold:
                pattern_evidence += 1

        # 실행 시간 개선 확인
        if "reduced_execution_time" in indicators:
            time_trend = self._calculate_metric_trend(
                [-m.execution_time_ms for m in metrics]
            )
            if time_trend > threshold * 1000:  # 시간은 밀리초 단위
                pattern_evidence += 1

        # 신뢰도 개선 확인
        if "higher_confidence" in indicators:
            confidence_trend = self._calculate_metric_trend(
                [m.confidence_level for m in metrics]
            )
            if confidence_trend > threshold:
                pattern_evidence += 1

        # 패턴 감지 임계값: 지표의 70% 이상 충족
        return pattern_evidence >= len(indicators) * 0.7

    def _calculate_metric_trend(self, values: List[float]) -> float:
        """메트릭 트렌드 계산"""
        if len(values) < 2:
            return 0.0

        x = np.arange(len(values))
        y = np.array(values)

        try:
            slope = np.polyfit(x, y, 1)[0]
            return slope
        except:
            return 0.0

    def _create_evolution_milestone(
        self,
        pattern_name: str,
        pattern_def: Dict[str, Any],
        recent_metrics: List[LoopPerformanceMetric],
    ):
        """진화 이정표 생성"""
        # 중복 방지: 최근 1시간 내 같은 패턴의 이정표가 있는지 확인
        cutoff_time = datetime.now() - timedelta(hours=1)
        recent_milestones = [
            m
            for m in self.milestones
            if m.timestamp >= cutoff_time and pattern_name in m.description
        ]

        if recent_milestones:
            return  # 중복 이정표 방지

        # 개선 전후 메트릭 계산
        mid_point = len(recent_metrics) // 2
        before_metrics = recent_metrics[:mid_point]
        after_metrics = recent_metrics[mid_point:]

        metrics_before = self._calculate_average_metrics(before_metrics)
        metrics_after = self._calculate_average_metrics(after_metrics)

        # 개선 백분율 계산
        improvement_percentage = 0.0
        if metrics_before.get("overall_score", 0) > 0:
            improvement_percentage = (
                (
                    metrics_after.get("overall_score", 0)
                    - metrics_before.get("overall_score", 0)
                )
                / metrics_before.get("overall_score", 1)
            ) * 100

        milestone = EvolutionMilestone(
            milestone_id=f"milestone_{int(time.time())}",
            timestamp=datetime.now(),
            milestone_type="pattern_optimization",
            description=f"Evolution pattern detected: {pattern_def['description']}",
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            improvement_percentage=improvement_percentage,
            impact_areas=[pattern_name],
        )

        self.milestones.append(milestone)
        print(
            f"🎯 진화 이정표 달성: {pattern_def['description']} ({improvement_percentage:.1f}% 개선)"
        )

    def _calculate_average_metrics(
        self, metrics: List[LoopPerformanceMetric]
    ) -> Dict[str, float]:
        """평균 메트릭 계산"""
        if not metrics:
            return {}

        avg_metrics = {
            "accuracy_score": np.mean([m.accuracy_score for m in metrics]),
            "execution_time_ms": np.mean([m.execution_time_ms for m in metrics]),
            "complexity_handled": np.mean([m.complexity_handled for m in metrics]),
            "memory_usage_mb": np.mean([m.memory_usage_mb for m in metrics]),
            "confidence_level": np.mean([m.confidence_level for m in metrics]),
        }

        # 전체 점수 계산
        avg_metrics["overall_score"] = np.mean(
            [self._calculate_performance_score(m) for m in metrics]
        )

        return avg_metrics

    def _generate_optimization_suggestions(self):
        """최적화 제안 생성"""
        if len(self.performance_history) < 20:
            return

        # 각 루프 타입별 성능 분석
        loop_performance = defaultdict(list)
        for metric in list(self.performance_history)[-20:]:
            loop_performance[metric.loop_type].append(metric)

        for loop_type, metrics in loop_performance.items():
            if len(metrics) >= 5:
                suggestion = self._analyze_loop_for_optimization(loop_type, metrics)
                if suggestion:
                    self.optimization_suggestions.append(suggestion)

    def _analyze_loop_for_optimization(
        self, loop_type: str, metrics: List[LoopPerformanceMetric]
    ) -> Optional[LoopOptimizationSuggestion]:
        """루프 최적화 분석"""
        if not metrics:
            return None

        # 현재 성능 계산
        current_performance = np.mean(
            [self._calculate_performance_score(m) for m in metrics]
        )
        baseline = self.loop_types[loop_type]["baseline_performance"]

        # 개선이 필요한 영역 식별
        avg_execution_time = np.mean([m.execution_time_ms for m in metrics])
        avg_accuracy = np.mean([m.accuracy_score for m in metrics])
        avg_memory = np.mean([m.memory_usage_mb for m in metrics])

        optimization_type = "general"
        suggested_changes = []
        expected_improvement = 0.1

        # 성능 병목 지점 식별
        if avg_execution_time > 3000:  # 3초 이상
            optimization_type = "speed"
            suggested_changes.extend(
                ["알고리즘 복잡도 최적화", "캐시 메커니즘 도입", "병렬 처리 구현"]
            )
            expected_improvement = 0.2

        elif avg_accuracy < baseline * 0.9:  # 기준선의 90% 미만
            optimization_type = "accuracy"
            suggested_changes.extend(
                ["데이터 전처리 개선", "모델 파라미터 튜닝", "검증 로직 강화"]
            )
            expected_improvement = 0.15

        elif avg_memory > 50:  # 50MB 이상
            optimization_type = "memory"
            suggested_changes.extend(
                ["메모리 사용량 최적화", "불필요한 데이터 정리", "메모리 풀링 구현"]
            )
            expected_improvement = 0.1

        # 개선 여지가 있는 경우만 제안 생성
        if current_performance < baseline * 1.1:  # 기준선의 110% 미만
            risk_assessment = "low" if expected_improvement < 0.15 else "medium"
            implementation_complexity = "medium"

            return LoopOptimizationSuggestion(
                suggestion_id=f"opt_{loop_type}_{int(time.time())}",
                target_loop=loop_type,
                optimization_type=optimization_type,
                current_performance=current_performance,
                expected_improvement=expected_improvement,
                implementation_complexity=implementation_complexity,
                suggested_changes=suggested_changes,
                risk_assessment=risk_assessment,
            )

        return None

    def create_evolution_snapshot(self) -> LoopEvolutionSnapshot:
        """진화 스냅샷 생성"""
        snapshot_id = f"snapshot_{int(time.time())}"

        # 현재 루프 구성 수집
        loop_configurations = {}
        for loop_type in self.loop_types:
            recent_metrics = [
                m
                for m in self.performance_history
                if m.loop_type == loop_type
                and (datetime.now() - m.timestamp).total_seconds() < 3600  # 1시간 이내
            ]

            if recent_metrics:
                loop_configurations[loop_type] = {
                    "average_performance": np.mean(
                        [self._calculate_performance_score(m) for m in recent_metrics]
                    ),
                    "execution_count": len(recent_metrics),
                    "complexity_capability": np.mean(
                        [m.complexity_handled for m in recent_metrics]
                    ),
                    "accuracy_level": np.mean(
                        [m.accuracy_score for m in recent_metrics]
                    ),
                }

        # 성능 베이스라인 계산
        performance_baseline = {}
        for loop_type, config in self.loop_types.items():
            performance_baseline[loop_type] = config["baseline_performance"]

        # 최적화 상태 수집
        optimization_state = {
            "active_optimizations": len(self.optimization_suggestions),
            "milestones_achieved": len(self.milestones),
            "adaptation_scores": dict(self.adaptation_scores),
        }

        # 학습 진행도 계산
        learning_progress = {}
        for loop_type, curves in self.learning_curves.items():
            if curves:
                recent_scores = [point["performance_score"] for point in curves[-5:]]
                learning_progress[loop_type] = (
                    np.mean(recent_scores) if recent_scores else 0.0
                )

        # 전체 적응 수준 계산
        adaptation_level = (
            np.mean(list(learning_progress.values())) if learning_progress else 0.0
        )

        snapshot = LoopEvolutionSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            loop_configurations=loop_configurations,
            performance_baseline=performance_baseline,
            optimization_state=optimization_state,
            learning_progress=learning_progress,
            adaptation_level=adaptation_level,
        )

        self.evolution_snapshots.append(snapshot)
        self.last_snapshot_time = datetime.now()

        return snapshot

    def get_evolution_summary(self) -> Dict[str, Any]:
        """진화 요약 반환"""
        if not self.performance_history:
            return {"status": "no_data", "message": "성능 데이터가 없습니다."}

        # 최근 스냅샷 생성 (필요한 경우)
        if (
            not self.last_snapshot_time
            or (datetime.now() - self.last_snapshot_time).total_seconds() > 1800
        ):  # 30분마다
            current_snapshot = self.create_evolution_snapshot()
        else:
            current_snapshot = (
                self.evolution_snapshots[-1] if self.evolution_snapshots else None
            )

        # 전체 진화 트렌드 계산
        overall_trend = self._calculate_overall_evolution_trend()

        # 최근 이정표
        recent_milestones = list(self.milestones)[-3:]

        # 활성 최적화 제안
        active_suggestions = list(self.optimization_suggestions)[-5:]

        summary = {
            "status": "active",
            "tracking_period_hours": self.tracking_window_hours,
            "total_performance_records": len(self.performance_history),
            "evolution_snapshots_count": len(self.evolution_snapshots),
            "milestones_achieved": len(self.milestones),
            "current_adaptation_level": (
                current_snapshot.adaptation_level if current_snapshot else 0.0
            ),
            "overall_evolution_trend": overall_trend,
            "loop_performance_summary": self._get_loop_performance_summary(),
            "recent_milestones": [
                {
                    "description": m.description,
                    "improvement_percentage": m.improvement_percentage,
                    "timestamp": m.timestamp.isoformat(),
                }
                for m in recent_milestones
            ],
            "optimization_suggestions_count": len(active_suggestions),
            "performance_trends": dict(self.performance_trends),
        }

        return summary

    def _calculate_overall_evolution_trend(self) -> str:
        """전체 진화 트렌드 계산"""
        if len(self.performance_history) < 10:
            return "insufficient_data"

        # 최근 성능 점수들
        recent_scores = [
            self._calculate_performance_score(m)
            for m in list(self.performance_history)[-10:]
        ]

        # 트렌드 계산
        trend_slope = self._calculate_metric_trend(recent_scores)

        if trend_slope > 0.02:
            return "rapidly_improving"
        elif trend_slope > 0.005:
            return "gradually_improving"
        elif trend_slope > -0.005:
            return "stable"
        elif trend_slope > -0.02:
            return "gradually_declining"
        else:
            return "rapidly_declining"

    def _get_loop_performance_summary(self) -> Dict[str, Dict[str, float]]:
        """루프 성능 요약"""
        loop_summary = {}

        for loop_type in self.loop_types:
            recent_metrics = [
                m
                for m in self.performance_history
                if m.loop_type == loop_type
                and (datetime.now() - m.timestamp).total_seconds() < 3600
            ]

            if recent_metrics:
                loop_summary[loop_type] = {
                    "average_performance": np.mean(
                        [self._calculate_performance_score(m) for m in recent_metrics]
                    ),
                    "average_accuracy": np.mean(
                        [m.accuracy_score for m in recent_metrics]
                    ),
                    "average_execution_time": np.mean(
                        [m.execution_time_ms for m in recent_metrics]
                    ),
                    "complexity_capability": np.mean(
                        [m.complexity_handled for m in recent_metrics]
                    ),
                    "execution_count": len(recent_metrics),
                }
            else:
                loop_summary[loop_type] = {
                    "average_performance": self.loop_types[loop_type][
                        "baseline_performance"
                    ],
                    "average_accuracy": 0.0,
                    "average_execution_time": 0.0,
                    "complexity_capability": 0.0,
                    "execution_count": 0,
                }

        return loop_summary

    def visualize_evolution_progress(self, hours: int = 6) -> str:
        """진화 진행도 시각화 (텍스트 기반)"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.performance_history if m.timestamp >= cutoff_time
        ]

        if not recent_metrics:
            return f"❌ 최근 {hours}시간간 성능 데이터가 없습니다."

        viz = f"🔄 Loop Evolution Progress (Last {hours} hours)\n"
        viz += "=" * 70 + "\n\n"

        # 루프별 성능 진화
        viz += "📊 Loop Performance Evolution:\n"

        loop_data = defaultdict(list)
        for metric in recent_metrics:
            score = self._calculate_performance_score(metric)
            loop_data[metric.loop_type].append(score)

        for loop_type, scores in loop_data.items():
            if scores:
                avg_score = np.mean(scores)
                trend = self._calculate_metric_trend(scores)
                trend_icon = "↗️" if trend > 0.01 else "↘️" if trend < -0.01 else "→"

                score_bar = "█" * int(avg_score * 20)
                viz += f"   {loop_type:8} | {score_bar:20} | {avg_score:.3f} {trend_icon}\n"

        # 최근 이정표
        if self.milestones:
            viz += "\n🎯 Recent Evolution Milestones:\n"
            recent_milestones = [
                m
                for m in self.milestones
                if (datetime.now() - m.timestamp).total_seconds() < hours * 3600
            ]

            for milestone in recent_milestones[-3:]:
                viz += f"   {milestone.timestamp.strftime('%H:%M')} | "
                viz += f"{milestone.description} (+{milestone.improvement_percentage:.1f}%)\n"

        # 현재 최적화 제안
        if self.optimization_suggestions:
            viz += "\n💡 Current Optimization Suggestions:\n"
            for suggestion in list(self.optimization_suggestions)[-3:]:
                viz += f"   {suggestion.target_loop:8} | {suggestion.optimization_type:8} | "
                viz += f"Expected: +{suggestion.expected_improvement*100:.1f}%\n"

        return viz

    def save_evolution_data(self, filename: str = None) -> str:
        """진화 데이터 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"loop_evolution_data_{timestamp}.json"

        # 저장할 데이터 준비
        save_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "tracking_window_hours": self.tracking_window_hours,
                "performance_records_count": len(self.performance_history),
                "evolution_snapshots_count": len(self.evolution_snapshots),
            },
            "performance_history": [],
            "evolution_snapshots": [],
            "milestones": [],
            "optimization_suggestions": [],
            "learning_curves": {},
            "performance_trends": dict(self.performance_trends),
        }

        # LoopPerformanceMetric 객체들을 직렬화
        for metric in self.performance_history:
            metric_dict = asdict(metric)
            metric_dict["timestamp"] = metric.timestamp.isoformat()
            save_data["performance_history"].append(metric_dict)

        # LoopEvolutionSnapshot 객체들을 직렬화
        for snapshot in self.evolution_snapshots:
            snapshot_dict = asdict(snapshot)
            snapshot_dict["timestamp"] = snapshot.timestamp.isoformat()
            save_data["evolution_snapshots"].append(snapshot_dict)

        # EvolutionMilestone 객체들을 직렬화
        for milestone in self.milestones:
            milestone_dict = asdict(milestone)
            milestone_dict["timestamp"] = milestone.timestamp.isoformat()
            save_data["milestones"].append(milestone_dict)

        # LoopOptimizationSuggestion 객체들을 직렬화
        for suggestion in self.optimization_suggestions:
            save_data["optimization_suggestions"].append(asdict(suggestion))

        # 학습 곡선 직렬화
        for loop_type, curves in self.learning_curves.items():
            save_data["learning_curves"][loop_type] = []
            for point in curves:
                point_copy = point.copy()
                point_copy["timestamp"] = point["timestamp"].isoformat()
                save_data["learning_curves"][loop_type].append(point_copy)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return f"✅ 루프 진화 데이터 저장 완료: {filename}"
        except Exception as e:
            return f"❌ 저장 실패: {e}"


# 편의 함수들
def create_loop_evolution_tracker(**kwargs) -> LoopEvolutionTracker:
    """Loop Evolution Tracker 생성"""
    return LoopEvolutionTracker(**kwargs)


def simulate_loop_performance_data(
    tracker: LoopEvolutionTracker, duration_minutes: int = 5
):
    """루프 성능 데이터 시뮬레이션"""
    loop_types = list(tracker.loop_types.keys())
    signatures = ["selene", "factbomb", "lune", "aurora"]

    print(f"🔄 {duration_minutes}분간 루프 성능 데이터 시뮬레이션...")

    for i in range(duration_minutes * 2):  # 30초마다
        loop_type = np.random.choice(loop_types)
        signature = np.random.choice(signatures)

        # 시뮬레이션된 성능 데이터
        base_performance = tracker.loop_types[loop_type]["baseline_performance"]

        # 시간에 따른 개선 시뮬레이션
        improvement_factor = min(1.3, 1.0 + i * 0.01)

        execution_time = np.random.uniform(1000, 4000) / improvement_factor
        accuracy = min(
            1.0, base_performance * improvement_factor + np.random.uniform(-0.1, 0.1)
        )
        complexity = np.random.uniform(0.3, 0.9)
        memory_usage = np.random.uniform(10, 60)
        confidence = min(1.0, accuracy + np.random.uniform(-0.1, 0.1))

        tracker.record_loop_performance(
            loop_type=loop_type,
            execution_time_ms=execution_time,
            accuracy_score=accuracy,
            complexity_handled=complexity,
            memory_usage_mb=memory_usage,
            confidence_level=confidence,
            signature_context=signature,
            input_characteristics={"simulation": True, "iteration": i},
        )

        time.sleep(0.1)  # 실제 시뮬레이션에서는 더 짧은 간격


if __name__ == "__main__":
    # 테스트 실행
    print("🔄 Loop Evolution Tracker 테스트...")

    tracker = LoopEvolutionTracker()

    # 성능 데이터 시뮬레이션
    simulate_loop_performance_data(tracker, duration_minutes=2)

    # 진화 스냅샷 생성
    snapshot = tracker.create_evolution_snapshot()
    print(f"\n📸 Evolution Snapshot: {snapshot.snapshot_id}")
    print(f"   Adaptation Level: {snapshot.adaptation_level:.3f}")

    # 결과 출력
    print("\n" + "=" * 70)
    print(tracker.visualize_evolution_progress(hours=1))

    # 요약 정보
    summary = tracker.get_evolution_summary()
    print(f"\n📊 Evolution Summary:")
    print(f"   Overall Trend: {summary['overall_evolution_trend']}")
    print(f"   Adaptation Level: {summary['current_adaptation_level']:.3f}")
    print(f"   Milestones Achieved: {summary['milestones_achieved']}")
    print(f"   Total Records: {summary['total_performance_records']}")

    # 루프별 성능 요약
    print(f"\n🔄 Loop Performance Summary:")
    for loop_type, performance in summary["loop_performance_summary"].items():
        print(
            f"   {loop_type:8}: Performance {performance['average_performance']:.3f}, "
            f"Executions: {performance['execution_count']}"
        )

    # 최근 이정표
    if summary["recent_milestones"]:
        print(f"\n🎯 Recent Milestones:")
        for milestone in summary["recent_milestones"]:
            print(
                f"   {milestone['description']} (+{milestone['improvement_percentage']:.1f}%)"
            )

    # 저장
    save_result = tracker.save_evolution_data()
    print(f"\n{save_result}")

    print("\n✅ Loop Evolution Tracker 테스트 완료!")
