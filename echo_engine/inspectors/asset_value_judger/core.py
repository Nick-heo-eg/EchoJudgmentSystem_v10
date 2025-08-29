"""
Asset Value Judger - Core Engine
================================

코드 자산의 가치를 T/S/P 점수로 평가하고 분류하는 핵심 엔진
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .collectors.meta_collector import collect_file_metadata
from .collectors.static_analyzer import analyze_static_metrics
from .collectors.dynamic_analyzer import analyze_dynamic_metrics
from .collectors.signature_linker import analyze_signature_links
from .collectors.roadmap_linker import match_roadmap_features
from .scorer.score_model import compute_tsp_scores
from .classifier.decide import classify_asset
from .schemas import AssetReport, AssetMetrics, AssetDecision


def judge_assets(
    root_path: str = ".",
    coverage_xml: Optional[str] = None,
    bridge_log: Optional[str] = None,
    weights_config: Optional[str] = None,
    registry_config: Optional[str] = None,
    roadmap_config: Optional[str] = None,
    output_file: Optional[str] = None,
) -> List[AssetReport]:
    """
    Echo 자산 가치 판단 메인 엔진

    Args:
        root_path: 분석할 루트 디렉토리
        coverage_xml: 커버리지 XML 파일 경로
        bridge_log: 브릿지 호출 로그 파일 경로
        weights_config: 가중치 설정 YAML 파일
        registry_config: 자산 레지스트리 YAML 파일
        roadmap_config: 로드맵 YAML 파일
        output_file: 결과 JSON 파일 저장 경로

    Returns:
        List[AssetReport]: 각 파일별 분석 결과
    """

    # 설정 파일 로드
    weights = _load_weights(weights_config)
    registry = _load_registry(registry_config)
    roadmap = _load_roadmap(roadmap_config)

    # 소스 파일 스캔
    source_files = _scan_source_files(root_path)

    # 데이터 수집
    print(f"📊 Analyzing {len(source_files)} files...")

    meta_data = collect_file_metadata(source_files)
    static_data = analyze_static_metrics(source_files, root_path)
    dynamic_data = analyze_dynamic_metrics(coverage_xml, bridge_log)
    signature_data = analyze_signature_links(source_files)
    roadmap_data = match_roadmap_features(source_files, roadmap)

    # 각 파일 분석
    reports = []
    for file_path in source_files:
        try:
            # 메트릭 병합
            metrics = _merge_metrics(
                file_path,
                meta_data,
                static_data,
                dynamic_data,
                signature_data,
                roadmap_data,
            )

            # T/S/P 점수 계산
            t_score, s_score, p_score, total_score = compute_tsp_scores(
                file_path, metrics, weights
            )

            # 분류 결정
            status, reason, actions = classify_asset(
                file_path, metrics, t_score, s_score, p_score, total_score, registry
            )

            # 리포트 생성
            report = AssetReport(
                path=file_path,
                owner=_get_file_owner(file_path, registry),
                metrics=metrics,
                scores={
                    "t_score": t_score,
                    "s_score": s_score,
                    "p_score": p_score,
                    "total": total_score,
                },
                decision=AssetDecision(status=status, reason=reason, actions=actions),
                timestamp=datetime.now().isoformat(),
            )

            reports.append(report)

        except Exception as e:
            print(f"⚠️ Error analyzing {file_path}: {e}")
            continue

    # 결과 요약 출력
    _print_summary(reports)

    # 파일 저장
    if output_file:
        _save_report(reports, output_file)

    return reports


def _load_weights(config_path: Optional[str]) -> Dict[str, Any]:
    """가중치 설정 로드"""
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    # 기본 가중치
    return {
        "total_weights": {"T": 0.4, "S": 0.4, "P": 0.2},
        "thresholds": {"dormant": 80, "pending": 50},
        "T": {
            "uniqueness": 0.3,
            "rebuild_cost": 0.3,
            "complexity": 0.2,
            "dependency": 0.2,
        },
        "S": {"philosophy": 0.4, "roadmap": 0.4, "edge": 0.2},
        "P": {"bridge": 0.4, "reuse": 0.3, "activation": 0.3},
    }


def _load_registry(config_path: Optional[str]) -> Dict[str, Any]:
    """자산 레지스트리 로드"""
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    # 기본 보호 규칙
    return {
        "protected_patterns": [
            "*/seed_kernel.py",
            "*/judgment_engine.py",
            "*/signature_*.py",
            "*/__init__.py",
        ],
        "force_dormant": ["*/signature_router.py", "*/policy_simulator.py"],
    }


def _load_roadmap(config_path: Optional[str]) -> Dict[str, Any]:
    """로드맵 설정 로드"""
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    # 기본 로드맵 키워드
    return {
        "features": [
            {
                "name": "multi_signature_routing",
                "keywords": ["signature", "router", "multi", "vote"],
                "priority": "high",
                "eta": "2025-Q2",
            },
            {
                "name": "policy_impact_simulation",
                "keywords": ["policy", "simulator", "impact", "scenario"],
                "priority": "medium",
                "eta": "2025-Q3",
            },
            {
                "name": "quantum_judgment_engine",
                "keywords": ["quantum", "judgment", "superposition"],
                "priority": "high",
                "eta": "2025-Q4",
            },
        ]
    }


def _scan_source_files(root_path: str) -> List[str]:
    """소스 파일 스캔"""
    source_files = []
    root = Path(root_path)

    for pattern in ["**/*.py"]:
        for file_path in root.glob(pattern):
            if file_path.is_file():
                # 제외 패턴
                exclude_patterns = [
                    "__pycache__",
                    ".venv",
                    ".git",
                    "node_modules",
                    "test_",
                    "_test.py",
                    ".pyc",
                ]

                if not any(exclude in str(file_path) for exclude in exclude_patterns):
                    source_files.append(str(file_path.relative_to(root)))

    return sorted(source_files)


def _merge_metrics(
    file_path: str,
    meta_data: Dict,
    static_data: Dict,
    dynamic_data: Dict,
    signature_data: Dict,
    roadmap_data: Dict,
) -> AssetMetrics:
    """각 수집기의 데이터를 하나의 메트릭으로 병합"""

    meta = meta_data.get(file_path, {})
    static = static_data.get(file_path, {})
    dynamic = dynamic_data.get(file_path, {})
    signature = signature_data.get(file_path, {})
    roadmap = roadmap_data.get(file_path, {})

    return AssetMetrics(
        loc=meta.get("loc", 0),
        complexity=static.get("complexity", 0),
        deps_in=static.get("deps_in", 0),
        deps_out=static.get("deps_out", 0),
        last_modified_days=meta.get("last_modified_days", 0),
        covered=dynamic.get("covered", False),
        bridge_called=dynamic.get("bridge_called", False),
        has_signature_link=signature.get("has_signature_link", False),
        has_judgment_link=signature.get("has_judgment_link", False),
        roadmap_matched=roadmap.get("matched", False),
        roadmap_priority=roadmap.get("priority", "low"),
        unique_patterns=static.get("unique_patterns", 0),
        unused_functions=static.get("unused_functions", 0),
    )


def _get_file_owner(file_path: str, registry: Dict) -> str:
    """파일 소유자 확인"""
    owners = registry.get("owners", {})

    for pattern, owner in owners.items():
        if pattern in file_path:
            return owner

    # 디렉토리 기반 기본 소유자
    if "echo_engine" in file_path:
        return "echo-core"
    elif "bridge" in file_path:
        return "bridge-team"
    else:
        return "unknown"


def _print_summary(reports: List[AssetReport]):
    """결과 요약 출력"""
    total = len(reports)
    dormant = sum(1 for r in reports if r.decision.status == "dormant")
    pending = sum(1 for r in reports if r.decision.status == "pending")
    junk = sum(1 for r in reports if r.decision.status == "junk")

    print(f"\n📈 Asset Analysis Summary")
    print(f"=" * 40)
    print(f"Total Files: {total}")
    print(f"🔒 Dormant (High Value): {dormant}")
    print(f"⏳ Pending (Review): {pending}")
    print(f"🗑️  Junk (Low Value): {junk}")
    print(f"")

    # Top 5 dormant assets
    dormant_assets = [r for r in reports if r.decision.status == "dormant"]
    dormant_assets.sort(key=lambda x: x.scores["total"], reverse=True)

    print(f"🌟 Top 5 Dormant Assets (High Potential):")
    for i, asset in enumerate(dormant_assets[:5], 1):
        print(f"  {i}. {asset.path} (Score: {asset.scores['total']:.1f})")

    # Junk candidates
    junk_assets = [r for r in reports if r.decision.status == "junk"]
    if junk_assets:
        print(f"\n🗑️  Junk Candidates for Cleanup:")
        for asset in junk_assets[:5]:
            print(f"  - {asset.path} ({asset.decision.reason})")


def _save_report(reports: List[AssetReport], output_file: str):
    """리포트를 JSON 파일로 저장"""
    report_data = [report.dict() for report in reports]

    with open(output_file, "w") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"💾 Report saved to: {output_file}")


if __name__ == "__main__":
    # CLI 실행 예시
    import sys

    root = sys.argv[1] if len(sys.argv) > 1 else "."
    output = sys.argv[2] if len(sys.argv) > 2 else "asset_audit_report.json"

    print(f"🔍 Echo Asset Value Judger")
    print(f"Analyzing: {root}")

    reports = judge_assets(root_path=root, output_file=output)

    print(f"✅ Analysis complete: {len(reports)} files processed")
