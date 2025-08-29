# echo_engine/testtools/diff_suggester.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple
import datetime, io, difflib, re, os

@dataclass
class ProposedPatch:
    file: str
    diff_text: str
    note: str

def _read_lines(path: str) -> List[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception:
        return []

def _write_patch(out_path: str, patch: ProposedPatch) -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(patch.diff_text)
    return out_path

def _is_float_token(s: str) -> bool:
    try:
        float(s)
        return True
    except Exception:
        return False

def _suggest_assert_approx(line: str) -> Optional[str]:
    # assert a == b  →  assert a == pytest.approx(b, rel=1e-6)
    if "assert " in line and "==" in line:
        parts = line.strip().split()
        # 매우 단순 휴리스틱: "assert X == Y"
        try:
            i = parts.index("assert")
            j = parts.index("==")
            left = " ".join(parts[i+1:j])
            right = " ".join(parts[j+1:])
            # 숫자 비교로 추정되면 approx 제안
            if any(_is_float_token(tok) for tok in re.split(r"[^\d\.eE+-]", left+right)):
                return line.replace("== " + right, f"== pytest.approx({right}, rel=1e-6)")
        except Exception:
            return None
    return None

def _suggest_with_open(line: str) -> Optional[str]:
    # f = open(...); → with open(...) as f:
    m = re.search(r"^\s*(\w+)\s*=\s*open\((.+)\)", line)
    if m:
        var = m.group(1)
        inner = m.group(2)
        return f"with open({inner}) as {var}:\n"
    return None

def propose_patch_for_line(path: str, line_no: int) -> Optional[ProposedPatch]:
    lines = _read_lines(path)
    if not lines or line_no < 1 or line_no > len(lines):
        return None
    orig = lines[line_no-1]
    cand = _suggest_assert_approx(orig) or _suggest_with_open(orig)
    if not cand:
        # 제안 불가: 가이드용 TODO 패치 생성
        cand = orig  # 동일 라인 유지 (패치 포맷을 위해)
        note = "No heuristic fix; please edit manually (skeleton diff)."
    else:
        note = "Heuristic fix applied."

    new_lines = lines.copy()
    new_lines[line_no-1] = cand

    diff = difflib.unified_diff(
        lines, new_lines,
        fromfile=path, tofile=path,
        lineterm=""
    )
    diff_text = "\n".join(diff) + "\n"
    return ProposedPatch(file=path, diff_text=diff_text, note=note)

def write_patch_file(patch: ProposedPatch, out_dir: str = "health_reports") -> str:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(out_dir, f"proposed_patch_{ts}.diff")
    return _write_patch(out, patch)