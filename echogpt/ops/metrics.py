#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGPT Metrics System
Performance and quality metrics tracking with operational extensions
"""
import time
import glob
import json
import os
from typing import Dict, List, Any, Optional
from collections import deque
from threading import Lock


class Metrics:
    """Thread-safe metrics collector with operational extensions"""

    def __init__(self, max_samples: int = 1000, events_dir: str = "meta_logs/traces"):
        self.max_samples = max_samples
        self.events_dir = events_dir
        self._lock = Lock()

        # 성능 메트릭
        self._ttl_samples = deque(maxlen=max_samples)  # Total Time to Live
        self._ttfb_samples = deque(maxlen=max_samples)  # Time to First Byte

        # 품질 메트릭
        self._intent_matches = 0  # Teacher-Student 일치 횟수
        self._total_requests = 0  # 총 요청 수
        self._tool_successes = 0  # 도구 성공 횟수
        self._tool_attempts = 0  # 도구 시도 횟수

        # 증류 학습 메트릭
        self._student_f1_estimate: Optional[float] = None  # 최신 학습 F1 기록

        # EWMA를 위한 시계열 샘플 저장 (timestamp, ttl_ms)
        self._ttl_samples_timeseries = deque(maxlen=2000)  # 최근 30분 정도 저장

        # 시스템 메트릭
        self._start_time = time.time()

        # 에러 추적
        self._errors = deque(maxlen=100)

    def observe_request(
        self,
        ttl_ms: int,
        ttfb_ms: int = None,
        intent_match: bool = True,
        tools_success: bool = True,
        tools_attempted: int = 0,
    ):
        """요청 메트릭 기록"""
        with self._lock:
            current_time = time.time()

            self._ttl_samples.append(ttl_ms)
            if ttfb_ms is not None:
                self._ttfb_samples.append(ttfb_ms)

            # EWMA를 위한 시계열 데이터 저장
            self._ttl_samples_timeseries.append((current_time, ttl_ms))

            self._total_requests += 1

            if intent_match:
                self._intent_matches += 1

            if tools_attempted > 0:
                self._tool_attempts += tools_attempted
                if tools_success:
                    self._tool_successes += tools_attempted

    def observe_error(self, error_type: str, error_msg: str):
        """에러 기록"""
        with self._lock:
            self._errors.append(
                {"type": error_type, "message": error_msg, "timestamp": time.time()}
            )

    def set_student_f1(self, f1_macro: Optional[float]):
        """Student 모델 F1 점수 업데이트"""
        with self._lock:
            if f1_macro is not None:
                self._student_f1_estimate = float(f1_macro)

    def _recent_trace_samples(self, k: int = 5) -> List[Dict[str, Any]]:
        """최근 trace 샘플 추출"""
        try:
            # events_dir에서 최신 .jsonl 파일 찾기
            pattern = os.path.join(self.events_dir, "*.jsonl")
            files = sorted(glob.glob(pattern))
            if not files:
                return []

            # 최신 파일에서 최근 k라인 읽기
            latest_file = files[-1]
            with open(latest_file, encoding="utf-8") as f:
                lines = f.readlines()[-k:]

            samples = []
            for line in lines:
                try:
                    event = json.loads(line.strip())
                    sample = {
                        "timestamp": event.get("timestamp", event.get("ts")),
                        "text_redacted": event.get("text_redacted", "***"),
                        "teacher_intent": (event.get("teacher") or {}).get("intent"),
                        "teacher_confidence": (event.get("teacher") or {}).get(
                            "confidence"
                        ),
                        "student_intent": (event.get("student") or {}).get("intent"),
                        "student_confidence": (event.get("student") or {}).get(
                            "confidence"
                        ),
                        "final_intent": (event.get("intent") or {}).get("intent_key"),
                        "agreement": event.get("agreement", True),
                    }
                    samples.append(sample)
                except json.JSONDecodeError:
                    continue

            return samples

        except Exception:
            return []

    def _ewma_latency(self, window_seconds: int) -> float:
        """Exponentially Weighted Moving Average 계산"""
        now = time.time()
        cutoff_time = now - window_seconds

        # 윈도우 내의 샘플만 필터링
        relevant_samples = []
        for timestamp, ttl_ms in self._ttl_samples_timeseries:
            if timestamp >= cutoff_time:
                age_seconds = now - timestamp
                relevant_samples.append((age_seconds, ttl_ms))

        if not relevant_samples:
            return 0.0

        # EWMA 계산 (tau = window / 2)
        tau = window_seconds / 2.0
        weighted_sum = 0.0
        weight_sum = 0.0

        for age, ttl in relevant_samples:
            # weight = exp(-age/tau)
            import math

            weight = math.exp(-age / tau)
            weighted_sum += ttl * weight
            weight_sum += weight

        return weighted_sum / weight_sum if weight_sum > 0 else 0.0

    def snapshot(self) -> Dict[str, Any]:
        """현재 메트릭 스냅샷 반환 (운영 확장 포함)"""
        with self._lock:
            # 평균 계산
            avg_ttl = (
                sum(self._ttl_samples) / len(self._ttl_samples)
                if self._ttl_samples
                else 0
            )
            avg_ttfb = (
                sum(self._ttfb_samples) / len(self._ttfb_samples)
                if self._ttfb_samples
                else 0
            )

            # 백분위수 계산
            p95_ttl = (
                self._percentile(self._ttl_samples, 0.95) if self._ttl_samples else 0
            )
            p99_ttl = (
                self._percentile(self._ttl_samples, 0.99) if self._ttl_samples else 0
            )

            # 비율 계산
            intent_agree_rate = self._intent_matches / max(1, self._total_requests)
            disagreement_rate = 1.0 - intent_agree_rate
            tool_success_rate = (
                self._tool_successes / max(1, self._tool_attempts)
                if self._tool_attempts > 0
                else 1.0
            )

            uptime = int(time.time() - self._start_time)

            return {
                # 기본 성능 메트릭 (기존 호환성)
                "count": self._total_requests,
                "avg_ttl_ms": int(avg_ttl),
                "intent_agree_rate": round(intent_agree_rate, 4),
                # 확장 운영 메트릭
                "disagreement_rate": round(disagreement_rate, 4),
                "tool_success_rate": round(tool_success_rate, 4),
                "student_f1_estimate": self._student_f1_estimate,
                "trace_samples": self._recent_trace_samples(5),
                # EWMA 지연 시간 메트릭 (스파이크 감지용)
                "ewma_latency_ms": {
                    "1m": round(self._ewma_latency(60), 2),
                    "5m": round(self._ewma_latency(300), 2),
                    "15m": round(self._ewma_latency(900), 2),
                },
                # 상세 성능 메트릭
                "performance": {
                    "avg_ttl_ms": int(avg_ttl),
                    "avg_ttfb_ms": int(avg_ttfb),
                    "p95_ttl_ms": int(p95_ttl),
                    "p99_ttl_ms": int(p99_ttl),
                    "samples": len(self._ttl_samples),
                },
                # 상세 품질 메트릭
                "quality": {
                    "intent_agree_rate": round(intent_agree_rate, 4),
                    "disagreement_rate": round(disagreement_rate, 4),
                    "tool_success_rate": round(tool_success_rate, 4),
                    "total_requests": self._total_requests,
                    "intent_matches": self._intent_matches,
                    "tool_successes": self._tool_successes,
                    "tool_attempts": self._tool_attempts,
                    "student_f1_estimate": self._student_f1_estimate,
                },
                # 시스템 메트릭
                "system": {
                    "uptime_seconds": uptime,
                    "error_count": len(self._errors),
                    "events_dir": self.events_dir,
                },
                # 최근 데이터
                "recent_errors": list(self._errors)[-5:] if self._errors else [],
                "recent_traces": self._recent_trace_samples(5),
            }

    def _percentile(self, samples: deque, percentile: float) -> float:
        """백분위수 계산"""
        if not samples:
            return 0.0

        sorted_samples = sorted(samples)
        index = int(len(sorted_samples) * percentile)
        return sorted_samples[min(index, len(sorted_samples) - 1)]

    def reset(self):
        """메트릭 초기화"""
        with self._lock:
            self._ttl_samples.clear()
            self._ttfb_samples.clear()
            self._intent_matches = 0
            self._total_requests = 0
            self._tool_successes = 0
            self._tool_attempts = 0
            self._errors.clear()
            self._start_time = time.time()

    def get_all_metrics(self) -> Dict[str, Any]:
        """모든 메트릭 반환 (snapshot의 별칭)"""
        return self.snapshot()

    def increment(self, counter_name: str):
        """카운터 증가"""
        with self._lock:
            if counter_name == "intent_agreement_rate":
                self._intent_matches += 1
            elif counter_name == "background_agreement_rate":
                # 백그라운드 agreement 추적 (별도 카운터가 필요하면 추가)
                pass
            elif counter_name == "background_disagreement_rate":
                # 백그라운드 disagreement 추적
                pass
            elif counter_name == "student_hotswap_success":
                # 핫스왑 성공 추적
                pass
            elif counter_name == "student_hotswap_failed":
                # 핫스왑 실패 추적
                pass
            # 추가 카운터들...

    def export_prometheus(self) -> str:
        """Prometheus text exposition format (v0)."""
        snap = self.snapshot()
        lines = []
        lines.append("# HELP echogpt_up EchoGPT process up indicator")
        lines.append("# TYPE echogpt_up gauge")
        lines.append("echogpt_up 1")

        lines.append("# HELP echogpt_requests_total Total handled requests")
        lines.append("# TYPE echogpt_requests_total counter")
        lines.append(f"echogpt_requests_total {snap.get('count', 0)}")

        lines.append("# HELP echogpt_avg_ttl_ms Average end-to-end latency (ms)")
        lines.append("# TYPE echogpt_avg_ttl_ms gauge")
        lines.append(f"echogpt_avg_ttl_ms {snap.get('avg_ttl_ms', 0)}")

        for k in ("intent_agree_rate", "disagreement_rate", "tool_success_rate"):
            lines.append(f"# HELP echogpt_{k} {k.replace('_',' ')}")
            lines.append("# TYPE echogpt_%s gauge" % k)
            v = snap.get(k)
            v = 0 if v is None else v
            lines.append(f"echogpt_{k} {v}")

        # Student F1 (optional)
        lines.append(
            "# HELP echogpt_student_f1_estimate Student classifier F1 estimate (macro)"
        )
        lines.append("# TYPE echogpt_student_f1_estimate gauge")
        f1 = snap.get("student_f1_estimate")
        lines.append(f"echogpt_student_f1_estimate {0 if f1 is None else f1}")

        # EWMA latency
        ewma = snap.get("ewma_latency_ms", {}) or {}
        lines.append("# HELP echogpt_ewma_latency_ms EWMA latency by window (ms)")
        lines.append("# TYPE echogpt_ewma_latency_ms gauge")
        for w in ("1m", "5m", "15m"):
            val = ewma.get(w, 0)
            lines.append(f'echogpt_ewma_latency_ms{{window="{w}"}} {val}')

        return "\n".join(lines) + "\n"
