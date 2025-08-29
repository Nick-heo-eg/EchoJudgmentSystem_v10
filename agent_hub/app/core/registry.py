from __future__ import annotations
from typing import Dict, Any, List
import yaml, os

CONFIG_PATH = os.environ.get("AGENT_HUB_CONFIG", os.path.join(os.path.dirname(__file__), "..", "config", "hub.yaml"))

class Registry:
    def __init__(self, path: str | None = None):
        self.path = path or CONFIG_PATH
        with open(self.path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        self.agents: List[dict] = data.get("agents", [])
        self.tools: List[dict] = data.get("tools", [])

    def get_agent(self, agent_id: str) -> Dict[str, Any] | None:
        return next((a for a in self.agents if a.get("id") == agent_id), None)

    def list_agents(self) -> List[dict]:
        return self.agents

    def list_tools(self) -> List[dict]:
        return self.tools
