"""
🌌 Plugin Base Class for Amoeba v0.2
플러그인 기본 인터페이스
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from echo_engine.amoeba.amoeba_manager import AmoebaManager


class Plugin(ABC):
    """모든 플러그인의 기본 클래스"""

    # 플러그인 메타데이터
    name: str = ""
    version: str = "0.1"
    api_version: str = "1.0"  # ✅ 표준 키
    api: str = "1.0"  # ✅ 구버전 별칭 유지
    requires: List[str] = []  # python package/module names
    description: str = ""
    author: str = ""

    # 권한 및 보안
    permissions: Dict[str, Any] = {}  # 필요한 권한 딕셔너리
    sandbox: bool = True  # 샌드박스에서 실행할지 여부

    def __init__(self):
        self._loaded = False
        self._started = False
        self._manager = None

    @abstractmethod
    def load(self, mgr: AmoebaManager) -> None:
        """플러그인 로드 (초기화)"""
        pass

    @abstractmethod
    def start(self, mgr: AmoebaManager) -> None:
        """플러그인 시작"""
        pass

    @abstractmethod
    def stop(self, mgr: AmoebaManager) -> None:
        """플러그인 정지"""
        pass

    def reload(self, mgr: AmoebaManager) -> None:
        """플러그인 리로드 (선택사항)"""
        if self._started:
            self.stop(mgr)
        if self._loaded:
            self.unload(mgr)
        self.load(mgr)
        self.start(mgr)

    def unload(self, mgr: AmoebaManager) -> None:
        """플러그인 언로드 (선택사항)"""
        if self._started:
            self.stop(mgr)
        self._loaded = False
        self._manager = None

    def get_info(self) -> Dict[str, Any]:
        """플러그인 정보 반환"""
        return {
            "name": self.name,
            "version": self.version,
            "api_version": self.api_version,
            "api": self.api,
            "description": self.description,
            "author": self.author,
            "requires": self.requires,
            "permissions": self.permissions,
            "sandbox": self.sandbox,
            "loaded": self._loaded,
            "started": self._started,
        }

    def check_requirements(self) -> Dict[str, bool]:
        """요구사항 체크"""
        results = {}
        for req in self.requires:
            try:
                __import__(req)
                results[req] = True
            except ImportError:
                results[req] = False
        return results

    def is_compatible(self, api_version: str) -> bool:
        """API 호환성 체크"""
        # 간단한 버전 체크 (major.minor)
        try:
            # api_version 우선, 없으면 api 사용
            plugin_api = getattr(self, "api_version", None) or getattr(
                self, "api", "1.0"
            )
            plugin_major, plugin_minor = map(int, plugin_api.split("."))
            api_major, api_minor = map(int, api_version.split("."))

            # Major 버전이 같고 Minor 버전이 호환되어야 함
            return plugin_major == api_major and plugin_minor <= api_minor
        except (ValueError, AttributeError):
            return False

    def _mark_loaded(self, mgr: AmoebaManager):
        """로드됨 표시 (내부 사용)"""
        self._loaded = True
        self._manager = mgr

    def _mark_started(self):
        """시작됨 표시 (내부 사용)"""
        self._started = True

    def _mark_stopped(self):
        """정지됨 표시 (내부 사용)"""
        self._started = False
