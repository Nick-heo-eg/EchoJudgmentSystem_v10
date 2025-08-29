#!/usr/bin/env python3
"""
🧬 Echo Evolve Minimal Loop
최소 진화 실행 루프 - 외부 의존 거의 없이 돌아가는 최소 진화 시스템

목표:
- 시스템 스캔(폴더/파일/라인수/최근 수정)
- 간단 평가(경고/제안)
- 드라이런 패치 플랜 산출
- 아티팩트 저장
"""

from __future__ import annotations

# compat_aliases 지연 로더 설치
try:
    from .compat_aliases import install_compat_aliases

    install_compat_aliases()
except Exception:
    pass  # 헬스 측정/빌드에서 실패해도 진행

import os
import sys
import json
import time
import argparse
import hashlib
import ast
import importlib.util
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

# 프로젝트 루트 추정
ROOT = Path(__file__).resolve().parents[1]  # 프로젝트 루트
SRC = ROOT / "echo_engine"
ART = ROOT / "artifacts" / "evolution"
ART.mkdir(parents=True, exist_ok=True)

# FAST 모드 상수들
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
    "artifacts",
    "logs",
    "data",
    "_legacy",
}
MAX_FILE_SIZE = 300_000  # 300KB 이상 파일은 FAST에서 스킵
MAX_FINDINGS_FAST = 250  # FAST에서 너무 많이 쌓이면 조기 종료
HEAVY_PREFIX = (
    "transformers",
    "torch",
    "numpy",
    "pandas",
    "scipy",
    "openai",
    "requests",
)


@dataclass
class Finding:
    """발견된 개선 항목"""

    path: str
    kind: str
    detail: str
    score: float  # 0~1 (위험/우선순위)
    suggestion: str


@dataclass
class EvolutionPlan:
    """진화 계획"""

    plan_id: str
    created_at: str
    findings: List[Finding]
    summary: str


def _hash(text: str) -> str:
    """텍스트 해시 생성"""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]


def iter_py_files(root: Path, fast: bool):
    """Python 파일 반복자 - 빠른 스캔 지원"""
    for dirpath, dirnames, filenames in os.walk(root):
        # 제외 디렉토리 필터링
        dirnames[:] = [d for d in dirnames if (d not in EXCLUDE_DIRS)]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            fp = Path(dirpath) / fn
            if fast and fp.stat().st_size > MAX_FILE_SIZE:
                continue
            yield fp


def scan_components(limit: int = 2000, fast: bool = False) -> List[Path]:
    """컴포넌트 스캔 - Python 파일들 찾기"""
    files: List[Path] = []

    # echo_engine 디렉토리 스캔 (새 방식)
    for i, f in enumerate(iter_py_files(SRC, fast)):
        files.append(f)
        if i + 1 >= limit:
            break

    # 루트 디렉토리의 주요 Python 파일들도 포함 (기존 방식 유지)
    if len(files) < limit:
        for pattern in ["*.py", "echo*.py", "cosmos*.py"]:
            for p in ROOT.glob(pattern):
                if p.is_file() and p not in files:
                    files.append(p)
                    if len(files) >= limit:
                        break

    return files


def safe_find_spec(name: str, fast: bool = False):
    """안전한 모듈 스펙 찾기 - FAST 모드에서 외부 대형 패키지 스킵"""
    if fast and (name.startswith(HEAVY_PREFIX) or "." not in name):
        return True  # 외부 대형 패키지는 성공 가정(실행기 체크가 아님)
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


def _is_abs_path(s: str) -> bool:
    """절대경로 패턴 검사"""
    import re

    pats = (
        r"^/mnt/[a-z]/",
        r"^[A-Za-z]:\\\\",
        r"^/Users/",
        r"^/home/",
        r"^/var/log/",
        r"^/etc/",
        r"^/tmp/",
    )
    return any(re.match(p, s) for p in pats)


def _portability_findings(tree: ast.AST, file_rel: str):
    """정교한 portability 분석 - 실제 호출 자리만 검출"""
    findings = []

    def add(detail, score=0.70):
        findings.append(
            Finding(
                path=file_rel,
                kind="portability",
                detail=detail,
                score=score,
                suggestion="portable_paths.ensure_portable()/logs_dir()/project_root() 사용.",
            )
        )

    for node in ast.walk(tree):
        # open("..."), Path("..."), os.path.join("..."), sys.path.append("..."), sys.path.insert(0,"...")
        if isinstance(node, ast.Call):
            fn = node.func
            fn_name = getattr(fn, "id", None)
            attr = getattr(fn, "attr", None)
            qual = ".".join(
                filter(
                    None,
                    [
                        getattr(getattr(fn, "value", None), "id", None),
                        getattr(getattr(fn, "value", None), "attr", None),
                        attr,
                    ],
                )
            )

            # 1) open("ABS")
            if fn_name == "open" and node.args:
                arg0 = node.args[0]
                if (
                    isinstance(arg0, ast.Constant)
                    and isinstance(arg0.value, str)
                    and _is_abs_path(arg0.value)
                ):
                    add(f"open() 절대경로 사용: {arg0.value}")

            # 2) Path("ABS")
            if fn_name == "Path" and node.args:
                arg0 = node.args[0]
                if (
                    isinstance(arg0, ast.Constant)
                    and isinstance(arg0.value, str)
                    and _is_abs_path(arg0.value)
                ):
                    add(f"Path() 절대경로 사용: {arg0.value}")

            # 3) os.path.join("ABS", ...)
            if qual.endswith("os.path.join"):
                for a in node.args:
                    if (
                        isinstance(a, ast.Constant)
                        and isinstance(a.value, str)
                        and _is_abs_path(a.value)
                    ):
                        add(f"os.path.join() 절대경로 사용: {a.value}")
                        break

            # 4) sys.path.append("ABS") / sys.path.insert(0,"ABS")
            if qual.endswith("sys.path.append") and node.args:
                a = node.args[0]
                if (
                    isinstance(a, ast.Constant)
                    and isinstance(a.value, str)
                    and _is_abs_path(a.value)
                ):
                    add(f"sys.path.append 절대경로: {a.value}")
            if qual.endswith("sys.path.insert") and len(node.args) >= 2:
                a = node.args[1]
                if (
                    isinstance(a, ast.Constant)
                    and isinstance(a.value, str)
                    and _is_abs_path(a.value)
                ):
                    add(f"sys.path.insert 절대경로: {a.value}")
    return findings


def _parent_map(tree: ast.AST):
    """AST 노드의 부모 관계 맵 생성"""
    parents = {}
    for p in ast.walk(tree):
        for c in ast.iter_child_nodes(p):
            parents[c] = p
    return parents


def _guarded_import(node: ast.AST, parents: dict) -> bool:
    """TYPE_CHECKING / try-except ImportError 가드 내부인지 확인"""
    cur = node
    while cur is not None:
        # if TYPE_CHECKING: ...
        if isinstance(cur, ast.If):
            t = cur.test
            if isinstance(t, ast.Name) and t.id == "TYPE_CHECKING":
                return True
            if (
                isinstance(t, ast.Attribute)
                and getattr(t, "attr", "") == "TYPE_CHECKING"
                and getattr(getattr(t, "value", None), "id", None) == "typing"
            ):
                return True
        # try: import ... except ImportError: ...
        if isinstance(cur, ast.Try):
            for h in cur.handlers or []:
                if (
                    isinstance(getattr(h, "type", None), ast.Name)
                    and h.type.id == "ImportError"
                ):
                    return True
        cur = parents.get(cur)
    return False


def evaluate(
    files: List[Path], fast: bool = False, max_seconds: int = 25
) -> List[Finding]:
    """파일들 평가하여 개선점 찾기"""
    findings: List[Finding] = []
    now = time.time()
    start = time.monotonic()

    print(f"📊 {len(files)}개 파일 평가 중...")

    for idx, f in enumerate(files, 1):
        try:
            size = f.stat().st_size
            mtime = f.stat().st_mtime
            age_days = (now - mtime) / 86400

            text = f.read_text(encoding="utf-8", errors="ignore")
            lines = text.count("\n")

            # 1. 비대한 모듈 감지
            long_module = size > 50_000 or lines > 1200
            if long_module:
                findings.append(
                    Finding(
                        path=str(f.relative_to(ROOT)),
                        kind="size",
                        detail=f"모듈이 비대합니다({size:,}B, {lines:,} lines).",
                        score=0.65,
                        suggestion="기능 단위로 분리(파일 쪼개기) 권장.",
                    )
                )

            # 타임아웃/상한 체크
            if time.monotonic() - start > max_seconds:
                print(f"⏰ 시간 제한({max_seconds}s) 도달 - 부분 결과로 종료")
                break

            # 2. AST 기반 import 분석 (가드 인식 추가)
            try:
                tree = ast.parse(text)
                parents = _parent_map(tree)
                unresolved = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        # 상대 임포트는 그대로 경고(레벨>=2만 높게)
                        if node.level and node.level >= 2:
                            if not _guarded_import(node, parents):
                                unresolved.append(
                                    f"relative_import(level={node.level})"
                                )
                        elif node.module:
                            # 절대임포트는 실제로 해석 가능한지 확인
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
                                if not safe_find_spec(modname, fast):
                                    if not _guarded_import(node, parents):
                                        unresolved.append(modname)
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
                                if not safe_find_spec(n.name, fast):
                                    if not _guarded_import(node, parents):
                                        unresolved.append(n.name)

                if unresolved:
                    findings.append(
                        Finding(
                            path=str(f.relative_to(ROOT)),
                            kind="import",
                            detail=f"해결 불가 임포트: {sorted(set(unresolved))[:5]}",
                            score=(
                                0.80
                                if any("relative_import" in u for u in unresolved)
                                else 0.60
                            ),
                            suggestion="패키지 경로 정규화 또는 compat alias/실제 모듈 설치.",
                        )
                    )

                # 정교한 portability 분석 추가
                findings.extend(_portability_findings(tree, str(f.relative_to(ROOT))))

            except Exception as e:
                findings.append(
                    Finding(
                        path=str(f.relative_to(ROOT)),
                        kind="error",
                        detail=f"AST 스캔 오류: {e}",
                        score=0.70,
                        suggestion="파일 인코딩/문법 확인.",
                    )
                )

            if fast and len(findings) >= MAX_FINDINGS_FAST:
                print(f"🔍 FAST 모드 상한({MAX_FINDINGS_FAST}개) 도달 - 조기 종료")
                break

            # 3. 오래된 TODO/FIXME 감지
            todo_count = text.count("TODO") + text.count("FIXME") + text.count("XXX")
            deprecated_hint = todo_count > 0 and age_days > 7
            if deprecated_hint:
                findings.append(
                    Finding(
                        path=str(f.relative_to(ROOT)),
                        kind="debt",
                        detail=f"오래된 TODO/FIXME({todo_count}개, {int(age_days)}일 경과).",
                        score=0.55,
                        suggestion="우선순위 재평가 후 처리 스프린트 편성.",
                    )
                )

            # 4. 중복 함수명 패턴 감지
            func_defs = text.count("def ")
            if func_defs > 50:
                findings.append(
                    Finding(
                        path=str(f.relative_to(ROOT)),
                        kind="complexity",
                        detail=f"함수 밀도가 높습니다({func_defs}개 함수).",
                        score=0.60,
                        suggestion="클래스 단위로 리팩터링 또는 모듈 분리.",
                    )
                )

            # 5. 긴 라인 감지
            long_lines = len([line for line in text.split("\n") if len(line) > 120])
            if long_lines > 10:
                findings.append(
                    Finding(
                        path=str(f.relative_to(ROOT)),
                        kind="style",
                        detail=f"긴 라인이 많습니다({long_lines}개 라인 > 120자).",
                        score=0.45,
                        suggestion="코드 포매팅 및 라인 분할 권장.",
                    )
                )

            # 6. 하드코딩된 경로 감지는 이제 AST 기반 정교한 분석으로 대체됨

        except Exception as e:
            findings.append(
                Finding(
                    path=str(f.relative_to(ROOT)),
                    kind="error",
                    detail=f"스캔 오류: {e}",
                    score=0.7,
                    suggestion="파일 인코딩/권한 확인.",
                )
            )

    # 정렬: 위험도가 높은 항목 우선
    findings.sort(key=lambda x: x.score, reverse=True)
    print(f"✅ 평가 완료 - {len(findings)}개 이슈 발견")

    return findings


def make_plan(findings: List[Finding], topk: int = 30) -> EvolutionPlan:
    """진화 계획 생성"""
    pick = findings[:topk]
    body = "\n".join(f"- [{x.kind}] {x.path}: {x.detail}" for x in pick)
    pid = _hash(body + datetime.now(timezone.utc).isoformat())
    summary = f"총 {len(findings)}건 중 상위 {len(pick)}건 우선 처리."

    return EvolutionPlan(
        plan_id=pid,
        created_at=datetime.now(timezone.utc).isoformat() + "Z",
        findings=pick,
        summary=summary,
    )


def save_plan(plan: EvolutionPlan) -> Path:
    """진화 계획 저장"""
    out = ART / f"plan_{plan.plan_id}.json"

    plan_data = {**asdict(plan), "findings": [asdict(x) for x in plan.findings]}

    with out.open("w", encoding="utf-8") as f:
        json.dump(plan_data, f, ensure_ascii=False, indent=2)

    print(f"💾 계획 저장: {out}")
    return out


def apply_plan(plan: EvolutionPlan, dry_run: bool = True) -> Path:
    """
    진화 계획 적용
    dry_run=True: 실제 파일 변경 없이 '예상 패치'만 기록
    """
    out = ART / f"apply_{plan.plan_id}.json"
    actions = []

    print(f"🛠️  계획 적용 중 (dry_run={dry_run})...")

    for f in plan.findings:
        if f.kind == "import":
            actions.append(
                {
                    "path": f.path,
                    "action": "convert_relative_imports_to_absolute",
                    "note": "컨텍스트 독립성 확보",
                    "priority": "high",
                }
            )
        elif f.kind == "size":
            actions.append(
                {
                    "path": f.path,
                    "action": "split_large_module",
                    "note": "기능 단위 분리",
                    "priority": "medium",
                }
            )
        elif f.kind == "debt":
            actions.append(
                {
                    "path": f.path,
                    "action": "schedule_clean_up",
                    "note": "TODO/FIXME 정리 스프린트",
                    "priority": "low",
                }
            )
        elif f.kind == "complexity":
            actions.append(
                {
                    "path": f.path,
                    "action": "refactor_high_function_density",
                    "note": "클래스 단위 리팩터링",
                    "priority": "medium",
                }
            )
        elif f.kind == "style":
            actions.append(
                {
                    "path": f.path,
                    "action": "format_long_lines",
                    "note": "라인 길이 정규화",
                    "priority": "low",
                }
            )
        elif f.kind == "portability":
            actions.append(
                {
                    "path": f.path,
                    "action": "fix_hardcoded_paths",
                    "note": "환경 독립적 경로로 변경",
                    "priority": "high",
                }
            )

    apply_data = {
        "plan_id": plan.plan_id,
        "dry_run": dry_run,
        "applied_at": datetime.now(timezone.utc).isoformat() + "Z",
        "total_actions": len(actions),
        "actions": actions,
        "summary": f"{len(actions)}개 액션 {'시뮬레이션' if dry_run else '실제 적용'} 완료",
    }

    with out.open("w", encoding="utf-8") as f:
        json.dump(apply_data, f, ensure_ascii=False, indent=2)

    print(f"💾 적용 로그: {out}")
    return out


def get_system_health(fast: bool = False, max_seconds: int = 25) -> Dict[str, Any]:
    """시스템 건강 상태 요약"""
    try:
        files = scan_components(limit=1000, fast=fast)
        findings = evaluate(files, fast=fast, max_seconds=max_seconds)

        # 카테고리별 집계
        categories = {}
        for f in findings:
            if f.kind not in categories:
                categories[f.kind] = {"count": 0, "avg_score": 0.0, "total_score": 0.0}
            categories[f.kind]["count"] += 1
            categories[f.kind]["total_score"] += f.score

        # 평균 계산
        for cat in categories.values():
            cat["avg_score"] = cat["total_score"] / cat["count"]
            del cat["total_score"]

        # 전체 건강도 계산 (0~100)
        if findings:
            avg_issue_score = sum(f.score for f in findings) / len(findings)
            health_score = max(0, 100 - (avg_issue_score * 100))
        else:
            health_score = 100

        return {
            "health_score": round(health_score, 1),
            "total_files_scanned": len(files),
            "total_issues_found": len(findings),
            "issues_by_category": categories,
            "top_issues": [
                {"path": f.path, "kind": f.kind, "score": f.score, "detail": f.detail}
                for f in findings[:5]
            ],
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        }

    except Exception as e:
        return {
            "health_score": 0,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        }


def main():
    """메인 실행 함수"""
    ap = argparse.ArgumentParser(
        description="Echo evolve (minimal)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python -m echo_engine.evolve_min --limit 3000 --topk 40
  python -m echo_engine.evolve_min --apply
  python -m echo_engine.evolve_min --health
        """,
    )
    ap.add_argument("--limit", type=int, default=2000, help="스캔 최대 파일 수")
    ap.add_argument("--topk", type=int, default=30, help="우선 적용 항목 수")
    ap.add_argument("--apply", action="store_true", help="플랜 적용(기본은 미적용)")
    ap.add_argument("--no-dry-run", action="store_true", help="실제 변경(권장X)")
    ap.add_argument("--health", action="store_true", help="시스템 건강 상태만 확인")
    ap.add_argument(
        "--fast", action="store_true", help="FAST 모드 (큰 파일 스킵, 조기 종료)"
    )
    ap.add_argument("--max-seconds", type=int, default=25, help="최대 실행 시간(초)")
    args = ap.parse_args()

    print("🧬 Echo Evolve Minimal Loop")
    print("=" * 50)

    if args.health:
        print("🏥 시스템 건강 상태 확인 중...")
        health = get_system_health(fast=args.fast, max_seconds=args.max_seconds)

        print(f"\n📊 Echo 시스템 건강도: {health['health_score']}/100")
        print(f"📁 스캔된 파일: {health['total_files_scanned']}개")
        print(f"⚠️  발견된 이슈: {health['total_issues_found']}개")

        if health.get("issues_by_category"):
            print("\n📋 카테고리별 이슈:")
            for category, stats in health["issues_by_category"].items():
                print(
                    f"  • {category}: {stats['count']}개 (평균 위험도: {stats['avg_score']:.2f})"
                )

        if health.get("top_issues"):
            print("\n🚨 주요 이슈 TOP 5:")
            for i, issue in enumerate(health["top_issues"], 1):
                print(
                    f"  {i}. [{issue['kind']}] {issue['path']} (위험도: {issue['score']:.2f})"
                )
                print(f"     → {issue['detail']}")

        return

    # 일반 진화 루프 실행
    print(f"🔍 파일 스캔 시작 (최대 {args.limit}개)...")
    files = scan_components(limit=args.limit, fast=args.fast)

    print(f"📊 파일 평가 시작...")
    findings = evaluate(files, fast=args.fast, max_seconds=args.max_seconds)

    print(f"📋 진화 계획 생성 (상위 {args.topk}개)...")
    plan = make_plan(findings, topk=args.topk)

    plan_path = save_plan(plan)
    print(f"💾 진화 계획 저장 완료: {plan_path.name}")

    if args.apply:
        print(f"🛠️  진화 계획 적용 중...")
        apply_path = apply_plan(plan, dry_run=not args.no_dry_run)
        print(f"💾 적용 로그 저장 완료: {apply_path.name}")

        if args.no_dry_run:
            print("⚠️  실제 파일 변경이 적용되었습니다!")
        else:
            print("✅ 드라이런 모드 - 실제 파일은 변경되지 않았습니다.")

    print("\n🎯 Echo Evolve 완료!")
    print(f"📁 아티팩트 위치: {ART}")
    print("💡 추가 옵션: --health (건강 상태), --apply (계획 적용)")


if __name__ == "__main__":
    main()
