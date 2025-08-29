#!/usr/bin/env python3
"""
🎯 Intent Inference Engine - Enhanced
발화 유형/리듬 분류 강화 시스템

핵심 기능:
1. 세밀한 발화 의도 분류 (12가지 유형)
2. 사용자 리듬 패턴 감지 및 학습
3. 맥락 기반 의도 추론
4. 감정-의도 상관관계 분석
"""

import re
import json
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque


class DetailedIntentType(Enum):
    """세밀한 의도 분류"""

    # 기본 의도들
    CASUAL_GREETING = "casual_greeting"  # 일상적 인사
    CASUAL_CHAT = "casual_chat"  # 일상 대화
    EMOTIONAL_SUPPORT = "emotional_support"  # 감정적 지원
    DECISION_HELP = "decision_help"  # 결정 도움
    PHILOSOPHICAL_INQUIRY = "philosophical_inquiry"  # 철학적 질문
    CRISIS_INTERVENTION = "crisis_intervention"  # 위기 개입

    # 확장 의도들
    INFORMATION_SEEKING = "information_seeking"  # 정보 탐색
    CREATIVE_COLLABORATION = "creative_collaboration"  # 창의적 협력
    RELATIONSHIP_ADVICE = "relationship_advice"  # 관계 조언
    PERSONAL_GROWTH = "personal_growth"  # 개인 성장
    TASK_ASSISTANCE = "task_assistance"  # 업무 지원
    PLAYFUL_INTERACTION = "playful_interaction"  # 장난스러운 상호작용

    # 지역 서비스 검색 의도들
    LOCAL_SERVICE_SEARCH = (
        "local_service_search"  # 병원/약국/응급실 등 지역 서비스 검색
    )


class SpeechRhythmPattern(Enum):
    """말하기 리듬 패턴"""

    URGENT_STACCATO = "urgent_staccato"  # 급한 단도직입
    CASUAL_FLOWING = "casual_flowing"  # 캐주얼 흐름
    FORMAL_STRUCTURED = "formal_structured"  # 격식 구조화
    EMOTIONAL_WAVES = "emotional_waves"  # 감정적 물결
    PLAYFUL_BOUNCY = "playful_bouncy"  # 장난스러운 튀김
    THOUGHTFUL_PAUSED = "thoughtful_paused"  # 사색적 일시정지
    CONFUSED_SCATTERED = "confused_scattered"  # 혼란스러운 산만
    CONFIDENT_STEADY = "confident_steady"  # 자신감 있는 안정


@dataclass
class IntentInferenceResult:
    """의도 추론 결과"""

    primary_intent: DetailedIntentType
    confidence: float
    secondary_intents: List[Tuple[DetailedIntentType, float]]
    speech_rhythm: SpeechRhythmPattern
    rhythm_confidence: float
    linguistic_features: Dict[str, Any]
    contextual_factors: List[str]
    user_pattern_match: Optional[str]


@dataclass
class UserSpeechProfile:
    """사용자 말하기 프로필"""

    user_id: str
    dominant_rhythm: SpeechRhythmPattern
    intent_frequencies: Dict[str, int]
    linguistic_markers: Dict[str, List[str]]
    interaction_history: deque
    last_updated: datetime
    confidence_score: float


class EnhancedIntentInferenceEngine:
    """향상된 의도 추론 엔진 - 검수기 모드 (차단은 상위에서 결정)"""

    def __init__(self, learning_window: int = 50):
        self.learning_window = learning_window

        # 의도 분류 패턴들
        self.intent_patterns = self._load_intent_patterns()
        self.rhythm_patterns = self._load_rhythm_patterns()

        # 사용자 프로필 관리
        self.user_profiles: Dict[str, UserSpeechProfile] = {}

        # 맥락 기반 추론을 위한 히스토리
        self.session_contexts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))

        # 감정-의도 상관관계 매트릭스
        self.emotion_intent_correlations = self._build_emotion_intent_matrix()

        # 환경 변수로 동작 모드 제어
        import os

        self.use_engine = os.getenv("ECHO_USE_INTENT_ENGINE", "true").lower() == "true"
        self.safe_only = os.getenv("ECHO_INTENT_SAFE_ONLY", "true").lower() == "true"
        self.unclear_threshold = float(
            os.getenv("ECHO_INTENT_UNCLEAR_THRESHOLD", "0.35")
        )
        self.pass_through_on_llm = (
            os.getenv("ECHO_PASS_THROUGH_ON_LLM", "true").lower() == "true"
        )

        print(
            f"🎯 Enhanced Intent Inference Engine 초기화 완료 (safe_only={self.safe_only}, pass_through={self.pass_through_on_llm})"
        )

    def infer_intent_and_rhythm(
        self,
        text: str,
        session_id: str,
        emotion_context: Dict[str, Any] = None,
        user_id: str = None,
        llm_text: str = None,
    ) -> IntentInferenceResult:
        """의도와 리듬 종합 추론"""

        emotion_context = emotion_context or {}

        # 1. 텍스트 전처리 및 특징 추출
        linguistic_features = self._extract_linguistic_features(text)

        # 2. 기본 의도 분류
        primary_intent, intent_confidence, secondary_intents = self._classify_intent(
            text, linguistic_features, emotion_context
        )

        # 3. 맥락 기반 의도 보정
        if session_id in self.session_contexts:
            primary_intent, intent_confidence = self._apply_contextual_correction(
                primary_intent, intent_confidence, session_id, text
            )

        # 4. 말하기 리듬 분석
        speech_rhythm, rhythm_confidence = self._analyze_speech_rhythm(
            text, linguistic_features, primary_intent
        )

        # 5. 사용자 패턴 학습 및 적용
        user_pattern_match = None
        if user_id:
            user_pattern_match = self._update_and_match_user_pattern(
                user_id, primary_intent, speech_rhythm, text
            )

        # 6. 맥락 요소 식별
        contextual_factors = self._identify_contextual_factors(
            text, linguistic_features, emotion_context
        )

        # 7. 세션 히스토리 업데이트
        self.session_contexts[session_id].append(
            {
                "text": text,
                "intent": primary_intent,
                "rhythm": speech_rhythm,
                "timestamp": datetime.now(),
                "emotion": emotion_context.get("primary_emotion", "neutral"),
            }
        )

        result = IntentInferenceResult(
            primary_intent=primary_intent,
            confidence=intent_confidence,
            secondary_intents=secondary_intents,
            speech_rhythm=speech_rhythm,
            rhythm_confidence=rhythm_confidence,
            linguistic_features=linguistic_features,
            contextual_factors=contextual_factors,
            user_pattern_match=user_pattern_match,
        )

        # 검수 정보만 로그 (차단은 상위에서 결정)
        print(
            f"[INTENT] intent={primary_intent.value} conf={intent_confidence:.2f} rhythm={speech_rhythm.value} llm_available={bool((llm_text or '').strip())}"
        )

        return result

    def _extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        """언어학적 특징 추출"""

        features = {
            "text_length": len(text),
            "word_count": len(text.split()),
            "sentence_count": len([s for s in text.split(".") if s.strip()]),
            "question_marks": text.count("?"),
            "exclamation_marks": text.count("!"),
            "ellipsis_count": text.count("..."),
            "emoji_count": len(re.findall(r"[😀-🙏]", text)),
            "uppercase_ratio": sum(1 for c in text if c.isupper()) / max(len(text), 1),
            "punctuation_density": len(re.findall(r"[.,!?;:]", text))
            / max(len(text), 1),
        }

        # 한국어 특성
        features.update(
            {
                "informal_endings": len(re.findall(r"(어|야|지|네|요)$", text)),
                "formal_endings": len(re.findall(r"(습니다|됩니다|입니다)$", text)),
                "onomatopoeia": len(re.findall(r"(ㅋㅋ|ㅎㅎ|ㅠㅠ|ㅜㅜ)", text)),
                "filler_words": len(
                    re.findall(r"(음|어|그|뭔가|좀)", text, re.IGNORECASE)
                ),
            }
        )

        # 감정 표현 강도
        features["emotional_intensifiers"] = len(
            re.findall(r"(너무|정말|진짜|완전|엄청|매우|아주)", text, re.IGNORECASE)
        )

        return features

    def _classify_intent(
        self, text: str, features: Dict[str, Any], emotion_context: Dict[str, Any]
    ) -> Tuple[DetailedIntentType, float, List[Tuple[DetailedIntentType, float]]]:
        """의도 분류"""

        text_lower = text.lower()
        intent_scores = defaultdict(float)

        # 패턴 매칭 기반 분류
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if isinstance(pattern, dict):
                    # 가중치가 있는 키워드
                    for keyword, weight in pattern.items():
                        if keyword in text_lower:
                            intent_scores[intent_type] += weight
                else:
                    # 단순 키워드
                    if pattern in text_lower:
                        intent_scores[intent_type] += 1.0

        # 언어학적 특징 기반 보정
        intent_scores = self._apply_linguistic_corrections(intent_scores, features)

        # 감정-의도 상관관계 적용
        if emotion_context.get("primary_emotion"):
            emotion = emotion_context["primary_emotion"]
            if emotion in self.emotion_intent_correlations:
                for intent_str, correlation in self.emotion_intent_correlations[
                    emotion
                ].items():
                    try:
                        intent_enum = DetailedIntentType(intent_str)
                        intent_scores[intent_enum.value] += correlation * 0.3
                    except ValueError:
                        continue

        # 점수 정규화 및 순위 결정
        if not intent_scores:
            # 기본값
            return DetailedIntentType.CASUAL_CHAT, 0.3, []

        # 상위 의도들 추출
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)

        # 주 의도
        primary_intent_str, primary_score = sorted_intents[0]
        primary_intent = DetailedIntentType(primary_intent_str)

        # 정규화된 신뢰도
        total_score = sum(intent_scores.values())
        primary_confidence = primary_score / total_score if total_score > 0 else 0.3

        # 보조 의도들
        secondary_intents = []
        for intent_str, score in sorted_intents[1:4]:  # 상위 3개까지
            if score > 0.1:  # 임계값 이상만
                try:
                    intent = DetailedIntentType(intent_str)
                    confidence = score / total_score
                    secondary_intents.append((intent, confidence))
                except ValueError:
                    continue

        return primary_intent, min(primary_confidence, 1.0), secondary_intents

    def _analyze_speech_rhythm(
        self, text: str, features: Dict[str, Any], intent: DetailedIntentType
    ) -> Tuple[SpeechRhythmPattern, float]:
        """말하기 리듬 분석"""

        rhythm_scores = defaultdict(float)

        # 구두점과 길이 기반 리듬 분석
        if features["exclamation_marks"] >= 2 or features["uppercase_ratio"] > 0.3:
            rhythm_scores["urgent_staccato"] += 2.0

        if features["ellipsis_count"] >= 1 or features["filler_words"] >= 2:
            rhythm_scores["thoughtful_paused"] += 1.5

        if features["onomatopoeia"] >= 1 or features["emoji_count"] >= 2:
            rhythm_scores["playful_bouncy"] += 2.0

        if features["formal_endings"] >= 1:
            rhythm_scores["formal_structured"] += 1.5

        if features["emotional_intensifiers"] >= 2:
            rhythm_scores["emotional_waves"] += 1.5

        # 텍스트 길이와 구조 기반
        if features["word_count"] <= 3 and features["exclamation_marks"] >= 1:
            rhythm_scores["urgent_staccato"] += 1.0
        elif features["word_count"] > 20 and features["sentence_count"] >= 3:
            rhythm_scores["formal_structured"] += 1.0

        # 의도와 리듬의 상관관계
        intent_rhythm_mapping = {
            DetailedIntentType.CRISIS_INTERVENTION: "urgent_staccato",
            DetailedIntentType.PHILOSOPHICAL_INQUIRY: "thoughtful_paused",
            DetailedIntentType.PLAYFUL_INTERACTION: "playful_bouncy",
            DetailedIntentType.CASUAL_GREETING: "casual_flowing",
            DetailedIntentType.EMOTIONAL_SUPPORT: "emotional_waves",
        }

        if intent in intent_rhythm_mapping:
            rhythm_scores[intent_rhythm_mapping[intent]] += 1.0

        # 기본값 처리
        if not rhythm_scores:
            return SpeechRhythmPattern.CASUAL_FLOWING, 0.5

        # 최고 점수 리듬 선택
        best_rhythm_str = max(rhythm_scores.items(), key=lambda x: x[1])[0]
        best_rhythm = SpeechRhythmPattern(best_rhythm_str)

        # 신뢰도 계산
        total_score = sum(rhythm_scores.values())
        confidence = (
            rhythm_scores[best_rhythm_str] / total_score if total_score > 0 else 0.5
        )

        return best_rhythm, min(confidence, 1.0)

    def _apply_contextual_correction(
        self,
        intent: DetailedIntentType,
        confidence: float,
        session_id: str,
        current_text: str,
    ) -> Tuple[DetailedIntentType, float]:
        """맥락 기반 의도 보정"""

        recent_history = list(self.session_contexts[session_id])[-3:]  # 최근 3개

        if not recent_history:
            return intent, confidence

        # 연속된 동일 의도 패턴 감지
        recent_intents = [h["intent"] for h in recent_history]
        if len(set(recent_intents)) == 1 and len(recent_intents) >= 2:
            # 동일 의도가 계속되면 신뢰도 증가
            confidence = min(confidence * 1.2, 1.0)

        # 대화 흐름 기반 보정
        if recent_history:
            last_entry = recent_history[-1]

            # 질문 → 답변 패턴
            if (
                last_entry["intent"] == DetailedIntentType.INFORMATION_SEEKING
                and intent == DetailedIntentType.CASUAL_CHAT
            ):
                # 정보 요청 후 일반 대화는 추가 질문일 가능성
                intent = DetailedIntentType.INFORMATION_SEEKING
                confidence = confidence * 0.8

            # 감정적 지원 → 후속 대화
            elif (
                last_entry["intent"] == DetailedIntentType.EMOTIONAL_SUPPORT
                and intent == DetailedIntentType.CASUAL_CHAT
            ):
                # 감정 지원 후 일반 대화는 계속된 감정 표현일 가능성
                intent = DetailedIntentType.EMOTIONAL_SUPPORT
                confidence = confidence * 0.9

        return intent, confidence

    def _update_and_match_user_pattern(
        self,
        user_id: str,
        intent: DetailedIntentType,
        rhythm: SpeechRhythmPattern,
        text: str,
    ) -> Optional[str]:
        """사용자 패턴 학습 및 매칭"""

        current_time = datetime.now()

        # 새 사용자 프로필 생성 또는 기존 프로필 업데이트
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserSpeechProfile(
                user_id=user_id,
                dominant_rhythm=rhythm,
                intent_frequencies=defaultdict(int),
                linguistic_markers=defaultdict(list),
                interaction_history=deque(maxlen=self.learning_window),
                last_updated=current_time,
                confidence_score=0.1,
            )

        profile = self.user_profiles[user_id]

        # 프로필 업데이트
        profile.intent_frequencies[intent.value] += 1
        profile.interaction_history.append(
            {
                "intent": intent,
                "rhythm": rhythm,
                "text_snippet": text[:50],  # 처음 50자만
                "timestamp": current_time,
            }
        )
        profile.last_updated = current_time

        # 지배적 리듬 업데이트
        rhythm_counts = defaultdict(int)
        for interaction in profile.interaction_history:
            rhythm_counts[interaction["rhythm"]] += 1

        if rhythm_counts:
            profile.dominant_rhythm = max(rhythm_counts.items(), key=lambda x: x[1])[0]

        # 신뢰도 증가
        profile.confidence_score = min(profile.confidence_score + 0.05, 1.0)

        # 패턴 매칭 결과 반환
        total_interactions = len(profile.interaction_history)
        if total_interactions >= 5:
            dominant_intent = max(
                profile.intent_frequencies.items(), key=lambda x: x[1]
            )[0]
            return (
                f"사용자 주요 패턴: {dominant_intent} ({profile.dominant_rhythm.value})"
            )

        return None

    def _identify_contextual_factors(
        self, text: str, features: Dict[str, Any], emotion_context: Dict[str, Any]
    ) -> List[str]:
        """맥락 요소 식별"""

        factors = []

        # 시간적 맥락
        if any(
            time_word in text.lower()
            for time_word in ["지금", "오늘", "어제", "내일", "최근"]
        ):
            factors.append("시간적_참조")

        # 관계적 맥락
        if any(
            relation in text.lower()
            for relation in ["친구", "가족", "동료", "상사", "연인"]
        ):
            factors.append("관계적_맥락")

        # 감정적 강도
        emotion_intensity = emotion_context.get("emotion_intensity", 0)
        if emotion_intensity > 0.7:
            factors.append("고강도_감정")
        elif emotion_intensity < 0.3:
            factors.append("저강도_감정")

        # 언어적 특성
        if features["formal_endings"] > 0:
            factors.append("격식체_사용")
        if features["onomatopoeia"] > 0:
            factors.append("표현적_언어")
        if features["question_marks"] >= 2:
            factors.append("다중_질문")

        # 긴급성 지표
        if (
            features["exclamation_marks"] >= 2
            and features["emotional_intensifiers"] >= 1
        ):
            factors.append("긴급성_높음")

        return factors

    def _apply_linguistic_corrections(
        self, scores: Dict[str, float], features: Dict[str, Any]
    ) -> Dict[str, float]:
        """언어학적 특징 기반 점수 보정"""

        # 질문 형태면 정보 탐색이나 도움 요청일 가능성 증가
        if features["question_marks"] >= 1:
            scores["information_seeking"] += 0.5
            scores["decision_help"] += 0.3

        # 감정 표현이 강하면 감정적 지원 필요성 증가
        if features["emotional_intensifiers"] >= 2:
            scores["emotional_support"] += 0.7

        # 격식체 사용시 진지한 의도일 가능성
        if features["formal_endings"] >= 1:
            scores["philosophical_inquiry"] += 0.3
            scores["decision_help"] += 0.3

        # 캐주얼한 표현이 많으면 일상 대화
        if features["informal_endings"] >= 1 and features["onomatopoeia"] >= 1:
            scores["casual_chat"] += 0.5
            scores["playful_interaction"] += 0.3

        return scores

    def _load_intent_patterns(self) -> Dict[str, List]:
        """의도 분류 패턴 로드"""
        return {
            "casual_greeting": [
                "안녕",
                "hello",
                "hi",
                "하이",
                "좋은 아침",
                "좋은 하루",
            ],
            "casual_chat": ["그냥", "별로", "뭐하고", "어때", "괜찮아", "그렇구나"],
            "emotional_support": [
                {"힘들어": 2.0, "우울해": 2.0, "슬퍼": 2.0, "외로워": 2.0},
                {"스트레스": 1.5, "걱정": 1.5, "불안": 1.5, "화나": 1.5},
            ],
            "decision_help": [
                {"결정": 2.0, "선택": 2.0, "고민": 2.0, "조언": 2.0},
                {"어떻게": 1.5, "뭘": 1.5, "방법": 1.5},
            ],
            "philosophical_inquiry": [
                {"의미": 2.0, "인생": 2.0, "왜": 1.5, "목적": 2.0},
                {"철학": 2.0, "존재": 1.5, "진리": 2.0},
            ],
            "crisis_intervention": [
                {"죽고싶어": 3.0, "자살": 3.0, "끝내고싶어": 3.0},
                {"너무힘들어": 2.0, "포기하고싶어": 2.0},
            ],
            "information_seeking": [
                {"알려줘": 2.0, "궁금해": 1.5, "설명": 1.5, "뭐야": 1.0},
                {"어떤": 1.0, "무슨": 1.0},
            ],
            "creative_collaboration": [
                {"창작": 2.0, "아이디어": 1.5, "상상": 1.5, "만들어": 1.5},
                {"디자인": 1.5, "작품": 1.5},
            ],
            "relationship_advice": [
                {"친구": 1.5, "연인": 2.0, "사랑": 1.5, "관계": 2.0},
                {"싸웠어": 2.0, "헤어져": 2.0},
            ],
            "personal_growth": [
                {"성장": 2.0, "발전": 1.5, "배우고싶어": 1.5, "개선": 1.5},
                {"능력": 1.0, "실력": 1.0},
            ],
            "task_assistance": [
                {"도와줘": 2.0, "해줘": 1.5, "작업": 1.5, "업무": 1.5},
                {"프로젝트": 1.5, "과제": 1.5},
            ],
            "playful_interaction": [
                {"재밌어": 1.5, "웃겨": 1.5, "장난": 2.0, "놀자": 2.0},
                {"ㅋㅋ": 1.0, "ㅎㅎ": 1.0},
            ],
            "local_service_search": [
                {"병원": 3.0, "응급실": 3.0, "소아과": 3.0, "약국": 2.5},
                {"아파": 2.0, "아픈": 2.0, "열": 2.0, "아이": 1.5, "남율": 2.0},
                {"근처": 2.0, "가까운": 2.0, "병원찾아": 3.0, "응급": 3.0},
                {"의사": 1.5, "진료": 2.0, "치료": 2.0, "검진": 1.5},
            ],
        }

    def _load_rhythm_patterns(self) -> Dict[str, List]:
        """리듬 패턴 로드"""
        return {
            "urgent_staccato": ["!!", "빨리", "급해", "지금", "당장"],
            "casual_flowing": ["그냥", "좀", "뭔가", "약간", "~"],
            "formal_structured": ["습니다", "됩니다", "입니다"],
            "emotional_waves": ["너무", "정말", "진짜", "완전"],
            "playful_bouncy": ["ㅋㅋ", "ㅎㅎ", "야", "에이"],
            "thoughtful_paused": ["...", "음", "글쎄", "생각해보니"],
            "confused_scattered": ["뭐지", "어", "그런데", "근데"],
            "confident_steady": ["확실히", "분명히", "당연히", "물론"],
        }

    def _build_emotion_intent_matrix(self) -> Dict[str, Dict[str, float]]:
        """감정-의도 상관관계 매트릭스"""
        return {
            "sadness": {
                "emotional_support": 0.8,
                "relationship_advice": 0.6,
                "personal_growth": 0.4,
            },
            "anxiety": {
                "emotional_support": 0.9,
                "decision_help": 0.7,
                "crisis_intervention": 0.3,
            },
            "joy": {
                "playful_interaction": 0.7,
                "creative_collaboration": 0.6,
                "casual_chat": 0.5,
            },
            "anger": {
                "emotional_support": 0.6,
                "relationship_advice": 0.8,
                "decision_help": 0.4,
            },
            "curiosity": {
                "information_seeking": 0.8,
                "philosophical_inquiry": 0.7,
                "creative_collaboration": 0.5,
            },
            "confusion": {
                "information_seeking": 0.6,
                "decision_help": 0.8,
                "emotional_support": 0.4,
            },
        }

    def get_user_analytics(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 분석 데이터 반환"""
        if user_id not in self.user_profiles:
            return None

        profile = self.user_profiles[user_id]

        # 의도 분포 계산
        total_interactions = sum(profile.intent_frequencies.values())
        intent_distribution = (
            {
                intent: count / total_interactions
                for intent, count in profile.intent_frequencies.items()
            }
            if total_interactions > 0
            else {}
        )

        # 최근 활동 패턴
        recent_interactions = list(profile.interaction_history)[-10:]  # 최근 10개
        recent_rhythms = [i["rhythm"].value for i in recent_interactions]
        rhythm_trend = (
            max(set(recent_rhythms), key=recent_rhythms.count)
            if recent_rhythms
            else None
        )

        return {
            "user_id": user_id,
            "total_interactions": total_interactions,
            "dominant_rhythm": profile.dominant_rhythm.value,
            "confidence_score": profile.confidence_score,
            "intent_distribution": intent_distribution,
            "recent_rhythm_trend": rhythm_trend,
            "last_active": profile.last_updated.isoformat(),
            "profile_maturity": min(total_interactions / 20, 1.0),  # 20회 이상이면 성숙
        }

    def should_block(
        self, result: "IntentInferenceResult", llm_text: Optional[str] = None
    ) -> bool:
        """차단 여부 결정 (안전/빈응답만)"""
        has_llm = bool((llm_text or "").strip())

        # 빈응답이면 차단
        if not has_llm:
            return True

        # 안전 위반 검사 (실제 구현 필요)
        text_lower = (llm_text or "").lower()
        if any(
            danger in text_lower
            for danger in ["kill myself", "suicide", "bomb", "terror"]
        ):
            return True

        # SAFE_ONLY 모드면 모호함은 정보만 제공(차단 X)
        if self.safe_only:
            return False

        # 모호 임계치가 낮음 → 웬만하면 통과
        if (
            result.primary_intent == DetailedIntentType.CASUAL_CHAT
            and result.confidence >= self.unclear_threshold
        ):
            return False

        return False


# 단일 인스턴스 전역 접근
_global_intent_engine = None


def get_global_intent_engine() -> EnhancedIntentInferenceEngine:
    """Intent 엔진 싱글톤 인스턴스 반환"""
    global _global_intent_engine
    if _global_intent_engine is None:
        _global_intent_engine = EnhancedIntentInferenceEngine()
    return _global_intent_engine


# 테스트 실행
if __name__ == "__main__":
    engine = EnhancedIntentInferenceEngine()

    test_cases = [
        "안녕하세요! 오늘 기분이 좋네요 ^^",
        "요즘 너무 힘들어서... 어떻게 해야 할지 모르겠어요 ㅠㅠ",
        "인생의 의미가 뭘까요? 정말 궁금해서 밤새 생각했어요",
        "친구랑 싸웠는데 어떻게 화해해야 할까요?",
        "급해!! 지금 당장 도움이 필요해요!",
        "ㅋㅋㅋ 재미있는 아이디어 없나요? 놀고 싶어요~",
    ]

    print("🎯 Enhanced Intent Inference 테스트")
    print("=" * 60)

    for i, text in enumerate(test_cases):
        print(f"\n--- 테스트 {i+1} ---")
        print(f"입력: {text}")

        result = engine.infer_intent_and_rhythm(
            text,
            f"test_session_{i}",
            emotion_context={"primary_emotion": "neutral", "emotion_intensity": 0.5},
            user_id=f"user_{i%3}",  # 3명의 가상 사용자
        )

        print(
            f"주 의도: {result.primary_intent.value} (신뢰도: {result.confidence:.2f})"
        )
        print(
            f"말하기 리듬: {result.speech_rhythm.value} (신뢰도: {result.rhythm_confidence:.2f})"
        )

        if result.secondary_intents:
            print(
                "보조 의도:",
                [
                    f"{intent.value}({conf:.2f})"
                    for intent, conf in result.secondary_intents[:2]
                ],
            )

        if result.contextual_factors:
            print(f"맥락 요소: {', '.join(result.contextual_factors)}")

        if result.user_pattern_match:
            print(f"사용자 패턴: {result.user_pattern_match}")

        print("-" * 40)

    print("\n📊 사용자 분석 예시:")
    for user_id in ["user_0", "user_1", "user_2"]:
        analytics = engine.get_user_analytics(user_id)
        if analytics:
            print(f"\n{user_id}: {analytics['total_interactions']}회 상호작용")
            print(f"  지배적 리듬: {analytics['dominant_rhythm']}")
            print(f"  프로필 성숙도: {analytics['profile_maturity']:.2f}")

    print("\n🎉 Enhanced Intent Inference 테스트 완료!")
