#!/usr/bin/env python3
"""
Portable paths utility - 중앙 경로 가드
하드코딩 치환 대신, 경로 해석을 한 군데로 모음.
"""
from __future__ import annotations
import os
import platform
import re
import tempfile
from pathlib import Path


# ---- 환경 기준점
def project_root() -> Path:
    """프로젝트 루트 경로 (echo_engine/infra/portable_paths.py -> echo_engine -> repo root)"""
    return Path(__file__).resolve().parents[2]


def home() -> Path:
    """사용자 홈 디렉토리"""
    return Path.home()


def logs_dir() -> Path:
    """로그 디렉토리 (환경변수 우선, 기본값은 프로젝트 루트/logs)"""
    return Path(os.environ.get("ECHO_LOG_DIR", project_root() / "logs"))


# ---- WSL/Windows 호스트 판단
def is_wsl() -> bool:
    """WSL 환경 여부 검사"""
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except Exception:
        return False


def is_windows() -> bool:
    """Windows 환경 여부 검사"""
    return platform.system().lower().startswith("win")


# ---- 경로 텍스트 ↔ Path 변환 (WSL/Windows 상호변환)
_WIN_DRIVE = re.compile(r"^[A-Za-z]:\\")


def win_to_wsl(path_str: str) -> str:
    """Windows 경로를 WSL 경로로 변환"""
    if not _WIN_DRIVE.match(path_str):
        return path_str
    drive = path_str[0].lower()
    rest = path_str[2:].replace("\\", "/").lstrip("/")
    return f"/mnt/{drive}/{rest}"


def wsl_to_win(path_str: str) -> str:
    """WSL 경로를 Windows 경로로 변환"""
    if not path_str.startswith("/mnt/"):
        return path_str
    try:
        _, _, drive, *rest = path_str.split("/")
        drive_letter = drive.upper()
        return f"{drive_letter}:\\{('\\'.join(rest))}"
    except Exception:
        return path_str


def ensure_portable(path_like: str | Path) -> Path:
    """Windows/WSL 절대경로를 현재 런타임에 맞춰 정규화."""
    if isinstance(path_like, Path):
        s = str(path_like)
    else:
        s = path_like

    if is_wsl() and _WIN_DRIVE.match(s):
        s = win_to_wsl(s)
    if is_windows() and s.startswith("/mnt/"):
        s = wsl_to_win(s)

    return Path(s)


# ---- 공용 단축 유틸
def temp_dir() -> Path:
    """임시 디렉토리"""
    return Path(tempfile.gettempdir())


def userprofile_wsl_guess(user: str | None = None) -> Path:
    """WSL 환경에서 Windows 사용자 프로필 경로 추정"""
    user = user or os.environ.get("USERNAME") or os.environ.get("USER") or "user"
    # 흔히 쓰는 기본 매핑
    if is_wsl():
        return Path(f"/mnt/c/Users/{user}")
    return Path.home()


# 예시 프리셋 (선택적으로 사용)
def cloud_log_dir() -> Path:
    """클라우드 로그 디렉토리"""
    return ensure_portable(os.environ.get("ECHO_CLOUD_LOG_DIR", "/var/log/cloud"))


def data_dir() -> Path:
    """데이터 디렉토리"""
    return ensure_portable(
        os.environ.get("ECHO_DATA_DIR", str(project_root() / "data"))
    )


def cache_dir() -> Path:
    """캐시 디렉토리"""
    return ensure_portable(
        os.environ.get("ECHO_CACHE_DIR", str(project_root() / ".cache"))
    )
