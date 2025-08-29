from __future__ import annotations
from typing import Dict, Any

ROUTES = {
    "search": ["what is", "latest", "news", "find"],
    "calc": ["sum", "average", "compute", "calculate"],
    "code": ["write code", "refactor", "bug", "script"],
    "affect": ["feeling", "emotion", "mood"],
}


class IntentRouterV2:
    """Hybrid rule stub. Can be extended with model scoring."""

    def route(self, query: str) -> Dict[str, Any]:
        q = query.lower()
        for name, keys in ROUTES.items():
            if any(k in q for k in keys):
                return {"route": name, "confidence": 0.7}
        return {"route": "signature", "confidence": 0.4}
