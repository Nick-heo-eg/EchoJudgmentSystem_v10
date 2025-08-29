from __future__ import annotations
import time
from dataclasses import dataclass


@dataclass
class Budget:
    seconds: float = 5.0
    tool_calls: int = 5


class ExecutionBudgeter:
    def __init__(self, budget: Budget | None = None):
        self.budget = budget or Budget()
        self._start = time.time()
        self._tool_calls = 0

    def time_ok(self) -> bool:
        return (time.time() - self._start) <= self.budget.seconds

    def tool_ok(self) -> bool:
        return self._tool_calls < self.budget.tool_calls

    def consume_tool(self) -> None:
        self._tool_calls += 1

    def remaining(self) -> dict:
        return {
            "seconds_left": max(0.0, self.budget.seconds - (time.time() - self._start)),
            "tool_calls_left": max(0, self.budget.tool_calls - self._tool_calls),
        }
