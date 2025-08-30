SHELL := /usr/bin/bash

BUNDLE := agent_hub_ci_bundle
VENV ?= $(BUNDLE)/venv_extensions
ACT  ?= source $(VENV)/bin/activate || true

# 최신 벤치 결과 폴더
LATEST_RUN ?= $(shell ls -1dt $(BUNDLE)/artifacts/bench/* 2>/dev/null | head -n 1)

# 파라미터
SIGNATURES ?= Aurora,Selene,Heo
STEPS ?= 20x200,50x1000,100x2000
WARMUP ?= 1
BASELINE ?= tests/agent_hub/bench_baseline.yaml

# ---- Debug ----
agent-show-config:
	@echo "VENV: $(VENV)"; \
	ls -la $(VENV)/bin 2>/dev/null || true; \
	which python || true; python -V || true

# ---- Targets ----
agent-bench-curve:
	@$(ACT) && python $(BUNDLE)/tests/agent_hub/bench_curve.py

agent-bench-curve-heavy:
	@$(ACT) && python $(BUNDLE)/tests/agent_hub/bench_curve.py --steps 20x200,50x1000,100x2000 --profile

agent-bench-visualize:
	@LATEST=$$(ls -td $(BUNDLE)/artifacts/bench/* | head -1); \
	$(ACT) && python $(BUNDLE)/tests/agent_hub/visualize_results.py $$LATEST/results.json

agent-bench-signatures:
	@$(ACT) && python $(BUNDLE)/tests/agent_hub/bench_signatures.py \
		--signatures $(SIGNATURES) --steps $(STEPS) --tag sigbench$(if $(WARMUP),-warmup,)

agent-bench-compare:
	@if [ -z "$(LATEST_RUN)" ]; then echo "No bench results found, skipping compare"; exit 0; fi; \
	if [ ! -f "$(LATEST_RUN)/combined.json" ]; then echo "No combined.json found, skipping compare"; exit 0; fi; \
	$(ACT) && python $(BUNDLE)/tests/agent_hub/visualize_compare.py \
		$(LATEST_RUN)/combined.json --out-dir $(LATEST_RUN)

agent-check-regression:
	@if [ -z "$(LATEST_RUN)" ]; then echo "No bench results found, skipping regression check"; exit 0; fi; \
	if [ ! -f "$(LATEST_RUN)/signature_Aurora.json" ]; then echo "No Aurora results found, skipping regression check"; exit 0; fi; \
	$(ACT) && python $(BUNDLE)/tests/agent_hub/check_regression.py \
		$(LATEST_RUN)/signature_Aurora.json --baseline $(BASELINE) --fail-on-violation

agent-slack-notify:
	@if [ -z "$(LATEST_RUN)" ]; then echo "No bench results found, skipping Slack notify"; exit 0; fi; \
	if [ ! -f "$(LATEST_RUN)/summary.json" ]; then echo "No summary.json found, skipping Slack notify"; exit 0; fi; \
	$(ACT) && python $(BUNDLE)/alerts/slack_notify.py \
		$(LATEST_RUN)/summary.json "Agent Hub Performance Report"

agent-dashboard-compare:
	@$(ACT) && streamlit run $(BUNDLE)/web/dashboard/streamlit_compare.py --server.port 8503

# 편의
agent-full-cycle: agent-bench-signatures agent-bench-compare agent-check-regression agent-slack-notify
