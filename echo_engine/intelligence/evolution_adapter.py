"""
Evolution Adapter - Thin adapter over PatternMemory for learning hints
======================================================================

Thin adapter that records success/failure capsules and provides simple
improvement hints for the next reasoning turn.
"""

from typing import Any, Dict
from echo_engine.reflect.pattern_memory import PatternMemory


class EvolutionAdapter:
    """Thin adapter over PatternMemory: record + suggest small nudges."""

    def __init__(self, memory: PatternMemory = None) -> None:
        self.memory = memory or PatternMemory("data/pattern_memory/capsules.json")

    def record(self, success: bool, capsule: Dict[str, Any]) -> None:
        """
        Record a success/failure experience in pattern memory.

        Args:
            success: Whether the reasoning/judgment was successful
            capsule: Data capsule containing context and metrics
        """
        kind = "success" if success else "failure"
        self.memory.add(kind, capsule)

    def next_hint(self) -> Dict[str, Any]:
        """
        Generate a simple hint for the next reasoning turn based on patterns.

        Returns:
            Dictionary with hint and optional parameters
        """
        # Get current bias summary
        summary = self.memory.summarize_bias()

        success_count = summary.get("success_count", 0)
        failure_count = summary.get("failure_count", 0)

        # Simple heuristic hints
        if failure_count > success_count and failure_count > 2:
            return {
                "hint": "Increase evidence count and run verifier twice.",
                "reason": "failure_dominant",
                "suggested_adjustments": {
                    "min_evidence_count": 3,
                    "verification_passes": 2,
                },
            }

        elif success_count > failure_count * 2 and success_count > 5:
            return {
                "hint": "Performance looks stable. Consider optimizing for speed.",
                "reason": "success_dominant",
                "suggested_adjustments": {
                    "allow_faster_strategies": True,
                    "reduce_verification_overhead": True,
                },
            }

        else:
            return {
                "hint": "Looks stable. Keep current routing.",
                "reason": "balanced",
                "suggested_adjustments": {},
            }

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get basic learning statistics."""
        summary = self.memory.summarize_bias()

        total_experiences = summary.get("success_count", 0) + summary.get(
            "failure_count", 0
        )
        success_rate = summary.get("success_count", 0) / max(total_experiences, 1)

        return {
            "total_experiences": total_experiences,
            "success_rate": success_rate,
            "pattern_summary": summary,
        }

    def reset_patterns(self) -> None:
        """Reset pattern memory - use with caution."""
        # Create a new empty pattern memory
        self.memory = PatternMemory("data/pattern_memory/capsules.json")
        # Note: This doesn't clear the file, just creates a new in-memory instance
