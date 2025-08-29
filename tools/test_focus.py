#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Failure Focus — single-file CLI
- analyze: run pytest with JUnit XML, then analyze failures
- from-xml: analyze given junit xml
- last: re-analyze the most recent xml in /tmp

No external deps. Optional VS Code integration via `code`.
"""
from __future__ import annotations
import argparse
import os
import re
import sys
import subprocess
import tempfile
import time
import glob
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Tuple, Dict
import difflib
import json

TMP_DIR = Path(tempfile.gettempdir())
DEFAULT_XML = TMP_DIR / "pytest_report.latest.xml"

# ------------------------- utils -------------------------


def sh(cmd: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    p = subprocess.Popen(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    out, err = p.communicate()
    return p.returncode, out, err


ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_BLUE = "\033[34m"
ANSI_RESET = "\033[0m"


def color(txt: str, c: str) -> str:
    return f"{c}{txt}{ANSI_RESET}"


# ------------------------- junit parse -------------------------
class Failure:
    def __init__(
        self,
        test_file: str,
        test_line: int,
        test_func: str,
        message: str,
        traceback: str,
    ):
        self.test_file = test_file
        self.test_line = test_line
        self.test_func = test_func
        self.message = message
        self.traceback = traceback
        # filled later
        self.impl_file: Optional[str] = None
        self.impl_line: Optional[int] = None


def parse_junit(xml_path: Path) -> List[Failure]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    failures: List[Failure] = []
    # pytest's junit layout: testcase elements with failure/error children
    for tc in root.iter("testcase"):
        fail_node = None
        for child in tc:
            if child.tag in ("failure", "error"):
                fail_node = child
                break
        if fail_node is None:  # 명시적으로 None 체크
            continue
        classname = tc.get("classname", "")
        name = tc.get("name", "")
        file_attr = tc.get("file") or tc.get("filename")
        line_attr = tc.get("line")
        # fallback: try to infer from failure text
        message = (fail_node.get("message") or "").strip()
        text = (fail_node.text or "").strip()
        tb = text
        test_file, test_line = infer_test_location(
            file_attr, line_attr, message, text, classname
        )
        failures.append(Failure(test_file, test_line, name, message, tb))
    return failures


def infer_test_location(
    file_attr, line_attr, message, text, classname=None
) -> Tuple[str, int]:
    if file_attr and line_attr:
        try:
            return file_attr, int(line_attr)
        except Exception:
            pass

    # Try to find lines like: "File \"tests/test_x.py\", line 42, in test_..."
    pat = re.compile(r'File "([^"]+)", line (\d+)')
    for m in pat.finditer(message + "\n" + text):
        f, ln = m.group(1), int(m.group(2))
        if f.endswith(".py"):
            return f, ln

    # Try to infer from classname
    if classname and classname != "pytest":
        test_file = classname + ".py"
        # Look for specific line numbers in the text
        line_pat = re.compile(rf"{re.escape(test_file)}:(\d+):")
        m = line_pat.search(text)
        if m:
            return test_file, int(m.group(1))
        return test_file, 1

    # fallback
    return (file_attr or "unknown"), int(line_attr or 1)


# ------------------------- impl mapping -------------------------


def infer_impl_from_trace(tb: str) -> Tuple[Optional[str], Optional[int]]:
    # choose first non-test *.py frame
    pat = re.compile(r'File "([^"]+)", line (\d+), in (.+)')
    for m in pat.finditer(tb):
        f, ln, func = m.group(1), int(m.group(2)), m.group(3)
        path_norm = f.replace("\\", "/")
        if path_norm.endswith(".py") and not (
            "/tests/" in path_norm or os.path.basename(path_norm).startswith("test_")
        ):
            return f, ln
    return None, None


# ------------------------- context printing -------------------------


def read_context(path: str, line: int, n: int = 15) -> List[Tuple[int, str, bool]]:
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []
    start = max(1, line - n)
    end = min(len(lines), line + n)
    view = []
    for i in range(start, end + 1):
        is_focus = i == line
        view.append((i, lines[i - 1], is_focus))
    return view


def print_context(title: str, path: str, line: int, n: int = 15):
    header = f"\n== {title}: {path}:{line} =="
    print(color(header, ANSI_BLUE))
    ctx = read_context(path, line, n)
    if not ctx:
        print(color("(파일을 읽을 수 없습니다)", ANSI_YELLOW))
        return
    for ln, txt, focus in ctx:
        prefix = "➡" if focus else "  "
        mark = color("▶", ANSI_RED) if focus else " "
        print(f"{prefix} {ln:5d}{mark} {txt}")


# ------------------------- diff extraction -------------------------
_EXPECTED_ACTUAL_PATTERNS = [
    re.compile(
        r"expected\s*[:=]\s*(.+?)\s*[,;]??\s*but got\s*[:=]\s*(.+)$",
        re.IGNORECASE | re.MULTILINE,
    ),
    re.compile(
        r"Expected\s*:\s*(.+?)\s*\nActual\s*:\s*(.+)$", re.IGNORECASE | re.DOTALL
    ),
    re.compile(r"E\s+assert\s+(.+?)\s*==\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"AssertionError:\s*(.+?)\s*!=\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"assert\s+(.+?)\s*==\s*(.+)", re.IGNORECASE),
]


def try_extract_expected_actual(msg: str, tb: str) -> Optional[Tuple[str, str]]:
    blob = (msg or "").strip() + "\n" + (tb or "")
    for pat in _EXPECTED_ACTUAL_PATTERNS:
        m = pat.search(blob)
        if m:
            left, right = m.group(1).strip(), m.group(2).strip()
            return left, right
    return None


def normalize_for_diff(s: str) -> str:
    s = s.strip()
    # try json pretty
    try:
        parsed = json.loads(s)
        return json.dumps(parsed, indent=2, ensure_ascii=False, sort_keys=True)
    except Exception:
        pass
    # strip quotes wrapper
    if (s.startswith("'") and s.endswith("'")) or (
        s.startswith('"') and s.endswith('"')
    ):
        return s[1:-1]
    return s


def print_text_diff(title: str, a: str, b: str, write_tmp: bool, open_vscode: bool):
    print(color(f"\n== {title} ==", ANSI_BLUE))
    a_norm, b_norm = normalize_for_diff(a), normalize_for_diff(b)
    diff = difflib.unified_diff(
        a_norm.splitlines(),
        b_norm.splitlines(),
        fromfile="expected",
        tofile="actual",
        lineterm="",
    )

    has_diff = False
    for line in diff:
        has_diff = True
        if line.startswith("+") and not line.startswith("+++"):
            print(color(line, ANSI_GREEN))
        elif line.startswith("-") and not line.startswith("---"):
            print(color(line, ANSI_RED))
        else:
            print(line)

    if not has_diff:
        print(color("(값이 동일하여 diff가 없습니다)", ANSI_YELLOW))
        return

    if write_tmp:
        fn_a = TMP_DIR / f"expected_{int(time.time())}.txt"
        fn_b = TMP_DIR / f"actual_{int(time.time())}.txt"
        fn_a.write_text(a_norm, encoding="utf-8")
        fn_b.write_text(b_norm, encoding="utf-8")
        print(color(f"\n(saved) {fn_a}  ⇄  {fn_b}", ANSI_YELLOW))
        if open_vscode and shutil_which("code"):
            rc, out, err = sh(["code", "--diff", str(fn_a), str(fn_b)])
            if rc != 0:
                print(color(f"(VS Code --diff 실패) {err}", ANSI_YELLOW))


def shutil_which(cmd: str) -> Optional[str]:
    from shutil import which

    return which(cmd)


# ------------------------- related tests -------------------------
TEST_DIR_CANDIDATES = ["tests", "test", "unit_tests", "integration_tests"]


def find_related_tests(symbols: List[str]) -> List[Tuple[str, int, str]]:
    # returns list of (file, line, matched_text)
    roots = [Path(p) for p in TEST_DIR_CANDIDATES if Path(p).exists()]
    hits: List[Tuple[str, int, str]] = []
    if not roots:
        return hits

    # Create pattern from symbols
    valid_symbols = [s for s in symbols if s and len(s) > 2]  # 너무 짧은 심볼 제외
    if not valid_symbols:
        return hits

    pat = re.compile("|".join([re.escape(s) for s in valid_symbols]), re.IGNORECASE)

    for root in roots:
        for py in root.rglob("*.py"):
            try:
                lines = py.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                continue
            for i, line in enumerate(lines, start=1):
                if pat.search(line):
                    hits.append((str(py), i, line.strip()))
    return hits


# ------------------------- main flows -------------------------


def analyze_from_xml(
    xml_path: Path,
    with_context: bool,
    context_lines: int,
    show_diff: bool,
    related: bool,
    open_editor: bool,
):
    if not xml_path.exists():
        print(color(f"JUnit XML not found: {xml_path}", ANSI_RED))
        sys.exit(2)
    failures = parse_junit(xml_path)
    if not failures:
        print(color("No failures found. 🎉", ANSI_GREEN))
        return

    for idx, f in enumerate(failures, start=1):
        print(color(f"\n\n【Failure {idx}/{len(failures)}】", ANSI_YELLOW))
        print(f"Test : {f.test_func}")
        print(f"File : {f.test_file}:{f.test_line}")
        if f.message:
            print(f"Msg  : {f.message}")
        impl_file, impl_line = infer_impl_from_trace(f.traceback)
        f.impl_file, f.impl_line = impl_file, impl_line

        if with_context:
            if f.test_file and f.test_line:
                print_context("TEST CONTEXT", f.test_file, f.test_line, context_lines)
            if impl_file and impl_line:
                print_context("IMPL CONTEXT", impl_file, impl_line, context_lines)
            if open_editor and shutil_which("code"):
                # open both panes; VS Code will restore layout
                sh(["code", "-g", f"{f.test_file}:{f.test_line}"])
                if impl_file and impl_line:
                    sh(["code", "-g", f"{impl_file}:{impl_line}"])

        if show_diff:
            pair = try_extract_expected_actual(f.message, f.traceback)
            if pair:
                exp, act = pair
                print_text_diff(
                    "Assertion diff (expected vs actual)",
                    exp,
                    act,
                    write_tmp=True,
                    open_vscode=open_editor,
                )
            else:
                print(
                    color(
                        "\n(expected/actual 패턴을 메시지에서 찾지 못했습니다)",
                        ANSI_YELLOW,
                    )
                )

        if related:
            symbols = []
            # crude symbols: test func name, impl file stem
            if f.test_func:
                symbols.append(f.test_func)
                # 테스트 함수명에서 test_ 제거한 버전도 추가
                clean_name = f.test_func.replace("test_", "").replace("Test", "")
                if clean_name:
                    symbols.append(clean_name)
            if f.impl_file:
                symbols.append(Path(f.impl_file).stem)
            hits = find_related_tests(symbols)
            print(color("\n== RELATED TESTS ==", ANSI_BLUE))
            if not hits:
                print("(연관 후보 없음)")
            else:
                # 중복 제거 및 현재 실패 테스트 제외
                unique_hits = []
                seen_files = set()
                current_test_file = str(Path(f.test_file).resolve())

                for path, ln, text in hits:
                    abs_path = str(Path(path).resolve())
                    if abs_path == current_test_file:
                        continue  # 현재 실패한 테스트 제외
                    if abs_path not in seen_files:
                        seen_files.add(abs_path)
                        unique_hits.append((path, ln, text))

                for path, ln, text in unique_hits[:10]:  # 상위 10개만
                    print(f"- {path}:{ln} | {text[:100]}")


def run_pytest_and_save(pytest_args: str) -> Path:
    xml_path = DEFAULT_XML
    cmd = ["pytest", "--junitxml", str(xml_path)] + pytest_args.split()
    print(color(f"Running: {' '.join(cmd)}", ANSI_BLUE))
    rc, out, err = sh(cmd)
    # Save stdout/stderr for reference
    (TMP_DIR / "pytest_stdout.txt").write_text(out, encoding="utf-8")
    (TMP_DIR / "pytest_stderr.txt").write_text(err, encoding="utf-8")
    print(out)
    if rc != 0:
        print(color(f"pytest exit code: {rc}", ANSI_YELLOW))
    else:
        print(color("pytest finished.", ANSI_GREEN))
    return xml_path


def find_latest_xml() -> Optional[Path]:
    cands = list(TMP_DIR.glob("pytest_report*.xml"))
    if not cands:
        if DEFAULT_XML.exists():
            return DEFAULT_XML
        return None
    return max(cands, key=lambda p: p.stat().st_mtime)


# ------------------------- CLI -------------------------


def main():
    ap = argparse.ArgumentParser(
        description="Test Failure Focus — with-context/diff/related"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_an = sub.add_parser("analyze", help="run pytest and analyze")
    ap_an.add_argument(
        "--pytest-args", default="-q --maxfail=50", help="args passed to pytest"
    )
    ap_an.add_argument("--with-context", action="store_true")
    ap_an.add_argument("--context-lines", type=int, default=15)
    ap_an.add_argument("--show-diff", action="store_true")
    ap_an.add_argument("--related-tests", action="store_true")
    ap_an.add_argument(
        "--open", action="store_true", help="open editors/diff via VS Code if available"
    )

    ap_xml = sub.add_parser("from-xml", help="analyze from an existing junit xml")
    ap_xml.add_argument("xml", type=str)
    ap_xml.add_argument("--with-context", action="store_true")
    ap_xml.add_argument("--context-lines", type=int, default=15)
    ap_xml.add_argument("--show-diff", action="store_true")
    ap_xml.add_argument("--related-tests", action="store_true")
    ap_xml.add_argument("--open", action="store_true")

    ap_last = sub.add_parser("last", help="analyze the latest junit xml in tmp")
    ap_last.add_argument("--with-context", action="store_true")
    ap_last.add_argument("--context-lines", type=int, default=15)
    ap_last.add_argument("--show-diff", action="store_true")
    ap_last.add_argument("--related-tests", action="store_true")
    ap_last.add_argument("--open", action="store_true")

    args = ap.parse_args()

    if args.cmd == "analyze":
        xml_path = run_pytest_and_save(args.pytest_args)
        # also copy timestamped
        ts_xml = TMP_DIR / f"pytest_report_{int(time.time())}.xml"
        try:
            ts_xml.write_text(
                Path(xml_path).read_text(encoding="utf-8"), encoding="utf-8"
            )
        except Exception:
            pass
        analyze_from_xml(
            xml_path,
            args.with_context,
            args.context_lines,
            args.show_diff,
            args.related_tests,
            args.open,
        )
    elif args.cmd == "from-xml":
        analyze_from_xml(
            Path(args.xml),
            args.with_context,
            args.context_lines,
            args.show_diff,
            args.related_tests,
            args.open,
        )
    elif args.cmd == "last":
        xml = find_latest_xml()
        if not xml:
            print(color("No stored JUnit XML found in tmp.", ANSI_RED))
            sys.exit(2)
        analyze_from_xml(
            xml,
            args.with_context,
            args.context_lines,
            args.show_diff,
            args.related_tests,
            args.open,
        )


if __name__ == "__main__":
    main()
