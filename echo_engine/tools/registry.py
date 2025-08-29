import os
from typing import Dict, Callable, Any, Optional
import logging

# Enhanced 우선 정책
PREFER_ENHANCED = os.getenv("ECHO_PREFER_ENHANCED", "true").lower() in (
    "1",
    "true",
    "yes",
)
DISABLED_TOOLS = set(
    t.strip() for t in os.getenv("ECHO_DISABLED_TOOLS", "").split(",") if t.strip()
)

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self):
        self.base_tools: Dict[str, Callable] = {}
        self.enhanced_tools: Dict[str, Callable] = {}

    def register_base(self, name: str, handler: Callable):
        """기본 도구 등록"""
        self.base_tools[name] = handler
        logger.info(f"✅ Registered base tool: {name}")

    def register_enhanced(self, name: str, handler: Callable):
        """Enhanced 도구 등록"""
        self.enhanced_tools[name] = handler
        logger.info(f"🚀 Registered enhanced tool: {name}")

    def resolve(self, tool_name: str) -> Optional[Callable]:
        """도구 이름으로 핸들러 해결 (Enhanced 우선)"""
        if tool_name in DISABLED_TOOLS:
            raise RuntimeError(f"Tool '{tool_name}' is disabled by policy")

        # Enhanced 우선 정책
        if PREFER_ENHANCED and tool_name in self.enhanced_tools:
            logger.debug(f"🔄 Routing {tool_name} -> enhanced version")
            return self.enhanced_tools[tool_name]

        # 기본 도구 폴백
        if tool_name in self.base_tools:
            logger.debug(f"📦 Using base version: {tool_name}")
            return self.base_tools[tool_name]

        return None

    def invoke(self, tool_name: str, **kwargs) -> Any:
        """도구를 직접 호출"""
        handler = self.resolve(tool_name)
        if not handler:
            raise RuntimeError(f"Tool '{tool_name}' not found")

        try:
            # 도구 클래스의 인스턴스인 경우 run 메서드 호출
            if hasattr(handler, "run"):
                return handler.run(**kwargs)
            # 일반 함수인 경우 직접 호출
            else:
                return handler(**kwargs)
        except Exception as e:
            raise RuntimeError(f"Tool '{tool_name}' execution failed: {e}")

    def list_available(self) -> Dict[str, Any]:
        """사용 가능한 도구 목록 (16개)"""
        available = {}
        all_tools = set(self.base_tools.keys()) | set(self.enhanced_tools.keys())

        for tool_name in sorted(all_tools):
            if tool_name not in DISABLED_TOOLS:
                # Enhanced 여부 표시
                has_enhanced = tool_name in self.enhanced_tools
                using_enhanced = PREFER_ENHANCED and has_enhanced

                available[tool_name] = {
                    "name": tool_name,
                    "endpoint": f"/{tool_name.replace('_', '-')}",
                    "has_enhanced": has_enhanced,
                    "using_enhanced": using_enhanced,
                    "status": "active",
                }

        return available


# 글로벌 레지스트리
_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    return _registry
