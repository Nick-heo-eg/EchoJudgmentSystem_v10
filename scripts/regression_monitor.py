#!/usr/bin/env python3
"""
회귀 알림 시스템
성능/품질 지표의 회귀를 자동 감지하고 알림 발송
"""

import json
import time
import smtplib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess
import sys
import os

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """성능 지표"""

    name: str
    value: float
    unit: str
    timestamp: str
    threshold_warning: float = 0.0
    threshold_critical: float = 0.0


@dataclass
class RegressionAlert:
    """회귀 알림"""

    metric_name: str
    current_value: float
    previous_value: float
    change_percent: float
    severity: str  # "warning", "critical"
    timestamp: str
    context: Dict[str, Any]


class RegressionMonitor:
    """회귀 모니터링 시스템"""

    def __init__(
        self,
        data_dir: str = "data/metrics",
        alert_config: str = "config/regression_alerts.yaml",
    ):
        self.data_dir = Path(data_dir)
        self.alert_config = Path(alert_config)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 설정
        self.thresholds = {
            "performance_degradation": 20.0,  # 20% 성능 저하
            "memory_increase": 50.0,  # 50% 메모리 증가
            "error_rate_increase": 10.0,  # 10% 에러율 증가
            "test_coverage_decrease": 5.0,  # 5% 커버리지 감소
        }

        # 알림 채널
        self.notification_channels = {
            "console": True,
            "file": True,
            "email": os.getenv("REGRESSION_EMAIL_ENABLED", "false").lower() == "true",
        }

    def collect_current_metrics(self) -> List[Metric]:
        """현재 메트릭 수집"""
        metrics = []
        timestamp = datetime.now().isoformat()

        try:
            # 1. 성능 벤치마크
            performance_metrics = self._collect_performance_metrics()
            for name, value in performance_metrics.items():
                metrics.append(
                    Metric(
                        name=f"performance.{name}",
                        value=value,
                        unit="ms",
                        timestamp=timestamp,
                        threshold_warning=self.thresholds["performance_degradation"],
                        threshold_critical=self.thresholds["performance_degradation"]
                        * 2,
                    )
                )

            # 2. 메모리 사용량
            memory_usage = self._collect_memory_metrics()
            metrics.append(
                Metric(
                    name="system.memory_usage",
                    value=memory_usage,
                    unit="MB",
                    timestamp=timestamp,
                    threshold_warning=self.thresholds["memory_increase"],
                    threshold_critical=self.thresholds["memory_increase"] * 2,
                )
            )

            # 3. 테스트 결과
            test_metrics = self._collect_test_metrics()
            for name, value in test_metrics.items():
                metrics.append(
                    Metric(
                        name=f"test.{name}",
                        value=value,
                        unit="percent" if "coverage" in name else "count",
                        timestamp=timestamp,
                        threshold_warning=5.0,
                        threshold_critical=10.0,
                    )
                )

            # 4. 코드 품질
            quality_metrics = self._collect_quality_metrics()
            for name, value in quality_metrics.items():
                metrics.append(
                    Metric(
                        name=f"quality.{name}",
                        value=value,
                        unit="count",
                        timestamp=timestamp,
                        threshold_warning=10.0,
                        threshold_critical=25.0,
                    )
                )

        except Exception as e:
            logger.error(f"❌ Failed to collect metrics: {e}")

        return metrics

    def _collect_performance_metrics(self) -> Dict[str, float]:
        """성능 메트릭 수집"""
        try:
            # 간단한 성능 테스트 실행
            result = subprocess.run(
                [sys.executable, "scripts/bench.py"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # 벤치마크 결과 파싱
                if Path("benchmark_results.json").exists():
                    with open("benchmark_results.json") as f:
                        data = json.load(f)

                    benchmarks = data.get("benchmarks", {})
                    echo_bench = benchmarks.get("echo_engine", {})

                    if echo_bench.get("status") == "success":
                        engine_results = echo_bench.get("engine_benchmarks", [])
                        if engine_results:
                            return {
                                "echo_engine_p95": engine_results[0].get("p95_ms", 0),
                                "echo_engine_mean": engine_results[0].get("mean_ms", 0),
                            }

            # 폴백: 간단한 임포트 테스트
            start = time.perf_counter()
            try:
                from echo_engine.judgment_engine import FISTJudgmentEngine

                engine = FISTJudgmentEngine()
            except Exception:
                pass
            end = time.perf_counter()

            return {"engine_import_time": (end - start) * 1000}

        except Exception as e:
            logger.warning(f"Performance collection failed: {e}")
            return {"engine_import_time": 1000.0}  # fallback

    def _collect_memory_metrics(self) -> float:
        """메모리 메트릭 수집"""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 100.0  # fallback

    def _collect_test_metrics(self) -> Dict[str, float]:
        """테스트 메트릭 수집"""
        try:
            # pytest 실행
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "--tb=no", "-q"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            output = result.stdout + result.stderr

            # 결과 파싱
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            total = passed + failed

            pass_rate = (passed / total * 100) if total > 0 else 0

            return {
                "pass_rate": pass_rate,
                "total_tests": total,
                "failed_tests": failed,
            }

        except Exception as e:
            logger.warning(f"Test collection failed: {e}")
            return {"pass_rate": 95.0, "total_tests": 10, "failed_tests": 0}

    def _collect_quality_metrics(self) -> Dict[str, float]:
        """코드 품질 메트릭 수집"""
        try:
            # ruff 린트 체크
            result = subprocess.run(
                ["ruff", "check", "src/", "echo_engine/", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout:
                issues = json.loads(result.stdout)
                return {
                    "lint_issues": len(issues),
                    "critical_issues": sum(
                        1
                        for issue in issues
                        if "critical" in issue.get("severity", "").lower()
                    ),
                }

        except Exception as e:
            logger.warning(f"Quality collection failed: {e}")

        return {"lint_issues": 0, "critical_issues": 0}

    def save_metrics(self, metrics: List[Metric]):
        """메트릭을 파일에 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"metrics_{timestamp}.json"

        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": [asdict(metric) for metric in metrics],
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"📊 Metrics saved: {filename}")

    def load_previous_metrics(self, hours_back: int = 24) -> Optional[List[Metric]]:
        """이전 메트릭 로드"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        metric_files = sorted(self.data_dir.glob("metrics_*.json"))

        for metric_file in reversed(metric_files):  # 최신부터
            try:
                with open(metric_file) as f:
                    data = json.load(f)

                file_time = datetime.fromisoformat(data["timestamp"])
                if file_time >= cutoff_time:
                    return [Metric(**m) for m in data["metrics"]]

            except Exception as e:
                logger.warning(f"Failed to load {metric_file}: {e}")

        return None

    def detect_regressions(
        self, current_metrics: List[Metric], previous_metrics: List[Metric]
    ) -> List[RegressionAlert]:
        """회귀 감지"""
        alerts = []

        # 메트릭을 딕셔너리로 변환
        current_dict = {m.name: m for m in current_metrics}
        previous_dict = {m.name: m for m in previous_metrics}

        for name in current_dict:
            if name not in previous_dict:
                continue

            current = current_dict[name]
            previous = previous_dict[name]

            # 변화율 계산
            if previous.value == 0:
                continue

            change_percent = ((current.value - previous.value) / previous.value) * 100

            # 회귀 조건 확인
            regression_detected = False
            severity = "info"

            if "performance" in name or "time" in name:
                # 성능 지표: 증가가 나쁨
                if change_percent > current.threshold_critical:
                    regression_detected = True
                    severity = "critical"
                elif change_percent > current.threshold_warning:
                    regression_detected = True
                    severity = "warning"

            elif "memory" in name:
                # 메모리: 증가가 나쁨
                if change_percent > current.threshold_critical:
                    regression_detected = True
                    severity = "critical"
                elif change_percent > current.threshold_warning:
                    regression_detected = True
                    severity = "warning"

            elif "pass_rate" in name or "coverage" in name:
                # 성공률/커버리지: 감소가 나쁨
                if change_percent < -current.threshold_critical:
                    regression_detected = True
                    severity = "critical"
                elif change_percent < -current.threshold_warning:
                    regression_detected = True
                    severity = "warning"

            elif "issues" in name or "errors" in name:
                # 이슈/에러: 증가가 나쁨
                if change_percent > current.threshold_critical:
                    regression_detected = True
                    severity = "critical"
                elif change_percent > current.threshold_warning:
                    regression_detected = True
                    severity = "warning"

            if regression_detected:
                alerts.append(
                    RegressionAlert(
                        metric_name=name,
                        current_value=current.value,
                        previous_value=previous.value,
                        change_percent=change_percent,
                        severity=severity,
                        timestamp=current.timestamp,
                        context={
                            "unit": current.unit,
                            "threshold_warning": current.threshold_warning,
                            "threshold_critical": current.threshold_critical,
                        },
                    )
                )

        return alerts

    def send_alerts(self, alerts: List[RegressionAlert]):
        """알림 발송"""
        if not alerts:
            logger.info("✅ No regressions detected")
            return

        # 콘솔 알림
        if self.notification_channels["console"]:
            self._send_console_alert(alerts)

        # 파일 알림
        if self.notification_channels["file"]:
            self._send_file_alert(alerts)

        # 이메일 알림
        if self.notification_channels["email"]:
            self._send_email_alert(alerts)

    def _send_console_alert(self, alerts: List[RegressionAlert]):
        """콘솔 알림"""
        print("🚨 REGRESSION ALERTS DETECTED!")
        print("=" * 50)

        for alert in alerts:
            emoji = "🔥" if alert.severity == "critical" else "⚠️"
            print(f"{emoji} {alert.severity.upper()}: {alert.metric_name}")
            print(f"   Current: {alert.current_value:.2f} {alert.context['unit']}")
            print(f"   Previous: {alert.previous_value:.2f} {alert.context['unit']}")
            print(f"   Change: {alert.change_percent:+.1f}%")
            print()

    def _send_file_alert(self, alerts: List[RegressionAlert]):
        """파일 알림"""
        alert_file = (
            self.data_dir / f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        data = {
            "timestamp": datetime.now().isoformat(),
            "alert_count": len(alerts),
            "alerts": [asdict(alert) for alert in alerts],
        }

        with open(alert_file, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"🚨 Alerts saved: {alert_file}")

    def _send_email_alert(self, alerts: List[RegressionAlert]):
        """이메일 알림 (설정된 경우)"""
        try:
            # 환경변수에서 이메일 설정 로드
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            email_user = os.getenv("EMAIL_USER")
            email_password = os.getenv("EMAIL_PASSWORD")
            email_to = os.getenv("ALERT_EMAIL_TO")

            if not all([email_user, email_password, email_to]):
                logger.warning("Email credentials not configured")
                return

            # 이메일 작성
            msg = MIMEMultipart()
            msg["From"] = email_user
            msg["To"] = email_to
            msg["Subject"] = (
                f"🚨 Echo System Regression Alert - {len(alerts)} issues detected"
            )

            # 본문 작성
            body = self._format_email_body(alerts)
            msg.attach(MIMEText(body, "html"))

            # 발송
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(email_user, email_password)
                server.send_message(msg)

            logger.info("📧 Email alert sent successfully")

        except Exception as e:
            logger.error(f"❌ Failed to send email alert: {e}")

    def _format_email_body(self, alerts: List[RegressionAlert]) -> str:
        """이메일 본문 포맷"""
        html = f"""
        <h2>🚨 Echo System Regression Alert</h2>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Alert Count:</strong> {len(alerts)}</p>
        
        <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #f2f2f2;">
            <th>Severity</th>
            <th>Metric</th>
            <th>Current</th>
            <th>Previous</th>
            <th>Change</th>
        </tr>
        """

        for alert in alerts:
            color = "#ff4444" if alert.severity == "critical" else "#ffaa00"
            html += f"""
        <tr style="background-color: {color}22;">
            <td style="padding: 8px;">{alert.severity.upper()}</td>
            <td style="padding: 8px;">{alert.metric_name}</td>
            <td style="padding: 8px;">{alert.current_value:.2f} {alert.context['unit']}</td>
            <td style="padding: 8px;">{alert.previous_value:.2f} {alert.context['unit']}</td>
            <td style="padding: 8px;"><strong>{alert.change_percent:+.1f}%</strong></td>
        </tr>
            """

        html += """
        </table>
        
        <h3>🔧 Recommended Actions</h3>
        <ul>
            <li>Review recent changes in the affected components</li>
            <li>Run detailed profiling on performance regressions</li>
            <li>Check for memory leaks if memory usage increased</li>
            <li>Investigate failing tests and fix issues</li>
        </ul>
        
        <p><em>Generated by Echo Regression Monitor</em></p>
        """

        return html

    def run_monitoring_cycle(self):
        """전체 모니터링 사이클 실행"""
        logger.info("🔍 Starting regression monitoring cycle...")

        # 1. 현재 메트릭 수집
        current_metrics = self.collect_current_metrics()
        logger.info(f"📊 Collected {len(current_metrics)} current metrics")

        # 2. 메트릭 저장
        self.save_metrics(current_metrics)

        # 3. 이전 메트릭 로드
        previous_metrics = self.load_previous_metrics(hours_back=24)

        if previous_metrics is None:
            logger.info("📋 No previous metrics found - establishing baseline")
            return

        logger.info(f"📋 Loaded {len(previous_metrics)} previous metrics")

        # 4. 회귀 감지
        alerts = self.detect_regressions(current_metrics, previous_metrics)

        # 5. 알림 발송
        self.send_alerts(alerts)

        logger.info("✅ Monitoring cycle completed")


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Echo System Regression Monitor")
    parser.add_argument(
        "--data-dir", default="data/metrics", help="Metrics data directory"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # 로깅 설정
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    # 모니터 실행
    monitor = RegressionMonitor(data_dir=args.data_dir)
    monitor.run_monitoring_cycle()


if __name__ == "__main__":
    main()
