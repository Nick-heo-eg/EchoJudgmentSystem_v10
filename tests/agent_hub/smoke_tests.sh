#!/usr/bin/env bash
set -euo pipefail
BASE="http://localhost:8014"

jq_check() { command -v jq >/dev/null 2>&1; }

echo "== Root =="
if jq_check; then curl -fsS "$BASE/" | jq; else curl -fsS "$BASE/"; fi

echo "== Health =="
if jq_check; then curl -fsS "$BASE/health" | jq; else curl -fsS "$BASE/health"; fi

echo "== Echo (direct) =="
curl -fsS "$BASE/echo" \
  -H "Content-Type: application/json" \
  -d '{"text":"테스트 문장입니다. 핵심만 뽑아줘.","context":{"tasks":["summarize","keywords"],"lang":"ko","trace_id":"smoke-echo-01"}}' | { jq 2>/dev/null || cat; }

echo "== Echo (file) =="
curl -fsS "$BASE/echo/file" \
  -H "Content-Type: application/json" \
  -d '{"file_chunks":["샘플 파일입니다. 파일 분석과 요약을 수행합니다.","두 번째 청크입니다."],"context":{"trace_id":"smoke-file-01"}}' | { jq 2>/dev/null || cat; }

echo "== Invoke (AI + Echo) =="
curl -fsS "$BASE/invoke/echo" \
  -H "Content-Type: application/json" \
  -d '{"agent":"gpt","prompt":"간단한 회귀 테스트 목록을 만들어줘","context":{"trace_id":"smoke-invoke-01"}}' | { jq 2>/dev/null || cat; }

echo "== Stats =="
if jq_check; then curl -fsS "$BASE/echo/stats" | jq; else curl -fsS "$BASE/echo/stats"; fi

echo "✅ Smoke tests completed."