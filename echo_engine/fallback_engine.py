#!/usr/bin/env python3
"""
🔄 Fallback Engine - 구조화된 판단 폴백 체인

EchoJudgmentSystem의 다단계 폴백 판단 엔진.
Echo Core → Claude → Mistral → FIST Templates → Static Response 순서로
안정적인 판단 결과를 보장합니다.

핵심 역할:
1. 다단계 폴백 체인 관리
2. 감정×전략 기반 템플릿 매칭 (36개 조합)
3. 판단 실패율 최소화
4. 응답 품질 보장 및 모니터링
"""

import time
import asyncio
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class FallbackStage(Enum):
    """폴백 단계 정의"""

    ECHO_CORE = "echo_core"
    CLAUDE_API = "claude_api"
    MISTRAL_LOCAL = "mistral_local"
    FIST_TEMPLATES = "fist_templates"
    STATIC_RESPONSE = "static_response"


@dataclass
class FallbackContext:
    """폴백 컨텍스트"""

    user_input: str
    emotion: str = "neutral"
    strategy: str = "adapt"
    confidence_threshold: float = 0.5
    max_attempts: int = 3
    timeout_per_stage: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None


@dataclass
class FallbackResult:
    """폴백 결과"""

    success: bool
    response_text: str
    stage_used: FallbackStage
    confidence: float
    processing_time: float
    attempts_made: int
    fallback_chain: List[str]
    template_used: Optional[str] = None
    error_messages: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FallbackJudgmentEngine:
    """🔄 폴백 판단 엔진"""

    def __init__(self, template_dir: str = "echo_engine/templates"):
        self.version = "1.0.0"
        self.template_dir = template_dir

        # 폴백 통계
        self.fallback_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "stage_usage": {},
            "average_processing_time": 0.0,
            "failure_rate_by_stage": {},
            "template_usage": {},
            "emotion_strategy_combinations": {},
        }

        # 폴백 체인 정의 (빠른 테스트를 위해 FIST 템플릿부터 시작)
        self.fallback_chain = [
            # FallbackStage.ECHO_CORE,  # 임시 비활성화
            # FallbackStage.CLAUDE_API,  # 임시 비활성화
            # FallbackStage.MISTRAL_LOCAL,  # 임시 비활성화
            FallbackStage.FIST_TEMPLATES,
            FallbackStage.STATIC_RESPONSE,
        ]

        # 단계별 핸들러 등록
        self.stage_handlers = self._register_stage_handlers()

        print(f"🔄 Fallback Judgment Engine v{self.version} 초기화 완료")
        print(
            f"   폴백 체인: {' → '.join([stage.value for stage in self.fallback_chain])}"
        )

    def judge(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> FallbackResult:
        """🎯 메인 폴백 판단 함수"""

        start_time = time.time()
        self.fallback_stats["total_requests"] += 1

        # 컨텍스트 준비
        fallback_context = self._prepare_fallback_context(user_input, context or {})

        # 감정 추론
        emotion = self._infer_primary_emotion(user_input)
        fallback_context.emotion = emotion

        # 전략 선택
        strategy = self._select_strategy(user_input, emotion)
        fallback_context.strategy = strategy

        print(f"🔄 폴백 판단 시작: {user_input[:50]}...")
        print(f"   감정: {emotion}, 전략: {strategy}")

        # 폴백 체인 실행
        fallback_chain_log = []
        attempts_made = 0
        last_errors = []

        for stage in self.fallback_chain:
            attempts_made += 1
            stage_name = stage.value
            fallback_chain_log.append(stage_name)

            print(f"🎯 시도 {attempts_made}: {stage_name}")

            try:
                # 단계별 판단 시도
                stage_result = self._execute_stage(stage, fallback_context)

                if stage_result["success"]:
                    # 성공한 경우
                    processing_time = time.time() - start_time

                    result = FallbackResult(
                        success=True,
                        response_text=stage_result["response_text"],
                        stage_used=stage,
                        confidence=stage_result.get("confidence", 0.5),
                        processing_time=processing_time,
                        attempts_made=attempts_made,
                        fallback_chain=fallback_chain_log,
                        template_used=stage_result.get("template_used"),
                        metadata=stage_result.get("metadata", {}),
                    )

                    # 성공 통계 업데이트
                    self._update_success_stats(
                        stage, processing_time, emotion, strategy
                    )

                    print(f"✅ 폴백 판단 성공: {stage_name} 단계에서 해결")
                    return result
                else:
                    # 실패한 경우, 다음 단계로
                    error_msg = stage_result.get("error", f"{stage_name} 단계 실패")
                    last_errors.append(error_msg)
                    print(f"❌ {stage_name} 단계 실패: {error_msg}")

                    # 실패 통계 업데이트
                    self._update_failure_stats(stage)

            except Exception as e:
                error_msg = f"{stage_name} 단계 오류: {e}"
                last_errors.append(error_msg)
                print(f"❌ {error_msg}")
                self._update_failure_stats(stage)

        # 모든 단계 실패한 경우
        processing_time = time.time() - start_time

        result = FallbackResult(
            success=False,
            response_text="죄송합니다. 현재 시스템에 일시적인 문제가 있어 적절한 응답을 드리지 못했습니다.",
            stage_used=FallbackStage.STATIC_RESPONSE,
            confidence=0.1,
            processing_time=processing_time,
            attempts_made=attempts_made,
            fallback_chain=fallback_chain_log,
            error_messages=last_errors,
        )

        print(f"❌ 모든 폴백 단계 실패")
        return result

    def _prepare_fallback_context(
        self, user_input: str, context: Dict[str, Any]
    ) -> FallbackContext:
        """폴백 컨텍스트 준비"""
        return FallbackContext(
            user_input=user_input,
            confidence_threshold=context.get("confidence_threshold", 0.5),
            max_attempts=context.get("max_attempts", 3),
            timeout_per_stage=context.get("timeout_per_stage", 30.0),
            metadata=context,
            session_id=context.get("session_id"),
        )

    def _infer_primary_emotion(self, user_input: str) -> str:
        """감정 추론"""
        try:
            # 절대 import 시도
            from echo_engine.emotion_infer import infer_emotion

            emotion_result = infer_emotion(user_input)

            # EmotionInferenceResult 객체인 경우
            if hasattr(emotion_result, "primary_emotion"):
                return emotion_result.primary_emotion
            # 딕셔너리인 경우
            elif isinstance(emotion_result, dict):
                return emotion_result.get("primary_emotion", "neutral")
            # 문자열인 경우
            elif isinstance(emotion_result, str):
                return emotion_result
            else:
                return "neutral"

        except ImportError:
            try:
                # 상대 import 시도
                from .emotion_infer import infer_emotion

                emotion_result = infer_emotion(user_input)
                if hasattr(emotion_result, "primary_emotion"):
                    return emotion_result.primary_emotion
                elif isinstance(emotion_result, dict):
                    return emotion_result.get("primary_emotion", "neutral")
                else:
                    return "neutral"
            except Exception:
                # 기본 감정 추론 (키워드 기반)
                return self._basic_emotion_inference(user_input)
        except Exception as e:
            print(f"⚠️ 감정 추론 실패: {e}")
            return self._basic_emotion_inference(user_input)

    def _select_strategy(self, user_input: str, emotion: str) -> str:
        """전략 선택"""
        try:
            # 절대 import 시도
            from echo_engine.strategy_picker import pick_strategy

            strategy_result = pick_strategy(user_input, emotion)

            # StrategyType enum인 경우
            if hasattr(strategy_result, "value"):
                return strategy_result.value
            # 문자열인 경우
            elif isinstance(strategy_result, str):
                return strategy_result
            else:
                return "adapt"

        except ImportError:
            try:
                # 상대 import 시도
                from .strategy_picker import pick_strategy

                strategy_result = pick_strategy(user_input, emotion)
                if hasattr(strategy_result, "value"):
                    return strategy_result.value
                else:
                    return (
                        strategy_result if isinstance(strategy_result, str) else "adapt"
                    )
            except Exception:
                # 기본 전략 선택 (감정 기반)
                return self._basic_strategy_selection(emotion, user_input)
        except Exception as e:
            print(f"⚠️ 전략 선택 실패: {e}")
            return self._basic_strategy_selection(emotion, user_input)

    def _register_stage_handlers(self) -> Dict[FallbackStage, Callable]:
        """단계별 핸들러 등록"""
        return {
            FallbackStage.ECHO_CORE: self._handle_echo_core,
            FallbackStage.CLAUDE_API: self._handle_claude_api,
            FallbackStage.MISTRAL_LOCAL: self._handle_mistral_local,
            FallbackStage.FIST_TEMPLATES: self._handle_fist_templates,
            FallbackStage.STATIC_RESPONSE: self._handle_static_response,
        }

    def _execute_stage(
        self, stage: FallbackStage, context: FallbackContext
    ) -> Dict[str, Any]:
        """단계별 실행"""
        handler = self.stage_handlers.get(stage)
        if not handler:
            return {"success": False, "error": f"핸들러를 찾을 수 없음: {stage.value}"}

        return handler(context)

    def _handle_echo_core(self, context: FallbackContext) -> Dict[str, Any]:
        """Echo Core 판단 시도"""
        try:
            # 절대 import 시도
            from echo_engine.loop_orchestrator import run_judgment_loop

            result = run_judgment_loop(context.user_input, context.metadata)

            if result and result.get("response_text"):
                return {
                    "success": True,
                    "response_text": result["response_text"],
                    "confidence": result.get("confidence", 0.8),
                    "metadata": {"source": "echo_core", "result": result},
                }
            else:
                return {"success": False, "error": "Echo Core 응답 없음"}

        except ImportError:
            # 상대 import 시도
            try:
                from .loop_orchestrator import run_judgment_loop

                result = run_judgment_loop(context.user_input, context.metadata)
                if result and result.get("response_text"):
                    return {
                        "success": True,
                        "response_text": result["response_text"],
                        "confidence": result.get("confidence", 0.8),
                        "metadata": {"source": "echo_core", "result": result},
                    }
                else:
                    return {"success": False, "error": "Echo Core 응답 없음"}
            except Exception:
                return {"success": False, "error": "Echo Core 모듈 없음"}
        except Exception as e:
            return {"success": False, "error": f"Echo Core 오류: {e}"}

    def _handle_claude_api(self, context: FallbackContext) -> Dict[str, Any]:
        """Claude API 판단 시도"""
        try:
            # Claude API 호출 (실제 구현 필요)
            # 현재는 모의 구현

            if len(context.user_input) > 500:
                # 복잡한 입력에 대해서는 Claude가 잘 처리할 것으로 가정
                response = f"Claude API를 통해 '{context.user_input[:50]}...'에 대해 분석했습니다."
                return {
                    "success": True,
                    "response_text": response,
                    "confidence": 0.85,
                    "metadata": {"source": "claude_api", "mock": True},
                }
            else:
                return {"success": False, "error": "Claude API 연결 실패 (모의)"}

        except Exception as e:
            return {"success": False, "error": f"Claude API 오류: {e}"}

    def _handle_mistral_local(self, context: FallbackContext) -> Dict[str, Any]:
        """Mistral 로컬 모델 판단 시도"""
        try:
            # 절대 import 시도
            from echo_engine.mistral_adapter import MistralAdapter

            adapter = MistralAdapter()
            result = adapter.generate_response(context.user_input)

            if result and result.get("response"):
                return {
                    "success": True,
                    "response_text": result["response"],
                    "confidence": result.get("confidence", 0.7),
                    "metadata": {
                        "source": "mistral_local",
                        "model": result.get("model"),
                    },
                }
            else:
                return {"success": False, "error": "Mistral 응답 생성 실패"}

        except ImportError:
            # 상대 import 시도
            try:
                from .mistral_adapter import MistralAdapter

                adapter = MistralAdapter()
                result = adapter.generate_response(context.user_input)
                if result and result.get("response"):
                    return {
                        "success": True,
                        "response_text": result["response"],
                        "confidence": result.get("confidence", 0.7),
                        "metadata": {
                            "source": "mistral_local",
                            "model": result.get("model"),
                        },
                    }
                else:
                    return {"success": False, "error": "Mistral 응답 생성 실패"}
            except Exception:
                return {"success": False, "error": "Mistral 모듈 없음"}
        except Exception as e:
            return {"success": False, "error": f"Mistral 오류: {e}"}

    def _handle_fist_templates(self, context: FallbackContext) -> Dict[str, Any]:
        """FIST 템플릿 판단 시도 (36개 감정×전략 조합) - 지연 로딩 적용"""
        try:
            # 지연 로딩 템플릿 엔진 사용
            from echo_engine.fist_templates.lazy_template_engine import (
                get_lazy_template_engine,
            )

            lazy_engine = get_lazy_template_engine()

            # 감정×전략 조합 템플릿 시도
            template = lazy_engine.get_emotion_strategy_template(
                context.emotion, context.strategy
            )
            template_key = f"{context.emotion}_{context.strategy}"

            if template:
                # 템플릿으로 응답 생성
                template_context = {"input_text": context.user_input}
                rendered_response = template.get_full_prompt(template_context)

                return {
                    "success": True,
                    "response_text": rendered_response,
                    "confidence": 0.6,
                    "template_used": template_key,
                    "metadata": {
                        "source": "fist_templates_lazy",
                        "emotion": context.emotion,
                        "strategy": context.strategy,
                        "template_id": template.template_id,
                    },
                }
            else:
                # 폴백: YAML 파일에서 로드 시도
                template_result = self._load_fist_template(template_key)

                if template_result:
                    rendered_response = self._render_fist_template(
                        template_result, context
                    )

                    return {
                        "success": True,
                        "response_text": rendered_response,
                        "confidence": 0.6,
                        "template_used": template_key,
                        "metadata": {
                            "source": "fist_templates_yaml",
                            "emotion": context.emotion,
                            "strategy": context.strategy,
                            "template": template_result,
                        },
                    }
                else:
                    return {
                        "success": False,
                        "error": f"템플릿을 찾을 수 없음: {template_key}",
                    }

        except Exception as e:
            return {"success": False, "error": f"FIST 템플릿 오류: {e}"}

    def _handle_static_response(self, context: FallbackContext) -> Dict[str, Any]:
        """정적 응답 (최종 폴백)"""
        # 감정별 정적 응답
        emotion_responses = {
            "joy": f"기쁜 마음이 느껴지네요! '{context.user_input}'에 대해 더 자세히 이야기해주세요.",
            "sadness": f"힘드신 상황이시군요. '{context.user_input}'에 대해 충분히 이해합니다.",
            "anger": f"속상하셨을 것 같아요. '{context.user_input}'에 대해 함께 생각해보겠습니다.",
            "fear": f"걱정이 많으시군요. '{context.user_input}'에 대해 차근차근 살펴보겠습니다.",
            "surprise": f"놀라운 상황이시네요! '{context.user_input}'에 대해 더 알려주세요.",
            "neutral": f"말씀해주신 '{context.user_input}'에 대해 생각해보고 있습니다.",
        }

        response = emotion_responses.get(context.emotion, emotion_responses["neutral"])

        return {
            "success": True,
            "response_text": response,
            "confidence": 0.3,
            "metadata": {
                "source": "static_response",
                "emotion": context.emotion,
                "fallback": True,
            },
        }

    def _load_fist_template(self, template_key: str) -> Optional[Dict[str, Any]]:
        """FIST 템플릿 로드"""
        try:
            import yaml

            template_file = (
                Path(self.template_dir) / "fist_autogen" / f"{template_key}.yaml"
            )

            if template_file.exists():
                with open(template_file, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)

            return None

        except Exception as e:
            print(f"⚠️ 템플릿 로드 실패 {template_key}: {e}")
            return None

    def _render_fist_template(
        self, template: Dict[str, Any], context: FallbackContext
    ) -> str:
        """FIST 템플릿 렌더링"""
        try:
            frame = template.get("frame", "상황을 분석하고 있습니다.")
            insight = template.get("insight", "통찰을 도출하고 있습니다.")
            tactics = template.get("tactics", "구체적인 방안을 생각하고 있습니다.")

            # 간단한 변수 치환
            frame = frame.replace("{input_text}", context.user_input)
            insight = insight.replace("{input_text}", context.user_input)
            tactics = tactics.replace("{input_text}", context.user_input)

            # FIST 구조 기반 응답 생성
            response = f"{frame}\n\n{insight}\n\n{tactics}"

            return response

        except Exception as e:
            print(f"⚠️ 템플릿 렌더링 실패: {e}")
            return f"템플릿 기반으로 '{context.user_input}'에 대해 응답하겠습니다."

    def _update_success_stats(
        self, stage: FallbackStage, processing_time: float, emotion: str, strategy: str
    ):
        """성공 통계 업데이트"""
        self.fallback_stats["successful_requests"] += 1

        # 단계별 사용 통계
        stage_name = stage.value
        self.fallback_stats["stage_usage"][stage_name] = (
            self.fallback_stats["stage_usage"].get(stage_name, 0) + 1
        )

        # 평균 처리 시간 업데이트
        total_successful = self.fallback_stats["successful_requests"]
        current_avg = self.fallback_stats["average_processing_time"]

        if total_successful == 1:
            self.fallback_stats["average_processing_time"] = processing_time
        else:
            new_avg = (
                current_avg * (total_successful - 1) + processing_time
            ) / total_successful
            self.fallback_stats["average_processing_time"] = new_avg

        # 감정×전략 조합 통계
        combination = f"{emotion}_{strategy}"
        self.fallback_stats["emotion_strategy_combinations"][combination] = (
            self.fallback_stats["emotion_strategy_combinations"].get(combination, 0) + 1
        )

    def _update_failure_stats(self, stage: FallbackStage):
        """실패 통계 업데이트"""
        stage_name = stage.value

        # 단계별 실패율 추적
        if stage_name not in self.fallback_stats["failure_rate_by_stage"]:
            self.fallback_stats["failure_rate_by_stage"][stage_name] = {
                "attempts": 0,
                "failures": 0,
            }

        self.fallback_stats["failure_rate_by_stage"][stage_name]["attempts"] += 1
        self.fallback_stats["failure_rate_by_stage"][stage_name]["failures"] += 1

    def get_fallback_stats(self) -> Dict[str, Any]:
        """폴백 통계 반환"""
        stats = self.fallback_stats.copy()

        # 성공률 계산
        total_requests = max(stats["total_requests"], 1)
        stats["overall_success_rate"] = (
            stats["successful_requests"] / total_requests
        ) * 100

        # 단계별 실패율 계산
        for stage_name, failure_data in stats["failure_rate_by_stage"].items():
            attempts = failure_data["attempts"]
            failures = failure_data["failures"]
            if attempts > 0:
                failure_data["failure_rate"] = (failures / attempts) * 100

        # 가장 많이 사용된 단계
        if stats["stage_usage"]:
            most_used_stage = max(stats["stage_usage"].items(), key=lambda x: x[1])
            stats["most_used_stage"] = {
                "stage": most_used_stage[0],
                "count": most_used_stage[1],
                "percentage": (most_used_stage[1] / total_requests) * 100,
            }

        return stats

    def _basic_emotion_inference(self, user_input: str) -> str:
        """기본 감정 추론 (키워드 기반)"""
        text_lower = user_input.lower()

        emotion_keywords = {
            "joy": [
                "기쁘",
                "좋",
                "행복",
                "즐거",
                "만족",
                "신나",
                "재미",
                "웃",
                "기분좋",
            ],
            "sadness": [
                "슬프",
                "우울",
                "힘들",
                "속상",
                "아쉽",
                "외로",
                "허무",
                "울",
                "눈물",
            ],
            "anger": [
                "화",
                "짜증",
                "빡",
                "분노",
                "열받",
                "억울",
                "답답",
                "미치",
                "개념",
            ],
            "fear": [
                "무서",
                "두려",
                "불안",
                "걱정",
                "초조",
                "긴장",
                "스트레스",
                "위험",
            ],
            "surprise": ["놀라", "신기", "와", "헉", "어", "정말", "진짜", "대박"],
        }

        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score

        if emotion_scores:
            return max(emotion_scores.items(), key=lambda x: x[1])[0]
        else:
            return "neutral"

    def _basic_strategy_selection(self, emotion: str, user_input: str) -> str:
        """기본 전략 선택 (감정 기반)"""

        # 감정별 기본 전략 매핑
        emotion_strategy_map = {
            "joy": "initiate",
            "sadness": "retreat",
            "anger": "confront",
            "fear": "analyze",
            "surprise": "analyze",
            "neutral": "adapt",
        }

        base_strategy = emotion_strategy_map.get(emotion, "adapt")

        # 텍스트 패턴으로 조정
        text_lower = user_input.lower()

        if any(word in text_lower for word in ["문제", "해결", "어떻게", "방법"]):
            return "analyze"
        elif any(word in text_lower for word in ["새로운", "만들", "아이디어", "창의"]):
            return "initiate"
        elif any(word in text_lower for word in ["도움", "지원", "같이", "함께"]):
            return "harmonize"
        elif any(word in text_lower for word in ["급", "빨리", "당장", "시급"]):
            return "confront"
        elif any(word in text_lower for word in ["쉬", "휴식", "그만", "멈춰"]):
            return "retreat"
        else:
            return base_strategy


# 글로벌 인스턴스
_global_fallback_engine = None


def get_fallback_engine() -> FallbackJudgmentEngine:
    """글로벌 폴백 엔진 인스턴스 반환"""
    global _global_fallback_engine
    if _global_fallback_engine is None:
        _global_fallback_engine = FallbackJudgmentEngine()
    return _global_fallback_engine


def fallback_judge(
    user_input: str, context: Optional[Dict[str, Any]] = None
) -> FallbackResult:
    """🔄 폴백 판단 - 메인 진입점"""
    engine = get_fallback_engine()
    return engine.judge(user_input, context)


if __name__ == "__main__":
    # 폴백 엔진 테스트
    print("🧪 Fallback Engine 테스트")

    test_cases = [
        {"input": "요즘 너무 힘들어서 우울해요", "description": "감정적 지원 요청"},
        {
            "input": "새로운 프로젝트 아이디어를 생각해보고 있어요",
            "description": "창의적 요청",
        },
        {
            "input": "복잡한 문제를 해결해야 하는데 어떻게 접근해야 할까요?",
            "description": "문제 해결 요청",
        },
        {"input": "안녕하세요", "description": "간단한 인사"},
    ]

    engine = get_fallback_engine()

    for i, case in enumerate(test_cases, 1):
        print(f"\n🎯 테스트 {i}: {case['description']}")
        print(f"   입력: {case['input']}")

        result = engine.judge(case["input"])

        print(f"   성공: {result.success}")
        print(f"   사용된 단계: {result.stage_used.value}")
        print(f"   신뢰도: {result.confidence:.2f}")
        print(f"   처리 시간: {result.processing_time:.3f}초")
        print(f"   응답: {result.response_text[:100]}...")

        if result.template_used:
            print(f"   사용된 템플릿: {result.template_used}")

    # 통계 출력
    stats = engine.get_fallback_stats()
    print(f"\n📊 폴백 엔진 통계:")
    print(f"   총 요청: {stats['total_requests']}")
    print(f"   성공률: {stats['overall_success_rate']:.1f}%")
    print(f"   평균 처리시간: {stats['average_processing_time']:.3f}초")

    if stats.get("most_used_stage"):
        most_used = stats["most_used_stage"]
        print(
            f"   가장 많이 사용된 단계: {most_used['stage']} ({most_used['percentage']:.1f}%)"
        )

    if stats["emotion_strategy_combinations"]:
        print(
            f"   감정×전략 조합 사용: {len(stats['emotion_strategy_combinations'])}가지"
        )
