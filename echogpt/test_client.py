#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoGPT Test Client
FastAPI 서버 테스트용 클라이언트
"""
import asyncio
import json
import sys
from typing import Dict, Any

import httpx


class EchoGPTClient:
    """EchoGPT API 클라이언트"""

    def __init__(self, base_url: str = "http://127.0.0.1:9001"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def chat_completion(
        self, messages: list, model: str = "echogpt-1.0"
    ) -> Dict[str, Any]:
        """ChatGPT 호환 채팅 완료"""
        url = f"{self.base_url}/v1/chat/completions"

        data = {
            "messages": messages,
            "model": model,
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        response = await self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()

    async def analyze_intent(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Intent 분석"""
        url = f"{self.base_url}/v1/intent/analyze"

        data = {"text": text, "context": context or {}}

        response = await self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()

    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        url = f"{self.base_url}/v1/system/status"

        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def trigger_training(self) -> Dict[str, Any]:
        """온라인 학습 트리거"""
        url = f"{self.base_url}/v1/system/train"

        response = await self.client.post(url)
        response.raise_for_status()
        return response.json()

    async def reload_model(self) -> Dict[str, Any]:
        """Student 모델 리로드"""
        url = f"{self.base_url}/v1/system/reload"

        response = await self.client.post(url)
        response.raise_for_status()
        return response.json()

    async def get_intent_labels(self) -> Dict[str, Any]:
        """Intent 라벨 목록 조회"""
        url = f"{self.base_url}/v1/debug/labels"

        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def close(self):
        """클라이언트 종료"""
        await self.client.aclose()


async def run_tests():
    """테스트 실행"""
    client = EchoGPTClient()

    print("🚀 EchoGPT Client Test Suite")
    print("=" * 50)

    try:
        # 1. 시스템 상태 확인
        print("\n1️⃣ System Status Check")
        try:
            status = await client.get_system_status()
            print(f"   Status: {status['status']}")
            print(f"   Pipeline Mode: {status['pipeline'].get('mode', 'N/A')}")
            print(
                f"   Teacher Available: {status['pipeline'].get('teacher_available', 'N/A')}"
            )
            print(
                f"   Student Available: {status['pipeline'].get('student_available', 'N/A')}"
            )
        except Exception as e:
            print(f"   ❌ Status check failed: {e}")

        # 2. Intent 라벨 확인
        print("\n2️⃣ Intent Labels")
        try:
            labels = await client.get_intent_labels()
            print(f"   Found {labels.get('count', 0)} labels")
            if "labels" in labels:
                print(f"   Sample labels: {labels['labels'][:5]}")
        except Exception as e:
            print(f"   ❌ Labels check failed: {e}")

        # 3. Intent 분석 테스트
        print("\n3️⃣ Intent Analysis Test")
        test_texts = [
            "안녕하세요! 근처 소아과 찾아주세요",
            "오늘 날씨는 어때요?",
            "2 + 2는 얼마인가요?",
            "슬픈 일이 있어서 위로가 필요해요",
        ]

        for i, text in enumerate(test_texts, 1):
            try:
                result = await client.analyze_intent(text)
                print(f"   [{i}] '{text[:30]}...'")
                print(f"       Intent: {result['intent']} ({result['confidence']:.3f})")
                print(
                    f"       Source: {result['source']} | Latency: {result['latency_ms']}ms"
                )
                if result.get("tags"):
                    print(f"       Tags: {result['tags']}")
            except Exception as e:
                print(f"   ❌ Analysis failed for text {i}: {e}")

        # 4. ChatGPT 호환 API 테스트
        print("\n4️⃣ ChatGPT Compatible API Test")
        chat_messages = [
            {"role": "user", "content": "안녕하세요! 근처 병원 찾아주세요"}
        ]

        try:
            response = await client.chat_completion(chat_messages)
            print(f"   Response ID: {response['id']}")
            print(f"   Model: {response['model']}")
            print(
                f"   Content: {response['choices'][0]['message']['content'][:100]}..."
            )
            print(f"   Usage: {response['usage']['total_tokens']} tokens")
        except Exception as e:
            print(f"   ❌ Chat completion failed: {e}")

        # 5. 시스템 관리 기능 테스트
        print("\n5️⃣ System Management Test")

        # 모델 리로드 테스트
        try:
            reload_result = await client.reload_model()
            print(f"   Model Reload: {'✅' if reload_result['success'] else '❌'}")
        except Exception as e:
            print(f"   ❌ Model reload failed: {e}")

        # 학습 트리거 테스트 (백그라운드)
        try:
            train_result = await client.trigger_training()
            print(f"   Training Trigger: {train_result['status']}")
        except Exception as e:
            print(f"   ❌ Training trigger failed: {e}")

        print("\n✅ Test Suite Completed!")

    except httpx.ConnectError:
        print(
            "❌ Cannot connect to EchoGPT server. Make sure it's running on http://127.0.0.1:9001"
        )
        print("   To start the server: python server.py")

    except Exception as e:
        print(f"❌ Test suite failed: {e}")

    finally:
        await client.close()


async def interactive_chat():
    """인터랙티브 채팅 모드"""
    client = EchoGPTClient()

    print("🤖 EchoGPT Interactive Chat")
    print(
        "Type 'quit' to exit, 'status' for system info, 'intent <text>' for intent analysis"
    )
    print("=" * 60)

    try:
        while True:
            user_input = input("\n👤 You: ").strip()

            if user_input.lower() in ["quit", "exit", "bye"]:
                print("👋 Goodbye!")
                break

            elif user_input.lower() == "status":
                try:
                    status = await client.get_system_status()
                    print(f"📊 System Status: {status['status']}")
                    print(f"   Pipeline: {status['pipeline']['mode']}")
                    print(f"   Uptime: {status['pipeline'].get('uptime_s', 0):.1f}s")
                    metrics = status["metrics"]["quality"]
                    print(
                        f"   Requests: {metrics['total_requests']}, Agreement: {metrics['intent_agree_rate']:.1%}"
                    )
                except Exception as e:
                    print(f"❌ Status error: {e}")
                continue

            elif user_input.lower().startswith("intent "):
                text = user_input[7:]  # Remove 'intent ' prefix
                try:
                    result = await client.analyze_intent(text)
                    print(
                        f"🎯 Intent: {result['intent']} (confidence: {result['confidence']:.3f})"
                    )
                    print(
                        f"   Source: {result['source']} | Latency: {result['latency_ms']}ms"
                    )
                    print(f"   Summary: {result['summary']}")
                except Exception as e:
                    print(f"❌ Intent analysis error: {e}")
                continue

            elif not user_input:
                continue

            # 일반 채팅
            try:
                messages = [{"role": "user", "content": user_input}]
                response = await client.chat_completion(messages)

                assistant_message = response["choices"][0]["message"]["content"]
                print(f"🤖 EchoGPT: {assistant_message}")

            except Exception as e:
                print(f"❌ Chat error: {e}")

    except KeyboardInterrupt:
        print("\n👋 Chat interrupted. Goodbye!")

    except Exception as e:
        print(f"❌ Chat session failed: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "test"

    if command == "test":
        asyncio.run(run_tests())
    elif command == "chat":
        asyncio.run(interactive_chat())
    else:
        print("Usage: python test_client.py [test|chat]")
        print("  test: Run automated test suite")
        print("  chat: Start interactive chat session")
