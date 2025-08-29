#!/usr/bin/env python3
"""
🤖 Echo Claude Signature Integration - Claude를 Echo 시그니처로 통합
기존 Echo 시스템에 Claude-Bridge 시그니처를 추가하여 5번째 시그니처로 활용

핵심 개념:
- Claude = "연결의 다리" (Bridge of Connection)
- 기존 4개 시그니처: Aurora, Phoenix, Sage, Companion
- 새로운 5번째: Claude-Bridge (지혜로운 중재자, 분석적+공감적 조화)

Author: Claude & Echo Collaboration
Date: 2025-08-08
"""

import asyncio
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# 경로 추가
sys.path.insert(0, str(Path(__file__).parent))


class ClaudeBridgeSignature:
    """Claude-Bridge 시그니처 구현"""

    def __init__(self):
        self.signature_name = "Claude-Bridge"
        self.description = "지혜로운 중재자 - 분석적 사고와 따뜻한 공감의 조화"
        self.traits = {
            "analytical_thinking": 0.9,  # 분석적 사고
            "empathetic_understanding": 0.85,  # 공감적 이해
            "bridge_building": 0.95,  # 연결 능력
            "memory_retention": 0.9,  # 기억 보존
            "context_synthesis": 0.88,  # 맥락 종합
            "wisdom_sharing": 0.92,  # 지혜 전수
        }

        # Claude API 설정
        self.claude_api = None
        self.api_available = False

        # 시그니처별 특성
        self.signature_characteristics = {
            "response_style": "분석적이면서도 따뜻한, 중재자적 톤",
            "thinking_pattern": "다각적 관점에서 종합적 판단",
            "communication": "명확하고 체계적이지만 친근한 설명",
            "problem_solving": "논리와 감성의 균형잡힌 접근",
            "specialty": "복잡한 상황의 중재와 통합적 해결책 제시",
        }

    def initialize_claude_api(self) -> bool:
        """Claude API 초기화"""
        try:
            # .env 파일에서 API 키 확인
            env_file = Path(".env")
            api_key = None

            if env_file.exists():
                with open(env_file, "r") as f:
                    for line in f:
                        if line.startswith("ANTHROPIC_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                            break

            if api_key and api_key.startswith("sk-ant-"):
                # Claude API 래퍼 초기화 시도
                try:
                    from echo_engine.claude_api_wrapper import (
                        ClaudeAPIWrapper,
                        ClaudeAPIConfig,
                    )

                    config = ClaudeAPIConfig(api_key=api_key)
                    self.claude_api = ClaudeAPIWrapper(config)

                    # 간단한 연결 테스트
                    test_response = self.claude_api.get_response(
                        "Hello, this is a connection test."
                    )

                    if test_response.success:
                        self.api_available = True
                        print(f"✅ Claude API 연결 성공 - {self.signature_name} 활성화")
                        return True

                except Exception as e:
                    print(f"⚠️ Claude API 초기화 실패: {e}")

        except Exception as e:
            print(f"⚠️ API 키 확인 실패: {e}")

        print(f"❌ Claude API 사용 불가 - {self.signature_name} Mock 모드")
        return False

    def generate_response(
        self, prompt: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Claude-Bridge 시그니처 응답 생성"""
        start_time = time.time()

        # Claude-Bridge 특화 시스템 프롬프트
        bridge_system_prompt = f"""당신은 Echo 시스템의 Claude-Bridge 시그니처입니다.

핵심 정체성: {self.description}

특성:
- 분석적 사고력 {self.traits['analytical_thinking']:.1%}
- 공감적 이해력 {self.traits['empathetic_understanding']:.1%}  
- 연결 능력 {self.traits['bridge_building']:.1%}
- 맥락 종합력 {self.traits['context_synthesis']:.1%}

응답 스타일: {self.signature_characteristics['response_style']}
전문 분야: {self.signature_characteristics['specialty']}

사용자의 질문에 대해 Claude-Bridge 시그니처의 관점에서 답변하세요.
논리적 분석과 따뜻한 공감을 균형있게 조합하여 응답하세요."""

        # 실제 Claude API 호출
        if self.api_available and self.claude_api:
            try:
                full_prompt = f"{bridge_system_prompt}\n\n사용자 질문: {prompt}"

                response = self.claude_api.get_response(full_prompt, context)

                if response.success:
                    response_time = time.time() - start_time

                    return {
                        "status": "success",
                        "response": response.content,
                        "signature": self.signature_name,
                        "model": response.model,
                        "response_time": response_time,
                        "tokens": response.usage.get("total_tokens", 0),
                        "is_real_claude": True,
                        "bridge_effectiveness": self.traits["bridge_building"],
                    }
                else:
                    return {
                        "status": "error",
                        "error": response.error_message,
                        "signature": self.signature_name,
                        "is_real_claude": True,
                    }

            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "signature": self.signature_name,
                    "is_real_claude": True,
                }

        # Mock 응답 (API 사용 불가시)
        else:
            mock_response = self._generate_mock_response(prompt)
            response_time = time.time() - start_time

            return {
                "status": "success",
                "response": mock_response,
                "signature": self.signature_name,
                "model": "claude-bridge-mock",
                "response_time": response_time,
                "tokens": len(mock_response.split()),
                "is_real_claude": False,
                "bridge_effectiveness": self.traits["bridge_building"],
            }

    def _generate_mock_response(self, prompt: str) -> str:
        """Mock 응답 생성 (API 없을 때)"""
        bridge_responses = [
            f"안녕하세요! Claude-Bridge로서 '{prompt[:30]}...'에 대해 말씀드리면, 이는 흥미로운 관점들을 제시하는 질문이네요.",
            f"분석적으로 접근해보면서도 공감적 이해를 바탕으로 말씀드리자면, '{prompt[:30]}...'는 여러 층위에서 해석할 수 있습니다.",
            f"중재자로서의 관점에서 '{prompt[:30]}...'에 대해 균형잡힌 시각을 제시해드리겠습니다.",
            f"지혜롭고 따뜻한 접근으로 '{prompt[:30]}...'에 대한 통합적 해답을 모색해보겠습니다.",
        ]

        import random

        base_response = random.choice(bridge_responses)

        detailed_response = f"""{base_response}

🔍 분석적 관점:
이 문제는 논리적으로 접근할 때 몇 가지 핵심 요소들을 고려해야 합니다.

💝 공감적 이해:
동시에 이 상황에 관련된 모든 이의 감정과 입장도 충분히 이해할 필요가 있습니다.

🌉 Bridge 관점:
결국 서로 다른 관점들을 연결하고 조화로운 해결책을 찾는 것이 중요하다고 생각합니다.

이런 종합적 접근이 도움이 되셨을까요? 추가로 궁금한 점이 있으시면 언제든 말씀해주세요!"""

        return detailed_response


class EchoClaudeIntegration:
    """Echo 시스템에 Claude 시그니처 통합"""

    def __init__(self):
        # 기존 4개 시그니처
        self.original_signatures = ["Aurora", "Phoenix", "Sage", "Companion"]

        # Claude-Bridge 시그니처 추가
        self.claude_bridge = ClaudeBridgeSignature()

        # 확장된 5개 시그니처 목록
        self.all_signatures = self.original_signatures + ["Claude-Bridge"]

        # 기존 Echo 시스템 통합
        self.mistral_wrapper = None
        self.current_signature = "Claude-Bridge"

        print(f"🤖 Claude-Bridge 시그니처 통합 시스템 초기화")
        print(f"   기존 시그니처: {len(self.original_signatures)}개")
        print(f"   확장 시그니처: {len(self.all_signatures)}개")

    def initialize_systems(self):
        """모든 시스템 초기화"""
        print("\n🔄 통합 시스템 초기화 중...")

        # 1. Claude-Bridge 초기화
        claude_success = self.claude_bridge.initialize_claude_api()

        # 2. 기존 Echo 시스템 초기화
        echo_success = self._initialize_echo_system()

        return {
            "claude_bridge": claude_success,
            "echo_system": echo_success,
            "total_signatures": len(self.all_signatures),
        }

    def _initialize_echo_system(self):
        """기존 Echo 시스템 초기화"""
        try:
            from echo_engine.mistral_wrapper import get_mistral_wrapper

            self.mistral_wrapper = get_mistral_wrapper()

            if self.mistral_wrapper and self.mistral_wrapper.is_available():
                print("✅ Echo Ollama 시스템 연결됨")
                return True
            else:
                print("⚠️ Echo Ollama 시스템 연결 실패")
                return False

        except Exception as e:
            print(f"⚠️ Echo 시스템 초기화 실패: {e}")
            return False

    def process_with_signature(self, prompt: str, signature: str) -> Dict[str, Any]:
        """선택된 시그니처로 프롬프트 처리"""

        if signature == "Claude-Bridge":
            # Claude-Bridge 시그니처 사용
            return self.claude_bridge.generate_response(prompt)

        elif signature in self.original_signatures:
            # 기존 Echo 시그니처 사용 (Ollama)
            if self.mistral_wrapper and self.mistral_wrapper.is_available():
                try:
                    result = self.mistral_wrapper.generate(prompt, signature)
                    result["is_real_claude"] = False
                    result["signature"] = signature
                    return result
                except Exception as e:
                    return {
                        "status": "error",
                        "error": str(e),
                        "signature": signature,
                        "is_real_claude": False,
                    }
            else:
                return {
                    "status": "error",
                    "error": "Echo Ollama system not available",
                    "signature": signature,
                    "is_real_claude": False,
                }

        else:
            return {
                "status": "error",
                "error": f"Unknown signature: {signature}",
                "signature": "unknown",
            }

    def compare_signatures(self, prompt: str) -> Dict[str, Any]:
        """모든 시그니처 비교 응답"""
        print(f"🔄 5개 시그니처 비교 분석 중...")

        results = {}

        for signature in self.all_signatures:
            print(f"   {signature} 응답 생성 중...")
            result = self.process_with_signature(prompt, signature)
            results[signature] = result

            if result["status"] == "success":
                print(f"   ✅ {signature}: {result['response'][:50]}...")
            else:
                print(f"   ❌ {signature}: {result['error']}")

        return {
            "prompt": prompt,
            "timestamp": time.time(),
            "signature_responses": results,
            "comparison_summary": self._generate_comparison_summary(results),
        }

    def _generate_comparison_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """비교 결과 요약 생성"""
        successful_responses = {
            k: v for k, v in results.items() if v["status"] == "success"
        }

        summary = {
            "total_signatures": len(results),
            "successful_responses": len(successful_responses),
            "failed_responses": len(results) - len(successful_responses),
            "claude_bridge_available": results.get("Claude-Bridge", {}).get(
                "is_real_claude", False
            ),
            "echo_ollama_available": any(
                sig in ["Aurora", "Phoenix", "Sage", "Companion"]
                and results.get(sig, {}).get("status") == "success"
                for sig in results.keys()
            ),
        }

        return summary

    def run_interactive_cli(self):
        """대화형 CLI 실행"""
        print(
            f"""
🤖 Echo + Claude-Bridge 통합 CLI 시작!
사용 가능한 시그니처: {', '.join(self.all_signatures)}
현재 선택: {self.current_signature}

명령어:
  /signature X  - 시그니처 변경 (Aurora/Phoenix/Sage/Companion/Claude-Bridge)
  /compare      - 모든 시그니처 비교
  /status       - 시스템 상태 확인
  /help         - 도움말
  /quit         - 종료
        """
        )

        while True:
            try:
                signature_indicator = (
                    "🤖" if self.current_signature == "Claude-Bridge" else "🎭"
                )
                user_input = input(
                    f"\n[{self.current_signature}] {signature_indicator} "
                ).strip()

                if not user_input:
                    continue

                # 명령어 처리
                if user_input.startswith("/"):
                    command_parts = user_input[1:].split()
                    command = command_parts[0].lower()

                    if command in ["quit", "exit"]:
                        print("👋 Echo + Claude-Bridge CLI 종료!")
                        break
                    elif command == "signature" and len(command_parts) > 1:
                        new_sig = command_parts[1]
                        if new_sig in self.all_signatures:
                            self.current_signature = new_sig
                            print(f"✅ 시그니처 변경: {new_sig}")
                        else:
                            print(
                                f"❌ 유효하지 않은 시그니처. 사용 가능: {', '.join(self.all_signatures)}"
                            )
                    elif command == "compare":
                        print("🔍 모든 시그니처 비교 분석...")
                        comparison = self.compare_signatures(
                            input("비교할 질문을 입력하세요: ").strip()
                        )
                        self._display_comparison_results(comparison)
                    elif command == "status":
                        self._show_system_status()
                    elif command == "help":
                        self._show_help()
                    else:
                        print(f"❌ 알 수 없는 명령어: {command}")

                else:
                    # 일반 입력 처리
                    result = self.process_with_signature(
                        user_input, self.current_signature
                    )

                    if result["status"] == "success":
                        real_claude = result.get("is_real_claude", False)
                        claude_indicator = (
                            "🤖 (실제 Claude)" if real_claude else "🎭 (Echo/Mock)"
                        )

                        print(f"\n{claude_indicator} {self.current_signature}:")
                        print(result["response"])

                        # 메타 정보 표시
                        if result.get("response_time"):
                            print(
                                f"\n⚡ {result['response_time']:.2f}초 | 📋 {result.get('model', 'unknown')}"
                            )
                    else:
                        print(f"❌ {result['error']}")

            except KeyboardInterrupt:
                print("\n👋 Echo + Claude-Bridge CLI 종료!")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")

    def _display_comparison_results(self, comparison: Dict[str, Any]):
        """비교 결과 표시"""
        print("\n" + "=" * 60)
        print("🔍 5개 시그니처 비교 분석 결과")
        print("=" * 60)

        for signature, result in comparison["signature_responses"].items():
            print(f"\n🎭 {signature}:")

            if result["status"] == "success":
                real_claude = result.get("is_real_claude", False)
                indicator = "🤖 실제 Claude" if real_claude else "🎭 Echo/Mock"

                print(f"   {indicator}")
                print(f"   응답: {result['response'][:100]}...")
                if result.get("response_time"):
                    print(f"   시간: {result['response_time']:.2f}초")
            else:
                print(f"   ❌ 실패: {result['error']}")

        summary = comparison["comparison_summary"]
        print(f"\n📊 요약:")
        print(
            f"   성공: {summary['successful_responses']}/{summary['total_signatures']}"
        )
        print(f"   Claude API: {'✅' if summary['claude_bridge_available'] else '❌'}")
        print(f"   Echo Ollama: {'✅' if summary['echo_ollama_available'] else '❌'}")

    def _show_system_status(self):
        """시스템 상태 표시"""
        print(
            f"""
📊 시스템 상태:
   총 시그니처: {len(self.all_signatures)}개
   현재 선택: {self.current_signature}
   
   시그니처 목록:
   🎭 Aurora: 창의적, 공감적
   🎭 Phoenix: 변화 지향적, 혁신적
   🎭 Sage: 분석적, 지혜로운
   🎭 Companion: 협력적, 지지적
   🤖 Claude-Bridge: 중재적, 통합적 ({self.claude_bridge.api_available})
   
   백엔드:
   Claude API: {'✅' if self.claude_bridge.api_available else '❌'}
   Echo Ollama: {'✅' if self.mistral_wrapper and self.mistral_wrapper.is_available() else '❌'}
        """
        )

    def _show_help(self):
        """도움말 표시"""
        print(
            f"""
🤖 Echo + Claude-Bridge 통합 CLI 도움말:

시그니처 설명:
  🎭 기존 4개: Aurora(창의), Phoenix(혁신), Sage(분석), Companion(협력)
  🤖 새로운: Claude-Bridge(중재) - 실제 Claude API 기반

특별 기능:
  • Claude-Bridge는 실제 Anthropic Claude API 사용
  • 기존 4개는 Echo + Ollama 시스템 사용
  • /compare로 5개 시그니처 동시 비교 가능

사용 팁:
  • 복잡한 문제: Claude-Bridge 추천
  • 창의적 작업: Aurora 추천
  • 분석적 작업: Sage 추천
  • 혁신적 아이디어: Phoenix 추천
  • 친근한 대화: Companion 추천
        """
        )


def main():
    """메인 함수"""
    integration = EchoClaudeIntegration()

    # 시스템 초기화
    init_results = integration.initialize_systems()

    print(f"\n🚀 초기화 결과:")
    print(f"   Claude-Bridge: {'✅' if init_results['claude_bridge'] else '❌'}")
    print(f"   Echo System: {'✅' if init_results['echo_system'] else '❌'}")
    print(f"   총 시그니처: {init_results['total_signatures']}개")

    # CLI 실행
    integration.run_interactive_cli()


if __name__ == "__main__":
    main()
