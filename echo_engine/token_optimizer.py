#!/usr/bin/env python3
"""
🎯 Claude Code 토큰 효율화 시스템
VS Code 환경에서 Claude Code 사용 시 토큰 소비량을 최적화하는 시스템

핵심 기능:
1. 컨텍스트 압축 및 요약
2. 중복 요청 방지 (캐싱)
3. Echo IDE를 통한 지능적 요청 최적화
4. 토큰 사용량 모니터링 및 예측
5. 배치 처리를 통한 효율성 증대
"""

import json
import os
import hashlib
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import pickle
import zlib
from pathlib import Path


@dataclass
class TokenUsage:
    """토큰 사용량 추적"""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_estimate: float
    timestamp: str
    request_type: str
    context_compressed: bool = False
    cache_hit: bool = False


@dataclass
class OptimizationResult:
    """최적화 결과"""

    original_size: int
    optimized_size: int
    compression_ratio: float
    estimated_token_savings: int
    optimization_methods: List[str]


@dataclass
class ContextSnapshot:
    """컨텍스트 스냅샷"""

    content_hash: str
    compressed_content: bytes
    summary: str
    token_count: int
    created_at: str
    access_count: int = 0
    last_accessed: str = None


class TokenOptimizer:
    """🎯 Claude Code 토큰 최적화 엔진"""

    def __init__(self, cache_dir: str = ".echo_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # 캐시 파일들
        self.context_cache_file = self.cache_dir / "context_cache.pkl"
        self.token_log_file = self.cache_dir / "token_usage.jsonl"
        self.optimization_stats_file = self.cache_dir / "optimization_stats.json"

        # 인메모리 캐시
        self.context_cache: Dict[str, ContextSnapshot] = {}
        self.token_usage_history: List[TokenUsage] = []

        # 최적화 설정
        self.compression_threshold = 1000  # 1000자 이상일 때 압축
        self.cache_ttl = 3600  # 1시간 캐시 유효
        self.max_cache_size = 1000  # 최대 캐시 항목 수

        # 토큰 비용 (대략적인 GPT-4 기준)
        self.cost_per_1k_input_tokens = 0.03
        self.cost_per_1k_output_tokens = 0.06

        self._load_cache()
        self._load_token_history()

        print("🎯 Token Optimizer 초기화 완료")
        print(f"   캐시 디렉토리: {self.cache_dir}")
        print(f"   로드된 캐시 항목: {len(self.context_cache)}개")

    def _load_cache(self):
        """캐시 로드"""
        if self.context_cache_file.exists():
            try:
                with open(self.context_cache_file, "rb") as f:
                    self.context_cache = pickle.load(f)
                print(f"✅ 캐시 로드 완료: {len(self.context_cache)}개 항목")
            except Exception as e:
                print(f"⚠️ 캐시 로드 실패: {e}")
                self.context_cache = {}

    def _save_cache(self):
        """캐시 저장"""
        try:
            with open(self.context_cache_file, "wb") as f:
                pickle.dump(self.context_cache, f)
        except Exception as e:
            print(f"⚠️ 캐시 저장 실패: {e}")

    def _load_token_history(self):
        """토큰 사용 이력 로드"""
        if self.token_log_file.exists():
            try:
                with open(self.token_log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            self.token_usage_history.append(TokenUsage(**data))
                print(f"✅ 토큰 이력 로드: {len(self.token_usage_history)}개 기록")
            except Exception as e:
                print(f"⚠️ 토큰 이력 로드 실패: {e}")

    def _log_token_usage(self, usage: TokenUsage):
        """토큰 사용량 로깅"""
        try:
            with open(self.token_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(usage)) + "\n")
            self.token_usage_history.append(usage)
        except Exception as e:
            print(f"⚠️ 토큰 로깅 실패: {e}")

    def optimize_context(
        self, content: str, request_type: str = "general"
    ) -> OptimizationResult:
        """컨텍스트 최적화"""
        original_size = len(content)
        optimization_methods = []

        # 1. 캐시 확인
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        if content_hash in self.context_cache:
            cache_entry = self.context_cache[content_hash]
            cache_entry.access_count += 1
            cache_entry.last_accessed = datetime.now().isoformat()

            print(f"💾 캐시 히트: {cache_entry.summary[:50]}...")
            optimization_methods.append("cache_hit")

            return OptimizationResult(
                original_size=original_size,
                optimized_size=0,  # 캐시 히트이므로 새로운 토큰 소비 없음
                compression_ratio=1.0,
                estimated_token_savings=cache_entry.token_count,
                optimization_methods=optimization_methods,
            )

        optimized_content = content

        # 2. 중복 공백 제거
        import re

        optimized_content = re.sub(r"\s+", " ", optimized_content.strip())
        if len(optimized_content) < original_size:
            optimization_methods.append("whitespace_cleanup")

        # 3. 긴 컨텍스트 압축
        if len(optimized_content) > self.compression_threshold:
            summary = self._create_context_summary(optimized_content, request_type)
            compressed_data = zlib.compress(optimized_content.encode())

            # 캐시에 저장
            snapshot = ContextSnapshot(
                content_hash=content_hash,
                compressed_content=compressed_data,
                summary=summary,
                token_count=self._estimate_tokens(optimized_content),
                created_at=datetime.now().isoformat(),
            )

            self.context_cache[content_hash] = snapshot
            optimization_methods.append("content_compression")
            optimization_methods.append("summary_generation")

            # 요약본으로 대체
            optimized_content = summary

            # 캐시 크기 관리
            self._manage_cache_size()

        # 4. Echo IDE 특화 최적화
        if request_type in ["code_analysis", "refactoring", "debugging"]:
            optimized_content = self._apply_echo_ide_optimization(
                optimized_content, request_type
            )
            optimization_methods.append("echo_ide_optimization")

        optimized_size = len(optimized_content)
        compression_ratio = optimized_size / original_size if original_size > 0 else 1.0

        # 토큰 절약량 추정
        original_tokens = self._estimate_tokens(content)
        optimized_tokens = self._estimate_tokens(optimized_content)
        token_savings = original_tokens - optimized_tokens

        print(
            f"🎯 컨텍스트 최적화: {original_size} → {optimized_size} ({compression_ratio:.2%})"
        )
        print(f"   토큰 절약 예상: {token_savings}개")

        return OptimizationResult(
            original_size=original_size,
            optimized_size=optimized_size,
            compression_ratio=compression_ratio,
            estimated_token_savings=token_savings,
            optimization_methods=optimization_methods,
        )

    def _create_context_summary(self, content: str, request_type: str) -> str:
        """컨텍스트 요약 생성"""
        # 간단한 요약 로직 (실제로는 더 정교한 요약 AI 사용 가능)
        lines = content.split("\n")

        # 요청 타입별 요약 전략
        if request_type == "code_analysis":
            # 코드 분석용: 함수/클래스 시그니처 중심
            summary_lines = []
            for line in lines[:50]:  # 상위 50줄만
                if any(
                    keyword in line
                    for keyword in ["def ", "class ", "import ", "from "]
                ):
                    summary_lines.append(line.strip())
            return "\n".join(summary_lines) or lines[:10]

        elif request_type == "debugging":
            # 디버깅용: 에러 관련 부분 중심
            error_lines = []
            for i, line in enumerate(lines):
                if any(
                    keyword in line.lower()
                    for keyword in ["error", "exception", "traceback", "failed"]
                ):
                    # 에러 전후 컨텍스트 포함
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    error_lines.extend(lines[start:end])
            return "\n".join(error_lines[:30]) if error_lines else "\n".join(lines[:20])

        else:
            # 일반적인 요약: 시작과 끝 부분
            if len(lines) <= 20:
                return content
            return "\n".join(
                lines[:10] + ["...", f"[생략된 {len(lines)-20}줄]", "..."] + lines[-10:]
            )

    def _apply_echo_ide_optimization(self, content: str, request_type: str) -> str:
        """Echo IDE 특화 최적화"""
        if request_type == "code_analysis":
            # 코드 분석: 불필요한 주석과 공백 제거
            lines = content.split("\n")
            filtered_lines = []
            for line in lines:
                stripped = line.strip()
                # 단순 주석이나 빈 줄 제거 (중요한 docstring은 유지)
                if stripped and not (stripped.startswith("#") and len(stripped) < 50):
                    filtered_lines.append(line)
            return "\n".join(filtered_lines)

        elif request_type == "refactoring":
            # 리팩토링: 메소드와 클래스 시그니처에 집중
            import re

            important_patterns = [
                r"^\s*(def|class|import|from)",
                r".*(?:TODO|FIXME|BUG).*",
                r".*(?:raise|except|finally).*",
            ]

            lines = content.split("\n")
            important_lines = []
            for line in lines:
                if any(
                    re.match(pattern, line, re.IGNORECASE)
                    for pattern in important_patterns
                ):
                    important_lines.append(line)

            return "\n".join(important_lines) if important_lines else content

        return content

    def _estimate_tokens(self, text: str) -> int:
        """토큰 수 추정 (대략적)"""
        # 간단한 토큰 추정: 단어 수 * 1.3 (평균적으로 1 word ≈ 1.3 tokens)
        words = len(text.split())
        return int(words * 1.3)

    def _manage_cache_size(self):
        """캐시 크기 관리"""
        if len(self.context_cache) <= self.max_cache_size:
            return

        # 오래되고 적게 사용된 항목부터 제거
        cache_items = list(self.context_cache.items())
        cache_items.sort(key=lambda x: (x[1].access_count, x[1].created_at))

        # 상위 20% 제거
        remove_count = len(cache_items) // 5
        for i in range(remove_count):
            hash_key, _ = cache_items[i]
            del self.context_cache[hash_key]

        print(f"🧹 캐시 정리: {remove_count}개 항목 제거")
        self._save_cache()

    def track_token_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        request_type: str = "general",
        cache_hit: bool = False,
        context_compressed: bool = False,
    ):
        """토큰 사용량 추적"""
        total_tokens = input_tokens + output_tokens
        cost_estimate = (
            input_tokens / 1000 * self.cost_per_1k_input_tokens
            + output_tokens / 1000 * self.cost_per_1k_output_tokens
        )

        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_estimate=cost_estimate,
            timestamp=datetime.now().isoformat(),
            request_type=request_type,
            context_compressed=context_compressed,
            cache_hit=cache_hit,
        )

        self._log_token_usage(usage)
        print(f"📊 토큰 사용: {total_tokens}개 (${cost_estimate:.4f})")

    def get_optimization_stats(self) -> Dict[str, Any]:
        """최적화 통계 반환"""
        if not self.token_usage_history:
            return {"message": "토큰 사용 이력이 없습니다."}

        total_tokens = sum(usage.total_tokens for usage in self.token_usage_history)
        total_cost = sum(usage.cost_estimate for usage in self.token_usage_history)
        cache_hits = sum(1 for usage in self.token_usage_history if usage.cache_hit)
        compressed_requests = sum(
            1 for usage in self.token_usage_history if usage.context_compressed
        )

        # 요청 타입별 통계
        by_type = defaultdict(list)
        for usage in self.token_usage_history:
            by_type[usage.request_type].append(usage)

        type_stats = {}
        for req_type, usages in by_type.items():
            type_stats[req_type] = {
                "count": len(usages),
                "total_tokens": sum(u.total_tokens for u in usages),
                "avg_tokens": sum(u.total_tokens for u in usages) / len(usages),
                "total_cost": sum(u.cost_estimate for u in usages),
            }

        return {
            "summary": {
                "total_requests": len(self.token_usage_history),
                "total_tokens_used": total_tokens,
                "total_cost_estimate": total_cost,
                "average_tokens_per_request": total_tokens
                / len(self.token_usage_history),
                "cache_hit_rate": (
                    cache_hits / len(self.token_usage_history)
                    if self.token_usage_history
                    else 0
                ),
                "compression_rate": (
                    compressed_requests / len(self.token_usage_history)
                    if self.token_usage_history
                    else 0
                ),
            },
            "by_request_type": type_stats,
            "cache_stats": {
                "cache_size": len(self.context_cache),
                "cache_hits": cache_hits,
                "most_accessed": sorted(
                    self.context_cache.values(),
                    key=lambda x: x.access_count,
                    reverse=True,
                )[:5],
            },
            "recent_activity": [
                asdict(usage) for usage in self.token_usage_history[-10:]
            ],
        }

    def suggest_optimizations(self) -> List[str]:
        """최적화 제안"""
        suggestions = []
        stats = self.get_optimization_stats()

        if not stats.get("summary"):
            return ["더 많은 사용 데이터가 필요합니다."]

        summary = stats["summary"]

        # 캐시 히트율이 낮은 경우
        if summary["cache_hit_rate"] < 0.3:
            suggestions.append(
                "🔄 반복적인 요청이 많습니다. 캐시 활용도를 높이기 위해 유사한 요청들을 배치 처리해보세요."
            )

        # 압축율이 낮은 경우
        if summary["compression_rate"] < 0.2:
            suggestions.append(
                "📦 긴 컨텍스트 압축률이 낮습니다. Echo IDE의 요약 기능을 더 적극적으로 활용해보세요."
            )

        # 토큰 사용량이 높은 경우
        avg_tokens = summary["average_tokens_per_request"]
        if avg_tokens > 2000:
            suggestions.append(
                f"⚡ 평균 토큰 사용량이 높습니다 ({avg_tokens:.0f}개). 요청을 더 작은 단위로 분할해보세요."
            )

        # 비용 관련 제안
        if summary["total_cost_estimate"] > 10:
            suggestions.append(
                f"💰 누적 비용이 ${summary['total_cost_estimate']:.2f}입니다. 정기적인 캐시 정리와 배치 처리를 고려해보세요."
            )

        # Echo IDE 특화 제안
        code_requests = stats.get("by_request_type", {}).get("code_analysis", {})
        if code_requests.get("count", 0) > 10:
            suggestions.append(
                "🔧 코드 분석 요청이 많습니다. Echo IDE의 스마트 컨텍스트 필터링을 활성화해보세요."
            )

        return suggestions or ["✅ 현재 최적화 상태가 양호합니다!"]


# 편의 함수들
_global_optimizer = None


def get_token_optimizer() -> TokenOptimizer:
    """전역 토큰 옵티마이저 인스턴스"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = TokenOptimizer()
    return _global_optimizer


def optimize_for_claude_code(
    content: str, request_type: str = "general"
) -> Tuple[str, OptimizationResult]:
    """Claude Code용 컨텍스트 최적화"""
    optimizer = get_token_optimizer()
    result = optimizer.optimize_context(content, request_type)

    if "cache_hit" in result.optimization_methods:
        # 캐시 히트인 경우, 캐시된 요약 반환
        hash_key = hashlib.sha256(content.encode()).hexdigest()
        cached_summary = optimizer.context_cache[hash_key].summary
        return cached_summary, result
    elif result.compression_ratio < 0.8:  # 20% 이상 압축된 경우
        # 압축된 컨텐츠는 이미 result에 반영됨
        return content[: result.optimized_size], result
    else:
        return content, result


if __name__ == "__main__":
    # 테스트
    print("🧪 Token Optimizer 테스트")

    optimizer = TokenOptimizer()

    # 테스트 컨텍스트
    test_content = (
        """
    def complex_function():
        # 이것은 복잡한 함수입니다
        data = []
        for i in range(100):
            if i % 2 == 0:
                data.append(i * 2)
        return data

    class MyClass:
        def __init__(self):
            self.value = 42

        def process(self):
            return self.value * 2
    """
        * 10
    )  # 긴 컨텍스트 시뮬레이션

    # 최적화 테스트
    result = optimizer.optimize_context(test_content, "code_analysis")
    print(f"\n📊 최적화 결과:")
    print(f"   원본 크기: {result.original_size}")
    print(f"   최적화 크기: {result.optimized_size}")
    print(f"   압축률: {result.compression_ratio:.1%}")
    print(f"   토큰 절약: {result.estimated_token_savings}개")
    print(f"   최적화 방법: {', '.join(result.optimization_methods)}")

    # 통계 확인
    stats = optimizer.get_optimization_stats()
    print(f"\n📈 최적화 통계: {stats}")

    # 제안사항
    suggestions = optimizer.suggest_optimizations()
    print(f"\n💡 최적화 제안:")
    for suggestion in suggestions:
        print(f"   {suggestion}")

    print("\n✅ Token Optimizer 테스트 완료")
