# Agent Hub Test Pack

## 구조
- `agent_hub_quicktests.http` — VS Code REST Client 수동 테스트
- `smoke_tests.sh` — cURL 스모크
- `bench_async.py` — aiohttp 기반 경량 벤치
- `regression.yaml` — 회귀 시나리오 정의
- `run_regression.py` — 회귀 러너(requests+PyYAML)
- Postman 컬렉션 — `Echo_Agent_Hub.postman_collection.json`

## 빠른 실행
```bash
make agent-smoke
make agent-bench
make agent-regress
```

## 의존성

* 스모크: curl, (선택) jq
* 벤치: `pip install aiohttp`
* 회귀: `pip install requests pyyaml`

## 사용법

### 1. Agent Hub 서버 시작
```bash
cd agent_hub
source venv/bin/activate
PYTHONPATH=/home/nick-heo123/EchoJudgmentSystem_v10:$PYTHONPATH uvicorn app.main:app --port 8014 --host 0.0.0.0 --reload
```

### 2. 테스트 실행
```bash
# 스모크 테스트 (기본 기능 확인)
make agent-smoke

# 벤치마크 (성능 측정)
make agent-bench

# 중부하 벤치마크
make agent-bench-heavy

# 회귀 테스트 (기능 검증)
make agent-regress
```

### 3. 수동 테스트
- VS Code에서 `agent_hub_quicktests.http` 파일을 열어서 REST Client로 수동 테스트
- Postman에서 `Echo_Agent_Hub.postman_collection.json` 임포트하여 테스트

## 엔드포인트 목록

### 기본
- `GET /` - 서비스 정보
- `GET /health` - 헬스체크
- `GET /agents` - 사용 가능한 AI 에이전트
- `GET /tools` - 사용 가능한 도구

### Echo 엔진
- `POST /echo` - 직접 텍스트 처리 (0.1ms 초고속)
- `POST /echo/file` - 파일 청크 처리 및 분석
- `GET /echo/stats` - Echo 엔진 성능 통계

### AI 에이전트 + Echo 통합
- `POST /invoke` - 기본 AI 에이전트 호출
- `POST /invoke/echo` - AI 에이전트 + Echo 엔진 결합 처리

## 성능 지표

- **Echo 직접 처리**: 0.05-0.1ms
- **파일 처리**: 0.1-0.5ms (청크 수에 따라)
- **AI + Echo 결합**: 약간 더 긴 시간 (AI 응답 + Echo 분석)
- **전체 성능**: 734K+ ops/sec (최적화 모드)