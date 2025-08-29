# 🔄 Configuration Migration Guide

## 개요
EchoJudgmentSystem v10.5에서 모든 설정 파일이 통합되었습니다.

## 변경사항

### 이전 (분산된 설정)
```python
# 이전 방식 - 여러 파일에서 설정 로드
import yaml

with open('config/llm_config.yaml') as f:
    llm_config = yaml.safe_load(f)

with open('echo_engine/llm_free/judge_config.yaml') as f:
    judge_config = yaml.safe_load(f)

# 설정 사용
judge_mode = llm_config['judge_mode']
confidence = llm_config['confidence_threshold']
```

### 이후 (통합 설정)
```python
# 새로운 방식 - 통합 설정 로더 사용
from config.config_loader import get_config, get_config_loader

# 간단한 설정 조회
judge_mode = get_config('judgment.mode')
confidence = get_config('judgment.confidence_threshold')

# 복잡한 설정 조회
loader = get_config_loader()
signature_config = loader.get_signature_config('Echo-Aurora')
fist_config = loader.get_fist_category_config('decision')
```

## 마이그레이션 체크리스트

### 1. Import 문 업데이트
- [ ] `config/llm_config.yaml` 직접 로드하는 코드 제거
- [ ] `echo_engine/llm_free/judge_config.yaml` 직접 로드하는 코드 제거
- [ ] `from config.config_loader import get_config` 추가

### 2. 설정 키 경로 업데이트
| 이전 | 이후 |
|------|------|
| `llm_config['judge_mode']` | `get_config('judgment.mode')` |
| `llm_config['confidence_threshold']` | `get_config('judgment.confidence_threshold')` |
| `llm_config['claude_settings']['model']` | `get_config('claude.model')` |
| `judge_config['judgment_settings']['reasoning_depth']` | `get_config('llm_free.defaults.reasoning_depth')` |

### 3. 환경별 설정 활용
```python
# 환경별 설정 로드
loader = get_config_loader()
config = loader.load_config('production')  # 또는 'development', 'testing'

# 환경 정보 확인
env_info = loader.get_environment_info()
```

### 4. 동적 설정 변경
```python
# 런타임에 설정 변경
loader = get_config_loader()
loader.set('judgment.mode', 'hybrid')
loader.set('fist_templates.enabled', True)
```

## 주요 변경점

### 설정 구조 변화
- **judgment**: 판단 시스템 통합 설정
- **signatures**: 시그니처 시스템 설정  
- **claude**: Claude API 설정
- **llm_free**: LLM-Free 시스템 설정
- **fist_templates**: FIST 템플릿 시스템 설정
- **meta_cognition**: 메타인지 반성 루프 설정

### 새로운 기능
- 환경별 설정 오버라이드 (`environments` 섹션)
- 환경 변수 기반 설정 (`ECHO_*` 환경 변수)
- 설정 검증 및 validation
- 실시간 설정 재로드
- 설정 내보내기/가져오기

## 호환성 보장

기존 코드가 즉시 중단되지 않도록 다음과 같은 방법을 권장합니다:

1. **점진적 마이그레이션**: 모듈별로 하나씩 새로운 설정 시스템으로 전환
2. **폴백 지원**: 기존 설정 파일이 존재하는 경우 임시로 로드
3. **로깅**: 마이그레이션 진행 상황 추적

## 문제 해결

### 설정을 찾을 수 없는 경우
```python
# 안전한 설정 조회 (기본값 포함)
mode = get_config('judgment.mode', 'llm_free')  # 기본값: 'llm_free'
```

### 환경별 설정 문제
```python
# 현재 환경 확인
loader = get_config_loader()
print(f"현재 환경: {loader.environment}")

# 환경 강제 변경
loader.load_config('development')
```

### 검증 오류
```python
# 설정 검증 결과 확인
loader = get_config_loader()
if loader.validation_result:
    if not loader.validation_result.is_valid:
        print("설정 오류:", loader.validation_result.errors)
```
