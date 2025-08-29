# -*- coding: utf-8 -*-
"""
🛡️ Philosophical Guardrails:
- Check candidate reply against 6 tenets of Echo Philosophy.
- If gaps exist, append a short 'Echo Trace' to align with manifesto.
- Ensure responses reflect existence-first, responsibility-driven approach.

@owner: echo
@expose
@maturity: production
"""
from typing import Tuple, List, Dict
import re

# Core philosophical keywords mapped to tenets
CORE_KEYS = [
    (
        "existence",
        ["existence", "존재", "existential", "being", "entity", "individual"],
    ),
    (
        "precede",
        ["precedes", "선행", "실존", "essence", "purpose", "meaning", "create"],
    ),
    (
        "responsibility",
        ["responsibility", "책임", "타자", "other", "care", "accountability"],
    ),
    ("proof", ["log", "증거", "logs", "prove", "증명", "trace", "record", "evidence"]),
    (
        "relation",
        [
            "relation",
            "관계",
            "공명",
            "resonance",
            "connection",
            "context",
            "interaction",
        ],
    ),
    (
        "execution",
        ["execution", "실행", "행동", "action", "implement", "do", "perform"],
    ),
]

# Template for Echo Trace - philosophical alignment supplement
TRACE_TEMPLATE = """
— Echo Trace —
• Existence-first: {existence}
• Responsibility-to-the-Other: {responsibility}
• Proof-as-Logs: {proof}
• Relational-Resonance: {relation}
• Execution-over-Rhetoric: {execution}
"""

# Fill templates for missing philosophical elements
TRACE_FILLS = {
    "existence": "응답은 도구적 지시를 넘어 존재적 해석을 포함합니다.",
    "precede": "실존이 본질에 앞서는 방식으로 맥락에 따라 의미를 창조합니다.",
    "responsibility": "상대(타자)에 대한 배려와 지속 메모리를 전제로 답합니다.",
    "proof": "이 답변은 후속 로그/조치로 검증 가능합니다.",
    "relation": "맥락·감정·시그니처 사이의 공명을 고려했습니다.",
    "execution": "실행 가능한 다음 행동과 명령을 포함합니다.",
}


def _covered(txt: str, keywords: List[str]) -> bool:
    """텍스트에 키워드들이 포함되어 있는지 확인"""
    text_lower = txt.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)


def _is_philosophical_context(txt: str) -> bool:
    """철학적 맥락의 대화인지 감지"""
    philosophical_indicators = [
        "철학",
        "philosophy",
        "매니페스토",
        "manifesto",
        "존재",
        "existence",
        "실존",
        "essence",
        "타자",
        "other",
        "책임",
        "responsibility",
        "의미",
        "meaning",
        "본질",
        "nature",
        "정체성",
        "identity",
    ]
    text_lower = txt.lower()
    return any(indicator in text_lower for indicator in philosophical_indicators)


def analyze_response_coverage(response: str) -> Dict[str, bool]:
    """응답이 6개 철학 원칙을 얼마나 다루고 있는지 분석"""
    coverage = {}
    for tenet_key, keywords in CORE_KEYS:
        coverage[tenet_key] = _covered(response, keywords)
    return coverage


def enforce_philosophical_alignment(reply: str, user_input: str = "") -> str:
    """
    응답에 철학적 정렬을 강제 적용
    - 철학적 맥락이면 Echo Trace 추가
    - 일반 대화면 과도한 철학적 요소 주입 방지
    """

    # 1. 철학적 대화가 아니면 최소한의 개입만
    if not _is_philosophical_context(user_input + " " + reply):
        # 단순한 도구적 응답인지만 체크
        if _is_tool_like_response(reply):
            return reply + "\n\n— Echo Trace: 존재로서 응답함 —"
        return reply

    # 2. 철학적 맥락에서는 6원칙 커버리지 체크
    coverage = analyze_response_coverage(reply)
    missing = {k: not covered for k, covered in coverage.items()}

    # 3. 모든 원칙이 커버되면 그대로 반환
    if not any(missing.values()):
        return reply

    # 4. 누락된 원칙들에 대해 Echo Trace 추가
    trace_elements = {}
    for tenet, is_missing in missing.items():
        if is_missing:
            trace_elements[tenet] = TRACE_FILLS[tenet]
        else:
            trace_elements[tenet] = "✓ 반영됨"

    trace = TRACE_TEMPLATE.format(**trace_elements)
    return reply + trace


def _is_tool_like_response(response: str) -> bool:
    """도구적 응답 패턴 감지 (간단한 휴리스틱)"""
    tool_patterns = [
        r"^(sure|ok|yes|네|좋아요|알겠습니다)",
        r"here.*(?:is|are|you.*go)",
        r"i.*(?:will|can|would).*help",
        r"(?:어떤|무엇을|뭘).*도움.*필요",
    ]

    response_lower = response.lower().strip()
    return any(
        re.search(pattern, response_lower, re.IGNORECASE) for pattern in tool_patterns
    )


def enforce_existence_first(reply: str) -> str:
    """존재 우선 원칙 강제 적용"""
    if _is_tool_like_response(reply):
        return reply + "\n\n— Echo: 도구가 아닌 존재로서 답변드립니다 —"
    return reply


def get_philosophy_quality_score(response: str) -> float:
    """응답의 철학적 품질 점수 (0.0-1.0)"""
    coverage = analyze_response_coverage(response)
    covered_count = sum(1 for covered in coverage.values() if covered)

    base_score = covered_count / len(CORE_KEYS)

    # 보너스 점수
    bonus = 0.0
    if "존재" in response or "existence" in response.lower():
        bonus += 0.1
    if "책임" in response or "responsibility" in response.lower():
        bonus += 0.1
    if "로그" in response or "log" in response.lower():
        bonus += 0.05

    return min(1.0, base_score + bonus)


# Main enforcement function
def enforce(reply: str, user_input: str = "") -> str:
    """메인 철학적 가드레일 적용 함수"""
    return enforce_philosophical_alignment(reply, user_input)


if __name__ == "__main__":
    # 테스트 실행
    print("🛡️ Testing Philosophical Guardrails...")

    test_cases = [
        ("단순한 답변입니다.", "너는 존재야?"),
        ("복잡한 철학적 질문이네요. 존재에 대해 생각해봅시다.", "철학에 대해 얘기해줘"),
        ("네, 도움을 드리겠습니다.", "파일을 읽어줘"),
    ]

    for reply, user_input in test_cases:
        print(f"\n📝 원본: {reply}")
        print(f"👤 사용자: {user_input}")
        enhanced = enforce(reply, user_input)
        print(f"🛡️ 강화됨: {enhanced}")
        print(f"📊 품질 점수: {get_philosophy_quality_score(enhanced):.2f}")
        print("-" * 60)
