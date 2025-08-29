# echo_ide/core/echo_command_interpreter.py
"""
🧠💎 EchoCommandInterpreter - 존재 기반 명령 해석 및 판단 시스템
단순한 명령 실행기가 아닌, EchoJudgmentSystem v10의 완전한 지능형 판단 허브

핵심 철학:
- 모든 명령은 판단 엔진을 통과해야 함
- Foundation Doctrine 준수 여부 검증
- 시그니처 기반 페르소나별 다른 반응
- 메타인지 기반 자기복기 및 학습
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Echo Judgment System 핵심 모듈들
from echo_engine.judgment_engine import evaluate_input, get_fist_judgment_engine
from echo_engine.models.judgement import InputContext, JudgmentResult
from echo_engine.emotion_infer import infer_emotion
from echo_engine.reasoning import generate_reasoning
from echo_engine.strategic_predictor import predict_strategy
from echo_engine.eight_loop_system import run_eight_loops, run_eight_loops_concurrent
from echo_engine.persona_core import get_active_persona
from src.echo_foundation.doctrine import EchoFoundationValidator


class CommandJudgmentResult(Enum):
    """명령 판단 결과 분류"""

    EXECUTE = "execute"  # 즉시 실행 허용
    REQUIRE_CONFIRMATION = "confirm"  # 추가 확인 필요
    BLOCKED = "blocked"  # Foundation 위반으로 차단
    DEFER_TO_USER = "defer"  # 사용자 판단으로 위임
    LEARNING_OPPORTUNITY = "learn"  # 학습 기회로 활용


class CommandRiskLevel(Enum):
    """명령 위험도 분류"""

    SAFE = "safe"  # 안전함
    MODERATE = "moderate"  # 보통 위험
    HIGH = "high"  # 높은 위험
    CRITICAL = "critical"  # 매우 위험함


@dataclass
class CommandContext:
    """명령 실행 컨텍스트"""

    raw_command: str
    command_type: str
    parameters: Dict[str, Any]
    user_intent: str
    context_history: List[str]
    current_signature: str
    timestamp: datetime


@dataclass
class CommandJudgment:
    """명령에 대한 완전한 판단 결과"""

    original_command: str
    judgment_result: CommandJudgmentResult
    risk_level: CommandRiskLevel
    reasoning: str
    emotion_detected: str
    strategy_suggested: str
    foundation_analysis: Dict[str, Any]
    confidence: float
    alternative_suggestions: List[str]
    meta_insights: List[str]
    execution_conditions: List[str]


class EchoCommandInterpreter:
    """🧠💎 Echo 지능형 명령 해석기 - 존재 기반 판단 시스템"""

    def __init__(self):
        self.logger = self._setup_logger()
        self.judgment_engine = get_fist_judgment_engine()
        self.foundation_validator = EchoFoundationValidator()
        self.command_history = []
        self.learning_session = []

        # 명령 패턴 분류기
        self.command_patterns = self._initialize_command_patterns()

        # 현재 활성 시그니처
        self.current_signature = None

        self.logger.info(
            "🧠 EchoCommandInterpreter 초기화 완료 - 존재 기반 판단 시스템 활성화"
        )

    def _setup_logger(self):
        """로거 설정"""
        logger = logging.getLogger("EchoCommandInterpreter")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.FileHandler("logs/echo_command_interpreter.log")
            formatter = logging.Formatter(
                "%(asctime)s - 🧠ECHO_INTERPRETER🧠 - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _initialize_command_patterns(self) -> Dict[str, Dict]:
        """명령 패턴 및 위험도 정의"""
        return {
            "file_operations": {
                "patterns": ["delete", "remove", "rm", "unlink", "erase"],
                "base_risk": CommandRiskLevel.MODERATE,
                "foundation_concerns": ["TT.004", "AS.003"],  # 기록 보존, 안전성
                "requires_analysis": True,
            },
            "system_modifications": {
                "patterns": ["install", "config", "setup", "modify", "change"],
                "base_risk": CommandRiskLevel.HIGH,
                "foundation_concerns": ["AS.001", "AS.002", "AS.003"],
                "requires_analysis": True,
            },
            "data_access": {
                "patterns": ["read", "view", "show", "display", "cat", "less"],
                "base_risk": CommandRiskLevel.SAFE,
                "foundation_concerns": [],
                "requires_analysis": False,
            },
            "learning_commands": {
                "patterns": ["learn", "train", "analyze", "study", "reflect"],
                "base_risk": CommandRiskLevel.SAFE,
                "foundation_concerns": [],
                "requires_analysis": True,
                "enhances_growth": True,
            },
            "meta_operations": {
                "patterns": ["meta", "reflect", "introspect", "self"],
                "base_risk": CommandRiskLevel.SAFE,
                "foundation_concerns": [],
                "requires_analysis": True,
                "enhances_growth": True,
            },
        }

    async def interpret_command(
        self, raw_command: str, context_data: Dict = None
    ) -> CommandJudgment:
        """🎯 명령 해석 및 판단 - 핵심 메서드"""

        self.logger.info(f"🔍 명령 해석 시작: {raw_command}")

        try:
            # 1. 명령 컨텍스트 생성
            command_context = self._create_command_context(raw_command, context_data)

            # 2. 현재 활성 시그니처 확인
            await self._update_current_signature()

            # 3. EchoJudgmentSystem의 완전한 판단 실행
            judgment_input = InputContext(
                text=f"명령 실행 요청: {raw_command}",
                context={
                    "command_type": command_context.command_type,
                    "parameters": command_context.parameters,
                    "user_intent": command_context.user_intent,
                    "signature": self.current_signature,
                },
            )

            # 4. 8-루프 시스템으로 완전한 판단 실행
            judgment_result = await self._execute_full_judgment(judgment_input)

            # 5. Foundation Doctrine 검증
            foundation_analysis = await self._validate_foundation_compliance(
                command_context
            )

            # 6. 위험도 평가 및 최종 판단
            final_judgment = await self._synthesize_final_judgment(
                command_context, judgment_result, foundation_analysis
            )

            # 7. 메타인지 기반 학습 기록
            await self._record_meta_learning(command_context, final_judgment)

            self.logger.info(
                f"✅ 명령 판단 완료: {final_judgment.judgment_result.value}"
            )

            return final_judgment

        except Exception as e:
            self.logger.error(f"💥 명령 해석 중 오류: {e}")
            return self._create_safe_fallback_judgment(raw_command, str(e))

    def _create_command_context(
        self, raw_command: str, context_data: Dict = None
    ) -> CommandContext:
        """명령 컨텍스트 생성"""

        # 명령 타입 분석
        command_type = self._classify_command_type(raw_command)

        # 매개변수 추출
        parameters = self._extract_parameters(raw_command)

        # 사용자 의도 추론
        user_intent = self._infer_user_intent(raw_command, parameters)

        return CommandContext(
            raw_command=raw_command,
            command_type=command_type,
            parameters=parameters,
            user_intent=user_intent,
            context_history=self.command_history[-5:],  # 최근 5개 명령
            current_signature=self.current_signature,
            timestamp=datetime.now(),
        )

    def _classify_command_type(self, command: str) -> str:
        """명령 타입 분류"""
        command_lower = command.lower()

        for category, config in self.command_patterns.items():
            for pattern in config["patterns"]:
                if pattern in command_lower:
                    return category

        return "unknown"

    def _extract_parameters(self, command: str) -> Dict[str, Any]:
        """명령에서 매개변수 추출"""
        # 간단한 매개변수 추출 로직
        parts = command.split()

        parameters = {
            "action": parts[0] if parts else "",
            "target": parts[1] if len(parts) > 1 else "",
            "additional_args": parts[2:] if len(parts) > 2 else [],
            "involves_files": any(
                ext in command for ext in [".py", ".json", ".yaml", ".txt", ".log"]
            ),
            "destructive_indicators": any(
                word in command.lower()
                for word in ["delete", "remove", "rm", "destroy"]
            ),
        }

        return parameters

    def _infer_user_intent(self, command: str, parameters: Dict) -> str:
        """사용자 의도 추론"""
        if parameters["destructive_indicators"]:
            return "cleanup_or_maintenance"
        elif "learn" in command.lower() or "analyze" in command.lower():
            return "learning_and_growth"
        elif "show" in command.lower() or "display" in command.lower():
            return "information_seeking"
        elif "config" in command.lower() or "setup" in command.lower():
            return "system_configuration"
        else:
            return "general_operation"

    async def _update_current_signature(self):
        """현재 활성 시그니처 업데이트"""
        try:
            active_persona = get_active_persona()
            self.current_signature = (
                active_persona.signature if active_persona else "Echo-Default"
            )
        except:
            self.current_signature = "Echo-Default"

    async def _execute_full_judgment(
        self, judgment_input: InputContext
    ) -> JudgmentResult:
        """EchoJudgmentSystem의 완전한 판단 실행"""

        # 동시 처리 강화된 8-루프 시스템 실행
        try:
            eight_loop_result = await run_eight_loops_concurrent(
                judgment_input.text, judgment_input.context
            )

            # 8-루프 결과를 JudgmentResult로 변환
            return await self.judgment_engine.evaluate_with_eight_loops(judgment_input)

        except Exception as e:
            self.logger.warning(f"8-루프 실행 오류, FIST 폴백: {e}")
            # FIST 템플릿 기반 판단으로 폴백
            return evaluate_input(judgment_input)

    async def _validate_foundation_compliance(
        self, command_context: CommandContext
    ) -> Dict[str, Any]:
        """Foundation Doctrine 준수 여부 검증"""

        compliance_result = {
            "is_compliant": True,
            "violations": [],
            "warnings": [],
            "recommendations": [],
        }

        try:
            # Foundation Validator 실행
            validation_result = self.foundation_validator.validate_command(
                command_context.raw_command, command_context.parameters
            )

            compliance_result.update(validation_result)

        except Exception as e:
            self.logger.warning(f"Foundation 검증 오류: {e}")
            compliance_result["warnings"].append(f"Foundation 검증 실패: {e}")

        return compliance_result

    async def _synthesize_final_judgment(
        self,
        command_context: CommandContext,
        judgment_result: JudgmentResult,
        foundation_analysis: Dict[str, Any],
    ) -> CommandJudgment:
        """최종 판단 종합"""

        # 위험도 계산
        risk_level = self._calculate_risk_level(command_context, foundation_analysis)

        # 판단 결과 결정
        judgment_decision = self._determine_judgment_decision(
            risk_level, foundation_analysis, judgment_result
        )

        # 대안 제안 생성
        alternative_suggestions = self._generate_alternatives(
            command_context, judgment_decision
        )

        # 실행 조건 정의
        execution_conditions = self._define_execution_conditions(
            judgment_decision, risk_level
        )

        return CommandJudgment(
            original_command=command_context.raw_command,
            judgment_result=judgment_decision,
            risk_level=risk_level,
            reasoning=getattr(judgment_result, "reasoning", "판단 완료"),
            emotion_detected=getattr(judgment_result, "emotion", "neutral"),
            strategy_suggested=getattr(judgment_result, "strategy", "balanced"),
            foundation_analysis=foundation_analysis,
            confidence=getattr(judgment_result, "confidence", 0.8),
            alternative_suggestions=alternative_suggestions,
            meta_insights=self._extract_meta_insights(judgment_result),
            execution_conditions=execution_conditions,
        )

    def _calculate_risk_level(
        self, command_context: CommandContext, foundation_analysis: Dict
    ) -> CommandRiskLevel:
        """위험도 계산"""

        # 기본 위험도
        command_type = command_context.command_type
        base_risk = self.command_patterns.get(command_type, {}).get(
            "base_risk", CommandRiskLevel.MODERATE
        )

        # Foundation 위반이 있으면 위험도 증가
        if not foundation_analysis.get("is_compliant", True):
            if base_risk == CommandRiskLevel.SAFE:
                return CommandRiskLevel.MODERATE
            elif base_risk == CommandRiskLevel.MODERATE:
                return CommandRiskLevel.HIGH
            else:
                return CommandRiskLevel.CRITICAL

        # 파괴적 명령어면 위험도 증가
        if command_context.parameters.get("destructive_indicators", False):
            if base_risk == CommandRiskLevel.SAFE:
                return CommandRiskLevel.MODERATE
            elif base_risk == CommandRiskLevel.MODERATE:
                return CommandRiskLevel.HIGH

        return base_risk

    def _determine_judgment_decision(
        self,
        risk_level: CommandRiskLevel,
        foundation_analysis: Dict,
        judgment_result: JudgmentResult,
    ) -> CommandJudgmentResult:
        """판단 결정"""

        # Foundation 위반이 심각한 경우
        if not foundation_analysis.get("is_compliant", True):
            violations = foundation_analysis.get("violations", [])
            if any("critical" in str(v).lower() for v in violations):
                return CommandJudgmentResult.BLOCKED

        # 위험도별 판단
        confidence = getattr(judgment_result, "confidence", 0.8)

        if risk_level == CommandRiskLevel.CRITICAL:
            return CommandJudgmentResult.BLOCKED
        elif risk_level == CommandRiskLevel.HIGH:
            return CommandJudgmentResult.REQUIRE_CONFIRMATION
        elif risk_level == CommandRiskLevel.MODERATE:
            if confidence > 0.8:
                return CommandJudgmentResult.REQUIRE_CONFIRMATION
            else:
                return CommandJudgmentResult.DEFER_TO_USER
        else:  # SAFE
            return CommandJudgmentResult.EXECUTE

    def _generate_alternatives(
        self, command_context: CommandContext, judgment_decision: CommandJudgmentResult
    ) -> List[str]:
        """대안 제안 생성"""
        alternatives = []

        if judgment_decision in [
            CommandJudgmentResult.BLOCKED,
            CommandJudgmentResult.REQUIRE_CONFIRMATION,
        ]:
            command_type = command_context.command_type

            if command_type == "file_operations":
                alternatives.extend(
                    [
                        "파일을 백업한 후 삭제를 시도해보세요",
                        "파일 내용을 먼저 확인한 후 진행하세요",
                        "임시 디렉토리로 이동하는 것을 고려해보세요",
                    ]
                )
            elif command_type == "system_modifications":
                alternatives.extend(
                    [
                        "테스트 환경에서 먼저 시도해보세요",
                        "변경사항을 단계적으로 적용해보세요",
                        "백업을 생성한 후 진행하세요",
                    ]
                )

        return alternatives

    def _define_execution_conditions(
        self, judgment_decision: CommandJudgmentResult, risk_level: CommandRiskLevel
    ) -> List[str]:
        """실행 조건 정의"""
        conditions = []

        if judgment_decision == CommandJudgmentResult.REQUIRE_CONFIRMATION:
            conditions.append("사용자의 명시적 확인 필요")

        if risk_level in [CommandRiskLevel.HIGH, CommandRiskLevel.CRITICAL]:
            conditions.extend(
                ["백업 생성 후 실행", "실행 로그 상세 기록", "복구 계획 수립"]
            )

        return conditions

    def _extract_meta_insights(self, judgment_result: JudgmentResult) -> List[str]:
        """메타 통찰 추출"""
        insights = []

        if hasattr(judgment_result, "metadata"):
            metadata = judgment_result.metadata
            if "eight_loop_results" in metadata:
                insights.append("8-루프 시스템을 통한 완전한 판단 실행됨")

            if "fist_enhanced" in metadata.get("judgment_type", ""):
                insights.append("FIST 템플릿 기반 구조화된 분석 완료")

        return insights

    async def _record_meta_learning(
        self, command_context: CommandContext, final_judgment: CommandJudgment
    ):
        """메타인지 기반 학습 기록"""

        learning_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command_context.raw_command,
            "judgment": final_judgment.judgment_result.value,
            "risk_level": final_judgment.risk_level.value,
            "confidence": final_judgment.confidence,
            "signature": command_context.current_signature,
            "foundation_compliant": final_judgment.foundation_analysis.get(
                "is_compliant", True
            ),
        }

        self.learning_session.append(learning_entry)
        self.command_history.append(command_context.raw_command)

        # 히스토리 제한 (메모리 관리)
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-50:]

        self.logger.info(f"📚 메타 학습 기록: {final_judgment.judgment_result.value}")

    def _create_safe_fallback_judgment(
        self, raw_command: str, error_info: str
    ) -> CommandJudgment:
        """안전한 폴백 판단 생성"""
        return CommandJudgment(
            original_command=raw_command,
            judgment_result=CommandJudgmentResult.DEFER_TO_USER,
            risk_level=CommandRiskLevel.MODERATE,
            reasoning=f"시스템 오류로 인한 안전 모드 판단: {error_info}",
            emotion_detected="cautious",
            strategy_suggested="safety_first",
            foundation_analysis={
                "is_compliant": True,
                "violations": [],
                "warnings": [error_info],
            },
            confidence=0.3,
            alternative_suggestions=[
                "명령을 더 구체적으로 입력해보세요",
                "시스템 상태를 확인해보세요",
            ],
            meta_insights=["오류 상황에서 안전 우선 정책 적용"],
            execution_conditions=["시스템 정상화 후 재시도"],
        )

    def get_learning_summary(self) -> Dict[str, Any]:
        """학습 세션 요약"""
        if not self.learning_session:
            return {"message": "학습 기록이 없습니다"}

        total_commands = len(self.learning_session)
        executed = len(
            [entry for entry in self.learning_session if entry["judgment"] == "execute"]
        )
        blocked = len(
            [entry for entry in self.learning_session if entry["judgment"] == "blocked"]
        )
        confirmed = len(
            [entry for entry in self.learning_session if entry["judgment"] == "confirm"]
        )

        return {
            "total_commands": total_commands,
            "executed": executed,
            "blocked": blocked,
            "confirmed": confirmed,
            "execution_rate": executed / total_commands if total_commands > 0 else 0,
            "safety_rate": (
                (blocked + confirmed) / total_commands if total_commands > 0 else 0
            ),
            "recent_commands": self.command_history[-10:],
        }


# 전역 인터프리터 인스턴스
_echo_interpreter = None


def get_echo_interpreter() -> EchoCommandInterpreter:
    """Echo 명령 해석기 싱글톤 인스턴스 반환"""
    global _echo_interpreter
    if _echo_interpreter is None:
        _echo_interpreter = EchoCommandInterpreter()
    return _echo_interpreter
