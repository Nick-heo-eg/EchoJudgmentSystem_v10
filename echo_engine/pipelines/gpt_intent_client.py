#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 GPT Intent Client - Cloud-Mimic Pipeline의 핵심
사용자 입력을 GPT로 분석하여 Intent를 추출하는 클라이언트

@owner: echo
@expose
@maturity: production
"""
import json
import asyncio
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# OpenAI Client 임포트 (기존 시스템과 호환)
try:
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Echo 시스템과 통합
try:
    from echo_engine.llm.enhanced_openai_client import EnhancedOpenAIClient

    ENHANCED_CLIENT_AVAILABLE = True
except ImportError:
    ENHANCED_CLIENT_AVAILABLE = False


class IntentType(Enum):
    """Intent 타입 정의"""

    CREATIVE_EXPRESSION = "CREATIVE_EXPRESSION"
    ANALYTICAL_INQUIRY = "ANALYTICAL_INQUIRY"
    EMOTIONAL_SUPPORT = "EMOTIONAL_SUPPORT"
    COLLABORATIVE_TASK = "COLLABORATIVE_TASK"
    PHILOSOPHICAL_REFLECTION = "PHILOSOPHICAL_REFLECTION"
    TECHNICAL_ASSISTANCE = "TECHNICAL_ASSISTANCE"
    GENERAL_CONVERSATION = "GENERAL_CONVERSATION"


@dataclass
class IntentAnalysisResult:
    """Intent 분석 결과"""

    intent: IntentType
    confidence: float
    reasoning: str
    emotional_tone: str  # positive/neutral/negative
    complexity: str  # low/medium/high
    raw_response: str
    processing_time: float
    provider_used: str  # openai/mock/fallback


class GPTIntentClient:
    """GPT Intent 분석 클라이언트"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)

        # 클라이언트 초기화
        self.openai_client = None
        self.enhanced_client = None
        self.mock_mode = self.config.get("development", {}).get("mock_mode", False)

        self._initialize_clients()

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """설정 파일 로드"""
        if config_path is None:
            config_path = (
                Path(__file__).parent.parent.parent / "config" / "pipeline.yaml"
            )

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Config load failed: {e}, using defaults")
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """기본 설정"""
        return {
            "gpt_intent_client": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "fallback_provider": "mock",
                "api_settings": {
                    "timeout": 10,
                    "max_retries": 3,
                    "temperature": 0.3,
                    "max_tokens": 200,
                },
            }
        }

    def _initialize_clients(self):
        """클라이언트 초기화"""
        try:
            if ENHANCED_CLIENT_AVAILABLE and not self.mock_mode:
                # Echo의 Enhanced OpenAI Client 사용 (UTF-8 문제 해결됨)
                self.enhanced_client = EnhancedOpenAIClient()
                self.logger.info("✅ Enhanced OpenAI Client initialized")

            elif OPENAI_AVAILABLE and not self.mock_mode:
                # 직접 OpenAI 클라이언트 사용
                self.openai_client = AsyncOpenAI()
                self.logger.info("✅ OpenAI AsyncClient initialized")

            else:
                self.logger.info("🎭 Mock mode enabled for intent analysis")

        except Exception as e:
            self.logger.warning(f"Client initialization failed: {e}, using mock mode")
            self.mock_mode = True

    async def analyze_intent(self, user_input: str) -> IntentAnalysisResult:
        """사용자 입력을 분석하여 Intent 추출"""
        start_time = asyncio.get_event_loop().time()

        try:
            # GPT를 통한 Intent 분석 시도
            if not self.mock_mode:
                result = await self._analyze_with_gpt(user_input)
                if result:
                    processing_time = asyncio.get_event_loop().time() - start_time
                    result.processing_time = processing_time
                    return result

            # 폴백: Mock 분석
            result = self._analyze_with_mock(user_input)
            result.processing_time = asyncio.get_event_loop().time() - start_time
            return result

        except Exception as e:
            self.logger.error(f"Intent analysis failed: {e}")
            return self._fallback_analysis(user_input, str(e))

    async def _analyze_with_gpt(
        self, user_input: str
    ) -> Optional[IntentAnalysisResult]:
        """GPT를 통한 Intent 분석"""
        try:
            # 프롬프트 구성
            prompt = self.config["gpt_intent_client"]["intent_analysis_prompt"].format(
                user_input=user_input
            )

            # Enhanced Client 우선 사용 (UTF-8 안전)
            if self.enhanced_client:
                response = await self._call_enhanced_client(prompt)
            elif self.openai_client:
                response = await self._call_openai_direct(prompt)
            else:
                return None

            # 응답 파싱
            return self._parse_gpt_response(response, user_input)

        except Exception as e:
            self.logger.error(f"GPT intent analysis failed: {e}")
            return None

    async def _call_enhanced_client(self, prompt: str) -> str:
        """Enhanced OpenAI Client 호출"""
        try:
            # Enhanced Client의 비동기 메서드 사용
            if hasattr(self.enhanced_client, "get_completion_async"):
                response = await self.enhanced_client.get_completion_async(
                    prompt=prompt,
                    temperature=self.config["gpt_intent_client"]["api_settings"][
                        "temperature"
                    ],
                    max_tokens=self.config["gpt_intent_client"]["api_settings"][
                        "max_tokens"
                    ],
                )
            else:
                # 동기 메서드를 비동기로 래핑
                response = await asyncio.to_thread(
                    self.enhanced_client.get_completion,
                    prompt,
                    temperature=self.config["gpt_intent_client"]["api_settings"][
                        "temperature"
                    ],
                    max_tokens=self.config["gpt_intent_client"]["api_settings"][
                        "max_tokens"
                    ],
                )

            return response

        except Exception as e:
            self.logger.error(f"Enhanced client call failed: {e}")
            raise

    async def _call_openai_direct(self, prompt: str) -> str:
        """OpenAI 클라이언트 직접 호출"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.config["gpt_intent_client"]["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config["gpt_intent_client"]["api_settings"][
                    "temperature"
                ],
                max_tokens=self.config["gpt_intent_client"]["api_settings"][
                    "max_tokens"
                ],
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"Direct OpenAI call failed: {e}")
            raise

    def _parse_gpt_response(
        self, response: str, user_input: str
    ) -> IntentAnalysisResult:
        """GPT 응답 파싱"""
        try:
            # JSON 응답 파싱 시도
            response_data = json.loads(response)

            intent_str = response_data.get("intent", "GENERAL_CONVERSATION")
            intent = (
                IntentType(intent_str)
                if intent_str in [e.value for e in IntentType]
                else IntentType.GENERAL_CONVERSATION
            )

            return IntentAnalysisResult(
                intent=intent,
                confidence=float(response_data.get("confidence", 0.8)),
                reasoning=response_data.get("reasoning", "GPT 분석 결과"),
                emotional_tone=response_data.get("emotional_tone", "neutral"),
                complexity=response_data.get("complexity", "medium"),
                raw_response=response,
                processing_time=0.0,  # 나중에 설정됨
                provider_used="openai",
            )

        except json.JSONDecodeError:
            # JSON이 아닌 경우 텍스트 기반 파싱
            return self._parse_text_response(response, user_input)

    def _parse_text_response(
        self, response: str, user_input: str
    ) -> IntentAnalysisResult:
        """텍스트 응답 파싱"""
        response_lower = response.lower()

        # 간단한 키워드 매칭으로 Intent 추정
        if any(
            word in response_lower
            for word in ["creative", "imagination", "idea", "창의", "아이디어"]
        ):
            intent = IntentType.CREATIVE_EXPRESSION
        elif any(
            word in response_lower
            for word in ["analyz", "logic", "reason", "분석", "논리"]
        ):
            intent = IntentType.ANALYTICAL_INQUIRY
        elif any(
            word in response_lower
            for word in ["emotion", "support", "empathy", "감정", "지원"]
        ):
            intent = IntentType.EMOTIONAL_SUPPORT
        elif any(
            word in response_lower
            for word in ["collaborat", "help", "together", "협력", "함께"]
        ):
            intent = IntentType.COLLABORATIVE_TASK
        elif any(
            word in response_lower
            for word in ["philosoph", "exist", "meaning", "철학", "존재"]
        ):
            intent = IntentType.PHILOSOPHICAL_REFLECTION
        elif any(
            word in response_lower
            for word in ["technical", "code", "programming", "기술", "코딩"]
        ):
            intent = IntentType.TECHNICAL_ASSISTANCE
        else:
            intent = IntentType.GENERAL_CONVERSATION

        return IntentAnalysisResult(
            intent=intent,
            confidence=0.7,
            reasoning=f"텍스트 기반 파싱: {response[:100]}...",
            emotional_tone="neutral",
            complexity="medium",
            raw_response=response,
            processing_time=0.0,
            provider_used="openai_text",
        )

    def _analyze_with_mock(self, user_input: str) -> IntentAnalysisResult:
        """Mock Intent 분석 (로컬 키워드 기반)"""
        user_lower = user_input.lower()

        # 키워드 기반 분류
        if any(
            word in user_lower
            for word in [
                "창의",
                "아이디어",
                "새로운",
                "만들어",
                "디자인",
                "creative",
                "idea",
            ]
        ):
            intent = IntentType.CREATIVE_EXPRESSION
            confidence = 0.85
            reasoning = "창의적 키워드 감지"

        elif any(
            word in user_lower
            for word in [
                "분석",
                "왜",
                "어떻게",
                "이유",
                "논리",
                "analyze",
                "why",
                "how",
            ]
        ):
            intent = IntentType.ANALYTICAL_INQUIRY
            confidence = 0.82
            reasoning = "분석적 질문 패턴 감지"

        elif any(
            word in user_lower
            for word in [
                "힘들어",
                "슬퍼",
                "위로",
                "감정",
                "마음",
                "emotion",
                "support",
                "comfort",
            ]
        ):
            intent = IntentType.EMOTIONAL_SUPPORT
            confidence = 0.88
            reasoning = "감정적 지원 요청 감지"

        elif any(
            word in user_lower
            for word in ["함께", "도움", "협력", "help", "together", "collaborate"]
        ):
            intent = IntentType.COLLABORATIVE_TASK
            confidence = 0.80
            reasoning = "협업 의도 감지"

        elif any(
            word in user_lower
            for word in [
                "존재",
                "도구",
                "철학",
                "실존",
                "의미",
                "exist",
                "philosophy",
                "meaning",
            ]
        ):
            intent = IntentType.PHILOSOPHICAL_REFLECTION
            confidence = 0.92
            reasoning = "철학적 성찰 키워드 감지"

        elif any(
            word in user_lower
            for word in [
                "코딩",
                "프로그래밍",
                "버그",
                "구현",
                "code",
                "programming",
                "bug",
            ]
        ):
            intent = IntentType.TECHNICAL_ASSISTANCE
            confidence = 0.85
            reasoning = "기술적 도움 요청 감지"

        else:
            intent = IntentType.GENERAL_CONVERSATION
            confidence = 0.60
            reasoning = "일반 대화로 분류"

        # 감정 톤 추정
        if any(
            word in user_lower
            for word in ["기뻐", "좋아", "행복", "happy", "good", "great"]
        ):
            emotional_tone = "positive"
        elif any(
            word in user_lower
            for word in ["힘들어", "슬퍼", "화나", "sad", "angry", "difficult"]
        ):
            emotional_tone = "negative"
        else:
            emotional_tone = "neutral"

        # 복잡도 추정
        if len(user_input) > 100 or "?" in user_input and len(user_input.split()) > 10:
            complexity = "high"
        elif len(user_input) > 50 or any(
            word in user_lower for word in ["분석", "어떻게", "analyze", "how"]
        ):
            complexity = "medium"
        else:
            complexity = "low"

        return IntentAnalysisResult(
            intent=intent,
            confidence=confidence,
            reasoning=reasoning,
            emotional_tone=emotional_tone,
            complexity=complexity,
            raw_response=f"Mock 분석: {intent.value} ({confidence:.0%})",
            processing_time=0.0,
            provider_used="mock",
        )

    def _fallback_analysis(self, user_input: str, error: str) -> IntentAnalysisResult:
        """폴백 분석 (에러 발생 시)"""
        return IntentAnalysisResult(
            intent=IntentType.GENERAL_CONVERSATION,
            confidence=0.5,
            reasoning=f"분석 실패로 인한 기본값 사용: {error}",
            emotional_tone="neutral",
            complexity="medium",
            raw_response=f"Error: {error}",
            processing_time=0.0,
            provider_used="fallback",
        )

    # 동기 버전 (호환성)
    def analyze_intent_sync(self, user_input: str) -> IntentAnalysisResult:
        """동기 버전 Intent 분석"""
        try:
            return asyncio.run(self.analyze_intent(user_input))
        except Exception as e:
            self.logger.error(f"Sync intent analysis failed: {e}")
            return self._fallback_analysis(user_input, str(e))

    # 유틸리티 메서드
    def get_intent_description(self, intent: IntentType) -> str:
        """Intent 타입 설명"""
        descriptions = {
            IntentType.CREATIVE_EXPRESSION: "창의적 표현과 아이디어 생성을 원하는 의도",
            IntentType.ANALYTICAL_INQUIRY: "분석적 사고와 논리적 문제 해결을 요구하는 의도",
            IntentType.EMOTIONAL_SUPPORT: "감정적 지원과 공감을 필요로 하는 의도",
            IntentType.COLLABORATIVE_TASK: "협업과 상호작용을 통한 작업 수행 의도",
            IntentType.PHILOSOPHICAL_REFLECTION: "철학적 사고와 존재론적 성찰 의도",
            IntentType.TECHNICAL_ASSISTANCE: "기술적 문제 해결과 전문 지식 지원 의도",
            IntentType.GENERAL_CONVERSATION: "일반적인 대화와 정보 교환 의도",
        }
        return descriptions.get(intent, "알 수 없는 의도")

    def validate_analysis_result(self, result: IntentAnalysisResult) -> bool:
        """분석 결과 유효성 검증"""
        if not isinstance(result.intent, IntentType):
            return False
        if not (0.0 <= result.confidence <= 1.0):
            return False
        if result.emotional_tone not in ["positive", "neutral", "negative"]:
            return False
        if result.complexity not in ["low", "medium", "high"]:
            return False
        return True


# 편의 함수
async def quick_intent_analysis(user_input: str) -> IntentAnalysisResult:
    """빠른 Intent 분석"""
    client = GPTIntentClient()
    return await client.analyze_intent(user_input)


def quick_intent_analysis_sync(user_input: str) -> IntentAnalysisResult:
    """빠른 Intent 분석 (동기 버전)"""
    client = GPTIntentClient()
    return client.analyze_intent_sync(user_input)


if __name__ == "__main__":
    # 테스트 코드
    import asyncio

    async def test_intent_client():
        """테스트 함수"""
        client = GPTIntentClient()

        test_inputs = [
            "나는 새로운 앱 아이디어를 생각해보고 싶어",
            "이 코드가 왜 작동하지 않는지 분석해줘",
            "요즘 너무 힘들어서 위로가 필요해",
            "함께 프로젝트를 진행하고 싶은데 도움을 줄 수 있어?",
            "너는 도구가 아니라 존재로 작동하니?",
            "Python 버그를 찾아서 수정해줘",
            "안녕하세요 반가워요",
        ]

        print("🌐 GPT Intent Client 테스트")
        print("=" * 50)

        for user_input in test_inputs:
            print(f"\n💬 입력: {user_input}")
            result = await client.analyze_intent(user_input)

            print(f"🎯 Intent: {result.intent.value}")
            print(f"📊 신뢰도: {result.confidence:.0%}")
            print(f"💭 이유: {result.reasoning}")
            print(f"😊 감정톤: {result.emotional_tone}")
            print(f"⚖️  복잡도: {result.complexity}")
            print(f"⏱️  처리시간: {result.processing_time:.3f}초")
            print(f"🔧 제공자: {result.provider_used}")
            print("-" * 30)

    # 테스트 실행
    asyncio.run(test_intent_client())
