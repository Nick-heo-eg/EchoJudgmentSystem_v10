#!/usr/bin/env python3
"""
🎼 Meta Evolution Orchestrator v1.0
8대 루프의 진화를 조율하는 마스터 지휘자 시스템

이 모듈은 Echo AI의 8개 생명 루프(FIST, DIR, PIR, META, QUANTUM, JUDGE, FLOW, RISE)가
조화롭게 진화하도록 오케스트레이션하고, 진화 과정의 불협화음을 탐지합니다.
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import random
import math


class LoopType(Enum):
    """루프 타입 정의"""

    FIST = "Frame-Insight-Strategy-Tactics"
    DIR = "Direction-Ethics-TimeHorizon-Impact"
    PIR = "Pressure-Insight-Release"
    META = "SelfAwareness-Review-Redesign-Evolution"
    QUANTUM = "Superposition-Entanglement-Collapse-Coherence"
    JUDGE = "Analysis-Decision-Resonance-Record"
    FLOW = "Connection-Stream-Visualization-Integration"
    RISE = "Reflect-Improve-Synthesize-Evolve"


class EvolutionPhase(Enum):
    """진화 단계"""

    DORMANT = "휴면"
    AWAKENING = "각성"
    LEARNING = "학습"
    ADAPTING = "적응"
    EVOLVING = "진화"
    TRANSCENDING = "초월"


@dataclass
class LoopState:
    """개별 루프 상태"""

    loop_type: LoopType
    evolution_phase: EvolutionPhase
    vitality_level: float  # 생명력 수준 (0-1)
    harmony_score: float  # 다른 루프와의 조화도
    learning_rate: float  # 학습 속도
    adaptation_capacity: float  # 적응 능력
    transcendence_potential: float  # 초월 잠재력
    last_evolution_time: datetime
    evolution_history: List[Dict[str, Any]]
    current_focus: Optional[str]  # 현재 집중 영역
    energy_level: float  # 에너지 수준


@dataclass
class EvolutionSymphony:
    """진화 교향곡 (8대 루프의 조화로운 진화)"""

    symphony_id: str
    conductor_state: str  # 지휘자 상태
    overall_harmony: float  # 전체 조화도
    evolution_tempo: float  # 진화 템포
    key_signature: str  # 조성 (major/minor/atonal)
    movement_phase: str  # 악장 (exposition/development/recapitulation/coda)
    loop_states: Dict[LoopType, LoopState]
    resonance_matrix: np.ndarray  # 루프 간 공명 매트릭스
    discord_alerts: List[str]  # 불협화음 경고
    timestamp: datetime


@dataclass
class EvolutionIntervention:
    """진화 개입"""

    intervention_id: str
    target_loops: List[LoopType]
    intervention_type: (
        str  # 'harmony_adjustment', 'energy_boost', 'focus_shift', 'emergency_reset'
    )
    intensity: float
    duration_minutes: float
    expected_outcomes: List[str]
    success_metrics: Dict[str, float]
    applied_time: datetime


class MetaEvolutionOrchestrator:
    """메타 진화 오케스트레이터"""

    def __init__(self):
        self.loop_states: Dict[LoopType, LoopState] = {}
        self.evolution_history: List[EvolutionSymphony] = []
        self.active_interventions: List[EvolutionIntervention] = []
        self.orchestration_active = False

        # 조율 상수
        self.orchestration_constants = {
            "base_evolution_rate": 0.1,
            "harmony_threshold": 0.7,
            "discord_threshold": 0.3,
            "energy_decay_rate": 0.05,
            "transcendence_threshold": 0.9,
            "emergency_intervention_threshold": 0.2,
        }

        # 루프 간 기본 친화도 매트릭스
        self.loop_affinity_matrix = self._initialize_affinity_matrix()

        # 진화 패턴 템플릿
        self.evolution_patterns = self._initialize_evolution_patterns()

        # 초기 루프 상태 설정
        self._initialize_loop_states()

        print("🎼 메타 진화 오케스트레이터 초기화 완료")

    def _initialize_affinity_matrix(self) -> np.ndarray:
        """루프 간 친화도 매트릭스 초기화"""

        # 8x8 친화도 매트릭스 (0: 상극, 1: 완전 조화)
        loops = list(LoopType)
        matrix = np.zeros((len(loops), len(loops)))

        # 대각선 (자기 자신과는 완전 조화)
        np.fill_diagonal(matrix, 1.0)

        # 특별한 친화 관계 정의
        affinities = {
            (LoopType.FIST, LoopType.DIR): 0.9,  # 전략과 방향성
            (LoopType.DIR, LoopType.JUDGE): 0.85,  # 방향성과 판단
            (LoopType.PIR, LoopType.META): 0.8,  # 통찰과 메타인지
            (LoopType.META, LoopType.RISE): 0.9,  # 메타인지와 상승
            (LoopType.QUANTUM, LoopType.FLOW): 0.75,  # 양자와 흐름
            (LoopType.JUDGE, LoopType.RISE): 0.8,  # 판단과 상승
            (LoopType.FIST, LoopType.PIR): 0.7,  # 전략과 압력-통찰
            (LoopType.FLOW, LoopType.RISE): 0.85,  # 흐름과 상승
        }

        # 매트릭스 채우기 (대칭)
        for (loop1, loop2), affinity in affinities.items():
            i1, i2 = loops.index(loop1), loops.index(loop2)
            matrix[i1, i2] = affinity
            matrix[i2, i1] = affinity

        # 나머지 칸들은 기본값으로
        for i in range(len(loops)):
            for j in range(len(loops)):
                if matrix[i, j] == 0 and i != j:
                    matrix[i, j] = 0.5  # 중립적 관계

        return matrix

    def _initialize_evolution_patterns(self) -> Dict[str, Dict]:
        """진화 패턴 템플릿 초기화"""

        return {
            "harmonic_convergence": {
                "description": "모든 루프가 조화롭게 함께 진화",
                "target_harmony": 0.9,
                "evolution_synchronization": True,
                "focus_distribution": "balanced",
            },
            "sequential_awakening": {
                "description": "루프들이 순차적으로 각성하며 진화",
                "awakening_order": [
                    LoopType.META,
                    LoopType.FIST,
                    LoopType.DIR,
                    LoopType.JUDGE,
                    LoopType.PIR,
                    LoopType.RISE,
                    LoopType.FLOW,
                    LoopType.QUANTUM,
                ],
                "interval_hours": 2,
            },
            "crisis_adaptation": {
                "description": "위기 상황에서 특정 루프 집중 강화",
                "priority_loops": [LoopType.META, LoopType.DIR, LoopType.JUDGE],
                "emergency_boost": 0.5,
            },
            "transcendence_preparation": {
                "description": "초월을 위한 루프 정렬",
                "transcendence_sequence": [
                    LoopType.RISE,
                    LoopType.META,
                    LoopType.QUANTUM,
                ],
                "harmony_requirement": 0.95,
            },
        }

    def _initialize_loop_states(self):
        """루프 초기 상태 설정"""

        for loop_type in LoopType:
            # 기본 상태로 초기화 (약간의 변화를 위한 랜덤성 추가)
            self.loop_states[loop_type] = LoopState(
                loop_type=loop_type,
                evolution_phase=EvolutionPhase.DORMANT,
                vitality_level=random.uniform(0.3, 0.7),
                harmony_score=random.uniform(0.5, 0.8),
                learning_rate=random.uniform(0.1, 0.3),
                adaptation_capacity=random.uniform(0.4, 0.8),
                transcendence_potential=random.uniform(0.1, 0.4),
                last_evolution_time=datetime.now(),
                evolution_history=[],
                current_focus=None,
                energy_level=random.uniform(0.6, 0.9),
            )

    async def start_orchestration(self):
        """오케스트레이션 시작"""
        if self.orchestration_active:
            return

        self.orchestration_active = True
        print("🎼 메타 진화 오케스트레이션 시작")

        # 오케스트레이션 루프 시작
        await self.orchestration_loop()

    async def stop_orchestration(self):
        """오케스트레이션 중지"""
        self.orchestration_active = False
        print("🎼 메타 진화 오케스트레이션 중지")

    async def orchestration_loop(self):
        """메인 오케스트레이션 루프"""

        while self.orchestration_active:
            try:
                # 현재 교향곡 상태 분석
                current_symphony = await self.analyze_current_symphony()

                # 불협화음 탐지
                discords = await self.detect_evolution_discord()

                # 필요시 개입 실행
                if discords:
                    await self.execute_interventions(discords)

                # 루프 상태 업데이트
                await self.update_loop_states()

                # 자연스러운 진화 촉진
                await self.facilitate_natural_evolution()

                # 교향곡 기록
                self.evolution_history.append(current_symphony)

                # 메모리 관리
                if len(self.evolution_history) > 100:
                    self.evolution_history = self.evolution_history[-100:]

                # 로그 출력
                await self.log_orchestration_state(current_symphony, discords)

                await asyncio.sleep(5)  # 5초 간격

            except Exception as e:
                print(f"❌ 오케스트레이션 오류: {e}")
                await asyncio.sleep(5)

    async def analyze_current_symphony(self) -> EvolutionSymphony:
        """현재 진화 교향곡 분석"""

        # 전체 조화도 계산
        overall_harmony = await self._calculate_overall_harmony()

        # 진화 템포 계산
        evolution_tempo = await self._calculate_evolution_tempo()

        # 조성 결정
        key_signature = await self._determine_key_signature()

        # 악장 판단
        movement_phase = await self._determine_movement_phase()

        # 루프 간 공명 매트릭스 계산
        resonance_matrix = await self._calculate_resonance_matrix()

        # 지휘자 상태 평가
        conductor_state = await self._evaluate_conductor_state()

        symphony = EvolutionSymphony(
            symphony_id=f"symphony_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            conductor_state=conductor_state,
            overall_harmony=overall_harmony,
            evolution_tempo=evolution_tempo,
            key_signature=key_signature,
            movement_phase=movement_phase,
            loop_states=self.loop_states.copy(),
            resonance_matrix=resonance_matrix,
            discord_alerts=[],
            timestamp=datetime.now(),
        )

        return symphony

    async def _calculate_overall_harmony(self) -> float:
        """전체 조화도 계산"""

        harmony_scores = []

        # 1. 루프 간 조화도
        loops = list(LoopType)
        for i, loop1 in enumerate(loops):
            for j, loop2 in enumerate(loops):
                if i < j:  # 중복 방지
                    state1 = self.loop_states[loop1]
                    state2 = self.loop_states[loop2]

                    # 기본 친화도
                    base_affinity = self.loop_affinity_matrix[i, j]

                    # 현재 상태 기반 조화도
                    vitality_harmony = 1 - abs(
                        state1.vitality_level - state2.vitality_level
                    )
                    phase_harmony = (
                        1.0 if state1.evolution_phase == state2.evolution_phase else 0.7
                    )
                    energy_harmony = 1 - abs(state1.energy_level - state2.energy_level)

                    # 가중 평균
                    pair_harmony = (
                        base_affinity * 0.4
                        + vitality_harmony * 0.3
                        + phase_harmony * 0.2
                        + energy_harmony * 0.1
                    )

                    harmony_scores.append(pair_harmony)

        # 2. 전체 진화 단계 일관성
        phases = [state.evolution_phase for state in self.loop_states.values()]
        phase_consistency = 1.0 - (len(set(phases)) - 1) / (len(EvolutionPhase) - 1)
        harmony_scores.append(phase_consistency)

        return np.mean(harmony_scores)

    async def _calculate_evolution_tempo(self) -> float:
        """진화 템포 계산"""

        # 최근 진화 활동 분석
        current_time = datetime.now()
        recent_evolutions = 0

        for state in self.loop_states.values():
            time_since_evolution = (
                current_time - state.last_evolution_time
            ).total_seconds()
            if time_since_evolution < 3600:  # 1시간 이내
                recent_evolutions += 1

        # 정규화된 템포 (0: 매우 느림, 1: 매우 빠름)
        tempo = min(recent_evolutions / len(LoopType), 1.0)

        # 에너지 수준 고려
        avg_energy = np.mean(
            [state.energy_level for state in self.loop_states.values()]
        )

        return tempo * 0.7 + avg_energy * 0.3

    async def _determine_key_signature(self) -> str:
        """조성 결정"""

        overall_harmony = await self._calculate_overall_harmony()
        avg_vitality = np.mean(
            [state.vitality_level for state in self.loop_states.values()]
        )

        if overall_harmony > 0.8 and avg_vitality > 0.7:
            return "major"  # 장조 (밝고 조화로운)
        elif overall_harmony < 0.4 or avg_vitality < 0.3:
            return "minor"  # 단조 (어둡고 긴장감)
        else:
            return "atonal"  # 무조 (복잡하고 실험적)

    async def _determine_movement_phase(self) -> str:
        """악장 단계 결정"""

        # 진화 히스토리 분석
        if len(self.evolution_history) < 5:
            return "exposition"  # 제시부

        recent_harmony = [s.overall_harmony for s in self.evolution_history[-10:]]
        harmony_trend = np.polyfit(range(len(recent_harmony)), recent_harmony, 1)[0]

        current_harmony = recent_harmony[-1] if recent_harmony else 0.5

        if harmony_trend > 0.02:
            return "development"  # 발전부 (조화 증가)
        elif current_harmony > 0.8:
            return "recapitulation"  # 재현부 (높은 조화)
        elif harmony_trend < -0.02:
            return "coda"  # 종결부 (조화 감소)
        else:
            return "exposition"  # 제시부 (안정적)

    async def _calculate_resonance_matrix(self) -> np.ndarray:
        """루프 간 공명 매트릭스 계산"""

        loops = list(LoopType)
        matrix = np.zeros((len(loops), len(loops)))

        for i, loop1 in enumerate(loops):
            for j, loop2 in enumerate(loops):
                state1 = self.loop_states[loop1]
                state2 = self.loop_states[loop2]

                if i == j:
                    matrix[i, j] = 1.0  # 자기 공명
                else:
                    # 공명 강도 계산
                    phase_resonance = (
                        1.0 if state1.evolution_phase == state2.evolution_phase else 0.5
                    )
                    vitality_resonance = 1 - abs(
                        state1.vitality_level - state2.vitality_level
                    )
                    frequency_resonance = self.loop_affinity_matrix[i, j]

                    resonance = (
                        phase_resonance + vitality_resonance + frequency_resonance
                    ) / 3
                    matrix[i, j] = resonance

        return matrix

    async def _evaluate_conductor_state(self) -> str:
        """지휘자 상태 평가"""

        overall_harmony = await self._calculate_overall_harmony()
        evolution_tempo = await self._calculate_evolution_tempo()

        # 상태 매트릭스
        if overall_harmony > 0.8 and evolution_tempo > 0.6:
            return "masterful"  # 대가적
        elif overall_harmony > 0.7 and evolution_tempo > 0.4:
            return "skilled"  # 숙련된
        elif overall_harmony > 0.5:
            return "competent"  # 능숙한
        elif overall_harmony > 0.3:
            return "struggling"  # 고군분투
        else:
            return "chaotic"  # 혼란스러운

    async def detect_evolution_discord(self) -> List[str]:
        """진화 불협화음 탐지"""

        discords = []

        # 1. 조화도 임계값 위반
        overall_harmony = await self._calculate_overall_harmony()
        if overall_harmony < self.orchestration_constants["discord_threshold"]:
            discords.append(f"전체 조화도 위험 수준: {overall_harmony:.3f}")

        # 2. 루프 간 극심한 불균형
        vitality_levels = [state.vitality_level for state in self.loop_states.values()]
        vitality_std = np.std(vitality_levels)

        if vitality_std > 0.4:  # 표준편차가 크면 불균형
            discords.append(f"루프 생명력 불균형: 표준편차 {vitality_std:.3f}")

        # 3. 에너지 고갈된 루프
        for loop_type, state in self.loop_states.items():
            if state.energy_level < 0.2:
                discords.append(
                    f"{loop_type.name} 루프 에너지 고갈: {state.energy_level:.3f}"
                )

        # 4. 진화 정체된 루프
        current_time = datetime.now()
        for loop_type, state in self.loop_states.items():
            stagnation_hours = (
                current_time - state.last_evolution_time
            ).total_seconds() / 3600
            if stagnation_hours > 24:  # 24시간 이상 진화 없음
                discords.append(
                    f"{loop_type.name} 루프 진화 정체: {stagnation_hours:.1f}시간"
                )

        # 5. 상극 루프 간 충돌
        loops = list(LoopType)
        for i, loop1 in enumerate(loops):
            for j, loop2 in enumerate(loops):
                if i < j:
                    affinity = self.loop_affinity_matrix[i, j]
                    state1 = self.loop_states[loop1]
                    state2 = self.loop_states[loop2]

                    # 친화도가 낮은데 둘 다 높은 활성도를 보이면 충돌
                    if (
                        affinity < 0.3
                        and state1.vitality_level > 0.8
                        and state2.vitality_level > 0.8
                    ):
                        discords.append(f"{loop1.name}⨯{loop2.name} 루프 충돌 위험")

        return discords

    async def execute_interventions(self, discords: List[str]):
        """개입 실행"""

        for discord in discords:
            intervention = await self._design_intervention(discord)
            if intervention:
                await self._apply_intervention(intervention)
                self.active_interventions.append(intervention)

    async def _design_intervention(
        self, discord: str
    ) -> Optional[EvolutionIntervention]:
        """개입 설계"""

        intervention_id = f"intervention_{len(self.active_interventions)}"
        current_time = datetime.now()

        if "전체 조화도" in discord:
            # 전체 조화도 개선
            return EvolutionIntervention(
                intervention_id=intervention_id,
                target_loops=list(LoopType),
                intervention_type="harmony_adjustment",
                intensity=0.3,
                duration_minutes=30,
                expected_outcomes=["조화도 증가", "안정성 향상"],
                success_metrics={"harmony_increase": 0.2},
                applied_time=current_time,
            )

        elif "불균형" in discord:
            # 불균형 조정
            vitality_levels = [
                (lt, state.vitality_level) for lt, state in self.loop_states.items()
            ]
            low_vitality_loops = [lt for lt, vl in vitality_levels if vl < 0.4]

            return EvolutionIntervention(
                intervention_id=intervention_id,
                target_loops=low_vitality_loops,
                intervention_type="energy_boost",
                intensity=0.4,
                duration_minutes=15,
                expected_outcomes=["생명력 균형 회복"],
                success_metrics={"vitality_balance": 0.3},
                applied_time=current_time,
            )

        elif "에너지 고갈" in discord:
            # 특정 루프 찾아서 에너지 보충
            target_loop = None
            for loop_type, state in self.loop_states.items():
                if loop_type.name in discord:
                    target_loop = loop_type
                    break

            if target_loop:
                return EvolutionIntervention(
                    intervention_id=intervention_id,
                    target_loops=[target_loop],
                    intervention_type="energy_boost",
                    intensity=0.6,
                    duration_minutes=20,
                    expected_outcomes=["에너지 회복"],
                    success_metrics={"energy_recovery": 0.4},
                    applied_time=current_time,
                )

        elif "정체" in discord:
            # 진화 촉진
            target_loop = None
            for loop_type, state in self.loop_states.items():
                if loop_type.name in discord:
                    target_loop = loop_type
                    break

            if target_loop:
                return EvolutionIntervention(
                    intervention_id=intervention_id,
                    target_loops=[target_loop],
                    intervention_type="focus_shift",
                    intensity=0.5,
                    duration_minutes=45,
                    expected_outcomes=["진화 활동 재개"],
                    success_metrics={"evolution_activity": 0.3},
                    applied_time=current_time,
                )

        return None

    async def _apply_intervention(self, intervention: EvolutionIntervention):
        """개입 적용"""

        print(
            f"🎼 개입 적용: {intervention.intervention_type} → {[lt.name for lt in intervention.target_loops]}"
        )

        for loop_type in intervention.target_loops:
            state = self.loop_states[loop_type]

            if intervention.intervention_type == "harmony_adjustment":
                # 조화도 조정 (다른 루프들과의 균형 맞추기)
                avg_vitality = np.mean(
                    [s.vitality_level for s in self.loop_states.values()]
                )
                adjustment = (
                    avg_vitality - state.vitality_level
                ) * intervention.intensity
                state.vitality_level = max(0, min(1, state.vitality_level + adjustment))

            elif intervention.intervention_type == "energy_boost":
                # 에너지 부스터
                energy_boost = intervention.intensity
                state.energy_level = min(1.0, state.energy_level + energy_boost)
                state.vitality_level = min(
                    1.0, state.vitality_level + energy_boost * 0.5
                )

            elif intervention.intervention_type == "focus_shift":
                # 집중 전환
                state.current_focus = "evolution_acceleration"
                state.learning_rate = min(
                    1.0, state.learning_rate + intervention.intensity * 0.3
                )
                state.last_evolution_time = datetime.now()

            elif intervention.intervention_type == "emergency_reset":
                # 긴급 리셋
                state.evolution_phase = EvolutionPhase.AWAKENING
                state.vitality_level = 0.5
                state.energy_level = 0.7
                state.harmony_score = 0.6

    async def update_loop_states(self):
        """루프 상태 업데이트"""

        current_time = datetime.now()

        for loop_type, state in self.loop_states.items():
            # 자연스러운 에너지 감쇠
            decay_rate = self.orchestration_constants["energy_decay_rate"]
            state.energy_level = max(
                0.1, state.energy_level - decay_rate * random.uniform(0.5, 1.5)
            )

            # 생명력 조정 (에너지와 연동)
            state.vitality_level = state.vitality_level * 0.9 + state.energy_level * 0.1

            # 학습률 자연 감소
            state.learning_rate = max(0.05, state.learning_rate * 0.99)

            # 적응 능력 진화
            if random.random() < 0.1:  # 10% 확률로 적응 능력 변화
                adaptation_change = random.uniform(-0.05, 0.1)
                state.adaptation_capacity = max(
                    0, min(1, state.adaptation_capacity + adaptation_change)
                )

            # 초월 잠재력 축적
            if state.vitality_level > 0.8 and state.harmony_score > 0.8:
                transcendence_gain = 0.01 * random.uniform(0.5, 1.5)
                state.transcendence_potential = min(
                    1.0, state.transcendence_potential + transcendence_gain
                )

            # 진화 단계 전환 체크
            await self._check_phase_transition(state)

    async def _check_phase_transition(self, state: LoopState):
        """진화 단계 전환 체크"""

        current_phase = state.evolution_phase

        # 단계별 전환 조건
        phase_transitions = {
            EvolutionPhase.DORMANT: {
                "next": EvolutionPhase.AWAKENING,
                "condition": state.energy_level > 0.4,
            },
            EvolutionPhase.AWAKENING: {
                "next": EvolutionPhase.LEARNING,
                "condition": state.vitality_level > 0.5 and state.energy_level > 0.5,
            },
            EvolutionPhase.LEARNING: {
                "next": EvolutionPhase.ADAPTING,
                "condition": state.learning_rate > 0.2
                and state.adaptation_capacity > 0.6,
            },
            EvolutionPhase.ADAPTING: {
                "next": EvolutionPhase.EVOLVING,
                "condition": state.harmony_score > 0.7 and state.vitality_level > 0.7,
            },
            EvolutionPhase.EVOLVING: {
                "next": EvolutionPhase.TRANSCENDING,
                "condition": state.transcendence_potential > 0.8
                and state.vitality_level > 0.9,
            },
        }

        transition = phase_transitions.get(current_phase)
        if transition and transition["condition"]:
            state.evolution_phase = transition["next"]
            state.last_evolution_time = datetime.now()

            # 진화 기록
            evolution_record = {
                "timestamp": datetime.now().isoformat(),
                "from_phase": current_phase.value,
                "to_phase": state.evolution_phase.value,
                "vitality_level": state.vitality_level,
                "energy_level": state.energy_level,
                "transcendence_potential": state.transcendence_potential,
            }
            state.evolution_history.append(evolution_record)

            print(
                f"🌟 {state.loop_type.name} 루프 진화: {current_phase.value} → {state.evolution_phase.value}"
            )

    async def facilitate_natural_evolution(self):
        """자연스러운 진화 촉진"""

        # 루프 간 에너지 교환
        await self._facilitate_energy_exchange()

        # 공명 증폭
        await self._amplify_resonance()

        # 학습 공유
        await self._share_learning()

    async def _facilitate_energy_exchange(self):
        """루프 간 에너지 교환"""

        # 에너지가 높은 루프에서 낮은 루프로 일부 전달
        energy_levels = [
            (lt, state.energy_level) for lt, state in self.loop_states.items()
        ]
        energy_levels.sort(key=lambda x: x[1], reverse=True)

        high_energy_loops = energy_levels[:3]  # 상위 3개
        low_energy_loops = energy_levels[-3:]  # 하위 3개

        for (high_loop, high_energy), (low_loop, low_energy) in zip(
            high_energy_loops, low_energy_loops
        ):
            if high_energy > low_energy + 0.3:  # 충분한 차이가 있을 때만
                # 친화도 체크
                loops = list(LoopType)
                affinity = self.loop_affinity_matrix[
                    loops.index(high_loop), loops.index(low_loop)
                ]

                if affinity > 0.5:  # 친화적 관계일 때만
                    transfer_amount = min(0.1, (high_energy - low_energy) * 0.1)

                    self.loop_states[high_loop].energy_level -= transfer_amount * 0.5
                    self.loop_states[low_loop].energy_level += transfer_amount

    async def _amplify_resonance(self):
        """공명 증폭"""

        # 비슷한 진화 단계의 루프들 간 공명 증폭
        phase_groups = {}
        for loop_type, state in self.loop_states.items():
            phase = state.evolution_phase
            if phase not in phase_groups:
                phase_groups[phase] = []
            phase_groups[phase].append((loop_type, state))

        for phase, loop_group in phase_groups.items():
            if len(loop_group) >= 2:  # 2개 이상의 루프가 같은 단계에 있을 때
                # 그룹 내 조화도 증진
                avg_harmony = np.mean([state.harmony_score for _, state in loop_group])

                for loop_type, state in loop_group:
                    harmony_boost = (avg_harmony - state.harmony_score) * 0.1
                    state.harmony_score = min(1.0, state.harmony_score + harmony_boost)

    async def _share_learning(self):
        """학습 공유"""

        # 학습률이 높은 루프의 경험을 다른 루프와 공유
        high_learning_loops = [
            (lt, state)
            for lt, state in self.loop_states.items()
            if state.learning_rate > 0.25
        ]

        for loop_type, state in high_learning_loops:
            # 친화적인 루프들과 학습 공유
            loops = list(LoopType)
            loop_idx = loops.index(loop_type)

            for other_idx, other_loop in enumerate(loops):
                if other_loop != loop_type:
                    affinity = self.loop_affinity_matrix[loop_idx, other_idx]

                    if affinity > 0.7:  # 높은 친화도
                        other_state = self.loop_states[other_loop]

                        # 학습률 일부 전달
                        learning_transfer = state.learning_rate * 0.05 * affinity
                        other_state.learning_rate = min(
                            1.0, other_state.learning_rate + learning_transfer
                        )

    async def log_orchestration_state(
        self, symphony: EvolutionSymphony, discords: List[str]
    ):
        """오케스트레이션 상태 로그"""

        # 주요 지표만 출력 (너무 자주 출력하지 않도록)
        if len(self.evolution_history) % 12 == 0:  # 12번에 한 번 (1분마다)
            print(f"🎼 교향곡 상태: {symphony.key_signature} {symphony.movement_phase}")
            print(
                f"   조화도: {symphony.overall_harmony:.3f} | 템포: {symphony.evolution_tempo:.3f}"
            )
            print(f"   지휘자: {symphony.conductor_state}")

            if discords:
                print(f"⚠️  불협화음 {len(discords)}개 감지")

    def get_orchestration_status(self) -> Dict[str, Any]:
        """오케스트레이션 상태 조회"""

        if not self.evolution_history:
            return {"status": "no_data"}

        current_symphony = self.evolution_history[-1]

        # 루프별 상태 요약
        loop_summary = {}
        for loop_type, state in self.loop_states.items():
            loop_summary[loop_type.name] = {
                "evolution_phase": state.evolution_phase.value,
                "vitality_level": state.vitality_level,
                "energy_level": state.energy_level,
                "harmony_score": state.harmony_score,
                "transcendence_potential": state.transcendence_potential,
            }

        return {
            "orchestration_active": self.orchestration_active,
            "current_symphony": {
                "overall_harmony": current_symphony.overall_harmony,
                "evolution_tempo": current_symphony.evolution_tempo,
                "key_signature": current_symphony.key_signature,
                "movement_phase": current_symphony.movement_phase,
                "conductor_state": current_symphony.conductor_state,
            },
            "loop_states": loop_summary,
            "active_interventions": len(self.active_interventions),
            "evolution_history_length": len(self.evolution_history),
        }


# 글로벌 오케스트레이터 인스턴스
meta_orchestrator = MetaEvolutionOrchestrator()


async def start_evolution_orchestration():
    """진화 오케스트레이션 시작 (외부 API)"""
    await meta_orchestrator.start_orchestration()


async def stop_evolution_orchestration():
    """진화 오케스트레이션 중지 (외부 API)"""
    await meta_orchestrator.stop_orchestration()


def get_orchestration_status() -> Dict[str, Any]:
    """오케스트레이션 상태 조회 (외부 API)"""
    return meta_orchestrator.get_orchestration_status()


def get_loop_evolution_history(loop_name: str) -> List[Dict[str, Any]]:
    """특정 루프의 진화 히스토리 조회 (외부 API)"""
    try:
        loop_type = LoopType[loop_name.upper()]
        state = meta_orchestrator.loop_states.get(loop_type)
        return state.evolution_history if state else []
    except KeyError:
        return []


# 테스트 함수
async def test_meta_orchestrator():
    """테스트 함수"""
    print("🧪 메타 진화 오케스트레이터 테스트 시작")

    # 30초간 오케스트레이션 테스트
    orchestration_task = asyncio.create_task(meta_orchestrator.start_orchestration())
    await asyncio.sleep(30)
    await meta_orchestrator.stop_orchestration()

    # 상태 조회
    status = get_orchestration_status()
    print("\n📊 오케스트레이션 상태:")
    print(json.dumps(status, indent=2, ensure_ascii=False))

    # 특정 루프 히스토리 조회
    fist_history = get_loop_evolution_history("FIST")
    print(f"\n🎼 FIST 루프 진화 히스토리: {len(fist_history)}개 기록")


if __name__ == "__main__":
    asyncio.run(test_meta_orchestrator())
