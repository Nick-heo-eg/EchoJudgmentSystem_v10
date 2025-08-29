# test_focus.py
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Failure:
    path: str
    line: Optional[int]
    test_id: Optional[str]
    error_type: Optional[str] = None
    error_message: Optional[str] = None


# pytest 패턴들
# 패턴 1: FAILED 요약 줄
RX_SUMMARY = re.compile(
    r"^FAILED\s+(?P<path>[\w\./\\-]+\.py)(?:::(?P<class>[\w_]+))?(?:::(?P<method>[\w_]+))?\s*-\s*(?P<error>.*)$",
    re.MULTILINE,
)

# 패턴 2: traceback 프레임 (path:line: in function)
RX_FRAME = re.compile(
    r"^(?P<path>[^\s:][^:]*\.py):(?P<line>\d+):\s+in\s+(?P<fn>[\w_]+)$", re.MULTILINE
)

# 패턴 3: 직접 실패 라인 (> assertion 등)
RX_ASSERTION = re.compile(
    r"^(?P<path>[^\s:][^:]*\.py):(?P<line>\d+):\s*$\n.*?>\s*(?P<assertion>.*)$",
    re.MULTILINE | re.DOTALL,
)

# 패턴 4: 에러 타입 추출
RX_ERROR_TYPE = re.compile(
    r"(?P<type>AssertionError|ValueError|TypeError|AttributeError|ImportError|KeyError|IndexError)(?::\s*(?P<msg>.*))?"
)

# Node.js/Jest 패턴들
RX_JEST_FAIL = re.compile(
    r"^\s*●\s+(?P<suite>.*?)\s*›\s*(?P<test>.*?)$.*?at\s+(?P<path>[^\s]+):(?P<line>\d+):(?P<col>\d+)",
    re.MULTILINE | re.DOTALL,
)

# Go test 패턴
RX_GO_FAIL = re.compile(
    r"^\s*---\s*FAIL:\s*(?P<test>[\w_/]+).*?(?P<path>[\w\./\\-]+\.go):(?P<line>\d+):",
    re.MULTILINE | re.DOTALL,
)


def parse_pytest_failures(text: str) -> List[Failure]:
    """pytest 출력에서 실패 정보 추출"""
    failures: List[Failure] = []
    seen_paths = set()  # 중복 방지

    # 1) traceback 프레임 우선 (가장 정확한 라인 번호)
    for match in RX_FRAME.finditer(text):
        path = match.group("path")
        line = int(match.group("line"))
        fn_name = match.group("fn")

        # 테스트 함수인지 확인 (test_ 또는 Test로 시작)
        if fn_name.startswith(("test_", "Test")):
            key = (path, line)
            if key not in seen_paths:
                failures.append(
                    Failure(
                        path=path,
                        line=line,
                        test_id=fn_name,
                        error_type=None,
                        error_message=None,
                    )
                )
                seen_paths.add(key)

    # 2) FAILED 요약 줄 (라인 번호가 없지만 테스트 ID가 정확)
    for match in RX_SUMMARY.finditer(text):
        path = match.group("path")
        class_name = match.group("class")
        method_name = match.group("method")
        error_text = match.group("error").strip()

        # 테스트 ID 구성
        test_id = method_name
        if class_name:
            test_id = f"{class_name}::{method_name}"

        # 에러 타입/메시지 추출
        error_match = RX_ERROR_TYPE.search(error_text)
        error_type = error_match.group("type") if error_match else None
        error_message = error_match.group("msg") if error_match else error_text

        # 이미 같은 경로가 있으면 정보만 보완
        existing = next(
            (f for f in failures if f.path == path and f.test_id == test_id), None
        )
        if existing:
            if not existing.error_type:
                existing.error_type = error_type
            if not existing.error_message:
                existing.error_message = error_message
        else:
            failures.append(
                Failure(
                    path=path,
                    line=None,
                    test_id=test_id,
                    error_type=error_type,
                    error_message=error_message,
                )
            )

    return failures


def parse_jest_failures(text: str) -> List[Failure]:
    """Jest/Node.js 테스트 실패 파싱"""
    failures: List[Failure] = []

    for match in RX_JEST_FAIL.finditer(text):
        path = match.group("path")
        line = int(match.group("line"))
        suite = match.group("suite")
        test_name = match.group("test")

        failures.append(
            Failure(
                path=path,
                line=line,
                test_id=f"{suite} > {test_name}",
                error_type="Jest",
            )
        )

    return failures


def parse_go_test_failures(text: str) -> List[Failure]:
    """Go test 실패 파싱"""
    failures: List[Failure] = []

    for match in RX_GO_FAIL.finditer(text):
        path = match.group("path")
        line = int(match.group("line"))
        test_name = match.group("test")

        failures.append(
            Failure(path=path, line=line, test_id=test_name, error_type="Go test")
        )

    return failures


def parse_test_failures(
    text: str, test_framework: Optional[str] = None
) -> List[Failure]:
    """다양한 테스트 프레임워크의 실패 파싱"""
    if test_framework == "pytest":
        return parse_pytest_failures(text)
    elif test_framework == "jest":
        return parse_jest_failures(text)
    elif test_framework == "go":
        return parse_go_test_failures(text)
    else:
        # 자동 감지 시도
        failures = []

        # pytest 시도
        pytest_failures = parse_pytest_failures(text)
        if pytest_failures:
            failures.extend(pytest_failures)

        # Jest 시도
        jest_failures = parse_jest_failures(text)
        if jest_failures:
            failures.extend(jest_failures)

        # Go test 시도
        go_failures = parse_go_test_failures(text)
        if go_failures:
            failures.extend(go_failures)

        return failures


def format_failure_summary(failures: List[Failure]) -> str:
    """실패 목록을 읽기 쉽게 포맷"""
    if not failures:
        return "✅ 테스트 실패를 찾지 못했습니다."

    lines = [f"🔴 {len(failures)}개 테스트 실패 발견:"]

    for i, failure in enumerate(failures, 1):
        location = f"{failure.path}:{failure.line}" if failure.line else failure.path
        test_info = f" [{failure.test_id}]" if failure.test_id else ""
        error_info = f" - {failure.error_type}" if failure.error_type else ""

        lines.append(f"{i}. {location}{test_info}{error_info}")

        if failure.error_message and len(failure.error_message) < 100:
            lines.append(f"   💬 {failure.error_message}")

    return "\n".join(lines)


__all__ = [
    "Failure",
    "parse_test_failures",
    "parse_pytest_failures",
    "format_failure_summary",
]
