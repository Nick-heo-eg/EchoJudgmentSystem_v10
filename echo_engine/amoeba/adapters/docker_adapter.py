"""
🌌 Docker Adapter for Amoeba v0.2
Docker 컨테이너 특화 어댑터
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from echo_engine.amoeba.env_detect import detect_docker

from .base import BaseAdapter

if TYPE_CHECKING:
    from echo_engine.amoeba.amoeba_manager import AmoebaManager

log = logging.getLogger("amoeba.docker_adapter")


class DockerAdapter(BaseAdapter):
    """Docker 환경 특화 어댑터"""

    name = "docker"
    priority = 9  # 매우 높은 우선순위

    def detect(self) -> bool:
        """Docker 환경 감지"""
        docker_info = detect_docker()
        is_docker = docker_info.get("is_docker", False)

        if is_docker:
            log.info("🐳 Docker 컨테이너 환경 감지")
            if docker_info.get("container_id"):
                log.info(f"🆔 Container ID: {docker_info['container_id']}")
            if docker_info.get("runtime"):
                log.info(f"🏃 Runtime: {docker_info['runtime']}")

        return is_docker

    def prelink(self, mgr: AmoebaManager) -> None:
        """Docker 연결 전 준비"""
        log.info("🔧 Docker 환경 준비 중...")

        # Docker 볼륨 매핑
        mgr.linker.enable_docker_bridge()

        # 컨테이너 특화 경로 매핑
        container_paths = {
            "/app": "/workspace",
            "/data": os.path.join(
                os.path.expanduser("~"), ".local", "share", "echo", r"echo/data"
            ),
            "/logs": os.path.join(
                os.path.expanduser("~"), ".cache", "echo", "logs", r"echo"
            ),
            "/config": os.path.join(
                os.path.expanduser("~"), ".config", "echo", r"echo"
            ),
        }

        mgr.linker.path_mapper.mappings.update(container_paths)
        log.info("🗂️ Docker 볼륨 매핑 설정 완료")

        # 환경 변수 설정
        os.environ["DOCKER_CONTAINER"] = "1"
        os.environ["CONTAINERIZED"] = "true"

    def link(self, mgr: AmoebaManager) -> None:
        """Docker 연결 수행"""
        log.info("🔗 Docker 시스템 연결 중...")

        # 헬스체크 엔드포인트 노출
        mgr.linker.expose_health_endpoint()

        # Docker 네트워크 설정
        mgr.linker.network_bridges.extend(["docker0", "bridge"])

        # Docker 서비스 등록
        mgr.linker.register_service(
            "docker_runtime",
            {
                "container_id": os.getenv("HOSTNAME", "unknown"),
                "image_name": os.getenv("DOCKER_IMAGE", "unknown"),
                "network_mode": "bridge",
            },
        )

        # 신호 처리 설정
        mgr.linker.register_service(
            "signal_handler", {"sigterm_graceful": True, "sigint_graceful": True}
        )

        log.info("✅ Docker 연결 완료")

    def optimize(self, mgr: AmoebaManager) -> None:
        """Docker 최적화"""
        log.info("⚡ Docker 최적화 시작...")

        # CPU 쿼터 제한
        mgr.optimizer.limit_cpu_quota_if_needed()

        # 메모리 최적화
        mgr.optimizer.optimize_memory()

        # 디스크 I/O 최적화
        mgr.optimizer.optimize_disk_io()

        # Docker 특화 최적화
        self._optimize_docker_specific(mgr)

        log.info("✅ Docker 최적화 완료")

    def _optimize_docker_specific(self, mgr: AmoebaManager) -> None:
        """Docker 특화 최적화"""
        # 컨테이너 리소스 제한 체크
        cgroup_memory = Path("/sys/fs/cgroup/memory/memory.limit_in_bytes")
        if cgroup_memory.exists():
            try:
                with open(cgroup_memory, "r") as f:
                    limit = int(f.read().strip())
                    # 매우 큰 값은 제한 없음을 의미
                    if limit < (1024**4):  # 1TB 미만이면 실제 제한
                        limit_gb = limit / (1024**3)
                        log.info(f"💾 메모리 제한: {limit_gb:.1f}GB")
                        mgr.optimizer.performance_metrics["memory_limit_gb"] = limit_gb
            except Exception as e:
                log.debug(f"메모리 제한 체크 실패: {e}")

        # CPU 제한 체크
        cgroup_cpu = Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
        if cgroup_cpu.exists():
            try:
                with open(cgroup_cpu, "r") as f:
                    quota = int(f.read().strip())
                    if quota > 0:
                        with open("/sys/fs/cgroup/cpu/cpu.cfs_period_us", "r") as pf:
                            period = int(pf.read().strip())
                            cpu_cores = quota / period
                            log.info(f"🖥️ CPU 제한: {cpu_cores:.1f} 코어")
                            mgr.optimizer.performance_metrics["cpu_limit_cores"] = (
                                cpu_cores
                            )
            except Exception as e:
                log.debug(f"CPU 제한 체크 실패: {e}")

        # 로그 회전 설정
        os.environ["PYTHONUNBUFFERED"] = "1"  # 실시간 로그 출력

        mgr.optimizer.optimizations_applied.extend(
            [
                "docker_resource_monitoring",
                "docker_logging_optimization",
                "docker_signal_handling",
            ]
        )
