#!/usr/bin/env python3
"""
🎭 Personality Profiler v1.0
사용자별 감정 반응 패턴 및 선호 응답 스타일을 개인화된 프로필로 저장하는 고도화 시스템

Phase 1: LLM-Free 판단 시스템 핵심 모듈
- 사용자별 감정 반응 패턴 학습 및 모델링
- 개인화된 응답 전략 자동 최적화
- 시간에 따른 사용자 변화 적응적 추적
- "디지털 공감 예술가"를 위한 과학적 인격 모델링

참조: LLM-Free 판단 시스템 완성도 극대화 가이드
- 인간의 직관과 감정을 수학적으로 모델링
- 각 사용자는 고유한 감정 반응 패턴을 가진다는 철학 기반
"""

import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics
import math


@dataclass
class EmotionProfile:
    """사용자 감정 프로필 데이터 클래스"""

    baseline_mood: float = 0.5  # 기본 감정 상태 (0.0: 매우 부정적, 1.0: 매우 긍정적)
    reactivity: float = 0.5  # 감정 반응 강도 (0.0: 무반응, 1.0: 극도 민감)
    recovery_rate: float = 0.5  # 감정 회복 속도 (0.0: 매우 느림, 1.0: 매우 빠름)
    stability: float = 0.5  # 감정 안정성 (0.0: 매우 불안정, 1.0: 매우 안정)
    openness: float = 0.5  # 개방성 (0.0: 폐쇄적, 1.0: 매우 개방적)


@dataclass
class ResponsePreferences:
    """응답 선호도 프로필"""

    directness: float = 0.5  # 직접성 선호도 (0.0: 간접적, 1.0: 직접적)
    empathy_level: float = 0.5  # 공감 수준 선호도 (0.0: 논리적, 1.0: 감정적)
    solution_focus: float = 0.5  # 해결책 지향성 (0.0: 경청 중심, 1.0: 해결책 중심)
    formality: float = 0.5  # 격식 선호도 (0.0: 비격식, 1.0: 격식)
    humor_acceptance: float = 0.5  # 유머 수용도 (0.0: 진지함, 1.0: 유머 환영)
    metaphor_preference: float = 0.5  # 은유 선호도 (0.0: 직설적, 1.0: 은유적)


@dataclass
class InteractionPattern:
    """상호작용 패턴 데이터"""

    timestamp: str
    emotion_before: str
    emotion_after: str
    strategy_used: str
    effectiveness_score: float  # 0.0 ~ 1.0
    response_time: float
    user_satisfaction: Optional[float] = None


class PersonalityProfiler:
    """사용자별 개인화 프로필링 시스템"""

    def __init__(self, data_dir: str = "data/user_profiles"):
        """초기화"""
        self.version = "1.0.0"
        self.data_dir = data_dir
        self.profiles_cache = {}
        self.analysis_count = 0

        # 데이터 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)

        # 감정 가중치 매트릭스 (감정 간 영향도)
        self.emotion_influence_matrix = {
            "joy": {
                "sadness": -0.7,
                "anger": -0.5,
                "fear": -0.3,
                "surprise": 0.2,
                "neutral": 0.1,
            },
            "sadness": {
                "joy": -0.6,
                "anger": 0.3,
                "fear": 0.4,
                "surprise": -0.2,
                "neutral": -0.1,
            },
            "anger": {
                "joy": -0.5,
                "sadness": 0.2,
                "fear": -0.1,
                "surprise": 0.1,
                "neutral": -0.2,
            },
            "fear": {
                "joy": -0.4,
                "sadness": 0.3,
                "anger": 0.2,
                "surprise": -0.3,
                "neutral": -0.1,
            },
            "surprise": {
                "joy": 0.3,
                "sadness": -0.1,
                "anger": 0.1,
                "fear": -0.2,
                "neutral": 0.0,
            },
            "neutral": {
                "joy": 0.1,
                "sadness": 0.0,
                "anger": 0.0,
                "fear": 0.0,
                "surprise": 0.0,
            },
        }

        # 트리거 패턴 카테고리
        self.trigger_categories = {
            "stress": [
                "일",
                "과제",
                "시험",
                "업무",
                "마감",
                "압박",
                "스트레스",
                "바쁘",
                "힘들",
            ],
            "comfort": [
                "집",
                "가족",
                "친구",
                "편안",
                "쉬",
                "휴식",
                "평화",
                "안전",
                "따뜻",
            ],
            "achievement": [
                "성공",
                "달성",
                "완료",
                "성취",
                "승리",
                "통과",
                "합격",
                "인정",
            ],
            "loss": ["실패", "포기", "잃", "떠나", "이별", "상실", "실망", "좌절"],
            "social": ["사람", "만남", "대화", "소통", "관계", "친구", "동료", "가족"],
            "solitude": ["혼자", "외롭", "고독", "조용", "침묵", "홀로", "독립"],
        }

        print(f"🎭 Personality Profiler v{self.version} 초기화 완료")
        print(f"📁 프로필 저장 경로: {self.data_dir}")

    def update_user_profile(self, user_id: str, new_data: Dict[str, Any]) -> None:
        """
        사용자의 감정 반응 및 응답 선호 업데이트

        Args:
            user_id: 사용자 식별자
            new_data: 새로운 상호작용 데이터
        """
        self.analysis_count += 1

        # 기존 프로필 로드 또는 새 프로필 생성
        profile = self.get_user_profile(user_id)

        # 상호작용 패턴 추가
        if "interaction" in new_data:
            interaction = InteractionPattern(**new_data["interaction"])
            profile["interaction_history"].append(asdict(interaction))

            # 히스토리 크기 제한 (최근 100개)
            if len(profile["interaction_history"]) > 100:
                profile["interaction_history"] = profile["interaction_history"][-100:]

        # 텍스트 분석을 통한 트리거 패턴 업데이트
        if "user_input" in new_data:
            self._update_trigger_patterns(profile, new_data["user_input"])

        # 감정 프로필 동적 업데이트
        if "emotion_data" in new_data:
            self._update_emotion_profile(profile, new_data["emotion_data"])

        # 응답 선호도 학습
        if "feedback" in new_data:
            self._update_response_preferences(profile, new_data["feedback"])

        # 프로필 메타데이터 업데이트
        profile["metadata"]["last_updated"] = datetime.now().isoformat()
        profile["metadata"]["total_interactions"] += 1
        profile["metadata"]["profile_version"] += 0.1

        # 저장
        self._save_user_profile(user_id, profile)

        # 캐시 업데이트
        self.profiles_cache[user_id] = profile

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        사용자별 반응 패턴, 선호 전략 반환

        Args:
            user_id: 사용자 식별자

        Returns:
            사용자 프로필 딕셔너리
        """
        # 캐시에서 먼저 확인
        if user_id in self.profiles_cache:
            return self.profiles_cache[user_id]

        # 파일에서 로드
        profile_path = os.path.join(self.data_dir, f"{user_id}.json")

        if os.path.exists(profile_path):
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                self.profiles_cache[user_id] = profile
                return profile
            except Exception as e:
                print(f"⚠️ 프로필 로드 실패 ({user_id}): {e}")

        # 새 프로필 생성
        profile = self._create_new_profile(user_id)
        self.profiles_cache[user_id] = profile
        self._save_user_profile(user_id, profile)

        return profile

    def _create_new_profile(self, user_id: str) -> Dict[str, Any]:
        """새 사용자 프로필 생성"""
        return {
            "user_id": user_id,
            "emotion_profile": asdict(EmotionProfile()),
            "response_preferences": asdict(ResponsePreferences()),
            "trigger_patterns": {
                category: [] for category in self.trigger_categories.keys()
            },
            "interaction_history": [],
            "learned_patterns": {
                "preferred_strategies": {},
                "effective_responses": [],
                "avoided_topics": [],
                "communication_style": "neutral",
            },
            "temporal_patterns": {
                "daily_mood_cycle": {},  # 시간대별 기분 패턴
                "weekly_patterns": {},  # 요일별 패턴
                "seasonal_effects": {},  # 계절적 영향
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_interactions": 0,
                "profile_version": 1.0,
                "confidence_score": 0.1,  # 프로필 신뢰도
            },
        }

    def _update_emotion_profile(
        self, profile: Dict[str, Any], emotion_data: Dict[str, Any]
    ) -> None:
        """감정 프로필 동적 업데이트"""
        emotion_profile = profile["emotion_profile"]

        # 감정 강도 기반 반응성 학습
        if "intensity" in emotion_data:
            intensity = emotion_data["intensity"]
            current_reactivity = emotion_profile["reactivity"]

            # 지수 이동 평균으로 반응성 업데이트
            alpha = 0.1  # 학습률
            emotion_profile["reactivity"] = (
                1 - alpha
            ) * current_reactivity + alpha * intensity

        # 감정 회복 속도 학습
        if "recovery_time" in emotion_data:
            recovery_time = emotion_data["recovery_time"]
            # 빠른 회복 = 높은 recovery_rate
            recovery_rate = max(
                0.0, min(1.0, 1.0 - (recovery_time / 3600))
            )  # 1시간 기준 정규화

            current_recovery = emotion_profile["recovery_rate"]
            emotion_profile["recovery_rate"] = (
                1 - alpha
            ) * current_recovery + alpha * recovery_rate

        # 기준선 기분 조정
        if "baseline_shift" in emotion_data:
            shift = emotion_data["baseline_shift"]
            current_baseline = emotion_profile["baseline_mood"]
            emotion_profile["baseline_mood"] = max(
                0.0, min(1.0, current_baseline + shift * 0.05)
            )

        # 감정 안정성 계산
        if len(profile["interaction_history"]) > 5:
            recent_emotions = [
                interaction.get("emotion_after", "neutral")
                for interaction in profile["interaction_history"][-10:]
            ]
            stability = self._calculate_emotional_stability(recent_emotions)
            emotion_profile["stability"] = stability

    def _update_response_preferences(
        self, profile: Dict[str, Any], feedback: Dict[str, Any]
    ) -> None:
        """응답 선호도 학습"""
        preferences = profile["response_preferences"]

        # 피드백 점수 기반 선호도 조정
        feedback_score = feedback.get("satisfaction_score", 0.5)
        response_style = feedback.get("response_style", {})

        alpha = 0.05  # 선호도 학습률 (더 보수적)

        for pref_key, pref_value in response_style.items():
            if pref_key in preferences:
                current_value = preferences[pref_key]

                # 긍정적 피드백이면 해당 스타일로 이동, 부정적이면 반대로 이동
                if feedback_score > 0.6:
                    target_value = pref_value
                elif feedback_score < 0.4:
                    target_value = 1.0 - pref_value
                else:
                    continue  # 중립적 피드백은 무시

                preferences[pref_key] = (
                    1 - alpha
                ) * current_value + alpha * target_value
                preferences[pref_key] = max(0.0, min(1.0, preferences[pref_key]))

    def _update_trigger_patterns(
        self, profile: Dict[str, Any], user_input: str
    ) -> None:
        """트리거 패턴 업데이트"""
        user_input_lower = user_input.lower()

        for category, keywords in self.trigger_categories.items():
            matches = [keyword for keyword in keywords if keyword in user_input_lower]

            if matches:
                # 기존 패턴에 새로운 키워드 추가
                existing_patterns = profile["trigger_patterns"][category]

                for match in matches:
                    if match not in existing_patterns:
                        existing_patterns.append(match)

                # 패턴 크기 제한 (카테고리당 최대 20개)
                if len(existing_patterns) > 20:
                    profile["trigger_patterns"][category] = existing_patterns[-20:]

    def _calculate_emotional_stability(self, emotion_sequence: List[str]) -> float:
        """감정 변화 시퀀스에서 안정성 계산"""
        if len(emotion_sequence) < 2:
            return 0.5

        # 감정 변화 횟수 계산
        changes = 0
        for i in range(1, len(emotion_sequence)):
            if emotion_sequence[i] != emotion_sequence[i - 1]:
                changes += 1

        # 안정성 = 1 - (변화율)
        change_rate = changes / (len(emotion_sequence) - 1)
        stability = 1.0 - change_rate

        return max(0.0, min(1.0, stability))

    def predict_optimal_strategy(
        self, user_id: str, current_emotion: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        사용자별 최적 전략 예측

        Args:
            user_id: 사용자 식별자
            current_emotion: 현재 감정
            context: 추가 컨텍스트

        Returns:
            최적 전략 추천
        """
        profile = self.get_user_profile(user_id)

        # 기본 전략 점수
        strategy_scores = {
            "soothe": 0.5,  # 위로하기
            "energize": 0.5,  # 활력 주기
            "analyze": 0.5,  # 분석적 접근
            "listen": 0.5,  # 경청하기
            "challenge": 0.5,  # 도전적 접근
            "humor": 0.5,  # 유머 사용
        }

        # 감정 프로필 기반 조정
        emotion_profile = profile["emotion_profile"]
        response_prefs = profile["response_preferences"]

        # 현재 감정에 따른 기본 전략 가중치
        emotion_strategy_weights = {
            "sadness": {"soothe": 0.8, "listen": 0.7, "analyze": 0.3},
            "anger": {"listen": 0.6, "analyze": 0.5, "challenge": 0.3},
            "fear": {"soothe": 0.7, "analyze": 0.6, "energize": 0.4},
            "joy": {"energize": 0.8, "humor": 0.6, "challenge": 0.5},
            "surprise": {"analyze": 0.6, "listen": 0.5, "energize": 0.4},
            "neutral": {"analyze": 0.5, "listen": 0.5, "energize": 0.5},
        }

        # 감정별 가중치 적용
        if current_emotion in emotion_strategy_weights:
            for strategy, weight in emotion_strategy_weights[current_emotion].items():
                strategy_scores[strategy] *= weight

        # 개인 선호도 반영
        strategy_scores["soothe"] *= 1.0 + response_prefs["empathy_level"]
        strategy_scores["analyze"] *= 1.0 + response_prefs["solution_focus"]
        strategy_scores["challenge"] *= 1.0 + response_prefs["directness"]
        strategy_scores["humor"] *= 1.0 + response_prefs["humor_acceptance"]

        # 과거 효과성 학습 반영
        learned_patterns = profile["learned_patterns"]["preferred_strategies"]
        for strategy, effectiveness in learned_patterns.items():
            if strategy in strategy_scores:
                strategy_scores[strategy] *= 0.5 + effectiveness

        # 컨텍스트 기반 조정
        if context:
            if context.get("urgency_level", 0) > 0.7:
                strategy_scores["analyze"] *= 1.3
                strategy_scores["humor"] *= 0.5

            if context.get("privacy_level", 0.5) < 0.3:  # 공개적 상황
                strategy_scores["humor"] *= 0.7
                strategy_scores["challenge"] *= 0.8

        # 최적 전략 선택
        best_strategy = max(strategy_scores, key=strategy_scores.get)
        confidence = strategy_scores[best_strategy]

        return {
            "recommended_strategy": best_strategy,
            "confidence": confidence,
            "all_scores": strategy_scores,
            "reasoning": self._generate_strategy_reasoning(
                current_emotion, emotion_profile, response_prefs, best_strategy
            ),
        }

    def _generate_strategy_reasoning(
        self, emotion: str, emotion_profile: Dict, response_prefs: Dict, strategy: str
    ) -> List[str]:
        """전략 선택 이유 생성"""
        reasoning = []

        # 감정 기반 추론
        reasoning.append(f"현재 감정 '{emotion}'에 적합한 접근법")

        # 개인 특성 기반 추론
        if response_prefs["empathy_level"] > 0.6 and strategy == "soothe":
            reasoning.append("사용자의 높은 공감 선호도에 맞는 위로 중심 접근")

        if response_prefs["solution_focus"] > 0.6 and strategy == "analyze":
            reasoning.append("해결책 지향적 성향에 맞는 분석적 접근")

        if emotion_profile["reactivity"] > 0.7 and strategy == "listen":
            reasoning.append("높은 감정 반응성을 고려한 경청 중심 접근")

        if emotion_profile["stability"] < 0.4 and strategy != "challenge":
            reasoning.append("감정 불안정성을 고려한 안전한 접근법 선택")

        return reasoning

    def analyze_user_evolution(self, user_id: str) -> Dict[str, Any]:
        """사용자 성향 변화 분석"""
        profile = self.get_user_profile(user_id)

        if len(profile["interaction_history"]) < 10:
            return {
                "message": "분석할 데이터 부족",
                "interactions": len(profile["interaction_history"]),
            }

        # 시간 구간별 감정 패턴 분석
        history = profile["interaction_history"]
        total_interactions = len(history)

        # 최근 20%, 중간 60%, 초기 20%로 구분
        early_period = history[: int(total_interactions * 0.2)]
        middle_period = history[
            int(total_interactions * 0.2) : int(total_interactions * 0.8)
        ]
        recent_period = history[int(total_interactions * 0.8) :]

        def analyze_period(interactions):
            emotions = [i.get("emotion_after", "neutral") for i in interactions]
            effectiveness = [i.get("effectiveness_score", 0.5) for i in interactions]

            return {
                "dominant_emotions": self._get_emotion_distribution(emotions),
                "avg_effectiveness": (
                    statistics.mean(effectiveness) if effectiveness else 0.5
                ),
                "interaction_count": len(interactions),
            }

        evolution_analysis = {
            "early_period": analyze_period(early_period),
            "middle_period": analyze_period(middle_period),
            "recent_period": analyze_period(recent_period),
            "overall_trends": self._calculate_trends(history),
            "profile_confidence": profile["metadata"]["confidence_score"],
        }

        return evolution_analysis

    def _get_emotion_distribution(self, emotions: List[str]) -> Dict[str, float]:
        """감정 분포 계산"""
        if not emotions:
            return {}

        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        total = len(emotions)
        return {emotion: count / total for emotion, count in emotion_counts.items()}

    def _calculate_trends(self, history: List[Dict]) -> Dict[str, Any]:
        """전체적 트렌드 계산"""
        if len(history) < 5:
            return {}

        # 효과성 트렌드
        effectiveness_scores = [
            interaction.get("effectiveness_score", 0.5) for interaction in history
        ]

        # 선형 회귀로 트렌드 계산 (간단한 버전)
        n = len(effectiveness_scores)
        x_values = list(range(n))

        # 기울기 계산
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(effectiveness_scores)

        numerator = sum(
            (x - x_mean) * (y - y_mean) for x, y in zip(x_values, effectiveness_scores)
        )
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        slope = numerator / denominator if denominator != 0 else 0

        return {
            "effectiveness_trend": (
                "improving"
                if slope > 0.01
                else "declining" if slope < -0.01 else "stable"
            ),
            "trend_strength": abs(slope),
            "recent_avg_effectiveness": (
                statistics.mean(effectiveness_scores[-10:])
                if len(effectiveness_scores) >= 10
                else y_mean
            ),
        }

    def _save_user_profile(self, user_id: str, profile: Dict[str, Any]) -> None:
        """사용자 프로필 저장"""
        profile_path = os.path.join(self.data_dir, f"{user_id}.json")

        try:
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 프로필 저장 실패 ({user_id}): {e}")

    def export_user_insights(self, user_id: str, filepath: str) -> bool:
        """사용자 인사이트 내보내기"""
        try:
            profile = self.get_user_profile(user_id)
            evolution = self.analyze_user_evolution(user_id)

            export_data = {
                "user_id": user_id,
                "export_timestamp": datetime.now().isoformat(),
                "profile_summary": {
                    "emotion_profile": profile["emotion_profile"],
                    "response_preferences": profile["response_preferences"],
                    "total_interactions": profile["metadata"]["total_interactions"],
                    "profile_confidence": profile["metadata"]["confidence_score"],
                },
                "evolution_analysis": evolution,
                "key_insights": self._generate_key_insights(profile, evolution),
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            print(f"✅ 사용자 인사이트 내보내기 완료: {filepath}")
            return True

        except Exception as e:
            print(f"❌ 인사이트 내보내기 실패: {e}")
            return False

    def _generate_key_insights(self, profile: Dict, evolution: Dict) -> List[str]:
        """핵심 인사이트 생성"""
        insights = []

        emotion_profile = profile["emotion_profile"]
        response_prefs = profile["response_preferences"]

        # 감정 특성 인사이트
        if emotion_profile["reactivity"] > 0.7:
            insights.append("감정 반응이 매우 민감한 사용자 - 세심한 접근 필요")
        elif emotion_profile["reactivity"] < 0.3:
            insights.append("감정 반응이 차분한 사용자 - 더 직접적인 접근 가능")

        if emotion_profile["recovery_rate"] > 0.7:
            insights.append("감정 회복이 빠른 편 - 적극적 개입 효과적")
        elif emotion_profile["recovery_rate"] < 0.3:
            insights.append("감정 회복이 느린 편 - 장기적 지원 필요")

        # 응답 선호도 인사이트
        if response_prefs["empathy_level"] > 0.7:
            insights.append("높은 공감을 선호 - 감정적 연결 중심 대화 효과적")

        if response_prefs["solution_focus"] > 0.7:
            insights.append("해결책 중심 접근 선호 - 실용적 조언 효과적")

        if response_prefs["directness"] > 0.7:
            insights.append("직접적 소통 선호 - 명확한 의사전달 중요")

        # 진화 트렌드 인사이트
        if evolution and "overall_trends" in evolution:
            trends = evolution["overall_trends"]
            if trends.get("effectiveness_trend") == "improving":
                insights.append("상호작용 효과성이 지속적으로 개선되고 있음")
            elif trends.get("effectiveness_trend") == "declining":
                insights.append("상호작용 효과성 저하 - 접근법 재검토 필요")

        return insights


def test_personality_profiler():
    """개인화 프로필러 테스트"""
    print("🧪 Personality Profiler 테스트 시작...")

    profiler = PersonalityProfiler()
    test_user_id = "test_user_001"

    # 테스트 시나리오 1: 새 사용자 프로필 생성
    print("\n📝 시나리오 1: 새 사용자 프로필 생성")
    profile = profiler.get_user_profile(test_user_id)
    print(f"✅ 새 프로필 생성 완료 - 버전: {profile['metadata']['profile_version']}")

    # 테스트 시나리오 2: 상호작용 데이터 업데이트
    print("\n📝 시나리오 2: 상호작용 데이터 업데이트")
    interaction_data = {
        "user_input": "요즘 일이 너무 스트레스받아서 힘들어요",
        "interaction": {
            "timestamp": datetime.now().isoformat(),
            "emotion_before": "neutral",
            "emotion_after": "sadness",
            "strategy_used": "soothe",
            "effectiveness_score": 0.8,
            "response_time": 2.5,
        },
        "emotion_data": {"intensity": 0.7, "recovery_time": 1800},  # 30분
    }

    profiler.update_user_profile(test_user_id, interaction_data)
    print("✅ 상호작용 데이터 업데이트 완료")

    # 테스트 시나리오 3: 최적 전략 예측
    print("\n📝 시나리오 3: 최적 전략 예측")
    strategy_recommendation = profiler.predict_optimal_strategy(
        test_user_id, "sadness", context={"urgency_level": 0.3, "privacy_level": 0.8}
    )

    print(f"🎯 추천 전략: {strategy_recommendation['recommended_strategy']}")
    print(f"💪 신뢰도: {strategy_recommendation['confidence']:.3f}")
    print(f"🧠 추론 근거:")
    for reason in strategy_recommendation["reasoning"]:
        print(f"   - {reason}")

    # 추가 상호작용 시뮬레이션
    print("\n📝 시나리오 4: 다중 상호작용 시뮬레이션")
    simulation_data = [
        {"emotion": "anger", "strategy": "listen", "effectiveness": 0.6},
        {"emotion": "joy", "strategy": "energize", "effectiveness": 0.9},
        {"emotion": "fear", "strategy": "soothe", "effectiveness": 0.7},
        {"emotion": "sadness", "strategy": "analyze", "effectiveness": 0.4},
        {"emotion": "neutral", "strategy": "humor", "effectiveness": 0.8},
    ]

    for i, data in enumerate(simulation_data):
        interaction = {
            "interaction": {
                "timestamp": (datetime.now() + timedelta(hours=i)).isoformat(),
                "emotion_before": "neutral",
                "emotion_after": data["emotion"],
                "strategy_used": data["strategy"],
                "effectiveness_score": data["effectiveness"],
                "response_time": 1.5 + i * 0.3,
            }
        }
        profiler.update_user_profile(test_user_id, interaction)

    print(f"✅ {len(simulation_data)}개 상호작용 시뮬레이션 완료")

    # 테스트 시나리오 5: 사용자 진화 분석
    print("\n📝 시나리오 5: 사용자 진화 분석")
    evolution = profiler.analyze_user_evolution(test_user_id)

    if "overall_trends" in evolution:
        trends = evolution["overall_trends"]
        print(f"📈 효과성 트렌드: {trends.get('effectiveness_trend', 'unknown')}")
        print(f"📊 최근 평균 효과성: {trends.get('recent_avg_effectiveness', 0):.3f}")

    # 프로필 요약 출력
    updated_profile = profiler.get_user_profile(test_user_id)
    emotion_profile = updated_profile["emotion_profile"]

    print(f"\n📋 최종 프로필 요약:")
    print(f"   반응성: {emotion_profile['reactivity']:.3f}")
    print(f"   회복속도: {emotion_profile['recovery_rate']:.3f}")
    print(f"   안정성: {emotion_profile['stability']:.3f}")
    print(f"   총 상호작용: {updated_profile['metadata']['total_interactions']}")

    print("\n🎉 Personality Profiler 테스트 완료!")


if __name__ == "__main__":
    test_personality_profiler()
