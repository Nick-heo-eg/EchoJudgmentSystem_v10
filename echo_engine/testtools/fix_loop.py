# echo_engine/testtools/fix_loop.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List
import subprocess, os

from .failure_focus import jump_to_first_failure
from .diff_suggester import propose_patch_for_line, write_patch_file
from ..assist.patcher import files_from_diff, backup_files, restore_backup, apply_unified_diff_text

@dataclass
class FixResult:
    applied: bool
    method: str
    snapshot: Optional[str]
    test_rc: int
    patch_file: Optional[str]
    message: str

def run_cmd(cmd: str) -> int:
    r = subprocess.run(cmd.split(), capture_output=True, text=True)
    return r.returncode

def auto_fix_once(
    test_cmd: str = "pytest -q --maxfail=1",
    junit_glob: Optional[str] = None,
    open_editor: bool = False
) -> FixResult:
    # 1) 실패 포인트 파악
    spot = jump_to_first_failure(cmd=test_cmd, junit_glob=junit_glob, open_editor=open_editor)
    if not spot:
        return FixResult(False, "n/a", None, 0, None, "No failure detected.")
    # 2) 힌트 패치 생성
    patch = propose_patch_for_line(spot.path, spot.line)
    if not patch:
        return FixResult(False, "n/a", None, 1, None, "Cannot propose a patch for this location.")
    patch_file = write_patch_file(patch)

    # 3) 백업
    targets = files_from_diff(patch.diff_text) or [spot.path]
    snap = backup_files(targets)

    # 4) 적용
    ok, method = apply_unified_diff_text(patch.diff_text)
    if not ok:
        # 롤백 (변경 없을 수 있지만 안전차)
        restore_backup(snap)
        return FixResult(False, method, snap, 1, patch_file, f"Patch apply failed: {method}")

    # 5) 재테스트
    rc = run_cmd(test_cmd)
    if rc != 0:
        # 6) 롤백
        restore_backup(snap)
        return FixResult(False, method, snap, rc, patch_file, "Retest failed; rolled back.")
    return FixResult(True, method, snap, rc, patch_file, "Retest passed; patch kept.")