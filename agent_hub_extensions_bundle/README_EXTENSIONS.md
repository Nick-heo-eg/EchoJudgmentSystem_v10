# Agent Hub — Extensions (Alerts, Regression Guard, Signature Compare)

## 1) 회귀 가드
```bash
python tests/agent_hub/check_regression.py artifacts/bench/<run>/results.json   --baseline tests/agent_hub/bench_baseline.yaml   --fail-on-violation
```

## 2) Slack 알림
GitHub Secrets에 `SLACK_WEBHOOK_URL` 추가 후, CI가 자동으로 통지합니다.
로컬 테스트:
```bash
python alerts/slack_notify.py artifacts/bench/<run>/summary.json "Agent Hub Bench Guard"
# 환경변수 SLACK_WEBHOOK_URL 없으면 콘솔 출력으로 대체
```

## 3) 시그니처 비교 벤치
```bash
python tests/agent_hub/bench_signatures.py --signatures Aurora,Selene,Heo   --steps 20x200,50x1000,100x2000 --tag sigbench
python tests/agent_hub/visualize_compare.py artifacts/bench/<run>/combined.json
```

## 4) 대시보드 (시그니처 비교)
```bash
streamlit run web/dashboard/streamlit_compare.py --server.port 8503
```

## 5) S3 업로드(선택)
```bash
bash scripts/upload_artifacts_s3.sh artifacts/bench/<run> s3://your-bucket/agent-hub/bench/<run>/
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION 필요
```

## 6) CI 추가 워크플로
`.github/workflows/agent_hub_alerts.yml` — 야간 벤치 + 회귀 가드 + Slack 알림
