from datetime import datetime
from typing import Dict, Any


def create_stub_response(
    module: str, version: str = "0.1.0-stub", hint: str = None
) -> Dict[str, Any]:
    """표준 스텁 응답 생성"""
    return {
        "ok": True,
        "module": module,
        "mode": "development_stub",
        "version": version,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "result": f"{module} is in development",
        "hint": hint
        or f"{module} module scaffold registered. Full implementation coming soon.",
        "next_steps": [
            "Module interface defined",
            "Backend integration in progress",
            "Full functionality will be available soon",
        ],
    }
