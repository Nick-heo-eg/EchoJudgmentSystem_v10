
# Agent Hub — CI, Bench Curve, Visualization

## Quick Start (local)
```bash
# 1) Smoke
bash tests/agent_hub/smoke_tests.sh

# 2) Bench curve
python tests/agent_hub/bench_curve.py --steps 20x200,50x1000 --tag local

# 3) Visualize latest
make -f Makefile.agent_hub.mk agent-bench-visualize
```

## Streamlit Dashboard
```bash
# from repo root
streamlit run web/dashboard/streamlit_app.py
```
Then open the shown URL; select the latest run under `artifacts/bench/*/results.json`.

## GitHub Actions
Workflow file: `.github/workflows/agent_hub_ci.yml`

- **PRs**: smoke + light bench (20x200), uploads artifacts
- **Nightly**: heavy curve (20x200,50x1000,100x2000) + plots + artifacts

> Adjust `env.SERVER_CMD` to match how you launch Agent Hub (e.g., `uvicorn agent_hub.app:app`).

## Result Schema
`tests/agent_hub/schemas/bench_results.schema.json`
