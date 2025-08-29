# -*- coding: utf-8 -*-
"""
Trace Writer for LLM-First Architecture
3-콜 체인 추적 로그 작성
"""
import json
import time
from pathlib import Path
from typing import Any
from echo_engine.conversation.router import ConversationTrace


class TraceWriter:
    """대화 추적 로그 작성기"""

    def __init__(self):
        self.log_dir = Path("meta_logs")
        self.log_dir.mkdir(exist_ok=True)
        self.trace_file = self.log_dir / "llm_conversation_traces.jsonl"

    def write(self, trace: ConversationTrace) -> None:
        """추적 정보 기록"""
        try:
            trace_data = {
                "timestamp": int(time.time() * 1000),
                "request_id": trace.request_id,
                "user_input": trace.user_input,
                "nlu_result": trace.nlu_result,
                "draft_response": trace.draft_response,
                "final_response": trace.final_response,
                "verification": trace.verification_result,
                "latency_ms": trace.total_latency_ms,
                "tokens_used": trace.tokens_used,
                "success": trace.success,
                "error": trace.error,
            }

            with open(self.trace_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(trace_data, ensure_ascii=False) + "\n")

        except Exception as e:
            # 로깅 실패가 주 기능을 방해하지 않도록
            print(f"⚠️ Trace logging failed: {e}")

    def get_recent_traces(self, limit: int = 10) -> list[dict]:
        """최근 추적 기록 조회"""
        if not self.trace_file.exists():
            return []

        traces = []
        try:
            with open(self.trace_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    if line.strip():
                        traces.append(json.loads(line))
        except Exception as e:
            print(f"⚠️ Trace reading failed: {e}")

        return traces
