#!/usr/bin/env python3
"""
Import 문제 정밀 치환기 - Pass 3
show_import_failures.py에서 식별된 패턴들을 자동 치환
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "echo_engine"

# Import 치환 규칙 - 자주 실패하는 패턴들 타게팅
FIX_PATTERNS = [
    # models.* → echo_engine.models.*
    (
        re.compile(
            r"^(\s*)from models\.([a-zA-Z_][a-zA-Z0-9_.]*) import", re.MULTILINE
        ),
        r"\1from echo_engine.models.\2 import",
    ),
    (
        re.compile(r"^(\s*)import models\.([a-zA-Z_][a-zA-Z0-9_.]*)", re.MULTILINE),
        r"\1import echo_engine.models.\2",
    ),
    # world_generator.* → echo_engine.world_generator.*
    (
        re.compile(
            r"^(\s*)from world_generator\.([a-zA-Z_][a-zA-Z0-9_.]*) import",
            re.MULTILINE,
        ),
        r"\1from echo_engine.world_generator.\2 import",
    ),
    (
        re.compile(
            r"^(\s*)import world_generator\.([a-zA-Z_][a-zA-Z0-9_.]*)", re.MULTILINE
        ),
        r"\1import echo_engine.world_generator.\2",
    ),
    # 상대임포트 level≥2 → level 1 또는 절대임포트로 변경
    (
        re.compile(r"^(\s*)from \.\.\.+([a-zA-Z_][a-zA-Z0-9_.]*) import", re.MULTILINE),
        r"\1from echo_engine.\2 import",
    ),
    # 일반적인 누락 패키지들 - echo_engine 하위로 간주
    (
        re.compile(
            r"^(\s*)from (signature_mapper|judgment_engine|emotion_infer|capsule_core) import",
            re.MULTILINE,
        ),
        r"\1from echo_engine.\2 import",
    ),
    (
        re.compile(
            r"^(\s*)import (signature_mapper|judgment_engine|emotion_infer|capsule_core)($|\s)",
            re.MULTILINE,
        ),
        r"\1import echo_engine.\2\3",
    ),
    # meta.* 계열 정리
    (
        re.compile(r"^(\s*)from meta\.([a-zA-Z_][a-zA-Z0-9_.]*) import", re.MULTILINE),
        r"\1from echo_engine.\2 import",
    ),
    (
        re.compile(r"^(\s*)import meta\.([a-zA-Z_][a-zA-Z0-9_.]*)", re.MULTILINE),
        r"\1import echo_engine.\2",
    ),
    # amoeba 계열
    (
        re.compile(
            r"^(\s*)from amoeba\.([a-zA-Z_][a-zA-Z0-9_.]*) import", re.MULTILINE
        ),
        r"\1from echo_engine.amoeba.\2 import",
    ),
    (
        re.compile(r"^(\s*)import amoeba\.([a-zA-Z_][a-zA-Z0-9_.]*)", re.MULTILINE),
        r"\1import echo_engine.amoeba.\2",
    ),
    # 새로운 정확 매핑 - 자주 실패하는 모듈들
    (
        re.compile(r"^(\s*)from (src\.echo_foundation\.doctrine) import", re.MULTILINE),
        r"\1from echo_engine.echo_foundation_doctrine import",
    ),
    (
        re.compile(
            r"^(\s*)import (src\.echo_foundation\.doctrine)($|\s)", re.MULTILINE
        ),
        r"\1import echo_engine.echo_foundation_doctrine\2",
    ),
    # claude_agent_runner → echo_engine 내부로 추정
    (
        re.compile(r"^(\s*)from (claude_agent_runner) import", re.MULTILINE),
        r"\1from echo_engine.\2 import",
    ),
    (
        re.compile(r"^(\s*)import (claude_agent_runner)($|\s)", re.MULTILINE),
        r"\1import echo_engine.\2\3",
    ),
    # agent_orchestra_runner → echo_engine 내부로 추정
    (
        re.compile(r"^(\s*)from (agent_orchestra_runner) import", re.MULTILINE),
        r"\1from echo_engine.\2 import",
    ),
    (
        re.compile(r"^(\s*)import (agent_orchestra_runner)($|\s)", re.MULTILINE),
        r"\1import echo_engine.\2\3",
    ),
    # 추가 정확 매핑 - 자주 실패하는 모듈들
    (
        re.compile(r"^(\s*)from (echo_engine\.amoeba_manager) import", re.MULTILINE),
        r"\1from echo_engine.amoeba.amoeba_manager import",
    ),
    (
        re.compile(r"^(\s*)import (echo_engine\.amoeba_manager)($|\s)", re.MULTILINE),
        r"\1import echo_engine.amoeba.amoeba_manager\2",
    ),
    # resonance.* → echo_engine.resonance_evaluator.*
    (
        re.compile(
            r"^(\s*)from resonance\.([a-zA-Z_][a-zA-Z0-9_.]*) import", re.MULTILINE
        ),
        r"\1from echo_engine.resonance_evaluator.\2 import",
    ),
    (
        re.compile(r"^(\s*)import resonance\.([a-zA-Z_][a-zA-Z0-9_.]*)", re.MULTILINE),
        r"\1import echo_engine.resonance_evaluator.\2",
    ),
    # foundation.* → echo_engine.* (일반 패턴)
    (
        re.compile(
            r"^(\s*)from foundation\.([a-zA-Z_][a-zA-Z0-9_.]*) import", re.MULTILINE
        ),
        r"\1from echo_engine.\2 import",
    ),
    (
        re.compile(r"^(\s*)import foundation\.([a-zA-Z_][a-zA-Z0-9_.]*)", re.MULTILINE),
        r"\1import echo_engine.\2",
    ),
    # 추가 정확 매핑 - TOP 실패 모듈들
    (
        re.compile(
            r"^(\s*)from (echo_engine\.amoeba\.amoeba_manager) import", re.MULTILINE
        ),
        r"\1from echo_engine.amoeba.amoeba_manager import",
    ),
    (
        re.compile(
            r"^(\s*)import (echo_engine\.amoeba\.amoeba_manager)($|\s)", re.MULTILINE
        ),
        r"\1import echo_engine.amoeba.amoeba_manager\2",
    ),
    # meta_log_writer → meta.meta_log_writer (compat_aliases에서 처리)
    (
        re.compile(r"^(\s*)from (meta_log_writer) import", re.MULTILINE),
        r"\1from echo_engine.meta_logger import",
    ),
    (
        re.compile(r"^(\s*)import (meta_log_writer)($|\s)", re.MULTILINE),
        r"\1import echo_engine.meta_logger\2",
    ),
]


def fix_imports_in_file(filepath: Path, dry_run: bool = True) -> bool:
    """파일의 import 문제 수정"""
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
        original = text
        changed = False

        for pattern, replacement in FIX_PATTERNS:
            new_text, count = pattern.subn(replacement, text)
            if count > 0:
                text = new_text
                changed = True

        if changed and not dry_run:
            filepath.write_text(text, encoding="utf-8")

        return changed

    except Exception as e:
        print(f"   ❌ 오류 {filepath.relative_to(ROOT)}: {e}")
        return False


def main():
    """Import 문제 일괄 수정"""
    import sys

    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == "--apply":
        dry_run = False

    mode = "DRY-RUN" if dry_run else "APPLY"
    print(f"🔧 Import 치환 Pass3 ({mode})...")

    fixed_files = []
    total_fixes = 0

    # echo_engine 하위 모든 Python 파일
    for py_file in SRC.rglob("*.py"):
        if py_file.name.startswith("__"):
            continue

        if fix_imports_in_file(py_file, dry_run=dry_run):
            rel_path = str(py_file.relative_to(ROOT))
            fixed_files.append(rel_path)
            print(f"   📝 {'예상' if dry_run else '수정'}: {rel_path}")

    # 루트 레벨 주요 파일들
    for pattern in ["*.py", "echo*.py", "cosmos*.py"]:
        for py_file in ROOT.glob(pattern):
            if py_file.is_file() and not py_file.name.startswith("fix_"):
                if fix_imports_in_file(py_file, dry_run=dry_run):
                    rel_path = str(py_file.relative_to(ROOT))
                    fixed_files.append(rel_path)
                    print(f"   📝 {'예상' if dry_run else '수정'}: {rel_path}")

    print(f"\n✅ {mode} 완료:")
    print(f"   수정된 파일: {len(fixed_files)}개")

    if fixed_files:
        print(f"\n📋 수정된 파일 목록:")
        for filepath in sorted(fixed_files)[:20]:  # 상위 20개만
            print(f"   • {filepath}")
        if len(fixed_files) > 20:
            print(f"   ... 및 {len(fixed_files) - 20}개 더")

    if dry_run:
        print(f"\n💡 실제 적용: python {sys.argv[0]} --apply")
    else:
        print(f"\n✅ 실제 파일 변경 완료!")
        print(f"💡 다음: python echo_engine/evolve_min.py --health --fast")


if __name__ == "__main__":
    main()
