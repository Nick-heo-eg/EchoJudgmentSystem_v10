from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from .core.registry import Registry
from .core.mcp_client import MCPClient
from .core.router import route_call
from .echo import signature_bridge, resonance_trace, hooks, echo_engine_bridge

app = FastAPI(title="Echo Agent Hub v0.4 (alpha1) — File Connector")

registry = Registry()
mcp = MCPClient(registry.list_tools())

class InvokeReq(BaseModel):
    agent: str = Field(..., description="agent id defined in config")
    prompt: str
    tools: Optional[List[str]] = None
    context: Dict[str, Any] = {}

class EchoReq(BaseModel):
    text: str = Field(..., description="text to process with Echo engine")
    context: Dict[str, Any] = {}

class FileEchoReq(BaseModel):
    file_chunks: List[str] = Field(..., description="file chunks to process")
    context: Dict[str, Any] = {}

@app.get("/")
def root():
    """Agent Hub + Echo 통합 시스템 루트"""
    return {
        "service": "Echo Agent Hub v0.4 (alpha1) — File Connector", 
        "status": "running",
        "echo_integration": "✅ EchoJudgmentSystem v10.5 최적화 엔진",
        "performance": "734K+ ops/sec",
        "endpoints": {
            "health": "/health",
            "agents": "/agents", 
            "tools": "/tools",
            "invoke": "/invoke",
            "echo_direct": "/echo",
            "echo_file": "/echo/file", 
            "echo_stats": "/echo/stats",
            "echo_invoke": "/invoke/echo",
            "api_docs": "/docs"
        }
    }

@app.get("/health")
def health():
    echo_health = echo_engine_bridge.echo_health_check()
    return {
        "status": "ok", 
        "agents": len(registry.list_agents()), 
        "tools": len(registry.list_tools()),
        "echo_engine": echo_health
    }

@app.get("/agents")
def agents():
    return registry.list_agents()

@app.get("/tools")
def tools():
    return registry.list_tools()

@app.post("/invoke")
def invoke(req: InvokeReq):
    payload = hooks.before_invoke(req.model_dump())
    agent = registry.get_agent(payload["agent"])
    if not agent:
        raise HTTPException(400, f"unknown agent '{payload['agent']}'")
    tool_results = mcp.run_tools(payload.get("tools") or [], {"text": payload["prompt"], "context": payload.get("context", {})})
    call_ctx = dict(payload.get("context", {}))
    call_ctx["tools"] = tool_results
    text = route_call(agent.get("provider"), agent.get("model"), payload["prompt"], call_ctx)
    enriched = signature_bridge.enhance(text, signature="Heo", mode="post")
    record = {"request": payload, "tool_results": tool_results, "model_text": text, "enriched": enriched}
    resonance_trace.save(record)
    return hooks.after_invoke(enriched)

@app.post("/echo")
def echo_process(req: EchoReq):
    """Echo 엔진으로 직접 텍스트 처리 (734K+ ops/sec)"""
    result = echo_engine_bridge.process_text_with_echo(req.text, req.context)
    return result

@app.post("/echo/file")
def echo_file_process(req: FileEchoReq):
    """Echo 엔진으로 파일 청크 처리 및 분석"""
    result = echo_engine_bridge.process_file_with_echo(req.file_chunks, req.context)
    return result

@app.get("/echo/stats")
def echo_stats():
    """Echo 엔진 성능 통계"""
    return echo_engine_bridge.echo_stats()

@app.post("/invoke/echo")
def invoke_with_echo(req: InvokeReq):
    """기존 invoke를 Echo 엔진으로 강화"""
    payload = hooks.before_invoke(req.model_dump())
    agent = registry.get_agent(payload["agent"])
    if not agent:
        raise HTTPException(400, f"unknown agent '{payload['agent']}'")
    
    # 도구 실행
    tool_results = mcp.run_tools(payload.get("tools") or [], {"text": payload["prompt"], "context": payload.get("context", {})})
    
    # 도구 결과를 포함한 컨텍스트 구성
    call_ctx = dict(payload.get("context", {}))
    call_ctx["tools"] = tool_results
    
    # Echo 엔진으로 처리 (기존 모델 대신)
    echo_result = echo_engine_bridge.process_text_with_echo(
        payload["prompt"], 
        call_ctx
    )
    
    # Echo 결과를 signature_bridge로 추가 강화
    text = echo_result.get("text", payload["prompt"])
    enriched = signature_bridge.enhance(text, signature="Echo-Aurora", mode="post")
    
    # Echo 정보 추가
    enriched["echo_processing"] = {
        "performance_mode": echo_result.get("performance_mode", "unknown"),
        "processing_time_ms": echo_result.get("processing_time_ms", 0),
        "emotion_analysis": echo_result.get("emotion_analysis", {}),
        "intent_classification": echo_result.get("intent_classification", {}),
        "persona_signature": echo_result.get("persona_signature", "Echo-Aurora")
    }
    
    # 기록 저장
    record = {
        "request": payload,
        "tool_results": tool_results, 
        "echo_result": echo_result,
        "enriched": enriched
    }
    resonance_trace.save(record)
    
    return hooks.after_invoke(enriched)
