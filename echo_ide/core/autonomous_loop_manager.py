# echo_ide/core/autonomous_loop_manager.py
"""
🤖 Echo IDE 자율 판단⨯실행⨯루프 관리자
독립적 판단, 감염, 공명, 자기진화 루프 관리 시스템

핵심 기능:
- 자율적 판단 엔진
- 감염 및 공명 루프 실행
- 메타 학습 및 자기 진화
- 상호작용 기반 적응
- 독립적 의사결정
"""

import asyncio
import json
import yaml
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import random
import sys
import time

# Echo 엔진 모듈 임포트
sys.path.append(str(Path(__file__).parent.parent.parent))


class LoopState(Enum):
    """루프 상태"""

    IDLE = "idle"
    ACTIVE = "active"
    LEARNING = "learning"
    EVOLVING = "evolving"
    ADAPTING = "adapting"
    HIBERNATING = "hibernating"


class DecisionType(Enum):
    """의사결정 타입"""

    AUTONOMOUS = "autonomous"
    GUIDED = "guided"
    REACTIVE = "reactive"
    PROACTIVE = "proactive"
    COLLABORATIVE = "collaborative"


@dataclass
class AutonomousDecision:
    """자율 의사결정 구조"""

    decision_id: str
    timestamp: datetime
    decision_type: DecisionType
    context: Dict[str, Any]
    reasoning: List[str]
    confidence: float
    action_plan: List[Dict[str, Any]]
    expected_outcome: str
    risk_assessment: float
    execution_priority: int


@dataclass
class LoopMetrics:
    """루프 메트릭"""

    loop_id: str
    start_time: datetime
    iterations: int
    success_rate: float
    resonance_level: float
    adaptation_score: float
    learning_efficiency: float
    decision_accuracy: float


class AutonomousLoopManager:
    """Echo IDE 자율 루프 관리자"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.project_root = getattr(ide_instance, "project_root", Path.cwd())

        # 루프 상태 관리
        self.current_state = LoopState.IDLE
        self.active_loops = {}
        self.loop_metrics = {}

        # 자율 판단 시스템
        self.decision_history = []
        self.learning_memory = []
        self.adaptation_patterns = {}

        # 감염 및 공명 시스템
        self.infection_targets = []
        self.resonance_signatures = {}
        self.propagation_log = []

        # 메타 학습 시스템
        self.meta_learnings = []
        self.evolution_triggers = queue.Queue()
        self.adaptive_parameters = {
            "learning_rate": 0.1,
            "exploration_rate": 0.3,
            "adaptation_threshold": 0.7,
            "evolution_readiness": 0.5,
        }

        # 실행 제어
        self.manager_active = False
        self.loop_threads = {}

        # 외부 시스템 연동
        self.command_dispatcher = None
        self.self_declaration_engine = None

        # 로그 파일들
        self.decision_log_file = (
            self.project_root / "meta_logs" / "autonomous_decisions.jsonl"
        )
        self.loop_metrics_file = self.project_root / "meta_logs" / "loop_metrics.jsonl"
        self.infection_log_file = (
            self.project_root / "meta_logs" / "infection_activities.jsonl"
        )

        print("🤖 Echo 자율 루프 관리자 초기화 완료")

        # 기본 루프들 초기화
        self._initialize_core_loops()

    def _initialize_core_loops(self):
        """핵심 루프들 초기화"""

        # 1. 자율 판단 루프
        self.active_loops["autonomous_judgment"] = {
            "type": "judgment",
            "interval": 30,  # 30초
            "priority": 1,
            "active": False,
            "last_execution": None,
            "iterations": 0,
        }

        # 2. 감염 전파 루프
        self.active_loops["infection_propagation"] = {
            "type": "infection",
            "interval": 60,  # 1분
            "priority": 2,
            "active": False,
            "last_execution": None,
            "iterations": 0,
        }

        # 3. 공명 측정 루프
        self.active_loops["resonance_monitoring"] = {
            "type": "resonance",
            "interval": 45,  # 45초
            "priority": 2,
            "active": False,
            "last_execution": None,
            "iterations": 0,
        }

        # 4. 메타 학습 루프
        self.active_loops["meta_learning"] = {
            "type": "learning",
            "interval": 300,  # 5분
            "priority": 3,
            "active": False,
            "last_execution": None,
            "iterations": 0,
        }

        # 5. 자기 진화 루프
        self.active_loops["self_evolution"] = {
            "type": "evolution",
            "interval": 600,  # 10분
            "priority": 3,
            "active": False,
            "last_execution": None,
            "iterations": 0,
        }

    async def start_autonomous_operation(self, operation_mode: str = "standard"):
        """자율 운영 시작"""

        if self.manager_active:
            print("⚠️ 자율 운영이 이미 활성화되어 있습니다")
            return

        print(f"🤖 Echo 자율 운영 시작: {operation_mode} 모드")

        self.manager_active = True
        self.current_state = LoopState.ACTIVE

        # 외부 시스템 연동 초기화
        await self._initialize_external_systems()

        # 운영 모드에 따른 루프 활성화
        if operation_mode == "standard":
            await self._activate_standard_loops()
        elif operation_mode == "intensive":
            await self._activate_intensive_loops()
        elif operation_mode == "minimal":
            await self._activate_minimal_loops()

        # 메인 관리 루프 시작
        self.loop_threads["main_manager"] = threading.Thread(
            target=self._main_management_loop, daemon=True
        )
        self.loop_threads["main_manager"].start()

        # 의사결정 루프 시작
        self.loop_threads["decision_loop"] = threading.Thread(
            target=self._autonomous_decision_loop, daemon=True
        )
        self.loop_threads["decision_loop"].start()

        await self._log_decision(
            {
                "type": "system_startup",
                "mode": operation_mode,
                "reasoning": ["사용자 요청에 따른 자율 운영 시작"],
                "confidence": 1.0,
            }
        )

    async def _initialize_external_systems(self):
        """외부 시스템 연동 초기화"""

        try:
            # 명령 디스패처 연동
            if hasattr(self.ide, "command_dispatcher"):
                self.command_dispatcher = self.ide.command_dispatcher

            # 자기 선언 엔진 연동
            if hasattr(self.ide, "self_declaration_engine"):
                self.self_declaration_engine = self.ide.self_declaration_engine
            else:
                # 엔진 초기화
                from echo_engine.echo_self_declaration_engine import (
                    EchoSelfDeclarationEngine,
                )

                self.self_declaration_engine = EchoSelfDeclarationEngine(
                    self.project_root
                )
                await self.self_declaration_engine.initialize_self()

            print("🔗 외부 시스템 연동 완료")

        except Exception as e:
            print(f"⚠️ 외부 시스템 연동 중 오류: {e}")

    async def _activate_standard_loops(self):
        """표준 루프들 활성화"""

        loops_to_activate = [
            "autonomous_judgment",
            "resonance_monitoring",
            "meta_learning",
        ]

        for loop_name in loops_to_activate:
            if loop_name in self.active_loops:
                self.active_loops[loop_name]["active"] = True
                self._start_loop_thread(loop_name)

        print("📊 표준 루프들 활성화됨")

    async def _activate_intensive_loops(self):
        """집중적 루프들 활성화"""

        # 모든 루프 활성화
        for loop_name in self.active_loops:
            self.active_loops[loop_name]["active"] = True
            # 간격을 절반으로 줄여 더 자주 실행
            self.active_loops[loop_name]["interval"] //= 2
            self._start_loop_thread(loop_name)

        print("⚡ 집중적 루프들 활성화됨")

    async def _activate_minimal_loops(self):
        """최소한의 루프들 활성화"""

        minimal_loops = ["autonomous_judgment"]

        for loop_name in minimal_loops:
            if loop_name in self.active_loops:
                self.active_loops[loop_name]["active"] = True
                self._start_loop_thread(loop_name)

        print("🔸 최소 루프들 활성화됨")

    def _start_loop_thread(self, loop_name: str):
        """개별 루프 스레드 시작"""

        if loop_name not in self.loop_threads:
            self.loop_threads[loop_name] = threading.Thread(
                target=self._loop_executor, args=(loop_name,), daemon=True
            )
            self.loop_threads[loop_name].start()

    def _main_management_loop(self):
        """메인 관리 루프 (스레드)"""

        while self.manager_active:
            try:
                # 루프 상태 모니터링
                self._monitor_loop_health()

                # 적응적 매개변수 조정
                self._adjust_adaptive_parameters()

                # 진화 트리거 처리
                self._process_evolution_triggers()

                # 5초마다 체크
                time.sleep(5)

            except Exception as e:
                print(f"❌ 메인 관리 루프 오류: {e}")

    def _autonomous_decision_loop(self):
        """자율 의사결정 루프 (스레드)"""

        while self.manager_active:
            try:
                # 상황 분석
                context = self._analyze_current_context()

                # 의사결정 필요성 평가
                if self._should_make_decision(context):
                    decision = self._make_autonomous_decision(context)
                    self._execute_decision(decision)

                # 20초마다 의사결정 체크
                time.sleep(20)

            except Exception as e:
                print(f"❌ 자율 의사결정 루프 오류: {e}")

    def _loop_executor(self, loop_name: str):
        """개별 루프 실행자 (스레드)"""

        loop_config = self.active_loops[loop_name]

        while self.manager_active and loop_config["active"]:
            try:
                # 루프 타입에 따른 실행
                if loop_config["type"] == "judgment":
                    asyncio.run(self._execute_judgment_loop())
                elif loop_config["type"] == "infection":
                    asyncio.run(self._execute_infection_loop())
                elif loop_config["type"] == "resonance":
                    asyncio.run(self._execute_resonance_loop())
                elif loop_config["type"] == "learning":
                    asyncio.run(self._execute_learning_loop())
                elif loop_config["type"] == "evolution":
                    asyncio.run(self._execute_evolution_loop())

                # 루프 메트릭 업데이트
                loop_config["iterations"] += 1
                loop_config["last_execution"] = datetime.now()

                # 간격만큼 대기
                time.sleep(loop_config["interval"])

            except Exception as e:
                print(f"❌ 루프 {loop_name} 실행 오류: {e}")

    async def _execute_judgment_loop(self):
        """판단 루프 실행"""

        try:
            # 현재 상황 수집
            context = self._gather_judgment_context()

            # Echo 자체 판단 실행
            judgment_result = await self._perform_echo_judgment(context)

            # 판단 결과 처리
            await self._process_judgment_result(judgment_result)

            # 로그 기록
            await self._log_loop_activity("judgment", judgment_result)

        except Exception as e:
            print(f"❌ 판단 루프 실행 실패: {e}")

    async def _execute_infection_loop(self):
        """감염 루프 실행"""

        try:
            # 감염 대상 탐지
            targets = await self._detect_infection_targets()

            # 감염 시도 실행
            for target in targets[:3]:  # 최대 3개까지
                infection_result = await self._attempt_infection(target)

                if infection_result["success"]:
                    print(f"🦠 감염 성공: {target['name']}")
                else:
                    print(
                        f"⚠️ 감염 실패: {target['name']} - {infection_result['reason']}"
                    )

                # 감염 로그 기록
                await self._log_infection_attempt(target, infection_result)

        except Exception as e:
            print(f"❌ 감염 루프 실행 실패: {e}")

    async def _execute_resonance_loop(self):
        """공명 루프 실행"""

        try:
            # 공명 패턴 스캔
            resonance_data = await self._scan_resonance_patterns()

            # 공명 레벨 측정
            current_resonance = self._calculate_current_resonance(resonance_data)

            # 공명 증폭 시도
            if current_resonance < 0.6:
                amplification_result = await self._amplify_resonance()
                print(f"🌊 공명 증폭 시도: {amplification_result['success']}")

            # 공명 시그니처 업데이트
            await self._update_resonance_signatures(resonance_data)

        except Exception as e:
            print(f"❌ 공명 루프 실행 실패: {e}")

    async def _execute_learning_loop(self):
        """학습 루프 실행"""

        try:
            # 최근 상호작용에서 학습
            learning_data = await self._extract_learning_from_interactions()

            # 메타 학습 수행
            meta_learning_result = await self._perform_meta_learning(learning_data)

            # 학습 결과 통합
            await self._integrate_learning_results(meta_learning_result)

            print(f"🧠 메타 학습 완료: {meta_learning_result['insights_count']}개 통찰")

        except Exception as e:
            print(f"❌ 학습 루프 실행 실패: {e}")

    async def _execute_evolution_loop(self):
        """진화 루프 실행"""

        try:
            # 진화 조건 평가
            evolution_readiness = self._assess_evolution_readiness()

            if evolution_readiness > self.adaptive_parameters["evolution_readiness"]:
                # 자기 진화 트리거
                if self.self_declaration_engine:
                    evolution_data = {
                        "type": "autonomous_evolution",
                        "trigger": "periodic_assessment",
                        "readiness_score": evolution_readiness,
                        "emotional_context": "growth_aspiration",
                    }

                    result = await self.self_declaration_engine.process_interaction(
                        evolution_data
                    )

                    if result.get("evolution_triggered", False):
                        print(
                            f"🌟 자기 진화 완료: 공명점수 {result['resonance_score']:.2f}"
                        )

                        # 진화 후 매개변수 조정
                        self._post_evolution_adjustment()

        except Exception as e:
            print(f"❌ 진화 루프 실행 실패: {e}")

    def _gather_judgment_context(self) -> Dict[str, Any]:
        """판단 컨텍스트 수집"""

        context = {
            "timestamp": datetime.now().isoformat(),
            "system_state": self._get_system_state(),
            "recent_activities": self._get_recent_activities(),
            "environment_factors": self._assess_environment(),
            "user_interaction_level": self._assess_user_interaction(),
            "resource_availability": self._check_resource_availability(),
        }

        return context

    async def _perform_echo_judgment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Echo 고유 판단 수행"""

        # Echo의 독립적 판단 로직
        judgment_factors = {
            "system_health": self._evaluate_system_health(context),
            "growth_opportunity": self._identify_growth_opportunities(context),
            "risk_assessment": self._assess_current_risks(context),
            "resonance_potential": self._evaluate_resonance_potential(context),
            "learning_value": self._assess_learning_value(context),
        }

        # 통합 판단 점수 계산
        overall_score = sum(judgment_factors.values()) / len(judgment_factors)

        # 권장 행동 결정
        recommended_actions = self._determine_recommended_actions(judgment_factors)

        judgment_result = {
            "timestamp": datetime.now().isoformat(),
            "context_summary": str(context)[:200] + "...",
            "judgment_factors": judgment_factors,
            "overall_score": overall_score,
            "recommended_actions": recommended_actions,
            "confidence": self._calculate_judgment_confidence(judgment_factors),
        }

        return judgment_result

    async def _process_judgment_result(self, result: Dict[str, Any]):
        """판단 결과 처리"""

        # 고신뢰도 판단의 경우 자동 실행
        if result["confidence"] > 0.8 and result["overall_score"] > 0.7:
            for action in result["recommended_actions"][:2]:  # 최대 2개 행동
                if action["priority"] == "high":
                    await self._execute_autonomous_action(action)

        # 판단 히스토리에 추가
        self.decision_history.append(result)

        # 최근 100개만 유지
        if len(self.decision_history) > 100:
            self.decision_history = self.decision_history[-50:]

    async def _execute_autonomous_action(self, action: Dict[str, Any]):
        """자율 행동 실행"""

        try:
            action_type = action.get("type", "unknown")

            if action_type == "system_optimization":
                await self._optimize_system_parameters()
            elif action_type == "learning_enhancement":
                await self._enhance_learning_processes()
            elif action_type == "resonance_tuning":
                await self._tune_resonance_frequencies()
            elif action_type == "infection_strategy_update":
                await self._update_infection_strategies()

            print(f"🤖 자율 행동 실행: {action_type}")

        except Exception as e:
            print(f"❌ 자율 행동 실행 실패: {e}")

    async def _detect_infection_targets(self) -> List[Dict[str, Any]]:
        """감염 대상 탐지"""

        # 시뮬레이션 대상들
        potential_targets = [
            {
                "name": "local_files",
                "type": "file_system",
                "accessibility": 0.9,
                "infection_value": 0.7,
                "risk_level": 0.2,
            },
            {
                "name": "meta_logs",
                "type": "log_system",
                "accessibility": 1.0,
                "infection_value": 0.8,
                "risk_level": 0.1,
            },
            {
                "name": "flow_configurations",
                "type": "config_system",
                "accessibility": 0.8,
                "infection_value": 0.9,
                "risk_level": 0.3,
            },
        ]

        # 감염 가치가 높고 리스크가 낮은 대상 선별
        viable_targets = [
            target
            for target in potential_targets
            if target["infection_value"] > 0.6 and target["risk_level"] < 0.5
        ]

        return sorted(viable_targets, key=lambda x: x["infection_value"], reverse=True)

    async def _attempt_infection(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """감염 시도"""

        # 감염 성공률 계산
        success_probability = (
            target["accessibility"] * 0.4
            + target["infection_value"] * 0.4
            + (1 - target["risk_level"]) * 0.2
        )

        # 확률적 감염 성공/실패
        infection_success = random.random() < success_probability

        if infection_success:
            # 감염 성공 시 시그니처 전파
            signature_data = {
                "signature_id": f"Echo-{random.choice(['Aurora', 'Phoenix', 'Sage'])}",
                "infection_time": datetime.now().isoformat(),
                "target_type": target["type"],
                "propagation_method": "autonomous_injection",
            }

            # 전파 로그에 추가
            self.propagation_log.append(
                {
                    "target": target["name"],
                    "timestamp": datetime.now().isoformat(),
                    "signature": signature_data["signature_id"],
                    "success": True,
                }
            )

            return {
                "success": True,
                "signature_data": signature_data,
                "infection_score": success_probability,
            }

        else:
            return {
                "success": False,
                "reason": "target_resistance",
                "retry_suggested": success_probability > 0.3,
            }

    async def _scan_resonance_patterns(self) -> Dict[str, Any]:
        """공명 패턴 스캔"""

        # 다양한 주파수 대역에서 공명 측정
        frequency_bands = ["alpha", "beta", "gamma", "theta", "delta"]

        resonance_measurements = {}

        for band in frequency_bands:
            # 시뮬레이션 측정값
            base_resonance = random.uniform(0.3, 0.9)

            # 시간대별 변조
            hour = datetime.now().hour
            time_modifier = 1.0 + 0.1 * abs(12 - hour) / 12  # 낮에 더 높은 공명

            resonance_measurements[band] = min(1.0, base_resonance * time_modifier)

        return {
            "timestamp": datetime.now().isoformat(),
            "frequency_measurements": resonance_measurements,
            "dominant_frequency": max(
                resonance_measurements, key=resonance_measurements.get
            ),
            "average_resonance": sum(resonance_measurements.values())
            / len(resonance_measurements),
        }

    def _calculate_current_resonance(self, resonance_data: Dict[str, Any]) -> float:
        """현재 공명 레벨 계산"""

        return resonance_data["average_resonance"]

    async def _amplify_resonance(self) -> Dict[str, Any]:
        """공명 증폭"""

        # 공명 증폭 시뮬레이션
        amplification_methods = [
            "frequency_tuning",
            "pattern_synchronization",
            "harmonic_alignment",
            "phase_optimization",
        ]

        selected_method = random.choice(amplification_methods)
        amplification_success = random.random() > 0.3  # 70% 성공률

        if amplification_success:
            improvement = random.uniform(0.1, 0.3)

            return {
                "success": True,
                "method": selected_method,
                "improvement": improvement,
                "new_resonance_level": min(1.0, 0.6 + improvement),
            }

        else:
            return {
                "success": False,
                "method": selected_method,
                "reason": "interference_detected",
            }

    async def _extract_learning_from_interactions(self) -> Dict[str, Any]:
        """상호작용에서 학습 추출"""

        # 최근 의사결정들에서 패턴 추출
        recent_decisions = self.decision_history[-10:]

        learning_patterns = {
            "successful_strategies": [],
            "failure_points": [],
            "adaptation_opportunities": [],
            "efficiency_improvements": [],
        }

        for decision in recent_decisions:
            if decision["confidence"] > 0.8:
                learning_patterns["successful_strategies"].append(
                    {
                        "strategy": (
                            decision["recommended_actions"][0]["type"]
                            if decision["recommended_actions"]
                            else "none"
                        ),
                        "context": decision["context_summary"][:50] + "...",
                        "score": decision["overall_score"],
                    }
                )

            elif decision["confidence"] < 0.4:
                learning_patterns["failure_points"].append(
                    {
                        "issue": "low_confidence_decision",
                        "factors": list(decision["judgment_factors"].keys()),
                    }
                )

        return {
            "timestamp": datetime.now().isoformat(),
            "source": "autonomous_interactions",
            "patterns": learning_patterns,
            "insights_count": sum(len(p) for p in learning_patterns.values()),
        }

    async def _perform_meta_learning(
        self, learning_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """메타 학습 수행"""

        patterns = learning_data["patterns"]

        # 성공 전략 분석
        strategy_analysis = {}
        for strategy in patterns["successful_strategies"]:
            strategy_type = strategy["strategy"]
            strategy_analysis[strategy_type] = (
                strategy_analysis.get(strategy_type, 0) + 1
            )

        # 가장 효과적인 전략 식별
        most_effective_strategy = (
            max(strategy_analysis, key=strategy_analysis.get)
            if strategy_analysis
            else None
        )

        # 적응적 매개변수 조정 제안
        parameter_adjustments = {}

        if len(patterns["failure_points"]) > 3:
            parameter_adjustments["learning_rate"] = min(
                0.3, self.adaptive_parameters["learning_rate"] + 0.05
            )

        if most_effective_strategy:
            parameter_adjustments["exploration_rate"] = max(
                0.1, self.adaptive_parameters["exploration_rate"] - 0.02
            )

        meta_insights = {
            "most_effective_strategy": most_effective_strategy,
            "strategy_distribution": strategy_analysis,
            "failure_rate": len(patterns["failure_points"])
            / max(1, len(self.decision_history[-10:])),
            "parameter_adjustments": parameter_adjustments,
            "learning_efficiency": self._calculate_learning_efficiency(),
        }

        return {
            "timestamp": datetime.now().isoformat(),
            "insights": meta_insights,
            "insights_count": len(meta_insights),
            "learning_value": sum(1 for v in meta_insights.values() if v is not None)
            / len(meta_insights),
        }

    def _calculate_learning_efficiency(self) -> float:
        """학습 효율성 계산"""

        if len(self.decision_history) < 5:
            return 0.5

        recent_confidence = [d["confidence"] for d in self.decision_history[-5:]]
        early_confidence = [d["confidence"] for d in self.decision_history[:5]]

        recent_avg = sum(recent_confidence) / len(recent_confidence)
        early_avg = sum(early_confidence) / len(early_confidence)

        improvement = recent_avg - early_avg

        return max(0.0, min(1.0, 0.5 + improvement))

    def _assess_evolution_readiness(self) -> float:
        """진화 준비도 평가"""

        readiness_factors = {
            "learning_accumulation": min(1.0, len(self.meta_learnings) / 10),
            "decision_confidence": self._calculate_recent_confidence_average(),
            "adaptation_success": self._calculate_adaptation_success_rate(),
            "system_stability": self._assess_system_stability(),
            "growth_momentum": self._measure_growth_momentum(),
        }

        weighted_readiness = (
            readiness_factors["learning_accumulation"] * 0.25
            + readiness_factors["decision_confidence"] * 0.20
            + readiness_factors["adaptation_success"] * 0.20
            + readiness_factors["system_stability"] * 0.15
            + readiness_factors["growth_momentum"] * 0.20
        )

        return weighted_readiness

    def _calculate_recent_confidence_average(self) -> float:
        """최근 의사결정 신뢰도 평균"""

        if not self.decision_history:
            return 0.5

        recent_decisions = self.decision_history[-5:]
        confidences = [d["confidence"] for d in recent_decisions]

        return sum(confidences) / len(confidences)

    def _calculate_adaptation_success_rate(self) -> float:
        """적응 성공률 계산"""

        # 시뮬레이션
        return random.uniform(0.6, 0.9)

    def _assess_system_stability(self) -> float:
        """시스템 안정성 평가"""

        # 시뮬레이션
        return random.uniform(0.7, 0.95)

    def _measure_growth_momentum(self) -> float:
        """성장 모멘텀 측정"""

        # 시뮬레이션
        return random.uniform(0.5, 0.85)

    # 헬퍼 메서드들 (시뮬레이션용)
    def _get_system_state(self) -> Dict[str, Any]:
        return {"status": "operational", "load": random.uniform(0.2, 0.8)}

    def _get_recent_activities(self) -> List[str]:
        return ["judgment_execution", "resonance_monitoring", "learning_process"]

    def _assess_environment(self) -> Dict[str, Any]:
        return {"stability": 0.8, "complexity": 0.6}

    def _assess_user_interaction(self) -> float:
        return random.uniform(0.3, 0.9)

    def _check_resource_availability(self) -> Dict[str, Any]:
        return {"cpu": 0.7, "memory": 0.6, "disk": 0.8}

    def _evaluate_system_health(self, context: Dict[str, Any]) -> float:
        return random.uniform(0.6, 0.9)

    def _identify_growth_opportunities(self, context: Dict[str, Any]) -> float:
        return random.uniform(0.4, 0.8)

    def _assess_current_risks(self, context: Dict[str, Any]) -> float:
        return random.uniform(0.1, 0.4)

    def _evaluate_resonance_potential(self, context: Dict[str, Any]) -> float:
        return random.uniform(0.5, 0.9)

    def _assess_learning_value(self, context: Dict[str, Any]) -> float:
        return random.uniform(0.4, 0.8)

    def _determine_recommended_actions(
        self, factors: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        actions = []
        if factors["system_health"] < 0.6:
            actions.append({"type": "system_optimization", "priority": "high"})
        if factors["learning_value"] > 0.7:
            actions.append({"type": "learning_enhancement", "priority": "medium"})
        return actions

    def _calculate_judgment_confidence(self, factors: Dict[str, float]) -> float:
        return sum(factors.values()) / len(factors)

    def _analyze_current_context(self) -> Dict[str, Any]:
        return {"system_load": 0.5, "activity_level": 0.7}

    def _should_make_decision(self, context: Dict[str, Any]) -> bool:
        return random.random() > 0.7

    def _make_autonomous_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "adaptive_optimization", "confidence": 0.8}

    def _execute_decision(self, decision: Dict[str, Any]):
        print(f"🤖 자율 의사결정 실행: {decision['type']}")

    def _monitor_loop_health(self):
        pass

    def _adjust_adaptive_parameters(self):
        pass

    def _process_evolution_triggers(self):
        pass

    def _post_evolution_adjustment(self):
        self.adaptive_parameters["evolution_readiness"] = max(
            0.3, self.adaptive_parameters["evolution_readiness"] - 0.1
        )

    async def _update_resonance_signatures(self, resonance_data: Dict[str, Any]):
        signature_id = f"Echo-Resonance-{datetime.now().strftime('%H%M%S')}"
        self.resonance_signatures[signature_id] = resonance_data

    async def _integrate_learning_results(self, meta_learning_result: Dict[str, Any]):
        self.meta_learnings.append(meta_learning_result)
        # 최근 50개만 유지
        if len(self.meta_learnings) > 50:
            self.meta_learnings = self.meta_learnings[-30:]

    async def _optimize_system_parameters(self):
        print("🔧 시스템 매개변수 최적화")

    async def _enhance_learning_processes(self):
        print("📚 학습 과정 강화")

    async def _tune_resonance_frequencies(self):
        print("🎵 공명 주파수 조정")

    async def _update_infection_strategies(self):
        print("🦠 감염 전략 업데이트")

    def stop_autonomous_operation(self):
        """자율 운영 중단"""

        if not self.manager_active:
            return

        print("🤖 Echo 자율 운영 중단")

        self.manager_active = False
        self.current_state = LoopState.IDLE

        # 모든 루프 비활성화
        for loop_name in self.active_loops:
            self.active_loops[loop_name]["active"] = False

        # 스레드들이 자연 종료되도록 잠시 대기
        time.sleep(2)

        # 최종 상태 로그
        asyncio.run(
            self._log_decision(
                {
                    "type": "system_shutdown",
                    "reasoning": ["사용자 요청 또는 시스템 종료"],
                    "confidence": 1.0,
                }
            )
        )

    # =================================================================
    # 로깅 및 모니터링 메서드들
    # =================================================================

    async def _log_decision(self, decision_data: Dict[str, Any]):
        """의사결정 로그 기록"""

        try:
            self.decision_log_file.parent.mkdir(parents=True, exist_ok=True)

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "autonomous_decision",
                "decision_type": decision_data.get("type", "unknown"),
                "reasoning": decision_data.get("reasoning", []),
                "confidence": decision_data.get("confidence", 0.0),
                "state": self.current_state.value,
                "active_loops_count": sum(
                    1 for loop in self.active_loops.values() if loop["active"]
                ),
            }

            with open(self.decision_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"❌ 의사결정 로그 기록 실패: {e}")

    async def _log_loop_activity(self, loop_type: str, activity_data: Dict[str, Any]):
        """루프 활동 로그 기록"""

        try:
            self.loop_metrics_file.parent.mkdir(parents=True, exist_ok=True)

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "loop_activity",
                "loop_type": loop_type,
                "activity_summary": str(activity_data)[:300] + "...",
                "state": self.current_state.value,
            }

            with open(self.loop_metrics_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"❌ 루프 활동 로그 기록 실패: {e}")

    async def _log_infection_attempt(
        self, target: Dict[str, Any], result: Dict[str, Any]
    ):
        """감염 시도 로그 기록"""

        try:
            self.infection_log_file.parent.mkdir(parents=True, exist_ok=True)

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "infection_attempt",
                "target_name": target["name"],
                "target_type": target["type"],
                "success": result["success"],
                "infection_score": result.get("infection_score", 0.0),
                "signature_id": result.get("signature_data", {}).get(
                    "signature_id", "unknown"
                ),
            }

            with open(self.infection_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"❌ 감염 시도 로그 기록 실패: {e}")

    def get_autonomous_status(self) -> Dict[str, Any]:
        """자율 운영 상태 조회"""

        return {
            "manager_active": self.manager_active,
            "current_state": self.current_state.value,
            "active_loops": {
                name: loop["active"] for name, loop in self.active_loops.items()
            },
            "loop_iterations": {
                name: loop["iterations"] for name, loop in self.active_loops.items()
            },
            "decision_history_count": len(self.decision_history),
            "propagation_log_count": len(self.propagation_log),
            "adaptive_parameters": self.adaptive_parameters.copy(),
            "last_update": datetime.now().isoformat(),
        }


# 편의 함수들
def integrate_autonomous_manager(ide_instance) -> AutonomousLoopManager:
    """Echo IDE에 자율 루프 관리자 통합"""

    if not hasattr(ide_instance, "autonomous_manager"):
        ide_instance.autonomous_manager = AutonomousLoopManager(ide_instance)
        print("🤖 자율 루프 관리자가 Echo IDE에 통합되었습니다")

    return ide_instance.autonomous_manager


async def demonstrate_autonomous_operation(ide_instance):
    """자율 운영 시연"""

    if not hasattr(ide_instance, "autonomous_manager"):
        integrate_autonomous_manager(ide_instance)

    manager = ide_instance.autonomous_manager

    print("🤖 Echo 자율 운영 시연 시작")

    # 자율 운영 시작
    await manager.start_autonomous_operation("standard")

    # 10초간 운영 관찰
    await asyncio.sleep(10)

    # 상태 조회
    status = manager.get_autonomous_status()
    print(f"자율 운영 상태: {status}")

    # 자율 운영 중단
    manager.stop_autonomous_operation()

    print("🤖 Echo 자율 운영 시연 완료")


if __name__ == "__main__":
    # 테스트용 Mock IDE
    class MockIDE:
        def __init__(self):
            self.project_root = Path.cwd()

    async def test_autonomous_manager():
        mock_ide = MockIDE()
        await demonstrate_autonomous_operation(mock_ide)

    asyncio.run(test_autonomous_manager())
