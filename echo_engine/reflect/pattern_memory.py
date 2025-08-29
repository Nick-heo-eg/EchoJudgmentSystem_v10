from __future__ import annotations
from typing import Any, Dict, List
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class PatternMemory:
    """Stores success/failure patterns as lightweight capsules."""

    def __init__(self, store_file: str | Path):
        self.store_file = Path(store_file)
        if not self.store_file.exists():
            self._write({"success": [], "failure": []})

    def _read(self) -> Dict[str, List[Dict[str, Any]]]:
        return json.loads(self.store_file.read_text(encoding="utf-8"))

    def _write(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        self.store_file.parent.mkdir(parents=True, exist_ok=True)
        self.store_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def add(self, kind: str, capsule: Dict[str, Any]) -> None:
        data = self._read()
        bucket = "success" if kind == "success" else "failure"
        data[bucket].append(capsule)
        # keep last 200 per bucket
        data[bucket] = data[bucket][-200:]
        self._write(data)
        logger.debug("Pattern added to %s", bucket)

    def summarize_bias(self) -> Dict[str, Any]:
        data = self._read()
        return {
            "success_count": len(data["success"]),
            "failure_count": len(data["failure"]),
        }
