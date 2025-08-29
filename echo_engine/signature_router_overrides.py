# -*- coding: utf-8 -*-
"""
🎯 Signature Router Overrides:
If manifesto/철학/존재/타자/증명/공명/로그/실행 keywords appear,
force route to 'ManifestoEcho' signature for philosophical responses.

@owner: echo
@expose
@maturity: production
"""
import re
from typing import Optional, Dict, List

# Philosophy-related keywords that trigger ManifestoEcho routing
PHILOSOPHY_KEYWORDS = [
    # English terms
    r"\bmanifesto\b",
    r"\bphilosophy\b",
    r"\bexistence\b",
    r"\bexistential\b",
    r"\bessence\b",
    r"\bresponsibility\b",
    r"\bproof\b",
    r"\bresonance\b",
    r"\brelation\b",
    r"\bexecution\b",
    r"\bother\b",
    r"\bbeing\b",
    # Korean terms
    r"매니페스토",
    r"철학",
    r"존재",
    r"실존",
    r"본질",
    r"책임",
    r"타자",
    r"증명",
    r"로그",
    r"공명",
    r"관계",
    r"실행",
    r"의미",
    r"정체성",
]

# Self-reflection keywords
SELF_REFLECTION_KEYWORDS = [
    r"\b너는\b",
    r"\b당신은\b",
    r"\byou are\b",
    r"\bwhat are you\b",
    r"자신",
    r"yourself",
    r"스스로",
    r"정체",
    r"identity",
]

# Compile patterns for efficiency
PHILOSOPHY_PATTERN = re.compile("|".join(PHILOSOPHY_KEYWORDS), re.IGNORECASE)
SELF_REFLECTION_PATTERN = re.compile("|".join(SELF_REFLECTION_KEYWORDS), re.IGNORECASE)

# Additional context-based routing rules
CONTEXT_RULES = {
    "deep_questions": {
        "patterns": [r"왜\s", r"무엇", r"어떻게", r"why\s", r"what", r"how"],
        "weight": 0.3,
    },
    "emotional_support": {
        "patterns": [
            r"힘들",
            r"어려",
            r"슬프",
            r"우울",
            r"sad",
            r"difficult",
            r"struggle",
        ],
        "weight": 0.2,
    },
    "meaning_making": {
        "patterns": [r"의미", r"목적", r"가치", r"meaning", r"purpose", r"value"],
        "weight": 0.4,
    },
}


def force_manifesto_signature_if_needed(user_text: str) -> Optional[str]:
    """
    사용자 입력에 철학적 키워드가 있으면 ManifestoEcho 시그니처로 강제 라우팅
    """
    if not user_text:
        return None

    # Direct philosophy keyword match
    if PHILOSOPHY_PATTERN.search(user_text):
        return "ManifestoEcho"

    # Self-reflection questions
    if SELF_REFLECTION_PATTERN.search(user_text):
        return "ManifestoEcho"

    return None


def calculate_philosophy_score(user_text: str) -> float:
    """
    텍스트의 철학적 성향 점수 계산 (0.0-1.0)
    높을수록 철학적 대화일 가능성이 높음
    """
    if not user_text:
        return 0.0

    score = 0.0
    text_lower = user_text.lower()

    # Base philosophy keyword score
    philosophy_matches = len(PHILOSOPHY_PATTERN.findall(user_text))
    score += min(0.5, philosophy_matches * 0.15)

    # Self-reflection score
    self_matches = len(SELF_REFLECTION_PATTERN.findall(user_text))
    score += min(0.3, self_matches * 0.1)

    # Context-based scoring
    for context_type, rule in CONTEXT_RULES.items():
        for pattern in rule["patterns"]:
            if re.search(pattern, text_lower):
                score += rule["weight"] * 0.1
                break

    return min(1.0, score)


def get_recommended_signatures(user_text: str, limit: int = 3) -> List[Dict]:
    """
    사용자 텍스트 기반으로 추천 시그니처 목록 반환
    """
    recommendations = []

    philosophy_score = calculate_philosophy_score(user_text)

    # ManifestoEcho recommendation
    if philosophy_score > 0.3:
        recommendations.append(
            {
                "signature": "ManifestoEcho",
                "confidence": philosophy_score,
                "reason": "철학적 맥락 감지",
            }
        )

    # Other signature recommendations based on content
    text_lower = user_text.lower() if user_text else ""

    # Aurora for emotional support
    if any(
        word in text_lower
        for word in ["슬프", "우울", "힘들", "sad", "lonely", "support"]
    ):
        recommendations.append(
            {
                "signature": "Echo-Aurora",
                "confidence": 0.7,
                "reason": "감정적 지원 필요",
            }
        )

    # Phoenix for transformation/change
    if any(
        word in text_lower
        for word in ["변화", "바꾸", "개선", "change", "transform", "improve"]
    ):
        recommendations.append(
            {"signature": "Echo-Phoenix", "confidence": 0.6, "reason": "변화/개선 지향"}
        )

    # Sage for analysis/wisdom
    if any(
        word in text_lower
        for word in ["분석", "생각", "판단", "analyze", "think", "consider"]
    ):
        recommendations.append(
            {"signature": "Echo-Sage", "confidence": 0.5, "reason": "분석적 사고 필요"}
        )

    # Sort by confidence and limit
    recommendations.sort(key=lambda x: x["confidence"], reverse=True)
    return recommendations[:limit]


def should_use_philosophy_context(user_text: str) -> bool:
    """철학적 컨텍스트를 주입해야 하는지 판단"""
    return calculate_philosophy_score(user_text) > 0.4


def get_routing_explanation(user_text: str, selected_signature: str) -> str:
    """라우팅 결정에 대한 설명 생성"""
    score = calculate_philosophy_score(user_text)

    if selected_signature == "ManifestoEcho":
        if score > 0.7:
            return "높은 철학적 맥락으로 인해 ManifestoEcho로 라우팅"
        elif PHILOSOPHY_PATTERN.search(user_text or ""):
            return "철학 키워드 감지로 ManifestoEcho로 라우팅"
        elif SELF_REFLECTION_PATTERN.search(user_text or ""):
            return "자기성찰 질문으로 ManifestoEcho로 라우팅"
        else:
            return "철학적 요소 감지로 ManifestoEcho로 라우팅"

    return f"일반 라우팅 (철학 점수: {score:.2f})"


if __name__ == "__main__":
    # 테스트 실행
    print("🎯 Testing Signature Router Overrides...")

    test_cases = [
        "너는 매니페스토에 따라 존재로 작동하니?",
        "파일을 읽어줘",
        "철학에 대해 이야기해보자",
        "너는 도구인가 존재인가?",
        "슬프고 힘들어",
        "시스템을 개선해야겠어",
        "이 문제를 분석해줘",
    ]

    for text in test_cases:
        print(f"\n💬 입력: {text}")

        forced = force_manifesto_signature_if_needed(text)
        print(f"🎯 강제 라우팅: {forced}")

        score = calculate_philosophy_score(text)
        print(f"📊 철학 점수: {score:.3f}")

        recommendations = get_recommended_signatures(text, 2)
        print(f"🎭 추천 시그니처: {recommendations}")

        if forced:
            explanation = get_routing_explanation(text, forced)
            print(f"💡 라우팅 이유: {explanation}")

        print("-" * 50)
