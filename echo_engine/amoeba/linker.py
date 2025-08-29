"""
🌌 Amoeba Linker v0.2
시스템 연결 및 매핑 관리
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

log = logging.getLogger("amoeba.linker")


class PathMapper:
    """경로 매핑 관리자"""

    def __init__(self):
        self.mappings: Dict[str, str] = {}
        self.wsl_enabled = False
        self.docker_enabled = False

    def enable_wsl_map(self):
        """WSL 경로 매핑 활성화"""
        self.wsl_enabled = True
        # Windows 경로를 WSL 경로로 매핑
        self.mappings.update(
            {
                "C:": "/mnt/c",
                "D:": "/mnt/d",
                "temp": os.path.join(tempfile.gettempdir()),
            }
        )
        log.info("🐧 WSL 경로 매핑 활성화")

    def enable_docker_map(self):
        """Docker 볼륨 매핑 활성화"""
        self.docker_enabled = True
        self.mappings.update(
            {"workspace": "/workspace", "data": "/data", "logs": "/logs"}
        )
        log.info("🐳 Docker 경로 매핑 활성화")

    def resolve_path(self, path: str) -> str:
        """경로 해결"""
        for alias, real_path in self.mappings.items():
            if path.startswith(alias):
                return path.replace(alias, real_path, 1)
        return path


class ServiceRegistry:
    """서비스 레지스트리"""

    def __init__(self):
        self.services: Dict[str, Any] = {}
        self.health_endpoints: List[str] = []

    def register_service(self, name: str, instance: Any):
        """서비스 등록"""
        self.services[name] = instance
        log.info(f"🔌 서비스 등록: {name}")

    def unregister_service(self, name: str):
        """서비스 해제"""
        if name in self.services:
            del self.services[name]
            log.info(f"🔌 서비스 해제: {name}")

    def get_service(self, name: str) -> Optional[Any]:
        """서비스 조회"""
        return self.services.get(name)

    def list_services(self) -> List[str]:
        """서비스 목록"""
        return list(self.services.keys())

    def add_health_endpoint(self, endpoint: str):
        """헬스체크 엔드포인트 추가"""
        self.health_endpoints.append(endpoint)
        log.info(f"🏥 헬스체크 엔드포인트 추가: {endpoint}")


class Linker:
    """Amoeba 연결 관리자"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.path_mapper = PathMapper()
        self.service_registry = ServiceRegistry()
        self.symlinks: List[tuple] = []
        self.network_bridges: List[str] = []

    def ensure_symlinks(self):
        """심볼릭 링크 보장"""
        try:
            for src, dst in self.symlinks:
                src_path = Path(src)
                dst_path = Path(dst)

                if not dst_path.exists() and src_path.exists():
                    dst_path.symlink_to(src_path)
                    log.info(f"🔗 심볼릭 링크 생성: {dst} -> {src}")
        except Exception as e:
            log.warning(f"⚠️ 심볼릭 링크 생성 실패: {e}")

    def enable_docker_bridge(self):
        """Docker 브리지 활성화"""
        self.network_bridges.append("docker0")
        self.path_mapper.enable_docker_map()
        log.info("🌉 Docker 브리지 활성화")

    def expose_health_endpoint(self):
        """헬스체크 엔드포인트 노출"""
        endpoint = "/health"
        self.service_registry.add_health_endpoint(endpoint)
        log.info(f"🏥 헬스체크 엔드포인트 노출: {endpoint}")

    def register_service(self, name: str, instance: Any):
        """서비스 등록 (래퍼)"""
        self.service_registry.register_service(name, instance)

    def get_status(self) -> Dict[str, Any]:
        """링커 상태 반환"""
        return {
            "path_mappings": len(self.path_mapper.mappings),
            "services": len(self.service_registry.services),
            "symlinks": len(self.symlinks),
            "bridges": len(self.network_bridges),
            "health_endpoints": len(self.service_registry.health_endpoints),
            "wsl_enabled": self.path_mapper.wsl_enabled,
            "docker_enabled": self.path_mapper.docker_enabled,
        }
