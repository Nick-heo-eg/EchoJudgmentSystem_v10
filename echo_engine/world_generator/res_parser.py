"""
Response parser compatibility shim.
Delegates to root world_generator.res_parser when possible.
"""

from __future__ import annotations
from typing import Any, Dict


def parse_emotion_from_reasoning(reasoning: str) -> str:
    """Parse emotion from reasoning text with fallback."""
    try:
        # Try to delegate to existing world_generator logic
        import echo_engine.world_generator.res_parser as wrp  # type: ignore

        if hasattr(wrp, "parse_emotion_from_reasoning"):
            return wrp.parse_emotion_from_reasoning(reasoning)  # type: ignore
    except Exception:
        pass

    # Safe fallback - basic emotion detection
    reasoning_lower = str(reasoning).lower()
    if any(word in reasoning_lower for word in ["happy", "joy", "glad", "excited"]):
        return "joy"
    elif any(word in reasoning_lower for word in ["sad", "disappointed", "upset"]):
        return "sad"
    elif any(word in reasoning_lower for word in ["angry", "frustrated", "mad"]):
        return "anger"
    elif any(word in reasoning_lower for word in ["scared", "afraid", "worried"]):
        return "fear"
    else:
        return "calm"
