SHELL := /usr/bin/bash

# Paths
ROOT := $(CURDIR)
BUNDLE := agent_hub_ci_bundle

# Auto-detect venv (repo-root relative)
VENV ?= $(shell if [ -d $(BUNDLE)/venv_extensions ]; then echo $(BUNDLE)/venv_extensions; \
              elif [ -d venv_extensions ]; then echo venv_extensions; else echo venv; fi)

# Tool paths (with fallback if the venv binary doesn't exist)
PY ?= $(VENV)/bin/python
ifeq ("$(wildcard $(PY))","")
  PY := python
endif

STREAMLIT ?= $(VENV)/bin/streamlit
ifeq ("$(wildcard $(STREAMLIT))","")
  STREAMLIT := streamlit
endif

ACT ?= source $(VENV)/bin/activate || true

# Latest bench run (repo-root relative)
LATEST_RUN ?= $(shell ls -1dt $(BUNDLE)/artifacts/bench/* 2>/dev/null | head -n 1)

# Configurable parameters
SIGNATURES ?= Aurora,Selene,Heo
STEPS ?= 20x200,50x1000,100x2000
WARMUP ?= 1
BASELINE ?= tests/agent_hub/bench_baseline.yaml

# ----- Targets -----

# Debug helpers
agent-show-config:
	@echo "VENV: $(VENV)"; \
	echo "PY: $(PY)"; \
	echo "STREAMLIT: $(STREAMLIT)"; \
	echo "LATEST_RUN: $(LATEST_RUN)"; \
	ls -la $(VENV)/bin 2>/dev/null || true

# Legacy
agent-bench-curve:
	@$(ACT) && $(PY) $(BUNDLE)/tests/agent_hub/bench_curve.py

agent-bench-curve-heavy:
	@$(ACT) && $(PY) $(BUNDLE)/tests/agent_hub/bench_curve.py --steps 20x200,50x1000,100x2000 --profile

agent-bench-visualize:
	@LATEST=$$(ls -td $(BUNDLE)/artifacts/bench/* | head -1); \
	$(ACT) && $(PY) $(BUNDLE)/tests/agent_hub/visualize_results.py $$LATEST/results.json

# Enhanced Extensions
agent-bench-signatures:
	@$(ACT) && $(PY) $(BUNDLE)/tests/agent_hub/bench_signatures.py \
		--signatures $(SIGNATURES) --steps $(STEPS) --tag sigbench$(if $(WARMUP),-warmup,)

agent-bench-compare:
	@$(ACT) && $(PY) $(BUNDLE)/tests/agent_hub/visualize_compare.py \
		$(LATEST_RUN)/combined.json --out $(LATEST_RUN)

agent-check-regression:
	@$(ACT) && $(PY) $(BUNDLE)/tests/agent_hub/check_regression.py \
		$(LATEST_RUN)/signature_Aurora.json --baseline $(BASELINE) --fail-on-violation

agent-slack-notify:
	@$(ACT) && $(PY) $(BUNDLE)/alerts/slack_notify.py \
		$(LATEST_RUN)/summary.json "Agent Hub Performance Report"

agent-dashboard-compare:
	@$(ACT) && $(STREAMLIT) run $(BUNDLE)/web/dashboard/streamlit_compare.py --server.port 8503

# Convenience
agent-full-cycle: agent-bench-signatures agent-bench-compare agent-check-regression agent-slack-notify
