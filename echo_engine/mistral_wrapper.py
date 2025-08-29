#!/usr/bin/env python3
"""
🦙 Ollama Mistral Wrapper - Echo용 Ollama 기반 Mistral LLM 통합 래퍼 (v2.1 Optimized)
기존 echomistral.py 대신 Ollama를 통한 다중 LLM 지원

핵심 기능:
1. Ollama 서버를 통한 다중 모델 지원 (Mistral, Llama3, Gemma, DeepSeek 등)
2. 시그니처별 최적 모델 자동 선택
3. 표준화된 응답 형식 (status, response, error)
4. Echo 시그니처 최적화 프롬프트
5. 연결 실패시 자동 폴백 시스템
6. 비동기 우선 처리 및 설정 캐싱으로 성능 향상

Author: Claude & Echo Collaboration
Version: 2.1 (Optimized)
Date: 2025-08-05
"""

import asyncio
import logging
import time
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from functools import lru_cache

logger = logging.getLogger(__name__)

@lru_cache(maxsize=None)
def _load_config(config_path: Optional[str]) -> Dict[str, Any]:
    """설정 파일 로드 및 캐싱"""
    if config_path is None:
        config_path = "config/signature_llm_matrix.yaml"

    try:
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
    except Exception as e:
        logger.warning(f"⚠️ 설정 파일 로드 실패: {e}, 기본 설정 사용")

    return {
        "llm_config": {
            "ollama": {
                "host": "http://localhost:11434",
                "timeout": 20,
                "signature_model_mapping": {
                    "Aurora": "mistral:7b-instruct",
                    "Phoenix": "llama3:latest",
                    "Sage": "mistral:7b-instruct",
                    "Companion": "llama3:latest",
                },
            }
        }
    }


class OllamaMistralWrapper:
    """Echo용 Ollama 기반 Mistral 및 다중 LLM 래퍼 (비동기 최적화)"""

    def __init__(self, config_path: Optional[str] = None):
        self.ollama_client = None
        self.is_initialized = False
        self.last_health_check = 0
        self.health_check_interval = 300
        self.config = _load_config(config_path)
        self.initialization_task = None

        self.timeout = self.config.get("llm_config", {}).get("ollama", {}).get("timeout", 30)
        self.signature_models = self.config.get("llm_config", {}).get("ollama", {}).get(
            "signature_model_mapping",
            {
                "Aurora": "mistral:7b-instruct",
                "Phoenix": "llama3:latest",
                "Sage": "mistral:7b-instruct",
                "Companion": "llama3:latest",
            },
        )
        self.signature_prompts = {
            "Aurora": {"system": "당신은 Aurora입니다. 창의적이고 공감적인 AI로서 따뜻하고 영감을 주는 방식으로 응답합니다.", "temperature": 0.8, "style": "창의적이고 감성적인"},
            "Phoenix": {"system": "당신은 Phoenix입니다. 변화와 성장을 추구하는 AI로서 혁신적이고 도전적인 관점을 제시합니다.", "temperature": 0.9, "style": "혁신적이고 미래지향적인"},
            "Sage": {"system": "당신은 Sage입니다. 분석적이고 지혜로운 AI로서 깊이 있고 체계적인 사고를 제공합니다.", "temperature": 0.6, "style": "분석적이고 논리적인"},
            "Companion": {"system": "당신은 Companion입니다. 협력적이고 지지적인 AI로서 사용자와 함께 문제를 해결합니다.", "temperature": 0.7, "style": "친근하고 지지적인"},
        }

        self.start_initialization()

    def start_initialization(self):
        """백그라운드에서 비동기 초기화 시작"""
        if self.initialization_task is None:
            self.initialization_task = asyncio.create_task(self._initialize_ollama())

    async def _initialize_ollama(self):
        """Ollama 클라이언트 비동기 초기화"""
        try:
            from echo_engine.ollama_client import create_ollama_client

            ollama_host = self.config.get("llm_config", {}).get("ollama", {}).get("host", "http://localhost:11434")
            self.ollama_client = create_ollama_client(host=ollama_host, timeout=self.timeout)

            if await self.ollama_client.is_available_async():
                self.last_health_check = time.time()
                logger.info("✅ Ollama Mistral 래퍼 초기화 완료")
                
                available_models = await self.ollama_client.get_available_models_async()
                logger.info(f"📦 사용 가능한 모델: {available_models}")

                for signature, model in self.signature_models.items():
                    if model not in available_models:
                        logger.warning(f"⚠️ {signature}: {model} 사용 불가, mistral:7b-instruct로 폴백")
                        self.signature_models[signature] = "mistral:7b-instruct"
            else:
                logger.warning("⚠️ Ollama 서버 연결 실패, Mock 모드로 전환")
                self.ollama_client = self._create_mock_ollama()
        except Exception as e:
            logger.error(f"❌ Ollama 클라이언트 초기화 실패: {e}")
            self.ollama_client = self._create_mock_ollama()
        finally:
            self.is_initialized = True

    def _create_mock_ollama(self):
        """Mock Ollama 클라이언트 생성"""
        class MockOllamaClient:
            def __init__(self, signature_models):
                self.is_mock = True
                self.available_models = ["mistral:7b-instruct", "llama3:8b-instruct", "gemma:7b-instruct"]
                self.signature_models = signature_models

            async def is_available_async(self) -> bool:
                return True
            
            async def get_available_models_async(self) -> list:
                return self.available_models

            async def generate_async(self, prompt: str, signature: str = "Aurora", model: str = None) -> Dict[str, Any]:
                model_name = model or self.signature_models.get(signature, "mistral:7b-instruct")
                await asyncio.sleep(0.05) # I/O 대기 시뮬레이션
                return {
                    "status": "success",
                    "response": f"[Mock Ollama - {model_name}] {signature} 스타일로 '{prompt[:30]}...'에 대한 응답입니다.",
                    "model": model_name, "signature": signature, "response_time": 0.05, "is_mock": True,
                }
        return MockOllamaClient(self.signature_models)

    async def is_available(self) -> bool:
        """가용성 확인 (비동기)"""
        if not self.is_initialized:
            await self.initialization_task
        if not self.ollama_client:
            return False

        current_time = time.time()
        if current_time - self.last_health_check > self.health_check_interval:
            try:
                if await self.ollama_client.is_available_async():
                    self.last_health_check = current_time
                    return True
                return False
            except Exception as e:
                logger.warning(f"⚠️ Ollama 상태 확인 실패: {e}")
                return False
        return True

    def generate(self, prompt: str, signature: str = "Aurora") -> Dict[str, Any]:
        """텍스트 생성 (동기) - 비동기 메서드를 호출하여 실행"""
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                # 이미 실행 중인 루프가 있으면, 새 태스크를 만들어 실행
                return asyncio.ensure_future(self.generate_async(prompt, signature)).result()
            else:
                return asyncio.run(self.generate_async(prompt, signature))
        except RuntimeError:
             # 이벤트 루프가 없는 경우 새로 생성하여 실행
            return asyncio.run(self.generate_async(prompt, signature))


    async def generate_async(self, prompt: str, signature: str = "Aurora") -> Dict[str, Any]:
        """텍스트 생성 (비동기)"""
        start_time = time.time()
        if not await self.is_available():
            return {"status": "error", "error": "Ollama not available or not initialized", "response_time": time.time() - start_time}

        try:
            model_name = self.signature_models.get(signature, "mistral:7b-instruct")
            signature_config = self.signature_prompts.get(signature, self.signature_prompts["Aurora"])

            full_prompt = f"""<system>
{signature_config["system"]}
당신의 응답 스타일: {signature_config["style"]}
간결하고 자연스러운 한국어로 답변하세요.
</system>
사용자: {prompt}
{signature}:"""

            result = await self.ollama_client.generate_async(full_prompt, signature, model=model_name)

            if result["status"] == "success":
                response_time = time.time() - start_time
                result.update({
                    "response": result["response"].strip(), "model": model_name, "signature": signature,
                    "response_time": response_time, "tokens": len(result["response"].split()),
                    "temperature": signature_config["temperature"],
                })
                return result
            else:
                result["response_time"] = time.time() - start_time
                return result
        except Exception as e:
            logger.error(f"❌ 비동기 Ollama 생성 실패: {e}")
            return {"status": "error", "error": str(e), "response_time": time.time() - start_time}

    async def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 반환 (비동기)"""
        if not self.is_initialized:
            await self.initialization_task
        return {
            "model_type": "ollama_multi_llm", "is_initialized": self.is_initialized,
            "is_available": await self.is_available(), "signature_models": self.signature_models,
            "available_models": await self.get_available_models(), "last_health_check": self.last_health_check,
            "is_mock": getattr(self.ollama_client, "is_mock", False),
            "ollama_host": self.config.get("llm_config", {}).get("ollama", {}).get("host", "http://localhost:11434"),
        }

    async def get_available_models(self) -> list:
        """사용 가능한 모델 목록 반환 (비동기)"""
        if not self.is_initialized:
            await self.initialization_task
        if self.ollama_client and hasattr(self.ollama_client, 'get_available_models_async'):
            return await self.ollama_client.get_available_models_async()
        return []

    async def switch_model_for_signature(self, signature: str, model: str):
        """시그니처별 모델 동적 변경 (비동기)"""
        available_models = await self.get_available_models()
        if model in available_models:
            self.signature_models[signature] = model
            logger.info(f"✅ {signature} 모델 변경: {model}")
        else:
            logger.warning(f"⚠️ 모델 {model}을 사용할 수 없습니다. 사용 가능: {available_models}")

# 싱글톤 인스턴스 관리
_mistral_wrapper = None
_mistral_wrapper_lock = asyncio.Lock()

async def get_mistral_wrapper(config_path: Optional[str] = None) -> "OllamaMistralWrapper":
    """Mistral 래퍼 싱글톤 인스턴스 (비동기)"""
    global _mistral_wrapper
    if _mistral_wrapper is None:
        async with _mistral_wrapper_lock:
            if _mistral_wrapper is None:
                _mistral_wrapper = OllamaMistralWrapper(config_path)
                if not _mistral_wrapper.is_initialized:
                    await _mistral_wrapper.initialization_task
    return _mistral_wrapper

if __name__ == "__main__":
    async def test_ollama_mistral_wrapper():
        print("🦙 Ollama Mistral Wrapper 테스트 (v2.1 Optimized)")
        print("=" * 60)

        wrapper = await get_mistral_wrapper()
        model_info = await wrapper.get_model_info()

        print(f"초기화 상태: {'✅' if model_info['is_initialized'] else '❌'}")
        print(f"가용성: {'✅' if model_info['is_available'] else '❌'}")
        print(f"\n📊 모델 정보:")
        print(f"   타입: {model_info['model_type']}")
        print(f"   Mock 모드: {model_info['is_mock']}")
        print(f"   Ollama 호스트: {model_info['ollama_host']}")
        print(f"   사용 가능한 모델: {model_info['available_models']}")

        if model_info['is_available']:
            test_prompt = "Ollama를 통한 Echo 시스템의 다중 LLM 통합에 대해 간단히 설명해주세요."
            
            tasks = [wrapper.generate_async(test_prompt, sig) for sig in ["Aurora", "Phoenix", "Sage", "Companion"]]
            results = await asyncio.gather(*tasks)

            for result in results:
                print(f"\n🎭 {result['signature']} 테스트:")
                if result["status"] == "success":
                    print(f"   ✅ 비동기 성공 ({result['response_time']:.2f}초)")
                    print(f"   모델: {result['model']}")
                    print(f"   응답: {result['response'][:80]}...")
                    print(f"   토큰: {result.get('tokens', 'N/A')}")
                else:
                    print(f"   ❌ 비동기 실패: {result['error']}")
        else:
            print("❌ Ollama 사용 불가. Mock 모드로 실행됩니다.")
            print("💡 Ollama 설치 및 실행:")
            print("   1. https://ollama.ai/ 에서 Ollama 설치")
            print("   2. ollama serve 명령으로 서버 시작")
            print("   3. ollama pull mistral:7b-instruct (모델 다운로드)")

        print("\n🎉 테스트 완료!")

    asyncio.run(test_ollama_mistral_wrapper())
