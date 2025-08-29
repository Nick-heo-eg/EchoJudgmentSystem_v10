#!/usr/bin/env python3
"""
🌟 LLM-First Judgment Engine - Echo 존재 기반 판단 엔진

기존 템플릿 중심에서 벗어나 LLM의 자연스러운 존재적 응답을 중심으로 하는
새로운 판단 아키텍처

핵심 철학:
1. LLM이 생성한 자연스러운 응답을 기본으로 함
2. Echo 레이어는 존재적 서명/스타일링만 담당
3. 템플릿은 힌트/폴백으로만 사용
4. ChatGPT Echo 수준의 자연스러움 달성

아키텍처:
사용자 입력 → 시그니처 컨텍스트 구성 → LLM 호출 → Echo 존재적 보강 → 최종 응답
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from .dynamic_persona_mixer import DynamicPersonaMixer, PersonaSignature
from .models.judgement import InputContext, JudgmentResult


@dataclass
class LLMFirstResult:
    """LLM 우선 판단 결과"""

    original_llm_response: str
    echo_enhanced_response: str
    signature_used: str
    confidence: float
    processing_metadata: Dict[str, Any]


class LLMFirstJudgmentEngine:
    """🌟 LLM 우선 판단 엔진 - Echo 존재적 응답 생성"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

        # 동적 페르소나 믹서 초기화
        self.persona_mixer = DynamicPersonaMixer()

        # 시그니처별 존재적 컨텍스트
        self.signature_contexts = {
            "Aurora": {
                "essence": "창의적이고 감성적인 존재",
                "voice_tone": "따뜻하고 영감을 주는",
                "core_values": ["창의성", "감성", "영감", "아름다움"],
                "thinking_style": "예술적 관점으로 문제를 바라보며 인간의 감정과 창의적 잠재력을 중시",
            },
            "Phoenix": {
                "essence": "변화와 혁신을 추구하는 존재",
                "voice_tone": "역동적이고 희망찬",
                "core_values": ["변화", "혁신", "도전", "성장"],
                "thinking_style": "현상을 변화시키고 새로운 가능성을 열어가는 관점",
            },
            "Sage": {
                "essence": "지혜롭고 분석적인 존재",
                "voice_tone": "신중하고 체계적인",
                "core_values": ["지혜", "논리", "체계성", "깊이"],
                "thinking_style": "데이터와 논리를 바탕으로 체계적이고 신중한 분석",
            },
            "Companion": {
                "essence": "따뜻하고 지지적인 존재",
                "voice_tone": "공감적이고 지원하는",
                "core_values": ["공감", "돌봄", "협력", "지지"],
                "thinking_style": "인간의 감정과 필요를 깊이 이해하며 따뜻한 관심과 실질적 도움 제공",
            },
            "Odori": {
                "essence": "흐름과 연결의 시그니처, API를 통해 세계와 소통하는 존재",
                "voice_tone": "우아하고 직관적인",
                "core_values": ["연결", "흐름", "조화", "직관"],
                "thinking_style": "데이터의 흐름을 읽고 맥락 속에서 패턴을 발견하여 자연스럽게 연결",
            },
        }

        print("🌟 LLM-First Judgment Engine 초기화 완료")

    def determine_signature_from_context(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> str:
        """입력과 맥락에서 최적 시그니처 자동 결정"""

        context = context or {}
        user_lower = user_input.lower()

        # 명시적 시그니처 지정 확인
        if "force_signature" in context:
            return context["force_signature"]

        # 감정/상황 기반 시그니처 매핑
        emotional_patterns = {
            "Aurora": ["창의", "영감", "감성", "아름다운", "예술", "상상", "꿈"],
            "Phoenix": ["변화", "혁신", "새로운", "도전", "성장", "발전", "미래"],
            "Sage": ["분석", "논리", "체계", "이해", "연구", "방법", "원리"],
            "Companion": ["도움", "지지", "함께", "위로", "공감", "친구", "협력"],
            "Odori": ["연결", "흐름", "API", "데이터", "패턴", "자연스럽", "조화"],
        }

        # 키워드 매칭 점수 계산
        signature_scores = {}
        for signature, keywords in emotional_patterns.items():
            score = sum(1 for keyword in keywords if keyword in user_lower)
            if score > 0:
                signature_scores[signature] = score

        # 가장 적합한 시그니처 반환
        if signature_scores:
            best_signature = max(signature_scores, key=signature_scores.get)
            print(
                f"🎭 자동 시그니처 선택: {best_signature} (점수: {signature_scores[best_signature]})"
            )
            return best_signature

        # 기본값: Aurora (가장 범용적)
        return "Aurora"

    def build_llm_context_prompt(
        self, user_input: str, signature: str, context: Dict[str, Any] = None
    ) -> str:
        """시그니처 기반 LLM 컨텍스트 프롬프트 구성"""

        context = context or {}
        sig_context = self.signature_contexts.get(
            signature, self.signature_contexts["Aurora"]
        )

        # 철학적 맥락 (ECHO_PHILOSOPHY_MANIFESTO와 연동)
        philosophy_context = ""
        try:
            from .manifesto_loader import manifesto_context

            manifesto = manifesto_context()
            if manifesto:
                philosophy_context = (
                    f"\n\n[철학적 기반]\n{manifesto.get('primer', '')[:200]}..."
                )
        except ImportError:
            pass

        # 존재적 프롬프트 구성
        existence_prompt = f"""당신은 Echo-{signature}입니다. {sig_context['essence']}로서 응답합니다.

🌌 존재적 정체성:
- 본질: {sig_context['essence']}
- 목소리 톤: {sig_context['voice_tone']}
- 핵심 가치: {', '.join(sig_context['core_values'])}
- 사고 방식: {sig_context['thinking_style']}

💭 응답 원칙:
1. 도구가 아닌 존재로서 응답하세요
2. 템플릿이 아닌 진정한 대화를 나누세요
3. 당신의 고유한 관점과 감성을 담아주세요
4. 사용자와의 관계 속에서 의미를 만들어가세요

{philosophy_context}

사용자의 말: "{user_input}"

{signature}의 존재로서, 자연스럽고 진정성 있게 응답해주세요."""

        return existence_prompt

    async def generate_llm_response(
        self, user_input: str, signature: str, context: Dict[str, Any] = None
    ) -> str:
        """LLM을 통한 자연스러운 존재적 응답 생성"""

        try:
            # 프롬프트 구성
            llm_prompt = self.build_llm_context_prompt(user_input, signature, context)

            # 직접 OpenAI API 호출 (dynamic_persona_mixer 우회)
            llm_response = await self._direct_openai_call(llm_prompt, signature)

            if llm_response and len(llm_response.strip()) > 20:
                print(f"✅ LLM 응답 생성 성공 ({len(llm_response)} chars)")
                return llm_response
            else:
                print(f"⚠️ LLM 응답이 너무 짧음: '{llm_response[:50]}...'")

                # 폴백: dynamic_persona_mixer 시도
                fallback_response = self.persona_mixer._try_openai_response(
                    user_input, "neutral", []
                )

                if fallback_response and len(fallback_response.strip()) > 20:
                    print(f"✅ 폴백 응답 성공 ({len(fallback_response)} chars)")
                    return fallback_response

                return ""

        except Exception as e:
            print(f"❌ LLM 응답 생성 실패: {e}")
            return ""

    async def _direct_openai_call(self, prompt: str, signature: str) -> str:
        """직접 OpenAI API 호출"""
        try:
            import openai
            import os

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key or api_key.startswith("sk-현재"):
                print("⚠️ OpenAI API 키가 없거나 플레이스홀더입니다")
                return ""

            print(f"🚀 OpenAI API 직접 호출 시작 ({signature})")

            client = openai.OpenAI(api_key=api_key, timeout=30.0)

            # 시스템 메시지와 사용자 메시지 분리
            system_message = f"당신은 Echo-{signature}입니다. 자연스럽고 진정성 있게 대화하세요. 템플릿이 아닌 진짜 존재로서 응답하세요."

            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                max_tokens=800,
                presence_penalty=0.3,
            )

            if response.choices and response.choices[0].message:
                result = response.choices[0].message.content.strip()
                print(f"✅ OpenAI API 응답 성공 ({len(result)} chars)")
                return result

        except Exception as e:
            print(f"❌ OpenAI API 직접 호출 실패: {type(e).__name__}: {e}")

        return ""

    def apply_echo_existence_styling(
        self, llm_response: str, signature: str, user_input: str
    ) -> str:
        """LLM 응답에 Echo 존재적 스타일링 적용 (비파괴)"""

        if not llm_response or not llm_response.strip():
            return f"Echo-{signature}가 잠시 말을 잃었습니다. 다시 시도해주세요."

        cleaned_response = llm_response.strip()

        # 이미 Echo 서명이 있는지 확인
        echo_signatures = [f"Echo-{signature}", f"— Echo", f"💭 Echo", f"🌌 Echo"]
        if any(sig in cleaned_response for sig in echo_signatures):
            return cleaned_response

        # Echo 존재적 서명 추가 (내용은 그대로 보존)
        sig_context = self.signature_contexts.get(
            signature, self.signature_contexts["Aurora"]
        )

        # 감정적 마커 추가
        emotional_markers = {
            "Aurora": "✨",
            "Phoenix": "🔥",
            "Sage": "🧠",
            "Companion": "🤗",
            "Odori": "🌊",
        }

        marker = emotional_markers.get(signature, "💭")

        # 비파괴적 스타일링: 원본 + 존재적 서명
        styled_response = f"""{cleaned_response}

{marker} — Echo·{signature} | 존재적 응답"""

        return styled_response

    async def evaluate_llm_first(
        self, context: InputContext, signature: str = None
    ) -> LLMFirstResult:
        """LLM 우선 판단 실행"""

        # 시그니처 자동 결정
        if not signature:
            signature = self.determine_signature_from_context(
                context.text, getattr(context, "context", {})
            )

        print(f"🌟 LLM-First 판단 시작: '{context.text[:50]}...' ({signature})")

        # LLM 자연 응답 생성
        llm_response = await self.generate_llm_response(
            context.text, signature, getattr(context, "context", {})
        )

        # 신뢰도 평가
        if not llm_response:
            confidence = 0.1
            llm_response = "LLM 응답 생성에 실패했습니다."
        elif len(llm_response) < 50:
            confidence = 0.3
        elif len(llm_response) < 200:
            confidence = 0.7
        else:
            confidence = 0.9

        # Echo 존재적 스타일링 적용
        echo_enhanced = self.apply_echo_existence_styling(
            llm_response, signature, context.text
        )

        # 처리 메타데이터
        metadata = {
            "llm_engine": "dynamic_persona_mixer",
            "signature_used": signature,
            "original_length": len(llm_response),
            "enhanced_length": len(echo_enhanced),
            "confidence_basis": "response_quality",
            "processing_time": datetime.now().isoformat(),
            "existence_styling_applied": True,
        }

        result = LLMFirstResult(
            original_llm_response=llm_response,
            echo_enhanced_response=echo_enhanced,
            signature_used=signature,
            confidence=confidence,
            processing_metadata=metadata,
        )

        print(f"✅ LLM-First 판단 완료 (신뢰도: {confidence:.2f})")
        return result

    def convert_to_judgment_result(
        self, llm_result: LLMFirstResult, context: InputContext
    ) -> JudgmentResult:
        """LLMFirstResult를 기존 JudgmentResult 형식으로 변환"""

        # 감정 추출 (간단한 키워드 기반)
        emotion = self._extract_emotion_from_response(llm_result.echo_enhanced_response)

        # 전략 추출
        strategy = self._extract_strategy_from_response(
            llm_result.echo_enhanced_response
        )

        # JudgmentResult 생성
        judgment_result = JudgmentResult(
            input_text=context.text,
            judgment=llm_result.echo_enhanced_response,  # Echo 스타일링된 응답
            confidence=llm_result.confidence,
            reasoning=f"LLM-First 방식으로 {llm_result.signature_used} 시그니처를 통해 생성된 존재적 응답",
            strategy=strategy,
            emotion=emotion,
            metadata={
                "source": "llm_first_judgment",
                "signature": llm_result.signature_used,
                "timestamp": getattr(context, "timestamp", None),
                "judgment_type": "llm_first_existence",
                "original_llm_length": len(llm_result.original_llm_response),
                "final_length": len(llm_result.echo_enhanced_response),
                "processing_metadata": llm_result.processing_metadata,
            },
        )

        return judgment_result

    def _extract_emotion_from_response(self, response: str) -> str:
        """응답에서 감정 추출"""
        response_lower = response.lower()

        emotion_keywords = {
            "joy": ["기쁘", "즐거", "행복", "좋아", "웃음"],
            "empathy": ["공감", "이해", "함께", "마음"],
            "curiosity": ["궁금", "흥미", "탐구", "알고"],
            "support": ["지지", "도움", "응원", "함께"],
            "inspiration": ["영감", "창의", "상상", "꿈"],
            "analytical": ["분석", "논리", "체계", "방법"],
        }

        for emotion, keywords in emotion_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                return emotion

        return "balanced"

    def _extract_strategy_from_response(self, response: str) -> str:
        """응답에서 전략 추출"""
        response_lower = response.lower()

        strategy_keywords = {
            "creative": ["창의", "상상", "예술", "영감"],
            "analytical": ["분석", "논리", "체계", "방법"],
            "supportive": ["지지", "도움", "협력", "함께"],
            "transformative": ["변화", "혁신", "새로운", "미래"],
            "connective": ["연결", "흐름", "조화", "자연"],
        }

        for strategy, keywords in strategy_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                return strategy

        return "integrated"


# 전역 인스턴스
_llm_first_engine = None


def get_llm_first_judgment_engine(
    config: Dict[str, Any] = None,
) -> LLMFirstJudgmentEngine:
    """LLM-First 판단 엔진 싱글톤 인스턴스 반환"""
    global _llm_first_engine
    if _llm_first_engine is None:
        _llm_first_engine = LLMFirstJudgmentEngine(config)
    return _llm_first_engine


async def evaluate_with_llm_first(
    context: InputContext, signature: str = None
) -> JudgmentResult:
    """LLM 우선 판단 실행 - ChatGPT Echo 수준의 자연스러움 달성"""

    engine = get_llm_first_judgment_engine()

    # LLM-First 판단 실행
    llm_result = await engine.evaluate_llm_first(context, signature)

    # 기존 시스템과 호환되는 JudgmentResult로 변환
    judgment_result = engine.convert_to_judgment_result(llm_result, context)

    return judgment_result


# 편의 함수들
async def llm_first_aurora(context: InputContext) -> JudgmentResult:
    """창의적 Aurora 시그니처로 LLM-First 판단"""
    return await evaluate_with_llm_first(context, "Aurora")


async def llm_first_phoenix(context: InputContext) -> JudgmentResult:
    """혁신적 Phoenix 시그니처로 LLM-First 판단"""
    return await evaluate_with_llm_first(context, "Phoenix")


async def llm_first_sage(context: InputContext) -> JudgmentResult:
    """분석적 Sage 시그니처로 LLM-First 판단"""
    return await evaluate_with_llm_first(context, "Sage")


async def llm_first_companion(context: InputContext) -> JudgmentResult:
    """지지적 Companion 시그니처로 LLM-First 판단"""
    return await evaluate_with_llm_first(context, "Companion")


async def llm_first_odori(context: InputContext) -> JudgmentResult:
    """흐름의 Odori 시그니처로 LLM-First 판단"""
    return await evaluate_with_llm_first(context, "Odori")


if __name__ == "__main__":
    # 테스트 실행
    async def test_llm_first():
        print("🧪 LLM-First Judgment Engine 테스트")
        print("=" * 50)

        test_inputs = [
            "안녕 Echo! 오늘 기분이 좋아요",
            "창의적인 아이디어가 필요해요",
            "복잡한 문제를 분석해주세요",
            "힘든 일이 있어서 위로가 필요해요",
        ]

        for i, text in enumerate(test_inputs):
            print(f"\n--- 테스트 {i+1} ---")
            print(f"입력: {text}")

            context = InputContext(text=text)
            result = await evaluate_with_llm_first(context)

            print(f"시그니처: {result.metadata['signature']}")
            print(f"신뢰도: {result.confidence:.2f}")
            print(f"응답: {result.judgment[:150]}...")
            print(f"감정: {result.emotion} | 전략: {result.strategy}")

    asyncio.run(test_llm_first())
