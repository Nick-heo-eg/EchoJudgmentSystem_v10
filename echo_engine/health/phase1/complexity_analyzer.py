import ast
from typing import Tuple
from echo_engine.health.registry import MetricResult

MAX_SCORE = 10.0


def _count_lines(node: ast.AST) -> int:
    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
        return int(node.end_lineno) - int(node.lineno) + 1
    return 0


def _nesting_depth(node: ast.AST, depth=0) -> int:
    max_d = depth
    for child in ast.iter_child_nodes(node):
        d = _nesting_depth(child, depth + 1)
        if d > max_d:
            max_d = d
    return max_d


def _cyclomatic(node: ast.AST) -> int:
    # 매우 단순 추정: 분기 노드 수 + 1
    count = 1
    for n in ast.walk(node):
        if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.BoolOp)):
            count += 1
    return count


def analyze_repo(root: str, max_files: int = 500) -> Tuple[int, int, int, int, int]:
    # returns (funcs, long, deep, complex, ok)
    import os

    funcs = long = deep = complex_ = ok = 0
    file_count = 0

    EXCLUDE_DIRS = (
        "venv",
        ".git",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
        "data",
        "logs",
        "health_reports",
    )

    for dirpath, dirs, filenames in os.walk(root):
        if any(h in dirpath for h in EXCLUDE_DIRS):
            continue
        # Prune dirs to avoid deep scanning
        dirs[:] = [d for d in dirs if not any(h in d for h in EXCLUDE_DIRS)]

        for fn in filenames:
            if not fn.endswith(".py") or file_count >= max_files:
                continue
            file_count += 1
            p = os.path.join(dirpath, fn)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if len(content) > 200000:  # Skip very large files
                        continue
                tree = ast.parse(content)
            except Exception:
                continue
            for n in ast.walk(tree):
                if isinstance(n, ast.FunctionDef):
                    funcs += 1
                    lines = _count_lines(n)
                    depth = _nesting_depth(n)
                    cyc = _cyclomatic(n)
                    bad = (lines >= 15) or (depth >= 6) or (cyc >= 10)
                    long += 1 if lines >= 15 else 0
                    deep += 1 if depth >= 6 else 0  # 전체 AST 깊이 기준, 넉넉히
                    complex_ += 1 if cyc >= 10 else 0
                    ok += 0 if bad else 1
        if file_count >= max_files:
            break
    return funcs, long, deep, complex_, ok


def run_complexity(root: str) -> MetricResult:
    funcs, long, deep, complex_, ok = analyze_repo(root)
    total_bad = long + deep + complex_
    # 간단 스코어: 문제가 적을수록 점수↑
    score = max(0.0, MAX_SCORE - (total_bad * 0.5))
    summary = f"func={funcs}, long={long}, deep={deep}, cyc10+={complex_}"
    return MetricResult(
        key="complexity", score=round(score, 2), max_score=MAX_SCORE, summary=summary
    )


def register(registry, root: str, weight: float):
    from echo_engine.health.registry import MetricSpec

    registry.register(
        MetricSpec(key="complexity", weight=weight, runner=lambda: run_complexity(root))
    )
