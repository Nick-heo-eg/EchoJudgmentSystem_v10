# -*- coding: utf-8 -*-
"""
Echo Engine Configuration
전역 설정과 템플릿 정책 정의
"""

# 코드 생성 기본 토큰
DEFAULT_CODEGEN_MAX_TOKENS = 2400

# 일반 대화 설정
#  - 키/엔진 없을 때 '존재 템플릿'으로 폴백 금지(명시 에러)
HARD_FAIL_CHAT_WHEN_ENGINE_MISSING = True
#  - 일반 대화도 토큰 상향(짧은 답변 방지)
DEFAULT_CHAT_MAX_TOKENS = 800
