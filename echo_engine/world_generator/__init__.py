"""
Compatibility shims for legacy `world_generator` imports.
This package provides a stable import surface under `echo_engine.world_generator.*`.
"""

from .symbol_mapper import map_strategy_to_symbol, map_emotion_to_symbol
from .seed_compiler import compile_seed, SeedConfig

__all__ = [
    "map_strategy_to_symbol",
    "map_emotion_to_symbol",
    "compile_seed",
    "SeedConfig",
]
