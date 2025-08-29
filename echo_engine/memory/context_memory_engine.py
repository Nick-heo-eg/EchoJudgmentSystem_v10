#!/usr/bin/env python3
"""
🌊 Context Memory Engine v1.0
대화 히스토리 압축 및 감정 변화 흐름을 기반으로 한 상황 인식 시스템

Phase 1: LLM-Free 판단 시스템 핵심 모듈
- 대화 맥락 벡터 생성 및 압축
- 감정 변화 궤적 추적 및 예측
- 상황별 컨텍스트 의존성 모델링
- "디지털 공감 예술가"를 위한 완전한 맥락 이해

참조: LLM-Free 판단 시스템 완성도 극대화 가이드
- 독립적 문장 처리를 넘어선 대화 흐름과 상황 맥락 완전 이해
- 대화 히스토리 압축을 통한 핵심 정보 추출 및 장기 기억 구축
- 시간, 요일, 계절 등 외부 요인을 고려한 상황 인식
"""

import os
import json
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics


@dataclass
class ConversationSnapshot:
    """대화 스냅샷 데이터 클래스"""

    session_id: str
    timestamp: str
    emotional_trajectory: List[float]  # 감정 변화 궤적 (최근 10개)
    topic_persistence: Dict[str, float]  # 주제별 지속성 점수
    interaction_depth: float  # 대화 깊이 (0.0 ~ 1.0)
    urgency_level: float  # 긴급도 (0.0 ~ 1.0)
    social_context: str  # 사회적 맥락 (private/semi-private/public)
    temporal_context: Dict[str, Any]  # 시간적 맥락
    coherence_score: float  # 대화 일관성 점수


@dataclass
class TopicEvolution:
    """주제 진화 추적"""

    topic_name: str
    emergence_time: str
    peak_intensity: float
    current_intensity: float
    related_emotions: List[str]
    keyword_cluster: List[str]
    transition_triggers: List[str]


class ContextMemoryEngine:
    """대화 맥락 및 상황 인식을 위한 고도화 메모리 엔진"""

    def __init__(self, data_dir: str = "data/context_memory"):
        """초기화"""
        self.version = "1.0.0"
        self.data_dir = data_dir
        self.session_cache = {}
        self.active_sessions = {}
        self.analysis_count = 0

        # 데이터 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)

        # 주제 분류 키워드 클러스터
        self.topic_clusters = {
            "work_career": {
                "keywords": [
                    "일",
                    "직장",
                    "업무",
                    "회사",
                    "동료",
                    "상사",
                    "프로젝트",
                    "과제",
                    "출근",
                    "퇴근",
                    "야근",
                    "승진",
                    "연봉",
                    "커리어",
                ],
                "weight": 1.0,
            },
            "relationships": {
                "keywords": [
                    "친구",
                    "연인",
                    "가족",
                    "부모",
                    "형제",
                    "자매",
                    "관계",
                    "사랑",
                    "이별",
                    "결혼",
                    "데이트",
                    "갈등",
                    "화해",
                ],
                "weight": 1.2,  # 관계 주제는 더 중요하게 가중
            },
            "health_wellness": {
                "keywords": [
                    "건강",
                    "병원",
                    "의사",
                    "아픈",
                    "피곤",
                    "스트레스",
                    "운동",
                    "다이어트",
                    "수면",
                    "휴식",
                    "치료",
                ],
                "weight": 1.1,
            },
            "education_learning": {
                "keywords": [
                    "공부",
                    "학교",
                    "시험",
                    "과제",
                    "학습",
                    "교육",
                    "강의",
                    "수업",
                    "성적",
                    "졸업",
                    "입학",
                    "학원",
                ],
                "weight": 0.9,
            },
            "hobbies_interests": {
                "keywords": [
                    "취미",
                    "게임",
                    "영화",
                    "음악",
                    "책",
                    "여행",
                    "요리",
                    "운동",
                    "쇼핑",
                    "드라마",
                ],
                "weight": 0.8,
            },
            "daily_life": {
                "keywords": [
                    "하루",
                    "일상",
                    "집",
                    "생활",
                    "루틴",
                    "습관",
                    "식사",
                    "청소",
                    "쇼핑",
                    "교통",
                ],
                "weight": 0.7,
            },
            "future_goals": {
                "keywords": [
                    "목표",
                    "계획",
                    "미래",
                    "꿈",
                    "희망",
                    "도전",
                    "성장",
                    "발전",
                    "변화",
                    "개선",
                ],
                "weight": 1.0,
            },
            "emotional_state": {
                "keywords": [
                    "기분",
                    "감정",
                    "마음",
                    "느낌",
                    "생각",
                    "고민",
                    "걱정",
                    "불안",
                    "행복",
                    "슬픔",
                ],
                "weight": 1.3,  # 감정 상태는 가장 중요
            },
        }

        # 시간적 컨텍스트 패턴
        self.temporal_patterns = {
            "time_of_day": {
                "morning": {"start": 6, "end": 12, "mood_modifier": 0.1},
                "afternoon": {"start": 12, "end": 18, "mood_modifier": 0.0},
                "evening": {"start": 18, "end": 22, "mood_modifier": -0.1},
                "night": {"start": 22, "end": 6, "mood_modifier": -0.2},
            },
            "day_of_week": {
                "monday": {"stress_modifier": 0.3, "energy_modifier": -0.1},
                "tuesday": {"stress_modifier": 0.1, "energy_modifier": 0.0},
                "wednesday": {"stress_modifier": 0.0, "energy_modifier": 0.0},
                "thursday": {"stress_modifier": 0.1, "energy_modifier": -0.1},
                "friday": {"stress_modifier": -0.1, "energy_modifier": 0.2},
                "saturday": {"stress_modifier": -0.3, "energy_modifier": 0.1},
                "sunday": {"stress_modifier": -0.2, "energy_modifier": -0.1},
            },
        }

        print(f"🌊 Context Memory Engine v{self.version} 초기화 완료")
        print(f"📁 메모리 저장 경로: {self.data_dir}")

    def get_context_snapshot(self, session_id: str) -> Dict[str, Any]:
        """
        현재 대화 세션의 요약 컨텍스트 반환

        Args:
            session_id: 세션 식별자

        Returns:
            대화 컨텍스트 스냅샷
        """
        if session_id not in self.active_sessions:
            return self._create_empty_context(session_id)

        session_data = self.active_sessions[session_id]

        # 현재 시점의 컨텍스트 스냅샷 생성
        snapshot = ConversationSnapshot(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            emotional_trajectory=self._calculate_emotional_trajectory(session_data),
            topic_persistence=self._calculate_topic_persistence(session_data),
            interaction_depth=self._calculate_interaction_depth(session_data),
            urgency_level=self._calculate_urgency_level(session_data),
            social_context=self._infer_social_context(session_data),
            temporal_context=self._analyze_temporal_context(),
            coherence_score=self._calculate_coherence_score(session_data),
        )

        return asdict(snapshot)

    def update_context_memory(
        self,
        session_id: str,
        user_input: str,
        emotion_vector: Dict[str, Any],
        response_data: Optional[Dict] = None,
    ) -> None:
        """
        실시간으로 감정 변화 및 주제 흐름 기록

        Args:
            session_id: 세션 식별자
            user_input: 사용자 입력
            emotion_vector: 감정 벡터 데이터
            response_data: 응답 관련 데이터 (선택적)
        """
        self.analysis_count += 1

        # 세션 초기화 (필요시)
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = self._initialize_session(session_id)

        session_data = self.active_sessions[session_id]

        # 새로운 상호작용 기록 추가
        interaction_record = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "input_length": len(user_input),
            "word_count": len(user_input.split()),
            "emotion_vector": emotion_vector,
            "detected_topics": self._extract_topics(user_input),
            "urgency_indicators": self._detect_urgency_indicators(user_input),
            "coherence_links": self._analyze_coherence_links(session_data, user_input),
            "temporal_markers": self._extract_temporal_markers(user_input),
            "response_data": response_data or {},
        }

        session_data["interactions"].append(interaction_record)
        session_data["last_updated"] = datetime.now().isoformat()
        session_data["total_interactions"] += 1

        # 상호작용 히스토리 크기 제한 (메모리 관리)
        if len(session_data["interactions"]) > 50:
            # 오래된 상호작용은 압축하여 저장
            self._compress_old_interactions(session_data)

        # 주제 진화 추적 업데이트
        self._update_topic_evolution(session_data, interaction_record)

        # 감정 궤적 업데이트
        self._update_emotional_trajectory(session_data, emotion_vector)

        # 대화 패턴 학습
        self._learn_conversation_patterns(session_data, interaction_record)

        # 주기적으로 디스크에 저장
        if self.analysis_count % 10 == 0:
            self._save_session_data(session_id, session_data)

    def _create_empty_context(self, session_id: str) -> Dict[str, Any]:
        """빈 컨텍스트 생성"""
        return {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "emotional_trajectory": [],
            "topic_persistence": {},
            "interaction_depth": 0.0,
            "urgency_level": 0.0,
            "social_context": "private",
            "temporal_context": self._analyze_temporal_context(),
            "coherence_score": 0.0,
        }

    def _initialize_session(self, session_id: str) -> Dict[str, Any]:
        """새 세션 초기화"""
        return {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_interactions": 0,
            "interactions": [],
            "topic_evolution": {},
            "emotional_trajectory": deque(maxlen=20),  # 최근 20개 감정만 유지
            "conversation_patterns": {
                "avg_response_length": 0.0,
                "topic_switching_frequency": 0.0,
                "emotional_volatility": 0.0,
                "coherence_trend": [],
            },
            "compressed_history": [],  # 압축된 과거 기록
        }

    def _extract_topics(self, user_input: str) -> Dict[str, float]:
        """사용자 입력에서 주제 추출 및 점수 계산"""
        user_input_lower = user_input.lower()
        topic_scores = {}

        for topic_name, topic_data in self.topic_clusters.items():
            score = 0.0
            matched_keywords = []

            for keyword in topic_data["keywords"]:
                if keyword in user_input_lower:
                    score += 1.0
                    matched_keywords.append(keyword)

            if score > 0:
                # 가중치 적용
                weighted_score = score * topic_data["weight"]
                # 키워드 밀도 고려
                keyword_density = score / max(len(user_input.split()), 1)
                final_score = weighted_score * (1 + keyword_density)

                topic_scores[topic_name] = {
                    "score": final_score,
                    "matched_keywords": matched_keywords,
                    "keyword_count": len(matched_keywords),
                }

        return topic_scores

    def _detect_urgency_indicators(self, user_input: str) -> Dict[str, Any]:
        """긴급도 지시어 감지"""
        urgency_patterns = {
            "high": [
                "급해",
                "빨리",
                "즉시",
                "당장",
                "지금",
                "긴급",
                "응급",
                "위급",
                "심각",
                "위험",
            ],
            "medium": ["빠른", "서둘러", "신속", "조금 급", "시간이 없어", "늦었어"],
            "time_pressure": ["마감", "시간", "늦", "부족", "촉박", "압박"],
        }

        urgency_score = 0.0
        detected_indicators = []

        user_input_lower = user_input.lower()

        for level, patterns in urgency_patterns.items():
            matches = [pattern for pattern in patterns if pattern in user_input_lower]
            if matches:
                if level == "high":
                    urgency_score += 0.8
                elif level == "medium":
                    urgency_score += 0.5
                elif level == "time_pressure":
                    urgency_score += 0.3

                detected_indicators.extend(matches)

        # 문장 구조 기반 긴급도 추가 판단
        if "!!" in user_input:
            urgency_score += 0.2
        if "?" in user_input and ("어떻게" in user_input or "뭘" in user_input):
            urgency_score += 0.1

        return {
            "urgency_score": min(urgency_score, 1.0),
            "indicators": detected_indicators,
            "has_time_pressure": any(
                "시간" in indicator for indicator in detected_indicators
            ),
        }

    def _analyze_coherence_links(
        self, session_data: Dict, current_input: str
    ) -> Dict[str, Any]:
        """대화 일관성 연결고리 분석"""
        if not session_data["interactions"]:
            return {"coherence_score": 0.5, "links": []}

        last_interaction = session_data["interactions"][-1]
        coherence_links = []
        coherence_score = 0.0

        # 주제 연속성 체크
        current_topics = self._extract_topics(current_input)
        last_topics = last_interaction.get("detected_topics", {})

        shared_topics = set(current_topics.keys()) & set(last_topics.keys())
        if shared_topics:
            coherence_score += 0.4
            coherence_links.append(f"주제 연속성: {', '.join(shared_topics)}")

        # 키워드 연결성 체크
        current_words = set(current_input.lower().split())
        last_words = set(last_interaction["user_input"].lower().split())

        shared_words = current_words & last_words
        if len(shared_words) > 1:  # 불용어 제외하고 실질적 공유 단어
            coherence_score += 0.2
            coherence_links.append(f"키워드 연결: {len(shared_words)}개 공유")

        # 시간적 연결성 체크
        time_diff = self._calculate_time_difference(
            last_interaction["timestamp"], datetime.now().isoformat()
        )

        if time_diff < 300:  # 5분 이내
            coherence_score += 0.2
        elif time_diff < 1800:  # 30분 이내
            coherence_score += 0.1

        # 감정적 연결성 체크
        last_emotion = last_interaction.get("emotion_vector", {}).get("primary", {})
        if last_emotion:
            coherence_links.append("감정적 연결성 고려")
            coherence_score += 0.1

        return {
            "coherence_score": min(coherence_score, 1.0),
            "links": coherence_links,
            "time_gap": time_diff,
        }

    def _extract_temporal_markers(self, user_input: str) -> Dict[str, List[str]]:
        """시간 표지 추출"""
        temporal_markers = {"past": [], "present": [], "future": []}

        past_patterns = ["어제", "지난", "예전", "과거", "전에", "했었", "았었", "였던"]
        present_patterns = ["지금", "오늘", "현재", "요즘", "이제", "하고있", "되고있"]
        future_patterns = ["내일", "다음", "앞으로", "미래", "될", "할", "예정", "계획"]

        user_input_lower = user_input.lower()

        for pattern in past_patterns:
            if pattern in user_input_lower:
                temporal_markers["past"].append(pattern)

        for pattern in present_patterns:
            if pattern in user_input_lower:
                temporal_markers["present"].append(pattern)

        for pattern in future_patterns:
            if pattern in user_input_lower:
                temporal_markers["future"].append(pattern)

        return temporal_markers

    def _calculate_emotional_trajectory(self, session_data: Dict) -> List[float]:
        """감정 변화 궤적 계산"""
        trajectory = []

        for interaction in session_data["interactions"][-10:]:  # 최근 10개
            emotion_vector = interaction.get("emotion_vector", {})

            if "intensity" in emotion_vector:
                intensity = emotion_vector["intensity"]
            else:
                # primary 감정에서 강도 추정
                primary = emotion_vector.get("primary", {})
                if primary:
                    intensity = max(primary.values()) if primary else 0.5
                else:
                    intensity = 0.5

            trajectory.append(intensity)

        return trajectory

    def _calculate_topic_persistence(self, session_data: Dict) -> Dict[str, float]:
        """주제별 지속성 점수 계산"""
        topic_persistence = defaultdict(float)
        total_interactions = len(session_data["interactions"])

        if total_interactions == 0:
            return {}

        # 최근 상호작용들에서 주제별 출현 빈도 계산
        for interaction in session_data["interactions"]:
            detected_topics = interaction.get("detected_topics", {})

            for topic, topic_data in detected_topics.items():
                score = (
                    topic_data.get("score", 0)
                    if isinstance(topic_data, dict)
                    else topic_data
                )
                topic_persistence[topic] += score

        # 정규화
        max_score = max(topic_persistence.values()) if topic_persistence else 1.0
        normalized_persistence = {
            topic: score / max_score for topic, score in topic_persistence.items()
        }

        return normalized_persistence

    def _calculate_interaction_depth(self, session_data: Dict) -> float:
        """대화 깊이 계산"""
        interactions = session_data["interactions"]

        if not interactions:
            return 0.0

        depth_factors = []

        for interaction in interactions:
            # 입력 길이 기반 깊이
            input_length = interaction.get("input_length", 0)
            length_depth = min(input_length / 100, 1.0)  # 100자 기준 정규화

            # 감정 강도 기반 깊이
            emotion_vector = interaction.get("emotion_vector", {})
            emotion_depth = emotion_vector.get("intensity", 0.0)

            # 주제 복잡도 기반 깊이
            detected_topics = interaction.get("detected_topics", {})
            topic_depth = min(len(detected_topics) / 3, 1.0)  # 3개 주제 기준

            # 종합 깊이 점수
            interaction_depth = (
                length_depth * 0.3 + emotion_depth * 0.5 + topic_depth * 0.2
            )
            depth_factors.append(interaction_depth)

        # 최근 상호작용에 더 큰 가중치
        if len(depth_factors) > 1:
            weights = [i / len(depth_factors) for i in range(1, len(depth_factors) + 1)]
            weighted_depth = sum(d * w for d, w in zip(depth_factors, weights)) / sum(
                weights
            )
        else:
            weighted_depth = depth_factors[0] if depth_factors else 0.0

        return weighted_depth

    def _calculate_urgency_level(self, session_data: Dict) -> float:
        """긴급도 레벨 계산"""
        if not session_data["interactions"]:
            return 0.0

        urgency_scores = []

        for interaction in session_data["interactions"][-5:]:  # 최근 5개
            urgency_data = interaction.get("urgency_indicators", {})
            urgency_score = urgency_data.get("urgency_score", 0.0)
            urgency_scores.append(urgency_score)

        # 최근 긴급도의 가중 평균
        if urgency_scores:
            weights = [
                i / len(urgency_scores) for i in range(1, len(urgency_scores) + 1)
            ]
            weighted_urgency = sum(
                s * w for s, w in zip(urgency_scores, weights)
            ) / sum(weights)
            return weighted_urgency

        return 0.0

    def _infer_social_context(self, session_data: Dict) -> str:
        """사회적 맥락 추론"""
        # 간단한 추론 로직 (실제로는 더 복잡한 분석 필요)

        # 개인적 주제가 많으면 private
        personal_topics = ["relationships", "emotional_state", "health_wellness"]
        recent_topics = []

        for interaction in session_data["interactions"][-3:]:
            detected_topics = interaction.get("detected_topics", {})
            recent_topics.extend(detected_topics.keys())

        personal_ratio = sum(
            1 for topic in recent_topics if topic in personal_topics
        ) / max(len(recent_topics), 1)

        if personal_ratio > 0.6:
            return "private"
        elif personal_ratio > 0.3:
            return "semi-private"
        else:
            return "public"

    def _analyze_temporal_context(self) -> Dict[str, Any]:
        """현재 시간적 맥락 분석"""
        now = datetime.now()

        # 시간대 결정
        hour = now.hour
        if 6 <= hour < 12:
            time_period = "morning"
        elif 12 <= hour < 18:
            time_period = "afternoon"
        elif 18 <= hour < 22:
            time_period = "evening"
        else:
            time_period = "night"

        # 요일
        day_names = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        day_of_week = day_names[now.weekday()]

        # 시간적 컨텍스트에 따른 수정자
        time_modifiers = self.temporal_patterns["time_of_day"].get(time_period, {})
        day_modifiers = self.temporal_patterns["day_of_week"].get(day_of_week, {})

        return {
            "timestamp": now.isoformat(),
            "time_period": time_period,
            "day_of_week": day_of_week,
            "hour": hour,
            "modifiers": {
                "mood_modifier": time_modifiers.get("mood_modifier", 0.0),
                "stress_modifier": day_modifiers.get("stress_modifier", 0.0),
                "energy_modifier": day_modifiers.get("energy_modifier", 0.0),
            },
        }

    def _calculate_coherence_score(self, session_data: Dict) -> float:
        """대화 일관성 점수 계산"""
        interactions = session_data["interactions"]

        if len(interactions) < 2:
            return 0.5  # 기본값

        coherence_scores = []

        for i in range(1, len(interactions)):
            current = interactions[i]
            previous = interactions[i - 1]

            coherence_links = current.get("coherence_links", {})
            score = coherence_links.get("coherence_score", 0.5)
            coherence_scores.append(score)

        return statistics.mean(coherence_scores) if coherence_scores else 0.5

    def _update_topic_evolution(
        self, session_data: Dict, interaction_record: Dict
    ) -> None:
        """주제 진화 추적 업데이트"""
        detected_topics = interaction_record.get("detected_topics", {})
        timestamp = interaction_record["timestamp"]

        for topic_name, topic_data in detected_topics.items():
            score = (
                topic_data.get("score", 0)
                if isinstance(topic_data, dict)
                else topic_data
            )

            if topic_name not in session_data["topic_evolution"]:
                # 새 주제 등장
                session_data["topic_evolution"][topic_name] = {
                    "emergence_time": timestamp,
                    "peak_intensity": score,
                    "current_intensity": score,
                    "intensity_history": [score],
                    "last_mentioned": timestamp,
                }
            else:
                # 기존 주제 업데이트
                topic_evo = session_data["topic_evolution"][topic_name]
                topic_evo["current_intensity"] = score
                topic_evo["last_mentioned"] = timestamp
                topic_evo["intensity_history"].append(score)

                # 최대 강도 업데이트
                if score > topic_evo["peak_intensity"]:
                    topic_evo["peak_intensity"] = score

                # 히스토리 크기 제한
                if len(topic_evo["intensity_history"]) > 20:
                    topic_evo["intensity_history"] = topic_evo["intensity_history"][
                        -20:
                    ]

    def _update_emotional_trajectory(
        self, session_data: Dict, emotion_vector: Dict
    ) -> None:
        """감정 궤적 업데이트"""
        intensity = emotion_vector.get("intensity", 0.5)
        session_data["emotional_trajectory"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "intensity": intensity,
                "primary_emotion": emotion_vector.get("primary", {}),
                "stability": emotion_vector.get("stability", 0.5),
            }
        )

    def _learn_conversation_patterns(
        self, session_data: Dict, interaction_record: Dict
    ) -> None:
        """대화 패턴 학습"""
        patterns = session_data["conversation_patterns"]

        # 평균 응답 길이 업데이트
        current_length = interaction_record["input_length"]
        total_interactions = session_data["total_interactions"]

        if total_interactions > 1:
            patterns["avg_response_length"] = (
                patterns["avg_response_length"] * (total_interactions - 1)
                + current_length
            ) / total_interactions
        else:
            patterns["avg_response_length"] = current_length

        # 감정 변동성 계산
        if len(session_data["emotional_trajectory"]) > 1:
            intensities = [
                entry["intensity"] for entry in session_data["emotional_trajectory"]
            ]
            if len(intensities) > 1:
                patterns["emotional_volatility"] = statistics.stdev(intensities)

        # 일관성 트렌드 추가
        coherence_score = interaction_record.get("coherence_links", {}).get(
            "coherence_score", 0.5
        )
        patterns["coherence_trend"].append(coherence_score)

        # 트렌드 크기 제한
        if len(patterns["coherence_trend"]) > 20:
            patterns["coherence_trend"] = patterns["coherence_trend"][-20:]

    def _compress_old_interactions(self, session_data: Dict) -> None:
        """오래된 상호작용 압축"""
        interactions = session_data["interactions"]

        # 오래된 10개 상호작용을 압축
        old_interactions = interactions[:10]

        # 압축 요약 생성
        compression_summary = {
            "period_start": old_interactions[0]["timestamp"],
            "period_end": old_interactions[-1]["timestamp"],
            "total_interactions": len(old_interactions),
            "dominant_topics": self._get_dominant_topics(old_interactions),
            "avg_emotion_intensity": self._calculate_avg_emotion_intensity(
                old_interactions
            ),
            "key_patterns": self._extract_key_patterns(old_interactions),
        }

        session_data["compressed_history"].append(compression_summary)
        session_data["interactions"] = interactions[10:]  # 오래된 것들 제거

    def _calculate_time_difference(self, time1: str, time2: str) -> float:
        """두 시간 간의 차이 계산 (초 단위)"""
        try:
            dt1 = datetime.fromisoformat(time1.replace("Z", "+00:00"))
            dt2 = datetime.fromisoformat(time2.replace("Z", "+00:00"))
            return abs((dt2 - dt1).total_seconds())
        except:
            return 0.0

    def _get_dominant_topics(self, interactions: List[Dict]) -> List[str]:
        """지배적 주제들 추출"""
        topic_scores = defaultdict(float)

        for interaction in interactions:
            detected_topics = interaction.get("detected_topics", {})
            for topic, data in detected_topics.items():
                score = data.get("score", 0) if isinstance(data, dict) else data
                topic_scores[topic] += score

        # 상위 3개 주제 반환
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, score in sorted_topics[:3]]

    def _calculate_avg_emotion_intensity(self, interactions: List[Dict]) -> float:
        """평균 감정 강도 계산"""
        intensities = []

        for interaction in interactions:
            emotion_vector = interaction.get("emotion_vector", {})
            intensity = emotion_vector.get("intensity", 0.5)
            intensities.append(intensity)

        return statistics.mean(intensities) if intensities else 0.5

    def _extract_key_patterns(self, interactions: List[Dict]) -> Dict[str, Any]:
        """핵심 패턴 추출"""
        return {
            "avg_input_length": statistics.mean(
                [i["input_length"] for i in interactions]
            ),
            "topic_diversity": len(
                set().union(
                    *[i.get("detected_topics", {}).keys() for i in interactions]
                )
            ),
            "urgency_episodes": sum(
                1
                for i in interactions
                if i.get("urgency_indicators", {}).get("urgency_score", 0) > 0.5
            ),
        }

    def _save_session_data(self, session_id: str, session_data: Dict) -> None:
        """세션 데이터 저장"""
        session_path = os.path.join(self.data_dir, f"{session_id}_context.json")

        try:
            # deque 객체를 리스트로 변환하여 저장
            save_data = dict(session_data)
            save_data["emotional_trajectory"] = list(save_data["emotional_trajectory"])

            with open(session_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 세션 데이터 저장 실패 ({session_id}): {e}")

    def get_session_insights(self, session_id: str) -> Dict[str, Any]:
        """세션 인사이트 분석"""
        if session_id not in self.active_sessions:
            return {"error": "세션을 찾을 수 없습니다"}

        session_data = self.active_sessions[session_id]

        insights = {
            "session_summary": {
                "total_interactions": session_data["total_interactions"],
                "session_duration": self._calculate_session_duration(session_data),
                "dominant_topics": self._get_dominant_topics(
                    session_data["interactions"]
                ),
                "avg_emotional_intensity": self._calculate_avg_emotion_intensity(
                    session_data["interactions"]
                ),
            },
            "conversation_flow": {
                "coherence_trend": session_data["conversation_patterns"][
                    "coherence_trend"
                ][-10:],
                "emotional_volatility": session_data["conversation_patterns"][
                    "emotional_volatility"
                ],
                "topic_switching_pattern": self._analyze_topic_switching(session_data),
            },
            "context_factors": {
                "current_urgency": self._calculate_urgency_level(session_data),
                "interaction_depth": self._calculate_interaction_depth(session_data),
                "social_context": self._infer_social_context(session_data),
            },
        }

        return insights

    def _calculate_session_duration(self, session_data: Dict) -> str:
        """세션 지속 시간 계산"""
        if not session_data["interactions"]:
            return "0분"

        start_time = datetime.fromisoformat(session_data["created_at"])
        end_time = datetime.fromisoformat(session_data["last_updated"])

        duration = end_time - start_time
        minutes = int(duration.total_seconds() / 60)

        return f"{minutes}분"

    def _analyze_topic_switching(self, session_data: Dict) -> Dict[str, Any]:
        """주제 전환 패턴 분석"""
        interactions = session_data["interactions"]

        if len(interactions) < 2:
            return {"switches": 0, "pattern": "insufficient_data"}

        topic_switches = 0
        previous_topics = set()

        for interaction in interactions:
            current_topics = set(interaction.get("detected_topics", {}).keys())

            if previous_topics and not (current_topics & previous_topics):
                topic_switches += 1

            previous_topics = current_topics

        switch_rate = topic_switches / max(len(interactions) - 1, 1)

        if switch_rate > 0.5:
            pattern = "high_switching"
        elif switch_rate > 0.2:
            pattern = "moderate_switching"
        else:
            pattern = "focused_conversation"

        return {
            "switches": topic_switches,
            "switch_rate": switch_rate,
            "pattern": pattern,
        }


def test_context_memory_engine():
    """컨텍스트 메모리 엔진 테스트"""
    print("🧪 Context Memory Engine 테스트 시작...")

    engine = ContextMemoryEngine()
    test_session_id = "test_session_001"

    # 테스트 시나리오 1: 첫 번째 상호작용
    print("\n📝 시나리오 1: 첫 번째 상호작용")
    emotion_vector_1 = {
        "primary": {"sadness": 0.7, "fear": 0.2},
        "intensity": 0.7,
        "stability": 0.4,
    }

    engine.update_context_memory(
        test_session_id,
        "요즘 직장 일이 너무 스트레스받아서 잠도 못 자고 있어요",
        emotion_vector_1,
    )

    context_1 = engine.get_context_snapshot(test_session_id)
    print(f"✅ 첫 상호작용 후 컨텍스트 스냅샷 생성")
    print(f"   주제: {list(context_1['topic_persistence'].keys())}")
    print(f"   긴급도: {context_1['urgency_level']:.3f}")

    # 테스트 시나리오 2: 연관된 주제로 대화 계속
    print("\n📝 시나리오 2: 연관된 주제로 대화 계속")
    emotion_vector_2 = {
        "primary": {"anger": 0.5, "sadness": 0.3},
        "intensity": 0.6,
        "stability": 0.3,
    }

    engine.update_context_memory(
        test_session_id,
        "상사가 계속 야근을 시키는데 정말 화가 나요. 이러다 건강까지 나빠질 것 같아요",
        emotion_vector_2,
    )

    context_2 = engine.get_context_snapshot(test_session_id)
    print(f"✅ 두 번째 상호작용 후 일관성 점수: {context_2['coherence_score']:.3f}")
    print(f"   감정 궤적: {context_2['emotional_trajectory']}")

    # 테스트 시나리오 3: 주제 전환
    print("\n📝 시나리오 3: 주제 전환")
    emotion_vector_3 = {
        "primary": {"joy": 0.6, "surprise": 0.2},
        "intensity": 0.5,
        "stability": 0.7,
    }

    engine.update_context_memory(
        test_session_id,
        "그런데 오늘 친구들과 영화 보러 가기로 했어요! 정말 오랜만이에요",
        emotion_vector_3,
    )

    context_3 = engine.get_context_snapshot(test_session_id)
    print(f"✅ 주제 전환 후 주제 지속성: {context_3['topic_persistence']}")

    # 테스트 시나리오 4: 긴급한 상황
    print("\n📝 시나리오 4: 긴급한 상황")
    emotion_vector_4 = {
        "primary": {"fear": 0.8, "anger": 0.1},
        "intensity": 0.9,
        "stability": 0.1,
    }

    engine.update_context_memory(
        test_session_id,
        "급해요! 내일까지 프로젝트 마감인데 아직 절반도 못 끝냈어요. 어떻게 해야 하죠?",
        emotion_vector_4,
    )

    context_4 = engine.get_context_snapshot(test_session_id)
    print(f"✅ 긴급 상황 감지 - 긴급도: {context_4['urgency_level']:.3f}")
    print(f"   상호작용 깊이: {context_4['interaction_depth']:.3f}")

    # 테스트 시나리오 5: 세션 인사이트 분석
    print("\n📝 시나리오 5: 세션 인사이트 분석")
    insights = engine.get_session_insights(test_session_id)

    print(f"📊 세션 요약:")
    print(f"   총 상호작용: {insights['session_summary']['total_interactions']}")
    print(f"   지속 시간: {insights['session_summary']['session_duration']}")
    print(f"   지배적 주제: {insights['session_summary']['dominant_topics']}")
    print(
        f"   평균 감정 강도: {insights['session_summary']['avg_emotional_intensity']:.3f}"
    )

    print(f"\n🔄 대화 흐름:")
    print(
        f"   감정 변동성: {insights['conversation_flow']['emotional_volatility']:.3f}"
    )
    print(
        f"   주제 전환 패턴: {insights['conversation_flow']['topic_switching_pattern']['pattern']}"
    )

    print(f"\n🌍 컨텍스트 요소:")
    print(f"   현재 긴급도: {insights['context_factors']['current_urgency']:.3f}")
    print(f"   상호작용 깊이: {insights['context_factors']['interaction_depth']:.3f}")
    print(f"   사회적 맥락: {insights['context_factors']['social_context']}")

    print("\n🎉 Context Memory Engine 테스트 완료!")


if __name__ == "__main__":
    test_context_memory_engine()
