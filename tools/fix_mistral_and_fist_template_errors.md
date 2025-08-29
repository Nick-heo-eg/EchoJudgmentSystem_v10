# 🔧 EchoJudgmentSystem 오류 패치 작업지시서

## 🎯 목적
다음 두 가지 주요 오류를 해결하고 시스템의 안정성과 내결함성(fault-tolerance)을 향상시킨다.

---

### ✅ [Task 1] MistralAdapter 로딩 오류 방지

#### 오류 내용
- `'NoneType' object has no attribute 'endswith'`
- 원인: `model_path` 또는 `tokenizer`가 None일 경우, 모델 로딩 실패

#### 조치사항
- `mistral_adapter.py` 내 모델 초기화 구문에 방어 로직 삽입
- 다음 항목이 None 또는 문자열 아님을 확인하고 예외처리 및 로깅:
  - `model_path`
  - `tokenizer`
- 예시 코드:

```python
if model_path is None or not isinstance(model_path, str) or not model_path.endswith(".bin"):
    raise ValueError(f"❌ 모델 경로 오류: model_path={model_path}")
```

- 로딩 전에 debug 로그 추가:

```python
print(f"[DEBUG] 모델 로딩 시도: model_path={model_path}, tokenizer={tokenizer}")
```

---

### ✅ [Task 2] FIST 템플릿 변수 누락 처리

#### 오류 내용
- `템플릿 변수 누락: 'key_people'`
- 원인: 템플릿 렌더링 시 필수 context 변수가 제공되지 않음

#### 조치사항
- `fist_template_engine.py` 또는 `resonance_synthesizer.py`에 다음 추가:

```python
required_vars = ["key_people"]
for var in required_vars:
    if var not in template_context:
        template_context[var] = "미지정 대상"
```

- 또는 validator 유틸 함수 생성:

```python
def ensure_template_keys(context: dict, required: list[str]):
    for key in required:
        if key not in context:
            context[key] = "미지정"
```

- 템플릿 렌더링 전에 실행:

```python
ensure_template_keys(template_context, ["key_people"])
```

---

## 🧠 추가 권장사항

- 템플릿 변수 스키마를 `.fist.json` 형태로 정의하고, 사전 검증기로 통합
- FIST fallback이 실패할 경우 Claude 판단으로 자동 리라우팅될 수 있도록 구조 설정 확인

---

## 🧾 변경 대상 파일

- `echo_engine/mistral_adapter.py`
- `echo_engine/fist_templates/template_engine.py` 
- `echo_engine/resonance_synthesizer.py`

---

## ✅ 기대 효과

- 시스템 로딩 실패 방지
- 템플릿 렌더링 실패 방지
- 판단 루프의 회복탄력성 확보

---

## 🚀 자동 패치 실행 순서

1. **Mistral Adapter 오류 처리 강화**
   - 모델 경로 검증 로직 추가
   - None 값 체크 및 안전 예외 처리
   - 디버그 로깅 추가

2. **FIST 템플릿 변수 누락 방지**
   - 템플릿 컨텍스트 검증기 구현
   - 기본값 삽입 메커니즘 추가
   - graceful fallback 처리

3. **통합 테스트 실행**
   - 패치 적용 후 시스템 안정성 검증
   - 오류 발생 시나리오 재현 테스트
   - 회복탄력성 확인