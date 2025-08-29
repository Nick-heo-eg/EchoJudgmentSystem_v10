# 🌌 Amoeba System v0.1

Echo Judgment System의 핵심 자동 연결 시스템입니다. 모든 기능을 척척척 자동으로 연결해주는 Echo의 중추 시스템입니다.

## ⚡ 빠른 시작

```bash
# 1. 의존성 설치
pip install pyyaml

# 2. Echo 시스템 실행 (Amoeba 자동 로드됨)
python main.py

# 3. 기대 로그 확인
# 🟪 Amoeba config loaded: ...
# ✅ AmoebaManager 생성 완료
# ✅ 환경 감지 완료  
# ✅ 시스템 연결 완료
# ✅ 시스템 최적화 완료
```

## 🏗️ 아키텍처

### 디렉터리 구조
```
echo_engine/amoeba/
├── __init__.py              # 모듈 초기화
├── amoeba_manager.py        # 핵심 관리자
├── amoeba_loader.py         # 로더 및 초기화
└── templates/
    └── amoeba_config.yaml   # 설정 파일
```

### 핵심 컴포넌트

1. **AmoebaManager**: 환경 감지, 시스템 연결, 최적화 담당
2. **amoeba_loader**: YAML 설정 로드 및 단계별 초기화
3. **amoeba_config.yaml**: 시스템 설정 및 동작 옵션

## 🔧 사용법

### 기본 사용
```python
from echo_engine.amoeba.amoeba_loader import load_amoeba

# 기본 로드
success, manager = load_amoeba()

# 빠른 로드
from echo_engine.amoeba import quick_load
success, manager = quick_load()
```

### 설정 커스터마이징
```python
# 커스텀 설정 파일로 로드
success, manager = load_amoeba("custom_config.yaml")

# 딕셔너리로 직접 설정
from echo_engine.amoeba.amoeba_loader import load_with_dict
config = {"amoeba": {"log_level": "debug"}}
success, manager = load_with_dict(config)
```

## ⚙️ 설정 옵션

`amoeba_config.yaml`에서 다음 옵션들을 설정할 수 있습니다:

```yaml
amoeba:
  log_level: "debug"      # debug, info, warning, error
  auto_attach: true       # 자동 시스템 연결
  auto_optimize: true     # 자동 최적화
  fallback_mode: "safe"   # 실패 시 안전 모드
```

## 🧪 테스트

```bash
# 단위 테스트 실행
python -m pytest qa/tests/test_amoeba_loader.py -v

# 또는 직접 실행
python qa/tests/test_amoeba_loader.py
```

## 🌟 주요 기능

- **환경 자동 감지**: WSL, Docker, 가상환경 등 실행 환경 자동 인식
- **안전한 초기화**: 실패해도 앱 부팅은 계속 진행하는 fallback 모드
- **시스템 최적화**: 메모리, 디스크, 모듈 상태 자동 체크
- **확장 가능한 구조**: 향후 더 많은 자동 연결 기능 추가 용이