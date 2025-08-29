"""
Roadmap Linker - 로드맵 기능 매칭 분석
==================================

파일과 로드맵 기능들의 연관성 분석
"""

import os
import re
from typing import Dict, List, Optional, Set
from pathlib import Path


def match_roadmap_features(
    file_paths: List[str], roadmap_config: Dict
) -> Dict[str, Dict]:
    """
    파일들과 로드맵 기능들의 매칭 분석

    Args:
        file_paths: 분석할 파일 경로 리스트
        roadmap_config: 로드맵 설정 딕셔너리

    Returns:
        Dict[str, Dict]: 파일별 로드맵 매칭 결과
    """
    print("🗺️ Analyzing roadmap feature matching...")

    features = roadmap_config.get("features", [])
    results = {}

    for file_path in file_paths:
        try:
            match_data = _analyze_file_roadmap_match(file_path, features)
            results[file_path] = match_data
        except Exception as e:
            print(f"⚠️ Error analyzing roadmap match for {file_path}: {e}")
            results[file_path] = _get_default_roadmap_data()

    return results


def _analyze_file_roadmap_match(file_path: str, features: List[Dict]) -> Dict:
    """단일 파일의 로드맵 매칭 분석"""

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return _get_default_roadmap_data()

    matched_features = []
    best_match_score = 0
    best_match_priority = "low"
    best_match_eta = None

    content_lower = content.lower()
    file_path_lower = file_path.lower()

    for feature in features:
        feature_name = feature.get("name", "")
        keywords = feature.get("keywords", [])
        priority = feature.get("priority", "low")
        eta = feature.get("eta", "")
        description = feature.get("description", "")

        # 키워드 매칭 점수 계산
        match_score = _calculate_feature_match_score(
            content_lower, file_path_lower, keywords, feature_name
        )

        if match_score > 0:
            matched_features.append(
                {
                    "name": feature_name,
                    "score": match_score,
                    "priority": priority,
                    "eta": eta,
                    "matched_keywords": _get_matched_keywords(
                        content_lower, file_path_lower, keywords
                    ),
                }
            )

            # 최고 점수 기능 추적
            if match_score > best_match_score:
                best_match_score = match_score
                best_match_priority = priority
                best_match_eta = eta

    # 매칭 강도 계산
    match_strength = min(best_match_score * 10, 100)  # 0-100 스케일

    # 미래 가치 평가
    future_value = _assess_future_value(matched_features, best_match_priority)

    return {
        "matched": len(matched_features) > 0,
        "match_count": len(matched_features),
        "best_match_score": best_match_score,
        "match_strength": match_strength,
        "priority": best_match_priority,
        "eta": best_match_eta,
        "matched_features": matched_features,
        "future_value": future_value,
        "strategic_importance": _calculate_strategic_importance(matched_features),
        "development_readiness": _assess_development_readiness(
            content, matched_features
        ),
    }


def _calculate_feature_match_score(
    content: str, file_path: str, keywords: List[str], feature_name: str
) -> float:
    """기능 매칭 점수 계산"""
    score = 0.0

    # 키워드 매칭 (기본 점수)
    for keyword in keywords:
        keyword_lower = keyword.lower()

        # 파일 경로에서 매칭 (가중치 높음)
        if keyword_lower in file_path:
            score += 3.0

        # 내용에서 매칭
        content_matches = content.count(keyword_lower)
        if content_matches > 0:
            score += min(content_matches * 0.5, 2.0)  # 최대 2점

    # 기능명 직접 매칭 (보너스)
    feature_name_lower = feature_name.lower().replace("_", " ")
    feature_keywords = feature_name_lower.split()

    for keyword in feature_keywords:
        if keyword in content or keyword in file_path:
            score += 1.5

    # 클래스/함수명 매칭 (고정밀 매칭)
    class_function_patterns = [
        rf"class.*{re.escape(keyword)}",
        rf"def.*{re.escape(keyword)}",
        rf"{re.escape(keyword)}.*class",
        rf"{re.escape(keyword)}.*def",
    ]

    for keyword in keywords:
        keyword_escaped = re.escape(keyword.lower())
        for pattern in class_function_patterns:
            pattern_filled = pattern.format(keyword=keyword_escaped)
            if re.search(pattern_filled, content, re.IGNORECASE):
                score += 2.0

    return score


def _get_matched_keywords(
    content: str, file_path: str, keywords: List[str]
) -> List[str]:
    """매칭된 키워드들 반환"""
    matched = []

    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in content or keyword_lower in file_path:
            matched.append(keyword)

    return matched


def _assess_future_value(matched_features: List[Dict], priority: str) -> int:
    """미래 가치 평가 (0-100)"""
    if not matched_features:
        return 0

    base_score = 30  # 기본 점수

    # 우선순위에 따른 가중치
    priority_weights = {"high": 40, "medium": 25, "low": 10}
    priority_score = priority_weights.get(priority, 10)

    # 매칭된 기능 수에 따른 보너스
    feature_count_bonus = min(len(matched_features) * 5, 20)

    # 높은 점수 기능이 있으면 추가 보너스
    max_score = max(feature.get("score", 0) for feature in matched_features)
    score_bonus = min(max_score * 2, 10)

    total_score = base_score + priority_score + feature_count_bonus + score_bonus
    return min(total_score, 100)


def _calculate_strategic_importance(matched_features: List[Dict]) -> str:
    """전략적 중요도 계산"""
    if not matched_features:
        return "low"

    # 최고 우선순위 기능 기준
    priorities = [feature.get("priority", "low") for feature in matched_features]

    if "high" in priorities:
        return "high"
    elif "medium" in priorities:
        return "medium"
    else:
        return "low"


def _assess_development_readiness(content: str, matched_features: List[Dict]) -> str:
    """개발 준비도 평가"""
    if not matched_features:
        return "not_ready"

    # 코드 완성도 지표들
    readiness_indicators = {
        "implemented": [
            r"class\s+\w+",
            r"def\s+\w+",
            r"return\s+",
            r"if\s+.*:",
            r"for\s+.*:",
            r"while\s+.*:",
            r"try:",
            r"except:",
        ],
        "partial": [
            r"TODO",
            r"FIXME",
            r"XXX",
            r"NotImplemented",
            r"pass\s*$",
            r"raise\s+NotImplementedError",
        ],
        "planned": [
            r"# Plan:",
            r"# Design:",
            r"# Architecture:",
            r"# TODO:",
            r'""".*plan.*"""',
            r'""".*design.*"""',
        ],
    }

    content_lower = content.lower()

    implemented_count = sum(
        len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
        for pattern in readiness_indicators["implemented"]
    )

    partial_count = sum(
        len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
        for pattern in readiness_indicators["partial"]
    )

    planned_count = sum(
        len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
        for pattern in readiness_indicators["planned"]
    )

    # 준비도 판단
    if implemented_count > 5 and partial_count < 3:
        return "ready"
    elif implemented_count > 2 or partial_count > 0:
        return "partial"
    elif planned_count > 0:
        return "planned"
    else:
        return "not_ready"


def _get_default_roadmap_data() -> Dict:
    """기본 로드맵 데이터 (오류 시)"""
    return {
        "matched": False,
        "match_count": 0,
        "best_match_score": 0,
        "match_strength": 0,
        "priority": "low",
        "eta": None,
        "matched_features": [],
        "future_value": 0,
        "strategic_importance": "low",
        "development_readiness": "not_ready",
    }


def create_sample_roadmap() -> Dict:
    """샘플 로드맵 생성 (테스트용)"""
    return {
        "features": [
            {
                "name": "multi_signature_routing",
                "keywords": ["signature", "router", "multi", "vote", "consensus"],
                "priority": "high",
                "eta": "2025-Q2",
                "description": "Multiple signature voting and routing system",
            },
            {
                "name": "policy_impact_simulation",
                "keywords": ["policy", "simulator", "impact", "scenario", "prediction"],
                "priority": "medium",
                "eta": "2025-Q3",
                "description": "Policy decision impact simulation framework",
            },
            {
                "name": "quantum_judgment_engine",
                "keywords": ["quantum", "judgment", "superposition", "uncertainty"],
                "priority": "high",
                "eta": "2025-Q4",
                "description": "Quantum-enhanced judgment processing",
            },
            {
                "name": "emotional_rhythm_analyzer",
                "keywords": ["emotion", "rhythm", "flow", "pattern", "analysis"],
                "priority": "medium",
                "eta": "2025-Q2",
                "description": "Advanced emotional rhythm pattern analysis",
            },
            {
                "name": "bridge_integration_framework",
                "keywords": ["bridge", "integration", "api", "connector", "interface"],
                "priority": "high",
                "eta": "2025-Q1",
                "description": "Universal bridge integration framework",
            },
            {
                "name": "meta_cognitive_loops",
                "keywords": ["meta", "cognitive", "loop", "reflection", "awareness"],
                "priority": "medium",
                "eta": "2025-Q3",
                "description": "Advanced meta-cognitive processing loops",
            },
        ]
    }


# CLI 테스트용
if __name__ == "__main__":
    import sys

    # 샘플 로드맵 사용
    sample_roadmap = create_sample_roadmap()

    if len(sys.argv) > 1:
        test_files = [sys.argv[1]]
    else:
        test_files = [__file__]

    print("🧪 Roadmap Linker Test")
    print(f"Testing with {len(sample_roadmap['features'])} roadmap features")

    result = match_roadmap_features(test_files, sample_roadmap)

    for file_path, analysis in result.items():
        print(f"\nFile: {file_path}")
        for key, value in analysis.items():
            if key == "matched_features" and value:
                print(f"  {key}:")
                for feature in value:
                    print(
                        f"    - {feature['name']} (score: {feature['score']}, priority: {feature['priority']})"
                    )
            else:
                print(f"  {key}: {value}")
