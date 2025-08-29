"""
Claude 판단기 연동 모듈 - claude_bridge.py 기반 API 통합
LLM-Free 판단 시스템 지원 추가
공통 판단 로직 통합 (SharedJudgmentEngine)
"""

import asyncio
import sys
import os
import time

# 상위 디렉토리 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from echo_engine.claude_bridge import ClaudeBridge, ClaudeJudgmentRequest
from echo_engine.llm_free.llm_free_judge import FallbackJudge, quick_judgment
from echo_engine.shared_judgment_logic import (
    SharedJudgmentEngine,
    JudgmentRequest,
    JudgmentMode,
    get_shared_judgment_engine,
)
from echo_engine.judgment_mode_switcher import (
    JudgmentModeSwitcher,
    SwitchingTrigger,
    get_mode_switcher,
)
import yaml
import os
from meta_log_writer import log_llm_free_judgment


class ClaudeJudgmentRunner:
    """Claude 판단기 실행 클래스"""

    def __init__(self, api_mode: str = "mock", judge_mode: str = None):
        self.api_mode = api_mode

        # 설정 파일 로드
        self.config = self._load_config()

        # 판단 모드 설정 (파라미터 우선, 그 다음 설정 파일)
        self.judge_mode = judge_mode or self.config.get("judge_mode", "claude")

        # Claude 브리지 초기화
        self.bridge = ClaudeBridge(api_mode=api_mode)

        # LLM-Free 판단기 초기화
        self.fallback_judge = FallbackJudge()

        # 공통 판단 엔진 초기화
        self.shared_engine = get_shared_judgment_engine()

        # 모드 전환기 초기화
        self.mode_switcher = get_mode_switcher(self.config.get("mode_switcher", {}))

        # 현재 모드 동기화
        if self.judge_mode != self.mode_switcher.get_current_mode().value:
            mode_enum = JudgmentMode(self.judge_mode)
            self.mode_switcher.switch_mode(
                mode_enum, SwitchingTrigger.MANUAL, "Initial sync"
            )

        # 성능 모니터링
        self.performance_stats = {
            "total_requests": 0,
            "claude_requests": 0,
            "fallback_requests": 0,
            "hybrid_requests": 0,
            "failed_requests": 0,
        }

    def _load_config(self) -> dict:
        """설정 파일 로드"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config",
            "llm_config.yaml",
        )

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️  설정 파일을 찾을 수 없습니다: {config_path}")
            # 기본 설정 반환
            return {
                "judge_mode": "claude",
                "confidence_threshold": 0.65,
                "claude_settings": {"api_mode": "mock"},
                "fallback_settings": {"min_confidence": 0.3},
            }
        except Exception as e:
            print(f"⚠️  설정 파일 로드 실패: {e}")
            return {"judge_mode": "claude", "confidence_threshold": 0.65}

    def run_claude_judgment(self, prompt: str, context: str = None) -> dict:
        """
        지능형 판단 실행 (자동 모드 선택 포함)

        Args:
            prompt: 판단 요청 텍스트
            context: 추가 맥락 정보

        Returns:
            판단 결과 딕셔너리
        """
        self.performance_stats["total_requests"] += 1

        try:
            # 1. 자동 모드 최적화 체크
            judgment_context = self._build_judgment_context(prompt, context)
            auto_switch = self.mode_switcher.auto_switch_mode(judgment_context)

            if auto_switch:
                # 자동 전환이 발생한 경우 모드 동기화
                self.judge_mode = self.mode_switcher.get_current_mode().value
                print(f"🎛️ 자동 모드 전환: {auto_switch.reason}")

            # 2. 현재 모드에 따라 판단 실행
            current_mode = self.mode_switcher.get_current_mode()

            if current_mode == JudgmentMode.LLM_FREE:
                self.performance_stats["fallback_requests"] += 1
                result = self._run_fallback_judgment(prompt, context)
            elif current_mode == JudgmentMode.HYBRID:
                self.performance_stats["hybrid_requests"] += 1
                result = self._run_hybrid_judgment(prompt, context)
            else:  # CLAUDE or FIST_ENHANCED
                self.performance_stats["claude_requests"] += 1
                # 폴백 체인이 활성화된 경우 Claude 실패 시 fallback 사용
                if self.config.get("judgment_settings", {}).get(
                    "enable_multimode", False
                ):
                    try:
                        result = self._run_enhanced_claude_judgment(prompt, context)
                    except Exception as e:
                        print(f"⚠️  Claude 판단 실패, fallback으로 전환: {e}")
                        self.performance_stats["fallback_requests"] += 1
                        result = self._run_fallback_judgment(prompt, context)
                else:
                    # 공통 로직이 강화된 Claude 판단 사용
                    result = self._run_enhanced_claude_judgment(prompt, context)

            # 3. 판단 결과를 모드 전환기에 기록
            self.mode_switcher.record_judgment_result(current_mode, result)

            # 4. 메타 정보 추가
            result["active_mode"] = current_mode.value
            result["auto_switched"] = auto_switch is not None
            if auto_switch:
                result["switch_reason"] = auto_switch.reason

            return result
        except Exception as e:
            self.performance_stats["failed_requests"] += 1
            print(f"❌ 판단 실행 실패: {e}")
            # 최후의 수단으로 간단한 fallback 사용
            return self._emergency_fallback(prompt, context)

    def _build_judgment_context(self, prompt: str, context: str = None) -> dict:
        """
        판단 컨텍스트 구성 (모드 전환기용)

        Args:
            prompt: 판단 요청 텍스트
            context: 추가 맥락 정보

        Returns:
            판단 컨텍스트 딕셔너리
        """
        # 기본 컨텍스트 분석
        text_length = len(prompt) if prompt else 0

        # 복잡도 추정
        complexity = "low"
        if text_length > 200 or (context and len(context) > 100):
            complexity = "high"
        elif text_length > 50:
            complexity = "medium"

        # 컨텍스트 타입 추정
        context_type = "general"
        if context:
            context_lower = context.lower()
            if any(
                word in context_lower for word in ["업무", "회의", "직장", "프로젝트"]
            ):
                context_type = "work"
            elif any(
                word in context_lower for word in ["친구", "가족", "개인", "관계"]
            ):
                context_type = "personal"
            elif any(
                word in context_lower for word in ["창의", "아이디어", "혁신", "새로운"]
            ):
                context_type = "creative"
            elif any(
                word in context_lower for word in ["분석", "데이터", "논리", "체계"]
            ):
                context_type = "analytical"

        # 긴급도 추정 (키워드 기반)
        urgency = "normal"
        if prompt:
            prompt_lower = prompt.lower()
            if any(word in prompt_lower for word in ["긴급", "급해", "빨리", "즉시"]):
                urgency = "high"
            elif any(word in prompt_lower for word in ["천천히", "나중에", "여유"]):
                urgency = "low"

        return {
            "text_length": text_length,
            "complexity": complexity,
            "context_type": context_type,
            "urgency": urgency,
            "has_context": bool(context),
            "timestamp": time.time(),
        }

    async def _async_judgment(self, prompt: str, context: str = None) -> dict:
        """비동기 Claude 판단 호출"""
        request = ClaudeJudgmentRequest(
            input_text=prompt,
            context=context,
            judgment_type="comprehensive",
            include_emotion=True,
            include_strategy=True,
        )

        response = await self.bridge.request_claude_judgment(request)

        # API 응답 형식에 맞게 변환
        return {
            "judgment": response.judgment,
            "confidence": response.confidence,
            "reasoning": response.reasoning,
            "emotion_detected": response.emotion_detected,
            "strategy_suggested": response.strategy_suggested,
            "alternatives": response.alternatives or [],
            "processing_time": response.processing_time,
        }

    def _run_fallback_judgment(self, prompt: str, context: str = None) -> dict:
        """
        LLM-Free 판단 실행

        Args:
            prompt: 판단 요청 텍스트
            context: 추가 맥락 정보

        Returns:
            판단 결과 딕셔너리
        """
        # 입력 데이터 구성
        input_data = {"text": prompt, "context": context or ""}

        # LLM-Free 판단 실행
        result = self.fallback_judge.evaluate(input_data)

        # API 응답 형식에 맞게 변환
        judgment_data = {
            "judgment": result.judgment,
            "confidence": result.confidence,
            "reasoning": " → ".join(result.reasoning_trace),
            "emotion_detected": result.emotion_detected,
            "strategy_suggested": result.strategy_suggested,
            "alternatives": [],  # LLM-Free에서는 대안 제공 안함
            "processing_time": result.processing_time,
            "fallback_used": True,
            "judgment_mode": "fallback",
        }

        # 메타 로그 기록
        try:
            log_llm_free_judgment(
                input_text=prompt,
                judgment_data=judgment_data,
                context=context or "",
                meta_info={"runner_mode": "fallback_judgment"},
            )
        except Exception as e:
            print(f"⚠️  메타 로그 기록 실패: {e}")

        return judgment_data

    def _run_enhanced_claude_judgment(self, prompt: str, context: str = None) -> dict:
        """
        공통 로직으로 강화된 Claude 판단 실행
        순서: (1) 감정 추론 → (2) 전략 추천 → (3) 판단 라벨링 → (4) Claude 응답과 병합

        Args:
            prompt: 판단 요청 텍스트
            context: 추가 맥락 정보

        Returns:
            강화된 판단 결과 딕셔너리
        """
        try:
            # 1. 공통 판단 로직으로 사전 분석
            shared_request = JudgmentRequest(
                text=prompt,
                context=context,
                judgment_mode=JudgmentMode.CLAUDE,
                include_emotion=True,
                include_strategy=True,
                include_context=True,
                include_alternatives=False,
            )

            shared_result = self.shared_engine.process_judgment(shared_request)

            # 2. Claude 판단 실행
            claude_result = asyncio.run(self._async_judgment(prompt, context))

            # 3. 공통 로직과 Claude 결과 병합
            merged_result = self._merge_judgments(
                shared_result, claude_result, prompt, context
            )

            return merged_result

        except Exception as e:
            print(f"⚠️ 강화된 Claude 판단 실패: {e}")
            # 폴백으로 일반 Claude 판단 시도
            return asyncio.run(self._async_judgment(prompt, context))

    def _run_hybrid_judgment(self, prompt: str, context: str = None) -> dict:
        """
        하이브리드 판단 실행 (공통 로직 + Claude 병합 최적화)

        Args:
            prompt: 판단 요청 텍스트
            context: 추가 맥락 정보

        Returns:
            하이브리드 판단 결과 딕셔너리
        """
        try:
            # 1. 공통 판단 로직으로 전체 분석
            shared_request = JudgmentRequest(
                text=prompt,
                context=context,
                judgment_mode=JudgmentMode.HYBRID,
                include_emotion=True,
                include_strategy=True,
                include_context=True,
                include_alternatives=True,
            )

            shared_result = self.shared_engine.process_judgment(shared_request)

            # 2. Claude 판단 병렬 실행 (선택적)
            claude_result = None
            if shared_result.confidence < 0.7:  # 신뢰도가 낮으면 Claude 보강
                try:
                    claude_result = asyncio.run(self._async_judgment(prompt, context))
                except Exception as e:
                    print(f"⚠️ 하이브리드 모드에서 Claude 판단 실패: {e}")

            # 3. 결과 병합 및 최적화
            if claude_result:
                merged_result = self._merge_judgments(
                    shared_result, claude_result, prompt, context, mode="hybrid"
                )
            else:
                # 공통 로직 결과를 API 형식으로 변환
                merged_result = self._convert_shared_to_api_format(
                    shared_result, prompt, context
                )

            merged_result["judgment_mode"] = "hybrid"
            merged_result["hybrid_confidence"] = shared_result.confidence

            return merged_result

        except Exception as e:
            print(f"❌ 하이브리드 판단 실패: {e}")
            # 폴백으로 공통 로직만 사용
            return self._run_fallback_judgment(prompt, context)

    def _merge_judgments(
        self,
        shared_result,
        claude_result: dict,
        prompt: str,
        context: str,
        mode: str = "enhanced",
    ) -> dict:
        """
        공통 로직 결과와 Claude 결과 병합

        Args:
            shared_result: SharedJudgmentResult 객체
            claude_result: Claude 판단 결과 딕셔너리
            prompt: 원본 프롬프트
            context: 문맥 정보
            mode: 병합 모드 ("enhanced" 또는 "hybrid")

        Returns:
            병합된 판단 결과 딕셔너리
        """
        try:
            # 감정 분석 병합 (공통 로직 우선, Claude 보조)
            final_emotion = shared_result.emotion_detected
            if claude_result.get("emotion_detected") and shared_result.confidence < 0.6:
                # 신뢰도가 낮으면 Claude 감정 분석 참고
                claude_emotion = claude_result.get("emotion_detected")
                if claude_emotion != "neutral":
                    final_emotion = f"{shared_result.emotion_detected}+{claude_emotion}"

            # 전략 추천 병합
            final_strategy = shared_result.strategy_suggested
            if (
                claude_result.get("strategy_suggested")
                and shared_result.confidence < 0.6
            ):
                claude_strategy = claude_result.get("strategy_suggested")
                if claude_strategy and claude_strategy != "balanced":
                    final_strategy = (
                        f"{shared_result.strategy_suggested}+{claude_strategy}"
                    )

            # 판단 내용 병합 (Claude 주, 공통 로직 보강)
            base_judgment = claude_result.get("judgment", shared_result.judgment)

            # 공통 로직의 추가 인사이트 추가
            if (
                shared_result.confidence > 0.5
                and shared_result.judgment != base_judgment
            ):
                enhanced_judgment = (
                    f"{base_judgment}\n\n[보조 분석] {shared_result.judgment}"
                )
            else:
                enhanced_judgment = base_judgment

            # 신뢰도 계산 (가중 평균)
            claude_confidence = claude_result.get("confidence", 0.5)
            if mode == "hybrid":
                # 하이브리드 모드에서는 공통 로직 가중치 높임
                final_confidence = (
                    shared_result.confidence * 0.7 + claude_confidence * 0.3
                )
            else:
                # 강화 모드에서는 Claude 가중치 높임
                final_confidence = (
                    shared_result.confidence * 0.4 + claude_confidence * 0.6
                )

            # 추론 과정 병합
            reasoning_parts = []
            reasoning_parts.extend(
                shared_result.reasoning_trace[-3:]
            )  # 공통 로직 마지막 3단계
            if claude_result.get("reasoning"):
                reasoning_parts.append(f"Claude 분석: {claude_result['reasoning']}")

            # 대안 제안 병합
            alternatives = list(shared_result.alternatives)
            if claude_result.get("alternatives"):
                alternatives.extend(claude_result["alternatives"])
            alternatives = list(dict.fromkeys(alternatives))[:3]  # 중복 제거, 최대 3개

            # 최종 결과 구성
            merged_result = {
                "judgment": enhanced_judgment,
                "confidence": round(final_confidence, 3),
                "reasoning": " → ".join(reasoning_parts),
                "emotion_detected": final_emotion,
                "strategy_suggested": final_strategy,
                "alternatives": alternatives,
                "processing_time": shared_result.processing_time
                + claude_result.get("processing_time", 0),
                "context_detected": shared_result.context_detected,
                "keywords_extracted": shared_result.keywords_extracted,
                "patterns_matched": shared_result.patterns_matched,
                # 메타 정보
                "merged_mode": mode,
                "shared_confidence": shared_result.confidence,
                "claude_confidence": claude_confidence,
                "shared_judgment": shared_result.judgment,
                "claude_judgment": claude_result.get("judgment", ""),
                "stage_timings": shared_result.stage_timings,
            }

            return merged_result

        except Exception as e:
            print(f"⚠️ 판단 병합 실패: {e}")
            # 병합 실패 시 Claude 결과 반환
            return claude_result

    def _convert_shared_to_api_format(
        self, shared_result, prompt: str, context: str
    ) -> dict:
        """
        SharedJudgmentResult를 API 형식으로 변환

        Args:
            shared_result: SharedJudgmentResult 객체
            prompt: 원본 프롬프트
            context: 문맥 정보

        Returns:
            API 형식 판단 결과 딕셔너리
        """
        return {
            "judgment": shared_result.judgment,
            "confidence": shared_result.confidence,
            "reasoning": " → ".join(shared_result.reasoning_trace),
            "emotion_detected": shared_result.emotion_detected,
            "strategy_suggested": shared_result.strategy_suggested,
            "alternatives": shared_result.alternatives,
            "processing_time": shared_result.processing_time,
            "context_detected": shared_result.context_detected,
            "keywords_extracted": shared_result.keywords_extracted,
            "patterns_matched": shared_result.patterns_matched,
            "judgment_mode": shared_result.judgment_mode.value,
            "stage_timings": shared_result.stage_timings,
            "shared_logic_only": True,
        }

    def _emergency_fallback(self, prompt: str, context: str = None) -> dict:
        """
        비상 폴백 (모든 방법 실패 시)

        Args:
            prompt: 판단 요청 텍스트
            context: 추가 맥락 정보

        Returns:
            기본 판단 결과 딕셔너리
        """
        return {
            "judgment": "입력을 분석했지만 명확한 판단을 내리기 어려운 상황입니다.",
            "confidence": 0.1,
            "reasoning": "시스템 오류로 인한 기본 응답",
            "emotion_detected": "neutral",
            "strategy_suggested": "cautious",
            "alternatives": [],
            "processing_time": 0.001,
            "fallback_used": True,
            "emergency_mode": True,
        }

    def get_performance_stats(self) -> dict:
        """성능 통계 반환"""
        total = max(self.performance_stats["total_requests"], 1)

        # 기본 성능 통계
        basic_stats = {
            **self.performance_stats,
            "claude_ratio": self.performance_stats["claude_requests"] / total,
            "fallback_ratio": self.performance_stats["fallback_requests"] / total,
            "hybrid_ratio": self.performance_stats["hybrid_requests"] / total,
            "failure_rate": self.performance_stats["failed_requests"] / total,
            "judge_mode": self.judge_mode,
            "shared_engine_stats": (
                self.shared_engine.get_performance_stats()
                if hasattr(self.shared_engine, "get_performance_stats")
                else {}
            ),
        }

        # 모드 전환기 통계 추가
        if hasattr(self, "mode_switcher") and self.mode_switcher:
            switching_stats = self.mode_switcher.get_switching_stats()
            basic_stats["mode_switcher"] = switching_stats
            basic_stats["current_active_mode"] = switching_stats["current_mode"]
            basic_stats["total_mode_switches"] = switching_stats["total_switches"]

        return basic_stats

    def manual_switch_mode(
        self, target_mode: str, reason: str = "Manual override"
    ) -> bool:
        """
        수동 모드 전환

        Args:
            target_mode: 대상 모드 ("claude", "llm_free", "hybrid")
            reason: 전환 이유

        Returns:
            전환 성공 여부
        """
        try:
            mode_enum = JudgmentMode(target_mode)
            success = self.mode_switcher.switch_mode(
                mode_enum, SwitchingTrigger.MANUAL, reason
            )

            if success:
                self.judge_mode = target_mode
                print(f"🎛️ 수동 모드 전환 완료: {target_mode} ({reason})")

            return success

        except Exception as e:
            print(f"❌ 수동 모드 전환 실패: {e}")
            return False

    def get_mode_recommendation(self, prompt: str, context: str = None) -> dict:
        """
        현재 상황에 대한 모드 추천

        Args:
            prompt: 판단 요청 텍스트
            context: 추가 맥락 정보

        Returns:
            추천 정보 딕셔너리
        """
        judgment_context = self._build_judgment_context(prompt, context)
        recommended_mode, score, reason = self.mode_switcher.get_mode_recommendation(
            judgment_context
        )

        return {
            "recommended_mode": recommended_mode.value,
            "confidence_score": score,
            "reason": reason,
            "current_mode": self.mode_switcher.get_current_mode().value,
            "should_switch": recommended_mode != self.mode_switcher.get_current_mode(),
            "context_analysis": judgment_context,
        }


# 새로운 통합 함수 추가
def generate_response(input_data: dict) -> dict:
    """
    통합 응답 생성 함수

    Args:
        input_data: 입력 데이터 (text, context, judge_mode 등)

    Returns:
        판단 결과 딕셔너리
    """
    judge_mode = input_data.get("judge_mode", "claude")
    text = input_data.get("text", "")
    context = input_data.get("context", "")

    if judge_mode == "fallback":
        # quick_judgment 사용
        result = quick_judgment(text, context)
        judgment_data = {
            "judgment": result.judgment,
            "confidence": result.confidence,
            "reasoning": " → ".join(result.reasoning_trace),
            "emotion_detected": result.emotion_detected,
            "strategy_suggested": result.strategy_suggested,
            "alternatives": [],
            "processing_time": result.processing_time,
            "fallback_used": True,
            "judgment_mode": "fallback",
        }

        # 메타 로그 기록
        try:
            log_llm_free_judgment(
                input_text=text,
                judgment_data=judgment_data,
                context=context,
                meta_info={"runner_mode": "generate_response"},
            )
        except Exception as e:
            print(f"⚠️  메타 로그 기록 실패: {e}")

        return judgment_data
    else:
        # 기존 Claude 판단 사용
        runner = get_claude_runner(judge_mode=judge_mode)
        return runner.run_claude_judgment(text, context)


# 전역 인스턴스 생성 (API 성능 최적화)
_claude_runner = None


def get_claude_runner(
    api_mode: str = "mock", judge_mode: str = "claude"
) -> ClaudeJudgmentRunner:
    """판단기 인스턴스 반환 (싱글톤 패턴)"""
    global _claude_runner
    if _claude_runner is None:
        _claude_runner = ClaudeJudgmentRunner(api_mode=api_mode, judge_mode=judge_mode)
    return _claude_runner


def run_claude_judgment(
    prompt: str, context: str = None, judge_mode: str = "claude"
) -> dict:
    """
    판단 함수 (Claude, LLM-Free, Hybrid)

    Args:
        prompt: 판단 요청 텍스트
        context: 추가 맥락 정보
        judge_mode: 판단 모드 ("claude", "fallback", "hybrid")

    Returns:
        판단 결과 딕셔너리
    """
    runner = get_claude_runner(judge_mode=judge_mode)
    return runner.run_claude_judgment(prompt, context)


def run_fallback_judgment(prompt: str, context: str = None) -> dict:
    """
    LLM-Free 판단 함수 (편의 함수)

    Args:
        prompt: 판단 요청 텍스트
        context: 추가 맥락 정보

    Returns:
        LLM-Free 판단 결과 딕셔너리
    """
    return run_claude_judgment(prompt, context, judge_mode="fallback")


def run_hybrid_judgment(prompt: str, context: str = None) -> dict:
    """
    하이브리드 판단 함수 (편의 함수)

    Args:
        prompt: 판단 요청 텍스트
        context: 추가 맥락 정보

    Returns:
        하이브리드 판단 결과 딕셔너리
    """
    return run_claude_judgment(prompt, context, judge_mode="hybrid")


def run_enhanced_claude_judgment(prompt: str, context: str = None) -> dict:
    """
    강화된 Claude 판단 함수 (편의 함수)
    공통 로직으로 감정/전략 분석 후 Claude와 병합

    Args:
        prompt: 판단 요청 텍스트
        context: 추가 맥락 정보

    Returns:
        강화된 Claude 판단 결과 딕셔너리
    """
    return run_claude_judgment(prompt, context, judge_mode="claude")


def get_current_judgment_mode() -> str:
    """현재 활성 판단 모드 반환"""
    runner = get_claude_runner()
    return runner.mode_switcher.get_current_mode().value


def switch_judgment_mode(target_mode: str, reason: str = "Manual switch") -> bool:
    """
    판단 모드 수동 전환

    Args:
        target_mode: 대상 모드 ("claude", "llm_free", "hybrid")
        reason: 전환 이유

    Returns:
        전환 성공 여부
    """
    runner = get_claude_runner()
    return runner.manual_switch_mode(target_mode, reason)


def get_judgment_mode_recommendation(prompt: str, context: str = None) -> dict:
    """
    현재 상황에 대한 모드 추천

    Args:
        prompt: 판단 요청 텍스트
        context: 추가 맥락 정보

    Returns:
        추천 정보 딕셔너리
    """
    runner = get_claude_runner()
    return runner.get_mode_recommendation(prompt, context)


def get_mode_switching_stats() -> dict:
    """모드 전환 통계 반환"""
    runner = get_claude_runner()
    return runner.get_performance_stats().get("mode_switcher", {})
