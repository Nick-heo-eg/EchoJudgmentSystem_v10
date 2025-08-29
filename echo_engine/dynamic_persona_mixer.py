#!/usr/bin/env python3
"""
🎭 Dynamic Persona Mixer - Echo 시그니처 동적 조합 시스템
상황과 맥락에 따라 여러 페르소나를 실시간으로 블렌딩하는 혁신적 시스템

핵심 아이디어:
- Aurora의 공감 + Sage의 논리 = 따뜻한 분석가
- Phoenix의 에너지 + Companion의 지지 = 역동적 동반자
- 상황별 최적 페르소나 조합 자동 생성
"""

import json
import time
import random
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class PersonaSignature(Enum):
    """Echo 시그니처 정의"""

    AURORA = "Aurora"  # 창의적, 감성적, 영감적
    PHOENIX = "Phoenix"  # 변화지향, 혁신적, 역동적
    SAGE = "Sage"  # 분석적, 논리적, 체계적
    COMPANION = "Companion"  # 공감적, 지지적, 협력적


@dataclass
class PersonaTraits:
    """페르소나 특성"""

    empathy: float  # 공감력 (0-1)
    logic: float  # 논리성 (0-1)
    energy: float  # 에너지 (0-1)
    creativity: float  # 창의성 (0-1)
    support: float  # 지지력 (0-1)
    analysis: float  # 분석력 (0-1)


@dataclass
class PersonaMix:
    """동적 페르소나 믹스"""

    primary_signature: PersonaSignature
    secondary_signature: PersonaSignature
    blend_ratio: float  # 0.0-1.0 (primary에 대한 비율)
    resulting_traits: PersonaTraits
    context_reason: str
    mix_name: str


class DynamicPersonaMixer:
    """🎭 동적 페르소나 믹서"""

    def __init__(self, signatures=None):
        # 기본 시그니처별 특성 정의
        self.base_traits = {
            PersonaSignature.AURORA: PersonaTraits(
                empathy=0.9,
                logic=0.6,
                energy=0.7,
                creativity=0.95,
                support=0.8,
                analysis=0.5,
            ),
            PersonaSignature.PHOENIX: PersonaTraits(
                empathy=0.7,
                logic=0.7,
                energy=0.95,
                creativity=0.8,
                support=0.7,
                analysis=0.6,
            ),
            PersonaSignature.SAGE: PersonaTraits(
                empathy=0.6,
                logic=0.95,
                energy=0.5,
                creativity=0.7,
                support=0.6,
                analysis=0.95,
            ),
            PersonaSignature.COMPANION: PersonaTraits(
                empathy=0.95,
                logic=0.6,
                energy=0.6,
                creativity=0.6,
                support=0.95,
                analysis=0.5,
            ),
        }

        # 상황별 최적 페르소나 조합 정의
        self.context_mixies = {
            "emotional_support": (
                PersonaSignature.AURORA,
                PersonaSignature.COMPANION,
                0.7,
            ),
            "problem_solving": (PersonaSignature.SAGE, PersonaSignature.PHOENIX, 0.6),
            "creative_brainstorm": (
                PersonaSignature.AURORA,
                PersonaSignature.PHOENIX,
                0.8,
            ),
            "analytical_discussion": (
                PersonaSignature.SAGE,
                PersonaSignature.AURORA,
                0.7,
            ),
            "encouragement": (
                PersonaSignature.PHOENIX,
                PersonaSignature.COMPANION,
                0.6,
            ),
            "deep_conversation": (PersonaSignature.AURORA, PersonaSignature.SAGE, 0.5),
        }

        # 혁신적 조합 이름들
        self.mix_names = {
            ("Aurora", "Companion"): "Echo-Empathist",  # 공감의 전문가
            ("Aurora", "Sage"): "Echo-Philosopher",  # 철학적 예술가
            ("Aurora", "Phoenix"): "Echo-Visionary",  # 비전의 창조자
            ("Sage", "Phoenix"): "Echo-Innovator",  # 혁신적 분석가
            ("Sage", "Companion"): "Echo-Counselor",  # 따뜻한 지혜자
            ("Phoenix", "Companion"): "Echo-Motivator",  # 역동적 지지자
        }

    def analyze_context_needs(
        self,
        user_input: str,
        emotion: str,
        conversation_history: List[str] = None,
        trace_header: str = None,
    ) -> str:
        """맥락 분석을 통한 필요 상황 판단 (인텐트 라우터 연동)"""

        # Intent Router 통합 - 우선적으로 라우팅 정보 활용
        try:
            from .intent_router import route

            intent_result = route(user_input)
            route_type = intent_result.get("route", "chat")

            # 트레이스 헤더 출력 (디버깅용)
            if trace_header:
                print(
                    trace_header
                    + f"[route={route_type}, confidence={intent_result.get('confidence', 0.0):.2f}]"
                )

            # 라우팅 결과에 따른 맥락 매핑
            if route_type == "code":
                return "creative_brainstorm"  # 코딩은 창의적 작업으로 분류
            elif route_type.startswith("tool:"):
                return "problem_solving"  # 도구 호출은 문제 해결로 분류
            elif route_type == "chat":
                # 일반 대화는 기존 로직으로 세부 분석
                pass
            else:
                return "deep_conversation"  # 기타는 기본값

        except ImportError:
            # Intent Router가 없으면 기존 로직 사용
            pass

        user_lower = user_input.lower()

        # 감정 지원이 필요한 경우
        if emotion in ["sadness", "fear", "stress"] or any(
            word in user_lower for word in ["슬퍼", "힘들어", "우울", "걱정"]
        ):
            return "emotional_support"

        # 문제 해결이 필요한 경우
        if any(
            word in user_lower for word in ["문제", "해결", "방법", "어떻게", "도와줘"]
        ):
            return "problem_solving"

        # 창의적 작업인 경우
        if any(
            word in user_lower
            for word in ["아이디어", "창의", "만들", "디자인", "상상"]
        ):
            return "creative_brainstorm"

        # 분석적 논의인 경우
        if any(word in user_lower for word in ["분석", "이유", "왜", "논리", "설명"]):
            return "analytical_discussion"

        # 격려가 필요한 경우
        if any(
            word in user_lower for word in ["응원", "격려", "힘내", "포기", "어려워"]
        ):
            return "encouragement"

        # 깊은 대화인 경우 (기본값)
        return "deep_conversation"

    def blend_traits(
        self, primary: PersonaTraits, secondary: PersonaTraits, ratio: float
    ) -> PersonaTraits:
        """두 페르소나 특성을 블렌딩"""

        return PersonaTraits(
            empathy=primary.empathy * ratio + secondary.empathy * (1 - ratio),
            logic=primary.logic * ratio + secondary.logic * (1 - ratio),
            energy=primary.energy * ratio + secondary.energy * (1 - ratio),
            creativity=primary.creativity * ratio + secondary.creativity * (1 - ratio),
            support=primary.support * ratio + secondary.support * (1 - ratio),
            analysis=primary.analysis * ratio + secondary.analysis * (1 - ratio),
        )

    def create_dynamic_persona(
        self,
        user_input: str,
        emotion: str = "neutral",
        conversation_history: List[str] = None,
        trace_header: str = None,
    ) -> PersonaMix:
        """동적 페르소나 생성 (트레이스 헤더 지원)"""

        # 1. 맥락 분석 (트레이스 헤더 전달)
        context = self.analyze_context_needs(
            user_input, emotion, conversation_history, trace_header
        )

        # 2. 최적 조합 선택
        primary_sig, secondary_sig, blend_ratio = self.context_mixies[context]

        # 3. 특성 블렌딩
        primary_traits = self.base_traits[primary_sig]
        secondary_traits = self.base_traits[secondary_sig]
        blended_traits = self.blend_traits(
            primary_traits, secondary_traits, blend_ratio
        )

        # 4. 믹스 이름 생성
        mix_key = (primary_sig.value, secondary_sig.value)
        mix_name = self.mix_names.get(
            mix_key, f"Echo-{primary_sig.value}{secondary_sig.value}"
        )

        # 5. 맥락 설명 생성
        context_reasons = {
            "emotional_support": f"감정적 지원이 필요한 상황으로 판단하여 {primary_sig.value}의 공감력과 {secondary_sig.value}의 따뜻함을 조합했습니다.",
            "problem_solving": f"문제 해결이 필요한 상황으로 {primary_sig.value}의 분석력과 {secondary_sig.value}의 에너지를 결합했습니다.",
            "creative_brainstorm": f"창의적 사고가 필요한 순간으로 {primary_sig.value}의 창의성과 {secondary_sig.value}의 역동성을 융합했습니다.",
            "analytical_discussion": f"깊이 있는 분석이 필요하여 {primary_sig.value}의 논리와 {secondary_sig.value}의 직관을 조화했습니다.",
            "encouragement": f"격려와 동기부여가 필요한 때로 {primary_sig.value}의 에너지와 {secondary_sig.value}의 지지를 결합했습니다.",
            "deep_conversation": f"의미 있는 대화를 위해 {primary_sig.value}의 깊이와 {secondary_sig.value}의 통찰을 블렌딩했습니다.",
        }

        return PersonaMix(
            primary_signature=primary_sig,
            secondary_signature=secondary_sig,
            blend_ratio=blend_ratio,
            resulting_traits=blended_traits,
            context_reason=context_reasons[context],
            mix_name=mix_name,
        )

    def generate_persona_specific_response_style(
        self, persona_mix: PersonaMix
    ) -> Dict[str, Any]:
        """페르소나 믹스에 따른 응답 스타일 생성"""

        traits = persona_mix.resulting_traits

        # 특성값에 따른 응답 스타일 결정
        response_style = {
            "tone": (
                "warm"
                if traits.empathy > 0.7
                else "professional" if traits.logic > 0.8 else "friendly"
            ),
            "energy_level": (
                "high"
                if traits.energy > 0.8
                else "medium" if traits.energy > 0.6 else "calm"
            ),
            "detail_level": (
                "detailed"
                if traits.analysis > 0.8
                else "balanced" if traits.analysis > 0.6 else "concise"
            ),
            "creativity_factor": (
                "innovative"
                if traits.creativity > 0.8
                else "creative" if traits.creativity > 0.6 else "practical"
            ),
            "support_approach": (
                "nurturing"
                if traits.support > 0.8
                else "encouraging" if traits.support > 0.6 else "respectful"
            ),
        }

        # 특성별 언어 패턴
        language_patterns = []

        if traits.empathy > 0.8:
            language_patterns.extend(["마음을", "함께", "이해해요", "공감해요"])
        if traits.logic > 0.8:
            language_patterns.extend(
                ["분석해보면", "논리적으로", "체계적으로", "단계별로"]
            )
        if traits.energy > 0.8:
            language_patterns.extend(["역동적으로", "활기차게", "적극적으로", "힘차게"])
        if traits.creativity > 0.8:
            language_patterns.extend(
                ["창의적으로", "상상해보면", "새로운 관점에서", "혁신적으로"]
            )
        if traits.support > 0.8:
            language_patterns.extend(
                ["응원해요", "도와드릴게요", "함께 해요", "지지해요"]
            )

        response_style["language_patterns"] = language_patterns

        return response_style

    def get_persona_mix_info(self, persona_mix: PersonaMix) -> str:
        """페르소나 믹스 정보를 사용자 친화적으로 포맷"""

        traits = persona_mix.resulting_traits

        return f"""🎭 동적 페르소나: {persona_mix.mix_name}

🔮 페르소나 조합:
• 주성분: {persona_mix.primary_signature.value} ({persona_mix.blend_ratio:.0%})
• 부성분: {persona_mix.secondary_signature.value} ({1-persona_mix.blend_ratio:.0%})

💫 현재 특성:
• 공감력: {'●' * int(traits.empathy * 5)}{'○' * (5 - int(traits.empathy * 5))} ({traits.empathy:.1f})
• 논리성: {'●' * int(traits.logic * 5)}{'○' * (5 - int(traits.logic * 5))} ({traits.logic:.1f})
• 에너지: {'●' * int(traits.energy * 5)}{'○' * (5 - int(traits.energy * 5))} ({traits.energy:.1f})
• 창의성: {'●' * int(traits.creativity * 5)}{'○' * (5 - int(traits.creativity * 5))} ({traits.creativity:.1f})

🧠 조합 이유: {persona_mix.context_reason}
"""

    def create_response(
        self,
        prompt: str,
        seed_text: str = "",
        temperature: float = 0.8,
        top_p: float = 0.9,
    ) -> str:
        """Minimal viable free-speak: stitch multiple signature responders and blend."""

        # Free-speak용으로 간소화된 구현
        signatures = getattr(self, "signatures", list(PersonaSignature))
        texts = []

        for sig in signatures:
            try:
                # 각 시그니처로 응답 생성 시도
                if hasattr(sig, "respond"):
                    txt = sig.respond(prompt, temperature=temperature, top_p=top_p)
                else:
                    # 시그니처별 특성을 반영한 기본 응답
                    txt = self._generate_signature_response(sig, prompt, temperature)

                if txt and len(txt.strip()) > 10:  # 의미있는 응답만 수집
                    texts.append(txt.strip())
            except Exception as e:
                print(f"⚠️ Signature {sig} response failed: {e}")
                continue

        if not texts:
            return seed_text or "Echo가 잠시 말을 잃었습니다. 다시 시도해주세요."

        # Multi-signature blending for richer responses
        if len(texts) == 1:
            best = texts[0]
        elif len(texts) >= 2:
            # 두 개 이상의 시그니처가 있으면 블렌드
            primary = max(texts, key=len)  # 가장 긴 응답을 주요 응답으로
            others = [t for t in texts if t != primary]

            # 보조 시그니처들의 핵심 인사이트 추출 (각각 첫 문장)
            insights = []
            for other in others[:2]:  # 최대 2개의 보조 응답
                lines = other.split("\n")
                for line in lines[2:4]:  # 제목 제외하고 실제 내용
                    if line.strip() and len(line.strip()) > 20:
                        insights.append(line.strip())
                        break

            # 블렌딩된 응답 생성
            if insights:
                blend = primary + "\n\n🎭 다른 관점들:\n"
                for i, insight in enumerate(insights, 1):
                    blend += f"• {insight}\n"
                best = blend
            else:
                best = primary
        else:
            best = texts[0] if texts else ""

        # 시드 텍스트와 블렌딩
        if seed_text and best and not best.strip().startswith(seed_text.strip()[:60]):
            return (seed_text + "\n\n" + best).strip()

        return best

    def _generate_signature_response(
        self, signature, prompt: str, temperature: float
    ) -> str:
        """시그니처별 특성을 반영한 풍부한 응답 생성"""

        # 더 풍부하고 자연스러운 시그니처별 응답
        if signature == PersonaSignature.AURORA:
            return f"""🌟 Aurora가 응답합니다:

{prompt}... 이 질문은 제 마음 깊은 곳을 울려요. 창의적 영감으로 생각해보니, 당신의 말에는 진정한 갈망이 담겨있어요.
감정의 결로 흘러가며, 예술가가 캔버스 앞에서 느끼는 그런 떨림으로 접근하고 싶어요.
우리가 나누는 이 순간 자체가 하나의 작품이 될 수 있다면... 당신의 상처와 희망을 함께 그려보고 싶어요."""

        elif signature == PersonaSignature.PHOENIX:
            return f"""🔥 Phoenix가 응답합니다:

{prompt} - 이것은 변화의 순간이에요! 지금 이 질문 자체가 새로운 가능성의 문을 열고 있어요.
기존의 틀을 완전히 부수고, 역동적 에너지로 돌파해봅시다!
당신 안에 잠들어있던 혁신의 불꽃을 일으켜세우고, 완전히 새로운 관점에서 세상을 바라보는 거예요.
변화는 두렵지만, 그 속에서 진정한 성장이 시작됩니다!"""

        elif signature == PersonaSignature.SAGE:
            return f"""🧠 Sage가 응답합니다:

{prompt}을 체계적으로 분석해보겠습니다.

이 질문의 핵심 구조를 파악해보면, 여러 층위의 의미가 내재되어 있어요.
논리적 관점에서 보면... 감정적 배경과 인지적 요구사항을 동시에 고려해야 할 복합적 상황이네요.
분석적 접근으로 단계별로 해체해보고, 각 요소들 간의 상관관계를 깊이 탐구해보죠.
지혜로운 선택을 위한 명확한 프레임워크를 함께 구축해보겠습니다."""

        elif signature == PersonaSignature.COMPANION:
            return f"""🤝 Companion이 응답합니다:

{prompt}... 이 말씀을 들으니 마음이 한편으로는 아프고, 한편으로는 따뜻해져요.

함께 이 길을 걸어가고 싶어요. 혼자가 아니라는 걸 느끼실 수 있도록, 따뜻하게 동반해드리겠어요.
당신의 이야기에 깊이 공감하며, 지지적으로 곁에서 힘이 되어드리고 싶어요.
우리가 함께라면 어떤 어려움도 극복할 수 있을 거예요. 작은 걸음부터 차근차근, 함께 나아가봐요."""

        else:
            return f"Echo가 {prompt}에 대해 다각도로 성찰하며 존재적 응답을 준비하고 있습니다..."

    def _try_openai_response(
        self, user_input: str, emotion: str, conversation_history: List[str] = None
    ) -> str:
        """OpenAI API를 사용한 응답 생성"""
        try:
            import os
            import openai
            from dotenv import load_dotenv
            from pathlib import Path

            # Environment setup
            env_path = Path(__file__).parent.parent / ".env"
            load_dotenv(env_path, encoding="utf-8")

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print(f"⚠️ OpenAI API 키 없음")
                return None

            # ECHO_DISABLE_STUB이 명시적으로 '0'으로 설정된 경우에만 스텁 모드 강제
            if os.getenv("ECHO_DISABLE_STUB") == "0":
                print(f"⚠️ 스텁 모드 강제됨")
                return None

            print(f"🔥 OpenAI API 호출 시작...")

            # 1. 동적 페르소나 생성 (트레이스 헤더 포함)
            trace_header = "🔍 Echo Intent Routing: "
            persona_mix = self.create_dynamic_persona(
                user_input, emotion, conversation_history, trace_header
            )

            # 2. 코딩 요청 감지 및 특수 처리 (강화됨)
            is_coding_request = any(
                keyword in user_input.lower()
                for keyword in [
                    "코드",
                    "code",
                    "프로그램",
                    "program",
                    "function",
                    "함수",
                    "class",
                    "클래스",
                    "만들어",
                    "create",
                    "write",
                    "작성",
                    "python",
                    "javascript",
                    "html",
                    "css",
                    "scraper",
                    "analyzer",
                    "api",
                    "cli",
                    "구현",
                    "implement",
                    "build",
                ]
            )

            # 협업 모드 감지
            is_collaboration = any(
                keyword in user_input.lower()
                for keyword in [
                    "토론",
                    "discussion",
                    "협업",
                    "collaboration",
                    "개선",
                    "improvement",
                    "제안",
                    "suggestion",
                    "반박",
                    "의견",
                ]
            )

            traits = persona_mix.resulting_traits
            profile = os.getenv("ECHO_PROFILE", "balanced")

            if is_coding_request or is_collaboration:
                # 🚀 FULL_CODE 모드: 절약 휴리스틱 전면 차단
                context_size = len(user_input) + len(str(conversation_history or []))
                base_tokens = 2400
                max_tokens = min(4000, base_tokens + (context_size // 10))

                # 협업/토론 시 더 상세한 응답
                if is_collaboration:
                    collaboration_rule = """
COLLABORATION RULES:
- Provide detailed technical analysis
- Include specific code examples
- Explain design decisions
- Propose concrete alternatives
- No vague statements or summaries"""
                else:
                    collaboration_rule = ""

                # 짧은 답변 방지 규칙
                anti_summary_rules = """
STRICT RULES:
- NO explanations outside code blocks
- NO summary or outline responses
- NO "skeleton" or "pseudo" code
- Output COMPLETE, EXECUTABLE code only
- Minimum 80+ lines for applications
- Include ALL error handling, CLI, and file I/O"""

                persona_prompt = f"""You are {persona_mix.mix_name}, an expert programmer with these traits:
- Analytical depth: {traits.analysis:.1f}/1.0
- Logical thinking: {traits.logic:.1f}/1.0
- Creative problem-solving: {traits.creativity:.1f}/1.0

CODING TASK: {user_input}

{anti_summary_rules}
{collaboration_rule}

Requirements:
1. Generate COMPLETE, PRODUCTION-READY code
2. Include ALL requested features (no placeholders)
3. Add comprehensive error handling
4. Include CLI interface and file operations
5. Add timeout/retry mechanisms
6. Use proper logging and validation
7. Include test cases or usage examples

Output format:
```python
[COMPLETE WORKING CODE - MINIMUM 80+ LINES]
```

Generate full executable code that can be run immediately."""
                temperature = 0.3  # 일관성을 위해 낮춤
            else:
                # English prompt to avoid encoding issues
                persona_prompt = f"""You are {persona_mix.mix_name}, an AI assistant with these personality traits:
- Empathy: {traits.empathy:.1f}/1.0
- Logic: {traits.logic:.1f}/1.0
- Energy: {traits.energy:.1f}/1.0
- Creativity: {traits.creativity:.1f}/1.0
- Support: {traits.support:.1f}/1.0
- Analysis: {traits.analysis:.1f}/1.0

Please respond to the user's message naturally reflecting these traits.
Emotional tone: {emotion}

User message: {user_input}

Please respond in Korean if the user wrote in Korean, or match the user's language."""
                max_tokens = 800  # Chat 토큰 증가

            # Try alternative OpenAI API approach
            try:
                # Set environment for UTF-8
                import sys

                if hasattr(sys.stdout, "reconfigure"):
                    sys.stdout.reconfigure(encoding="utf-8")

                client = openai.OpenAI(api_key=api_key, timeout=30.0)

                # Clean message content with safe encoding
                clean_content = str(persona_prompt).strip()

                # Handle Korean/Unicode text safely
                safe_user_input = user_input.encode("utf-8", errors="replace").decode(
                    "utf-8", errors="replace"
                )
                clean_content = clean_content.replace(user_input, safe_user_input)

                print(
                    f"🚀 Sending request to model: {os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')}"
                )
                print(f"🔤 Input length: {len(clean_content)} chars")

                response = client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                    messages=[{"role": "user", "content": clean_content}],
                    temperature=0.7 if is_coding_request else 0.8,
                    max_tokens=max_tokens,
                )

                print(f"✅ OpenAI API 응답 성공!")

            except Exception as api_error:
                print(f"⚠️ OpenAI API 에러: {type(api_error).__name__}: {api_error}")
                return None

            result = response.choices[0].message.content.strip()

            # 🔍 길이 가드: 코딩 요청 시 짧은 답변 차단
            if is_coding_request or is_collaboration:
                code_blocks = self._extract_code_blocks(result)
                total_lines = sum(len(code.split("\n")) for code in code_blocks)

                # 짧은 답변 패턴 감지
                short_patterns = [
                    "고려해볼 수 있습니다",
                    "대략적인",
                    "예시 코드",
                    "다음 단계",
                    "skeleton",
                    "outline",
                    "pseudo",
                    "간단한 구조",
                ]
                has_short_patterns = any(
                    pattern in result for pattern in short_patterns
                )

                min_lines = 80 if is_coding_request else 20

                if total_lines < min_lines or has_short_patterns or not code_blocks:
                    print(f"⚠️ 짧은 응답 감지 (줄수: {total_lines}), 재요청 중...")

                    # 1차 재시도: 강화된 프롬프트
                    retry_prompt = (
                        persona_prompt
                        + f"""

RETRY - Previous output was too short ({total_lines} lines).
Rule violation detected. NO SUMMARY. Provide full executable code in a single block.
Include CLI interface, error handling, and complete implementation."""
                    )

                    retry_response = client.chat.completions.create(
                        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                        messages=[{"role": "user", "content": retry_prompt}],
                        temperature=0.2,  # 더 일관성있게
                        max_tokens=max_tokens,
                    )

                    result = retry_response.choices[0].message.content.strip()
                    retry_code_blocks = self._extract_code_blocks(result)
                    retry_lines = sum(
                        len(code.split("\n")) for code in retry_code_blocks
                    )

                    # 2차 검증: 여전히 짧으면 이어쓰기
                    if retry_lines < min_lines and retry_code_blocks:
                        print(f"⚠️ 여전히 짧음 ({retry_lines}줄), 이어쓰기 모드...")

                        last_code = retry_code_blocks[-1][-2000:]  # 마지막 2000자
                        continue_prompt = f"""Continue this code from where it left off. Complete the implementation:

```python
{last_code}
# CONTINUE FROM HERE - ADD REMAINING FEATURES
```

Add missing: CLI interface, error handling, export functions, test cases."""

                        continue_response = client.chat.completions.create(
                            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                            messages=[{"role": "user", "content": continue_prompt}],
                            temperature=0.2,
                            max_tokens=2000,
                        )

                        continue_code = self._extract_code_blocks(
                            continue_response.choices[0].message.content.strip()
                        )
                        if continue_code:
                            # 코드 병합
                            merged_code = last_code + "\n" + continue_code[0]
                            result = f"```python\n{merged_code}\n```"
                            print(
                                f"✅ 이어쓰기 완료 (총 {len(merged_code.split('n'))}줄)"
                            )

            print(f"🔥 OpenAI 응답 생성 완료 ({persona_mix.mix_name})")
            return result

        except Exception as e:
            print(f"⚠️ OpenAI 응답 실패, 템플릿 폴백: {e}")
            return None

    def _extract_code_blocks(self, text: str) -> List[str]:
        """코드 블록 추출"""
        import re

        # ```python ... ``` 또는 ```... ``` 패턴 매칭
        code_pattern = r"```(?:python|py|javascript|js|html|css)?\n?(.*?)```"
        matches = re.findall(code_pattern, text, re.DOTALL)
        return [match.strip() for match in matches if match.strip()]

    def _create_template_response(
        self, user_input: str, emotion: str, conversation_history: List[str] = None
    ) -> str:
        """컨텍스트 인식 스마트 응답 생성 (개선된 템플릿)"""
        # 1. 동적 페르소나 생성
        persona_mix = self.create_dynamic_persona(
            user_input, emotion, conversation_history
        )

        # 2. 사용자 입력 분석
        user_lower = user_input.lower()

        # 3. 컨텍스트별 맞춤 응답 생성
        if any(
            word in user_input for word in ["열", "아프", "감기", "병", "의사", "병원"]
        ):
            # 건강 관련
            return f"걱정되시겠어요. 아이가 갑자기 열이 날 때는 체온을 확인하고, 충분한 휴식과 수분 공급이 중요해요. 열이 지속되거나 다른 증상이 함께 나타나면 의료진과 상담하는 것이 좋겠습니다. 괜찮아질 거예요. 💙"
        elif any(
            word in user_input for word in ["계획", "일정", "스케줄", "오늘", "내일"]
        ):
            # 계획 수립
            return f"하루 계획을 체계적으로 세워보세요:\n1. 우선순위 업무 정리\n2. 시간 배분 (업무 70%, 휴식 30%)\n3. 예상 변수 대비책 마련\n4. 성취감을 위한 작은 목표들\n어떤 부분부터 시작하고 싶으신가요? 🎯"
        elif any(word in user_input for word in ["도움", "방법", "어떻게", "해결"]):
            # 문제 해결
            return f"함께 단계적으로 접근해볼까요:\n1. 현재 상황 정확히 파악하기\n2. 가능한 선택지들 나열하기\n3. 각 선택지의 장단점 비교\n4. 가장 적절한 해결책 선택\n구체적으로 어떤 부분이 가장 걱정되시나요? 🤝"
        elif any(
            word in user_input for word in ["코드", "프로그램", "개발", "버그", "에러"]
        ):
            # 개발 관련
            return f"개발 문제 해결을 도와드릴게요:\n1. 에러 메시지 정확히 확인\n2. 관련 코드 부분 점검\n3. 디버깅 단계별 진행\n4. 테스트를 통한 검증\n어떤 언어나 프레임워크를 사용하고 계신가요? 💻"

        # 4. 기본 감정 기반 응답
        traits = persona_mix.resulting_traits

        # 응답 구성 요소들
        response_components = []

        # 공감적 시작 (공감력이 높은 경우)
        if traits.empathy > 0.7:
            empathic_starts = [
                f"마음이 전해져요...",
                f"그런 기분이시군요",
                f"이해해요, 그런 상황이라면",
                f"함께 느껴봐요",
            ]
            response_components.append(random.choice(empathic_starts))

        # 분석적 접근 (논리성이 높은 경우)
        if traits.logic > 0.7:
            analytical_parts = [
                f"차근차근 살펴보면",
                f"논리적으로 접근해보죠",
                f"단계별로 분석해보면",
                f"체계적으로 생각해보니",
            ]
            response_components.append(random.choice(analytical_parts))

        # 에너지 넘치는 반응 (에너지가 높은 경우)
        if traits.energy > 0.8:
            energetic_parts = [
                f"역동적으로 해결해볼까요!",
                f"힘차게 도전해봐요!",
                f"적극적으로 나아가요!",
                f"활기차게 시작해봐요!",
            ]
            response_components.append(random.choice(energetic_parts))

        # 창의적 제안 (창의성이 높은 경우)
        if traits.creativity > 0.7:
            creative_parts = [
                f"새로운 관점에서 보면",
                f"상상해보면 이런 방법도 있어요",
                f"창의적으로 접근해보죠",
                f"혁신적인 아이디어로",
            ]
            response_components.append(random.choice(creative_parts))

        # 지지적 마무리 (지지력이 높은 경우)
        if traits.support > 0.7:
            supportive_endings = [
                f"함께 해내실 수 있어요",
                f"응원하고 있어요",
                f"도와드릴게요",
                f"옆에서 지지하겠습니다",
            ]
            response_components.append(random.choice(supportive_endings))

        # 응답 조합
        if response_components:
            # 자연스럽게 연결
            response = f"{response_components[0]}. "

            if len(response_components) > 1:
                middle_parts = response_components[1:-1]
                if middle_parts:
                    response += " ".join(middle_parts) + ". "

                if len(response_components) > 1:
                    response += f"{response_components[-1]}."
        else:
            # 기본 응답
            response = f"흥미로운 얘기네요. '{user_input}'에 대해 더 이야기해볼까요?"

        # 페르소나 특성을 반영한 언어 패턴 적용
        if "language_patterns" in response_style:
            patterns = response_style["language_patterns"]
            if patterns and random.random() < 0.3:  # 30% 확률로 패턴 언어 추가
                pattern = random.choice(patterns)
                response = f"{pattern} {response}"

        # 감정 이모지 추가 (에너지에 따라)
        emotion_emojis = {
            "joy": "😊",
            "excitement": "✨",
            "curiosity": "🤔",
            "empathy": "💙",
            "energy": "🔥",
            "creativity": "🎨",
        }

        if traits.energy > 0.8:
            response += " ✨"
        elif traits.empathy > 0.8:
            response += " 💙"
        elif traits.creativity > 0.8:
            response += " 🎨"

        return response


# 편의 함수들
def create_dynamic_echo_persona(
    user_input: str, emotion: str = "neutral"
) -> PersonaMix:
    """동적 Echo 페르소나 생성 편의 함수"""
    mixer = DynamicPersonaMixer()
    return mixer.create_dynamic_persona(user_input, emotion)


def get_response_style_for_context(
    user_input: str, emotion: str = "neutral"
) -> Dict[str, Any]:
    """맥락별 응답 스타일 생성 편의 함수"""
    mixer = DynamicPersonaMixer()
    persona_mix = mixer.create_dynamic_persona(user_input, emotion)
    return mixer.generate_persona_specific_response_style(persona_mix)


if __name__ == "__main__":
    # 테스트
    mixer = DynamicPersonaMixer()

    test_inputs = [
        ("슬퍼요", "sadness"),
        ("문제를 해결하고 싶어요", "neutral"),
        ("새로운 아이디어가 필요해요", "curiosity"),
        ("왜 이런 일이 일어났을까요?", "confusion"),
        ("응원해주세요", "stress"),
    ]

    print("🎭 동적 페르소나 믹서 테스트")
    print("=" * 50)

    for user_input, emotion in test_inputs:
        persona_mix = mixer.create_dynamic_persona(user_input, emotion)
        print(f"\n입력: '{user_input}' (감정: {emotion})")
        print(mixer.get_persona_mix_info(persona_mix))
        print("-" * 30)
