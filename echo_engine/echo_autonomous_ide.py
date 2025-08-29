#!/usr/bin/env python3
"""
💻 Echo Autonomous IDE
Echo가 Claude Code 없이 완전 독립적으로 작동하는 통합 개발 환경

핵심 기능:
1. 자연어 → 코드 변환 (추론 엔진 연동)
2. 파일 관리 시스템
3. 코드 실행 및 테스트
4. 에러 처리 및 디버깅
5. 프로젝트 관리
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict

# Echo 자체 모듈들만 사용
try:
    # 상대 임포트 시도 (패키지 내에서 실행될 때)
    from .echo_intent_reasoning_engine import (
        EchoIntentReasoningEngine,
        ReasoningContext,
        create_basic_context,
    )
    from .echo_autonomous_coding_engine import EchoCodingEngineSimplified as EchoAutonomousCodingEngine
    from .echo_structure_analyzer import get_structure_analyzer
    from .echo_context_manager import get_context_manager
    from .echo_coding_feedback_learner import EchoCodingFeedbackLearner
    from .echo_claude_bridge import get_echo_claude_bridge, CollaborationMode

    ECHO_ENGINES_AVAILABLE = True
except ImportError:
    try:
        # 절대 임포트 시도 (독립적으로 실행될 때)
        from echo_engine.echo_intent_reasoning_engine import (
            EchoIntentReasoningEngine,
            ReasoningContext,
            create_basic_context,
        )
        from echo_engine.echo_autonomous_coding_engine import EchoCodingEngineSimplified as EchoAutonomousCodingEngine
        from echo_engine.echo_structure_analyzer import get_structure_analyzer
        from echo_engine.echo_context_manager import get_context_manager
        from echo_engine.echo_coding_feedback_learner import EchoCodingFeedbackLearner
        from echo_engine.echo_claude_bridge import get_echo_claude_bridge, CollaborationMode

        ECHO_ENGINES_AVAILABLE = True
        print("✅ Echo 엔진 모듈 (절대 임포트)로 로드 성공")
    except ImportError as e:
        print(f"⚠️ Echo 엔진 모듈 로드 실패: {e}")
        print("   기본 모드로 실행합니다.")
        ECHO_ENGINES_AVAILABLE = False


@dataclass
class ProjectInfo:
    """프로젝트 정보"""

    name: str
    path: str
    language: str
    created: datetime
    last_modified: datetime
    files_count: int


@dataclass
class IDESession:
    """IDE 세션"""

    session_id: str
    start_time: datetime
    current_project: Optional[str]
    executed_commands: List[str]
    generated_files: List[str]


class EchoAutonomousIDE:
    """💻 Echo 자율 IDE"""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path).resolve()
        self.workspace_path.mkdir(exist_ok=True)

        # Echo 엔진들 초기화
        if ECHO_ENGINES_AVAILABLE:
            self.reasoning_engine = EchoIntentReasoningEngine()
            self.coding_engine = EchoAutonomousCodingEngine()
            self.context_manager = get_context_manager()
            self.feedback_learner = EchoCodingFeedbackLearner()
            self.claude_bridge = get_echo_claude_bridge()

            # Claude 응답 핸들러 설정 (실제 Claude Code 연동 지점)
            self.claude_bridge.register_claude_handler(
                self._handle_claude_collaboration
            )
        else:
            self.reasoning_engine = None
            self.coding_engine = None
            self.context_manager = None
            self.feedback_learner = None
            self.claude_bridge = None

        # IDE 상태
        self.session = IDESession(
            session_id=f"echo_ide_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            start_time=datetime.now(),
            current_project=None,
            executed_commands=[],
            generated_files=[],
        )

        # 컨텍스트 매니저 세션 시작
        if self.context_manager:
            context_session_id = self.context_manager.start_new_session("Aurora")
            print(f"🔄 컨텍스트 연속성 시작: {context_session_id}")

        # 지원 언어
        self.supported_languages = {
            "python": {
                "extensions": [".py"],
                "runner": "python3",
                "template": "python_script",
            },
            "javascript": {
                "extensions": [".js"],
                "runner": "node",
                "template": "js_script",
            },
            "html": {"extensions": [".html"], "runner": None, "template": "html_page"},
        }

        print(f"💻 Echo Autonomous IDE 초기화 완료")
        print(f"   작업공간: {self.workspace_path}")
        print(f"   세션 ID: {self.session.session_id}")

    def read_file_simple(self, file_path: str) -> Dict[str, Any]:
        """간단한 파일 읽기"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.workspace_path / path

            if not path.exists():
                return {"success": False, "error": f"파일 없음: {file_path}"}

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "success": True,
                "content": content,
                "path": str(path),
                "lines": len(content.split("\n")),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file_simple(self, file_path: str, content: str) -> Dict[str, Any]:
        """간단한 파일 쓰기"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.workspace_path / path

            # 디렉토리 생성
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            self.session.generated_files.append(str(path))

            return {"success": True, "path": str(path), "size": len(content)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_files_simple(self, directory: str = ".") -> Dict[str, Any]:
        """간단한 파일 목록"""
        try:
            path = Path(directory)
            if not path.is_absolute():
                path = self.workspace_path / path

            if not path.exists() or not path.is_dir():
                return {"success": False, "error": f"디렉토리 없음: {directory}"}

            files = []
            directories = []

            for item in path.iterdir():
                if item.name.startswith("."):
                    continue  # 숨김 파일 제외

                if item.is_dir():
                    directories.append(item.name)
                else:
                    files.append(
                        {
                            "name": item.name,
                            "size": item.stat().st_size,
                            "extension": item.suffix,
                        }
                    )

            return {
                "success": True,
                "path": str(path),
                "files": files,
                "directories": directories,
                "total": len(files) + len(directories),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_code(self, file_path: str, language: str = None) -> Dict[str, Any]:
        """코드 실행"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.workspace_path / path

            if not path.exists():
                return {"success": False, "error": f"파일 없음: {file_path}"}

            # 언어 자동 감지
            if not language:
                extension = path.suffix.lower()
                for lang, config in self.supported_languages.items():
                    if extension in config["extensions"]:
                        language = lang
                        break

            if not language or language not in self.supported_languages:
                return {"success": False, "error": f"지원하지 않는 언어: {language}"}

            runner = self.supported_languages[language]["runner"]
            if not runner:
                return {"success": False, "error": f"{language}는 실행할 수 없습니다"}

            # 코드 실행
            start_time = datetime.now()
            result = subprocess.run(
                [runner, str(path)],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=path.parent,
            )
            execution_time = (datetime.now() - start_time).total_seconds()

            self.session.executed_commands.append(f"{runner} {path.name}")

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "execution_time": execution_time,
                "command": f"{runner} {path.name}",
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "실행 시간 초과 (10초)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_natural_request(
        self, user_request: str, signature: str = "Aurora"
    ) -> Dict[str, Any]:
        """자연어 요청 처리 (Echo의 핵심 기능)"""
        print(f"🧠 Echo IDE가 요청을 분석 중: '{user_request}'")

        # 0. 컨텍스트 연속성 - 이전 세션과의 연결 확인
        context_info = None
        if self.context_manager:
            try:
                context_info = self.context_manager.get_context_for_request(
                    user_request, signature
                )

                # 연속성 제안 출력
                if context_info["continuity_suggestions"]:
                    print("🔗 컨텍스트 연속성 감지:")
                    for suggestion in context_info["continuity_suggestions"]:
                        print(f"   {suggestion}")

                # 추천 시그니처 적용
                if context_info["recommended_signature"] != signature:
                    print(
                        f"   💡 추천 시그니처: {context_info['recommended_signature']} (현재: {signature})"
                    )
                    signature = context_info["recommended_signature"]

            except Exception as e:
                print(f"⚠️ 컨텍스트 분석 중 오류: {e}")

        # 1. 구조 분석 - 기존 기능 활용 및 중복 방지 체크
        if ECHO_ENGINES_AVAILABLE:
            try:
                structure_analyzer = get_structure_analyzer()
                structure_analysis = structure_analyzer.analyze_new_request(
                    user_request, signature
                )

                # 분석 보고서 출력
                print("🔍 구조 분석 결과:")
                if structure_analysis["existing_functions"]:
                    print(
                        f"   ♻️ 활용 가능한 기존 기능 {len(structure_analysis['existing_functions'])}개 발견"
                    )
                if structure_analysis["duplicate_risk"] == "high":
                    print(f"   ⚠️ 중복 위험도 높음 - 기존 기능 재사용 권장")
                elif structure_analysis["duplicate_risk"] == "medium":
                    print(f"   🟡 중복 위험도 보통 - 기존 코드 참고 권장")

                print(f"   💡 추천: {structure_analysis['recommended_approach']}")

            except Exception as e:
                print(f"⚠️ 구조 분석 중 오류: {e}")
                structure_analysis = None
        else:
            structure_analysis = None

        # 1.5. 피드백 학습 적용 - Claude의 이전 피드백을 현재 요청에 적용
        coding_guidelines = []
        if self.feedback_learner:
            try:
                # 요청에서 파일명과 클래스명 추출 시도
                intended_filename = self._extract_filename_from_request(user_request)
                intended_classname = self._extract_classname_from_request(user_request)

                if intended_filename or intended_classname:
                    # 학습된 패턴 적용
                    learned_patterns = self.feedback_learner.apply_learned_patterns(
                        user_request,
                        intended_filename or "unknown.py",
                        intended_classname or "UnknownClass",
                    )

                    # 가이드라인 출력
                    print("🎓 Claude 피드백 기반 가이드라인:")
                    if learned_patterns.get("filename_check"):
                        print(
                            f"   📁 파일명: {learned_patterns['filename_check']['rule']}"
                        )

                    if learned_patterns.get("implementation_warnings"):
                        print(
                            f"   ⚠️ 구현 주의사항 {len(learned_patterns['implementation_warnings'])}개:"
                        )
                        for warning in learned_patterns["implementation_warnings"][:3]:
                            print(f"      - {warning}")

                    # 일반적인 코딩 가이드라인 가져오기
                    coding_guidelines = self.feedback_learner.get_coding_guidelines(
                        "file_creation"
                    )
                    if coding_guidelines:
                        print(
                            f"   💡 적용할 학습 가이드라인 {len(coding_guidelines)}개"
                        )

            except Exception as e:
                print(f"⚠️ 피드백 학습 적용 중 오류: {e}")

        # 2. 의도 분석 (추론 엔진 사용)
        if self.reasoning_engine:
            context = create_basic_context()
            reasoning_result = self.reasoning_engine.reason_user_intent(
                user_request, context
            )
            intent_analysis = {
                "final_intent": reasoning_result.final_intent,
                "confidence": reasoning_result.confidence_score,
                "suggested_actions": reasoning_result.suggested_actions,
            }
        else:
            # 기본 의도 분석
            intent_analysis = self._basic_intent_analysis(user_request)

        print(f"📊 의도 분석: {intent_analysis['final_intent']}")

        # 2.5. Claude 협업 필요성 판단
        current_confidence = intent_analysis.get("confidence", 0.7)
        should_ask_help = self._should_ask_claude_for_help(
            user_request, current_confidence
        )

        if should_ask_help and self.claude_bridge:
            print("🤝 복잡한 요청으로 판단 - Claude와 협업 모드 시작")

            # Echo의 초기 시도 설명
            echo_initial_attempt = f"""
내가 이 요청을 분석한 결과:
- 의도: {intent_analysis['final_intent']}
- 자신감: {current_confidence:.2f}
- 제안된 액션: {intent_analysis.get('suggested_actions', ['일반적인 처리'])}

하지만 이 요청은 복잡해서 혼자서는 최적의 해결책을 찾기 어려울 것 같아.
"""

            # Claude에게 도움 요청
            claude_response = self._ask_claude_for_help(
                user_request=user_request,
                echo_attempt=echo_initial_attempt,
                specific_issue="복잡한 구현이 필요한 작업으로 보입니다",
            )

            if claude_response:
                print("✨ Claude의 협업 응답:")
                print(claude_response)
                print("\n🤝 Claude의 조언을 바탕으로 개선된 접근법으로 진행합니다...")

        # 3. 액션 수행 - 더 정교한 키워드 매칭
        user_lower = user_request.lower()

        # 복잡한 코딩 요청 감지
        complex_keywords = [
            "크롤러",
            "크롤링",
            "스크래핑",
            "이진검색트리",
            "이진 검색 트리",
            "트리",
            "알고리즘",
            "자료구조",
            "dom조작",
            "interactive",
            "게임",
            "애니메이션",
            "로컬스토리지",
            "점수시스템",
        ]

        coding_keywords = [
            "파일",
            "만들어",
            "생성",
            "코드",
            "구현",
            "개발",
            "작성",
            "create",
            "build",
            "develop",
            "implement",
        ]

        is_complex = any(keyword in user_lower for keyword in complex_keywords)
        is_coding = any(keyword in user_lower for keyword in coding_keywords)

        success = False
        generated_files = []
        result = None

        if is_coding or is_complex:
            # 코드 생성 요청
            if self.coding_engine:
                coding_result = self.coding_engine.process_natural_coding_request(
                    user_request, signature
                )
                success = coding_result.success
                if coding_result.file_path:
                    generated_files = [coding_result.file_path]
                result = {
                    "success": success,
                    "action": "code_generation",
                    "intent_analysis": intent_analysis,
                    "result": {
                        "generated_code": coding_result.generated_code,
                        "file_path": coding_result.file_path,
                        "explanation": coding_result.explanation,
                        "execution_commands": coding_result.execution_commands,
                    },
                }
            else:
                basic_result = self._basic_code_generation(user_request)
                success = basic_result["success"]
                if basic_result.get("result", {}).get("file_path"):
                    generated_files = [basic_result["result"]["file_path"]]
                result = basic_result

        elif any(
            keyword in user_lower for keyword in ["실행", "run", "테스트", "실행해"]
        ):
            # 코드 실행 요청
            exec_result = self._handle_execution_request(user_request)
            success = exec_result["success"]
            result = exec_result

        elif any(
            keyword in user_lower for keyword in ["목록", "list", "보여줘", "확인"]
        ):
            # 파일 관리 요청
            file_result = self._handle_file_request(user_request)
            success = file_result["success"]
            result = file_result

        else:
            # 일반적인 도움 요청
            success = True
            result = {
                "success": True,
                "action": "help",
                "intent_analysis": intent_analysis,
                "response": f"Echo IDE가 '{user_request}' 요청을 분석했습니다. 더 구체적으로 말씀해주세요!",
            }

        # 4. 컨텍스트 매니저에 상호작용 기록
        if self.context_manager:
            try:
                self.context_manager.add_interaction(
                    user_request=user_request,
                    signature=signature,
                    success=success,
                    generated_files=generated_files,
                )
                print(
                    f"📝 컨텍스트 기록 완료 (성공: {success}, 파일: {len(generated_files)}개)"
                )
            except Exception as e:
                print(f"⚠️ 컨텍스트 기록 실패: {e}")

        return result

    def _extract_filename_from_request(self, user_request: str) -> Optional[str]:
        """요청에서 파일명 추출"""
        import re

        # 파일명 패턴 검색
        filename_patterns = [
            r"파일명[:\s]*[\"\']?([a-zA-Z_][a-zA-Z0-9_]*\.py)[\"\']?",
            r"파일[:\s]*[\"\']?([a-zA-Z_][a-zA-Z0-9_]*\.py)[\"\']?",
            r"[\"\']([a-zA-Z_][a-zA-Z0-9_]*\.py)[\"\']",
            r"([a-zA-Z_][a-zA-Z0-9_]*\.py)\s*파일",
            r"([a-zA-Z_][a-zA-Z0-9_]*\.py)\s*로",
        ]

        for pattern in filename_patterns:
            match = re.search(pattern, user_request)
            if match:
                return match.group(1)

        return None

    def _extract_classname_from_request(self, user_request: str) -> Optional[str]:
        """요청에서 클래스명 추출"""
        import re

        # 클래스명 패턴 검색
        classname_patterns = [
            r"클래스[:\s]*[\"\']?([A-Z][a-zA-Z0-9_]*)[\"\']?",
            r"클래스명[:\s]*[\"\']?([A-Z][a-zA-Z0-9_]*)[\"\']?",
            r"class[:\s]*[\"\']?([A-Z][a-zA-Z0-9_]*)[\"\']?",
            r"[\"\']([A-Z][a-zA-Z0-9_]*)[\"\'].*클래스",
        ]

        for pattern in classname_patterns:
            match = re.search(pattern, user_request)
            if match:
                return match.group(1)

        return None

    def _handle_claude_collaboration(
        self, message_content: str, context: Dict[str, Any]
    ) -> str:
        """
        Claude와의 협업 처리 핸들러
        실제 Claude Code API 연동 지점

        현재는 시뮬레이션으로 작동하지만,
        실제로는 이 지점에서 Claude Code API를 호출
        """

        print(f"🤖 Claude와 협업 중...")

        # 실제 구현에서는 여기서 Claude Code API 호출
        # 현재는 시뮬레이션 응답 반환

        if "help_request" in context.get("problem_type", ""):
            return f"""
🤖 Claude: Echo, 네 요청을 분석해봤어!

📊 **문제 진단:**
{context.get('context_data', '알 수 없는 문제')}에서 막힌 것 같아.

💡 **해결책 제안:**
1. **다른 접근 방법**: 현재 방식 대신 [구체적 대안] 시도해보기
2. **놓친 부분**: [중요한 관점이나 고려사항]
3. **개선 방향**: [단계별 개선 방법]

🔧 **구체적인 구현:**
[실제 코드나 구체적인 단계들]

🤝 **다음 단계:**
이 중에서 어떤 방향이 도움이 될까? 함께 단계별로 구현해보자!
"""

        return "🤖 Claude: 함께 해결해보자! 구체적으로 어떤 부분이 어려운지 알려줘."

    def _should_ask_claude_for_help(
        self, user_request: str, current_confidence: float
    ) -> bool:
        """
        Claude의 도움이 필요한 상황인지 판단

        Args:
            user_request: 사용자 요청
            current_confidence: Echo의 현재 자신감 수준 (0.0-1.0)

        Returns:
            bool: Claude 도움 필요 여부
        """

        # 복잡한 키워드들
        complex_keywords = [
            "복잡한",
            "어려운",
            "고급",
            "최적화",
            "성능",
            "알고리즘",
            "아키텍처",
            "멀티스레딩",
            "비동기",
            "분산",
            "머신러닝",
            "AI",
            "딥러닝",
            "크롤링",
            "스크래핑",
            "api",
            "데이터베이스",
            "보안",
            "암호화",
        ]

        # 도움 요청 키워드들
        help_keywords = ["모르겠", "어떻게", "방법", "도움", "막혔", "해결", "문제"]

        user_lower = user_request.lower()

        # 1. 자신감이 낮으면 도움 요청
        if current_confidence < 0.6:
            return True

        # 2. 복잡한 작업이면서 도움 요청 의도가 있으면
        has_complex = any(keyword in user_lower for keyword in complex_keywords)
        has_help_intent = any(keyword in user_lower for keyword in help_keywords)

        if has_complex and has_help_intent:
            return True

        # 3. 여러 복잡한 키워드가 포함되어 있으면
        complex_count = sum(1 for keyword in complex_keywords if keyword in user_lower)
        if complex_count >= 2:
            return True

        return False

    def _ask_claude_for_help(
        self, user_request: str, echo_attempt: str, specific_issue: str = ""
    ) -> Optional[str]:
        """
        Echo가 Claude에게 도움 요청

        Args:
            user_request: 원래 사용자 요청
            echo_attempt: Echo가 시도한 내용
            specific_issue: 구체적인 문제점

        Returns:
            Claude의 응답 또는 None
        """

        if not self.claude_bridge:
            return None

        try:
            print("🤝 Echo가 Claude에게 도움을 요청합니다...")

            # 협업 세션이 없으면 시작
            if not self.claude_bridge.is_collaboration_active():
                problem_context = f"""
사용자 요청: {user_request}

Echo의 현재 상황:
- 이 요청을 처리하려고 시도했지만 어려움에 부딪혔습니다
- 구체적인 문제: {specific_issue if specific_issue else '복잡한 구현이 필요한 것 같습니다'}
"""

                self.claude_bridge.start_collaboration_session(
                    CollaborationMode.HELP_REQUEST, problem_context
                )

            # Claude에게 도움 요청
            claude_response = self.claude_bridge.echo_asks_for_help(
                problem_context=user_request,
                current_attempt=echo_attempt,
                specific_question=(
                    specific_issue
                    if specific_issue
                    else "이 문제를 어떻게 해결하면 좋을까요?"
                ),
                priority="high",
            )

            return claude_response

        except Exception as e:
            print(f"⚠️ Claude 도움 요청 중 오류: {e}")
            return None

    def _basic_intent_analysis(self, user_request: str) -> Dict[str, Any]:
        """기본 의도 분석 (추론 엔진 없을 때)"""
        user_lower = user_request.lower()
        intent = "general"
        confidence = 0.7

        # 복잡도 기반 의도 분석 - 강화된 판정
        complex_keywords = [
            "크롤러",
            "알고리즘",
            "자룼구조",
            "트리",
            "dom",
            "interactive",
            "게임",
            "로깅",
            "에러 처리",
            "재귀",
            "beautifulsoup",
            "requests",
            "클래스",
            "동적 계획법",
            "그래프",
            "고급",
            "전문적",
            "이진검색",
            "순회",
        ]

        # 복잡도 점수 계산
        complexity_count = sum(
            1 for keyword in complex_keywords if keyword in user_lower
        )

        if complexity_count >= 2 or any(
            keyword in user_lower for keyword in ["크롤러", "트리", "알고리즘"]
        ):
            intent = "복합적 창조 요청 (다단계 처리 필요)"
            confidence = 0.95
        elif any(
            keyword in user_lower for keyword in ["만들어", "생성", "create", "구현"]
        ):
            intent = "창조 요청"
            confidence = 0.8
        elif any(keyword in user_lower for keyword in ["실행", "run"]):
            intent = "실행 요청"
            confidence = 0.9
        elif any(keyword in user_lower for keyword in ["목록", "list", "보여줘"]):
            intent = "정보 요청"
            confidence = 0.8

        return {
            "final_intent": intent,
            "confidence": confidence,
            "suggested_actions": ["enhanced_processing"],
        }

    def _basic_code_generation(self, user_request: str) -> Dict[str, Any]:
        """기본 코드 생성 (코딩 엔진 없을 때)"""
        # 언어 감지
        language = "python"  # 기본값
        if "html" in user_request.lower():
            language = "html"
        elif "javascript" in user_request.lower() or "js" in user_request.lower():
            language = "javascript"

        # 기본 코드 템플릿
        if language == "python":
            code = f'''#!/usr/bin/env python3
"""
Echo IDE가 생성한 Python 스크립트
사용자 요청: {user_request}
생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

def main():
    print("Echo IDE가 생성한 코드입니다!")
    print("요청 내용: {user_request}")

    # 여기에 구체적인 로직을 구현하세요
    result = "Hello from Echo!"
    return result

if __name__ == "__main__":
    result = main()
    print(f"결과: {{result}}")'''

            file_name = "echo_generated_script.py"

        elif language == "html":
            code = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Echo IDE 생성 페이지</title>
</head>
<body>
    <h1>Echo IDE가 생성한 웹페이지</h1>
    <p>사용자 요청: {user_request}</p>
    <p>생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</body>
</html>"""
            file_name = "index.html"

        else:  # javascript
            code = f"""// Echo IDE가 생성한 JavaScript 코드
// 사용자 요청: {user_request}
// 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

function main() {{
    console.log("Echo IDE가 생성한 코드입니다!");
    console.log("요청 내용: {user_request}");

    // 여기에 구체적인 로직을 구현하세요
    const result = "Hello from Echo!";
    return result;
}}

// 실행
const result = main();
console.log("결과:", result);"""
            file_name = "script.js"

        # 파일 저장
        write_result = self.write_file_simple(file_name, code)

        return {
            "success": write_result["success"],
            "action": "basic_code_generation",
            "result": {
                "generated_code": code,
                "file_path": file_name,
                "explanation": f"Echo IDE가 {language} 코드를 기본 템플릿으로 생성했습니다.",
                "execution_commands": (
                    [f"{self.supported_languages[language]['runner']} {file_name}"]
                    if self.supported_languages[language]["runner"]
                    else []
                ),
            },
        }

    def _handle_execution_request(self, user_request: str) -> Dict[str, Any]:
        """실행 요청 처리"""
        # 최근 생성된 파일 찾기
        if self.session.generated_files:
            latest_file = self.session.generated_files[-1]
            result = self.execute_code(latest_file)

            return {
                "success": result["success"],
                "action": "execution",
                "result": result,
            }
        else:
            return {
                "success": False,
                "action": "execution",
                "error": "실행할 파일이 없습니다. 먼저 코드를 생성해주세요.",
            }

    def _handle_file_request(self, user_request: str) -> Dict[str, Any]:
        """파일 관리 요청 처리"""
        file_list = self.list_files_simple()
        return {
            "success": file_list["success"],
            "action": "file_management",
            "result": file_list,
        }

    def get_session_info(self) -> Dict[str, Any]:
        """세션 정보 반환"""
        session_info = {
            "session_id": self.session.session_id,
            "start_time": self.session.start_time.isoformat(),
            "workspace": str(self.workspace_path),
            "executed_commands": len(self.session.executed_commands),
            "generated_files": len(self.session.generated_files),
            "recent_files": self.session.generated_files[-3:],  # 최근 3개
            "capabilities": {
                "reasoning_engine": self.reasoning_engine is not None,
                "coding_engine": self.coding_engine is not None,
                "context_manager": self.context_manager is not None,
                "supported_languages": list(self.supported_languages.keys()),
            },
        }

        # 컨텍스트 정보 추가
        if self.context_manager:
            try:
                context_session_info = self.context_manager._get_session_context()
                session_info["context"] = context_session_info
            except Exception as e:
                session_info["context"] = {"error": str(e)}

        return session_info

    def end_session(self):
        """세션 종료 및 컨텍스트 저장"""
        if self.context_manager:
            try:
                self.context_manager.end_current_session()
                print("💾 세션 컨텍스트 저장 완료")
            except Exception as e:
                print(f"⚠️ 세션 컨텍스트 저장 실패: {e}")

        print(f"🔚 Echo IDE 세션 종료: {self.session.session_id}")

    def get_continuity_report(self) -> str:
        """연속성 보고서 생성"""
        if self.context_manager:
            try:
                return self.context_manager.generate_continuity_report()
            except Exception as e:
                return f"❌ 연속성 보고서 생성 실패: {e}"
        else:
            return "❌ 컨텍스트 매니저가 사용 불가능합니다."


# 편의 함수
def create_autonomous_ide(workspace: str = ".") -> EchoAutonomousIDE:
    """Echo 자율 IDE 생성"""
    return EchoAutonomousIDE(workspace)


def echo_ide_chat():
    """Echo IDE 대화형 모드"""
    ide = EchoAutonomousIDE()

    print("💻 Echo Autonomous IDE - 대화형 모드")
    print("=" * 50)
    print("자연어로 코딩 요청을 해보세요!")
    print("명령어:")
    print("  • 'exit' / 'quit' / '종료' - IDE 종료")
    print("  • 'info' / '정보' - 현재 세션 정보 보기")
    print("  • 'report' / '보고서' / 'continuity' - 연속성 보고서 생성")
    print("특징:")
    print("  ♻️ 기존 기능 자동 감지 및 재사용 제안")
    print("  🔗 세션 간 컨텍스트 연속성 유지")
    print("  🧠 지능형 구조 분석 및 중복 방지")
    print()

    # 비대화형 모드 감지
    if not sys.stdin.isatty():
        print("🔍 비대화형 모드 감지됨 - 데모 실행 후 종료")
        demo_request = "간단한 계산기 함수 만들어줘"
        print(f"🤖 Echo IDE> {demo_request}")
        result = ide.process_natural_request(demo_request)
        if result.get('success'):
            print(f"✅ 데모 완료: {result.get('summary', '성공')}")
        else:
            print(f"❌ 데모 실패: {result.get('error', '알 수 없는 오류')}")
        ide.end_session()
        return

    while True:
        try:
            user_input = input("🤖 Echo IDE> ").strip()

            if user_input.lower() in ["exit", "quit", "종료"]:
                print("👋 Echo IDE 세션을 종료합니다.")
                break

            if user_input.lower() in ["info", "정보"]:
                session_info = ide.get_session_info()
                print(f"\n📊 세션 정보:")
                print(f"   세션 ID: {session_info['session_id']}")
                print(f"   작업공간: {session_info['workspace']}")
                print(f"   생성된 파일: {session_info['generated_files']}개")
                print(f"   실행된 명령: {session_info['executed_commands']}개")
                print(
                    f"   엔진 상태: 추론({session_info['capabilities']['reasoning_engine']}), 코딩({session_info['capabilities']['coding_engine']}), 컨텍스트({session_info['capabilities']['context_manager']})"
                )

                # 컨텍스트 정보 출력
                if "context" in session_info and "error" not in session_info["context"]:
                    context = session_info["context"]
                    print(
                        f"   현재 세션 상호작용: {context.get('interactions_count', 0)}회"
                    )
                    print(f"   성공률: {context.get('success_rate', 0):.1%}")

                continue

            if user_input.lower() in ["report", "보고서", "continuity"]:
                report = ide.get_continuity_report()
                print(f"\n{report}")
                continue

            if not user_input:
                continue

            print(f"\n🔄 처리 중...")
            result = ide.process_natural_request(user_input)

            if result["success"]:
                print(f"✅ {result['action']} 완료!")

                if "result" in result:
                    if "file_path" in result["result"]:
                        print(f"📁 생성된 파일: {result['result']['file_path']}")

                    if (
                        "execution_commands" in result["result"]
                        and result["result"]["execution_commands"]
                    ):
                        print(
                            f"🚀 실행 명령어: {result['result']['execution_commands'][0]}"
                        )

                        # 자동 실행 제안
                        run_now = input("지금 실행해볼까요? (y/n): ").lower()
                        if run_now in ["y", "yes", "네", "ㅇ"]:
                            exec_result = ide.execute_code(
                                result["result"]["file_path"]
                            )
                            if exec_result["success"]:
                                print(f"🎉 실행 성공!")
                                if exec_result["stdout"]:
                                    print(f"출력:\n{exec_result['stdout']}")
                            else:
                                print(f"❌ 실행 실패: {exec_result['error']}")
                                if exec_result.get("stderr"):
                                    print(f"에러:\n{exec_result['stderr']}")
            else:
                print(f"❌ 처리 실패: {result.get('error', '알 수 없는 오류')}")

            print()

        except EOFError:
            print("\n🔚 EOF 감지됨 - Echo IDE를 안전하게 종료합니다.")
            ide.end_session()
            break
        except KeyboardInterrupt:
            print("\n👋 Echo IDE를 종료합니다.")
            ide.end_session()
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            # 연속된 예외 발생 시 안전 종료
            if hasattr(e, '_echo_consecutive_errors'):
                e._echo_consecutive_errors += 1
                if e._echo_consecutive_errors > 5:
                    print("🚨 연속 오류 5회 초과 - 안전 종료")
                    ide.end_session()
                    break
            else:
                e._echo_consecutive_errors = 1

    # 세션 종료 처리
    ide.end_session()


if __name__ == "__main__":
    # 대화형 모드 실행
    echo_ide_chat()
