#!/usr/bin/env python3
"""
🎯 Strategy Picker v2.0 - 코사인 유사도 기반 전략 선택 엔진

감정 상태와 상황 컨텍스트를 분석하여 최적의 전략을 선택하는 모듈.
36개 감정×전략 조합 템플릿과 연동하여 fallback 판단의 정확성을 높입니다.

GPT 스타일 보강 사항:
1. 코사인 유사도 기반 전략 프레임 정확도 향상
2. 감정 confidence 낮을 경우 예외 전략 부가 출력
3. 임베딩 기반 의미론적 전략 매칭
4. 동적 전략 적응 및 학습 강화

핵심 역할:
1. 감정 상태 기반 전략 매칭 (v2.0 강화)
2. 컨텍스트 분석을 통한 전략 가중치 계산
3. 입력 텍스트 패턴 기반 전략 추천
4. 코사인 유사도 기반 정확도 보강
5. 동적 전략 적응 및 학습
"""

import re
import random
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# 임베딩 기반 유사도 계산을 위한 선택적 import
try:
    from sentence_transformers import SentenceTransformer

    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False


class StrategyType(Enum):
    """전략 타입 정의"""

    ADAPT = "adapt"  # 적응: 상황에 맞춰 유연하게 변화
    CONFRONT = "confront"  # 대응: 문제에 직면하여 해결
    RETREAT = "retreat"  # 후퇴: 일시적으로 물러나서 재정비
    ANALYZE = "analyze"  # 분석: 상황을 깊이 파악하고 이해
    INITIATE = "initiate"  # 주도: 적극적으로 변화를 이끔
    HARMONIZE = "harmonize"  # 조화: 균형과 화합을 추구


@dataclass
class StrategyContext:
    """전략 선택 컨텍스트"""

    input_text: str
    emotion: str = "neutral"
    urgency_level: float = 0.5
    complexity_level: float = 0.5
    relationship_context: bool = False
    problem_solving_context: bool = False
    creative_context: bool = False
    support_needed: bool = False
    confidence_level: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyRecommendation:
    """전략 추천 결과 (v2.0 강화)"""

    primary_strategy: StrategyType
    secondary_strategy: Optional[StrategyType]
    confidence: float
    reasoning: List[str]
    emotion_match_score: float
    context_match_score: float
    pattern_match_score: float
    total_score: float
    # v2.0 추가 필드
    cosine_similarity_score: float = 0.0
    low_confidence_alternatives: List[StrategyType] = field(default_factory=list)
    semantic_match_used: bool = False
    embedding_quality: float = 0.0


class StrategyPicker:
    """🎯 전략 선택 엔진 v2.0 (코사인 유사도 기반 강화)"""

    def __init__(self):
        global EMBEDDING_AVAILABLE

        self.version = "2.0.0-cosine"

        # 임베딩 모델 초기화 (v2.0 추가)
        self.embedding_model = None
        if EMBEDDING_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer(
                    "BM-K/KoSimCSE-roberta-multitask"
                )
                print("✅ StrategyPicker v2.0 - 코사인 유사도 모델 로드 완료")
            except Exception as e:
                print(f"⚠️ 임베딩 모델 로드 실패: {e}")
                self.embedding_model = None
                # 임베딩 모델 로드 실패 시 EMBEDDING_AVAILABLE을 False로 재설정
                EMBEDDING_AVAILABLE = False

        # 전략별 의미론적 레퍼런스 문장들 (v2.0 추가)
        self.strategy_semantic_references = self._build_strategy_references()

        # 전략 선택 통계
        self.selection_stats = {
            "total_selections": 0,
            "strategy_usage": {},
            "emotion_strategy_pairs": {},
            "success_rate_by_strategy": {},
            "context_pattern_usage": {},
        }

        # 감정-전략 매칭 규칙
        self.emotion_strategy_mappings = self._initialize_emotion_strategy_mappings()

        # 컨텍스트 패턴 규칙
        self.context_patterns = self._initialize_context_patterns()

        # 텍스트 패턴 매칭 규칙
        self.text_patterns = self._initialize_text_patterns()

        print(f"🎯 Strategy Picker v{self.version} 초기화 완료")
        print(f"   임베딩 기반 유사도: {'✅' if EMBEDDING_AVAILABLE else '❌'}")

    def _build_strategy_references(self) -> Dict[str, List[str]]:
        """전략별 의미론적 레퍼런스 문장 구성 (v2.0 추가)"""
        return {
            "adapt": [
                "상황에 맞게 유연하게 대응하겠습니다",
                "변화하는 환경에 적응해보겠습니다",
                "상황을 보며 조절해나가겠습니다",
                "융통성 있게 접근해보겠습니다",
            ],
            "confront": [
                "문제에 정면으로 맞서겠습니다",
                "직접적으로 해결해보겠습니다",
                "과감하게 도전해보겠습니다",
                "적극적으로 대응하겠습니다",
            ],
            "retreat": [
                "잠시 물러서서 재정비하겠습니다",
                "한 걸음 뒤로 물러나 생각해보겠습니다",
                "여유를 갖고 차분히 접근하겠습니다",
                "휴식을 취하며 회복하겠습니다",
            ],
            "analyze": [
                "상황을 자세히 분석해보겠습니다",
                "깊이 있게 파악해보겠습니다",
                "체계적으로 검토해보겠습니다",
                "논리적으로 접근해보겠습니다",
            ],
            "initiate": [
                "적극적으로 시작해보겠습니다",
                "주도적으로 이끌어나가겠습니다",
                "새로운 변화를 만들어보겠습니다",
                "능동적으로 추진하겠습니다",
            ],
            "harmonize": [
                "균형과 조화를 이루어보겠습니다",
                "화합과 협력을 추구하겠습니다",
                "평화롭게 해결해보겠습니다",
                "상호 이해를 바탕으로 접근하겠습니다",
            ],
        }

    def pick_strategy(
        self,
        input_text: str,
        emotion: str = "neutral",
        context: Optional[Dict[str, Any]] = None,
    ) -> StrategyType:
        """🎯 메인 전략 선택 함수 (v2.0 강화)"""

        self.selection_stats["total_selections"] += 1

        # 컨텍스트 분석
        strategy_context = self._analyze_context(input_text, emotion, context or {})

        # 전략 추천 (v2.0 강화된 로직)
        recommendation = self._recommend_strategy_v2(strategy_context)

        # 통계 업데이트
        self._update_selection_stats(recommendation)

        # v2.0: 낮은 신뢰도에 대한 상세 로깅
        if (
            recommendation.confidence < 0.5
            and recommendation.low_confidence_alternatives
        ):
            print(
                f"🎯 전략 선택: {recommendation.primary_strategy.value} (신뢰도: {recommendation.confidence:.2f})"
            )
            print(
                f"   ⚠️ 낮은 신뢰도 - 대안 전략: {[s.value for s in recommendation.low_confidence_alternatives]}"
            )
        else:
            print(
                f"🎯 전략 선택: {recommendation.primary_strategy.value} (신뢰도: {recommendation.confidence:.2f})"
            )

        return recommendation.primary_strategy

    def select(
        self,
        emotion: str,
        confidence: float = 1.0,
        input_text: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """v2.0 강화된 select 메서드 - 감정 confidence가 낮을 경우 예외 전략 부가 출력"""
        global EMBEDDING_AVAILABLE

        # 기본 전략 선택
        primary_strategy = self.pick_strategy(input_text, emotion, context)

        # 낮은 confidence에 대한 대안 전략 생성
        alternatives = []
        fallback_strategy = None

        if confidence < 0.7:  # 낮은 신뢰도
            # 대안 전략들 계산
            detailed_rec = self.get_detailed_recommendation(
                input_text, emotion, context
            )
            alternatives = detailed_rec.low_confidence_alternatives

            # 폴백 전략 (감정이 불분명할 때)
            if confidence < 0.5:
                fallback_strategy = self._get_neutral_fallback_strategy(input_text)

        return {
            "primary_strategy": primary_strategy.value,
            "confidence": confidence,
            "alternatives": [s.value for s in alternatives],
            "fallback_strategy": fallback_strategy.value if fallback_strategy else None,
            "confidence_level": (
                "high"
                if confidence >= 0.7
                else "moderate" if confidence >= 0.5 else "low"
            ),
            "semantic_match_used": EMBEDDING_AVAILABLE
            and self.embedding_model is not None,
        }

    def get_detailed_recommendation(
        self,
        input_text: str,
        emotion: str = "neutral",
        context: Optional[Dict[str, Any]] = None,
    ) -> StrategyRecommendation:
        """상세한 전략 추천 결과 반환 (v2.0 강화)"""

        strategy_context = self._analyze_context(input_text, emotion, context or {})
        return self._recommend_strategy_v2(strategy_context)

    def _analyze_context(
        self, input_text: str, emotion: str, context: Dict[str, Any]
    ) -> StrategyContext:
        """컨텍스트 분석"""

        # 긴급도 분석
        urgency_level = self._analyze_urgency(input_text)

        # 복잡도 분석
        complexity_level = self._analyze_complexity(input_text)

        # 관계 컨텍스트 감지
        relationship_context = self._detect_relationship_context(input_text)

        # 문제 해결 컨텍스트 감지
        problem_solving_context = self._detect_problem_solving_context(input_text)

        # 창의적 컨텍스트 감지
        creative_context = self._detect_creative_context(input_text)

        # 지원 필요 여부 감지
        support_needed = self._detect_support_need(input_text)

        # 신뢰도 수준 추정
        confidence_level = self._estimate_confidence_level(input_text, emotion)

        return StrategyContext(
            input_text=input_text,
            emotion=emotion,
            urgency_level=urgency_level,
            complexity_level=complexity_level,
            relationship_context=relationship_context,
            problem_solving_context=problem_solving_context,
            creative_context=creative_context,
            support_needed=support_needed,
            confidence_level=confidence_level,
            metadata=context,
        )

    def _recommend_strategy(self, context: StrategyContext) -> StrategyRecommendation:
        """전략 추천"""

        strategy_scores = {}
        reasoning = []

        # 1. 감정 기반 점수 계산
        emotion_scores = self._calculate_emotion_based_scores(context.emotion)
        for strategy, score in emotion_scores.items():
            strategy_scores[strategy] = strategy_scores.get(strategy, 0.0) + score

        emotion_match_score = max(emotion_scores.values()) if emotion_scores else 0.0
        reasoning.append(f"감정 '{context.emotion}' 기반 전략 매칭")

        # 2. 컨텍스트 패턴 기반 점수 계산
        context_scores = self._calculate_context_based_scores(context)
        for strategy, score in context_scores.items():
            strategy_scores[strategy] = strategy_scores.get(strategy, 0.0) + score

        context_match_score = max(context_scores.values()) if context_scores else 0.0
        reasoning.append(f"컨텍스트 패턴 분석 적용")

        # 3. 텍스트 패턴 기반 점수 계산
        pattern_scores = self._calculate_text_pattern_scores(context.input_text)
        for strategy, score in pattern_scores.items():
            strategy_scores[strategy] = strategy_scores.get(strategy, 0.0) + score

        pattern_match_score = max(pattern_scores.values()) if pattern_scores else 0.0
        reasoning.append(f"텍스트 패턴 매칭 적용")

        # 4. 최종 전략 선택
        if not strategy_scores:
            # 폴백: 감정에 따른 기본 전략
            primary_strategy = self._get_fallback_strategy(context.emotion)
            secondary_strategy = None
            confidence = 0.4
            reasoning.append("기본 폴백 전략 적용")
        else:
            sorted_strategies = sorted(
                strategy_scores.items(), key=lambda x: x[1], reverse=True
            )

            primary_strategy = StrategyType(sorted_strategies[0][0])
            secondary_strategy = (
                StrategyType(sorted_strategies[1][0])
                if len(sorted_strategies) > 1
                else None
            )

            # 신뢰도 계산 (최고 점수의 정규화된 값)
            max_score = sorted_strategies[0][1]
            total_possible_score = 3.0  # 감정 + 컨텍스트 + 패턴 최대 점수
            confidence = min(max_score / total_possible_score, 1.0)

            reasoning.append(f"최고 점수 전략 선택: {max_score:.2f}")

        total_score = sum(strategy_scores.values())

        return StrategyRecommendation(
            primary_strategy=primary_strategy,
            secondary_strategy=secondary_strategy,
            confidence=confidence,
            reasoning=reasoning,
            emotion_match_score=emotion_match_score,
            context_match_score=context_match_score,
            pattern_match_score=pattern_match_score,
            total_score=total_score,
        )

    def _recommend_strategy_v2(
        self, context: StrategyContext
    ) -> StrategyRecommendation:
        """전략 추천 v2.0 - 코사인 유사도 기반 강화"""
        global EMBEDDING_AVAILABLE

        strategy_scores = {}
        reasoning = []
        cosine_similarity_score = 0.0
        semantic_match_used = False
        embedding_quality = 0.0

        # 1. 기존 감정 기반 점수 계산
        emotion_scores = self._calculate_emotion_based_scores(context.emotion)
        for strategy, score in emotion_scores.items():
            strategy_scores[strategy] = strategy_scores.get(strategy, 0.0) + score

        emotion_match_score = max(emotion_scores.values()) if emotion_scores else 0.0
        reasoning.append(f"감정 '{context.emotion}' 기반 전략 매칭")

        # 2. v2.0 추가: 코사인 유사도 기반 의미론적 매칭
        try:
            if EMBEDDING_AVAILABLE and self.embedding_model:
                similarity_scores, embedding_quality = (
                    self._calculate_cosine_similarity_scores(context.input_text)
                )
                if similarity_scores:
                    semantic_match_used = True
                    cosine_similarity_score = max(similarity_scores.values())
                    for strategy, score in similarity_scores.items():
                        strategy_scores[strategy] = (
                            strategy_scores.get(strategy, 0.0) + score * 0.8
                        )
                    reasoning.append(
                        f"코사인 유사도 기반 의미론적 매칭 (품질: {embedding_quality:.3f})"
                    )
                else:
                    reasoning.append("임베딩 기반 매칭 실패 - 기본 analyze 전략 적용")
                    strategy_scores["analyze"] = (
                        strategy_scores.get("analyze", 0.0) + 0.7
                    )
            else:
                # 임베딩 불가 시 fallback
                if not EMBEDDING_AVAILABLE:
                    reasoning.append("임베딩 모듈 미설치 - 기본 전략 적용")
                else:
                    reasoning.append("임베딩 모델 로드 실패 - 기본 전략 적용")
                strategy_scores["analyze"] = strategy_scores.get("analyze", 0.0) + 0.7
        except ImportError as e:
            print(f"⚠️ 임베딩 모듈 가져오기 실패: {e}")
            reasoning.append("임베딩 모듈 가져오기 실패 - 기본 전략 적용")
            strategy_scores["analyze"] = strategy_scores.get("analyze", 0.0) + 0.7
        except Exception as e:
            print(f"⚠️ 임베딩 기반 전략 추천 실패: {e}")
            reasoning.append("임베딩 예외 발생 - 기본 전략 적용")
            strategy_scores["analyze"] = strategy_scores.get("analyze", 0.0) + 0.7

        # 3. 기존 컨텍스트 및 패턴 점수 계산
        context_scores = self._calculate_context_based_scores(context)
        for strategy, score in context_scores.items():
            strategy_scores[strategy] = strategy_scores.get(strategy, 0.0) + score

        context_match_score = max(context_scores.values()) if context_scores else 0.0
        reasoning.append(f"컨텍스트 패턴 분석 적용")

        pattern_scores = self._calculate_text_pattern_scores(context.input_text)
        for strategy, score in pattern_scores.items():
            strategy_scores[strategy] = strategy_scores.get(strategy, 0.0) + score

        pattern_match_score = max(pattern_scores.values()) if pattern_scores else 0.0
        reasoning.append(f"텍스트 패턴 매칭 적용")

        # 4. 최종 전략 선택
        if not strategy_scores:
            # 폴백: 감정에 따른 기본 전략
            primary_strategy = self._get_fallback_strategy(context.emotion)
            secondary_strategy = None
            confidence = 0.4
            reasoning.append("기본 폴백 전략 적용")
            low_confidence_alternatives = [StrategyType.ADAPT, StrategyType.ANALYZE]
        else:
            sorted_strategies = sorted(
                strategy_scores.items(), key=lambda x: x[1], reverse=True
            )

            primary_strategy = StrategyType(sorted_strategies[0][0])
            secondary_strategy = (
                StrategyType(sorted_strategies[1][0])
                if len(sorted_strategies) > 1
                else None
            )

            # v2.0 강화된 신뢰도 계산
            max_score = sorted_strategies[0][1]
            total_possible_score = (
                4.0 if semantic_match_used else 3.0
            )  # 감정 + 코사인 + 컨텍스트 + 패턴
            confidence = min(max_score / total_possible_score, 1.0)

            # 코사인 유사도가 사용된 경우 신뢰도 보정
            if semantic_match_used and embedding_quality > 0.7:
                confidence = min(confidence * 1.1, 1.0)  # 10% 보너스

            reasoning.append(f"최고 점수 전략 선택: {max_score:.2f}")

            # v2.0: 낮은 신뢰도 대안 전략 생성
            low_confidence_alternatives = []
            if confidence < 0.6:
                # 상위 3개 전략을 대안으로 제공
                for strategy_name, _ in sorted_strategies[1:4]:
                    try:
                        alt_strategy = StrategyType(strategy_name)
                        if alt_strategy != primary_strategy:
                            low_confidence_alternatives.append(alt_strategy)
                    except ValueError:
                        continue

        total_score = sum(strategy_scores.values())

        return StrategyRecommendation(
            primary_strategy=primary_strategy,
            secondary_strategy=secondary_strategy,
            confidence=confidence,
            reasoning=reasoning,
            emotion_match_score=emotion_match_score,
            context_match_score=context_match_score,
            pattern_match_score=pattern_match_score,
            total_score=total_score,
            cosine_similarity_score=cosine_similarity_score,
            low_confidence_alternatives=low_confidence_alternatives,
            semantic_match_used=semantic_match_used,
            embedding_quality=embedding_quality,
        )

    def _initialize_emotion_strategy_mappings(self) -> Dict[str, Dict[str, float]]:
        """감정-전략 매핑 규칙 초기화"""
        return {
            "joy": {
                "initiate": 0.9,  # 기쁠 때는 주도적으로
                "harmonize": 0.8,  # 조화를 추구
                "adapt": 0.7,  # 적응력도 높음
                "confront": 0.5,  # 대응도 가능
                "analyze": 0.4,  # 분석보다는 행동
                "retreat": 0.2,  # 후퇴는 잘 안함
            },
            "sadness": {
                "retreat": 0.9,  # 슬플 때는 잠시 후퇴
                "harmonize": 0.7,  # 조화로 회복
                "analyze": 0.6,  # 상황 분석 필요
                "adapt": 0.5,  # 적응 시도
                "confront": 0.3,  # 대응은 어려움
                "initiate": 0.2,  # 주도는 힘듦
            },
            "anger": {
                "confront": 0.9,  # 화날 때는 직면
                "initiate": 0.8,  # 주도적 행동
                "analyze": 0.6,  # 분석으로 진정
                "adapt": 0.4,  # 적응은 어려움
                "harmonize": 0.3,  # 조화는 나중에
                "retreat": 0.2,  # 후퇴는 피함
            },
            "fear": {
                "retreat": 0.8,  # 두려울 때는 후퇴
                "analyze": 0.9,  # 분석으로 이해
                "adapt": 0.7,  # 상황 적응
                "harmonize": 0.5,  # 조화로 안정
                "confront": 0.3,  # 대응은 두려움
                "initiate": 0.2,  # 주도는 어려움
            },
            "surprise": {
                "analyze": 0.9,  # 놀랄 때는 분석
                "adapt": 0.8,  # 빠른 적응
                "retreat": 0.6,  # 잠시 후퇴
                "harmonize": 0.5,  # 균형 회복
                "confront": 0.4,  # 상황에 따라
                "initiate": 0.3,  # 주도는 신중히
            },
            "neutral": {
                "analyze": 0.7,  # 중립적 분석
                "adapt": 0.7,  # 유연한 적응
                "harmonize": 0.7,  # 균형 유지
                "confront": 0.5,  # 필요시 대응
                "initiate": 0.5,  # 필요시 주도
                "retreat": 0.4,  # 필요시 후퇴
            },
        }

    def _initialize_context_patterns(self) -> Dict[str, Dict[str, float]]:
        """컨텍스트 패턴 규칙 초기화"""
        return {
            "high_urgency": {
                "confront": 0.8,
                "initiate": 0.7,
                "adapt": 0.6,
                "analyze": 0.4,
                "harmonize": 0.3,
                "retreat": 0.2,
            },
            "high_complexity": {
                "analyze": 0.9,
                "adapt": 0.7,
                "harmonize": 0.6,
                "confront": 0.5,
                "initiate": 0.4,
                "retreat": 0.3,
            },
            "relationship_context": {
                "harmonize": 0.9,
                "adapt": 0.8,
                "analyze": 0.6,
                "retreat": 0.5,
                "confront": 0.3,
                "initiate": 0.3,
            },
            "problem_solving": {
                "analyze": 0.9,
                "confront": 0.8,
                "adapt": 0.7,
                "initiate": 0.6,
                "harmonize": 0.4,
                "retreat": 0.3,
            },
            "creative_context": {
                "initiate": 0.9,
                "adapt": 0.8,
                "harmonize": 0.7,
                "analyze": 0.6,
                "confront": 0.4,
                "retreat": 0.3,
            },
            "support_needed": {
                "harmonize": 0.9,
                "adapt": 0.7,
                "retreat": 0.6,
                "analyze": 0.5,
                "confront": 0.3,
                "initiate": 0.3,
            },
        }

    def _initialize_text_patterns(self) -> Dict[str, Dict[str, float]]:
        """텍스트 패턴 매칭 규칙 초기화"""
        return {
            # 질문 패턴
            "questions": {
                "patterns": ["어떻", "무엇", "왜", "언제", "어디", "누가", "?"],
                "strategy_weights": {"analyze": 0.8, "adapt": 0.6, "harmonize": 0.5},
            },
            # 문제/도전 패턴
            "problems": {
                "patterns": ["문제", "어려", "힘들", "도전", "해결", "극복"],
                "strategy_weights": {"confront": 0.8, "analyze": 0.7, "adapt": 0.6},
            },
            # 창의/아이디어 패턴
            "creative": {
                "patterns": ["아이디어", "창의", "새로운", "혁신", "발명", "만들"],
                "strategy_weights": {"initiate": 0.9, "adapt": 0.7, "harmonize": 0.6},
            },
            # 관계/소통 패턴
            "relationships": {
                "patterns": ["관계", "소통", "대화", "친구", "가족", "동료"],
                "strategy_weights": {"harmonize": 0.9, "adapt": 0.7, "analyze": 0.5},
            },
            # 학습/성장 패턴
            "learning": {
                "patterns": ["배우", "성장", "발전", "개선", "향상", "공부"],
                "strategy_weights": {"analyze": 0.8, "adapt": 0.8, "initiate": 0.6},
            },
            # 휴식/회복 패턴
            "recovery": {
                "patterns": ["휴식", "쉬", "회복", "재충전", "치유", "편안"],
                "strategy_weights": {"retreat": 0.9, "harmonize": 0.8, "adapt": 0.5},
            },
        }

    def _calculate_emotion_based_scores(self, emotion: str) -> Dict[str, float]:
        """감정 기반 전략 점수 계산"""
        return self.emotion_strategy_mappings.get(
            emotion, self.emotion_strategy_mappings["neutral"]
        )

    def _calculate_context_based_scores(
        self, context: StrategyContext
    ) -> Dict[str, float]:
        """컨텍스트 기반 전략 점수 계산"""
        scores = {}

        # 긴급도가 높으면
        if context.urgency_level > 0.7:
            for strategy, weight in self.context_patterns["high_urgency"].items():
                scores[strategy] = scores.get(strategy, 0.0) + weight * 0.3

        # 복잡도가 높으면
        if context.complexity_level > 0.7:
            for strategy, weight in self.context_patterns["high_complexity"].items():
                scores[strategy] = scores.get(strategy, 0.0) + weight * 0.3

        # 관계 컨텍스트가 있으면
        if context.relationship_context:
            for strategy, weight in self.context_patterns[
                "relationship_context"
            ].items():
                scores[strategy] = scores.get(strategy, 0.0) + weight * 0.4

        # 문제 해결 컨텍스트가 있으면
        if context.problem_solving_context:
            for strategy, weight in self.context_patterns["problem_solving"].items():
                scores[strategy] = scores.get(strategy, 0.0) + weight * 0.4

        # 창의적 컨텍스트가 있으면
        if context.creative_context:
            for strategy, weight in self.context_patterns["creative_context"].items():
                scores[strategy] = scores.get(strategy, 0.0) + weight * 0.4

        # 지원이 필요하면
        if context.support_needed:
            for strategy, weight in self.context_patterns["support_needed"].items():
                scores[strategy] = scores.get(strategy, 0.0) + weight * 0.3

        return scores

    def _calculate_text_pattern_scores(self, text: str) -> Dict[str, float]:
        """텍스트 패턴 기반 전략 점수 계산"""
        scores = {}
        text_lower = text.lower()

        for pattern_type, pattern_info in self.text_patterns.items():
            patterns = pattern_info["patterns"]
            strategy_weights = pattern_info["strategy_weights"]

            # 패턴 매치 개수 계산
            match_count = sum(1 for pattern in patterns if pattern in text_lower)

            if match_count > 0:
                # 매치 강도 계산 (매치 수 / 전체 패턴 수)
                match_intensity = min(match_count / len(patterns), 1.0)

                # 각 전략에 가중치 적용
                for strategy, weight in strategy_weights.items():
                    scores[strategy] = (
                        scores.get(strategy, 0.0) + weight * match_intensity * 0.3
                    )

        return scores

    def _analyze_urgency(self, text: str) -> float:
        """긴급도 분석"""
        urgency_markers = [
            "급해",
            "빨리",
            "당장",
            "즉시",
            "긴급",
            "어서",
            "시급",
            "바로",
        ]

        urgency_score = 0.0
        text_lower = text.lower()

        for marker in urgency_markers:
            if marker in text_lower:
                urgency_score += 0.2

        # 느낌표 개수도 고려
        urgency_score += min(text.count("!") * 0.1, 0.3)

        return min(urgency_score, 1.0)

    def _analyze_complexity(self, text: str) -> float:
        """복잡도 분석"""
        # 텍스트 길이 기반
        length_complexity = min(len(text) / 200.0, 0.4)

        # 문장 수 기반
        sentence_count = max(len([s for s in text.split(".") if s.strip()]), 1)
        sentence_complexity = min(sentence_count / 5.0, 0.3)

        # 복잡한 키워드 존재 여부
        complex_markers = [
            "복잡",
            "어려운",
            "다양한",
            "여러",
            "많은",
            "구체적",
            "세부적",
            "다각도",
        ]

        complexity_keywords = sum(
            1 for marker in complex_markers if marker in text.lower()
        )
        keyword_complexity = min(complexity_keywords * 0.1, 0.3)

        return min(length_complexity + sentence_complexity + keyword_complexity, 1.0)

    def _detect_relationship_context(self, text: str) -> bool:
        """관계 컨텍스트 감지"""
        relationship_markers = [
            "관계",
            "친구",
            "가족",
            "동료",
            "상사",
            "부모",
            "자녀",
            "연인",
            "소통",
            "대화",
            "갈등",
            "화해",
            "이해",
            "공감",
        ]

        return any(marker in text.lower() for marker in relationship_markers)

    def _detect_problem_solving_context(self, text: str) -> bool:
        """문제 해결 컨텍스트 감지"""
        problem_markers = [
            "문제",
            "해결",
            "방법",
            "어떻게",
            "도움",
            "조언",
            "제안",
            "개선",
            "수정",
            "고치",
            "해결책",
            "대안",
        ]

        return any(marker in text.lower() for marker in problem_markers)

    def _detect_creative_context(self, text: str) -> bool:
        """창의적 컨텍스트 감지"""
        creative_markers = [
            "아이디어",
            "창의",
            "새로운",
            "혁신",
            "발명",
            "디자인",
            "만들",
            "작성",
            "그리",
            "상상",
            "독창적",
            "예술",
        ]

        return any(marker in text.lower() for marker in creative_markers)

    def _detect_support_need(self, text: str) -> bool:
        """지원 필요 여부 감지"""
        support_markers = [
            "도와",
            "지원",
            "부탁",
            "도움",
            "어려워",
            "힘들어",
            "모르겠",
            "확실하지",
            "고민",
            "걱정",
        ]

        return any(marker in text.lower() for marker in support_markers)

    def _estimate_confidence_level(self, text: str, emotion: str) -> float:
        """신뢰도 수준 추정"""
        # 긍정적 감정은 높은 신뢰도
        if emotion in ["joy", "neutral"]:
            base_confidence = 0.7
        elif emotion in ["surprise"]:
            base_confidence = 0.5
        else:  # sadness, anger, fear
            base_confidence = 0.4

        # 확신 표현 감지
        confident_markers = ["확실", "분명", "당연", "틀림없", "자신"]
        uncertain_markers = ["모르", "확실하지", "아마", "혹시", "걱정"]

        text_lower = text.lower()

        confident_count = sum(1 for marker in confident_markers if marker in text_lower)
        uncertain_count = sum(1 for marker in uncertain_markers if marker in text_lower)

        confidence_adjustment = (confident_count * 0.1) - (uncertain_count * 0.1)

        return max(0.1, min(base_confidence + confidence_adjustment, 1.0))

    def _calculate_cosine_similarity_scores(
        self, text: str
    ) -> Tuple[Dict[str, float], float]:
        """v2.0 코사인 유사도 기반 전략 점수 계산"""
        global EMBEDDING_AVAILABLE

        if not EMBEDDING_AVAILABLE or not self.embedding_model:
            return {}, 0.0

        try:
            # 입력 텍스트 임베딩
            text_embedding = self.embedding_model.encode([text])[0]

            strategy_similarities = {}
            all_similarities = []

            # 각 전략의 레퍼런스 문장들과 유사도 계산
            for strategy_name, references in self.strategy_semantic_references.items():
                ref_embeddings = self.embedding_model.encode(references)

                # 각 레퍼런스와의 코사인 유사도 계산
                similarities = []
                for ref_embedding in ref_embeddings:
                    similarity = np.dot(text_embedding, ref_embedding) / (
                        np.linalg.norm(text_embedding) * np.linalg.norm(ref_embedding)
                    )
                    similarities.append(similarity)
                    all_similarities.append(similarity)

                # 최대 유사도를 해당 전략의 점수로 사용
                max_similarity = max(similarities)
                if max_similarity > 0.3:  # 임계값
                    strategy_similarities[strategy_name] = max_similarity

            # 임베딩 품질 계산 (전체 유사도의 분산으로 품질 추정)
            if all_similarities:
                mean_sim = np.mean(all_similarities)
                std_sim = np.std(all_similarities)
                embedding_quality = min(mean_sim + (1.0 - std_sim), 1.0)
            else:
                embedding_quality = 0.0

            return strategy_similarities, embedding_quality

        except Exception as e:
            print(f"⚠️ 코사인 유사도 계산 오류: {e}")
            return {}, 0.0

    def _get_neutral_fallback_strategy(self, text: str) -> StrategyType:
        """중립적 폴백 전략 선택 (감정이 불분명할 때)"""
        text_lower = text.lower()

        # 텍스트 패턴에 따른 중립적 전략 선택
        if any(word in text_lower for word in ["질문", "궁금", "어떻", "무엇"]):
            return StrategyType.ANALYZE
        elif any(word in text_lower for word in ["도움", "지원", "조언"]):
            return StrategyType.HARMONIZE
        elif any(word in text_lower for word in ["문제", "어려움", "해결"]):
            return StrategyType.CONFRONT
        else:
            return StrategyType.ADAPT  # 기본값

    def _get_fallback_strategy(self, emotion: str) -> StrategyType:
        """폴백 전략 선택"""
        fallback_mappings = {
            "joy": StrategyType.INITIATE,
            "sadness": StrategyType.RETREAT,
            "anger": StrategyType.CONFRONT,
            "fear": StrategyType.ANALYZE,
            "surprise": StrategyType.ANALYZE,
            "neutral": StrategyType.ADAPT,
        }

        return fallback_mappings.get(emotion, StrategyType.ADAPT)

    def _update_selection_stats(self, recommendation: StrategyRecommendation):
        """선택 통계 업데이트"""
        strategy = recommendation.primary_strategy.value

        # 전략 사용 횟수
        self.selection_stats["strategy_usage"][strategy] = (
            self.selection_stats["strategy_usage"].get(strategy, 0) + 1
        )

    def get_strategy_analytics(self) -> Dict[str, Any]:
        """전략 선택 분석 결과 반환"""
        total_selections = self.selection_stats["total_selections"]

        if total_selections == 0:
            return {"message": "선택 이력이 없습니다"}

        # 전략 사용 분포
        strategy_distribution = {}
        for strategy, count in self.selection_stats["strategy_usage"].items():
            strategy_distribution[strategy] = {
                "count": count,
                "percentage": (count / total_selections) * 100,
            }

        # 가장 많이 사용된 전략
        most_used_strategy = (
            max(self.selection_stats["strategy_usage"].items(), key=lambda x: x[1])
            if self.selection_stats["strategy_usage"]
            else None
        )

        return {
            "total_selections": total_selections,
            "strategy_distribution": strategy_distribution,
            "most_used_strategy": (
                {
                    "strategy": most_used_strategy[0],
                    "count": most_used_strategy[1],
                    "percentage": (most_used_strategy[1] / total_selections) * 100,
                }
                if most_used_strategy
                else None
            ),
            "available_strategies": [s.value for s in StrategyType],
        }


# 글로벌 인스턴스
_global_strategy_picker = None


def get_strategy_picker() -> StrategyPicker:
    """글로벌 전략 선택기 인스턴스 반환"""
    global _global_strategy_picker
    if _global_strategy_picker is None:
        _global_strategy_picker = StrategyPicker()
    return _global_strategy_picker


def pick_strategy(
    input_text: str, emotion: str = "neutral", context: Optional[Dict[str, Any]] = None
) -> StrategyType:
    """🎯 전략 선택 - 메인 진입점"""
    picker = get_strategy_picker()
    return picker.pick_strategy(input_text, emotion, context)


def get_detailed_strategy_recommendation(
    input_text: str, emotion: str = "neutral", context: Optional[Dict[str, Any]] = None
) -> StrategyRecommendation:
    """상세한 전략 추천 결과 반환"""
    picker = get_strategy_picker()
    return picker.get_detailed_recommendation(input_text, emotion, context)


if __name__ == "__main__":
    # 전략 선택기 테스트
    print("🧪 Strategy Picker 테스트")

    test_cases = [
        {
            "text": "요즘 너무 힘들어서 우울해요",
            "emotion": "sadness",
            "expected": "retreat",
        },
        {
            "text": "새로운 아이디어를 만들어보고 싶어요",
            "emotion": "joy",
            "expected": "initiate",
        },
        {
            "text": "이 문제를 어떻게 해결해야 할까요?",
            "emotion": "neutral",
            "expected": "analyze",
        },
        {"text": "급하게 도움이 필요해요!", "emotion": "fear", "expected": "confront"},
    ]

    picker = get_strategy_picker()

    for i, case in enumerate(test_cases, 1):
        print(f"\n🎯 테스트 {i}: {case['text']}")

        recommendation = picker.get_detailed_recommendation(
            case["text"], case["emotion"]
        )

        print(f"   선택된 전략: {recommendation.primary_strategy.value}")
        print(f"   예상 전략: {case['expected']}")
        print(
            f"   일치 여부: {'✅' if recommendation.primary_strategy.value == case['expected'] else '❌'}"
        )
        print(f"   신뢰도: {recommendation.confidence:.2f}")
        print(f"   추론: {', '.join(recommendation.reasoning)}")

    # 분석 결과 출력
    analytics = picker.get_strategy_analytics()
    print(f"\n📊 전략 선택 분석:")
    if analytics.get("total_selections"):
        print(f"   총 선택 횟수: {analytics['total_selections']}")
        if analytics.get("most_used_strategy"):
            most_used = analytics["most_used_strategy"]
            print(
                f"   가장 많이 사용된 전략: {most_used['strategy']} ({most_used['percentage']:.1f}%)"
            )
    else:
        print(f"   분석 결과: {analytics.get('message', '데이터 없음')}")
