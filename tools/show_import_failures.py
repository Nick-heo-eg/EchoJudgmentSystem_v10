#!/usr/bin/env python3
"""
Import 실패 분석기 - Import 13개 이슈의 정체를 정확히 파악
"""
import ast
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "echo_engine"


def safe_find_spec(name: str) -> bool:
    """모듈 스펙 찾기 시도"""
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


def analyze_imports_in_file(filepath: Path):
    """파일의 import 문제 분석"""
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(text)
        problems = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.level and node.level >= 2:
                    problems.append(
                        {
                            "type": "relative_import_deep",
                            "module": f"level={node.level}",
                            "line": node.lineno,
                            "severity": "high",
                        }
                    )
                elif node.module:
                    modname = node.module if node.level == 0 else None
                    if modname and not modname.startswith(
                        (
                            "typing",
                            "collections",
                            "dataclasses",
                            "pathlib",
                            "os",
                            "sys",
                            "json",
                            "time",
                            "datetime",
                            "functools",
                            "itertools",
                            "contextlib",
                            "concurrent",
                            "asyncio",
                            "re",
                            "uuid",
                            "hashlib",
                            "abc",
                            "enum",
                            "__future__",
                        )
                    ):
                        if not safe_find_spec(modname):
                            problems.append(
                                {
                                    "type": "unresolved_module",
                                    "module": modname,
                                    "line": node.lineno,
                                    "severity": "medium",
                                }
                            )
            elif isinstance(node, ast.Import):
                for n in node.names:
                    if not n.name.startswith(
                        (
                            "typing",
                            "collections",
                            "dataclasses",
                            "pathlib",
                            "os",
                            "sys",
                            "json",
                            "time",
                            "datetime",
                            "functools",
                            "itertools",
                            "contextlib",
                            "concurrent",
                            "asyncio",
                            "re",
                            "uuid",
                            "hashlib",
                            "abc",
                            "enum",
                            "__future__",
                        )
                    ):
                        if not safe_find_spec(n.name):
                            problems.append(
                                {
                                    "type": "unresolved_import",
                                    "module": n.name,
                                    "line": node.lineno,
                                    "severity": "medium",
                                }
                            )

        return problems
    except Exception as e:
        return [{"type": "parse_error", "error": str(e), "severity": "error"}]


def main():
    """Import 문제 파일들 분석"""
    print("🔍 Import 실패 분석 시작...")

    problem_files = []
    total_problems = 0

    # echo_engine 하위 모든 Python 파일 스캔
    for py_file in SRC.rglob("*.py"):
        if py_file.name == "__pycache__":
            continue

        problems = analyze_imports_in_file(py_file)
        if problems:
            rel_path = py_file.relative_to(ROOT)
            problem_files.append(
                {
                    "path": str(rel_path),
                    "problems": problems,
                    "problem_count": len(problems),
                }
            )
            total_problems += len(problems)

    # 루트 레벨 주요 파일들도 체크
    for pattern in ["*.py", "echo*.py", "cosmos*.py"]:
        for py_file in ROOT.glob(pattern):
            if py_file.is_file():
                problems = analyze_imports_in_file(py_file)
                if problems:
                    rel_path = py_file.relative_to(ROOT)
                    problem_files.append(
                        {
                            "path": str(rel_path),
                            "problems": problems,
                            "problem_count": len(problems),
                        }
                    )
                    total_problems += len(problems)

    # 결과 출력
    print(f"\n📊 Import 문제 요약:")
    print(f"   문제 파일: {len(problem_files)}개")
    print(f"   총 문제: {total_problems}개")

    # 심각도별 분류
    high_severity = []
    medium_severity = []
    errors = []

    for file_info in problem_files:
        for problem in file_info["problems"]:
            item = f"{file_info['path']}:{problem.get('line', '?')} - {problem.get('module', problem.get('error', 'Unknown'))}"
            if problem["severity"] == "high":
                high_severity.append(item)
            elif problem["severity"] == "medium":
                medium_severity.append(item)
            else:
                errors.append(item)

    if high_severity:
        print(f"\n🚨 HIGH (상대임포트 level≥2): {len(high_severity)}개")
        for item in sorted(high_severity)[:10]:  # 상위 10개만
            print(f"   • {item}")

    if medium_severity:
        print(f"\n⚠️  MEDIUM (해결불가 모듈): {len(medium_severity)}개")
        for item in sorted(medium_severity)[:10]:  # 상위 10개만
            print(f"   • {item}")

    if errors:
        print(f"\n❌ ERRORS (파싱실패): {len(errors)}개")
        for item in sorted(errors)[:5]:  # 상위 5개만
            print(f"   • {item}")

    # 자주 나오는 모듈명 통계
    module_counts = {}
    for file_info in problem_files:
        for problem in file_info["problems"]:
            if problem["type"] in ["unresolved_module", "unresolved_import"]:
                module = problem["module"]
                module_counts[module] = module_counts.get(module, 0) + 1

    if module_counts:
        print(f"\n📈 자주 실패하는 모듈 TOP 10:")
        sorted_modules = sorted(module_counts.items(), key=lambda x: x[1], reverse=True)
        for module, count in sorted_modules[:10]:
            print(f"   • {module}: {count}번")

    print(f"\n💡 다음 단계: tools/fix_imports_pass3.py 실행")


if __name__ == "__main__":
    main()
