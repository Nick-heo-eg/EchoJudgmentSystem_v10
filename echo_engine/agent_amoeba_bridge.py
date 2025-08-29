import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass
from echo_engine.amoeba.amoeba_manager import AmoebaManager
from echo_engine.amoeba.plugins.base import Plugin
from echo_engine.amoeba.plugins.registry import PluginRegistry
from echo_engine.agent_registry import AgentRegistry, AgentInfo

# echo_engine/agent_amoeba_bridge.py
"""
🌌 Agent-Amoeba Bridge
- 기존 아메바 플러그인 시스템과 에이전트 시스템 통합
- 에이전트를 아메바 플러그인으로 자동 변환
- 연결성 체크, 헬스 모니터링 등 아메바 기능 활용
"""


logger = logging.getLogger(__name__)


@dataclass
class AgentPluginAdapter(Plugin):
    """에이전트를 아메바 플러그인으로 어댑팅"""

    def __init__(self, agent_info: AgentInfo):
        # 아메바 플러그인 기본 속성
        self.name = f"agent_{agent_info.name}"
        self.version = "1.0.0"
        self.api_version = "1.0"
        self.description = agent_info.description
        self.permissions = {"network": False, "files": False}  # 에이전트는 보통 안전

        # 에이전트 정보 저장
        self.agent_info = agent_info
        self._loaded = False
        self._started = False

    def load(self, manager):
        """플러그인 로드"""
        logger.info(f"🔌 Agent plugin loading: {self.agent_info.name}")
        self._loaded = True

    def start(self, manager):
        """플러그인 시작"""
        logger.info(f"▶️ Agent plugin starting: {self.agent_info.name}")
        self._started = True

    def stop(self, manager):
        """플러그인 정지"""
        logger.info(f"⏸️ Agent plugin stopping: {self.agent_info.name}")
        self._started = False

    def unload(self, manager):
        """플러그인 언로드"""
        logger.info(f"📤 Agent plugin unloading: {self.agent_info.name}")
        self._loaded = False

    def reload(self, manager):
        """플러그인 리로드"""
        logger.info(f"🔄 Agent plugin reloading: {self.agent_info.name}")
        # 에이전트는 단순하므로 stop->start로 충분
        if self._started:
            self.stop(manager)
            self.start(manager)

    def check_requirements(self) -> Dict[str, bool]:
        """의존성 확인"""
        return {"asyncio": True, "python": True}  # 에이전트는 asyncio 기반

    def is_compatible(self, api_version: str) -> bool:
        """API 호환성 확인"""
        return api_version == "1.0"

    def get_info(self) -> Dict[str, Any]:
        """플러그인 정보"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "agent_endpoint": self.agent_info.endpoint_path,
            "input_schema": self.agent_info.input_schema,
            "output_schema": self.agent_info.output_schema,
            "offline_mode": self.agent_info.offline_mode,
            "loaded": self._loaded,
            "started": self._started,
        }

    async def execute_agent(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """에이전트 실행"""
        if not self._started:
            return {"error": "Agent plugin not started", "mode": "error"}

        try:
            return await self.agent_info.stub_function(payload)
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {"error": str(e), "mode": "error"}


class AgentAmoebaManager:
    """에이전트-아메바 통합 관리자"""

    def __init__(self, amoeba_config: Dict[str, Any] = None):
        self.amoeba_config = amoeba_config or {}
        self.amoeba_manager = AmoebaManager(self.amoeba_config)
        self.agent_registry = AgentRegistry()
        self.agent_plugins: Dict[str, AgentPluginAdapter] = {}

        # 아메바 플러그인 레지스트리에 접근
        self.plugin_registry = PluginRegistry(self.amoeba_config, self.amoeba_manager)

    def initialize(self):
        """시스템 초기화"""
        logger.info("🌌 Agent-Amoeba bridge initializing...")

        # 아메바 시스템 초기화
        self.amoeba_manager.initialize()

        # 에이전트 자동 발견
        self.agent_registry.auto_discover_agents()

        # 에이전트를 아메바 플러그인으로 변환
        self._convert_agents_to_plugins()

        logger.info(
            f"✅ Agent-Amoeba bridge initialized with {len(self.agent_plugins)} agent plugins"
        )

    def _convert_agents_to_plugins(self):
        """에이전트를 아메바 플러그인으로 변환"""
        for agent_name, agent_info in self.agent_registry.agents.items():
            plugin_adapter = AgentPluginAdapter(agent_info)
            self.agent_plugins[agent_name] = plugin_adapter

            # 아메바 플러그인 레지스트리에 수동 등록
            self.plugin_registry.active_plugins[plugin_adapter.name] = plugin_adapter

            logger.info(
                f"🔄 Converted agent to plugin: {agent_name} -> {plugin_adapter.name}"
            )

    def start_all_agents(self):
        """모든 에이전트 플러그인 시작"""
        logger.info("🚀 Starting all agent plugins...")

        for plugin_name, plugin in self.agent_plugins.items():
            try:
                plugin.load(self.amoeba_manager)
                plugin.start(self.amoeba_manager)
                logger.info(f"✅ Agent plugin started: {plugin_name}")
            except Exception as e:
                logger.error(f"❌ Failed to start agent plugin {plugin_name}: {e}")

    def stop_all_agents(self):
        """모든 에이전트 플러그인 정지"""
        logger.info("⏹️ Stopping all agent plugins...")

        for plugin_name, plugin in self.agent_plugins.items():
            try:
                plugin.stop(self.amoeba_manager)
                plugin.unload(self.amoeba_manager)
                logger.info(f"✅ Agent plugin stopped: {plugin_name}")
            except Exception as e:
                logger.error(f"❌ Failed to stop agent plugin {plugin_name}: {e}")

    async def execute_agent(
        self, agent_name: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """에이전트 실행 (아메바 연결성 체크 포함)"""
        if agent_name not in self.agent_plugins:
            return {"error": f"Agent not found: {agent_name}", "mode": "error"}

        plugin = self.agent_plugins[agent_name]

        # 아메바 연결성 체크
        connectivity_status = self._check_agent_connectivity(agent_name)
        if not connectivity_status["healthy"]:
            logger.warning(f"⚠️ Agent connectivity issues: {agent_name}")
            # 여전히 실행은 시도하되, 응답에 경고 포함

        # 에이전트 실행
        result = await plugin.execute_agent(payload)

        # 아메바 텔레메트리 기록
        self._record_telemetry(agent_name, payload, result)

        # 연결성 정보 추가
        if not connectivity_status["healthy"]:
            result["connectivity_warning"] = connectivity_status["issues"]

        return result

    def _check_agent_connectivity(self, agent_name: str) -> Dict[str, Any]:
        """아메바 시스템을 이용한 에이전트 연결성 체크"""
        try:
            # 아메바의 환경 감지 및 연결 체크 활용
            env_info = self.amoeba_manager.env_info

            # 기본 연결성 체크
            issues = []

            # 메모리 체크
            if env_info.get("memory", {}).get("available_mb", 0) < 100:
                issues.append("Low memory")

            # 디스크 체크
            if env_info.get("disk", {}).get("available_gb", 0) < 1:
                issues.append("Low disk space")

            # 네트워크 체크 (아메바 어댑터 활용)
            if self.amoeba_manager.adapter and hasattr(
                self.amoeba_manager.adapter, "check_network"
            ):
                if not self.amoeba_manager.adapter.check_network():
                    issues.append("Network connectivity issues")

            return {"healthy": len(issues) == 0, "issues": issues, "env_info": env_info}

        except Exception as e:
            logger.error(f"Connectivity check failed for {agent_name}: {e}")
            return {
                "healthy": False,
                "issues": [f"Connectivity check error: {str(e)}"],
                "env_info": {},
            }

    def _record_telemetry(
        self, agent_name: str, payload: Dict[str, Any], result: Dict[str, Any]
    ):
        """아메바 텔레메트리에 에이전트 실행 기록"""
        try:
            telemetry_data = {
                "agent": agent_name,
                "input_size": len(str(payload)),
                "output_size": len(str(result)),
                "mode": result.get("mode", "unknown"),
                "success": "error" not in result,
            }

            # 아메바 텔레메트리 시스템에 기록
            self.amoeba_manager.telemetry.record_event(
                "agent_execution", telemetry_data
            )

        except Exception as e:
            logger.debug(f"Telemetry recording failed: {e}")

    def get_agent_status(self) -> Dict[str, Any]:
        """모든 에이전트 상태 (아메바 스타일)"""
        status = {
            "amoeba_info": self.amoeba_manager.get_system_status(),
            "agent_plugins": {},
            "connectivity": {},
            "telemetry_summary": {},
        }

        for agent_name, plugin in self.agent_plugins.items():
            # 플러그인 상태
            status["agent_plugins"][agent_name] = plugin.get_info()

            # 연결성 상태
            status["connectivity"][agent_name] = self._check_agent_connectivity(
                agent_name
            )

        # 텔레메트리 요약
        try:
            status["telemetry_summary"] = self.amoeba_manager.telemetry.get_summary()
        except:
            status["telemetry_summary"] = {"error": "telemetry unavailable"}

        return status

    def get_available_endpoints(self) -> List[Dict[str, Any]]:
        """사용 가능한 에이전트 엔드포인트 목록"""
        endpoints = []

        for agent_name, agent_info in self.agent_registry.agents.items():
            plugin = self.agent_plugins.get(agent_name)
            connectivity = self._check_agent_connectivity(agent_name)

            endpoints.append(
                {
                    "agent": agent_name,
                    "endpoint": agent_info.endpoint_path,
                    "description": agent_info.description,
                    "input_schema": agent_info.input_schema,
                    "healthy": connectivity["healthy"],
                    "plugin_loaded": plugin._loaded if plugin else False,
                    "plugin_started": plugin._started if plugin else False,
                }
            )

        return endpoints


# 글로벌 브리지 인스턴스
_agent_amoeba_bridge: Optional[AgentAmoebaManager] = None


def get_agent_amoeba_bridge(amoeba_config: Dict[str, Any] = None) -> AgentAmoebaManager:
    """에이전트-아메바 브리지 싱글톤"""
    global _agent_amoeba_bridge
    if _agent_amoeba_bridge is None:
        _agent_amoeba_bridge = AgentAmoebaManager(amoeba_config)
        _agent_amoeba_bridge.initialize()
    return _agent_amoeba_bridge
