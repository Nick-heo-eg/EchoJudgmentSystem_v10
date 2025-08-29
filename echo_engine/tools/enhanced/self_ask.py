# -*- coding: utf-8 -*-
"""
SelfAskTool
Echo가 '스스로' 현재 사용 가능한 기능/도구/모드/환경을 조사하고,
사용자 질문에 대해 내부 능력 범위 내에서 답하도록 한다.
"""
from __future__ import annotations
from typing import Any, Dict, Optional
import os, json, platform, datetime


class SelfAskTool:
    name = "self_ask"
    description = "Inspect Echo's available tools, modes, and environment; answer meta-questions about capabilities."
    schema = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "User's meta question about Echo's capabilities",
            }
        },
    }

    def __init__(self):
        self._registry = None

    # 등록 시 레지스트리 주입 (존재하면)
    def set_registry(self, registry):
        self._registry = registry

    def _collect_tools(self) -> Dict[str, Dict[str, Any]]:
        tools = {}
        try:
            # 다양한 레지스트리 구현을 대응
            if hasattr(self._registry, "list_tools"):
                for t in self._registry.list_tools():
                    tools[t.name] = {
                        "description": getattr(t, "description", ""),
                        "schema": getattr(t, "schema", None),
                    }
            elif hasattr(self._registry, "tools"):
                # dict-like
                for name, t in getattr(self._registry, "tools").items():  # type: ignore
                    tools[getattr(t, "name", name)] = {
                        "description": getattr(t, "description", ""),
                        "schema": getattr(t, "schema", None),
                    }
        except Exception:
            pass
        return tools

    def _collect_env(self) -> Dict[str, Any]:
        return {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
            "engine": os.getenv("ECHO_ENGINE", ""),
            "profile": os.getenv("ECHO_PROFILE", ""),
            "now": datetime.datetime.now().isoformat(timespec="seconds"),
        }

    def run(self, question: Optional[str] = None, **_) -> Dict[str, Any]:
        tools = self._collect_tools()
        env = self._collect_env()
        summary_lines = []
        summary_lines.append("## Echo Self-Inspection")
        summary_lines.append(
            f"- Python: {env['python']}  |  Platform: {env['platform']}"
        )
        summary_lines.append(
            f"- Engine: {env['engine'] or '(unset)'}  |  OPENAI_API_KEY: {'yes' if env['has_openai_key'] else 'no'}"
        )
        summary_lines.append(
            f"- Profile: {env['profile'] or '(default)'}  |  Time: {env['now']}"
        )
        summary_lines.append("")
        summary_lines.append("### Available Tools")
        if tools:
            for n, meta in sorted(tools.items()):
                desc = (meta.get("description") or "").strip()
                summary_lines.append(f"- **{n}** — {desc[:160]}")
        else:
            summary_lines.append("- (No tools found or registry not injected)")
        summary_lines.append("")
        summary_lines.append("### Quick Usage")
        summary_lines.append("- 자연어: 그냥 물어보면 됩니다.")
        summary_lines.append(
            '- 도구 직접 호출: `TOOL:self_ask {"question":"에코 Self 질문 기능 있는지 검색해봐"}`'
        )
        summary_lines.append("- IDE 프로필 변경: `/profile full_code` (코딩시 추천)")
        summary_lines.append("")

        # 최소 응답 (LLM 없이도 동작)
        answer = "\n".join(summary_lines)
        # LLM 키가 있으면 질문 요약/가이드 생성 시도 (선택)
        if (
            question
            and env["has_openai_key"]
            and hasattr(self._registry, "call_llm_summary")
        ):
            try:
                tip = self._registry.call_llm_summary(
                    question=question, context={"tools": list(tools.keys())}
                )  # 옵셔널 API 가정
                if tip:
                    answer += "\n### Tip\n" + tip.strip()
            except Exception:
                pass

        return {"ok": True, "message_markdown": answer}
