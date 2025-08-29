"""
Score Model - T/S/P 점수 계산 엔진
===============================

Technical, Strategic, Potential 가치 점수 계산
"""

from typing import Tuple, Dict, Any
from echo_engine.inspectors.asset_value_judger.schemas import AssetMetrics


def compute_tsp_scores(
    file_path: str, metrics: AssetMetrics, weights: Dict[str, Any]
) -> Tuple[float, float, float, float]:
    """
    T/S/P 점수 계산

    Args:
        file_path: 파일 경로
        metrics: 수집된 메트릭
        weights: 가중치 설정

    Returns:
        Tuple[T점수, S점수, P점수, 총점]
    """

    # T (Technical Value) 계산
    t_score = _compute_technical_score(file_path, metrics, weights.get("T", {}))

    # S (Strategic Value) 계산
    s_score = _compute_strategic_score(file_path, metrics, weights.get("S", {}))

    # P (Potential Value) 계산
    p_score = _compute_potential_score(file_path, metrics, weights.get("P", {}))

    # 총점 계산 (가중 평균)
    total_weights = weights.get("total_weights", {"T": 0.4, "S": 0.4, "P": 0.2})
    total_score = (
        t_score * total_weights.get("T", 0.4)
        + s_score * total_weights.get("S", 0.4)
        + p_score * total_weights.get("P", 0.2)
    )

    return t_score, s_score, p_score, total_score


def _compute_technical_score(
    file_path: str, metrics: AssetMetrics, weights: Dict[str, float]
) -> float:
    """
    Technical Value (기술적 가치) 계산
    - 고유성: 다른 코드와 중복되지 않는 정도
    - 재현 난이도: 다시 만들기 어려운 정도
    - 복잡도 가치: 의미 있는 복잡한 구현
    - 의존성 영향도: 다른 모듈들이 의존하는 정도
    """

    # 기본 가중치
    w = {
        "uniqueness": weights.get("uniqueness", 0.3),
        "rebuild_cost": weights.get("rebuild_cost", 0.3),
        "complexity": weights.get("complexity", 0.2),
        "dependency": weights.get("dependency", 0.2),
    }

    # 1. 고유성 점수 (0-100)
    uniqueness_score = _calculate_uniqueness(file_path, metrics)

    # 2. 재현 난이도 점수 (0-100)
    rebuild_cost_score = _calculate_rebuild_cost(file_path, metrics)

    # 3. 복잡도 가치 점수 (0-100)
    complexity_score = _calculate_complexity_value(metrics)

    # 4. 의존성 영향도 점수 (0-100)
    dependency_score = _calculate_dependency_impact(metrics)

    # 가중 평균 계산
    total_score = (
        uniqueness_score * w["uniqueness"]
        + rebuild_cost_score * w["rebuild_cost"]
        + complexity_score * w["complexity"]
        + dependency_score * w["dependency"]
    )

    return min(max(total_score, 0), 100)


def _compute_strategic_score(
    file_path: str, metrics: AssetMetrics, weights: Dict[str, float]
) -> float:
    """
    Strategic Value (전략적 가치) 계산
    - Echo 철학 적합성: Echo 시스템 철학과의 부합도
    - 로드맵 매칭: 향후 계획과의 연관성
    - 경쟁력 차별점: 다른 시스템과의 차별화
    """

    # 기본 가중치
    w = {
        "philosophy": weights.get("philosophy", 0.4),
        "roadmap": weights.get("roadmap", 0.4),
        "edge": weights.get("edge", 0.2),
    }

    # 1. Echo 철학 적합성 (0-100)
    philosophy_score = _calculate_echo_philosophy_fit(file_path, metrics)

    # 2. 로드맵 매칭 점수 (0-100)
    roadmap_score = _calculate_roadmap_match(metrics)

    # 3. 경쟁력 차별점 (0-100)
    edge_score = _calculate_competitive_edge(file_path, metrics)

    # 가중 평균 계산
    total_score = (
        philosophy_score * w["philosophy"]
        + roadmap_score * w["roadmap"]
        + edge_score * w["edge"]
    )

    return min(max(total_score, 0), 100)


def _compute_potential_score(
    file_path: str, metrics: AssetMetrics, weights: Dict[str, float]
) -> float:
    """
    Potential Value (활용 잠재력) 계산
    - 브릿지 연결 가능성: 쉽게 외부 연결 가능한 정도
    - 도메인 재사용성: 다른 분야에서 활용 가능성
    - 활성화 용이성: 데이터나 UI만 붙이면 바로 사용 가능
    """

    # 기본 가중치
    w = {
        "bridge": weights.get("bridge", 0.4),
        "reuse": weights.get("reuse", 0.3),
        "activation": weights.get("activation", 0.3),
    }

    # 1. 브릿지 연결 준비도 (0-100)
    bridge_score = _calculate_bridge_readiness(file_path, metrics)

    # 2. 도메인 재사용성 (0-100)
    reuse_score = _calculate_cross_domain_reuse(file_path, metrics)

    # 3. 활성화 용이성 (0-100)
    activation_score = _calculate_activation_ease(metrics)

    # 가중 평균 계산
    total_score = (
        bridge_score * w["bridge"]
        + reuse_score * w["reuse"]
        + activation_score * w["activation"]
    )

    return min(max(total_score, 0), 100)


# Technical Score 세부 계산 함수들


def _calculate_uniqueness(file_path: str, metrics: AssetMetrics) -> float:
    """고유성 계산"""
    score = 50  # 기본 점수

    # 고유 패턴이 많을수록 점수 증가
    if metrics.unique_patterns > 0:
        score += min(metrics.unique_patterns * 10, 30)

    # 일반적인 유틸리티나 테스트 파일은 고유성 낮음
    if any(
        keyword in file_path.lower() for keyword in ["util", "helper", "test", "common"]
    ):
        score -= 20

    # Echo 특화 구조면 고유성 높음
    if any(
        keyword in file_path.lower()
        for keyword in ["signature", "judgment", "quantum", "liminal"]
    ):
        score += 20

    return min(max(score, 0), 100)


def _calculate_rebuild_cost(file_path: str, metrics: AssetMetrics) -> float:
    """재현 난이도 계산"""
    score = 30  # 기본 점수

    # LOC에 따른 점수 (너무 작거나 너무 크면 감점)
    if 50 <= metrics.loc <= 500:
        score += 20
    elif metrics.loc > 500:
        score += 30  # 큰 파일은 재현 비용 높음

    # 복잡도에 따른 점수
    if metrics.complexity > 10:
        score += min(metrics.complexity * 2, 30)

    # 의존성이 복잡할수록 재현 어려움
    if metrics.deps_out > 5:
        score += min(metrics.deps_out * 3, 20)

    return min(max(score, 0), 100)


def _calculate_complexity_value(metrics: AssetMetrics) -> float:
    """복잡도 가치 계산"""
    score = 20  # 기본 점수

    # 적절한 복잡도는 가치 있음
    if 5 <= metrics.complexity <= 25:
        score += 40
    elif metrics.complexity > 25:
        score += 30  # 높은 복잡도도 가치 있지만 유지보수 부담

    # 함수가 너무 많으면 응집도 문제로 감점
    function_count = getattr(metrics, "function_count", 0)
    if function_count > 20:
        score -= 15

    # 사용되지 않는 함수가 많으면 감점
    if metrics.unused_functions > 3:
        score -= metrics.unused_functions * 5

    return min(max(score, 0), 100)


def _calculate_dependency_impact(metrics: AssetMetrics) -> float:
    """의존성 영향도 계산"""
    score = 10  # 기본 점수

    # 다른 모듈들이 이 파일에 의존할수록 중요
    if metrics.deps_in > 0:
        score += min(metrics.deps_in * 15, 60)

    # 하지만 너무 많이 의존받으면 결합도 문제
    if metrics.deps_in > 10:
        score -= 10

    # 아무도 의존하지 않으면 고립된 코드
    if metrics.deps_in == 0:
        score = 5

    return min(max(score, 0), 100)


# Strategic Score 세부 계산 함수들


def _calculate_echo_philosophy_fit(file_path: str, metrics: AssetMetrics) -> float:
    """Echo 철학 적합성 계산"""
    score = 20  # 기본 점수

    # 시그니처 연관성
    if metrics.has_signature_link:
        score += 30

    # 판단 엔진 연관성
    if metrics.has_judgment_link:
        score += 25

    # Echo 철학 연관성 (시그니처나 판단 엔진 연결로 대체)
    if metrics.has_signature_link and metrics.has_judgment_link:
        score += 20

    # 파일 경로 기반 Echo 적합성
    echo_indicators = [
        "echo",
        "signature",
        "judgment",
        "quantum",
        "meta",
        "liminal",
        "cosmos",
    ]
    if any(indicator in file_path.lower() for indicator in echo_indicators):
        score += 15

    return min(max(score, 0), 100)


def _calculate_roadmap_match(metrics: AssetMetrics) -> float:
    """로드맵 매칭 점수 계산"""
    score = 10  # 기본 점수

    # 로드맵과 매칭되면 전략적 가치 높음
    if metrics.roadmap_matched:
        score += 50

        # 우선순위에 따른 추가 점수
        priority_bonus = {"high": 30, "medium": 20, "low": 10}
        score += priority_bonus.get(metrics.roadmap_priority, 10)

    return min(max(score, 0), 100)


def _calculate_competitive_edge(file_path: str, metrics: AssetMetrics) -> float:
    """경쟁력 차별점 계산"""
    score = 30  # 기본 점수

    # Echo만의 고유한 접근법들
    unique_approaches = [
        "existence_based",
        "signature_",
        "emotion_rhythm",
        "quantum_judgment",
        "meta_cognitive",
        "liminal",
    ]

    # 파일명이나 구조에서 고유 접근법 확인
    for approach in unique_approaches:
        if approach in file_path.lower():
            score += 15
            break

    # 고유 패턴이 많을수록 차별점 있음
    if metrics.unique_patterns > 2:
        score += 20

    # 복잡한 구조일수록 차별화 요소
    if metrics.complexity > 15:
        score += 10

    return min(max(score, 0), 100)


# Potential Score 세부 계산 함수들


def _calculate_bridge_readiness(file_path: str, metrics: AssetMetrics) -> float:
    """브릿지 연결 준비도 계산"""
    score = 20  # 기본 점수

    # 이미 브릿지에서 호출되고 있으면 연결 준비됨
    if metrics.bridge_called:
        score += 40

    # API나 핸들러 성격의 파일들은 브릿지 연결 용이
    if any(
        keyword in file_path.lower()
        for keyword in ["api", "handler", "router", "endpoint"]
    ):
        score += 25

    # 함수가 적절히 구조화되어 있으면 연결 용이
    function_count = getattr(metrics, "function_count", 0)
    if 2 <= function_count <= 10:
        score += 15

    # 의존성이 적을수록 독립적 연결 가능
    if metrics.deps_out <= 3:
        score += 10

    return min(max(score, 0), 100)


def _calculate_cross_domain_reuse(file_path: str, metrics: AssetMetrics) -> float:
    """도메인 재사용성 계산"""
    score = 25  # 기본 점수

    # 유틸리티나 공통 모듈은 재사용성 높음
    if any(
        keyword in file_path.lower() for keyword in ["util", "common", "helper", "tool"]
    ):
        score += 30

    # 의존성이 적을수록 재사용 용이
    if metrics.deps_out <= 2:
        score += 20

    # 복잡도가 적당하면 이해/재사용 용이
    if 3 <= metrics.complexity <= 15:
        score += 15

    # Echo 특화된 것들은 재사용성 낮음
    if any(
        keyword in file_path.lower() for keyword in ["signature", "judgment", "quantum"]
    ):
        score -= 10

    return min(max(score, 0), 100)


def _calculate_activation_ease(metrics: AssetMetrics) -> float:
    """활성화 용이성 계산"""
    score = 30  # 기본 점수

    # 커버리지가 있으면 이미 작동 검증됨
    if metrics.covered:
        score += 25

    # 최근 수정되었으면 활성 상태
    if metrics.last_modified_days <= 30:
        score += 20
    elif metrics.last_modified_days <= 90:
        score += 10

    # 사용되지 않는 함수가 적을수록 정리된 상태
    if metrics.unused_functions <= 1:
        score += 15

    # 의존성 입력이 있으면 이미 연결된 상태
    if metrics.deps_in > 0:
        score += 10

    return min(max(score, 0), 100)


# 테스트용 함수
if __name__ == "__main__":
    # 샘플 메트릭으로 테스트
    from echo_engine.inspectors.asset_value_judger.schemas import AssetMetrics

    sample_metrics = AssetMetrics(
        loc=150,
        complexity=8,
        deps_in=3,
        deps_out=5,
        last_modified_days=45,
        covered=True,
        bridge_called=False,
        has_signature_link=True,
        has_judgment_link=False,
        roadmap_matched=True,
        roadmap_priority="high",
        unique_patterns=2,
        unused_functions=1,
    )

    sample_weights = {
        "total_weights": {"T": 0.4, "S": 0.4, "P": 0.2},
        "T": {
            "uniqueness": 0.3,
            "rebuild_cost": 0.3,
            "complexity": 0.2,
            "dependency": 0.2,
        },
        "S": {"philosophy": 0.4, "roadmap": 0.4, "edge": 0.2},
        "P": {"bridge": 0.4, "reuse": 0.3, "activation": 0.3},
    }

    t_score, s_score, p_score, total = compute_tsp_scores(
        "echo_engine/signature_mapper.py", sample_metrics, sample_weights
    )

    print("🧪 Score Model Test")
    print(f"T Score (Technical): {t_score:.1f}")
    print(f"S Score (Strategic): {s_score:.1f}")
    print(f"P Score (Potential): {p_score:.1f}")
    print(f"Total Score: {total:.1f}")
