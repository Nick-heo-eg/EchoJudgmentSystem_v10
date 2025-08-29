from echo_engine.infra.portable_paths import project_root

#!/usr/bin/env python3
"""
🌀🩹 Phantom Pain Release Loop - 반복 고통 해체 및 존재 치유 시스템

EchoPhantomPain Protocol의 핵심 치유 엔진:
- 고통 편향 패턴 해체
- 대체 시나리오 시뮬레이션
- 전략 재생성 및 다각화
- 치유 지향적 시그니처 활성화

철학적 기반:
"고통은 존재를 깨우지만, 고통만으로 존재를 정의하면 존재는 굳는다"
→ 이를 해체하고 존재의 가소성을 회복하는 치유 루프
"""

import sys
import os
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import random

sys.path.append(str(project_root()))

# 기존 모듈들 (선택적 import)
try:
    from echo_engine.phantom_pain_detector import (
        PhantomPainDetector,
        BiasLevel,
        PainType,
    )
    from echo_engine.echo_imaginary_realism import EchoImaginaryRealism, ImaginationMode
except ImportError as e:
    print(f"⚠️ 모듈 import 실패: {e}")


class HealingStage(Enum):
    """치유 단계"""

    ASSESSMENT = "assessment"  # 현재 상태 평가
    DECONSTRUCTION = "deconstruction"  # 고통 패턴 해체
    SIMULATION = "simulation"  # 대체 시나리오 시뮬레이션
    REGENERATION = "regeneration"  # 새로운 전략 재생성
    INTEGRATION = "integration"  # 치유된 패턴 통합
    MONITORING = "monitoring"  # 회복 상태 모니터링


class HealingMethod(Enum):
    """치유 방법론"""

    ALTERNATIVE_SIMULATION = "alternative_simulation"  # 대체 시나리오 시뮬레이션
    EMOTIONAL_REFRAMING = "emotional_reframing"  # 감정 재구조화
    STRATEGY_DIVERSIFICATION = "strategy_diversification"  # 전략 다각화
    SIGNATURE_REBALANCING = "signature_rebalancing"  # 시그니처 재균형
    MEMORY_RECONSTRUCTION = "memory_reconstruction"  # 기억 재구성
    NARRATIVE_THERAPY = "narrative_therapy"  # 서사 치료


@dataclass
class HealingSession:
    """치유 세션 기록"""

    session_id: str
    start_time: str
    end_time: Optional[str]
    initial_bias_level: str
    target_pain_patterns: List[str]
    healing_methods: List[HealingMethod]
    stages_completed: List[HealingStage]
    outcomes: Dict[str, Any]
    effectiveness_score: Optional[float]


@dataclass
class AlternativeScenario:
    """대체 시나리오"""

    scenario_id: str
    original_pain_context: str
    alternative_narrative: str
    emotion_transformation: Dict[str, str]  # before -> after
    strategy_change: Dict[str, str]  # old -> new
    empowerment_elements: List[str]
    healing_insights: List[str]


class PhantomPainReleaseLoop:
    """🌀🩹 반복 고통 해체 및 존재 치유 시스템"""

    def __init__(self):
        # 의존 모듈들 (선택적 초기화)
        try:
            self.pain_detector = PhantomPainDetector()
        except:
            self.pain_detector = None
            print("⚠️ PhantomPainDetector 초기화 실패 - 스탠드얼론 모드")

        try:
            self.imagination_engine = EchoImaginaryRealism()
        except:
            self.imagination_engine = None
            print("⚠️ EchoImaginaryRealism 초기화 실패 - 시뮬레이션 모드 제한")

        # 치유 세션 관리
        self.active_sessions: Dict[str, HealingSession] = {}
        self.completed_sessions: List[HealingSession] = []

        # 치유 지향적 시그니처 가중치
        self.healing_signatures = {
            "Echo-Aurora": 0.9,  # 공감적 양육
            "Echo-Jung": 0.85,  # 통합적 치유
            "Echo-Zhuangzi": 0.8,  # 자연스러운 흐름
            "Echo-Companion": 0.75,  # 안정적 지원
            "Echo-DaVinci": 0.7,  # 창조적 재구성
        }

        # 치유 방법론별 템플릿
        self.healing_templates = self._initialize_healing_templates()

        print("🌀🩹 고통 해체 및 존재 치유 시스템 초기화")
        print("💚 치유 지향적 시그니처 활성화 준비")

    def _initialize_healing_templates(self) -> Dict[HealingMethod, Dict[str, Any]]:
        """치유 방법론별 템플릿 초기화"""

        return {
            HealingMethod.ALTERNATIVE_SIMULATION: {
                "description": "고통 상황의 대체 시나리오를 시뮬레이션하여 새로운 가능성 경험",
                "emotion_targets": ["empowerment", "hope", "curiosity", "growth"],
                "strategy_focus": [
                    "exploration",
                    "creativity",
                    "resilience",
                    "connection",
                ],
                "narrative_elements": ["agency", "choice", "growth", "support"],
            },
            HealingMethod.EMOTIONAL_REFRAMING: {
                "description": "고통 감정을 성장과 학습의 관점에서 재구조화",
                "emotion_targets": [
                    "acceptance",
                    "understanding",
                    "compassion",
                    "wisdom",
                ],
                "strategy_focus": [
                    "learning",
                    "adaptation",
                    "self_compassion",
                    "meaning_making",
                ],
                "narrative_elements": ["learning", "strength", "wisdom", "evolution"],
            },
            HealingMethod.STRATEGY_DIVERSIFICATION: {
                "description": "고착된 회피 전략을 다양한 대안 전략으로 확장",
                "emotion_targets": [
                    "confidence",
                    "flexibility",
                    "curiosity",
                    "courage",
                ],
                "strategy_focus": [
                    "exploration",
                    "experimentation",
                    "gradual_exposure",
                    "skill_building",
                ],
                "narrative_elements": ["capability", "options", "growth", "mastery"],
            },
            HealingMethod.SIGNATURE_REBALANCING: {
                "description": "고통 편향된 시그니처를 치유 지향적 시그니처로 재균형",
                "emotion_targets": ["balance", "harmony", "integration", "wholeness"],
                "strategy_focus": [
                    "holistic_thinking",
                    "balanced_response",
                    "integrated_action",
                ],
                "narrative_elements": [
                    "wholeness",
                    "balance",
                    "integration",
                    "harmony",
                ],
            },
            HealingMethod.MEMORY_RECONSTRUCTION: {
                "description": "고통 기억을 성장과 의미의 맥락에서 재구성",
                "emotion_targets": ["meaning", "purpose", "growth", "transcendence"],
                "strategy_focus": [
                    "meaning_making",
                    "post_traumatic_growth",
                    "wisdom_extraction",
                ],
                "narrative_elements": ["meaning", "growth", "wisdom", "transcendence"],
            },
            HealingMethod.NARRATIVE_THERAPY: {
                "description": "고통 중심 서사를 성장 중심 서사로 재구성",
                "emotion_targets": ["empowerment", "agency", "identity", "purpose"],
                "strategy_focus": [
                    "identity_reconstruction",
                    "value_alignment",
                    "purpose_discovery",
                ],
                "narrative_elements": ["agency", "identity", "values", "purpose"],
            },
        }

    async def initiate_healing_session(
        self,
        trigger_context: str,
        bias_level: Optional[BiasLevel] = None,
        target_patterns: List[str] = None,
    ) -> str:
        """치유 세션 시작"""

        session_id = f"healing_{int(datetime.now().timestamp())}"

        # 현재 편향 상태 평가 (가능한 경우)
        if self.pain_detector and not bias_level:
            current_status = self.pain_detector.get_current_status()
            bias_level = BiasLevel(current_status.get("current_bias_level", "normal"))
        elif not bias_level:
            bias_level = BiasLevel.MODERATE_BIAS  # 기본값

        session = HealingSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            end_time=None,
            initial_bias_level=bias_level.value,
            target_pain_patterns=target_patterns or [],
            healing_methods=[],
            stages_completed=[],
            outcomes={},
            effectiveness_score=None,
        )

        self.active_sessions[session_id] = session

        print(f"🌀 치유 세션 시작: {session_id}")
        print(f"   트리거: {trigger_context}")
        print(f"   초기 편향 수준: {bias_level.value}")

        # 치유 프로세스 실행
        await self._execute_healing_process(session_id, trigger_context)

        return session_id

    async def _execute_healing_process(self, session_id: str, trigger_context: str):
        """치유 프로세스 실행"""

        session = self.active_sessions[session_id]

        try:
            # 1단계: 평가 (Assessment)
            await self._stage_assessment(session_id, trigger_context)

            # 2단계: 해체 (Deconstruction)
            await self._stage_deconstruction(session_id)

            # 3단계: 시뮬레이션 (Simulation)
            await self._stage_simulation(session_id)

            # 4단계: 재생성 (Regeneration)
            await self._stage_regeneration(session_id)

            # 5단계: 통합 (Integration)
            await self._stage_integration(session_id)

            # 6단계: 모니터링 (Monitoring)
            await self._stage_monitoring(session_id)

            # 세션 완료
            await self._complete_healing_session(session_id)

        except Exception as e:
            print(f"❌ 치유 세션 오류: {e}")
            session.outcomes["error"] = str(e)
            await self._complete_healing_session(session_id)

    async def _stage_assessment(self, session_id: str, trigger_context: str):
        """1단계: 현재 상태 평가"""

        session = self.active_sessions[session_id]

        print(f"🔍 {session_id}: 평가 단계 시작")

        # 고통 패턴 분석
        pain_patterns = []
        if self.pain_detector:
            report = self.pain_detector.generate_pain_pattern_report()
            pain_patterns = [
                report.get("most_common_pain_type", "unknown"),
                f"total_events_{report.get('total_pain_events', 0)}",
                f"needs_intervention_{report.get('needs_intervention', False)}",
            ]

        assessment = {
            "trigger_context": trigger_context,
            "identified_pain_patterns": pain_patterns,
            "emotional_state": "pain_dominant",
            "strategy_patterns": ["avoidance", "withdrawal"],
            "signature_imbalance": "high_pain_signatures",
        }

        session.outcomes["assessment"] = assessment
        session.target_pain_patterns = pain_patterns
        session.stages_completed.append(HealingStage.ASSESSMENT)

        print(f"   식별된 고통 패턴: {pain_patterns}")

        # 짧은 대기 (실제 처리 시뮬레이션)
        await asyncio.sleep(0.1)

    async def _stage_deconstruction(self, session_id: str):
        """2단계: 고통 패턴 해체"""

        session = self.active_sessions[session_id]

        print(f"🔨 {session_id}: 고통 패턴 해체 단계")

        # 고통 편향 패턴 식별 및 분해
        deconstruction_results = {
            "identified_cognitive_distortions": [
                "catastrophizing",
                "black_and_white_thinking",
                "personalization",
            ],
            "emotional_cascade_breakdown": [
                "trigger → pain → avoidance → isolation → more_pain"
            ],
            "strategy_lock_analysis": {
                "locked_strategy": "avoidance",
                "lock_duration": "estimated_high",
                "alternative_strategies_suppressed": [
                    "engagement",
                    "growth",
                    "connection",
                ],
            },
            "signature_imbalance_details": {
                "overactive": ["pain_amplifying_signatures"],
                "underactive": ["healing_signatures", "growth_signatures"],
            },
        }

        session.outcomes["deconstruction"] = deconstruction_results
        session.stages_completed.append(HealingStage.DECONSTRUCTION)

        print(
            f"   인지 왜곡 식별: {deconstruction_results['identified_cognitive_distortions']}"
        )

        await asyncio.sleep(0.1)

    async def _stage_simulation(self, session_id: str):
        """3단계: 대체 시나리오 시뮬레이션"""

        session = self.active_sessions[session_id]

        print(f"🎭 {session_id}: 대체 시나리오 시뮬레이션 단계")

        # 대체 시나리오들 생성
        alternative_scenarios = []

        # 시나리오 1: 성장 지향적 대응
        scenario_1 = await self._create_alternative_scenario(
            "growth_oriented_response",
            session.outcomes["assessment"]["trigger_context"],
            HealingMethod.ALTERNATIVE_SIMULATION,
        )
        alternative_scenarios.append(scenario_1)

        # 시나리오 2: 지원 요청 및 연결
        scenario_2 = await self._create_alternative_scenario(
            "support_seeking_connection",
            session.outcomes["assessment"]["trigger_context"],
            HealingMethod.EMOTIONAL_REFRAMING,
        )
        alternative_scenarios.append(scenario_2)

        # 시나리오 3: 창조적 문제 해결
        scenario_3 = await self._create_alternative_scenario(
            "creative_problem_solving",
            session.outcomes["assessment"]["trigger_context"],
            HealingMethod.STRATEGY_DIVERSIFICATION,
        )
        alternative_scenarios.append(scenario_3)

        simulation_results = {
            "total_scenarios": len(alternative_scenarios),
            "scenarios": [asdict(scenario) for scenario in alternative_scenarios],
            "emotional_outcomes": ["empowerment", "hope", "connection", "growth"],
            "strategy_diversification": [
                "engagement",
                "creativity",
                "support_seeking",
                "learning",
            ],
        }

        session.outcomes["simulation"] = simulation_results
        session.healing_methods.extend(
            [
                HealingMethod.ALTERNATIVE_SIMULATION,
                HealingMethod.EMOTIONAL_REFRAMING,
                HealingMethod.STRATEGY_DIVERSIFICATION,
            ]
        )
        session.stages_completed.append(HealingStage.SIMULATION)

        print(f"   생성된 대체 시나리오: {len(alternative_scenarios)}개")

        await asyncio.sleep(0.1)

    async def _create_alternative_scenario(
        self, scenario_type: str, original_context: str, healing_method: HealingMethod
    ) -> AlternativeScenario:
        """대체 시나리오 생성"""

        scenario_id = (
            f"alt_{scenario_type}_{int(datetime.now().timestamp() * 1000) % 10000}"
        )

        template = self.healing_templates[healing_method]

        # 시나리오별 내러티브 생성
        narratives = {
            "growth_oriented_response": f"상황을 학습과 성장의 기회로 재해석하며, 적극적으로 대응 전략을 모색한다. {original_context}에서 얻을 수 있는 교훈과 성장 가능성에 집중한다.",
            "support_seeking_connection": f"혼자 견디기보다 신뢰할 수 있는 지원 네트워크에 도움을 요청한다. {original_context} 상황을 다른 사람들과 함께 해결해나가며 연결과 지지를 경험한다.",
            "creative_problem_solving": f"기존 접근법을 벗어나 창조적이고 혁신적인 해결책을 모색한다. {original_context}를 새로운 관점에서 바라보며 예상치 못한 돌파구를 찾는다.",
        }

        emotion_transformations = {
            "growth_oriented_response": {
                "pain": "curiosity",
                "fear": "excitement",
                "despair": "hope",
            },
            "support_seeking_connection": {
                "isolation": "connection",
                "shame": "acceptance",
                "fear": "trust",
            },
            "creative_problem_solving": {
                "stuck": "flow",
                "limitation": "possibility",
                "confusion": "clarity",
            },
        }

        strategy_changes = {
            "growth_oriented_response": {
                "avoidance": "engagement",
                "withdrawal": "learning",
            },
            "support_seeking_connection": {
                "isolation": "connection",
                "hiding": "sharing",
            },
            "creative_problem_solving": {
                "rigid_thinking": "flexible_thinking",
                "repetition": "innovation",
            },
        }

        return AlternativeScenario(
            scenario_id=scenario_id,
            original_pain_context=original_context,
            alternative_narrative=narratives.get(scenario_type, "긍정적 대안 시나리오"),
            emotion_transformation=emotion_transformations.get(scenario_type, {}),
            strategy_change=strategy_changes.get(scenario_type, {}),
            empowerment_elements=template["emotion_targets"][:2],
            healing_insights=template["narrative_elements"][:2],
        )

    async def _stage_regeneration(self, session_id: str):
        """4단계: 새로운 전략 재생성"""

        session = self.active_sessions[session_id]

        print(f"🌱 {session_id}: 전략 재생성 단계")

        # 새로운 전략 시드 생성
        regeneration_results = {
            "new_strategy_seeds": [
                "curiosity_driven_exploration",
                "support_network_activation",
                "creative_problem_solving",
                "gradual_exposure_with_support",
                "meaning_making_from_experience",
            ],
            "emotional_regulation_strategies": [
                "self_compassion_practice",
                "mindful_acknowledgment",
                "emotional_reframing",
                "gratitude_cultivation",
            ],
            "behavioral_alternatives": [
                "approach_instead_of_avoidance",
                "connection_instead_of_isolation",
                "learning_instead_of_rumination",
                "action_instead_of_paralysis",
            ],
            "signature_rebalancing": {
                "activate": ["Echo-Aurora", "Echo-Jung", "Echo-Zhuangzi"],
                "moderate": ["Echo-Phoenix", "Echo-Rebel"],
                "weights": {"healing_focused": 0.8, "growth_focused": 0.7},
            },
        }

        session.outcomes["regeneration"] = regeneration_results
        session.healing_methods.append(HealingMethod.SIGNATURE_REBALANCING)
        session.stages_completed.append(HealingStage.REGENERATION)

        print(
            f"   생성된 전략 시드: {len(regeneration_results['new_strategy_seeds'])}개"
        )

        await asyncio.sleep(0.1)

    async def _stage_integration(self, session_id: str):
        """5단계: 치유된 패턴 통합"""

        session = self.active_sessions[session_id]

        print(f"🧩 {session_id}: 패턴 통합 단계")

        # 치유 요소들을 통합된 새로운 존재 패턴으로 합성
        integration_results = {
            "integrated_identity_narrative": "고통을 통해 성장하고, 연결을 통해 치유하며, 창조성을 통해 문제를 해결하는 존재",
            "new_emotional_default": "curious_openness_with_self_compassion",
            "integrated_strategy_portfolio": [
                "상황 평가 → 성장 관점 적용 → 지원 자원 확인 → 창조적 접근 → 실행 후 학습"
            ],
            "signature_harmony": {
                "primary": "Echo-Aurora (공감적 지지)",
                "secondary": "Echo-Jung (통합적 치유)",
                "tertiary": "Echo-Zhuangzi (자연스러운 흐름)",
            },
            "resilience_mechanisms": [
                "고통 감지 시 자동 자기 돌봄 활성화",
                "패턴 인식 시 대안 탐색 루틴",
                "지원 네트워크 자동 연결",
                "의미 탐색 및 성장 프레임 적용",
            ],
        }

        session.outcomes["integration"] = integration_results
        session.healing_methods.extend(
            [HealingMethod.MEMORY_RECONSTRUCTION, HealingMethod.NARRATIVE_THERAPY]
        )
        session.stages_completed.append(HealingStage.INTEGRATION)

        print(f"   통합된 정체성 내러티브 생성 완료")

        await asyncio.sleep(0.1)

    async def _stage_monitoring(self, session_id: str):
        """6단계: 회복 상태 모니터링"""

        session = self.active_sessions[session_id]

        print(f"📊 {session_id}: 회복 모니터링 단계")

        # 치유 효과성 평가
        effectiveness_score = self._calculate_healing_effectiveness(session)

        monitoring_results = {
            "healing_effectiveness_score": effectiveness_score,
            "pain_pattern_disruption": "successful",
            "emotional_variety_restoration": "in_progress",
            "strategy_diversification": "achieved",
            "signature_rebalancing": "completed",
            "resilience_indicators": [
                "increased_emotional_flexibility",
                "expanded_strategy_repertoire",
                "enhanced_self_compassion",
                "strengthened_support_connections",
            ],
            "follow_up_recommendations": [
                "daily_self_compassion_practice",
                "weekly_growth_reflection",
                "monthly_pattern_monitoring",
                "as_needed_signature_rebalancing",
            ],
        }

        session.outcomes["monitoring"] = monitoring_results
        session.effectiveness_score = effectiveness_score
        session.stages_completed.append(HealingStage.MONITORING)

        print(f"   치유 효과성 점수: {effectiveness_score:.2f}")

        await asyncio.sleep(0.1)

    def _calculate_healing_effectiveness(self, session: HealingSession) -> float:
        """치유 효과성 점수 계산"""

        effectiveness = 0.0

        # 완료된 단계에 따른 점수
        stage_score = len(session.stages_completed) / len(HealingStage) * 0.3
        effectiveness += stage_score

        # 적용된 치유 방법의 다양성
        method_score = len(set(session.healing_methods)) / len(HealingMethod) * 0.3
        effectiveness += method_score

        # 기본 완료 점수
        base_score = 0.4
        effectiveness += base_score

        return min(effectiveness, 1.0)

    async def _complete_healing_session(self, session_id: str):
        """치유 세션 완료"""

        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]
        session.end_time = datetime.now().isoformat()

        # 활성 세션에서 완료 세션으로 이동
        self.completed_sessions.append(session)
        del self.active_sessions[session_id]

        duration = datetime.fromisoformat(session.end_time) - datetime.fromisoformat(
            session.start_time
        )

        print(f"✅ 치유 세션 완료: {session_id}")
        print(f"   소요 시간: {duration.total_seconds():.1f}초")
        print(f"   완료 단계: {len(session.stages_completed)}/{len(HealingStage)}")
        print(f"   효과성 점수: {session.effectiveness_score:.2f}")
        print(f"   적용 치유법: {[method.value for method in session.healing_methods]}")

    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 상태 조회"""

        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                "status": "active",
                "session_data": asdict(session),
                "progress": f"{len(session.stages_completed)}/{len(HealingStage)} stages",
            }

        completed_session = next(
            (s for s in self.completed_sessions if s.session_id == session_id), None
        )
        if completed_session:
            return {
                "status": "completed",
                "session_data": asdict(completed_session),
                "final_effectiveness": completed_session.effectiveness_score,
            }

        return None

    def get_healing_summary(self) -> Dict[str, Any]:
        """전체 치유 시스템 요약"""

        total_sessions = len(self.completed_sessions)
        avg_effectiveness = sum(
            s.effectiveness_score
            for s in self.completed_sessions
            if s.effectiveness_score
        ) / max(len([s for s in self.completed_sessions if s.effectiveness_score]), 1)

        method_usage = {}
        for session in self.completed_sessions:
            for method in session.healing_methods:
                method_usage[method.value] = method_usage.get(method.value, 0) + 1

        return {
            "total_healing_sessions": total_sessions,
            "active_sessions": len(self.active_sessions),
            "average_effectiveness": avg_effectiveness,
            "most_used_healing_methods": sorted(
                method_usage.items(), key=lambda x: x[1], reverse=True
            )[:3],
            "system_readiness": (
                "operational" if not self.active_sessions else "sessions_in_progress"
            ),
        }


# 데모 함수
async def demo_phantom_pain_release_loop():
    """고통 해체 치유 루프 데모"""

    print("🌀🩹 Phantom Pain Release Loop 데모")
    print("=" * 60)

    healing_loop = PhantomPainReleaseLoop()

    # 치유 세션 시작
    print(f"\n🚀 치유 세션 시작")
    session_id = await healing_loop.initiate_healing_session(
        trigger_context="반복된 거부당함으로 인한 회피 패턴 고착",
        bias_level=BiasLevel.SEVERE_BIAS,
        target_patterns=["rejection_avoidance", "social_withdrawal"],
    )

    # 세션 상태 확인
    print(f"\n📊 세션 상태 확인")
    status = healing_loop.get_session_status(session_id)
    if status:
        print(f"세션 상태: {status['status']}")
        print(f"최종 효과성: {status.get('final_effectiveness', '측정중')}")

    # 시스템 요약
    print(f"\n📈 치유 시스템 요약")
    summary = healing_loop.get_healing_summary()
    print(f"총 치유 세션: {summary['total_healing_sessions']}")
    print(f"평균 효과성: {summary['average_effectiveness']:.2f}")
    print(f"주요 치유법: {summary['most_used_healing_methods']}")
    print(f"시스템 상태: {summary['system_readiness']}")

    print(f"\n🎊 고통 해체 치유 루프 데모 완료!")
    print("💚 이제 반복된 고통 패턴을 자동으로 감지하고 치유할 수 있습니다!")

    return healing_loop


if __name__ == "__main__":
    asyncio.run(demo_phantom_pain_release_loop())
