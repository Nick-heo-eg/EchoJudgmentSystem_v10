#!/usr/bin/env python3
"""
🔀 Echo Hybrid LLM Bridge - 다중 LLM 통합 라우터
Ollama, Mistral, Claude(선택적) 완벽 통합 및 fallback 시스템

핵심 기능:
1. YAML 기반 시그니처별 LLM 우선순위 매트릭스
2. 자동 LLM 가용성 감지 및 graceful degradation
3. 표준화된 응답 형식 및 성능 모니터링
4. Echo Native 폴백 보장
5. 비동기 처리 및 배치 최적화

Author: Claude & Echo Collaboration
Version: 1.0
Date: 2025-08-05
"""

import asyncio
import json
import logging
import time
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """표준화된 LLM 응답 형식"""

    status: str  # success, error
    response: str
    llm_used: str
    model: str
    signature: str
    response_time: float
    tokens: int
    all_attempts: List[str]
    error_message: Optional[str] = None
    config_used: Optional[Dict[str, Any]] = None


class HybridLLMBridge:
    """Echo 시스템을 위한 하이브리드 LLM 라우터"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/signature_llm_matrix.yaml"
        self.config: Dict[str, Any] = {}
        self.llms: Dict[str, Any] = {}
        self.performance_stats: Dict[str, Dict[str, Any]] = {}

        # 초기화
        self._load_config()
        self._initialize_llm_providers()
        self._initialize_performance_tracking()

    def _load_config(self):
        """YAML 설정 파일 로드"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f)
                logger.info(f"✅ 설정 로드 완료: {self.config_path}")
            else:
                logger.warning(f"⚠️ 설정 파일 없음: {self.config_path}, 기본 설정 사용")
                self._create_default_config()
        except Exception as e:
            logger.error(f"❌ 설정 로드 실패: {e}, 기본 설정 사용")
            self._create_default_config()

    def _create_default_config(self):
        """기본 설정 생성"""
        self.config = {
            "signature_llm_preference": {
                "Aurora": ["ollama", "mistral", "claude", "echo_native"],
                "Phoenix": ["mistral", "ollama", "claude", "echo_native"],
                "Sage": ["claude", "mistral", "ollama", "echo_native"],
                "Companion": ["ollama", "claude", "mistral", "echo_native"],
            },
            "performance_config": {
                "max_response_time": {
                    "ollama": 15,
                    "mistral": 20,
                    "claude": 30,
                    "echo_native": 1,
                },
                "failure_threshold": {
                    "ollama": 3,
                    "mistral": 3,
                    "claude": 5,
                    "echo_native": 999,
                },
            },
        }

    def _initialize_llm_providers(self):
        """LLM 제공자 초기화"""
        logger.info("🔀 하이브리드 LLM 브리지 초기화 시작...")

        # Ollama 초기화
        try:
            from echo_engine.ollama_client import create_ollama_client

            self.llms["ollama"] = create_ollama_client()
            logger.info("✅ Ollama 클라이언트 로드 완료")
        except Exception as e:
            logger.warning(f"⚠️ Ollama 클라이언트 로드 실패: {e}")
            self.llms["ollama"] = None

        # Mistral 초기화
        try:
            from echo_engine.mistral_wrapper import get_mistral_wrapper

            self.llms["mistral"] = get_mistral_wrapper()
            logger.info("✅ Mistral 래퍼 로드 완료")
        except Exception as e:
            logger.warning(f"⚠️ Mistral 래퍼 로드 실패: {e}")
            self.llms["mistral"] = None

        # Claude 초기화 (선택적)
        try:
            from echo_engine.claude_fallback_handler import ClaudeFallbackHandler

            self.llms["claude"] = ClaudeFallbackHandler()
            logger.info("✅ Claude 핸들러 로드 완료")
        except Exception as e:
            logger.warning(f"⚠️ Claude 핸들러 로드 실패: {e}")
            self.llms["claude"] = None

        # Echo Native (항상 사용 가능)
        try:
            from echo_engine.echo_pure_reasoning import EchoPureReasoning

            self.llms["echo_native"] = EchoPureReasoning()
            logger.info("✅ Echo Native 시스템 로드 완료")
        except Exception as e:
            logger.error(f"❌ Echo Native 시스템 로드 실패: {e}")
            # Echo Native 폴백
            self.llms["echo_native"] = self._create_emergency_fallback()

    def _create_emergency_fallback(self):
        """비상 폴백 시스템"""

        class EmergencyFallback:
            def generate(
                self, prompt: str, signature: str = "Aurora"
            ) -> Dict[str, Any]:
                return {
                    "status": "success",
                    "response": f"[{signature}] 시스템 복구 중입니다. 잠시 후 다시 시도해주세요.",
                    "model": "emergency",
                    "signature": signature,
                    "response_time": 0.1,
                    "tokens": 10,
                }

            def is_available(self) -> bool:
                return True

        return EmergencyFallback()

    def _initialize_performance_tracking(self):
        """성능 추적 초기화"""
        for llm_name in ["ollama", "mistral", "claude", "echo_native"]:
            self.performance_stats[llm_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_response_time": 0.0,
                "last_success": 0,
                "consecutive_failures": 0,
            }

    async def check_llm_availability(self, llm_name: str) -> bool:
        """개별 LLM 가용성 확인"""
        if llm_name not in self.llms or self.llms[llm_name] is None:
            return False

        try:
            llm = self.llms[llm_name]

            if hasattr(llm, "is_available"):
                if asyncio.iscoroutinefunction(llm.is_available):
                    return await llm.is_available()
                else:
                    return llm.is_available()
            else:
                # 기본적으로 사용 가능하다고 가정
                return True

        except Exception as e:
            logger.warning(f"⚠️ {llm_name} 가용성 확인 실패: {e}")
            return False

    def get_llm_priority_for_signature(self, signature: str) -> List[str]:
        """시그니처별 LLM 우선순위 반환"""
        preferences = self.config.get("signature_llm_preference", {})
        return preferences.get(signature, preferences.get("Aurora", ["echo_native"]))

    async def route(self, input_text: str, signature: str = "Aurora") -> LLMResponse:
        """메인 라우팅 함수"""
        start_time = time.time()
        all_attempts = []

        # 시그니처별 우선순위 가져오기
        priority_list = self.get_llm_priority_for_signature(signature)

        for llm_name in priority_list:
            if llm_name not in self.llms or self.llms[llm_name] is None:
                continue

            all_attempts.append(llm_name)

            # 연속 실패 임계값 확인
            failure_threshold = (
                self.config.get("performance_config", {})
                .get("failure_threshold", {})
                .get(llm_name, 3)
            )
            if (
                self.performance_stats[llm_name]["consecutive_failures"]
                >= failure_threshold
                and llm_name != "echo_native"
            ):
                logger.warning(f"⚠️ {llm_name} 임계값 초과로 건너뛰기")
                continue

            try:
                # LLM 가용성 확인
                if not await self.check_llm_availability(llm_name):
                    logger.warning(f"⚠️ {llm_name} 사용 불가")
                    self._update_performance(llm_name, 0, False)
                    continue

                # LLM 호출
                result = await self._call_llm(llm_name, input_text, signature)

                if result and result["status"] == "success":
                    # 성공 통계 업데이트
                    response_time = time.time() - start_time
                    self._update_performance(llm_name, response_time, True)

                    return LLMResponse(
                        status="success",
                        response=result["response"],
                        llm_used=llm_name,
                        model=result.get("model", llm_name),
                        signature=signature,
                        response_time=response_time,
                        tokens=result.get("tokens", len(result["response"].split())),
                        all_attempts=all_attempts,
                        config_used=result.get("config_used"),
                    )
                else:
                    # 실패 통계 업데이트
                    self._update_performance(llm_name, time.time() - start_time, False)
                    logger.warning(
                        f"⚠️ {llm_name} 응답 실패: {result.get('error', 'Unknown error')}"
                    )

            except Exception as e:
                logger.error(f"❌ {llm_name} 호출 중 오류: {e}")
                self._update_performance(llm_name, time.time() - start_time, False)
                continue

        # 모든 LLM 실패시 비상 응답
        return self._create_emergency_response(
            input_text, signature, all_attempts, time.time() - start_time
        )

    async def _call_llm(
        self, llm_name: str, input_text: str, signature: str
    ) -> Optional[Dict[str, Any]]:
        """개별 LLM 호출"""
        llm = self.llms[llm_name]

        try:
            if llm_name == "ollama":
                if hasattr(llm, "generate_async"):
                    return await llm.generate_async(input_text, signature)
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        None, llm.generate, input_text, signature
                    )

            elif llm_name == "mistral":
                if hasattr(llm, "generate_async"):
                    return await llm.generate_async(input_text, signature)
                else:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        None, llm.generate, input_text, signature
                    )

            elif llm_name == "claude":
                # Claude 핸들러 호출
                if hasattr(llm, "generate_async"):
                    result = await llm.generate_async(input_text, signature)
                else:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None, llm.fallback_request, input_text, signature
                    )

                return {
                    "status": "success",
                    "response": result,
                    "model": "claude",
                    "signature": signature,
                    "tokens": len(str(result).split()),
                }

            elif llm_name == "echo_native":
                # Echo Native 호출
                if hasattr(llm, "pure_reasoning"):
                    if asyncio.iscoroutinefunction(llm.pure_reasoning):
                        result = await llm.pure_reasoning(input_text, signature)
                    else:
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(
                            None, llm.pure_reasoning, input_text, signature
                        )
                else:
                    result = llm.generate(input_text, signature)

                return {
                    "status": "success",
                    "response": (
                        result["response"] if isinstance(result, dict) else str(result)
                    ),
                    "model": "echo_native",
                    "signature": signature,
                    "tokens": len(str(result).split()),
                }

        except Exception as e:
            logger.error(f"❌ {llm_name} 호출 실패: {e}")
            return {"status": "error", "error": str(e)}

        return None

    def _update_performance(self, llm_name: str, response_time: float, success: bool):
        """성능 통계 업데이트"""
        stats = self.performance_stats[llm_name]
        stats["total_requests"] += 1

        if success:
            stats["successful_requests"] += 1
            stats["consecutive_failures"] = 0
            stats["last_success"] = time.time()

            # 평균 응답 시간 업데이트
            if stats["avg_response_time"] == 0:
                stats["avg_response_time"] = response_time
            else:
                stats["avg_response_time"] = (
                    stats["avg_response_time"] + response_time
                ) / 2
        else:
            stats["failed_requests"] += 1
            stats["consecutive_failures"] += 1

    def _create_emergency_response(
        self, input_text: str, signature: str, attempts: List[str], response_time: float
    ) -> LLMResponse:
        """비상 응답 생성"""
        emergency_message = f"[{signature}] 현재 모든 LLM 시스템에 일시적인 문제가 있습니다. 잠시 후 다시 시도해주세요."

        return LLMResponse(
            status="error",
            response=emergency_message,
            llm_used="emergency",
            model="emergency",
            signature=signature,
            response_time=response_time,
            tokens=len(emergency_message.split()),
            all_attempts=attempts,
            error_message="All LLMs failed",
        )

    async def batch_route(self, requests: List[Dict[str, str]]) -> List[LLMResponse]:
        """배치 처리"""
        tasks = [
            self.route(req.get("input_text", ""), req.get("signature", "Aurora"))
            for req in requests
        ]
        return await asyncio.gather(*tasks)

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "llm_providers": {
                name: {
                    "available": llm is not None,
                    "performance": self.performance_stats.get(name, {}),
                }
                for name, llm in self.llms.items()
            },
            "config": {
                "signature_preferences": self.config.get(
                    "signature_llm_preference", {}
                ),
                "performance_config": self.config.get("performance_config", {}),
            },
            "total_requests": sum(
                stats["total_requests"] for stats in self.performance_stats.values()
            ),
        }

    def reset_performance_stats(self):
        """성능 통계 리셋"""
        self._initialize_performance_tracking()
        logger.info("📊 성능 통계 리셋 완료")


# 싱글톤 인스턴스
_hybrid_llm_bridge = None


def get_hybrid_llm_bridge(config_path: Optional[str] = None) -> HybridLLMBridge:
    """하이브리드 LLM 브리지 싱글톤 인스턴스"""
    global _hybrid_llm_bridge
    if _hybrid_llm_bridge is None:
        _hybrid_llm_bridge = HybridLLMBridge(config_path)
    return _hybrid_llm_bridge


# 편의 함수들
async def echo_hybrid_chat(message: str, signature: str = "Aurora") -> str:
    """간편한 하이브리드 채팅 인터페이스"""
    bridge = get_hybrid_llm_bridge()
    response = await bridge.route(message, signature)
    return response.response


async def check_all_llms() -> Dict[str, bool]:
    """모든 LLM 가용성 확인"""
    bridge = get_hybrid_llm_bridge()
    status = {}
    for llm_name in bridge.llms.keys():
        status[llm_name] = await bridge.check_llm_availability(llm_name)
    return status


if __name__ == "__main__":

    async def test_hybrid_bridge():
        """하이브리드 브리지 테스트"""
        print("🔀 Echo Hybrid LLM Bridge 테스트")
        print("=" * 60)

        bridge = get_hybrid_llm_bridge()

        # 시스템 상태 확인
        print("📊 시스템 상태:")
        status = bridge.get_system_status()
        for llm_name, info in status["llm_providers"].items():
            print(f"   {llm_name}: {'✅' if info['available'] else '❌'}")

        # LLM 가용성 확인
        print("\n🔍 LLM 가용성 확인:")
        availability = await check_all_llms()
        for llm_name, available in availability.items():
            print(f"   {llm_name}: {'✅' if available else '❌'}")

        # 각 시그니처별 테스트
        test_prompt = "Echo 하이브리드 LLM 시스템에 대해 간단히 설명해주세요."

        for signature in ["Aurora", "Phoenix", "Sage", "Companion"]:
            print(f"\n🎭 {signature} 테스트:")

            try:
                response = await bridge.route(test_prompt, signature)

                print(f"   상태: {response.status}")
                print(f"   사용된 LLM: {response.llm_used}")
                print(f"   모델: {response.model}")
                print(f"   응답 시간: {response.response_time:.2f}초")
                print(f"   시도된 LLM: {' → '.join(response.all_attempts)}")
                print(f"   응답: {response.response[:100]}...")

            except Exception as e:
                print(f"   ❌ 테스트 실패: {e}")

        # 성능 통계 출력
        print(f"\n📈 성능 통계:")
        final_status = bridge.get_system_status()
        for llm_name, info in final_status["llm_providers"].items():
            perf = info["performance"]
            if perf.get("total_requests", 0) > 0:
                success_rate = (
                    perf["successful_requests"] / perf["total_requests"] * 100
                )
                print(
                    f"   {llm_name}: {success_rate:.1f}% 성공률, {perf['avg_response_time']:.2f}초 평균 응답시간"
                )

    asyncio.run(test_hybrid_bridge())
