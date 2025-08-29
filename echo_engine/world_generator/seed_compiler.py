from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class SeedConfig:
    payload: Dict[str, Any] = field(default_factory=dict)


def compile_seed(seed: Any, **kwargs) -> Dict[str, Any]:
    """
    Minimal, safe normalizer:
    - dict → as-is
    - SeedConfig → payload
    - str/other → wrapped dict (lossless)
    """
    if isinstance(seed, SeedConfig):
        base = dict(seed.payload)
        base.update(kwargs)
        return base
    if isinstance(seed, dict):
        base = dict(seed)
        base.update(kwargs)
        return base
    return {"seed": seed, **kwargs}
