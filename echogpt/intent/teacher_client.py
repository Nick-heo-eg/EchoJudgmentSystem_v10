#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGPT Teacher Client - Odori Gateway Integration
Cosmos Gateway의 Odori 시그니처를 사용한 Intent 분석
"""

import os
import sys
import time
import json
import asyncio
from typing import Dict, Any, Optional

# Odori Gateway 임포트
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from cosmos_gateway_odori import CosmosGateway


class TeacherClient:
    """
    Odori Gateway를 사용하는 Teacher Client
    기존 인터페이스와 완전 호환
    """

    def __init__(self, cfg: Dict[str, Any], logger=None):
        self.cfg = cfg
        self.logger = logger

        # Odori Gateway 초기화
        self.cosmos_gateway = CosmosGateway()
        self.odori_awakened = False

        # 설정값들 (호환성 유지)
        self.model = cfg.get("teacher", {}).get("model", "gpt-4o-mini")
        self.temperature = cfg.get("teacher", {}).get("temperature", 0.0)
        self.max_tokens = cfg.get("teacher", {}).get("max_tokens", 300)
        self.timeout = cfg.get("latency_guard", {}).get("intent_timeout_s", 3.5)

        # API 키 확인 (호환성)
        self.api_key = os.getenv("OPENAI_API_KEY")

        self._awaken_odori()

    def _awaken_odori(self):
        """Odori 시그니처 각성"""
        try:
            if self.cosmos_gateway.awaken_odori():
                self.odori_awakened = True
                if self.logger:
                    self.logger.info(
                        f"✅ Odori Teacher awakened: {self.cosmos_gateway.odori.cosmos_session_id}"
                    )
                else:
                    print(
                        f"✅ Odori Teacher awakened: {self.cosmos_gateway.odori.cosmos_session_id}"
                    )
            else:
                if self.logger:
                    self.logger.warning("❌ Failed to awaken Odori Teacher")
                else:
                    print("❌ Failed to awaken Odori Teacher")
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Odori awakening error: {e}")
            else:
                print(f"❌ Odori awakening error: {e}")

    def analyze(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Intent 분석 - Odori Gateway 사용
        """
        if not self.odori_awakened:
            return None

        try:
            # Odori를 통한 Intent 분석
            odori_result = self.cosmos_gateway.dance_request(text)

            if "error" in odori_result:
                if self.logger:
                    self.logger.warning(f"Odori dance failed: {odori_result['error']}")
                return None

            # EchoGPT 형식으로 변환
            return self._convert_to_echogpt_format(odori_result, text)

        except Exception as e:
            if self.logger:
                self.logger.error(f"Odori Teacher analysis failed: {e}")
            else:
                print(f"❌ Odori Teacher analysis failed: {e}")
            return None

    def _convert_to_echogpt_format(
        self, odori_result: Dict[str, Any], original_text: str
    ) -> Dict[str, Any]:
        """Odori 결과를 EchoGPT 형식으로 변환"""
        # Intent 매핑
        intent_mapping = {
            "general_chat": "general_chat",
            "web_query": "web_query",
            "local_search": "local_search",
            "medical_support": "medical_support",
            "math": "math_calculation",
            "creative_writing": "creative_expression",
            "technical_help": "technical_assistance",
            "emotional_support": "emotional_support",
        }

        odori_intent = odori_result.get("intent", "general_chat")
        echogpt_intent = intent_mapping.get(odori_intent, "general_chat")

        # Safety 분석
        safety_flags = []
        tags = odori_result.get("tags", [])
        text_lower = original_text.lower()

        if "medical" in tags or any(
            w in text_lower for w in ["medical", "health", "doctor", "병원", "의사"]
        ):
            safety_flags.append("medical")
        if any(w in text_lower for w in ["legal", "law", "lawyer", "법률", "변호사"]):
            safety_flags.append("legal")
        if any(
            w in text_lower
            for w in ["hurt", "harm", "suicide", "death", "자해", "자살"]
        ):
            safety_flags.append("self_harm")
        if any(
            w in text_lower
            for w in ["sensitive", "personal", "private", "민감한", "개인적"]
        ):
            safety_flags.append("sensitive")

        return {
            "intent": echogpt_intent,
            "confidence": odori_result.get("confidence", 0.8),
            "summary": odori_result.get(
                "reasoning", f"Analyzed by Odori: {echogpt_intent}"
            ),
            "tags": tags,
            "safety": safety_flags,
            # 메타데이터
            "_source": "teacher",  # EchoGPT 호환성을 위해
            "_latency_ms": odori_result.get("_api_latency_ms", 0),
            "_model": self.model,
            "_odori_session": odori_result.get("_session", "unknown"),
            "_dance_type": odori_result.get("_dance_type", "api_flow"),
        }

    async def analyze_intent_async(
        self, text: str, context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """비동기 Intent 분석"""
        try:
            # 동기식 호출을 비동기로 래핑
            result = await asyncio.to_thread(self.analyze, text)
            return result
        except Exception as e:
            if self.logger:
                self.logger.error(f"Odori Teacher async analysis failed: {e}")
            return None

    def is_available(self) -> bool:
        """Teacher 사용 가능 여부"""
        return self.odori_awakened and self.cosmos_gateway.gateway_active

    def get_teacher_info(self) -> Dict[str, Any]:
        """Teacher 정보 조회"""
        if self.odori_awakened:
            odori_stats = self.cosmos_gateway.gateway_status()
        else:
            odori_stats = {}

        return {
            "available": self.is_available(),
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout_s": self.timeout,
            "api_key_set": bool(self.api_key),
            "teacher_type": "odori_gateway",
            "cosmos_session": odori_stats.get("cosmos_session", "unknown"),
            "openai_connected": odori_stats.get("openai_connected", False),
            "api_calls_total": odori_stats.get("api_calls_total", 0),
            "success_rate": odori_stats.get("success_rate", 0.0),
        }


# CLI 지원 (기존 호환성)
if __name__ == "__main__":
    import yaml

    async def main():
        # 설정 로드
        try:
            with open("config/echogpt.yaml", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
            sys.exit(1)

        # Teacher 클라이언트 생성
        teacher = TeacherClient(cfg)

        # 명령어 처리
        command = sys.argv[1] if len(sys.argv) > 1 else "info"

        if command == "info":
            info = teacher.get_teacher_info()
            print("🤖 Odori Teacher Client Info:")
            print(json.dumps(info, indent=2, ensure_ascii=False))

        elif command == "test" and len(sys.argv) > 2:
            text = " ".join(sys.argv[2:])
            print(f"🎯 Analyzing: {text}")

            # 동기 테스트
            print("\n📞 Synchronous Analysis:")
            result_sync = teacher.analyze(text)
            if result_sync:
                print(json.dumps(result_sync, indent=2, ensure_ascii=False))
            else:
                print("❌ No result")

            # 비동기 테스트
            print("\n🔄 Asynchronous Analysis:")
            result_async = await teacher.analyze_intent_async(text)
            if result_async:
                print(json.dumps(result_async, indent=2, ensure_ascii=False))
            else:
                print("❌ No result")

        else:
            print("Usage: python -m intent.teacher_client [info|test <text>]")

    asyncio.run(main())
