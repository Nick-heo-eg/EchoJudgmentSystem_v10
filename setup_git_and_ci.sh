#!/bin/bash
# save as: setup_git_and_ci.sh
# usage: bash setup_git_and_ci.sh "<YOUR_GH_REPO_URL or leave empty>"

set -euo pipefail

ROOT="${ROOT:-$HOME/EchoJudgmentSystem_v10}"
cd "$ROOT"

echo ">> Working dir: $(pwd)"

# 0) git init (idempotent)
if [ ! -d .git ]; then
  echo ">> git init"
  git init
else
  echo ">> git repo already initialized"
fi

# 1) .gitignore 생성/보강
cat > .gitignore <<'EOF'
# venv & python
venv*/
**/__pycache__/
*.pyc
*.pyo
*.pyd

# IDE
.idea/
.vscode/
.DS_Store

# logs & temps
*.log
*.tmp

# agent hub artifacts & streamlit
agent_hub_ci_bundle/artifacts/
.streamlit/
EOF
echo ">> .gitignore written"

# 2) Makefile 셸 고정 (source not found 방지)
MAKES=(Makefile Makefile.agent_hub.mk agent_hub_ci_bundle/Makefile.agent_hub.mk)
for mf in "${MAKES[@]}"; do
  if [ -f "$mf" ]; then
    if ! grep -q '^SHELL *:=' "$mf"; then
      sed -i '1i SHELL := /usr/bin/bash' "$mf"
      echo ">> SHELL pinned in $mf"
    else
      echo ">> SHELL already pinned in $mf"
    fi
  fi
done

# 3) CI requirements (옵션 파일)
mkdir -p agent_hub_ci_bundle
cat > agent_hub_ci_bundle/requirements_ci.txt <<'EOF'
aiohttp
matplotlib
orjson
PyYAML
streamlit
EOF
echo ">> requirements_ci.txt written"

# 4) GitHub Actions 워크플로 추가
mkdir -p .github/workflows
cat > .github/workflows/agent-bench.yml <<'YAML'
name: Agent Bench Full Cycle

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  bench:
    runs-on: ubuntu-latest
    defaults:
      run:
        shell: bash
    env:
      PYTHON_VERSION: "3.12"
      SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: "pip"

      - name: Create venv & install deps
        run: |
          python -m venv agent_hub_ci_bundle/venv_extensions
          source agent_hub_ci_bundle/venv_extensions/bin/activate
          python -V
          pip install -U pip wheel
          if [ -f agent_hub_ci_bundle/requirements_ci.txt ]; then
            pip install -r agent_hub_ci_bundle/requirements_ci.txt
          else
            pip install aiohttp matplotlib orjson PyYAML streamlit
          fi

      - name: Run signature benchmarks (with warmup)
        run: |
          source agent_hub_ci_bundle/venv_extensions/bin/activate
          make -f agent_hub_ci_bundle/Makefile.agent_hub.mk agent-bench-signatures SIGNATURES="Aurora,Selene,Heo" WARMUP=1

      - name: Compare & generate plots
        run: |
          source agent_hub_ci_bundle/venv_extensions/bin/activate
          make -f agent_hub_ci_bundle/Makefile.agent_hub.mk agent-bench-compare

      - name: Regression check
        run: |
          source agent_hub_ci_bundle/venv_extensions/bin/activate
          make -f agent_hub_ci_bundle/Makefile.agent_hub.mk agent-check-regression

      - name: Slack notify (optional)
        if: env.SLACK_WEBHOOK_URL != ''
        run: |
          source agent_hub_ci_bundle/venv_extensions/bin/activate
          make -f agent_hub_ci_bundle/Makefile.agent_hub.mk agent-slack-notify

      - name: Capture latest run path
        id: latest
        run: |
          LATEST_RUN=$(ls -1dt agent_hub_ci_bundle/artifacts/bench/* | head -n 1 || true)
          echo "latest_run=${LATEST_RUN}" >> $GITHUB_OUTPUT
          echo "LATEST_RUN=$LATEST_RUN"

      - name: Upload artifacts
        if: steps.latest.outputs.latest_run != ''
        uses: actions/upload-artifact@v4
        with:
          name: bench-artifacts
          path: ${{ steps.latest.outputs.latest_run }}
          if-no-files-found: warn
YAML
echo ">> workflow written"

# 5) 첫 커밋
git add -A
if git diff --cached --quiet; then
  echo ">> nothing to commit"
else
  git commit -m "ci(repo): init git, .gitignore, pin bash shell, add agent bench workflow"
  echo ">> initial commit created"
fi

# 6) 원격 연결 (인자에 URL 주면 자동 연결)
REMOTE_URL="${1:-}"
if [ -n "$REMOTE_URL" ]; then
  if git remote | grep -q '^origin'; then
    echo ">> origin already set"
  else
    git remote add origin "$REMOTE_URL"
    echo ">> origin set to $REMOTE_URL"
  fi
  git branch -M main
  git push -u origin main
  echo ">> pushed to origin main"
else
  echo ">> Skipped remote push (no URL given). To push:"
  echo "   git remote add origin https://github.com/<USER>/<REPO>.git"
  echo "   git branch -M main && git push -u origin main"
fi

echo ">> DONE."