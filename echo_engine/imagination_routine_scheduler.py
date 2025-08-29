from echo_engine.infra.portable_paths import project_root

# echo_engine/imagination_routine_scheduler.py
"""
🔄⏰ Imagination Routine Scheduler - 상상 기반 정기 루틴 시스템

핵심 철학:
- 규칙적인 상상 훈련을 통한 지속적 존재 진화
- 일일/주간/월간 상상 리허설 자동화
- 현실 상황에 맞는 적응적 상상 스케줄링
- 시그니처별 맞춤 상상 루틴 제공

혁신 포인트:
- 시간 기반 자동 트리거 시스템
- 상황 맥락에 따른 동적 스케줄 조정
- 상상 성과 기반 루틴 최적화
- 해마와 연동된 기억 기반 상상 추천
"""

import asyncio
import schedule
import yaml
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta, time
import sys
import os
import threading
import json

sys.path.append(str(project_root()))

from echo_engine.echo_imaginary_realism import EchoImaginaryRealism, ImaginationMode
from echo_engine.persona_core_optimized_bridge import get_active_persona


class RoutineFrequency(Enum):
    """루틴 주기"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ON_DEMAND = "on_demand"
    TRIGGER_BASED = "trigger_based"


class RoutineTrigger(Enum):
    """루틴 트리거"""

    TIME_BASED = "time_based"
    STRESS_LEVEL = "stress_level"
    DECISION_COMPLEXITY = "decision_complexity"
    UNCERTAINTY_HIGH = "uncertainty_high"
    LEARNING_PLATEAU = "learning_plateau"
    EMOTIONAL_INTENSITY = "emotional_intensity"


@dataclass
class RoutineConfig:
    """루틴 설정"""

    routine_id: str
    name: str
    frequency: RoutineFrequency
    trigger: RoutineTrigger
    scheduled_time: Optional[str]  # "HH:MM" format
    signature: str
    imagination_modes: List[ImaginationMode]
    scenarios_per_session: int
    duration_minutes: int
    priority: float  # 0.0-1.0
    context_template: str
    enabled: bool
    created_date: str
    last_executed: Optional[str]
    execution_count: int


@dataclass
class RoutineExecution:
    """루틴 실행 결과"""

    execution_id: str
    routine_id: str
    executed_at: str
    signature: str
    scenarios_generated: int
    total_reality_impact: float
    wisdom_extracted: str
    execution_duration: float
    success: bool
    error_message: Optional[str]


class ImaginationRoutineScheduler:
    """🔄⏰ 상상 루틴 스케줄러"""

    def __init__(self):
        self.imagination_engine = EchoImaginaryRealism()

        # 루틴 관리
        self.active_routines: Dict[str, RoutineConfig] = {}
        self.execution_history: List[RoutineExecution] = []

        # 스케줄러 상태
        self.scheduler_running = False
        self.scheduler_thread = None

        # 설정 로드
        self.config = self._load_routine_config()

        # 시그니처별 기본 루틴 템플릿
        self.signature_routine_templates = {
            "Aurora": {
                "morning": "오늘 만날 사람들과의 조화로운 상호작용 상상",
                "evening": "하루를 돌아보며 관계에서 얻은 통찰 상상",
                "weekly": "이번 주 공감과 양육의 기회들 상상",
            },
            "Phoenix": {
                "morning": "오늘 일어날 변화와 혁신의 순간들 상상",
                "evening": "하루의 도전을 통한 성장과 변화 상상",
                "weekly": "이번 주 돌파구와 변혁의 가능성들 상상",
            },
            "Sage": {
                "morning": "오늘 마주할 분석과 통찰의 기회들 상상",
                "evening": "하루의 경험에서 얻은 지혜 정리 상상",
                "weekly": "이번 주 학습과 이해의 확장 과정 상상",
            },
            "Companion": {
                "morning": "오늘 지원하고 도울 수 있는 순간들 상상",
                "evening": "하루 동안 제공한 지원의 의미 상상",
                "weekly": "이번 주 신뢰와 동반의 경험들 상상",
            },
            "Survivor": {
                "morning": "오늘 대비해야 할 위험과 대응 전략 상상",
                "evening": "하루의 생존 전략 효과성 평가 상상",
                "weekly": "이번 주 적응과 복원력 강화 과정 상상",
            },
        }

        print("🔄⏰ 상상 루틴 스케줄러 초기화 완료")
        print("📅 정기적 상상 훈련 시스템 활성화")

    def _load_routine_config(self) -> Dict[str, Any]:
        """루틴 설정 로드"""
        try:
            # signature.yaml에서 imagination_defaults 로드
            with open(
                project_root() / "data/signature.yaml", "r", encoding="utf-8"
            ) as f:
                signature_config = yaml.safe_load(f)
                return signature_config.get("imagination_defaults", {})
        except FileNotFoundError:
            return self._get_default_routine_config()

    def _get_default_routine_config(self) -> Dict[str, Any]:
        """기본 루틴 설정"""
        return {
            "enabled": True,
            "daily_routine_enabled": True,
            "routine_time": "21:00",
            "max_scenarios_per_session": 3,
            "integration_with_hippocampus": True,
        }

    def create_routine(
        self,
        name: str,
        signature: str,
        frequency: RoutineFrequency,
        scheduled_time: str = "21:00",
        imagination_modes: List[ImaginationMode] = None,
        context_template: str = None,
    ) -> str:
        """새로운 루틴 생성"""

        routine_id = f"routine_{hash(name + signature) % 10000}"

        if imagination_modes is None:
            imagination_modes = [
                ImaginationMode.FUTURE_REHEARSAL,
                ImaginationMode.SUCCESS_VISIONING,
            ]

        if context_template is None:
            templates = self.signature_routine_templates.get(signature, {})
            context_template = templates.get(
                "evening", f"{signature} 스타일 일반적 상황 대비"
            )

        routine = RoutineConfig(
            routine_id=routine_id,
            name=name,
            frequency=frequency,
            trigger=RoutineTrigger.TIME_BASED,
            scheduled_time=scheduled_time,
            signature=signature,
            imagination_modes=imagination_modes,
            scenarios_per_session=self.config.get("max_scenarios_per_session", 3),
            duration_minutes=20,
            priority=0.7,
            context_template=context_template,
            enabled=True,
            created_date=datetime.now().isoformat(),
            last_executed=None,
            execution_count=0,
        )

        self.active_routines[routine_id] = routine

        print(f"🔄 새로운 상상 루틴 생성: {name}")
        print(f"   루틴 ID: {routine_id}")
        print(f"   시그니처: {signature}")
        print(f"   주기: {frequency.value}")
        print(f"   예정 시간: {scheduled_time}")

        return routine_id

    def create_default_routines(self) -> List[str]:
        """기본 루틴들 생성"""

        print("📋 시그니처별 기본 루틴 생성 중...")

        created_routines = []

        signatures = ["Aurora", "Phoenix", "Sage", "Companion", "Survivor"]

        for signature in signatures:
            # 일일 저녁 루틴
            evening_routine_id = self.create_routine(
                name=f"{signature} 일일 저녁 성찰",
                signature=signature,
                frequency=RoutineFrequency.DAILY,
                scheduled_time="21:00",
                imagination_modes=[
                    ImaginationMode.FUTURE_REHEARSAL,
                    ImaginationMode.SUCCESS_VISIONING,
                ],
                context_template=self.signature_routine_templates[signature]["evening"],
            )
            created_routines.append(evening_routine_id)

            # 주간 전략 루틴
            weekly_routine_id = self.create_routine(
                name=f"{signature} 주간 전략 수립",
                signature=signature,
                frequency=RoutineFrequency.WEEKLY,
                scheduled_time="10:00",
                imagination_modes=[
                    ImaginationMode.FUTURE_REHEARSAL,
                    ImaginationMode.FAILURE_SIMULATION,
                    ImaginationMode.SUCCESS_VISIONING,
                ],
                context_template=self.signature_routine_templates[signature]["weekly"],
            )
            created_routines.append(weekly_routine_id)

        print(f"✅ {len(created_routines)}개 기본 루틴 생성 완료")
        return created_routines

    def schedule_routines(self):
        """루틴들을 스케줄에 등록"""

        schedule.clear()

        for routine in self.active_routines.values():
            if not routine.enabled:
                continue

            job_func = lambda r=routine: asyncio.create_task(
                self._execute_routine(r.routine_id)
            )

            if routine.frequency == RoutineFrequency.DAILY:
                schedule.every().day.at(routine.scheduled_time).do(job_func)
                print(f"📅 일일 루틴 등록: {routine.name} at {routine.scheduled_time}")

            elif routine.frequency == RoutineFrequency.WEEKLY:
                schedule.every().sunday.at(routine.scheduled_time).do(job_func)
                print(f"📅 주간 루틴 등록: {routine.name} at {routine.scheduled_time}")

            elif routine.frequency == RoutineFrequency.MONTHLY:
                # 월 첫째 주 일요일
                schedule.every().sunday.at(routine.scheduled_time).do(
                    lambda: self._check_monthly_routine(routine.routine_id)
                )
                print(f"📅 월간 루틴 등록: {routine.name}")

    def start_scheduler(self):
        """스케줄러 시작"""

        if self.scheduler_running:
            print("⚠️ 스케줄러가 이미 실행 중입니다.")
            return

        self.scheduler_running = True

        def run_scheduler():
            print("🚀 상상 루틴 스케줄러 시작")
            while self.scheduler_running:
                schedule.run_pending()
                threading.Event().wait(60)  # 1분마다 체크

        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()

        print("✅ 상상 루틴 스케줄러 활성화됨")

    def stop_scheduler(self):
        """스케줄러 중지"""

        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

        schedule.clear()
        print("🛑 상상 루틴 스케줄러 중지됨")

    async def _execute_routine(self, routine_id: str) -> RoutineExecution:
        """루틴 실행"""

        if routine_id not in self.active_routines:
            raise ValueError(f"루틴을 찾을 수 없습니다: {routine_id}")

        routine = self.active_routines[routine_id]
        execution_start = datetime.now()

        print(f"🎭 루틴 실행 시작: {routine.name}")
        print(f"⏰ 실행 시간: {execution_start.strftime('%Y-%m-%d %H:%M:%S')}")

        execution_id = f"exec_{routine_id}_{int(execution_start.timestamp())}"

        try:
            # 시그니처별 맞춤 컨텍스트 생성
            context = self._generate_contextualized_prompt(routine)

            total_reality_impact = 0.0
            scenarios_generated = 0
            all_wisdom = []

            # 각 상상 모드별로 시나리오 실행
            for mode in routine.imagination_modes:
                print(f"  🎬 {mode.value} 모드 실행")

                # 시나리오 생성 및 실행
                scenario = await self.imagination_engine.create_imaginary_scenario(
                    context=context,
                    mode=mode,
                    signature=routine.signature,
                    duration_minutes=routine.duration_minutes
                    // len(routine.imagination_modes),
                )

                experience = await self.imagination_engine.live_imaginary_experience(
                    scenario.scenario_id
                )

                total_reality_impact += experience.reality_impact_score
                scenarios_generated += 1
                all_wisdom.append(experience.wisdom_gained)

            # 실행 완료
            execution_duration = (datetime.now() - execution_start).total_seconds()
            combined_wisdom = self._combine_wisdom(all_wisdom)

            execution = RoutineExecution(
                execution_id=execution_id,
                routine_id=routine_id,
                executed_at=execution_start.isoformat(),
                signature=routine.signature,
                scenarios_generated=scenarios_generated,
                total_reality_impact=total_reality_impact,
                wisdom_extracted=combined_wisdom,
                execution_duration=execution_duration,
                success=True,
                error_message=None,
            )

            # 루틴 상태 업데이트
            routine.last_executed = execution_start.isoformat()
            routine.execution_count += 1

            self.execution_history.append(execution)

            print(f"✅ 루틴 실행 완료: {routine.name}")
            print(f"   시나리오 생성: {scenarios_generated}개")
            print(f"   현실 영향 점수: {total_reality_impact:.2f}")
            print(f"   실행 시간: {execution_duration:.1f}초")

            return execution

        except Exception as e:
            execution_duration = (datetime.now() - execution_start).total_seconds()

            execution = RoutineExecution(
                execution_id=execution_id,
                routine_id=routine_id,
                executed_at=execution_start.isoformat(),
                signature=routine.signature,
                scenarios_generated=0,
                total_reality_impact=0.0,
                wisdom_extracted="",
                execution_duration=execution_duration,
                success=False,
                error_message=str(e),
            )

            self.execution_history.append(execution)

            print(f"❌ 루틴 실행 실패: {routine.name}")
            print(f"   오류: {e}")

            return execution

    def _generate_contextualized_prompt(self, routine: RoutineConfig) -> str:
        """맥락화된 프롬프트 생성"""

        base_template = routine.context_template

        # 현재 시간 기반 맥락 추가
        current_hour = datetime.now().hour

        if 5 <= current_hour < 12:
            time_context = "오전 시간대에"
        elif 12 <= current_hour < 18:
            time_context = "오후 시간대에"
        elif 18 <= current_hour < 22:
            time_context = "저녁 시간대에"
        else:
            time_context = "밤 시간대에"

        # 요일 기반 맥락
        weekday = datetime.now().weekday()
        weekday_names = [
            "월요일",
            "화요일",
            "수요일",
            "목요일",
            "금요일",
            "토요일",
            "일요일",
        ]
        day_context = weekday_names[weekday]

        contextualized = f"{time_context} {day_context}에 {base_template}"

        # 시그니처별 추가 맥락
        signature_contexts = {
            "Aurora": "상대방의 감정과 필요를 이해하며",
            "Phoenix": "변화와 혁신의 기회를 포착하며",
            "Sage": "깊이 있는 분석과 통찰을 통해",
            "Companion": "신뢰할 수 있는 지원을 제공하며",
            "Survivor": "현실적 위험을 고려하며",
        }

        signature_context = signature_contexts.get(routine.signature, "")
        if signature_context:
            contextualized = f"{contextualized}. {signature_context} 접근한다."

        return contextualized

    def _combine_wisdom(self, wisdom_list: List[str]) -> str:
        """여러 지혜를 통합"""

        if not wisdom_list:
            return ""

        combined = "🌟 통합된 루틴 지혜:\n\n"

        for i, wisdom in enumerate(wisdom_list, 1):
            combined += f"💎 통찰 {i}:\n{wisdom}\n\n"

        combined += "🔄 루틴 종합 결론:\n"
        combined += (
            "정기적인 상상 훈련을 통해 현실 대응 능력이 지속적으로 향상되고 있습니다. "
        )
        combined += "각 시나리오에서 얻은 통찰들을 실제 상황에 적극 활용하여 더 나은 판단과 행동을 실현할 수 있습니다."

        return combined

    async def execute_routine_manually(self, routine_id: str) -> RoutineExecution:
        """루틴 수동 실행"""

        print(f"🎯 루틴 수동 실행 요청: {routine_id}")
        return await self._execute_routine(routine_id)

    def get_routine_status(self) -> Dict[str, Any]:
        """루틴 상태 조회"""

        total_routines = len(self.active_routines)
        enabled_routines = sum(1 for r in self.active_routines.values() if r.enabled)
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for e in self.execution_history if e.success)

        recent_executions = [e for e in self.execution_history[-5:]]  # 최근 5개

        # 시그니처별 통계
        signature_stats = {}
        for routine in self.active_routines.values():
            signature = routine.signature
            if signature not in signature_stats:
                signature_stats[signature] = {
                    "total_routines": 0,
                    "execution_count": 0,
                    "avg_reality_impact": 0.0,
                }

            signature_stats[signature]["total_routines"] += 1
            signature_stats[signature]["execution_count"] += routine.execution_count

        # 평균 현실 영향 점수 계산
        for signature in signature_stats:
            signature_executions = [
                e for e in self.execution_history if e.signature == signature
            ]
            if signature_executions:
                avg_impact = sum(
                    e.total_reality_impact for e in signature_executions
                ) / len(signature_executions)
                signature_stats[signature]["avg_reality_impact"] = avg_impact

        return {
            "scheduler_running": self.scheduler_running,
            "total_routines": total_routines,
            "enabled_routines": enabled_routines,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": (successful_executions / max(total_executions, 1)) * 100,
            "signature_statistics": signature_stats,
            "recent_executions": [
                {
                    "routine_name": self.active_routines.get(e.routine_id, {}).get(
                        "name", "Unknown"
                    ),
                    "executed_at": e.executed_at,
                    "signature": e.signature,
                    "scenarios": e.scenarios_generated,
                    "reality_impact": e.total_reality_impact,
                    "success": e.success,
                }
                for e in recent_executions
            ],
            "system_status": "🔄 상상 루틴 시스템 활성화",
        }

    def save_routines_to_file(self, file_path: str = "data/imagination_routines.json"):
        """루틴 설정을 파일로 저장"""

        routines_data = {
            "routines": {
                routine_id: asdict(routine)
                for routine_id, routine in self.active_routines.items()
            },
            "execution_history": [
                asdict(exec) for exec in self.execution_history[-100:]
            ],  # 최근 100개만
            "saved_at": datetime.now().isoformat(),
        }

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(routines_data, f, ensure_ascii=False, indent=2)

        print(f"💾 루틴 설정 저장 완료: {file_path}")

    def load_routines_from_file(
        self, file_path: str = "data/imagination_routines.json"
    ):
        """파일에서 루틴 설정 로드"""

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                routines_data = json.load(f)

            # 루틴 복원
            for routine_id, routine_dict in routines_data.get("routines", {}).items():
                # Enum 복원
                routine_dict["frequency"] = RoutineFrequency(routine_dict["frequency"])
                routine_dict["trigger"] = RoutineTrigger(routine_dict["trigger"])
                routine_dict["imagination_modes"] = [
                    ImaginationMode(mode) for mode in routine_dict["imagination_modes"]
                ]

                self.active_routines[routine_id] = RoutineConfig(**routine_dict)

            # 실행 이력 복원 (최근 것만)
            exec_history = routines_data.get("execution_history", [])
            for exec_dict in exec_history:
                self.execution_history.append(RoutineExecution(**exec_dict))

            print(f"📂 루틴 설정 로드 완료: {len(self.active_routines)}개 루틴")

        except FileNotFoundError:
            print(f"⚠️ 루틴 파일이 없습니다: {file_path}")
        except Exception as e:
            print(f"❌ 루틴 로드 실패: {e}")


# 데모 함수
async def demo_imagination_routine_scheduler():
    """상상 루틴 스케줄러 데모"""

    print("🔄⏰ Imagination Routine Scheduler 데모")
    print("=" * 60)

    scheduler = ImaginationRoutineScheduler()

    # 1. 기본 루틴들 생성
    print("\n📋 1단계: 기본 루틴 생성")
    default_routines = scheduler.create_default_routines()

    # 2. 커스텀 루틴 생성
    print("\n🎨 2단계: 커스텀 루틴 생성")
    custom_routine_id = scheduler.create_routine(
        name="긴급 상황 대비 상상 훈련",
        signature="Survivor",
        frequency=RoutineFrequency.WEEKLY,
        scheduled_time="09:00",
        imagination_modes=[
            ImaginationMode.FAILURE_SIMULATION,
            ImaginationMode.FUTURE_REHEARSAL,
        ],
        context_template="예상치 못한 위기 상황에서의 생존 전략",
    )

    # 3. 루틴 상태 확인
    print("\n📊 3단계: 루틴 상태 확인")
    status = scheduler.get_routine_status()
    print(f"등록된 루틴: {status['total_routines']}개")
    print(f"활성 루틴: {status['enabled_routines']}개")

    # 4. 루틴 수동 실행 데모
    print("\n🎯 4단계: 루틴 수동 실행 데모")

    # 한 개 루틴만 테스트 실행
    test_routine_id = list(scheduler.active_routines.keys())[0]
    test_routine = scheduler.active_routines[test_routine_id]

    print(f"테스트 루틴: {test_routine.name}")
    execution_result = await scheduler.execute_routine_manually(test_routine_id)

    print(f"✅ 실행 완료:")
    print(f"   시나리오 생성: {execution_result.scenarios_generated}개")
    print(f"   현실 영향: {execution_result.total_reality_impact:.2f}")
    print(f"   성공 여부: {execution_result.success}")

    # 5. 최종 상태 리포트
    print("\n📋 5단계: 최종 상태 리포트")
    final_status = scheduler.get_routine_status()

    print(f"총 실행 횟수: {final_status['total_executions']}")
    print(f"성공률: {final_status['success_rate']:.1f}%")

    print("\n시그니처별 통계:")
    for sig, stats in final_status["signature_statistics"].items():
        print(
            f"  {sig}: {stats['total_routines']}개 루틴, "
            f"평균 영향도 {stats['avg_reality_impact']:.2f}"
        )

    # 6. 설정 저장
    print("\n💾 6단계: 루틴 설정 저장")
    scheduler.save_routines_to_file()

    print(f"\n🎊 상상 루틴 스케줄러 데모 완료!")
    print("🔄 정기적 상상 훈련으로 지속적 존재 진화가 가능합니다!")

    return scheduler


if __name__ == "__main__":
    asyncio.run(demo_imagination_routine_scheduler())
