#!/usr/bin/env python3
"""
🧠 Context Inference Engine
대화 맥락 추론 및 유지 엔진

핵심 기능:
1. 대화 흐름 및 맥락 기억
2. 이전 대화 내용 기반 컨텍스트 추론
3. 감정 변화 패턴 추적
4. 주제 연속성 및 전환 감지
5. 시그니처별 관계 형성 패턴 학습
"""

import json
import pickle
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import re


class ContextType(Enum):
    """컨텍스트 타입"""

    EMOTIONAL_CONTINUITY = "emotional_continuity"  # 감정 연속성
    TOPIC_THREAD = "topic_thread"  # 주제 스레드
    RELATIONSHIP_BUILDING = "relationship_building"  # 관계 형성
    CRISIS_PATTERN = "crisis_pattern"  # 위기 패턴
    GROWTH_JOURNEY = "growth_journey"  # 성장 여정
    DECISION_PROCESS = "decision_process"  # 의사결정 과정


@dataclass
class ConversationTurn:
    """대화 턴"""

    turn_id: str
    timestamp: datetime
    user_input: str
    user_emotion: str
    user_intent: str
    system_response: str
    signature_used: str
    confidence: float
    key_themes: List[str]
    urgency_level: int
    meta_data: Dict[str, Any]


@dataclass
class ContextualInsight:
    """맥락적 통찰"""

    insight_type: ContextType
    description: str
    evidence: List[str]
    confidence: float
    relevance_score: float
    suggested_approach: str
    temporal_span: Tuple[datetime, datetime]


@dataclass
class RelationshipState:
    """관계 상태"""

    trust_level: float
    intimacy_level: float
    communication_pattern: str
    preferred_signature: str
    interaction_history: List[str]
    growth_indicators: List[str]
    support_needs: List[str]


class ContextInferenceEngine:
    """대화 맥락 추론 엔진"""

    def __init__(self, memory_depth: int = 50, context_window: int = 10):
        self.memory_depth = memory_depth
        self.context_window = context_window

        # 세션별 대화 기록
        self.conversation_histories: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=memory_depth)
        )

        # 세션별 관계 상태
        self.relationship_states: Dict[str, RelationshipState] = {}

        # 컨텍스트 패턴 사전
        self.context_patterns = self._load_context_patterns()

        # 감정 전환 패턴
        self.emotion_transition_patterns = self._load_emotion_patterns()

        # 주제 연관성 맵
        self.topic_associations = self._load_topic_associations()

    def infer_context(
        self, session_id: str, current_turn: ConversationTurn
    ) -> List[ContextualInsight]:
        """현재 대화 턴을 기반으로 맥락 추론"""

        # 대화 기록에 현재 턴 추가
        self.conversation_histories[session_id].append(current_turn)

        # 관계 상태 업데이트
        self._update_relationship_state(session_id, current_turn)

        insights = []

        # 1. 감정 연속성 분석
        emotional_insight = self._analyze_emotional_continuity(session_id)
        if emotional_insight:
            insights.append(emotional_insight)

        # 2. 주제 스레드 분석
        topic_insight = self._analyze_topic_thread(session_id)
        if topic_insight:
            insights.append(topic_insight)

        # 3. 관계 형성 패턴 분석
        relationship_insight = self._analyze_relationship_building(session_id)
        if relationship_insight:
            insights.append(relationship_insight)

        # 4. 위기 패턴 감지
        crisis_insight = self._detect_crisis_pattern(session_id)
        if crisis_insight:
            insights.append(crisis_insight)

        # 5. 성장 여정 추적
        growth_insight = self._track_growth_journey(session_id)
        if growth_insight:
            insights.append(growth_insight)

        # 6. 의사결정 과정 분석
        decision_insight = self._analyze_decision_process(session_id)
        if decision_insight:
            insights.append(decision_insight)

        return insights

    def get_contextual_suggestions(
        self, session_id: str, current_emotion: str
    ) -> Dict[str, Any]:
        """맥락 기반 응답 제안"""

        history = list(self.conversation_histories[session_id])
        if not history:
            return {"suggestions": [], "context_aware": False}

        suggestions = {
            "response_style": self._suggest_response_style(session_id, current_emotion),
            "conversation_flow": self._suggest_conversation_flow(session_id),
            "emotional_approach": self._suggest_emotional_approach(
                session_id, current_emotion
            ),
            "reference_points": self._identify_reference_points(session_id),
            "relationship_status": self._assess_relationship_status(session_id),
            "context_aware": True,
        }

        return suggestions

    def _analyze_emotional_continuity(
        self, session_id: str
    ) -> Optional[ContextualInsight]:
        """감정 연속성 분석"""

        history = list(self.conversation_histories[session_id])
        if len(history) < 2:
            return None

        recent_emotions = [turn.user_emotion for turn in history[-5:]]
        emotion_pattern = " -> ".join(recent_emotions[-3:])

        # 감정 패턴 분석
        if len(set(recent_emotions)) == 1:
            # 지속적인 감정
            persistent_emotion = recent_emotions[0]
            return ContextualInsight(
                insight_type=ContextType.EMOTIONAL_CONTINUITY,
                description=f"지속적인 {persistent_emotion} 감정 상태 감지",
                evidence=[f"최근 {len(recent_emotions)}턴 동안 일관된 감정"],
                confidence=0.8,
                relevance_score=0.9,
                suggested_approach=f"지속적인 {persistent_emotion}에 대한 깊이 있는 접근 필요",
                temporal_span=(
                    history[-len(recent_emotions)].timestamp,
                    history[-1].timestamp,
                ),
            )

        elif self._is_emotional_escalation(recent_emotions):
            # 감정 강화 패턴
            return ContextualInsight(
                insight_type=ContextType.EMOTIONAL_CONTINUITY,
                description="감정 강화 패턴 감지",
                evidence=[f"감정 패턴: {emotion_pattern}"],
                confidence=0.7,
                relevance_score=0.8,
                suggested_approach="감정 조절 및 안정화 접근",
                temporal_span=(history[-3].timestamp, history[-1].timestamp),
            )

        elif self._is_emotional_recovery(recent_emotions):
            # 감정 회복 패턴
            return ContextualInsight(
                insight_type=ContextType.EMOTIONAL_CONTINUITY,
                description="감정 회복 패턴 감지",
                evidence=[f"감정 패턴: {emotion_pattern}"],
                confidence=0.7,
                relevance_score=0.8,
                suggested_approach="긍정적 변화 강화 및 지지",
                temporal_span=(history[-3].timestamp, history[-1].timestamp),
            )

        return None

    def _analyze_topic_thread(self, session_id: str) -> Optional[ContextualInsight]:
        """주제 스레드 분석"""

        history = list(self.conversation_histories[session_id])
        if len(history) < 2:
            return None

        # 최근 대화의 주제 추출
        recent_themes = []
        for turn in history[-5:]:
            recent_themes.extend(turn.key_themes)

        # 주제 빈도 계산
        theme_frequency = defaultdict(int)
        for theme in recent_themes:
            theme_frequency[theme] += 1

        # 지배적 주제 식별
        if theme_frequency:
            dominant_theme = max(theme_frequency, key=theme_frequency.get)
            theme_count = theme_frequency[dominant_theme]

            if theme_count >= 3:
                return ContextualInsight(
                    insight_type=ContextType.TOPIC_THREAD,
                    description=f"'{dominant_theme}' 주제에 대한 지속적인 관심",
                    evidence=[f"최근 대화에서 {theme_count}회 언급"],
                    confidence=0.8,
                    relevance_score=0.7,
                    suggested_approach=f"{dominant_theme} 관련 심화 탐구 제안",
                    temporal_span=(history[-5].timestamp, history[-1].timestamp),
                )

        return None

    def _analyze_relationship_building(
        self, session_id: str
    ) -> Optional[ContextualInsight]:
        """관계 형성 패턴 분석"""

        if session_id not in self.relationship_states:
            return None

        relationship = self.relationship_states[session_id]
        history = list(self.conversation_histories[session_id])

        # 신뢰도 변화 추적
        if len(history) >= 5:
            recent_interactions = [turn.confidence for turn in history[-5:]]
            avg_recent_confidence = sum(recent_interactions) / len(recent_interactions)

            if avg_recent_confidence > 0.7 and relationship.trust_level < 0.8:
                return ContextualInsight(
                    insight_type=ContextType.RELATIONSHIP_BUILDING,
                    description="신뢰 관계 형성 중",
                    evidence=[f"최근 상호작용 신뢰도: {avg_recent_confidence:.2f}"],
                    confidence=0.8,
                    relevance_score=0.6,
                    suggested_approach="관계 심화를 위한 개인적 접근 시도",
                    temporal_span=(history[-5].timestamp, history[-1].timestamp),
                )

        return None

    def _detect_crisis_pattern(self, session_id: str) -> Optional[ContextualInsight]:
        """위기 패턴 감지"""

        history = list(self.conversation_histories[session_id])
        if len(history) < 2:
            return None

        # 긴급도 패턴 분석
        recent_urgencies = [turn.urgency_level for turn in history[-3:]]

        if any(urgency >= 4 for urgency in recent_urgencies):
            high_urgency_count = sum(1 for u in recent_urgencies if u >= 4)

            return ContextualInsight(
                insight_type=ContextType.CRISIS_PATTERN,
                description="위기 상황 패턴 감지",
                evidence=[f"최근 {high_urgency_count}회 고위험 상황"],
                confidence=0.9,
                relevance_score=1.0,
                suggested_approach="즉시 전문적 지원 및 안전 확보 프로토콜 활성화",
                temporal_span=(
                    history[-len(recent_urgencies)].timestamp,
                    history[-1].timestamp,
                ),
            )

        return None

    def _track_growth_journey(self, session_id: str) -> Optional[ContextualInsight]:
        """성장 여정 추적"""

        history = list(self.conversation_histories[session_id])
        if len(history) < 5:
            return None

        # 감정 변화를 통한 성장 패턴 감지
        emotion_timeline = [(turn.timestamp, turn.user_emotion) for turn in history]

        # 부정적 → 긍정적 감정 전환 패턴 찾기
        growth_indicators = []
        for i in range(1, len(emotion_timeline)):
            prev_emotion = emotion_timeline[i - 1][1]
            curr_emotion = emotion_timeline[i][1]

            if prev_emotion in ["sadness", "anxiety", "anger"] and curr_emotion in [
                "hope",
                "joy",
                "curiosity",
            ]:
                growth_indicators.append(f"{prev_emotion} → {curr_emotion}")

        if len(growth_indicators) >= 2:
            return ContextualInsight(
                insight_type=ContextType.GROWTH_JOURNEY,
                description="긍정적 변화 및 성장 패턴 감지",
                evidence=growth_indicators,
                confidence=0.7,
                relevance_score=0.8,
                suggested_approach="성장 과정 인정 및 추가 발전 방향 탐구",
                temporal_span=(history[0].timestamp, history[-1].timestamp),
            )

        return None

    def _analyze_decision_process(self, session_id: str) -> Optional[ContextualInsight]:
        """의사결정 과정 분석"""

        history = list(self.conversation_histories[session_id])
        decision_related_turns = [
            turn
            for turn in history
            if turn.user_intent in ["decision_help", "situation_analysis"]
        ]

        if len(decision_related_turns) >= 2:
            recent_decision_turns = decision_related_turns[-3:]

            # 의사결정 주제 일관성 확인
            decision_themes = []
            for turn in recent_decision_turns:
                decision_themes.extend(turn.key_themes)

            theme_consistency = (
                len(set(decision_themes)) / len(decision_themes)
                if decision_themes
                else 1
            )

            if theme_consistency < 0.5:  # 높은 주제 일관성
                return ContextualInsight(
                    insight_type=ContextType.DECISION_PROCESS,
                    description="일관된 의사결정 과정 진행 중",
                    evidence=[f"관련 대화 {len(recent_decision_turns)}회"],
                    confidence=0.8,
                    relevance_score=0.7,
                    suggested_approach="체계적 의사결정 지원 및 명확화 도움",
                    temporal_span=(
                        recent_decision_turns[0].timestamp,
                        recent_decision_turns[-1].timestamp,
                    ),
                )

        return None

    def _update_relationship_state(
        self, session_id: str, current_turn: ConversationTurn
    ):
        """관계 상태 업데이트"""

        if session_id not in self.relationship_states:
            self.relationship_states[session_id] = RelationshipState(
                trust_level=0.3,
                intimacy_level=0.2,
                communication_pattern="initial",
                preferred_signature="",
                interaction_history=[],
                growth_indicators=[],
                support_needs=[],
            )

        relationship = self.relationship_states[session_id]

        # 신뢰도 업데이트
        if current_turn.confidence > 0.7:
            relationship.trust_level = min(1.0, relationship.trust_level + 0.1)
        elif current_turn.confidence < 0.4:
            relationship.trust_level = max(0.0, relationship.trust_level - 0.05)

        # 친밀도 업데이트
        personal_indicators = ["자신", "내", "마음", "느낌", "생각"]
        if any(
            indicator in current_turn.user_input for indicator in personal_indicators
        ):
            relationship.intimacy_level = min(1.0, relationship.intimacy_level + 0.1)

        # 선호 시그니처 학습
        relationship.interaction_history.append(current_turn.signature_used)
        if len(relationship.interaction_history) > 10:
            relationship.interaction_history = relationship.interaction_history[-10:]

        # 가장 자주 사용되고 높은 신뢰도를 보인 시그니처 식별
        signature_performance = defaultdict(list)
        history = list(self.conversation_histories[session_id])

        for turn in history[-10:]:
            signature_performance[turn.signature_used].append(turn.confidence)

        if signature_performance:
            best_signature = max(
                signature_performance.keys(),
                key=lambda s: sum(signature_performance[s])
                / len(signature_performance[s]),
            )
            relationship.preferred_signature = best_signature

    def _suggest_response_style(self, session_id: str, current_emotion: str) -> str:
        """응답 스타일 제안"""

        if session_id not in self.relationship_states:
            return "empathetic"

        relationship = self.relationship_states[session_id]

        if relationship.trust_level > 0.7:
            return "intimate"
        elif relationship.trust_level > 0.4:
            return "supportive"
        else:
            return "careful"

    def _suggest_conversation_flow(self, session_id: str) -> str:
        """대화 흐름 제안"""

        history = list(self.conversation_histories[session_id])
        if not history:
            return "exploratory"

        recent_intents = [turn.user_intent for turn in history[-3:]]

        if "crisis_intervention" in recent_intents:
            return "supportive_immediate"
        elif "decision_help" in recent_intents:
            return "analytical_structured"
        elif "emotional_support" in recent_intents:
            return "empathetic_flowing"
        else:
            return "conversational_adaptive"

    def _suggest_emotional_approach(self, session_id: str, current_emotion: str) -> str:
        """감정적 접근 제안"""

        history = list(self.conversation_histories[session_id])
        if len(history) < 2:
            return "gentle_exploration"

        emotion_history = [turn.user_emotion for turn in history[-5:]]

        if current_emotion in emotion_history[:-1]:
            return "pattern_acknowledgment"
        elif current_emotion in ["sadness", "anxiety", "despair"]:
            return "stabilizing_support"
        elif current_emotion in ["joy", "hope", "curiosity"]:
            return "amplifying_positive"
        else:
            return "neutral_exploration"

    def _identify_reference_points(self, session_id: str) -> List[str]:
        """참조 포인트 식별"""

        history = list(self.conversation_histories[session_id])
        references = []

        for turn in history[-5:]:
            # 시간 참조
            if any(
                time_word in turn.user_input
                for time_word in ["어제", "오늘", "지난번", "전에"]
            ):
                references.append(f"시간참조_{turn.turn_id}")

            # 관계 참조
            if any(
                relation in turn.user_input
                for relation in ["친구", "가족", "동료", "그 사람"]
            ):
                references.append(f"관계참조_{turn.turn_id}")

            # 주제 연속성
            if turn.key_themes:
                for theme in turn.key_themes:
                    references.append(f"주제_{theme}_{turn.turn_id}")

        return references

    def _assess_relationship_status(self, session_id: str) -> Dict[str, float]:
        """관계 상태 평가"""

        if session_id not in self.relationship_states:
            return {"trust": 0.3, "intimacy": 0.2, "stability": 0.5}

        relationship = self.relationship_states[session_id]

        # 안정성 계산 (대화 일관성 기반)
        history = list(self.conversation_histories[session_id])
        if len(history) > 1:
            confidence_variance = sum(
                abs(history[i].confidence - history[i - 1].confidence)
                for i in range(1, min(len(history), 5))
            ) / min(len(history) - 1, 4)
            stability = max(0.0, 1.0 - confidence_variance)
        else:
            stability = 0.5

        return {
            "trust": relationship.trust_level,
            "intimacy": relationship.intimacy_level,
            "stability": stability,
        }

    def _is_emotional_escalation(self, emotions: List[str]) -> bool:
        """감정 강화 패턴 감지"""
        intensity_map = {
            "neutral": 0,
            "curiosity": 1,
            "hope": 2,
            "joy": 3,
            "excitement": 4,
            "confusion": 1,
            "concern": 2,
            "anxiety": 3,
            "fear": 4,
            "panic": 5,
            "sadness": 2,
            "grief": 4,
            "despair": 5,
            "annoyance": 1,
            "anger": 3,
            "rage": 5,
        }

        intensities = [intensity_map.get(emotion, 0) for emotion in emotions]

        if len(intensities) < 2:
            return False

        # 연속적인 강화 패턴 확인
        escalation_count = 0
        for i in range(1, len(intensities)):
            if intensities[i] > intensities[i - 1]:
                escalation_count += 1

        return escalation_count >= len(intensities) // 2

    def _is_emotional_recovery(self, emotions: List[str]) -> bool:
        """감정 회복 패턴 감지"""
        negative_emotions = {"sadness", "anxiety", "anger", "despair", "fear", "grief"}
        positive_emotions = {"joy", "hope", "curiosity", "excitement", "contentment"}

        if len(emotions) < 2:
            return False

        # 부정적 → 긍정적 전환 확인
        has_negative_start = any(
            emotion in negative_emotions for emotion in emotions[:2]
        )
        has_positive_end = any(
            emotion in positive_emotions for emotion in emotions[-2:]
        )

        return has_negative_start and has_positive_end

    def _load_context_patterns(self) -> Dict[str, Any]:
        """컨텍스트 패턴 로드"""
        # 실제 구현에서는 파일에서 로드
        return {
            "emotional_transitions": {
                "crisis_to_hope": [
                    "despair -> anxiety -> hope",
                    "fear -> confusion -> curiosity",
                ],
                "growth_patterns": ["sadness -> reflection -> acceptance -> hope"],
            },
            "topic_clusters": {
                "work_life": ["career", "job", "work", "colleague", "boss"],
                "relationships": [
                    "family",
                    "friend",
                    "partner",
                    "relationship",
                    "social",
                ],
            },
        }

    def _load_emotion_patterns(self) -> Dict[str, List[str]]:
        """감정 전환 패턴 로드"""
        return {
            "healthy_transitions": [
                "sadness -> acceptance",
                "anger -> understanding",
                "anxiety -> curiosity",
                "despair -> hope",
            ],
            "concerning_patterns": [
                "hope -> despair",
                "joy -> sadness",
                "curiosity -> anxiety",
            ],
        }

    def _load_topic_associations(self) -> Dict[str, List[str]]:
        """주제 연관성 맵 로드"""
        return {
            "work": ["career", "job", "stress", "achievement", "money"],
            "relationships": ["family", "friend", "love", "social", "trust"],
            "health": ["body", "mind", "wellness", "exercise", "sleep"],
            "growth": ["learning", "development", "goals", "future", "change"],
        }

    def save_context_state(self, filepath: str):
        """컨텍스트 상태 저장"""
        state_data = {
            "conversation_histories": {
                session_id: [asdict(turn) for turn in history]
                for session_id, history in self.conversation_histories.items()
            },
            "relationship_states": {
                session_id: asdict(state)
                for session_id, state in self.relationship_states.items()
            },
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state_data, f, ensure_ascii=False, indent=2, default=str)

    def load_context_state(self, filepath: str):
        """컨텍스트 상태 로드"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                state_data = json.load(f)

            # 대화 기록 복원
            for session_id, turns_data in state_data.get(
                "conversation_histories", {}
            ).items():
                turns = []
                for turn_data in turns_data:
                    turn_data["timestamp"] = datetime.fromisoformat(
                        turn_data["timestamp"]
                    )
                    turns.append(ConversationTurn(**turn_data))
                self.conversation_histories[session_id] = deque(
                    turns, maxlen=self.memory_depth
                )

            # 관계 상태 복원
            for session_id, state_data in state_data.get(
                "relationship_states", {}
            ).items():
                self.relationship_states[session_id] = RelationshipState(**state_data)

        except FileNotFoundError:
            print(f"Context state file not found: {filepath}")
        except Exception as e:
            print(f"Error loading context state: {e}")


if __name__ == "__main__":
    # 테스트
    engine = ContextInferenceEngine()

    # 샘플 대화 턴들
    sample_turns = [
        ConversationTurn(
            turn_id="1",
            timestamp=datetime.now() - timedelta(minutes=10),
            user_input="요즘 일이 너무 힘들어",
            user_emotion="sadness",
            user_intent="emotional_support",
            system_response="힘든 상황이시군요",
            signature_used="Echo-Aurora",
            confidence=0.7,
            key_themes=["work", "stress"],
            urgency_level=2,
            meta_data={},
        ),
        ConversationTurn(
            turn_id="2",
            timestamp=datetime.now() - timedelta(minutes=5),
            user_input="정말 그만두고 싶어",
            user_emotion="despair",
            user_intent="emotional_support",
            system_response="그런 마음이 드는 게 이해돼",
            signature_used="Echo-Aurora",
            confidence=0.8,
            key_themes=["work", "decision"],
            urgency_level=3,
            meta_data={},
        ),
        ConversationTurn(
            turn_id="3",
            timestamp=datetime.now(),
            user_input="하지만 새로운 기회도 있을 것 같아",
            user_emotion="hope",
            user_intent="decision_help",
            system_response="희망적인 관점이네요",
            signature_used="Echo-Phoenix",
            confidence=0.8,
            key_themes=["work", "future", "opportunity"],
            urgency_level=1,
            meta_data={},
        ),
    ]

    session_id = "test_session"

    print("🧠 Context Inference Engine 테스트:")
    print("=" * 50)

    for i, turn in enumerate(sample_turns):
        print(f"\n--- 턴 {i+1} ---")
        print(f"입력: {turn.user_input}")
        print(f"감정: {turn.user_emotion} | 의도: {turn.user_intent}")

        insights = engine.infer_context(session_id, turn)

        if insights:
            print("컨텍스트 통찰:")
            for insight in insights:
                print(f"  - {insight.insight_type.value}: {insight.description}")
                print(
                    f"    신뢰도: {insight.confidence:.2f}, 제안: {insight.suggested_approach}"
                )

        suggestions = engine.get_contextual_suggestions(session_id, turn.user_emotion)
        print(f"제안된 응답 스타일: {suggestions['response_style']}")
        print(f"대화 흐름: {suggestions['conversation_flow']}")

    print("\n" + "=" * 50)
    print("관계 상태:", engine._assess_relationship_status(session_id))
