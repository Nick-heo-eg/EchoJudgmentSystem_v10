# echo_engine/signature/echo_signature_network.py
from typing import Dict, List
from .signature_registry import SignatureRegistry
from meta_liminal_cosmos_integration import CosmicMirror, InfiniteObserver

registry = SignatureRegistry()


def init_signatures() -> SignatureRegistry:
    # 1) 기존 기본 시그니처 로드 (Aurora, Selene, Lune 등)
    registry.load_default_signatures()

    # Aurora 시그니처 임시 등록 (테스트용)
    try:
        from aurora_meta_liminal_creative_session import AuroraCreativeAgent

        if not registry.has_signature("Aurora"):
            registry.register_signature("Aurora", AuroraCreativeAgent())
    except ImportError:
        # 간단한 Aurora Mock 등록
        class AuroraMock:
            def respond_to(self, text):
                return f"Aurora: {text[:50]}..."

            def synthesize(self, inputs, mode="default"):
                return f"Aurora synthesis of {len(inputs)} inputs"

        if not registry.has_signature("Aurora"):
            registry.register_signature("Aurora", AuroraMock())

    # 2) Cosmos 확장 비판단자 등록
    if not registry.has_signature("CosmicMirror"):
        registry.register_signature("CosmicMirror", CosmicMirror())
    if not registry.has_signature("InfiniteObserver"):
        registry.register_signature("InfiniteObserver", InfiniteObserver())

    print("✅ Signature Network Ready:", registry.list_signatures())
    return registry


# 모듈 import 시 자동 초기화(필요 시 주석처리)
init_signatures()
