from __future__ import annotations
from typing import Dict, Any
import os, anthropic

def call(model: str, prompt: str, context: Dict[str, Any]) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    resp = client.messages.create(
        model=model,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text
