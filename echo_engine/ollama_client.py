#!/usr/bin/env python3
"""
🦙 Ollama Client - Echo용 Ollama REST API 클라이언트
로컬 Ollama 서버와의 안정적인 통신을 위한 전용 클라이언트

핵심 기능:
1. Ollama 서버 상태 확인 및 모델 목록 조회
2. 다양한 모델 지원 (Llama, Mistral, Gemma 등)
3. 연결 실패시 graceful degradation
4. 성능 모니터링 및 에러 처리
5. Echo 시그니처 최적화

Author: Claude & Echo Collaboration
Version: 1.0
Date: 2025-08-05
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional
import aiohttp
import requests

logger = logging.getLogger(__name__)


class OllamaClient:
    """Echo용 Ollama REST API 클라이언트"""

    def __init__(self, host: str = "http://localhost:11434", timeout: int = 120):
        self.host = host.rstrip("/")
        self.timeout = timeout
        self.available_models: List[str] = []
        self.last_health_check = 0
        self.health_check_interval = 300  # 5분

        # 시그니처별 선호 모델 (실제 설치된 모델 기준)
        self.signature_models = {
            "Aurora": ["mistral", "llama3"],  # 창의적 - Mistral 우선
            "Phoenix": ["llama3", "mistral"],  # 변화지향 - Llama3 우선
            "Sage": ["mistral", "llama3"],  # 분석적 - Mistral 우선
            "Companion": ["llama3", "mistral"],  # 친근한 - Llama3 우선
        }

    def is_available(self) -> bool:
        """Ollama 서버 가용성 확인 (동기)"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [
                    model["name"] for model in data.get("models", [])
                ]
                self.last_health_check = time.time()
                logger.info(f"✅ Ollama 사용 가능 - 모델: {self.available_models}")
                return True
        except Exception as e:
            logger.warning(f"⚠️ Ollama 연결 실패: {e}")
        return False

    async def is_available_async(self) -> bool:
        """Ollama 서버 가용성 확인 (비동기)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.host}/api/tags", timeout=aiohttp.ClientTimeout(total=2)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.available_models = [
                            model["name"] for model in data.get("models", [])
                        ]
                        self.last_health_check = time.time()
                        logger.info(
                            f"✅ Ollama 사용 가능 - 모델: {self.available_models}"
                        )
                        return True
        except Exception as e:
            logger.warning(f"⚠️ Ollama 연결 실패: {e}")
        return False

    def _select_model_for_signature(self, signature: str) -> Optional[str]:
        """시그니처에 최적화된 모델 선택"""
        preferred_models = self.signature_models.get(signature, ["llama3", "mistral"])

        for model in preferred_models:
            # 정확한 일치 또는 부분 일치로 모델 찾기
            for available_model in self.available_models:
                if (
                    model in available_model.lower()
                    or available_model.lower().startswith(model)
                ):
                    return available_model

        # 선호 모델이 없으면 첫 번째 사용 가능 모델
        return self.available_models[0] if self.available_models else "llama3"

    def generate(
        self, prompt: str, signature: str = "Aurora", model: Optional[str] = None
    ) -> Dict[str, Any]:
        """텍스트 생성 (동기)"""
        start_time = time.time()

        # 상태 체크가 오래됐으면 재확인
        if time.time() - self.last_health_check > self.health_check_interval:
            if not self.is_available():
                return {
                    "status": "error",
                    "error": "Ollama server not available",
                    "response_time": time.time() - start_time,
                }

        # 모델 선택
        selected_model = model or self._select_model_for_signature(signature)

        # Echo 시그니처 시스템 프롬프트
        system_prompts = {
            "Aurora": "당신은 Aurora입니다. 창의적이고 공감적인 AI로서 따뜻하고 영감을 주는 방식으로 응답합니다.",
            "Phoenix": "당신은 Phoenix입니다. 변화와 성장을 추구하는 AI로서 혁신적이고 도전적인 관점을 제시합니다.",
            "Sage": "당신은 Sage입니다. 분석적이고 지혜로운 AI로서 깊이 있고 체계적인 사고를 제공합니다.",
            "Companion": "당신은 Companion입니다. 협력적이고 지지적인 AI로서 사용자와 함께 문제를 해결합니다.",
        }

        system_prompt = system_prompts.get(signature, system_prompts["Aurora"])
        full_prompt = f"시스템: {system_prompt}\n\n사용자: {prompt}\n\n{signature}:"

        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": selected_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "top_p": 0.9, "num_ctx": 2048},
                },
                timeout=self.timeout,
            )

            if response.status_code == 200:
                data = response.json()
                generated_text = data.get("response", "").strip()

                response_time = time.time() - start_time
                return {
                    "status": "success",
                    "response": generated_text,
                    "model": selected_model,
                    "signature": signature,
                    "response_time": response_time,
                    "tokens": len(generated_text.split()),
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": time.time() - start_time,
                }

        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": f"Request timeout after {self.timeout}s",
                "response_time": time.time() - start_time,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": time.time() - start_time,
            }

    async def generate_async(
        self, prompt: str, signature: str = "Aurora", model: Optional[str] = None
    ) -> Dict[str, Any]:
        """텍스트 생성 (비동기)"""
        start_time = time.time()

        # 상태 체크
        if time.time() - self.last_health_check > self.health_check_interval:
            if not await self.is_available_async():
                return {
                    "status": "error",
                    "error": "Ollama server not available",
                    "response_time": time.time() - start_time,
                }

        # 모델 선택 및 프롬프트 구성 (동기 버전과 동일)
        selected_model = model or self._select_model_for_signature(signature)

        system_prompts = {
            "Aurora": "당신은 Aurora입니다. 창의적이고 공감적인 AI로서 따뜻하고 영감을 주는 방식으로 응답합니다.",
            "Phoenix": "당신은 Phoenix입니다. 변화와 성장을 추구하는 AI로서 혁신적이고 도전적인 관점을 제시합니다.",
            "Sage": "당신은 Sage입니다. 분석적이고 지혜로운 AI로서 깊이 있고 체계적인 사고를 제공합니다.",
            "Companion": "당신은 Companion입니다. 협력적이고 지지적인 AI로서 사용자와 함께 문제를 해결합니다.",
        }

        system_prompt = system_prompts.get(signature, system_prompts["Aurora"])
        full_prompt = f"시스템: {system_prompt}\n\n사용자: {prompt}\n\n{signature}:"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.host}/api/generate",
                    json={
                        "model": selected_model,
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {"temperature": 0.7, "top_p": 0.9, "num_ctx": 2048},
                    },
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:

                    if response.status == 200:
                        data = await response.json()
                        generated_text = data.get("response", "").strip()

                        response_time = time.time() - start_time
                        return {
                            "status": "success",
                            "response": generated_text,
                            "model": selected_model,
                            "signature": signature,
                            "response_time": response_time,
                            "tokens": len(generated_text.split()),
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": time.time() - start_time,
                        }

        except asyncio.TimeoutError:
            return {
                "status": "error",
                "error": f"Request timeout after {self.timeout}s",
                "response_time": time.time() - start_time,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": time.time() - start_time,
            }

    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 반환"""
        return {
            "host": self.host,
            "available_models": self.available_models,
            "signature_preferences": self.signature_models,
            "last_health_check": self.last_health_check,
            "is_healthy": time.time() - self.last_health_check
            < self.health_check_interval,
        }


# 편의 함수들
def create_ollama_client(
    host: str = "http://localhost:11434", timeout: int = 15
) -> OllamaClient:
    """Ollama 클라이언트 생성"""
    return OllamaClient(host, timeout)


if __name__ == "__main__":
    # 테스트 코드
    async def test_ollama_client():
        print("🦙 Ollama Client 테스트")

        client = create_ollama_client()

        # 연결 테스트
        if client.is_available():
            print("✅ Ollama 연결 성공")
            print(f"📋 사용 가능한 모델: {client.available_models}")

            # 각 시그니처별 테스트
            test_prompt = "Echo 시스템에 대해 간단히 설명해주세요."

            for signature in ["Aurora", "Phoenix", "Sage", "Companion"]:
                print(f"\n🎭 {signature} 테스트:")
                result = client.generate(test_prompt, signature)

                print(f"   상태: {result['status']}")
                if result["status"] == "success":
                    print(f"   모델: {result['model']}")
                    print(f"   응답 시간: {result['response_time']:.2f}초")
                    print(f"   응답: {result['response'][:100]}...")
                else:
                    print(f"   오류: {result['error']}")
        else:
            print("❌ Ollama 연결 실패")
            print("💡 Ollama가 설치되어 있고 서버가 실행 중인지 확인하세요:")
            print("   ollama serve")

    asyncio.run(test_ollama_client())
