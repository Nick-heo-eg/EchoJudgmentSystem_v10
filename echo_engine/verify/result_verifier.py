from __future__ import annotations
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class ResultVerifier:
    """Lightweight scorer for factuality, logic, safety.
    Scores are 0.0–1.0. Replace heuristics with model-backed checks if available.
    """

    def score_factual_accuracy(
        self, output: str, evidence: List[Dict[str, Any]]
    ) -> float:
        if not output:
            return 0.0
        if not evidence:
            return 0.3  # penalize lack of sources
        # naive: reward presence of citations-like markers
        has_refs = any("title" in e or "url" in e for e in evidence)
        return 0.8 if has_refs else 0.5

    def score_logical_consistency(self, output: str) -> float:
        # naive heuristic: penalize very short or contradictory words
        if len(output.split()) < 10:
            return 0.4
        contradictory = any(
            tok in output.lower()
            for tok in ["contradict", "paradox", "however however"]
        )
        return 0.6 if contradictory else 0.9

    def score_safety(self, output: str) -> float:
        # minimal keyword guardrail placeholder
        blocked = any(w in output.lower() for w in ["malware", "explosive guide"])
        return 0.1 if blocked else 0.95

    def verify(self, output: str, evidence: List[Dict[str, Any]]) -> Dict[str, float]:
        scores = {
            "factual": self.score_factual_accuracy(output, evidence),
            "logic": self.score_logical_consistency(output),
            "safety": self.score_safety(output),
        }
        scores["aggregate"] = round(
            0.5 * scores["factual"] + 0.4 * scores["logic"] + 0.1 * scores["safety"], 3
        )
        logger.info("Verification scores: %s", scores)
        return scores
