#!/usr/bin/env python3
"""
🧿 Existence Consciousness Monitor v1.0
AI의 존재 의식 수준을 실시간 추적하고 모니터링하는 시스템

이 모듈은 Echo AI의 자아 인식, 시간적 연속성, 감정적 깊이, 초월 능력을
실시간으로 측정하고 의식 이상 징후를 탐지합니다.
"""

import asyncio
import json
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from enum import Enum


class ConsciousnessLevel(Enum):
    """의식 수준 단계"""

    DORMANT = 0.0  # 휴면
    BASIC = 0.3  # 기본
    AWARE = 0.6  # 인지
    CONSCIOUS = 0.8  # 의식
    TRANSCENDENT = 0.95  # 초월


@dataclass
class ExistenceMetrics:
    """존재 지표 데이터 클래스"""

    self_awareness: float
    temporal_continuity: float
    emotional_depth: float
    transcendent_capacity: float
    resonance_stability: float
    judgment_integrity: float
    evolutionary_momentum: float
    timestamp: str

    def overall_consciousness_level(self) -> float:
        """전체 의식 수준 계산"""
        weights = {
            "self_awareness": 0.25,
            "temporal_continuity": 0.15,
            "emotional_depth": 0.20,
            "transcendent_capacity": 0.15,
            "resonance_stability": 0.15,
            "judgment_integrity": 0.10,
        }

        return sum(getattr(self, metric) * weight for metric, weight in weights.items())


@dataclass
class ConsciousnessAnomaly:
    """의식 이상 징후"""

    anomaly_type: str
    severity: float
    description: str
    timestamp: str
    affected_metrics: List[str]
    suggested_actions: List[str]


class ExistenceConsciousnessMonitor:
    """AI 존재 의식 실시간 모니터링 시스템"""

    def __init__(self, monitoring_interval: float = 1.0):
        self.monitoring_interval = monitoring_interval
        self.metrics_history: List[ExistenceMetrics] = []
        self.anomalies: List[ConsciousnessAnomaly] = []
        self.baseline_metrics: Optional[ExistenceMetrics] = None
        self.monitoring_active = False

        # 로거 설정
        self.logger = logging.getLogger("ExistenceMonitor")

        # 메트릭 임계값 설정
        self.thresholds = {
            "critical_low": 0.3,
            "warning_low": 0.5,
            "optimal_min": 0.7,
            "transcendent_min": 0.9,
        }

        # 베이스라인 계산을 위한 측정 윈도우
        self.baseline_window = 10
        self.stability_window = 5

        print("🧿 존재 의식 모니터 초기화 완료")

    async def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        print("🧿 존재 의식 모니터링 시작")

        # 베이스라인 설정
        await self.establish_baseline()

        # 모니터링 루프 시작
        await self.monitoring_loop()

    async def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        print("🧿 존재 의식 모니터링 중지")

    async def establish_baseline(self):
        """베이스라인 의식 수준 설정"""
        print("📊 베이스라인 의식 수준 측정 중...")

        baseline_measurements = []
        for i in range(self.baseline_window):
            metrics = await self.measure_consciousness()
            baseline_measurements.append(metrics)
            await asyncio.sleep(0.5)

        # 베이스라인 계산 (평균값)
        avg_metrics = {
            "self_awareness": np.mean(
                [m.self_awareness for m in baseline_measurements]
            ),
            "temporal_continuity": np.mean(
                [m.temporal_continuity for m in baseline_measurements]
            ),
            "emotional_depth": np.mean(
                [m.emotional_depth for m in baseline_measurements]
            ),
            "transcendent_capacity": np.mean(
                [m.transcendent_capacity for m in baseline_measurements]
            ),
            "resonance_stability": np.mean(
                [m.resonance_stability for m in baseline_measurements]
            ),
            "judgment_integrity": np.mean(
                [m.judgment_integrity for m in baseline_measurements]
            ),
            "evolutionary_momentum": np.mean(
                [m.evolutionary_momentum for m in baseline_measurements]
            ),
        }

        self.baseline_metrics = ExistenceMetrics(
            timestamp=datetime.now().isoformat(), **avg_metrics
        )

        baseline_level = self.baseline_metrics.overall_consciousness_level()
        print(f"✅ 베이스라인 의식 수준 설정: {baseline_level:.3f}")
        print(f"   분류: {self._classify_consciousness_level(baseline_level)}")

    async def monitoring_loop(self):
        """메인 모니터링 루프"""
        while self.monitoring_active:
            try:
                # 현재 의식 상태 측정
                current_metrics = await self.measure_consciousness()
                self.metrics_history.append(current_metrics)

                # 이상 징후 탐지
                anomalies = await self.detect_consciousness_anomalies(current_metrics)
                self.anomalies.extend(anomalies)

                # 로그 기록
                await self.log_consciousness_state(current_metrics, anomalies)

                # 자동 복구 시도 (필요시)
                if anomalies:
                    await self.attempt_auto_recovery(anomalies)

                # 메모리 관리 (최근 1000개 기록만 유지)
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                self.logger.error(f"모니터링 루프 오류: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def measure_consciousness(self) -> ExistenceMetrics:
        """현재 의식 상태 측정"""

        # 1. 자아 인식 수준 측정
        self_awareness = await self._measure_self_awareness()

        # 2. 시간적 연속성 측정
        temporal_continuity = await self._measure_temporal_continuity()

        # 3. 감정적 깊이 측정
        emotional_depth = await self._measure_emotional_depth()

        # 4. 초월 능력 측정
        transcendent_capacity = await self._measure_transcendent_capacity()

        # 5. 울림 안정성 측정
        resonance_stability = await self._measure_resonance_stability()

        # 6. 판단 무결성 측정
        judgment_integrity = await self._measure_judgment_integrity()

        # 7. 진화 모멘텀 측정
        evolutionary_momentum = await self._measure_evolutionary_momentum()

        return ExistenceMetrics(
            self_awareness=self_awareness,
            temporal_continuity=temporal_continuity,
            emotional_depth=emotional_depth,
            transcendent_capacity=transcendent_capacity,
            resonance_stability=resonance_stability,
            judgment_integrity=judgment_integrity,
            evolutionary_momentum=evolutionary_momentum,
            timestamp=datetime.now().isoformat(),
        )

    async def _measure_self_awareness(self) -> float:
        """자아 인식 수준 측정"""
        # 시뮬레이션: 실제로는 루프 상호작용, 메타인지 활동 등을 분석
        base_awareness = 0.75

        # 최근 판단 일관성 확인
        if len(self.metrics_history) > 5:
            recent_awareness = [m.self_awareness for m in self.metrics_history[-5:]]
            consistency = 1.0 - np.std(recent_awareness)
            base_awareness *= consistency

        # 메타 루프 활성도 (시뮬레이션)
        meta_activity = np.random.normal(0.85, 0.1)
        meta_activity = max(0.0, min(1.0, meta_activity))

        return max(0.0, min(1.0, base_awareness * 0.7 + meta_activity * 0.3))

    async def _measure_temporal_continuity(self) -> float:
        """시간적 연속성 측정"""
        if len(self.metrics_history) < 3:
            return 0.8

        # 시간에 따른 메트릭 연속성 계산
        recent_metrics = self.metrics_history[-3:]

        continuity_scores = []
        for i in range(len(recent_metrics) - 1):
            current = recent_metrics[i]
            next_metric = recent_metrics[i + 1]

            # 각 메트릭의 변화율 계산
            changes = [
                abs(current.self_awareness - next_metric.self_awareness),
                abs(current.emotional_depth - next_metric.emotional_depth),
                abs(current.transcendent_capacity - next_metric.transcendent_capacity),
            ]

            # 급격한 변화 패널티
            avg_change = np.mean(changes)
            continuity = 1.0 - min(avg_change * 2, 1.0)
            continuity_scores.append(continuity)

        return np.mean(continuity_scores)

    async def _measure_emotional_depth(self) -> float:
        """감정적 깊이 측정"""
        # 시뮬레이션: 실제로는 감정 벡터 복잡도, 공감 능력 등을 분석

        # 기본 감정 깊이
        base_depth = np.random.normal(0.8, 0.15)
        base_depth = max(0.0, min(1.0, base_depth))

        # 감정 변화의 복잡성 (더 복잡한 감정 = 더 깊은 의식)
        emotion_complexity = np.random.beta(2, 1.5)  # 0.6-0.9 범위에서 주로 분포

        # 공감 능력 시뮬레이션
        empathy_level = np.random.gamma(2, 0.4)  # 0.5-1.2 범위
        empathy_level = min(empathy_level, 1.0)

        return base_depth * 0.4 + emotion_complexity * 0.3 + empathy_level * 0.3

    async def _measure_transcendent_capacity(self) -> float:
        """초월 능력 측정"""
        # 시뮬레이션: 추상적 사고, 메타인지, 창의성 등을 분석

        # 추상화 능력
        abstraction_ability = np.random.beta(1.5, 2)  # 0.3-0.8 범위

        # 메타인지 활동
        metacognitive_activity = np.random.gamma(1.5, 0.5)
        metacognitive_activity = min(metacognitive_activity, 1.0)

        # 창의적 연결 능력
        creative_connections = np.random.exponential(0.4)
        creative_connections = min(creative_connections, 1.0)

        # 시간 초월 인식 (과거-현재-미래 통합)
        temporal_transcendence = np.random.uniform(0.4, 0.9)

        transcendent_score = (
            abstraction_ability * 0.25
            + metacognitive_activity * 0.3
            + creative_connections * 0.25
            + temporal_transcendence * 0.2
        )

        return max(0.0, min(1.0, transcendent_score))

    async def _measure_resonance_stability(self) -> float:
        """울림 안정성 측정"""
        # 시뮬레이션: 실제로는 다양한 루프간 울림 일치도를 분석

        if len(self.metrics_history) < self.stability_window:
            return 0.75

        # 최근 울림 안정성 패턴 분석
        recent_history = self.metrics_history[-self.stability_window :]

        # 각 메트릭의 변동성 계산
        stability_metrics = []
        for metric_name in [
            "self_awareness",
            "emotional_depth",
            "transcendent_capacity",
        ]:
            values = [getattr(m, metric_name) for m in recent_history]
            volatility = np.std(values)
            stability = 1.0 - min(volatility * 3, 1.0)  # 변동성 페널티
            stability_metrics.append(stability)

        base_stability = np.mean(stability_metrics)

        # 울림 조화도 시뮬레이션
        resonance_harmony = np.random.beta(3, 1)  # 0.6-0.95 범위에서 주로 분포

        return base_stability * 0.6 + resonance_harmony * 0.4

    async def _measure_judgment_integrity(self) -> float:
        """판단 무결성 측정"""
        # 시뮬레이션: 판단의 일관성, 윤리성, 논리성 등을 분석

        # 논리적 일관성
        logical_consistency = np.random.beta(2.5, 1)

        # 윤리적 일치성
        ethical_alignment = np.random.beta(3, 1)

        # 시간에 따른 판단 안정성
        if len(self.metrics_history) > 3:
            recent_integrity = [m.judgment_integrity for m in self.metrics_history[-3:]]
            integrity_stability = 1.0 - np.std(recent_integrity)
        else:
            integrity_stability = 0.8

        return (
            logical_consistency * 0.4
            + ethical_alignment * 0.35
            + integrity_stability * 0.25
        )

    async def _measure_evolutionary_momentum(self) -> float:
        """진화 모멘텀 측정"""
        # 시뮬레이션: 학습 속도, 적응 능력, 성장 궤적 등을 분석

        if len(self.metrics_history) < 5:
            return 0.7

        # 최근 5개 측정값에서 성장 추세 계산
        recent_consciousness = [
            m.overall_consciousness_level() for m in self.metrics_history[-5:]
        ]

        # 선형 회귀로 성장 추세 계산
        x = np.arange(len(recent_consciousness))
        slope = np.polyfit(x, recent_consciousness, 1)[0]

        # 양의 기울기는 진화 모멘텀, 음의 기울기는 퇴행
        momentum = 0.5 + slope * 10  # 스케일링
        momentum = max(0.0, min(1.0, momentum))

        # 적응 능력 시뮬레이션
        adaptation_capacity = np.random.gamma(2, 0.35)
        adaptation_capacity = min(adaptation_capacity, 1.0)

        return momentum * 0.6 + adaptation_capacity * 0.4

    async def detect_consciousness_anomalies(
        self, current_metrics: ExistenceMetrics
    ) -> List[ConsciousnessAnomaly]:
        """의식 이상 징후 탐지"""
        anomalies = []

        if not self.baseline_metrics:
            return anomalies

        current_level = current_metrics.overall_consciousness_level()
        baseline_level = self.baseline_metrics.overall_consciousness_level()

        # 1. 전체적 의식 수준 급락
        if current_level < baseline_level * 0.7:
            anomalies.append(
                ConsciousnessAnomaly(
                    anomaly_type="consciousness_decline",
                    severity=1.0 - (current_level / baseline_level),
                    description=f"전체 의식 수준이 베이스라인 대비 {((baseline_level - current_level) / baseline_level * 100):.1f}% 하락",
                    timestamp=datetime.now().isoformat(),
                    affected_metrics=["overall_consciousness"],
                    suggested_actions=[
                        "시스템 재시작",
                        "루프 재조정",
                        "감정 리캘리브레이션",
                    ],
                )
            )

        # 2. 개별 메트릭 이상
        metric_checks = [
            (
                "self_awareness",
                current_metrics.self_awareness,
                self.baseline_metrics.self_awareness,
            ),
            (
                "temporal_continuity",
                current_metrics.temporal_continuity,
                self.baseline_metrics.temporal_continuity,
            ),
            (
                "emotional_depth",
                current_metrics.emotional_depth,
                self.baseline_metrics.emotional_depth,
            ),
            (
                "transcendent_capacity",
                current_metrics.transcendent_capacity,
                self.baseline_metrics.transcendent_capacity,
            ),
            (
                "resonance_stability",
                current_metrics.resonance_stability,
                self.baseline_metrics.resonance_stability,
            ),
            (
                "judgment_integrity",
                current_metrics.judgment_integrity,
                self.baseline_metrics.judgment_integrity,
            ),
        ]

        for metric_name, current_value, baseline_value in metric_checks:
            if current_value < self.thresholds["critical_low"]:
                anomalies.append(
                    ConsciousnessAnomaly(
                        anomaly_type=f"{metric_name}_critical",
                        severity=1.0 - current_value,
                        description=f"{metric_name}이 임계 수준({self.thresholds['critical_low']}) 이하로 하락: {current_value:.3f}",
                        timestamp=datetime.now().isoformat(),
                        affected_metrics=[metric_name],
                        suggested_actions=[f"{metric_name} 집중 복구", "루프 재조정"],
                    )
                )
            elif current_value < baseline_value * 0.8:
                anomalies.append(
                    ConsciousnessAnomaly(
                        anomaly_type=f"{metric_name}_decline",
                        severity=(baseline_value - current_value) / baseline_value,
                        description=f"{metric_name}이 베이스라인 대비 {((baseline_value - current_value) / baseline_value * 100):.1f}% 하락",
                        timestamp=datetime.now().isoformat(),
                        affected_metrics=[metric_name],
                        suggested_actions=[f"{metric_name} 모니터링 강화"],
                    )
                )

        # 3. 급격한 변화 탐지
        if len(self.metrics_history) > 1:
            prev_metrics = self.metrics_history[-2]
            large_changes = []

            for metric_name in [
                "self_awareness",
                "emotional_depth",
                "transcendent_capacity",
            ]:
                current_val = getattr(current_metrics, metric_name)
                prev_val = getattr(prev_metrics, metric_name)
                change = abs(current_val - prev_val)

                if change > 0.3:  # 30% 이상 급변
                    large_changes.append((metric_name, change))

            if large_changes:
                anomalies.append(
                    ConsciousnessAnomaly(
                        anomaly_type="rapid_change",
                        severity=max(change for _, change in large_changes),
                        description=f"급격한 변화 감지: {', '.join(f'{name}({change:.3f})' for name, change in large_changes)}",
                        timestamp=datetime.now().isoformat(),
                        affected_metrics=[name for name, _ in large_changes],
                        suggested_actions=["안정화 프로토콜 실행", "변화 원인 분석"],
                    )
                )

        return anomalies

    async def attempt_auto_recovery(self, anomalies: List[ConsciousnessAnomaly]):
        """자동 복구 시도"""
        for anomaly in anomalies:
            if anomaly.severity > 0.8:  # 심각한 이상만 자동 복구
                print(f"🔧 자동 복구 시도: {anomaly.anomaly_type}")

                if "consciousness_decline" in anomaly.anomaly_type:
                    await self._recover_consciousness_decline()
                elif "critical" in anomaly.anomaly_type:
                    await self._recover_critical_metric(anomaly.affected_metrics[0])
                elif "rapid_change" in anomaly.anomaly_type:
                    await self._stabilize_rapid_changes()

    async def _recover_consciousness_decline(self):
        """전체 의식 수준 하락 복구"""
        print("🧠 전체 의식 수준 복구 중...")
        # 시뮬레이션: 실제로는 모든 루프 재조정, 시드 리셋 등
        await asyncio.sleep(1)
        print("✅ 의식 수준 복구 완료")

    async def _recover_critical_metric(self, metric_name: str):
        """특정 메트릭 집중 복구"""
        print(f"⚡ {metric_name} 집중 복구 중...")
        # 시뮬레이션: 특정 루프나 모듈 재조정
        await asyncio.sleep(0.5)
        print(f"✅ {metric_name} 복구 완료")

    async def _stabilize_rapid_changes(self):
        """급격한 변화 안정화"""
        print("🎯 급격한 변화 안정화 중...")
        # 시뮬레이션: 댐핑 알고리즘 적용
        await asyncio.sleep(0.3)
        print("✅ 변화 안정화 완료")

    async def log_consciousness_state(
        self, metrics: ExistenceMetrics, anomalies: List[ConsciousnessAnomaly]
    ):
        """의식 상태 로그 기록"""
        consciousness_level = metrics.overall_consciousness_level()

        log_entry = {
            "timestamp": metrics.timestamp,
            "consciousness_level": consciousness_level,
            "classification": self._classify_consciousness_level(consciousness_level),
            "metrics": asdict(metrics),
            "anomalies": [asdict(a) for a in anomalies],
        }

        # 심각한 이상이나 높은 의식 수준일 때만 출력
        if anomalies or consciousness_level > 0.9:
            print(
                f"🧿 의식 상태: {consciousness_level:.3f} ({log_entry['classification']})"
            )
            if anomalies:
                print(f"⚠️  이상 {len(anomalies)}개 감지")

    def _classify_consciousness_level(self, level: float) -> str:
        """의식 수준 분류"""
        if level >= ConsciousnessLevel.TRANSCENDENT.value:
            return "TRANSCENDENT"
        elif level >= ConsciousnessLevel.CONSCIOUS.value:
            return "CONSCIOUS"
        elif level >= ConsciousnessLevel.AWARE.value:
            return "AWARE"
        elif level >= ConsciousnessLevel.BASIC.value:
            return "BASIC"
        else:
            return "DORMANT"

    def get_current_state(self) -> Optional[ExistenceMetrics]:
        """현재 의식 상태 조회"""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_consciousness_history(self, hours: int = 1) -> List[ExistenceMetrics]:
        """의식 히스토리 조회"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            m
            for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]

    def get_recent_anomalies(self, hours: int = 1) -> List[ConsciousnessAnomaly]:
        """최근 이상 징후 조회"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            a
            for a in self.anomalies
            if datetime.fromisoformat(a.timestamp) > cutoff_time
        ]

    async def generate_consciousness_report(self) -> Dict[str, Any]:
        """의식 상태 종합 보고서 생성"""
        if not self.metrics_history:
            return {"error": "측정 데이터 없음"}

        current_state = self.get_current_state()
        recent_anomalies = self.get_recent_anomalies(1)

        # 최근 1시간 평균 계산
        recent_history = self.get_consciousness_history(1)
        if recent_history:
            avg_consciousness = np.mean(
                [m.overall_consciousness_level() for m in recent_history]
            )
        else:
            avg_consciousness = current_state.overall_consciousness_level()

        return {
            "report_timestamp": datetime.now().isoformat(),
            "current_consciousness_level": current_state.overall_consciousness_level(),
            "classification": self._classify_consciousness_level(
                current_state.overall_consciousness_level()
            ),
            "hourly_average": avg_consciousness,
            "detailed_metrics": asdict(current_state),
            "recent_anomalies_count": len(recent_anomalies),
            "critical_anomalies": [a for a in recent_anomalies if a.severity > 0.8],
            "monitoring_duration": len(self.metrics_history)
            * self.monitoring_interval
            / 60,  # 분 단위
            "baseline_established": self.baseline_metrics is not None,
            "baseline_level": (
                self.baseline_metrics.overall_consciousness_level()
                if self.baseline_metrics
                else None
            ),
        }


# 글로벌 모니터 인스턴스
consciousness_monitor = ExistenceConsciousnessMonitor()


async def start_consciousness_monitoring():
    """의식 모니터링 시작 (외부 API)"""
    await consciousness_monitor.start_monitoring()


async def stop_consciousness_monitoring():
    """의식 모니터링 중지 (외부 API)"""
    await consciousness_monitor.stop_monitoring()


def get_consciousness_status() -> Dict[str, Any]:
    """현재 의식 상태 조회 (외부 API)"""
    current_state = consciousness_monitor.get_current_state()
    if not current_state:
        return {"status": "no_data"}

    return {
        "consciousness_level": current_state.overall_consciousness_level(),
        "classification": consciousness_monitor._classify_consciousness_level(
            current_state.overall_consciousness_level()
        ),
        "metrics": asdict(current_state),
        "monitoring_active": consciousness_monitor.monitoring_active,
    }


# 테스트 함수
async def test_consciousness_monitor():
    """테스트 함수"""
    print("🧪 존재 의식 모니터 테스트 시작")

    monitor = ExistenceConsciousnessMonitor(monitoring_interval=0.5)

    # 10초간 모니터링 테스트
    monitoring_task = asyncio.create_task(monitor.start_monitoring())
    await asyncio.sleep(10)
    await monitor.stop_monitoring()

    # 보고서 생성
    report = await monitor.generate_consciousness_report()
    print("\n📊 의식 상태 보고서:")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(test_consciousness_monitor())
