from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PlanNode:
    id: str
    title: str
    kind: str  # e.g., "PLAN" | "SUBPLAN" | "ACTION"
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    children: List["PlanNode"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "kind": self.kind,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "children": [c.to_dict() for c in self.children],
        }


class GoalPlannerV2:
    """High-level → subplan → executable actions tree builder.

    Minimal, deterministic scaffolding:
    - create_plan: builds root PLAN node
    - expand_subplans: derives SUBPLAN and ACTION nodes
    """

    def __init__(self, schema_path: str | Path):
        self.schema_path = Path(schema_path)
        logger.debug("GoalPlannerV2 initialized with schema: %s", self.schema_path)

    def create_plan(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        root = PlanNode(
            id=intent.get("id", "plan-1"),
            title=intent.get("title", "Untitled Plan"),
            kind="PLAN",
            inputs={"intent": intent},
        )
        logger.info("Created root plan node: %s", root.id)
        return root.to_dict()

    def expand_subplans(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        # Simple rule-based expansion compatible with v10 loop
        root = self._from_dict(plan)
        topic = root.inputs.get("intent", {}).get("topic", "general")

        # Example decomposition (replace with domain rules):
        research = PlanNode(
            id=f"{root.id}-s1", title="Collect evidence", kind="SUBPLAN"
        )
        research.children.append(
            PlanNode(
                id=f"{research.id}-a1", title=f"Search about {topic}", kind="ACTION"
            )
        )
        research.children.append(
            PlanNode(id=f"{research.id}-a2", title="Summarize sources", kind="ACTION")
        )

        reasoning = PlanNode(
            id=f"{root.id}-s2", title="Reason and draft answer", kind="SUBPLAN"
        )
        reasoning.children.append(
            PlanNode(id=f"{reasoning.id}-a1", title="Outline key claims", kind="ACTION")
        )
        reasoning.children.append(
            PlanNode(id=f"{reasoning.id}-a2", title="Draft response", kind="ACTION")
        )

        verify = PlanNode(id=f"{root.id}-s3", title="Verify & finalize", kind="SUBPLAN")
        verify.children.append(
            PlanNode(id=f"{verify.id}-a1", title="Run verifier", kind="ACTION")
        )
        verify.children.append(
            PlanNode(id=f"{verify.id}-a2", title="Bind evidence", kind="ACTION")
        )

        root.children = [research, reasoning, verify]
        logger.info("Expanded plan %s into %d subplans", root.id, len(root.children))
        return root.to_dict()

    def export_schema(self) -> None:
        if not self.schema_path.parent.exists():
            self.schema_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "node_kinds": ["PLAN", "SUBPLAN", "ACTION"],
            "required_keys": {"PLAN": ["id", "title", "children"]},
        }
        self.schema_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("Plan schema exported to %s", self.schema_path)

    # --- helpers ---
    def _from_dict(self, data: Dict[str, Any]) -> PlanNode:
        node = PlanNode(
            id=data["id"], title=data.get("title", ""), kind=data.get("kind", "PLAN")
        )
        node.inputs = data.get("inputs", {})
        node.outputs = data.get("outputs", {})
        node.children = [self._from_dict(c) for c in data.get("children", [])]
        return node
