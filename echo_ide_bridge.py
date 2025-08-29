#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Echo IDE Bridge — v1
CLI 명령어가 VS Code/Cursor를 직접 제어하는 브릿지 서버

핵심 기능:
- 파일 열기 + 라인 포커스 (code -g / cursor -g 자동 감지)
- 파일 쓰기/추가 (백업 포함)
- Git/patch 이중 적용 시스템 (실패 시 명시적 에러)
- watchdog 파일 모니터링 (향후 자동 동기화)
- RESTful API (FastAPI)

실행:
  pip install fastapi uvicorn watchdog pydantic
  sudo apt-get install -y ripgrep patch
  python echo_ide_bridge.py

API 엔드포인트:
- POST /open-file {"file": "path", "line": 120}
- POST /write-file {"file": "path", "text": "content", "append": false}
- POST /apply-diff {"base": ".", "diff": "patch content"}
- GET /health
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Echo Editor 심볼 검색 연동
from echo_editor import EchoEditor

# v2 확장 모듈들
from context_probe import collect_context, format_context_report
from hint_engine import suggest, format_hints

# from test_focus import parse_test_failures, format_failure_summary  # 기존 간단 함수

# Test Focus CLI 통합
import sys

sys.path.append("tools")
from tools.test_focus import (
    parse_junit,
    run_pytest_and_save,
    find_latest_xml,
    analyze_from_xml,
    infer_impl_from_trace,
)
from change_tracker import (
    git_last_patch_changes,
    parse_unified_diff_text,
    get_changed_files_summary,
)


# ────────────────────────────── Models ──────────────────────────────
class OpenFileRequest(BaseModel):
    file: str
    line: Optional[int] = None


class WriteFileRequest(BaseModel):
    file: str
    text: str
    append: bool = False
    backup: bool = True


class ApplyDiffRequest(BaseModel):
    base: str = "."
    diff: str


class RevealSymbolRequest(BaseModel):
    symbol: str
    root: str = "."
    file_patterns: Optional[list] = None


class ContextRequest(BaseModel):
    start: str = "."


class AnalyzeErrorRequest(BaseModel):
    text: str


class HintRequest(BaseModel):
    text: str


class JumpToFailedTestRequest(BaseModel):
    text: str
    open_first: bool = True
    framework: Optional[str] = None


class TestFocusRequest(BaseModel):
    pytest_args: str = "-q --maxfail=50"
    xml_file: Optional[str] = None
    with_context: bool = False
    show_diff: bool = False
    related_tests: bool = False
    open_editor: bool = False


class JumpToChangesRequest(BaseModel):
    root: str = "."
    diff_text: Optional[str] = None
    open_first: bool = True


class HealthCheckRequest(BaseModel):
    with_ports: bool = False


class FocusSeqRequest(BaseModel):
    items: list[dict]  # [{"path": str, "lines": [int,...]}]
    step: bool = False


class HealthResponse(BaseModel):
    status: str
    ide_detected: Optional[str]
    tools: Dict[str, bool]


# ────────────────────────────── Setup ──────────────────────────────
app = FastAPI(title="Echo IDE Bridge", version="1.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Echo Editor 인스턴스
echo_editor = EchoEditor()


# ────────────────────────────── Utilities ──────────────────────────────
def detect_ide() -> Optional[str]:
    """IDE 자동 감지: VS Code > Cursor > None"""
    if shutil.which("code"):
        return "code"
    elif shutil.which("cursor"):
        return "cursor"
    return None


def run_command(cmd: list, capture=True, cwd=None) -> tuple[int, str, str]:
    """명령 실행 래퍼"""
    try:
        result = subprocess.run(
            cmd, capture_output=capture, text=True, cwd=cwd, timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return -1, "", str(e)


def check_tool_availability() -> Dict[str, bool]:
    """필수 도구 가용성 체크"""
    tools = {}
    for tool in ["git", "patch", "rg"]:
        tools[tool] = shutil.which(tool) is not None
    return tools


# ────────────────────────────── Core Functions ──────────────────────────────
def open_file_in_ide(file_path: str, line: Optional[int] = None) -> dict:
    """파일을 IDE에서 열기 + 라인 포커스"""
    ide = detect_ide()
    if not ide:
        raise HTTPException(status_code=500, detail="No IDE detected (code/cursor)")

    # 절대 경로 변환
    abs_path = Path(file_path).resolve()
    if not abs_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    # 명령 구성
    if line:
        cmd = [ide, "-g", f"{abs_path}:{line}"]
    else:
        cmd = [ide, str(abs_path)]

    returncode, stdout, stderr = run_command(cmd)

    if returncode != 0:
        logger.error(f"IDE open failed: {stderr}")
        raise HTTPException(status_code=500, detail=f"IDE open failed: {stderr}")

    return {
        "success": True,
        "ide": ide,
        "file": str(abs_path),
        "line": line,
        "message": f"Opened in {ide}",
    }


def write_file_content(
    file_path: str, text: str, append: bool = False, backup: bool = True
) -> dict:
    """파일 쓰기/추가 (백업 포함)"""
    abs_path = Path(file_path).resolve()

    # 백업 생성
    backup_path = None
    if backup and abs_path.exists():
        backup_path = abs_path.with_suffix(abs_path.suffix + ".backup")
        shutil.copy2(abs_path, backup_path)

    try:
        # 디렉터리 생성
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        # 파일 쓰기
        mode = "a" if append else "w"
        with open(abs_path, mode, encoding="utf-8") as f:
            f.write(text)

        return {
            "success": True,
            "file": str(abs_path),
            "mode": "append" if append else "write",
            "backup": str(backup_path) if backup_path else None,
            "bytes_written": len(text.encode("utf-8")),
        }

    except Exception as e:
        # 백업 복원
        if backup_path and backup_path.exists():
            shutil.copy2(backup_path, abs_path)
        raise HTTPException(status_code=500, detail=f"Write failed: {e}")


def apply_diff_patch(base_path: str, diff_content: str) -> dict:
    """Git/patch 이중 적용 시스템"""
    base_path = Path(base_path).resolve()

    if not base_path.exists():
        raise HTTPException(status_code=404, detail=f"Base path not found: {base_path}")

    # 1차: git apply 시도
    with tempfile.NamedTemporaryFile(mode="w", suffix=".patch", delete=False) as f:
        f.write(diff_content)
        patch_file = f.name

    try:
        # Git apply 시도
        returncode, stdout, stderr = run_command(
            ["git", "apply", "--verbose", patch_file], cwd=base_path
        )

        if returncode == 0:
            return {
                "success": True,
                "method": "git apply",
                "message": f"Patch applied successfully via git apply\n{stdout}",
                "base": str(base_path),
            }

        logger.warning(f"git apply failed: {stderr}")

        # 2차: patch 시도
        returncode, stdout, stderr = run_command(
            ["patch", "-p1", "-i", patch_file], cwd=base_path
        )

        if returncode == 0:
            return {
                "success": True,
                "method": "patch",
                "message": f"Patch applied successfully via patch\n{stdout}",
                "base": str(base_path),
            }

        # 둘 다 실패
        raise HTTPException(
            status_code=500,
            detail=f"Both git apply and patch failed.\nGit error: {stderr}\nPatch error: {stderr}",
        )

    finally:
        # 임시 파일 정리
        try:
            os.unlink(patch_file)
        except:
            pass


# ────────────────────────────── API Endpoints ──────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """시스템 상태 확인"""
    ide = detect_ide()
    tools = check_tool_availability()

    return HealthResponse(
        status="healthy" if ide and tools.get("git", False) else "degraded",
        ide_detected=ide,
        tools=tools,
    )


@app.post("/open-file")
async def open_file(request: OpenFileRequest):
    """파일 열기 + 라인 포커스"""
    return open_file_in_ide(request.file, request.line)


@app.post("/write-file")
async def write_file(request: WriteFileRequest):
    """파일 쓰기/추가"""
    return write_file_content(
        request.file, request.text, request.append, request.backup
    )


@app.post("/apply-diff")
async def apply_diff(request: ApplyDiffRequest):
    """diff/patch 적용"""
    return apply_diff_patch(request.base, request.diff)


@app.post("/reveal-symbol")
async def reveal_symbol(request: RevealSymbolRequest):
    """심볼 검색 + IDE 포커스"""
    try:
        # 심볼 검색
        matches = echo_editor.search_symbol(
            request.symbol, request.root, request.file_patterns, prefer_definitions=True
        )

        if not matches:
            raise HTTPException(
                status_code=404,
                detail=f"Symbol '{request.symbol}' not found in {request.root}",
            )

        # 최고 매치로 IDE 포커스
        best_match = matches[0]
        ide_result = open_file_in_ide(str(best_match.path), best_match.line_number)

        return {
            "success": True,
            "symbol": request.symbol,
            "total_matches": len(matches),
            "focused": {
                "path": str(best_match.path),
                "line": best_match.line_number,
                "type": best_match.symbol_type,
                "content": best_match.raw_line,
            },
            "ide_result": ide_result,
            "all_matches": [
                {
                    "path": str(m.path),
                    "line": m.line_number,
                    "type": m.symbol_type,
                    "content": m.raw_line,
                }
                for m in matches[:5]  # 상위 5개만
            ],
        }

    except Exception as e:
        logger.error(f"Symbol reveal failed: {e}")
        raise HTTPException(status_code=500, detail=f"Symbol reveal failed: {e}")


@app.post("/context")
async def context_info(request: ContextRequest):
    """컨텍스트 정보 수집"""
    try:
        report = collect_context(request.start)
        return {
            "success": True,
            "report": {
                "root": report.root,
                "git": {"branch": report.git.branch, "commits": report.git.commits},
                "stack": {
                    "managers": report.stack.managers,
                    "langs": report.stack.langs,
                },
                "has_vscode": report.has_vscode,
                "has_cursor": report.has_cursor,
            },
            "formatted": format_context_report(report),
        }
    except Exception as e:
        logger.error(f"Context collection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Context collection failed: {e}")


@app.post("/analyze-error")
async def analyze_error(request: AnalyzeErrorRequest):
    """에러 로그 분석 및 IDE 포커스"""
    try:
        text = request.text

        # Python traceback 패턴
        import re

        py_pattern = re.compile(r'File "(?P<path>.+?)", line (?P<line>\d+)')
        # Node.js stack trace 패턴
        node_pattern = re.compile(r"\((?P<path>[^:]+):(?P<line>\d+):\d+\)")

        target = None
        matches = py_pattern.findall(text) or node_pattern.findall(text)

        if matches:
            # 첫 번째 매치 사용 (최상단 프레임)
            if isinstance(matches[0], tuple):
                path, line = matches[0][0], int(matches[0][1])
            else:
                path, line = matches[0], 1

            try:
                # IDE에서 파일 열기 시도
                ide_result = open_file_in_ide(path, line)
                target = {"path": path, "line": line, "opened": True}
            except Exception as open_error:
                logger.warning(f"Failed to open file in IDE: {open_error}")
                target = {"path": path, "line": line, "opened": False}

        return {
            "success": bool(target),
            "target": target,
            "total_frames": len(matches) if matches else 0,
        }

    except Exception as e:
        logger.error(f"Error analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Error analysis failed: {e}")


@app.post("/hint")
async def get_hints(request: HintRequest):
    """에러 텍스트 기반 힌트 제공"""
    try:
        hints = suggest(request.text)
        return {
            "success": True,
            "hints": [
                {
                    "title": h.title,
                    "steps": h.steps,
                    "category": h.category,
                    "confidence": h.confidence,
                }
                for h in hints
            ],
            "formatted": format_hints(hints),
        }
    except Exception as e:
        logger.error(f"Hint generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Hint generation failed: {e}")


@app.post("/jump-to-failed-test")
async def jump_to_failed_test(request: JumpToFailedTestRequest):
    """테스트 실패 지점으로 IDE 포커스 이동 (기존 버전)"""
    try:
        # 간단한 텍스트 기반 파싱 대신 test_focus 모듈 사용
        import re

        # pytest 실패 패턴 파싱
        failures = []
        py_failures = re.findall(r"FAILED (.*?)::(.*?) - (.*)", request.text)

        for match in py_failures:
            file_path, test_name, error = match
            failures.append(
                {
                    "path": file_path,
                    "line": 1,
                    "test_id": f"{file_path}::{test_name}",
                    "error_type": "AssertionError",
                    "error_message": error,
                }
            )

        opened = None
        if request.open_first and failures:
            first_failure = failures[0]
            try:
                ide_result = open_file_in_ide(
                    first_failure["path"], first_failure["line"]
                )
                opened = {
                    "path": first_failure["path"],
                    "line": first_failure["line"],
                    "test_id": first_failure["test_id"],
                    "error_type": first_failure["error_type"],
                }
            except Exception as open_error:
                logger.warning(f"Failed to open test file: {open_error}")
                opened = {
                    "path": first_failure["path"],
                    "line": first_failure["line"],
                    "opened": False,
                }

        return {
            "success": bool(failures),
            "opened": opened,
            "total_failures": len(failures),
            "failures": failures[:10],
            "formatted": f"Found {len(failures)} test failures",
        }

    except Exception as e:
        logger.error(f"Test failure analysis failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Test failure analysis failed: {e}"
        )


@app.post("/jump-to-changes")
async def jump_to_changes(request: JumpToChangesRequest):
    """변경 지점으로 IDE 점프"""
    try:
        # 변경사항 추출
        if request.diff_text:
            changes = parse_unified_diff_text(request.diff_text)
        else:
            changes = git_last_patch_changes(request.root)

        opened = None
        if request.open_first and changes:
            first_change = changes[0]
            first_line = first_change.lines[0] if first_change.lines else 1
            try:
                ide_result = open_file_in_ide(first_change.path, first_line)
                opened = {"path": first_change.path, "line": first_line}
            except Exception as open_error:
                logger.warning(f"Failed to open file in IDE: {open_error}")
                opened = {
                    "path": first_change.path,
                    "line": first_line,
                    "opened": False,
                }

        summary = get_changed_files_summary(changes)

        return {
            "success": bool(changes),
            "opened": opened,
            "changes": [{"path": c.path, "lines": c.lines} for c in changes],
            "summary": summary,
        }

    except Exception as e:
        logger.error(f"Jump to changes failed: {e}")
        raise HTTPException(status_code=500, detail=f"Jump to changes failed: {e}")


@app.post("/health-check")
async def health_check(request: HealthCheckRequest):
    """시스템 헬스체크 및 포트 확인"""
    try:
        import socket

        # 기본 도구 확인
        tools_status = {
            "git": shutil.which("git") is not None,
            "rg": shutil.which("rg") is not None,
            "patch": shutil.which("patch") is not None,
            "pytest": shutil.which("pytest") is not None,
        }

        # IDE 확인
        ide_status = {
            "code": shutil.which("code") is not None,
            "cursor": shutil.which("cursor") is not None,
        }

        report = {
            "tools": tools_status,
            "editor": ide_status,
            "ide_detected": detect_ide(),
        }

        # 포트 상태 확인
        if request.with_ports:

            def _is_port_open(port: int) -> bool:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.settimeout(0.2)
                    result = sock.connect_ex(("127.0.0.1", port))
                    return result == 0
                except Exception:
                    return False
                finally:
                    sock.close()

            port_status = {}
            test_ports = [8000, 8001, 8002, 9009, 8501, 8080]
            for port in test_ports:
                port_status[port] = _is_port_open(port)

            report["ports"] = port_status

        # 전체 상태 판단
        overall_status = "healthy"
        if not report["ide_detected"]:
            overall_status = "degraded"
        elif not tools_status.get("git", False):
            overall_status = "degraded"

        return {"success": True, "status": overall_status, "report": report}

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@app.post("/focus-seq")
async def focus_seq(request: FocusSeqRequest):
    """순차 포커스 - 다중 파일/라인을 순차적으로 IDE에서 열기"""
    try:
        ide = detect_ide()
        if not ide:
            raise HTTPException(status_code=404, detail="No IDE detected")
        
        opened = []
        for item in request.items:
            path = item.get("path")
            lines = item.get("lines", [1])
            line = lines[0] if lines else 1
            
            try:
                # IDE에서 파일 열기
                cmd = [ide, "-g", f"{path}:{line}"]
                result = subprocess.run(cmd, check=False, capture_output=True, text=True)
                
                if result.returncode == 0:
                    opened.append({"path": path, "line": line, "success": True})
                else:
                    # 라인 없이 다시 시도
                    cmd = [ide, path]
                    subprocess.run(cmd, check=False)
                    opened.append({"path": path, "line": None, "success": True})
                    
            except Exception as e:
                logger.warning(f"Failed to open {path}:{line} - {e}")
                opened.append({"path": path, "line": line, "success": False, "error": str(e)})
            
            # step=false면 즉시 다음으로 진행 (IDE가 탭 스택으로 누적)
            # step=true면 향후 키 입력 대기 기능 추가 가능
        
        success_count = sum(1 for item in opened if item.get("success"))
        return {
            "success": success_count > 0,
            "opened": opened,
            "total": len(request.items),
            "success_count": success_count,
            "ide": ide
        }
        
    except Exception as e:
        logger.error(f"Focus seq failed: {e}")
        raise HTTPException(status_code=500, detail=f"Focus seq failed: {e}")


@app.post("/test-focus")
async def test_focus(request: TestFocusRequest):
    """테스트 포커스 통합 - pytest 실행 + JUnit XML 분석 + IDE 점프"""
    try:
        # 1. XML 파일 결정
        if request.xml_file:
            from pathlib import Path

            xml_path = Path(request.xml_file)
            if not xml_path.exists():
                raise HTTPException(
                    status_code=404, detail=f"XML file not found: {request.xml_file}"
                )
        else:
            # pytest 실행 + XML 생성
            xml_path = run_pytest_and_save(request.pytest_args)

        # 2. JUnit XML 파싱
        failures = parse_junit(xml_path)

        # 각 실패에 대해 구현 파일 위치 추론
        for failure in failures:
            impl_file, impl_line = infer_impl_from_trace(failure.traceback)
            failure.impl_file = impl_file
            failure.impl_line = impl_line

        if not failures:
            return {
                "success": True,
                "formatted": "✅ No test failures found. All tests passed!",
                "failures": [],
                "focused": None,
            }

        # 3. IDE에서 첫 번째 실패 열기
        focused = None
        if request.open_editor and failures:
            first_failure = failures[0]
            try:
                ide_result = open_file_in_ide(
                    first_failure.test_file, first_failure.test_line
                )
                focused = {
                    "file": first_failure.test_file,
                    "line": first_failure.test_line,
                    "test_func": first_failure.test_func,
                }

                # 구현 파일도 열기
                if first_failure.impl_file and first_failure.impl_line:
                    impl_result = open_file_in_ide(
                        first_failure.impl_file, first_failure.impl_line
                    )
                    focused["impl_file"] = first_failure.impl_file
                    focused["impl_line"] = first_failure.impl_line

            except Exception as open_error:
                logger.warning(f"Failed to open in IDE: {open_error}")

        # 4. 결과 포매팅
        formatted_output = (
            f"🔥 Test Focus Analysis - {len(failures)} failures found\n\n"
        )

        for i, failure in enumerate(failures[:5], 1):
            formatted_output += f"🎯 {i}. {failure.test_func}\n"
            formatted_output += f"   📄 {failure.test_file}:{failure.test_line}\n"
            if failure.message:
                formatted_output += f"   ❌ {failure.message[:100]}...\n"
            formatted_output += "\n"

        if len(failures) > 5:
            formatted_output += f"... and {len(failures) - 5} more failures\n"

        return {
            "success": True,
            "formatted": formatted_output,
            "failures": [
                {
                    "test_file": f.test_file,
                    "test_line": f.test_line,
                    "test_func": f.test_func,
                    "message": f.message,
                    "impl_file": f.impl_file,
                    "impl_line": f.impl_line,
                }
                for f in failures
            ],
            "focused": focused,
            "xml_path": str(xml_path),
        }

    except Exception as e:
        logger.error(f"Test focus failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test focus failed: {e}")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "Echo IDE Bridge",
        "version": "1.0",
        "status": "running",
        "endpoints": [
            "/health",
            "/open-file",
            "/write-file",
            "/apply-diff",
            "/reveal-symbol",
            "/context",
            "/analyze-error",
            "/hint",
            "/jump-to-failed-test",
            "/test-focus",
            "/jump-to-changes",
            "/health-check",
        ],
    }


# ────────────────────────────── Main Server ──────────────────────────────
def main():
    """브릿지 서버 시작"""
    logger.info("🎨 Echo IDE Bridge v1 Starting...")

    # 환경 체크
    ide = detect_ide()
    tools = check_tool_availability()

    logger.info(f"IDE detected: {ide or 'None'}")
    logger.info(f"Tools available: {tools}")

    if not ide:
        logger.warning("⚠️  No IDE detected. Install VS Code or Cursor.")

    if not tools.get("git"):
        logger.warning("⚠️  Git not found. Some features may not work.")

    # 서버 시작
    logger.info("🚀 Server starting on http://localhost:9009")
    uvicorn.run(
        "echo_ide_bridge:app",
        host="127.0.0.1",
        port=9009,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
