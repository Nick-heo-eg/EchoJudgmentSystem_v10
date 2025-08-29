"""
🌌 Base Adapter for Amoeba v0.2
어댑터 기본 인터페이스
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from echo_engine.amoeba.amoeba_manager import AmoebaManager


class BaseAdapter(ABC):
    """모든 어댑터의 기본 클래스"""

    name: str = "base"
    priority: int = 0  # 높을수록 우선순위 높음

    @abstractmethod
    def detect(self) -> bool:
        """현재 환경이 이 어댑터에 적합한지 감지"""
        pass

    @abstractmethod
    def prelink(self, mgr: AmoebaManager) -> None:
        """연결 전 준비 작업"""
        pass

    @abstractmethod
    def link(self, mgr: AmoebaManager) -> None:
        """실제 연결 수행"""
        pass

    @abstractmethod
    def optimize(self, mgr: AmoebaManager) -> None:
        """환경별 최적화 수행"""
        pass

    def get_info(self) -> Dict[str, Any]:
        """어댑터 정보 반환"""
        return {"name": self.name, "priority": self.priority, "active": True}
