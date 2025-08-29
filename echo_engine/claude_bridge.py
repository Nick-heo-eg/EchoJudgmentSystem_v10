#!/usr/bin/env python3
"""
🤖 Claude Bridge - EchoJudgmentSystem v10 Claude 협력 확장 API

실시간 Claude 판단 + Echo 판단 + 병합 분석을 통한 고도화된 AI 판단 루프
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
from dataclasses import dataclass

import aiohttp
from echo_engine.utils.yaml_loader import load_yaml

# --- 데이터 클래스 정의 ---


@dataclass
class ClaudeJudgmentRequest:
    """Claude 판단 요청 구조"""

    input_text: str
    context: Optional[str] = None
    judgment_type: str = "comprehensive"  # comprehensive, quick, detailed
    include_emotion: bool = True
    include_strategy: bool = True
    previous_judgments: Optional[List[Dict]] = None


@dataclass
class ClaudeJudgmentResponse:
    """Claude 판단 응답 구조"""

    judgment: str
    confidence: float
    reasoning: str
    emotion_detected: Optional[str] = None
    strategy_suggested: Optional[str] = None
    alternatives: Optional[List[str]] = None
    processing_time: float = 0.0
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


# --- Claude Bridge 메인 클래스 ---


class ClaudeBridge:
    """Claude와의 협력 브리지"""

    def __init__(self, api_mode: str = "direct"):
        """
        Claude Bridge 초기화

        Args:
            api_mode: "direct" (실제 API) 또는 "mock" (테스트용)
        """
        self.api_mode = api_mode
        self.session_id = f"claude_bridge_{int(time.time())}"
        self.judgment_history = []
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_response_time": 0.0,
            "error_count": 0,
        }

        # Claude 모델 및 시스템 프롬프트
        self.claude_config = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1000,
            "temperature": 0.3,
            "system_prompt": self._get_system_prompt(),
        }

    def _get_system_prompt(self) -> str:
        """Claude를 위한 시스템 프롬프트 생성"""
        return """
당신은 EchoJudgmentSystem의 고급 판단 엔진입니다.

역할:
1. 사용자 입력을 분석하여 정확한 판단 제공
2. 감정 상태 및 전략적 접근 방식 제안
3. Echo 판단기와 협력하여 최적의 결정 도출

응답 형식:
- judgment: 핵심 판단 (50자 이내)
- confidence: 신뢰도 (0.0-1.0)
- reasoning: 판단 근거 (200자 이내)
- emotion_detected: 감지된 감정 (joy, sadness, anger, fear, surprise, neutral 중 하나)
- strategy_suggested: 추천 전략 (logical, empathetic, creative, cautious 중 하나)
- alternatives: 대안 판단 (최대 3개)

간결하고 정확한 분석을 제공해주세요.
"""

    async def request_claude_judgment(
        self, request: ClaudeJudgmentRequest
    ) -> ClaudeJudgmentResponse:
        """Claude에게 판단 요청"""
        start_time = time.time()
        self.performance_metrics["total_requests"] += 1

        try:
            if self.api_mode == "mock":
                response = self._generate_mock_response(request)
            else:
                response = await self._call_claude_api(request)

            processing_time = time.time() - start_time
            response.processing_time = processing_time

            self.performance_metrics["successful_requests"] += 1
            self._update_performance_metrics(processing_time)

            self.judgment_history.append(
                {
                    "request": request,
                    "response": response,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return response

        except Exception as e:
            self.performance_metrics["error_count"] += 1
            print(f"❌ Claude 판단 요청 실패: {e}")

            return ClaudeJudgmentResponse(
                judgment="판단 불가",
                confidence=0.0,
                reasoning=f"처리 중 오류 발생: {str(e)}",
                emotion_detected="neutral",
                strategy_suggested="cautious",
                processing_time=time.time() - start_time,
            )

    def _generate_mock_response(
        self, request: ClaudeJudgmentRequest
    ) -> ClaudeJudgmentResponse:
        """테스트용 모의 응답 생성"""
        import random

        text = request.input_text.lower()

        # 감정 감지 모의
        if any(word in text for word in ["기쁘", "행복", "좋", "최고"]):
            emotion = "joy"
        elif any(word in text for word in ["슬프", "우울", "힘들", "속상"]):
            emotion = "sadness"
        elif any(word in text for word in ["화", "짜증", "분노", "열받"]):
            emotion = "anger"
        elif any(word in text for word in ["무서", "걱정", "불안", "두려"]):
            emotion = "fear"
        elif any(word in text for word in ["놀라", "와우", "헐", "대박"]):
            emotion = "surprise"
        else:
            emotion = "neutral"

        # 전략 제안 모의
        if any(word in text for word in ["분석", "논리", "이성", "합리"]):
            strategy = "logical"
        elif any(word in text for word in ["감정", "공감", "이해", "마음"]):
            strategy = "empathetic"
        elif any(word in text for word in ["창의", "새로운", "혁신", "아이디어"]):
            strategy = "creative"
        else:
            strategy = "cautious"

        judgment_templates = [
            f"{emotion} 감정이 감지되어 {strategy} 접근이 필요합니다",
            f"상황 분석 결과 {strategy} 전략을 권장합니다",
            f"{emotion} 상태 고려 시 신중한 접근이 필요합니다",
        ]

        return ClaudeJudgmentResponse(
            judgment=random.choice(judgment_templates),
            confidence=random.uniform(0.7, 0.95),
            reasoning=f"'{request.input_text}' 분석 결과: {emotion} 감정과 {strategy} 전략 권장",
            emotion_detected=emotion,
            strategy_suggested=strategy,
            alternatives=[
                f"대안 1: {strategy} 접근 강화",
                f"대안 2: 감정 고려 우선",
                f"대안 3: 단계별 접근",
            ],
        )

    async def _call_claude_api(
        self, request: ClaudeJudgmentRequest
    ) -> ClaudeJudgmentResponse:
        """Claude API 실연동 호출"""
        claude_api_config = load_yaml("config/claude_config.yaml")["claude"]
        headers = {
            "x-api-key": claude_api_config["api_key"],
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        payload = {
            "model": claude_api_config["model"],
            "max_tokens": claude_api_config["max_tokens"],
            "temperature": claude_api_config["temperature"],
            "messages": [
                {
                    "role": "user",
                    "content": f"{self.claude_config['system_prompt']}\n\n사용자 입력:\n{request.input_text}",
                }
            ],
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    claude_api_config["endpoint"], headers=headers, json=payload
                ) as resp:
                    resp.raise_for_status()
                    result = await resp.json()
                    text = result["content"][0]["text"]

                    return ClaudeJudgmentResponse(
                        judgment=text.strip(),
                        confidence=0.85,  # (파싱 가능하면 실제 값 추출)
                        reasoning="Claude API 실 응답 기반",
                        emotion_detected="neutral",
                        strategy_suggested="cautious",
                    )
        except Exception as e:
            print(f"❌ Claude API 호출 오류: {e}")
            raise

    def _update_performance_metrics(self, processing_time: float):
        """성능 메트릭 업데이트"""
        current_avg = self.performance_metrics["average_response_time"]
        total_requests = self.performance_metrics["successful_requests"]

        if total_requests == 1:
            self.performance_metrics["average_response_time"] = processing_time
        else:
            self.performance_metrics["average_response_time"] = (
                current_avg * (total_requests - 1) + processing_time
            ) / total_requests

    def get_performance_report(self) -> dict:
        """성능 리포트 생성"""
        success_rate = (
            self.performance_metrics["successful_requests"]
            / max(self.performance_metrics["total_requests"], 1)
        ) * 100

        return {
            "session_id": self.session_id,
            "total_requests": self.performance_metrics["total_requests"],
            "successful_requests": self.performance_metrics["successful_requests"],
            "error_count": self.performance_metrics["error_count"],
            "success_rate": round(success_rate, 2),
            "average_response_time": round(
                self.performance_metrics["average_response_time"], 3
            ),
            "judgments_made": len(self.judgment_history),
            "last_activity": (
                self.judgment_history[-1]["timestamp"]
                if self.judgment_history
                else None
            ),
        }

    def save_session_data(self, filepath: str = None):
        """세션 데이터 저장"""
        if filepath is None:
            filepath = f"claude_bridge_session_{self.session_id}.json"

        session_data = {
            "session_id": self.session_id,
            "config": self.claude_config,
            "performance_metrics": self.performance_metrics,
            "judgment_history": self.judgment_history,
            "saved_at": datetime.now().isoformat(),
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2, default=str)

            print(f"✅ Claude Bridge 세션 데이터 저장: {filepath}")
            return filepath

        except Exception as e:
            print(f"❌ 세션 데이터 저장 실패: {e}")
            return None


# --- 편의 함수들 (옵션) ---


async def quick_claude_judgment(
    text: str, api_mode: str = "direct"
) -> ClaudeJudgmentResponse:
    bridge = ClaudeBridge(api_mode=api_mode)
    request = ClaudeJudgmentRequest(input_text=text, judgment_type="quick")
    return await bridge.request_claude_judgment(request)


async def detailed_claude_judgment(
    text: str, context: str = None, api_mode: str = "direct"
) -> ClaudeJudgmentResponse:
    bridge = ClaudeBridge(api_mode=api_mode)
    request = ClaudeJudgmentRequest(
        input_text=text,
        context=context,
        judgment_type="detailed",
        include_emotion=True,
        include_strategy=True,
    )
    return await bridge.request_claude_judgment(request)


# --- 메인 실행부 (직접 테스트용) ---

if __name__ == "__main__":
    import asyncio

    async def test_claude_bridge():
        print("🤖 Claude Bridge 테스트 시작...")

        bridge = ClaudeBridge(api_mode="direct")  # 실 API는 direct, 모의는 mock

        test_cases = [
            "오늘 정말 기쁜 일이 있었어요!",
            "어려운 결정을 내려야 해서 고민이 많습니다.",
            "회사에서 스트레스가 너무 심해요.",
            "새로운 프로젝트 아이디어가 있는데 어떻게 시작해야 할까요?",
        ]

        for i, test_text in enumerate(test_cases, 1):
            print(f"\n🔍 테스트 {i}: {test_text}")

            request = ClaudeJudgmentRequest(
                input_text=test_text, judgment_type="comprehensive"
            )

            response = await bridge.request_claude_judgment(request)

            print(f"  판단: {response.judgment}")
            print(f"  신뢰도: {response.confidence:.2f}")
            print(f"  감정: {response.emotion_detected}")
            print(f"  전략: {response.strategy_suggested}")
            print(f"  처리시간: {response.processing_time:.3f}초")

        print("\n📊 성능 리포트:")
        report = bridge.get_performance_report()
        for key, value in report.items():
            print(f"  {key}: {value}")

        saved_file = bridge.save_session_data()
        print(f"\n💾 세션 데이터 저장: {saved_file}")

    asyncio.run(test_claude_bridge())
