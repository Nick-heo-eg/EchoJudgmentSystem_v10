"""
Asset Classifier - 자산 분류 결정
==============================

T/S/P 점수를 기반으로 dormant/pending/junk 분류
"""

from typing import Tuple, List, Dict, Any
from echo_engine.inspectors.asset_value_judger.schemas import AssetMetrics, AssetStatus


def classify_asset(
    file_path: str,
    metrics: AssetMetrics,
    t_score: float,
    s_score: float,
    p_score: float,
    total_score: float,
    registry: Dict[str, Any],
) -> Tuple[AssetStatus, str, List[str]]:
    """
    자산 분류 결정

    Args:
        file_path: 파일 경로
        metrics: 수집된 메트릭
        t_score: Technical Value 점수
        s_score: Strategic Value 점수
        p_score: Potential Value 점수
        total_score: 총 점수
        registry: 자산 레지스트리 설정

    Returns:
        Tuple[상태, 이유, 권장액션들]
    """

    # 1단계: 레지스트리 오버라이드 확인
    registry_result = _check_registry_override(file_path, registry)
    if registry_result:
        return registry_result

    # 2단계: 보호 패턴 확인
    protection_result = _check_protection_patterns(file_path, registry)
    if protection_result:
        return protection_result

    # 3단계: T/S/P 점수 기반 분류
    score_result = _classify_by_scores(
        file_path, metrics, t_score, s_score, p_score, total_score, registry
    )
    if score_result:
        return score_result

    # 4단계: 메트릭 기반 추가 규칙
    metrics_result = _classify_by_metrics(file_path, metrics)
    if metrics_result:
        return metrics_result

    # 기본: pending 상태
    return (
        AssetStatus.PENDING,
        "needs manual review - scores in middle range",
        [
            "📋 Manual review required",
            "🔍 Consider usage patterns",
            "⚖️ Evaluate strategic importance",
        ],
    )


def _check_registry_override(
    file_path: str, registry: Dict[str, Any]
) -> Tuple[AssetStatus, str, List[str]]:
    """레지스트리 강제 분류 확인"""

    # 강제 dormant 지정
    force_dormant = registry.get("force_dormant", [])
    for pattern in force_dormant:
        if _match_pattern(file_path, pattern):
            return (
                AssetStatus.SLEEPING_VALUABLE,
                f"registry override: force valuable ({pattern})",
                [
                    "🔒 Protected by registry",
                    "🌟 High strategic value confirmed",
                    "📈 Monitor for reactivation opportunity",
                ],
            )

    # 강제 junk 지정 (위험하므로 신중히 사용)
    force_junk = registry.get("force_junk", [])
    for pattern in force_junk:
        if _match_pattern(file_path, pattern):
            return (
                AssetStatus.DEPRECATED,
                f"registry override: force deprecated ({pattern})",
                [
                    "⚠️ Marked for cleanup",
                    "🗑️ Safe to remove",
                    "📋 Document removal reason",
                ],
            )

    return None


def _check_protection_patterns(
    file_path: str, registry: Dict[str, Any]
) -> Tuple[AssetStatus, str, List[str]]:
    """보호 패턴 확인"""

    protected_patterns = registry.get("protected_patterns", [])

    for pattern in protected_patterns:
        if _match_pattern(file_path, pattern):
            return (
                AssetStatus.ACTIVE,
                f"protected pattern match ({pattern})",
                ["🛡️ Protected asset", "🔒 Do not remove", "📊 Monitor usage patterns"],
            )

    # 기본 보호 패턴들
    critical_patterns = [
        "*/__init__.py",
        "*/seed_kernel.py",
        "*/judgment_engine.py",
        "*/core.py",
        "*/main.py",
    ]

    for pattern in critical_patterns:
        if _match_pattern(file_path, pattern):
            return (
                AssetStatus.ACTIVE,
                f"critical system file ({pattern})",
                [
                    "🚨 Critical system component",
                    "🔒 Never remove",
                    "⚡ Essential for system operation",
                ],
            )

    return None


def _classify_by_scores(
    file_path: str,
    metrics: AssetMetrics,
    t_score: float,
    s_score: float,
    p_score: float,
    total_score: float,
    registry: Dict[str, Any],
) -> Tuple[AssetStatus, str, List[str]]:
    """실용적 활용도 기반 분류"""

    # 활용도 지표 계산
    usage_score = _calculate_usage_score(metrics)
    value_score = total_score

    # 1. ACTIVE - 현재 활발히 사용중
    if _is_actively_used(metrics, usage_score):
        return (
            AssetStatus.ACTIVE,
            f"actively used (usage: {usage_score:.1f}, value: {value_score:.1f})",
            ["⚡ Keep using", "📊 Monitor performance", "🔄 Regular maintenance"],
        )

    # 2. SLEEPING_VALUABLE - 미활용이지만 가치있음
    if _is_sleeping_valuable(metrics, value_score, usage_score):
        return (
            AssetStatus.SLEEPING_VALUABLE,
            f"high value but underused (value: {value_score:.1f}, usage: {usage_score:.1f})",
            [
                "🌟 Consider reactivation",
                "🔍 Find usage opportunities",
                "📈 Promote to active use",
            ],
        )

    # 3. DEPRECATED - 폐기 예정/정리 대상
    if _is_deprecated(metrics, value_score, usage_score):
        return (
            AssetStatus.DEPRECATED,
            f"low value and unused (value: {value_score:.1f}, usage: {usage_score:.1f})",
            ["🗑️ Safe to remove", "📦 Archive first", "🔍 Check dependencies"],
        )

    # 4. DORMANT - 활용되지 않음 (검토 필요)
    return (
        AssetStatus.DORMANT,
        f"needs review (value: {value_score:.1f}, usage: {usage_score:.1f})",
        ["🤔 Manual review needed", "⚖️ Evaluate potential", "📋 Consider future plans"],
    )


def _calculate_usage_score(metrics: AssetMetrics) -> float:
    """활용도 점수 계산 (0-100)"""
    score = 0

    # 의존성 기반 사용도 (가장 중요한 지표)
    if metrics.deps_in > 0:
        score += min(metrics.deps_in * 12, 35)

    # 브릿지 호출 여부 (실제 사용의 강력한 지표)
    if metrics.bridge_called:
        score += 30

    # 테스트 커버리지 (관리되고 있다는 지표)
    if metrics.covered:
        score += 10

    # 최근 수정 여부 (활발한 개발 지표)
    if metrics.last_modified_days <= 30:
        score += 15
    elif metrics.last_modified_days <= 90:
        score += 8
    elif metrics.last_modified_days > 180:
        score -= 5  # 오래 방치된 경우 감점

    # import 빈도 (실제 사용 빈도)
    if hasattr(metrics, "import_frequency") and metrics.import_frequency > 0:
        score += min(metrics.import_frequency * 1.5, 12)

    # 실행 빈도 (실제 실행 여부)
    if hasattr(metrics, "execution_frequency") and metrics.execution_frequency > 0:
        score += min(metrics.execution_frequency * 2, 15)

    # 최근 커밋 (지속적 관리 지표)
    if hasattr(metrics, "recent_commits") and metrics.recent_commits > 0:
        score += min(metrics.recent_commits * 3, 10)

    return max(0, min(score, 100))


def _is_actively_used(metrics: AssetMetrics, usage_score: float) -> bool:
    """현재 활발히 사용중인지 판단"""
    # 높은 활용도 (임계값 상향 조정)
    if usage_score >= 70:
        return True

    # 브릿지 호출은 강력한 활용 지표
    if metrics.bridge_called:
        return True

    # 최근 활동 + 여러 의존성
    if metrics.last_modified_days <= 30 and metrics.deps_in >= 3:
        return True

    # 높은 import/execution 빈도
    import_freq = getattr(metrics, "import_frequency", 0)
    exec_freq = getattr(metrics, "execution_frequency", 0)
    if import_freq >= 8 and exec_freq >= 10:
        return True

    return False


def _is_sleeping_valuable(
    metrics: AssetMetrics, value_score: float, usage_score: float
) -> bool:
    """미활용이지만 가치있는지 판단"""
    # 높은 가치 + 낮은 활용도
    if value_score >= 70 and usage_score < 40:
        return True

    # Echo 핵심 컴포넌트지만 미활용
    if (metrics.has_signature_link or metrics.has_judgment_link) and usage_score < 30:
        return True

    # 로드맵 매칭 + 미활용
    if (
        metrics.roadmap_matched
        and metrics.roadmap_priority in ["high", "medium"]
        and usage_score < 35
    ):
        return True

    # 복잡하고 고유한 코드지만 미활용
    if metrics.complexity >= 10 and metrics.unique_patterns >= 2 and usage_score < 25:
        return True

    return False


def _is_deprecated(
    metrics: AssetMetrics, value_score: float, usage_score: float
) -> bool:
    """폐기 대상인지 판단"""
    # 낮은 가치 + 낮은 활용도
    if value_score < 30 and usage_score < 20:
        return True

    # 오래된 + 의존성 없음 + 커버리지 없음
    if (
        metrics.last_modified_days > 365
        and metrics.deps_in == 0
        and not metrics.covered
        and not metrics.bridge_called
    ):
        return True

    # 많은 사용되지 않는 함수
    if metrics.unused_functions > 5 and usage_score < 15:
        return True

    return False


def _classify_by_metrics(
    file_path: str, metrics: AssetMetrics
) -> Tuple[AssetStatus, str, List[str]]:
    """메트릭 기반 추가 분류 규칙"""

    # 브릿지에서 활발히 사용 중이면 dormant
    if metrics.bridge_called and getattr(metrics, "call_frequency", 0) > 10:
        return (
            AssetStatus.DORMANT,
            "actively used by bridge system",
            [
                "🌉 Bridge integration active",
                "⚡ High usage frequency",
                "📈 Monitor performance",
            ],
        )

    # 최근 활발히 수정되고 커버리지 있으면 dormant
    if metrics.last_modified_days <= 30 and metrics.covered:
        return (
            AssetStatus.DORMANT,
            "recently active with test coverage",
            ["🔥 Recently active", "✅ Well tested", "🚀 Ready for use"],
        )

    # 아무도 의존하지 않고 오래된 파일은 junk 후보
    if (
        metrics.deps_in == 0
        and metrics.last_modified_days > 365
        and not metrics.covered
        and not metrics.bridge_called
    ):

        return (
            AssetStatus.JUNK,
            "isolated + stale + untested + unused",
            [
                "🕸️ Appears abandoned",
                "🗑️ Safe removal candidate",
                "📦 Archive before deletion",
            ],
        )

    # 테스트 파일 특별 처리
    if _is_test_file(file_path):
        if metrics.last_modified_days > 180 and not metrics.covered:
            return (
                AssetStatus.JUNK,
                "stale test file with no coverage",
                [
                    "🧪 Outdated test",
                    "🗑️ Safe to remove",
                    "📋 Check if functionality still exists",
                ],
            )

    return None


def _create_dormant_result(
    reason: str, score: float
) -> Tuple[AssetStatus, str, List[str]]:
    """Dormant 결과 생성"""
    return (
        AssetStatus.DORMANT,
        f"{reason} (score: {score:.1f})",
        [
            "🌟 High value asset",
            "🔄 Consider reactivation",
            "📊 Monitor for usage opportunities",
        ],
    )


def _match_pattern(file_path: str, pattern: str) -> bool:
    """패턴 매칭 (간단한 와일드카드 지원)"""
    import fnmatch

    return fnmatch.fnmatch(file_path, pattern)


def _is_test_file(file_path: str) -> bool:
    """테스트 파일인지 확인"""
    path_lower = file_path.lower()
    return (
        path_lower.startswith("test_")
        or "_test.py" in path_lower
        or "/test" in path_lower
        or "tests/" in path_lower
    )


def get_classification_summary(
    classifications: List[Tuple[str, AssetStatus, str, List[str]]],
) -> Dict[str, Any]:
    """분류 결과 요약"""

    status_counts = {status.value: 0 for status in AssetStatus}
    total_files = len(classifications)

    dormant_files = []
    junk_files = []
    pending_files = []

    for file_path, status, reason, actions in classifications:
        status_counts[status.value] += 1

        if status == AssetStatus.DORMANT:
            dormant_files.append({"path": file_path, "reason": reason})
        elif status == AssetStatus.JUNK:
            junk_files.append({"path": file_path, "reason": reason})
        else:
            pending_files.append({"path": file_path, "reason": reason})

    return {
        "total_files": total_files,
        "status_counts": status_counts,
        "dormant_percentage": (
            (status_counts["dormant"] / total_files * 100) if total_files > 0 else 0
        ),
        "junk_percentage": (
            (status_counts["junk"] / total_files * 100) if total_files > 0 else 0
        ),
        "top_dormant": dormant_files[:10],  # 상위 10개
        "junk_candidates": junk_files[:10],  # 정리 후보 10개
        "review_needed": pending_files[:5],  # 검토 필요 5개
    }


# 테스트용
if __name__ == "__main__":
    from echo_engine.inspectors.asset_value_judger.schemas import (
        AssetMetrics,
        AssetStatus,
    )

    # 샘플 테스트
    sample_metrics = AssetMetrics(
        loc=50,
        complexity=3,
        deps_in=0,
        deps_out=1,
        last_modified_days=200,
        covered=False,
        bridge_called=False,
        has_signature_link=False,
        has_judgment_link=False,
        roadmap_matched=False,
        roadmap_priority="low",
        unique_patterns=0,
        unused_functions=2,
    )

    sample_registry = {
        "thresholds": {"dormant": 80, "pending": 50},
        "protected_patterns": ["*/core.py", "*/__init__.py"],
        "force_dormant": ["*/signature_mapper.py"],
    }

    status, reason, actions = classify_asset(
        "old_utils/helper.py",
        sample_metrics,
        30.0,  # t_score
        20.0,  # s_score
        25.0,  # p_score
        25.0,  # total_score
        sample_registry,
    )

    print("🧪 Classifier Test")
    print(f"Status: {status.value}")
    print(f"Reason: {reason}")
    print(f"Actions: {actions}")

    # 보호된 파일 테스트
    status2, reason2, actions2 = classify_asset(
        "echo_engine/core.py", sample_metrics, 30.0, 20.0, 25.0, 25.0, sample_registry
    )

    print(f"\nProtected file test:")
    print(f"Status: {status2.value}")
    print(f"Reason: {reason2}")
