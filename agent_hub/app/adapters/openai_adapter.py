from __future__ import annotations
from typing import Dict, Any
import os
from openai import OpenAI

def call(model: str, prompt: str, context: Dict[str, Any]) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are Echo Agent Hub adapter."},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content
