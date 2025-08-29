from __future__ import annotations
from typing import Dict

# Try to delegate to existing logic if present.
try:
    # If your real logic lives here, we reuse it.
    from echo_engine import warden_world as ww  # type: ignore
except Exception:
    ww = None

# Conservative defaults (safe, deterministic). Adjust later if needed.
_STRATEGY_MAP: Dict[str, str] = {
    "baseline": "◇",
    "aggressive": "⚡",
    "defensive": "🛡",
    "explore": "🧭",
}

_EMOTION_MAP: Dict[str, str] = {
    "calm": "・",
    "focus": "◆",
    "warn": "!",
    "halt": "‖",
    "joy": "☺",
    "sad": "…",
    "anger": "✕",
    "fear": "△",
}


def map_strategy_to_symbol(strategy: str) -> str:
    if ww and hasattr(ww, "map_strategy_to_symbol"):
        return ww.map_strategy_to_symbol(strategy)  # type: ignore[attr-defined]
    return _STRATEGY_MAP.get(str(strategy).lower(), str(strategy))


def map_emotion_to_symbol(emotion: str) -> str:
    if ww and hasattr(ww, "map_emotion_to_symbol"):
        return ww.map_emotion_to_symbol(emotion)  # type: ignore[attr-defined]
    return _EMOTION_MAP.get(str(emotion).lower(), str(emotion))
