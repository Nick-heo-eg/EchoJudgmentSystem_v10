# -*- coding: utf-8 -*-
"""
Hybrid Intent Router
1) 하드 규칙: 명령/툴/코딩 키워드
2) 의미 규칙: 한국어 일반 요청 표현(계획 짜줘/정리해줘/검색해봐 등)
3) (선택) LLM 분류: 엔진/키가 있을 때만, 신뢰도 보강
"""
from __future__ import annotations
import os, re, json
from typing import Dict, Any

HARD_RULES = [
    (r"^/(help|quit|exit|profile|mode|diag)\b", {"route": "command"}),
    (r"^TOOL:", {"route": "tool_call"}),
]

TOOL_RULES = [
    (
        r"(self\s*질문|도구\s*목록|self\s*ask|기능\s*있는지\s*검색해봐)",
        {"route": "tool:self_ask"},
    ),
    (r"(파일|스크립트).*(만들어|생성|작성|저장)", {"route": "code"}),
    (r"(검색해봐|찾아봐)", {"route": "tool:workspace_search"}),
]

CODE_RULE = re.compile(
    r"(code|코드|program|프로그램|function|함수|class|클래스|patch|diff|python|javascript)",
    re.I,
)

CHAT_HINTS = re.compile(
    r"(계획|정리|요약|설명|추천|비교|장단점|아이디어|목록|스텝|단계|하루\s*계획|일정|메뉴)",
    re.I,
)


def _rule_match(text: str, rules):
    for pat, out in rules:
        if re.search(pat, text, re.I):
            return out
    return None


def route(user_input: str) -> Dict[str, Any]:
    t = user_input.strip()
    if not t:
        return {"route": "empty", "confidence": 1.0}
    # 1) 하드 규칙
    m = _rule_match(t, HARD_RULES)
    if m:
        return {"route": m["route"], "confidence": 1.0}
    # 2) 툴 규칙
    m = _rule_match(t, TOOL_RULES)
    if m:
        return {"route": m["route"], "confidence": 0.9}
    # 3) 코드 규칙
    if CODE_RULE.search(t):
        return {"route": "code", "confidence": 0.85}
    # 4) 일반 대화 힌트
    if CHAT_HINTS.search(t) or t.endswith(("해줘", "주세요", "알려줘", "정리해줘")):
        return {"route": "chat", "confidence": 0.7}
    # 5) (선택) LLM 분류 시도
    if os.getenv("OPENAI_API_KEY"):
        try:
            # 간단 프롬프트 분류 (엔진 코드가 별도라면 registry 쪽에서 호출)
            # 여기선 신뢰도 보강만 가정하고, 실패해도 조용히 무시
            pass
        except Exception:
            pass
    # 6) 기본은 chat로 (폴백 시에도 템플릿이 아닌 'LLM chat'로)
    return {"route": "chat", "confidence": 0.5}
