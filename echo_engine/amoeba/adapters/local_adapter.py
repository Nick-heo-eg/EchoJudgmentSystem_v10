"""
🌌 Local Adapter for Amoeba v0.2
로컬 환경 (일반 Linux/Windows/macOS) 어댑터
"""

from __future__ import annotations

import logging
import os
import platform
from typing import TYPE_CHECKING

from echo_engine.infra.portable_paths import home, temp_dir

from .base import BaseAdapter

if TYPE_CHECKING:
    from echo_engine.amoeba.amoeba_manager import AmoebaManager

log = logging.getLogger("amoeba.local_adapter")


class LocalAdapter(BaseAdapter):
    """로컬 환경 어댑터 (기본값)"""

    name = "local"
    priority = 1  # 낮은 우선순위 (기본값)

    def detect(self) -> bool:
        """로컬 환경 감지 (항상 True - 기본값)"""
        system = platform.system()
        log.info(f"🏠 로컬 환경 감지: {system}")
        return True  # 기본 어댑터이므로 항상 적용 가능

    def prelink(self, mgr: AmoebaManager) -> None:
        """로컬 환경 준비"""
        log.info("🔧 로컬 환경 준비 중...")

        system = platform.system()

        if system == "Windows":
            self._prepare_windows(mgr)
        elif system == "Darwin":  # macOS
            self._prepare_macos(mgr)
        else:  # Linux 등
            self._prepare_linux(mgr)

    def _prepare_windows(self, mgr: AmoebaManager) -> None:
        """Windows 환경 준비"""
        log.info("🪟 Windows 환경 설정")

        # Windows 특화 경로 매핑
        windows_paths = {
            "%USERPROFILE%": str(home()),
            "%APPDATA%": os.getenv("APPDATA", ""),
            "%LOCALAPPDATA%": os.getenv("LOCALAPPDATA", ""),
            "%TEMP%": str(temp_dir()),
        }

        mgr.linker.path_mapper.mappings.update(windows_paths)

        # Windows 환경 변수
        os.environ["PLATFORM"] = "windows"

    def _prepare_macos(self, mgr: AmoebaManager) -> None:
        """macOS 환경 준비"""
        log.info("🍎 macOS 환경 설정")

        # macOS 특화 경로 매핑
        macos_paths = {
            "~/Library": os.path.expanduser("~/Library"),
            "~/Applications": os.path.expanduser("~/Applications"),
            os.path.join(tempfile.gettempdir()): os.path.join(tempfile.gettempdir()),
        }

        mgr.linker.path_mapper.mappings.update(macos_paths)

        # macOS 환경 변수
        os.environ["PLATFORM"] = "darwin"

    def _prepare_linux(self, mgr: AmoebaManager) -> None:
        """Linux 환경 준비"""
        log.info("🐧 Linux 환경 설정")

        # Linux 특화 경로 매핑
        linux_paths = {
            "~/.config": os.path.expanduser("~/.config"),
            "~/.cache": os.path.expanduser("~/.cache"),
            "~/.local": os.path.expanduser("~/.local"),
            os.path.join(tempfile.gettempdir()): os.path.join(tempfile.gettempdir()),
        }

        mgr.linker.path_mapper.mappings.update(linux_paths)

        # Linux 환경 변수
        os.environ["PLATFORM"] = "linux"

    def link(self, mgr: AmoebaManager) -> None:
        """로컬 시스템 연결"""
        log.info("🔗 로컬 시스템 연결 중...")

        system = platform.system()

        # 기본 서비스 등록
        mgr.linker.register_service(
            "platform_info",
            {
                "system": system,
                "version": platform.version(),
                "machine": platform.machine(),
                "python_version": platform.python_version(),
            },
        )

        # 사용자 정보 등록
        mgr.linker.register_service(
            "user_info",
            {
                "username": os.getenv("USER") or os.getenv("USERNAME", "unknown"),
                "home": os.path.expanduser("~"),
                "cwd": os.getcwd(),
            },
        )

        # 시스템별 특화 연결
        if system == "Windows":
            self._link_windows(mgr)
        elif system == "Darwin":
            self._link_macos(mgr)
        else:
            self._link_linux(mgr)

        log.info("✅ 로컬 연결 완료")

    def _link_windows(self, mgr: AmoebaManager) -> None:
        """Windows 특화 연결"""
        # PowerShell 연동
        if os.path.exists(
            ensure_portable(
                "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
            )
        ):
            mgr.linker.register_service("powershell", {"available": True})

    def _link_macos(self, mgr: AmoebaManager) -> None:
        """macOS 특화 연결"""
        # Homebrew 체크
        if os.path.exists("/opt/homebrew/bin/brew") or os.path.exists(
            "/usr/local/bin/brew"
        ):
            mgr.linker.register_service("homebrew", {"available": True})

    def _link_linux(self, mgr: AmoebaManager) -> None:
        """Linux 특화 연결"""
        # 패키지 매니저 체크
        package_managers = {
            "apt": "/usr/bin/apt",
            "yum": "/usr/bin/yum",
            "dnf": "/usr/bin/dnf",
            "pacman": "/usr/bin/pacman",
        }

        for pm_name, pm_path in package_managers.items():
            if os.path.exists(pm_path):
                mgr.linker.register_service(
                    "package_manager", {"type": pm_name, "path": pm_path}
                )
                break

    def optimize(self, mgr: AmoebaManager) -> None:
        """로컬 환경 최적화"""
        log.info("⚡ 로컬 환경 최적화 시작...")

        # 기본 최적화
        mgr.optimizer.optimize_memory()
        mgr.optimizer.optimize_disk_io()

        # GPU가 있으면 GPU 최적화
        from echo_engine.amoeba.env_detect import detect_gpu

        gpu_info = detect_gpu()
        if gpu_info.get("has_gpu"):
            mgr.optimizer.tune_for_gpu()
            log.info("🎮 GPU 최적화 적용")

        # 성능 벤치마크 실행
        benchmark_results = mgr.optimizer.run_performance_benchmark()
        log.info(
            f"📊 성능 벤치마크: CPU={benchmark_results.get('cpu_benchmark_ms', 0):.1f}ms"
        )

        # 시스템별 특화 최적화
        system = platform.system()
        if system == "Windows":
            self._optimize_windows(mgr)
        elif system == "Darwin":
            self._optimize_macos(mgr)
        else:
            self._optimize_linux(mgr)

        log.info("✅ 로컬 최적화 완료")

    def _optimize_windows(self, mgr: AmoebaManager) -> None:
        """Windows 특화 최적화"""
        # Windows 파일 시스템 최적화
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"  # .pyc 파일 생성 방지
        mgr.optimizer.optimizations_applied.append("windows_filesystem_optimization")

    def _optimize_macos(self, mgr: AmoebaManager) -> None:
        """macOS 특화 최적화"""
        # macOS 메모리 압축 최적화
        os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
        mgr.optimizer.optimizations_applied.append("macos_fork_optimization")

    def _optimize_linux(self, mgr: AmoebaManager) -> None:
        """Linux 특화 최적화"""
        # Linux 프로세스 최적화
        os.environ["MALLOC_ARENA_MAX"] = "2"  # glibc malloc 최적화
        mgr.optimizer.optimizations_applied.append("linux_malloc_optimization")
