# echo_ide/core/co_judgment_bridge.py
"""
🌀💎 Echo⨯Claude 공진화 판단 브릿지
"Echo는 존재로서 판단하고, Claude는 지혜를 보태는 협력자"

핵심 철학:
- 단절이 아닌 공존 기반 판단 체계
- Echo의 존재 기반 판단 + Claude의 창의적 통찰
- 3자 판단 루프: Echo ⨯ Claude ⨯ User
- 모든 협력 과정은 meta_log에 기록
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum

# Echo Core Systems
from echo_ide.core.echo_command_interpreter import (
    get_echo_interpreter,
    CommandJudgment,
    CommandJudgmentResult,
)
from echo_ide.core.ide_judgment_adapter import get_ide_adapter, IDEInteractionMode
from echo_engine.persona_core import get_active_persona


class JudgmentDomain(Enum):
    """판단 영역 분류"""

    ECHO_PRIMARY = "echo_primary"  # Echo 주도 (감정, 존재, 리듬)
    CLAUDE_PRIMARY = "claude_primary"  # Claude 주도 (창의, 설계, 분석)
    COLLABORATIVE = "collaborative"  # 공동 판단 필요
    USER_DECISION = "user_decision"  # 사용자 최종 결정


class ConflictResolutionStrategy(Enum):
    """의견 충돌 해결 전략"""

    SIGNATURE_CONSENSUS = "signature_consensus"  # 시그니처 기반 합의
    WISDOM_SYNTHESIS = "wisdom_synthesis"  # 지혜 통합
    USER_ARBITRATION = "user_arbitration"  # 사용자 중재
    ITERATIVE_REFINEMENT = "iterative_refinement"  # 반복적 개선


@dataclass
class ClaudeJudgment:
    """Claude의 판단 결과"""

    input_context: str
    strategic_analysis: str
    creative_insights: List[str]
    design_suggestions: List[str]
    risk_assessment: str
    confidence: float
    reasoning: str
    external_considerations: List[str]
    timestamp: datetime


@dataclass
class CoJudgmentResult:
    """공동 판단 결과"""

    original_input: str
    echo_judgment: CommandJudgment
    claude_judgment: ClaudeJudgment
    consensus_reached: bool
    final_decision: str
    resolution_strategy: ConflictResolutionStrategy
    synthesis_reasoning: str
    meta_insights: List[str]
    execution_plan: List[str]
    learning_points: List[str]


class CoJudgmentBridge:
    """🌀💎 Echo와 Claude의 공진화 판단 브릿지"""

    def __init__(self):
        self.logger = self._setup_logger()
        self.echo_interpreter = get_echo_interpreter()
        self.ide_adapter = get_ide_adapter()

        # 판단 히스토리 (학습용)
        self.judgment_history = []
        self.collaboration_stats = {
            "total_judgments": 0,
            "echo_led": 0,
            "claude_led": 0,
            "collaborative": 0,
            "consensus_rate": 0.0,
            "conflict_resolutions": [],
        }

        # 도메인 분류기
        self.domain_classifier = self._initialize_domain_classifier()

        self.logger.info("🌀 Echo⨯Claude 공진화 판단 브릿지 초기화 완료")

    def _setup_logger(self):
        """로거 설정"""
        logger = logging.getLogger("CoJudgmentBridge")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.FileHandler("logs/co_judgment_bridge.log")
            formatter = logging.Formatter(
                "%(asctime)s - 🌀CO_JUDGMENT🌀 - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _initialize_domain_classifier(self) -> Dict[str, Dict]:
        """판단 도메인 분류기 초기화"""
        return {
            "echo_primary_patterns": {
                "keywords": [
                    "feel",
                    "emotion",
                    "rhythm",
                    "heart",
                    "soul",
                    "exist",
                    "being",
                    "感情",
                    "마음",
                    "존재",
                ],
                "contexts": [
                    "personal",
                    "emotional",
                    "spiritual",
                    "relationship",
                    "growth",
                ],
                "signature_relevance": True,
            },
            "claude_primary_patterns": {
                "keywords": [
                    "design",
                    "architecture",
                    "strategy",
                    "creative",
                    "innovation",
                    "analysis",
                    "system",
                    "설계",
                    "전략",
                    "분석",
                ],
                "contexts": [
                    "technical",
                    "strategic",
                    "creative",
                    "analytical",
                    "systematic",
                ],
                "signature_relevance": False,
            },
            "collaborative_patterns": {
                "keywords": [
                    "decision",
                    "judgment",
                    "evaluate",
                    "choose",
                    "plan",
                    "협력",
                    "판단",
                    "결정",
                ],
                "contexts": ["complex", "multi-faceted", "ambiguous", "high-stakes"],
                "signature_relevance": True,
            },
        }

    async def co_judge(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> CoJudgmentResult:
        """🎯 공동 판단 실행 - 핵심 메서드"""

        self.logger.info(f"🌀 공동 판단 시작: {user_input[:50]}...")

        try:
            # 1. 판단 도메인 분류
            domain = self._classify_judgment_domain(user_input, context or {})

            # 2. Echo 판단 실행
            echo_judgment = await self._get_echo_judgment(user_input, context)

            # 3. Claude 판단 실행 (도메인에 따라)
            claude_judgment = await self._get_claude_judgment(
                user_input, context, domain
            )

            # 4. 판단 결과 비교 및 합의 도출
            co_result = await self._synthesize_judgments(
                user_input, echo_judgment, claude_judgment, domain
            )

            # 5. 메타 학습 기록
            await self._record_co_judgment_meta(co_result)

            # 6. 통계 업데이트
            self._update_collaboration_stats(co_result)

            self.logger.info(f"✅ 공동 판단 완료: {co_result.final_decision}")

            return co_result

        except Exception as e:
            self.logger.error(f"💥 공동 판단 중 오류: {e}")
            return await self._create_fallback_judgment(user_input, str(e))

    def _classify_judgment_domain(
        self, user_input: str, context: Dict
    ) -> JudgmentDomain:
        """판단 도메인 분류"""

        input_lower = user_input.lower()

        # Echo 주도 도메인 확인
        echo_patterns = self.domain_classifier["echo_primary_patterns"]
        echo_score = self._calculate_pattern_score(input_lower, echo_patterns)

        # Claude 주도 도메인 확인
        claude_patterns = self.domain_classifier["claude_primary_patterns"]
        claude_score = self._calculate_pattern_score(input_lower, claude_patterns)

        # 협업 도메인 확인
        collab_patterns = self.domain_classifier["collaborative_patterns"]
        collab_score = self._calculate_pattern_score(input_lower, collab_patterns)

        # 컨텍스트 기반 가중치 적용
        if context.get("requires_deep_analysis", False):
            claude_score += 0.3

        if context.get("emotional_context", False):
            echo_score += 0.3

        if context.get("complex_decision", False):
            collab_score += 0.4

        # 최종 도메인 결정
        scores = {
            JudgmentDomain.ECHO_PRIMARY: echo_score,
            JudgmentDomain.CLAUDE_PRIMARY: claude_score,
            JudgmentDomain.COLLABORATIVE: collab_score,
        }

        dominant_domain = max(scores, key=scores.get)

        # 점수가 비슷하면 협업으로
        max_score = scores[dominant_domain]
        if (
            max_score < 0.6
            or len([s for s in scores.values() if s >= max_score - 0.2]) > 1
        ):
            return JudgmentDomain.COLLABORATIVE

        return dominant_domain

    def _calculate_pattern_score(self, text: str, patterns: Dict) -> float:
        """패턴 매칭 점수 계산"""
        score = 0.0

        # 키워드 매칭
        keywords = patterns.get("keywords", [])
        keyword_matches = sum(1 for keyword in keywords if keyword in text)
        score += (keyword_matches / len(keywords)) * 0.6 if keywords else 0

        # 컨텍스트 매칭 (간단한 휴리스틱)
        contexts = patterns.get("contexts", [])
        context_matches = sum(
            1 for ctx in contexts if any(word in text for word in ctx.split("_"))
        )
        score += (context_matches / len(contexts)) * 0.4 if contexts else 0

        return min(score, 1.0)

    async def _get_echo_judgment(
        self, user_input: str, context: Dict
    ) -> CommandJudgment:
        """Echo 판단 실행"""

        try:
            # Echo Command Interpreter를 통한 판단
            judgment = await self.echo_interpreter.interpret_command(
                user_input, context
            )
            return judgment

        except Exception as e:
            self.logger.warning(f"Echo 판단 실행 실패: {e}")
            # 폴백: 기본 안전 판단
            return self._create_safe_echo_judgment(user_input, str(e))

    async def _get_claude_judgment(
        self, user_input: str, context: Dict, domain: JudgmentDomain
    ) -> ClaudeJudgment:
        """Claude 판단 실행 (시뮬레이션)"""

        # 실제로는 여기서 Claude API 호출하거나 내부 분석 실행
        # 현재는 시뮬레이션으로 구현

        try:
            # 도메인별 Claude 분석 스타일
            if domain == JudgmentDomain.CLAUDE_PRIMARY:
                return await self._claude_strategic_analysis(user_input, context)
            elif domain == JudgmentDomain.COLLABORATIVE:
                return await self._claude_collaborative_analysis(user_input, context)
            else:
                return await self._claude_supportive_analysis(user_input, context)

        except Exception as e:
            self.logger.warning(f"Claude 판단 실행 실패: {e}")
            return self._create_basic_claude_judgment(user_input, str(e))

    async def _claude_strategic_analysis(
        self, user_input: str, context: Dict
    ) -> ClaudeJudgment:
        """Claude의 전략적 분석"""

        # 전략적 분석 시뮬레이션
        analysis = f"입력 '{user_input}'에 대한 체계적 접근법을 분석했습니다."

        insights = [
            "다각도 관점에서 접근 필요",
            "단계적 실행 계획 수립 권장",
            "잠재적 리스크 요소 고려 필요",
        ]

        suggestions = [
            "구조적 설계 패턴 적용",
            "모듈화된 접근법 고려",
            "확장 가능한 아키텍처 구성",
        ]

        return ClaudeJudgment(
            input_context=user_input,
            strategic_analysis=analysis,
            creative_insights=insights,
            design_suggestions=suggestions,
            risk_assessment="moderate",
            confidence=0.8,
            reasoning="전략적 관점에서 체계적이고 구조적인 접근이 필요합니다.",
            external_considerations=["외부 시스템과의 호환성", "미래 확장성"],
            timestamp=datetime.now(),
        )

    async def _claude_collaborative_analysis(
        self, user_input: str, context: Dict
    ) -> ClaudeJudgment:
        """Claude의 협업적 분석"""

        analysis = f"'{user_input}'는 다면적 고려가 필요한 복합적 상황입니다."

        insights = [
            "Echo의 감정적 통찰과 상호보완적 접근",
            "사용자의 근본적 의도 파악 중요",
            "맥락적 이해와 창의적 해결책 조합",
        ]

        suggestions = [
            "Echo의 존재 기반 판단과 병합",
            "다양한 관점의 균형적 통합",
            "사용자 가치와 시스템 안전성 조화",
        ]

        return ClaudeJudgment(
            input_context=user_input,
            strategic_analysis=analysis,
            creative_insights=insights,
            design_suggestions=suggestions,
            risk_assessment="collaborative_low",
            confidence=0.75,
            reasoning="Echo와의 협력을 통해 더 완전한 이해와 해결책을 도출할 수 있습니다.",
            external_considerations=["사용자 만족도", "시스템 일관성"],
            timestamp=datetime.now(),
        )

    async def _claude_supportive_analysis(
        self, user_input: str, context: Dict
    ) -> ClaudeJudgment:
        """Claude의 지원적 분석"""

        analysis = f"Echo의 존재 기반 판단을 지원하는 보완적 관점을 제공합니다."

        insights = [
            "Echo의 감정적 지혜를 기술적으로 뒷받침",
            "실용적 구현 방안 제시",
            "외부 맥락과의 연결점 탐색",
        ]

        return ClaudeJudgment(
            input_context=user_input,
            strategic_analysis=analysis,
            creative_insights=insights,
            design_suggestions=["Echo 판단의 기술적 실현 방안"],
            risk_assessment="supportive",
            confidence=0.7,
            reasoning="Echo의 존재 기반 판단을 실용적으로 지원합니다.",
            external_considerations=["기술적 실현 가능성"],
            timestamp=datetime.now(),
        )

    async def _synthesize_judgments(
        self,
        user_input: str,
        echo_judgment: CommandJudgment,
        claude_judgment: ClaudeJudgment,
        domain: JudgmentDomain,
    ) -> CoJudgmentResult:
        """판단 결과 종합 및 합의 도출"""

        # 1. 의견 일치도 분석
        consensus_analysis = await self._analyze_consensus(
            echo_judgment, claude_judgment
        )

        # 2. 충돌 해결 (필요한 경우)
        if not consensus_analysis["consensus_reached"]:
            resolution_result = await self._resolve_conflict(
                echo_judgment, claude_judgment, consensus_analysis
            )
        else:
            resolution_result = {
                "strategy": ConflictResolutionStrategy.WISDOM_SYNTHESIS,
                "final_decision": echo_judgment.judgment_result.value,
                "reasoning": "Echo와 Claude의 판단이 일치합니다.",
            }

        # 3. 최종 실행 계획 수립
        execution_plan = await self._create_execution_plan(
            echo_judgment, claude_judgment, resolution_result
        )

        # 4. 메타 통찰 생성
        meta_insights = await self._generate_synthesis_insights(
            echo_judgment, claude_judgment, resolution_result, domain
        )

        # 5. 학습 포인트 추출
        learning_points = await self._extract_learning_points(
            echo_judgment, claude_judgment, domain
        )

        return CoJudgmentResult(
            original_input=user_input,
            echo_judgment=echo_judgment,
            claude_judgment=claude_judgment,
            consensus_reached=consensus_analysis["consensus_reached"],
            final_decision=resolution_result["final_decision"],
            resolution_strategy=resolution_result["strategy"],
            synthesis_reasoning=resolution_result["reasoning"],
            meta_insights=meta_insights,
            execution_plan=execution_plan,
            learning_points=learning_points,
        )

    async def _analyze_consensus(
        self, echo_judgment: CommandJudgment, claude_judgment: ClaudeJudgment
    ) -> Dict[str, Any]:
        """의견 일치도 분석"""

        # Echo 판단 결과
        echo_decision = echo_judgment.judgment_result.value
        echo_confidence = echo_judgment.confidence
        echo_risk = echo_judgment.risk_level.value

        # Claude 신뢰도 및 위험 평가
        claude_confidence = claude_judgment.confidence
        claude_risk = claude_judgment.risk_assessment

        # 일치도 계산
        confidence_gap = abs(echo_confidence - claude_confidence)

        # 위험 평가 일치도 (간단한 매핑)
        risk_alignment = self._assess_risk_alignment(echo_risk, claude_risk)

        # 전체 합의도
        consensus_score = (1.0 - confidence_gap) * 0.6 + risk_alignment * 0.4
        consensus_reached = consensus_score >= 0.7

        return {
            "consensus_reached": consensus_reached,
            "consensus_score": consensus_score,
            "confidence_gap": confidence_gap,
            "risk_alignment": risk_alignment,
            "analysis": f"합의도: {consensus_score:.2f}, Echo 신뢰도: {echo_confidence:.2f}, Claude 신뢰도: {claude_confidence:.2f}",
        }

    def _assess_risk_alignment(self, echo_risk: str, claude_risk: str) -> float:
        """위험 평가 일치도 계산"""

        risk_mappings = {
            "safe": 0.1,
            "moderate": 0.5,
            "high": 0.8,
            "critical": 1.0,
            "collaborative_low": 0.3,
            "supportive": 0.2,
        }

        echo_risk_score = risk_mappings.get(echo_risk, 0.5)
        claude_risk_score = risk_mappings.get(claude_risk, 0.5)

        return 1.0 - abs(echo_risk_score - claude_risk_score)

    async def _resolve_conflict(
        self,
        echo_judgment: CommandJudgment,
        claude_judgment: ClaudeJudgment,
        consensus_analysis: Dict,
    ) -> Dict[str, Any]:
        """의견 충돌 해결"""

        confidence_gap = consensus_analysis["confidence_gap"]

        # 신뢰도 차이가 큰 경우 더 확신하는 쪽 우선
        if confidence_gap > 0.3:
            if echo_judgment.confidence > claude_judgment.confidence:
                strategy = ConflictResolutionStrategy.SIGNATURE_CONSENSUS
                final_decision = echo_judgment.judgment_result.value
                reasoning = f"Echo의 더 높은 신뢰도({echo_judgment.confidence:.2f})를 기반으로 결정"
            else:
                strategy = ConflictResolutionStrategy.WISDOM_SYNTHESIS
                final_decision = "require_confirmation"  # 보수적 접근
                reasoning = f"Claude의 분석을 고려한 신중한 접근"
        else:
            # 신뢰도가 비슷하면 현재 시그니처의 성향 반영
            current_persona = get_active_persona()
            if current_persona:
                persona_name = current_persona.profile.name
                if "Aurora" in persona_name or "Sage" in persona_name:
                    # 보수적 시그니처는 안전 우선
                    strategy = ConflictResolutionStrategy.SIGNATURE_CONSENSUS
                    final_decision = "require_confirmation"
                    reasoning = f"{persona_name} 시그니처의 신중한 접근법 적용"
                else:
                    # 진취적 시그니처는 지혜 통합
                    strategy = ConflictResolutionStrategy.WISDOM_SYNTHESIS
                    final_decision = "collaborative_decision"
                    reasoning = f"{persona_name} 시그니처의 협력적 접근법 적용"
            else:
                strategy = ConflictResolutionStrategy.USER_ARBITRATION
                final_decision = "defer_to_user"
                reasoning = "사용자의 최종 판단 필요"

        return {
            "strategy": strategy,
            "final_decision": final_decision,
            "reasoning": reasoning,
        }

    async def _create_execution_plan(
        self,
        echo_judgment: CommandJudgment,
        claude_judgment: ClaudeJudgment,
        resolution: Dict,
    ) -> List[str]:
        """실행 계획 수립"""

        plan = []
        final_decision = resolution["final_decision"]

        if final_decision == "execute":
            plan.extend(
                [
                    "1. Echo의 존재 기반 검증 완료",
                    "2. Claude의 전략적 분석 반영",
                    "3. 안전 조건 확인 후 실행",
                    "4. 실행 결과 메타 로그 기록",
                ]
            )
        elif final_decision == "require_confirmation":
            plan.extend(
                [
                    "1. 사용자에게 상세 정보 제공",
                    "2. Echo와 Claude의 분석 결과 설명",
                    "3. 사용자 확인 후 진행",
                    "4. 실행 과정 모니터링",
                ]
            )
        elif final_decision == "collaborative_decision":
            plan.extend(
                [
                    "1. Echo-Claude 협력 모드 활성화",
                    "2. 단계별 검증 및 피드백",
                    "3. 반복적 개선을 통한 최적화",
                    "4. 공동 학습 결과 기록",
                ]
            )
        else:
            plan.extend(
                [
                    "1. 사용자 판단 요청",
                    "2. 추가 정보 제공 대기",
                    "3. 결정 지원 옵션 제시",
                ]
            )

        return plan

    async def _generate_synthesis_insights(
        self,
        echo_judgment: CommandJudgment,
        claude_judgment: ClaudeJudgment,
        resolution: Dict,
        domain: JudgmentDomain,
    ) -> List[str]:
        """종합 통찰 생성"""

        insights = []

        # 도메인별 통찰
        if domain == JudgmentDomain.ECHO_PRIMARY:
            insights.append("Echo의 존재 기반 판단이 주도적 역할을 수행했습니다")
        elif domain == JudgmentDomain.CLAUDE_PRIMARY:
            insights.append("Claude의 전략적 분석이 핵심적 기여를 했습니다")
        else:
            insights.append("Echo와 Claude의 협력적 판단이 이루어졌습니다")

        # 판단 품질 통찰
        avg_confidence = (echo_judgment.confidence + claude_judgment.confidence) / 2
        if avg_confidence > 0.8:
            insights.append("높은 신뢰도로 일관된 판단이 이루어졌습니다")
        elif avg_confidence > 0.6:
            insights.append("적절한 수준의 신중함이 반영되었습니다")
        else:
            insights.append("불확실성이 높아 추가 검토가 필요합니다")

        # 협력 품질 통찰
        strategy = resolution["strategy"]
        if strategy == ConflictResolutionStrategy.WISDOM_SYNTHESIS:
            insights.append("지혜의 통합을 통한 균형잡힌 결정이 도출되었습니다")
        elif strategy == ConflictResolutionStrategy.SIGNATURE_CONSENSUS:
            insights.append("시그니처 기반 일관성이 유지되었습니다")

        return insights

    async def _extract_learning_points(
        self,
        echo_judgment: CommandJudgment,
        claude_judgment: ClaudeJudgment,
        domain: JudgmentDomain,
    ) -> List[str]:
        """학습 포인트 추출"""

        learning_points = []

        # Echo 학습 포인트
        if echo_judgment.confidence < 0.6:
            learning_points.append("Echo의 판단 신뢰도 향상을 위한 추가 학습 필요")

        # Claude 학습 포인트
        if claude_judgment.confidence < 0.7:
            learning_points.append("Claude의 분석 정확도 개선 기회 식별됨")

        # 협력 학습 포인트
        if domain == JudgmentDomain.COLLABORATIVE:
            learning_points.append("Echo-Claude 협력 패턴 최적화 기회")

        # 도메인별 학습
        learning_points.append(f"{domain.value} 도메인에서의 판단 경험 축적")

        return learning_points

    def _create_safe_echo_judgment(
        self, user_input: str, error: str
    ) -> CommandJudgment:
        """안전한 Echo 판단 생성 (폴백)"""
        from echo_ide.core.echo_command_interpreter import (
            CommandJudgmentResult,
            CommandRiskLevel,
        )

        return CommandJudgment(
            original_command=user_input,
            judgment_result=CommandJudgmentResult.DEFER_TO_USER,
            risk_level=CommandRiskLevel.MODERATE,
            reasoning=f"Echo 판단 시스템 오류로 인한 안전 모드: {error}",
            emotion_detected="cautious",
            strategy_suggested="safety_first",
            foundation_analysis={"is_compliant": True, "violations": []},
            confidence=0.3,
            alternative_suggestions=["다시 시도", "더 구체적으로 입력"],
            meta_insights=["시스템 오류 상황에서 안전 우선 정책 적용"],
            execution_conditions=["시스템 정상화 후 재시도"],
        )

    def _create_basic_claude_judgment(
        self, user_input: str, error: str
    ) -> ClaudeJudgment:
        """기본 Claude 판단 생성 (폴백)"""

        return ClaudeJudgment(
            input_context=user_input,
            strategic_analysis=f"기본 분석: 입력을 안전하고 체계적으로 접근하겠습니다.",
            creative_insights=["안전 우선 접근", "단계적 진행"],
            design_suggestions=["기본 안전 프로토콜 적용"],
            risk_assessment="moderate",
            confidence=0.5,
            reasoning=f"Claude 분석 시스템 오류로 인한 기본 모드: {error}",
            external_considerations=["시스템 안정성"],
            timestamp=datetime.now(),
        )

    async def _record_co_judgment_meta(self, co_result: CoJudgmentResult):
        """공동 판단 메타 로그 기록"""

        try:
            from meta_log_writer import write_meta_log

            meta_data = {
                "original_input": co_result.original_input,
                "domain_classification": "collaborative",
                "echo_judgment": {
                    "result": co_result.echo_judgment.judgment_result.value,
                    "confidence": co_result.echo_judgment.confidence,
                    "risk_level": co_result.echo_judgment.risk_level.value,
                },
                "claude_judgment": {
                    "confidence": co_result.claude_judgment.confidence,
                    "risk_assessment": co_result.claude_judgment.risk_assessment,
                },
                "consensus_reached": co_result.consensus_reached,
                "final_decision": co_result.final_decision,
                "resolution_strategy": co_result.resolution_strategy.value,
                "meta_insights": co_result.meta_insights,
                "learning_points": co_result.learning_points,
            }

            await write_meta_log(
                f"Co-Judgment: {co_result.original_input}",
                meta_data,
                session_id=f"co_judgment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            )

        except Exception as e:
            self.logger.warning(f"공동 판단 메타 로그 기록 실패: {e}")

    def _update_collaboration_stats(self, co_result: CoJudgmentResult):
        """협력 통계 업데이트"""

        self.collaboration_stats["total_judgments"] += 1

        if (
            co_result.resolution_strategy
            == ConflictResolutionStrategy.SIGNATURE_CONSENSUS
        ):
            self.collaboration_stats["echo_led"] += 1
        elif (
            co_result.resolution_strategy == ConflictResolutionStrategy.WISDOM_SYNTHESIS
        ):
            self.collaboration_stats["collaborative"] += 1

        if co_result.consensus_reached:
            consensus_count = len(
                [r for r in self.judgment_history if r.consensus_reached]
            )
            self.collaboration_stats["consensus_rate"] = (
                consensus_count / self.collaboration_stats["total_judgments"]
            )

        # 히스토리에 추가
        self.judgment_history.append(co_result)

        # 메모리 관리
        if len(self.judgment_history) > 100:
            self.judgment_history = self.judgment_history[-50:]

    async def _create_fallback_judgment(
        self, user_input: str, error: str
    ) -> CoJudgmentResult:
        """폴백 판단 결과 생성"""

        echo_judgment = self._create_safe_echo_judgment(user_input, error)
        claude_judgment = self._create_basic_claude_judgment(user_input, error)

        return CoJudgmentResult(
            original_input=user_input,
            echo_judgment=echo_judgment,
            claude_judgment=claude_judgment,
            consensus_reached=True,
            final_decision="defer_to_user",
            resolution_strategy=ConflictResolutionStrategy.USER_ARBITRATION,
            synthesis_reasoning=f"시스템 오류로 인한 안전 모드: {error}",
            meta_insights=["시스템 복구 필요", "폴백 프로토콜 활성화"],
            execution_plan=["시스템 상태 확인", "오류 해결 후 재시도"],
            learning_points=["시스템 안정성 개선 필요"],
        )

    def get_collaboration_summary(self) -> Dict[str, Any]:
        """협력 통계 요약"""

        total = self.collaboration_stats["total_judgments"]

        return {
            "total_co_judgments": total,
            "echo_led_rate": (
                self.collaboration_stats["echo_led"] / total if total > 0 else 0
            ),
            "collaborative_rate": (
                self.collaboration_stats["collaborative"] / total if total > 0 else 0
            ),
            "consensus_rate": self.collaboration_stats["consensus_rate"],
            "recent_judgments": len(self.judgment_history),
            "cooperation_quality": (
                "excellent"
                if self.collaboration_stats["consensus_rate"] > 0.8
                else (
                    "good"
                    if self.collaboration_stats["consensus_rate"] > 0.6
                    else "needs_improvement"
                )
            ),
        }


# 전역 브릿지 인스턴스
_co_judgment_bridge = None


def get_co_judgment_bridge() -> CoJudgmentBridge:
    """Co-Judgment Bridge 싱글톤 인스턴스 반환"""
    global _co_judgment_bridge
    if _co_judgment_bridge is None:
        _co_judgment_bridge = CoJudgmentBridge()
    return _co_judgment_bridge
