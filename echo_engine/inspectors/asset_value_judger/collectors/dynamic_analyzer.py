"""
Dynamic Analyzer - 동적 실행 분석
==============================

커버리지, 브릿지 호출 로그 등 실행 시 데이터 분석
"""

import os
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from pathlib import Path


def analyze_dynamic_metrics(
    coverage_xml: Optional[str] = None, bridge_log: Optional[str] = None
) -> Dict[str, Dict]:
    """
    동적 실행 메트릭 분석

    Args:
        coverage_xml: coverage.xml 파일 경로
        bridge_log: 브릿지 호출 로그 파일 경로

    Returns:
        Dict[str, Dict]: 파일별 동적 분석 결과
    """
    print("⚡ Running dynamic analysis...")

    # 커버리지 데이터 분석
    coverage_data = _analyze_coverage(coverage_xml) if coverage_xml else {}

    # 브릿지 호출 로그 분석
    bridge_data = _analyze_bridge_calls(bridge_log) if bridge_log else {}

    # 실행 빈도 분석 (로그 기반)
    execution_data = _analyze_execution_frequency(bridge_log) if bridge_log else {}

    # 결과 통합
    all_files = (
        set(coverage_data.keys()) | set(bridge_data.keys()) | set(execution_data.keys())
    )

    results = {}
    for file_path in all_files:
        results[file_path] = {
            "covered": coverage_data.get(file_path, {}).get("covered", False),
            "line_coverage": coverage_data.get(file_path, {}).get("line_rate", 0.0),
            "branch_coverage": coverage_data.get(file_path, {}).get("branch_rate", 0.0),
            "bridge_called": bridge_data.get(file_path, {}).get("called", False),
            "call_frequency": bridge_data.get(file_path, {}).get("frequency", 0),
            "last_execution": execution_data.get(file_path, {}).get(
                "last_execution", None
            ),
            "execution_count": execution_data.get(file_path, {}).get("count", 0),
            "is_hot_path": execution_data.get(file_path, {}).get("is_hot", False),
        }

    return results


def _analyze_coverage(coverage_xml: str) -> Dict[str, Dict]:
    """coverage.xml 파일 분석"""
    coverage_data = {}

    if not os.path.exists(coverage_xml):
        print(f"⚠️ Coverage file not found: {coverage_xml}")
        return coverage_data

    try:
        tree = ET.parse(coverage_xml)
        root = tree.getroot()

        # packages/classes/methods 구조 파싱
        for package in root.findall(".//package"):
            for class_elem in package.findall("classes/class"):
                filename = class_elem.get("filename", "")

                if filename:
                    # 상대 경로로 정규화
                    normalized_path = _normalize_path(filename)

                    line_rate = float(class_elem.get("line-rate", 0))
                    branch_rate = float(class_elem.get("branch-rate", 0))

                    coverage_data[normalized_path] = {
                        "covered": line_rate > 0,
                        "line_rate": line_rate,
                        "branch_rate": branch_rate,
                        "lines_covered": int(class_elem.get("lines-covered", 0)),
                        "lines_valid": int(class_elem.get("lines-valid", 0)),
                    }

        print(f"✅ Parsed coverage for {len(coverage_data)} files")

    except Exception as e:
        print(f"⚠️ Error parsing coverage XML: {e}")

    return coverage_data


def _analyze_bridge_calls(bridge_log: str) -> Dict[str, Dict]:
    """브릿지 호출 로그 분석"""
    bridge_data = {}

    if not os.path.exists(bridge_log):
        print(f"⚠️ Bridge log not found: {bridge_log}")
        return bridge_data

    try:
        call_counts = {}

        # JSON Lines 형식이라고 가정
        with open(bridge_log, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    log_entry = json.loads(line)

                    # 로그에서 파일 경로 추출
                    module_path = _extract_module_path_from_log(log_entry)
                    if module_path:
                        call_counts[module_path] = call_counts.get(module_path, 0) + 1

                except json.JSONDecodeError:
                    # 플레인 텍스트 로그 처리
                    module_path = _extract_module_path_from_text(line)
                    if module_path:
                        call_counts[module_path] = call_counts.get(module_path, 0) + 1

        # 결과 구성
        for file_path, count in call_counts.items():
            normalized_path = _normalize_path(file_path)
            bridge_data[normalized_path] = {
                "called": True,
                "frequency": count,
                "is_frequent": count > 10,  # 10회 이상 호출되면 자주 사용됨
            }

        print(f"✅ Analyzed bridge calls for {len(bridge_data)} files")

    except Exception as e:
        print(f"⚠️ Error analyzing bridge log: {e}")

    return bridge_data


def _analyze_execution_frequency(bridge_log: str) -> Dict[str, Dict]:
    """실행 빈도 및 핫패스 분석"""
    execution_data = {}

    if not os.path.exists(bridge_log):
        return execution_data

    try:
        file_executions = {}
        recent_executions = {}

        with open(bridge_log, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    log_entry = json.loads(line)
                    timestamp = log_entry.get("timestamp")
                    module_path = _extract_module_path_from_log(log_entry)

                    if module_path:
                        normalized_path = _normalize_path(module_path)

                        # 실행 횟수 카운트
                        file_executions[normalized_path] = (
                            file_executions.get(normalized_path, 0) + 1
                        )

                        # 최근 실행 시간 기록
                        if timestamp:
                            if (
                                normalized_path not in recent_executions
                                or timestamp > recent_executions[normalized_path]
                            ):
                                recent_executions[normalized_path] = timestamp

                except (json.JSONDecodeError, KeyError):
                    continue

        # 핫패스 식별 (상위 20% 실행 빈도)
        if file_executions:
            execution_counts = list(file_executions.values())
            execution_counts.sort(reverse=True)
            hot_threshold = (
                execution_counts[int(len(execution_counts) * 0.2)]
                if execution_counts
                else 0
            )

            for file_path, count in file_executions.items():
                execution_data[file_path] = {
                    "count": count,
                    "last_execution": recent_executions.get(file_path),
                    "is_hot": count >= hot_threshold and count > 5,
                }

        print(f"✅ Analyzed execution frequency for {len(execution_data)} files")

    except Exception as e:
        print(f"⚠️ Error analyzing execution frequency: {e}")

    return execution_data


def _extract_module_path_from_log(log_entry: Dict) -> Optional[str]:
    """로그 엔트리에서 모듈 경로 추출"""

    # 일반적인 로그 필드들 확인
    path_fields = ["module", "file", "source", "path", "filename"]

    for field in path_fields:
        if field in log_entry:
            path = log_entry[field]
            if isinstance(path, str) and path.endswith(".py"):
                return path

    # 스택 트레이스에서 추출
    if "stack" in log_entry or "traceback" in log_entry:
        stack_data = log_entry.get("stack") or log_entry.get("traceback")
        if isinstance(stack_data, str):
            # 파일 경로 패턴 찾기
            import re

            paths = re.findall(r'File "([^"]+\.py)"', stack_data)
            if paths:
                return paths[0]

    # 메시지에서 추출
    message = log_entry.get("message", "") or log_entry.get("msg", "")
    if isinstance(message, str):
        import re

        # 일반적인 파일 경로 패턴
        paths = re.findall(r"([a-zA-Z_][a-zA-Z0-9_/]*\.py)", message)
        if paths:
            return paths[0]

    return None


def _extract_module_path_from_text(text_line: str) -> Optional[str]:
    """플레인 텍스트 로그에서 모듈 경로 추출"""
    import re

    # 파일 경로 패턴들
    patterns = [
        r'File "([^"]+\.py)"',
        r"module=([a-zA-Z_][a-zA-Z0-9_/]*\.py)",
        r"path=([a-zA-Z_][a-zA-Z0-9_/]*\.py)",
        r"([a-zA-Z_][a-zA-Z0-9_/]*\.py):",
        r"\b([a-zA-Z_][a-zA-Z0-9_/]*\.py)\b",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text_line)
        if matches:
            return matches[0]

    return None


def _normalize_path(file_path: str) -> str:
    """파일 경로 정규화"""
    # 절대 경로를 상대 경로로 변환
    path = Path(file_path)

    # 현재 디렉토리 기준 상대 경로 생성
    try:
        current_dir = Path.cwd()
        if path.is_absolute():
            try:
                relative_path = path.relative_to(current_dir)
                return str(relative_path).replace("\\", "/")
            except ValueError:
                # 다른 드라이브나 경로인 경우
                return str(path).replace("\\", "/")
        else:
            return str(path).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


# 테스트용 브릿지 로그 생성
def generate_sample_bridge_log(output_file: str = "sample_bridge.log"):
    """테스트용 샘플 브릿지 로그 생성"""
    import json
    from datetime import datetime, timedelta

    sample_logs = [
        {
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
            "module": "echo_engine/judgment_engine.py",
            "message": "Processing judgment request",
            "level": "INFO",
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "module": "echo_engine/signature_mapper.py",
            "message": "Signature mapping completed",
            "level": "INFO",
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
            "file": "echo_engine/handlers/echo_decide.py",
            "message": "Echo decide handler called",
            "level": "INFO",
        },
    ]

    with open(output_file, "w") as f:
        for log in sample_logs:
            f.write(json.dumps(log) + "\n")

    print(f"📝 Sample bridge log created: {output_file}")


# CLI 테스트용
if __name__ == "__main__":
    import sys

    print("🧪 Dynamic Analyzer Test")

    # 샘플 로그 생성
    generate_sample_bridge_log()

    # 테스트 실행
    coverage_file = sys.argv[1] if len(sys.argv) > 1 else None
    bridge_file = sys.argv[2] if len(sys.argv) > 2 else "sample_bridge.log"

    result = analyze_dynamic_metrics(coverage_file, bridge_file)

    print(f"\nAnalyzed {len(result)} files:")
    for file_path, metrics in result.items():
        print(f"\nFile: {file_path}")
        for key, value in metrics.items():
            print(f"  {key}: {value}")

    # 정리
    if os.path.exists("sample_bridge.log"):
        os.remove("sample_bridge.log")
