"""
🌌 Plugin Registry for Amoeba v0.2
플러그인 레지스트리 및 로더
"""

from __future__ import annotations

import fnmatch
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from echo_engine.amoeba.security import check_permissions, verify_signature

from .base import Plugin
from .sandbox import safe_import, validate_plugin_file

if TYPE_CHECKING:
    from echo_engine.amoeba.amoeba_manager import AmoebaManager

log = logging.getLogger("amoeba.registry")


@dataclass(frozen=True)
class DiscoveryItem:
    """플러그인 발견 항목"""

    name: str
    path: Path


class PluginRegistry:
    """플러그인 레지스트리 및 관리자"""

    def __init__(self, config: Dict[str, Any], mgr: AmoebaManager):
        self.config = config.get("plugins", {})
        self.mgr = mgr
        self.active_plugins: Dict[str, Plugin] = {}
        self.failed_plugins: Dict[str, str] = {}  # name -> error message
        self.discovery_paths: List[str] = []
        self.allowlist: List[str] = []
        self.blocklist: List[str] = []

        self._load_config()

    def _load_config(self):
        """설정 로드"""
        self.discovery_paths = self.config.get("discovery_paths", ["./plugins_ext"])
        self.allowlist = self.config.get("allowlist", ["*"])  # 기본적으로 모든 것 허용
        self.blocklist = self.config.get("blocklist", [])

        log.info(f"📂 탐색 경로: {self.discovery_paths}")
        log.info(f"✅ 허용 패턴: {self.allowlist}")
        log.info(f"❌ 차단 패턴: {self.blocklist}")

    def discover(self) -> List[DiscoveryItem]:
        """플러그인 파일 탐색"""
        items = []

        for path_str in self.discovery_paths:
            path = Path(path_str)

            if not path.exists():
                log.warning(f"⚠️ 탐색 경로가 존재하지 않습니다: {path}")
                continue

            # .py 파일 탐색
            if path.is_file() and path.suffix == ".py":
                if self._is_plugin_allowed(path.stem):
                    items.append(DiscoveryItem(path.stem, path))
            elif path.is_dir():
                for py_file in path.rglob("*.py"):
                    if self._is_plugin_allowed(py_file.stem):
                        items.append(DiscoveryItem(py_file.stem, py_file))

        log.info(f"🔍 발견된 플러그인 파일: {len(items)}개")
        for item in items:
            log.debug(f"  📄 {item.name} -> {item.path}")

        return items

    def discover_paths(self) -> List[Path]:
        """호환성을 위한 헬퍼: 경로 리스트 반환"""
        return [item.path for item in self.discover()]

    def discover_map(self) -> Dict[str, Path]:
        """호환성을 위한 헬퍼: 이름->경로 매핑 반환"""
        return {item.name: item.path for item in self.discover()}

    def _is_plugin_allowed(self, plugin_name: str) -> bool:
        """플러그인이 허용되는지 확인"""
        # 차단리스트 체크
        for pattern in self.blocklist:
            if fnmatch.fnmatch(plugin_name, pattern):
                log.debug(f"❌ 차단됨: {plugin_name} (패턴: {pattern})")
                return False

        # 허용리스트 체크
        for pattern in self.allowlist:
            if fnmatch.fnmatch(plugin_name, pattern):
                log.debug(f"✅ 허용됨: {plugin_name} (패턴: {pattern})")
                return True

        log.debug(f"❌ 허용리스트에 없음: {plugin_name}")
        return False

    def load(self, plugin_path: Path) -> Optional[Plugin]:
        """플러그인 로드"""
        log.info(f"📦 플러그인 로드 시작: {plugin_path.name}")

        try:
            # 파일 검증
            validation = validate_plugin_file(plugin_path)
            if not validation["valid"]:
                errors = ", ".join(validation["errors"])
                raise RuntimeError(f"플러그인 검증 실패: {errors}")

            if validation["warnings"]:
                for warning in validation["warnings"]:
                    log.warning(f"⚠️ {plugin_path.name}: {warning}")

            # 보안 체크
            security_config = self.config.get("security", {})
            if security_config.get("plugin_signature_required", False):
                verify_signature(plugin_path, required=True)

            # 안전한 임포트
            start_time = time.time()
            timeout_ms = security_config.get("max_import_time_ms", 800)

            module = safe_import(plugin_path, timeout_ms=timeout_ms)

            # PLUGIN 객체 확인
            plugin_instance = getattr(module, "PLUGIN", None)
            if plugin_instance is None:
                raise RuntimeError("PLUGIN 객체가 없습니다")

            if not isinstance(plugin_instance, Plugin):
                raise RuntimeError("PLUGIN은 Plugin 클래스의 인스턴스여야 합니다")

            # 메타데이터 보정 (누락 시 기본값 설정)
            if not plugin_instance.name:
                plugin_instance.name = plugin_path.stem
            if not hasattr(plugin_instance, "version") or not plugin_instance.version:
                setattr(plugin_instance, "version", "0.1")
            if not hasattr(plugin_instance, "api_version"):
                setattr(
                    plugin_instance,
                    "api_version",
                    getattr(plugin_instance, "api", "1.0"),
                )
            if (
                not hasattr(plugin_instance, "permissions")
                or not plugin_instance.permissions
            ):
                setattr(plugin_instance, "permissions", {})

            # API 호환성 체크
            if not plugin_instance.is_compatible("1.0"):  # 현재 API 버전
                raise RuntimeError(f"API 버전 비호환: {plugin_instance.api}")

            # 요구사항 체크
            requirements = plugin_instance.check_requirements()
            missing = [req for req, available in requirements.items() if not available]
            if missing:
                raise RuntimeError(f"누락된 의존성: {', '.join(missing)}")

            # 권한 체크
            check_permissions(plugin_instance)

            # 플러그인 로드
            plugin_instance.load(self.mgr)
            plugin_instance._mark_loaded(self.mgr)

            # 레지스트리에 등록
            self.active_plugins[plugin_instance.name] = plugin_instance

            load_time = time.time() - start_time
            log.info(
                f"✅ 플러그인 로드 완료: {plugin_instance.name} v{plugin_instance.version} ({load_time:.3f}s)"
            )

            return plugin_instance

        except Exception as e:
            error_msg = str(e)
            self.failed_plugins[plugin_path.stem] = error_msg
            log.error(f"❌ 플러그인 로드 실패: {plugin_path.name} - {error_msg}")
            return None

    def start_all(self):
        """모든 플러그인 시작"""
        log.info(f"🚀 플러그인 시작: {len(self.active_plugins)}개")

        for name, plugin in self.active_plugins.items():
            try:
                log.info(f"▶️ 플러그인 시작: {name}")
                plugin.start(self.mgr)
                plugin._mark_started()
                log.info(f"✅ 플러그인 시작 완료: {name}")

            except Exception as e:
                log.error(f"❌ 플러그인 시작 실패: {name} - {e}")
                # 시작 실패한 플러그인은 활성 목록에서 제거하지 않음 (재시작 가능)

    def stop_all(self):
        """모든 플러그인 정지"""
        log.info(f"⏹️ 플러그인 정지: {len(self.active_plugins)}개")

        for name, plugin in list(self.active_plugins.items()):
            try:
                if plugin._started:
                    log.info(f"⏸️ 플러그인 정지: {name}")
                    plugin.stop(self.mgr)
                    plugin._mark_stopped()
                    log.info(f"✅ 플러그인 정지 완료: {name}")

            except Exception as e:
                log.error(f"❌ 플러그인 정지 실패: {name} - {e}")

    def unload_all(self):
        """모든 플러그인 언로드"""
        log.info(f"📤 플러그인 언로드: {len(self.active_plugins)}개")

        # 먼저 모든 플러그인 정지
        self.stop_all()

        # 언로드
        for name, plugin in list(self.active_plugins.items()):
            try:
                log.info(f"📤 플러그인 언로드: {name}")
                plugin.unload(self.mgr)
                del self.active_plugins[name]
                log.info(f"✅ 플러그인 언로드 완료: {name}")

            except Exception as e:
                log.error(f"❌ 플러그인 언로드 실패: {name} - {e}")

    def reload_plugin(self, name: str) -> bool:
        """특정 플러그인 리로드"""
        if name not in self.active_plugins:
            log.error(f"❌ 플러그인을 찾을 수 없습니다: {name}")
            return False

        try:
            plugin = self.active_plugins[name]
            log.info(f"🔄 플러그인 리로드: {name}")
            plugin.reload(self.mgr)
            log.info(f"✅ 플러그인 리로드 완료: {name}")
            return True

        except Exception as e:
            log.error(f"❌ 플러그인 리로드 실패: {name} - {e}")
            return False

    def auto_load_plugins(self):
        """자동 로드 플러그인 처리"""
        autoload_list = self.config.get("autoload", [])
        if not autoload_list:
            log.info("📋 자동 로드할 플러그인이 없습니다")
            return

        log.info(f"🔄 자동 로드 플러그인: {autoload_list}")

        # 플러그인 파일 탐색
        discovered_files = self.discover()

        # 자동 로드 목록에 있는 플러그인 로드
        for plugin_item in discovered_files:
            plugin_name = plugin_item.name
            if plugin_name in autoload_list:
                self.load(plugin_item.path)

        # 로드된 플러그인 시작
        self.start_all()

    def get_plugin_info(self, name: str) -> Optional[Dict[str, Any]]:
        """플러그인 정보 조회"""
        if name in self.active_plugins:
            return self.active_plugins[name].get_info()
        elif name in self.failed_plugins:
            return {
                "name": name,
                "status": "failed",
                "error": self.failed_plugins[name],
            }
        return None

    def list_plugins(self) -> Dict[str, Any]:
        """모든 플러그인 목록"""
        return {
            "active": {
                name: plugin.get_info() for name, plugin in self.active_plugins.items()
            },
            "failed": {
                name: {"error": error} for name, error in self.failed_plugins.items()
            },
            "count": {
                "active": len(self.active_plugins),
                "failed": len(self.failed_plugins),
                "total": len(self.active_plugins) + len(self.failed_plugins),
            },
        }

    def get_status(self) -> Dict[str, Any]:
        """레지스트리 상태"""
        return {
            "discovery_paths": self.discovery_paths,
            "allowlist": self.allowlist,
            "blocklist": self.blocklist,
            "active_count": len(self.active_plugins),
            "failed_count": len(self.failed_plugins),
            "plugins": self.list_plugins(),
        }
