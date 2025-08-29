# echo_engine/agent_registry.py
"""
🔌 Echo Agent Plugin Registry
- 에이전트 자동 발견 및 등록
- 플러그인 방식으로 새 에이전트 추가 가능
"""
import os
import importlib
import inspect
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentInfo:
    """에이전트 정보"""

    name: str
    module_path: str
    stub_function: Callable
    full_function: Optional[Callable]
    endpoint_path: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    offline_mode: bool = True


class AgentRegistry:
    """에이전트 레지스트리"""

    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.endpoints: Dict[str, str] = {}  # endpoint -> agent_name 매핑

    def register_agent(self, agent_info: AgentInfo):
        """에이전트 수동 등록"""
        self.agents[agent_info.name] = agent_info
        self.endpoints[agent_info.endpoint_path] = agent_info.name
        logger.info(
            f"✅ Agent registered: {agent_info.name} -> {agent_info.endpoint_path}"
        )

    def auto_discover_agents(self, agents_dir: str = "echo_engine/agents"):
        """에이전트 자동 발견 및 등록"""
        agents_path = Path(agents_dir)
        if not agents_path.exists():
            logger.warning(f"Agents directory not found: {agents_dir}")
            # 폴백: 코어 에이전트 셋 자동 등록
            self._register_core_agent_set()
            return

        for agent_file in agents_path.glob("*_agent.py"):
            try:
                self._discover_agent_from_file(agent_file, agents_dir)
            except Exception as e:
                logger.error(f"Failed to discover agent from {agent_file}: {e}")

    def _discover_agent_from_file(self, agent_file: Path, agents_dir: str):
        """파일에서 에이전트 발견"""
        module_name = agent_file.stem
        module_path = f"{agents_dir.replace('/', '.')}.{module_name}"

        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            logger.debug(f"Could not import {module_path}: {e}")
            return

        # 에이전트 스텁 함수 찾기 (규칙: async def agent_name(spec) -> dict)
        for name, obj in inspect.getmembers(module):
            if (
                inspect.iscoroutinefunction(obj)
                and not name.startswith("_")
                and name not in ["execute_task", "get_capabilities"]
            ):

                # 함수 시그니처 검사
                sig = inspect.signature(obj)
                if len(sig.parameters) >= 1:
                    agent_name = self._extract_agent_name(module_name, name)
                    endpoint_path = f"/{agent_name.replace('_', '-')}"

                    agent_info = AgentInfo(
                        name=agent_name,
                        module_path=module_path,
                        stub_function=obj,
                        full_function=None,  # 나중에 풀모드에서 설정
                        endpoint_path=endpoint_path,
                        description=obj.__doc__ or f"{agent_name} agent",
                        input_schema=self._extract_input_schema(sig),
                        output_schema={
                            "type": "object",
                            "description": "Agent response",
                        },
                        offline_mode=True,
                    )

                    self.register_agent(agent_info)
                    break  # 파일당 하나의 주요 함수만

    def _extract_agent_name(self, module_name: str, function_name: str) -> str:
        """에이전트 이름 추출"""
        # code_generator_agent.py의 generate_code -> code_generator
        if module_name.endswith("_agent"):
            return module_name[:-6]  # '_agent' 제거
        return function_name

    def _extract_input_schema(self, sig: inspect.Signature) -> Dict[str, Any]:
        """입력 스키마 추출"""
        schema = {"type": "object", "properties": {}, "required": []}

        for param_name, param in sig.parameters.items():
            if param_name in ["self", "cls"]:
                continue

            param_schema = {"type": "object"}
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == str:
                    param_schema["type"] = "string"
                elif param.annotation == int:
                    param_schema["type"] = "integer"
                elif param.annotation == float:
                    param_schema["type"] = "number"
                elif param.annotation == bool:
                    param_schema["type"] = "boolean"

            schema["properties"][param_name] = param_schema

            if param.default == inspect.Parameter.empty:
                schema["required"].append(param_name)

        return schema

    async def call_agent(
        self, agent_name: str, payload: Dict[str, Any], offline_mode: bool = True
    ) -> Dict[str, Any]:
        """에이전트 호출"""
        if agent_name not in self.agents:
            return {"error": f"Agent not found: {agent_name}", "mode": "error"}

        agent_info = self.agents[agent_name]

        try:
            if offline_mode or agent_info.offline_mode:
                # 오프라인 스텁 호출
                result = await agent_info.stub_function(payload)
            else:
                # 풀모드 호출 (나중에 구현)
                if agent_info.full_function:
                    result = await agent_info.full_function(payload)
                else:
                    result = await agent_info.stub_function(payload)

            return result

        except Exception as e:
            logger.error(f"Agent {agent_name} failed: {e}")
            return {
                "error": f"Agent execution failed: {str(e)}",
                "mode": "error",
                "agent": agent_name,
            }

    def get_agent_by_endpoint(self, endpoint_path: str) -> Optional[AgentInfo]:
        """엔드포인트로 에이전트 찾기"""
        agent_name = self.endpoints.get(endpoint_path)
        if agent_name:
            return self.agents.get(agent_name)
        return None

    def list_agents(self) -> List[Dict[str, Any]]:
        """등록된 에이전트 목록"""
        return [
            {
                "name": agent.name,
                "endpoint": agent.endpoint_path,
                "description": agent.description,
                "offline_mode": agent.offline_mode,
                "input_schema": agent.input_schema,
            }
            for agent in self.agents.values()
        ]

    def get_openapi_paths(self) -> Dict[str, Any]:
        """OpenAPI 경로 정의 생성"""
        paths = {}

        for agent in self.agents.values():
            paths[agent.endpoint_path] = {
                "post": {
                    "summary": agent.description,
                    "description": f"Execute {agent.name} agent",
                    "requestBody": {
                        "content": {"application/json": {"schema": agent.input_schema}}
                    },
                    "responses": {
                        "200": {
                            "description": "Agent response",
                            "content": {
                                "application/json": {"schema": agent.output_schema}
                            },
                        }
                    },
                    "tags": ["agents"],
                }
            }

        return paths

    def _register_core_agent_set(self):
        """코어 에이전트 셋 등록 (16개 기본 에이전트)"""
        logger.info("🌌 Registering core agent set (16 agents)...")

        core_agents = [
            "code_generator",
            "refactorer",
            "designer",
            "shell_runner",
            "git_helper",
            "fs_manager",
            "http_client",
            "sql_helper",
            "web_scraper",
            "report_builder",
            "risk_matrix",
            "abc_analyzer",
            "signature_responder",
            "capsule_writer",
            "timeline_logger",
            "visualizer",
        ]

        for agent_name in core_agents:
            agent_info = AgentInfo(
                name=agent_name,
                module_path=f"echo_engine.agents.{agent_name}_agent",
                stub_function=self._create_stub_function(agent_name),
                full_function=None,
                endpoint_path=f"/{agent_name.replace('_', '-')}",
                description=f"Core {agent_name} agent",
                input_schema={
                    "type": "object",
                    "properties": {"spec": {"type": "object"}},
                    "required": ["spec"],
                },
                output_schema={
                    "type": "object",
                    "properties": {"result": {"type": "object"}},
                },
                offline_mode=True,
            )
            self.register_agent(agent_info)

    def _create_stub_function(self, agent_name: str):
        """코어 에이전트용 스텁 함수 생성"""

        async def core_agent_stub(spec):
            return {
                "agent": agent_name,
                "mode": "core_fallback",
                "result": f"Core {agent_name} executed",
                "spec_received": spec,
                "timestamp": str(__import__("datetime").datetime.now()),
            }

        return core_agent_stub


# 글로벌 레지스트리 인스턴스
_agent_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """에이전트 레지스트리 싱글톤"""
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
        # 자동 발견 실행
        _agent_registry.auto_discover_agents()
    return _agent_registry


def register_agent_decorator(name: str, endpoint: str = None, description: str = None):
    """에이전트 등록 데코레이터"""

    def decorator(func):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError("Agent function must be async")

        endpoint_path = endpoint or f"/{name.replace('_', '-')}"
        sig = inspect.signature(func)

        agent_info = AgentInfo(
            name=name,
            module_path=func.__module__,
            stub_function=func,
            full_function=None,
            endpoint_path=endpoint_path,
            description=description or func.__doc__ or f"{name} agent",
            input_schema=get_agent_registry()._extract_input_schema(sig),
            output_schema={"type": "object", "description": "Agent response"},
            offline_mode=True,
        )

        get_agent_registry().register_agent(agent_info)
        return func

    return decorator
