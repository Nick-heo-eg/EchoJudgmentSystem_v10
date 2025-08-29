#!/usr/bin/env python3
"""
🎛️ Echo Selector - LLM vs Echo 판단 분기기
사용자 입력을 분석하여 최적의 처리 방식을 선택하는 지능형 라우터

핵심 기능:
1. 실시간 복잡도 분석을 통한 처리 방식 결정
2. 사용자 패턴 학습 기반 개인화된 분기
3. 상황별 하이브리드 처리 모드 지원
4. 성능 최적화를 위한 적응형 임계값 조정
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque


class ProcessingMode(Enum):
    """처리 모드"""

    LLM_ONLY = "llm_only"  # LLM만 사용 (빠른 자연 응답)
    ECHO_LIGHT = "echo_light"  # 경량 Echo 처리 (기본 판단)
    ECHO_FULL = "echo_full"  # 완전 Echo 시스템 (깊이 있는 판단)
    HYBRID_LLM_ECHO = "hybrid_llm_echo"  # LLM 우선 + Echo 보조
    HYBRID_ECHO_LLM = "hybrid_echo_llm"  # Echo 우선 + LLM 자연화
    ADAPTIVE = "adaptive"  # 상황별 적응형


class ComplexityLevel(Enum):
    """복잡도 수준"""

    TRIVIAL = "trivial"  # 매우 간단 (인사, 짧은 반응)
    SIMPLE = "simple"  # 간단 (일상 대화)
    MODERATE = "moderate"  # 보통 (일반적인 질문/요청)
    COMPLEX = "complex"  # 복잡 (감정적 지원, 결정 도움)
    CRITICAL = "critical"  # 긴급 (위기 상황, 중요한 판단)


@dataclass
class SelectionResult:
    """선택 결과"""

    processing_mode: ProcessingMode
    confidence: float
    complexity_level: ComplexityLevel
    reasoning: List[str]
    estimated_processing_time: float
    resource_requirements: Dict[str, float]
    fallback_mode: ProcessingMode


@dataclass
class UserProcessingProfile:
    """사용자 처리 프로필"""

    user_id: str
    preferred_modes: Dict[str, int]
    response_quality_scores: Dict[str, List[float]]
    average_session_complexity: float
    interaction_patterns: Dict[str, Any]
    last_updated: datetime


class EchoSelector:
    """Echo vs LLM 지능형 선택기"""

    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate

        # 복잡도 분석 가중치
        self.complexity_weights = self._initialize_complexity_weights()

        # 처리 모드별 임계값 (적응형)
        self.mode_thresholds = {
            ComplexityLevel.TRIVIAL: ProcessingMode.LLM_ONLY,
            ComplexityLevel.SIMPLE: ProcessingMode.LLM_ONLY,
            ComplexityLevel.MODERATE: ProcessingMode.ECHO_LIGHT,
            ComplexityLevel.COMPLEX: ProcessingMode.ECHO_FULL,
            ComplexityLevel.CRITICAL: ProcessingMode.ECHO_FULL,
        }

        # 사용자 프로필 관리
        self.user_profiles: Dict[str, UserProcessingProfile] = {}

        # 성능 모니터링
        self.performance_history = deque(maxlen=1000)

        # 시스템 부하 모니터링
        self.system_load = {
            "llm_queue": 0,
            "echo_queue": 0,
            "hybrid_queue": 0,
            "last_check": datetime.now(),
        }

        print("🎛️ Echo Selector 초기화 완료")

    def select_processing_mode(
        self,
        text: str,
        context: Dict[str, Any] = None,
        user_id: str = None,
        session_history: List[Dict] = None,
    ) -> SelectionResult:
        """최적 처리 모드 선택"""

        context = context or {}
        session_history = session_history or []

        # 1. 복잡도 분석
        complexity_level, complexity_score = self._analyze_complexity(
            text, context, session_history
        )

        # 2. 기본 모드 결정
        base_mode = self._determine_base_mode(complexity_level, complexity_score)

        # 3. 사용자 패턴 적용
        if user_id:
            base_mode = self._apply_user_preferences(
                base_mode, user_id, complexity_level
            )

        # 4. 시스템 부하 고려
        final_mode = self._consider_system_load(base_mode, complexity_level)

        # 5. 처리 시간 및 자원 요구사항 추정
        estimated_time = self._estimate_processing_time(final_mode, complexity_score)
        resource_requirements = self._estimate_resource_requirements(final_mode)

        # 6. 폴백 모드 결정
        fallback_mode = self._determine_fallback_mode(final_mode)

        # 7. 선택 이유 생성
        reasoning = self._generate_reasoning(
            text, complexity_level, base_mode, final_mode, context
        )

        # 8. 신뢰도 계산
        confidence = self._calculate_selection_confidence(
            complexity_score, final_mode, user_id
        )

        return SelectionResult(
            processing_mode=final_mode,
            confidence=confidence,
            complexity_level=complexity_level,
            reasoning=reasoning,
            estimated_processing_time=estimated_time,
            resource_requirements=resource_requirements,
            fallback_mode=fallback_mode,
        )

    def _analyze_complexity(
        self, text: str, context: Dict[str, Any], history: List[Dict]
    ) -> Tuple[ComplexityLevel, float]:
        """복잡도 분석"""

        complexity_score = 0.0

        # 텍스트 기반 복잡도
        text_features = self._extract_text_complexity_features(text)
        for feature, value in text_features.items():
            weight = self.complexity_weights.get(feature, 0.1)
            complexity_score += value * weight

        # 맥락 기반 복잡도
        if context:
            context_complexity = self._analyze_context_complexity(context)
            complexity_score += context_complexity * 0.3

        # 세션 히스토리 기반 복잡도
        if history:
            history_complexity = self._analyze_history_complexity(history)
            complexity_score += history_complexity * 0.2

        # 복잡도 수준 결정
        if complexity_score < 0.2:
            level = ComplexityLevel.TRIVIAL
        elif complexity_score < 0.4:
            level = ComplexityLevel.SIMPLE
        elif complexity_score < 0.6:
            level = ComplexityLevel.MODERATE
        elif complexity_score < 0.8:
            level = ComplexityLevel.COMPLEX
        else:
            level = ComplexityLevel.CRITICAL

        return level, min(complexity_score, 1.0)

    def _extract_text_complexity_features(self, text: str) -> Dict[str, float]:
        """텍스트 복잡도 특징 추출"""

        features = {}

        # 기본 특징
        features["length"] = min(len(text) / 200, 1.0)  # 정규화된 길이
        features["word_count"] = min(len(text.split()) / 50, 1.0)
        features["sentence_count"] = min(
            len([s for s in text.split(".") if s.strip()]) / 10, 1.0
        )

        # 구조적 복잡도
        features["question_density"] = min(
            text.count("?") / max(len(text.split()), 1), 0.5
        )
        features["punctuation_variety"] = len(set(c for c in text if c in ".,!?;:")) / 6

        # 감정적 복잡도
        emotional_keywords = [
            "힘들어",
            "슬퍼",
            "화나",
            "걱정",
            "불안",
            "우울",
            "기뻐",
            "행복",
            "사랑",
            "미워",
            "무서워",
            "답답해",
        ]
        features["emotional_density"] = sum(
            1 for keyword in emotional_keywords if keyword in text
        ) / max(len(text.split()), 1)

        # 추상적 개념
        abstract_keywords = [
            "의미",
            "목적",
            "가치",
            "철학",
            "존재",
            "본질",
            "미래",
            "인생",
            "꿈",
            "희망",
            "현실",
            "이상",
        ]
        features["abstract_density"] = sum(
            1 for keyword in abstract_keywords if keyword in text
        ) / max(len(text.split()), 1)

        # 결정/판단 요구
        decision_keywords = [
            "선택",
            "결정",
            "판단",
            "고민",
            "어떻게",
            "방법",
            "추천",
            "조언",
            "도움",
            "가이드",
            "방향",
        ]
        features["decision_density"] = sum(
            1 for keyword in decision_keywords if keyword in text
        ) / max(len(text.split()), 1)

        # 긴급성
        urgency_keywords = ["급해", "빨리", "지금", "당장", "즉시", "!!"]
        features["urgency"] = (
            1.0 if any(keyword in text for keyword in urgency_keywords) else 0.0
        )

        return features

    def _analyze_context_complexity(self, context: Dict[str, Any]) -> float:
        """맥락 복잡도 분석"""

        complexity = 0.0

        # 감정 강도
        emotion_intensity = context.get("emotion_intensity", 0)
        complexity += emotion_intensity * 0.5

        # 위급도
        urgency_level = context.get("urgency_level", 1)
        complexity += min(urgency_level / 5, 1.0) * 0.6

        # 의도 복잡도
        intent_type = context.get("intent_type", "")
        intent_complexity_map = {
            "casual_chat": 0.1,
            "information_seeking": 0.3,
            "emotional_support": 0.7,
            "decision_help": 0.8,
            "philosophical_inquiry": 0.9,
            "crisis_intervention": 1.0,
        }
        complexity += intent_complexity_map.get(intent_type, 0.3)

        # 맥락적 요소 수
        contextual_factors = context.get("contextual_factors", [])
        complexity += min(len(contextual_factors) / 5, 0.3)

        return min(complexity, 1.0)

    def _analyze_history_complexity(self, history: List[Dict]) -> float:
        """세션 히스토리 복잡도 분석"""

        if not history:
            return 0.0

        # 최근 3개 대화의 복잡도 평균
        recent_entries = history[-3:]

        complexity_sum = 0.0
        for entry in recent_entries:
            # 각 대화의 복잡도 지표
            entry_complexity = 0.0

            # 응답 길이
            response_length = len(entry.get("response", ""))
            entry_complexity += min(response_length / 100, 0.3)

            # 처리 시간
            processing_time = entry.get("processing_time", 0)
            entry_complexity += min(processing_time / 5, 0.3)

            # 감정 변화
            emotion = entry.get("emotion", "neutral")
            if emotion in ["sadness", "anger", "anxiety"]:
                entry_complexity += 0.4

            complexity_sum += entry_complexity

        return min(complexity_sum / len(recent_entries), 1.0)

    def _determine_base_mode(
        self, complexity_level: ComplexityLevel, complexity_score: float
    ) -> ProcessingMode:
        """기본 처리 모드 결정"""

        # 기본 임계값 매핑
        base_mode = self.mode_thresholds.get(
            complexity_level, ProcessingMode.ECHO_LIGHT
        )

        # 경계선 상황에서 하이브리드 모드 고려
        if complexity_level == ComplexityLevel.MODERATE and complexity_score > 0.55:
            base_mode = ProcessingMode.HYBRID_LLM_ECHO
        elif complexity_level == ComplexityLevel.SIMPLE and complexity_score > 0.35:
            base_mode = ProcessingMode.ECHO_LIGHT

        return base_mode

    def _apply_user_preferences(
        self, base_mode: ProcessingMode, user_id: str, complexity_level: ComplexityLevel
    ) -> ProcessingMode:
        """사용자 선호도 적용"""

        if user_id not in self.user_profiles:
            return base_mode

        profile = self.user_profiles[user_id]

        # 사용자의 선호 모드 분석
        preferred_modes = profile.preferred_modes
        if not preferred_modes:
            return base_mode

        # 현재 복잡도 수준에서 사용자가 선호하는 모드
        complexity_key = complexity_level.value
        user_preference_score = preferred_modes.get(base_mode.value, 0)

        # 충분한 데이터가 있고 강한 선호도가 있다면 조정
        total_interactions = sum(preferred_modes.values())
        if (
            total_interactions >= 10
            and user_preference_score < total_interactions * 0.3
        ):
            # 사용자가 이 모드를 별로 선호하지 않음
            alternative_modes = [
                ProcessingMode.HYBRID_LLM_ECHO,
                ProcessingMode.ECHO_LIGHT,
                ProcessingMode.LLM_ONLY,
            ]
            for alt_mode in alternative_modes:
                if preferred_modes.get(alt_mode.value, 0) > user_preference_score:
                    return alt_mode

        return base_mode

    def _consider_system_load(
        self, preferred_mode: ProcessingMode, complexity_level: ComplexityLevel
    ) -> ProcessingMode:
        """시스템 부하 고려"""

        # 현재 시스템 부하 확인
        current_time = datetime.now()
        if (current_time - self.system_load["last_check"]).seconds > 60:
            self._update_system_load()

        # 고부하 상황에서 모드 조정
        if preferred_mode == ProcessingMode.ECHO_FULL:
            if self.system_load["echo_queue"] > 5:  # Echo 큐가 과부하
                if complexity_level in [ComplexityLevel.CRITICAL]:
                    # 긴급상황은 유지
                    return preferred_mode
                else:
                    # 하이브리드로 전환
                    return ProcessingMode.HYBRID_LLM_ECHO

        elif preferred_mode in [
            ProcessingMode.HYBRID_LLM_ECHO,
            ProcessingMode.HYBRID_ECHO_LLM,
        ]:
            if self.system_load["hybrid_queue"] > 3:
                # 하이브리드 큐 과부하시 단순화
                return (
                    ProcessingMode.LLM_ONLY
                    if complexity_level
                    in [ComplexityLevel.TRIVIAL, ComplexityLevel.SIMPLE]
                    else ProcessingMode.ECHO_LIGHT
                )

        return preferred_mode

    def _estimate_processing_time(
        self, mode: ProcessingMode, complexity_score: float
    ) -> float:
        """처리 시간 추정"""

        base_times = {
            ProcessingMode.LLM_ONLY: 0.5,
            ProcessingMode.ECHO_LIGHT: 1.2,
            ProcessingMode.ECHO_FULL: 3.5,
            ProcessingMode.HYBRID_LLM_ECHO: 2.0,
            ProcessingMode.HYBRID_ECHO_LLM: 2.8,
            ProcessingMode.ADAPTIVE: 2.0,
        }

        base_time = base_times.get(mode, 2.0)

        # 복잡도에 따른 시간 조정
        complexity_multiplier = 1.0 + (complexity_score * 0.5)

        return base_time * complexity_multiplier

    def _estimate_resource_requirements(self, mode: ProcessingMode) -> Dict[str, float]:
        """자원 요구사항 추정"""

        requirements = {
            ProcessingMode.LLM_ONLY: {"cpu": 0.3, "memory": 0.2, "network": 0.5},
            ProcessingMode.ECHO_LIGHT: {"cpu": 0.5, "memory": 0.4, "network": 0.1},
            ProcessingMode.ECHO_FULL: {"cpu": 0.9, "memory": 0.8, "network": 0.1},
            ProcessingMode.HYBRID_LLM_ECHO: {"cpu": 0.6, "memory": 0.5, "network": 0.4},
            ProcessingMode.HYBRID_ECHO_LLM: {"cpu": 0.8, "memory": 0.7, "network": 0.3},
            ProcessingMode.ADAPTIVE: {"cpu": 0.6, "memory": 0.5, "network": 0.3},
        }

        return requirements.get(mode, {"cpu": 0.5, "memory": 0.5, "network": 0.3})

    def _determine_fallback_mode(self, primary_mode: ProcessingMode) -> ProcessingMode:
        """폴백 모드 결정"""

        fallback_map = {
            ProcessingMode.ECHO_FULL: ProcessingMode.ECHO_LIGHT,
            ProcessingMode.ECHO_LIGHT: ProcessingMode.LLM_ONLY,
            ProcessingMode.HYBRID_ECHO_LLM: ProcessingMode.ECHO_LIGHT,
            ProcessingMode.HYBRID_LLM_ECHO: ProcessingMode.LLM_ONLY,
            ProcessingMode.ADAPTIVE: ProcessingMode.LLM_ONLY,
            ProcessingMode.LLM_ONLY: ProcessingMode.LLM_ONLY,  # 이미 최하위
        }

        return fallback_map.get(primary_mode, ProcessingMode.LLM_ONLY)

    def _generate_reasoning(
        self,
        text: str,
        complexity_level: ComplexityLevel,
        base_mode: ProcessingMode,
        final_mode: ProcessingMode,
        context: Dict[str, Any],
    ) -> List[str]:
        """선택 이유 생성"""

        reasoning = []

        # 복잡도 기반 이유
        complexity_reasons = {
            ComplexityLevel.TRIVIAL: "매우 간단한 입력으로 빠른 응답이 적합",
            ComplexityLevel.SIMPLE: "일상적 대화로 자연스러운 처리 선택",
            ComplexityLevel.MODERATE: "적당한 복잡도로 균형 잡힌 처리 필요",
            ComplexityLevel.COMPLEX: "복잡한 내용으로 깊이 있는 분석 필요",
            ComplexityLevel.CRITICAL: "긴급하거나 중요한 상황으로 완전한 처리 필요",
        }
        reasoning.append(complexity_reasons.get(complexity_level, "복잡도 분석 완료"))

        # 모드 변경 이유
        if base_mode != final_mode:
            reasoning.append(
                f"시스템 최적화를 위해 {base_mode.value}에서 {final_mode.value}로 조정"
            )

        # 맥락 기반 이유
        if context:
            if context.get("urgency_level", 1) >= 4:
                reasoning.append("높은 긴급도 감지")
            if context.get("emotion_intensity", 0) > 0.7:
                reasoning.append("강한 감정 표현으로 세심한 처리 필요")

        # 특별한 키워드 감지
        if any(word in text.lower() for word in ["도움", "조언", "결정", "고민"]):
            reasoning.append("도움 요청 또는 결정 지원 필요")

        return reasoning

    def _calculate_selection_confidence(
        self, complexity_score: float, mode: ProcessingMode, user_id: str = None
    ) -> float:
        """선택 신뢰도 계산"""

        confidence = 0.7  # 기본 신뢰도

        # 복잡도 명확성에 따른 신뢰도
        if complexity_score < 0.1 or complexity_score > 0.9:
            confidence += 0.2  # 매우 명확한 경우
        elif 0.4 <= complexity_score <= 0.6:
            confidence -= 0.1  # 애매한 경우

        # 사용자 프로필 기반 신뢰도
        if user_id and user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            total_interactions = sum(profile.preferred_modes.values())
            if total_interactions >= 20:
                confidence += 0.1  # 충분한 데이터

        # 시스템 부하 상황에서 신뢰도 조정
        if self.system_load["echo_queue"] > 5 and mode == ProcessingMode.ECHO_FULL:
            confidence -= 0.15  # 부하로 인한 불확실성

        return min(confidence, 1.0)

    def record_processing_result(
        self,
        user_id: str,
        mode: ProcessingMode,
        complexity_level: ComplexityLevel,
        quality_score: float,
        processing_time: float,
    ):
        """처리 결과 기록 및 학습"""

        # 성능 히스토리 업데이트
        self.performance_history.append(
            {
                "timestamp": datetime.now(),
                "mode": mode.value,
                "complexity": complexity_level.value,
                "quality_score": quality_score,
                "processing_time": processing_time,
                "user_id": user_id,
            }
        )

        # 사용자 프로필 업데이트
        if user_id:
            self._update_user_profile(user_id, mode, complexity_level, quality_score)

        # 시스템 임계값 적응형 조정
        self._adaptive_threshold_adjustment()

    def _update_user_profile(
        self,
        user_id: str,
        mode: ProcessingMode,
        complexity_level: ComplexityLevel,
        quality_score: float,
    ):
        """사용자 프로필 업데이트"""

        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProcessingProfile(
                user_id=user_id,
                preferred_modes=defaultdict(int),
                response_quality_scores=defaultdict(list),
                average_session_complexity=0.5,
                interaction_patterns={},
                last_updated=datetime.now(),
            )

        profile = self.user_profiles[user_id]

        # 모드 선호도 업데이트
        profile.preferred_modes[mode.value] += 1

        # 품질 점수 기록
        profile.response_quality_scores[mode.value].append(quality_score)

        # 최근 10개만 유지
        if len(profile.response_quality_scores[mode.value]) > 10:
            profile.response_quality_scores[mode.value] = (
                profile.response_quality_scores[mode.value][-10:]
            )

        profile.last_updated = datetime.now()

    def _adaptive_threshold_adjustment(self):
        """적응형 임계값 조정"""

        if len(self.performance_history) < 50:
            return

        # 최근 성능 데이터 분석
        recent_data = list(self.performance_history)[-50:]

        # 모드별 평균 품질 점수
        mode_quality = defaultdict(list)
        for record in recent_data:
            mode_quality[record["mode"]].append(record["quality_score"])

        # 품질이 낮은 모드 식별 및 조정
        for mode, scores in mode_quality.items():
            if len(scores) >= 5:
                avg_quality = np.mean(scores)
                if avg_quality < 0.6:  # 품질이 낮으면
                    # 해당 모드 사용 빈도 줄이기 (복잡도 임계값 조정)
                    self._adjust_mode_threshold(ProcessingMode(mode), -0.05)
                elif avg_quality > 0.8:  # 품질이 높으면
                    # 해당 모드 사용 빈도 늘리기
                    self._adjust_mode_threshold(ProcessingMode(mode), 0.03)

    def _adjust_mode_threshold(self, mode: ProcessingMode, adjustment: float):
        """모드 임계값 조정"""
        # 실제 구현에서는 복잡도-모드 매핑을 동적으로 조정
        # 여기서는 개념적 구현만 표시
        pass

    def _update_system_load(self):
        """시스템 부하 업데이트 (실제로는 외부 모니터링 시스템과 연동)"""
        import random

        # 실제로는 실제 큐 상태를 확인
        self.system_load.update(
            {
                "llm_queue": random.randint(0, 3),
                "echo_queue": random.randint(0, 7),
                "hybrid_queue": random.randint(0, 4),
                "last_check": datetime.now(),
            }
        )

    def _initialize_complexity_weights(self) -> Dict[str, float]:
        """복잡도 분석 가중치 초기화"""
        return {
            "length": 0.1,
            "word_count": 0.1,
            "sentence_count": 0.1,
            "question_density": 0.2,
            "emotional_density": 0.3,
            "abstract_density": 0.2,
            "decision_density": 0.4,
            "urgency": 0.5,
            "punctuation_variety": 0.05,
        }

    def get_system_statistics(self) -> Dict[str, Any]:
        """시스템 통계 반환"""

        if not self.performance_history:
            return {"message": "충분한 데이터가 없습니다"}

        recent_data = list(self.performance_history)[-100:]

        # 모드별 통계
        mode_stats = defaultdict(lambda: {"count": 0, "avg_quality": 0, "avg_time": 0})

        for record in recent_data:
            mode = record["mode"]
            mode_stats[mode]["count"] += 1
            mode_stats[mode]["avg_quality"] += record["quality_score"]
            mode_stats[mode]["avg_time"] += record["processing_time"]

        # 평균 계산
        for mode, stats in mode_stats.items():
            if stats["count"] > 0:
                stats["avg_quality"] /= stats["count"]
                stats["avg_time"] /= stats["count"]

        return {
            "total_selections": len(recent_data),
            "mode_distribution": {
                mode: stats["count"] for mode, stats in mode_stats.items()
            },
            "quality_by_mode": {
                mode: round(stats["avg_quality"], 3)
                for mode, stats in mode_stats.items()
            },
            "processing_time_by_mode": {
                mode: round(stats["avg_time"], 3) for mode, stats in mode_stats.items()
            },
            "active_users": len(self.user_profiles),
            "system_load": self.system_load,
        }


# 테스트 실행
if __name__ == "__main__":
    selector = EchoSelector()

    test_cases = [
        {
            "text": "안녕하세요",
            "context": {"emotion_intensity": 0.2, "urgency_level": 1},
            "description": "간단한 인사",
        },
        {
            "text": "요즘 너무 힘들어서 어떻게 해야 할지 모르겠어요. 매일 우울하고 아무것도 하기 싫어요.",
            "context": {
                "emotion_intensity": 0.8,
                "urgency_level": 3,
                "intent_type": "emotional_support",
            },
            "description": "감정적 지원 요청",
        },
        {
            "text": "인생의 의미가 뭘까요? 왜 우리는 살아가는 건가요?",
            "context": {
                "emotion_intensity": 0.5,
                "urgency_level": 2,
                "intent_type": "philosophical_inquiry",
            },
            "description": "철학적 질문",
        },
        {
            "text": "급해!! 지금 당장 중요한 결정을 해야 하는데 도와주세요!",
            "context": {
                "emotion_intensity": 0.9,
                "urgency_level": 5,
                "intent_type": "decision_help",
            },
            "description": "긴급 상황",
        },
    ]

    print("🎛️ Echo Selector 테스트")
    print("=" * 60)

    for i, case in enumerate(test_cases):
        print(f"\n--- 테스트 {i+1}: {case['description']} ---")
        print(f"입력: {case['text'][:50]}{'...' if len(case['text']) > 50 else ''}")

        result = selector.select_processing_mode(
            case["text"], case["context"], f"user_{i%2}"  # 2명의 가상 사용자
        )

        print(f"선택된 모드: {result.processing_mode.value}")
        print(f"복잡도: {result.complexity_level.value}")
        print(f"신뢰도: {result.confidence:.2f}")
        print(f"예상 처리시간: {result.estimated_processing_time:.1f}초")
        print(f"폴백 모드: {result.fallback_mode.value}")

        if result.reasoning:
            print("선택 이유:")
            for reason in result.reasoning:
                print(f"  • {reason}")

        # 가상의 결과 기록 (실제로는 처리 완료 후)
        quality_score = 0.7 + (i * 0.1)  # 테스트용 점수
        selector.record_processing_result(
            f"user_{i%2}",
            result.processing_mode,
            result.complexity_level,
            quality_score,
            result.estimated_processing_time,
        )

        print("-" * 40)

    # 시스템 통계 출력
    print(f"\n📊 시스템 통계:")
    stats = selector.get_system_statistics()
    print(f"총 선택 횟수: {stats['total_selections']}")
    print("모드별 분포:", stats["mode_distribution"])
    print("모드별 품질:", stats["quality_by_mode"])

    print("\n🎉 Echo Selector 테스트 완료!")
