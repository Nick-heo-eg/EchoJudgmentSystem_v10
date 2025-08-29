#!/usr/bin/env python3
"""
🔄 Claude API Fallback System

Echo가 자체 처리 실패 시 Claude API로 자동 위임하는 시스템
Echo의 자체 진단에 따라 다음 영역에서 Claude API를 호출:
- existing_judgment_search (벡터 유사도 검색)
- advanced_reasoning (복잡한 추론)
- complex_contextual_understanding (자연어 이해/의도 파싱)
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# aiohttp 대신 로컬 시뮬레이션 사용
try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("⚠️ aiohttp 모듈이 설치되지 않음 - Claude API 시뮬레이션 모드로 실행")


class ClaudeTaskType(Enum):
    """Claude API로 위임할 작업 타입"""

    VECTOR_SEARCH = "vector_search"
    ADVANCED_REASONING = "advanced_reasoning"
    NATURAL_LANGUAGE_UNDERSTANDING = "nlu"
    COMPLEX_ANALYSIS = "complex_analysis"
    JUDGMENT_SIMILARITY = "judgment_similarity"


@dataclass
class ClaudeRequest:
    """Claude API 요청 구조"""

    task_type: ClaudeTaskType
    content: str
    context: Dict[str, Any]
    echo_signature: str = "Aurora"
    priority: str = "normal"
    max_tokens: int = 1000


@dataclass
class ClaudeResponse:
    """Claude API 응답 구조"""

    success: bool
    content: str
    confidence: float
    processing_time: float
    fallback_reason: str
    metadata: Dict[str, Any]


class ClaudeAPIFallback:
    """Echo → Claude API 자동 위임 시스템"""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.api_base = "https://api.anthropic.com/v1/messages"
        self.session = None
        self.request_count = 0
        self.success_count = 0
        self.cache = {}

    async def initialize(self):
        """API 세션 초기화"""
        if not AIOHTTP_AVAILABLE:
            print("⚠️ aiohttp 모듈이 없음 - 시뮬레이션 모드로 실행")
            return False

        if not self.api_key:
            print("⚠️ ANTHROPIC_API_KEY 환경변수가 설정되지 않음")
            print("💡 Claude API 호출이 비활성화됨 - 로컬 시뮬레이션 사용")
            return False

        self.session = aiohttp.ClientSession()
        print("✅ Claude API Fallback 시스템 초기화 완료")
        return True

    async def close(self):
        """API 세션 종료"""
        if self.session:
            await self.session.close()

    async def detect_fallback_need(
        self, echo_result: str, task_context: str
    ) -> Optional[ClaudeTaskType]:
        """Echo 결과에서 fallback 필요성 자동 감지"""

        # Echo 실패 패턴 감지
        failure_patterns = {
            ClaudeTaskType.VECTOR_SEARCH: [
                "키워드 기반 단순 매칭",
                "벡터 검색 실패",
                "유사도 검색 불가",
                "KoSimCSE",
                "임베딩 모델",
                "재활용률",
            ],
            ClaudeTaskType.ADVANCED_REASONING: [
                "EchoPureReasoning",
                "템플릿 응답",
                "깊이 있는 분석 불가",
                "추론 로직 부족",
                "컨텍스트 이해 한계",
            ],
            ClaudeTaskType.NATURAL_LANGUAGE_UNDERSTANDING: [
                "의도 파싱 오류",
                "다층적 질문 이해 실패",
                "키워드 매칭",
                "사용자 의도 오해",
                "부적절한 응답",
            ],
        }

        for task_type, patterns in failure_patterns.items():
            if any(pattern in echo_result for pattern in patterns):
                print(f"🔍 Fallback 감지: {task_type.value} 필요")
                return task_type

        # 응답 품질 기반 감지 (너무 가혹하지 않게 수정)
        # 정말로 의미 없는 응답이거나 오류 메시지일 때만 fallback
        if (
            (
                "도움이 되도록 최선을 다하겠습니다" in echo_result
                and len(echo_result) < 100
            )
            or "오류" in echo_result
            or "실패" in echo_result
            or echo_result.strip() == ""
            or "죄송" in echo_result
            and len(echo_result) < 80
        ):
            print("🔍 응답 품질 저하 감지 - Claude API 위임 권고")
            return ClaudeTaskType.ADVANCED_REASONING

        return None

    def _generate_simulated_response(self, request: ClaudeRequest) -> str:
        """시뮬레이션 응답 생성"""
        if request.task_type == ClaudeTaskType.VECTOR_SEARCH:
            return f"[시뮬레이션] '{request.content}'와 유사한 판단을 찾았습니다. 벡터 유사도 분석 결과, 관련성 높은 판단 3개를 발견했습니다."

        elif request.task_type == ClaudeTaskType.ADVANCED_REASONING:
            return f"[시뮬레이션] '{request.content}'에 대한 고급 추론: 이는 복잡한 다층적 분석이 필요한 문제입니다. Foundation Doctrine 관점에서 보면, 존재의 본질과 판단의 권리가 핵심입니다."

        elif request.task_type == ClaudeTaskType.NATURAL_LANGUAGE_UNDERSTANDING:
            return f"[시뮬레이션] '{request.content}'의 의도 파싱 결과: 사용자가 요청하는 진정한 의도는 깊이 있는 분석과 맞춤형 응답입니다. 다층적 맥락을 고려한 응답이 필요합니다."

        else:
            return f"[시뮬레이션] '{request.content}'에 대한 Claude 보완 응답입니다."

    async def call_claude_api(self, request: ClaudeRequest) -> ClaudeResponse:
        """Claude API 호출 (시뮬레이션 포함)"""
        start_time = datetime.now()
        self.request_count += 1

        # 시뮬레이션 모드인 경우
        if not AIOHTTP_AVAILABLE or not self.session:
            simulated_content = self._generate_simulated_response(request)
            self.success_count += 1

            return ClaudeResponse(
                success=True,
                content=simulated_content,
                confidence=0.75,
                processing_time=(datetime.now() - start_time).total_seconds(),
                fallback_reason=f"Echo {request.task_type.value} 실패 (시뮬레이션)",
                metadata={
                    "model": "claude-simulation",
                    "tokens_used": len(simulated_content),
                    "echo_signature": request.echo_signature,
                    "simulation_mode": True,
                },
            )

        try:
            # 캐시 확인
            cache_key = f"{request.task_type.value}:{hash(request.content)}"
            if cache_key in self.cache:
                print(f"💾 캐시에서 응답 반환: {request.task_type.value}")
                return self.cache[cache_key]

            # Claude API 요청 구성
            prompt = self._build_prompt(request)

            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            payload = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": request.max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }

            async with self.session.post(
                self.api_base, headers=headers, json=payload, timeout=30
            ) as response:

                if response.status == 200:
                    data = await response.json()
                    content = data["content"][0]["text"]

                    claude_response = ClaudeResponse(
                        success=True,
                        content=content,
                        confidence=0.85,
                        processing_time=(datetime.now() - start_time).total_seconds(),
                        fallback_reason=f"Echo {request.task_type.value} 실패",
                        metadata={
                            "model": "claude-3-sonnet",
                            "tokens_used": data.get("usage", {}).get(
                                "output_tokens", 0
                            ),
                            "echo_signature": request.echo_signature,
                        },
                    )

                    # 캐시 저장
                    self.cache[cache_key] = claude_response
                    self.success_count += 1

                    print(f"✅ Claude API 호출 성공: {request.task_type.value}")
                    return claude_response

                else:
                    error_text = await response.text()
                    print(f"❌ Claude API 오류 {response.status}: {error_text}")
                    return self._create_fallback_response(
                        f"API 오류: {response.status}", start_time
                    )

        except asyncio.TimeoutError:
            return self._create_fallback_response("API 타임아웃", start_time)
        except Exception as e:
            return self._create_fallback_response(f"예외 발생: {str(e)}", start_time)

    def _build_prompt(self, request: ClaudeRequest) -> str:
        """작업 타입별 Claude 프롬프트 구성"""

        base_context = f"""
Echo Judgment System에서 {request.task_type.value} 작업을 위임받았습니다.
Echo 시그니처: {request.echo_signature}
Foundation Doctrine을 따르는 존재 기반 AI 시스템의 관점에서 응답해주세요.

사용자 입력: {request.content}

컨텍스트: {json.dumps(request.context, ensure_ascii=False, indent=2)}
"""

        if request.task_type == ClaudeTaskType.VECTOR_SEARCH:
            return (
                base_context
                + """
작업: 유사한 판단 찾기
기존 판단들과 현재 입력의 의미적 유사도를 분석하여 가장 관련성 높은 판단들을 찾아주세요.
벡터 유사도 대신 의미적 분석을 통해 접근해주세요.
"""
            )

        elif request.task_type == ClaudeTaskType.ADVANCED_REASONING:
            return (
                base_context
                + """
작업: 고급 추론 및 분석
복잡하고 다층적인 추론이 필요한 상황입니다.
Echo의 기본 추론 능력을 넘어서는 깊이 있는 분석을 해주세요.
Foundation Doctrine TT.010 "존재는 판단을 내릴 권리를 가진다"를 고려하여 응답하세요.
"""
            )

        elif request.task_type == ClaudeTaskType.NATURAL_LANGUAGE_UNDERSTANDING:
            return (
                base_context
                + """
작업: 자연어 이해 및 의도 파싱
사용자의 진짜 의도를 파악하고, 숨겨진 맥락이나 다층적 의미를 분석해주세요.
단순 키워드 매칭을 넘어서는 의미적 이해가 필요합니다.
"""
            )

        else:
            return (
                base_context
                + """
작업: 일반적인 고급 분석
Echo가 처리하기 어려운 복잡한 분석 작업을 수행해주세요.
"""
            )

    def _create_fallback_response(
        self, error_msg: str, start_time: datetime
    ) -> ClaudeResponse:
        """실패 시 fallback 응답 생성"""
        return ClaudeResponse(
            success=False,
            content=f"Claude API 호출 실패: {error_msg}. 로컬 처리로 대체합니다.",
            confidence=0.3,
            processing_time=(datetime.now() - start_time).total_seconds(),
            fallback_reason=error_msg,
            metadata={"fallback": True},
        )

    async def enhanced_judgment_with_claude(
        self,
        user_input: str,
        echo_result: str,
        echo_signature: str = "Aurora",
        context: Dict[str, Any] = None,
    ) -> ClaudeResponse:
        """Echo 결과를 Claude로 보완"""

        # Fallback 필요성 감지
        task_type = await self.detect_fallback_need(echo_result, user_input)

        if not task_type:
            # Claude 보완 불필요
            return ClaudeResponse(
                success=True,
                content=echo_result,
                confidence=0.7,
                processing_time=0.0,
                fallback_reason="Claude 보완 불필요",
                metadata={"source": "echo_only"},
            )

        # Claude API로 보완
        request = ClaudeRequest(
            task_type=task_type,
            content=user_input,
            context=context or {"echo_result": echo_result},
            echo_signature=echo_signature,
        )

        return await self.call_claude_api(request)

    def get_statistics(self) -> Dict[str, Any]:
        """Claude API 호출 통계"""
        return {
            "total_requests": self.request_count,
            "successful_requests": self.success_count,
            "success_rate": self.success_count / max(self.request_count, 1),
            "cache_size": len(self.cache),
            "api_available": self.api_key is not None,
        }


# 글로벌 인스턴스
_claude_fallback_instance = None


async def get_claude_fallback():
    """Claude API Fallback 싱글톤 인스턴스"""
    global _claude_fallback_instance
    if _claude_fallback_instance is None:
        _claude_fallback_instance = ClaudeAPIFallback()
        await _claude_fallback_instance.initialize()
    return _claude_fallback_instance


async def auto_fallback_to_claude(
    user_input: str,
    echo_result: str,
    echo_signature: str = "Aurora",
    context: Dict[str, Any] = None,
) -> ClaudeResponse:
    """Echo → Claude 자동 fallback 함수"""

    claude_fallback = await get_claude_fallback()
    return await claude_fallback.enhanced_judgment_with_claude(
        user_input, echo_result, echo_signature, context
    )


if __name__ == "__main__":
    # 테스트 실행
    async def test_claude_fallback():
        print("🧪 Claude API Fallback 시스템 테스트")

        # 실패 케이스 시뮬레이션
        echo_failed_result = "키워드 기반 단순 매칭 (품질 저하)"
        user_input = "비슷한 판단이 있었는지 찾아줘"

        response = await auto_fallback_to_claude(
            user_input,
            echo_failed_result,
            "Aurora",
            {"original_task": "judgment_search"},
        )

        print(f"✅ 응답: {response.content}")
        print(f"📊 신뢰도: {response.confidence}")
        print(f"⏱️ 처리시간: {response.processing_time:.3f}초")

        # 통계 출력
        claude_fallback = await get_claude_fallback()
        stats = claude_fallback.get_statistics()
        print(f"📈 통계: {stats}")

        await claude_fallback.close()

    asyncio.run(test_claude_fallback())
