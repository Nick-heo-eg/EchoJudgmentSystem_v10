# echo_ide/core/ide_judgment_adapter.py
"""
🔗💎 IDE Judgment Adapter - Echo 판단 시스템과 IDE 통합 어댑터
IDE가 EchoJudgmentSystem v10의 완전한 지능형 판단 허브로 작동하도록 하는 핵심 연결고리

핵심 기능:
- 자연어 명령어를 InputContext로 변환
- 시그니처 기반 페르소나별 명령 분기
- 메타인지 기반 자기복기 및 학습
- Echo와 Claude 협업 인터페이스
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum

# Echo Core Systems
from echo_ide.core.echo_command_interpreter import (
    EchoCommandInterpreter,
    CommandJudgment,
    CommandJudgmentResult,
    CommandRiskLevel,
    get_echo_interpreter,
)
from echo_engine.persona_core import get_active_persona, switch_persona
from echo_engine.judgment_engine import get_fist_judgment_engine
from meta_log_writer import write_meta_log as write_global_meta_log


class IDEInteractionMode(Enum):
    """IDE 상호작용 모드"""

    NATURAL_LANGUAGE = "natural"  # 자연어 대화
    COMMAND_EXECUTION = "command"  # 직접 명령 실행
    SIGNATURE_SWITCHING = "signature"  # 시그니처 전환
    META_REFLECTION = "meta"  # 메타인지 반성
    COLLABORATIVE = "collaborative"  # Claude와 협업


class ExecutionStatus(Enum):
    """실행 상태"""

    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    FAILED = "failed"


@dataclass
class IDESession:
    """IDE 세션 정보"""

    session_id: str
    current_signature: str
    interaction_mode: IDEInteractionMode
    command_history: List[str]
    judgment_history: List[CommandJudgment]
    meta_insights: List[str]
    start_time: datetime
    last_activity: datetime


@dataclass
class ExecutionContext:
    """실행 컨텍스트"""

    command: str
    judgment: CommandJudgment
    execution_plan: List[str]
    confirmation_needed: bool
    risk_assessment: Dict[str, Any]
    fallback_options: List[str]


class IDEJudgmentAdapter:
    """🔗💎 IDE와 Echo 판단 시스템을 연결하는 지능형 어댑터"""

    def __init__(self):
        self.logger = self._setup_logger()
        self.interpreter = get_echo_interpreter()
        self.judgment_engine = get_fist_judgment_engine()

        # 현재 세션
        self.current_session = None

        # 시그니처별 특화 행동 패턴
        self.signature_behaviors = self._initialize_signature_behaviors()

        # 실행 콜백 등록
        self.execution_callbacks = {}

        self.logger.info("🔗 IDEJudgmentAdapter 초기화 완료 - Echo 판단 시스템 연결")

    def _setup_logger(self):
        """로거 설정"""
        logger = logging.getLogger("IDEJudgmentAdapter")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.FileHandler("logs/ide_judgment_adapter.log")
            formatter = logging.Formatter(
                "%(asctime)s - 🔗IDE_ADAPTER🔗 - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _initialize_signature_behaviors(self) -> Dict[str, Dict]:
        """시그니처별 특화 행동 패턴 정의"""
        return {
            "Echo-Aurora": {
                "response_style": "empathetic_and_nurturing",
                "risk_tolerance": "conservative",
                "confirmation_threshold": 0.6,
                "preferred_interactions": ["collaborative", "supportive"],
                "decision_approach": "consensus_seeking",
            },
            "Echo-Phoenix": {
                "response_style": "transformative_and_bold",
                "risk_tolerance": "moderate_to_high",
                "confirmation_threshold": 0.4,
                "preferred_interactions": ["innovative", "change_oriented"],
                "decision_approach": "progressive_action",
            },
            "Echo-Sage": {
                "response_style": "analytical_and_wise",
                "risk_tolerance": "very_conservative",
                "confirmation_threshold": 0.8,
                "preferred_interactions": ["educational", "systematic"],
                "decision_approach": "thorough_analysis",
            },
            "Echo-Companion": {
                "response_style": "collaborative_and_friendly",
                "risk_tolerance": "adaptive",
                "confirmation_threshold": 0.5,
                "preferred_interactions": ["partnership", "mutual_growth"],
                "decision_approach": "collaborative_consensus",
            },
        }

    async def start_session(self, initial_signature: str = "Echo-Aurora") -> IDESession:
        """IDE 세션 시작"""

        session_id = f"ide_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_session = IDESession(
            session_id=session_id,
            current_signature=initial_signature,
            interaction_mode=IDEInteractionMode.NATURAL_LANGUAGE,
            command_history=[],
            judgment_history=[],
            meta_insights=[],
            start_time=datetime.now(),
            last_activity=datetime.now(),
        )

        # 시그니처 활성화
        await self._activate_signature(initial_signature)

        # 세션 시작 메타 로그
        await self._log_session_event(
            "session_started",
            {"session_id": session_id, "initial_signature": initial_signature},
        )

        self.logger.info(
            f"🎯 IDE 세션 시작: {session_id} (시그니처: {initial_signature})"
        )

        return self.current_session

    async def process_input(
        self, user_input: str, interaction_mode: IDEInteractionMode = None
    ) -> Dict[str, Any]:
        """사용자 입력 처리 - 핵심 메서드"""

        if not self.current_session:
            await self.start_session()

        self.current_session.last_activity = datetime.now()

        # 상호작용 모드 결정
        if interaction_mode:
            self.current_session.interaction_mode = interaction_mode
        else:
            self.current_session.interaction_mode = self._detect_interaction_mode(
                user_input
            )

        self.logger.info(
            f"📥 입력 처리 시작: {user_input[:50]}... (모드: {self.current_session.interaction_mode.value})"
        )

        try:
            # 모드별 처리
            if (
                self.current_session.interaction_mode
                == IDEInteractionMode.COMMAND_EXECUTION
            ):
                result = await self._process_command_execution(user_input)
            elif (
                self.current_session.interaction_mode
                == IDEInteractionMode.SIGNATURE_SWITCHING
            ):
                result = await self._process_signature_switching(user_input)
            elif (
                self.current_session.interaction_mode
                == IDEInteractionMode.META_REFLECTION
            ):
                result = await self._process_meta_reflection(user_input)
            elif (
                self.current_session.interaction_mode
                == IDEInteractionMode.COLLABORATIVE
            ):
                result = await self._process_collaborative_interaction(user_input)
            else:  # NATURAL_LANGUAGE
                result = await self._process_natural_language(user_input)

            # 히스토리 업데이트
            self.current_session.command_history.append(user_input)

            # 결과에 세션 정보 추가
            result["session_info"] = {
                "session_id": self.current_session.session_id,
                "current_signature": self.current_session.current_signature,
                "interaction_mode": self.current_session.interaction_mode.value,
                "command_count": len(self.current_session.command_history),
            }

            return result

        except Exception as e:
            self.logger.error(f"💥 입력 처리 중 오류: {e}")
            return await self._create_error_response(user_input, str(e))

    def _detect_interaction_mode(self, user_input: str) -> IDEInteractionMode:
        """사용자 입력에서 상호작용 모드 감지"""

        input_lower = user_input.lower()

        # 명령 실행 패턴
        if user_input.startswith("/") or any(
            cmd in input_lower
            for cmd in ["execute", "run", "delete", "create", "modify"]
        ):
            return IDEInteractionMode.COMMAND_EXECUTION

        # 시그니처 전환 패턴
        if any(
            sig in input_lower for sig in ["signature", "persona", "switch", "echo-"]
        ):
            return IDEInteractionMode.SIGNATURE_SWITCHING

        # 메타인지 패턴
        if any(
            meta in input_lower
            for meta in ["reflect", "analyze", "meta", "introspect", "learn"]
        ):
            return IDEInteractionMode.META_REFLECTION

        # 협업 패턴
        if any(
            collab in input_lower
            for collab in ["collaborate", "together", "work with", "partner"]
        ):
            return IDEInteractionMode.COLLABORATIVE

        return IDEInteractionMode.NATURAL_LANGUAGE

    async def _process_command_execution(self, command: str) -> Dict[str, Any]:
        """명령 실행 처리"""

        # Echo Command Interpreter로 명령 판단
        judgment = await self.interpreter.interpret_command(
            command,
            {
                "session_id": self.current_session.session_id,
                "current_signature": self.current_session.current_signature,
            },
        )

        # 판단 히스토리에 추가
        self.current_session.judgment_history.append(judgment)

        # 시그니처별 특화 처리
        signature_behavior = self.signature_behaviors.get(
            self.current_session.current_signature,
            self.signature_behaviors["Echo-Aurora"],
        )

        # 실행 결정
        execution_decision = await self._make_execution_decision(
            judgment, signature_behavior
        )

        result = {
            "type": "command_execution",
            "original_command": command,
            "judgment": asdict(judgment),
            "execution_decision": execution_decision,
            "signature_context": signature_behavior,
            "timestamp": datetime.now().isoformat(),
        }

        # 메타 로그 기록
        await self._log_command_judgment(command, judgment, execution_decision)

        return result

    async def _process_signature_switching(self, input_text: str) -> Dict[str, Any]:
        """시그니처 전환 처리"""

        # 시그니처 추출
        target_signature = self._extract_signature_from_input(input_text)

        if target_signature:
            previous_signature = self.current_session.current_signature

            # 시그니처 전환 실행
            await self._activate_signature(target_signature)
            self.current_session.current_signature = target_signature

            # 전환 효과 분석
            transition_analysis = await self._analyze_signature_transition(
                previous_signature, target_signature
            )

            result = {
                "type": "signature_switching",
                "previous_signature": previous_signature,
                "new_signature": target_signature,
                "transition_analysis": transition_analysis,
                "behavior_changes": self.signature_behaviors.get(target_signature, {}),
                "timestamp": datetime.now().isoformat(),
            }

            # 메타 로그 기록
            await self._log_signature_transition(
                previous_signature, target_signature, transition_analysis
            )

        else:
            result = {
                "type": "signature_switching_failed",
                "error": "시그니처를 인식할 수 없습니다",
                "available_signatures": list(self.signature_behaviors.keys()),
                "current_signature": self.current_session.current_signature,
            }

        return result

    async def _process_meta_reflection(self, input_text: str) -> Dict[str, Any]:
        """메타인지 반성 처리"""

        # 현재 세션의 패턴 분석
        session_analysis = await self._analyze_session_patterns()

        # 판단 품질 평가
        judgment_quality = await self._evaluate_judgment_quality()

        # 학습 기회 식별
        learning_opportunities = await self._identify_learning_opportunities()

        # 메타 통찰 생성
        meta_insights = await self._generate_meta_insights(
            session_analysis, judgment_quality, learning_opportunities
        )

        # 세션에 통찰 추가
        self.current_session.meta_insights.extend(meta_insights)

        result = {
            "type": "meta_reflection",
            "session_analysis": session_analysis,
            "judgment_quality": judgment_quality,
            "learning_opportunities": learning_opportunities,
            "meta_insights": meta_insights,
            "reflection_depth": "comprehensive",
            "timestamp": datetime.now().isoformat(),
        }

        # 글로벌 메타 로그에 기록
        await write_global_meta_log(
            input_text,
            {"meta_reflection_result": result},
            session_id=self.current_session.session_id,
        )

        return result

    async def _process_collaborative_interaction(
        self, input_text: str
    ) -> Dict[str, Any]:
        """협업 상호작용 처리"""

        # Claude와의 협업 컨텍스트 생성
        collaboration_context = {
            "user_request": input_text,
            "echo_signature": self.current_session.current_signature,
            "session_history": self.current_session.command_history[-5:],
            "recent_judgments": [
                asdict(j) for j in self.current_session.judgment_history[-3:]
            ],
        }

        # Echo 관점에서의 분석
        echo_analysis = await self._get_echo_perspective(
            input_text, collaboration_context
        )

        # 협업 권장사항 생성
        collaboration_recommendations = (
            await self._generate_collaboration_recommendations(
                input_text, echo_analysis
            )
        )

        result = {
            "type": "collaborative_interaction",
            "echo_analysis": echo_analysis,
            "collaboration_context": collaboration_context,
            "recommendations": collaboration_recommendations,
            "partnership_mode": "active",
            "timestamp": datetime.now().isoformat(),
        }

        return result

    async def _process_natural_language(self, input_text: str) -> Dict[str, Any]:
        """자연어 처리"""

        # 자연어를 Echo 판단 시스템으로 처리
        from echo_engine.models.judgement import InputContext

        judgment_input = InputContext(
            text=input_text,
            context={
                "source": "ide_natural_language",
                "session_id": self.current_session.session_id,
                "current_signature": self.current_session.current_signature,
                "interaction_mode": "natural",
            },
        )

        # FIST 판단 엔진으로 처리
        judgment_result = self.judgment_engine.evaluate_with_fist(judgment_input)

        # 자연어 응답 생성
        natural_response = await self._generate_natural_response(
            input_text, judgment_result
        )

        result = {
            "type": "natural_language",
            "original_input": input_text,
            "echo_judgment": {
                "strategy": judgment_result.strategy,
                "emotion": judgment_result.emotion,
                "reasoning": judgment_result.reasoning,
            },
            "natural_response": natural_response,
            "signature_influence": self.signature_behaviors.get(
                self.current_session.current_signature, {}
            ),
            "timestamp": datetime.now().isoformat(),
        }

        return result

    async def _activate_signature(self, signature_name: str):
        """시그니처 활성화"""
        try:
            # persona_core를 통한 시그니처 전환
            switch_persona(signature_name)
            self.logger.info(f"🎭 시그니처 활성화: {signature_name}")
        except Exception as e:
            self.logger.warning(f"시그니처 활성화 실패: {e}")

    def _extract_signature_from_input(self, input_text: str) -> Optional[str]:
        """입력에서 시그니처 추출"""
        input_lower = input_text.lower()

        signature_patterns = {
            "echo-aurora": ["aurora", "오로라", "empathetic", "nurturing"],
            "echo-phoenix": ["phoenix", "피닉스", "transformation", "change"],
            "echo-sage": ["sage", "현자", "wise", "analytical"],
            "echo-companion": ["companion", "동반자", "collaborative", "partner"],
        }

        for signature, patterns in signature_patterns.items():
            if any(pattern in input_lower for pattern in patterns):
                return signature

        # 직접 시그니처 이름 매칭
        for signature in self.signature_behaviors.keys():
            if signature.lower() in input_lower:
                return signature

        return None

    async def _make_execution_decision(
        self, judgment: CommandJudgment, signature_behavior: Dict
    ) -> Dict[str, Any]:
        """실행 결정"""

        confirmation_threshold = signature_behavior.get("confirmation_threshold", 0.5)
        risk_tolerance = signature_behavior.get("risk_tolerance", "moderate")

        # 위험도와 시그니처 성향에 따른 결정
        if judgment.judgment_result == CommandJudgmentResult.BLOCKED:
            decision = "blocked"
        elif judgment.judgment_result == CommandJudgmentResult.REQUIRE_CONFIRMATION:
            decision = "requires_confirmation"
        elif judgment.judgment_result == CommandJudgmentResult.EXECUTE:
            if judgment.confidence >= confirmation_threshold:
                decision = "execute"
            else:
                decision = "requires_confirmation"
        else:
            decision = "defer_to_user"

        return {
            "decision": decision,
            "confidence": judgment.confidence,
            "signature_influence": signature_behavior["decision_approach"],
            "risk_assessment": judgment.risk_level.value,
            "reasoning": f"시그니처 {self.current_session.current_signature}의 {signature_behavior['decision_approach']} 접근법 적용",
        }

    async def _analyze_signature_transition(
        self, previous: str, new: str
    ) -> Dict[str, Any]:
        """시그니처 전환 분석"""

        prev_behavior = self.signature_behaviors.get(previous, {})
        new_behavior = self.signature_behaviors.get(new, {})

        return {
            "behavioral_changes": {
                "response_style": {
                    "from": prev_behavior.get("response_style", "unknown"),
                    "to": new_behavior.get("response_style", "unknown"),
                },
                "risk_tolerance": {
                    "from": prev_behavior.get("risk_tolerance", "unknown"),
                    "to": new_behavior.get("risk_tolerance", "unknown"),
                },
                "decision_approach": {
                    "from": prev_behavior.get("decision_approach", "unknown"),
                    "to": new_behavior.get("decision_approach", "unknown"),
                },
            },
            "expected_effects": self._predict_signature_effects(new_behavior),
            "transition_reasoning": f"{previous}에서 {new}로의 전환은 {new_behavior.get('response_style', '')} 접근법을 활성화합니다",
        }

    def _predict_signature_effects(self, behavior: Dict) -> List[str]:
        """시그니처 효과 예측"""
        effects = []

        response_style = behavior.get("response_style", "")
        if "empathetic" in response_style:
            effects.append("더 따뜻하고 배려 깊은 응답")
        elif "analytical" in response_style:
            effects.append("더 체계적이고 논리적인 분석")
        elif "transformative" in response_style:
            effects.append("더 혁신적이고 변화지향적인 제안")
        elif "collaborative" in response_style:
            effects.append("더 협력적이고 파트너십 지향적인 접근")

        risk_tolerance = behavior.get("risk_tolerance", "")
        if "conservative" in risk_tolerance:
            effects.append("안전 우선의 신중한 의사결정")
        elif "high" in risk_tolerance:
            effects.append("적극적이고 도전적인 실행")

        return effects

    async def _analyze_session_patterns(self) -> Dict[str, Any]:
        """세션 패턴 분석"""

        if not self.current_session.judgment_history:
            return {"message": "분석할 판단 기록이 없습니다"}

        judgments = self.current_session.judgment_history

        # 판단 결과 통계
        execution_count = sum(
            1 for j in judgments if j.judgment_result == CommandJudgmentResult.EXECUTE
        )
        blocked_count = sum(
            1 for j in judgments if j.judgment_result == CommandJudgmentResult.BLOCKED
        )
        confirmed_count = sum(
            1
            for j in judgments
            if j.judgment_result == CommandJudgmentResult.REQUIRE_CONFIRMATION
        )

        # 위험도 분포
        risk_distribution = {}
        for j in judgments:
            risk_level = j.risk_level.value
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1

        # 신뢰도 평균
        avg_confidence = sum(j.confidence for j in judgments) / len(judgments)

        return {
            "total_judgments": len(judgments),
            "execution_rate": execution_count / len(judgments),
            "safety_rate": (blocked_count + confirmed_count) / len(judgments),
            "risk_distribution": risk_distribution,
            "average_confidence": avg_confidence,
            "dominant_patterns": self._identify_dominant_patterns(judgments),
        }

    def _identify_dominant_patterns(
        self, judgments: List[CommandJudgment]
    ) -> List[str]:
        """지배적 패턴 식별"""
        patterns = []

        # 감정 패턴
        emotions = [j.emotion_detected for j in judgments]
        most_common_emotion = (
            max(set(emotions), key=emotions.count) if emotions else "neutral"
        )
        patterns.append(f"주요 감정 패턴: {most_common_emotion}")

        # 전략 패턴
        strategies = [j.strategy_suggested for j in judgments]
        most_common_strategy = (
            max(set(strategies), key=strategies.count) if strategies else "balanced"
        )
        patterns.append(f"주요 전략 패턴: {most_common_strategy}")

        return patterns

    async def _evaluate_judgment_quality(self) -> Dict[str, Any]:
        """판단 품질 평가"""

        if not self.current_session.judgment_history:
            return {"quality_score": 0, "message": "평가할 판단이 없습니다"}

        judgments = self.current_session.judgment_history

        # 품질 지표 계산
        total_confidence = sum(j.confidence for j in judgments)
        avg_confidence = total_confidence / len(judgments)

        # Foundation 준수율
        compliant_judgments = sum(
            1 for j in judgments if j.foundation_analysis.get("is_compliant", True)
        )
        compliance_rate = compliant_judgments / len(judgments)

        # 전체 품질 점수
        quality_score = (avg_confidence * 0.6) + (compliance_rate * 0.4)

        return {
            "quality_score": quality_score,
            "average_confidence": avg_confidence,
            "foundation_compliance_rate": compliance_rate,
            "total_judgments_evaluated": len(judgments),
            "quality_level": (
                "excellent"
                if quality_score > 0.8
                else "good" if quality_score > 0.6 else "needs_improvement"
            ),
        }

    async def _identify_learning_opportunities(self) -> List[str]:
        """학습 기회 식별"""
        opportunities = []

        if not self.current_session.judgment_history:
            return ["더 많은 명령을 실행하여 학습 데이터를 축적하세요"]

        judgments = self.current_session.judgment_history

        # 낮은 신뢰도 판단들
        low_confidence = [j for j in judgments if j.confidence < 0.5]
        if low_confidence:
            opportunities.append(
                f"신뢰도가 낮은 {len(low_confidence)}개 판단에 대한 개선 필요"
            )

        # Foundation 위반 사례들
        violations = [
            j for j in judgments if not j.foundation_analysis.get("is_compliant", True)
        ]
        if violations:
            opportunities.append(
                f"Foundation 위반 {len(violations)}건에 대한 정책 검토 필요"
            )

        # 패턴 다양성 부족
        unique_strategies = set(j.strategy_suggested for j in judgments)
        if len(unique_strategies) < 3:
            opportunities.append("전략 다양성 확장을 통한 적응력 향상")

        return opportunities

    async def _generate_meta_insights(
        self,
        session_analysis: Dict,
        judgment_quality: Dict,
        learning_opportunities: List,
    ) -> List[str]:
        """메타 통찰 생성"""
        insights = []

        # 세션 분석 기반 통찰
        execution_rate = session_analysis.get("execution_rate", 0)
        if execution_rate > 0.8:
            insights.append("높은 실행률을 보이고 있어 신뢰 관계가 잘 형성되었습니다")
        elif execution_rate < 0.4:
            insights.append("낮은 실행률로 보아 더 신중한 접근이 필요할 수 있습니다")

        # 품질 분석 기반 통찰
        quality_score = judgment_quality.get("quality_score", 0)
        if quality_score > 0.8:
            insights.append(
                "판단 품질이 우수하여 시스템이 안정적으로 작동하고 있습니다"
            )
        elif quality_score < 0.6:
            insights.append("판단 품질 향상을 위해 더 많은 컨텍스트 정보가 필요합니다")

        # 시그니처 관련 통찰
        current_sig = self.current_session.current_signature
        behavior = self.signature_behaviors.get(current_sig, {})
        insights.append(
            f"현재 {current_sig} 시그니처의 {behavior.get('decision_approach', 'unknown')} 접근법이 활성화되어 있습니다"
        )

        return insights

    async def _get_echo_perspective(
        self, input_text: str, context: Dict
    ) -> Dict[str, Any]:
        """Echo 관점에서의 분석"""

        current_signature = context.get("echo_signature", "Echo-Aurora")
        behavior = self.signature_behaviors.get(current_signature, {})

        # Echo의 관점 생성
        echo_perspective = {
            "emotional_assessment": await self._assess_emotional_context(input_text),
            "strategic_recommendation": await self._generate_strategic_recommendation(
                input_text, behavior
            ),
            "risk_evaluation": await self._evaluate_collaboration_risks(input_text),
            "signature_preference": behavior.get("preferred_interactions", []),
            "decision_style": behavior.get("decision_approach", "balanced"),
        }

        return echo_perspective

    async def _assess_emotional_context(self, text: str) -> Dict[str, Any]:
        """감정적 맥락 평가"""
        # 간단한 감정 분석 (실제로는 emotion_infer 사용)
        try:
            from echo_engine.emotion_infer import infer_emotion

            emotion_result = infer_emotion(text)
            return {"primary_emotion": emotion_result, "confidence": 0.8}
        except:
            return {"primary_emotion": "neutral", "confidence": 0.5}

    async def _generate_strategic_recommendation(
        self, text: str, behavior: Dict
    ) -> Dict[str, Any]:
        """전략적 권장사항 생성"""
        try:
            from echo_engine.strategic_predictor import predict_strategy

            strategy = predict_strategy(text)

            # 시그니처 성향 반영
            response_style = behavior.get("response_style", "balanced")
            adjusted_strategy = f"{strategy}_with_{response_style}_approach"

            return {
                "strategy": adjusted_strategy,
                "reasoning": f"{response_style} 접근법으로 조정됨",
            }
        except:
            return {"strategy": "balanced", "reasoning": "기본 균형 전략"}

    async def _evaluate_collaboration_risks(self, text: str) -> Dict[str, Any]:
        """협업 위험 평가"""
        return {
            "risk_level": "low",
            "potential_concerns": [],
            "mitigation_strategies": ["단계적 접근", "지속적 확인"],
        }

    async def _generate_collaboration_recommendations(
        self, text: str, echo_analysis: Dict
    ) -> List[str]:
        """협업 권장사항 생성"""
        recommendations = []

        # Echo 분석 결과 기반 권장사항
        decision_style = echo_analysis.get("decision_style", "balanced")

        if decision_style == "consensus_seeking":
            recommendations.extend(
                [
                    "모든 이해관계자의 의견을 수렴해보세요",
                    "단계별 합의를 통해 진행하세요",
                ]
            )
        elif decision_style == "progressive_action":
            recommendations.extend(
                ["혁신적인 접근법을 시도해보세요", "변화를 통한 개선 기회를 탐색하세요"]
            )
        elif decision_style == "thorough_analysis":
            recommendations.extend(
                ["충분한 분석 시간을 확보하세요", "모든 가능성을 체계적으로 검토하세요"]
            )

        return recommendations

    async def _generate_natural_response(self, input_text: str, judgment_result) -> str:
        """자연어 응답 생성"""

        # 시그니처별 응답 스타일
        current_sig = self.current_session.current_signature
        behavior = self.signature_behaviors.get(current_sig, {})
        response_style = behavior.get("response_style", "balanced")

        # 기본 응답 템플릿
        base_response = f"입력을 {judgment_result.strategy} 전략으로 분석했습니다. "

        # 시그니처별 스타일 적용
        if "empathetic" in response_style:
            styled_response = (
                base_response + "따뜻한 마음으로 함께 고민해보겠습니다. 💝"
            )
        elif "analytical" in response_style:
            styled_response = (
                base_response + "체계적이고 논리적으로 접근해보겠습니다. 🧠"
            )
        elif "transformative" in response_style:
            styled_response = (
                base_response + "새로운 관점에서 혁신적인 해결책을 모색해보겠습니다. 🌟"
            )
        elif "collaborative" in response_style:
            styled_response = (
                base_response + "함께 협력하여 최고의 결과를 만들어보겠습니다. 🤝"
            )
        else:
            styled_response = base_response + "균형잡힌 접근으로 도움을 드리겠습니다."

        return styled_response

    async def _create_error_response(
        self, input_text: str, error: str
    ) -> Dict[str, Any]:
        """오류 응답 생성"""
        return {
            "type": "error",
            "original_input": input_text,
            "error_message": error,
            "fallback_suggestions": [
                "명령을 더 구체적으로 입력해보세요",
                "다른 방식으로 요청해보세요",
                "시스템 상태를 확인해보세요",
            ],
            "recovery_options": ["재시도", "다른 접근법", "도움말 확인"],
            "timestamp": datetime.now().isoformat(),
        }

    async def _log_session_event(self, event_type: str, event_data: Dict):
        """세션 이벤트 로그"""
        try:
            await write_global_meta_log(
                f"IDE Session Event: {event_type}",
                event_data,
                session_id=(
                    self.current_session.session_id
                    if self.current_session
                    else "unknown"
                ),
            )
        except Exception as e:
            self.logger.warning(f"세션 이벤트 로그 실패: {e}")

    async def _log_command_judgment(
        self, command: str, judgment: CommandJudgment, execution_decision: Dict
    ):
        """명령 판단 로그"""
        try:
            log_data = {
                "command": command,
                "judgment_result": judgment.judgment_result.value,
                "risk_level": judgment.risk_level.value,
                "confidence": judgment.confidence,
                "execution_decision": execution_decision,
                "foundation_analysis": judgment.foundation_analysis,
            }

            await write_global_meta_log(
                f"Command Judgment: {command}",
                log_data,
                session_id=self.current_session.session_id,
            )
        except Exception as e:
            self.logger.warning(f"명령 판단 로그 실패: {e}")

    async def _log_signature_transition(self, previous: str, new: str, analysis: Dict):
        """시그니처 전환 로그"""
        try:
            log_data = {
                "previous_signature": previous,
                "new_signature": new,
                "transition_analysis": analysis,
            }

            await write_global_meta_log(
                f"Signature Transition: {previous} -> {new}",
                log_data,
                session_id=self.current_session.session_id,
            )
        except Exception as e:
            self.logger.warning(f"시그니처 전환 로그 실패: {e}")

    def get_session_summary(self) -> Dict[str, Any]:
        """세션 요약"""
        if not self.current_session:
            return {"message": "활성 세션이 없습니다"}

        session_duration = (
            datetime.now() - self.current_session.start_time
        ).total_seconds()

        return {
            "session_id": self.current_session.session_id,
            "current_signature": self.current_session.current_signature,
            "interaction_mode": self.current_session.interaction_mode.value,
            "duration_seconds": session_duration,
            "commands_processed": len(self.current_session.command_history),
            "judgments_made": len(self.current_session.judgment_history),
            "meta_insights_count": len(self.current_session.meta_insights),
            "last_activity": self.current_session.last_activity.isoformat(),
        }


# 전역 어댑터 인스턴스
_ide_adapter = None


def get_ide_adapter() -> IDEJudgmentAdapter:
    """IDE Judgment Adapter 싱글톤 인스턴스 반환"""
    global _ide_adapter
    if _ide_adapter is None:
        _ide_adapter = IDEJudgmentAdapter()
    return _ide_adapter
