#!/usr/bin/env python3
"""
🔄 Short Input Judgment Loop v1.0 - 짧은 입력 판단 루프

LLM-Free 환경에서 짧은 자연어 입력에 대해:
1. 기존 판단 탐색 (유사도 기반)
2. 신규 판단 생성 (감정→전략→템플릿→스타일링)
3. 결과 캐싱 및 반환

핵심 기능:
- MicroReactor 우선 처리 (극단적 짧은 발화)
- 기존 판단 유사도 탐색
- 전체 판단 파이프라인 실행
- 무한루프 방지 및 fallback 체인
"""

import re
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# 기존 모듈 임포트 (연동만 수행)
try:
    from .judgment_microreactor import get_microreactor
    from .existing_judgment_search import ExistingJudgmentSearcher
    from .generate_new_judgment import NewJudgmentGenerator
    from .judgment_cache import JudgmentCache
    from .claude_api_fallback import auto_fallback_to_claude, ClaudeResponse
except ImportError:
    # 상대 임포트 실패 시 절대 임포트 시도
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from echo_engine.judgment_microreactor import get_microreactor
    from echo_engine.existing_judgment_search import ExistingJudgmentSearcher
    from echo_engine.generate_new_judgment import NewJudgmentGenerator
    from echo_engine.judgment_cache import JudgmentCache
    from echo_engine.claude_api_fallback import auto_fallback_to_claude, ClaudeResponse


@dataclass
class JudgmentRequest:
    """판단 요청 정보"""

    input_text: str
    signature: str = "Selene"
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: str = field(default="")

    def __post_init__(self):
        if not self.request_id:
            # 입력과 시간으로 고유 ID 생성
            content = f"{self.input_text}_{self.signature}_{self.timestamp.isoformat()}"
            self.request_id = hashlib.md5(content.encode()).hexdigest()[:8]


@dataclass
class JudgmentResult:
    """판단 결과"""

    input: str
    normalized_input: str
    emotion: str
    emotion_confidence: float
    strategy: str
    strategy_confidence: float
    template: str
    styled_sentence: str
    signature: str
    processing_method: str  # "microreactor", "cached", "generated", "claude_enhanced"
    processing_time: float
    cache_hit: bool = False
    microreactor_used: bool = False
    claude_enhanced: bool = False
    claude_response: Optional["ClaudeResponse"] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class ShortInputJudgmentLoop:
    """🔄 짧은 입력 판단 루프 메인 오케스트레이터"""

    def __init__(self):
        """초기화"""
        self.version = "1.0.0"

        # 하위 모듈 초기화
        self.microreactor = get_microreactor()
        self.judgment_searcher = ExistingJudgmentSearcher()
        self.judgment_generator = NewJudgmentGenerator()
        self.judgment_cache = JudgmentCache()

        # 설정
        self.max_recursion_depth = 3
        self.similarity_threshold = 0.7
        self.microreactor_enabled = True
        self.cache_enabled = True

        # 통계
        self.stats = {
            "total_requests": 0,
            "microreactor_hits": 0,
            "cache_hits": 0,
            "new_generations": 0,
            "claude_enhancements": 0,
            "errors": 0,
            "processing_times": [],
            "method_distribution": {
                "microreactor": 0,
                "cached": 0,
                "generated": 0,
                "claude_enhanced": 0,
            },
        }

        print(f"🔄 ShortInputJudgmentLoop v{self.version} 초기화 완료")
        print(f"   MicroReactor: {'✅' if self.microreactor_enabled else '❌'}")
        print(f"   캐시 시스템: {'✅' if self.cache_enabled else '❌'}")

    def normalize_input(self, text: str) -> str:
        """입력 정규화"""
        # 공백 정리
        normalized = re.sub(r"\s+", " ", text.strip())

        # 특수 문자 정리 (필요한 경우)
        # normalized = re.sub(r'[^\w\s\?\!\.\,\-]', '', normalized)

        return normalized.lower()

    async def handle_short_input(
        self,
        user_input: str,
        signature: str = "Selene",
        context: Optional[Dict[str, Any]] = None,
    ) -> JudgmentResult:
        """
        메인 핸들러 - 짧은 입력에 대한 판단 수행

        Args:
            user_input: 사용자 입력
            signature: 시그니처 (Selene, Aurora, Phoenix, Sage, Companion)
            context: 추가 컨텍스트

        Returns:
            JudgmentResult: 판단 결과
        """
        start_time = time.time()
        self.stats["total_requests"] += 1

        # 요청 객체 생성
        request = JudgmentRequest(
            input_text=user_input, signature=signature, context=context or {}
        )

        try:
            # 1단계: MicroReactor 우선 처리 (극단적 짧은 발화)
            if self.microreactor_enabled:
                micro_result = self._try_microreactor(request)
                if micro_result:
                    micro_result.processing_time = time.time() - start_time
                    self._update_stats("microreactor", micro_result.processing_time)
                    return micro_result

            # 2단계: 입력 정규화
            normalized_input = self.normalize_input(user_input)

            # 3단계: 기존 판단 탐색 (캐시된 유사 판단)
            if self.cache_enabled:
                cached_result = self._try_cached_judgment(request, normalized_input)
                if cached_result:
                    cached_result.processing_time = time.time() - start_time
                    self._update_stats("cached", cached_result.processing_time)
                    return cached_result

            # 4단계: 신규 판단 생성
            new_result = self._generate_new_judgment(request, normalized_input)

            # 5단계: Claude API 자동 fallback 확인 및 보완
            enhanced_result = await self._try_claude_enhancement(new_result, request)
            enhanced_result.processing_time = time.time() - start_time

            # 6단계: 결과 캐싱
            if self.cache_enabled and not enhanced_result.error:
                self.judgment_cache.save_judgment(enhanced_result)

            # 통계 업데이트
            if enhanced_result.claude_enhanced:
                self._update_stats("claude_enhanced", enhanced_result.processing_time)
            else:
                self._update_stats("generated", enhanced_result.processing_time)

            return enhanced_result

        except Exception as e:
            # 에러 처리
            self.stats["errors"] += 1
            error_result = JudgmentResult(
                input=user_input,
                normalized_input=self.normalize_input(user_input),
                emotion="neutral",
                emotion_confidence=0.0,
                strategy="analyze",
                strategy_confidence=0.0,
                template="error_fallback",
                styled_sentence=f"죄송해요, 처리 중 문제가 발생했어요. ({str(e)[:50]})",
                signature=signature,
                processing_method="error",
                processing_time=time.time() - start_time,
                error=str(e),
                request_id=request.request_id,
            )

            print(f"❌ 판단 루프 에러: {e}")
            return error_result

    def _try_microreactor(self, request: JudgmentRequest) -> Optional[JudgmentResult]:
        """MicroReactor로 처리 시도"""
        try:
            micro_response = self.microreactor.run(
                request.input_text, request.signature
            )

            if micro_response:
                self.stats["microreactor_hits"] += 1

                return JudgmentResult(
                    input=request.input_text,
                    normalized_input=self.normalize_input(request.input_text),
                    emotion="neutral",  # MicroReactor는 감정 추론 없음
                    emotion_confidence=1.0,
                    strategy="microreactor",
                    strategy_confidence=micro_response.confidence,
                    template=micro_response.tag,
                    styled_sentence=micro_response.text,
                    signature=request.signature,
                    processing_method="microreactor",
                    processing_time=0.0,  # 나중에 설정
                    microreactor_used=True,
                    request_id=request.request_id,
                )

        except Exception as e:
            print(f"⚠️ MicroReactor 처리 실패: {e}")

        return None

    def _try_cached_judgment(
        self, request: JudgmentRequest, normalized_input: str
    ) -> Optional[JudgmentResult]:
        """캐시된 판단 탐색 시도"""
        try:
            cached_judgment = self.judgment_searcher.search_similar_judgment(
                normalized_input,
                signature=request.signature,
                threshold=self.similarity_threshold,
            )

            if cached_judgment:
                self.stats["cache_hits"] += 1

                # 캐시된 결과를 현재 요청에 맞게 조정
                return JudgmentResult(
                    input=request.input_text,
                    normalized_input=normalized_input,
                    emotion=cached_judgment.get("emotion", "neutral"),
                    emotion_confidence=cached_judgment.get("emotion_confidence", 0.8),
                    strategy=cached_judgment.get("strategy", "analyze"),
                    strategy_confidence=cached_judgment.get("strategy_confidence", 0.8),
                    template=cached_judgment.get("template", "cached_template"),
                    styled_sentence=cached_judgment.get("styled_sentence", ""),
                    signature=request.signature,
                    processing_method="cached",
                    processing_time=0.0,  # 나중에 설정
                    cache_hit=True,
                    metadata={
                        "original_input": cached_judgment.get("input", ""),
                        "similarity_score": cached_judgment.get(
                            "similarity_score", 0.0
                        ),
                        "cache_timestamp": cached_judgment.get("timestamp", ""),
                    },
                    request_id=request.request_id,
                )

        except Exception as e:
            print(f"⚠️ 캐시 탐색 실패: {e}")

        return None

    def _generate_new_judgment(
        self, request: JudgmentRequest, normalized_input: str
    ) -> JudgmentResult:
        """신규 판단 생성"""
        try:
            self.stats["new_generations"] += 1

            # 신규 판단 생성기 호출
            judgment_data = self.judgment_generator.generate_judgment(
                input_text=request.input_text,
                signature=request.signature,
                context=request.context,
            )

            return JudgmentResult(
                input=request.input_text,
                normalized_input=normalized_input,
                emotion=judgment_data.get("emotion", "neutral"),
                emotion_confidence=judgment_data.get("emotion_confidence", 0.5),
                strategy=judgment_data.get("strategy", "analyze"),
                strategy_confidence=judgment_data.get("strategy_confidence", 0.5),
                template=judgment_data.get("template", "generated_template"),
                styled_sentence=judgment_data.get("styled_sentence", ""),
                signature=request.signature,
                processing_method="generated",
                processing_time=0.0,  # 나중에 설정
                metadata=judgment_data.get("metadata", {}),
                request_id=request.request_id,
            )

        except Exception as e:
            # 신규 생성 실패 시 최종 fallback
            return self._create_fallback_result(request, normalized_input, str(e))

    def _create_fallback_result(
        self, request: JudgmentRequest, normalized_input: str, error: str
    ) -> JudgmentResult:
        """최종 fallback 결과 생성"""

        # 시그니처별 fallback 응답
        fallback_responses = {
            "Selene": "음... 조금 더 자세히 말씀해주시겠어요?",
            "Aurora": "흥미로워요! 더 구체적으로 얘기해주세요!",
            "Phoenix": "새로운 관점이네요. 더 발전시켜봅시다.",
            "Sage": "흥미로운 주제네요. 분석해볼 가치가 있어 보입니다.",
            "Companion": "그렇구나! 더 자세히 얘기해줄래?",
        }

        return JudgmentResult(
            input=request.input_text,
            normalized_input=normalized_input,
            emotion="neutral",
            emotion_confidence=0.3,
            strategy="analyze",
            strategy_confidence=0.3,
            template="fallback_template",
            styled_sentence=fallback_responses.get(
                request.signature, "음... 더 이야기해주세요."
            ),
            signature=request.signature,
            processing_method="fallback",
            processing_time=0.0,
            error=f"Fallback due to: {error}",
            request_id=request.request_id,
        )

    async def _try_claude_enhancement(
        self, echo_result: JudgmentResult, request: JudgmentRequest
    ) -> JudgmentResult:
        """Claude API로 Echo 결과 보완 시도"""
        try:
            # Echo 결과를 Claude API로 보완
            claude_response = await auto_fallback_to_claude(
                user_input=request.input_text,
                echo_result=echo_result.styled_sentence,
                echo_signature=request.signature,
                context={
                    "echo_emotion": echo_result.emotion,
                    "echo_strategy": echo_result.strategy,
                    "echo_template": echo_result.template,
                    "processing_method": echo_result.processing_method,
                    "original_context": request.context,
                },
            )

            if (
                claude_response.success
                and claude_response.content != echo_result.styled_sentence
            ):
                # Claude가 보완한 경우
                print(
                    f"🧠 Claude 보완 적용: {echo_result.processing_method} → claude_enhanced"
                )
                self.stats["claude_enhancements"] += 1

                enhanced_result = JudgmentResult(
                    input=echo_result.input,
                    normalized_input=echo_result.normalized_input,
                    emotion=echo_result.emotion,
                    emotion_confidence=echo_result.emotion_confidence,
                    strategy=echo_result.strategy,
                    strategy_confidence=echo_result.strategy_confidence,
                    template=echo_result.template,
                    styled_sentence=claude_response.content,  # Claude가 보완한 응답 사용
                    signature=echo_result.signature,
                    processing_method="claude_enhanced",
                    processing_time=echo_result.processing_time,
                    cache_hit=echo_result.cache_hit,
                    microreactor_used=echo_result.microreactor_used,
                    claude_enhanced=True,
                    claude_response=claude_response,
                    error=echo_result.error,
                    metadata={
                        **echo_result.metadata,
                        "claude_fallback_reason": claude_response.fallback_reason,
                        "claude_confidence": claude_response.confidence,
                        "original_echo_response": echo_result.styled_sentence,
                    },
                    request_id=echo_result.request_id,
                    timestamp=echo_result.timestamp,
                )

                return enhanced_result
            else:
                # Claude 보완 불필요 또는 실패
                return echo_result

        except Exception as e:
            print(f"⚠️ Claude 보완 중 오류: {e}")
            # 에러 발생 시 원본 Echo 결과 반환
            return echo_result

    def _update_stats(self, method: str, processing_time: float):
        """통계 업데이트"""
        self.stats["method_distribution"][method] += 1
        self.stats["processing_times"].append(processing_time)

    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        total = self.stats["total_requests"]
        if total == 0:
            return {"message": "처리된 요청이 없습니다"}

        avg_time = (
            sum(self.stats["processing_times"]) / len(self.stats["processing_times"])
            if self.stats["processing_times"]
            else 0
        )

        return {
            "total_requests": total,
            "microreactor_hits": self.stats["microreactor_hits"],
            "cache_hits": self.stats["cache_hits"],
            "new_generations": self.stats["new_generations"],
            "claude_enhancements": self.stats["claude_enhancements"],
            "errors": self.stats["errors"],
            "hit_rates": {
                "microreactor": f"{(self.stats['microreactor_hits'] / total) * 100:.1f}%",
                "cache": f"{(self.stats['cache_hits'] / total) * 100:.1f}%",
                "generation": f"{(self.stats['new_generations'] / total) * 100:.1f}%",
                "claude_enhanced": f"{(self.stats['claude_enhancements'] / total) * 100:.1f}%",
            },
            "average_processing_time": f"{avg_time:.3f}초",
            "method_distribution": self.stats["method_distribution"],
        }

    def clear_cache(self):
        """캐시 초기화"""
        self.judgment_cache.clear_cache()
        print("✅ 판단 캐시가 초기화되었습니다.")

    def set_similarity_threshold(self, threshold: float):
        """유사도 임계값 설정"""
        self.similarity_threshold = max(0.0, min(1.0, threshold))
        print(f"✅ 유사도 임계값을 {self.similarity_threshold:.2f}로 설정했습니다.")


# 글로벌 인스턴스
_global_judgment_loop = None


def get_judgment_loop() -> ShortInputJudgmentLoop:
    """글로벌 판단 루프 인스턴스 반환"""
    global _global_judgment_loop
    if _global_judgment_loop is None:
        _global_judgment_loop = ShortInputJudgmentLoop()
    return _global_judgment_loop


async def quick_judgment(user_input: str, signature: str = "Selene") -> str:
    """빠른 판단 함수 - styled_sentence만 반환"""
    loop = get_judgment_loop()
    result = await loop.handle_short_input(user_input, signature)
    return result.styled_sentence


if __name__ == "__main__":
    import asyncio

    async def test_judgment_loop():
        # 테스트
        print("🔄 ShortInputJudgmentLoop + Claude API Fallback 테스트")

        loop = get_judgment_loop()

        test_cases = [
            "안녕",
            "오늘 너무 피곤해",
            "새로운 아이디어가 필요해",
            "이 문제를 어떻게 해결하지?",
            "ㅋㅋㅋ",
            "복잡한 철학적 문제에 대해 깊이 있는 분석을 해주세요",  # Claude API fallback 유도
        ]

        for i, test_input in enumerate(test_cases, 1):
            print(f"\n🔄 테스트 {i}: '{test_input}'")
            result = await loop.handle_short_input(test_input, "Aurora")
            print(f"   응답: {result.styled_sentence}")
            print(f"   방법: {result.processing_method}")
            print(f"   Claude 보완: {'✅' if result.claude_enhanced else '❌'}")
            print(f"   시간: {result.processing_time:.3f}초")

            if result.claude_enhanced and result.claude_response:
                print(f"   보완 이유: {result.claude_response.fallback_reason}")

        # 통계 출력
        stats = loop.get_statistics()
        print(f"\n📊 처리 통계:")
        for key, value in stats.items():
            if key != "method_distribution":
                print(f"   {key}: {value}")

    # 비동기 테스트 실행
    asyncio.run(test_judgment_loop())
