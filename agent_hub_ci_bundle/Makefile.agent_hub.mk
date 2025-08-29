
# Enhanced Agent Hub Makefile with auto-detection and parameterization
# Include with: make -f Makefile.agent_hub.mk <target>

SHELL := /usr/bin/bash

# Auto-detect virtual environment path
VENV?=$(shell if [ -d agent_hub_ci_bundle/venv_extensions ]; then echo agent_hub_ci_bundle/venv_extensions; elif [ -d venv_extensions ]; then echo venv_extensions; else echo venv; fi)
PY?=$(VENV)/bin/python
ACT?=source $(VENV)/bin/activate

# Auto-detect latest benchmark run
LATEST_RUN?=$(shell ls -1dt agent_hub_ci_bundle/artifacts/bench/* 2>/dev/null | head -n 1)

# Configurable parameters
SIGNATURES?=Aurora,Selene,Heo
STEPS?=20x200,50x1000,100x2000
WARMUP?=1
BASELINE?=tests/agent_hub/bench_baseline.yaml

# Legacy targets (maintained for compatibility)
agent-bench-curve:
	@$(ACT) && python tests/agent_hub/bench_curve.py

agent-bench-curve-heavy:
	@$(ACT) && python tests/agent_hub/bench_curve.py --steps 20x200,50x1000,100x2000 --profile

agent-bench-visualize:
	LATEST=$$(ls -td artifacts/bench/* | head -1); \
	$(ACT) && python tests/agent_hub/visualize_results.py $$LATEST/results.json

# Enhanced Extensions with auto-detection and parameters
agent-bench-signatures:
	@$(ACT) && cd agent_hub_ci_bundle && $(PY) tests/agent_hub/bench_signatures.py \
		--signatures $(SIGNATURES) --steps $(STEPS) --tag sigbench$(if $(WARMUP),-warmup,)

agent-bench-compare:
	@$(ACT) && cd agent_hub_ci_bundle && $(PY) tests/agent_hub/visualize_compare.py \
		$(LATEST_RUN)/combined.json --out $(LATEST_RUN)

agent-check-regression:
	@$(ACT) && cd agent_hub_ci_bundle && $(PY) tests/agent_hub/check_regression.py \
		$(LATEST_RUN)/signature_Aurora.json --baseline $(BASELINE) --fail-on-violation

agent-slack-notify:
	@$(ACT) && cd agent_hub_ci_bundle && $(PY) alerts/slack_notify.py \
		$(LATEST_RUN)/summary.json "Agent Hub Performance Report"

agent-dashboard-compare:
	@$(ACT) && cd agent_hub_ci_bundle && streamlit run web/dashboard/streamlit_compare.py --server.port 8503

# Convenience targets
agent-full-cycle: agent-bench-signatures agent-bench-compare agent-check-regression agent-slack-notify

# Debug helpers
agent-show-config:
	@echo "VENV: $(VENV)"
	@echo "LATEST_RUN: $(LATEST_RUN)"
	@echo "SIGNATURES: $(SIGNATURES)"
	@echo "STEPS: $(STEPS)"
