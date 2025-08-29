# echo_engine/signature/signature_registry.py
from typing import Dict, List


class SignatureRegistry:
    def __init__(self):
        self._sig: Dict[str, object] = {}

    def load_default_signatures(self):
        """기존 구현 유지 (Aurora 등 로드)"""
        # 기본 시그니처 로드 로직
        pass

    def register_signature(self, name: str, obj: object):
        self._sig[name] = obj

    def has_signature(self, name: str) -> bool:
        return name in self._sig

    def get_signature(self, name: str):
        return self._sig.get(name)

    def list_signatures(self) -> List[str]:
        return list(self._sig.keys())
