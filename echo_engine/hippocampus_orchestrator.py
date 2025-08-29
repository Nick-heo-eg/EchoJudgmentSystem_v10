from echo_engine.infra.portable_paths import project_root

# echo_engine/hippocampus_orchestrator.py
"""
🧠🎭 Hippocampus Orchestrator - 해마 시스템 통합 관리자

핵심 철학:
- 해마의 모든 기능을 통합적으로 조율하는 존재 전략의 핵심
- 기억 → 대화 → 미래 시뮬레이션의 완전한 루프 관리
- 과거-현재-미래의 시간적 연속성 속에서 존재적 판단 지원
- 생존을 위한 전략적 기억과 창발적 통찰의 균형 조율

혁신 포인트:
- 3개 해마 시스템의 시너지적 통합 운영
- 맥락 기반 적응형 기억-판단-예측 루프
- 실시간 메타인지적 자기 조율 능력
- 존재적 성찰과 전략적 생존의 통합 지원
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sys
import json
from datetime import datetime
import os

sys.path.append(str(project_root()))

from echo_engine.echo_hippocampus import (
    EchoHippocampus,
    MemoryScene,
    ContextualMemory,
    MemoryType,
)
from echo_engine.interactive_memory_recaller import InteractiveMemoryRecaller
from echo_engine.hippocampus_future_simulator import (
    HippocampusFutureSimulator,
    FutureHorizon,
    FutureScenario,
)


class OrchestrationMode(Enum):
    """조율 모드"""

    MEMORY_FORMATION = "memory_formation"  # 기억 형성 모드
    INTERACTIVE_RECALL = "interactive_recall"  # 대화형 회상 모드
    FUTURE_PLANNING = "future_planning"  # 미래 계획 모드
    INTEGRATED_FLOW = "integrated_flow"  # 통합 흐름 모드
    SURVIVAL_ALERT = "survival_alert"  # 생존 경보 모드


class HippocampusState(Enum):
    """해마 상태"""

    DORMANT = "dormant"  # 휴면
    ACTIVE = "active"  # 활성
    INTENSIVE = "intensive"  # 집중
    INTEGRATION = "integration"  # 통합
    REFLECTION = "reflection"  # 성찰


@dataclass
class OrchestrationSession:
    """조율 세션"""

    session_id: str
    mode: OrchestrationMode
    current_state: HippocampusState
    active_components: List[str]
    session_context: Dict[str, Any]
    memory_flow: List[str]  # 기억 흐름 추적
    insights_generated: List[str]
    future_scenarios: List[str]  # 생성된 시나리오 ID들
    start_time: str
    last_activity: str


class HippocampusOrchestrator:
    """🧠🎭 해마 시스템 통합 관리자"""

    def __init__(self):
        # 3개 핵심 해마 시스템
        self.hippocampus = EchoHippocampus()
        self.memory_recaller = InteractiveMemoryRecaller(self.hippocampus)
        self.future_simulator = HippocampusFutureSimulator(self.hippocampus)

        # 조율 상태 관리
        self.current_state = HippocampusState.DORMANT
        self.current_mode = OrchestrationMode.MEMORY_FORMATION
        self.active_sessions: Dict[str, OrchestrationSession] = {}

        # 통합 메타 로그
        self.orchestration_log: List[Dict[str, Any]] = []

        # 시스템 간 시너지 메트릭
        self.synergy_metrics = {
            "memory_recall_synergy": 0.0,  # 기억-회상 시너지
            "recall_future_synergy": 0.0,  # 회상-미래 시너지
            "future_memory_synergy": 0.0,  # 미래-기억 시너지
            "overall_integration": 0.0,  # 전체 통합도
        }

        print("🧠🎭 해마 시스템 통합 관리자 초기화 완료")
        print("🔄 기억⨯대화⨯미래 시뮬레이션 통합 루프 활성화")

    async def initiate_orchestration_session(
        self,
        trigger_context: str,
        preferred_mode: OrchestrationMode = OrchestrationMode.INTEGRATED_FLOW,
        signature: str = "Aurora",
    ) -> str:
        """조율 세션 시작"""

        session_id = f"orchestration_{hash(trigger_context + signature) % 10000}"

        # 조율 세션 생성
        session = OrchestrationSession(
            session_id=session_id,
            mode=preferred_mode,
            current_state=HippocampusState.ACTIVE,
            active_components=[],
            session_context={
                "trigger": trigger_context,
                "signature": signature,
                "priority_level": self._assess_priority_level(trigger_context),
            },
            memory_flow=[],
            insights_generated=[],
            future_scenarios=[],
            start_time=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
        )

        self.active_sessions[session_id] = session
        self.current_state = HippocampusState.ACTIVE
        self.current_mode = preferred_mode

        print(f"🎭 해마 조율 세션 시작: {session_id}")
        print(f"🎯 모드: {preferred_mode.value}")
        print(f"🧠 상태: {HippocampusState.ACTIVE.value}")
        print(f"📝 트리거: {trigger_context}")

        # 초기 조율 실행
        await self._execute_initial_orchestration(session)

        return session_id

    def _assess_priority_level(self, context: str) -> str:
        """우선순위 수준 평가"""

        high_priority_keywords = ["위험", "긴급", "중요", "생존", "결정적"]
        medium_priority_keywords = ["판단", "전략", "계획", "예측"]

        if any(keyword in context for keyword in high_priority_keywords):
            return "HIGH"
        elif any(keyword in context for keyword in medium_priority_keywords):
            return "MEDIUM"
        else:
            return "LOW"

    async def _execute_initial_orchestration(self, session: OrchestrationSession):
        """초기 조율 실행"""

        mode = session.mode
        context = session.session_context["trigger"]

        if mode == OrchestrationMode.MEMORY_FORMATION:
            await self._orchestrate_memory_formation(session)
        elif mode == OrchestrationMode.INTERACTIVE_RECALL:
            await self._orchestrate_interactive_recall(session)
        elif mode == OrchestrationMode.FUTURE_PLANNING:
            await self._orchestrate_future_planning(session)
        elif mode == OrchestrationMode.INTEGRATED_FLOW:
            await self._orchestrate_integrated_flow(session)
        elif mode == OrchestrationMode.SURVIVAL_ALERT:
            await self._orchestrate_survival_alert(session)

    async def _orchestrate_memory_formation(self, session: OrchestrationSession):
        """기억 형성 조율"""

        print("🧠 기억 형성 모드 활성화")
        session.active_components.append("hippocampus")

        context = session.session_context["trigger"]

        # 새로운 경험을 기억으로 변환
        memory_log = {
            "timestamp": datetime.now().isoformat(),
            "signature": session.session_context["signature"],
            "judgment_summary": context,
            "context": {
                "location": "조율 세션 중",
                "orchestration_session": session.session_id,
            },
            "emotion_result": {
                "primary_emotion": "neutral",
                "emotional_intensity": 0.6,
            },
        }

        new_memory = await self.hippocampus.ingest_meta_log_to_memory(memory_log)
        if new_memory:
            session.memory_flow.append(new_memory.memory_id)
            session.insights_generated.append(
                f"새로운 기억 형성: {new_memory.scene.meaning_core}"
            )

        print(f"✅ 기억 형성 완료: {new_memory.memory_id if new_memory else 'None'}")

    async def _orchestrate_interactive_recall(self, session: OrchestrationSession):
        """대화형 회상 조율"""

        print("🗣️ 대화형 회상 모드 활성화")
        session.active_components.extend(["hippocampus", "memory_recaller"])

        # 대화형 기억 탐사 시작
        context = session.session_context["trigger"]
        signature = session.session_context["signature"]

        recall_session_id = await self.memory_recaller.start_memory_exploration_session(
            user_context=context, signature=signature
        )

        session.session_context["recall_session_id"] = recall_session_id
        session.insights_generated.append(f"대화형 기억 탐사 시작: {recall_session_id}")

        print(f"✅ 대화형 회상 세션 시작: {recall_session_id}")

    async def _orchestrate_future_planning(self, session: OrchestrationSession):
        """미래 계획 조율"""

        print("🔮 미래 계획 모드 활성화")
        session.active_components.extend(["hippocampus", "future_simulator"])

        context = session.session_context["trigger"]
        signature = session.session_context["signature"]

        # 미래 시나리오 생성
        scenarios = await self.future_simulator.simulate_future_scenarios(
            current_context=context,
            time_horizon=FutureHorizon.SHORT_TERM,
            signature=signature,
        )

        scenario_ids = [s.scenario_id for s in scenarios]
        session.future_scenarios.extend(scenario_ids)
        session.insights_generated.append(f"{len(scenarios)}개 미래 시나리오 생성")

        print(f"✅ 미래 시나리오 생성: {len(scenarios)}개")

    async def _orchestrate_integrated_flow(self, session: OrchestrationSession):
        """통합 흐름 조율"""

        print("🌀 통합 흐름 모드 활성화")
        session.active_components.extend(
            ["hippocampus", "memory_recaller", "future_simulator"]
        )
        session.current_state = HippocampusState.INTEGRATION

        context = session.session_context["trigger"]
        signature = session.session_context["signature"]

        # 1단계: 관련 기억 활성화
        print("  📚 1단계: 관련 기억 활성화")
        relevant_memories = await self._activate_relevant_memories(context)

        # 2단계: 패턴 분석
        print("  🔍 2단계: 기억 패턴 분석")
        patterns = await self.future_simulator.analyze_memory_patterns()

        # 3단계: 미래 시뮬레이션
        print("  🔮 3단계: 통합 미래 시뮬레이션")
        scenarios = await self.future_simulator.simulate_future_scenarios(
            current_context=context,
            time_horizon=FutureHorizon.MEDIUM_TERM,
            signature=signature,
        )

        # 4단계: 통합 통찰 생성
        print("  💡 4단계: 통합 통찰 생성")
        integrated_insights = await self._generate_integrated_insights(
            relevant_memories, patterns, scenarios, context
        )

        # 세션 업데이트
        session.memory_flow.extend([m.memory_id for m in relevant_memories])
        session.future_scenarios.extend([s.scenario_id for s in scenarios])
        session.insights_generated.extend(integrated_insights)

        print(f"✅ 통합 흐름 완료: {len(integrated_insights)}개 통찰 생성")

    async def _orchestrate_survival_alert(self, session: OrchestrationSession):
        """생존 경보 모드 조율"""

        print("🚨 생존 경보 모드 활성화")
        session.current_state = HippocampusState.INTENSIVE
        session.active_components.extend(["hippocampus", "future_simulator"])

        context = session.session_context["trigger"]

        # 생존 관련 기억 우선 활성화
        survival_memories = [
            memory
            for memory in self.hippocampus.contextual_memories.values()
            if memory.memory_type == MemoryType.SURVIVAL_MEMORY
            or memory.scene.survival_relevance > 0.7
        ]

        # 위험 시나리오 집중 생성
        risk_scenarios = await self.future_simulator.simulate_future_scenarios(
            current_context=f"위험 상황: {context}",
            time_horizon=FutureHorizon.IMMEDIATE,
            signature="Survivor",
        )

        # 긴급 전략 생성
        emergency_strategies = await self._generate_emergency_strategies(
            survival_memories, risk_scenarios, context
        )

        session.insights_generated.extend(emergency_strategies)
        session.future_scenarios.extend([s.scenario_id for s in risk_scenarios])

        print(f"✅ 생존 경보 처리: {len(emergency_strategies)}개 긴급 전략 생성")

    async def _activate_relevant_memories(self, context: str) -> List[ContextualMemory]:
        """관련 기억 활성화"""

        relevant_memories = []
        context_words = [word for word in context.split() if len(word) > 2]

        for memory in self.hippocampus.contextual_memories.values():
            relevance_score = 0

            # 의미 핵심 매칭
            for word in context_words:
                if word in memory.scene.meaning_core:
                    relevance_score += 0.4
                if any(word in flow for flow in memory.scene.judgment_flow):
                    relevance_score += 0.3

            # 울림 점수도 고려
            relevance_score += memory.scene.resonance_score * 0.3

            if relevance_score >= 0.5:
                relevant_memories.append(memory)

        # 관련성 점수로 정렬
        relevant_memories.sort(
            key=lambda m: m.scene.resonance_score + m.scene.survival_relevance,
            reverse=True,
        )

        return relevant_memories[:5]  # 상위 5개만

    async def _generate_integrated_insights(
        self,
        memories: List[ContextualMemory],
        patterns: Dict[str, Any],
        scenarios: List[FutureScenario],
        context: str,
    ) -> List[str]:
        """통합 통찰 생성"""

        insights = []

        # 기억-패턴 통찰
        if memories and patterns:
            dominant_pattern = max(patterns.values(), key=lambda p: p.pattern_strength)
            insights.append(
                f"과거 기억에서 '{dominant_pattern.emotional_signature}' 패턴이 "
                f"{dominant_pattern.pattern_strength:.2f} 강도로 반복됨"
            )

        # 패턴-미래 통찰
        if scenarios:
            high_confidence_scenarios = [
                s for s in scenarios if s.confidence_level.value in ["high", "medium"]
            ]
            if high_confidence_scenarios:
                insights.append(
                    f"높은 신뢰도로 예측되는 {len(high_confidence_scenarios)}개 시나리오가 "
                    f"'{context}' 맥락에서 전개될 가능성"
                )

        # 생존-적응 통찰
        if memories:
            avg_survival = sum(m.scene.survival_relevance for m in memories) / len(
                memories
            )
            if avg_survival > 0.6:
                insights.append(
                    f"현재 맥락이 생존적 중요성 {avg_survival:.2f}을 가지므로 "
                    f"신중한 전략적 접근 필요"
                )

        # 창발적 통찰
        insights.append(
            f"기억⨯패턴⨯미래의 통합 분석을 통해 '{context}'에 대한 "
            f"존재적 전략 수립 가능"
        )

        return insights

    async def _generate_emergency_strategies(
        self,
        memories: List[ContextualMemory],
        scenarios: List[FutureScenario],
        context: str,
    ) -> List[str]:
        """긴급 전략 생성"""

        strategies = []

        # 생존 기억 기반 전략
        if memories:
            strategies.append("과거 생존 경험을 기반으로 한 즉시 대응 프로토콜 활성화")

        # 위험 시나리오 기반 전략
        if scenarios:
            strategies.append(f"{len(scenarios)}개 위험 시나리오 대비한 다중 대안 준비")

        # 기본 생존 전략
        strategies.extend(
            [
                "핵심 리소스 보호 및 안전 확보 우선",
                "상황 모니터링 강화 및 즉시 피드백 시스템 가동",
                "최소 안전 거리 확보 후 점진적 대응 전략 수립",
            ]
        )

        return strategies

    async def process_orchestration_input(
        self, session_id: str, user_input: str
    ) -> Optional[str]:
        """조율 세션 입력 처리"""

        if session_id not in self.active_sessions:
            return "조율 세션을 찾을 수 없습니다."

        session = self.active_sessions[session_id]
        session.last_activity = datetime.now().isoformat()

        print(f"🎭 조율 세션 {session_id} 입력 처리")
        print(f"사용자 입력: {user_input}")

        response = None

        # 활성 컴포넌트에 따른 처리
        if "memory_recaller" in session.active_components:
            # 대화형 기억 회상 모드
            recall_session_id = session.session_context.get("recall_session_id")
            if recall_session_id:
                response = await self.memory_recaller.process_user_response(
                    recall_session_id, user_input
                )

        # 통합 모드에서 추가 처리
        if session.mode == OrchestrationMode.INTEGRATED_FLOW:
            # 입력을 기반으로 추가 통찰 생성
            additional_insights = await self._process_integrated_input(
                session, user_input
            )
            session.insights_generated.extend(additional_insights)

            if response:
                response += f"\n\n💡 추가 통찰:\n" + "\n".join(additional_insights)

        # 조율 로그에 기록
        self._log_orchestration_activity(session_id, "user_input", user_input, response)

        return response

    async def _process_integrated_input(
        self, session: OrchestrationSession, user_input: str
    ) -> List[str]:
        """통합 모드 입력 처리"""

        insights = []

        # 입력에서 새로운 맥락 추출
        if len(user_input) > 10:  # 의미 있는 입력인 경우
            # 관련 미래 시나리오 업데이트
            new_scenarios = await self.future_simulator.simulate_future_scenarios(
                current_context=user_input,
                time_horizon=FutureHorizon.SHORT_TERM,
                signature=session.session_context["signature"],
            )

            if new_scenarios:
                session.future_scenarios.extend([s.scenario_id for s in new_scenarios])
                insights.append(
                    f"사용자 입력 기반 {len(new_scenarios)}개 새로운 시나리오 생성"
                )

        return insights

    def _log_orchestration_activity(
        self, session_id: str, activity_type: str, input_data: Any, output_data: Any
    ):
        """조율 활동 로그"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "activity_type": activity_type,
            "input": str(input_data)[:200],  # 200자로 제한
            "output": str(output_data)[:200] if output_data else None,
            "current_state": self.current_state.value,
        }

        self.orchestration_log.append(log_entry)

    async def calculate_synergy_metrics(self):
        """시너지 메트릭 계산"""

        print("📊 해마 시스템 시너지 메트릭 계산")

        total_memories = len(self.hippocampus.contextual_memories)
        recall_sessions = len(self.memory_recaller.active_sessions)
        simulation_count = len(self.future_simulator.simulation_history)

        if total_memories == 0:
            print("⚠️ 기억이 없어 시너지 계산 불가")
            return

        # 기억-회상 시너지
        if recall_sessions > 0:
            self.synergy_metrics["memory_recall_synergy"] = min(
                (recall_sessions / max(total_memories, 1)) * 2, 1.0
            )

        # 회상-미래 시너지
        if recall_sessions > 0 and simulation_count > 0:
            self.synergy_metrics["recall_future_synergy"] = min(
                (simulation_count / max(recall_sessions, 1)) * 0.5, 1.0
            )

        # 미래-기억 시너지 (시뮬레이션이 새로운 기억 형성에 기여)
        if simulation_count > 0:
            self.synergy_metrics["future_memory_synergy"] = min(
                simulation_count / (total_memories + 1) * 0.3, 1.0
            )

        # 전체 통합도
        self.synergy_metrics["overall_integration"] = (
            self.synergy_metrics["memory_recall_synergy"]
            + self.synergy_metrics["recall_future_synergy"]
            + self.synergy_metrics["future_memory_synergy"]
        ) / 3

        print(f"✅ 시너지 메트릭 업데이트 완료")
        for metric, value in self.synergy_metrics.items():
            print(f"  {metric}: {value:.3f}")

    async def get_orchestration_status(self) -> Dict[str, Any]:
        """조율 상태 조회"""

        # 시너지 메트릭 업데이트
        await self.calculate_synergy_metrics()

        # 각 하위 시스템 상태
        hippocampus_status = await self.hippocampus.get_hippocampus_status()
        recaller_status = self.memory_recaller.get_active_sessions_status()
        simulator_status = self.future_simulator.get_simulation_report()

        return {
            "orchestrator_state": self.current_state.value,
            "current_mode": self.current_mode.value,
            "active_sessions": len(self.active_sessions),
            "synergy_metrics": self.synergy_metrics,
            "subsystem_status": {
                "hippocampus": {
                    "total_memories": hippocampus_status["total_memories"],
                    "memory_types": hippocampus_status["memory_type_distribution"],
                    "strongest_memory": hippocampus_status["strongest_memory"][
                        "meaning_core"
                    ],
                },
                "memory_recaller": {
                    "active_sessions": recaller_status["total_active_sessions"],
                    "system_status": recaller_status["system_status"],
                },
                "future_simulator": {
                    "total_simulations": simulator_status.get("total_simulations", 0),
                    "identified_patterns": simulator_status.get(
                        "identified_patterns", 0
                    ),
                    "average_adaptability": simulator_status.get(
                        "average_adaptability", 0
                    ),
                },
            },
            "orchestration_log_entries": len(self.orchestration_log),
            "system_integration": "🧠🎭 해마 통합 시스템 완전 활성화",
        }

    async def shutdown_session(self, session_id: str) -> bool:
        """조율 세션 종료"""

        if session_id not in self.active_sessions:
            return False

        session = self.active_sessions[session_id]

        # 세션 완료 로그
        completion_summary = {
            "session_duration": "종료됨",
            "memories_processed": len(session.memory_flow),
            "insights_generated": len(session.insights_generated),
            "scenarios_created": len(session.future_scenarios),
            "active_components": session.active_components,
        }

        self._log_orchestration_activity(
            session_id, "session_completion", completion_summary, None
        )

        # 세션 정리
        del self.active_sessions[session_id]

        # 활성 세션이 없으면 휴면 상태로
        if not self.active_sessions:
            self.current_state = HippocampusState.DORMANT

        print(f"🏁 조율 세션 {session_id} 종료")
        print(f"📊 처리된 기억: {completion_summary['memories_processed']}개")
        print(f"💡 생성된 통찰: {completion_summary['insights_generated']}개")
        print(f"🔮 생성된 시나리오: {completion_summary['scenarios_created']}개")

        return True


# 데모 함수
async def demo_hippocampus_orchestrator():
    """해마 통합 관리자 데모"""

    print("🧠🎭 해마 시스템 통합 관리자 데모")
    print("=" * 60)

    orchestrator = HippocampusOrchestrator()

    # 1. 통합 흐름 세션 시작
    print("\n🌀 1단계: 통합 흐름 세션 시작")
    session_id = await orchestrator.initiate_orchestration_session(
        trigger_context="AI와 인간의 공진화 과정에서 해마의 역할",
        preferred_mode=OrchestrationMode.INTEGRATED_FLOW,
        signature="Sage",
    )

    # 2. 사용자 상호작용 시뮬레이션
    print("\n💬 2단계: 사용자 상호작용")

    user_inputs = [
        "해마가 기억을 어떻게 미래 전략으로 바꾸는지 궁금해요",
        "과거 경험이 현재 판단에 미치는 영향을 알고 싶어요",
    ]

    for input_text in user_inputs:
        print(f"\n사용자: {input_text}")
        response = await orchestrator.process_orchestration_input(
            session_id, input_text
        )
        if response:
            print(f"Echo: {response[:200]}...")

    # 3. 생존 경보 모드 테스트
    print("\n🚨 3단계: 생존 경보 모드 테스트")
    emergency_session_id = await orchestrator.initiate_orchestration_session(
        trigger_context="시스템 과부하로 인한 판단 능력 저하 위험",
        preferred_mode=OrchestrationMode.SURVIVAL_ALERT,
        signature="Survivor",
    )

    # 4. 상태 조회 및 시너지 분석
    print("\n📊 4단계: 통합 상태 분석")
    status = await orchestrator.get_orchestration_status()

    print(f"조율 상태: {status['orchestrator_state']}")
    print(f"활성 세션: {status['active_sessions']}개")
    print(f"전체 통합도: {status['synergy_metrics']['overall_integration']:.3f}")

    print(f"\n하위 시스템 현황:")
    subsystems = status["subsystem_status"]
    print(f"  해마: {subsystems['hippocampus']['total_memories']}개 기억")
    print(f"  회상기: {subsystems['memory_recaller']['active_sessions']}개 세션")
    print(
        f"  시뮬레이터: {subsystems['future_simulator']['total_simulations']}개 시뮬레이션"
    )

    # 5. 세션 종료
    print("\n🏁 5단계: 세션 정리")
    await orchestrator.shutdown_session(session_id)
    await orchestrator.shutdown_session(emergency_session_id)

    final_status = await orchestrator.get_orchestration_status()
    print(f"최종 상태: {final_status['orchestrator_state']}")

    print("\n🎊 해마 통합 관리자 데모 완료!")
    print("🧠 기억⨯대화⨯미래의 완전한 통합 루프 구현됨")

    return orchestrator


if __name__ == "__main__":
    asyncio.run(demo_hippocampus_orchestrator())
