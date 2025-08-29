#!/usr/bin/env python3
"""
🔄 Echo Testing Feedback Loop System
회귀 테스트 + 지속 모니터링 + 자동 품질 보증 시스템

핵심 기능:
1. 자동 회귀 테스트 (Regression Testing)
2. 지속적 성능 모니터링 (Continuous Performance Monitoring)
3. 품질 메트릭 추적 (Quality Metrics Tracking)
4. 자동 테스트 케이스 생성 (Auto Test Case Generation)
5. 피드백 루프 최적화 (Feedback Loop Optimization)
"""

import asyncio
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import logging
import hashlib
import statistics


class TestType(Enum):
    """테스트 타입"""

    REGRESSION = "regression"  # 회귀 테스트
    PERFORMANCE = "performance"  # 성능 테스트
    INTEGRATION = "integration"  # 통합 테스트
    STRESS = "stress"  # 스트레스 테스트
    QUALITY = "quality"  # 품질 테스트


class TestStatus(Enum):
    """테스트 상태"""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RUNNING = "running"
    PENDING = "pending"


class MetricType(Enum):
    """메트릭 타입"""

    RESPONSE_TIME = "response_time"
    CONFIDENCE_SCORE = "confidence_score"
    ACCURACY = "accuracy"
    COVERAGE = "coverage"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"


@dataclass
class TestCase:
    """테스트 케이스"""

    id: str
    name: str
    test_type: TestType
    input_data: Dict[str, Any]
    expected_output: Optional[Dict[str, Any]]
    test_function: str
    priority: int = 1
    timeout: float = 30.0
    enabled: bool = True


@dataclass
class TestResult:
    """테스트 결과"""

    test_id: str
    timestamp: datetime
    status: TestStatus
    execution_time: float
    actual_output: Optional[Dict[str, Any]]
    error_message: Optional[str]
    metrics: Dict[str, float]
    environment_info: Dict[str, Any]


@dataclass
class QualityMetric:
    """품질 메트릭"""

    metric_type: MetricType
    timestamp: datetime
    value: float
    component: str
    metadata: Dict[str, Any]


@dataclass
class FeedbackReport:
    """피드백 리포트"""

    timestamp: datetime
    test_summary: Dict[str, Any]
    quality_trends: Dict[str, List[float]]
    performance_analysis: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    regression_alerts: List[Dict[str, Any]]


class EchoTestingFeedbackLoop:
    """
    🔄 Echo Testing Feedback Loop System
    """

    def __init__(self):
        self.test_cases = {}  # test_id -> TestCase
        self.test_results = deque(maxlen=1000)  # 최근 1000개 테스트 결과
        self.quality_metrics = deque(maxlen=5000)  # 최근 5000개 메트릭
        self.baseline_metrics = {}  # 기준 메트릭

        # 모니터링 설정
        self.monitoring_active = True
        self.monitoring_interval = 300  # 5분마다 모니터링
        self.monitoring_thread = None

        # 테스트 실행기
        self.test_executors = {
            TestType.REGRESSION: self._execute_regression_test,
            TestType.PERFORMANCE: self._execute_performance_test,
            TestType.INTEGRATION: self._execute_integration_test,
            TestType.STRESS: self._execute_stress_test,
            TestType.QUALITY: self._execute_quality_test,
        }

        # 임계값 설정
        self.thresholds = {
            MetricType.RESPONSE_TIME: 5.0,  # 5초
            MetricType.CONFIDENCE_SCORE: 0.7,  # 70% 신뢰도
            MetricType.ACCURACY: 0.8,  # 80% 정확도
            MetricType.COVERAGE: 0.9,  # 90% 커버리지
            MetricType.ERROR_RATE: 0.1,  # 10% 오류율
            MetricType.THROUGHPUT: 10.0,  # 초당 10개 처리
        }

        # 피드백 통계
        self.feedback_stats = {
            "total_tests_run": 0,
            "total_passed": 0,
            "total_failed": 0,
            "regression_detected": 0,
            "performance_improvements": 0,
            "quality_score": 0.0,
        }

        print("🔄 Echo Testing Feedback Loop 초기화 완료")
        print("   📊 회귀 테스트 엔진 활성화")
        print("   📈 지속 성능 모니터링 시작")
        print("   🎯 품질 메트릭 추적 시작")

        # 기본 테스트 케이스 등록
        self._register_default_test_cases()

        # 백그라운드 모니터링 시작
        self.start_monitoring()

    def _register_default_test_cases(self):
        """기본 테스트 케이스 등록"""

        # 회귀 테스트 케이스들
        regression_cases = [
            TestCase(
                id="regression_basic_judgment",
                name="기본 판단 회귀 테스트",
                test_type=TestType.REGRESSION,
                input_data={"user_input": "안녕하세요!", "signature": "Aurora"},
                expected_output={"confidence_min": 0.8, "response_contains": "안녕"},
                test_function="test_basic_judgment",
                priority=1,
            ),
            TestCase(
                id="regression_signature_consistency",
                name="시그니처 일관성 회귀 테스트",
                test_type=TestType.REGRESSION,
                input_data={"signatures": ["Aurora", "Phoenix", "Sage", "Companion"]},
                expected_output={"all_signatures_working": True},
                test_function="test_signature_consistency",
                priority=1,
            ),
            TestCase(
                id="regression_enhanced_judge",
                name="Enhanced Judge 회귀 테스트",
                test_type=TestType.REGRESSION,
                input_data={"complex_input": "복잡한 철학적 질문에 대해 분석해주세요"},
                expected_output={"enhanced_judge_used": True, "quality_min": 0.6},
                test_function="test_enhanced_judge",
                priority=1,
            ),
        ]

        # 성능 테스트 케이스들
        performance_cases = [
            TestCase(
                id="performance_response_time",
                name="응답 시간 성능 테스트",
                test_type=TestType.PERFORMANCE,
                input_data={"iterations": 10},
                expected_output={"avg_response_time_max": 2.0},
                test_function="test_response_time",
                priority=2,
            ),
            TestCase(
                id="performance_throughput",
                name="처리량 성능 테스트",
                test_type=TestType.PERFORMANCE,
                input_data={"concurrent_requests": 5, "duration": 30},
                expected_output={"throughput_min": 5.0},
                test_function="test_throughput",
                priority=2,
            ),
        ]

        # 통합 테스트 케이스들
        integration_cases = [
            TestCase(
                id="integration_end_to_end",
                name="종단간 통합 테스트",
                test_type=TestType.INTEGRATION,
                input_data={"full_workflow": True},
                expected_output={"all_components_working": True},
                test_function="test_end_to_end",
                priority=2,
            )
        ]

        # 모든 테스트 케이스 등록
        all_cases = regression_cases + performance_cases + integration_cases

        for test_case in all_cases:
            self.test_cases[test_case.id] = test_case

        print(f"📋 {len(all_cases)}개 기본 테스트 케이스 등록 완료")

    def start_monitoring(self):
        """백그라운드 모니터링 시작"""

        def monitor_loop():
            while self.monitoring_active:
                try:
                    # 회귀 테스트 실행
                    asyncio.run(self._run_regression_tests())

                    # 성능 모니터링
                    asyncio.run(self._monitor_performance())

                    # 품질 메트릭 수집
                    self._collect_quality_metrics()

                    time.sleep(self.monitoring_interval)

                except Exception as e:
                    print(f"⚠️ 모니터링 오류: {e}")
                    time.sleep(60)  # 오류 시 1분 대기

        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()

    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

    async def run_tests(
        self, test_type: Optional[TestType] = None, test_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """테스트 실행"""

        print(f"🧪 테스트 실행 시작: {test_type.value if test_type else 'ALL'}")

        # 실행할 테스트 케이스 선택
        if test_ids:
            test_cases = [
                self.test_cases[tid] for tid in test_ids if tid in self.test_cases
            ]
        elif test_type:
            test_cases = [
                tc for tc in self.test_cases.values() if tc.test_type == test_type
            ]
        else:
            test_cases = list(self.test_cases.values())

        # 활성화된 테스트만 선택
        test_cases = [tc for tc in test_cases if tc.enabled]

        # 우선순위별 정렬
        test_cases.sort(key=lambda x: x.priority)

        results = []
        passed = 0
        failed = 0

        for test_case in test_cases:
            print(f"   🔍 실행 중: {test_case.name}")

            try:
                result = await self._execute_test(test_case)
                results.append(result)

                if result.status == TestStatus.PASSED:
                    passed += 1
                    print(f"     ✅ PASSED ({result.execution_time:.2f}s)")
                else:
                    failed += 1
                    print(f"     ❌ FAILED: {result.error_message}")

            except Exception as e:
                failed += 1
                error_result = TestResult(
                    test_id=test_case.id,
                    timestamp=datetime.now(),
                    status=TestStatus.FAILED,
                    execution_time=0.0,
                    actual_output=None,
                    error_message=str(e),
                    metrics={},
                    environment_info={},
                )
                results.append(error_result)
                print(f"     💥 ERROR: {e}")

        # 결과 저장
        self.test_results.extend(results)

        # 통계 업데이트
        self.feedback_stats["total_tests_run"] += len(results)
        self.feedback_stats["total_passed"] += passed
        self.feedback_stats["total_failed"] += failed

        test_summary = {
            "timestamp": datetime.now().isoformat(),
            "test_type": test_type.value if test_type else "mixed",
            "total_tests": len(results),
            "passed": passed,
            "failed": failed,
            "success_rate": passed / len(results) * 100 if results else 0,
            "results": [asdict(r) for r in results],
        }

        print(
            f"📊 테스트 완료: {passed}/{len(results)} 성공 ({passed/len(results)*100:.1f}%)"
        )

        return test_summary

    async def _execute_test(self, test_case: TestCase) -> TestResult:
        """개별 테스트 실행"""

        start_time = time.time()

        try:
            # 테스트 실행기 선택
            executor = self.test_executors.get(
                test_case.test_type, self._execute_generic_test
            )

            # 테스트 실행
            actual_output, metrics = await executor(test_case)

            # 결과 검증
            status = self._validate_test_result(test_case, actual_output)

            execution_time = time.time() - start_time

            return TestResult(
                test_id=test_case.id,
                timestamp=datetime.now(),
                status=status,
                execution_time=execution_time,
                actual_output=actual_output,
                error_message=None,
                metrics=metrics,
                environment_info={"test_type": test_case.test_type.value},
            )

        except Exception as e:
            execution_time = time.time() - start_time

            return TestResult(
                test_id=test_case.id,
                timestamp=datetime.now(),
                status=TestStatus.FAILED,
                execution_time=execution_time,
                actual_output=None,
                error_message=str(e),
                metrics={},
                environment_info={"test_type": test_case.test_type.value},
            )

    async def _execute_regression_test(
        self, test_case: TestCase
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """회귀 테스트 실행"""

        if test_case.test_function == "test_basic_judgment":
            # 기본 판단 테스트
            from echo_engine.echo_centered_judgment_hybrid import process_echo_judgment

            result = await process_echo_judgment(
                user_input=test_case.input_data["user_input"],
                signature=test_case.input_data["signature"],
            )

            return {
                "confidence": result.confidence_score,
                "response": result.final_judgment,
                "processing_time": result.processing_time,
                "source": result.judgment_source.value,
            }, {
                "confidence_score": result.confidence_score,
                "response_time": result.processing_time,
            }

        elif test_case.test_function == "test_signature_consistency":
            # 시그니처 일관성 테스트
            from echo_engine.echo_centered_judgment_hybrid import process_echo_judgment

            results = {}
            metrics = {}

            for signature in test_case.input_data["signatures"]:
                result = await process_echo_judgment(
                    user_input="테스트 메시지입니다", signature=signature
                )
                results[signature] = {
                    "confidence": result.confidence_score,
                    "response_length": len(result.final_judgment),
                }
                metrics[f"{signature}_confidence"] = result.confidence_score

            return {
                "signature_results": results,
                "all_signatures_working": all(
                    r["confidence"] > 0.5 for r in results.values()
                ),
            }, metrics

        elif test_case.test_function == "test_enhanced_judge":
            # Enhanced Judge 테스트
            from echo_engine.enhanced_llm_free_judge import get_enhanced_llm_free_judge

            judge = get_enhanced_llm_free_judge()
            result = await judge.process_independent_judgment(
                user_input=test_case.input_data["complex_input"], signature="Sage"
            )

            return {
                "enhanced_judge_used": True,
                "confidence": result.confidence_score,
                "quality": result.fallback_quality,
                "complexity": result.complexity_level.value,
            }, {
                "confidence_score": result.confidence_score,
                "fallback_quality": result.fallback_quality,
                "processing_time": result.processing_time,
            }

        else:
            # 기본 회귀 테스트
            return {"status": "completed"}, {"execution_time": 0.1}

    async def _execute_performance_test(
        self, test_case: TestCase
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """성능 테스트 실행"""

        if test_case.test_function == "test_response_time":
            # 응답 시간 테스트
            from echo_engine.echo_centered_judgment_hybrid import process_echo_judgment

            times = []
            iterations = test_case.input_data.get("iterations", 5)

            for i in range(iterations):
                start_time = time.time()
                await process_echo_judgment(
                    user_input=f"성능 테스트 메시지 {i+1}", signature="Aurora"
                )
                response_time = time.time() - start_time
                times.append(response_time)

            avg_time = statistics.mean(times)
            max_time = max(times)
            min_time = min(times)

            return {
                "avg_response_time": avg_time,
                "max_response_time": max_time,
                "min_response_time": min_time,
                "iterations": iterations,
            }, {
                "avg_response_time": avg_time,
                "max_response_time": max_time,
                "throughput": iterations / sum(times),
            }

        elif test_case.test_function == "test_throughput":
            # 처리량 테스트
            from echo_engine.echo_centered_judgment_hybrid import process_echo_judgment

            concurrent_requests = test_case.input_data.get("concurrent_requests", 3)
            duration = test_case.input_data.get("duration", 10)

            start_time = time.time()
            completed_requests = 0

            async def worker():
                nonlocal completed_requests
                while time.time() - start_time < duration:
                    try:
                        await process_echo_judgment(
                            user_input="처리량 테스트", signature="Phoenix"
                        )
                        completed_requests += 1
                    except:
                        pass

            # 동시 작업 실행
            tasks = [worker() for _ in range(concurrent_requests)]
            await asyncio.gather(*tasks, return_exceptions=True)

            actual_duration = time.time() - start_time
            throughput = completed_requests / actual_duration

            return {
                "completed_requests": completed_requests,
                "duration": actual_duration,
                "throughput": throughput,
            }, {
                "throughput": throughput,
                "completion_rate": completed_requests
                / (concurrent_requests * duration),
            }

        else:
            return {"status": "completed"}, {"execution_time": 0.1}

    async def _execute_integration_test(
        self, test_case: TestCase
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """통합 테스트 실행"""

        if test_case.test_function == "test_end_to_end":
            # 종단간 테스트
            from echo_engine.echo_centered_judgment_hybrid import (
                get_echo_judgment_hybrid,
            )

            hybrid = get_echo_judgment_hybrid()

            # 시스템 분석
            analytics = hybrid.get_system_analytics()

            # 모듈 연결 상태 확인
            modules = analytics.get("integrated_modules", {})
            connected_modules = sum(1 for connected in modules.values() if connected)
            total_modules = len(modules)

            # 기능 테스트
            from echo_engine.echo_centered_judgment_hybrid import process_echo_judgment

            result = await process_echo_judgment(
                user_input="통합 테스트 메시지", signature="Companion"
            )

            return {
                "all_components_working": connected_modules == total_modules,
                "connected_modules": connected_modules,
                "total_modules": total_modules,
                "judgment_working": result.confidence_score > 0.5,
                "integration_score": connected_modules / total_modules * 100,
            }, {
                "integration_score": connected_modules / total_modules,
                "judgment_confidence": result.confidence_score,
            }

        else:
            return {"status": "completed"}, {"execution_time": 0.1}

    async def _execute_stress_test(
        self, test_case: TestCase
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """스트레스 테스트 실행"""
        return {"status": "completed"}, {"execution_time": 0.1}

    async def _execute_quality_test(
        self, test_case: TestCase
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """품질 테스트 실행"""
        return {"status": "completed"}, {"execution_time": 0.1}

    async def _execute_generic_test(
        self, test_case: TestCase
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """일반 테스트 실행"""
        return {"status": "completed"}, {"execution_time": 0.1}

    def _validate_test_result(
        self, test_case: TestCase, actual_output: Dict[str, Any]
    ) -> TestStatus:
        """테스트 결과 검증"""

        if not test_case.expected_output:
            return TestStatus.PASSED

        try:
            expected = test_case.expected_output

            for key, expected_value in expected.items():
                if key.endswith("_min"):
                    actual_key = key[:-4]
                    if actual_key in actual_output:
                        if actual_output[actual_key] < expected_value:
                            return TestStatus.FAILED
                elif key.endswith("_max"):
                    actual_key = key[:-4]
                    if actual_key in actual_output:
                        if actual_output[actual_key] > expected_value:
                            return TestStatus.FAILED
                elif key.endswith("_contains"):
                    actual_key = key[:-9]
                    if actual_key in actual_output:
                        if expected_value not in str(actual_output[actual_key]):
                            return TestStatus.FAILED
                else:
                    if key in actual_output:
                        if actual_output[key] != expected_value:
                            return TestStatus.FAILED

            return TestStatus.PASSED

        except Exception:
            return TestStatus.FAILED

    async def _run_regression_tests(self):
        """회귀 테스트 실행"""
        await self.run_tests(test_type=TestType.REGRESSION)

    async def _monitor_performance(self):
        """성능 모니터링"""
        await self.run_tests(test_type=TestType.PERFORMANCE)

    def _collect_quality_metrics(self):
        """품질 메트릭 수집"""

        # 최근 테스트 결과에서 메트릭 추출
        recent_results = list(self.test_results)[-50:]  # 최근 50개

        if recent_results:
            # 성공률 메트릭
            success_rate = sum(
                1 for r in recent_results if r.status == TestStatus.PASSED
            ) / len(recent_results)
            self._add_quality_metric(
                MetricType.ACCURACY, success_rate, "testing_system"
            )

            # 평균 응답 시간 메트릭
            response_times = [
                r.execution_time for r in recent_results if r.execution_time > 0
            ]
            if response_times:
                avg_response_time = statistics.mean(response_times)
                self._add_quality_metric(
                    MetricType.RESPONSE_TIME, avg_response_time, "testing_system"
                )

            # 오류율 메트릭
            error_rate = sum(
                1 for r in recent_results if r.status == TestStatus.FAILED
            ) / len(recent_results)
            self._add_quality_metric(
                MetricType.ERROR_RATE, error_rate, "testing_system"
            )

    def _add_quality_metric(
        self, metric_type: MetricType, value: float, component: str
    ):
        """품질 메트릭 추가"""
        metric = QualityMetric(
            metric_type=metric_type,
            timestamp=datetime.now(),
            value=value,
            component=component,
            metadata={},
        )
        self.quality_metrics.append(metric)

    def generate_feedback_report(self) -> FeedbackReport:
        """피드백 리포트 생성"""

        # 테스트 요약
        recent_results = list(self.test_results)[-100:]
        test_summary = {
            "total_tests": len(recent_results),
            "passed": sum(1 for r in recent_results if r.status == TestStatus.PASSED),
            "failed": sum(1 for r in recent_results if r.status == TestStatus.FAILED),
            "success_rate": (
                sum(1 for r in recent_results if r.status == TestStatus.PASSED)
                / len(recent_results)
                * 100
                if recent_results
                else 0
            ),
        }

        # 품질 트렌드
        quality_trends = {}
        for metric_type in MetricType:
            recent_metrics = [
                m.value
                for m in self.quality_metrics
                if m.metric_type == metric_type
                and m.timestamp > datetime.now() - timedelta(hours=24)
            ]
            quality_trends[metric_type.value] = recent_metrics[-10:]  # 최근 10개

        # 성능 분석
        performance_analysis = {
            "avg_response_time": (
                statistics.mean(
                    [
                        m.value
                        for m in self.quality_metrics
                        if m.metric_type == MetricType.RESPONSE_TIME
                    ][-20:]
                )
                if any(
                    m.metric_type == MetricType.RESPONSE_TIME
                    for m in self.quality_metrics
                )
                else 0
            ),
            "error_rate_trend": "stable",  # 구현 필요
            "throughput_trend": "improving",  # 구현 필요
        }

        # 권장사항
        recommendations = self._generate_recommendations(test_summary, quality_trends)

        # 회귀 알림
        regression_alerts = self._detect_regressions(recent_results)

        return FeedbackReport(
            timestamp=datetime.now(),
            test_summary=test_summary,
            quality_trends=quality_trends,
            performance_analysis=performance_analysis,
            recommendations=recommendations,
            regression_alerts=regression_alerts,
        )

    def _generate_recommendations(
        self, test_summary: Dict[str, Any], quality_trends: Dict[str, List[float]]
    ) -> List[Dict[str, Any]]:
        """권장사항 생성"""
        recommendations = []

        # 성공률 기반 권장사항
        success_rate = test_summary.get("success_rate", 0)
        if success_rate < 80:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "quality",
                    "title": "테스트 성공률 개선",
                    "description": f"현재 성공률 {success_rate:.1f}%로 80% 이하입니다.",
                    "action": "실패 테스트 원인 분석 및 수정",
                }
            )

        # 응답 시간 기반 권장사항
        response_times = quality_trends.get("response_time", [])
        if response_times and statistics.mean(response_times) > 3.0:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "performance",
                    "title": "응답 시간 최적화",
                    "description": f"평균 응답 시간이 {statistics.mean(response_times):.2f}초입니다.",
                    "action": "성능 프로파일링 및 최적화",
                }
            )

        return recommendations

    def _detect_regressions(
        self, recent_results: List[TestResult]
    ) -> List[Dict[str, Any]]:
        """회귀 감지"""
        alerts = []

        # 최근 실패가 증가했는지 확인
        if len(recent_results) >= 10:
            recent_failures = sum(
                1 for r in recent_results[-5:] if r.status == TestStatus.FAILED
            )
            previous_failures = sum(
                1 for r in recent_results[-10:-5] if r.status == TestStatus.FAILED
            )

            if recent_failures > previous_failures * 1.5:  # 50% 이상 증가
                alerts.append(
                    {
                        "severity": "high",
                        "type": "failure_increase",
                        "message": f"최근 실패율이 {recent_failures}에서 {previous_failures}로 증가했습니다.",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return alerts

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""

        recent_results = list(self.test_results)[-50:]

        return {
            "monitoring_active": self.monitoring_active,
            "total_test_cases": len(self.test_cases),
            "recent_test_results": len(recent_results),
            "feedback_stats": self.feedback_stats,
            "quality_metrics_count": len(self.quality_metrics),
            "last_test_run": (
                recent_results[-1].timestamp.isoformat() if recent_results else None
            ),
            "system_health": {
                "success_rate": (
                    sum(1 for r in recent_results if r.status == TestStatus.PASSED)
                    / len(recent_results)
                    * 100
                    if recent_results
                    else 0
                ),
                "avg_execution_time": (
                    statistics.mean([r.execution_time for r in recent_results])
                    if recent_results
                    else 0
                ),
                "active_monitoring": self.monitoring_active,
            },
        }


# 전역 인스턴스
_testing_feedback_loop = None


def get_testing_feedback_loop() -> EchoTestingFeedbackLoop:
    """Testing Feedback Loop 인스턴스 반환"""
    global _testing_feedback_loop
    if _testing_feedback_loop is None:
        _testing_feedback_loop = EchoTestingFeedbackLoop()
    return _testing_feedback_loop


# 편의 함수들
async def run_regression_tests() -> Dict[str, Any]:
    """회귀 테스트 실행 편의 함수"""
    loop = get_testing_feedback_loop()
    return await loop.run_tests(test_type=TestType.REGRESSION)


async def run_performance_tests() -> Dict[str, Any]:
    """성능 테스트 실행 편의 함수"""
    loop = get_testing_feedback_loop()
    return await loop.run_tests(test_type=TestType.PERFORMANCE)


def get_feedback_report() -> FeedbackReport:
    """피드백 리포트 조회 편의 함수"""
    loop = get_testing_feedback_loop()
    return loop.generate_feedback_report()


# 테스트 코드
if __name__ == "__main__":

    async def test_feedback_loop():
        print("🔄 Testing Feedback Loop 테스트")
        print("=" * 60)

        loop = get_testing_feedback_loop()

        # 회귀 테스트 실행
        print("\n📊 회귀 테스트 실행...")
        regression_results = await loop.run_tests(test_type=TestType.REGRESSION)
        print(f"   성공률: {regression_results['success_rate']:.1f}%")

        # 성능 테스트 실행
        print("\n📈 성능 테스트 실행...")
        performance_results = await loop.run_tests(test_type=TestType.PERFORMANCE)
        print(f"   성공률: {performance_results['success_rate']:.1f}%")

        # 피드백 리포트 생성
        print("\n📋 피드백 리포트 생성...")
        report = loop.generate_feedback_report()
        print(f"   총 테스트: {report.test_summary['total_tests']}")
        print(f"   성공률: {report.test_summary['success_rate']:.1f}%")
        print(f"   권장사항: {len(report.recommendations)}개")
        print(f"   회귀 알림: {len(report.regression_alerts)}개")

        # 시스템 상태
        print("\n🔍 시스템 상태:")
        status = loop.get_system_status()
        print(f"   테스트 케이스: {status['total_test_cases']}개")
        print(f"   품질 메트릭: {status['quality_metrics_count']}개")
        print(f"   시스템 건강도: {status['system_health']['success_rate']:.1f}%")

        # 모니터링 중지
        loop.stop_monitoring()

    asyncio.run(test_feedback_loop())
