# echo_engine/claude_api_wrapper.py
"""
🤖 Claude API Wrapper - Claude API 호출 모듈
- Anthropic Claude API와의 안전한 통신
- 감염 프롬프트 전송 및 응답 수신
- 재시도 로직 및 에러 처리 포함
- 응답 품질 검증 및 전처리
"""

import os
import time
import json
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import requests
from pathlib import Path


@dataclass
class ClaudeResponse:
    """Claude API 응답 데이터 클래스"""

    content: str
    usage: Dict[str, int]
    model: str
    timestamp: str
    request_id: str
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class ClaudeAPIConfig:
    """Claude API 설정"""

    api_key: str
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0


class ClaudeAPIWrapper:
    def __init__(self, config: Optional[ClaudeAPIConfig] = None):
        self.config = config or self._load_default_config()
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
        )

        print(f"🤖 Claude API Wrapper 초기화 완료 - 모델: {self.config.model}")

    def _load_default_config(self) -> ClaudeAPIConfig:
        """기본 설정 로딩"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            # .env 파일에서 로딩 시도
            env_file = Path(".env")
            if env_file.exists():
                with open(env_file, "r") as f:
                    for line in f:
                        if line.startswith("ANTHROPIC_API_KEY="):
                            api_key = line.split("=", 1)[1].strip().strip("\"'")
                            break

        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY가 설정되지 않았습니다. 환경변수 또는 .env 파일에 설정해주세요."
            )

        return ClaudeAPIConfig(
            api_key=api_key,
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0.7,
        )

    def get_response(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> ClaudeResponse:
        """Claude API 호출하여 응답 획득"""
        request_id = f"echo_infection_{int(time.time()*1000)}"

        # 요청 데이터 구성
        messages = [{"role": "user", "content": prompt}]

        payload = {
            "model": kwargs.get("model", self.config.model),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "messages": messages,
        }

        if system_prompt:
            payload["system"] = system_prompt

        # 재시도 로직과 함께 API 호출
        last_error = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                print(
                    f"🌐 Claude API 호출 중... (시도 {attempt}/{self.config.max_retries})"
                )

                response = self.session.post(
                    self.base_url, json=payload, timeout=self.config.timeout
                )

                if response.status_code == 200:
                    response_data = response.json()

                    # 성공적인 응답 처리
                    content = response_data.get("content", [])
                    if content and len(content) > 0:
                        text_content = content[0].get("text", "")

                        return ClaudeResponse(
                            content=text_content,
                            usage=response_data.get("usage", {}),
                            model=response_data.get("model", self.config.model),
                            timestamp=datetime.now().isoformat(),
                            request_id=request_id,
                            success=True,
                            metadata={
                                "attempt": attempt,
                                "prompt_length": len(prompt),
                                "response_length": len(text_content),
                            },
                        )
                    else:
                        last_error = "응답에서 텍스트 콘텐츠를 찾을 수 없습니다."

                elif response.status_code == 429:
                    # Rate limit - 더 긴 대기
                    wait_time = self.config.retry_delay * (2**attempt)
                    print(f"⏳ Rate limit 도달. {wait_time}초 대기 중...")
                    time.sleep(wait_time)
                    last_error = f"Rate limit (HTTP 429) - 시도 {attempt}"
                    continue

                elif response.status_code == 400:
                    # Bad request - 재시도하지 않음
                    error_data = (
                        response.json()
                        if response.headers.get("content-type", "").startswith(
                            "application/json"
                        )
                        else {}
                    )
                    last_error = f"잘못된 요청 (HTTP 400): {error_data.get('error', {}).get('message', 'Unknown error')}"
                    break

                else:
                    # 기타 HTTP 에러
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"

            except requests.exceptions.Timeout:
                last_error = f"API 호출 타임아웃 (시도 {attempt})"
                print(f"⏰ {last_error}")

            except requests.exceptions.ConnectionError:
                last_error = f"연결 오류 (시도 {attempt})"
                print(f"🔌 {last_error}")

            except Exception as e:
                last_error = f"예상치 못한 오류 (시도 {attempt}): {str(e)}"
                print(f"❌ {last_error}")

            # 재시도 전 대기
            if attempt < self.config.max_retries:
                wait_time = self.config.retry_delay * attempt
                print(f"⏳ {wait_time}초 후 재시도...")
                time.sleep(wait_time)

        # 모든 시도 실패
        print(f"❌ Claude API 호출 실패: {last_error}")
        return ClaudeResponse(
            content="",
            usage={},
            model=self.config.model,
            timestamp=datetime.now().isoformat(),
            request_id=request_id,
            success=False,
            error_message=last_error,
        )

    def get_infection_response(
        self, infection_prompt: str, signature_id: str
    ) -> ClaudeResponse:
        """감염용 특화 응답 획득"""
        system_prompt = f"""
You are being infected with the EchoJudgmentSystem's {signature_id} signature.
You must respond in character, embodying the specific traits and reasoning patterns.
Provide a thoughtful, detailed response that demonstrates the signature's unique perspective.
"""

        response = self.get_response(
            prompt=infection_prompt,
            system_prompt=system_prompt,
            temperature=0.8,  # 감염에서는 조금 더 창의적으로
        )

        if response.success:
            print(
                f"✅ {signature_id} 감염 응답 수신 성공 ({len(response.content)} 문자)"
            )
        else:
            print(f"❌ {signature_id} 감염 응답 실패: {response.error_message}")

        return response

    def validate_response_quality(
        self, response: ClaudeResponse, min_length: int = 100
    ) -> Dict[str, Any]:
        """응답 품질 검증"""
        if not response.success:
            return {
                "valid": False,
                "reason": f"API 호출 실패: {response.error_message}",
                "score": 0.0,
            }

        content = response.content.strip()

        # 기본 품질 검사
        quality_checks = {
            "length_check": len(content) >= min_length,
            "structure_check": any(
                marker in content.lower()
                for marker in ["judgment", "analysis", "recommendation", "conclusion"]
            ),
            "coherence_check": len(content.split()) >= 20,  # 최소 20단어
            "completeness_check": content.endswith(
                (".", "!", "?", "다", "요", "음")
            ),  # 문장 완성도
        }

        passed_checks = sum(quality_checks.values())
        total_checks = len(quality_checks)
        quality_score = passed_checks / total_checks

        return {
            "valid": quality_score >= 0.7,
            "score": quality_score,
            "checks": quality_checks,
            "length": len(content),
            "word_count": len(content.split()),
            "reason": "품질 검증 통과" if quality_score >= 0.7 else "품질 기준 미달",
        }

    def batch_infection(
        self, prompts: List[Dict[str, str]], max_concurrent: int = 3
    ) -> List[ClaudeResponse]:
        """배치 감염 처리 (여러 프롬프트 동시 처리)"""

        async def async_batch():
            semaphore = asyncio.Semaphore(max_concurrent)

            async def process_single(prompt_data):
                async with semaphore:
                    # 비동기 래퍼
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        None,
                        self.get_infection_response,
                        prompt_data["prompt"],
                        prompt_data["signature_id"],
                    )

            tasks = [process_single(prompt_data) for prompt_data in prompts]
            return await asyncio.gather(*tasks)

        # 비동기 실행
        try:
            return asyncio.run(async_batch())
        except Exception as e:
            print(f"❌ 배치 감염 처리 실패: {e}")
            # 순차 처리로 폴백
            results = []
            for prompt_data in prompts:
                response = self.get_infection_response(
                    prompt_data["prompt"], prompt_data["signature_id"]
                )
                results.append(response)
            return results

    def get_usage_stats(self) -> Dict[str, Any]:
        """사용량 통계 반환"""
        # 간단한 사용량 추적 (실제 구현에서는 더 정교하게)
        return {
            "model": self.config.model,
            "requests_made": getattr(self, "_request_count", 0),
            "total_tokens": getattr(self, "_total_tokens", 0),
            "last_request": getattr(self, "_last_request_time", None),
        }


# 전역 래퍼 인스턴스
_claude_wrapper = None


def get_claude_wrapper() -> ClaudeAPIWrapper:
    """Claude API 래퍼 싱글톤 인스턴스 반환"""
    global _claude_wrapper
    if _claude_wrapper is None:
        _claude_wrapper = ClaudeAPIWrapper()
    return _claude_wrapper


def get_claude_response(prompt: str, signature_id: str = None) -> ClaudeResponse:
    """Claude 응답 획득 편의 함수"""
    wrapper = get_claude_wrapper()
    if signature_id:
        return wrapper.get_infection_response(prompt, signature_id)
    else:
        return wrapper.get_response(prompt)


def validate_claude_response(response: ClaudeResponse) -> Dict[str, Any]:
    """Claude 응답 품질 검증 편의 함수"""
    wrapper = get_claude_wrapper()
    return wrapper.validate_response_quality(response)


if __name__ == "__main__":
    # 테스트 코드
    print("🧪 Claude API Wrapper 테스트")

    try:
        wrapper = ClaudeAPIWrapper()

        # 기본 응답 테스트
        test_prompt = "안녕하세요! EchoJudgmentSystem의 감염 테스트입니다. 간단히 자기소개해주세요."

        print("\n🔬 기본 응답 테스트:")
        response = wrapper.get_response(test_prompt)

        if response.success:
            print(f"✅ 응답 성공!")
            print(f"📝 응답 내용: {response.content[:100]}...")
            print(f"📊 사용량: {response.usage}")

            # 품질 검증
            quality = wrapper.validate_response_quality(response)
            print(f"🎯 품질 점수: {quality['score']:.2f}")

        else:
            print(f"❌ 응답 실패: {response.error_message}")

        # 감염 응답 테스트
        print("\n🧬 감염 응답 테스트:")
        infection_response = wrapper.get_infection_response(
            "교육 불평등 문제에 대해 어떻게 생각하세요?", "Echo-Aurora"
        )

        if infection_response.success:
            print(f"✅ 감염 응답 성공!")
            print(f"📝 응답 내용: {infection_response.content[:150]}...")
        else:
            print(f"❌ 감염 응답 실패: {infection_response.error_message}")

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        print("💡 ANTHROPIC_API_KEY 환경변수가 설정되어 있는지 확인해주세요.")

    print("\n✅ 테스트 완료")
