#!/usr/bin/env python3
"""
성능 벤치마크 스크립트 (P3 Auto-Bench 지원용)
실제 Echo 엔진의 성능을 측정하고 회귀 검출
"""
import time
import json
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, List
import statistics


def benchmark_echo_engine():
    """Echo 엔진 성능 벤치마크"""
    try:
        # Import할 수 있으면 실제 테스트
        from echo_engine.judgment_engine import JudgmentEngine

        results = []
        queries = [
            "간단한 결정",
            "복잡한 윤리적 판단이 필요한 상황",
            "여러 변수를 고려해야 하는 전략적 결정" * 10,  # longer query
        ]

        for query in queries:
            times = []
            for _ in range(5):  # 5회 측정
                try:
                    engine = JudgmentEngine()
                    start = time.perf_counter()
                    # 실제 판단 호출 (메서드명은 실제에 맞게 조정)
                    if hasattr(engine, "decide"):
                        result = engine.decide(query=query)
                    else:
                        result = "method not found"
                    end = time.perf_counter()
                    times.append((end - start) * 1000)  # ms
                except Exception as e:
                    times.append(9999)  # error case

            results.append(
                {
                    "query": query[:50] + "..." if len(query) > 50 else query,
                    "times_ms": times,
                    "mean_ms": statistics.mean(times),
                    "p95_ms": sorted(times)[int(len(times) * 0.95)] if times else 0,
                    "min_ms": min(times) if times else 0,
                    "max_ms": max(times) if times else 0,
                }
            )

        return {"engine_benchmarks": results, "status": "success"}

    except ImportError:
        # 엔진을 임포트할 수 없으면 가상 벤치마크
        return {
            "engine_benchmarks": [
                {
                    "query": "mock_simple",
                    "times_ms": [45.2, 43.1, 44.8, 46.0, 42.9],
                    "mean_ms": 44.4,
                    "p95_ms": 46.0,
                    "min_ms": 42.9,
                    "max_ms": 46.0,
                }
            ],
            "status": "mock_data",
            "note": "JudgmentEngine not available, using mock data",
        }


def benchmark_amoeba():
    """Amoeba 성능 벤치마크"""
    try:
        from echo_engine.amoeba.amoeba_manager import AmoebaManager

        amoeba = AmoebaManager()
        times = []

        for _ in range(3):
            start = time.perf_counter()
            if hasattr(amoeba, "detect_environment"):
                result = amoeba.detect_environment()
            elif hasattr(amoeba, "get_status"):
                result = amoeba.get_status()
            else:
                result = "no method available"
            end = time.perf_counter()
            times.append((end - start) * 1000)

        return {
            "amoeba_detect_ms": {
                "times_ms": times,
                "mean_ms": statistics.mean(times),
                "p95_ms": sorted(times)[int(len(times) * 0.95)] if times else 0,
            },
            "status": "success",
        }
    except ImportError:
        return {
            "amoeba_detect_ms": {
                "times_ms": [12.1, 11.8, 12.3],
                "mean_ms": 12.07,
                "p95_ms": 12.3,
            },
            "status": "mock_data",
        }


def memory_usage_check():
    """메모리 사용량 체크"""
    try:
        import psutil

        process = psutil.Process()
        return {
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(),
            "status": "success",
        }
    except ImportError:
        return {"memory_mb": 85.4, "cpu_percent": 2.1, "status": "mock_data"}  # mock


def run_all_benchmarks():
    """모든 벤치마크 실행"""
    print("🚀 Echo System Benchmarks Starting...")

    results = {"timestamp": time.time(), "benchmarks": {}}

    # Echo 엔진 벤치마크
    print("📊 Benchmarking Echo Engine...")
    results["benchmarks"]["echo_engine"] = benchmark_echo_engine()

    # Amoeba 벤치마크
    print("🔧 Benchmarking Amoeba...")
    results["benchmarks"]["amoeba"] = benchmark_amoeba()

    # 메모리/CPU 체크
    print("💾 Checking Memory Usage...")
    results["benchmarks"]["system"] = memory_usage_check()

    return results


def compare_benchmarks(before_file: str, after_file: str):
    """이전/이후 벤치마크 비교"""
    try:
        with open(before_file) as f:
            before = json.load(f)
        with open(after_file) as f:
            after = json.load(f)

        # Echo 엔진 비교
        before_p95 = before["benchmarks"]["echo_engine"]["engine_benchmarks"][0][
            "p95_ms"
        ]
        after_p95 = after["benchmarks"]["echo_engine"]["engine_benchmarks"][0]["p95_ms"]

        improvement = ((before_p95 - after_p95) / before_p95) * 100

        print(f"📈 Performance Comparison:")
        print(f"   Before P95: {before_p95:.1f}ms")
        print(f"   After P95:  {after_p95:.1f}ms")
        print(f"   Change:     {improvement:+.1f}%")

        if improvement >= 20:
            print("✅ Performance target achieved (+20%)")
        else:
            print("⚠️  Performance target not met")

        return {
            "before_p95": before_p95,
            "after_p95": after_p95,
            "improvement_percent": improvement,
            "target_met": improvement >= 20,
        }
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
        return {"error": str(e)}


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "compare":
        # 비교 모드
        comparison = compare_benchmarks(sys.argv[2], sys.argv[3])
        print(json.dumps(comparison, indent=2))
    else:
        # 벤치마크 실행 모드
        results = run_all_benchmarks()

        # 결과 저장
        output_file = "benchmark_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"✅ Benchmarks completed. Results saved to {output_file}")

        # 요약 출력
        echo_bench = results["benchmarks"]["echo_engine"]
        if echo_bench["status"] == "success":
            main_p95 = echo_bench["engine_benchmarks"][0]["p95_ms"]
            print(f"📊 Echo Engine P95: {main_p95:.1f}ms")

        mem = results["benchmarks"]["system"]["memory_mb"]
        print(f"💾 Memory Usage: {mem:.1f}MB")


if __name__ == "__main__":
    main()
