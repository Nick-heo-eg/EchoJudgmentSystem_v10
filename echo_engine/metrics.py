# -*- coding: utf-8 -*-
"""
Route/Metrics logger for Echo.
Writes JSON Lines to meta_logs/route_metrics.jsonl
"""
from __future__ import annotations
import os, json, time, uuid
from pathlib import Path
from typing import Any, Dict, Optional

LOG_DIR = Path(os.getenv("ECHO_LOG_DIR", "meta_logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "route_metrics.jsonl"


def _now_ms() -> int:
    return int(time.time() * 1000)


def log_route_event(event: Dict[str, Any]) -> None:
    """
    event minimal fields (others optional):
      - event_id, ts_ms, route, confidence
      - engine_set(bool), coding(bool), profile(str)
      - tool(str|None), latency_ms(int|None)
      - tokens: {prompt, completion, total} (optional)
      - success(bool|None), error_type(str|None), message(str|None)
    """
    try:
        event.setdefault("event_id", str(uuid.uuid4()))
        event.setdefault("ts_ms", _now_ms())
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        # Logging must never crash main flow
        pass
