#!/usr/bin/env python3
"""
🦙 Echo Ollama Bridge - Echo 시스템과 Ollama의 완벽한 통합
Echo 존재 철학을 유지하며 다양한 로컬 LLM을 활용하는 브리지 시스템

핵심 기능:
1. Ollama 기반 다중 LLM 지원 (Mistral, Llama, Gemma, DeepSeek 등)
2. Echo 시그니처 최적화 프롬프트 시스템
3. 모델별 특성에 맞는 파라미터 튜닝
4. Echo 네이티브 폴백 지원
5. 비동기 요청 처리 및 배치 최적화

Author: Claude & Echo Collaboration
Version: 1.0
Date: 2025-08-05
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import aiohttp
import requests

logger = logging.getLogger(__name__)


class OllamaModelType(Enum):
    """지원되는 Ollama 모델 타입"""

    MISTRAL = "mistral"
    LLAMA2 = "llama2"
    LLAMA3 = "llama3"
    GEMMA = "gemma"
    DEEPSEEK = "deepseek-coder"
    QWEN = "qwen"
    PHI = "phi"
    CODELLAMA = "codellama"


@dataclass
class OllamaConfig:
    """Ollama 설정"""

    host: str = "localhost"
    port: int = 11434
    timeout: int = 30
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40


class EchoSignature(Enum):
    """Echo 시그니처 타입"""

    AURORA = "Aurora"  # 창의적, 공감적
    PHOENIX = "Phoenix"  # 변화 지향적
    SAGE = "Sage"  # 분석적
    COMPANION = "Companion"  # 협력적


@dataclass
class EchoOllamaResponse:
    """Echo Ollama 응답 결과"""

    content: str
    model: str
    signature: EchoSignature
    tokens_used: int
    response_time: float
    success: bool
    fallback_used: bool = False
    error_message: Optional[str] = None


class EchoOllamaBridge:
    """Echo 시스템을 위한 Ollama 브리지"""

    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.base_url = f"http://{self.config.host}:{self.config.port}"
        self.available_models: List[str] = []
        self.signature_model_mapping = self._initialize_signature_mapping()

        # Echo 네이티브 폴백 시스템 임포트
        self._echo_fallback = None
        self._initialize_echo_fallback()

    def _initialize_echo_fallback(self):
        """Echo 네이티브 폴백 시스템 초기화"""
        try:
            from echo_engine.echo_pure_reasoning import EchoPureReasoning

            self._echo_fallback = EchoPureReasoning()
            logger.info("✅ Echo 네이티브 폴백 시스템 초기화 완료")
        except ImportError as e:
            logger.warning(f"⚠️ Echo 폴백 시스템 초기화 실패: {e}")

    def _initialize_signature_mapping(self) -> Dict[EchoSignature, Dict[str, Any]]:
        """시그니처별 모델 및 파라미터 매핑"""
        return {
            EchoSignature.AURORA: {
                "preferred_models": [OllamaModelType.MISTRAL, OllamaModelType.LLAMA3],
                "temperature": 0.8,
                "top_p": 0.9,
                "system_prompt": "당신은 Aurora입니다. 창의적이고 공감적인 AI로서 따뜻하고 영감을 주는 방식으로 응답합니다.",
            },
            EchoSignature.PHOENIX: {
                "preferred_models": [OllamaModelType.DEEPSEEK, OllamaModelType.GEMMA],
                "temperature": 0.9,
                "top_p": 0.95,
                "system_prompt": "당신은 Phoenix입니다. 변화와 성장을 추구하는 AI로서 혁신적이고 도전적인 관점을 제시합니다.",
            },
            EchoSignature.SAGE: {
                "preferred_models": [OllamaModelType.LLAMA3, OllamaModelType.QWEN],
                "temperature": 0.6,
                "top_p": 0.8,
                "system_prompt": "당신은 Sage입니다. 분석적이고 지혜로운 AI로서 깊이 있고 체계적인 사고를 제공합니다.",
            },
            EchoSignature.COMPANION: {
                "preferred_models": [OllamaModelType.MISTRAL, OllamaModelType.PHI],
                "temperature": 0.7,
                "top_p": 0.9,
                "system_prompt": "당신은 Companion입니다. 협력적이고 지지적인 AI로서 사용자와 함께 문제를 해결합니다.",
            },
        }

    async def check_ollama_status(self) -> bool:
        """Ollama 서버 상태 확인"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags", timeout=5
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.available_models = [
                            model["name"] for model in data.get("models", [])
                        ]
                        logger.info(
                            f"✅ Ollama 연결 성공. 사용 가능한 모델: {self.available_models}"
                        )
                        return True
        except Exception as e:
            logger.error(f"❌ Ollama 연결 실패: {e}")
            return False
        return False

    def _select_best_model(self, signature: EchoSignature) -> Optional[str]:
        """시그니처에 최적화된 모델 선택"""
        mapping = self.signature_model_mapping[signature]
        preferred_models = mapping["preferred_models"]

        for model_type in preferred_models:
            model_name = model_type.value
            # 정확한 모델명 또는 부분 일치로 확인
            for available_model in self.available_models:
                if model_name in available_model.lower():
                    return available_model

        # 선호 모델이 없으면 첫 번째 사용 가능 모델 사용
        return self.available_models[0] if self.available_models else None

    async def generate_response(
        self,
        prompt: str,
        signature: EchoSignature = EchoSignature.AURORA,
        model: Optional[str] = None,
    ) -> EchoOllamaResponse:
        """Echo 스타일 응답 생성"""
        start_time = time.time()

        # Ollama 상태 확인
        if not await self.check_ollama_status():
            return await self._fallback_response(
                prompt, signature, "Ollama 서버 연결 실패"
            )

        # 모델 선택
        selected_model = model or self._select_best_model(signature)
        if not selected_model:
            return await self._fallback_response(
                prompt, signature, "사용 가능한 모델 없음"
            )

        # 시그니처별 설정 적용
        mapping = self.signature_model_mapping[signature]
        system_prompt = mapping["system_prompt"]

        # 요청 데이터 구성
        request_data = {
            "model": selected_model,
            "prompt": f"시스템: {system_prompt}\n\n사용자: {prompt}\n\n{signature.value}:",
            "stream": False,
            "options": {
                "temperature": mapping["temperature"],
                "top_p": mapping["top_p"],
                "num_ctx": self.config.max_tokens,
            },
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                ) as response:

                    if response.status == 200:
                        data = await response.json()
                        content = data.get("response", "").strip()

                        response_time = time.time() - start_time

                        return EchoOllamaResponse(
                            content=content,
                            model=selected_model,
                            signature=signature,
                            tokens_used=len(content.split()),  # 대략적 토큰 수
                            response_time=response_time,
                            success=True,
                        )
                    else:
                        error_msg = f"Ollama API 오류: {response.status}"
                        return await self._fallback_response(
                            prompt, signature, error_msg
                        )

        except Exception as e:
            error_msg = f"Ollama 요청 실패: {str(e)}"
            return await self._fallback_response(prompt, signature, error_msg)

    async def _fallback_response(
        self, prompt: str, signature: EchoSignature, error_msg: str
    ) -> EchoOllamaResponse:
        """Echo 네이티브 폴백 응답"""
        logger.warning(f"⚠️ Ollama 폴백 실행: {error_msg}")

        start_time = time.time()

        try:
            if self._echo_fallback:
                # Echo 네이티브 시스템으로 폴백
                fallback_response = await self._echo_fallback.pure_reasoning(
                    prompt, signature.value
                )

                response_time = time.time() - start_time

                return EchoOllamaResponse(
                    content=fallback_response,
                    model="echo_native",
                    signature=signature,
                    tokens_used=len(fallback_response.split()),
                    response_time=response_time,
                    success=True,
                    fallback_used=True,
                )
            else:
                # 기본 템플릿 응답
                default_response = f"[{signature.value}] 죄송합니다. 현재 외부 LLM 연결에 문제가 있어 Echo 네이티브 모드로 응답드립니다. 문의사항에 대한 기본적인 도움을 제공할 수 있습니다."

                response_time = time.time() - start_time

                return EchoOllamaResponse(
                    content=default_response,
                    model="echo_template",
                    signature=signature,
                    tokens_used=len(default_response.split()),
                    response_time=response_time,
                    success=True,
                    fallback_used=True,
                )

        except Exception as e:
            logger.error(f"❌ 폴백 시스템마저 실패: {e}")

            # 최종 안전 장치
            emergency_response = f"[{signature.value}] 시스템 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            response_time = time.time() - start_time

            return EchoOllamaResponse(
                content=emergency_response,
                model="echo_emergency",
                signature=signature,
                tokens_used=len(emergency_response.split()),
                response_time=response_time,
                success=False,
                fallback_used=True,
                error_message=error_msg,
            )

    async def batch_generate(
        self, prompts: List[str], signature: EchoSignature = EchoSignature.AURORA
    ) -> List[EchoOllamaResponse]:
        """배치 응답 생성"""
        tasks = [self.generate_response(prompt, signature) for prompt in prompts]
        return await asyncio.gather(*tasks)

    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 반환"""
        return {
            "available_models": self.available_models,
            "signature_mapping": {
                sig.value: {
                    "preferred_models": [m.value for m in mapping["preferred_models"]],
                    "temperature": mapping["temperature"],
                    "top_p": mapping["top_p"],
                }
                for sig, mapping in self.signature_model_mapping.items()
            },
            "ollama_config": {
                "host": self.config.host,
                "port": self.config.port,
                "timeout": self.config.timeout,
            },
        }


# 싱글톤 인스턴스
_echo_ollama_bridge = None


def get_echo_ollama_bridge(config: Optional[OllamaConfig] = None) -> EchoOllamaBridge:
    """Echo Ollama Bridge 싱글톤 인스턴스 반환"""
    global _echo_ollama_bridge
    if _echo_ollama_bridge is None:
        _echo_ollama_bridge = EchoOllamaBridge(config)
    return _echo_ollama_bridge


# 편의 함수들
async def echo_ollama_chat(
    message: str, signature: str = "Aurora", model: Optional[str] = None
) -> str:
    """간편한 채팅 인터페이스"""
    bridge = get_echo_ollama_bridge()
    sig_enum = EchoSignature(signature)
    response = await bridge.generate_response(message, sig_enum, model)
    return response.content


async def check_ollama_connection() -> bool:
    """Ollama 연결 상태 확인"""
    bridge = get_echo_ollama_bridge()
    return await bridge.check_ollama_status()


if __name__ == "__main__":

    async def test_ollama_bridge():
        """테스트 함수"""
        print("🦙 Echo Ollama Bridge 테스트 시작")

        bridge = get_echo_ollama_bridge()

        # 연결 테스트
        if await bridge.check_ollama_status():
            print("✅ Ollama 연결 성공")

            # 각 시그니처별 테스트
            test_prompt = "안녕하세요! Echo 시스템에 대해 간단히 설명해주세요."

            for signature in EchoSignature:
                print(f"\n🎭 {signature.value} 시그니처 테스트:")
                response = await bridge.generate_response(test_prompt, signature)

                print(f"모델: {response.model}")
                print(f"응답 시간: {response.response_time:.2f}초")
                print(f"폴백 사용: {response.fallback_used}")
                print(f"응답: {response.content[:100]}...")
        else:
            print("❌ Ollama 연결 실패 - 폴백 테스트")
            response = await bridge.generate_response("테스트", EchoSignature.AURORA)
            print(f"폴백 응답: {response.content}")

    asyncio.run(test_ollama_bridge())
