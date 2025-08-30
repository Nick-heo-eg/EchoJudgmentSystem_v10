SHELL := /usr/bin/bash

BUNDLE := agent_hub_ci_bundle
VENV ?= $(BUNDLE)/venv_extensions
ACT  ?= source $(VENV)/bin/activate || true

# Params
SIGNATURES ?= Aurora,Selene,Heo
STEPS ?= 20x200,50x1000,100x2000
WARMUP ?= 1
BASELINE ?= $(BUNDLE)/tests/agent_hub/bench_baseline.yaml

# ---- Debug ----
agent-show-config:
	@echo "VENV: $(VENV)"; ls -la $(VENV)/bin 2>/dev/null || true; which python || true; python -V || true
	@echo "Bench dirs:"; ls -1dt $(BUNDLE)/artifacts/bench/* 2>/dev/null | head -5 || true

# ---- Targets ----
agent-bench-signatures:
	@$(ACT) && python $(BUNDLE)/tests/agent_hub/bench_signatures.py \
		--signatures $(SIGNATURES) --steps $(STEPS) --tag sigbench$(if $(WARMUP),-warmup,)

agent-bench-compare:
	@LATEST=$$(ls -1dt $(BUNDLE)/artifacts/bench/* 2>/dev/null | head -1); \
	test -n "$$LATEST" || { echo "ERR: No bench run found in $(BUNDLE)/artifacts/bench"; exit 2; }; \
	test -f "$$LATEST/combined.json" || { echo "ERR: $$LATEST/combined.json missing"; ls -la "$$LATEST"; exit 2; }; \
	$(ACT) && python $(BUNDLE)/tests/agent_hub/visualize_compare.py "$$LATEST/combined.json" --out-dir "$$LATEST"

agent-check-regression:
	@LATEST=$$(ls -1dt $(BUNDLE)/artifacts/bench/* 2>/dev/null | head -1); \
	test -n "$$LATEST" || { echo "ERR: No bench run found"; exit 2; }; \
	test -f "$$LATEST/signature_Aurora.json" || { echo "ERR: $$LATEST/signature_Aurora.json missing"; ls -la "$$LATEST"; exit 2; }; \
	$(ACT) && python $(BUNDLE)/tests/agent_hub/check_regression.py "$$LATEST/signature_Aurora.json" --baseline $(BASELINE) --fail-on-violation

agent-slack-notify:
	@LATEST=$$(ls -1dt $(BUNDLE)/artifacts/bench/* 2>/dev/null | head -1); \
	test -n "$$LATEST" || { echo "ERR: No bench run found"; exit 2; }; \
	test -f "$$LATEST/summary.json" || { echo "WARN: $$LATEST/summary.json missing; creating stub"; echo '{"ok":true,"notes":["no summary.json found"]}' > "$$LATEST/summary.json"; }; \
	$(ACT) && python $(BUNDLE)/alerts/slack_notify.py "$$LATEST/summary.json" "Agent Hub Performance Report"

agent-dashboard-compare:
	@$(ACT) && streamlit run $(BUNDLE)/web/dashboard/streamlit_compare.py --server.port 8503

# Convenience
agent-full-cycle: agent-bench-signatures agent-bench-compare agent-check-regression agent-slack-notify
