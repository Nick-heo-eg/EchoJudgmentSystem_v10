from .registry import get_registry
import asyncio

# 기본 도구 import
from . import (
    trinity_insight,
    consciousness_bridge,
    cosmos_init,
    cosmos_explore,
    echo_analyze,
    amoeba_adapt,
)

# Enhanced 도구 import
try:
    from .enhanced import (
        echo_decide_enhanced,
        echo_quantum_coding_enhanced,
        trinity_insight_enhanced,
        consciousness_bridge_enhanced,
        echo_meta_liminal_enhanced,
        cosmos_init_enhanced,
        cosmos_explore_enhanced,
        echo_analyze_enhanced,
        amoeba_adapt_enhanced,
    )

    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False


def initialize_tools():
    """모든 도구를 레지스트리에 등록"""
    registry = get_registry()

    # 🔄 6개 스텁 등록
    registry.register_base("trinity_insight", trinity_insight.run)
    registry.register_base("consciousness_bridge", consciousness_bridge.run)
    registry.register_base("cosmos_init", cosmos_init.run)
    registry.register_base("cosmos_explore", cosmos_explore.run)
    registry.register_base("echo_analyze", echo_analyze.run)
    registry.register_base("amoeba_adapt", amoeba_adapt.run)

    # 🚀 Enhanced 버전들 등록
    if ENHANCED_AVAILABLE:
        registry.register_enhanced("echo_decide", echo_decide_enhanced.run)
        registry.register_enhanced(
            "echo_quantum_coding", echo_quantum_coding_enhanced.run
        )
        registry.register_enhanced("trinity_insight", trinity_insight_enhanced.run)
        registry.register_enhanced(
            "consciousness_bridge", consciousness_bridge_enhanced.run
        )
        registry.register_enhanced("echo_meta_liminal", echo_meta_liminal_enhanced.run)
        registry.register_enhanced("cosmos_init", cosmos_init_enhanced.run)
        registry.register_enhanced("cosmos_explore", cosmos_explore_enhanced.run)
        registry.register_enhanced("echo_analyze", echo_analyze_enhanced.run)
        registry.register_enhanced("amoeba_adapt", amoeba_adapt_enhanced.run)
        print("✅ Enhanced tools registered successfully (9 enhanced tools)")
    else:
        print("⚠️ Enhanced tools not available - using stubs")

    # 🛠️ Self-Ask Tool 등록 (핵심 기능)
    try:
        from .enhanced.self_ask import SelfAskTool

        sa = SelfAskTool()
        registry.register_enhanced("self_ask", sa.run)
        # 도구가 레지스트리 주입을 지원하면 연결
        if hasattr(sa, "set_registry"):
            try:
                sa.set_registry(registry)
            except Exception:
                pass
        print("✅ Self-Ask tool registered successfully")
    except Exception as e:
        print(f"⚠️ Self-Ask tool registration failed: {e}")

    # 기존 도구들도 등록 (예시 - 실제 핸들러로 교체 필요)
    from .stubs.base_stub import create_stub_response

    async def echo_decide_stub(**kwargs):
        return create_stub_response(
            "echo_decide", hint="Decision making with Echo judgment engine"
        )

    async def echo_quantum_coding_stub(**kwargs):
        return create_stub_response(
            "echo_quantum_coding", hint="AI-powered quantum coding system"
        )

    async def echo_meta_liminal_stub(**kwargs):
        return create_stub_response(
            "echo_meta_liminal", hint="Meta-liminal analysis and transformation"
        )

    async def echo_ping_stub(**kwargs):
        return {
            "ok": True,
            "result": "pong",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        }

    async def echo_health_stub(**kwargs):
        return {
            "ok": True,
            "result": "healthy",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        }

    registry.register_base("echo_decide", echo_decide_stub)
    registry.register_base("echo_quantum_coding", echo_quantum_coding_stub)
    registry.register_base("echo_meta_liminal", echo_meta_liminal_stub)
    registry.register_base("echo_ping", echo_ping_stub)
    registry.register_base("echo_health", echo_health_stub)

    return registry


# 자동 초기화
initialize_tools()
