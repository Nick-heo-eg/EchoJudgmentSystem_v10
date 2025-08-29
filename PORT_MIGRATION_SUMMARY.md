# 🌐 Port Migration Summary - Windows Conflict 방지

## 📋 변경된 포트 할당

**기존 → 신규 (Windows C 드라이브 충돌 방지)**

| 서비스 | 기존 포트 | 신규 포트 | 설명 |
|--------|-----------|-----------|------|
| **🔧 Main Echo API** | `8000` | `9000` | 메인 Echo 판단 엔진 API |
| **🤖 EchoGPT API** | `8001` | `9001` | Teacher-Student 증류 시스템 |
| **🎨 IDE Bridge** | `8009` | `9009` | CLI↔IDE 브릿지 서버 (Test Focus) |
| **📊 Streamlit Dashboard** | `8501` | `9501` | 실시간 모니터링 대시보드 |
| **🌐 Web Dashboard** | `8080` | `9080` | 기타 웹 인터페이스 |

## 🔧 수정된 파일 목록

### 핵심 설정 파일
- `config/echo_system_config.yaml` - 메인 API 포트 (8000 → 9000)
- `config/system.yaml` - API 및 대시보드 포트
- `Makefile` - 모든 헬스체크 및 스모크테스트 URL

### API 서버 파일들
- `echo_engine/echo_agent_api.py` - 메인 API 서버 (8000 → 9000)
- `echo_engine/echo_agent_api_slim.py` - Slim API 서버 환경변수 기본값
- `echogpt/server.py` - EchoGPT API 서버 (8001 → 9001)
- `echogpt/test_client.py` - EchoGPT 테스트 클라이언트

### 대시보드 및 UI
- `streamlit_ui/comprehensive_dashboard.py` - API 연결 URL 업데이트
- `echo_ide_bridge.py` - IDE 브릿지 포트 (8009 → 9009)
- `cosmos_auto_init.py` - Cosmos 자동 초기화 시스템

### 문서 파일들
- `CLAUDE.md` - Claude 전용 가이드 모든 포트 참조
- `ANCHOR.md` - 공통 포트 표 및 예제 URL
- `README_Amoeba.md` - Amoeba 시스템 포트 참조

## 🚀 새로운 접속 URL

```bash
# 🔧 메인 Echo API 서버
python echo_engine/echo_agent_api.py
# → http://localhost:9000
# → http://localhost:9000/docs (API 문서)

# 🤖 EchoGPT 서버  
cd echogpt && python server.py
# → http://localhost:9001

# 🎨 IDE 브릿지 서버
python echo_ide_bridge.py
# → http://localhost:9009

# 📊 Streamlit 대시보드
streamlit run streamlit_ui/comprehensive_dashboard.py
# → http://localhost:9501 (Streamlit 기본 설정에 따라)
```

## 🏥 헬스체크 명령어

```bash
# 환경변수로 포트 커스터마이징
export ECHO_API_PORT=9000
export ECHOGPT_PORT=9001  
export DASHBOARD_PORT=9501

# Makefile 헬스체크
make health     # 새로운 포트로 자동 체크
make smoke      # 새로운 포트로 스모크테스트

# 개별 서비스 체크
curl http://localhost:9000/health    # Echo API
curl http://localhost:9001/          # EchoGPT  
curl http://localhost:9501/          # Dashboard (브라우저 필요)
```

## ✅ 검증 완료 사항

- [x] 모든 Python 파일의 포트 참조 업데이트
- [x] 모든 Markdown 문서의 포트 참조 업데이트  
- [x] Makefile 헬스체크 및 스모크테스트 URL 수정
- [x] 설정 파일 (YAML) 포트 변경
- [x] 환경변수 기본값 변경
- [x] 테스트 클라이언트 URL 업데이트

## 🚨 주의사항

1. **기존 북마크 업데이트 필요**: 브라우저 북마크를 새 포트로 변경
2. **외부 연동 시스템 확인**: API를 호출하는 외부 시스템이 있다면 새 포트로 업데이트
3. **환경변수 우선**: 환경변수 `ECHO_API_PORT` 등으로 포트를 오버라이드 가능
4. **Docker 환경**: Docker 설정이 있다면 별도 확인 필요

## 🎯 마이그레이션 성공 확인

```bash
# 전체 시스템 헬스체크
make health

# 개별 서비스 확인  
curl -f http://localhost:9000/health && echo "✅ Echo API OK"
curl -f http://localhost:9001/v1/system/status && echo "✅ EchoGPT OK"

# 포트 사용 확인
netstat -tulpn | grep :90
```

---
**변경 완료일**: 2025-08-28  
**변경 사유**: WSL과 Windows C 드라이브 포트 충돌 방지  
**마이그레이션 범위**: 전체 시스템 (9000번대 포트로 통일)