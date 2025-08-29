"""
🌌 Plugin Sandbox for Amoeba v0.2
안전한 플러그인 임포트 및 실행 환경
"""

from __future__ import annotations

import importlib.util
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional

log = logging.getLogger("amoeba.sandbox")


class ImportTimeoutError(Exception):
    """임포트 타임아웃 예외"""

    pass


class SandboxError(Exception):
    """샌드박스 실행 예외"""

    pass


def safe_import(
    plugin_path: str | Path, timeout_ms: int = 800, use_subprocess: bool = True
) -> Any:
    """
    안전한 플러그인 임포트

    Args:
        plugin_path: 플러그인 파일 경로
        timeout_ms: 타임아웃 (밀리초)
        use_subprocess: 서브프로세스 사용 여부

    Returns:
        임포트된 모듈

    Raises:
        ImportTimeoutError: 타임아웃 발생
        SandboxError: 샌드박스 오류
    """
    plugin_path = Path(plugin_path)

    if not plugin_path.exists():
        raise FileNotFoundError(f"플러그인 파일이 존재하지 않습니다: {plugin_path}")

    if use_subprocess:
        return _safe_import_subprocess(plugin_path, timeout_ms)
    else:
        return _safe_import_direct(plugin_path, timeout_ms)


def _safe_import_direct(plugin_path: Path, timeout_ms: int) -> Any:
    """직접 임포트 (타임아웃 적용)"""
    import signal

    def timeout_handler(signum, frame):
        raise ImportTimeoutError(f"플러그인 임포트 타임아웃: {plugin_path}")

    # 타임아웃 설정 (Unix 시스템만)
    if hasattr(signal, "SIGALRM"):
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_ms // 1000 + 1)  # 초 단위로 변환

    try:
        start_time = time.time()

        # 모듈 스펙 생성
        spec = importlib.util.spec_from_file_location(plugin_path.stem, plugin_path)

        if spec is None:
            raise SandboxError(f"플러그인 스펙 생성 실패: {plugin_path}")

        # 모듈 생성
        module = importlib.util.module_from_spec(spec)

        # 타임아웃 체크
        if time.time() - start_time > timeout_ms / 1000:
            raise ImportTimeoutError(f"플러그인 임포트 타임아웃: {plugin_path}")

        # 모듈 실행
        spec.loader.exec_module(module)

        log.info(
            f"✅ 플러그인 임포트 완료: {plugin_path} ({time.time() - start_time:.3f}s)"
        )
        return module

    except ImportTimeoutError:
        raise
    except Exception as e:
        raise SandboxError(f"플러그인 임포트 실패: {plugin_path} - {e}")
    finally:
        # 타임아웃 해제
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)


def _safe_import_subprocess(plugin_path: Path, timeout_ms: int) -> Any:
    """서브프로세스를 통한 안전한 임포트"""

    # 임시 스크립트 생성
    script_content = f"""
import sys
import importlib.util
import json
import traceback
from pathlib import Path

try:
    plugin_path = Path(r"{plugin_path}")

    # 모듈 임포트
    spec = importlib.util.spec_from_file_location(plugin_path.stem, plugin_path)
    if spec is None:
        raise Exception("스펙 생성 실패")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # PLUGIN 객체 확인
    plugin = getattr(module, "PLUGIN", None)
    if plugin is None:
        raise Exception("PLUGIN 객체가 없습니다")

    # 플러그인 정보 출력
    info = {{
        "success": True,
        "name": getattr(plugin, "name", "unknown"),
        "version": getattr(plugin, "version", "0.1"),
        "api": getattr(plugin, "api", "1.0"),
        "requires": getattr(plugin, "requires", [])
    }}

    print(json.dumps(info))

except Exception as e:
    error_info = {{
        "success": False,
        "error": str(e),
        "traceback": traceback.format_exc()
    }}
    print(json.dumps(error_info))
"""

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as temp_file:
            temp_file.write(script_content)
            temp_script = temp_file.name

        # 서브프로세스 실행
        result = subprocess.run(
            [sys.executable, temp_script],
            capture_output=True,
            text=True,
            timeout=timeout_ms / 1000,
            cwd=plugin_path.parent,
        )

        if result.returncode != 0:
            raise SandboxError(f"서브프로세스 실행 실패: {result.stderr}")

        # 결과 파싱
        try:
            info = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            raise SandboxError(f"결과 파싱 실패: {result.stdout}")

        if not info.get("success"):
            error = info.get("error", "알 수 없는 오류")
            raise SandboxError(f"플러그인 검증 실패: {error}")

        # 실제 모듈 임포트 (검증 완료 후)
        return _safe_import_direct(plugin_path, timeout_ms)

    except subprocess.TimeoutExpired:
        raise ImportTimeoutError(f"플러그인 검증 타임아웃: {plugin_path}")
    finally:
        # 임시 파일 정리
        try:
            os.unlink(temp_script)
        except:
            pass


def create_restricted_environment() -> Dict[str, Any]:
    """제한된 실행 환경 생성"""

    # 제한된 builtins
    safe_builtins = {
        "abs",
        "all",
        "any",
        "bool",
        "dict",
        "enumerate",
        "filter",
        "float",
        "frozenset",
        "getattr",
        "hasattr",
        "hash",
        "int",
        "isinstance",
        "issubclass",
        "iter",
        "len",
        "list",
        "map",
        "max",
        "min",
        "next",
        "print",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "setattr",
        "sorted",
        "str",
        "sum",
        "tuple",
        "type",
        "vars",
        "zip",
    }

    # 위험한 함수들 제거
    restricted_builtins = {
        name: getattr(__builtins__, name)
        for name in safe_builtins
        if hasattr(__builtins__, name)
    }

    return {
        "__builtins__": restricted_builtins,
        "__name__": "__sandbox__",
        "__doc__": "Amoeba Plugin Sandbox Environment",
    }


def validate_plugin_file(plugin_path: Path) -> Dict[str, Any]:
    """플러그인 파일 검증"""
    validation_result = {"valid": False, "errors": [], "warnings": [], "info": {}}

    try:
        # 파일 존재 확인
        if not plugin_path.exists():
            validation_result["errors"].append("파일이 존재하지 않습니다")
            return validation_result

        # 파일 크기 체크 (10MB 제한)
        file_size = plugin_path.stat().st_size
        if file_size > 10 * 1024 * 1024:
            validation_result["errors"].append(
                f"파일 크기가 너무 큽니다: {file_size / 1024 / 1024:.1f}MB"
            )
            return validation_result

        # 파일 확장자 체크
        if plugin_path.suffix != ".py":
            validation_result["warnings"].append("Python 파일이 아닙니다")

        # 기본 구문 체크
        try:
            with open(plugin_path, "r", encoding="utf-8") as f:
                content = f.read()

            compile(content, str(plugin_path), "exec")
            validation_result["info"]["syntax_ok"] = True

        except SyntaxError as e:
            validation_result["errors"].append(f"문법 오류: {e}")
            return validation_result

        # PLUGIN 객체 존재 확인 (간단한 텍스트 검색)
        if "PLUGIN" not in content:
            validation_result["warnings"].append("PLUGIN 객체가 보이지 않습니다")

        # 위험한 코드 패턴 체크
        dangerous_patterns = [
            "__import__",
            "exec(",
            "eval(",
            "subprocess",
            "os.system",
            "open(",
            "file(",
            "input(",
            "raw_input(",
        ]

        found_dangerous = []
        for pattern in dangerous_patterns:
            if pattern in content:
                found_dangerous.append(pattern)

        if found_dangerous:
            validation_result["warnings"].append(
                f"위험할 수 있는 코드 패턴: {', '.join(found_dangerous)}"
            )

        validation_result["valid"] = len(validation_result["errors"]) == 0
        validation_result["info"]["file_size"] = file_size
        validation_result["info"]["line_count"] = content.count("\n") + 1

    except Exception as e:
        validation_result["errors"].append(f"검증 중 오류: {e}")

    return validation_result
