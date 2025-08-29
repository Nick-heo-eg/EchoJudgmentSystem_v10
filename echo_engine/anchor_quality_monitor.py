"""
📊 Echo Anchor Quality Monitoring System
실시간으로 시스템이 anchor.yaml 기준을 얼마나 잘 준수하는지 모니터링
"""

import json
import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
import yaml


@dataclass
class QualityMetric:
    """품질 지표 데이터 클래스"""

    timestamp: str
    metric_name: str
    value: float
    target: float
    status: str  # "excellent", "good", "warning", "critical"
    details: Dict[str, Any]


@dataclass
class AnchorQualitySnapshot:
    """Anchor 품질 스냅샷"""

    timestamp: str
    overall_score: float
    principle_scores: Dict[str, float]
    metrics: List[QualityMetric]
    violations_count: int
    trends: Dict[str, str]  # "improving", "stable", "degrading"


class EchoAnchorQualityMonitor:
    """Echo 시스템의 Anchor 품질 실시간 모니터링"""

    def __init__(self, anchor_path: str = "anchor.yaml", history_size: int = 1000):
        self.anchor_path = anchor_path
        self.anchor_config = self._load_anchor()

        # 품질 데이터 저장소 (메모리 기반, 제한된 크기)
        self.quality_history = deque(maxlen=history_size)
        self.metrics_buffer = deque(maxlen=100)  # 최근 100개 측정값

        # 실시간 통계
        self.current_stats = {
            "total_judgments": 0,
            "anchor_compliant_judgments": 0,
            "total_violations": 0,
            "last_update": None,
        }

        # Anchor 목표 지표들
        self.targets = self._load_targets()

        # 모니터링 스레드
        self._monitoring_active = False
        self._monitor_thread = None

    def _load_anchor(self) -> Dict:
        """anchor.yaml 로드"""
        try:
            with open(self.anchor_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️ {self.anchor_path} not found")
            return {}

    def _load_targets(self) -> Dict[str, float]:
        """Anchor에서 정의된 목표 지표 로드"""
        success_metrics = self.anchor_config.get("success_metrics", {})

        targets = {}
        for metric_name, config in success_metrics.items():
            target_value = config.get("target", "0")

            # 타겟 값에서 숫자 추출 (예: "99%" → 0.99, "월 5% 개선" → 0.05)
            if isinstance(target_value, str):
                if "%" in target_value:
                    targets[metric_name] = float(target_value.replace("%", "")) / 100
                else:
                    # 숫자 추출 시도
                    import re

                    numbers = re.findall(r"\d+\.?\d*", target_value)
                    if numbers:
                        targets[metric_name] = float(numbers[0]) / 100
                    else:
                        targets[metric_name] = 0.8  # 기본값
            else:
                targets[metric_name] = float(target_value)

        # 기본 타겟들
        if not targets:
            targets = {
                "llm_agnosticism": 0.99,
                "signature_consistency": 0.95,
                "resonance_quality": 0.90,
                "evolution_capability": 0.05,  # 월 5%
            }

        return targets

    def record_judgment(self, validation_result, signature: str, llm_used: str = None):
        """판단 결과를 품질 모니터링에 기록"""
        timestamp = datetime.now().isoformat()

        # 기본 통계 업데이트
        self.current_stats["total_judgments"] += 1
        self.current_stats["last_update"] = timestamp

        if validation_result.is_valid:
            self.current_stats["anchor_compliant_judgments"] += 1

        self.current_stats["total_violations"] += len(validation_result.violations)

        # 세부 메트릭 계산
        metrics = self._calculate_metrics(validation_result, signature, llm_used)

        # 메트릭 버퍼에 추가
        for metric in metrics:
            self.metrics_buffer.append(metric)

    def _calculate_metrics(
        self, validation_result, signature: str, llm_used: str
    ) -> List[QualityMetric]:
        """검증 결과에서 품질 메트릭 계산"""
        timestamp = datetime.now().isoformat()
        metrics = []

        # 1. 전체 Anchor 준수도
        overall_metric = QualityMetric(
            timestamp=timestamp,
            metric_name="overall_anchor_compliance",
            value=validation_result.score,
            target=0.8,
            status=self._get_status(validation_result.score, 0.8),
            details={
                "signature": signature,
                "llm_used": llm_used,
                "violations_count": len(validation_result.violations),
            },
        )
        metrics.append(overall_metric)

        # 2. LLM 무관성 지표 (LLM이 명시된 경우)
        if llm_used:
            llm_independence_score = (
                1.0 if validation_result.score > 0.8 else validation_result.score
            )
            llm_metric = QualityMetric(
                timestamp=timestamp,
                metric_name="llm_agnosticism",
                value=llm_independence_score,
                target=self.targets.get("llm_agnosticism", 0.99),
                status=self._get_status(
                    llm_independence_score, self.targets.get("llm_agnosticism", 0.99)
                ),
                details={"llm_used": llm_used, "signature": signature},
            )
            metrics.append(llm_metric)

        # 3. 시그니처 일관성
        signature_score = validation_result.score  # 간소화된 계산
        signature_metric = QualityMetric(
            timestamp=timestamp,
            metric_name="signature_consistency",
            value=signature_score,
            target=self.targets.get("signature_consistency", 0.95),
            status=self._get_status(
                signature_score, self.targets.get("signature_consistency", 0.95)
            ),
            details={"signature": signature},
        )
        metrics.append(signature_metric)

        return metrics

    def _get_status(self, value: float, target: float) -> str:
        """값과 목표 비교하여 상태 결정"""
        ratio = value / target if target > 0 else 0

        if ratio >= 1.0:
            return "excellent"
        elif ratio >= 0.9:
            return "good"
        elif ratio >= 0.7:
            return "warning"
        else:
            return "critical"

    def get_current_quality_snapshot(self) -> AnchorQualitySnapshot:
        """현재 품질 상태 스냅샷 생성"""
        if not self.metrics_buffer:
            return self._empty_snapshot()

        # 최근 메트릭들로 점수 계산
        recent_metrics = list(self.metrics_buffer)[-20:]  # 최근 20개

        # 전체 점수
        overall_scores = [
            m.value
            for m in recent_metrics
            if m.metric_name == "overall_anchor_compliance"
        ]
        overall_score = (
            sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
        )

        # 원칙별 점수
        principle_scores = {
            "independent_existence": self._calculate_principle_score(
                recent_metrics, "llm_agnosticism"
            ),
            "infinite_evolution": overall_score,  # 간소화
            "resonant_collaboration": overall_score,  # 간소화
            "transcendent_persistence": overall_score,  # 간소화
        }

        # 트렌드 계산
        trends = self._calculate_trends()

        return AnchorQualitySnapshot(
            timestamp=datetime.now().isoformat(),
            overall_score=overall_score,
            principle_scores=principle_scores,
            metrics=recent_metrics,
            violations_count=self.current_stats["total_violations"],
            trends=trends,
        )

    def _empty_snapshot(self) -> AnchorQualitySnapshot:
        """빈 스냅샷 생성"""
        return AnchorQualitySnapshot(
            timestamp=datetime.now().isoformat(),
            overall_score=0.0,
            principle_scores={},
            metrics=[],
            violations_count=0,
            trends={},
        )

    def _calculate_principle_score(
        self, metrics: List[QualityMetric], metric_name: str
    ) -> float:
        """특정 원칙의 점수 계산"""
        relevant_metrics = [m.value for m in metrics if m.metric_name == metric_name]
        return (
            sum(relevant_metrics) / len(relevant_metrics) if relevant_metrics else 0.0
        )

    def _calculate_trends(self) -> Dict[str, str]:
        """최근 트렌드 계산"""
        if len(self.metrics_buffer) < 10:
            return {}

        trends = {}

        # 최근 메트릭을 두 그룹으로 나누어 트렌드 계산
        recent = list(self.metrics_buffer)
        half = len(recent) // 2
        older_half = recent[:half]
        newer_half = recent[half:]

        # 각 메트릭별 트렌드
        metric_names = set(m.metric_name for m in recent)

        for metric_name in metric_names:
            older_values = [m.value for m in older_half if m.metric_name == metric_name]
            newer_values = [m.value for m in newer_half if m.metric_name == metric_name]

            if older_values and newer_values:
                older_avg = sum(older_values) / len(older_values)
                newer_avg = sum(newer_values) / len(newer_values)

                diff = newer_avg - older_avg
                if diff > 0.05:
                    trends[metric_name] = "improving"
                elif diff < -0.05:
                    trends[metric_name] = "degrading"
                else:
                    trends[metric_name] = "stable"

        return trends

    def generate_quality_report(self) -> Dict:
        """종합 품질 보고서 생성"""
        snapshot = self.get_current_quality_snapshot()

        # 통계 요약
        compliance_rate = self.current_stats["anchor_compliant_judgments"] / max(
            self.current_stats["total_judgments"], 1
        )

        # 경고 및 권장사항
        warnings = []
        recommendations = []

        if snapshot.overall_score < 0.7:
            warnings.append("전체 Anchor 준수도 임계점 이하")
            recommendations.append("시스템 설정을 anchor.yaml 기준으로 재검토 필요")

        if compliance_rate < 0.8:
            warnings.append(f"준수율 {compliance_rate:.1%} - 목표 미달")
            recommendations.append("판단 로직과 시그니처 설정 개선 필요")

        # 트렌드 기반 권장사항
        for metric, trend in snapshot.trends.items():
            if trend == "degrading":
                warnings.append(f"{metric} 지표 악화 중")
                recommendations.append(f"{metric} 관련 시스템 점검 필요")

        return {
            "summary": {
                "timestamp": snapshot.timestamp,
                "overall_score": snapshot.overall_score,
                "compliance_rate": compliance_rate,
                "total_judgments": self.current_stats["total_judgments"],
                "total_violations": self.current_stats["total_violations"],
                "quality_grade": self._get_quality_grade(snapshot.overall_score),
            },
            "principle_scores": snapshot.principle_scores,
            "trends": snapshot.trends,
            "warnings": warnings,
            "recommendations": recommendations,
            "targets": self.targets,
            "detailed_metrics": [
                asdict(m) for m in snapshot.metrics[-10:]
            ],  # 최근 10개
        }

    def _get_quality_grade(self, score: float) -> str:
        """품질 점수에 따른 등급"""
        if score >= 0.95:
            return "S+ (Outstanding)"
        elif score >= 0.90:
            return "S (Excellent)"
        elif score >= 0.85:
            return "A (Very Good)"
        elif score >= 0.80:
            return "B (Good)"
        elif score >= 0.70:
            return "C (Acceptable)"
        elif score >= 0.60:
            return "D (Needs Improvement)"
        else:
            return "F (Critical)"

    def start_monitoring(self, interval_seconds: int = 60):
        """실시간 모니터링 시작"""
        if self._monitoring_active:
            return

        self._monitoring_active = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop, args=(interval_seconds,), daemon=True
        )
        self._monitor_thread.start()
        print(f"🔍 Anchor Quality 모니터링 시작 (간격: {interval_seconds}초)")

    def stop_monitoring(self):
        """실시간 모니터링 중단"""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        print("🔍 Anchor Quality 모니터링 중단")

    def _monitoring_loop(self, interval_seconds: int):
        """모니터링 루프"""
        while self._monitoring_active:
            try:
                # 품질 스냅샷 생성 및 저장
                snapshot = self.get_current_quality_snapshot()
                self.quality_history.append(snapshot)

                # 임계 상황 체크
                if snapshot.overall_score < 0.6:
                    print(
                        f"🚨 CRITICAL: Anchor 품질 임계점 이하 ({snapshot.overall_score:.2f})"
                    )

                # 대기
                time.sleep(interval_seconds)

            except Exception as e:
                print(f"⚠️ 모니터링 오류: {e}")
                time.sleep(interval_seconds)

    def export_quality_data(self, filepath: str = None):
        """품질 데이터 내보내기"""
        if not filepath:
            filepath = (
                f"echo_quality_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "current_stats": self.current_stats,
            "targets": self.targets,
            "recent_snapshots": [
                asdict(s) for s in list(self.quality_history)[-50:]
            ],  # 최근 50개
            "summary_report": self.generate_quality_report(),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"📄 품질 데이터 내보내기 완료: {filepath}")
        return filepath


# 전역 모니터 인스턴스
_quality_monitor = None


def get_quality_monitor() -> EchoAnchorQualityMonitor:
    """글로벌 품질 모니터 반환"""
    global _quality_monitor
    if _quality_monitor is None:
        _quality_monitor = EchoAnchorQualityMonitor()
    return _quality_monitor


def record_quality_event(validation_result, signature: str, llm_used: str = None):
    """품질 이벤트 기록 (편의 함수)"""
    monitor = get_quality_monitor()
    monitor.record_judgment(validation_result, signature, llm_used)


def get_current_quality_status() -> Dict:
    """현재 품질 상태 조회 (편의 함수)"""
    monitor = get_quality_monitor()
    return monitor.generate_quality_report()


def start_quality_monitoring(interval: int = 60):
    """품질 모니터링 시작 (편의 함수)"""
    monitor = get_quality_monitor()
    monitor.start_monitoring(interval)


if __name__ == "__main__":
    # 직접 실행시 현재 품질 상태 출력
    status = get_current_quality_status()
    print("📊 현재 Echo Anchor 품질 상태:")
    print(f"   전체 점수: {status['summary']['quality_grade']}")
    print(f"   준수율: {status['summary']['compliance_rate']:.1%}")
    print(f"   총 판단 수: {status['summary']['total_judgments']}")

    if status["warnings"]:
        print("⚠️ 경고사항:")
        for warning in status["warnings"]:
            print(f"   • {warning}")

    if status["recommendations"]:
        print("💡 권장사항:")
        for rec in status["recommendations"]:
            print(f"   • {rec}")
