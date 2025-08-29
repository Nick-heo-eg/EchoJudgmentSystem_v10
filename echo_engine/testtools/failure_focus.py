# echo_engine/testtools/failure_focus.py
from __future__ import annotations
import os, re, glob, subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional, Tuple, List, Iterable

@dataclass
class FailureSpot:
    path: str
    line: int
    message: str

def _which(name: str) -> Optional[str]:
    from shutil import which
    return which(name)

def _open_in_editor(path: str, line: int, editors: List[str]) -> bool:
    for ed in editors:
        exe = _which(ed)
        if not exe:
            continue
        try:
            if ed in ("code","cursor"):
                subprocess.run([exe, "-g", f"{path}:{line}"], check=False)
            elif ed == "pycharm":
                subprocess.run([exe, "--line", str(line), path], check=False)
            return True
        except Exception:
            continue
    return False

def _run_test_cmd(cmd: str, junit_path: Optional[str]) -> Tuple[int, str]:
    parts = cmd.split()
    if junit_path and "--junitxml" not in parts:
        parts += ["--junitxml", junit_path]
    r = subprocess.run(parts, capture_output=True, text=True)
    return r.returncode, r.stdout + "\n" + r.stderr

def _iter_failure_nodes(root) -> Iterable[ET.Element]:
    # pytest / unittest-xml-reporting 모두 지원: testcase/failure|error
    for tc in root.iter("testcase"):
        for child in tc:
            if child.tag in ("failure","error"):
                yield child

def _parse_failure(child: ET.Element) -> Optional[FailureSpot]:
    # 우선 trace 안의 File "x", line N 패턴
    txt = (child.text or "")[:10000]
    m = re.search(r'File "(.+?)", line (\d+)', txt)
    if m:
        return FailureSpot(path=m.group(1), line=int(m.group(2)), message=child.get("message") or child.tag)
    # 속성 기반(일부 리포터는 file, line 속성 사용)
    f = child.get("file"); ln = child.get("line")
    if f and ln and ln.isdigit():
        return FailureSpot(path=f, line=int(ln), message=child.get("message") or child.tag)
    return None

def _parse_junit_file(path: str) -> Optional[FailureSpot]:
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        for child in _iter_failure_nodes(root):
            spot = _parse_failure(child)
            if spot:
                return spot
    except Exception:
        return None
    return None

def _parse_junit_many(glob_pat: str) -> Optional[FailureSpot]:
    # 다중 샤드(xdist) 지원: 일단 첫 실패를 반환
    for p in sorted(glob.glob(glob_pat)):
        spot = _parse_junit_file(p)
        if spot:
            return spot
    return None

def _parse_stdout_fallback(stdout: str) -> Optional[FailureSpot]:
    m = re.search(r'File "(.+?)", line (\d+)', stdout)
    if m:
        return FailureSpot(path=m.group(1), line=int(m.group(2)), message="stdout-trace")
    m2 = re.search(r"(.*?)\((.*?)\)\s+\.\.\.\s+FAIL", stdout)
    if m2:
        return FailureSpot(path=m2.group(2), line=1, message="unittest-fail")
    return None

def jump_to_first_failure(
    cmd: str = "pytest -q",
    junit_path: Optional[str] = "health_reports/last_pytest.xml",
    junit_glob: Optional[str] = None,
    editors: Optional[List[str]] = None,
    open_editor: bool = True
) -> Optional[FailureSpot]:
    os.makedirs("health_reports", exist_ok=True)
    rc, out = _run_test_cmd(cmd, junit_path if (junit_path and not junit_glob) else None)

    spot = None
    if junit_glob:
        spot = _parse_junit_many(junit_glob)
    if (not spot) and junit_path:
        spot = _parse_junit_file(junit_path)
    if not spot:
        spot = _parse_stdout_fallback(out)

    if spot and open_editor:
        _open_in_editor(spot.path, spot.line, editors or ["cursor","code","pycharm"])
    return spot