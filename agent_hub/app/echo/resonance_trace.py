from __future__ import annotations
import json, os, time

TRACE_DIR = os.environ.get("ECHO_TRACE_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "traces"))

def save(record: dict) -> str:
    os.makedirs(TRACE_DIR, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = os.path.join(TRACE_DIR, f"trace_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return path
