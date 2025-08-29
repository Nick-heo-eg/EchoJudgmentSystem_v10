from __future__ import annotations
from typing import Dict, Any

def before_invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    return payload

def after_invoke(response: Dict[str, Any]) -> Dict[str, Any]:
    return response
