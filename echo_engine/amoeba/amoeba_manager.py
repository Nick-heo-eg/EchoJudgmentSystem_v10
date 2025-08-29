from __future__ import annotations
import logging
import os
import platform
from typing import Any, Dict, Optional
from echo_engine.amoeba.adapters.cloud_adapter import CloudAdapter
from echo_engine.amoeba.adapters.docker_adapter import DockerAdapter  
from echo_engine.amoeba.adapters.local_adapter import LocalAdapter
from echo_engine.amoeba.adapters.wsl_adapter import WSLAdapter
from echo_engine.amoeba.env_detect import detect_comprehensive_environment
from echo_engine.amoeba.linker import Linker
from echo_engine.amoeba.optimizer import Optimizer
from echo_engine.amoeba.plugins.registry import PluginRegistry
from echo_engine.amoeba.security import SecurityManager
from echo_engine.amoeba.telemetry import Telemetry

"""
🌌 Amoeba Manager v0.2
Echo Judgment System의 환경 감지 및 자동 연결 관리자 (적응형)
"""




log = logging.getLogger("amoeba")


class AmoebaManager:
    """Amoeba v0.2 시스템의 핵심 관리자"""

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self.env_info: Dict[str, Any] = {}
        self.adapter: Optional[Any] = None

        # 로그 레벨 설정
        log_level = self.config.get("log_level", "info").upper()
        log.setLevel(getattr(logging, log_level, logging.INFO))

        # v0.2 컴포넌트 초기화
        self.linker = Linker(self.config)
        self.optimizer = Optimizer(self.config)
        self.telemetry = Telemetry(self.config)
        self.security = SecurityManager(self.config)
        self.plugins: Optional[PluginRegistry] = None

        # 어댑터 목록 (우선순위 순)
        self.available_adapters = [
            DockerAdapter(),  # priority: 9
            WSLAdapter(),  # priority: 8
            CloudAdapter(),  # priority: 7
            LocalAdapter(),  # priority: 1 (기본값)
        ]

        log.info("🟪 AmoebaManager v0.2 초기화")
        self.telemetry.log_event(
            "amoeba_manager.initialized",
            {"version": "0.2", "config_keys": list(self.config.keys())},
        )

    def detect_environment(self) -> Dict[str, Any]:
        """현재 실행 환경을 종합적으로 감지합니다."""
        log.info("🔍 환경 감지 시작...")

        # 종합적 환경 감지
        self.env_info = detect_comprehensive_environment()

        # 로그 출력
        os_info = self.env_info.get("os", {})
        python_info = self.env_info.get("python", {})
        runtime_info = self.env_info.get("runtime", {})

        log.info(
            f"💻 OS: {os_info.get('system', 'Unknown')} ({os_info.get('release', 'Unknown')})"
        )
        log.info(f"🐍 Python: {python_info.get('version', 'Unknown')}")

        if runtime_info.get("is_wsl"):
            log.info("🐧 WSL 환경 감지")
        if runtime_info.get("is_docker"):
            log.info("🐳 Docker 환경 감지")
        if runtime_info.get("is_cloud"):
            provider = runtime_info.get("provider", "Unknown")
            log.info(f"☁️ 클라우드 환경 감지: {provider.upper()}")

        # GPU 정보
        gpu_info = self.env_info.get("capabilities", {})
        if gpu_info.get("has_gpu"):
            gpu_count = len(gpu_info.get("gpus", []))
            log.info(f"🎮 GPU 감지: {gpu_count}개")

        # 어댑터 선택
        self.adapter = self.select_adapter()

        # 텔레메트리 이벤트 기록
        self.telemetry.log_event(
            "environment.detected",
            {
                "os": os_info.get("system"),
                "python": python_info.get("version"),
                "adapter": self.adapter.name if self.adapter else "none",
                "runtime_flags": {
                    "wsl": runtime_info.get("is_wsl", False),
                    "docker": runtime_info.get("is_docker", False),
                    "cloud": runtime_info.get("is_cloud", False),
                    "gpu": gpu_info.get("has_gpu", False),
                },
            },
        )

        log.debug("env_info=%s", self.env_info)
        return self.env_info

    def select_adapter(self):
        """환경에 적합한 어댑터 선택"""
        environment_preference = self.config.get("environment", {}).get(
            "prefer", "auto"
        )

        if environment_preference != "auto":
            # 명시적 어댑터 지정
            adapter_map = {
                "wsl": WSLAdapter(),
                "docker": DockerAdapter(),
                "local": LocalAdapter(),
                "cloud": CloudAdapter(),
            }

            selected = adapter_map.get(environment_preference)
            if selected and selected.detect():
                log.info(f"🎯 명시적 어댑터 선택: {selected.name}")
                return selected
            else:
                log.warning(
                    f"⚠️ 지정된 어댑터 사용 불가: {environment_preference}, 자동 선택으로 전환"
                )

        # 자동 선택 (우선순위 순)
        sorted_adapters = sorted(
            self.available_adapters, key=lambda a: a.priority, reverse=True
        )

        for adapter in sorted_adapters:
            if adapter.detect():
                log.info(
                    f"✅ 어댑터 자동 선택: {adapter.name} (우선순위: {adapter.priority})"
                )
                return adapter

        # 기본값 (Local)
        log.warning("⚠️ 적합한 어댑터를 찾을 수 없음, Local 어댑터 사용")
        return LocalAdapter()

    def attach(self) -> bool:
        """Echo 시스템의 다양한 컴포넌트들을 어댑터를 통해 연결합니다."""
        log.info("🔗 Amoeba 시스템 연결 시작...")

        try:
            # 어댑터 기반 연결
            if self.adapter:
                log.info(f"🔧 {self.adapter.name} 어댑터 사용")

                # 1. 연결 전 준비
                self.adapter.prelink(self)

                # 2. 실제 연결 수행
                self.adapter.link(self)

                # 텔레메트리 이벤트
                self.telemetry.log_event(
                    "adapter.attached",
                    {
                        "adapter": self.adapter.name,
                        "services": self.linker.service_registry.list_services(),
                    },
                )

            # 텔레메트리 모니터링 시작 (attach 시점에)
            if hasattr(self.telemetry, "start_monitoring"):
                self.telemetry.start_monitoring()

            # 플러그인 시스템 초기화 (설정에 따라)
            plugins_config = self.config.get("plugins", {})
            if plugins_config and plugins_config.get("discovery_paths"):
                self.plugins = PluginRegistry(self.config, self)
                self.plugins.auto_load_plugins()

                self.telemetry.log_event(
                    "plugins.initialized",
                    {
                        "active_count": len(self.plugins.active_plugins),
                        "failed_count": len(self.plugins.failed_plugins),
                    },
                )
            else:
                log.info("🔌 플러그인 시스템 비활성화")

            log.info("✅ Amoeba 시스템 연결 완료")
            return True

        except Exception as e:
            log.error(f"❌ 시스템 연결 실패: {e}")
            self.telemetry.log_event("attach.failed", {"error": str(e)})
            return False

    def optimize(self) -> Dict[str, Any]:
        """어댑터를 통한 환경별 최적화를 수행합니다."""
        log.info("⚡ Amoeba 시스템 최적화 시작...")

        try:
            # 어댑터 기반 최적화
            if self.adapter:
                log.info(f"🔧 {self.adapter.name} 어댑터 최적화")
                self.adapter.optimize(self)

            # 최적화 결과 수집
            optimization_report = self.optimizer.get_optimization_report()

            # 텔레메트리 이벤트
            self.telemetry.log_event(
                "optimization.completed",
                {
                    "adapter": self.adapter.name if self.adapter else "none",
                    "optimizations_count": len(
                        optimization_report.get("optimizations_applied", [])
                    ),
                    "performance_metrics": optimization_report.get(
                        "performance_metrics", {}
                    ),
                },
            )

            log.info("✅ Amoeba 시스템 최적화 완료")
            return optimization_report

        except Exception as e:
            log.error(f"❌ 시스템 최적화 실패: {e}")
            self.telemetry.log_event("optimization.failed", {"error": str(e)})
            return {"status": "failed", "error": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Amoeba v0.2 시스템의 종합 상태를 반환합니다."""
        status = {
            "version": "0.2",
            "config": self.config,
            "environment": self.env_info,
            "adapter": self.adapter.get_info() if self.adapter else None,
            "linker": self.linker.get_status() if self.linker else {},
            "optimizer": (
                self.optimizer.get_optimization_report() if self.optimizer else {}
            ),
            "telemetry": self.telemetry.collector.get_stats() if self.telemetry else {},
            "plugins": (
                self.plugins.get_status()
                if self.plugins
                else {"active_count": 0, "failed_count": 0}
            ),
            "timestamp": platform.node(),
        }

        return status

    def shutdown(self):
        """Amoeba 시스템을 안전하게 종료합니다."""
        log.info("🔻 Amoeba 시스템 종료 시작...")

        try:
            # 플러그인 정지 및 언로드
            if self.plugins:
                self.plugins.unload_all()

            # 텔레메트리 모니터링 중지 및 종료
            if self.telemetry:
                if hasattr(self.telemetry, "stop_monitoring"):
                    self.telemetry.stop_monitoring()
                if hasattr(self.telemetry, "shutdown"):
                    self.telemetry.shutdown()

            # 어댑터 정리 (필요시)
            self.adapter = None

            log.info("✅ Amoeba 시스템 종료 완료")

        except Exception as e:
            log.error(f"❌ 시스템 종료 중 오류: {e}")

    def reload_plugins(self):
        """플러그인 시스템 리로드"""
        if self.plugins:
            log.info("🔄 플러그인 시스템 리로드...")
            self.plugins.unload_all()
            self.plugins.auto_load_plugins()

            self.telemetry.log_event(
                "plugins.reloaded",
                {
                    "active_count": len(self.plugins.active_plugins),
                    "failed_count": len(self.plugins.failed_plugins),
                },
            )
        else:
            log.warning("⚠️ 플러그인 시스템이 초기화되지 않음")
