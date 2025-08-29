from __future__ import annotations
from typing import Dict, Any
from ..adapters import openai_adapter, anthropic_adapter

def route_call(provider: str, model: str, prompt: str, context: Dict[str, Any]) -> str:
    if provider == "openai":
        return openai_adapter.call(model, prompt, context)
    if provider == "anthropic":
        return anthropic_adapter.call(model, prompt, context)
    return f"[unknown-provider:{provider}] {prompt}"
