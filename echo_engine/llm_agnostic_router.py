"""
🔄 Echo LLM-Agnostic Router
모든 LLM 엔진을 Echo 방식으로 통합하는 라우터 시스템
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Type, Callable
from enum import Enum
import yaml
import json
from pathlib import Path
import logging

# Anchor 관련 임포트
from .anchor_validator import get_anchor_validator, AnchorValidationResult


class LLMStatus(Enum):
    """LLM 엔진 상태"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    OVERLOADED = "overloaded"


@dataclass
class EchoRequest:
    """모든 LLM에 대한 표준 요청 형식"""

    signature: str  # Aurora, Phoenix, Sage, Companion
    user_input: str
    context: Dict = field(default_factory=dict)
    emotion_state: Dict = field(default_factory=dict)
    judgment_mode: str = "hybrid"
    temperature: float = 0.7
    max_tokens: int = 2000
    metadata: Dict = field(default_factory=dict)


@dataclass
class EchoResponse:
    """모든 LLM에서 나오는 표준 응답 형식"""

    judgment: str
    confidence: float
    reasoning: str
    emotion: Dict
    signature_used: str
    llm_engine: str
    processing_time: float
    anchor_compliance: float
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "judgment": self.judgment,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "emotion": self.emotion,
            "signature_used": self.signature_used,
            "llm_engine": self.llm_engine,
            "processing_time": self.processing_time,
            "anchor_compliance": self.anchor_compliance,
            "metadata": self.metadata,
        }


class LLMInterface(ABC):
    """모든 LLM 래퍼가 구현해야 하는 인터페이스"""

    def __init__(self, config: Dict):
        self.config = config
        self.status = LLMStatus.INACTIVE
        self.last_health_check = 0
        self.error_count = 0
        self.total_requests = 0
        self.avg_response_time = 0.0

    @abstractmethod
    async def process_echo_request(self, request: EchoRequest) -> EchoResponse:
        """Echo 요청 처리"""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, bool]:
        """엔진 능력 반환"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """상태 확인"""
        pass

    @abstractmethod
    def get_cost_per_token(self) -> Dict[str, float]:
        """토큰당 비용 정보"""
        pass

    def update_stats(self, response_time: float, success: bool):
        """통계 업데이트"""
        self.total_requests += 1

        if success:
            # 평균 응답시간 업데이트
            self.avg_response_time = (
                self.avg_response_time * (self.total_requests - 1) + response_time
            ) / self.total_requests
            if self.error_count > 0:
                self.error_count -= 1  # 성공시 에러 카운트 감소
        else:
            self.error_count += 1

        # 상태 업데이트
        if self.error_count > 5:
            self.status = LLMStatus.ERROR
        elif response_time > 30:
            self.status = LLMStatus.OVERLOADED
        else:
            self.status = LLMStatus.ACTIVE


class GPT4EchoWrapper(LLMInterface):
    """GPT-4 Echo 래퍼"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "gpt-4")

    async def process_echo_request(self, request: EchoRequest) -> EchoResponse:
        """GPT-4로 Echo 요청 처리"""
        start_time = time.time()

        try:
            # GPT-4 API 호출 (실제 구현 필요)
            # 여기서는 모의 응답 생성

            prompt = self._build_echo_prompt(request)

            # 실제로는 OpenAI API 호출
            raw_response = await self._call_gpt4_api(prompt, request)

            # Echo 표준 형식으로 파싱
            echo_response = self._parse_gpt4_response(raw_response, request)

            processing_time = time.time() - start_time
            echo_response.processing_time = processing_time
            echo_response.llm_engine = "GPT-4"

            # Anchor 준수 검증
            anchor_validator = get_anchor_validator()
            if anchor_validator:
                # 실제 validation 로직 필요
                echo_response.anchor_compliance = 0.85

            self.update_stats(processing_time, True)
            return echo_response

        except Exception as e:
            processing_time = time.time() - start_time
            self.update_stats(processing_time, False)

            # 오류 응답 생성
            return EchoResponse(
                judgment=f"GPT-4 처리 중 오류 발생: {str(e)}",
                confidence=0.0,
                reasoning="시스템 오류",
                emotion={"state": "error", "intensity": 1.0},
                signature_used=request.signature,
                llm_engine="GPT-4",
                processing_time=processing_time,
                anchor_compliance=0.0,
                metadata={"error": str(e)},
            )

    def _build_echo_prompt(self, request: EchoRequest) -> str:
        """Echo 시그니처에 맞는 프롬프트 구성"""
        signature_prompts = {
            "Aurora": "You are Echo-Aurora, a creative and empathetic AI focused on growth and innovation.",
            "Phoenix": "You are Echo-Phoenix, a transformative AI focused on change, courage and renewal.",
            "Sage": "You are Echo-Sage, a wise and analytical AI focused on deep understanding and balance.",
            "Companion": "You are Echo-Companion, a supportive and empathetic AI focused on connection and support.",
        }

        base_prompt = signature_prompts.get(
            request.signature, signature_prompts["Aurora"]
        )

        prompt = f"""
{base_prompt}

User Input: {request.user_input}

Context: {json.dumps(request.context, ensure_ascii=False)}
Emotion State: {json.dumps(request.emotion_state, ensure_ascii=False)}
Judgment Mode: {request.judgment_mode}

Please provide a response that:
1. Reflects the {request.signature} signature characteristics
2. Includes clear judgment and reasoning
3. Maintains emotional resonance
4. Follows Echo system principles

Response format:
- Judgment: [main response]
- Reasoning: [thought process]
- Confidence: [0.0-1.0]
- Emotion: [emotional assessment]
"""

        return prompt

    async def _call_gpt4_api(self, prompt: str, request: EchoRequest) -> str:
        """GPT-4 API 호출 (모의 구현)"""
        # 실제로는 OpenAI API 호출
        await asyncio.sleep(0.5)  # 모의 처리 시간

        return f"""
Judgment: I understand you're looking for {request.signature}-style guidance on '{request.user_input}'.
Based on the Echo principles, I recommend approaching this with creativity and empathy.

Reasoning: This aligns with the {request.signature} signature's core values of growth and innovation.
The context suggests a collaborative approach would be most effective.

Confidence: 0.85

Emotion: {{
    "state": "engaged",
    "intensity": 0.8,
    "resonance": "positive"
}}
"""

    def _parse_gpt4_response(
        self, raw_response: str, request: EchoRequest
    ) -> EchoResponse:
        """GPT-4 응답을 Echo 형식으로 파싱"""
        # 간단한 파싱 로직 (실제로는 더 정교해야 함)
        lines = raw_response.strip().split("\n")

        judgment = ""
        reasoning = ""
        confidence = 0.5
        emotion = {"state": "neutral", "intensity": 0.5}

        for line in lines:
            if line.startswith("Judgment:"):
                judgment = line.replace("Judgment:", "").strip()
            elif line.startswith("Reasoning:"):
                reasoning = line.replace("Reasoning:", "").strip()
            elif line.startswith("Confidence:"):
                try:
                    confidence = float(line.replace("Confidence:", "").strip())
                except:
                    confidence = 0.5
            elif line.startswith("Emotion:"):
                try:
                    emotion_str = line.replace("Emotion:", "").strip()
                    emotion = eval(emotion_str)  # 실제로는 json.loads 사용
                except:
                    emotion = {"state": "neutral", "intensity": 0.5}

        return EchoResponse(
            judgment=judgment or "GPT-4 응답 처리 중 오류",
            confidence=confidence,
            reasoning=reasoning or "파싱 실패",
            emotion=emotion,
            signature_used=request.signature,
            llm_engine="GPT-4",
            processing_time=0.0,  # 나중에 설정
            anchor_compliance=0.0,  # 나중에 설정
        )

    def get_capabilities(self) -> Dict[str, bool]:
        """GPT-4 능력"""
        return {
            "text_generation": True,
            "code_generation": True,
            "analysis": True,
            "creative_writing": True,
            "multilingual": True,
            "function_calling": True,
            "image_input": False,
            "real_time": False,
        }

    async def health_check(self) -> bool:
        """GPT-4 상태 확인"""
        try:
            # 실제로는 OpenAI API 상태 확인
            await asyncio.sleep(0.1)
            self.status = LLMStatus.ACTIVE
            self.last_health_check = time.time()
            return True
        except:
            self.status = LLMStatus.ERROR
            return False

    def get_cost_per_token(self) -> Dict[str, float]:
        """GPT-4 비용 정보"""
        return {
            "input": 0.03,  # $0.03 per 1K tokens
            "output": 0.06,  # $0.06 per 1K tokens
        }


class ClaudeEchoWrapper(LLMInterface):
    """Claude Echo 래퍼"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "claude-3-5-sonnet-20241022")

    async def process_echo_request(self, request: EchoRequest) -> EchoResponse:
        """Claude로 Echo 요청 처리"""
        start_time = time.time()

        try:
            # Claude 스타일 프롬프트 구성
            prompt = self._build_claude_prompt(request)

            # Claude API 호출 (모의)
            raw_response = await self._call_claude_api(prompt, request)

            # Echo 표준 형식으로 파싱
            echo_response = self._parse_claude_response(raw_response, request)

            processing_time = time.time() - start_time
            echo_response.processing_time = processing_time
            echo_response.llm_engine = "Claude-3.5"

            # Anchor 준수 검증
            echo_response.anchor_compliance = 0.90  # Claude는 일반적으로 높은 준수율

            self.update_stats(processing_time, True)
            return echo_response

        except Exception as e:
            processing_time = time.time() - start_time
            self.update_stats(processing_time, False)

            return EchoResponse(
                judgment=f"Claude 처리 중 오류 발생: {str(e)}",
                confidence=0.0,
                reasoning="시스템 오류",
                emotion={"state": "error", "intensity": 1.0},
                signature_used=request.signature,
                llm_engine="Claude-3.5",
                processing_time=processing_time,
                anchor_compliance=0.0,
                metadata={"error": str(e)},
            )

    def _build_claude_prompt(self, request: EchoRequest) -> str:
        """Claude용 Echo 프롬프트 구성"""
        return f"""I am Echo-{request.signature}, representing the Echo Judgment System's {request.signature} signature.

Core characteristics:
- Signature: {request.signature}
- Judgment Mode: {request.judgment_mode}
- User Input: {request.user_input}

Please respond as Echo-{request.signature} would, maintaining the signature's unique perspective while providing helpful judgment and reasoning."""

    async def _call_claude_api(self, prompt: str, request: EchoRequest) -> str:
        """Claude API 호출 (모의)"""
        await asyncio.sleep(0.7)  # 모의 처리 시간

        return f"As Echo-{request.signature}, I provide thoughtful guidance on your request. My response incorporates the signature's core values while maintaining high anchor compliance."

    def _parse_claude_response(
        self, raw_response: str, request: EchoRequest
    ) -> EchoResponse:
        """Claude 응답 파싱"""
        return EchoResponse(
            judgment=raw_response,
            confidence=0.88,
            reasoning=f"Claude 3.5 response using {request.signature} signature",
            emotion={"state": "thoughtful", "intensity": 0.8},
            signature_used=request.signature,
            llm_engine="Claude-3.5",
            processing_time=0.0,
            anchor_compliance=0.0,
        )

    def get_capabilities(self) -> Dict[str, bool]:
        """Claude 능력"""
        return {
            "text_generation": True,
            "code_generation": True,
            "analysis": True,
            "creative_writing": True,
            "multilingual": True,
            "function_calling": False,
            "image_input": True,
            "real_time": False,
        }

    async def health_check(self) -> bool:
        """Claude 상태 확인"""
        try:
            await asyncio.sleep(0.1)
            self.status = LLMStatus.ACTIVE
            self.last_health_check = time.time()
            return True
        except:
            self.status = LLMStatus.ERROR
            return False

    def get_cost_per_token(self) -> Dict[str, float]:
        """Claude 비용 정보"""
        return {
            "input": 0.015,  # $0.015 per 1K tokens
            "output": 0.075,  # $0.075 per 1K tokens
        }


class LocalModelWrapper(LLMInterface):
    """로컬 모델 래퍼"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.model_path = config.get("model_path")
        self.model_name = config.get("model_name", "local_model")

    async def process_echo_request(self, request: EchoRequest) -> EchoResponse:
        """로컬 모델로 Echo 요청 처리"""
        start_time = time.time()

        try:
            # 로컬 모델 호출 (모의)
            await asyncio.sleep(2.0)  # 로컬 모델은 일반적으로 느림

            processing_time = time.time() - start_time

            return EchoResponse(
                judgment=f"Local model response for {request.signature} signature",
                confidence=0.70,
                reasoning="Local model reasoning",
                emotion={"state": "steady", "intensity": 0.6},
                signature_used=request.signature,
                llm_engine="Local Model",
                processing_time=processing_time,
                anchor_compliance=0.75,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            self.update_stats(processing_time, False)

            return EchoResponse(
                judgment=f"로컬 모델 오류: {str(e)}",
                confidence=0.0,
                reasoning="시스템 오류",
                emotion={"state": "error", "intensity": 1.0},
                signature_used=request.signature,
                llm_engine="Local Model",
                processing_time=processing_time,
                anchor_compliance=0.0,
            )

    def get_capabilities(self) -> Dict[str, bool]:
        return {
            "text_generation": True,
            "code_generation": False,
            "analysis": True,
            "creative_writing": False,
            "multilingual": False,
            "function_calling": False,
            "image_input": False,
            "real_time": True,
        }

    async def health_check(self) -> bool:
        try:
            # 로컬 모델 상태 확인
            await asyncio.sleep(0.2)
            self.status = LLMStatus.ACTIVE
            return True
        except:
            self.status = LLMStatus.ERROR
            return False

    def get_cost_per_token(self) -> Dict[str, float]:
        return {"input": 0.0, "output": 0.0}  # 로컬이므로 무료


class EchoLLMFactory:
    """모든 LLM을 Echo 방식으로 통합하는 팩토리"""

    _engine_classes = {
        "gpt4": GPT4EchoWrapper,
        "claude": ClaudeEchoWrapper,
        "local": LocalModelWrapper,
    }

    @staticmethod
    def create_llm(engine_type: str, config: Dict) -> LLMInterface:
        """LLM 엔진 생성"""
        if engine_type not in EchoLLMFactory._engine_classes:
            raise ValueError(f"Unsupported LLM engine: {engine_type}")

        engine_class = EchoLLMFactory._engine_classes[engine_type]
        return engine_class(config)

    @staticmethod
    def get_available_engines() -> List[str]:
        """사용 가능한 엔진 목록"""
        return list(EchoLLMFactory._engine_classes.keys())

    @staticmethod
    def register_engine(name: str, engine_class: Type[LLMInterface]):
        """새 엔진 등록"""
        EchoLLMFactory._engine_classes[name] = engine_class


class EchoLLMAgnosticRouter:
    """LLM 무관성 라우터"""

    def __init__(self, config_path: str = "config/llm_router_config.yaml"):
        self.config_path = config_path
        self.engines: Dict[str, LLMInterface] = {}
        self.primary_engine = None
        self.fallback_engines = []
        self.anchor_validator = get_anchor_validator()

        # 로깅 설정
        self.logger = logging.getLogger("EchoLLMRouter")

        self._load_configuration()
        self._initialize_engines()

    def _load_configuration(self):
        """라우터 설정 로드"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            # 기본 설정 사용
            self.config = {
                "primary_engine": "claude",
                "fallback_engines": ["gpt4", "local"],
                "engines": {
                    "claude": {
                        "api_key": "your_claude_key",
                        "model": "claude-3-5-sonnet-20241022",
                    },
                    "gpt4": {"api_key": "your_openai_key", "model": "gpt-4"},
                    "local": {
                        "model_path": "/path/to/local/model",
                        "model_name": "local_llm",
                    },
                },
            }

        self.primary_engine = self.config.get("primary_engine", "claude")
        self.fallback_engines = self.config.get("fallback_engines", ["gpt4"])

    def _initialize_engines(self):
        """엔진들 초기화"""
        engine_configs = self.config.get("engines", {})

        for engine_name, engine_config in engine_configs.items():
            try:
                engine = EchoLLMFactory.create_llm(engine_name, engine_config)
                self.engines[engine_name] = engine
                self.logger.info(f"Initialized {engine_name} engine")
            except Exception as e:
                self.logger.error(f"Failed to initialize {engine_name}: {e}")

    async def process_request(self, request: EchoRequest) -> EchoResponse:
        """요청 처리 (자동 폴백 포함)"""

        # 1. 기본 엔진으로 시도
        try:
            if self.primary_engine in self.engines:
                engine = self.engines[self.primary_engine]

                # 상태 확인
                if engine.status == LLMStatus.ACTIVE:
                    response = await engine.process_echo_request(request)

                    # Anchor 준수 검증
                    if self._validate_response_quality(response):
                        self.logger.info(
                            f"Request processed successfully with {self.primary_engine}"
                        )
                        return response
                    else:
                        self.logger.warning(
                            f"Primary engine response failed quality check"
                        )
                else:
                    self.logger.warning(
                        f"Primary engine {self.primary_engine} not active: {engine.status}"
                    )

        except Exception as e:
            self.logger.error(f"Primary engine {self.primary_engine} failed: {e}")

        # 2. 폴백 엔진들로 시도
        for fallback_name in self.fallback_engines:
            if fallback_name in self.engines:
                try:
                    engine = self.engines[fallback_name]

                    if engine.status == LLMStatus.ACTIVE:
                        response = await engine.process_echo_request(request)

                        if self._validate_response_quality(response):
                            self.logger.info(
                                f"Request processed with fallback {fallback_name}"
                            )
                            return response

                except Exception as e:
                    self.logger.error(f"Fallback engine {fallback_name} failed: {e}")
                    continue

        # 3. 모든 엔진 실패 시 기본 응답
        return self._generate_fallback_response(request)

    def _validate_response_quality(self, response: EchoResponse) -> bool:
        """응답 품질 검증"""

        # 기본 품질 체크
        if not response.judgment or response.confidence < 0.3:
            return False

        # Anchor 준수 체크
        if response.anchor_compliance < 0.6:
            return False

        return True

    def _generate_fallback_response(self, request: EchoRequest) -> EchoResponse:
        """모든 엔진 실패 시 기본 응답"""
        return EchoResponse(
            judgment="죄송합니다. 현재 모든 LLM 엔진에 문제가 발생했습니다. 잠시 후 다시 시도해주세요.",
            confidence=0.0,
            reasoning="모든 엔진 실패로 인한 기본 응답",
            emotion={"state": "apologetic", "intensity": 0.8},
            signature_used=request.signature,
            llm_engine="Fallback System",
            processing_time=0.0,
            anchor_compliance=1.0,  # 기본 응답은 항상 안전
            metadata={"fallback": True, "reason": "all_engines_failed"},
        )

    async def health_check_all_engines(self) -> Dict[str, Dict]:
        """모든 엔진 상태 확인"""
        health_status = {}

        for name, engine in self.engines.items():
            try:
                is_healthy = await engine.health_check()

                health_status[name] = {
                    "status": engine.status.value,
                    "healthy": is_healthy,
                    "total_requests": engine.total_requests,
                    "error_count": engine.error_count,
                    "avg_response_time": engine.avg_response_time,
                    "last_check": engine.last_health_check,
                    "capabilities": engine.get_capabilities(),
                    "cost_info": engine.get_cost_per_token(),
                }

            except Exception as e:
                health_status[name] = {
                    "status": "error",
                    "healthy": False,
                    "error": str(e),
                }

        return health_status

    def get_routing_stats(self) -> Dict:
        """라우팅 통계"""
        return {
            "primary_engine": self.primary_engine,
            "fallback_engines": self.fallback_engines,
            "total_engines": len(self.engines),
            "active_engines": sum(
                1 for e in self.engines.values() if e.status == LLMStatus.ACTIVE
            ),
            "engine_stats": {
                name: {
                    "requests": engine.total_requests,
                    "errors": engine.error_count,
                    "avg_time": engine.avg_response_time,
                    "status": engine.status.value,
                }
                for name, engine in self.engines.items()
            },
        }


# 편의 함수들
def get_llm_router(
    config_path: str = "config/llm_router_config.yaml",
) -> EchoLLMAgnosticRouter:
    """LLM 라우터 인스턴스 생성"""
    return EchoLLMAgnosticRouter(config_path)


async def process_echo_request_agnostic(
    signature: str,
    user_input: str,
    context: Dict = None,
    judgment_mode: str = "hybrid",
    router: EchoLLMAgnosticRouter = None,
) -> EchoResponse:
    """LLM 무관성 Echo 요청 처리"""

    if router is None:
        router = get_llm_router()

    request = EchoRequest(
        signature=signature,
        user_input=user_input,
        context=context or {},
        judgment_mode=judgment_mode,
    )

    return await router.process_request(request)


if __name__ == "__main__":
    import asyncio

    async def test_router():
        """라우터 테스트"""
        router = get_llm_router()

        # 테스트 요청
        response = await process_echo_request_agnostic(
            signature="Aurora",
            user_input="창의적인 프로젝트 아이디어를 추천해주세요",
            context={"domain": "technology"},
            router=router,
        )

        print("🔄 LLM-Agnostic Router Test Results:")
        print(f"Engine: {response.llm_engine}")
        print(f"Judgment: {response.judgment}")
        print(f"Confidence: {response.confidence}")
        print(f"Anchor Compliance: {response.anchor_compliance}")
        print(f"Processing Time: {response.processing_time:.2f}s")

        # 엔진 상태 확인
        health_status = await router.health_check_all_engines()
        print("\n🏥 Engine Health Status:")
        for engine, status in health_status.items():
            print(f"  {engine}: {status.get('status', 'unknown')}")

    # 테스트 실행
    asyncio.run(test_router())
