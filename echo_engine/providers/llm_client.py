# -*- coding: utf-8 -*-
"""
LLM Client with Retry/Backoff/Fallback
백오프/재시도/폴백 내장 LLM 클라이언트
"""
import time
import os
from typing import Optional, List, Dict, Any
import openai
from dataclasses import dataclass


@dataclass
class LLMProvider:
    name: str
    type: str  # 'openai', 'local'
    model: str
    max_tokens: int
    available: bool = True


class LLMClient:
    """재시도/폴백 기능 내장 LLM 클라이언트"""

    def __init__(self):
        self.providers = self._init_providers()
        self.retry_config = {"max_attempts": 2, "backoff_ms": 400}

    def _init_providers(self) -> List[LLMProvider]:
        """프로바이더 초기화"""
        providers = []
        api_key = os.getenv("OPENAI_API_KEY", "")

        # API 키 유효성 검사 (실제 OpenAI 키는 sk-로 시작하고 영숫자만 포함)
        is_valid_openai_key = (
            api_key.startswith("sk-")
            and len(api_key) > 20
            and all(c.isalnum() or c in "-_" for c in api_key)
        )

        if is_valid_openai_key:
            # Primary: OpenAI
            providers.append(
                LLMProvider(
                    name="primary", type="openai", model="gpt-3.5-turbo", max_tokens=800
                )
            )

            # Fallback1: OpenAI 다른 모델
            providers.append(
                LLMProvider(
                    name="fallback1",
                    type="openai",
                    model="gpt-3.5-turbo-1106",
                    max_tokens=800,
                )
            )
        else:
            # Mock 모드 (데모/테스트용)
            providers.append(
                LLMProvider(name="mock", type="mock", model="mock-llm", max_tokens=800)
            )

        return providers

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 800,
        temperature: float = 0.7,
    ) -> str:
        """텍스트 생성 (재시도/폴백 포함)"""

        for provider in self.providers:
            if not provider.available:
                continue

            for attempt in range(self.retry_config["max_attempts"]):
                try:
                    if provider.type == "openai":
                        result = self._call_openai(
                            prompt, model or provider.model, max_tokens, temperature
                        )
                        if result:
                            return result
                    elif provider.type == "mock":
                        result = self._call_mock(prompt, max_tokens, temperature)
                        if result:
                            return result

                except Exception as e:
                    print(f"⚠️ {provider.name} attempt {attempt + 1} failed: {e}")

                    # Rate limit 에러면 백오프
                    if "rate" in str(e).lower() or "limit" in str(e).lower():
                        time.sleep(self.retry_config["backoff_ms"] / 1000)
                        continue

                    # 다른 에러면 다음 프로바이더로
                    break

        # 모든 프로바이더 실패
        raise Exception("All LLM providers failed")

    def _call_openai(
        self, prompt: str, model: str, max_tokens: int, temperature: float
    ) -> Optional[str]:
        """OpenAI API 호출"""
        try:
            # UTF-8 완전 안전 처리 - OpenAI는 UTF-8을 완전 지원함
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=30.0)

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],  # UTF-8 직접 전달
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.choices[0].message.content.strip()

        except UnicodeEncodeError as ue:
            # UTF-8 인코딩 에러 발생 시 더 안전한 방법 시도
            try:
                # 문제 문자를 안전하게 처리
                safe_prompt = prompt.encode("utf-8", errors="replace").decode("utf-8")
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": safe_prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content.strip()
            except Exception:
                # 최후 방법: ASCII 안전 모드
                ascii_prompt = "".join(c for c in prompt if ord(c) < 128)
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": f"[Safe Mode] {ascii_prompt}"}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            raise e

    def _call_mock(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Mock LLM - 데모/테스트용 지능형 응답"""
        import random

        # 간단한 키워드 기반 응답 생성
        prompt_lower = prompt.lower()

        # NLU 요청 감지
        if "json" in prompt_lower and "intent" in prompt_lower:
            # 의료 관련 키워드 검사
            if any(
                word in prompt_lower
                for word in ["아프", "치료", "병", "증상", "의료", "health"]
            ):
                return """{
  "intent": "health",
  "domain": "의료",
  "entities": {"concern": "health_inquiry"},
  "emotion": "concern",
  "missing_info": [],
  "urgency": "medium",
  "safety_flags": ["medical_content"]
}"""
            # 개발 관련
            elif any(
                word in prompt_lower
                for word in ["코드", "프로그래밍", "개발", "code", "programming"]
            ):
                return """{
  "intent": "development",
  "domain": "개발",
  "entities": {"topic": "programming"},
  "emotion": "curiosity",
  "missing_info": [],
  "urgency": "low",
  "safety_flags": []
}"""
            # 기본 일상 대화
            else:
                return """{
  "intent": "casual",
  "domain": "일상",
  "entities": {},
  "emotion": "neutral",
  "missing_info": [],
  "urgency": "low",
  "safety_flags": []
}"""

        # Draft 생성 요청 감지
        elif "초안" in prompt_lower or "draft" in prompt_lower:
            responses = [
                "안녕하세요! 🌟 어떤 도움이 필요하시나요? 구체적으로 알려주시면 더 정확한 답변을 드릴 수 있어요.\n\n궁금한 것이 있으시다면:\n1. 상황을 자세히 설명해주세요\n2. 원하시는 결과나 목표를 알려주세요\n3. 어떤 방식의 도움을 선호하시는지 말씀해주세요\n\n함께 해결해나가요! 😊",
                "반갑습니다! ✨ 도움이 필요한 부분이 있으시군요. 어떤 주제든 함께 논의할 수 있어요.\n\n몇 가지 질문이 있어요:\n• 현재 상황이 어떤가요?\n• 어떤 결과를 기대하고 계시나요?\n• 시급한 문제인가요, 아니면 천천히 생각해볼 수 있나요?\n\n최선을 다해 도와드리겠습니다! 🤝",
            ]
            return random.choice(responses)

        # Rewrite 요청 감지
        elif (
            "다듬" in prompt_lower
            or "rewrite" in prompt_lower
            or "리라이트" in prompt_lower
        ):
            # 원본 텍스트에서 핵심 내용 추출해서 자연스럽게 다듬기
            if "안녕" in prompt_lower:
                return "안녕하세요! 😊 무엇을 도와드릴까요? 궁금한 것이나 해결하고 싶은 것이 있으시면 언제든 말씀해주세요. 함께 차근차근 알아보겠습니다! ✨"
            else:
                return "도움이 필요한 부분을 알려주시면 최선을 다해 지원해드리겠습니다. 구체적인 상황이나 질문을 공유해주시면 더 정확한 답변을 제공할 수 있어요! 🌟"

        # 일반적인 응답
        general_responses = [
            "안녕하세요! 😊 어떤 도움이 필요하신가요? 구체적으로 알려주시면 더 좋은 답변을 드릴 수 있어요!",
            "반갑습니다! ✨ 궁금한 것이 있으시면 언제든 말씀해주세요. 함께 해결해나가요!",
            "안녕하세요! 🌟 어떤 주제든 편하게 이야기해주세요. 최선을 다해 도와드리겠습니다!",
        ]
        return random.choice(general_responses)


# 전역 클라이언트 인스턴스
_client = None


def get_llm_client() -> LLMClient:
    """글로벌 LLM 클라이언트 반환"""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
