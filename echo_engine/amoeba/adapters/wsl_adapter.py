"""
🌌 WSL Adapter for Amoeba v0.2
Windows Subsystem for Linux 특화 어댑터
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from echo_engine.amoeba.env_detect import detect_wsl
from echo_engine.infra.portable_paths import temp_dir, userprofile_wsl_guess

from .base import BaseAdapter

if TYPE_CHECKING:
    from echo_engine.amoeba.amoeba_manager import AmoebaManager

log = logging.getLogger("amoeba.wsl_adapter")


class WSLAdapter(BaseAdapter):
    """WSL 환경 특화 어댑터"""

    name = "wsl"
    priority = 8  # 높은 우선순위

    def detect(self) -> bool:
        """WSL 환경 감지"""
        wsl_info = detect_wsl()
        is_wsl = wsl_info.get("is_wsl", False)

        if is_wsl:
            log.info(f"🐧 WSL 환경 감지: v{wsl_info.get('version', 'unknown')}")
            if wsl_info.get("distro"):
                log.info(f"🐧 배포판: {wsl_info['distro']}")

        return is_wsl

    def prelink(self, mgr: AmoebaManager) -> None:
        """WSL 연결 전 준비"""
        log.info("🔧 WSL 환경 준비 중...")

        # PathMapper WSL 매핑 활성화
        mgr.linker.path_mapper.enable_wsl_map()

        # Windows 경로 매핑 추가
        additional_mappings = {
            "C:\\": "/mnt/c/",
            "D:\\": "/mnt/d/",
            "%USERPROFILE%": str(userprofile_wsl_guess()),
            "%TEMP%": str(temp_dir()),
        }

        mgr.linker.path_mapper.mappings.update(additional_mappings)
        log.info("🗺️ Windows 경로 매핑 설정 완료")

    def link(self, mgr: AmoebaManager) -> None:
        """WSL 연결 수행"""
        log.info("🔗 WSL 시스템 연결 중...")

        # WSL 특화 심볼릭 링크 설정
        wsl_symlinks = [
            ("/mnt/c/Windows/System32/wsl.exe", "/usr/local/bin/wsl"),
            ("/mnt/c/Windows/System32/cmd.exe", "/usr/local/bin/cmd"),
        ]

        for src, dst in wsl_symlinks:
            if Path(src).exists():
                mgr.linker.symlinks.append((src, dst))

        # WSL interop 설정
        mgr.linker.ensure_symlinks()

        # WSL 서비스 등록
        mgr.linker.register_service(
            "wsl_interop",
            {"enabled": True, "windows_path_access": True, "cmd_integration": True},
        )

        log.info("✅ WSL 연결 완료")

    def optimize(self, mgr: AmoebaManager) -> None:
        """WSL 최적화"""
        log.info("⚡ WSL 최적화 시작...")

        # I/O 버퍼 튜닝 (WSL 특화)
        mgr.optimizer.tune_io_buffer()

        # 메모리 최적화
        mgr.optimizer.optimize_memory()

        # WSL 특화 최적화
        import os

        # WSL 파일시스템 최적화
        os.environ["WSLENV"] = "PATH/l:PYTHONPATH/l"

        # Windows interop 최적화
        if Path("/proc/sys/fs/binfmt_misc/WSLInterop").exists():
            log.info("🔄 WSL interop 활성화됨")

        mgr.optimizer.optimizations_applied.append("wsl_filesystem_optimization")
        mgr.optimizer.optimizations_applied.append("wsl_interop_optimization")

        log.info("✅ WSL 최적화 완료")
