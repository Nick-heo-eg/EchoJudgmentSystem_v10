from __future__ import annotations
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class EvidenceBinder:
    """Bind answer text with structured evidence list."""

    def bind(self, answer: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        bundle = {
            "answer": answer,
            "evidence": evidence,
            "meta": {"evidence_count": len(evidence)},
        }
        logger.debug("Bound evidence: %d items", len(evidence))
        return bundle
