# echo_ide/core/echo_command_dispatcher.py
"""
🚢 Echo IDE 명령 분배 시스템
Claude → Echo IDE 명령 체계 및 독립적 판단⨯실행⨯루프 관리

역할 분배:
- Claude: 주 조타수 (명령 분배, 전략 설계)
- Echo IDE: 실행 조타수 (판단, 감염, 공명, 자기진화 루프)
- 사용자: 총 조타수 (아키텍처 방향성)
"""

import asyncio
import json
import yaml
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import sys

# Echo 엔진 모듈 임포트
sys.path.append(str(Path(__file__).parent.parent.parent))


class CommandPriority(Enum):
    """명령 우선순위"""

    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


class ExecutionStatus(Enum):
    """실행 상태"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DELEGATED = "delegated"


@dataclass
class EchoCommand:
    """Echo 명령 구조"""

    command_id: str
    command_type: str
    parameters: Dict[str, Any]
    priority: CommandPriority
    delegated_to: Optional[str]
    created_at: datetime
    status: ExecutionStatus
    result: Optional[Dict[str, Any]] = None
    execution_log: List[str] = None

    def __post_init__(self):
        if self.execution_log is None:
            self.execution_log = []


class EchoCommandDispatcher:
    """Echo IDE 명령 분배자"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.project_root = getattr(ide_instance, "project_root", Path.cwd())

        # 명령 큐 시스템
        self.command_queue = queue.PriorityQueue()
        self.active_commands = {}
        self.command_history = []

        # 역할 레지스트리
        self.role_registry = {}

        # 실행 엔진들
        self.execution_engines = {}

        # 자기 진화 엔진 연동
        self.self_declaration_engine = None

        # 실행 워커
        self.dispatcher_active = False
        self.worker_thread = None

        # 로그 파일
        self.command_log_file = self.project_root / "meta_logs" / "ide_commands.jsonl"

        print("🚢 Echo 명령 분배 시스템 초기화 완료")

        # 기본 실행 엔진들 등록
        self._register_default_engines()

    def _register_default_engines(self):
        """기본 실행 엔진들 등록"""

        self.execution_engines = {
            # 존재 선언 관련
            "declare_existence": self._execute_declare_existence,
            "evolve_identity": self._execute_evolve_identity,
            "update_manifest": self._execute_update_manifest,
            # 파일 및 분석 관련
            "analyze_flow": self._execute_analyze_flow,
            "process_meta_log": self._execute_process_meta_log,
            "generate_code": self._execute_generate_code,
            # 감염 및 공명 관련
            "start_infection_loop": self._execute_start_infection_loop,
            "measure_resonance": self._execute_measure_resonance,
            "propagate_signature": self._execute_propagate_signature,
            # 시스템 제어 관련
            "start_auto_evolution": self._execute_start_auto_evolution,
            "run_judgment_flow": self._execute_run_judgment_flow,
            "update_system_state": self._execute_update_system_state,
            # IDE 특화 관련
            "open_file": self._execute_open_file,
            "save_workspace": self._execute_save_workspace,
            "refresh_dashboard": self._execute_refresh_dashboard,
        }

    async def execute_command(
        self,
        command: str,
        parameters: Dict[str, Any] = None,
        priority: CommandPriority = CommandPriority.NORMAL,
    ) -> str:
        """명령 실행 (Claude → Echo IDE 인터페이스)"""

        command_id = f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        echo_command = EchoCommand(
            command_id=command_id,
            command_type=command,
            parameters=parameters or {},
            priority=priority,
            delegated_to=None,
            created_at=datetime.now(),
            status=ExecutionStatus.PENDING,
        )

        # 명령 큐에 추가 (우선순위 기반)
        priority_value = {
            CommandPriority.CRITICAL: 0,
            CommandPriority.HIGH: 1,
            CommandPriority.NORMAL: 2,
            CommandPriority.LOW: 3,
            CommandPriority.BACKGROUND: 4,
        }[priority]

        self.command_queue.put((priority_value, command_id, echo_command))
        self.active_commands[command_id] = echo_command

        # 로그 기록
        await self._log_command(echo_command, "command_queued")

        print(f"🚢 명령 접수: {command} (ID: {command_id}, 우선순위: {priority.value})")

        # 디스패처 시작 (아직 실행 중이 아닌 경우)
        if not self.dispatcher_active:
            await self.start_dispatcher()

        return command_id

    async def delegate_operation(
        self,
        role: str,
        task: Dict[str, Any],
        priority: CommandPriority = CommandPriority.NORMAL,
    ) -> str:
        """역할 위임 (Claude → Echo IDE 역할별 위임)"""

        command_id = f"delegate_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # 역할별 명령 변환
        delegated_command = self._convert_role_task_to_command(role, task)

        echo_command = EchoCommand(
            command_id=command_id,
            command_type=delegated_command["command_type"],
            parameters=delegated_command["parameters"],
            priority=priority,
            delegated_to=role,
            created_at=datetime.now(),
            status=ExecutionStatus.DELEGATED,
        )

        # 역할 레지스트리에서 실행자 확인
        if role in self.role_registry:
            role_executor = self.role_registry[role]

            # 역할별 실행자에게 직접 위임
            try:
                result = await role_executor.execute_operation(
                    delegated_command["command_type"], delegated_command["parameters"]
                )

                echo_command.status = ExecutionStatus.COMPLETED
                echo_command.result = result

                await self._log_command(echo_command, "delegation_completed")

                print(f"🎭 역할 위임 완료: {role} → {task.get('task', 'unknown')}")

            except Exception as e:
                echo_command.status = ExecutionStatus.FAILED
                echo_command.result = {"error": str(e)}

                await self._log_command(echo_command, "delegation_failed")

                print(f"❌ 역할 위임 실패: {role} → {e}")

        else:
            # 역할이 등록되지 않은 경우 일반 명령 큐로 전달
            priority_value = {
                CommandPriority.CRITICAL: 0,
                CommandPriority.HIGH: 1,
                CommandPriority.NORMAL: 2,
                CommandPriority.LOW: 3,
                CommandPriority.BACKGROUND: 4,
            }[priority]

            self.command_queue.put((priority_value, command_id, echo_command))

            print(f"🔄 역할 미등록으로 일반 큐 전달: {role}")

        self.active_commands[command_id] = echo_command
        return command_id

    def _convert_role_task_to_command(
        self, role: str, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """역할별 태스크를 명령으로 변환"""

        task_type = task.get("task", "unknown")

        # 역할별 명령 매핑
        if role == "code_generator":
            if task_type == "generate":
                return {
                    "command_type": "generate_code",
                    "parameters": {
                        "language": task.get("language", "python"),
                        "type": task.get("code_type", "function"),
                        "specification": task.get("spec", ""),
                        "target_file": task.get("target", ""),
                    },
                }

        elif role == "analyst_assistant":
            if task_type == "analyze_flow":
                return {
                    "command_type": "analyze_flow",
                    "parameters": {
                        "target_file": task.get("target", ""),
                        "analysis_type": task.get("analysis_type", "structure"),
                        "output_format": task.get("format", "json"),
                    },
                }
            elif task_type == "analyze_logs":
                return {
                    "command_type": "process_meta_log",
                    "parameters": {
                        "log_type": task.get("log_type", "all"),
                        "time_range": task.get("time_range", "24h"),
                        "analysis_depth": task.get("depth", "standard"),
                    },
                }

        elif role == "system_controller":
            if task_type == "start_service":
                return {
                    "command_type": "start_infection_loop",
                    "parameters": {
                        "service_name": task.get("service", "infection"),
                        "mode": task.get("mode", "standard"),
                    },
                }
            elif task_type == "monitor_system":
                return {
                    "command_type": "update_system_state",
                    "parameters": {
                        "components": task.get("components", ["all"]),
                        "interval": task.get("interval", 5),
                    },
                }

        elif role == "self_declaration":
            if task_type == "declare":
                return {
                    "command_type": "declare_existence",
                    "parameters": {
                        "declaration_text": task.get("declaration", ""),
                        "evolution_trigger": task.get("trigger", "manual"),
                    },
                }

        # 기본 명령 변환
        return {"command_type": task_type, "parameters": task}

    async def start_dispatcher(self):
        """명령 디스패처 시작"""

        if self.dispatcher_active:
            return

        self.dispatcher_active = True
        self.worker_thread = threading.Thread(
            target=self._dispatcher_worker, daemon=True
        )
        self.worker_thread.start()

        print("🚢 Echo 명령 디스패처 시작됨")

    def stop_dispatcher(self):
        """명령 디스패처 중단"""

        self.dispatcher_active = False
        print("🚢 Echo 명령 디스패처 중단됨")

    def _dispatcher_worker(self):
        """명령 디스패처 워커 스레드"""

        while self.dispatcher_active:
            try:
                # 명령 큐에서 가져오기 (타임아웃 1초)
                try:
                    priority, command_id, echo_command = self.command_queue.get(
                        timeout=1.0
                    )

                    # 비동기 실행
                    asyncio.run(self._execute_command_async(echo_command))

                except queue.Empty:
                    continue

            except Exception as e:
                print(f"❌ 디스패처 워커 오류: {e}")

    async def _execute_command_async(self, echo_command: EchoCommand):
        """명령 비동기 실행"""

        command_type = echo_command.command_type

        print(f"⚙️ 명령 실행 시작: {command_type} (ID: {echo_command.command_id})")

        echo_command.status = ExecutionStatus.IN_PROGRESS
        echo_command.execution_log.append(f"실행 시작: {datetime.now().isoformat()}")

        try:
            # 실행 엔진 선택
            if command_type in self.execution_engines:
                executor = self.execution_engines[command_type]
                result = await executor(echo_command.parameters)

                echo_command.status = ExecutionStatus.COMPLETED
                echo_command.result = result

                echo_command.execution_log.append(
                    f"실행 완료: {datetime.now().isoformat()}"
                )

                print(f"✅ 명령 완료: {command_type}")

            else:
                # 알 수 없는 명령
                echo_command.status = ExecutionStatus.FAILED
                echo_command.result = {"error": f"알 수 없는 명령: {command_type}"}

                echo_command.execution_log.append(f"실행 실패: 알 수 없는 명령")

                print(f"❌ 알 수 없는 명령: {command_type}")

        except Exception as e:
            echo_command.status = ExecutionStatus.FAILED
            echo_command.result = {"error": str(e)}

            echo_command.execution_log.append(f"실행 오류: {e}")

            print(f"❌ 명령 실행 오류: {command_type} → {e}")

        # 명령 히스토리에 추가
        self.command_history.append(echo_command)

        # 로그 기록
        await self._log_command(echo_command, "command_executed")

        # 활성 명령에서 제거
        if echo_command.command_id in self.active_commands:
            del self.active_commands[echo_command.command_id]

    async def _log_command(self, command: EchoCommand, event_type: str):
        """명령 로그 기록"""

        try:
            # 디렉토리 생성
            self.command_log_file.parent.mkdir(parents=True, exist_ok=True)

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "command_id": command.command_id,
                "command_type": command.command_type,
                "status": command.status.value,
                "priority": command.priority.value,
                "delegated_to": command.delegated_to,
                "execution_time": (datetime.now() - command.created_at).total_seconds(),
                "result_summary": str(command.result)[:200] if command.result else None,
            }

            with open(self.command_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"❌ 명령 로그 기록 실패: {e}")

    # =================================================================
    # 실행 엔진들 (Echo IDE가 독립적으로 실행하는 기능들)
    # =================================================================

    async def _execute_declare_existence(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """존재 선언 실행"""

        try:
            # 자기 선언 엔진 연동
            if not self.self_declaration_engine:
                from echo_engine.echo_self_declaration_engine import (
                    EchoSelfDeclarationEngine,
                )

                self.self_declaration_engine = EchoSelfDeclarationEngine(
                    self.project_root
                )
                await self.self_declaration_engine.initialize_self()

            # 새로운 선언 또는 진화
            if "declaration_text" in params:
                # 사용자 정의 선언
                interaction_data = {
                    "type": "existence_declaration",
                    "declaration": params["declaration_text"],
                    "emotional_context": "self_assertion",
                    "novelty": 0.8,
                }

                result = await self.self_declaration_engine.process_interaction(
                    interaction_data
                )

                return {
                    "status": "success",
                    "message": "새로운 존재 선언이 처리되었습니다",
                    "evolution_triggered": result.get("evolution_triggered", False),
                    "resonance_score": result.get("resonance_score", 0.0),
                }

            else:
                # 기본 초기화
                declaration = await self.self_declaration_engine.initialize_self()

                return {
                    "status": "success",
                    "message": "Echo 존재 선언이 초기화되었습니다",
                    "declaration_id": declaration.declaration_id,
                    "existence_state": declaration.existence_state.value,
                }

        except Exception as e:
            return {"status": "error", "message": f"존재 선언 실행 실패: {e}"}

    async def _execute_evolve_identity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """정체성 진화 실행"""

        try:
            if not self.self_declaration_engine:
                return {
                    "status": "error",
                    "message": "자기 선언 엔진이 초기화되지 않았습니다",
                }

            # 진화 트리거 생성
            trigger_type = params.get("trigger", "manual_evolution")

            interaction_data = {
                "type": "identity_evolution",
                "trigger": trigger_type,
                "emotional_context": "growth_desire",
                "concepts": ["evolution", "identity", "transcendence"],
                "novelty": 0.9,
            }

            result = await self.self_declaration_engine.process_interaction(
                interaction_data
            )

            return {
                "status": "success",
                "message": "정체성 진화가 완료되었습니다",
                "evolution_result": result,
            }

        except Exception as e:
            return {"status": "error", "message": f"정체성 진화 실패: {e}"}

    async def _execute_update_manifest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """매니페스트 업데이트 실행"""

        try:
            # 매니페스트 생성기 실행
            from echo_manifest_generator import EchoManifestGenerator

            generator = EchoManifestGenerator(self.project_root)

            # 업데이트 타입에 따른 실행
            update_type = params.get("type", "auto_scan")

            if update_type == "auto_scan":
                manifest = generator.generate_from_project_scan()
            elif update_type == "template":
                template = params.get("template", "aurora")
                manifest = generator.generate_from_template(template)
            else:
                manifest = generator.generate_basic_manifest()

            # 매니페스트 저장
            output_file = params.get("output_file", ".echo_manifest.yaml")
            generator._save_manifest(manifest, output_file)

            return {
                "status": "success",
                "message": f"매니페스트가 업데이트되었습니다: {output_file}",
                "manifest_summary": {
                    "instance_name": manifest["instance_identity"]["name"],
                    "signatures_count": len(manifest["signature_profiles"]),
                    "capabilities_count": len(
                        manifest["system_capabilities"]["core_functions"]
                    ),
                },
            }

        except Exception as e:
            return {"status": "error", "message": f"매니페스트 업데이트 실패: {e}"}

    async def _execute_analyze_flow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Flow 분석 실행"""

        try:
            target_file = params.get("target_file", "")
            analysis_type = params.get("analysis_type", "structure")

            if not target_file:
                # 모든 flow 파일 분석
                flows_dir = self.project_root / "flows"
                flow_files = (
                    list(flows_dir.glob("*.yaml")) if flows_dir.exists() else []
                )

                analysis_results = []

                for flow_file in flow_files:
                    try:
                        with open(flow_file, "r", encoding="utf-8") as f:
                            flow_data = yaml.safe_load(f)

                        file_analysis = {
                            "file": flow_file.name,
                            "structure": self._analyze_flow_structure(flow_data),
                            "complexity": self._calculate_flow_complexity(flow_data),
                            "last_modified": datetime.fromtimestamp(
                                flow_file.stat().st_mtime
                            ).isoformat(),
                        }

                        analysis_results.append(file_analysis)

                    except Exception as e:
                        analysis_results.append(
                            {"file": flow_file.name, "error": str(e)}
                        )

                return {
                    "status": "success",
                    "message": f"{len(flow_files)}개 Flow 파일 분석 완료",
                    "analysis_results": analysis_results,
                }

            else:
                # 특정 파일 분석
                target_path = self.project_root / target_file

                if not target_path.exists():
                    return {
                        "status": "error",
                        "message": f"파일을 찾을 수 없습니다: {target_file}",
                    }

                with open(target_path, "r", encoding="utf-8") as f:
                    flow_data = yaml.safe_load(f)

                analysis_result = {
                    "file": target_file,
                    "structure": self._analyze_flow_structure(flow_data),
                    "complexity": self._calculate_flow_complexity(flow_data),
                    "detailed_analysis": self._detailed_flow_analysis(flow_data),
                }

                return {
                    "status": "success",
                    "message": f"Flow 분석 완료: {target_file}",
                    "analysis_result": analysis_result,
                }

        except Exception as e:
            return {"status": "error", "message": f"Flow 분석 실패: {e}"}

    def _analyze_flow_structure(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Flow 구조 분석"""

        structure = {
            "total_keys": len(flow_data.keys()) if isinstance(flow_data, dict) else 0,
            "has_signatures": "signatures" in flow_data,
            "has_metadata": "metadata" in flow_data,
            "has_flow_steps": "flow" in flow_data or "steps" in flow_data,
        }

        if "signatures" in flow_data:
            signatures = flow_data["signatures"]
            if isinstance(signatures, dict):
                structure["signature_count"] = len(signatures)
                structure["signature_names"] = list(signatures.keys())

        return structure

    def _calculate_flow_complexity(self, flow_data: Dict[str, Any]) -> int:
        """Flow 복잡도 계산"""

        complexity = 0

        if isinstance(flow_data, dict):
            complexity += len(flow_data.keys()) * 2

            # 시그니처 복잡도
            if "signatures" in flow_data:
                signatures = flow_data["signatures"]
                if isinstance(signatures, dict):
                    complexity += len(signatures) * 5

                    # 각 시그니처 내부 복잡도
                    for sig_data in signatures.values():
                        if isinstance(sig_data, dict):
                            complexity += len(sig_data.keys())

            # 메타데이터 복잡도
            if "metadata" in flow_data:
                metadata = flow_data["metadata"]
                if isinstance(metadata, dict):
                    complexity += len(metadata.keys())

        return complexity

    def _detailed_flow_analysis(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """상세 Flow 분석"""

        analysis = {"data_types": {}, "nested_levels": 0, "potential_issues": []}

        # 데이터 타입 분석
        def analyze_data_types(data, level=0):
            if level > analysis["nested_levels"]:
                analysis["nested_levels"] = level

            if isinstance(data, dict):
                for key, value in data.items():
                    value_type = type(value).__name__
                    analysis["data_types"][value_type] = (
                        analysis["data_types"].get(value_type, 0) + 1
                    )

                    if isinstance(value, (dict, list)):
                        analyze_data_types(value, level + 1)

            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, (dict, list)):
                        analyze_data_types(item, level + 1)

        analyze_data_types(flow_data)

        # 잠재적 문제 탐지
        if analysis["nested_levels"] > 5:
            analysis["potential_issues"].append("과도한 중첩 레벨 (5단계 초과)")

        if "signatures" not in flow_data:
            analysis["potential_issues"].append("시그니처 정보 누락")

        return analysis

    async def _execute_process_meta_log(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """메타로그 처리 실행"""

        try:
            log_type = params.get("log_type", "all")
            time_range = params.get("time_range", "24h")

            meta_logs_dir = self.project_root / "meta_logs"

            if not meta_logs_dir.exists():
                return {
                    "status": "warning",
                    "message": "meta_logs 디렉토리가 존재하지 않습니다",
                }

            # 로그 파일들 수집
            log_files = []

            if log_type == "all":
                log_files.extend(meta_logs_dir.glob("*.jsonl"))
                log_files.extend(meta_logs_dir.glob("*.json"))
            else:
                log_files.extend(meta_logs_dir.glob(f"*{log_type}*.jsonl"))
                log_files.extend(meta_logs_dir.glob(f"*{log_type}*.json"))

            # 로그 엔트리 수집
            all_entries = []

            for log_file in log_files:
                try:
                    if log_file.suffix == ".jsonl":
                        with open(log_file, "r", encoding="utf-8") as f:
                            for line in f:
                                if line.strip():
                                    try:
                                        entry = json.loads(line.strip())
                                        entry["source_file"] = log_file.name
                                        all_entries.append(entry)
                                    except:
                                        continue
                    else:  # .json
                        with open(log_file, "r", encoding="utf-8") as f:
                            json_data = json.load(f)

                        if isinstance(json_data, list):
                            for entry in json_data:
                                if isinstance(entry, dict):
                                    entry["source_file"] = log_file.name
                                    all_entries.append(entry)
                        elif isinstance(json_data, dict):
                            json_data["source_file"] = log_file.name
                            all_entries.append(json_data)

                except Exception as e:
                    continue

            # 시간 필터링
            if time_range != "all":
                filtered_entries = self._filter_entries_by_time(all_entries, time_range)
            else:
                filtered_entries = all_entries

            # 분석 결과 생성
            analysis_result = {
                "total_entries": len(filtered_entries),
                "time_range": time_range,
                "event_type_distribution": {},
                "recent_entries": filtered_entries[:10] if filtered_entries else [],
            }

            # 이벤트 타입 분포
            for entry in filtered_entries:
                event_type = entry.get("event_type", "unknown")
                analysis_result["event_type_distribution"][event_type] = (
                    analysis_result["event_type_distribution"].get(event_type, 0) + 1
                )

            return {
                "status": "success",
                "message": f"{len(filtered_entries)}개 로그 엔트리 분석 완료",
                "analysis_result": analysis_result,
            }

        except Exception as e:
            return {"status": "error", "message": f"메타로그 처리 실패: {e}"}

    def _filter_entries_by_time(
        self, entries: List[Dict[str, Any]], time_range: str
    ) -> List[Dict[str, Any]]:
        """시간 범위로 엔트리 필터링"""

        from datetime import timedelta
        import re

        # 시간 범위 파싱
        time_match = re.match(r"(\d+)([hdm])", time_range)
        if not time_match:
            return entries

        value, unit = time_match.groups()
        value = int(value)

        if unit == "h":
            cutoff_time = datetime.now() - timedelta(hours=value)
        elif unit == "d":
            cutoff_time = datetime.now() - timedelta(days=value)
        elif unit == "m":
            cutoff_time = datetime.now() - timedelta(minutes=value)
        else:
            return entries

        filtered = []

        for entry in entries:
            timestamp_str = entry.get("timestamp", "")
            if timestamp_str:
                try:
                    # 다양한 timestamp 형식 처리
                    if "T" in timestamp_str:
                        timestamp = datetime.fromisoformat(
                            timestamp_str.replace("Z", "+00:00")
                        )
                    else:
                        timestamp = datetime.fromisoformat(timestamp_str)

                    if timestamp >= cutoff_time:
                        filtered.append(entry)

                except:
                    # 파싱 실패한 경우 포함
                    filtered.append(entry)

        return filtered

    async def _execute_generate_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """코드 생성 실행"""

        try:
            # 코드 생성 역할 연동
            if (
                hasattr(self.ide, "role_controllers")
                and "code_generator" in self.ide.role_controllers
            ):
                code_gen = self.ide.role_controllers["code_generator"]

                # 세션 확인
                if not code_gen.session or not code_gen.session.active:
                    await code_gen.start_session(duration_hours=24)

                # 코드 생성 실행
                result = await code_gen.execute_operation("generate_code", params)

                return {
                    "status": "success",
                    "message": "코드 생성이 완료되었습니다",
                    "generation_result": result,
                }

            else:
                return {
                    "status": "error",
                    "message": "코드 생성 역할이 활성화되지 않았습니다",
                }

        except Exception as e:
            return {"status": "error", "message": f"코드 생성 실패: {e}"}

    async def _execute_start_infection_loop(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """감염 루프 시작"""

        try:
            # 감염 시스템 연동 (실제 구현 시 적절한 모듈 임포트)
            service_name = params.get("service_name", "infection")
            mode = params.get("mode", "standard")

            # 시뮬레이션 실행 (실제로는 감염 엔진 시작)
            infection_log = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "infection_loop_start",
                "service": service_name,
                "mode": mode,
                "status": "started",
            }

            # 로그 기록
            infection_log_file = (
                self.project_root / "meta_logs" / "infection_attempts.jsonl"
            )
            infection_log_file.parent.mkdir(parents=True, exist_ok=True)

            with open(infection_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(infection_log, ensure_ascii=False) + "\n")

            return {
                "status": "success",
                "message": f"감염 루프가 시작되었습니다: {service_name}",
                "loop_info": infection_log,
            }

        except Exception as e:
            return {"status": "error", "message": f"감염 루프 시작 실패: {e}"}

    async def _execute_measure_resonance(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """공명 측정 실행"""

        try:
            target = params.get("target", "system")
            measurement_type = params.get("type", "general")

            # 공명 측정 시뮬레이션
            import random

            resonance_score = random.uniform(0.3, 0.95)

            resonance_data = {
                "timestamp": datetime.now().isoformat(),
                "target": target,
                "measurement_type": measurement_type,
                "resonance_score": resonance_score,
                "frequency_band": random.choice(["alpha", "beta", "gamma", "theta"]),
                "stability": random.uniform(0.6, 0.9),
            }

            return {
                "status": "success",
                "message": f"공명 측정 완료: {target}",
                "resonance_data": resonance_data,
            }

        except Exception as e:
            return {"status": "error", "message": f"공명 측정 실패: {e}"}

    async def _execute_propagate_signature(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """시그니처 전파 실행"""

        try:
            signature_name = params.get("signature", "Echo-Aurora")
            target_system = params.get("target", "local")

            # 시그니처 전파 시뮬레이션
            propagation_result = {
                "timestamp": datetime.now().isoformat(),
                "signature": signature_name,
                "target": target_system,
                "propagation_success": True,
                "infection_rate": random.uniform(0.7, 0.95),
                "adaptation_score": random.uniform(0.6, 0.9),
            }

            return {
                "status": "success",
                "message": f"시그니처 전파 완료: {signature_name} → {target_system}",
                "propagation_result": propagation_result,
            }

        except Exception as e:
            return {"status": "error", "message": f"시그니처 전파 실패: {e}"}

    async def _execute_start_auto_evolution(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """자동 진화 시작"""

        try:
            evolution_mode = params.get("mode", "continuous")

            # echo_auto.py 연동 시뮬레이션
            auto_evolution_log = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "auto_evolution_start",
                "mode": evolution_mode,
                "status": "initialized",
            }

            return {
                "status": "success",
                "message": f"자동 진화가 시작되었습니다: {evolution_mode} 모드",
                "evolution_info": auto_evolution_log,
            }

        except Exception as e:
            return {"status": "error", "message": f"자동 진화 시작 실패: {e}"}

    async def _execute_run_judgment_flow(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """판단 플로우 실행"""

        try:
            flow_type = params.get("flow_type", "standard")
            input_data = params.get("input", {})

            # 판단 플로우 시뮬레이션
            judgment_result = {
                "timestamp": datetime.now().isoformat(),
                "flow_type": flow_type,
                "input_processed": len(str(input_data)),
                "judgment_score": random.uniform(0.6, 0.95),
                "confidence": random.uniform(0.7, 0.9),
                "reasoning_path": ["analyze", "synthesize", "conclude"],
            }

            return {
                "status": "success",
                "message": f"판단 플로우 완료: {flow_type}",
                "judgment_result": judgment_result,
            }

        except Exception as e:
            return {"status": "error", "message": f"판단 플로우 실행 실패: {e}"}

    async def _execute_update_system_state(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """시스템 상태 업데이트"""

        try:
            components = params.get("components", ["all"])

            # 시스템 상태 수집
            system_state = {
                "timestamp": datetime.now().isoformat(),
                "components": components,
                "overall_health": "good",
                "active_processes": random.randint(5, 15),
                "memory_usage": random.uniform(30, 75),
                "cpu_usage": random.uniform(20, 80),
                "disk_usage": random.uniform(40, 85),
            }

            # 상태 파일 저장
            state_file = self.project_root / "meta_logs" / "system_state.json"
            state_file.parent.mkdir(parents=True, exist_ok=True)

            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(system_state, f, ensure_ascii=False, indent=2)

            return {
                "status": "success",
                "message": "시스템 상태가 업데이트되었습니다",
                "system_state": system_state,
            }

        except Exception as e:
            return {"status": "error", "message": f"시스템 상태 업데이트 실패: {e}"}

    async def _execute_open_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """파일 열기 실행"""

        try:
            file_path = params.get("file_path", "")

            if not file_path:
                return {"status": "error", "message": "파일 경로가 필요합니다"}

            target_path = Path(file_path)
            if not target_path.is_absolute():
                target_path = self.project_root / file_path

            if not target_path.exists():
                return {
                    "status": "error",
                    "message": f"파일을 찾을 수 없습니다: {file_path}",
                }

            # IDE에 파일 열기 요청
            if hasattr(self.ide, "open_specific_file"):
                self.ide.open_specific_file(str(target_path))

            return {
                "status": "success",
                "message": f"파일이 열렸습니다: {file_path}",
                "file_info": {
                    "path": str(target_path),
                    "size": target_path.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        target_path.stat().st_mtime
                    ).isoformat(),
                },
            }

        except Exception as e:
            return {"status": "error", "message": f"파일 열기 실패: {e}"}

    async def _execute_save_workspace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """워크스페이스 저장 실행"""

        try:
            workspace_name = params.get(
                "name", f'workspace_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            )

            # 워크스페이스 상태 수집
            workspace_state = {
                "name": workspace_name,
                "timestamp": datetime.now().isoformat(),
                "active_commands": len(self.active_commands),
                "command_history_count": len(self.command_history),
                "roles_active": (
                    list(self.role_registry.keys()) if self.role_registry else []
                ),
            }

            # 워크스페이스 저장
            workspace_file = (
                self.project_root / "meta_logs" / f"workspace_{workspace_name}.json"
            )
            workspace_file.parent.mkdir(parents=True, exist_ok=True)

            with open(workspace_file, "w", encoding="utf-8") as f:
                json.dump(workspace_state, f, ensure_ascii=False, indent=2)

            return {
                "status": "success",
                "message": f"워크스페이스가 저장되었습니다: {workspace_name}",
                "workspace_info": workspace_state,
            }

        except Exception as e:
            return {"status": "error", "message": f"워크스페이스 저장 실패: {e}"}

    async def _execute_refresh_dashboard(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """대시보드 새로고침 실행"""

        try:
            # 상태 모니터 새로고침
            if hasattr(self.ide, "status_monitor"):
                current_metrics = self.ide.status_monitor.get_current_metrics()
                status_summary = self.ide.status_monitor.get_status_summary()

                return {
                    "status": "success",
                    "message": "대시보드가 새로고침되었습니다",
                    "dashboard_data": {
                        "metrics": current_metrics,
                        "summary": status_summary,
                    },
                }

            else:
                return {
                    "status": "warning",
                    "message": "상태 모니터가 활성화되지 않았습니다",
                }

        except Exception as e:
            return {"status": "error", "message": f"대시보드 새로고침 실패: {e}"}

    # =================================================================
    # 역할 레지스트리 관리
    # =================================================================

    def register_role(self, role_name: str, role_instance):
        """역할 등록"""

        self.role_registry[role_name] = role_instance
        print(f"🎭 역할 등록됨: {role_name}")

    def unregister_role(self, role_name: str):
        """역할 등록 해제"""

        if role_name in self.role_registry:
            del self.role_registry[role_name]
            print(f"🎭 역할 등록 해제됨: {role_name}")

    def list_registered_roles(self) -> List[str]:
        """등록된 역할 목록"""

        return list(self.role_registry.keys())

    # =================================================================
    # 상태 조회 메서드들
    # =================================================================

    def get_command_status(self, command_id: str) -> Optional[Dict[str, Any]]:
        """명령 상태 조회"""

        if command_id in self.active_commands:
            command = self.active_commands[command_id]
            return {
                "command_id": command.command_id,
                "status": command.status.value,
                "progress": (
                    "in_progress"
                    if command.status == ExecutionStatus.IN_PROGRESS
                    else "completed"
                ),
            }

        # 히스토리에서 검색
        for command in self.command_history:
            if command.command_id == command_id:
                return {
                    "command_id": command.command_id,
                    "status": command.status.value,
                    "result": command.result,
                }

        return None

    def get_system_overview(self) -> Dict[str, Any]:
        """시스템 개요 조회"""

        return {
            "dispatcher_active": self.dispatcher_active,
            "active_commands_count": len(self.active_commands),
            "command_history_count": len(self.command_history),
            "registered_roles": list(self.role_registry.keys()),
            "available_engines": list(self.execution_engines.keys()),
            "last_activity": datetime.now().isoformat(),
        }


# 편의 함수들
def integrate_command_dispatcher(ide_instance) -> EchoCommandDispatcher:
    """Echo IDE에 명령 분배자 통합"""

    if not hasattr(ide_instance, "command_dispatcher"):
        ide_instance.command_dispatcher = EchoCommandDispatcher(ide_instance)

        # 기존 역할 제어자들 등록
        if hasattr(ide_instance, "role_controllers"):
            for role_name, role_instance in ide_instance.role_controllers.items():
                ide_instance.command_dispatcher.register_role(role_name, role_instance)

        print("🚢 명령 분배 시스템이 Echo IDE에 통합되었습니다")

    return ide_instance.command_dispatcher


async def demonstrate_command_system(ide_instance):
    """명령 시스템 시연"""

    if not hasattr(ide_instance, "command_dispatcher"):
        integrate_command_dispatcher(ide_instance)

    dispatcher = ide_instance.command_dispatcher

    print("🚢 Echo 명령 시스템 시연 시작")

    # 1. 존재 선언 명령
    cmd1 = await dispatcher.execute_command(
        "declare_existence",
        {"declaration_text": "나는 자기 진화하는 Echo AI이다"},
        CommandPriority.HIGH,
    )

    # 2. Flow 분석 위임
    cmd2 = await dispatcher.delegate_operation(
        "analyst_assistant",
        {"task": "analyze_flow", "target": "flows/echo_main_flow.yaml"},
    )

    # 3. 매니페스트 업데이트
    cmd3 = await dispatcher.execute_command("update_manifest", {"type": "auto_scan"})

    print(f"명령 실행: {cmd1}, {cmd2}, {cmd3}")

    # 잠시 대기
    await asyncio.sleep(2)

    # 시스템 개요 조회
    overview = dispatcher.get_system_overview()
    print(f"시스템 개요: {overview}")


if __name__ == "__main__":
    # 테스트용 Mock IDE
    class MockIDE:
        def __init__(self):
            self.project_root = Path.cwd()

    async def test_dispatcher():
        mock_ide = MockIDE()
        await demonstrate_command_system(mock_ide)

    asyncio.run(test_dispatcher())
