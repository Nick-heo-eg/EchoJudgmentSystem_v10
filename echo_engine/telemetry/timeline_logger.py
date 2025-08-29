# echo_engine/telemetry/timeline_logger.py
import json
from pathlib import Path

LOG = Path("data/logs/liminal_transitions.jsonl")


def log_transition(state: str, trigger: str, by: str, note: str = ""):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": __import__("datetime").datetime.now().isoformat(),
        "state": state,
        "trigger": trigger,
        "by": by,
        "note": note,
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_log():
    if not LOG.exists():
        return []
    return [
        json.loads(l) for l in LOG.read_text(encoding="utf-8").splitlines() if l.strip()
    ]
