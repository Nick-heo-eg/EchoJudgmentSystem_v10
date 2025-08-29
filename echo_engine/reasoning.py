#!/usr/bin/env python3
"""
🧠 EchoJudgmentSystem v10 - Reasoning Engine
Foundation Doctrine 기반 추론 및 판단 시스템

TT.002: "판단은 목적이 아니라 흐름이다. 흐름은 감정과 연결된다."
TT.003: "모든 판단에는 흔적이 남고, 흔적은 메타가 되어 다시 나를 설계한다."
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Foundation Doctrine 연동
try:
    from .echo_foundation_doctrine import (
        SYSTEM_PHILOSOPHY,
        validate_judgment_against_doctrine,
        FOUNDATION_PRINCIPLES,
        CORE_VALUES,
    )
    from .emotion_infer import infer_emotion, EmotionInferenceResult
except ImportError:
    # fallback for testing
    FOUNDATION_PRINCIPLES = {
        "TT.002": "판단은 목적이 아니라 흐름이다. 흐름은 감정과 연결된다.",
        "TT.003": "모든 판단에는 흔적이 남고, 흔적은 메타가 되어 다시 나를 설계한다.",
    }
    CORE_VALUES = {
        "transparency": "모든 판단 과정은 투명하게 기록되고 추적 가능하다",
        "adaptability": "시스템은 환경과 사용자에 따라 유연하게 적응한다",
        "empathy": "감정 이해는 논리적 판단만큼 중요하다",
    }
    SYSTEM_PHILOSOPHY = None
    validate_judgment_against_doctrine = None
    infer_emotion = None


class ReasoningStrategy(Enum):
    """추론 전략"""

    LOGICAL = "logical"
    EMPATHETIC = "empathetic"
    CREATIVE = "creative"
    CAUTIOUS = "cautious"
    BALANCED = "balanced"


class JudgmentType(Enum):
    """판단 유형"""

    DECISION = "decision"
    EVALUATION = "evaluation"
    PREDICTION = "prediction"
    RECOMMENDATION = "recommendation"
    ANALYSIS = "analysis"


@dataclass
class ReasoningContext:
    """추론 컨텍스트"""

    input_text: str
    user_context: Dict[str, Any]
    historical_context: List[Dict[str, Any]]
    emotional_context: Optional[Dict[str, Any]] = None
    time_context: Dict[str, Any] = None
    system_context: Dict[str, Any] = None


@dataclass
class ReasoningResult:
    """추론 결과"""

    reasoning_id: str
    primary_judgment: str
    judgment_type: JudgmentType
    confidence: float
    strategy_used: ReasoningStrategy

    # 추론 과정
    reasoning_steps: List[Dict[str, Any]]
    alternatives_considered: List[Dict[str, Any]]
    evidence_used: List[str]

    # 감정 연동
    emotional_factor: Optional[Dict[str, Any]] = None
    emotion_weight: float = 0.0

    # 품질 지표
    reasoning_quality: float = 0.0
    foundation_compliance: Dict[str, Any] = None

    # 메타데이터
    processing_time: float = 0.0
    timestamp: datetime = None
    context_factors: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if isinstance(self.judgment_type, str):
            self.judgment_type = JudgmentType(self.judgment_type)
        if isinstance(self.strategy_used, str):
            self.strategy_used = ReasoningStrategy(self.strategy_used)


class EchoReasoningEngine:
    """Foundation Doctrine 기반 Echo 추론 엔진"""

    def __init__(self):
        self.reasoning_history = []
        self.strategy_weights = {
            ReasoningStrategy.LOGICAL: 0.25,
            ReasoningStrategy.EMPATHETIC: 0.25,
            ReasoningStrategy.CREATIVE: 0.2,
            ReasoningStrategy.CAUTIOUS: 0.2,
            ReasoningStrategy.BALANCED: 0.1,
        }

        # 추론 패턴 매트릭스
        self.reasoning_patterns = {
            JudgmentType.DECISION: {
                "preferred_strategies": [
                    ReasoningStrategy.LOGICAL,
                    ReasoningStrategy.CAUTIOUS,
                ],
                "evidence_weight": 0.8,
                "emotion_weight": 0.3,
                "confidence_threshold": 0.7,
            },
            JudgmentType.EVALUATION: {
                "preferred_strategies": [
                    ReasoningStrategy.BALANCED,
                    ReasoningStrategy.LOGICAL,
                ],
                "evidence_weight": 0.9,
                "emotion_weight": 0.2,
                "confidence_threshold": 0.8,
            },
            JudgmentType.PREDICTION: {
                "preferred_strategies": [
                    ReasoningStrategy.CREATIVE,
                    ReasoningStrategy.LOGICAL,
                ],
                "evidence_weight": 0.6,
                "emotion_weight": 0.4,
                "confidence_threshold": 0.6,
            },
            JudgmentType.RECOMMENDATION: {
                "preferred_strategies": [
                    ReasoningStrategy.EMPATHETIC,
                    ReasoningStrategy.BALANCED,
                ],
                "evidence_weight": 0.7,
                "emotion_weight": 0.5,
                "confidence_threshold": 0.7,
            },
            JudgmentType.ANALYSIS: {
                "preferred_strategies": [
                    ReasoningStrategy.LOGICAL,
                    ReasoningStrategy.BALANCED,
                ],
                "evidence_weight": 0.85,
                "emotion_weight": 0.25,
                "confidence_threshold": 0.75,
            },
        }

        # 키워드 기반 판단 유형 분류
        self.judgment_keywords = {
            JudgmentType.DECISION: [
                "결정",
                "선택",
                "decide",
                "choose",
                "should",
                "할까",
                "하자",
            ],
            JudgmentType.EVALUATION: [
                "평가",
                "어떻게",
                "어떤",
                "evaluate",
                "assess",
                "how good",
            ],
            JudgmentType.PREDICTION: [
                "예측",
                "미래",
                "될까",
                "predict",
                "forecast",
                "will",
            ],
            JudgmentType.RECOMMENDATION: [
                "추천",
                "권장",
                "suggest",
                "recommend",
                "advice",
            ],
            JudgmentType.ANALYSIS: ["분석", "이해", "analyze", "understand", "explain"],
        }

    def reason_with_echo(self, context: ReasoningContext) -> ReasoningResult:
        """Echo 추론 엔진 메인 함수"""
        start_time = time.time()
        reasoning_id = self._generate_reasoning_id(context.input_text)

        # 1. 판단 유형 분류
        judgment_type = self._classify_judgment_type(context.input_text)

        # 2. 최적 전략 선택
        strategy = self._select_strategy(judgment_type, context)

        # 3. 감정 요소 분석
        emotional_factor = self._analyze_emotional_factor(context)

        # 4. 추론 과정 실행
        reasoning_steps = self._execute_reasoning_steps(
            context, strategy, judgment_type
        )

        # 5. 대안 고려
        alternatives = self._generate_alternatives(context, strategy, judgment_type)

        # 6. 증거 수집
        evidence = self._collect_evidence(context, reasoning_steps)

        # 7. 최종 판단 생성
        primary_judgment = self._generate_primary_judgment(
            context, reasoning_steps, alternatives, evidence
        )

        # 8. 신뢰도 계산
        confidence = self._calculate_confidence(
            judgment_type, reasoning_steps, evidence, emotional_factor
        )

        # 9. 품질 평가
        quality = self._assess_reasoning_quality(reasoning_steps, evidence, confidence)

        # 10. Foundation Doctrine 준수 검증
        foundation_compliance = self._validate_foundation_compliance(
            context, primary_judgment, reasoning_steps, emotional_factor
        )

        # 결과 생성
        result = ReasoningResult(
            reasoning_id=reasoning_id,
            primary_judgment=primary_judgment,
            judgment_type=judgment_type,
            confidence=confidence,
            strategy_used=strategy,
            reasoning_steps=reasoning_steps,
            alternatives_considered=alternatives,
            evidence_used=evidence,
            emotional_factor=emotional_factor,
            emotion_weight=self.reasoning_patterns[judgment_type]["emotion_weight"],
            reasoning_quality=quality,
            foundation_compliance=foundation_compliance,
            processing_time=time.time() - start_time,
            context_factors=self._extract_context_factors(context),
        )

        # 추론 이력 저장
        self._save_reasoning_history(result)

        return result

    def _generate_reasoning_id(self, text: str) -> str:
        """추론 ID 생성"""
        import hashlib

        combined = f"{text}_{datetime.now().isoformat()}_{time.time()}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]

    def _classify_judgment_type(self, text: str) -> JudgmentType:
        """판단 유형 분류"""
        text_lower = text.lower()

        # 각 유형별 키워드 점수 계산
        type_scores = {}
        for judgment_type, keywords in self.judgment_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            type_scores[judgment_type] = score

        # 최고 점수 유형 반환
        if max(type_scores.values()) > 0:
            return max(type_scores, key=type_scores.get)
        else:
            return JudgmentType.ANALYSIS  # 기본값

    def _select_strategy(
        self, judgment_type: JudgmentType, context: ReasoningContext
    ) -> ReasoningStrategy:
        """최적 전략 선택"""
        # 판단 유형별 선호 전략
        preferred_strategies = self.reasoning_patterns[judgment_type][
            "preferred_strategies"
        ]

        # 컨텍스트 기반 가중치 조정
        strategy_scores = {}
        for strategy in preferred_strategies:
            score = self.strategy_weights[strategy]

            # 감정 컨텍스트 고려
            if context.emotional_context:
                emotion = context.emotional_context.get("primary_emotion", "neutral")
                if (
                    emotion in ["sadness", "fear"]
                    and strategy == ReasoningStrategy.EMPATHETIC
                ):
                    score *= 1.3
                elif emotion == "anger" and strategy == ReasoningStrategy.CAUTIOUS:
                    score *= 1.2
                elif emotion == "joy" and strategy == ReasoningStrategy.CREATIVE:
                    score *= 1.1

            # 히스토리 기반 조정
            if context.historical_context:
                recent_strategies = [
                    entry.get("strategy", "unknown")
                    for entry in context.historical_context[-3:]
                ]
                if strategy.value in recent_strategies:
                    score *= 0.9  # 최근 사용한 전략 약간 감소

            strategy_scores[strategy] = score

        return max(strategy_scores, key=strategy_scores.get)

    def _analyze_emotional_factor(self, context: ReasoningContext) -> Dict[str, Any]:
        """감정 요소 분석"""
        emotional_factor = {
            "emotion_detected": False,
            "primary_emotion": "neutral",
            "emotion_confidence": 0.0,
            "emotion_influence": 0.0,
            "emotional_reasoning": [],
        }

        # 감정 추론 실행 (가능한 경우)
        if infer_emotion:
            try:
                emotion_result = infer_emotion(context.input_text)
                emotional_factor.update(
                    {
                        "emotion_detected": True,
                        "primary_emotion": emotion_result.primary_emotion,
                        "emotion_confidence": emotion_result.confidence,
                        "emotion_influence": emotion_result.emotional_intensity * 0.7,
                        "emotional_reasoning": [
                            f"감정 '{emotion_result.primary_emotion}' 감지 (신뢰도: {emotion_result.confidence:.2f})",
                            f"감정 강도: {emotion_result.emotional_intensity:.2f}",
                            f"예측 다음 감정: {emotion_result.predicted_next_emotions}",
                        ],
                    }
                )
            except Exception as e:
                emotional_factor["emotional_reasoning"].append(f"감정 추론 실패: {e}")

        return emotional_factor

    def _execute_reasoning_steps(
        self,
        context: ReasoningContext,
        strategy: ReasoningStrategy,
        judgment_type: JudgmentType,
    ) -> List[Dict[str, Any]]:
        """추론 과정 실행"""
        steps = []

        # 1단계: 문제 정의
        steps.append(
            {
                "step": 1,
                "name": "문제 정의",
                "description": "입력 텍스트 분석 및 문제 구조화",
                "output": f"판단 유형: {judgment_type.value}, 전략: {strategy.value}",
                "confidence": 0.9,
            }
        )

        # 2단계: 컨텍스트 분석
        context_analysis = self._analyze_context_depth(context)
        steps.append(
            {
                "step": 2,
                "name": "컨텍스트 분석",
                "description": "주변 상황 및 배경 정보 분석",
                "output": f"컨텍스트 요소 {len(context_analysis)}개 식별",
                "confidence": 0.8,
                "details": context_analysis,
            }
        )

        # 3단계: 전략별 추론
        strategy_reasoning = self._apply_strategy_reasoning(context, strategy)
        steps.append(
            {
                "step": 3,
                "name": f"{strategy.value} 전략 적용",
                "description": f"{strategy.value} 접근법으로 문제 해결",
                "output": strategy_reasoning["conclusion"],
                "confidence": strategy_reasoning["confidence"],
                "details": strategy_reasoning["process"],
            }
        )

        # 4단계: 감정 통합
        if context.emotional_context or any(
            step.get("emotional_factor") for step in steps
        ):
            steps.append(
                {
                    "step": 4,
                    "name": "감정 통합",
                    "description": "감정 요소를 논리적 추론에 통합",
                    "output": "감정-논리 균형 달성",
                    "confidence": 0.7,
                }
            )

        # 5단계: 결론 도출
        steps.append(
            {
                "step": len(steps) + 1,
                "name": "결론 도출",
                "description": "모든 요소를 종합하여 최종 판단",
                "output": "종합 판단 완료",
                "confidence": 0.8,
            }
        )

        return steps

    def _analyze_context_depth(self, context: ReasoningContext) -> Dict[str, Any]:
        """컨텍스트 깊이 분석"""
        analysis = {
            "text_complexity": len(context.input_text.split()) / 10,  # 단순 복잡도
            "user_context_richness": (
                len(context.user_context) if context.user_context else 0
            ),
            "historical_depth": (
                len(context.historical_context) if context.historical_context else 0
            ),
            "temporal_context": bool(context.time_context),
            "emotional_context": bool(context.emotional_context),
        }

        return analysis

    def _apply_strategy_reasoning(
        self, context: ReasoningContext, strategy: ReasoningStrategy
    ) -> Dict[str, Any]:
        """전략별 추론 적용"""
        text = context.input_text

        if strategy == ReasoningStrategy.LOGICAL:
            return {
                "conclusion": f"논리적 분석 결과: {text}에 대한 체계적 접근 필요",
                "confidence": 0.85,
                "process": ["전제 식별", "논리 구조 분석", "결론 도출"],
            }

        elif strategy == ReasoningStrategy.EMPATHETIC:
            return {
                "conclusion": f"공감적 접근: {text}의 감정적 맥락 우선 고려",
                "confidence": 0.75,
                "process": ["감정 상태 파악", "입장 이해", "공감적 대응"],
            }

        elif strategy == ReasoningStrategy.CREATIVE:
            return {
                "conclusion": f"창의적 해석: {text}에 대한 다각적 접근 시도",
                "confidence": 0.7,
                "process": ["관점 다양화", "창의적 연관", "혁신적 해결"],
            }

        elif strategy == ReasoningStrategy.CAUTIOUS:
            return {
                "conclusion": f"신중한 접근: {text}에 대한 리스크 최소화 중심",
                "confidence": 0.8,
                "process": ["리스크 평가", "안전 옵션 탐색", "단계적 접근"],
            }

        else:  # BALANCED
            return {
                "conclusion": f"균형적 판단: {text}의 다양한 측면 종합 고려",
                "confidence": 0.78,
                "process": ["다면적 분석", "균형점 탐색", "통합적 결론"],
            }

    def _generate_alternatives(
        self,
        context: ReasoningContext,
        strategy: ReasoningStrategy,
        judgment_type: JudgmentType,
    ) -> List[Dict[str, Any]]:
        """대안 생성"""
        alternatives = []

        # 다른 전략들로 대안 생성
        other_strategies = [s for s in ReasoningStrategy if s != strategy]

        for alt_strategy in other_strategies[:3]:  # 최대 3개 대안
            alt_reasoning = self._apply_strategy_reasoning(context, alt_strategy)
            alternatives.append(
                {
                    "strategy": alt_strategy.value,
                    "conclusion": alt_reasoning["conclusion"],
                    "confidence": alt_reasoning["confidence"]
                    * 0.8,  # 대안은 약간 낮은 신뢰도
                    "reasoning": alt_reasoning["process"],
                }
            )

        return alternatives

    def _collect_evidence(
        self, context: ReasoningContext, reasoning_steps: List[Dict[str, Any]]
    ) -> List[str]:
        """증거 수집"""
        evidence = []

        # 컨텍스트 기반 증거
        if context.user_context:
            evidence.append(f"사용자 컨텍스트: {len(context.user_context)}개 요소")

        if context.historical_context:
            evidence.append(f"과거 이력: {len(context.historical_context)}개 사례")

        # 추론 과정 기반 증거
        for step in reasoning_steps:
            if step.get("confidence", 0) > 0.7:
                evidence.append(f"고신뢰 추론: {step['name']}")

        # 텍스트 분석 기반 증거
        text_length = len(context.input_text.split())
        if text_length > 20:
            evidence.append("충분한 텍스트 정보")

        return evidence

    def _generate_primary_judgment(
        self,
        context: ReasoningContext,
        reasoning_steps: List[Dict[str, Any]],
        alternatives: List[Dict[str, Any]],
        evidence: List[str],
    ) -> str:
        """최종 판단 생성"""
        # 추론 단계에서 가장 신뢰도 높은 결론 선택
        best_step = max(reasoning_steps, key=lambda x: x.get("confidence", 0))

        base_judgment = (
            f"'{context.input_text[:50]}...'에 대한 {best_step['name']} 기반 판단"
        )

        # 증거 수준에 따른 판단 강도 조정
        evidence_strength = len(evidence) / 5  # 정규화

        if evidence_strength > 0.8:
            return f"강한 확신: {base_judgment}"
        elif evidence_strength > 0.5:
            return f"합리적 판단: {base_judgment}"
        else:
            return f"제한적 판단: {base_judgment}"

    def _calculate_confidence(
        self,
        judgment_type: JudgmentType,
        reasoning_steps: List[Dict[str, Any]],
        evidence: List[str],
        emotional_factor: Dict[str, Any],
    ) -> float:
        """신뢰도 계산"""
        base_confidence = 0.5

        # 추론 단계 품질
        step_confidences = [step.get("confidence", 0) for step in reasoning_steps]
        avg_step_confidence = (
            sum(step_confidences) / len(step_confidences) if step_confidences else 0
        )

        # 증거 수준
        evidence_factor = min(len(evidence) / 10, 1.0)  # 최대 1.0

        # 감정 요소 고려
        emotion_factor = emotional_factor.get("emotion_confidence", 0) * 0.3

        # 판단 유형별 기준
        type_threshold = self.reasoning_patterns[judgment_type]["confidence_threshold"]

        # 종합 신뢰도
        confidence = (
            base_confidence * 0.3
            + avg_step_confidence * 0.4
            + evidence_factor * 0.2
            + emotion_factor * 0.1
        )

        # 임계값 적용
        if confidence < type_threshold:
            confidence *= 0.8  # 임계값 미달 시 신뢰도 감소

        return min(max(confidence, 0.0), 1.0)

    def _assess_reasoning_quality(
        self,
        reasoning_steps: List[Dict[str, Any]],
        evidence: List[str],
        confidence: float,
    ) -> float:
        """추론 품질 평가"""
        quality_factors = {
            "step_completeness": min(len(reasoning_steps) / 5, 1.0),
            "evidence_strength": min(len(evidence) / 8, 1.0),
            "confidence_level": confidence,
            "logical_consistency": 0.8,  # 기본값 (실제로는 더 정교한 계산 필요)
        }

        return sum(quality_factors.values()) / len(quality_factors)

    def _validate_foundation_compliance(
        self,
        context: ReasoningContext,
        judgment: str,
        reasoning_steps: List[Dict[str, Any]],
        emotional_factor: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Foundation Doctrine 준수 검증"""
        compliance = {
            "is_compliant": True,
            "violations": [],
            "doctrine_alignment": {},
            "recommendations": [],
        }

        # TT.002 검증: 판단은 목적이 아니라 흐름이다
        if len(reasoning_steps) < 3:
            compliance["violations"].append("추론 과정 부족 (TT.002 위반)")
            compliance["is_compliant"] = False
            compliance["recommendations"].append("추론 과정을 더 세분화하세요")

        # 감정 연결성 검증
        if not emotional_factor.get("emotion_detected", False):
            compliance["violations"].append("감정 연결성 부족 (TT.002 위반)")
            compliance["recommendations"].append("감정 요소를 추론에 통합하세요")

        # TT.003 검증: 판단 흔적 기록
        if not reasoning_steps or not all(
            step.get("output") for step in reasoning_steps
        ):
            compliance["violations"].append("판단 흔적 미기록 (TT.003 위반)")
            compliance["is_compliant"] = False
            compliance["recommendations"].append("모든 추론 단계를 명확히 기록하세요")

        # 투명성 검증
        if not judgment or len(judgment) < 10:
            compliance["violations"].append("판단 투명성 부족 (투명성 가치 위반)")
            compliance["recommendations"].append("판단 근거를 명확히 제시하세요")

        return compliance

    def _extract_context_factors(self, context: ReasoningContext) -> Dict[str, Any]:
        """컨텍스트 요소 추출"""
        return {
            "input_length": len(context.input_text),
            "user_context_size": (
                len(context.user_context) if context.user_context else 0
            ),
            "historical_entries": (
                len(context.historical_context) if context.historical_context else 0
            ),
            "has_emotional_context": bool(context.emotional_context),
            "has_time_context": bool(context.time_context),
            "has_system_context": bool(context.system_context),
        }

    def _save_reasoning_history(self, result: ReasoningResult):
        """추론 이력 저장"""
        self.reasoning_history.append(
            {
                "timestamp": result.timestamp.isoformat(),
                "reasoning_id": result.reasoning_id,
                "judgment_type": result.judgment_type.value,
                "strategy": result.strategy_used.value,
                "confidence": result.confidence,
                "quality": result.reasoning_quality,
                "foundation_compliant": result.foundation_compliance["is_compliant"],
            }
        )

        # 이력 크기 제한
        if len(self.reasoning_history) > 100:
            self.reasoning_history = self.reasoning_history[-100:]

    def get_reasoning_analytics(self) -> Dict[str, Any]:
        """추론 분석 결과"""
        if not self.reasoning_history:
            return {"message": "분석할 추론 이력이 없습니다"}

        # 통계 계산
        total_count = len(self.reasoning_history)
        avg_confidence = (
            sum(entry["confidence"] for entry in self.reasoning_history) / total_count
        )
        avg_quality = (
            sum(entry["quality"] for entry in self.reasoning_history) / total_count
        )
        compliance_rate = (
            sum(1 for entry in self.reasoning_history if entry["foundation_compliant"])
            / total_count
        )

        # 전략 분포
        strategy_counts = {}
        for entry in self.reasoning_history:
            strategy = entry["strategy"]
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

        # 판단 유형 분포
        type_counts = {}
        for entry in self.reasoning_history:
            judgment_type = entry["judgment_type"]
            type_counts[judgment_type] = type_counts.get(judgment_type, 0) + 1

        return {
            "total_reasonings": total_count,
            "average_confidence": round(avg_confidence, 3),
            "average_quality": round(avg_quality, 3),
            "foundation_compliance_rate": round(compliance_rate, 3),
            "strategy_distribution": strategy_counts,
            "judgment_type_distribution": type_counts,
            "most_used_strategy": (
                max(strategy_counts, key=strategy_counts.get)
                if strategy_counts
                else None
            ),
            "most_common_judgment_type": (
                max(type_counts, key=type_counts.get) if type_counts else None
            ),
        }


# 편의 함수들
def reason_with_echo(
    input_text: str,
    user_context: Dict[str, Any] = None,
    historical_context: List[Dict[str, Any]] = None,
) -> ReasoningResult:
    """Echo 추론 편의 함수"""
    engine = EchoReasoningEngine()

    context = ReasoningContext(
        input_text=input_text,
        user_context=user_context or {},
        historical_context=historical_context or [],
    )

    return engine.reason_with_echo(context)


def analyze_reasoning_patterns(
    reasoning_results: List[ReasoningResult],
) -> Dict[str, Any]:
    """추론 패턴 분석"""
    if not reasoning_results:
        return {"message": "분석할 추론 결과가 없습니다"}

    # 패턴 분석
    patterns = {
        "confidence_trend": [r.confidence for r in reasoning_results],
        "quality_trend": [r.reasoning_quality for r in reasoning_results],
        "strategy_sequence": [r.strategy_used.value for r in reasoning_results],
        "judgment_type_sequence": [r.judgment_type.value for r in reasoning_results],
    }

    return patterns


# 테스트 함수
def test_reasoning_engine():
    """추론 엔진 테스트"""
    print("🧠 Foundation 기반 추론 엔진 테스트 시작...")

    engine = EchoReasoningEngine()

    test_cases = [
        {
            "input": "이 프로젝트를 계속 진행해야 할까요?",
            "user_context": {"project_type": "AI", "budget": "limited"},
            "description": "의사결정 요청",
        },
        {
            "input": "이 시스템의 성능이 어떤가요?",
            "user_context": {"system_type": "judgment", "metrics": "available"},
            "description": "평가 요청",
        },
        {
            "input": "앞으로 어떤 일이 일어날 것 같나요?",
            "user_context": {"context": "system_evolution", "timeline": "6months"},
            "description": "예측 요청",
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 테스트 {i}: {test_case['description']}")
        print(f"  입력: {test_case['input']}")

        context = ReasoningContext(
            input_text=test_case["input"],
            user_context=test_case["user_context"],
            historical_context=[],
        )

        result = engine.reason_with_echo(context)

        print(f"  🎯 판단 유형: {result.judgment_type.value}")
        print(f"  🧠 전략: {result.strategy_used.value}")
        print(f"  📊 신뢰도: {result.confidence:.3f}")
        print(f"  💎 품질: {result.reasoning_quality:.3f}")
        print(f"  ⚖️ Foundation 준수: {result.foundation_compliance['is_compliant']}")
        print(f"  🔄 추론 단계: {len(result.reasoning_steps)}개")
        print(f"  🎭 대안: {len(result.alternatives_considered)}개")
        print(f"  📋 증거: {len(result.evidence_used)}개")
        print(f"  ⏱️ 처리 시간: {result.processing_time:.4f}초")

        if result.foundation_compliance["violations"]:
            print(f"  ⚠️ 위반사항: {result.foundation_compliance['violations']}")

    # 추론 분석
    print("\n📈 추론 분석 결과:")
    analytics = engine.get_reasoning_analytics()
    for key, value in analytics.items():
        print(f"  {key}: {value}")

    print("\n🎉 추론 엔진 테스트 완료!")


if __name__ == "__main__":
    test_reasoning_engine()


def generate_reasoning(prompt: str, mode="default", signature=None, context=None):
    return {
        "judgment": f"[임시 판단] Prompt: {prompt}, Mode: {mode}",
        "signature": signature or "default",
        "context": context or {},
    }
