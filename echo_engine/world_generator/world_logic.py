"""
World logic compatibility shim.
Delegates to root world_generator.world_logic when possible.
"""

from __future__ import annotations
from typing import Any, Dict


def generate_world(*args, **kwargs) -> Dict[str, Any]:
    """Safe world generation with fallback."""
    try:
        # Try to delegate to existing world_generator logic
        import echo_engine.world_generator.world_logic as wgl  # type: ignore

        if hasattr(wgl, "generate_world"):
            return wgl.generate_world(*args, **kwargs)  # type: ignore
    except Exception:
        pass

    # Safe fallback - return minimal world structure
    return {
        "world_id": "minimal_world",
        "status": "generated",
        "args": args,
        "kwargs": kwargs,
    }
