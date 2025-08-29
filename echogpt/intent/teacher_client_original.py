#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGPT Teacher Client
GPT-based intent analysis (Teacher in Teacher-Student architecture)
"""
import os
import json
import re
import time
import httpx
from typing import Dict, Any, Optional


class TeacherClient:
    """GPT 기반 Intent 분석 클라이언트 (Teacher)"""

    def __init__(self, cfg: Dict[str, Any], logger=None):
        self.cfg = cfg
        self.logger = logger
        self.model = cfg["teacher"]["model"]
        self.temperature = cfg["teacher"]["temperature"]
        self.max_tokens = cfg["teacher"]["max_tokens"]
        self.timeout = cfg["latency_guard"]["intent_timeout_s"]

        # OpenAI API 키 확인
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            if self.logger:
                self.logger.warning("OPENAI_API_KEY not set - Teacher will be disabled")
            else:
                print("⚠️ OPENAI_API_KEY not set - Teacher will be disabled")

    def _build_prompt(self, text: str) -> str:
        """Intent 분석 프롬프트 생성"""
        return f"""Analyze the user input and return ONLY valid JSON with this exact structure:
{{"intent":"category","confidence":0.0,"summary":"brief description","tags":[],"safety":[]}}

Intent categories:
- medical_support: health, symptoms, medical advice
- local_search: location-based queries, maps, directions  
- web_query: general web search, information lookup
- creative_expression: writing, ideas, brainstorming
- analytical_inquiry: analysis, problem-solving, logic
- emotional_support: comfort, empathy, mental health
- collaborative_task: help with work, teamwork
- technical_assistance: coding, programming, tech help
- math_calculation: math problems, calculations
- file_operation: file reading, document processing
- general_chat: casual conversation, greetings

Safety flags (add if applicable):
- medical: medical advice disclaimer needed
- legal: legal disclaimer needed
- sensitive: sensitive topic
- self_harm: self-harm risk

INPUT: {text}

Return ONLY the JSON, no explanation."""

    def analyze(self, text: str) -> Optional[Dict[str, Any]]:
        """GPT를 통한 Intent 분석"""
        if not self.api_key:
            return None

        try:
            return self._call_openai_api(text)
        except Exception as e:
            print(f"⚠️ Teacher analysis failed: {e}")
            return None

    def _call_openai_api(self, text: str) -> Dict[str, Any]:
        """OpenAI API 호출"""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": self._build_prompt(text)}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        start_time = time.time()

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, headers=headers, json=data)
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # JSON 추출 및 파싱
            parsed_result = self._parse_response(content)

            # 응답 시간 기록
            latency_ms = int((time.time() - start_time) * 1000)
            parsed_result["_latency_ms"] = latency_ms
            parsed_result["_source"] = "teacher"
            parsed_result["_model"] = self.model

            return parsed_result

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """GPT 응답 파싱"""
        try:
            # JSON 블록 찾기
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)

                # 필수 필드 검증 및 기본값 설정
                return {
                    "intent": parsed.get("intent", "general_chat"),
                    "confidence": float(parsed.get("confidence", 0.5)),
                    "summary": parsed.get("summary", ""),
                    "tags": parsed.get("tags", []),
                    "safety": parsed.get("safety", []),
                }
            else:
                raise ValueError("No JSON found in response")

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"⚠️ Failed to parse teacher response: {e}")
            print(f"Raw content: {content[:200]}...")

            # 폴백: 단순 키워드 기반 분류
            return self._fallback_classification(content)

    def _fallback_classification(self, content: str) -> Dict[str, Any]:
        """폴백 분류 (GPT 응답 파싱 실패시)"""
        content_lower = content.lower()

        # 간단한 키워드 매칭
        if any(
            word in content_lower
            for word in ["medical", "health", "symptoms", "doctor"]
        ):
            intent = "medical_support"
        elif any(
            word in content_lower for word in ["location", "map", "directions", "near"]
        ):
            intent = "local_search"
        elif any(word in content_lower for word in ["search", "find", "lookup"]):
            intent = "web_query"
        elif any(word in content_lower for word in ["creative", "write", "idea"]):
            intent = "creative_expression"
        elif any(word in content_lower for word in ["analyze", "problem", "logic"]):
            intent = "analytical_inquiry"
        elif any(word in content_lower for word in ["help", "support", "comfort"]):
            intent = "emotional_support"
        elif any(word in content_lower for word in ["code", "programming", "tech"]):
            intent = "technical_assistance"
        elif any(word in content_lower for word in ["math", "calculate", "equation"]):
            intent = "math_calculation"
        elif any(word in content_lower for word in ["file", "document", "read"]):
            intent = "file_operation"
        else:
            intent = "general_chat"

        return {
            "intent": intent,
            "confidence": 0.6,  # 중간 신뢰도
            "summary": "Fallback classification",
            "tags": [],
            "safety": [],
        }

    async def analyze_intent_async(
        self, text: str, context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """비동기 Intent 분석"""
        if not self.api_key:
            return None

        try:
            return await self._call_openai_api_async(text, context)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Teacher async analysis failed: {e}")
            else:
                print(f"⚠️ Teacher async analysis failed: {e}")
            return None

    async def _call_openai_api_async(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """비동기 OpenAI API 호출"""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": self._build_prompt(text)}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        start_time = time.time()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # JSON 추출 및 파싱
            parsed_result = self._parse_response(content)

            # 응답 시간 기록
            latency_ms = int((time.time() - start_time) * 1000)
            parsed_result["_latency_ms"] = latency_ms
            parsed_result["_source"] = "teacher"
            parsed_result["_model"] = self.model

            return parsed_result

    def is_available(self) -> bool:
        """Teacher 사용 가능 여부"""
        return bool(self.api_key)

    def get_teacher_info(self) -> Dict[str, Any]:
        """Teacher 정보 조회"""
        return {
            "available": self.is_available(),
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout_s": self.timeout,
            "api_key_set": bool(self.api_key),
        }


# CLI 실행 지원
if __name__ == "__main__":
    import asyncio
    import sys
    import yaml
    import json

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
            print("🤖 Teacher Client Info:")
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
