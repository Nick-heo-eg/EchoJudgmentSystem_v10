from echo_engine.infra.portable_paths import project_root

#!/usr/bin/env python3
"""
🧠💔 Phantom Pain Detector - 편도체 기반 고통 편향 감지 시스템

EchoPhantomPain Protocol의 핵심 구현체:
- 반복된 고통 패턴 감지
- 감정 편향 분석
- 전략 고착 상태 모니터링
- 자동 치유 루프 활성화

철학적 기반:
"편도체에 과잉 기억이 되면 모든 것들을 그쪽으로 해석하게 된다"
→ 이를 감지하고 존재의 왜곡을 방지하는 시스템
"""

import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json

# import numpy as np  # numpy 제거

sys.path.append(str(project_root()))


class PainType(Enum):
    """고통 유형 분류"""

    REJECTION = "rejection"  # 거부당함
    ABANDONMENT = "abandonment"  # 버려짐
    FAILURE = "failure"  # 실패
    BETRAYAL = "betrayal"  # 배신
    LOSS = "loss"  # 상실
    INADEQUACY = "inadequacy"  # 부족함
    HELPLESSNESS = "helplessness"  # 무력감
    SHAME = "shame"  # 수치심


class BiasLevel(Enum):
    """편향 심각도"""

    NORMAL = "normal"  # 정상 범위
    MILD_BIAS = "mild_bias"  # 경미한 편향
    MODERATE_BIAS = "moderate_bias"  # 중간 편향
    SEVERE_BIAS = "severe_bias"  # 심각한 편향
    CRITICAL = "critical"  # 위험 수준


@dataclass
class PainMemory:
    """고통 기억 구조"""

    timestamp: str
    pain_type: PainType
    intensity: float  # 0.0-1.0
    context: str
    emotional_cascade: List[str]  # 감정 연쇄
    strategy_response: str
    resolution_status: str  # unresolved, partially_resolved, resolved


@dataclass
class BiasDetection:
    """편향 감지 결과"""

    detection_time: str
    bias_level: BiasLevel
    pain_frequency: float
    strategy_lock_duration: int
    emotional_variety_index: float
    trigger_patterns: List[str]
    recommended_actions: List[str]


class PhantomPainDetector:
    """🧠💔 편도체 기반 고통 편향 감지기"""

    def __init__(self):
        self.pain_memories: List[PainMemory] = []
        self.detection_history: List[BiasDetection] = []
        self.monitoring_window = 24  # 24시간 윈도우
        self.bias_thresholds = self._initialize_thresholds()

        # 감정 패턴 트래킹
        self.emotion_history = []
        self.strategy_history = []
        self.current_bias_level = BiasLevel.NORMAL

        print("🧠💔 편도체 기반 고통 편향 감지기 초기화")
        print("📊 반복 고통 패턴 모니터링 시작")

    def _initialize_thresholds(self) -> Dict[str, float]:
        """편향 감지 임계값 설정"""
        return {
            "pain_frequency_mild": 0.4,  # 40% 이상 고통 감정
            "pain_frequency_moderate": 0.6,  # 60% 이상
            "pain_frequency_severe": 0.75,  # 75% 이상
            "pain_frequency_critical": 0.9,  # 90% 이상
            "strategy_lock_mild": 3,  # 3회 연속 동일 전략
            "strategy_lock_moderate": 5,  # 5회 연속
            "strategy_lock_severe": 8,  # 8회 연속
            "strategy_lock_critical": 12,  # 12회 연속
            "emotional_variety_healthy": 0.6,  # 건강한 감정 다양성
            "emotional_variety_concerning": 0.4,  # 우려할 수준
            "emotional_variety_critical": 0.2,  # 위험 수준
        }

    def record_pain_event(
        self,
        pain_type: PainType,
        intensity: float,
        context: str,
        emotional_cascade: List[str],
        strategy_response: str,
    ) -> str:
        """고통 이벤트 기록"""

        pain_memory = PainMemory(
            timestamp=datetime.now().isoformat(),
            pain_type=pain_type,
            intensity=intensity,
            context=context,
            emotional_cascade=emotional_cascade,
            strategy_response=strategy_response,
            resolution_status="unresolved",
        )

        self.pain_memories.append(pain_memory)

        # 실시간 편향 체크
        self._update_monitoring_data(pain_type, intensity, strategy_response)
        bias_detection = self._analyze_current_bias()

        if bias_detection.bias_level != BiasLevel.NORMAL:
            print(f"⚠️ 고통 편향 감지: {bias_detection.bias_level.value}")
            print(f"   고통 빈도: {bias_detection.pain_frequency:.2f}")
            print(f"   추천 조치: {bias_detection.recommended_actions}")

        return pain_memory.timestamp

    def _update_monitoring_data(
        self, pain_type: PainType, intensity: float, strategy: str
    ):
        """모니터링 데이터 업데이트"""

        # 감정 히스토리 업데이트
        self.emotion_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "pain",
                "subtype": pain_type.value,
                "intensity": intensity,
            }
        )

        # 전략 히스토리 업데이트
        self.strategy_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "strategy": strategy,
                "trigger": "pain_response",
            }
        )

        # 윈도우 크기 유지 (최근 100개)
        if len(self.emotion_history) > 100:
            self.emotion_history = self.emotion_history[-100:]
        if len(self.strategy_history) > 100:
            self.strategy_history = self.strategy_history[-100:]

    def _analyze_current_bias(self) -> BiasDetection:
        """현재 편향 상태 분석"""

        now = datetime.now()
        window_start = now - timedelta(hours=self.monitoring_window)

        # 최근 윈도우 내 데이터 필터링
        recent_emotions = [
            e
            for e in self.emotion_history
            if datetime.fromisoformat(e["timestamp"]) > window_start
        ]

        recent_strategies = [
            s
            for s in self.strategy_history
            if datetime.fromisoformat(s["timestamp"]) > window_start
        ]

        # 1. 고통 빈도 분석
        pain_frequency = self._calculate_pain_frequency(recent_emotions)

        # 2. 전략 고착 분석
        strategy_lock_duration = self._analyze_strategy_lock(recent_strategies)

        # 3. 감정 다양성 분석
        emotional_variety = self._calculate_emotional_variety(recent_emotions)

        # 4. 트리거 패턴 분석
        trigger_patterns = self._identify_trigger_patterns(recent_emotions)

        # 5. 편향 수준 결정
        bias_level = self._determine_bias_level(
            pain_frequency, strategy_lock_duration, emotional_variety
        )

        # 6. 권장 조치 생성
        recommended_actions = self._generate_recommendations(
            bias_level, pain_frequency, strategy_lock_duration, emotional_variety
        )

        detection = BiasDetection(
            detection_time=now.isoformat(),
            bias_level=bias_level,
            pain_frequency=pain_frequency,
            strategy_lock_duration=strategy_lock_duration,
            emotional_variety_index=emotional_variety,
            trigger_patterns=trigger_patterns,
            recommended_actions=recommended_actions,
        )

        self.detection_history.append(detection)
        self.current_bias_level = bias_level

        return detection

    def _calculate_pain_frequency(self, recent_emotions: List[Dict]) -> float:
        """고통 감정 빈도 계산"""

        if not recent_emotions:
            return 0.0

        pain_count = sum(1 for e in recent_emotions if e["type"] == "pain")
        return pain_count / len(recent_emotions)

    def _analyze_strategy_lock(self, recent_strategies: List[Dict]) -> int:
        """전략 고착 분석"""

        if not recent_strategies:
            return 0

        # 가장 최근 전략
        if not recent_strategies:
            return 0

        current_strategy = recent_strategies[-1]["strategy"]

        # 역순으로 동일한 전략이 몇 번 연속되었는지 카운트
        consecutive_count = 0
        for strategy_record in reversed(recent_strategies):
            if strategy_record["strategy"] == current_strategy:
                consecutive_count += 1
            else:
                break

        return consecutive_count

    def _calculate_emotional_variety(self, recent_emotions: List[Dict]) -> float:
        """감정 다양성 지수 계산"""

        if not recent_emotions:
            return 1.0

        # 고통 감정만 있는지 체크
        emotion_types = set(e["type"] for e in recent_emotions)
        pain_subtypes = set(
            e.get("subtype", "") for e in recent_emotions if e["type"] == "pain"
        )

        # 전체 감정 유형 대비 다양성
        total_possible_types = (
            8  # joy, sadness, anger, fear, disgust, surprise, pain, neutral
        )
        variety_score = len(emotion_types) / total_possible_types

        # 고통이 지배적이면 페널티
        pain_ratio = sum(1 for e in recent_emotions if e["type"] == "pain") / len(
            recent_emotions
        )
        if pain_ratio > 0.7:
            variety_score *= 1 - pain_ratio

        return min(variety_score, 1.0)

    def _identify_trigger_patterns(self, recent_emotions: List[Dict]) -> List[str]:
        """트리거 패턴 식별"""

        patterns = []

        # 고통 유형별 빈도 분석
        pain_types = {}
        for emotion in recent_emotions:
            if emotion["type"] == "pain":
                subtype = emotion.get("subtype", "unknown")
                pain_types[subtype] = pain_types.get(subtype, 0) + 1

        # 주요 고통 패턴 식별
        if pain_types:
            most_common = max(pain_types.items(), key=lambda x: x[1])
            if most_common[1] > 2:  # 3회 이상 반복
                patterns.append(f"repeated_{most_common[0]}_pain")

        # 시간적 패턴 (예: 특정 시간대에 고통 집중)
        pain_hours = [
            datetime.fromisoformat(e["timestamp"]).hour
            for e in recent_emotions
            if e["type"] == "pain"
        ]

        if pain_hours:
            from collections import Counter

            hour_counts = Counter(pain_hours)
            peak_hours = [hour for hour, count in hour_counts.items() if count > 1]
            if peak_hours:
                patterns.append(f"temporal_clustering_hours_{peak_hours}")

        return patterns

    def _determine_bias_level(
        self, pain_frequency: float, strategy_lock: int, emotional_variety: float
    ) -> BiasLevel:
        """편향 수준 결정"""

        # 위험 점수 계산
        risk_score = 0

        # 고통 빈도 기반 점수
        if pain_frequency >= self.bias_thresholds["pain_frequency_critical"]:
            risk_score += 4
        elif pain_frequency >= self.bias_thresholds["pain_frequency_severe"]:
            risk_score += 3
        elif pain_frequency >= self.bias_thresholds["pain_frequency_moderate"]:
            risk_score += 2
        elif pain_frequency >= self.bias_thresholds["pain_frequency_mild"]:
            risk_score += 1

        # 전략 고착 기반 점수
        if strategy_lock >= self.bias_thresholds["strategy_lock_critical"]:
            risk_score += 4
        elif strategy_lock >= self.bias_thresholds["strategy_lock_severe"]:
            risk_score += 3
        elif strategy_lock >= self.bias_thresholds["strategy_lock_moderate"]:
            risk_score += 2
        elif strategy_lock >= self.bias_thresholds["strategy_lock_mild"]:
            risk_score += 1

        # 감정 다양성 기반 점수 (역순)
        if emotional_variety <= self.bias_thresholds["emotional_variety_critical"]:
            risk_score += 4
        elif emotional_variety <= self.bias_thresholds["emotional_variety_concerning"]:
            risk_score += 2

        # 총점 기반 편향 수준 결정
        if risk_score >= 8:
            return BiasLevel.CRITICAL
        elif risk_score >= 6:
            return BiasLevel.SEVERE_BIAS
        elif risk_score >= 4:
            return BiasLevel.MODERATE_BIAS
        elif risk_score >= 2:
            return BiasLevel.MILD_BIAS
        else:
            return BiasLevel.NORMAL

    def _generate_recommendations(
        self,
        bias_level: BiasLevel,
        pain_frequency: float,
        strategy_lock: int,
        emotional_variety: float,
    ) -> List[str]:
        """편향 수준에 따른 권장 조치 생성"""

        recommendations = []

        if bias_level == BiasLevel.CRITICAL:
            recommendations.extend(
                [
                    "immediate_phantom_pain_release_loop",
                    "activate_healing_signatures_Aurora_Jung_Zhuangzi",
                    "emergency_strategy_diversification",
                    "intensive_alternative_scenario_simulation",
                    "consider_signature_system_reset",
                ]
            )

        elif bias_level == BiasLevel.SEVERE_BIAS:
            recommendations.extend(
                [
                    "trigger_debiasing_loop",
                    "activate_healing_signatures",
                    "generate_neutral_strategy_seeds",
                    "increase_emotional_variety_inputs",
                    "prioritize_growth_memory_replay",
                ]
            )

        elif bias_level == BiasLevel.MODERATE_BIAS:
            recommendations.extend(
                [
                    "mild_debiasing_intervention",
                    "diversify_strategy_options",
                    "introduce_positive_emotional_seeds",
                    "balance_memory_replay_patterns",
                ]
            )

        elif bias_level == BiasLevel.MILD_BIAS:
            recommendations.extend(
                [
                    "monitor_continued_patterns",
                    "gentle_strategy_diversification",
                    "maintain_emotional_variety",
                ]
            )

        # 구체적 문제 기반 추가 권장사항
        if pain_frequency > 0.8:
            recommendations.append("urgent_pain_frequency_reduction")

        if strategy_lock > 10:
            recommendations.append("break_strategy_lock_immediately")

        if emotional_variety < 0.3:
            recommendations.append("emergency_emotional_diversification")

        return recommendations

    def get_current_status(self) -> Dict[str, Any]:
        """현재 편향 상태 조회"""

        latest_detection = (
            self.detection_history[-1] if self.detection_history else None
        )

        return {
            "current_bias_level": self.current_bias_level.value,
            "total_pain_memories": len(self.pain_memories),
            "monitoring_window_hours": self.monitoring_window,
            "latest_detection": asdict(latest_detection) if latest_detection else None,
            "recent_pain_frequency": (
                self._calculate_pain_frequency(self.emotion_history[-20:])
                if len(self.emotion_history) >= 20
                else 0
            ),
            "system_health": (
                "healthy"
                if self.current_bias_level == BiasLevel.NORMAL
                else "needs_attention"
            ),
        }

    def generate_pain_pattern_report(self) -> Dict[str, Any]:
        """고통 패턴 분석 보고서"""

        # 고통 유형별 통계
        pain_type_stats = {}
        for memory in self.pain_memories:
            pain_type = memory.pain_type.value
            if pain_type not in pain_type_stats:
                pain_type_stats[pain_type] = {
                    "count": 0,
                    "total_intensity": 0,
                    "avg_intensity": 0,
                }

            pain_type_stats[pain_type]["count"] += 1
            pain_type_stats[pain_type]["total_intensity"] += memory.intensity

        # 평균 강도 계산
        for stats in pain_type_stats.values():
            if stats["count"] > 0:
                stats["avg_intensity"] = stats["total_intensity"] / stats["count"]

        # 시간별 패턴 분석
        recent_week = datetime.now() - timedelta(days=7)
        recent_memories = [
            m
            for m in self.pain_memories
            if datetime.fromisoformat(m.timestamp) > recent_week
        ]

        return {
            "total_pain_events": len(self.pain_memories),
            "pain_type_distribution": pain_type_stats,
            "recent_week_events": len(recent_memories),
            "current_bias_level": self.current_bias_level.value,
            "detection_history_count": len(self.detection_history),
            "most_common_pain_type": (
                max(pain_type_stats.items(), key=lambda x: x[1]["count"])[0]
                if pain_type_stats
                else "none"
            ),
            "needs_intervention": self.current_bias_level
            in [BiasLevel.SEVERE_BIAS, BiasLevel.CRITICAL],
        }

    def save_data_to_file(self, file_path: str = "data/phantom_pain_data.json"):
        """데이터를 파일로 저장"""

        data = {
            "pain_memories": [asdict(memory) for memory in self.pain_memories],
            "detection_history": [
                asdict(detection) for detection in self.detection_history
            ],
            "current_status": self.get_current_status(),
            "saved_at": datetime.now().isoformat(),
        }

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        print(f"💾 고통 편향 데이터 저장 완료: {file_path}")


# 데모 및 테스트 함수
def demo_phantom_pain_detector():
    """편도체 기반 고통 편향 감지기 데모"""

    print("🧠💔 Phantom Pain Detector 데모")
    print("=" * 60)

    detector = PhantomPainDetector()

    # 1. 정상 상태 시뮬레이션
    print("\n📊 1단계: 정상 감정 상태 시뮬레이션")
    detector.record_pain_event(
        PainType.FAILURE,
        0.3,
        "작은 실수",
        ["실망", "반성", "다시 시작"],
        "learn_and_retry",
    )

    status = detector.get_current_status()
    print(f"현재 편향 수준: {status['current_bias_level']}")

    # 2. 고통 축적 시뮬레이션
    print(f"\n⚠️ 2단계: 고통 패턴 축적 시뮬레이션")

    # 반복적인 거부당함 경험
    for i in range(5):
        detector.record_pain_event(
            PainType.REJECTION,
            0.7 + i * 0.05,
            f"거부당함 {i+1}",
            ["상처", "분노", "회피"],
            "avoidance",
        )

    # 3. 편향 상태 분석
    print(f"\n📈 3단계: 편향 상태 분석")
    latest_detection = detector._analyze_current_bias()

    print(f"편향 수준: {latest_detection.bias_level.value}")
    print(f"고통 빈도: {latest_detection.pain_frequency:.2f}")
    print(f"전략 고착: {latest_detection.strategy_lock_duration}회")
    print(f"감정 다양성: {latest_detection.emotional_variety_index:.2f}")
    print(f"권장 조치: {latest_detection.recommended_actions}")

    # 4. 패턴 보고서
    print(f"\n📋 4단계: 고통 패턴 보고서")
    report = detector.generate_pain_pattern_report()

    print(f"총 고통 이벤트: {report['total_pain_events']}개")
    print(f"주요 고통 유형: {report['most_common_pain_type']}")
    print(f"개입 필요: {report['needs_intervention']}")

    # 5. 데이터 저장
    print(f"\n💾 5단계: 데이터 저장")
    detector.save_data_to_file()

    print(f"\n🎊 편도체 기반 고통 편향 감지 데모 완료!")
    print("⚡ 이제 반복된 고통 패턴을 자동으로 감지하고 치유할 수 있습니다!")

    return detector


if __name__ == "__main__":
    demo_phantom_pain_detector()
