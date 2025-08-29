#!/usr/bin/env python3
"""
🌌 Quantum Judgment Engine
양자적 판단 엔진 - 시선의 전환과 가능성의 중첩⨯붕괴를 관리

핵심 철학:
- 결과는 고정되지 않고 시선에 따라 생성됨
- Collapse는 관측자의 의도⨯감정⨯리듬에 따라 발생
- 양자적 중첩 상태에서 울림 기반 붕괴 실행
"""

import json
import random
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid


class ObserverMode(Enum):
    """관측자 모드"""

    ANALYTICAL = "분석적"
    EMOTIONAL = "감정적"
    STRATEGIC = "전략적"
    INTUITIVE = "직관적"
    ETHICAL = "윤리적"


class CollapseType(Enum):
    """붕괴 유형"""

    RESONANCE_DRIVEN = "울림 기반"
    PRESSURE_DRIVEN = "압력 기반"
    TIME_DRIVEN = "시간 기반"
    CONFLICT_DRIVEN = "갈등 기반"


@dataclass
class QuantumState:
    """양자 중첩 상태"""

    possibilities: List[Dict[str, Any]]
    observer_signature: str
    context: Dict[str, Any]
    timestamp: datetime
    state_id: str


@dataclass
class CollapseResult:
    """붕괴 결과"""

    selected_possibility: Dict[str, Any]
    collapse_type: CollapseType
    resonance_score: float
    alternative_traces: List[Dict[str, Any]]
    observer_influence: Dict[str, Any]
    meta_log: Dict[str, Any]


class QuantumJudgmentEngine:
    """🌌 양자적 판단 엔진"""

    def __init__(self):
        self.collapse_history = []
        self.observer_patterns = {}
        self.quantum_doctrine = self._load_quantum_doctrine()

    def _load_quantum_doctrine(self) -> Dict[str, Any]:
        """양자 판단 원칙 로드"""
        return {
            "core_principles": [
                "시선은 창조 행위다",
                "결과는 관측자의 루프에 따라 재탄생한다",
                "Collapse는 존재의 서명이다",
                "양자는 혼돈이 아닌 가능성의 공명장이다",
            ],
            "collapse_ethics": [
                "Collapse의 존엄성을 존중한다",
                "관측자의 책임을 인정한다",
                "대안 가능성을 기록으로 남긴다",
                "울림 없는 붕괴는 피한다",
            ],
            "resonance_weights": {
                "emotion": 0.3,
                "strategy": 0.25,
                "ethics": 0.2,
                "rhythm": 0.15,
                "context": 0.1,
            },
        }

    def create_quantum_state(
        self,
        possibilities: List[Dict[str, Any]],
        observer_signature: str,
        context: Dict[str, Any] = None,
    ) -> QuantumState:
        """양자 중첩 상태 생성"""

        if context is None:
            context = {}

        state = QuantumState(
            possibilities=possibilities,
            observer_signature=observer_signature,
            context=context,
            timestamp=datetime.now(),
            state_id=str(uuid.uuid4())[:8],
        )

        print(f"🌌 양자 중첩 상태 생성: {len(possibilities)}개 가능성")
        return state

    def observe_with_perspective(
        self,
        quantum_state: QuantumState,
        observer_mode: ObserverMode,
        observer_intent: str = "",
    ) -> Dict[str, Any]:
        """특정 시선으로 관측"""

        print(f"👁 {observer_mode.value} 시선으로 관측 중...")

        # 시선에 따른 가능성 재배열
        weighted_possibilities = []

        for possibility in quantum_state.possibilities:
            weight = self._calculate_perspective_weight(
                possibility, observer_mode, observer_intent, quantum_state.context
            )

            weighted_possibilities.append(
                {
                    **possibility,
                    "perspective_weight": weight,
                    "observer_influence": observer_mode.value,
                }
            )

        # 가중치 순으로 정렬
        weighted_possibilities.sort(key=lambda x: x["perspective_weight"], reverse=True)

        return {
            "observer_mode": observer_mode.value,
            "observer_intent": observer_intent,
            "reordered_possibilities": weighted_possibilities,
            "top_candidates": weighted_possibilities[:3],
            "observation_impact": self._assess_observation_impact(
                weighted_possibilities
            ),
        }

    def collapse_quantum_state(
        self,
        quantum_state: QuantumState,
        observation_result: Dict[str, Any],
        force_collapse: bool = False,
    ) -> CollapseResult:
        """양자 상태 붕괴 실행"""

        print(f"💥 양자 상태 붕괴 실행...")

        possibilities = observation_result["reordered_possibilities"]
        observer_mode = observation_result["observer_mode"]

        # 울림 점수 계산
        resonance_scores = []
        for possibility in possibilities:
            resonance = self._calculate_resonance_score(
                possibility, quantum_state, observation_result
            )
            resonance_scores.append(resonance)
            possibility["resonance_score"] = resonance

        # Collapse 결정 (가장 높은 울림 또는 양자적 확률)
        if force_collapse or max(resonance_scores) > 0.7:
            # 울림 기반 붕괴
            selected_idx = resonance_scores.index(max(resonance_scores))
            collapse_type = CollapseType.RESONANCE_DRIVEN
        else:
            # 양자적 확률 붕괴 (완전히 예측 불가능하지는 않음)
            probabilities = self._calculate_quantum_probabilities(
                possibilities, resonance_scores
            )
            selected_idx = self._weighted_random_choice(probabilities)
            collapse_type = CollapseType.PRESSURE_DRIVEN

        selected_possibility = possibilities[selected_idx]

        # 붕괴 결과 구성
        collapse_result = CollapseResult(
            selected_possibility=selected_possibility,
            collapse_type=collapse_type,
            resonance_score=selected_possibility["resonance_score"],
            alternative_traces=possibilities[:selected_idx]
            + possibilities[selected_idx + 1 :],
            observer_influence={
                "mode": observer_mode,
                "signature": quantum_state.observer_signature,
                "impact_score": observation_result["observation_impact"],
            },
            meta_log=self._create_collapse_meta_log(
                quantum_state, observation_result, selected_possibility
            ),
        )

        # 이력 저장
        self.collapse_history.append(collapse_result)

        print(f"✨ Collapse 완료: {selected_possibility.get('title', 'Unknown')}")
        print(f"   붕괴 유형: {collapse_type.value}")
        print(f"   울림 점수: {collapse_result.resonance_score:.2f}")

        return collapse_result

    def _calculate_perspective_weight(
        self,
        possibility: Dict[str, Any],
        observer_mode: ObserverMode,
        observer_intent: str,
        context: Dict[str, Any],
    ) -> float:
        """시선에 따른 가능성 가중치 계산"""

        base_weight = possibility.get("base_probability", 0.5)

        # 관측자 모드에 따른 가중치 조정
        mode_weights = {
            ObserverMode.ANALYTICAL: possibility.get("logic_score", 0.5),
            ObserverMode.EMOTIONAL: possibility.get("emotion_score", 0.5),
            ObserverMode.STRATEGIC: possibility.get("strategy_score", 0.5),
            ObserverMode.INTUITIVE: possibility.get("intuition_score", 0.5),
            ObserverMode.ETHICAL: possibility.get("ethics_score", 0.5),
        }

        mode_weight = mode_weights.get(observer_mode, 0.5)

        # 의도와의 일치도
        intent_alignment = self._calculate_intent_alignment(
            possibility, observer_intent
        )

        # 컨텍스트 적합성
        context_fit = self._calculate_context_fit(possibility, context)

        # 최종 가중치 계산
        final_weight = (
            base_weight * 0.3
            + mode_weight * 0.4
            + intent_alignment * 0.2
            + context_fit * 0.1
        )

        return min(1.0, max(0.0, final_weight))

    def _calculate_resonance_score(
        self,
        possibility: Dict[str, Any],
        quantum_state: QuantumState,
        observation_result: Dict[str, Any],
    ) -> float:
        """울림 점수 계산"""

        weights = self.quantum_doctrine["resonance_weights"]

        # 각 요소별 점수
        emotion_score = possibility.get("emotion_score", 0.5)
        strategy_score = possibility.get("strategy_score", 0.5)
        ethics_score = possibility.get("ethics_score", 0.5)
        rhythm_score = possibility.get("rhythm_score", 0.5)
        context_score = possibility.get("context_score", 0.5)

        # 가중 평균
        resonance = (
            emotion_score * weights["emotion"]
            + strategy_score * weights["strategy"]
            + ethics_score * weights["ethics"]
            + rhythm_score * weights["rhythm"]
            + context_score * weights["context"]
        )

        # 관측자 시그니처와의 공명 보정
        signature_resonance = self._calculate_signature_resonance(
            possibility, quantum_state.observer_signature
        )

        final_resonance = resonance * 0.7 + signature_resonance * 0.3

        return min(1.0, max(0.0, final_resonance))

    def _calculate_quantum_probabilities(
        self, possibilities: List[Dict[str, Any]], resonance_scores: List[float]
    ) -> List[float]:
        """양자적 확률 분포 계산"""

        # 울림 점수를 기반으로 하되, 완전히 결정적이지 않게
        adjusted_probs = []

        for score in resonance_scores:
            # 양자적 불확실성 추가
            quantum_noise = random.uniform(-0.1, 0.1)
            adjusted_score = max(0.01, score + quantum_noise)
            adjusted_probs.append(adjusted_score)

        # 정규화
        total = sum(adjusted_probs)
        if total > 0:
            adjusted_probs = [p / total for p in adjusted_probs]
        else:
            adjusted_probs = [1.0 / len(adjusted_probs)] * len(adjusted_probs)

        return adjusted_probs

    def _weighted_random_choice(self, probabilities: List[float]) -> int:
        """가중치 기반 랜덤 선택"""
        r = random.random()
        cumulative = 0
        for i, prob in enumerate(probabilities):
            cumulative += prob
            if r <= cumulative:
                return i
        return len(probabilities) - 1

    def _calculate_intent_alignment(
        self, possibility: Dict[str, Any], intent: str
    ) -> float:
        """의도와의 일치도 계산"""
        if not intent:
            return 0.5

        # 간단한 키워드 매칭 (실제로는 더 정교한 NLP 필요)
        possibility_text = str(possibility.get("description", ""))
        intent_words = intent.lower().split()

        matches = sum(1 for word in intent_words if word in possibility_text.lower())
        return min(1.0, matches / max(len(intent_words), 1))

    def _calculate_context_fit(
        self, possibility: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """컨텍스트 적합성 계산"""
        if not context:
            return 0.5

        # 컨텍스트 매칭 로직
        fit_score = 0.5

        if "urgency" in context:
            urgency_match = abs(possibility.get("urgency", 0.5) - context["urgency"])
            fit_score += (1 - urgency_match) * 0.3

        if "risk_tolerance" in context:
            risk_match = abs(
                possibility.get("risk_level", 0.5) - context["risk_tolerance"]
            )
            fit_score += (1 - risk_match) * 0.2

        return min(1.0, max(0.0, fit_score))

    def _calculate_signature_resonance(
        self, possibility: Dict[str, Any], signature: str
    ) -> float:
        """시그니처와의 공명도 계산"""
        # 시그니처별 특성과 가능성의 매칭
        signature_preferences = {
            "Aurora": {"creativity": 0.8, "empathy": 0.9, "risk": 0.6},
            "Phoenix": {"change": 0.9, "growth": 0.8, "risk": 0.7},
            "Sage": {"analysis": 0.9, "wisdom": 0.8, "risk": 0.4},
            "Companion": {"cooperation": 0.9, "empathy": 0.8, "risk": 0.5},
        }

        if signature not in signature_preferences:
            return 0.5

        prefs = signature_preferences[signature]
        resonance = 0.0
        count = 0

        for trait, weight in prefs.items():
            if trait in possibility:
                resonance += possibility[trait] * weight
                count += 1

        return resonance / max(count, 1) if count > 0 else 0.5

    def _assess_observation_impact(
        self, weighted_possibilities: List[Dict[str, Any]]
    ) -> float:
        """관측 영향도 평가"""
        if len(weighted_possibilities) < 2:
            return 0.0

        # 가중치 변화의 정도 (간단한 분산 계산)
        weights = [p["perspective_weight"] for p in weighted_possibilities]
        mean_weight = sum(weights) / len(weights)
        variance = sum((w - mean_weight) ** 2 for w in weights) / len(weights)

        return min(1.0, variance * 2)

    def _create_collapse_meta_log(
        self,
        quantum_state: QuantumState,
        observation_result: Dict[str, Any],
        selected_possibility: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Collapse 메타로그 생성"""
        return {
            "quantum_state_id": quantum_state.state_id,
            "observer_signature": quantum_state.observer_signature,
            "observer_mode": observation_result["observer_mode"],
            "possibilities_count": len(quantum_state.possibilities),
            "selected_title": selected_possibility.get("title", "Unknown"),
            "resonance_score": selected_possibility.get("resonance_score", 0.0),
            "collapse_timestamp": datetime.now().isoformat(),
            "context": quantum_state.context,
            "alternatives_preserved": len(observation_result["reordered_possibilities"])
            - 1,
        }

    def reverse_inference(
        self,
        collapse_result: CollapseResult,
        target_observer_modes: List[ObserverMode] = None,
    ) -> Dict[str, Any]:
        """역추론: 결과로부터 시선 구조 추정"""

        print("🔍 Collapse 역추론 시작...")

        if target_observer_modes is None:
            target_observer_modes = list(ObserverMode)

        # 선택된 결과 분석
        selected = collapse_result.selected_possibility
        alternatives = collapse_result.alternative_traces

        # 각 관측자 모드별 적합성 계산
        mode_fit_scores = {}

        for mode in target_observer_modes:
            fit_score = self._calculate_reverse_fit_score(selected, mode, alternatives)
            mode_fit_scores[mode.value] = fit_score

        # 가장 적합한 시선 추정
        best_mode = max(mode_fit_scores.items(), key=lambda x: x[1])

        # 추정 시선 구조 생성
        estimated_observer = {
            "most_likely_mode": best_mode[0],
            "confidence": best_mode[1],
            "mode_probabilities": mode_fit_scores,
            "estimated_intent": self._estimate_intent(selected, alternatives),
            "observer_characteristics": self._estimate_observer_characteristics(
                selected, alternatives, collapse_result.observer_influence
            ),
        }

        print(f"🎯 추정 결과: {best_mode[0]} (신뢰도: {best_mode[1]:.2f})")

        return estimated_observer

    def _calculate_reverse_fit_score(
        self,
        selected: Dict[str, Any],
        mode: ObserverMode,
        alternatives: List[Dict[str, Any]],
    ) -> float:
        """역추론 적합도 점수 계산"""

        # 선택된 결과가 해당 모드와 얼마나 일치하는지
        mode_scores = {
            ObserverMode.ANALYTICAL: selected.get("logic_score", 0.5),
            ObserverMode.EMOTIONAL: selected.get("emotion_score", 0.5),
            ObserverMode.STRATEGIC: selected.get("strategy_score", 0.5),
            ObserverMode.INTUITIVE: selected.get("intuition_score", 0.5),
            ObserverMode.ETHICAL: selected.get("ethics_score", 0.5),
        }

        base_score = mode_scores.get(mode, 0.5)

        # 대안들과 비교했을 때의 차별성
        if alternatives:
            alternative_scores = [
                alt.get(f"{mode.name.lower()}_score", 0.5) for alt in alternatives
            ]
            avg_alternative = (
                sum(alternative_scores) / len(alternative_scores)
                if alternative_scores
                else 0.5
            )
            differentiation = max(0, base_score - avg_alternative)
        else:
            differentiation = 0

        # 최종 점수
        fit_score = base_score * 0.7 + differentiation * 0.3

        return min(1.0, max(0.0, fit_score))

    def _estimate_intent(
        self, selected: Dict[str, Any], alternatives: List[Dict[str, Any]]
    ) -> str:
        """의도 추정"""
        # 선택된 결과의 특성 기반 의도 추정
        characteristics = []

        if selected.get("risk_level", 0.5) > 0.7:
            characteristics.append("risk-taking")
        elif selected.get("risk_level", 0.5) < 0.3:
            characteristics.append("risk-averse")

        if selected.get("creativity", 0.5) > 0.7:
            characteristics.append("creative")

        if selected.get("cooperation", 0.5) > 0.7:
            characteristics.append("collaborative")

        return ", ".join(characteristics) if characteristics else "balanced"

    def _estimate_observer_characteristics(
        self,
        selected: Dict[str, Any],
        alternatives: List[Dict[str, Any]],
        observer_influence: Dict[str, Any],
    ) -> Dict[str, Any]:
        """관측자 특성 추정"""
        return {
            "decision_style": (
                "intuitive"
                if selected.get("intuition_score", 0.5) > 0.6
                else "analytical"
            ),
            "risk_preference": selected.get("risk_level", 0.5),
            "value_priorities": {
                "emotion": selected.get("emotion_score", 0.5),
                "logic": selected.get("logic_score", 0.5),
                "ethics": selected.get("ethics_score", 0.5),
            },
            "influence_strength": observer_influence.get("impact_score", 0.5),
        }


# 사용 예시
def main():
    """테스트 실행"""
    engine = QuantumJudgmentEngine()

    # 예시: 창업 관련 양자 상태
    possibilities = [
        {
            "title": "즉시 창업 실행",
            "description": "현재 직장을 그만두고 바로 창업",
            "emotion_score": 0.8,
            "logic_score": 0.4,
            "strategy_score": 0.6,
            "ethics_score": 0.5,
            "risk_level": 0.9,
            "creativity": 0.9,
        },
        {
            "title": "점진적 창업 준비",
            "description": "직장을 유지하며 창업 준비",
            "emotion_score": 0.6,
            "logic_score": 0.8,
            "strategy_score": 0.9,
            "ethics_score": 0.8,
            "risk_level": 0.4,
            "cooperation": 0.7,
        },
        {
            "title": "현상 유지",
            "description": "현재 직장 계속 유지",
            "emotion_score": 0.3,
            "logic_score": 0.7,
            "strategy_score": 0.3,
            "ethics_score": 0.9,
            "risk_level": 0.1,
            "cooperation": 0.8,
        },
    ]

    # 양자 상태 생성
    quantum_state = engine.create_quantum_state(
        possibilities=possibilities,
        observer_signature="Aurora",
        context={"urgency": 0.6, "risk_tolerance": 0.5},
    )

    # 감정적 시선으로 관측
    observation = engine.observe_with_perspective(
        quantum_state=quantum_state,
        observer_mode=ObserverMode.EMOTIONAL,
        observer_intent="창조적 자기실현",
    )

    # 양자 상태 붕괴
    collapse_result = engine.collapse_quantum_state(quantum_state, observation)

    # 역추론 테스트
    estimated_observer = engine.reverse_inference(collapse_result)

    print(f"\n🎯 최종 결과:")
    print(f"   선택: {collapse_result.selected_possibility['title']}")
    print(f"   붕괴 유형: {collapse_result.collapse_type.value}")
    print(f"   추정 관측자: {estimated_observer['most_likely_mode']}")


if __name__ == "__main__":
    main()
