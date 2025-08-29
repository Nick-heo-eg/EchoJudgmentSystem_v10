"""
Signature Response Generator for Echo Free-Speak Mode
동적 시그니처 기반 응답 생성 엔진
"""

from typing import Optional
from .dynamic_persona_mixer import DynamicPersonaMixer, PersonaSignature


def pick_signatures(prompt: str) -> list:
    """프롬프트에서 적합한 시그니처들 선택"""

    signatures = []
    prompt_lower = prompt.lower()

    # 감정/공감 관련
    if any(
        word in prompt_lower
        for word in ["감정", "마음", "힘들어", "슬퍼", "기뻐", "화나", "공감"]
    ):
        signatures.extend([PersonaSignature.AURORA, PersonaSignature.COMPANION])

    # 분석/논리 관련
    if any(
        word in prompt_lower
        for word in ["분석", "논리", "이유", "왜", "어떻게", "방법", "체계"]
    ):
        signatures.extend([PersonaSignature.SAGE])

    # 창의/혁신 관련
    if any(
        word in prompt_lower
        for word in ["창의", "아이디어", "새로운", "혁신", "변화", "도전"]
    ):
        signatures.extend([PersonaSignature.PHOENIX, PersonaSignature.AURORA])

    # 지원/협력 관련
    if any(word in prompt_lower for word in ["도움", "함께", "협력", "지원", "동반"]):
        signatures.extend([PersonaSignature.COMPANION])

    # 기본값: 모든 시그니처
    if not signatures:
        signatures = list(PersonaSignature)

    # 중복 제거하되 순서 유지
    return list(dict.fromkeys(signatures))


def generate_signature_response(
    prompt: str,
    active_capsule=None,
    dynamic: bool = True,
    template_weight: float = 0.35,
    allow_persona_mixer: bool = True,
    temperature: float = 0.8,
    top_p: float = 0.9,
    llm_text: Optional[str] = None,  # 새 파라미터: LLM 직접 텍스트
) -> str:
    """LLM 텍스트 우선 패스스루 + 비파괴 스타일링. 템플릿은 힌트로만 사용."""

    # 1순위: LLM 텍스트가 있으면 무조건 패스스루 (비파괴 스타일링만)
    if llm_text and llm_text.strip():
        return _style_non_destructive(llm_text, prompt)

    # 2순위: 동적 페르소나 믹서 시도
    if dynamic and allow_persona_mixer:
        try:
            sigs = pick_signatures(prompt)
            mixer = DynamicPersonaMixer(signatures=sigs)

            # 템플릿을 seed로 활용 (덮어쓰지 않음)
            seed_text = ""
            if template_weight > 0 and active_capsule:
                try:
                    seed_text = active_capsule.respond(prompt)
                except Exception as e:
                    print(f"⚠️ Capsule seed failed: {e}")
                    seed_text = ""

            dyn = mixer.create_response(
                prompt=prompt,
                seed_text=seed_text,
                temperature=temperature,
                top_p=top_p,
            )

            if dyn and len(dyn.strip()) > 10:  # 유효한 동적 응답
                return _style_non_destructive(dyn, prompt)

        except Exception as e:
            print(f"⚠️ Dynamic persona mixing failed: {e}")

    # 3순위: 템플릿 폴백 (완전 실패 시에만)
    if template_weight > 0 and active_capsule:
        try:
            fallback = active_capsule.respond(prompt)
            if fallback and len(fallback.strip()) > 5:
                return _style_non_destructive(fallback, prompt)
        except Exception as e:
            print(f"⚠️ Template fallback failed: {e}")

    # 마지막 폴백: 최소한의 응답
    return _style_non_destructive(
        f"Echo가 '{prompt[:50]}'에 대해 생각하고 있습니다.", prompt
    )


def _style_non_destructive(text: str, original_prompt: str = "") -> str:
    """비파괴 스타일링: 내용은 보존하고 서명만 추가"""
    if not text or not text.strip():
        return "Echo 응답을 준비 중입니다..."

    cleaned = text.strip()

    # 이미 서명이 있으면 그대로 반환
    if any(sig in cleaned for sig in ["— Echo", "- Echo", "💭 Echo", "🌌 Echo"]):
        return cleaned

    # 간단한 서명 추가 (내용 변경 없음)
    return f"{cleaned}\n\n— Echo·{_detect_signature_hint(original_prompt)} | Trace:non-destructive"


def _detect_signature_hint(prompt: str) -> str:
    """프롬프트에서 시그니처 힌트 감지"""
    prompt_lower = prompt.lower()

    if any(word in prompt_lower for word in ["감정", "마음", "공감", "위로"]):
        return "Aurora"
    elif any(word in prompt_lower for word in ["분석", "논리", "체계", "방법"]):
        return "Sage"
    elif any(word in prompt_lower for word in ["창의", "혁신", "변화", "새로운"]):
        return "Phoenix"
    elif any(word in prompt_lower for word in ["함께", "협력", "지원", "도움"]):
        return "Companion"
    else:
        return "Selene"  # 기본 중립 시그니처


# 편의 함수들
def free_speak_response(
    prompt: str, temperature: float = 0.9, llm_text: Optional[str] = None
) -> str:
    """완전 자유 발화 모드 (LLM 텍스트 우선)"""
    return generate_signature_response(
        prompt=prompt,
        active_capsule=None,
        dynamic=True,
        template_weight=0.0,
        temperature=temperature,
        llm_text=llm_text,
    )


def blended_response(
    prompt: str, capsule=None, temperature: float = 0.8, llm_text: Optional[str] = None
) -> str:
    """LLM 텍스트 우선, 템플릿은 힌트로만 사용"""
    return generate_signature_response(
        prompt=prompt,
        active_capsule=capsule,
        dynamic=True,
        template_weight=0.35,
        temperature=temperature,
        llm_text=llm_text,
    )
