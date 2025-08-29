from __future__ import annotations
from typing import Any, Dict
import datetime as dt

def _tool_time(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"now_iso": dt.datetime.utcnow().isoformat() + "Z"}

def _tool_echo(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"echo": payload.get("text") or payload}

builtin_tools = {
    "time": _tool_time,
    "echo": _tool_echo,
}
