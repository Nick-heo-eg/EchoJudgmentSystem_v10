# 4블록 지시문 템플릿 (Claude Code 패리티)

## 사용법
이 템플릿을 Claude에게 복붙해서 작업 요청 시 사용하세요.

---

## PLAN
- 목적: [한 줄 목표를 여기에 작성]
- 제약: apply_patch만 사용(직접 쓰기 금지), 테스트 선행, 실패 시 RESULT에 recovery_plan 필수
- 단계: Spec 작성 → Test 생성 → 최소 구현 → 실행/검증 → 결과 요약

## PATCH (unified diff only)
```diff
# 여기에 변경사항을 모두 diff로 제시
# 예시:
--- a/src/example.py
+++ b/src/example.py
@@ -1,3 +1,5 @@
 def hello():
+    # Added comment
     print("Hello")
+    return True
```

## RUN
- 테스트: `pytest -q`
- 벤치: `pytest -q --benchmark-only || python scripts/bench.py`
- 린트: `ruff check .`
- 타입: `mypy .`
- 시크릿: `./gitleaks detect --no-banner --log-opts="--all" -v`
- 라이선스: `pip-licenses --format=json > licenses.json`

## RESULT
- 테스트: [통과/실패, 실패 목록]
- 벤치: [p95 전후 비교표, 목표 달성 여부]
- 린트/타입/시크릿/라이선스: [표 요약]
- 영향 범위: [변경된 파일들과 의존성]
- 롤백 포인트: [복구 방법]
- 재시도 계획 (recovery_plan): [실패 시 대응 방안]

---

## 예시 사용

**요청**: "user_auth 모듈에 패스워드 검증 기능 추가"

### PLAN
- 목적: 패스워드 강도 검증 기능 추가 (최소 8자, 대소문자+숫자 포함)
- 제약: apply_patch만 사용, 테스트 선행, recovery_plan 필수
- 단계: 테스트 작성 → 최소 구현 → 검증 → 결과

### PATCH
```diff
--- /dev/null
+++ b/tests/test_password_validator.py
@@ -0,0 +1,20 @@
+import pytest
+from src.auth.password_validator import validate_password
+
+def test_valid_password():
+    assert validate_password("Abc123456") == True
+
+def test_too_short():
+    assert validate_password("Abc1") == False
...
```

### RUN
- 테스트: `pytest tests/test_password_validator.py -v`
- 린트: `ruff check src/auth/password_validator.py`

### RESULT  
- 테스트: ✅ 5/5 통과
- 린트: ✅ 0 issues
- 영향 범위: src/auth/, tests/
- 롤백 포인트: `git reset HEAD~1`
- recovery_plan: 실패 시 pytest 출력 확인 → 구현 수정 → 재실행