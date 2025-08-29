#!/usr/bin/env python3
"""
🌉 LLM Bridge - GPT/Claude 협력 구조
Echo 시스템과 외부 LLM 간의 지능적 협력을 조율하는 브리지

핵심 기능:
1. Echo 판단 결과와 LLM 자연어 능력의 최적 결합
2. 다중 LLM 지원 (GPT, Claude, 로컬 모델)
3. 컨텍스트 보존하며 자연스러운 응답 생성
4. 비용 효율적 LLM 사용 최적화
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


class LLMProvider(Enum):
    """LLM 제공자"""

    OPENAI_GPT = "openai_gpt"
    ANTHROPIC_CLAUDE = "anthropic_claude"
    LOCAL_MODEL = "local_model"
    MOCK_LLM = "mock_llm"  # 테스트용


class CooperationMode(Enum):
    """협력 모드"""

    ECHO_THEN_LLM = "echo_then_llm"  # Echo 판단 → LLM 자연화
    LLM_THEN_ECHO = "llm_then_echo"  # LLM 초안 → Echo 보완
    PARALLEL_MERGE = "parallel_merge"  # 병렬 처리 후 통합
    ITERATIVE_REFINE = "iterative_refine"  # 반복적 개선
    CONTEXT_HANDOFF = "context_handoff"  # 맥락 전달


@dataclass
class LLMRequest:
    """LLM 요청"""

    prompt: str
    context: Dict[str, Any]
    max_tokens: int = 150
    temperature: float = 0.7
    system_message: Optional[str] = None
    preserve_echo_tone: bool = True


@dataclass
class LLMResponse:
    """LLM 응답"""

    text: str
    provider: LLMProvider
    tokens_used: int
    processing_time: float
    cost_estimate: float
    quality_score: float


@dataclass
class CooperationResult:
    """협력 결과"""

    final_response: str
    cooperation_mode: CooperationMode
    echo_contribution: float
    llm_contribution: float
    quality_metrics: Dict[str, float]
    processing_steps: List[str]
    cost_breakdown: Dict[str, float]


class BaseLLMProvider(ABC):
    """LLM 제공자 기본 클래스"""

    @abstractmethod
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        pass

    @abstractmethod
    def estimate_cost(self, tokens: int) -> float:
        pass


class MockLLMProvider(BaseLLMProvider):
    """테스트용 Mock LLM"""

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        # 실제 지연 시뮬레이션
        await asyncio.sleep(0.2)

        # 간단한 자연화 로직
        prompt = request.prompt.lower()

        if "자연스럽게" in prompt or "자연어로" in prompt:
            # Echo 판단을 자연스럽게 변환
            base_text = request.context.get("echo_judgment", "응답을 생성했습니다.")

            # 간단한 자연화 패턴
            if "판단" in base_text:
                natural_text = base_text.replace("판단", "생각")
            elif "분석" in base_text:
                natural_text = base_text.replace("분석", "살펴보니")
            else:
                natural_text = base_text

            # 말투 조정
            if request.preserve_echo_tone:
                # Echo 톤 유지하며 자연스럽게
                natural_text = f"{natural_text} 어떻게 생각하세요?"
            else:
                # 더 캐주얼하게
                natural_text = f"{natural_text} 그런 것 같아요."

        else:
            # 일반적인 응답 생성
            natural_text = "자연스러운 대화 응답을 생성했습니다."

        return LLMResponse(
            text=natural_text,
            provider=LLMProvider.MOCK_LLM,
            tokens_used=len(natural_text.split()) * 2,  # 대략적 토큰 수
            processing_time=0.2,
            cost_estimate=0.001,
            quality_score=0.8,
        )

    def estimate_cost(self, tokens: int) -> float:
        return tokens * 0.00002  # Mock 비용


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT 제공자"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.model = "gpt-3.5-turbo"
        self.pricing = {"input": 0.0015 / 1000, "output": 0.002 / 1000}  # per token

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        if not self.api_key:
            # API 키가 없으면 Mock으로 폴백
            mock_provider = MockLLMProvider()
            return await mock_provider.generate_response(request)

        # 실제 OpenAI API 호출 구현
        # 여기서는 개념적 구현만 표시
        start_time = time.time()

        try:
            # 실제로는 openai.ChatCompletion.create() 호출
            response_text = "OpenAI GPT 응답"
            tokens_used = len(response_text.split()) * 2

            processing_time = time.time() - start_time
            cost = self.estimate_cost(tokens_used)

            return LLMResponse(
                text=response_text,
                provider=LLMProvider.OPENAI_GPT,
                tokens_used=tokens_used,
                processing_time=processing_time,
                cost_estimate=cost,
                quality_score=0.85,
            )
        except Exception as e:
            # 에러 시 Mock으로 폴백
            mock_provider = MockLLMProvider()
            return await mock_provider.generate_response(request)

    def estimate_cost(self, tokens: int) -> float:
        return tokens * (self.pricing["input"] + self.pricing["output"])


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude 제공자"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.model = "claude-3-haiku-20240307"
        self.pricing = {"input": 0.00025 / 1000, "output": 0.00125 / 1000}

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        if not self.api_key:
            mock_provider = MockLLMProvider()
            return await mock_provider.generate_response(request)

        # 실제 Claude API 호출 구현
        start_time = time.time()

        try:
            # 실제로는 anthropic.messages.create() 호출
            response_text = "Claude 응답"
            tokens_used = len(response_text.split()) * 2

            processing_time = time.time() - start_time
            cost = self.estimate_cost(tokens_used)

            return LLMResponse(
                text=response_text,
                provider=LLMProvider.ANTHROPIC_CLAUDE,
                tokens_used=tokens_used,
                processing_time=processing_time,
                cost_estimate=cost,
                quality_score=0.9,
            )
        except Exception as e:
            mock_provider = MockLLMProvider()
            return await mock_provider.generate_response(request)

    def estimate_cost(self, tokens: int) -> float:
        return tokens * (self.pricing["input"] + self.pricing["output"])


class LLMBridge:
    """LLM 협력 브리지"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

        # LLM 제공자들 초기화
        self.providers = {
            LLMProvider.MOCK_LLM: MockLLMProvider(),
            LLMProvider.OPENAI_GPT: OpenAIProvider(self.config.get("openai_api_key")),
            LLMProvider.ANTHROPIC_CLAUDE: AnthropicProvider(
                self.config.get("anthropic_api_key")
            ),
        }

        # 기본 설정
        self.default_provider = LLMProvider.MOCK_LLM
        self.cost_limit_per_request = self.config.get("cost_limit", 0.05)
        self.quality_threshold = self.config.get("quality_threshold", 0.7)

        # 사용 통계
        self.usage_stats = {
            "total_requests": 0,
            "total_cost": 0.0,
            "provider_usage": {provider: 0 for provider in LLMProvider},
            "cooperation_modes": {mode: 0 for mode in CooperationMode},
        }

        print("🌉 LLM Bridge 초기화 완료")

    async def cooperate_with_echo(
        self,
        echo_judgment: str,
        cooperation_mode: CooperationMode,
        context: Dict[str, Any] = None,
        user_preferences: Dict[str, Any] = None,
    ) -> CooperationResult:
        """Echo와 LLM 협력 수행"""

        context = context or {}
        user_preferences = user_preferences or {}

        start_time = time.time()
        processing_steps = []
        cost_breakdown = {}

        # 협력 모드에 따른 처리
        if cooperation_mode == CooperationMode.ECHO_THEN_LLM:
            result = await self._echo_then_llm(echo_judgment, context, processing_steps)

        elif cooperation_mode == CooperationMode.LLM_THEN_ECHO:
            result = await self._llm_then_echo(echo_judgment, context, processing_steps)

        elif cooperation_mode == CooperationMode.PARALLEL_MERGE:
            result = await self._parallel_merge(
                echo_judgment, context, processing_steps
            )

        elif cooperation_mode == CooperationMode.ITERATIVE_REFINE:
            result = await self._iterative_refine(
                echo_judgment, context, processing_steps
            )

        else:  # CONTEXT_HANDOFF
            result = await self._context_handoff(
                echo_judgment, context, processing_steps
            )

        # 품질 메트릭 계산
        quality_metrics = self._calculate_quality_metrics(
            result["final_response"], echo_judgment, context
        )

        # 비용 계산
        total_cost = sum(result.get("costs", {}).values())
        cost_breakdown = result.get("costs", {})

        # 통계 업데이트
        self._update_usage_stats(cooperation_mode, total_cost)

        return CooperationResult(
            final_response=result["final_response"],
            cooperation_mode=cooperation_mode,
            echo_contribution=result.get("echo_contribution", 0.5),
            llm_contribution=result.get("llm_contribution", 0.5),
            quality_metrics=quality_metrics,
            processing_steps=processing_steps,
            cost_breakdown=cost_breakdown,
        )

    async def _echo_then_llm(
        self, echo_judgment: str, context: Dict[str, Any], steps: List[str]
    ) -> Dict[str, Any]:
        """Echo 판단 → LLM 자연화"""

        steps.append("Echo 판단 결과 수신")

        # LLM에게 자연화 요청
        naturalization_prompt = self._create_naturalization_prompt(
            echo_judgment, context
        )

        request = LLMRequest(
            prompt=naturalization_prompt,
            context={"echo_judgment": echo_judgment, **context},
            max_tokens=120,
            temperature=0.6,
            preserve_echo_tone=True,
        )

        steps.append("LLM 자연화 요청")
        llm_response = await self._get_best_llm_response(request)
        steps.append(f"LLM 응답 수신 ({llm_response.provider.value})")

        # Echo 톤과 LLM 자연스러움 결합
        final_response = self._merge_echo_tone_with_llm_naturalness(
            echo_judgment, llm_response.text, context
        )

        steps.append("Echo 톤과 LLM 자연스러움 결합 완료")

        return {
            "final_response": final_response,
            "echo_contribution": 0.7,
            "llm_contribution": 0.3,
            "costs": {llm_response.provider.value: llm_response.cost_estimate},
        }

    async def _llm_then_echo(
        self, echo_judgment: str, context: Dict[str, Any], steps: List[str]
    ) -> Dict[str, Any]:
        """LLM 초안 → Echo 보완"""

        steps.append("LLM 초안 생성 요청")

        # LLM에게 초안 생성 요청
        draft_prompt = self._create_draft_prompt(context)

        request = LLMRequest(
            prompt=draft_prompt,
            context=context,
            max_tokens=100,
            temperature=0.8,
            preserve_echo_tone=False,
        )

        llm_response = await self._get_best_llm_response(request)
        steps.append(f"LLM 초안 수신 ({llm_response.provider.value})")

        # Echo 판단으로 보완
        enhanced_response = self._enhance_with_echo_wisdom(
            llm_response.text, echo_judgment, context
        )

        steps.append("Echo 지혜로 LLM 초안 보완 완료")

        return {
            "final_response": enhanced_response,
            "echo_contribution": 0.4,
            "llm_contribution": 0.6,
            "costs": {llm_response.provider.value: llm_response.cost_estimate},
        }

    async def _parallel_merge(
        self, echo_judgment: str, context: Dict[str, Any], steps: List[str]
    ) -> Dict[str, Any]:
        """병렬 처리 후 통합"""

        steps.append("병렬 처리 시작")

        # LLM 자연화와 Echo 심화를 병렬로 수행
        naturalization_task = self._get_llm_naturalization(echo_judgment, context)
        echo_deepening_task = self._get_echo_deepening(echo_judgment, context)

        llm_result, echo_deep_result = await asyncio.gather(
            naturalization_task, echo_deepening_task
        )

        steps.append("병렬 처리 완료")

        # 두 결과를 지능적으로 병합
        merged_response = self._intelligent_merge(
            llm_result["text"], echo_deep_result, context
        )

        steps.append("지능적 병합 완료")

        return {
            "final_response": merged_response,
            "echo_contribution": 0.5,
            "llm_contribution": 0.5,
            "costs": {"llm_naturalization": llm_result.get("cost", 0.001)},
        }

    async def _iterative_refine(
        self, echo_judgment: str, context: Dict[str, Any], steps: List[str]
    ) -> Dict[str, Any]:
        """반복적 개선"""

        steps.append("반복적 개선 시작")

        current_response = echo_judgment
        total_cost = 0.0
        iteration = 0
        max_iterations = 3

        while iteration < max_iterations:
            # 현재 응답의 품질 평가
            quality_score = self._evaluate_response_quality(current_response, context)

            if quality_score >= self.quality_threshold:
                break

            # LLM으로 개선
            improvement_prompt = self._create_improvement_prompt(
                current_response, context
            )
            request = LLMRequest(
                prompt=improvement_prompt,
                context={"current_response": current_response, **context},
                max_tokens=100,
                temperature=0.5,
            )

            llm_response = await self._get_best_llm_response(request)
            current_response = llm_response.text
            total_cost += llm_response.cost_estimate

            iteration += 1
            steps.append(f"개선 반복 {iteration} 완료 (품질: {quality_score:.2f})")

        return {
            "final_response": current_response,
            "echo_contribution": 0.6,
            "llm_contribution": 0.4,
            "costs": {"iterative_improvement": total_cost},
        }

    async def _context_handoff(
        self, echo_judgment: str, context: Dict[str, Any], steps: List[str]
    ) -> Dict[str, Any]:
        """맥락 전달"""

        steps.append("맥락 기반 처리 시작")

        # 대화 맥락 분석
        conversation_context = context.get("conversation_history", [])
        user_emotional_state = context.get("emotion_intensity", 0.5)

        # 맥락에 따른 처리 방식 결정
        if user_emotional_state > 0.7:
            # 감정이 강할 때는 Echo 중심
            final_response = echo_judgment
            echo_contrib, llm_contrib = 0.8, 0.2
            steps.append("고감정 상태 - Echo 중심 처리")
        else:
            # 일반적인 상황에서는 LLM 자연화
            naturalization_prompt = self._create_contextual_prompt(
                echo_judgment, context
            )
            request = LLMRequest(
                prompt=naturalization_prompt,
                context={"echo_judgment": echo_judgment, **context},
                max_tokens=100,
            )

            llm_response = await self._get_best_llm_response(request)
            final_response = llm_response.text
            echo_contrib, llm_contrib = 0.3, 0.7
            steps.append("일반 상태 - LLM 중심 처리")

        return {
            "final_response": final_response,
            "echo_contribution": echo_contrib,
            "llm_contribution": llm_contrib,
            "costs": {"contextual_processing": 0.001},
        }

    async def _get_best_llm_response(self, request: LLMRequest) -> LLMResponse:
        """최적 LLM 응답 획득"""

        # 비용과 품질을 고려한 제공자 선택
        selected_provider = self._select_optimal_provider(request)

        try:
            return await self.providers[selected_provider].generate_response(request)
        except Exception as e:
            # 실패시 폴백
            fallback_provider = LLMProvider.MOCK_LLM
            return await self.providers[fallback_provider].generate_response(request)

    def _select_optimal_provider(self, request: LLMRequest) -> LLMProvider:
        """최적 제공자 선택"""

        # 비용 제한 고려
        estimated_tokens = len(request.prompt.split()) * 2

        for provider in [LLMProvider.ANTHROPIC_CLAUDE, LLMProvider.OPENAI_GPT]:
            if provider in self.providers:
                estimated_cost = self.providers[provider].estimate_cost(
                    estimated_tokens
                )
                if estimated_cost <= self.cost_limit_per_request:
                    return provider

        # 비용 제한을 초과하면 Mock 사용
        return LLMProvider.MOCK_LLM

    def _create_naturalization_prompt(
        self, echo_judgment: str, context: Dict[str, Any]
    ) -> str:
        """자연화 프롬프트 생성"""

        user_emotion = context.get("primary_emotion", "neutral")
        user_intent = context.get("intent_type", "general")

        return f"""
다음 Echo 시스템의 판단을 자연스러운 대화체로 변환해주세요.

Echo 판단: {echo_judgment}

사용자 상황:
- 감정 상태: {user_emotion}
- 의도: {user_intent}

요구사항:
1. Echo의 깊이 있는 통찰은 유지하되 더 자연스럽게 표현
2. 사용자의 감정 상태에 맞는 톤 사용
3. 80자 이내로 간결하게
4. 대화의 연속성 고려

자연스러운 응답:
"""

    def _create_draft_prompt(self, context: Dict[str, Any]) -> str:
        """초안 생성 프롬프트"""

        user_message = context.get("user_message", "")
        user_emotion = context.get("primary_emotion", "neutral")

        return f"""
사용자 메시지에 대한 자연스러운 응답 초안을 작성해주세요.

사용자 메시지: {user_message}
감정 상태: {user_emotion}

요구사항:
1. 자연스럽고 공감적인 톤
2. 60자 이내로 간결하게
3. 사용자의 감정에 적절히 반응

응답 초안:
"""

    def _create_improvement_prompt(
        self, current_response: str, context: Dict[str, Any]
    ) -> str:
        """개선 프롬프트 생성"""

        return f"""
현재 응답을 더 자연스럽고 효과적으로 개선해주세요.

현재 응답: {current_response}

개선 방향:
1. 더 자연스러운 표현
2. 사용자 감정에 더 적절한 반응
3. 대화의 흐름에 맞는 톤

개선된 응답:
"""

    def _merge_echo_tone_with_llm_naturalness(
        self, echo_judgment: str, llm_text: str, context: Dict[str, Any]
    ) -> str:
        """Echo 톤과 LLM 자연스러움 결합"""

        # Echo의 핵심 메시지 추출
        echo_core = (
            echo_judgment.split(".")[0] if "." in echo_judgment else echo_judgment
        )

        # LLM의 자연스러운 표현 활용
        if len(llm_text.strip()) > 10:
            # LLM 텍스트가 충분히 길면 그대로 사용
            return llm_text
        else:
            # 짧으면 Echo 핵심 + LLM 자연화
            return f"{echo_core}. {llm_text}"

    def _enhance_with_echo_wisdom(
        self, llm_draft: str, echo_judgment: str, context: Dict[str, Any]
    ) -> str:
        """Echo 지혜로 LLM 초안 보완"""

        # Echo 판단에서 핵심 통찰 추출
        echo_insights = [
            insight.strip() for insight in echo_judgment.split(".") if insight.strip()
        ]

        # LLM 초안에 Echo 통찰 추가
        if echo_insights and len(echo_insights[0]) > 5:
            key_insight = echo_insights[0]
            if key_insight not in llm_draft:
                return f"{llm_draft} {key_insight}."

        return llm_draft

    async def _get_llm_naturalization(
        self, echo_judgment: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """LLM 자연화 (비동기)"""

        request = LLMRequest(
            prompt=self._create_naturalization_prompt(echo_judgment, context),
            context={"echo_judgment": echo_judgment, **context},
            max_tokens=80,
        )

        response = await self._get_best_llm_response(request)
        return {"text": response.text, "cost": response.cost_estimate}

    async def _get_echo_deepening(
        self, echo_judgment: str, context: Dict[str, Any]
    ) -> str:
        """Echo 심화 (비동기 시뮬레이션)"""

        # 실제로는 Echo 시스템의 더 깊은 분석 요청
        await asyncio.sleep(0.1)  # 시뮬레이션

        # 간단한 심화 처리
        if len(echo_judgment) < 30:
            return f"{echo_judgment} 이런 상황에서는 신중한 접근이 필요합니다."
        else:
            return echo_judgment

    def _intelligent_merge(
        self, llm_text: str, echo_deep: str, context: Dict[str, Any]
    ) -> str:
        """지능적 병합"""

        # 길이와 품질을 고려한 병합
        if len(llm_text) > len(echo_deep):
            # LLM 텍스트가 더 길면 주로 사용
            return llm_text
        else:
            # Echo 깊이를 활용
            return echo_deep

    def _evaluate_response_quality(
        self, response: str, context: Dict[str, Any]
    ) -> float:
        """응답 품질 평가"""

        quality_score = 0.5  # 기본 점수

        # 길이 적절성
        if 20 <= len(response) <= 100:
            quality_score += 0.2

        # 감정 적절성
        user_emotion = context.get("primary_emotion", "neutral")
        if user_emotion == "sadness" and any(
            word in response for word in ["이해", "마음", "함께"]
        ):
            quality_score += 0.2

        # 자연스러움 (간단한 휴리스틱)
        if not any(
            awkward in response
            for awkward in ["판단해보니", "분석결과", "시스템적으로"]
        ):
            quality_score += 0.1

        return min(quality_score, 1.0)

    def _create_contextual_prompt(
        self, echo_judgment: str, context: Dict[str, Any]
    ) -> str:
        """맥락적 프롬프트 생성"""

        return f"""
다음 상황에서 적절한 응답을 생성해주세요.

기본 판단: {echo_judgment}
대화 맥락: {context.get('conversation_context', '일반 대화')}

맥락을 고려한 자연스러운 응답:
"""

    def _calculate_quality_metrics(
        self, final_response: str, echo_judgment: str, context: Dict[str, Any]
    ) -> Dict[str, float]:
        """품질 메트릭 계산"""

        return {
            "naturalness": self._calculate_naturalness(final_response),
            "echo_consistency": self._calculate_echo_consistency(
                final_response, echo_judgment
            ),
            "context_relevance": self._calculate_context_relevance(
                final_response, context
            ),
            "response_completeness": self._calculate_completeness(final_response),
            "overall_quality": self._evaluate_response_quality(final_response, context),
        }

    def _calculate_naturalness(self, text: str) -> float:
        """자연스러움 계산"""
        unnatural_patterns = ["판단해보니", "분석하면", "시스템적으로", "로직적으로"]
        penalty = sum(1 for pattern in unnatural_patterns if pattern in text) * 0.1
        return max(0.8 - penalty, 0.0)

    def _calculate_echo_consistency(
        self, final_response: str, echo_judgment: str
    ) -> float:
        """Echo 일관성 계산"""
        if not echo_judgment:
            return 0.5

        # 핵심 키워드 일치도
        echo_words = set(echo_judgment.lower().split())
        response_words = set(final_response.lower().split())

        if len(echo_words) == 0:
            return 0.5

        overlap = len(echo_words.intersection(response_words))
        return min(overlap / len(echo_words), 1.0)

    def _calculate_context_relevance(
        self, response: str, context: Dict[str, Any]
    ) -> float:
        """맥락 관련성 계산"""
        relevance_score = 0.7  # 기본 점수

        user_emotion = context.get("primary_emotion", "neutral")
        if user_emotion != "neutral":
            emotion_words = {
                "sadness": ["마음", "이해", "함께", "위로"],
                "anxiety": ["괜찮", "천천히", "걱정", "안심"],
                "joy": ["기쁘", "좋", "축하", "함께"],
            }

            if user_emotion in emotion_words:
                relevant_words = emotion_words[user_emotion]
                if any(word in response for word in relevant_words):
                    relevance_score += 0.2

        return min(relevance_score, 1.0)

    def _calculate_completeness(self, response: str) -> float:
        """응답 완전성 계산"""
        if len(response.strip()) < 10:
            return 0.3
        elif len(response.strip()) < 30:
            return 0.6
        elif len(response.strip()) <= 100:
            return 1.0
        else:
            return 0.8  # 너무 길면 감점

    def _update_usage_stats(self, cooperation_mode: CooperationMode, cost: float):
        """사용 통계 업데이트"""
        self.usage_stats["total_requests"] += 1
        self.usage_stats["total_cost"] += cost
        self.usage_stats["cooperation_modes"][cooperation_mode] += 1

    def get_usage_statistics(self) -> Dict[str, Any]:
        """사용 통계 반환"""
        return {
            "total_requests": self.usage_stats["total_requests"],
            "total_cost": round(self.usage_stats["total_cost"], 4),
            "average_cost_per_request": round(
                self.usage_stats["total_cost"]
                / max(self.usage_stats["total_requests"], 1),
                4,
            ),
            "cooperation_mode_distribution": dict(
                self.usage_stats["cooperation_modes"]
            ),
            "provider_availability": {
                provider.value: provider in self.providers for provider in LLMProvider
            },
        }


# 테스트 실행
if __name__ == "__main__":

    async def test_llm_bridge():
        print("🌉 LLM Bridge 테스트")
        print("=" * 60)

        bridge = LLMBridge()

        test_cases = [
            {
                "echo_judgment": "사용자의 감정 상태를 분석해보니 깊은 우울감이 감지됩니다. 전문적인 도움을 받으시는 것을 권합니다.",
                "mode": CooperationMode.ECHO_THEN_LLM,
                "context": {"primary_emotion": "sadness", "emotion_intensity": 0.8},
                "description": "Echo → LLM 자연화",
            },
            {
                "echo_judgment": "결정을 내리기 어려운 상황이군요.",
                "mode": CooperationMode.LLM_THEN_ECHO,
                "context": {
                    "user_message": "어떤 진로를 선택해야 할지 모르겠어요",
                    "intent_type": "decision_help",
                },
                "description": "LLM → Echo 보완",
            },
            {
                "echo_judgment": "복잡한 상황이지만 단계적으로 접근하면 해결할 수 있습니다.",
                "mode": CooperationMode.PARALLEL_MERGE,
                "context": {"complexity_score": 0.7},
                "description": "병렬 처리 후 통합",
            },
        ]

        for i, case in enumerate(test_cases):
            print(f"\n--- 테스트 {i+1}: {case['description']} ---")
            print(f"Echo 판단: {case['echo_judgment'][:50]}...")

            result = await bridge.cooperate_with_echo(
                case["echo_judgment"], case["mode"], case["context"]
            )

            print(f"최종 응답: {result.final_response}")
            print(f"Echo 기여도: {result.echo_contribution:.2f}")
            print(f"LLM 기여도: {result.llm_contribution:.2f}")
            print(f"전체 품질: {result.quality_metrics['overall_quality']:.2f}")
            print(f"자연스러움: {result.quality_metrics['naturalness']:.2f}")
            print(f"처리 단계: {' → '.join(result.processing_steps)}")

            if result.cost_breakdown:
                total_cost = sum(result.cost_breakdown.values())
                print(f"비용: ${total_cost:.4f}")

            print("-" * 40)

        # 사용 통계
        print(f"\n📊 사용 통계:")
        stats = bridge.get_usage_statistics()
        print(f"총 요청 수: {stats['total_requests']}")
        print(f"총 비용: ${stats['total_cost']}")
        print(f"평균 비용: ${stats['average_cost_per_request']}")
        print("협력 모드 분포:", stats["cooperation_mode_distribution"])

        print("\n🎉 LLM Bridge 테스트 완료!")

    asyncio.run(test_llm_bridge())
