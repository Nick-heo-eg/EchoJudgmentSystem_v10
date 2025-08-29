#!/usr/bin/env python3
"""
🚀 Intelligent Agent Dispatcher - 지능형 에이전트 디스패처
Echo 시스템의 모든 에이전트를 지능적으로 선택, 배치, 실행하는 중앙 조정 시스템

핵심 기능:
- 자연어 요청 분석하여 최적 에이전트 조합 선택
- 다중 에이전트 협업 오케스트레이션
- 실시간 성능 모니터링 및 적응적 라우팅
- 에이전트 간 데이터 파이프라인 관리
"""

import yaml
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import importlib
import inspect
from pathlib import Path

from .universal_agent_factory import UniversalAgentFactory
from .agent_domain_mapper import AgentDomainMapper


@dataclass
class AgentTask:
    """에이전트 작업 정의"""

    task_id: str
    description: str
    priority: str  # high, medium, low
    deadline: Optional[datetime]
    input_data: Dict[str, Any]
    expected_output: Dict[str, str]
    constraints: List[str]


@dataclass
class AgentExecution:
    """에이전트 실행 결과"""

    execution_id: str
    agent_id: str
    task_id: str
    status: str  # running, completed, failed, timeout
    start_time: datetime
    end_time: Optional[datetime]
    result: Optional[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    error_message: Optional[str]


@dataclass
class AgentPipeline:
    """에이전트 파이프라인"""

    pipeline_id: str
    agents: List[str]
    data_flow: Dict[str, str]  # agent_id -> next_agent_id
    parallel_stages: List[List[str]]
    error_handling: str  # stop, continue, retry


class IntelligentAgentDispatcher:
    """🚀 지능형 에이전트 디스패처"""

    def __init__(self):
        self.factory = UniversalAgentFactory()
        self.domain_mapper = AgentDomainMapper()

        # 에이전트 레지스트리
        self.available_agents = self._load_available_agents()
        self.agent_performance = self._load_performance_history()

        # 실행 상태 추적
        self.active_executions: Dict[str, AgentExecution] = {}
        self.execution_queue: List[AgentTask] = []
        self.completed_executions: List[AgentExecution] = []

        # 성능 최적화
        self.agent_affinity_matrix = self._build_affinity_matrix()
        self.load_balancer = {}

        # 자연어 이해 패턴
        self.intent_patterns = self._load_intent_patterns()

    def _load_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """사용 가능한 에이전트 로드"""
        agents = self.factory.list_available_agents()
        return agents.get("agents", {})

    def _load_performance_history(self) -> Dict[str, Dict[str, float]]:
        """에이전트 성능 이력 로드"""
        performance_file = "data/agent_performance.json"

        if Path(performance_file).exists():
            with open(performance_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # 기본 성능 데이터
        return {
            agent_id: {
                "success_rate": 0.8,
                "avg_execution_time": 5.0,
                "reliability": 0.7,
            }
            for agent_id in self.available_agents.keys()
        }

    def _build_affinity_matrix(self) -> Dict[str, List[str]]:
        """에이전트 간 친화도 매트릭스 구축"""
        affinity = {}

        for agent_id, agent_info in self.available_agents.items():
            domain = agent_info.get("domain", "general")
            collaborating_domains = self.domain_mapper.find_collaborating_domains(
                domain
            )

            affinity[agent_id] = []
            for other_agent_id, other_info in self.available_agents.items():
                if other_info.get("domain") in collaborating_domains:
                    affinity[agent_id].append(other_agent_id)

        return affinity

    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """의도 패턴 로드"""
        return {
            "data_collection": ["수집", "가져오", "크롤링", "스크래핑", "모으", "조사"],
            "data_processing": ["처리", "변환", "분석", "계산", "정리"],
            "automation": ["자동화", "자동", "스케줄", "정기적", "반복"],
            "monitoring": ["모니터링", "감시", "추적", "확인", "체크"],
            "communication": ["발송", "전송", "알림", "메시지", "이메일"],
            "reporting": ["보고서", "리포트", "요약", "정리", "문서화"],
        }

    def analyze_request(self, request: str) -> Dict[str, Any]:
        """자연어 요청 분석"""

        # 의도 분석
        detected_intents = []
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in request for pattern in patterns):
                detected_intents.append(intent)

        # 복잡도 분석
        complexity_indicators = {
            "simple": ["하나", "단순", "간단", "기본"],
            "medium": ["여러", "다양", "복합", "통합"],
            "complex": ["복잡", "고급", "정교", "종합"],
        }

        complexity = "medium"  # 기본값
        for level, indicators in complexity_indicators.items():
            if any(indicator in request for indicator in indicators):
                complexity = level
                break

        # 우선순위 분석
        priority_indicators = {
            "high": ["긴급", "빨리", "즉시", "중요"],
            "low": ["나중에", "천천히", "여유", "참고"],
        }

        priority = "medium"  # 기본값
        for level, indicators in priority_indicators.items():
            if any(indicator in request for indicator in indicators):
                priority = level
                break

        # 시간 제약 분석
        time_indicators = ["분", "시간", "일", "주", "월"]
        has_deadline = any(indicator in request for indicator in time_indicators)

        return {
            "intents": detected_intents,
            "complexity": complexity,
            "priority": priority,
            "has_deadline": has_deadline,
            "estimated_agents_needed": len(detected_intents) if detected_intents else 1,
        }

    def select_optimal_agents(
        self, analysis: Dict[str, Any], task: AgentTask
    ) -> List[str]:
        """최적 에이전트 선택"""

        candidates = []

        # 의도 기반 에이전트 매칭
        for intent in analysis["intents"]:
            domain_suggestions = self._map_intent_to_domains(intent)

            for domain in domain_suggestions:
                domain_agents = [
                    agent_id
                    for agent_id, agent_info in self.available_agents.items()
                    if agent_info.get("domain") == domain
                ]
                candidates.extend(domain_agents)

        # 중복 제거
        candidates = list(set(candidates))

        # 성능 기반 정렬
        candidates.sort(
            key=lambda agent_id: (
                self.agent_performance.get(agent_id, {}).get("success_rate", 0),
                -self.agent_performance.get(agent_id, {}).get(
                    "avg_execution_time", 999
                ),
            ),
            reverse=True,
        )

        # 복잡도에 따른 에이전트 수 결정
        if analysis["complexity"] == "simple":
            return candidates[:1]
        elif analysis["complexity"] == "medium":
            return candidates[:2]
        else:  # complex
            return candidates[:3]

    def _map_intent_to_domains(self, intent: str) -> List[str]:
        """의도를 도메인으로 매핑"""
        mapping = {
            "data_collection": ["web", "api"],
            "data_processing": ["document", "api"],
            "automation": ["desktop", "web"],
            "monitoring": ["web", "api", "desktop"],
            "communication": ["communication"],
            "reporting": ["document", "communication"],
        }

        return mapping.get(intent, ["web"])  # 기본값: web

    def create_execution_pipeline(
        self, agents: List[str], task: AgentTask
    ) -> AgentPipeline:
        """실행 파이프라인 생성"""

        pipeline_id = f"pipeline_{int(datetime.now().timestamp())}"

        # 에이전트 간 데이터 흐름 설계
        data_flow = {}
        for i, agent_id in enumerate(agents[:-1]):
            data_flow[agent_id] = agents[i + 1]

        # 병렬 실행 가능한 단계 식별
        parallel_stages = []

        # 단순한 병렬화: 독립적인 에이전트들을 병렬로 실행
        independent_agents = []
        dependent_agents = []

        for agent_id in agents:
            if agent_id in self.agent_affinity_matrix:
                dependent_agents.append(agent_id)
            else:
                independent_agents.append(agent_id)

        if independent_agents:
            parallel_stages.append(independent_agents)
        if dependent_agents:
            parallel_stages.append(dependent_agents)

        # 파이프라인이 너무 단순하면 순차 실행
        if len(parallel_stages) <= 1:
            parallel_stages = [[agent] for agent in agents]

        return AgentPipeline(
            pipeline_id=pipeline_id,
            agents=agents,
            data_flow=data_flow,
            parallel_stages=parallel_stages,
            error_handling="retry",  # 기본값
        )

    async def execute_pipeline(
        self, pipeline: AgentPipeline, task: AgentTask
    ) -> Dict[str, Any]:
        """파이프라인 실행"""

        print(f"🚀 파이프라인 '{pipeline.pipeline_id}' 실행 시작")

        results = {}
        errors = []

        try:
            # 각 병렬 단계 실행
            for stage_index, stage_agents in enumerate(pipeline.parallel_stages):
                print(
                    f"📍 단계 {stage_index + 1}: {len(stage_agents)}개 에이전트 병렬 실행"
                )

                # 병렬 실행
                stage_tasks = []
                for agent_id in stage_agents:
                    task_coroutine = self._execute_single_agent(agent_id, task, results)
                    stage_tasks.append(task_coroutine)

                # 모든 에이전트 완료 대기
                stage_results = await asyncio.gather(
                    *stage_tasks, return_exceptions=True
                )

                # 결과 처리
                for i, result in enumerate(stage_results):
                    agent_id = stage_agents[i]

                    if isinstance(result, Exception):
                        error_msg = f"에이전트 {agent_id} 실행 실패: {result}"
                        errors.append(error_msg)
                        print(f"❌ {error_msg}")

                        if pipeline.error_handling == "stop":
                            raise result
                    else:
                        results[agent_id] = result
                        print(f"✅ {agent_id} 완료")

            # 최종 결과 집계
            final_result = {
                "pipeline_id": pipeline.pipeline_id,
                "task_id": task.task_id,
                "status": "completed",
                "agent_results": results,
                "errors": errors,
                "execution_summary": {
                    "total_agents": len(pipeline.agents),
                    "successful_agents": len(results),
                    "failed_agents": len(errors),
                    "success_rate": (
                        len(results) / len(pipeline.agents) if pipeline.agents else 0
                    ),
                },
            }

            print(
                f"🎉 파이프라인 완료: {final_result['execution_summary']['success_rate']:.1%} 성공률"
            )

            return final_result

        except Exception as e:
            print(f"💥 파이프라인 실행 실패: {e}")
            return {
                "pipeline_id": pipeline.pipeline_id,
                "task_id": task.task_id,
                "status": "failed",
                "error": str(e),
                "partial_results": results,
            }

    async def _execute_single_agent(
        self, agent_id: str, task: AgentTask, previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """단일 에이전트 실행"""

        execution_id = f"exec_{agent_id}_{int(datetime.now().timestamp())}"
        start_time = datetime.now()

        try:
            # 에이전트 정보 조회
            agent_info = self.available_agents.get(agent_id)
            if not agent_info:
                raise ValueError(f"에이전트 {agent_id}를 찾을 수 없습니다")

            # 실행 기록 시작
            execution = AgentExecution(
                execution_id=execution_id,
                agent_id=agent_id,
                task_id=task.task_id,
                status="running",
                start_time=start_time,
                end_time=None,
                result=None,
                performance_metrics={},
                error_message=None,
            )

            self.active_executions[execution_id] = execution

            # 입력 데이터 준비 (이전 결과 포함)
            input_data = dict(task.input_data)
            input_data["previous_results"] = previous_results

            # 시뮬레이션된 에이전트 실행 (실제로는 동적 import 필요)
            await asyncio.sleep(1)  # 실행 시간 시뮬레이션

            # 가상의 성공 결과
            result = {
                "agent_id": agent_id,
                "execution_id": execution_id,
                "output": f"{agent_id} 실행 완료",
                "metadata": {
                    "execution_time": 1.0,
                    "input_size": len(str(input_data)),
                    "output_size": 100,
                },
            }

            # 실행 완료 기록
            execution.status = "completed"
            execution.end_time = datetime.now()
            execution.result = result
            execution.performance_metrics = {
                "execution_time": (
                    execution.end_time - execution.start_time
                ).total_seconds(),
                "success": True,
            }

            # 성능 업데이트
            self._update_agent_performance(agent_id, execution)

            return result

        except Exception as e:
            # 오류 처리
            execution.status = "failed"
            execution.end_time = datetime.now()
            execution.error_message = str(e)
            execution.performance_metrics = {
                "execution_time": (
                    execution.end_time - execution.start_time
                ).total_seconds(),
                "success": False,
            }

            self._update_agent_performance(agent_id, execution)

            raise e

        finally:
            # 활성 실행에서 제거
            if execution_id in self.active_executions:
                completed_execution = self.active_executions.pop(execution_id)
                self.completed_executions.append(completed_execution)

    def _update_agent_performance(self, agent_id: str, execution: AgentExecution):
        """에이전트 성능 업데이트"""

        if agent_id not in self.agent_performance:
            self.agent_performance[agent_id] = {
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "reliability": 0.0,
                "total_executions": 0,
                "successful_executions": 0,
            }

        perf = self.agent_performance[agent_id]
        perf["total_executions"] += 1

        if execution.status == "completed":
            perf["successful_executions"] += 1

        # 성공률 업데이트
        perf["success_rate"] = perf["successful_executions"] / perf["total_executions"]

        # 평균 실행 시간 업데이트
        exec_time = execution.performance_metrics.get("execution_time", 0)
        perf["avg_execution_time"] = (
            perf["avg_execution_time"] * (perf["total_executions"] - 1) + exec_time
        ) / perf["total_executions"]

        # 신뢰도 업데이트 (성공률과 실행 시간 고려)
        time_factor = min(5.0 / max(perf["avg_execution_time"], 0.1), 1.0)
        perf["reliability"] = perf["success_rate"] * 0.7 + time_factor * 0.3

    async def process_request(self, request: str, **kwargs) -> Dict[str, Any]:
        """자연어 요청 처리"""

        print(f"🧠 요청 분석 중: {request}")

        # 1. 요청 분석
        analysis = self.analyze_request(request)
        print(f"📊 분석 결과: {analysis}")

        # 2. 작업 생성
        task = AgentTask(
            task_id=f"task_{int(datetime.now().timestamp())}",
            description=request,
            priority=analysis["priority"],
            deadline=kwargs.get("deadline"),
            input_data=kwargs,
            expected_output={"type": "mixed"},
            constraints=[],
        )

        # 3. 최적 에이전트 선택
        selected_agents = self.select_optimal_agents(analysis, task)
        print(f"🤖 선택된 에이전트: {selected_agents}")

        if not selected_agents:
            # 새 에이전트 생성 제안
            creation_result = self.factory.execute_agent_creation_flow(request)
            if creation_result.get("success"):
                selected_agents = [creation_result["agent_id"]]
                print(f"🆕 새 에이전트 생성: {creation_result['agent_name']}")
            else:
                return {
                    "success": False,
                    "error": "적합한 에이전트를 찾거나 생성할 수 없습니다",
                    "suggestion": "요청을 더 구체적으로 작성해주세요",
                }

        # 4. 파이프라인 생성
        pipeline = self.create_execution_pipeline(selected_agents, task)
        print(f"⚙️ 파이프라인 생성: {pipeline.pipeline_id}")

        # 5. 실행
        result = await self.execute_pipeline(pipeline, task)

        return result

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""

        total_agents = len(self.available_agents)
        active_executions = len(self.active_executions)
        completed_executions = len(self.completed_executions)

        # 전체 성능 통계
        if self.agent_performance:
            avg_success_rate = sum(
                p.get("success_rate", 0) for p in self.agent_performance.values()
            ) / len(self.agent_performance)
            avg_execution_time = sum(
                p.get("avg_execution_time", 0) for p in self.agent_performance.values()
            ) / len(self.agent_performance)
        else:
            avg_success_rate = 0
            avg_execution_time = 0

        return {
            "dispatcher_status": "active",
            "total_available_agents": total_agents,
            "active_executions": active_executions,
            "completed_executions": completed_executions,
            "system_performance": {
                "average_success_rate": avg_success_rate,
                "average_execution_time": avg_execution_time,
            },
            "top_performing_agents": sorted(
                self.agent_performance.items(),
                key=lambda x: x[1].get("reliability", 0),
                reverse=True,
            )[:5],
            "last_updated": datetime.now().isoformat(),
        }


# 편의 함수들
async def process_natural_request(request: str, **kwargs) -> Dict[str, Any]:
    """자연어 요청 처리 (편의 함수)"""
    dispatcher = IntelligentAgentDispatcher()
    return await dispatcher.process_request(request, **kwargs)


def get_dispatcher_status() -> Dict[str, Any]:
    """디스패처 상태 조회 (편의 함수)"""
    dispatcher = IntelligentAgentDispatcher()
    return dispatcher.get_system_status()


if __name__ == "__main__":
    # 테스트 실행
    async def test_dispatcher():
        dispatcher = IntelligentAgentDispatcher()

        print("🚀 Intelligent Agent Dispatcher 테스트")
        print("=" * 60)

        # 테스트 요청들
        test_requests = [
            "웹에서 최신 뉴스를 수집해서 요약 보고서를 만들어줘",
            "매일 주식 가격을 모니터링하고 변화가 있으면 이메일로 알려줘",
            "PDF 문서들을 워드 파일로 변환하고 정리해줘",
        ]

        for i, request in enumerate(test_requests, 1):
            print(f"\n📝 테스트 {i}: {request}")

            try:
                result = await dispatcher.process_request(request)
                print(f"✅ 결과: {result.get('status', 'unknown')}")
                if result.get("execution_summary"):
                    summary = result["execution_summary"]
                    print(f"   📊 성공률: {summary['success_rate']:.1%}")
                    print(
                        f"   🤖 사용된 에이전트: {summary['successful_agents']}/{summary['total_agents']}"
                    )
            except Exception as e:
                print(f"❌ 오류: {e}")

        # 시스템 상태 출력
        print(f"\n📊 시스템 상태:")
        status = dispatcher.get_system_status()
        print(f"   • 전체 에이전트: {status['total_available_agents']}개")
        print(
            f"   • 평균 성공률: {status['system_performance']['average_success_rate']:.1%}"
        )
        print(
            f"   • 평균 실행 시간: {status['system_performance']['average_execution_time']:.1f}초"
        )

    # 비동기 테스트 실행
    asyncio.run(test_dispatcher())
