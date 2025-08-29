"""
Meta Collector - 파일 기본 메타데이터 수집
=======================================

파일 크기, 수정일, LOC 등 기본적인 파일 정보 수집
"""

import os
import re
from pathlib import Path
from typing import Dict, List
from datetime import datetime


def collect_file_metadata(file_paths: List[str]) -> Dict[str, Dict]:
    """
    파일들의 기본 메타데이터 수집

    Args:
        file_paths: 분석할 파일 경로 리스트

    Returns:
        Dict[str, Dict]: 파일별 메타데이터
    """
    metadata = {}

    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                metadata[file_path] = _collect_single_file_metadata(file_path)
            else:
                metadata[file_path] = _get_default_metadata()
        except Exception as e:
            print(f"⚠️ Error collecting metadata for {file_path}: {e}")
            metadata[file_path] = _get_default_metadata()

    return metadata


def _collect_single_file_metadata(file_path: str) -> Dict:
    """단일 파일의 메타데이터 수집"""

    file_stats = os.stat(file_path)

    # 파일 크기 및 수정일
    file_size = file_stats.st_size
    modified_time = datetime.fromtimestamp(file_stats.st_mtime)
    last_modified_days = (datetime.now() - modified_time).days

    # LOC 계산
    loc, sloc = _count_lines_of_code(file_path)

    # 파일 타입 분석
    file_type = _analyze_file_type(file_path)

    # 복잡성 지표 (간단한 휴리스틱)
    complexity_indicators = _count_complexity_indicators(file_path)

    return {
        "file_size": file_size,
        "loc": loc,
        "sloc": sloc,  # Source Lines of Code (주석/빈줄 제외)
        "last_modified_days": last_modified_days,
        "last_modified": modified_time.isoformat(),
        "file_type": file_type,
        **complexity_indicators,
    }


def _count_lines_of_code(file_path: str) -> tuple[int, int]:
    """LOC와 SLOC 계산"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        total_lines = len(lines)
        source_lines = 0

        in_multiline_comment = False

        for line in lines:
            stripped = line.strip()

            # 빈 줄 건너뛰기
            if not stripped:
                continue

            # 멀티라인 주석 처리 (Python docstring)
            if '"""' in stripped or "'''" in stripped:
                if in_multiline_comment:
                    in_multiline_comment = False
                    continue
                else:
                    in_multiline_comment = True
                    continue

            if in_multiline_comment:
                continue

            # 단일 라인 주석 건너뛰기
            if stripped.startswith("#"):
                continue

            source_lines += 1

        return total_lines, source_lines

    except Exception as e:
        print(f"⚠️ Error counting LOC for {file_path}: {e}")
        return 0, 0


def _analyze_file_type(file_path: str) -> str:
    """파일 타입 분석"""

    path = Path(file_path)

    # 파일명 패턴으로 타입 추정
    if path.name.startswith("test_") or "_test.py" in path.name:
        return "test"
    elif path.name in ["__init__.py"]:
        return "module_init"
    elif "config" in path.name.lower():
        return "config"
    elif any(keyword in path.name.lower() for keyword in ["util", "helper", "tool"]):
        return "utility"
    elif any(keyword in str(path) for keyword in ["api", "server", "router"]):
        return "api"
    elif any(keyword in str(path) for keyword in ["engine", "core"]):
        return "core"
    elif any(keyword in str(path) for keyword in ["ui", "dashboard", "web"]):
        return "interface"
    else:
        return "module"


def _count_complexity_indicators(file_path: str) -> Dict:
    """복잡성 지표들 계산"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # 함수/클래스 개수
        function_count = len(re.findall(r"^def\s+\w+", content, re.MULTILINE))
        class_count = len(re.findall(r"^class\s+\w+", content, re.MULTILINE))

        # import 개수 (의존성 추정)
        import_count = len(re.findall(r"^(import|from)\s+", content, re.MULTILINE))

        # 조건문/반복문 개수 (복잡도 추정)
        control_structures = len(
            re.findall(r"\b(if|elif|else|for|while|try|except|finally)\b", content)
        )

        # TODO/FIXME/XXX 주석 (기술부채 지표)
        todo_count = len(
            re.findall(r"#.*\b(TODO|FIXME|XXX|HACK)\b", content, re.IGNORECASE)
        )

        # 긴 함수 개수 (20줄 이상)
        long_functions = _count_long_functions(content)

        return {
            "function_count": function_count,
            "class_count": class_count,
            "import_count": import_count,
            "control_structures": control_structures,
            "todo_count": todo_count,
            "long_functions": long_functions,
        }

    except Exception as e:
        print(f"⚠️ Error analyzing complexity for {file_path}: {e}")
        return {
            "function_count": 0,
            "class_count": 0,
            "import_count": 0,
            "control_structures": 0,
            "todo_count": 0,
            "long_functions": 0,
        }


def _count_long_functions(content: str) -> int:
    """20줄 이상의 긴 함수 개수 세기"""
    lines = content.split("\n")
    long_function_count = 0
    current_function_lines = 0
    in_function = False
    base_indent = 0

    for line in lines:
        stripped = line.strip()

        # 함수 시작 감지
        if re.match(r"^def\s+\w+", stripped):
            if in_function and current_function_lines > 20:
                long_function_count += 1

            in_function = True
            current_function_lines = 1
            base_indent = len(line) - len(line.lstrip())
            continue

        if in_function:
            if stripped:  # 비어있지 않은 줄
                current_indent = len(line) - len(line.lstrip())

                # 함수 끝 감지 (인덴트가 함수 레벨과 같거나 작음)
                if current_indent <= base_indent:
                    if current_function_lines > 20:
                        long_function_count += 1
                    in_function = False
                else:
                    current_function_lines += 1

    # 파일 끝에서 함수가 끝나는 경우
    if in_function and current_function_lines > 20:
        long_function_count += 1

    return long_function_count


def _get_default_metadata() -> Dict:
    """기본 메타데이터 (파일이 없거나 오류 시)"""
    return {
        "file_size": 0,
        "loc": 0,
        "sloc": 0,
        "last_modified_days": 9999,
        "last_modified": "1970-01-01T00:00:00",
        "file_type": "unknown",
        "function_count": 0,
        "class_count": 0,
        "import_count": 0,
        "control_structures": 0,
        "todo_count": 0,
        "long_functions": 0,
    }


# 테스트용 함수
if __name__ == "__main__":
    # 현재 파일 자체를 테스트
    test_files = [__file__]
    result = collect_file_metadata(test_files)

    print("🧪 Meta Collector Test")
    for file_path, metadata in result.items():
        print(f"\nFile: {file_path}")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
