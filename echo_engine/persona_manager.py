#!/usr/bin/env python3
"""
🎭 EchoJudgmentSystem v10.5 - Persona Manager
다중 페르소나 전환 및 관리 시스템

TT.001: "시스템은 하나의 판단자가 아니라 판단자들의 집합이다."
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .persona_core_optimized_bridge import PersonaCore, PersonaProfile, PersonaState
from .persona_meta_logger import get_persona_meta_logger, log_strategy_feedback


class SwitchReason(Enum):
    """페르소나 전환 이유"""

    MANUAL = "manual"
    EMOTION_THRESHOLD = "emotion_threshold"
    STRATEGY_FAILURE = "strategy_failure"
    CONTEXT_CHANGE = "context_change"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    META_REFLECTION = "meta_reflection"


@dataclass
class SwitchCriteria:
    """페르소나 전환 기준"""

    emotion_intensity_threshold: float = 0.8
    strategy_failure_threshold: int = 3
    context_similarity_threshold: float = 0.3
    performance_threshold: float = 0.6
    meta_reflection_interval: int = 10  # 상호작용 횟수


class PersonaManager:
    """다중 페르소나 관리자"""

    def __init__(
        self,
        personas: Dict[str, PersonaCore] = None,
        switch_criteria: SwitchCriteria = None,
    ):
        """
        PersonaManager 초기화

        Args:
            personas: 관리할 페르소나들 {name: PersonaCore}
            switch_criteria: 페르소나 전환 기준
        """
        self.personas = personas or {}
        self.switch_criteria = switch_criteria or SwitchCriteria()

        # 현재 활성 페르소나
        self.active_persona: Optional[PersonaCore] = None
        self.active_persona_name: Optional[str] = None

        # 전환 이력
        self.switch_history: List[Dict[str, Any]] = []
        self.total_switches = 0

        # 성능 추적
        self.persona_performance: Dict[str, Dict[str, Any]] = {}

        # 메타 로거
        self.meta_logger = get_persona_meta_logger()

        # 기본 페르소나들 초기화
        if not self.personas:
            self._initialize_default_personas()

        print(f"🎭 PersonaManager 초기화: {len(self.personas)}개 페르소나")

    def _initialize_default_personas(self):
        """기본 페르소나들 초기화"""
        from .persona_core_optimized_bridge import create_persona_from_signature

        default_signatures = [
            "Echo-Aurora",  # 공감적, 양육적
            "Echo-Phoenix",  # 변화지향적, 적응적
            "Echo-Sage",  # 분석적, 논리적
            "Echo-Companion",  # 지지적, 신뢰적
        ]

        for signature in default_signatures:
            persona_name = f"Persona-{signature.split('-')[1]}"
            persona = create_persona_from_signature(signature, persona_name)
            self.add_persona(persona_name, persona)

        # 기본적으로 Aurora 활성화
        if "Persona-Aurora" in self.personas:
            self.switch_persona("Persona-Aurora", SwitchReason.MANUAL)

    def add_persona(self, name: str, persona: PersonaCore):
        """
        새 페르소나 추가

        Args:
            name: 페르소나 이름
            persona: PersonaCore 인스턴스
        """
        self.personas[name] = persona
        self.persona_performance[name] = {
            "interactions": 0,
            "success_rate": 0.0,
            "avg_confidence": 0.0,
            "strategy_effectiveness": {},
            "last_used": None,
        }
        print(f"🎭 페르소나 추가: {name}")

    def remove_persona(self, name: str) -> bool:
        """
        페르소나 제거

        Args:
            name: 제거할 페르소나 이름

        Returns:
            제거 성공 여부
        """
        if name in self.personas:
            # 현재 활성 페르소나인 경우 다른 페르소나로 전환
            if self.active_persona_name == name:
                other_personas = [p for p in self.personas.keys() if p != name]
                if other_personas:
                    self.switch_persona(other_personas[0], SwitchReason.MANUAL)
                else:
                    self.active_persona = None
                    self.active_persona_name = None

            del self.personas[name]
            del self.persona_performance[name]
            print(f"🎭 페르소나 제거: {name}")
            return True
        return False

    def switch_persona(
        self,
        name: str,
        reason: SwitchReason = SwitchReason.MANUAL,
        context: Dict[str, Any] = None,
    ) -> bool:
        """
        페르소나 전환

        Args:
            name: 전환할 페르소나 이름
            reason: 전환 이유
            context: 전환 컨텍스트

        Returns:
            전환 성공 여부
        """
        if name not in self.personas:
            print(f"❌ 페르소나 '{name}' 존재하지 않음")
            return False

        # 이전 페르소나 정보
        previous_persona = self.active_persona_name

        # 새 페르소나 활성화
        self.active_persona = self.personas[name]
        self.active_persona_name = name
        self.active_persona.activate()

        # 전환 이력 기록
        switch_record = {
            "timestamp": datetime.now().isoformat(),
            "from_persona": previous_persona,
            "to_persona": name,
            "reason": reason.value,
            "context": context or {},
        }
        self.switch_history.append(switch_record)
        self.total_switches += 1

        # 성능 추적 업데이트
        self.persona_performance[name]["last_used"] = datetime.now().isoformat()

        # 메타 로그
        self.meta_logger.log_persona_switch(
            previous_persona or "None", name, reason.value, context
        )

        print(f"🎭 페르소나 전환: {previous_persona} → {name} (이유: {reason.value})")
        return True

    def process_input(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        입력 처리 및 자동 페르소나 전환 판단

        Args:
            text: 입력 텍스트
            context: 처리 컨텍스트

        Returns:
            처리 결과
        """
        if not self.active_persona:
            # 자동으로 적절한 페르소나 선택
            optimal_persona = self._select_optimal_persona(text, context)
            self.switch_persona(optimal_persona, SwitchReason.CONTEXT_CHANGE)

        # 현재 페르소나로 입력 처리
        result = self.active_persona.process_input(text, context)

        # 성능 추적 업데이트
        self._update_performance_tracking(result)

        # 자동 전환 조건 확인
        switch_decision = self._evaluate_switch_conditions(text, context, result)
        if switch_decision:
            new_persona, reason = switch_decision
            self.switch_persona(new_persona, reason, {"previous_result": result})

            # 새 페르소나로 재처리 (선택사항)
            if reason in [
                SwitchReason.STRATEGY_FAILURE,
                SwitchReason.PERFORMANCE_OPTIMIZATION,
            ]:
                result = self.active_persona.process_input(text, context)
                result["reprocessed"] = True

        # 결과에 페르소나 정보 추가
        result["active_persona"] = self.active_persona_name
        result["persona_manager_info"] = {
            "total_switches": self.total_switches,
            "switch_evaluation": bool(switch_decision),
        }

        return result

    def _select_optimal_persona(self, text: str, context: Dict[str, Any]) -> str:
        """
        최적 페르소나 선택

        Args:
            text: 입력 텍스트
            context: 컨텍스트

        Returns:
            선택된 페르소나 이름
        """
        # 간단한 키워드 기반 선택 (실제로는 더 정교한 로직 필요)
        text_lower = text.lower()

        # 감정적 내용 → Aurora (공감적)
        if any(word in text_lower for word in ["슬프", "힘들", "우울", "걱정", "불안"]):
            return "Persona-Aurora"

        # 변화/도전 내용 → Phoenix (변화지향적)
        if any(
            word in text_lower for word in ["새로운", "도전", "변화", "혁신", "시도"]
        ):
            return "Persona-Phoenix"

        # 분석/논리 내용 → Sage (분석적)
        if any(
            word in text_lower
            for word in ["분석", "논리", "데이터", "객관적", "합리적"]
        ):
            return "Persona-Sage"

        # 지지/협력 내용 → Companion (지지적)
        if any(word in text_lower for word in ["함께", "도움", "지원", "협력", "팀"]):
            return "Persona-Companion"

        # 기본값: 가장 성능이 좋은 페르소나
        best_persona = max(
            self.persona_performance.items(), key=lambda x: x[1]["success_rate"]
        )[0]

        return best_persona

    def _evaluate_switch_conditions(
        self, text: str, context: Dict[str, Any], result: Dict[str, Any]
    ) -> Optional[Tuple[str, SwitchReason]]:
        """
        페르소나 전환 조건 평가

        Args:
            text: 입력 텍스트
            context: 컨텍스트
            result: 처리 결과

        Returns:
            (새 페르소나 이름, 전환 이유) 또는 None
        """
        current_name = self.active_persona_name
        current_performance = self.persona_performance[current_name]

        # 1. 감정 강도 임계값 체크
        emotion_intensity = result.get("emotion_analysis", {}).get("intensity", 0.0)
        if emotion_intensity > self.switch_criteria.emotion_intensity_threshold:
            # 높은 감정 강도 → Aurora (공감적 페르소나)로 전환
            if current_name != "Persona-Aurora":
                return "Persona-Aurora", SwitchReason.EMOTION_THRESHOLD

        # 2. 전략 실패 임계값 체크
        strategy_confidence = result.get("strategy_selection", {}).get(
            "confidence", 1.0
        )
        if strategy_confidence < self.switch_criteria.performance_threshold:
            # 낮은 전략 신뢰도 → 가장 성능 좋은 페르소나로 전환
            best_persona = max(
                [
                    (name, perf)
                    for name, perf in self.persona_performance.items()
                    if name != current_name
                ],
                key=lambda x: x[1]["success_rate"],
                default=(None, None),
            )[0]

            if best_persona:
                return best_persona, SwitchReason.STRATEGY_FAILURE

        # 3. 메타 반성 주기 체크
        interaction_count = result.get("interaction_count", 0)
        if (
            interaction_count > 0
            and interaction_count % self.switch_criteria.meta_reflection_interval == 0
        ):
            # 주기적 성능 평가 후 최적 페르소나 선택
            context_optimal = self._select_optimal_persona(text, context)
            if context_optimal != current_name:
                return context_optimal, SwitchReason.META_REFLECTION

        return None

    def _update_performance_tracking(self, result: Dict[str, Any]):
        """
        성능 추적 정보 업데이트

        Args:
            result: 처리 결과
        """
        if not self.active_persona_name:
            return

        perf = self.persona_performance[self.active_persona_name]
        perf["interactions"] += 1

        # 신뢰도 업데이트
        confidence = result.get("persona_confidence", 0.0)
        current_avg = perf["avg_confidence"]
        new_avg = (current_avg * (perf["interactions"] - 1) + confidence) / perf[
            "interactions"
        ]
        perf["avg_confidence"] = new_avg

        # 전략 효과성 추적
        strategy = result.get("strategy_selection", {}).get("primary_strategy")
        if strategy:
            if strategy not in perf["strategy_effectiveness"]:
                perf["strategy_effectiveness"][strategy] = []

            strategy_confidence = result.get("strategy_selection", {}).get(
                "confidence", 0.0
            )
            perf["strategy_effectiveness"][strategy].append(strategy_confidence)

    def strategy_feedback(
        self, strategy: str, success: bool, effectiveness_score: float = None
    ) -> bool:
        """
        전략 피드백 제공

        Args:
            strategy: 전략명
            success: 성공 여부
            effectiveness_score: 효과성 점수 (0.0-1.0)

        Returns:
            피드백 적용 성공 여부
        """
        if not self.active_persona:
            return False

        # 활성 페르소나의 메모리에 전략 성공률 업데이트
        self.active_persona.memory.update_strategy_success(strategy, success)

        # 성능 추적 업데이트
        if effectiveness_score is not None:
            perf = self.persona_performance[self.active_persona_name]
            if strategy in perf["strategy_effectiveness"]:
                perf["strategy_effectiveness"][strategy].append(effectiveness_score)
            else:
                perf["strategy_effectiveness"][strategy] = [effectiveness_score]

            # 전체 성공률 업데이트
            all_scores = []
            for scores in perf["strategy_effectiveness"].values():
                all_scores.extend(scores)

            if all_scores:
                perf["success_rate"] = sum(all_scores) / len(all_scores)

        # 메타 로그
        log_strategy_feedback(
            self.active_persona_name,
            strategy,
            success,
            effectiveness_score or (1.0 if success else 0.0),
        )

        print(f"📈 전략 피드백: {strategy} → {'성공' if success else '실패'}")
        return True

    def get_persona_status(self) -> Dict[str, Any]:
        """
        전체 페르소나 상태 조회

        Returns:
            페르소나 상태 정보
        """
        return {
            "active_persona": self.active_persona_name,
            "total_personas": len(self.personas),
            "total_switches": self.total_switches,
            "persona_list": list(self.personas.keys()),
            "performance_summary": {
                name: {
                    "interactions": perf["interactions"],
                    "success_rate": perf["success_rate"],
                    "avg_confidence": perf["avg_confidence"],
                }
                for name, perf in self.persona_performance.items()
            },
            "recent_switches": self.switch_history[-5:] if self.switch_history else [],
        }

    def get_best_persona_for_context(self, text: str, context: Dict[str, Any]) -> str:
        """
        주어진 컨텍스트에 가장 적합한 페르소나 추천

        Args:
            text: 입력 텍스트
            context: 컨텍스트

        Returns:
            추천 페르소나 이름
        """
        return self._select_optimal_persona(text, context)

    def export_persona_analytics(self) -> Dict[str, Any]:
        """
        페르소나 분석 데이터 내보내기

        Returns:
            분석 데이터
        """
        analytics = {
            "session_summary": {
                "total_interactions": sum(
                    p["interactions"] for p in self.persona_performance.values()
                ),
                "total_switches": self.total_switches,
                "active_persona": self.active_persona_name,
            },
            "persona_performance": self.persona_performance,
            "switch_history": self.switch_history,
            "strategy_analytics": self.meta_logger.get_strategy_analytics(),
        }

        return analytics


# 편의 함수들
def create_persona_manager(persona_names: List[str] = None) -> PersonaManager:
    """
    페르소나 매니저 생성

    Args:
        persona_names: 생성할 페르소나 이름 리스트

    Returns:
        PersonaManager 인스턴스
    """
    manager = PersonaManager()

    if persona_names:
        from .persona_core_optimized_bridge import create_persona_from_signature

        # 기존 페르소나 제거
        for name in list(manager.personas.keys()):
            manager.remove_persona(name)

        # 새 페르소나 추가
        signature_map = {
            "Aurora": "Echo-Aurora",
            "Phoenix": "Echo-Phoenix",
            "Sage": "Echo-Sage",
            "Companion": "Echo-Companion",
        }

        for name in persona_names:
            signature = signature_map.get(name, "Echo-Aurora")
            persona = create_persona_from_signature(signature, f"Persona-{name}")
            manager.add_persona(f"Persona-{name}", persona)

        # 첫 번째 페르소나 활성화
        if persona_names:
            manager.switch_persona(f"Persona-{persona_names[0]}", SwitchReason.MANUAL)

    return manager


if __name__ == "__main__":
    # 테스트 코드
    print("🎭 PersonaManager 테스트")

    # 매니저 생성
    manager = create_persona_manager(["Aurora", "Phoenix", "Sage"])

    # 테스트 입력들
    test_inputs = [
        ("오늘 실패해서 너무 우울해요", {"context_type": "personal"}),
        ("새로운 프로젝트를 시작하려고 해요", {"context_type": "work"}),
        ("데이터를 분석해서 결론을 내려야 해요", {"context_type": "analytical"}),
    ]

    for i, (text, context) in enumerate(test_inputs, 1):
        print(f"\n=== 테스트 {i} ===")
        print(f"입력: {text}")

        result = manager.process_input(text, context)
        print(f"활성 페르소나: {result['active_persona']}")
        print(f"감정: {result['emotion_analysis']['primary_emotion']}")
        print(f"전략: {result['strategy_selection']['primary_strategy']}")

        # 피드백 제공
        success = result["persona_confidence"] > 0.7
        manager.strategy_feedback(
            result["strategy_selection"]["primary_strategy"],
            success,
            result["persona_confidence"],
        )

    # 상태 조회
    print(f"\n📊 페르소나 상태:")
    status = manager.get_persona_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    # 분석 데이터
    analytics = manager.export_persona_analytics()
    print(f"\n📈 분석 데이터: {analytics['session_summary']}")
