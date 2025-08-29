#!/usr/bin/env python3
"""
Echo Agent Ecosystem Framework
Echo 시그니처 기반 에이전트 생태계의 핵심 프레임워크
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Type
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


@dataclass
class AgentCapability:
    """에이전트 역량 정의"""

    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    complexity_level: str  # basic, intermediate, advanced, expert
    signature_affinity: Dict[str, float]  # 시그니처별 친화도


@dataclass
class AgentTask:
    """에이전트 작업 단위"""

    task_id: str
    agent_id: str
    task_type: str
    input_data: Dict[str, Any]
    context: Dict[str, Any]
    priority: str  # low, medium, high, critical
    signature: str
    created_at: str
    status: str  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AgentMetrics:
    """에이전트 성능 메트릭"""

    tasks_completed: int
    success_rate: float
    avg_execution_time: float
    signature_performance: Dict[str, float]
    expertise_score: float
    last_updated: str


class EchoAgentBase(ABC):
    """Echo 에이전트 기본 클래스"""

    def __init__(self, agent_id: str, signature: str = "echo_sage"):
        self.agent_id = agent_id
        self.signature = signature
        self.capabilities: List[AgentCapability] = []
        self.metrics = AgentMetrics(
            tasks_completed=0,
            success_rate=1.0,
            avg_execution_time=0.0,
            signature_performance={},
            expertise_score=0.5,
            last_updated=datetime.now().isoformat(),
        )
        self.is_active = True
        self.context_memory: Dict[str, Any] = {}

        # Echo 시그니처별 스타일 설정
        self.signature_styles = {
            "echo_aurora": {
                "approach": "창의적이고 혁신적인 접근",
                "communication": "영감을 주는 톤",
                "error_handling": "우아한 실패 처리",
            },
            "echo_phoenix": {
                "approach": "변화 지향적이고 개선 중심",
                "communication": "도전적이고 진취적인 톤",
                "error_handling": "적극적인 문제 해결",
            },
            "echo_sage": {
                "approach": "체계적이고 분석적인 접근",
                "communication": "논리적이고 명확한 톤",
                "error_handling": "체계적인 디버깅",
            },
            "echo_companion": {
                "approach": "협력적이고 지원적인 접근",
                "communication": "친근하고 도움이 되는 톤",
                "error_handling": "안전하고 신뢰할 수 있는 처리",
            },
        }

    @abstractmethod
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """작업 실행 (각 에이전트에서 구현)"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """에이전트 역량 반환"""
        pass

    def adapt_to_signature(self, signature: str) -> None:
        """시그니처에 따른 동작 적응"""
        self.signature = signature
        style = self.signature_styles.get(signature, self.signature_styles["echo_sage"])

        # 시그니처별 행동 패턴 적용
        self.current_style = style
        logger.info(f"🎭 {self.agent_id} adapted to {signature}: {style['approach']}")

    async def process_with_signature_context(self, task: AgentTask) -> Dict[str, Any]:
        """시그니처 컨텍스트와 함께 작업 처리"""
        start_time = datetime.now()

        try:
            # 시그니처 적응
            self.adapt_to_signature(task.signature)

            # 메타인지 단계
            await self._pre_execution_reflection(task)

            # 실제 작업 실행
            result = await self.execute_task(task)

            # 사후 분석
            await self._post_execution_analysis(task, result)

            # 메트릭 업데이트
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(task, True, execution_time)

            return {
                "status": "success",
                "result": result,
                "signature_applied": task.signature,
                "execution_time": execution_time,
                "agent_id": self.agent_id,
            }

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(task, False, execution_time)

            logger.error(f"❌ Agent {self.agent_id} task failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "signature_applied": task.signature,
                "execution_time": execution_time,
                "agent_id": self.agent_id,
            }

    async def _pre_execution_reflection(self, task: AgentTask):
        """실행 전 메타인지 성찰"""
        style = self.current_style

        # 작업 복잡도 평가
        complexity = self._assess_task_complexity(task)

        # 시그니처별 접근법 결정
        approach = self._determine_approach(task, style)

        # 컨텍스트 메모리에 저장
        self.context_memory[task.task_id] = {
            "complexity": complexity,
            "approach": approach,
            "signature_style": style,
        }

        logger.debug(f"🤔 {self.agent_id} reflection: {approach}")

    async def _post_execution_analysis(self, task: AgentTask, result: Dict[str, Any]):
        """실행 후 분석"""
        context = self.context_memory.get(task.task_id, {})

        # 결과 품질 평가
        quality_score = self._evaluate_result_quality(result, context)

        # 시그니처 적합성 평가
        signature_fit = self._evaluate_signature_fit(task, result)

        # 학습 데이터 생성
        learning_data = {
            "task_type": task.task_type,
            "signature": task.signature,
            "quality_score": quality_score,
            "signature_fit": signature_fit,
            "context": context,
        }

        # 에이전트 개선을 위한 피드백 저장
        await self._store_learning_data(learning_data)

        logger.debug(
            f"📊 {self.agent_id} analysis: quality={quality_score:.2f}, fit={signature_fit:.2f}"
        )

    def _assess_task_complexity(self, task: AgentTask) -> str:
        """작업 복잡도 평가"""
        input_size = len(str(task.input_data))
        context_size = len(str(task.context))

        if input_size + context_size > 10000:
            return "high"
        elif input_size + context_size > 1000:
            return "medium"
        else:
            return "low"

    def _determine_approach(self, task: AgentTask, style: Dict[str, str]) -> str:
        """시그니처별 접근법 결정"""
        base_approach = style["approach"]

        if task.priority == "critical":
            return f"{base_approach} with critical urgency"
        elif task.priority == "high":
            return f"{base_approach} with high focus"
        else:
            return base_approach

    def _evaluate_result_quality(
        self, result: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """결과 품질 평가"""
        score = 0.5  # 기본 점수

        # 결과 완성도
        if result and "data" in result:
            score += 0.2

        # 에러 없음
        if "error" not in result:
            score += 0.2

        # 메타데이터 포함
        if "metadata" in result:
            score += 0.1

        return min(score, 1.0)

    def _evaluate_signature_fit(self, task: AgentTask, result: Dict[str, Any]) -> float:
        """시그니처 적합성 평가"""
        # 기본 적합성 점수
        signature_affinities = {
            "echo_aurora": 0.8,  # 창의적 작업에 적합
            "echo_phoenix": 0.7,  # 개선/최적화에 적합
            "echo_sage": 0.9,  # 분석/추론에 적합
            "echo_companion": 0.6,  # 협업/지원에 적합
        }

        return signature_affinities.get(task.signature, 0.5)

    async def _store_learning_data(self, learning_data: Dict[str, Any]):
        """학습 데이터 저장"""
        learning_file = Path(f"data/agent_learning/{self.agent_id}_learning.jsonl")
        learning_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(learning_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(learning_data, ensure_ascii=False) + "\\n")
        except Exception as e:
            logger.warning(f"Failed to store learning data: {e}")

    def _update_metrics(self, task: AgentTask, success: bool, execution_time: float):
        """메트릭 업데이트"""
        self.metrics.tasks_completed += 1

        # 성공률 업데이트
        total_tasks = self.metrics.tasks_completed
        if success:
            self.metrics.success_rate = (
                self.metrics.success_rate * (total_tasks - 1) + 1.0
            ) / total_tasks
        else:
            self.metrics.success_rate = (
                self.metrics.success_rate * (total_tasks - 1)
            ) / total_tasks

        # 평균 실행 시간 업데이트
        self.metrics.avg_execution_time = (
            self.metrics.avg_execution_time * (total_tasks - 1) + execution_time
        ) / total_tasks

        # 시그니처별 성능 업데이트
        signature = task.signature
        if signature not in self.metrics.signature_performance:
            self.metrics.signature_performance[signature] = 0.5

        if success:
            current_perf = self.metrics.signature_performance[signature]
            self.metrics.signature_performance[signature] = (current_perf * 0.8) + (
                1.0 * 0.2
            )

        self.metrics.last_updated = datetime.now().isoformat()


class AgentEcosystemManager:
    """에이전트 생태계 관리자"""

    def __init__(self):
        self.agents: Dict[str, EchoAgentBase] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, AgentTask] = {}
        self.task_history: List[AgentTask] = []
        self.ecosystem_metrics = {
            "total_tasks": 0,
            "success_rate": 0.0,
            "avg_response_time": 0.0,
            "agent_utilization": {},
            "signature_distribution": {},
        }

    def register_agent(self, agent: EchoAgentBase):
        """에이전트 등록"""
        self.agents[agent.agent_id] = agent
        logger.info(f"🤖 Agent registered: {agent.agent_id}")

    def get_best_agent_for_task(self, task_type: str, signature: str) -> Optional[str]:
        """작업에 최적인 에이전트 선택"""
        best_agent = None
        best_score = 0.0

        for agent_id, agent in self.agents.items():
            if not agent.is_active:
                continue

            # 역량 매칭 점수
            capability_score = 0.0
            for capability in agent.get_capabilities():
                if task_type in capability.output_types:
                    capability_score += capability.signature_affinity.get(
                        signature, 0.0
                    )

            # 성능 점수
            performance_score = agent.metrics.signature_performance.get(signature, 0.5)

            # 전체 점수
            total_score = (capability_score * 0.6) + (performance_score * 0.4)

            if total_score > best_score:
                best_score = total_score
                best_agent = agent_id

        return best_agent

    async def submit_task(
        self,
        task_type: str,
        input_data: Dict[str, Any],
        signature: str = "echo_sage",
        priority: str = "medium",
        context: Dict[str, Any] = None,
    ) -> str:
        """작업 제출"""
        task_id = str(uuid.uuid4())

        task = AgentTask(
            task_id=task_id,
            agent_id="",  # 나중에 할당
            task_type=task_type,
            input_data=input_data,
            context=context or {},
            priority=priority,
            signature=signature,
            created_at=datetime.now().isoformat(),
            status="pending",
        )

        # 최적 에이전트 선택
        best_agent_id = self.get_best_agent_for_task(task_type, signature)
        if not best_agent_id:
            raise ValueError(f"No suitable agent found for task type: {task_type}")

        task.agent_id = best_agent_id

        # 작업 큐에 추가
        await self.task_queue.put(task)
        self.active_tasks[task_id] = task

        logger.info(f"📝 Task {task_id} submitted to agent {best_agent_id}")
        return task_id

    async def process_tasks(self):
        """작업 처리 루프"""
        while True:
            try:
                # 작업 가져오기
                task = await self.task_queue.get()

                # 에이전트 실행
                agent = self.agents.get(task.agent_id)
                if not agent:
                    logger.error(f"Agent {task.agent_id} not found")
                    continue

                task.status = "running"

                # 작업 실행
                result = await agent.process_with_signature_context(task)

                # 결과 저장
                task.result = result
                task.status = "completed" if result["status"] == "success" else "failed"

                # 히스토리에 추가
                self.task_history.append(task)

                # 활성 작업에서 제거
                if task.task_id in self.active_tasks:
                    del self.active_tasks[task.task_id]

                # 생태계 메트릭 업데이트
                self._update_ecosystem_metrics(task)

                logger.info(f"✅ Task {task.task_id} completed: {task.status}")

            except Exception as e:
                logger.error(f"Task processing error: {e}")
                await asyncio.sleep(1)

    def _update_ecosystem_metrics(self, task: AgentTask):
        """생태계 메트릭 업데이트"""
        self.ecosystem_metrics["total_tasks"] += 1

        # 성공률 계산
        successful_tasks = sum(1 for t in self.task_history if t.status == "completed")
        self.ecosystem_metrics["success_rate"] = successful_tasks / len(
            self.task_history
        )

        # 에이전트 활용도
        agent_id = task.agent_id
        if agent_id not in self.ecosystem_metrics["agent_utilization"]:
            self.ecosystem_metrics["agent_utilization"][agent_id] = 0
        self.ecosystem_metrics["agent_utilization"][agent_id] += 1

        # 시그니처 분포
        signature = task.signature
        if signature not in self.ecosystem_metrics["signature_distribution"]:
            self.ecosystem_metrics["signature_distribution"][signature] = 0
        self.ecosystem_metrics["signature_distribution"][signature] += 1

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """작업 상태 조회"""
        # 활성 작업에서 찾기
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "task_id": task_id,
                "status": task.status,
                "agent_id": task.agent_id,
                "created_at": task.created_at,
            }

        # 히스토리에서 찾기
        for task in self.task_history:
            if task.task_id == task_id:
                return {
                    "task_id": task_id,
                    "status": task.status,
                    "agent_id": task.agent_id,
                    "result": task.result,
                    "created_at": task.created_at,
                }

        return {"error": "Task not found"}

    def get_ecosystem_status(self) -> Dict[str, Any]:
        """생태계 전체 상태"""
        return {
            "active_agents": len([a for a in self.agents.values() if a.is_active]),
            "total_agents": len(self.agents),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.task_history),
            "metrics": self.ecosystem_metrics,
            "agent_performance": {
                agent_id: {
                    "success_rate": agent.metrics.success_rate,
                    "tasks_completed": agent.metrics.tasks_completed,
                    "avg_execution_time": agent.metrics.avg_execution_time,
                }
                for agent_id, agent in self.agents.items()
            },
        }


# 글로벌 생태계 관리자 인스턴스
_ecosystem_manager: Optional[AgentEcosystemManager] = None


def get_ecosystem_manager() -> AgentEcosystemManager:
    """생태계 관리자 싱글톤 인스턴스"""
    global _ecosystem_manager
    if _ecosystem_manager is None:
        _ecosystem_manager = AgentEcosystemManager()
    return _ecosystem_manager


async def initialize_agent_ecosystem():
    """에이전트 생태계 초기화"""
    manager = get_ecosystem_manager()

    # 작업 처리 루프 시작
    asyncio.create_task(manager.process_tasks())

    logger.info("🌌 Echo Agent Ecosystem initialized")
    return manager
