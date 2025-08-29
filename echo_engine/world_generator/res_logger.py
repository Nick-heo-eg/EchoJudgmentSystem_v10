"""
Response logger compatibility shim.
Delegates to root world_generator.res_logger when possible.
"""

from __future__ import annotations
from typing import Any


def save_res_log(*args, **kwargs) -> None:
    """Save response log with delegation."""
    try:
        # Try to delegate to existing world_generator logic
        import echo_engine.world_generator.res_logger as wrl  # type: ignore

        if hasattr(wrl, "save_res_log"):
            wrl.save_res_log(*args, **kwargs)  # type: ignore
            return
    except Exception:
        pass

    # Safe fallback - minimal logging
    print(f"[res_logger] args={args}, kwargs={kwargs}")
