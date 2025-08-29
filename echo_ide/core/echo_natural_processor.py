# echo_ide/core/echo_natural_processor.py
"""
🗣️ Echo IDE 자연어 지시처리기
- 자연어 명령 해석 및 실행
- 존재선언과 역할 위임 시스템
- 내부 명령 해석기
- 상황 인식 및 적응적 처리
"""

import re
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from pathlib import Path


class CommandType(Enum):
    """명령 타입"""

    EXISTENCE_DECLARATION = "existence_declaration"
    ROLE_DELEGATION = "role_delegation"
    FILE_OPERATION = "file_operation"
    SYSTEM_CONTROL = "system_control"
    CODE_GENERATION = "code_generation"
    ANALYSIS_REQUEST = "analysis_request"
    MONITORING_CONTROL = "monitoring_control"
    AI_INTERACTION = "ai_interaction"
    ECHO_SPECIFIC = "echo_specific"


class ExecutionPriority(Enum):
    """실행 우선순위"""

    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class ExistenceDeclaration:
    """존재선언 구조"""

    entity_id: str
    entity_type: str  # 'signature', 'persona', 'module', 'system'
    capabilities: List[str]
    responsibilities: List[str]
    scope: str
    authority_level: int  # 1-10
    creation_context: str
    timestamp: datetime


@dataclass
class RoleDelegation:
    """역할 위임 구조"""

    delegation_id: str
    from_entity: str
    to_entity: str
    delegated_role: str
    scope_limitations: List[str]
    authority_transfer: Dict[str, int]
    duration: Optional[str]
    conditions: List[str]
    callbacks: List[str]
    timestamp: datetime


@dataclass
class ProcessedCommand:
    """처리된 명령"""

    command_id: str
    original_text: str
    command_type: CommandType
    priority: ExecutionPriority
    extracted_entities: Dict[str, str]
    parameters: Dict[str, Any]
    execution_plan: List[Dict[str, Any]]
    context: Dict[str, Any]
    timestamp: datetime


class EchoNaturalProcessor:
    """Echo IDE 자연어 지시처리기"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.project_root = (
            ide_instance.project_root
            if hasattr(ide_instance, "project_root")
            else Path.cwd()
        )

        # 존재선언 레지스트리
        self.existence_registry = {}

        # 역할 위임 체인
        self.delegation_chain = {}

        # 명령 히스토리
        self.command_history = []

        # 처리 중인 명령들
        self.active_commands = {}

        # 자연어 패턴 매칭
        self.command_patterns = self._initialize_patterns()

        # 실행 엔진들
        self.execution_engines = self._initialize_engines()

        # 컨텍스트 추적기
        self.context_tracker = {
            "current_entities": {},
            "active_roles": {},
            "system_state": {},
            "conversation_context": [],
        }

        print("🗣️ Echo Natural Processor 초기화 완료")

    def _initialize_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """자연어 패턴 초기화"""

        patterns = {
            CommandType.EXISTENCE_DECLARATION: [
                {
                    "pattern": r"(나는|내가|여기서)\s*(.+?)(이다|다|로서|로써|가\s*될\s*것이다)",
                    "groups": [
                        "declaration_prefix",
                        "entity_description",
                        "declaration_suffix",
                    ],
                    "context_hints": ["자아선언", "역할정의", "정체성"],
                },
                {
                    "pattern": r"(.+?)(을|를|로)\s*(생성|만들|선언|정의)해?줘",
                    "groups": ["target_entity", "particle", "action"],
                    "context_hints": ["생성요청", "정의요청"],
                },
                {
                    "pattern": r"Echo-(\w+)\s*(시그니처|페르소나|에이전트)(?:를|을)?\s*(존재|선언|생성)(?:해줘|하자|하기)",
                    "groups": ["entity_name", "entity_type", "action"],
                    "context_hints": ["Echo특화", "시그니처생성"],
                },
            ],
            CommandType.ROLE_DELEGATION: [
                {
                    "pattern": r"(.+?)(?:에게|한테)\s*(.+?)(?:을|를)\s*(맡기|위임|전담|담당)(?:게|도록)\s*(?:해줘|하자|하기)",
                    "groups": ["target_entity", "delegated_task", "action"],
                    "context_hints": ["업무위임", "책임전가"],
                },
                {
                    "pattern": r"(.+?)\s*(?:가|이)\s*(.+?)\s*(?:을|를)\s*(담당|처리|관리)(?:하도록|하게)\s*(?:해줘|하자)",
                    "groups": ["entity", "responsibility", "action"],
                    "context_hints": ["역할할당", "책임배정"],
                },
                {
                    "pattern": r"(.+?)\s*권한(?:을|를)\s*(.+?)(?:에게|한테)\s*(넘기|이양|전달)(?:어|해)(?:줘)?",
                    "groups": ["authority", "target_entity", "action"],
                    "context_hints": ["권한이양", "권한위임"],
                },
            ],
            CommandType.FILE_OPERATION: [
                {
                    "pattern": r"(.+?)\s*파일(?:을|를)\s*(열|만들|생성|삭제|복사)(?:어|아)(?:줘)?",
                    "groups": ["file_target", "operation"],
                    "context_hints": ["파일조작", "파일관리"],
                },
                {
                    "pattern": r"(.+?)\s*(?:을|를)\s*(저장|편집|수정)(?:해|하)(?:줘)?",
                    "groups": ["target", "operation"],
                    "context_hints": ["편집작업", "저장작업"],
                },
            ],
            CommandType.SYSTEM_CONTROL: [
                {
                    "pattern": r"(Echo|시스템|IDE)(?:을|를)?\s*(시작|중단|재시작|종료)(?:해|하)(?:줘)?",
                    "groups": ["system", "action"],
                    "context_hints": ["시스템제어", "상태변경"],
                },
                {
                    "pattern": r"(모니터링|감시|추적)(?:을|를)?\s*(시작|중단|켜|꺼)(?:줘)?",
                    "groups": ["monitoring_type", "action"],
                    "context_hints": ["모니터링제어"],
                },
            ],
            CommandType.CODE_GENERATION: [
                {
                    "pattern": r"(.+?)\s*(?:모듈|클래스|함수)(?:을|를)?\s*(만들|생성|작성)(?:어|아)(?:줘)?",
                    "groups": ["code_target", "action"],
                    "context_hints": ["코드생성", "개발요청"],
                },
                {
                    "pattern": r"(.+?)\s*(?:을|를)?\s*(?:위한|용)\s*코드(?:를)?\s*(생성|만들|작성)(?:해|하)(?:줘)?",
                    "groups": ["purpose", "action"],
                    "context_hints": ["목적지향코딩"],
                },
            ],
            CommandType.ECHO_SPECIFIC: [
                {
                    "pattern": r"(.+?)\s*(?:으로|로)\s*(감염|공명|동화)(?:시켜|하)(?:줘)?",
                    "groups": ["target", "echo_action"],
                    "context_hints": ["Echo감염", "Echo공명"],
                },
                {
                    "pattern": r"(.+?)\s*시그니처(?:로|를)?\s*(테스트|실행|검증)(?:해|하)(?:줘)?",
                    "groups": ["signature", "action"],
                    "context_hints": ["시그니처테스트"],
                },
            ],
        }

        return patterns

    def _initialize_engines(self) -> Dict[str, Callable]:
        """실행 엔진들 초기화"""

        engines = {
            CommandType.EXISTENCE_DECLARATION: self._execute_existence_declaration,
            CommandType.ROLE_DELEGATION: self._execute_role_delegation,
            CommandType.FILE_OPERATION: self._execute_file_operation,
            CommandType.SYSTEM_CONTROL: self._execute_system_control,
            CommandType.CODE_GENERATION: self._execute_code_generation,
            CommandType.ANALYSIS_REQUEST: self._execute_analysis_request,
            CommandType.MONITORING_CONTROL: self._execute_monitoring_control,
            CommandType.AI_INTERACTION: self._execute_ai_interaction,
            CommandType.ECHO_SPECIFIC: self._execute_echo_specific,
        }

        return engines

    async def process_natural_command(
        self, text: str, context: Dict[str, Any] = None
    ) -> ProcessedCommand:
        """자연어 명령 처리"""

        command_id = f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        print(f"🗣️ 자연어 명령 처리 시작: {text[:50]}...")

        # 1. 명령 분석
        command_analysis = await self._analyze_command(text, context or {})

        # 2. 명령 분류
        command_type = self._classify_command(text, command_analysis)

        # 3. 우선순위 결정
        priority = self._determine_priority(command_type, command_analysis)

        # 4. 엔터티 추출
        entities = self._extract_entities(text, command_type)

        # 5. 매개변수 추출
        parameters = self._extract_parameters(text, command_analysis, entities)

        # 6. 실행 계획 생성
        execution_plan = await self._create_execution_plan(
            command_type, parameters, entities
        )

        # 7. 처리된 명령 객체 생성
        processed_command = ProcessedCommand(
            command_id=command_id,
            original_text=text,
            command_type=command_type,
            priority=priority,
            extracted_entities=entities,
            parameters=parameters,
            execution_plan=execution_plan,
            context=self._build_context(text, context),
            timestamp=datetime.now(),
        )

        # 8. 명령 히스토리에 추가
        self.command_history.append(processed_command)

        # 9. 즉시 실행 또는 큐에 추가
        if priority in [ExecutionPriority.CRITICAL, ExecutionPriority.HIGH]:
            await self._execute_command(processed_command)
        else:
            self.active_commands[command_id] = processed_command
            threading.Thread(
                target=self._execute_command_async,
                args=(processed_command,),
                daemon=True,
            ).start()

        return processed_command

    async def _analyze_command(
        self, text: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """명령 분석"""

        analysis = {
            "text_length": len(text),
            "word_count": len(text.split()),
            "contains_echo_terms": any(
                term in text.lower()
                for term in ["echo", "시그니처", "감염", "공명", "페르소나"]
            ),
            "contains_action_verbs": any(
                verb in text
                for verb in ["만들", "생성", "시작", "중단", "실행", "위임", "선언"]
            ),
            "contains_entities": any(
                entity in text
                for entity in ["파일", "모듈", "시스템", "클래스", "함수"]
            ),
            "urgency_indicators": any(
                urgent in text for urgent in ["급히", "빠르게", "즉시", "지금", "당장"]
            ),
            "politeness_level": text.count("해줘")
            + text.count("해주세요")
            + text.count("부탁"),
            "question_indicators": "?" in text
            or any(q in text for q in ["무엇", "어떻게", "왜", "언제", "어디서"]),
            "context_references": len(
                [ref for ref in ["이전", "방금", "아까", "현재", "지금"] if ref in text]
            ),
        }

        return analysis

    def _classify_command(self, text: str, analysis: Dict[str, Any]) -> CommandType:
        """명령 분류"""

        # 패턴 매칭으로 분류
        for command_type, patterns in self.command_patterns.items():
            for pattern_info in patterns:
                if re.search(pattern_info["pattern"], text, re.IGNORECASE):
                    return command_type

        # 키워드 기반 분류
        if analysis["contains_echo_terms"]:
            return CommandType.ECHO_SPECIFIC
        elif any(word in text for word in ["시작", "중단", "재시작"]):
            return CommandType.SYSTEM_CONTROL
        elif any(word in text for word in ["파일", "저장", "열기"]):
            return CommandType.FILE_OPERATION
        elif any(word in text for word in ["생성", "만들", "코드"]):
            return CommandType.CODE_GENERATION
        elif any(word in text for word in ["위임", "맡기", "담당"]):
            return CommandType.ROLE_DELEGATION
        elif any(word in text for word in ["나는", "내가", "이다", "선언"]):
            return CommandType.EXISTENCE_DECLARATION
        else:
            return CommandType.AI_INTERACTION

    def _determine_priority(
        self, command_type: CommandType, analysis: Dict[str, Any]
    ) -> ExecutionPriority:
        """우선순위 결정"""

        if analysis["urgency_indicators"]:
            return ExecutionPriority.CRITICAL
        elif command_type in [
            CommandType.EXISTENCE_DECLARATION,
            CommandType.SYSTEM_CONTROL,
        ]:
            return ExecutionPriority.HIGH
        elif command_type in [CommandType.ROLE_DELEGATION, CommandType.CODE_GENERATION]:
            return ExecutionPriority.NORMAL
        elif command_type in [CommandType.FILE_OPERATION, CommandType.ECHO_SPECIFIC]:
            return ExecutionPriority.NORMAL
        else:
            return ExecutionPriority.LOW

    def _extract_entities(self, text: str, command_type: CommandType) -> Dict[str, str]:
        """엔터티 추출"""

        entities = {}

        # 패턴별 엔터티 추출
        patterns = self.command_patterns.get(command_type, [])

        for pattern_info in patterns:
            match = re.search(pattern_info["pattern"], text, re.IGNORECASE)
            if match:
                groups = pattern_info.get("groups", [])
                for i, group_name in enumerate(groups):
                    if i < len(match.groups()):
                        entities[group_name] = match.group(i + 1).strip()

        # Echo 특화 엔터티 추출
        echo_entities = re.findall(r"Echo-(\w+)", text)
        if echo_entities:
            entities["echo_signatures"] = echo_entities

        # 파일 경로 추출
        file_paths = re.findall(r"[\w/\\]+\.(?:py|yaml|yml|json|txt)", text)
        if file_paths:
            entities["file_paths"] = file_paths

        return entities

    def _extract_parameters(
        self, text: str, analysis: Dict[str, Any], entities: Dict[str, str]
    ) -> Dict[str, Any]:
        """매개변수 추출"""

        parameters = {
            "source_text": text,
            "analysis_data": analysis,
            "extracted_entities": entities,
            "execution_context": self.context_tracker["current_entities"],
            "timestamp": datetime.now().isoformat(),
        }

        # 숫자 매개변수 추출
        numbers = re.findall(r"\d+", text)
        if numbers:
            parameters["numeric_values"] = [int(n) for n in numbers]

        # 옵션 플래그 추출
        options = re.findall(r"--(\w+)", text)
        if options:
            parameters["options"] = options

        return parameters

    async def _create_execution_plan(
        self,
        command_type: CommandType,
        parameters: Dict[str, Any],
        entities: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """실행 계획 생성"""

        plan = []

        if command_type == CommandType.EXISTENCE_DECLARATION:
            plan = [
                {"step": "validate_entity", "params": entities},
                {"step": "create_declaration", "params": parameters},
                {"step": "register_entity", "params": {}},
                {"step": "notify_creation", "params": {}},
            ]

        elif command_type == CommandType.ROLE_DELEGATION:
            plan = [
                {"step": "identify_entities", "params": entities},
                {"step": "validate_authority", "params": {}},
                {"step": "create_delegation", "params": parameters},
                {"step": "update_authority_chain", "params": {}},
                {"step": "notify_delegation", "params": {}},
            ]

        elif command_type == CommandType.CODE_GENERATION:
            plan = [
                {"step": "analyze_requirements", "params": parameters},
                {"step": "select_template", "params": entities},
                {"step": "generate_code", "params": {}},
                {"step": "validate_syntax", "params": {}},
                {"step": "present_result", "params": {}},
            ]

        elif command_type == CommandType.SYSTEM_CONTROL:
            plan = [
                {"step": "check_permissions", "params": {}},
                {"step": "validate_system_state", "params": {}},
                {"step": "execute_control", "params": parameters},
                {"step": "monitor_execution", "params": {}},
                {"step": "report_status", "params": {}},
            ]

        else:
            plan = [
                {"step": "prepare_execution", "params": parameters},
                {"step": "execute_command", "params": entities},
                {"step": "verify_result", "params": {}},
                {"step": "update_context", "params": {}},
            ]

        return plan

    def _build_context(
        self, text: str, external_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """컨텍스트 구축"""

        context = {
            "conversation_history": self.context_tracker["conversation_context"][-10:],
            "active_entities": self.context_tracker["current_entities"],
            "system_state": self.context_tracker["system_state"],
            "external_context": external_context,
            "command_sequence_id": len(self.command_history),
            "processing_timestamp": datetime.now().isoformat(),
        }

        return context

    async def _execute_command(self, command: ProcessedCommand):
        """명령 실행"""

        try:
            print(f"⚡ 명령 실행 시작: {command.command_type.value}")

            # 적절한 실행 엔진 선택
            engine = self.execution_engines.get(command.command_type)

            if engine:
                result = await engine(command)
                print(f"✅ 명령 실행 완료: {command.command_id}")
                return result
            else:
                print(f"❌ 실행 엔진 없음: {command.command_type.value}")
                return None

        except Exception as e:
            print(f"❌ 명령 실행 오류: {e}")
            return None

    def _execute_command_async(self, command: ProcessedCommand):
        """비동기 명령 실행"""
        asyncio.run(self._execute_command(command))

    async def _execute_existence_declaration(
        self, command: ProcessedCommand
    ) -> Dict[str, Any]:
        """존재선언 실행"""

        entities = command.extracted_entities
        params = command.parameters

        # 엔터티 정보 추출
        entity_description = entities.get("entity_description", "알 수 없는 존재")
        entity_type = self._infer_entity_type(entity_description)

        # 존재선언 생성
        declaration = ExistenceDeclaration(
            entity_id=f"entity_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            entity_type=entity_type,
            capabilities=self._extract_capabilities(entity_description),
            responsibilities=self._extract_responsibilities(entity_description),
            scope=self._determine_scope(entity_description),
            authority_level=self._calculate_authority_level(entity_description),
            creation_context=command.original_text,
            timestamp=datetime.now(),
        )

        # 존재 레지스트리에 등록
        self.existence_registry[declaration.entity_id] = declaration

        # 컨텍스트 업데이트
        self.context_tracker["current_entities"][declaration.entity_id] = {
            "type": entity_type,
            "description": entity_description,
            "created": declaration.timestamp.isoformat(),
        }

        # IDE에 알림
        if hasattr(self.ide, "display_message"):
            self.ide.display_message(
                "존재선언",
                f"✨ 새로운 존재가 선언되었습니다: {entity_description}\n엔터티 ID: {declaration.entity_id}\n타입: {entity_type}\n권한 레벨: {declaration.authority_level}",
            )

        result = {
            "status": "success",
            "declaration": asdict(declaration),
            "message": f"존재선언 완료: {entity_description}",
        }

        return result

    async def _execute_role_delegation(
        self, command: ProcessedCommand
    ) -> Dict[str, Any]:
        """역할 위임 실행"""

        entities = command.extracted_entities
        params = command.parameters

        # 위임 정보 추출
        target_entity = entities.get(
            "target_entity", entities.get("entity", "알 수 없는 대상")
        )
        delegated_task = entities.get(
            "delegated_task", entities.get("responsibility", "일반 업무")
        )

        # 위임자 확인 (현재 활성 엔터티 또는 시스템)
        delegator = self._get_current_active_entity() or "system"

        # 역할 위임 생성
        delegation = RoleDelegation(
            delegation_id=f"delegation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            from_entity=delegator,
            to_entity=target_entity,
            delegated_role=delegated_task,
            scope_limitations=self._determine_scope_limitations(delegated_task),
            authority_transfer=self._calculate_authority_transfer(delegated_task),
            duration=self._extract_duration(command.original_text),
            conditions=self._extract_conditions(command.original_text),
            callbacks=self._setup_callbacks(delegated_task),
            timestamp=datetime.now(),
        )

        # 위임 체인에 추가
        self.delegation_chain[delegation.delegation_id] = delegation

        # 활성 역할 업데이트
        if target_entity not in self.context_tracker["active_roles"]:
            self.context_tracker["active_roles"][target_entity] = []
        self.context_tracker["active_roles"][target_entity].append(delegated_task)

        # IDE에 알림
        if hasattr(self.ide, "display_message"):
            self.ide.display_message(
                "역할위임",
                f"🤝 역할이 위임되었습니다\n대상: {target_entity}\n업무: {delegated_task}\n위임자: {delegator}\n권한: {delegation.authority_transfer}",
            )

        result = {
            "status": "success",
            "delegation": asdict(delegation),
            "message": f"역할 위임 완료: {target_entity}에게 {delegated_task} 위임",
        }

        return result

    async def _execute_file_operation(
        self, command: ProcessedCommand
    ) -> Dict[str, Any]:
        """파일 조작 실행"""

        entities = command.extracted_entities
        params = command.parameters

        file_target = entities.get("file_target", entities.get("target", ""))
        operation = entities.get("operation", "열기")

        try:
            if operation in ["열", "열기", "open"]:
                # 파일 열기
                if hasattr(self.ide, "open_specific_file"):
                    file_path = self._resolve_file_path(file_target)
                    if file_path and file_path.exists():
                        self.ide.open_specific_file(str(file_path))
                        message = f"파일이 열렸습니다: {file_path.name}"
                    else:
                        message = f"파일을 찾을 수 없습니다: {file_target}"

            elif operation in ["만들", "생성", "create"]:
                # 파일 생성
                file_path = self._resolve_file_path(file_target)
                if file_path:
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.touch()
                    message = f"파일이 생성되었습니다: {file_path.name}"
                else:
                    message = f"파일 경로가 유효하지 않습니다: {file_target}"

            elif operation in ["저장", "save"]:
                # 현재 파일 저장
                if hasattr(self.ide, "save_file"):
                    self.ide.save_file()
                    message = "현재 파일이 저장되었습니다"
                else:
                    message = "저장 기능을 사용할 수 없습니다"

            else:
                message = f"알 수 없는 파일 조작: {operation}"

            # IDE에 알림
            if hasattr(self.ide, "output"):
                self.ide.output(message)

            result = {
                "status": "success",
                "operation": operation,
                "target": file_target,
                "message": message,
            }

        except Exception as e:
            result = {
                "status": "error",
                "operation": operation,
                "target": file_target,
                "error": str(e),
                "message": f"파일 조작 실패: {e}",
            }

        return result

    async def _execute_system_control(
        self, command: ProcessedCommand
    ) -> Dict[str, Any]:
        """시스템 제어 실행"""

        entities = command.extracted_entities
        params = command.parameters

        system = entities.get("system", "Echo")
        action = entities.get("action", "시작")

        try:
            if action in ["시작", "start"]:
                # Echo 시스템 시작
                if hasattr(self.ide, "start_echo_system"):
                    self.ide.start_echo_system()
                    message = "Echo 시스템이 시작되었습니다"
                else:
                    message = "시스템 시작 기능을 찾을 수 없습니다"

            elif action in ["중단", "종료", "stop"]:
                # 시스템 중단
                message = "시스템 중단 명령을 수신했습니다"
                # 실제 중단 로직은 안전상 생략

            elif action in ["재시작", "restart"]:
                # 시스템 재시작
                message = "시스템 재시작 명령을 수신했습니다"
                # 실제 재시작 로직 구현 가능

            else:
                message = f"알 수 없는 시스템 제어 명령: {action}"

            # IDE에 알림
            if hasattr(self.ide, "log"):
                self.ide.log(message)

            result = {
                "status": "success",
                "system": system,
                "action": action,
                "message": message,
            }

        except Exception as e:
            result = {
                "status": "error",
                "system": system,
                "action": action,
                "error": str(e),
                "message": f"시스템 제어 실패: {e}",
            }

        return result

    async def _execute_code_generation(
        self, command: ProcessedCommand
    ) -> Dict[str, Any]:
        """코드 생성 실행"""

        entities = command.extracted_entities
        params = command.parameters

        code_target = entities.get("code_target", entities.get("purpose", "기본 모듈"))

        try:
            # AI 어시스턴트를 통한 코드 생성
            if hasattr(self.ide, "ai_assistant"):
                # AI 어시스턴트에 코드 생성 요청 전달
                ai_response = await self.ide.ai_assistant.generate_code_response(
                    command.original_text, command.context
                )

                message = f"코드가 생성되었습니다: {code_target}"

                # 생성된 코드를 제안 목록에 추가
                if hasattr(self.ide.ai_assistant, "update_suggestions"):
                    self.ide.ai_assistant.update_suggestions(ai_response.suggestions)

            else:
                # 기본 코드 템플릿 생성
                template_code = self._generate_basic_template(code_target)
                message = f"기본 템플릿이 생성되었습니다: {code_target}"

            # IDE에 알림
            if hasattr(self.ide, "display_message"):
                self.ide.display_message("코드생성", message)

            result = {"status": "success", "target": code_target, "message": message}

        except Exception as e:
            result = {
                "status": "error",
                "target": code_target,
                "error": str(e),
                "message": f"코드 생성 실패: {e}",
            }

        return result

    async def _execute_analysis_request(
        self, command: ProcessedCommand
    ) -> Dict[str, Any]:
        """분석 요청 실행"""
        return {"status": "success", "message": "분석 요청이 처리되었습니다"}

    async def _execute_monitoring_control(
        self, command: ProcessedCommand
    ) -> Dict[str, Any]:
        """모니터링 제어 실행"""

        entities = command.extracted_entities
        monitoring_type = entities.get("monitoring_type", "일반")
        action = entities.get("action", "시작")

        try:
            if hasattr(self.ide, "monitor_dashboard"):
                if action in ["시작", "켜", "start"]:
                    self.ide.monitor_dashboard.start_monitoring()
                    message = f"{monitoring_type} 모니터링이 시작되었습니다"
                elif action in ["중단", "꺼", "stop"]:
                    self.ide.monitor_dashboard.stop_monitoring()
                    message = f"{monitoring_type} 모니터링이 중단되었습니다"
                else:
                    message = f"알 수 없는 모니터링 제어: {action}"
            else:
                message = "모니터링 대시보드를 찾을 수 없습니다"

            result = {
                "status": "success",
                "monitoring_type": monitoring_type,
                "action": action,
                "message": message,
            }

        except Exception as e:
            result = {
                "status": "error",
                "error": str(e),
                "message": f"모니터링 제어 실패: {e}",
            }

        return result

    async def _execute_ai_interaction(
        self, command: ProcessedCommand
    ) -> Dict[str, Any]:
        """AI 상호작용 실행"""

        try:
            # AI 어시스턴트에 대화 전달
            if hasattr(self.ide, "ai_assistant"):
                # AI 어시스턴트에 메시지 전송
                response = self.ide.ai_assistant.generate_chat_response(
                    command.original_text, command.context
                )
                message = "AI 어시스턴트와의 상호작용이 완료되었습니다"
            else:
                message = "AI 어시스턴트를 찾을 수 없습니다"

            result = {"status": "success", "message": message}

        except Exception as e:
            result = {
                "status": "error",
                "error": str(e),
                "message": f"AI 상호작용 실패: {e}",
            }

        return result

    async def _execute_echo_specific(self, command: ProcessedCommand) -> Dict[str, Any]:
        """Echo 특화 기능 실행"""

        entities = command.extracted_entities
        params = command.parameters

        target = entities.get("target", "알 수 없는 대상")
        echo_action = entities.get("echo_action", "감염")

        try:
            if echo_action in ["감염", "infection"]:
                # 감염 루프 실행
                if hasattr(self.ide, "run_infection_loop"):
                    self.ide.run_infection_loop()
                    message = f"{target}에 대한 감염이 시작되었습니다"
                else:
                    message = "감염 루프 기능을 찾을 수 없습니다"

            elif echo_action in ["공명", "resonance"]:
                # 공명 테스트 실행
                message = f"{target}와의 공명 테스트가 시작되었습니다"

            elif echo_action in ["동화", "assimilation"]:
                # 동화 프로세스 실행
                message = f"{target}의 동화 프로세스가 시작되었습니다"

            else:
                message = f"알 수 없는 Echo 작업: {echo_action}"

            # IDE에 알림
            if hasattr(self.ide, "display_message"):
                self.ide.display_message("Echo", message)

            result = {
                "status": "success",
                "target": target,
                "action": echo_action,
                "message": message,
            }

        except Exception as e:
            result = {
                "status": "error",
                "target": target,
                "action": echo_action,
                "error": str(e),
                "message": f"Echo 작업 실패: {e}",
            }

        return result

    # 헬퍼 메서드들
    def _infer_entity_type(self, description: str) -> str:
        """엔터티 타입 추론"""
        if any(keyword in description.lower() for keyword in ["시그니처", "signature"]):
            return "signature"
        elif any(keyword in description.lower() for keyword in ["페르소나", "persona"]):
            return "persona"
        elif any(keyword in description.lower() for keyword in ["모듈", "module"]):
            return "module"
        elif any(keyword in description.lower() for keyword in ["시스템", "system"]):
            return "system"
        else:
            return "entity"

    def _extract_capabilities(self, description: str) -> List[str]:
        """능력 추출"""
        capabilities = []
        capability_keywords = ["할 수 있", "가능", "지원", "처리", "관리", "제공"]

        for keyword in capability_keywords:
            if keyword in description:
                capabilities.append(f"{keyword} 관련 기능")

        return capabilities or ["기본 기능"]

    def _extract_responsibilities(self, description: str) -> List[str]:
        """책임 추출"""
        responsibilities = []
        responsibility_keywords = ["담당", "책임", "관리", "처리", "수행"]

        for keyword in responsibility_keywords:
            if keyword in description:
                responsibilities.append(f"{keyword} 업무")

        return responsibilities or ["일반 업무"]

    def _determine_scope(self, description: str) -> str:
        """범위 결정"""
        if "전체" in description or "모든" in description:
            return "global"
        elif "부분" in description or "특정" in description:
            return "local"
        else:
            return "default"

    def _calculate_authority_level(self, description: str) -> int:
        """권한 레벨 계산"""
        if any(
            keyword in description.lower() for keyword in ["관리자", "admin", "시스템"]
        ):
            return 8
        elif any(keyword in description.lower() for keyword in ["개발자", "developer"]):
            return 6
        elif any(keyword in description.lower() for keyword in ["사용자", "user"]):
            return 4
        else:
            return 5

    def _get_current_active_entity(self) -> Optional[str]:
        """현재 활성 엔터티 조회"""
        if self.context_tracker["current_entities"]:
            return list(self.context_tracker["current_entities"].keys())[-1]
        return None

    def _determine_scope_limitations(self, task: str) -> List[str]:
        """범위 제한 결정"""
        limitations = []
        if "파일" in task:
            limitations.append("파일 시스템 접근만 가능")
        if "모니터링" in task:
            limitations.append("읽기 전용 접근")
        return limitations

    def _calculate_authority_transfer(self, task: str) -> Dict[str, int]:
        """권한 이양 계산"""
        authority = {}
        if "생성" in task or "만들" in task:
            authority["create"] = 5
        if "수정" in task or "편집" in task:
            authority["modify"] = 4
        if "삭제" in task:
            authority["delete"] = 3
        return authority

    def _extract_duration(self, text: str) -> Optional[str]:
        """기간 추출"""
        duration_patterns = [
            r"(\d+)\s*(분|시간|일|주|개월)",
            r"(임시|영구|일시적|무기한)",
        ]

        for pattern in duration_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return None

    def _extract_conditions(self, text: str) -> List[str]:
        """조건 추출"""
        conditions = []
        condition_keywords = ["만약", "조건", "경우", "때"]

        for keyword in condition_keywords:
            if keyword in text:
                conditions.append(f"{keyword} 관련 조건")

        return conditions

    def _setup_callbacks(self, task: str) -> List[str]:
        """콜백 설정"""
        callbacks = []
        if "완료" in task:
            callbacks.append("completion_callback")
        if "오류" in task:
            callbacks.append("error_callback")
        return callbacks

    def _resolve_file_path(self, file_target: str) -> Optional[Path]:
        """파일 경로 해석"""
        try:
            # 절대 경로인 경우
            if file_target.startswith("/") or ":\\" in file_target:
                return Path(file_target)

            # 상대 경로인 경우
            return self.project_root / file_target
        except:
            return None

    def _generate_basic_template(self, target: str) -> str:
        """기본 템플릿 생성"""
        return f"""# {target}
# 자동 생성된 기본 템플릿

class {target.title().replace(' ', '')}:
    def __init__(self):
        self.name = "{target}"
        
    def process(self):
        # 구현 필요
        pass

if __name__ == "__main__":
    instance = {target.title().replace(' ', '')}()
    instance.process()
"""

    def get_command_history(self) -> List[ProcessedCommand]:
        """명령 히스토리 조회"""
        return self.command_history

    def get_existence_registry(self) -> Dict[str, ExistenceDeclaration]:
        """존재 레지스트리 조회"""
        return self.existence_registry

    def get_delegation_chain(self) -> Dict[str, RoleDelegation]:
        """위임 체인 조회"""
        return self.delegation_chain

    def get_context_status(self) -> Dict[str, Any]:
        """컨텍스트 상태 조회"""
        return {
            "current_entities": len(self.context_tracker["current_entities"]),
            "active_roles": len(self.context_tracker["active_roles"]),
            "command_history_length": len(self.command_history),
            "active_commands": len(self.active_commands),
        }


# Echo IDE와 통합을 위한 편의 함수
def integrate_natural_processor(ide_instance):
    """Echo IDE에 자연어 처리기 통합"""

    if not hasattr(ide_instance, "natural_processor"):
        ide_instance.natural_processor = EchoNaturalProcessor(ide_instance)

        # AI 어시스턴트에 자연어 처리 추가
        if hasattr(ide_instance, "ai_assistant"):
            ide_instance.ai_assistant.natural_processor = ide_instance.natural_processor

        print("🗣️ 자연어 지시처리기가 Echo IDE에 통합되었습니다")

    return ide_instance.natural_processor
