from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
from pathlib import Path
import json
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class ReflectionRecord:
    run_id: str
    success: bool
    reason: str
    verifier_scores: Dict[str, float]
    timestamp: float
    tags: Dict[str, Any]


class ReflectionLogger:
    def __init__(self, store_dir: str | Path):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Reflection store at %s", self.store_dir)

    def log(
        self,
        run_id: str,
        success: bool,
        reason: str,
        verifier_scores: Dict[str, float],
        tags: Optional[Dict[str, Any]] = None,
    ) -> Path:
        rec = ReflectionRecord(
            run_id=run_id,
            success=success,
            reason=reason,
            verifier_scores=verifier_scores,
            timestamp=time.time(),
            tags=tags or {},
        )
        path = self.store_dir / f"{run_id}.json"
        path.write_text(
            json.dumps(asdict(rec), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("Reflection written: %s", path)
        return path
