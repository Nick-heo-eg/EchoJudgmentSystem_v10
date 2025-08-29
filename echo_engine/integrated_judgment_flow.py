#!/usr/bin/env python3
"""
🧩 EchoJudgmentSystem v10.5 - Integrated Judgment Flow
Persona⨯Reasoning⨯Action 통합 판단 흐름

이 모듈은 다음 구조를 구현합니다:
Signature → Persona → Emotion → Strategy → Reasoner → Q-Table → Judgment → MetaLog

양쪽 판단 흐름(LLM-Free, Claude)에서 공통으로 사용 가능합니다.
"""

import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# 내부 모듈들
try:
    from .persona_core_optimized_bridge import PersonaCore, PersonaProfile, create_persona_from_signature
    from .q_strategy_selector import (
        QTableStrategySelector,
        QState,
        QAction,
        ActionType,
        create_q_state_from_judgment_context,
    )
    from .shared_judgment_logic import (
        SharedJudgmentEngine,
        JudgmentRequest,
        JudgmentMode,
        get_shared_judgment_engine,
    )
except ImportError:
    # 개발/테스트 시 상대 임포트
    import sys
    import os

    # sys.path 수정 불필요
    from .persona_core_optimized_bridge import PersonaCore, PersonaProfile, create_persona_from_signature
    from q_strategy_selector import (
        QTableStrategySelector,
        QState,
        QAction,
        ActionType,
        create_q_state_from_judgment_context,
    )
    from shared_judgment_logic import (
        SharedJudgmentEngine,
        JudgmentRequest,
        JudgmentMode,
        get_shared_judgment_engine,
    )

# Claude Reasoning (선택적)
try:
    import sys
    import os

    # sys.path 수정 불필요
    from .reasoning import ReasoningChain, ReasoningStep

    REASONING_AVAILABLE = True
except ImportError:
    REASONING_AVAILABLE = False
    print("⚠️ Claude Reasoning 모듈 없음 - 기본 추론 사용")


class JudgmentFlowMode(Enum):
    """판단 흐름 모드"""

    LLM_FREE = "llm_free"
    CLAUDE = "claude"
    HYBRID = "hybrid"
    PERSONA_ENHANCED = "persona_enhanced"


class ReasoningMode(Enum):
    """추론 모드"""

    PATTERN_BASED = "pattern_based"  # LLM-Free 패턴 기반
    CLAUDE_BASED = "claude_based"  # Claude 추론
    HYBRID_REASONING = "hybrid"  # 혼합 추론
    Q_ENHANCED = "q_enhanced"  # Q-Table 강화


@dataclass
class IntegratedJudgmentResult:
    """통합 판단 결과"""

    # 핵심 결과
    judgment: str
    confidence: float

    # 각 단계별 결과
    signature_applied: str
    persona_analysis: Dict[str, Any]
    emotion_analysis: Dict[str, Any]
    strategy_selection: Dict[str, Any]
    reasoning_result: Dict[str, Any]
    q_action_selected: Dict[str, Any]

    # 메타 정보
    processing_time: float
    flow_mode: JudgmentFlowMode
    reasoning_mode: ReasoningMode

    # 학습 데이터
    persona_state: Dict[str, Any] = field(default_factory=dict)
    q_learning_reward: float = 0.0
    meta_insights: List[str] = field(default_factory=list)

    # 추적 정보
    stage_timings: Dict[str, float] = field(default_factory=dict)
    debug_info: Dict[str, Any] = field(default_factory=dict)


class IntegratedJudgmentEngine:
    """통합 판단 엔진 - Persona⨯Reasoning⨯Action"""

    def __init__(
        self,
        default_signature: str = "Echo-Phoenix",
        flow_mode: JudgmentFlowMode = JudgmentFlowMode.HYBRID,
        reasoning_mode: ReasoningMode = ReasoningMode.PATTERN_BASED,
        enable_q_learning: bool = True,
        enable_meta_reflection: bool = True,
    ):
        """
        통합 판단 엔진 초기화

        Args:
            default_signature: 기본 시그니처
            flow_mode: 판단 흐름 모드
            reasoning_mode: 추론 모드
            enable_q_learning: Q-Learning 활성화
            enable_meta_reflection: 메타 반성 활성화
        """
        self.default_signature = default_signature
        self.flow_mode = flow_mode
        self.reasoning_mode = reasoning_mode
        self.enable_q_learning = enable_q_learning
        self.enable_meta_reflection = enable_meta_reflection

        # 각 구성요소 초기화
        self._initialize_components()

        # 성능 통계
        self.total_judgments = 0
        self.successful_judgments = 0
        self.average_confidence = 0.0
        self.personas_used = {}

        print(f"🧩 통합 판단 엔진 초기화 완료")
        print(f"   기본 시그니처: {default_signature}")
        print(f"   흐름 모드: {flow_mode.value}")
        print(f"   추론 모드: {reasoning_mode.value}")
        print(f"   Q-Learning: {'활성화' if enable_q_learning else '비활성화'}")

    def _initialize_components(self):
        """구성요소들 초기화"""
        # 1. 페르소나 풀 생성
        self.personas = {}
        signature_types = ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"]

        for sig_type in signature_types:
            persona = create_persona_from_signature(sig_type)
            self.personas[sig_type] = persona

        print(f"🧠 페르소나 {len(self.personas)}개 초기화 완료")

        # 2. 공통 판단 엔진
        self.shared_engine = get_shared_judgment_engine()

        # 3. Q-Table 전략 선택기
        if self.enable_q_learning:
            self.q_selector = QTableStrategySelector(
                learning_rate=0.1, exploration_rate=0.2, exploration_decay=0.99
            )
        else:
            self.q_selector = None

        # 4. Claude 추론 체인 (선택적)
        if REASONING_AVAILABLE and self.reasoning_mode in [
            ReasoningMode.CLAUDE_BASED,
            ReasoningMode.HYBRID_REASONING,
        ]:
            self.reasoning_chain = ReasoningChain()
        else:
            self.reasoning_chain = None

        print(f"🧩 모든 구성요소 초기화 완료")

    def run_integrated_judgment(
        self,
        text: str,
        context: Optional[str] = None,
        signature: Optional[str] = None,
        custom_settings: Optional[Dict[str, Any]] = None,
    ) -> IntegratedJudgmentResult:
        """
        통합 판단 실행

        Args:
            text: 입력 텍스트
            context: 추가 컨텍스트
            signature: 사용할 시그니처 (None이면 기본값)
            custom_settings: 커스텀 설정

        Returns:
            통합 판단 결과
        """
        start_time = time.time()
        self.total_judgments += 1

        # 사용할 시그니처 결정
        active_signature = signature or self.default_signature

        # 결과 객체 초기화
        result = IntegratedJudgmentResult(
            judgment="",
            confidence=0.0,
            signature_applied=active_signature,
            persona_analysis={},
            emotion_analysis={},
            strategy_selection={},
            reasoning_result={},
            q_action_selected={},
            processing_time=0.0,
            flow_mode=self.flow_mode,
            reasoning_mode=self.reasoning_mode,
        )

        try:
            # === 단계 1: 시그니처 → 페르소나 활성화 ===
            stage_start = time.time()
            persona_result = self._activate_persona(active_signature, text, context)
            result.persona_analysis = persona_result
            result.stage_timings["persona_activation"] = time.time() - stage_start

            # === 단계 2: 페르소나 → 감정 분석 ===
            stage_start = time.time()
            emotion_result = self._analyze_emotion_with_persona(
                text, context, persona_result
            )
            result.emotion_analysis = emotion_result
            result.stage_timings["emotion_analysis"] = time.time() - stage_start

            # === 단계 3: 감정 → 전략 선택 ===
            stage_start = time.time()
            strategy_result = self._select_strategy_with_context(
                emotion_result, persona_result, context
            )
            result.strategy_selection = strategy_result
            result.stage_timings["strategy_selection"] = time.time() - stage_start

            # === 단계 4: 전략 → 추론 수행 ===
            stage_start = time.time()
            reasoning_result = self._perform_reasoning(
                text, context, emotion_result, strategy_result
            )
            result.reasoning_result = reasoning_result
            result.stage_timings["reasoning"] = time.time() - stage_start

            # === 단계 5: Q-Table 행동 선택 ===
            stage_start = time.time()
            q_action_result = self._select_q_action(
                emotion_result, strategy_result, reasoning_result
            )
            result.q_action_selected = q_action_result
            result.stage_timings["q_action_selection"] = time.time() - stage_start

            # === 단계 6: 최종 판단 생성 ===
            stage_start = time.time()
            final_judgment = self._generate_integrated_judgment(
                text,
                context,
                persona_result,
                emotion_result,
                strategy_result,
                reasoning_result,
                q_action_result,
            )
            result.judgment = final_judgment["judgment"]
            result.confidence = final_judgment["confidence"]
            result.stage_timings["judgment_generation"] = time.time() - stage_start

            # === 단계 7: 메타 로그 및 학습 ===
            stage_start = time.time()
            meta_result = self._perform_meta_learning(result, custom_settings)
            result.meta_insights = meta_result.get("insights", [])
            result.q_learning_reward = meta_result.get("reward", 0.0)
            result.stage_timings["meta_learning"] = time.time() - stage_start

            # 성공 통계 업데이트
            self.successful_judgments += 1

        except Exception as e:
            # 오류 처리
            result.judgment = f"통합 판단 처리 중 오류가 발생했습니다: {str(e)[:100]}"
            result.confidence = 0.0
            result.debug_info["error"] = str(e)
            print(f"❌ 통합 판단 오류: {e}")

        # 최종 처리 시간 계산
        result.processing_time = time.time() - start_time

        # 평균 신뢰도 업데이트
        total_confidence = (
            self.average_confidence * (self.total_judgments - 1) + result.confidence
        )
        self.average_confidence = total_confidence / self.total_judgments

        return result

    def _activate_persona(
        self, signature: str, text: str, context: Optional[str]
    ) -> Dict[str, Any]:
        """페르소나 활성화 및 분석"""
        if signature not in self.personas:
            signature = self.default_signature

        persona = self.personas[signature]

        # 페르소나별 사용 통계
        if signature not in self.personas_used:
            self.personas_used[signature] = 0
        self.personas_used[signature] += 1

        # 페르소나 처리
        persona_context = {
            "context_type": self._infer_context_type(context or ""),
            "urgency": self._infer_urgency(text),
            "complexity": self._infer_complexity(text),
        }

        persona_analysis = persona.process_input(text, persona_context)

        return {
            "signature_used": signature,
            "persona_name": persona_analysis["persona_name"],
            "persona_state": persona_analysis["persona_state"],
            "persona_confidence": persona_analysis["persona_confidence"],
            "energy_level": persona_analysis["energy_level"],
            "interaction_count": persona_analysis["interaction_count"],
            "meta_insights": persona_analysis["meta_insights"],
            "raw_persona_analysis": persona_analysis,
        }

    def _analyze_emotion_with_persona(
        self, text: str, context: Optional[str], persona_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """페르소나 강화된 감정 분석"""
        # 기본 감정 분석 (공통 엔진 사용)
        shared_request = JudgmentRequest(
            text=text,
            context=context,
            judgment_mode=JudgmentMode.HYBRID,
            include_emotion=True,
            include_strategy=False,
            include_context=True,
        )

        shared_result = self.shared_engine.process_judgment(shared_request)

        # 페르소나 감정 분석 가져오기
        persona_emotion = persona_result["raw_persona_analysis"]["emotion_analysis"]

        # 감정 융합 (페르소나 + 공통 엔진)
        shared_emotion = shared_result.emotion_detected
        shared_confidence = shared_result.confidence

        persona_emotion_detected = persona_emotion["primary_emotion"]
        persona_confidence = persona_emotion["intensity"]

        # 신뢰도 기반 가중 평균
        if shared_confidence > persona_confidence:
            final_emotion = shared_emotion
            final_confidence = shared_confidence * 0.7 + persona_confidence * 0.3
        else:
            final_emotion = persona_emotion_detected
            final_confidence = persona_confidence * 0.7 + shared_confidence * 0.3

        return {
            "primary_emotion": final_emotion,
            "confidence": final_confidence,
            "shared_engine_emotion": shared_emotion,
            "persona_emotion": persona_emotion_detected,
            "emotion_intensity": persona_emotion["intensity"],
            "intensity_category": persona_emotion["intensity_category"],
            "trigger_activated": persona_emotion.get("trigger_activated", False),
            "fusion_method": "confidence_weighted",
        }

    def _select_strategy_with_context(
        self,
        emotion_result: Dict[str, Any],
        persona_result: Dict[str, Any],
        context: Optional[str],
    ) -> Dict[str, Any]:
        """컨텍스트 강화된 전략 선택"""
        # 페르소나 전략 가져오기
        persona_strategy = persona_result["raw_persona_analysis"]["strategy_selection"]

        # Q-Table 추천 (있다면)
        q_recommendation = None
        if self.enable_q_learning and self.q_selector:
            q_state = create_q_state_from_judgment_context(
                emotion_result["primary_emotion"],
                emotion_result["confidence"],
                self._infer_context_type(context or ""),
                self._infer_urgency(context or ""),
                persona_result["energy_level"] / 100.0,  # 정규화
                persona_result["persona_confidence"],
            )

            q_recommendation = self.q_selector.get_strategy_recommendations(q_state)

        # 전략 통합 결정
        primary_strategy = persona_strategy["primary_strategy"]
        strategy_confidence = persona_strategy["confidence"]

        if q_recommendation and q_recommendation["primary_strategy"]:
            q_strategy = q_recommendation["primary_strategy"]
            q_confidence = (
                q_recommendation["strategy_scores"]
                .get(q_strategy, {})
                .get("score", 0.0)
            )

            # Q-Table 추천이 더 신뢰도가 높으면 사용
            if q_confidence > strategy_confidence:
                primary_strategy = q_strategy
                strategy_confidence = q_confidence

        return {
            "primary_strategy": primary_strategy,
            "confidence": strategy_confidence,
            "persona_strategy": persona_strategy["primary_strategy"],
            "q_recommended_strategy": (
                q_recommendation["primary_strategy"] if q_recommendation else None
            ),
            "alternative_strategies": persona_strategy.get("alternatives", []),
            "strategy_reasoning": f"페르소나 기반 전략 선택 (Q-Table 보강: {'예' if q_recommendation else '아니오'})",
        }

    def _perform_reasoning(
        self,
        text: str,
        context: Optional[str],
        emotion_result: Dict[str, Any],
        strategy_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """추론 수행 (모드에 따라)"""
        reasoning_start = time.time()

        if self.reasoning_mode == ReasoningMode.CLAUDE_BASED and self.reasoning_chain:
            # Claude 기반 추론
            reasoning_result = self._claude_reasoning(
                text, context, emotion_result, strategy_result
            )
        elif (
            self.reasoning_mode == ReasoningMode.HYBRID_REASONING
            and self.reasoning_chain
        ):
            # 혼합 추론
            reasoning_result = self._hybrid_reasoning(
                text, context, emotion_result, strategy_result
            )
        else:
            # 패턴 기반 추론 (기본)
            reasoning_result = self._pattern_based_reasoning(
                text, context, emotion_result, strategy_result
            )

        reasoning_time = time.time() - reasoning_start
        reasoning_result["reasoning_time"] = reasoning_time
        reasoning_result["reasoning_mode"] = self.reasoning_mode.value

        return reasoning_result

    def _claude_reasoning(
        self,
        text: str,
        context: Optional[str],
        emotion_result: Dict[str, Any],
        strategy_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Claude 기반 추론"""
        if not self.reasoning_chain:
            return self._pattern_based_reasoning(
                text, context, emotion_result, strategy_result
            )

        try:
            # Claude 추론 체인 실행
            reasoning_context = {
                "input_text": text,
                "context": context or "",
                "detected_emotion": emotion_result["primary_emotion"],
                "emotion_confidence": emotion_result["confidence"],
                "selected_strategy": strategy_result["primary_strategy"],
                "strategy_confidence": strategy_result["confidence"],
            }

            steps = [
                ReasoningStep(
                    "emotion_validation",
                    f"감정 '{emotion_result['primary_emotion']}' 분석을 검증하세요.",
                ),
                ReasoningStep(
                    "strategy_evaluation",
                    f"전략 '{strategy_result['primary_strategy']}' 적절성을 평가하세요.",
                ),
                ReasoningStep(
                    "context_integration", "주어진 컨텍스트와 상황을 종합 분석하세요."
                ),
                ReasoningStep(
                    "final_synthesis", "최종 판단을 위한 종합적 추론을 수행하세요."
                ),
            ]

            reasoning_result = self.reasoning_chain.execute_chain(
                steps, reasoning_context
            )

            return {
                "reasoning_type": "claude_based",
                "reasoning_steps": reasoning_result.get("steps", []),
                "final_reasoning": reasoning_result.get(
                    "final_conclusion", "추론 완료"
                ),
                "reasoning_confidence": reasoning_result.get("confidence", 0.7),
                "claude_insights": reasoning_result.get("insights", []),
            }

        except Exception as e:
            print(f"⚠️ Claude 추론 실패, 패턴 기반으로 폴백: {e}")
            return self._pattern_based_reasoning(
                text, context, emotion_result, strategy_result
            )

    def _hybrid_reasoning(
        self,
        text: str,
        context: Optional[str],
        emotion_result: Dict[str, Any],
        strategy_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """혼합 추론 (패턴 + Claude)"""
        # 패턴 기반 추론
        pattern_result = self._pattern_based_reasoning(
            text, context, emotion_result, strategy_result
        )

        # Claude 추론 (보강용)
        claude_result = self._claude_reasoning(
            text, context, emotion_result, strategy_result
        )

        # 두 결과 융합
        hybrid_confidence = (
            pattern_result["reasoning_confidence"]
            + claude_result.get("reasoning_confidence", 0.5)
        ) / 2

        return {
            "reasoning_type": "hybrid",
            "pattern_reasoning": pattern_result["reasoning_logic"],
            "claude_reasoning": claude_result.get("final_reasoning", ""),
            "hybrid_insights": pattern_result["insights"]
            + claude_result.get("claude_insights", []),
            "reasoning_confidence": hybrid_confidence,
            "fusion_method": "weighted_average",
        }

    def _pattern_based_reasoning(
        self,
        text: str,
        context: Optional[str],
        emotion_result: Dict[str, Any],
        strategy_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """패턴 기반 추론 (기본)"""
        emotion = emotion_result["primary_emotion"]
        strategy = strategy_result["primary_strategy"]

        # 기본 추론 로직
        reasoning_logic = []

        # 감정 기반 추론
        if emotion in ["joy", "surprise"]:
            reasoning_logic.append("긍정적 감정 상태이므로 적극적 접근이 유효합니다.")
        elif emotion in ["sadness", "fear"]:
            reasoning_logic.append(
                "부정적 감정 상태이므로 신중하고 지지적인 접근이 필요합니다."
            )
        elif emotion == "anger":
            reasoning_logic.append(
                "분노 감정이므로 침착하고 단계적인 접근이 중요합니다."
            )
        else:
            reasoning_logic.append("중립적 감정 상태이므로 균형잡힌 접근이 적절합니다.")

        # 전략 기반 추론
        if strategy == "empathetic":
            reasoning_logic.append("공감적 전략을 통해 감정적 연결을 강화합니다.")
        elif strategy == "analytical":
            reasoning_logic.append("분석적 전략을 통해 논리적 해결책을 모색합니다.")
        elif strategy == "supportive":
            reasoning_logic.append("지지적 전략을 통해 안정감을 제공합니다.")

        # 컨텍스트 기반 추론
        if context:
            if "업무" in context or "work" in context.lower():
                reasoning_logic.append(
                    "업무 상황이므로 전문적이고 체계적인 접근이 필요합니다."
                )
            elif "개인" in context or "personal" in context.lower():
                reasoning_logic.append(
                    "개인적 상황이므로 따뜻하고 이해적인 접근이 적합합니다."
                )

        # 추론 신뢰도 계산
        confidence_factors = [
            emotion_result["confidence"],
            strategy_result["confidence"],
            0.6 if context else 0.4,  # 컨텍스트 유무
        ]
        reasoning_confidence = sum(confidence_factors) / len(confidence_factors)

        return {
            "reasoning_type": "pattern_based",
            "reasoning_logic": reasoning_logic,
            "reasoning_confidence": reasoning_confidence,
            "insights": [
                f"감정 '{emotion}' 기반 추론 적용",
                f"전략 '{strategy}' 기반 논리 구성",
                f"추론 신뢰도: {reasoning_confidence:.3f}",
            ],
        }

    def _select_q_action(
        self,
        emotion_result: Dict[str, Any],
        strategy_result: Dict[str, Any],
        reasoning_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Q-Table 기반 행동 선택"""
        if not self.enable_q_learning or not self.q_selector:
            return {
                "action_selected": None,
                "q_learning_enabled": False,
                "fallback_reason": "Q-Learning 비활성화",
            }

        try:
            # 현재 상태 구성
            q_state = create_q_state_from_judgment_context(
                emotion_result["primary_emotion"],
                emotion_result["confidence"],
                "general",  # 기본 컨텍스트
                "normal",  # 기본 긴급도
                0.7,  # 기본 에너지
                reasoning_result["reasoning_confidence"],
            )

            # 사용 가능한 전략들
            available_strategies = [strategy_result["primary_strategy"]]
            if strategy_result.get("alternative_strategies"):
                available_strategies.extend(
                    strategy_result["alternative_strategies"][:2]
                )

            # Q-Table 행동 선택
            selected_action = self.q_selector.select_action(
                q_state, available_strategies
            )

            return {
                "action_selected": {
                    "type": selected_action.action_type.value,
                    "strategy": selected_action.strategy,
                    "intensity": selected_action.intensity,
                },
                "q_state_key": q_state.to_key(),
                "available_strategies": available_strategies,
                "q_learning_enabled": True,
                "selection_method": "q_table_policy",
            }

        except Exception as e:
            print(f"⚠️ Q-Action 선택 실패: {e}")
            return {
                "action_selected": None,
                "q_learning_enabled": False,
                "error": str(e),
            }

    def _generate_integrated_judgment(
        self,
        text: str,
        context: Optional[str],
        persona_result: Dict[str, Any],
        emotion_result: Dict[str, Any],
        strategy_result: Dict[str, Any],
        reasoning_result: Dict[str, Any],
        q_action_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """통합 판단 생성"""

        # 기본 판단 템플릿 구성
        emotion = emotion_result["primary_emotion"]
        strategy = strategy_result["primary_strategy"]
        persona_name = persona_result["persona_name"]

        # 판단 생성 로직
        judgment_parts = []

        # 페르소나 인사이트
        if persona_result.get("meta_insights"):
            judgment_parts.append(
                f"[{persona_name}의 관점] {persona_result['meta_insights'][0]}"
            )

        # 감정 기반 판단
        emotion_judgments = {
            "joy": "긍정적인 에너지가 느껴집니다. 이 기쁨을 활용하여 더 나은 결과를 만들어보세요.",
            "sadness": "어려운 시간이지만, 이런 감정도 성장의 기회입니다. 천천히 극복해나가시길 바랍니다.",
            "anger": "화가 나는 상황이지만, 잠시 숨을 고르고 냉정하게 접근해보시는 것이 좋겠습니다.",
            "fear": "불안한 마음이 들지만, 차근차근 준비하고 대처하면 충분히 해결할 수 있습니다.",
            "surprise": "예상치 못한 상황이네요. 새로운 관점으로 접근해보시는 것은 어떨까요?",
            "neutral": "현재 상황을 차분히 분석하여 최적의 방향을 찾아보시기 바랍니다.",
        }

        base_judgment = emotion_judgments.get(
            emotion, "상황을 종합적으로 고려하여 신중하게 접근하시기 바랍니다."
        )
        judgment_parts.append(base_judgment)

        # 전략 기반 조언
        strategy_advice = {
            "empathetic": "다른 사람들의 감정과 입장을 충분히 고려하여 진행하세요.",
            "analytical": "데이터와 논리를 바탕으로 체계적으로 접근해보시기 바랍니다.",
            "supportive": "주변의 지지와 도움을 받으며 함께 해결해나가시길 바랍니다.",
            "creative": "기존과 다른 창의적인 방법을 시도해보시는 것이 좋겠습니다.",
            "cautious": "신중하게 검토하고 준비를 충분히 한 후 진행하시기 바랍니다.",
            "balanced": "다양한 측면을 균형있게 고려하여 결정하시기 바랍니다.",
        }

        if strategy in strategy_advice:
            judgment_parts.append(strategy_advice[strategy])

        # 추론 결과 반영
        if reasoning_result.get("insights"):
            key_insight = reasoning_result["insights"][0]
            judgment_parts.append(f"[추론 결과] {key_insight}")

        # Q-Action 반영
        if q_action_result.get("action_selected"):
            action = q_action_result["action_selected"]
            if action["type"] == "meta_reflection":
                judgment_parts.append(
                    "이 상황에서 한 번 더 깊이 생각해보시는 것이 도움이 될 것 같습니다."
                )

        # 최종 판단 조합
        final_judgment = " ".join(judgment_parts)

        # 신뢰도 계산 (모든 단계의 가중 평균)
        confidence_components = [
            emotion_result["confidence"] * 0.25,
            strategy_result["confidence"] * 0.25,
            reasoning_result["reasoning_confidence"] * 0.3,
            persona_result["persona_confidence"] * 0.2,
        ]

        final_confidence = sum(confidence_components)
        final_confidence = max(0.1, min(0.95, final_confidence))  # 범위 제한

        return {
            "judgment": final_judgment,
            "confidence": final_confidence,
            "judgment_components": len(judgment_parts),
            "primary_influence": "integrated_analysis",
        }

    def _perform_meta_learning(
        self,
        result: IntegratedJudgmentResult,
        custom_settings: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """메타 학습 및 Q-Table 업데이트"""
        insights = []
        reward = 0.0

        try:
            # Q-Learning 보상 계산 및 업데이트
            if (
                self.enable_q_learning
                and self.q_selector
                and result.q_action_selected.get("action_selected")
            ):
                # 판단 결과로부터 보상 계산
                judgment_result = {
                    "confidence": result.confidence,
                    "processing_time": result.processing_time,
                    "error_occurred": result.confidence < 0.3,
                    "emotion_detected": result.emotion_analysis["primary_emotion"],
                    "strategy_suggested": result.strategy_selection["primary_strategy"],
                }

                reward = self.q_selector.calculate_reward(judgment_result)

                # Q-값 업데이트 (단순화된 버전)
                if result.q_action_selected.get("q_state_key"):
                    # 실제 구현에서는 더 정교한 상태 전이 필요
                    insights.append(f"Q-Learning 보상: {reward:.3f}")

            # 페르소나 학습 피드백
            if result.persona_analysis and result.confidence > 0.6:
                insights.append(
                    f"페르소나 '{result.persona_analysis['persona_name']}' 성공적 적용"
                )

            # 추론 모드 효과성 분석
            if result.reasoning_result:
                reasoning_confidence = result.reasoning_result.get(
                    "reasoning_confidence", 0.5
                )
                if reasoning_confidence > 0.7:
                    insights.append(f"추론 모드 '{result.reasoning_mode.value}' 효과적")

            # 처리 시간 분석
            if result.processing_time > 5.0:
                insights.append("처리 시간 최적화 필요")
            elif result.processing_time < 1.0:
                insights.append("빠른 처리 성공")

        except Exception as e:
            insights.append(f"메타 학습 부분 실패: {str(e)[:50]}")

        return {
            "insights": insights,
            "reward": reward,
            "learning_applied": self.enable_q_learning,
            "meta_reflection_enabled": self.enable_meta_reflection,
        }

    def _infer_context_type(self, text: str) -> str:
        """컨텍스트 타입 추론"""
        text_lower = text.lower()

        if any(
            word in text_lower
            for word in ["업무", "회의", "직장", "프로젝트", "work", "meeting"]
        ):
            return "work"
        elif any(
            word in text_lower
            for word in ["친구", "가족", "연인", "개인", "friend", "family"]
        ):
            return "personal"
        elif any(
            word in text_lower for word in ["공부", "학교", "시험", "study", "school"]
        ):
            return "academic"
        elif any(
            word in text_lower
            for word in ["창의", "아이디어", "혁신", "creative", "idea"]
        ):
            return "creative"
        else:
            return "general"

    def _infer_urgency(self, text: str) -> str:
        """긴급도 추론"""
        text_lower = text.lower()

        if any(
            word in text_lower
            for word in ["긴급", "급해", "빨리", "즉시", "urgent", "quickly"]
        ):
            return "high"
        elif any(
            word in text_lower
            for word in ["천천히", "나중에", "여유", "slowly", "later"]
        ):
            return "low"
        else:
            return "normal"

    def _infer_complexity(self, text: str) -> str:
        """복잡도 추론"""
        if len(text) > 200:
            return "high"
        elif len(text) > 50:
            return "medium"
        else:
            return "low"

    def get_engine_stats(self) -> Dict[str, Any]:
        """엔진 통계 반환"""
        success_rate = (self.successful_judgments / max(self.total_judgments, 1)) * 100

        stats = {
            "total_judgments": self.total_judgments,
            "successful_judgments": self.successful_judgments,
            "success_rate": success_rate,
            "average_confidence": self.average_confidence,
            "flow_mode": self.flow_mode.value,
            "reasoning_mode": self.reasoning_mode.value,
            "q_learning_enabled": self.enable_q_learning,
            "meta_reflection_enabled": self.enable_meta_reflection,
            "personas_used": dict(self.personas_used),
        }

        # Q-Learning 통계 추가
        if self.q_selector:
            stats["q_learning_stats"] = self.q_selector.get_stats()

        # 페르소나 통계 추가
        persona_stats = {}
        for sig_type, persona in self.personas.items():
            persona_status = persona.get_status()
            persona_stats[sig_type] = {
                "interaction_count": persona_status["interaction_count"],
                "confidence": persona_status["confidence"],
                "energy_level": persona_status["energy_level"],
            }
        stats["persona_stats"] = persona_stats

        return stats


# 편의 함수들
def create_integrated_engine(
    signature: str = "Echo-Phoenix",
    flow_mode: str = "hybrid",
    reasoning_mode: str = "pattern_based",
) -> IntegratedJudgmentEngine:
    """통합 엔진 생성 편의 함수"""
    flow_mode_enum = JudgmentFlowMode(flow_mode)
    reasoning_mode_enum = ReasoningMode(reasoning_mode)

    return IntegratedJudgmentEngine(
        default_signature=signature,
        flow_mode=flow_mode_enum,
        reasoning_mode=reasoning_mode_enum,
    )


def quick_integrated_judgment(
    text: str, context: Optional[str] = None, signature: str = "Echo-Phoenix"
) -> Dict[str, Any]:
    """빠른 통합 판단 실행"""
    engine = create_integrated_engine(signature)
    result = engine.run_integrated_judgment(text, context)

    return {
        "judgment": result.judgment,
        "confidence": result.confidence,
        "signature": result.signature_applied,
        "emotion": result.emotion_analysis.get("primary_emotion", "neutral"),
        "strategy": result.strategy_selection.get("primary_strategy", "balanced"),
        "processing_time": result.processing_time,
    }


if __name__ == "__main__":
    # 테스트 코드
    print("🧩 통합 판단 흐름 테스트")
    print("=" * 60)

    # 통합 엔진 생성
    engine = create_integrated_engine(
        signature="Echo-Phoenix", flow_mode="hybrid", reasoning_mode="pattern_based"
    )

    # 테스트 케이스들
    test_cases = [
        {
            "text": "오늘 프로젝트에서 큰 실패를 했지만 다시 도전하고 싶어요",
            "context": "업무 상황에서 좌절감을 느끼고 있습니다",
            "signature": "Echo-Phoenix",
        },
        {
            "text": "새로운 아이디어가 있는데 팀원들을 어떻게 설득해야 할까요?",
            "context": "창의적인 업무 환경",
            "signature": "Echo-Sage",
        },
        {
            "text": "친구와 갈등이 있어서 마음이 아픕니다",
            "context": "개인적인 인간관계 문제",
            "signature": "Echo-Aurora",
        },
    ]

    # 각 테스트 케이스 실행
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*20} 테스트 {i} {'='*20}")
        print(f"📝 입력: {test_case['text']}")
        print(f"🏷️ 컨텍스트: {test_case['context']}")
        print(f"🎭 시그니처: {test_case['signature']}")

        # 통합 판단 실행
        result = engine.run_integrated_judgment(
            text=test_case["text"],
            context=test_case["context"],
            signature=test_case["signature"],
        )

        print(f"\n📊 결과:")
        print(f"   판단: {result.judgment}")
        print(f"   신뢰도: {result.confidence:.3f}")
        print(f"   감정: {result.emotion_analysis.get('primary_emotion', 'N/A')}")
        print(f"   전략: {result.strategy_selection.get('primary_strategy', 'N/A')}")
        print(f"   페르소나: {result.persona_analysis.get('persona_name', 'N/A')}")
        print(f"   처리시간: {result.processing_time:.3f}초")

        # 단계별 시간
        print(f"\n⏱️ 단계별 처리시간:")
        for stage, timing in result.stage_timings.items():
            print(f"      {stage}: {timing:.3f}초")

        # 메타 인사이트
        if result.meta_insights:
            print(f"\n💡 메타 인사이트:")
            for insight in result.meta_insights:
                print(f"      • {insight}")

    # 최종 엔진 통계
    print(f"\n📈 엔진 통계:")
    stats = engine.get_engine_stats()
    for key, value in stats.items():
        if isinstance(value, dict) and len(value) <= 5:
            print(f"   {key}:")
            for sub_key, sub_value in value.items():
                print(f"      {sub_key}: {sub_value}")
        elif isinstance(value, (int, float)):
            if isinstance(value, float):
                print(f"   {key}: {value:.3f}")
            else:
                print(f"   {key}: {value}")
        else:
            print(f"   {key}: {value}")
