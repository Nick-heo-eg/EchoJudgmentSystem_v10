# echo_ide/core/role_based_controllers.py
"""
🎭 Echo IDE 역할 기반 제어 시스템
권한별 기능 제어 및 역할 위임 관리

지원하는 역할:
- 코드 생성 전용 역할 (CodeGeneratorRole)
- 시스템 제어 전용 역할 (SystemControllerRole)
- 분석 전용 어시스턴트 (AnalystAssistantRole)
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
import queue


class PermissionLevel(Enum):
    """권한 레벨"""

    NONE = 0
    READ_ONLY = 1
    LIMITED_WRITE = 2
    FULL_ACCESS = 3
    ADMIN = 4


class RoleType(Enum):
    """역할 타입"""

    CODE_GENERATOR = "code_generator"
    SYSTEM_CONTROLLER = "system_controller"
    ANALYST_ASSISTANT = "analyst_assistant"
    GENERAL_ASSISTANT = "general_assistant"


@dataclass
class RoleCapability:
    """역할 능력 정의"""

    capability_id: str
    name: str
    description: str
    permission_level: PermissionLevel
    allowed_operations: List[str]
    restricted_areas: List[str]
    resource_limits: Dict[str, Any]


@dataclass
class RoleSession:
    """역할 세션 정보"""

    session_id: str
    role_type: RoleType
    start_time: datetime
    expiry_time: Optional[datetime]
    active: bool
    capabilities: List[RoleCapability]
    context: Dict[str, Any]
    operation_log: List[Dict[str, Any]]


class BaseRoleController:
    """기본 역할 제어자"""

    def __init__(self, ide_instance, role_type: RoleType):
        self.ide = ide_instance
        self.role_type = role_type
        self.session = None
        self.operation_queue = queue.Queue()
        self.permission_cache = {}

        # 기본 능력 설정
        self.base_capabilities = self._define_base_capabilities()

        # 작업 제한
        self.rate_limits = {
            "operations_per_minute": 30,
            "file_operations_per_hour": 100,
            "api_calls_per_hour": 50,
        }

        # 사용량 추적
        self.usage_tracker = {"operations": [], "file_ops": [], "api_calls": []}

        print(f"🎭 {role_type.value} 역할 제어자 초기화 완료")

    def _define_base_capabilities(self) -> List[RoleCapability]:
        """기본 능력 정의"""
        return [
            RoleCapability(
                capability_id="base_read",
                name="기본 읽기",
                description="파일 및 상태 읽기",
                permission_level=PermissionLevel.READ_ONLY,
                allowed_operations=["read_file", "get_status"],
                restricted_areas=[],
                resource_limits={"max_file_size": 10 * 1024 * 1024},  # 10MB
            )
        ]

    async def start_session(
        self, duration_hours: int = 24, context: Dict[str, Any] = None
    ) -> str:
        """역할 세션 시작"""

        session_id = (
            f"{self.role_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        self.session = RoleSession(
            session_id=session_id,
            role_type=self.role_type,
            start_time=datetime.now(),
            expiry_time=(
                datetime.now() + timedelta(hours=duration_hours)
                if duration_hours > 0
                else None
            ),
            active=True,
            capabilities=self.base_capabilities.copy(),
            context=context or {},
            operation_log=[],
        )

        await self._initialize_role_specific_setup()

        if hasattr(self.ide, "display_message"):
            self.ide.display_message(
                "역할세션시작",
                f"🎭 {self.role_type.value} 세션이 시작되었습니다\n세션 ID: {session_id}\n만료 시간: {self.session.expiry_time or '무제한'}",
            )

        return session_id

    async def _initialize_role_specific_setup(self):
        """역할별 특화 설정"""
        # 상속 클래스에서 구현
        pass

    def check_permission(self, operation: str, resource: str = None) -> bool:
        """권한 확인"""

        if not self.session or not self.session.active:
            return False

        # 세션 만료 확인
        if self.session.expiry_time and datetime.now() > self.session.expiry_time:
            self.session.active = False
            return False

        # 사용량 제한 확인
        if not self._check_rate_limits():
            return False

        # 능력별 권한 확인
        for capability in self.session.capabilities:
            if operation in capability.allowed_operations:
                if resource and any(
                    restricted in resource for restricted in capability.restricted_areas
                ):
                    return False
                return True

        return False

    def _check_rate_limits(self) -> bool:
        """사용량 제한 확인"""

        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)

        # 최근 1분간 작업 수 확인
        recent_ops = [
            op
            for op in self.usage_tracker["operations"]
            if op["timestamp"] > minute_ago
        ]
        if len(recent_ops) >= self.rate_limits["operations_per_minute"]:
            return False

        # 최근 1시간 파일 작업 수 확인
        recent_file_ops = [
            op for op in self.usage_tracker["file_ops"] if op["timestamp"] > hour_ago
        ]
        if len(recent_file_ops) >= self.rate_limits["file_operations_per_hour"]:
            return False

        # 최근 1시간 API 호출 수 확인
        recent_api_calls = [
            op for op in self.usage_tracker["api_calls"] if op["timestamp"] > hour_ago
        ]
        if len(recent_api_calls) >= self.rate_limits["api_calls_per_hour"]:
            return False

        return True

    async def execute_operation(
        self, operation: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """작업 실행"""

        if not self.check_permission(
            operation, params.get("resource") if params else None
        ):
            return {
                "status": "denied",
                "message": f"권한 없음: {operation}",
                "role": self.role_type.value,
            }

        try:
            # 사용량 기록
            self._record_usage(operation, params)

            # 역할별 작업 실행
            result = await self._execute_role_specific_operation(
                operation, params or {}
            )

            # 작업 로그 기록
            self.session.operation_log.append(
                {
                    "operation": operation,
                    "params": params,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return result

        except Exception as e:
            error_result = {
                "status": "error",
                "message": f"작업 실행 오류: {e}",
                "operation": operation,
                "role": self.role_type.value,
            }

            self.session.operation_log.append(
                {
                    "operation": operation,
                    "params": params,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return error_result

    async def _execute_role_specific_operation(
        self, operation: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """역할별 특화 작업 실행"""
        # 상속 클래스에서 구현
        return {
            "status": "success",
            "message": f"기본 작업 완료: {operation}",
            "role": self.role_type.value,
        }

    def _record_usage(self, operation: str, params: Dict[str, Any] = None):
        """사용량 기록"""

        timestamp = datetime.now()

        # 전체 작업 기록
        self.usage_tracker["operations"].append(
            {"operation": operation, "timestamp": timestamp}
        )

        # 파일 작업 기록
        if any(
            file_op in operation
            for file_op in ["read_file", "write_file", "create_file", "delete_file"]
        ):
            self.usage_tracker["file_ops"].append(
                {"operation": operation, "timestamp": timestamp}
            )

        # API 호출 기록
        if any(
            api_op in operation for api_op in ["api_call", "generate_code", "analyze"]
        ):
            self.usage_tracker["api_calls"].append(
                {"operation": operation, "timestamp": timestamp}
            )

        # 오래된 기록 정리 (메모리 관리)
        cutoff_time = timestamp - timedelta(hours=24)

        for tracker_type in self.usage_tracker:
            self.usage_tracker[tracker_type] = [
                record
                for record in self.usage_tracker[tracker_type]
                if record["timestamp"] > cutoff_time
            ]

    def get_session_info(self) -> Dict[str, Any]:
        """세션 정보 조회"""

        if not self.session:
            return {"status": "no_session"}

        return {
            "session_id": self.session.session_id,
            "role_type": self.session.role_type.value,
            "active": self.session.active,
            "start_time": self.session.start_time.isoformat(),
            "expiry_time": (
                self.session.expiry_time.isoformat()
                if self.session.expiry_time
                else None
            ),
            "capabilities": [cap.capability_id for cap in self.session.capabilities],
            "operations_count": len(self.session.operation_log),
            "usage_summary": {
                "recent_operations": len(
                    [
                        op
                        for op in self.usage_tracker["operations"]
                        if op["timestamp"] > datetime.now() - timedelta(minutes=10)
                    ]
                ),
                "total_file_ops": len(self.usage_tracker["file_ops"]),
                "total_api_calls": len(self.usage_tracker["api_calls"]),
            },
        }

    def end_session(self) -> Dict[str, Any]:
        """세션 종료"""

        if not self.session:
            return {"status": "no_session"}

        session_summary = {
            "session_id": self.session.session_id,
            "duration": (datetime.now() - self.session.start_time).total_seconds(),
            "total_operations": len(self.session.operation_log),
            "role_type": self.session.role_type.value,
        }

        self.session.active = False

        if hasattr(self.ide, "display_message"):
            self.ide.display_message(
                "역할세션종료",
                f"🏁 {self.role_type.value} 세션이 종료되었습니다\n총 작업: {session_summary['total_operations']}개\n지속 시간: {session_summary['duration']:.1f}초",
            )

        return session_summary


class SystemControllerRole(BaseRoleController):
    """시스템 제어 전용 역할"""

    def __init__(self, ide_instance):
        super().__init__(ide_instance, RoleType.SYSTEM_CONTROLLER)

        # 시스템 제어 특화 능력 추가
        self.base_capabilities.extend(
            [
                RoleCapability(
                    capability_id="process_management",
                    name="프로세스 관리",
                    description="시스템 프로세스 시작, 중단, 모니터링",
                    permission_level=PermissionLevel.ADMIN,
                    allowed_operations=[
                        "start_process",
                        "stop_process",
                        "restart_process",
                        "monitor_process",
                    ],
                    restricted_areas=["critical_system_processes"],
                    resource_limits={"max_concurrent_processes": 10},
                ),
                RoleCapability(
                    capability_id="service_control",
                    name="서비스 제어",
                    description="Echo 시스템 서비스 제어",
                    permission_level=PermissionLevel.FULL_ACCESS,
                    allowed_operations=[
                        "start_service",
                        "stop_service",
                        "restart_service",
                        "check_status",
                    ],
                    restricted_areas=["system_services"],
                    resource_limits={"service_restart_limit": 5},
                ),
                RoleCapability(
                    capability_id="monitoring_control",
                    name="모니터링 제어",
                    description="시스템 모니터링 및 로깅 제어",
                    permission_level=PermissionLevel.FULL_ACCESS,
                    allowed_operations=[
                        "start_monitoring",
                        "stop_monitoring",
                        "configure_logging",
                    ],
                    restricted_areas=[],
                    resource_limits={"max_monitors": 20},
                ),
            ]
        )

        # 시스템 상태 추적
        self.system_state = {
            "echo_services": {},
            "active_monitors": {},
            "running_processes": {},
            "last_health_check": None,
        }

        # 제어 제한
        self.control_limits = {
            "restart_cooldown": 30,  # 재시작 간 대기시간 (초)
            "max_restarts_per_hour": 5,
            "allowed_services": [
                "echo_main",
                "echo_infection",
                "echo_monitoring",
                "echo_auto",
            ],
        }

        print("🎛️ 시스템 제어 전용 역할 초기화 완료")

    async def _initialize_role_specific_setup(self):
        """시스템 제어 역할 특화 설정"""

        # 시스템 상태 초기 확인
        await self._initial_system_check()

        # 자동 모니터링 설정
        if hasattr(self.ide, "monitor_dashboard"):
            self.system_state["monitoring_available"] = True

    async def _initial_system_check(self):
        """초기 시스템 상태 확인"""

        self.system_state["last_health_check"] = datetime.now()

        # Echo 서비스 상태 확인
        for service in self.control_limits["allowed_services"]:
            self.system_state["echo_services"][service] = {
                "status": "unknown",
                "last_check": datetime.now(),
                "restart_count": 0,
            }

    async def _execute_role_specific_operation(
        self, operation: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """시스템 제어 역할 특화 작업 실행"""

        if operation == "start_service":
            return await self._start_service(params)

        elif operation == "stop_service":
            return await self._stop_service(params)

        elif operation == "restart_service":
            return await self._restart_service(params)

        elif operation == "check_status":
            return await self._check_system_status(params)

        elif operation == "start_monitoring":
            return await self._start_monitoring(params)

        elif operation == "stop_monitoring":
            return await self._stop_monitoring(params)

        elif operation == "system_health_check":
            return await self._system_health_check(params)

        else:
            return await super()._execute_role_specific_operation(operation, params)

    async def _start_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """서비스 시작"""

        service_name = params.get("service_name")

        if not service_name:
            return {"status": "error", "message": "서비스 이름이 필요합니다"}

        if service_name not in self.control_limits["allowed_services"]:
            return {
                "status": "error",
                "message": f"허용되지 않은 서비스: {service_name}",
            }

        try:
            # 서비스 상태 확인
            if service_name in self.system_state["echo_services"]:
                current_status = self.system_state["echo_services"][service_name][
                    "status"
                ]
                if current_status == "running":
                    return {
                        "status": "info",
                        "message": f"서비스가 이미 실행 중입니다: {service_name}",
                    }

            # 서비스별 시작 로직
            if service_name == "echo_main":
                result = await self._start_echo_main()
            elif service_name == "echo_infection":
                result = await self._start_echo_infection()
            elif service_name == "echo_monitoring":
                result = await self._start_echo_monitoring()
            elif service_name == "echo_auto":
                result = await self._start_echo_auto()
            else:
                result = {
                    "status": "error",
                    "message": f"알 수 없는 서비스: {service_name}",
                }

            # 상태 업데이트
            if result["status"] == "success":
                self.system_state["echo_services"][service_name] = {
                    "status": "running",
                    "last_check": datetime.now(),
                    "restart_count": self.system_state["echo_services"]
                    .get(service_name, {})
                    .get("restart_count", 0),
                }

            return result

        except Exception as e:
            return {"status": "error", "message": f"서비스 시작 실패: {e}"}

    async def _start_echo_main(self) -> Dict[str, Any]:
        """Echo 메인 시스템 시작"""

        try:
            if hasattr(self.ide, "start_echo_system"):
                self.ide.start_echo_system()
                return {
                    "status": "success",
                    "message": "Echo 메인 시스템이 시작되었습니다",
                }
            else:
                return {
                    "status": "error",
                    "message": "Echo 메인 시스템 시작 기능을 찾을 수 없습니다",
                }
        except Exception as e:
            return {"status": "error", "message": f"Echo 메인 시스템 시작 실패: {e}"}

    async def _start_echo_infection(self) -> Dict[str, Any]:
        """Echo 감염 시스템 시작"""

        try:
            if hasattr(self.ide, "run_infection_loop"):
                # 비동기로 감염 루프 시작
                threading.Thread(
                    target=self.ide.run_infection_loop, daemon=True
                ).start()
                return {
                    "status": "success",
                    "message": "Echo 감염 시스템이 시작되었습니다",
                }
            else:
                return {
                    "status": "error",
                    "message": "Echo 감염 시스템 시작 기능을 찾을 수 없습니다",
                }
        except Exception as e:
            return {"status": "error", "message": f"Echo 감염 시스템 시작 실패: {e}"}

    async def _start_echo_monitoring(self) -> Dict[str, Any]:
        """Echo 모니터링 시스템 시작"""

        try:
            if hasattr(self.ide, "monitor_dashboard"):
                self.ide.monitor_dashboard.start_monitoring()
                return {
                    "status": "success",
                    "message": "Echo 모니터링 시스템이 시작되었습니다",
                }
            else:
                return {
                    "status": "error",
                    "message": "Echo 모니터링 시스템을 찾을 수 없습니다",
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Echo 모니터링 시스템 시작 실패: {e}",
            }

    async def _start_echo_auto(self) -> Dict[str, Any]:
        """Echo 자동진화 시스템 시작"""

        return {
            "status": "success",
            "message": "Echo 자동진화 시스템 시작 명령이 수신되었습니다",
        }

    async def _stop_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """서비스 중단"""

        service_name = params.get("service_name")

        if not service_name:
            return {"status": "error", "message": "서비스 이름이 필요합니다"}

        if service_name not in self.control_limits["allowed_services"]:
            return {
                "status": "error",
                "message": f"허용되지 않은 서비스: {service_name}",
            }

        try:
            # 서비스별 중단 로직
            if service_name == "echo_monitoring":
                if hasattr(self.ide, "monitor_dashboard"):
                    self.ide.monitor_dashboard.stop_monitoring()
                    message = "Echo 모니터링 시스템이 중단되었습니다"
                else:
                    message = "Echo 모니터링 시스템을 찾을 수 없습니다"
            else:
                message = f"{service_name} 서비스 중단 명령이 수신되었습니다"

            # 상태 업데이트
            if service_name in self.system_state["echo_services"]:
                self.system_state["echo_services"][service_name]["status"] = "stopped"
                self.system_state["echo_services"][service_name][
                    "last_check"
                ] = datetime.now()

            return {"status": "success", "message": message}

        except Exception as e:
            return {"status": "error", "message": f"서비스 중단 실패: {e}"}

    async def _restart_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """서비스 재시작"""

        service_name = params.get("service_name")

        if not service_name:
            return {"status": "error", "message": "서비스 이름이 필요합니다"}

        # 재시작 제한 확인
        service_info = self.system_state["echo_services"].get(service_name, {})
        restart_count = service_info.get("restart_count", 0)

        if restart_count >= self.control_limits["max_restarts_per_hour"]:
            return {"status": "error", "message": "시간당 재시작 제한을 초과했습니다"}

        try:
            # 서비스 중단
            stop_result = await self._stop_service(params)
            if stop_result["status"] != "success":
                return stop_result

            # 대기 시간
            await asyncio.sleep(self.control_limits["restart_cooldown"])

            # 서비스 시작
            start_result = await self._start_service(params)

            # 재시작 카운트 증가
            if start_result["status"] == "success":
                if service_name in self.system_state["echo_services"]:
                    self.system_state["echo_services"][service_name][
                        "restart_count"
                    ] = (restart_count + 1)

            return {
                "status": start_result["status"],
                "message": f"서비스 재시작 완료: {service_name}",
                "restart_count": restart_count + 1,
            }

        except Exception as e:
            return {"status": "error", "message": f"서비스 재시작 실패: {e}"}

    async def _check_system_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """시스템 상태 확인"""

        try:
            # 시스템 상태 업데이트
            await self._update_system_status()

            status_report = {
                "timestamp": datetime.now().isoformat(),
                "echo_services": self.system_state["echo_services"],
                "active_monitors": len(self.system_state["active_monitors"]),
                "system_health": "good",  # 상세 로직으로 계산 가능
                "last_health_check": (
                    self.system_state["last_health_check"].isoformat()
                    if self.system_state["last_health_check"]
                    else None
                ),
            }

            # IDE에 상태 표시
            if hasattr(self.ide, "display_message"):
                self.ide.display_message(
                    "시스템상태",
                    f"📊 시스템 상태 확인 완료\n활성 서비스: {len([s for s in self.system_state['echo_services'].values() if s['status'] == 'running'])}개\n모니터: {len(self.system_state['active_monitors'])}개\n상태: {status_report['system_health']}",
                )

            return {"status": "success", "system_status": status_report}

        except Exception as e:
            return {"status": "error", "message": f"시스템 상태 확인 실패: {e}"}

    async def _update_system_status(self):
        """시스템 상태 업데이트"""

        self.system_state["last_health_check"] = datetime.now()

        # 각 서비스 상태 확인 (실제 구현에서는 더 정교한 로직 필요)
        for service_name in self.system_state["echo_services"]:
            self.system_state["echo_services"][service_name][
                "last_check"
            ] = datetime.now()

    async def _start_monitoring(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """모니터링 시작"""

        monitor_type = params.get("monitor_type", "general")
        target = params.get("target", "system")

        try:
            monitor_id = f"monitor_{monitor_type}_{datetime.now().strftime('%H%M%S')}"

            self.system_state["active_monitors"][monitor_id] = {
                "type": monitor_type,
                "target": target,
                "start_time": datetime.now(),
                "status": "active",
            }

            # 모니터링 대시보드 연동
            if hasattr(self.ide, "monitor_dashboard"):
                self.ide.monitor_dashboard.start_monitoring()

            return {
                "status": "success",
                "message": f"{monitor_type} 모니터링이 시작되었습니다",
                "monitor_id": monitor_id,
            }

        except Exception as e:
            return {"status": "error", "message": f"모니터링 시작 실패: {e}"}

    async def _stop_monitoring(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """모니터링 중단"""

        monitor_id = params.get("monitor_id")

        if monitor_id and monitor_id in self.system_state["active_monitors"]:
            del self.system_state["active_monitors"][monitor_id]
            message = f"모니터링이 중단되었습니다: {monitor_id}"
        else:
            # 모든 모니터링 중단
            self.system_state["active_monitors"].clear()
            message = "모든 모니터링이 중단되었습니다"

            if hasattr(self.ide, "monitor_dashboard"):
                self.ide.monitor_dashboard.stop_monitoring()

        return {"status": "success", "message": message}

    async def _system_health_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """시스템 헬스 체크"""

        try:
            health_report = {
                "timestamp": datetime.now().isoformat(),
                "overall_health": "good",
                "services_status": {},
                "resource_usage": {},
                "recommendations": [],
            }

            # 서비스 상태 체크
            for service_name, service_info in self.system_state[
                "echo_services"
            ].items():
                health_report["services_status"][service_name] = service_info["status"]

                # 재시작 횟수가 많으면 경고
                if service_info.get("restart_count", 0) > 3:
                    health_report["recommendations"].append(
                        f"{service_name} 서비스의 잦은 재시작을 확인하세요"
                    )

            # 모니터링 상태
            active_monitor_count = len(self.system_state["active_monitors"])
            if active_monitor_count == 0:
                health_report["recommendations"].append(
                    "모니터링을 활성화하는 것을 권장합니다"
                )

            return {"status": "success", "health_report": health_report}

        except Exception as e:
            return {"status": "error", "message": f"헬스 체크 실패: {e}"}

    def get_system_control_stats(self) -> Dict[str, Any]:
        """시스템 제어 통계"""

        if not self.session:
            return {"status": "no_session"}

        control_operations = [
            op
            for op in self.session.operation_log
            if op["operation"]
            in [
                "start_service",
                "stop_service",
                "restart_service",
                "start_monitoring",
                "stop_monitoring",
            ]
        ]

        return {
            "total_control_operations": len(control_operations),
            "service_operations": len(
                [op for op in control_operations if "service" in op["operation"]]
            ),
            "monitoring_operations": len(
                [op for op in control_operations if "monitoring" in op["operation"]]
            ),
            "active_services": len(
                [
                    s
                    for s in self.system_state["echo_services"].values()
                    if s["status"] == "running"
                ]
            ),
            "active_monitors": len(self.system_state["active_monitors"]),
        }


class AnalystAssistantRole(BaseRoleController):
    """분석 전용 어시스턴트 역할"""

    def __init__(self, ide_instance):
        super().__init__(ide_instance, RoleType.ANALYST_ASSISTANT)

        # 분석 특화 능력 추가
        self.base_capabilities.extend(
            [
                RoleCapability(
                    capability_id="data_analysis",
                    name="데이터 분석",
                    description="로그, 메트릭, 시스템 데이터 분석",
                    permission_level=PermissionLevel.READ_ONLY,
                    allowed_operations=[
                        "analyze_logs",
                        "generate_report",
                        "extract_metrics",
                        "trend_analysis",
                    ],
                    restricted_areas=[],
                    resource_limits={"max_analysis_size": 100 * 1024 * 1024},  # 100MB
                ),
                RoleCapability(
                    capability_id="code_analysis",
                    name="코드 분석",
                    description="소스 코드 구조 및 품질 분석",
                    permission_level=PermissionLevel.READ_ONLY,
                    allowed_operations=[
                        "analyze_code_structure",
                        "check_code_quality",
                        "find_patterns",
                    ],
                    restricted_areas=[],
                    resource_limits={"max_files_per_analysis": 500},
                ),
                RoleCapability(
                    capability_id="performance_analysis",
                    name="성능 분석",
                    description="시스템 성능 및 최적화 분석",
                    permission_level=PermissionLevel.READ_ONLY,
                    allowed_operations=[
                        "performance_analysis",
                        "bottleneck_detection",
                        "optimization_suggestions",
                    ],
                    restricted_areas=[],
                    resource_limits={"analysis_timeout": 300},  # 5분
                ),
            ]
        )

        # 분석 결과 저장소
        self.analysis_results = {}

        # 분석 도구 설정
        self.analysis_tools = {
            "supported_formats": ["json", "csv", "log", "yaml", "py", "js", "ts"],
            "analysis_types": [
                "structure",
                "performance",
                "quality",
                "security",
                "trend",
            ],
            "output_formats": ["text", "json", "html", "markdown"],
        }

        # 패턴 인식 데이터베이스
        self.pattern_database = self._initialize_pattern_database()

        print("🔍 분석 전용 어시스턴트 역할 초기화 완료")

    def _initialize_pattern_database(self) -> Dict[str, Any]:
        """패턴 인식 데이터베이스 초기화"""

        return {
            "log_patterns": {
                "error_patterns": [
                    r"ERROR.*?(\w+Error|\w+Exception)",
                    r"FAILED.*?(\w+)",
                    r"CRITICAL.*?(\w+)",
                ],
                "warning_patterns": [r"WARNING.*?(\w+)", r"WARN.*?(\w+)"],
                "performance_patterns": [
                    r"slow.*?(\d+\.?\d*)\s*(ms|seconds?)",
                    r"timeout.*?(\d+\.?\d*)",
                    r"latency.*?(\d+\.?\d*)",
                ],
            },
            "code_patterns": {
                "complexity_indicators": [
                    r"if.*?if.*?if",  # 중첩 조건문
                    r"for.*?for.*?for",  # 중첩 반복문
                    r"def \w+\([^)]{50,}\)",  # 긴 매개변수 목록
                ],
                "quality_issues": [r"# TODO.*", r"# FIXME.*", r"# HACK.*"],
            },
        }

    async def _initialize_role_specific_setup(self):
        """분석 역할 특화 설정"""

        # 분석 대상 디렉토리 스캔
        await self._scan_analysis_targets()

        # 기존 로그 파일 발견
        await self._discover_log_files()

    async def _scan_analysis_targets(self):
        """분석 대상 스캔"""

        if hasattr(self.ide, "project_root"):
            project_root = Path(self.ide.project_root)

            # 분석 가능한 파일 목록 생성
            self.analysis_targets = {
                "code_files": list(project_root.glob("**/*.py"))
                + list(project_root.glob("**/*.js")),
                "config_files": list(project_root.glob("**/*.yaml"))
                + list(project_root.glob("**/*.json")),
                "log_files": list(project_root.glob("**/*.log"))
                + list(project_root.glob("**/*.jsonl")),
            }

    async def _discover_log_files(self):
        """로그 파일 발견"""

        log_directories = ["logs", "meta_logs", "data"]

        for log_dir in log_directories:
            if hasattr(self.ide, "project_root"):
                log_path = Path(self.ide.project_root) / log_dir
                if log_path.exists():
                    self.analysis_targets.setdefault("log_files", []).extend(
                        log_path.glob("*.log")
                    )
                    self.analysis_targets.setdefault("log_files", []).extend(
                        log_path.glob("*.jsonl")
                    )

    async def _execute_role_specific_operation(
        self, operation: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """분석 역할 특화 작업 실행"""

        if operation == "analyze_logs":
            return await self._analyze_logs(params)

        elif operation == "analyze_code_structure":
            return await self._analyze_code_structure(params)

        elif operation == "generate_report":
            return await self._generate_analysis_report(params)

        elif operation == "extract_metrics":
            return await self._extract_metrics(params)

        elif operation == "trend_analysis":
            return await self._trend_analysis(params)

        elif operation == "performance_analysis":
            return await self._performance_analysis(params)

        elif operation == "find_patterns":
            return await self._find_patterns(params)

        else:
            return await super()._execute_role_specific_operation(operation, params)

    async def _analyze_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """로그 분석"""

        log_file = params.get("log_file")
        analysis_type = params.get("analysis_type", "general")

        if not log_file:
            # 사용 가능한 로그 파일 목록 반환
            available_logs = getattr(self, "analysis_targets", {}).get("log_files", [])
            return {
                "status": "info",
                "message": "로그 파일을 지정해주세요",
                "available_logs": [
                    str(f) for f in available_logs[:10]
                ],  # 최대 10개만 표시
            }

        try:
            log_path = Path(log_file)
            if not log_path.exists():
                return {
                    "status": "error",
                    "message": f"로그 파일을 찾을 수 없습니다: {log_file}",
                }

            # 파일 크기 확인
            file_size = log_path.stat().st_size
            max_size = self.base_capabilities[1].resource_limits["max_analysis_size"]

            if file_size > max_size:
                return {
                    "status": "error",
                    "message": f"파일이 너무 큽니다 (최대 {max_size//1024//1024}MB)",
                }

            # 로그 파일 읽기 및 분석
            with open(log_path, "r", encoding="utf-8") as f:
                log_content = f.read()

            analysis_result = await self._perform_log_analysis(
                log_content, analysis_type
            )

            # 결과 저장
            analysis_id = f"log_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.analysis_results[analysis_id] = {
                "type": "log_analysis",
                "file": str(log_path),
                "analysis_type": analysis_type,
                "result": analysis_result,
                "timestamp": datetime.now().isoformat(),
            }

            return {
                "status": "success",
                "analysis_id": analysis_id,
                "result": analysis_result,
                "file_analyzed": str(log_path),
            }

        except Exception as e:
            return {"status": "error", "message": f"로그 분석 실패: {e}"}

    async def _perform_log_analysis(
        self, log_content: str, analysis_type: str
    ) -> Dict[str, Any]:
        """로그 분석 수행"""

        lines = log_content.split("\n")
        result = {
            "total_lines": len(lines),
            "analysis_type": analysis_type,
            "patterns_found": {},
            "summary": {},
        }

        # 패턴 기반 분석
        for pattern_type, patterns in self.pattern_database["log_patterns"].items():
            matches = []
            for pattern in patterns:
                import re

                pattern_matches = re.findall(pattern, log_content, re.IGNORECASE)
                matches.extend(pattern_matches)

            result["patterns_found"][pattern_type] = {
                "count": len(matches),
                "samples": matches[:5],  # 최대 5개 샘플
            }

        # 기본 통계
        result["summary"] = {
            "error_count": result["patterns_found"]
            .get("error_patterns", {})
            .get("count", 0),
            "warning_count": result["patterns_found"]
            .get("warning_patterns", {})
            .get("count", 0),
            "performance_issues": result["patterns_found"]
            .get("performance_patterns", {})
            .get("count", 0),
        }

        # 시간별 분포 (간단한 예시)
        if analysis_type == "temporal":
            result["temporal_distribution"] = await self._analyze_temporal_distribution(
                lines
            )

        return result

    async def _analyze_temporal_distribution(
        self, log_lines: List[str]
    ) -> Dict[str, Any]:
        """시간별 분포 분석"""

        import re
        from collections import defaultdict

        timestamp_pattern = r"(\d{4}-\d{2}-\d{2})\s+(\d{2}):"
        hourly_distribution = defaultdict(int)

        for line in log_lines:
            match = re.search(timestamp_pattern, line)
            if match:
                date, hour = match.groups()
                hourly_distribution[f"{date}_{hour}"] += 1

        return {
            "hourly_counts": dict(hourly_distribution),
            "peak_hour": (
                max(hourly_distribution, key=hourly_distribution.get)
                if hourly_distribution
                else None
            ),
            "total_timestamped_entries": sum(hourly_distribution.values()),
        }

    async def _analyze_code_structure(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """코드 구조 분석"""

        target_path = params.get("target_path")

        if not target_path:
            # 분석 가능한 코드 파일 목록 반환
            available_files = getattr(self, "analysis_targets", {}).get(
                "code_files", []
            )
            return {
                "status": "info",
                "message": "분석할 파일 또는 디렉토리를 지정해주세요",
                "available_files": [str(f) for f in available_files[:10]],
            }

        try:
            path = Path(target_path)

            if path.is_file():
                # 단일 파일 분석
                result = await self._analyze_single_file(path)
            elif path.is_dir():
                # 디렉토리 분석
                result = await self._analyze_directory(path)
            else:
                return {
                    "status": "error",
                    "message": f"경로를 찾을 수 없습니다: {target_path}",
                }

            # 결과 저장
            analysis_id = f"code_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.analysis_results[analysis_id] = {
                "type": "code_structure",
                "target": str(path),
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }

            return {
                "status": "success",
                "analysis_id": analysis_id,
                "result": result,
                "target_analyzed": str(path),
            }

        except Exception as e:
            return {"status": "error", "message": f"코드 구조 분석 실패: {e}"}

    async def _analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """단일 파일 분석"""

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            result = {
                "file_info": {
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "lines": len(lines),
                    "extension": file_path.suffix,
                },
                "structure_analysis": {},
                "quality_metrics": {},
            }

            # Python 파일 특화 분석
            if file_path.suffix == ".py":
                result["structure_analysis"] = await self._analyze_python_structure(
                    content
                )
                result["quality_metrics"] = await self._analyze_python_quality(content)

            # 일반적인 분석
            result["general_metrics"] = {
                "comment_lines": len(
                    [line for line in lines if line.strip().startswith("#")]
                ),
                "empty_lines": len([line for line in lines if not line.strip()]),
                "code_lines": len(
                    [
                        line
                        for line in lines
                        if line.strip() and not line.strip().startswith("#")
                    ]
                ),
            }

            return result

        except Exception as e:
            return {"error": f"파일 분석 중 오류: {e}"}

    async def _analyze_python_structure(self, content: str) -> Dict[str, Any]:
        """Python 구조 분석"""

        import re

        structure = {
            "classes": [],
            "functions": [],
            "imports": [],
            "complexity_indicators": 0,
        }

        # 클래스 찾기
        class_pattern = r"class\s+(\w+)(?:\([^)]*\))?:"
        structure["classes"] = re.findall(class_pattern, content)

        # 함수 찾기
        function_pattern = r"def\s+(\w+)\s*\([^)]*\):"
        structure["functions"] = re.findall(function_pattern, content)

        # import 문 찾기
        import_pattern = r"(?:from\s+\w+\s+)?import\s+([^\n]+)"
        structure["imports"] = re.findall(import_pattern, content)

        # 복잡도 지표
        for pattern in self.pattern_database["code_patterns"]["complexity_indicators"]:
            structure["complexity_indicators"] += len(re.findall(pattern, content))

        return structure

    async def _analyze_python_quality(self, content: str) -> Dict[str, Any]:
        """Python 품질 분석"""

        import re

        quality = {"docstring_coverage": 0, "todo_count": 0, "potential_issues": []}

        # TODO/FIXME 카운트
        for pattern in self.pattern_database["code_patterns"]["quality_issues"]:
            matches = re.findall(pattern, content)
            if "TODO" in pattern:
                quality["todo_count"] = len(matches)
            quality["potential_issues"].extend(matches)

        # 독스트링 커버리지 (간단한 계산)
        docstring_pattern = r'""".*?"""'
        function_pattern = r"def\s+\w+"

        docstrings = len(re.findall(docstring_pattern, content, re.DOTALL))
        functions = len(re.findall(function_pattern, content))

        if functions > 0:
            quality["docstring_coverage"] = docstrings / functions

        return quality

    async def _analyze_directory(self, dir_path: Path) -> Dict[str, Any]:
        """디렉토리 분석"""

        result = {
            "directory_info": {
                "name": dir_path.name,
                "total_files": 0,
                "file_types": {},
                "subdirectories": [],
            },
            "aggregate_metrics": {
                "total_lines": 0,
                "total_classes": 0,
                "total_functions": 0,
            },
        }

        try:
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    result["directory_info"]["total_files"] += 1

                    # 파일 타입별 카운트
                    ext = file_path.suffix
                    result["directory_info"]["file_types"][ext] = (
                        result["directory_info"]["file_types"].get(ext, 0) + 1
                    )

                    # Python 파일 분석
                    if ext == ".py":
                        file_analysis = await self._analyze_single_file(file_path)
                        if "structure_analysis" in file_analysis:
                            result["aggregate_metrics"]["total_classes"] += len(
                                file_analysis["structure_analysis"].get("classes", [])
                            )
                            result["aggregate_metrics"]["total_functions"] += len(
                                file_analysis["structure_analysis"].get("functions", [])
                            )
                        if "file_info" in file_analysis:
                            result["aggregate_metrics"]["total_lines"] += file_analysis[
                                "file_info"
                            ].get("lines", 0)

                elif file_path.is_dir():
                    result["directory_info"]["subdirectories"].append(file_path.name)

            return result

        except Exception as e:
            return {"error": f"디렉토리 분석 중 오류: {e}"}

    async def _generate_analysis_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """분석 보고서 생성"""

        analysis_ids = params.get("analysis_ids", [])
        report_format = params.get("format", "text")

        if not analysis_ids:
            # 모든 분석 결과 포함
            analysis_ids = list(self.analysis_results.keys())

        if not analysis_ids:
            return {"status": "error", "message": "분석 결과가 없습니다"}

        try:
            report = {
                "report_id": f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generation_time": datetime.now().isoformat(),
                "included_analyses": analysis_ids,
                "summary": {},
                "detailed_results": {},
            }

            # 분석 결과 통합
            for analysis_id in analysis_ids:
                if analysis_id in self.analysis_results:
                    analysis = self.analysis_results[analysis_id]
                    report["detailed_results"][analysis_id] = analysis

            # 요약 생성
            report["summary"] = await self._generate_summary(report["detailed_results"])

            # 포맷별 출력
            if report_format == "markdown":
                formatted_report = self._format_report_markdown(report)
            elif report_format == "json":
                formatted_report = json.dumps(report, indent=2, ensure_ascii=False)
            else:
                formatted_report = self._format_report_text(report)

            return {
                "status": "success",
                "report": formatted_report,
                "report_id": report["report_id"],
                "format": report_format,
            }

        except Exception as e:
            return {"status": "error", "message": f"보고서 생성 실패: {e}"}

    async def _generate_summary(
        self, detailed_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """요약 생성"""

        summary = {
            "total_analyses": len(detailed_results),
            "analysis_types": {},
            "key_findings": [],
        }

        for analysis_id, analysis in detailed_results.items():
            analysis_type = analysis.get("type", "unknown")
            summary["analysis_types"][analysis_type] = (
                summary["analysis_types"].get(analysis_type, 0) + 1
            )

            # 주요 발견사항 추출
            if analysis_type == "log_analysis":
                result = analysis.get("result", {})
                error_count = result.get("summary", {}).get("error_count", 0)
                if error_count > 0:
                    summary["key_findings"].append(
                        f"로그에서 {error_count}개의 오류 발견"
                    )

            elif analysis_type == "code_structure":
                result = analysis.get("result", {})
                if "aggregate_metrics" in result:
                    metrics = result["aggregate_metrics"]
                    summary["key_findings"].append(
                        f"총 {metrics.get('total_functions', 0)}개 함수, {metrics.get('total_classes', 0)}개 클래스 분석"
                    )

        return summary

    def _format_report_text(self, report: Dict[str, Any]) -> str:
        """텍스트 형식 보고서"""

        lines = [
            f"📊 분석 보고서 - {report['report_id']}",
            f"생성 시간: {report['generation_time']}",
            "=" * 50,
            "",
            "📋 요약:",
            f"  총 분석 수: {report['summary']['total_analyses']}",
            f"  분석 타입: {', '.join(report['summary']['analysis_types'].keys())}",
            "",
            "🔍 주요 발견사항:",
        ]

        for finding in report["summary"]["key_findings"]:
            lines.append(f"  • {finding}")

        return "\n".join(lines)

    def _format_report_markdown(self, report: Dict[str, Any]) -> str:
        """마크다운 형식 보고서"""

        md_lines = [
            f"# 📊 분석 보고서 - {report['report_id']}",
            "",
            f"**생성 시간:** {report['generation_time']}",
            "",
            "## 📋 요약",
            "",
            f"- **총 분석 수:** {report['summary']['total_analyses']}",
            f"- **분석 타입:** {', '.join(report['summary']['analysis_types'].keys())}",
            "",
            "## 🔍 주요 발견사항",
            "",
        ]

        for finding in report["summary"]["key_findings"]:
            md_lines.append(f"- {finding}")

        return "\n".join(md_lines)

    def get_analysis_stats(self) -> Dict[str, Any]:
        """분석 통계"""

        if not self.session:
            return {"status": "no_session"}

        analysis_operations = [
            op
            for op in self.session.operation_log
            if op["operation"]
            in ["analyze_logs", "analyze_code_structure", "generate_report"]
        ]

        return {
            "total_analyses": len(self.analysis_results),
            "analysis_operations": len(analysis_operations),
            "available_targets": {
                "code_files": len(
                    getattr(self, "analysis_targets", {}).get("code_files", [])
                ),
                "log_files": len(
                    getattr(self, "analysis_targets", {}).get("log_files", [])
                ),
                "config_files": len(
                    getattr(self, "analysis_targets", {}).get("config_files", [])
                ),
            },
        }


class CodeGeneratorRole(BaseRoleController):
    """코드 생성 전용 역할"""

    def __init__(self, ide_instance):
        super().__init__(ide_instance, RoleType.CODE_GENERATOR)

        # 코드 생성 특화 능력 추가
        self.base_capabilities.extend(
            [
                RoleCapability(
                    capability_id="code_generation",
                    name="코드 생성",
                    description="다양한 프로그래밍 언어로 코드 생성",
                    permission_level=PermissionLevel.FULL_ACCESS,
                    allowed_operations=[
                        "generate_code",
                        "create_file",
                        "write_file",
                        "validate_syntax",
                    ],
                    restricted_areas=["system", "config", "/etc"],
                    resource_limits={"max_code_lines": 1000, "max_files_per_hour": 50},
                ),
                RoleCapability(
                    capability_id="template_management",
                    name="템플릿 관리",
                    description="코드 템플릿 생성 및 관리",
                    permission_level=PermissionLevel.LIMITED_WRITE,
                    allowed_operations=[
                        "create_template",
                        "use_template",
                        "modify_template",
                    ],
                    restricted_areas=["core_templates"],
                    resource_limits={"max_templates": 100},
                ),
            ]
        )

        # 코드 생성 설정
        self.code_settings = {
            "supported_languages": [
                "python",
                "javascript",
                "typescript",
                "java",
                "cpp",
                "yaml",
                "json",
            ],
            "default_style": "clean",
            "include_comments": True,
            "include_docstrings": True,
            "include_type_hints": True,
        }

        # 템플릿 저장소
        self.templates = {}

        print("💻 코드 생성 전용 역할 초기화 완료")

    async def _initialize_role_specific_setup(self):
        """코드 생성 역할 특화 설정"""

        # 기본 템플릿 로드
        await self._load_default_templates()

        # AI 어시스턴트와 연동
        if hasattr(self.ide, "ai_assistant"):
            self.ide.ai_assistant.register_code_generator(self)

    async def _load_default_templates(self):
        """기본 템플릿 로드"""

        self.templates = {
            "python_class": {
                "name": "Python 클래스",
                "template": '''class {class_name}:
    """
    {description}
    """
    
    def __init__(self):
        self.name = "{class_name}"
    
    def process(self):
        # 구현 필요
        pass
''',
                "variables": ["class_name", "description"],
            },
            "python_function": {
                "name": "Python 함수",
                "template": '''def {function_name}({parameters}):
    """
    {description}
    
    Args:
        {args_doc}
    
    Returns:
        {return_doc}
    """
    # 구현 필요
    pass
''',
                "variables": [
                    "function_name",
                    "parameters",
                    "description",
                    "args_doc",
                    "return_doc",
                ],
            },
            "config_yaml": {
                "name": "YAML 설정 파일",
                "template": """# {config_name} 설정
version: "1.0"
name: "{config_name}"

settings:
  enabled: true
  debug: false
  
parameters:
  # 설정 파라미터들
  
metadata:
  created: "{creation_date}"
  description: "{description}"
""",
                "variables": ["config_name", "creation_date", "description"],
            },
        }

    async def _execute_role_specific_operation(
        self, operation: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """코드 생성 역할 특화 작업 실행"""

        if operation == "generate_code":
            return await self._generate_code(params)

        elif operation == "create_template":
            return await self._create_template(params)

        elif operation == "use_template":
            return await self._use_template(params)

        elif operation == "validate_syntax":
            return await self._validate_syntax(params)

        elif operation == "create_file":
            return await self._create_code_file(params)

        else:
            return await super()._execute_role_specific_operation(operation, params)

    async def _generate_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """코드 생성"""

        code_type = params.get("type", "function")
        language = params.get("language", "python")
        description = params.get("description", "자동 생성된 코드")
        name = params.get("name", "generated_code")

        if language not in self.code_settings["supported_languages"]:
            return {"status": "error", "message": f"지원하지 않는 언어: {language}"}

        try:
            if code_type == "class" and language == "python":
                code = self._generate_python_class(name, description, params)
            elif code_type == "function" and language == "python":
                code = self._generate_python_function(name, description, params)
            elif code_type == "config" and language in ["yaml", "yml"]:
                code = self._generate_yaml_config(name, description, params)
            else:
                code = self._generate_generic_code(
                    code_type, language, name, description, params
                )

            # IDE에 결과 표시
            if hasattr(self.ide, "display_message"):
                self.ide.display_message(
                    "코드생성완료",
                    f"✨ 코드 생성이 완료되었습니다\n타입: {code_type}\n언어: {language}\n이름: {name}\n\n{code[:200]}...",
                )

            return {
                "status": "success",
                "code": code,
                "type": code_type,
                "language": language,
                "name": name,
                "lines": len(code.split("\n")),
            }

        except Exception as e:
            return {"status": "error", "message": f"코드 생성 실패: {e}"}

    def _generate_python_class(
        self, name: str, description: str, params: Dict[str, Any]
    ) -> str:
        """Python 클래스 생성"""

        methods = params.get("methods", ["__init__", "process"])
        inheritance = params.get("inheritance", "")

        class_def = f"class {name}"
        if inheritance:
            class_def += f"({inheritance})"
        class_def += ":"

        code_lines = [class_def, f'    """', f"    {description}", f'    """', ""]

        # __init__ 메서드
        if "__init__" in methods:
            code_lines.extend(
                ["    def __init__(self):", f'        self.name = "{name}"', ""]
            )

        # 기타 메서드들
        for method in methods:
            if method != "__init__":
                code_lines.extend(
                    [
                        f"    def {method}(self):",
                        f'        """',
                        f"        {method} 메서드",
                        f'        """',
                        "        # 구현 필요",
                        "        pass",
                        "",
                    ]
                )

        return "\n".join(code_lines)

    def _generate_python_function(
        self, name: str, description: str, params: Dict[str, Any]
    ) -> str:
        """Python 함수 생성"""

        arguments = params.get("arguments", [])
        return_type = params.get("return_type", "None")

        arg_str = ", ".join(arguments) if arguments else ""

        code_lines = [
            f"def {name}({arg_str}):",
            f'    """',
            f"    {description}",
            f"    ",
        ]

        if arguments:
            code_lines.append("    Args:")
            for arg in arguments:
                code_lines.append(f"        {arg}: 매개변수 설명")
            code_lines.append("    ")

        code_lines.extend(
            [
                f"    Returns:",
                f"        {return_type}: 반환값 설명",
                f'    """',
                "    # 구현 필요",
                "    pass",
            ]
        )

        return "\n".join(code_lines)

    def _generate_yaml_config(
        self, name: str, description: str, params: Dict[str, Any]
    ) -> str:
        """YAML 설정 파일 생성"""

        config_type = params.get("config_type", "general")

        template = self.templates["config_yaml"]["template"]

        return template.format(
            config_name=name,
            description=description,
            creation_date=datetime.now().isoformat(),
        )

    def _generate_generic_code(
        self,
        code_type: str,
        language: str,
        name: str,
        description: str,
        params: Dict[str, Any],
    ) -> str:
        """일반적인 코드 생성"""

        if language == "javascript":
            return f"""// {description}
function {name}() {{
    // 구현 필요
    console.log("{name} 함수 실행");
}}

module.exports = {name};
"""

        elif language == "typescript":
            return f"""// {description}
export function {name}(): void {{
    // 구현 필요
    console.log("{name} 함수 실행");
}}
"""

        else:
            return f"""// {description}
// 언어: {language}
// 타입: {code_type}
// 이름: {name}

// 구현 필요
"""

    async def _create_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """템플릿 생성"""

        template_id = params.get("id")
        template_name = params.get("name")
        template_content = params.get("content")
        variables = params.get("variables", [])

        if not all([template_id, template_name, template_content]):
            return {
                "status": "error",
                "message": "필수 매개변수 누락: id, name, content",
            }

        self.templates[template_id] = {
            "name": template_name,
            "template": template_content,
            "variables": variables,
            "created": datetime.now().isoformat(),
        }

        return {
            "status": "success",
            "message": f"템플릿이 생성되었습니다: {template_name}",
            "template_id": template_id,
        }

    async def _use_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """템플릿 사용"""

        template_id = params.get("template_id")
        variables = params.get("variables", {})

        if template_id not in self.templates:
            return {
                "status": "error",
                "message": f"템플릿을 찾을 수 없습니다: {template_id}",
            }

        template = self.templates[template_id]

        try:
            generated_code = template["template"].format(**variables)

            return {
                "status": "success",
                "code": generated_code,
                "template_name": template["name"],
                "variables_used": variables,
            }

        except KeyError as e:
            return {"status": "error", "message": f"템플릿 변수 누락: {e}"}

    async def _validate_syntax(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """구문 검증"""

        code = params.get("code")
        language = params.get("language", "python")

        if not code:
            return {"status": "error", "message": "검증할 코드가 없습니다"}

        try:
            if language == "python":
                compile(code, "<string>", "exec")

            return {
                "status": "success",
                "message": "구문이 유효합니다",
                "language": language,
            }

        except SyntaxError as e:
            return {
                "status": "error",
                "message": f"구문 오류: {e}",
                "line": e.lineno,
                "language": language,
            }

    async def _create_code_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """코드 파일 생성"""

        filename = params.get("filename")
        code = params.get("code")

        if not all([filename, code]):
            return {"status": "error", "message": "파일명과 코드가 필요합니다"}

        try:
            file_path = Path(filename)

            # 안전한 경로인지 확인
            if any(
                restricted in str(file_path)
                for restricted in ["system", "config", "/etc"]
            ):
                return {"status": "error", "message": "제한된 경로입니다"}

            # 디렉토리 생성
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 파일 작성
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)

            return {
                "status": "success",
                "message": f"파일이 생성되었습니다: {filename}",
                "file_path": str(file_path),
                "size": len(code),
            }

        except Exception as e:
            return {"status": "error", "message": f"파일 생성 실패: {e}"}

    def get_available_templates(self) -> Dict[str, Any]:
        """사용 가능한 템플릿 목록"""

        return {
            template_id: {"name": template["name"], "variables": template["variables"]}
            for template_id, template in self.templates.items()
        }

    def get_code_generation_stats(self) -> Dict[str, Any]:
        """코드 생성 통계"""

        if not self.session:
            return {"status": "no_session"}

        code_operations = [
            op
            for op in self.session.operation_log
            if op["operation"] in ["generate_code", "create_file", "use_template"]
        ]

        return {
            "total_code_generations": len(code_operations),
            "templates_used": len(
                [op for op in code_operations if op["operation"] == "use_template"]
            ),
            "files_created": len(
                [op for op in code_operations if op["operation"] == "create_file"]
            ),
            "available_templates": len(self.templates),
        }


# 편의 함수들
def create_code_generator_role(ide_instance) -> CodeGeneratorRole:
    """코드 생성 역할 생성"""
    return CodeGeneratorRole(ide_instance)


def create_system_controller_role(ide_instance) -> SystemControllerRole:
    """시스템 제어 역할 생성"""
    return SystemControllerRole(ide_instance)


def create_analyst_assistant_role(ide_instance) -> AnalystAssistantRole:
    """분석 어시스턴트 역할 생성"""
    return AnalystAssistantRole(ide_instance)


def integrate_role_controllers(ide_instance):
    """Echo IDE에 역할 제어자들 통합"""

    if not hasattr(ide_instance, "role_controllers"):
        ide_instance.role_controllers = {}

    # 모든 역할 제어자 추가
    ide_instance.role_controllers["code_generator"] = CodeGeneratorRole(ide_instance)
    ide_instance.role_controllers["system_controller"] = SystemControllerRole(
        ide_instance
    )
    ide_instance.role_controllers["analyst_assistant"] = AnalystAssistantRole(
        ide_instance
    )

    # 역할 관리 메서드 추가
    ide_instance.get_role_controller = (
        lambda role_type: ide_instance.role_controllers.get(role_type)
    )
    ide_instance.list_available_roles = lambda: list(
        ide_instance.role_controllers.keys()
    )

    # 자연어 처리기와 연동
    if hasattr(ide_instance, "natural_processor"):
        ide_instance.natural_processor.role_controllers = ide_instance.role_controllers

    print("🎭 역할 기반 제어 시스템이 Echo IDE에 통합되었습니다")
    print(f"사용 가능한 역할: {', '.join(ide_instance.role_controllers.keys())}")

    return ide_instance.role_controllers


async def demonstrate_role_capabilities(ide_instance):
    """역할별 능력 시연"""

    if not hasattr(ide_instance, "role_controllers"):
        print("❌ 역할 제어 시스템이 통합되지 않았습니다")
        return

    print("🎭 역할별 능력 시연 시작")
    print("=" * 50)

    # 1. 코드 생성 역할 시연
    print("\n💻 코드 생성 역할 시연:")
    code_gen = ide_instance.role_controllers["code_generator"]
    session_id = await code_gen.start_session(duration_hours=1)

    # 간단한 Python 클래스 생성
    result = await code_gen.execute_operation(
        "generate_code",
        {
            "type": "class",
            "language": "python",
            "name": "DataProcessor",
            "description": "데이터 처리를 위한 클래스",
        },
    )
    print(f"  코드 생성 결과: {result['status']}")

    # 2. 시스템 제어 역할 시연
    print("\n🎛️ 시스템 제어 역할 시연:")
    sys_ctrl = ide_instance.role_controllers["system_controller"]
    session_id = await sys_ctrl.start_session(duration_hours=1)

    # 시스템 상태 확인
    result = await sys_ctrl.execute_operation("check_status", {})
    print(f"  시스템 상태 확인: {result['status']}")

    # 3. 분석 어시스턴트 역할 시연
    print("\n🔍 분석 어시스턴트 역할 시연:")
    analyst = ide_instance.role_controllers["analyst_assistant"]
    session_id = await analyst.start_session(duration_hours=1)

    # 분석 타겟 스캔
    await analyst._scan_analysis_targets()
    stats = analyst.get_analysis_stats()
    print(f"  분석 가능한 파일: {stats}")

    print("\n✅ 역할별 능력 시연 완료")
