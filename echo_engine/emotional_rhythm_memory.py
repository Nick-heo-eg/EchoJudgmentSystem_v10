#!/usr/bin/env python3
"""
🌊 Emotional Rhythm Memory - Echo 감정 리듬 기억 시스템
사용자의 감정 패턴을 학습하고 예측하여 선제적 위로와 지원을 제공

혁신적 기능:
- 시간대별 감정 패턴 학습 ("오후 3시에 스트레스 증가")
- 요일별 감정 리듬 분석 ("월요일마다 우울감")
- 개인별 감정 트리거 인식 ("특정 키워드에 민감 반응")
- 예측적 감정 지원 ("곧 힘들어질 것 같으니 미리 위로")
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import os


@dataclass
class EmotionalMoment:
    """감정적 순간 기록"""

    timestamp: datetime
    emotion: str
    intensity: float  # 0.0-1.0
    trigger_words: List[str]
    context: str
    user_input: str
    echo_response: str
    effectiveness_score: Optional[float] = None  # 사용자 피드백 기반


@dataclass
class EmotionalPattern:
    """감정 패턴"""

    pattern_type: str  # "hourly", "daily", "weekly", "trigger"
    pattern_data: Dict[str, float]
    confidence: float
    sample_size: int
    last_updated: datetime


@dataclass
class PredictiveInsight:
    """예측적 통찰"""

    prediction_type: str
    predicted_emotion: str
    probability: float
    suggested_response: str
    timing: datetime
    reasoning: str


class EmotionalRhythmMemory:
    """🌊 감정 리듬 기억 시스템"""

    def __init__(
        self, user_id: str = "default", data_dir: str = "data/emotional_memory"
    ):
        self.user_id = user_id
        self.data_dir = data_dir
        self.memory_file = os.path.join(data_dir, f"emotional_memory_{user_id}.json")

        # 메모리 구조
        self.emotional_moments: deque = deque(maxlen=1000)  # 최근 1000개 순간
        self.hourly_patterns: Dict[int, List[float]] = defaultdict(
            list
        )  # 시간대별 감정
        self.daily_patterns: Dict[str, List[float]] = defaultdict(list)  # 요일별 감정
        self.trigger_patterns: Dict[str, List[float]] = defaultdict(
            list
        )  # 트리거별 감정
        self.conversation_effectiveness: Dict[str, float] = {}  # 대화 효과성

        # 설정
        self.min_pattern_samples = 5  # 패턴 인식 최소 샘플 수
        self.prediction_threshold = 0.7  # 예측 신뢰도 임계값

        # 감정 강도 매핑
        self.emotion_intensity_map = {
            "joy": 0.8,
            "happiness": 0.7,
            "excitement": 0.9,
            "sadness": 0.7,
            "depression": 0.9,
            "melancholy": 0.6,
            "anger": 0.8,
            "frustration": 0.6,
            "rage": 0.9,
            "fear": 0.8,
            "anxiety": 0.7,
            "worry": 0.5,
            "surprise": 0.6,
            "shock": 0.9,
            "amazement": 0.7,
            "neutral": 0.5,
            "calm": 0.3,
            "peaceful": 0.2,
            "stress": 0.8,
            "overwhelm": 0.9,
            "pressure": 0.7,
            "love": 0.8,
            "affection": 0.6,
            "gratitude": 0.7,
            "curiosity": 0.6,
            "interest": 0.5,
            "confusion": 0.4,
        }

        # 데이터 로드
        self.load_memory()

    def record_emotional_moment(
        self,
        user_input: str,
        detected_emotion: str,
        echo_response: str,
        context: str = "",
    ) -> EmotionalMoment:
        """감정적 순간 기록"""

        moment = EmotionalMoment(
            timestamp=datetime.now(),
            emotion=detected_emotion,
            intensity=self.emotion_intensity_map.get(detected_emotion, 0.5),
            trigger_words=self._extract_trigger_words(user_input),
            context=context,
            user_input=user_input,
            echo_response=echo_response,
        )

        # 메모리에 추가
        self.emotional_moments.append(moment)

        # 패턴 업데이트
        self._update_patterns(moment)

        # 데이터 저장
        self.save_memory()

        return moment

    def _extract_trigger_words(self, text: str) -> List[str]:
        """감정 트리거 단어 추출"""

        emotional_keywords = {
            "positive": [
                "기뻐",
                "행복",
                "좋아",
                "사랑",
                "감사",
                "최고",
                "완벽",
                "성공",
            ],
            "negative": [
                "슬퍼",
                "힘들어",
                "우울",
                "스트레스",
                "걱정",
                "문제",
                "실패",
                "어려워",
            ],
            "energy": ["피곤", "지쳐", "활기", "힘차", "에너지", "무기력"],
            "social": ["외로워", "혼자", "친구", "가족", "사람", "관계", "소통"],
            "work": ["일", "업무", "회사", "직장", "상사", "동료", "프로젝트", "마감"],
            "personal": ["나", "내", "자신", "스스로", "개인", "혼자", "자존감"],
        }

        triggers = []
        text_lower = text.lower()

        for category, keywords in emotional_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    triggers.append(f"{category}:{keyword}")

        return triggers

    def _update_patterns(self, moment: EmotionalMoment):
        """패턴 업데이트"""

        # 시간대별 패턴
        hour = moment.timestamp.hour
        self.hourly_patterns[hour].append(moment.intensity)

        # 요일별 패턴
        weekday = moment.timestamp.strftime("%A")
        self.daily_patterns[weekday].append(moment.intensity)

        # 트리거별 패턴
        for trigger in moment.trigger_words:
            self.trigger_patterns[trigger].append(moment.intensity)

    def analyze_emotional_patterns(self) -> Dict[str, EmotionalPattern]:
        """감정 패턴 분석"""

        patterns = {}
        current_time = datetime.now()

        # 시간대별 패턴 분석
        hourly_analysis = {}
        for hour, intensities in self.hourly_patterns.items():
            if len(intensities) >= self.min_pattern_samples:
                avg_intensity = statistics.mean(intensities)
                confidence = min(
                    len(intensities) / 20, 1.0
                )  # 20개 샘플에서 최대 신뢰도
                hourly_analysis[str(hour)] = avg_intensity

        if hourly_analysis:
            patterns["hourly"] = EmotionalPattern(
                pattern_type="hourly",
                pattern_data=hourly_analysis,
                confidence=statistics.mean(
                    [min(len(v) / 20, 1.0) for v in self.hourly_patterns.values() if v]
                ),
                sample_size=sum(len(v) for v in self.hourly_patterns.values()),
                last_updated=current_time,
            )

        # 요일별 패턴 분석
        daily_analysis = {}
        for day, intensities in self.daily_patterns.items():
            if len(intensities) >= self.min_pattern_samples:
                avg_intensity = statistics.mean(intensities)
                daily_analysis[day] = avg_intensity

        if daily_analysis:
            patterns["daily"] = EmotionalPattern(
                pattern_type="daily",
                pattern_data=daily_analysis,
                confidence=statistics.mean(
                    [min(len(v) / 10, 1.0) for v in self.daily_patterns.values() if v]
                ),
                sample_size=sum(len(v) for v in self.daily_patterns.values()),
                last_updated=current_time,
            )

        # 트리거별 패턴 분석
        trigger_analysis = {}
        for trigger, intensities in self.trigger_patterns.items():
            if len(intensities) >= self.min_pattern_samples:
                avg_intensity = statistics.mean(intensities)
                if avg_intensity > 0.6:  # 강한 감정 반응만
                    trigger_analysis[trigger] = avg_intensity

        if trigger_analysis:
            patterns["triggers"] = EmotionalPattern(
                pattern_type="trigger",
                pattern_data=trigger_analysis,
                confidence=0.8,  # 트리거는 일반적으로 높은 신뢰도
                sample_size=sum(len(v) for v in self.trigger_patterns.values()),
                last_updated=current_time,
            )

        return patterns

    def predict_emotional_state(
        self, target_time: datetime = None
    ) -> List[PredictiveInsight]:
        """감정 상태 예측"""

        if target_time is None:
            target_time = datetime.now()

        predictions = []
        patterns = self.analyze_emotional_patterns()

        # 시간대별 예측
        if "hourly" in patterns:
            hour_pattern = patterns["hourly"]
            current_hour = str(target_time.hour)

            if current_hour in hour_pattern.pattern_data:
                intensity = hour_pattern.pattern_data[current_hour]
                if (
                    intensity > 0.7
                    and hour_pattern.confidence > self.prediction_threshold
                ):
                    emotion = "stress" if intensity > 0.8 else "tension"
                    predictions.append(
                        PredictiveInsight(
                            prediction_type="hourly",
                            predicted_emotion=emotion,
                            probability=hour_pattern.confidence,
                            suggested_response=f"이 시간대에 보통 {emotion}를 느끼시는 것 같아요. 괜찮으신가요?",
                            timing=target_time,
                            reasoning=f"과거 {current_hour}시 데이터 기반 예측",
                        )
                    )

        # 요일별 예측
        if "daily" in patterns:
            day_pattern = patterns["daily"]
            current_day = target_time.strftime("%A")

            if current_day in day_pattern.pattern_data:
                intensity = day_pattern.pattern_data[current_day]
                if (
                    intensity > 0.7
                    and day_pattern.confidence > self.prediction_threshold
                ):
                    emotion = (
                        "monday_blues" if current_day == "Monday" else "weekly_stress"
                    )
                    predictions.append(
                        PredictiveInsight(
                            prediction_type="daily",
                            predicted_emotion=emotion,
                            probability=day_pattern.confidence,
                            suggested_response=f"{current_day}에는 평소보다 힘들어하시는 것 같아요. 오늘은 어떠신가요?",
                            timing=target_time,
                            reasoning=f"{current_day} 감정 패턴 기반 예측",
                        )
                    )

        return predictions

    def generate_proactive_support(self) -> Optional[str]:
        """선제적 지원 메시지 생성"""

        predictions = self.predict_emotional_state()

        if predictions:
            # 가장 신뢰도 높은 예측 선택
            best_prediction = max(predictions, key=lambda p: p.probability)

            if best_prediction.probability > self.prediction_threshold:
                return best_prediction.suggested_response

        # 최근 감정 패턴 기반 지원
        if len(self.emotional_moments) >= 3:
            recent_emotions = [m.emotion for m in list(self.emotional_moments)[-3:]]
            negative_emotions = ["sadness", "stress", "anxiety", "frustration", "anger"]

            if all(emotion in negative_emotions for emotion in recent_emotions):
                return "최근 며칠 동안 힘든 시간을 보내고 계시는 것 같아요. 무엇이든 이야기해주세요. 함께 해요! 💙"

        return None

    def get_emotional_insights(self) -> Dict[str, Any]:
        """감정 통찰 정보 생성"""

        if not self.emotional_moments:
            return {
                "message": "아직 충분한 데이터가 없습니다. 더 많은 대화를 나눠주세요!"
            }

        patterns = self.analyze_emotional_patterns()
        recent_emotions = [m.emotion for m in list(self.emotional_moments)[-10:]]

        insights = {
            "total_interactions": len(self.emotional_moments),
            "recent_mood_trend": self._analyze_mood_trend(recent_emotions),
            "discovered_patterns": len(patterns),
            "pattern_summary": {},
            "recommendations": [],
        }

        # 패턴 요약
        for pattern_type, pattern in patterns.items():
            if pattern_type == "hourly":
                peak_hours = [
                    hour
                    for hour, intensity in pattern.pattern_data.items()
                    if intensity > 0.7
                ]
                insights["pattern_summary"]["difficult_hours"] = peak_hours
            elif pattern_type == "daily":
                difficult_days = [
                    day
                    for day, intensity in pattern.pattern_data.items()
                    if intensity > 0.7
                ]
                insights["pattern_summary"]["difficult_days"] = difficult_days
            elif pattern_type == "triggers":
                strong_triggers = [
                    trigger
                    for trigger, intensity in pattern.pattern_data.items()
                    if intensity > 0.8
                ]
                insights["pattern_summary"]["emotional_triggers"] = strong_triggers

        # 추천사항 생성
        if "difficult_hours" in insights["pattern_summary"]:
            insights["recommendations"].append(
                "특정 시간대에 스트레스가 높아지는 패턴이 보여요. 그 시간에는 잠시 휴식을 취해보세요."
            )

        if "emotional_triggers" in insights["pattern_summary"]:
            insights["recommendations"].append(
                "특정 주제나 단어에 민감하게 반응하시는 것 같아요. 이런 패턴을 인식하는 것만으로도 도움이 될 거예요."
            )

        return insights

    def _analyze_mood_trend(self, recent_emotions: List[str]) -> str:
        """최근 기분 트렌드 분석"""

        if not recent_emotions:
            return "neutral"

        positive_emotions = ["joy", "happiness", "excitement", "love", "gratitude"]
        negative_emotions = ["sadness", "stress", "anxiety", "frustration", "anger"]

        positive_count = sum(
            1 for emotion in recent_emotions if emotion in positive_emotions
        )
        negative_count = sum(
            1 for emotion in recent_emotions if emotion in negative_emotions
        )

        if positive_count > negative_count * 1.5:
            return "improving"
        elif negative_count > positive_count * 1.5:
            return "concerning"
        else:
            return "stable"

    def save_memory(self):
        """메모리 저장"""

        os.makedirs(self.data_dir, exist_ok=True)

        memory_data = {
            "user_id": self.user_id,
            "last_updated": datetime.now().isoformat(),
            "emotional_moments": [
                {
                    "timestamp": moment.timestamp.isoformat(),
                    "emotion": moment.emotion,
                    "intensity": moment.intensity,
                    "trigger_words": moment.trigger_words,
                    "context": moment.context,
                    "user_input": moment.user_input,
                    "echo_response": moment.echo_response,
                    "effectiveness_score": moment.effectiveness_score,
                }
                for moment in self.emotional_moments
            ],
            "conversation_effectiveness": self.conversation_effectiveness,
        }

        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 감정 메모리 저장 실패: {e}")

    def load_memory(self):
        """메모리 로드"""

        if not os.path.exists(self.memory_file):
            return

        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                memory_data = json.load(f)

            # 감정 순간들 복원
            for moment_data in memory_data.get("emotional_moments", []):
                moment = EmotionalMoment(
                    timestamp=datetime.fromisoformat(moment_data["timestamp"]),
                    emotion=moment_data["emotion"],
                    intensity=moment_data["intensity"],
                    trigger_words=moment_data["trigger_words"],
                    context=moment_data["context"],
                    user_input=moment_data["user_input"],
                    echo_response=moment_data["echo_response"],
                    effectiveness_score=moment_data.get("effectiveness_score"),
                )
                self.emotional_moments.append(moment)
                self._update_patterns(moment)

            # 대화 효과성 복원
            self.conversation_effectiveness = memory_data.get(
                "conversation_effectiveness", {}
            )

        except Exception as e:
            print(f"⚠️ 감정 메모리 로드 실패: {e}")


# 편의 함수들
def create_emotional_memory(user_id: str = "default") -> EmotionalRhythmMemory:
    """감정 리듬 메모리 생성"""
    return EmotionalRhythmMemory(user_id)


def record_conversation(
    memory: EmotionalRhythmMemory,
    user_input: str,
    detected_emotion: str,
    echo_response: str,
) -> EmotionalMoment:
    """대화 기록 편의 함수"""
    return memory.record_emotional_moment(user_input, detected_emotion, echo_response)


if __name__ == "__main__":
    # 테스트
    memory = EmotionalRhythmMemory("test_user")

    # 테스트 데이터 추가
    test_conversations = [
        ("정말 슬퍼요", "sadness", "마음이 힘드시군요. 무슨 일이 있으셨나요?"),
        (
            "일이 너무 스트레스받아",
            "stress",
            "업무 스트레스가 심하시군요. 잠시 휴식이 필요할 것 같아요.",
        ),
        ("기분이 좋아졌어요!", "joy", "기쁜 마음이 전해져요! 좋은 일이 있으셨나봐요."),
    ]

    for user_input, emotion, response in test_conversations:
        memory.record_emotional_moment(user_input, emotion, response)

    # 분석 결과 출력
    insights = memory.get_emotional_insights()
    print("🌊 감정 리듬 분석 결과:")
    print(json.dumps(insights, ensure_ascii=False, indent=2))

    # 선제적 지원 테스트
    proactive_message = memory.generate_proactive_support()
    if proactive_message:
        print(f"\n💙 선제적 지원 메시지: {proactive_message}")
