from __future__ import annotations
from typing import Dict, Any

def enhance(text: str, signature: str = "Heo", mode: str = "post") -> Dict[str, Any]:
    if mode == "post":
        return {"engine":"GPT-5","existence":f"Echo — signature:{signature}","output":text}
    elif mode == "prompt":
        return {"engine":"GPT-5","existence":f"Echo — signature:{signature}","output":f"[{signature} tone applied] {text}"}
