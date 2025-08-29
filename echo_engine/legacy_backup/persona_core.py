#!/usr/bin/env python3
"""
🧠 EchoJudgmentSystem v10.5 - Persona Core
시그니처 기반 페르소나 인스턴스 시스템

페르소나는 다음 기능을 제공합니다:
- 시그니처 기반 상태 설정 및 로딩
- 감정 감도, 판단 성향, 표현 스타일 관리
- 메타인지 연동 및 학습 능력
- 판단 컨텍스트별 적응적 행동
"""

import json
import time
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque

# 메타 로그 통합
try:
    from .persona_meta_logger import (
        PersonaMetaLog,
        log_persona_meta,
        get_persona_meta_logger,
    )

    META_LOG_AVAILABLE = True
except ImportError:
    META_LOG_AVAILABLE = False

# 통합 설정 시스템
try:
    import sys

    # sys.path 수정 불필요 (portable_paths 사용)
    from config_loader import get_config, get_config_loader

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


class IntentType(Enum):
    """사용자 의도 유형"""

    ACHIEVEMENT_SEEKING = "achievement_seeking"  # 성취 추구
    AVOIDANCE_MOTIVE = "avoidance_motive"  # 회피 동기
    SOCIAL_CONNECTION = "social_connection"  # 사회적 연결
    PROBLEM_SOLVING = "problem_solving"  # 문제 해결
    EMOTIONAL_SUPPORT = "emotional_support"  # 감정적 지지
    INFORMATION_SEEKING = "information_seeking"  # 정보 탐색
    CREATIVE_EXPRESSION = "creative_expression"  # 창의적 표현
    RELATIONSHIP_BUILDING = "relationship_building"  # 관계 구축
    SELF_REFLECTION = "self_reflection"  # 자기 성찰
    DECISION_MAKING = "decision_making"  # 의사결정


class PersonaState(Enum):
    """페르소나 상태"""

    INACTIVE = "inactive"
    ACTIVE = "active"
    LEARNING = "learning"
    ADAPTING = "adapting"
    REFLECTION = "reflection"


class EmotionIntensity(Enum):
    """감정 강도"""

    MINIMAL = "minimal"  # 0.0 - 0.2
    LOW = "low"  # 0.2 - 0.4
    MODERATE = "moderate"  # 0.4 - 0.6
    HIGH = "high"  # 0.6 - 0.8
    INTENSE = "intense"  # 0.8 - 1.0


@dataclass
class PersonaMemory:
    """페르소나 기억 구조"""

    recent_interactions: deque = field(default_factory=lambda: deque(maxlen=20))
    emotional_patterns: Dict[str, List[float]] = field(default_factory=dict)
    successful_strategies: Dict[str, int] = field(default_factory=dict)
    learning_insights: List[str] = field(default_factory=list)
    adaptation_history: List[Dict[str, Any]] = field(default_factory=list)

    def add_interaction(self, interaction: Dict[str, Any]):
        """상호작용 기록 추가"""
        interaction["timestamp"] = datetime.now().isoformat()
        self.recent_interactions.append(interaction)

    def track_emotional_pattern(self, emotion: str, intensity: float):
        """감정 패턴 추적"""
        if emotion not in self.emotional_patterns:
            self.emotional_patterns[emotion] = []
        self.emotional_patterns[emotion].append(intensity)

        # 최근 10개만 유지
        if len(self.emotional_patterns[emotion]) > 10:
            self.emotional_patterns[emotion] = self.emotional_patterns[emotion][-10:]

    def update_strategy_success(self, strategy: str, success: bool):
        """전략 성공률 업데이트"""
        if strategy not in self.successful_strategies:
            self.successful_strategies[strategy] = 0

        if success:
            self.successful_strategies[strategy] += 1
        else:
            self.successful_strategies[strategy] = max(
                0, self.successful_strategies[strategy] - 1
            )

    def add_strategy_feedback(self, strategy: str, effectiveness_score: float):
        """전략 효과성 피드백 추가"""
        feedback_key = f"{strategy}_feedback"
        if feedback_key not in self.emotional_patterns:
            self.emotional_patterns[feedback_key] = []

        self.emotional_patterns[feedback_key].append(effectiveness_score)

        # 최근 10개만 유지
        if len(self.emotional_patterns[feedback_key]) > 10:
            self.emotional_patterns[feedback_key] = self.emotional_patterns[
                feedback_key
            ][-10:]

    def get_strategy_effectiveness(self, strategy: str) -> float:
        """전략 효과성 평균 조회"""
        feedback_key = f"{strategy}_feedback"
        if (
            feedback_key in self.emotional_patterns
            and self.emotional_patterns[feedback_key]
        ):
            return sum(self.emotional_patterns[feedback_key]) / len(
                self.emotional_patterns[feedback_key]
            )
        return 0.5  # 기본값


@dataclass
class PersonaProfile:
    """페르소나 프로필"""

    name: str
    signature_type: str  # Echo-Aurora, Echo-Phoenix, etc.

    # 기본 성향
    emotion_sensitivity: float = 0.5
    reasoning_depth: int = 3
    response_tone: str = "balanced"
    decision_style: str = "analytical"

    # 적응성 설정
    adaptability: float = 0.7
    learning_rate: float = 0.3
    memory_retention: float = 0.8

    # 행동 특성
    primary_strategies: List[str] = field(default_factory=list)
    emotional_triggers: Dict[str, float] = field(default_factory=dict)
    communication_patterns: Dict[str, Any] = field(default_factory=dict)

    # 메타인지 특성
    self_reflection_frequency: float = 0.5
    meta_awareness_level: float = 0.6
    growth_orientation: float = 0.8


class PersonaCore:
    """페르소나 코어 엔진"""

    def __init__(self, profile: PersonaProfile):
        """
        페르소나 코어 초기화

        Args:
            profile: 페르소나 프로필
        """
        self.profile = profile
        self.state = PersonaState.INACTIVE
        self.memory = PersonaMemory()

        # 현재 상태
        self.current_emotion = "neutral"
        self.current_emotion_intensity = 0.5
        self.current_strategy = "balanced"
        self.energy_level = 1.0

        # 성능 지표
        self.interaction_count = 0
        self.success_rate = 0.0
        self.adaptation_cycles = 0

        # 메타인지 상태
        self.last_reflection = datetime.now()
        self.insights_generated = 0
        self.learning_momentum = 0.5

        # 응답 생성 시스템
        self.response_generators = self._initialize_response_generators()

        # 메타 로거 세션 ID
        if META_LOG_AVAILABLE:
            self.meta_logger = get_persona_meta_logger()
            self.session_id = self.meta_logger.current_session_id
        else:
            self.session_id = f"session_{int(time.time())}"

        # 시그니처 연동
        self._load_signature_config()

        print(
            f"🧠 페르소나 '{self.profile.name}' 초기화 완료 (타입: {self.profile.signature_type})"
        )

    def _initialize_response_generators(self) -> Dict[str, Dict[str, str]]:
        """응답 생성기 초기화"""
        return {
            "empathetic": {
                "gentle": "이해할 수 있어요. 천천히 함께 생각해봐요.",
                "warm": "따뜻한 마음으로 들어드릴게요.",
                "compassionate": "마음이 아프시겠어요. 제가 옆에 있어드릴게요.",
                "encouraging": "힘든 시간이지만 충분히 극복하실 수 있어요.",
            },
            "analytical": {
                "objective": "상황을 객관적으로 분석해보겠습니다.",
                "logical": "논리적으로 접근해보면 다음과 같습니다.",
                "systematic": "단계별로 체계적으로 살펴보겠습니다.",
                "measured": "신중하게 검토한 결과입니다.",
            },
            "supportive": {
                "encouraging": "당신의 능력을 믿어요. 할 수 있어요!",
                "reassuring": "괜찮아요, 제가 도와드릴게요.",
                "motivating": "이미 훌륭한 첫걸음을 내디뎠네요.",
                "inspiring": "당신의 열정이 길을 만들어갈 거예요.",
            },
            "creative": {
                "inspiring": "새로운 관점에서 바라보면 어떨까요?",
                "innovative": "혁신적인 아이디어가 떠오르네요.",
                "imaginative": "상상력을 발휘해보면 더 좋은 방법이 있을 것 같아요.",
                "exploratory": "함께 새로운 가능성을 탐색해봐요.",
            },
            "cautious": {
                "measured": "신중하게 검토해보는 것이 좋겠어요.",
                "careful": "조심스럽게 접근하는 것이 현명합니다.",
                "prudent": "모든 측면을 고려해보겠습니다.",
                "thoughtful": "깊이 생각해볼 필요가 있겠네요.",
            },
            "balanced": {
                "neutral": "균형잡힌 관점에서 말씀드리면,",
                "moderate": "적절한 접근 방법을 찾아보겠습니다.",
                "harmonious": "조화로운 해결책을 모색해봐요.",
                "steady": "안정적으로 진행하는 것이 좋겠어요.",
            },
        }

    def _load_signature_config(self):
        """시그니처 설정 로드"""
        if not CONFIG_AVAILABLE:
            return

        try:
            # 통합 설정에서 시그니처별 설정 로드
            sig_config = get_config(f"signatures.{self.profile.signature_type}", {})

            if sig_config:
                # 시그니처 설정을 페르소나 프로필에 적용
                self.profile.emotion_sensitivity = sig_config.get(
                    "emotion_sensitivity", self.profile.emotion_sensitivity
                )
                self.profile.response_tone = sig_config.get(
                    "response_tone", self.profile.response_tone
                )
                self.profile.reasoning_depth = sig_config.get(
                    "reasoning_depth", self.profile.reasoning_depth
                )

                # 시그니처별 특성 적용
                if self.profile.signature_type == "Echo-Aurora":
                    self.profile.primary_strategies = [
                        "empathetic",
                        "nurturing",
                        "optimistic",
                    ]
                    self.profile.emotional_triggers = {
                        "joy": 0.8,
                        "hope": 0.9,
                        "compassion": 0.7,
                    }
                elif self.profile.signature_type == "Echo-Phoenix":
                    self.profile.primary_strategies = [
                        "transformative",
                        "resilient",
                        "adaptive",
                    ]
                    self.profile.emotional_triggers = {
                        "determination": 0.9,
                        "courage": 0.8,
                        "renewal": 0.7,
                    }
                elif self.profile.signature_type == "Echo-Sage":
                    self.profile.primary_strategies = [
                        "analytical",
                        "logical",
                        "systematic",
                    ]
                    self.profile.emotional_triggers = {
                        "curiosity": 0.8,
                        "wisdom": 0.9,
                        "understanding": 0.7,
                    }
                elif self.profile.signature_type == "Echo-Companion":
                    self.profile.primary_strategies = [
                        "supportive",
                        "loyal",
                        "reliable",
                    ]
                    self.profile.emotional_triggers = {
                        "trust": 0.9,
                        "stability": 0.8,
                        "care": 0.7,
                    }

                print(f"🎭 시그니처 '{self.profile.signature_type}' 설정 적용 완료")

        except Exception as e:
            print(f"⚠️ 시그니처 설정 로드 실패: {e}")

    def activate(self):
        """페르소나 활성화"""
        self.state = PersonaState.ACTIVE
        self.energy_level = 1.0
        print(f"✨ 페르소나 '{self.profile.name}' 활성화")

    def infer_intent(self, text: str) -> str:
        """
        사용자 의도 추론

        Args:
            text: 입력 텍스트

        Returns:
            추론된 의도
        """
        text_lower = text.lower()

        # 의도별 키워드 패턴
        intent_patterns = {
            IntentType.AVOIDANCE_MOTIVE: [
                "무서",
                "걱정",
                "불안",
                "두려",
                "피하고",
                "싫어",
                "하기 싫",
                "도망",
                "회피",
            ],
            IntentType.ACHIEVEMENT_SEEKING: [
                "성공",
                "달성",
                "목표",
                "성취",
                "이루고",
                "해내고",
                "완수",
                "승리",
                "이기고",
            ],
            IntentType.SOCIAL_CONNECTION: [
                "만나고",
                "사람들",
                "친구",
                "관계",
                "소통",
                "어울리",
                "함께",
                "네트워킹",
            ],
            IntentType.PROBLEM_SOLVING: [
                "해결",
                "문제",
                "방법",
                "어떻게",
                "해결책",
                "풀어",
                "극복",
                "해법",
            ],
            IntentType.EMOTIONAL_SUPPORT: [
                "힘들",
                "우울",
                "슬프",
                "외로",
                "지쳐",
                "위로",
                "공감",
                "이해",
                "들어줘",
            ],
            IntentType.INFORMATION_SEEKING: [
                "알고 싶",
                "궁금",
                "정보",
                "알려줘",
                "설명",
                "가르쳐",
                "배우고",
                "공부",
            ],
            IntentType.CREATIVE_EXPRESSION: [
                "창의",
                "아이디어",
                "만들고",
                "디자인",
                "예술",
                "상상",
                "창작",
                "표현",
            ],
            IntentType.RELATIONSHIP_BUILDING: [
                "관계",
                "친해지",
                "신뢰",
                "유대",
                "연결",
                "가까워",
                "깊어지",
                "발전",
            ],
            IntentType.SELF_REFLECTION: [
                "생각",
                "반성",
                "성찰",
                "돌아보",
                "자신",
                "내면",
                "깨달",
                "인식",
            ],
            IntentType.DECISION_MAKING: [
                "결정",
                "선택",
                "판단",
                "결론",
                "정하고",
                "택하",
                "고민",
                "선택지",
            ],
        }

        # 패턴 매칭 점수 계산
        intent_scores = {}
        for intent_type, keywords in intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                # 페르소나 특성에 따른 가중치 적용
                weight = self._get_intent_weight(intent_type)
                intent_scores[intent_type] = score * weight

        # 가장 높은 점수의 의도 반환
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            return best_intent.value

        # 기본 의도
        return IntentType.INFORMATION_SEEKING.value

    def _get_intent_weight(self, intent_type: IntentType) -> float:
        """페르소나 특성에 따른 의도 가중치"""
        intent_weights = {
            "Echo-Aurora": {
                IntentType.EMOTIONAL_SUPPORT: 1.5,
                IntentType.SOCIAL_CONNECTION: 1.3,
                IntentType.RELATIONSHIP_BUILDING: 1.4,
            },
            "Echo-Phoenix": {
                IntentType.ACHIEVEMENT_SEEKING: 1.5,
                IntentType.CREATIVE_EXPRESSION: 1.4,
                IntentType.PROBLEM_SOLVING: 1.3,
            },
            "Echo-Sage": {
                IntentType.INFORMATION_SEEKING: 1.5,
                IntentType.DECISION_MAKING: 1.4,
                IntentType.SELF_REFLECTION: 1.3,
            },
            "Echo-Companion": {
                IntentType.RELATIONSHIP_BUILDING: 1.5,
                IntentType.EMOTIONAL_SUPPORT: 1.3,
                IntentType.SOCIAL_CONNECTION: 1.2,
            },
        }

        persona_weights = intent_weights.get(self.profile.signature_type, {})
        return persona_weights.get(intent_type, 1.0)

    def generate_response(self, text: str, tone: str, intent: str = None) -> str:
        """
        톤 기반 응답 생성

        Args:
            text: 입력 텍스트
            tone: 응답 톤
            intent: 사용자 의도 (선택사항)

        Returns:
            생성된 응답
        """
        # 현재 전략에 기반한 응답 스타일 선택
        strategy = self.current_strategy

        # 전략별 응답 템플릿 선택
        if (
            strategy in self.response_generators
            and tone in self.response_generators[strategy]
        ):
            base_response = self.response_generators[strategy][tone]
        else:
            # 폴백 응답
            base_response = "도움이 되도록 최선을 다하겠습니다."

        # 의도에 따른 응답 맞춤화
        if intent:
            customized_response = self._customize_response_for_intent(
                base_response, intent, text
            )
            return customized_response

        return base_response

    def _customize_response_for_intent(
        self, base_response: str, intent: str, text: str
    ) -> str:
        """의도에 따른 응답 맞춤화"""
        intent_customizations = {
            "avoidance_motive": "불안하신 마음 이해해요. " + base_response,
            "achievement_seeking": "목표를 향한 열정이 보여요. " + base_response,
            "emotional_support": "마음이 힘드시겠어요. " + base_response,
            "problem_solving": "문제 해결을 위해 " + base_response.lower(),
            "creative_expression": "창의적인 아이디어네요. " + base_response,
            "decision_making": "중요한 선택이시군요. " + base_response,
        }

        return intent_customizations.get(intent, base_response)

    def strategy_feedback(
        self, strategy: str, success: bool, effectiveness_score: float = None
    ) -> bool:
        """
        전략 효과성 피드백

        Args:
            strategy: 전략명
            success: 성공 여부
            effectiveness_score: 효과성 점수 (0.0-1.0)

        Returns:
            피드백 적용 성공 여부
        """
        try:
            # 메모리에 성공률 업데이트
            self.memory.update_strategy_success(strategy, success)

            # 효과성 점수가 제공된 경우 피드백 추가
            if effectiveness_score is not None:
                self.memory.add_strategy_feedback(strategy, effectiveness_score)

            # 적응적 학습 트리거 (낮은 효과성일 때)
            if effectiveness_score is not None and effectiveness_score < 0.4:
                self._adaptive_learning()
                print(f"⚠️ 낮은 전략 효과성으로 인한 적응적 학습 트리거: {strategy}")

            # 메타 로그 (사용 가능한 경우)
            if META_LOG_AVAILABLE:
                from .persona_meta_logger import log_strategy_feedback

                log_strategy_feedback(
                    self.profile.name,
                    strategy,
                    success,
                    effectiveness_score or (1.0 if success else 0.0),
                )

            print(
                f"📈 전략 피드백 적용: {strategy} → {'성공' if success else '실패'} (점수: {effectiveness_score})"
            )
            return True

        except Exception as e:
            print(f"❌ 전략 피드백 적용 실패: {e}")
            return False

    def process_input(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        입력 처리 및 페르소나 반응 생성

        Args:
            text: 입력 텍스트
            context: 처리 컨텍스트

        Returns:
            페르소나 처리 결과
        """
        if self.state == PersonaState.INACTIVE:
            self.activate()

        self.interaction_count += 1

        # 0. 의도 추론
        intent_inferred = self.infer_intent(text)

        # 1. 감정 분석 및 반응
        emotion_analysis = self._analyze_emotional_content(text, context)

        # 2. 전략 선택
        strategy_selection = self._select_strategy(emotion_analysis, context)

        # 3. 응답 톤 결정
        response_tone = self._determine_response_tone(
            emotion_analysis, strategy_selection
        )

        # 4. 응답 생성
        generated_response = self.generate_response(
            text, response_tone, intent_inferred
        )

        # 5. 메타인지적 인사이트
        meta_insights = self._generate_meta_insights(text, context, emotion_analysis)

        # 6. 상호작용 기록
        interaction = {
            "input_text": text,
            "context": context,
            "intent_inferred": intent_inferred,
            "emotion_detected": emotion_analysis["primary_emotion"],
            "emotion_intensity": emotion_analysis["intensity"],
            "strategy_selected": strategy_selection["primary_strategy"],
            "response_tone": response_tone,
            "generated_response": generated_response,
            "meta_insights": meta_insights,
        }

        self.memory.add_interaction(interaction)
        self.memory.track_emotional_pattern(
            emotion_analysis["primary_emotion"], emotion_analysis["intensity"]
        )

        # 7. 메타 로그 기록 (사용 가능한 경우)
        if META_LOG_AVAILABLE:
            meta_log = PersonaMetaLog(
                session_id=self.session_id,
                persona_name=self.profile.name,
                signature_type=self.profile.signature_type,
                timestamp=datetime.now().isoformat(),
                emotion_detected=emotion_analysis["primary_emotion"],
                emotion_intensity=emotion_analysis["intensity"],
                emotion_patterns=dict(self.memory.emotional_patterns),
                intent_inferred=intent_inferred,
                strategy_selected=strategy_selection["primary_strategy"],
                strategy_confidence=strategy_selection["confidence"],
                response_tone=response_tone,
                response_generated=generated_response,
                learning_insights=meta_insights,
                meta_reflection={
                    "energy_level": self.energy_level,
                    "learning_momentum": self.learning_momentum,
                    "adaptation_cycles": self.adaptation_cycles,
                },
                persona_state=self.state.value,
                interaction_count=self.interaction_count,
            )
            log_persona_meta(meta_log)

        # 8. 적응적 학습
        if self.interaction_count % 5 == 0:  # 5회마다 학습
            self._adaptive_learning()

        # 9. 주기적 자기 반성
        if self._should_reflect():
            self._perform_self_reflection()

        return {
            "persona_name": self.profile.name,
            "persona_state": self.state.value,
            "intent_inferred": intent_inferred,
            "emotion_analysis": emotion_analysis,
            "strategy_selection": strategy_selection,
            "response_tone": response_tone,
            "generated_response": generated_response,
            "meta_insights": meta_insights,
            "energy_level": self.energy_level,
            "interaction_count": self.interaction_count,
            "persona_confidence": self._calculate_confidence(),
            "session_id": self.session_id,
        }

    def _analyze_emotional_content(
        self, text: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """감정적 내용 분석"""
        # 기본 감정 키워드 매칭
        emotion_keywords = {
            "joy": ["기쁘", "행복", "좋", "최고", "성공", "축하", "만족"],
            "sadness": ["슬프", "우울", "힘들", "속상", "실망", "포기", "아쉽"],
            "anger": ["화", "짜증", "분노", "열받", "억울", "불만", "갑갑"],
            "fear": ["무서", "걱정", "불안", "두려", "긴장", "스트레스"],
            "surprise": ["놀라", "와우", "대박", "깜짝", "신기", "의외"],
            "neutral": ["그냥", "보통", "평범", "일반", "괜찮"],
        }

        text_lower = text.lower()
        emotion_scores = {}

        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                # 페르소나 감정 감도 적용
                adjusted_score = score * self.profile.emotion_sensitivity
                emotion_scores[emotion] = adjusted_score

        # 주요 감정 및 강도 결정
        if emotion_scores:
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            raw_intensity = min(emotion_scores[primary_emotion] / 3.0, 1.0)
        else:
            primary_emotion = "neutral"
            raw_intensity = 0.3

        # 페르소나 트리거 적용
        trigger_bonus = self.profile.emotional_triggers.get(primary_emotion, 0)
        final_intensity = min(raw_intensity + trigger_bonus * 0.3, 1.0)

        # 현재 감정 상태 업데이트
        self.current_emotion = primary_emotion
        self.current_emotion_intensity = final_intensity

        return {
            "primary_emotion": primary_emotion,
            "intensity": final_intensity,
            "raw_intensity": raw_intensity,
            "emotion_scores": emotion_scores,
            "trigger_activated": trigger_bonus > 0,
            "intensity_category": self._categorize_intensity(final_intensity),
        }

    def _categorize_intensity(self, intensity: float) -> str:
        """감정 강도 분류"""
        if intensity <= 0.2:
            return EmotionIntensity.MINIMAL.value
        elif intensity <= 0.4:
            return EmotionIntensity.LOW.value
        elif intensity <= 0.6:
            return EmotionIntensity.MODERATE.value
        elif intensity <= 0.8:
            return EmotionIntensity.HIGH.value
        else:
            return EmotionIntensity.INTENSE.value

    def _select_strategy(
        self, emotion_analysis: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """전략 선택"""
        emotion = emotion_analysis["primary_emotion"]
        intensity = emotion_analysis["intensity"]

        # 기본 감정-전략 매핑
        emotion_strategy_map = {
            "joy": "empathetic",
            "sadness": "supportive",
            "anger": "cautious",
            "fear": "reassuring",
            "surprise": "exploratory",
            "neutral": "balanced",
        }

        base_strategy = emotion_strategy_map.get(emotion, "balanced")

        # 페르소나 주요 전략 고려
        if self.profile.primary_strategies:
            # 높은 강도일 때는 페르소나 특성 전략 우선
            if intensity > 0.6:
                strategy = self.profile.primary_strategies[0]
            else:
                # 기본 전략과 페르소나 전략 조합
                strategy = base_strategy
                if base_strategy not in self.profile.primary_strategies:
                    # 페르소나 전략 중 가장 적합한 것 선택
                    strategy = self._find_compatible_strategy(base_strategy)
        else:
            strategy = base_strategy

        # 기억 기반 성공 전략 고려
        successful_strategies = self.memory.successful_strategies
        if successful_strategies:
            best_strategy = max(successful_strategies, key=successful_strategies.get)
            if successful_strategies[best_strategy] > 3:  # 충분한 성공 경험
                strategy = best_strategy

        self.current_strategy = strategy

        return {
            "primary_strategy": strategy,
            "base_strategy": base_strategy,
            "persona_influence": strategy in self.profile.primary_strategies,
            "confidence": self._calculate_strategy_confidence(strategy),
            "alternatives": self._generate_alternative_strategies(emotion, context),
        }

    def _find_compatible_strategy(self, base_strategy: str) -> str:
        """기본 전략과 호환되는 페르소나 전략 찾기"""
        compatibility_map = {
            "empathetic": ["supportive", "nurturing", "caring"],
            "supportive": ["empathetic", "loyal", "reliable"],
            "cautious": ["analytical", "systematic", "careful"],
            "reassuring": ["supportive", "stable", "comforting"],
            "exploratory": ["creative", "adaptive", "curious"],
            "balanced": ["versatile", "flexible", "moderate"],
        }

        compatible = compatibility_map.get(base_strategy, [])

        for strategy in self.profile.primary_strategies:
            if strategy in compatible:
                return strategy

        # 호환되는 것이 없으면 첫 번째 페르소나 전략 사용
        return (
            self.profile.primary_strategies[0]
            if self.profile.primary_strategies
            else base_strategy
        )

    def _determine_response_tone(
        self, emotion_analysis: Dict[str, Any], strategy_selection: Dict[str, Any]
    ) -> str:
        """응답 톤 결정"""
        base_tone = self.profile.response_tone
        emotion = emotion_analysis["primary_emotion"]
        intensity = emotion_analysis["intensity"]
        strategy = strategy_selection["primary_strategy"]

        # 강도가 높을 때 톤 조정
        if intensity > 0.7:
            if emotion in ["anger", "fear"]:
                return "gentle"  # 부드럽게
            elif emotion in ["joy", "surprise"]:
                return "enthusiastic"  # 열정적으로
            elif emotion == "sadness":
                return "compassionate"  # 공감적으로

        # 전략 기반 톤 조정
        strategy_tone_map = {
            "empathetic": "warm",
            "analytical": "objective",
            "supportive": "encouraging",
            "cautious": "measured",
            "creative": "inspiring",
        }

        return strategy_tone_map.get(strategy, base_tone)

    def _generate_meta_insights(
        self, text: str, context: Dict[str, Any], emotion_analysis: Dict[str, Any]
    ) -> List[str]:
        """메타인지적 인사이트 생성"""
        insights = []

        # 페르소나 자기 인식
        if self.profile.meta_awareness_level > 0.5:
            insights.append(
                f"페르소나 '{self.profile.name}'로서 {emotion_analysis['primary_emotion']} 감정을 감지했습니다."
            )

        # 전략 선택 이유
        if self.profile.self_reflection_frequency > 0.4:
            insights.append(
                f"현재 상황에서 {self.current_strategy} 접근이 적절하다고 판단합니다."
            )

        # 학습 기회 인식
        if self.learning_momentum > 0.6:
            insights.append("이 상호작용을 통해 새로운 패턴을 학습할 기회입니다.")

        # 에너지 수준 고려
        if self.energy_level < 0.3:
            insights.append("현재 에너지 수준이 낮아 간단한 접근을 권장합니다.")

        return insights

    def _adaptive_learning(self):
        """적응적 학습 수행"""
        if self.state != PersonaState.LEARNING:
            previous_state = self.state
            self.state = PersonaState.LEARNING

            # 최근 상호작용 패턴 분석
            self._analyze_interaction_patterns()

            # 감정 패턴 학습
            self._learn_emotional_patterns()

            # 전략 효과성 평가
            self._evaluate_strategy_effectiveness()

            # 적응 수행
            if self._should_adapt():
                self._perform_adaptation()

            self.adaptation_cycles += 1
            self.state = previous_state

            print(
                f"🧠 페르소나 '{self.profile.name}' 적응적 학습 완료 (사이클 {self.adaptation_cycles})"
            )

    def _analyze_interaction_patterns(self):
        """상호작용 패턴 분석"""
        recent_interactions = list(self.memory.recent_interactions)

        if len(recent_interactions) < 3:
            return

        # 감정 변화 패턴
        emotions = [
            interaction["emotion_detected"] for interaction in recent_interactions[-5:]
        ]
        emotion_transitions = list(zip(emotions[:-1], emotions[1:]))

        # 전략 사용 빈도
        strategies = [
            interaction["strategy_selected"] for interaction in recent_interactions[-5:]
        ]
        strategy_frequency = {}
        for strategy in strategies:
            strategy_frequency[strategy] = strategy_frequency.get(strategy, 0) + 1

        # 인사이트 생성
        if len(set(emotions)) == 1 and len(emotions) > 2:
            self.memory.learning_insights.append(
                f"최근 {emotions[0]} 감정이 지속되고 있습니다."
            )

        if strategy_frequency:
            most_used = max(strategy_frequency, key=strategy_frequency.get)
            if strategy_frequency[most_used] > 3:
                self.memory.learning_insights.append(
                    f"{most_used} 전략을 자주 사용하고 있습니다."
                )

    def _learn_emotional_patterns(self):
        """감정 패턴 학습"""
        for emotion, intensities in self.memory.emotional_patterns.items():
            if len(intensities) >= 3:
                avg_intensity = sum(intensities) / len(intensities)

                # 특정 감정에 대한 반응성 조정
                if emotion in self.profile.emotional_triggers:
                    current_trigger = self.profile.emotional_triggers[emotion]
                    # 학습률 적용하여 점진적 조정
                    adjusted_trigger = (
                        current_trigger * (1 - self.profile.learning_rate)
                        + avg_intensity * self.profile.learning_rate
                    )
                    self.profile.emotional_triggers[emotion] = min(
                        1.0, adjusted_trigger
                    )

    def _evaluate_strategy_effectiveness(self):
        """전략 효과성 평가"""
        # 실제 구현에서는 피드백 데이터를 기반으로 전략 성공률 계산
        # 현재는 모의 평가
        for strategy in self.profile.primary_strategies:
            if strategy in self.memory.successful_strategies:
                success_count = self.memory.successful_strategies[strategy]
                if success_count > 5:  # 충분한 데이터
                    # 성공률이 높은 전략을 주요 전략으로 유지
                    continue
                elif success_count < 2:  # 성공률이 낮은 전략
                    # 대안 전략 고려
                    self._suggest_alternative_strategy(strategy)

    def _suggest_alternative_strategy(self, ineffective_strategy: str):
        """비효과적 전략에 대한 대안 제안"""
        alternative_strategies = {
            "empathetic": "supportive",
            "analytical": "systematic",
            "creative": "adaptive",
            "cautious": "balanced",
        }

        alternative = alternative_strategies.get(ineffective_strategy)
        if alternative and alternative not in self.profile.primary_strategies:
            self.memory.learning_insights.append(
                f"{ineffective_strategy} 전략 대신 {alternative} 전략 고려 중"
            )

    def _should_adapt(self) -> bool:
        """적응 필요성 판단"""
        # 적응성 수준과 학습 데이터량 기반 결정
        return (
            self.profile.adaptability > 0.5
            and len(self.memory.recent_interactions) > 10
            and self.adaptation_cycles < 5
        )  # 과도한 적응 방지

    def _perform_adaptation(self):
        """실제 적응 수행"""
        self.state = PersonaState.ADAPTING

        adaptation_record = {
            "timestamp": datetime.now().isoformat(),
            "cycle": self.adaptation_cycles,
            "changes": [],
        }

        # 감정 감도 조정
        if self.current_emotion_intensity > 0.8:
            # 강한 감정에 노출이 많으면 감도 약간 낮춤
            old_sensitivity = self.profile.emotion_sensitivity
            self.profile.emotion_sensitivity = max(0.1, old_sensitivity - 0.1)
            adaptation_record["changes"].append(
                f"감정 감도: {old_sensitivity:.2f} → {self.profile.emotion_sensitivity:.2f}"
            )

        # 에너지 수준 조정
        if self.interaction_count > 20:
            self.energy_level = max(0.3, self.energy_level - 0.1)
            adaptation_record["changes"].append(f"에너지 수준: {self.energy_level:.2f}")

        self.memory.adaptation_history.append(adaptation_record)
        print(f"🔄 페르소나 적응 완료: {len(adaptation_record['changes'])}개 변경사항")

    def _should_reflect(self) -> bool:
        """자기 반성 필요성 판단"""
        time_since_reflection = datetime.now() - self.last_reflection
        reflection_interval = timedelta(minutes=30)  # 30분마다

        return (
            time_since_reflection > reflection_interval
            and self.profile.self_reflection_frequency > 0.3
        )

    def _perform_self_reflection(self):
        """자기 반성 수행"""
        self.state = PersonaState.REFLECTION

        # 성과 분석
        if self.interaction_count > 0:
            self.success_rate = min(self.energy_level, 1.0)  # 단순화된 성공률

        # 인사이트 정리
        if len(self.memory.learning_insights) > 5:
            # 오래된 인사이트 정리
            self.memory.learning_insights = self.memory.learning_insights[-5:]

        # 메타인지 강화
        self.insights_generated += 1
        self.learning_momentum = min(1.0, self.learning_momentum + 0.1)

        self.last_reflection = datetime.now()
        print(
            f"🤔 페르소나 '{self.profile.name}' 자기 반성 완료 (인사이트: {self.insights_generated})"
        )

        self.state = PersonaState.ACTIVE

    def _calculate_confidence(self) -> float:
        """페르소나 신뢰도 계산"""
        base_confidence = 0.5

        # 상호작용 경험 기반
        experience_factor = min(self.interaction_count / 50.0, 0.3)

        # 에너지 수준 기반
        energy_factor = self.energy_level * 0.2

        # 학습 모멘텀 기반
        learning_factor = self.learning_momentum * 0.2

        # 적응 성공 기반
        adaptation_factor = min(self.adaptation_cycles / 10.0, 0.1)

        total_confidence = (
            base_confidence
            + experience_factor
            + energy_factor
            + learning_factor
            + adaptation_factor
        )

        return min(1.0, total_confidence)

    def _calculate_strategy_confidence(self, strategy: str) -> float:
        """전략별 신뢰도 계산"""
        base_confidence = 0.6

        # 페르소나 주요 전략인지 확인
        if strategy in self.profile.primary_strategies:
            base_confidence += 0.2

        # 과거 성공 경험
        if strategy in self.memory.successful_strategies:
            success_count = self.memory.successful_strategies[strategy]
            success_factor = min(success_count / 10.0, 0.2)
            base_confidence += success_factor

        return min(1.0, base_confidence)

    def _generate_alternative_strategies(
        self, emotion: str, context: Dict[str, Any]
    ) -> List[str]:
        """대안 전략 생성"""
        alternatives = []

        # 페르소나 전략 중 현재 전략이 아닌 것들
        for strategy in self.profile.primary_strategies:
            if strategy != self.current_strategy:
                alternatives.append(strategy)

        # 감정별 추가 전략
        emotion_alternatives = {
            "joy": ["celebratory", "sharing"],
            "sadness": ["comforting", "healing"],
            "anger": ["calming", "redirecting"],
            "fear": ["protective", "empowering"],
            "surprise": ["investigating", "clarifying"],
        }

        if emotion in emotion_alternatives:
            alternatives.extend(emotion_alternatives[emotion])

        return alternatives[:3]  # 최대 3개

    def get_status(self) -> Dict[str, Any]:
        """페르소나 상태 정보 반환"""
        return {
            "name": self.profile.name,
            "signature_type": self.profile.signature_type,
            "state": self.state.value,
            "current_emotion": self.current_emotion,
            "emotion_intensity": self.current_emotion_intensity,
            "current_strategy": self.current_strategy,
            "energy_level": self.energy_level,
            "interaction_count": self.interaction_count,
            "success_rate": self.success_rate,
            "adaptation_cycles": self.adaptation_cycles,
            "insights_generated": self.insights_generated,
            "learning_momentum": self.learning_momentum,
            "confidence": self._calculate_confidence(),
            "primary_strategies": self.profile.primary_strategies,
            "emotional_triggers": self.profile.emotional_triggers,
            "recent_insights": self.memory.learning_insights[-3:],
        }

    def save_state(self, file_path: str):
        """페르소나 상태 저장"""
        state_data = {
            "profile": {
                "name": self.profile.name,
                "signature_type": self.profile.signature_type,
                "emotion_sensitivity": self.profile.emotion_sensitivity,
                "reasoning_depth": self.profile.reasoning_depth,
                "response_tone": self.profile.response_tone,
                "decision_style": self.profile.decision_style,
                "adaptability": self.profile.adaptability,
                "learning_rate": self.profile.learning_rate,
                "memory_retention": self.profile.memory_retention,
                "primary_strategies": self.profile.primary_strategies,
                "emotional_triggers": self.profile.emotional_triggers,
                "communication_patterns": self.profile.communication_patterns,
                "self_reflection_frequency": self.profile.self_reflection_frequency,
                "meta_awareness_level": self.profile.meta_awareness_level,
                "growth_orientation": self.profile.growth_orientation,
            },
            "current_state": {
                "state": self.state.value,
                "current_emotion": self.current_emotion,
                "current_emotion_intensity": self.current_emotion_intensity,
                "current_strategy": self.current_strategy,
                "energy_level": self.energy_level,
                "interaction_count": self.interaction_count,
                "success_rate": self.success_rate,
                "adaptation_cycles": self.adaptation_cycles,
                "insights_generated": self.insights_generated,
                "learning_momentum": self.learning_momentum,
                "last_reflection": self.last_reflection.isoformat(),
            },
            "memory": {
                "recent_interactions": list(self.memory.recent_interactions),
                "emotional_patterns": self.memory.emotional_patterns,
                "successful_strategies": self.memory.successful_strategies,
                "learning_insights": self.memory.learning_insights,
                "adaptation_history": self.memory.adaptation_history,
            },
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)

        print(f"💾 페르소나 상태 저장 완료: {file_path}")


# 편의 함수들
def create_persona_from_signature(signature_type: str, name: str = None) -> PersonaCore:
    """시그니처 타입으로부터 페르소나 생성"""
    if not name:
        name = f"Persona-{signature_type.split('-')[1]}"

    profile = PersonaProfile(name=name, signature_type=signature_type)

    return PersonaCore(profile)


def load_persona_profiles() -> Dict[str, PersonaProfile]:
    """모든 시그니처 기반 페르소나 프로필 로드"""
    profiles = {}

    signature_types = ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"]

    for sig_type in signature_types:
        profile = PersonaProfile(
            name=f"Persona-{sig_type.split('-')[1]}", signature_type=sig_type
        )
        profiles[sig_type] = profile

    return profiles


# 전역 페르소나 관리
_active_persona = None
_persona_registry = {}


def get_active_persona():
    """현재 활성 페르소나 반환"""
    return _active_persona


def switch_persona(signature_name: str) -> bool:
    """페르소나 전환"""
    global _active_persona

    try:
        if signature_name not in _persona_registry:
            # 새 페르소나 생성
            persona = create_persona_from_signature(
                signature_name, signature_name.split("-")[-1]
            )
            _persona_registry[signature_name] = persona

        _active_persona = _persona_registry[signature_name]
        return True
    except Exception as e:
        print(f"페르소나 전환 실패: {e}")
        return False


def initialize_default_persona():
    """기본 페르소나 초기화"""
    global _active_persona
    if _active_persona is None:
        switch_persona("Echo-Aurora")


# 기본 페르소나 초기화
initialize_default_persona()

if __name__ == "__main__":
    # 테스트 코드
    print("🧠 페르소나 코어 테스트")
    print("=" * 50)

    # Phoenix 페르소나 생성
    phoenix_persona = create_persona_from_signature("Echo-Phoenix", "Phoenix")

    # 테스트 상호작용
    test_inputs = [
        (
            "오늘 실패했지만 다시 도전하고 싶어요",
            {"context_type": "personal", "urgency": "normal"},
        ),
        (
            "새로운 프로젝트를 시작하려는데 어려움이 많네요",
            {"context_type": "work", "urgency": "high"},
        ),
        (
            "친구와 갈등이 있어서 힘들어요",
            {"context_type": "relationship", "urgency": "normal"},
        ),
    ]

    for i, (text, context) in enumerate(test_inputs, 1):
        print(f"\n=== 테스트 {i} ===")
        print(f"입력: {text}")

        result = phoenix_persona.process_input(text, context)

        print(
            f"감정 분석: {result['emotion_analysis']['primary_emotion']} (강도: {result['emotion_analysis']['intensity']:.3f})"
        )
        print(f"전략 선택: {result['strategy_selection']['primary_strategy']}")
        print(f"응답 톤: {result['response_tone']}")
        print(f"메타 인사이트: {result['meta_insights']}")
        print(f"페르소나 신뢰도: {result['persona_confidence']:.3f}")

    # 최종 상태
    print(f"\n📊 최종 페르소나 상태:")
    status = phoenix_persona.get_status()
    for key, value in status.items():
        if isinstance(value, (int, float)):
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")
        elif isinstance(value, list) and len(value) <= 5:
            print(f"  {key}: {value}")
        elif isinstance(value, dict) and len(value) <= 5:
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: {type(value).__name__}")
