"""
Static Analyzer - 정적 코드 분석
==============================

의존성 그래프, 복잡도, 미사용 코드 등 정적 분석 수행
"""

import os
import ast
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


def analyze_static_metrics(
    file_paths: List[str], root_path: str = "."
) -> Dict[str, Dict]:
    """
    정적 코드 분석 수행

    Args:
        file_paths: 분석할 파일 경로 리스트
        root_path: 프로젝트 루트 경로

    Returns:
        Dict[str, Dict]: 파일별 정적 분석 결과
    """
    print("🔍 Running static analysis...")

    # 의존성 그래프 분석
    dependency_graph = _analyze_dependencies(file_paths, root_path)

    # 복잡도 분석
    complexity_data = _analyze_complexity(file_paths)

    # 미사용 코드 분석
    unused_data = _analyze_unused_code(file_paths)

    # 고유 패턴 분석
    unique_patterns = _analyze_unique_patterns(file_paths)

    # 결과 통합
    results = {}
    for file_path in file_paths:
        results[file_path] = {
            "deps_in": dependency_graph["deps_in"].get(file_path, 0),
            "deps_out": dependency_graph["deps_out"].get(file_path, 0),
            "complexity": complexity_data.get(file_path, 0),
            "unused_functions": unused_data.get(file_path, 0),
            "unique_patterns": unique_patterns.get(file_path, 0),
            "dependency_depth": dependency_graph["depth"].get(file_path, 0),
            "is_leaf": dependency_graph["deps_out"].get(file_path, 0) == 0,
            "is_root": dependency_graph["deps_in"].get(file_path, 0) == 0,
        }

    return results


def _analyze_dependencies(
    file_paths: List[str], root_path: str
) -> Dict[str, Dict[str, int]]:
    """의존성 그래프 분석"""
    deps_in = defaultdict(int)  # 이 파일을 import하는 수
    deps_out = defaultdict(int)  # 이 파일이 import하는 수
    depth = defaultdict(int)  # 의존성 깊이

    # 모든 파일의 import 관계 추출
    import_graph = {}

    for file_path in file_paths:
        try:
            imports = _extract_imports(file_path, root_path)
            import_graph[file_path] = imports
            deps_out[file_path] = len(imports)

            # 역방향 의존성 계산
            for imported_file in imports:
                deps_in[imported_file] += 1

        except Exception as e:
            print(f"⚠️ Error analyzing dependencies for {file_path}: {e}")
            continue

    # 의존성 깊이 계산 (간단한 휴리스틱)
    for file_path in file_paths:
        depth[file_path] = _calculate_dependency_depth(file_path, import_graph, set())

    return {"deps_in": dict(deps_in), "deps_out": dict(deps_out), "depth": dict(depth)}


def _extract_imports(file_path: str, root_path: str) -> Set[str]:
    """파일에서 import하는 모듈들 추출"""
    imports = set()

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # AST 파싱으로 정확한 import 추출
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_path = _resolve_module_path(alias.name, root_path)
                        if module_path:
                            imports.add(module_path)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_path = _resolve_module_path(node.module, root_path)
                        if module_path:
                            imports.add(module_path)

        except SyntaxError:
            # AST 파싱 실패 시 정규식 fallback
            imports.update(_extract_imports_regex(content, root_path))

    except Exception as e:
        print(f"⚠️ Error extracting imports from {file_path}: {e}")

    return imports


def _extract_imports_regex(content: str, root_path: str) -> Set[str]:
    """정규식으로 import 추출 (fallback)"""
    imports = set()

    # import 패턴 매칭
    import_patterns = [
        r"^import\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
        r"^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import",
    ]

    for pattern in import_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        for match in matches:
            module_path = _resolve_module_path(match, root_path)
            if module_path:
                imports.add(module_path)

    return imports


def _resolve_module_path(module_name: str, root_path: str) -> str:
    """모듈명을 실제 파일 경로로 변환"""
    # 상대 import 처리
    if module_name.startswith("."):
        return None

    # 프로젝트 내부 모듈인지 확인
    possible_paths = [
        f"{module_name.replace('.', '/')}.py",
        f"{module_name.replace('.', '/')}/__init__.py",
    ]

    for possible_path in possible_paths:
        full_path = os.path.join(root_path, possible_path)
        if os.path.exists(full_path):
            return possible_path

    return None


def _calculate_dependency_depth(
    file_path: str, import_graph: Dict[str, Set[str]], visited: Set[str]
) -> int:
    """의존성 깊이 계산 (순환 참조 방지)"""
    if file_path in visited:
        return 0  # 순환 참조 방지

    visited.add(file_path)

    imports = import_graph.get(file_path, set())
    if not imports:
        return 0

    max_depth = 0
    for imported_file in imports:
        depth = _calculate_dependency_depth(imported_file, import_graph, visited.copy())
        max_depth = max(max_depth, depth + 1)

    return max_depth


def _analyze_complexity(file_paths: List[str]) -> Dict[str, int]:
    """순환 복잡도 분석"""
    complexity_data = {}

    for file_path in file_paths:
        try:
            complexity = _calculate_cyclomatic_complexity(file_path)
            complexity_data[file_path] = complexity
        except Exception as e:
            print(f"⚠️ Error calculating complexity for {file_path}: {e}")
            complexity_data[file_path] = 0

    return complexity_data


def _calculate_cyclomatic_complexity(file_path: str) -> int:
    """간단한 순환 복잡도 계산"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # 복잡도를 증가시키는 구문들 카운트
        complexity_keywords = [
            r"\bif\b",
            r"\belif\b",
            r"\bwhile\b",
            r"\bfor\b",
            r"\btry\b",
            r"\bexcept\b",
            r"\band\b",
            r"\bor\b",
            r"\?",
            r"&&",
            r"\|\|",  # 삼항연산자, 논리연산자
        ]

        total_complexity = 1  # 기본 경로

        for pattern in complexity_keywords:
            matches = re.findall(pattern, content, re.IGNORECASE)
            total_complexity += len(matches)

        return total_complexity

    except Exception:
        return 0


def _analyze_unused_code(file_paths: List[str]) -> Dict[str, int]:
    """미사용 코드 분석"""
    unused_data = {}

    for file_path in file_paths:
        try:
            unused_count = _count_unused_functions(file_path)
            unused_data[file_path] = unused_count
        except Exception as e:
            print(f"⚠️ Error analyzing unused code for {file_path}: {e}")
            unused_data[file_path] = 0

    return unused_data


def _count_unused_functions(file_path: str) -> int:
    """미사용 함수 개수 추정 (간단한 휴리스틱)"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # 함수 정의 추출
        function_defs = re.findall(r"^def\s+(\w+)", content, re.MULTILINE)

        # 프라이빗 함수(_로 시작)는 미사용으로 간주할 가능성 높음
        private_functions = [
            f for f in function_defs if f.startswith("_") and not f.startswith("__")
        ]

        # 실제 사용 여부 확인
        unused_count = 0
        for func_name in private_functions:
            # 함수 호출 패턴 검색
            call_pattern = rf"\b{func_name}\s*\("
            calls = re.findall(call_pattern, content)

            # 정의부 제외하고 호출이 없으면 미사용으로 판단
            if len(calls) <= 1:  # 정의부 1개만 있는 경우
                unused_count += 1

        return unused_count

    except Exception:
        return 0


def _analyze_unique_patterns(file_paths: List[str]) -> Dict[str, int]:
    """고유 패턴/알고리즘 분석"""
    unique_patterns = {}

    # 프로젝트 전체에서 고유한 패턴들 찾기
    all_patterns = defaultdict(list)

    for file_path in file_paths:
        try:
            patterns = _extract_code_patterns(file_path)
            for pattern in patterns:
                all_patterns[pattern].append(file_path)
        except Exception as e:
            print(f"⚠️ Error analyzing patterns for {file_path}: {e}")
            continue

    # 고유 패턴 (1-2개 파일에서만 사용) 계산
    for file_path in file_paths:
        unique_count = 0
        try:
            patterns = _extract_code_patterns(file_path)
            for pattern in patterns:
                if len(all_patterns[pattern]) <= 2:  # 고유하거나 거의 고유한 패턴
                    unique_count += 1
            unique_patterns[file_path] = unique_count
        except Exception:
            unique_patterns[file_path] = 0

    return unique_patterns


def _extract_code_patterns(file_path: str) -> Set[str]:
    """코드에서 특징적 패턴 추출"""
    patterns = set()

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # 클래스명 패턴
        class_names = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
        patterns.update(f"class:{name}" for name in class_names)

        # 함수명 패턴 (특징적인 것들)
        function_names = re.findall(r"^def\s+(\w+)", content, re.MULTILINE)
        significant_functions = [f for f in function_names if len(f) > 8 or "_" in f]
        patterns.update(f"func:{name}" for name in significant_functions)

        # 특별한 데코레이터 패턴
        decorators = re.findall(r"@(\w+)", content)
        patterns.update(f"decorator:{dec}" for dec in decorators)

        # Echo 시스템 특화 패턴
        echo_patterns = [
            "signature_",
            "judgment_",
            "echo_",
            "meta_",
            "liminal_",
            "quantum_",
            "cosmos_",
            "bridge_",
            "aurora_",
            "phoenix_",
        ]

        for pattern in echo_patterns:
            if pattern in content.lower():
                patterns.add(f"echo:{pattern}")

        return patterns

    except Exception:
        return set()


# CLI 테스트용
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        test_files = [sys.argv[1]]
    else:
        test_files = [__file__]

    print("🧪 Static Analyzer Test")
    result = analyze_static_metrics(test_files, ".")

    for file_path, metrics in result.items():
        print(f"\nFile: {file_path}")
        for key, value in metrics.items():
            print(f"  {key}: {value}")
