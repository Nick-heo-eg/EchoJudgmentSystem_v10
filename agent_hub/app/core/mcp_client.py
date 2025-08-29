from __future__ import annotations
from typing import Dict, Any, List
from .tool_api import builtin_tools
from ..connectors import notion_connector, slack_connector, web_search_connector, file_connector

external_tools = {
    "notion": notion_connector.mcp_notion,
    "slack": slack_connector.mcp_slack,
    "websearch": web_search_connector.mcp_websearch,
    "file": file_connector.mcp_file,
}

class MCPClient:
    def __init__(self, tools_config: List[dict]):
        self._tools = {t["id"]: t for t in tools_config}

    def run_tools(self, tool_ids: List[str], payload: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        for tid in tool_ids or []:
            if tid in builtin_tools:
                results[tid] = builtin_tools[tid](payload)
            elif tid in external_tools:
                ctx = payload.get("context", {})
                tool_payload = {**payload, **ctx}
                results[tid] = external_tools[tid](tool_payload)
            else:
                results[tid] = {"status":"error", "error": f"tool '{tid}' not available"}
        return results
