# echo_engine/assist/patcher.py
from __future__ import annotations
import os, re, shutil, subprocess, tempfile, time
from typing import List, Tuple, Optional

DIFF_HEADER = re.compile(r"^\+\+\+\s+(?:b/)?(.+)$")  # '+++ b/path' or '+++ path'

def is_unified_diff(text: str) -> bool:
    return "@@ " in text and ("--- " in text and "+++ " in text)

def files_from_diff(text: str) -> List[str]:
    targets = []
    for line in text.splitlines():
        m = DIFF_HEADER.match(line.strip())
        if m:
            targets.append(m.group(1).strip())
    return list(dict.fromkeys(targets))

def backup_files(files: List[str], out_dir: str = "health_backups") -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    snap = os.path.join(out_dir, f"snapshot_{ts}")
    for f in files:
        src = f
        dst = os.path.join(snap, f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(src):
            shutil.copy2(src, dst)
    return snap

def restore_backup(snapshot_dir: str):
    # Copy back all files from snapshot to repo
    for root, _, files in os.walk(snapshot_dir):
        for fn in files:
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, snapshot_dir)
            dst = rel
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

def _write_temp_diff(text: str) -> str:
    d = tempfile.mkdtemp(prefix="echo_diff_")
    path = os.path.join(d, "patch.diff")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path

def try_git_apply(diff_text: str) -> Tuple[bool, str]:
    if not shutil.which("git"):
        return False, "git-not-found"
    path = _write_temp_diff(diff_text)
    # --check 먼저
    chk = subprocess.run(["git","apply","--check",path], capture_output=True, text=True)
    if chk.returncode != 0:
        return False, f"git-apply-check-failed: {chk.stderr.strip()}"
    run = subprocess.run(["git","apply",path], capture_output=True, text=True)
    if run.returncode == 0:
        return True, "git-apply"
    return False, f"git-apply-failed: {run.stderr.strip()}"

def try_posix_patch(diff_text: str) -> Tuple[bool, str]:
    if not shutil.which("patch"):
        return False, "patch-not-found"
    path = _write_temp_diff(diff_text)
    dry = subprocess.run(["patch","-p0","--forward","--dry-run","-i",path], capture_output=True, text=True)
    if dry.returncode != 0:
        return False, f"patch-dry-run-failed: {dry.stderr.strip()}"
    run = subprocess.run(["patch","-p0","--forward","-i",path], capture_output=True, text=True)
    if run.returncode == 0:
        return True, "patch"
    return False, f"patch-failed: {run.stderr.strip()}"

def apply_unified_diff_text(diff_text: str) -> Tuple[bool, str]:
    if not is_unified_diff(diff_text):
        return False, "not-unified-diff"
    ok, how = try_git_apply(diff_text)
    if ok:
        return True, how
    ok, how = try_posix_patch(diff_text)
    return ok, how