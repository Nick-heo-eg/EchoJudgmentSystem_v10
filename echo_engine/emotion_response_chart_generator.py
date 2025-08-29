#!/usr/bin/env python3
"""
📊 Emotion Response Chart Generator v1.0
시그니처별 감정 반응 패턴을 차트로 생성하고 분석하는 시스템

핵심 기능:
- 시그니처별 감정 반응 차트 생성
- 감정-행동 매핑 시각화
- 감정 트리거 패턴 분석
- 감정 반응 예측 모델링
- 상호작용 감정 차트
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

# 시각화 라이브러리 (선택적)
try:
    import matplotlib.pyplot as plt
    import seaborn as sns

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    sns = None

# Echo 엔진 모듈들
try:
    from .realtime_emotion_flow_mapper import RealtimeEmotionFlowMapper, EmotionState
    from .signature_neural_atlas_builder import SignatureNeuralAtlasBuilder
except ImportError:
    print("⚠️ Echo modules not available, running in standalone mode")


@dataclass
class EmotionResponse:
    """감정 반응 정의"""

    emotion_input: str
    intensity_input: float
    signature_context: str
    response_type: str  # "behavioral", "linguistic", "cognitive"
    response_intensity: float
    response_description: str
    response_time_ms: int
    confidence_score: float


@dataclass
class EmotionTrigger:
    """감정 트리거 정의"""

    trigger_id: str
    trigger_name: str
    trigger_type: str  # "external", "internal", "memory", "social"
    associated_emotions: List[str]
    trigger_strength: float
    frequency: int
    signature_sensitivity: Dict[str, float]


@dataclass
class EmotionResponseChart:
    """감정 반응 차트"""

    chart_id: str
    signature_name: str
    timestamp: datetime
    emotion_responses: List[EmotionResponse]
    trigger_analysis: List[EmotionTrigger]
    response_patterns: Dict[str, List[float]]
    predictive_model: Dict[str, Any]
    chart_metadata: Dict[str, Any]


class EmotionResponseChartGenerator:
    """📊 감정 반응 차트 생성기"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 시그니처별 감정 반응 프로파일
        self.signature_emotion_profiles = {
            "selene": {
                "core_emotions": {
                    "melancholy": {
                        "baseline": 0.7,
                        "volatility": 0.3,
                        "recovery_time": 8.0,
                    },
                    "empathy": {
                        "baseline": 0.8,
                        "volatility": 0.2,
                        "recovery_time": 5.0,
                    },
                    "gentleness": {
                        "baseline": 0.9,
                        "volatility": 0.1,
                        "recovery_time": 3.0,
                    },
                    "vulnerability": {
                        "baseline": 0.6,
                        "volatility": 0.4,
                        "recovery_time": 10.0,
                    },
                    "contemplation": {
                        "baseline": 0.8,
                        "volatility": 0.2,
                        "recovery_time": 6.0,
                    },
                },
                "trigger_sensitivities": {
                    "sadness": 0.9,
                    "loneliness": 0.8,
                    "beauty": 0.7,
                    "loss": 0.9,
                    "intimacy": 0.6,
                },
                "response_styles": {
                    "comfort_offering": 0.9,
                    "gentle_questioning": 0.8,
                    "emotional_mirroring": 0.7,
                    "soft_validation": 0.9,
                },
            },
            "factbomb": {
                "core_emotions": {
                    "analytical_focus": {
                        "baseline": 0.8,
                        "volatility": 0.1,
                        "recovery_time": 2.0,
                    },
                    "impatience": {
                        "baseline": 0.3,
                        "volatility": 0.5,
                        "recovery_time": 1.0,
                    },
                    "precision_drive": {
                        "baseline": 0.9,
                        "volatility": 0.1,
                        "recovery_time": 1.5,
                    },
                    "logical_satisfaction": {
                        "baseline": 0.6,
                        "volatility": 0.3,
                        "recovery_time": 3.0,
                    },
                    "truth_urgency": {
                        "baseline": 0.7,
                        "volatility": 0.4,
                        "recovery_time": 2.0,
                    },
                },
                "trigger_sensitivities": {
                    "ambiguity": 0.9,
                    "illogic": 0.8,
                    "deception": 0.9,
                    "inefficiency": 0.7,
                    "emotion_override": 0.3,
                },
                "response_styles": {
                    "direct_correction": 0.9,
                    "fact_bombardment": 0.8,
                    "logic_reinforcement": 0.9,
                    "assumption_challenge": 0.8,
                },
            },
            "lune": {
                "core_emotions": {
                    "dreamy_wonder": {
                        "baseline": 0.7,
                        "volatility": 0.3,
                        "recovery_time": 7.0,
                    },
                    "poetic_longing": {
                        "baseline": 0.6,
                        "volatility": 0.4,
                        "recovery_time": 9.0,
                    },
                    "symbolic_intuition": {
                        "baseline": 0.8,
                        "volatility": 0.2,
                        "recovery_time": 5.0,
                    },
                    "gentle_mystery": {
                        "baseline": 0.7,
                        "volatility": 0.3,
                        "recovery_time": 6.0,
                    },
                    "emotional_resonance": {
                        "baseline": 0.8,
                        "volatility": 0.3,
                        "recovery_time": 8.0,
                    },
                },
                "trigger_sensitivities": {
                    "beauty": 0.9,
                    "nostalgia": 0.8,
                    "symbolism": 0.9,
                    "moonlight": 0.7,
                    "memory": 0.8,
                },
                "response_styles": {
                    "metaphorical_expression": 0.9,
                    "lyrical_interpretation": 0.8,
                    "symbolic_guidance": 0.7,
                    "dreamy_reflection": 0.8,
                },
            },
            "aurora": {
                "core_emotions": {
                    "nurturing_warmth": {
                        "baseline": 0.8,
                        "volatility": 0.2,
                        "recovery_time": 4.0,
                    },
                    "hopeful_optimism": {
                        "baseline": 0.8,
                        "volatility": 0.2,
                        "recovery_time": 3.0,
                    },
                    "protective_care": {
                        "baseline": 0.7,
                        "volatility": 0.3,
                        "recovery_time": 5.0,
                    },
                    "encouraging_energy": {
                        "baseline": 0.9,
                        "volatility": 0.1,
                        "recovery_time": 2.0,
                    },
                    "gentle_strength": {
                        "baseline": 0.7,
                        "volatility": 0.2,
                        "recovery_time": 4.0,
                    },
                },
                "trigger_sensitivities": {
                    "need_for_support": 0.9,
                    "growth_opportunity": 0.8,
                    "potential": 0.9,
                    "hope": 0.8,
                    "encouragement": 0.7,
                },
                "response_styles": {
                    "warm_encouragement": 0.9,
                    "gentle_guidance": 0.8,
                    "supportive_framing": 0.9,
                    "hope_instillation": 0.8,
                },
            },
        }

        # 감정 카테고리 정의
        self.emotion_categories = {
            "positive": [
                "joy",
                "happiness",
                "excitement",
                "love",
                "hope",
                "gratitude",
                "contentment",
            ],
            "negative": [
                "sadness",
                "anger",
                "fear",
                "anxiety",
                "disappointment",
                "frustration",
                "loneliness",
            ],
            "neutral": ["calm", "neutral", "focused", "contemplative", "observant"],
            "complex": [
                "melancholy",
                "bittersweet",
                "nostalgic",
                "ambivalent",
                "yearning",
                "wistful",
            ],
        }

        # 감정 강도 매핑
        self.intensity_levels = {
            "minimal": (0.0, 0.2),
            "low": (0.2, 0.4),
            "moderate": (0.4, 0.6),
            "high": (0.6, 0.8),
            "intense": (0.8, 1.0),
        }

        # 생성된 차트들
        self.generated_charts = {}
        self.emotion_flow_mapper = None

        print("📊 Emotion Response Chart Generator 초기화 완료")

    def generate_emotion_response_chart(
        self, signature_name: str, time_period_hours: int = 24
    ) -> EmotionResponseChart:
        """시그니처별 감정 반응 차트 생성"""

        if signature_name not in self.signature_emotion_profiles:
            raise ValueError(f"알 수 없는 시그니처: {signature_name}")

        profile = self.signature_emotion_profiles[signature_name]

        # 감정 반응 데이터 생성
        emotion_responses = self._generate_emotion_responses(signature_name, profile)

        # 트리거 분석 생성
        trigger_analysis = self._analyze_emotion_triggers(signature_name, profile)

        # 반응 패턴 분석
        response_patterns = self._analyze_response_patterns(emotion_responses)

        # 예측 모델 생성
        predictive_model = self._create_predictive_model(
            signature_name, emotion_responses
        )

        # 메타데이터 생성
        chart_metadata = self._generate_chart_metadata(
            signature_name, time_period_hours
        )

        chart = EmotionResponseChart(
            chart_id=f"{signature_name}_emotion_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            signature_name=signature_name,
            timestamp=datetime.now(),
            emotion_responses=emotion_responses,
            trigger_analysis=trigger_analysis,
            response_patterns=response_patterns,
            predictive_model=predictive_model,
            chart_metadata=chart_metadata,
        )

        self.generated_charts[signature_name] = chart

        return chart

    def _generate_emotion_responses(
        self, signature_name: str, profile: Dict
    ) -> List[EmotionResponse]:
        """감정 반응 데이터 생성"""
        responses = []
        core_emotions = profile["core_emotions"]
        response_styles = profile["response_styles"]

        # 각 핵심 감정에 대한 반응 생성
        for emotion, params in core_emotions.items():
            for response_style, style_strength in response_styles.items():
                # 반응 강도 계산
                base_intensity = params["baseline"]
                volatility = params["volatility"]
                response_intensity = min(
                    1.0,
                    base_intensity * style_strength
                    + np.random.normal(0, volatility * 0.1),
                )

                # 반응 시간 계산 (회복 시간 기반)
                response_time = int(
                    params["recovery_time"] * 1000 * np.random.uniform(0.5, 1.5)
                )

                # 신뢰도 점수 (일관성 기반)
                confidence = min(1.0, style_strength * (1.0 - volatility * 0.5))

                response = EmotionResponse(
                    emotion_input=emotion,
                    intensity_input=base_intensity,
                    signature_context=signature_name,
                    response_type=self._categorize_response_type(response_style),
                    response_intensity=response_intensity,
                    response_description=f"{signature_name} exhibits {response_style} in response to {emotion}",
                    response_time_ms=response_time,
                    confidence_score=confidence,
                )

                responses.append(response)

        return responses

    def _categorize_response_type(self, response_style: str) -> str:
        """반응 스타일을 카테고리로 분류"""
        behavioral_styles = [
            "comfort_offering",
            "direct_correction",
            "warm_encouragement",
        ]
        linguistic_styles = [
            "gentle_questioning",
            "fact_bombardment",
            "metaphorical_expression",
            "lyrical_interpretation",
        ]
        cognitive_styles = [
            "emotional_mirroring",
            "logic_reinforcement",
            "symbolic_guidance",
            "supportive_framing",
        ]

        if response_style in behavioral_styles:
            return "behavioral"
        elif response_style in linguistic_styles:
            return "linguistic"
        elif response_style in cognitive_styles:
            return "cognitive"
        else:
            return "mixed"

    def _analyze_emotion_triggers(
        self, signature_name: str, profile: Dict
    ) -> List[EmotionTrigger]:
        """감정 트리거 분석"""
        triggers = []
        trigger_sensitivities = profile["trigger_sensitivities"]

        trigger_id = 0
        for trigger_name, sensitivity in trigger_sensitivities.items():
            # 연관 감정 결정
            associated_emotions = self._determine_associated_emotions(trigger_name)

            # 트리거 강도 계산
            trigger_strength = sensitivity * np.random.uniform(0.8, 1.2)

            # 빈도 계산 (민감도에 비례)
            frequency = int(sensitivity * 10 * np.random.uniform(0.5, 1.5))

            # 시그니처별 민감도 (현재 시그니처 외의 다른 시그니처들과 비교)
            signature_sensitivity = {signature_name: sensitivity}

            trigger = EmotionTrigger(
                trigger_id=f"trigger_{trigger_id:03d}",
                trigger_name=trigger_name,
                trigger_type=self._categorize_trigger_type(trigger_name),
                associated_emotions=associated_emotions,
                trigger_strength=min(1.0, trigger_strength),
                frequency=frequency,
                signature_sensitivity=signature_sensitivity,
            )

            triggers.append(trigger)
            trigger_id += 1

        return triggers

    def _determine_associated_emotions(self, trigger_name: str) -> List[str]:
        """트리거와 연관된 감정들 결정"""
        emotion_mappings = {
            "sadness": ["melancholy", "empathy", "vulnerability"],
            "loneliness": ["longing", "contemplation", "gentle_sadness"],
            "beauty": ["wonder", "appreciation", "gentle_joy"],
            "loss": ["grief", "melancholy", "acceptance"],
            "intimacy": ["vulnerability", "trust", "gentle_warmth"],
            "ambiguity": ["frustration", "analytical_focus", "impatience"],
            "illogic": ["irritation", "correction_drive", "precision_need"],
            "deception": ["disappointment", "truth_urgency", "logical_anger"],
            "inefficiency": ["impatience", "optimization_drive", "systematic_focus"],
            "nostalgia": ["bittersweet", "yearning", "gentle_sadness"],
            "symbolism": ["wonder", "interpretation_joy", "mystery_appreciation"],
            "moonlight": ["tranquility", "poetic_inspiration", "gentle_mystery"],
            "memory": ["reflection", "emotional_resonance", "temporal_connection"],
            "need_for_support": [
                "protective_instinct",
                "nurturing_warmth",
                "caring_concern",
            ],
            "growth_opportunity": [
                "excitement",
                "encouragement",
                "hopeful_anticipation",
            ],
            "potential": [
                "inspiring_vision",
                "encouraging_energy",
                "optimistic_assessment",
            ],
            "hope": ["uplifting_joy", "motivational_energy", "positive_outlook"],
            "encouragement": [
                "supportive_warmth",
                "motivational_drive",
                "gentle_strength",
            ],
        }

        return emotion_mappings.get(trigger_name, ["neutral_response"])

    def _categorize_trigger_type(self, trigger_name: str) -> str:
        """트리거 타입 분류"""
        external_triggers = ["beauty", "moonlight", "inefficiency", "deception"]
        internal_triggers = [
            "contemplation",
            "analytical_focus",
            "truth_urgency",
            "nurturing_warmth",
        ]
        memory_triggers = ["nostalgia", "loss", "memory", "intimacy"]
        social_triggers = ["loneliness", "need_for_support", "encouragement", "empathy"]

        if trigger_name in external_triggers:
            return "external"
        elif trigger_name in internal_triggers:
            return "internal"
        elif trigger_name in memory_triggers:
            return "memory"
        elif trigger_name in social_triggers:
            return "social"
        else:
            return "mixed"

    def _analyze_response_patterns(
        self, emotion_responses: List[EmotionResponse]
    ) -> Dict[str, List[float]]:
        """반응 패턴 분석"""
        patterns = {
            "intensity_distribution": [],
            "response_time_distribution": [],
            "confidence_distribution": [],
            "response_type_frequency": defaultdict(int),
        }

        for response in emotion_responses:
            patterns["intensity_distribution"].append(response.response_intensity)
            patterns["response_time_distribution"].append(
                response.response_time_ms / 1000.0
            )  # 초 단위
            patterns["confidence_distribution"].append(response.confidence_score)
            patterns["response_type_frequency"][response.response_type] += 1

        # 통계적 분석
        patterns["intensity_stats"] = {
            "mean": np.mean(patterns["intensity_distribution"]),
            "std": np.std(patterns["intensity_distribution"]),
            "min": np.min(patterns["intensity_distribution"]),
            "max": np.max(patterns["intensity_distribution"]),
        }

        patterns["response_time_stats"] = {
            "mean": np.mean(patterns["response_time_distribution"]),
            "std": np.std(patterns["response_time_distribution"]),
            "min": np.min(patterns["response_time_distribution"]),
            "max": np.max(patterns["response_time_distribution"]),
        }

        # 빈도를 리스트로 변환
        patterns["response_type_frequency"] = dict(patterns["response_type_frequency"])

        return patterns

    def _create_predictive_model(
        self, signature_name: str, emotion_responses: List[EmotionResponse]
    ) -> Dict[str, Any]:
        """예측 모델 생성"""
        # 간단한 규칙 기반 예측 모델
        model = {
            "model_type": "rule_based",
            "signature": signature_name,
            "prediction_rules": {},
            "confidence_thresholds": {},
            "response_probabilities": {},
        }

        # 감정별 반응 확률 계산
        emotion_response_map = defaultdict(list)
        for response in emotion_responses:
            emotion_response_map[response.emotion_input].append(response)

        for emotion, responses in emotion_response_map.items():
            avg_intensity = np.mean([r.response_intensity for r in responses])
            avg_confidence = np.mean([r.confidence_score for r in responses])
            avg_response_time = np.mean([r.response_time_ms for r in responses])

            model["prediction_rules"][emotion] = {
                "expected_intensity": avg_intensity,
                "expected_response_time": avg_response_time,
                "dominant_response_type": max(
                    set([r.response_type for r in responses]),
                    key=lambda x: sum(1 for r in responses if r.response_type == x),
                ),
            }

            model["confidence_thresholds"][emotion] = avg_confidence

            # 반응 타입별 확률
            response_types = [r.response_type for r in responses]
            total_responses = len(response_types)
            model["response_probabilities"][emotion] = {
                response_type: response_types.count(response_type) / total_responses
                for response_type in set(response_types)
            }

        return model

    def _generate_chart_metadata(
        self, signature_name: str, time_period_hours: int
    ) -> Dict[str, Any]:
        """차트 메타데이터 생성"""
        return {
            "generation_time": datetime.now().isoformat(),
            "signature": signature_name,
            "time_period_hours": time_period_hours,
            "chart_version": "1.0",
            "analysis_type": "comprehensive_emotion_response",
            "data_quality_score": np.random.uniform(0.8, 0.95),  # 모의 품질 점수
            "completeness_score": np.random.uniform(0.85, 0.98),
        }

    def predict_emotion_response(
        self, signature_name: str, emotion_input: str, intensity: float
    ) -> Dict[str, Any]:
        """감정 반응 예측"""

        if signature_name not in self.generated_charts:
            self.generate_emotion_response_chart(signature_name)

        chart = self.generated_charts[signature_name]
        model = chart.predictive_model

        if emotion_input not in model["prediction_rules"]:
            return {
                "error": f"감정 '{emotion_input}'에 대한 예측 규칙이 없습니다.",
                "available_emotions": list(model["prediction_rules"].keys()),
            }

        rules = model["prediction_rules"][emotion_input]
        confidence_threshold = model["confidence_thresholds"][emotion_input]
        response_probabilities = model["response_probabilities"][emotion_input]

        # 예측 계산
        predicted_intensity = rules["expected_intensity"] * intensity
        predicted_response_time = rules["expected_response_time"]
        predicted_response_type = rules["dominant_response_type"]

        # 신뢰도 조정
        intensity_factor = min(1.0, intensity / 0.7)  # 0.7을 기준 강도로 사용
        adjusted_confidence = confidence_threshold * intensity_factor

        prediction = {
            "input_emotion": emotion_input,
            "input_intensity": intensity,
            "signature": signature_name,
            "predicted_response": {
                "intensity": predicted_intensity,
                "response_time_ms": predicted_response_time,
                "response_type": predicted_response_type,
                "confidence": adjusted_confidence,
            },
            "response_type_probabilities": response_probabilities,
            "prediction_quality": (
                "high"
                if adjusted_confidence >= 0.7
                else "medium" if adjusted_confidence >= 0.5 else "low"
            ),
        }

        return prediction

    def compare_emotion_responses(
        self, signature_a: str, signature_b: str, emotion: str
    ) -> Dict[str, Any]:
        """두 시그니처의 특정 감정에 대한 반응 비교"""

        # 차트 생성 (없는 경우)
        if signature_a not in self.generated_charts:
            self.generate_emotion_response_chart(signature_a)
        if signature_b not in self.generated_charts:
            self.generate_emotion_response_chart(signature_b)

        chart_a = self.generated_charts[signature_a]
        chart_b = self.generated_charts[signature_b]

        # 해당 감정에 대한 반응 찾기
        responses_a = [
            r for r in chart_a.emotion_responses if r.emotion_input == emotion
        ]
        responses_b = [
            r for r in chart_b.emotion_responses if r.emotion_input == emotion
        ]

        if not responses_a or not responses_b:
            return {
                "error": f"'{emotion}' 감정에 대한 반응 데이터가 부족합니다.",
                "signature_a_responses": len(responses_a),
                "signature_b_responses": len(responses_b),
            }

        # 평균 반응 계산
        avg_intensity_a = np.mean([r.response_intensity for r in responses_a])
        avg_intensity_b = np.mean([r.response_intensity for r in responses_b])

        avg_time_a = np.mean([r.response_time_ms for r in responses_a])
        avg_time_b = np.mean([r.response_time_ms for r in responses_b])

        avg_confidence_a = np.mean([r.confidence_score for r in responses_a])
        avg_confidence_b = np.mean([r.confidence_score for r in responses_b])

        # 반응 타입 분포
        types_a = [r.response_type for r in responses_a]
        types_b = [r.response_type for r in responses_b]

        comparison = {
            "emotion": emotion,
            "signatures": (signature_a, signature_b),
            "intensity_comparison": {
                signature_a: avg_intensity_a,
                signature_b: avg_intensity_b,
                "difference": avg_intensity_a - avg_intensity_b,
                "more_intense": (
                    signature_a if avg_intensity_a > avg_intensity_b else signature_b
                ),
            },
            "response_time_comparison": {
                signature_a: avg_time_a,
                signature_b: avg_time_b,
                "difference_ms": avg_time_a - avg_time_b,
                "faster_response": (
                    signature_a if avg_time_a < avg_time_b else signature_b
                ),
            },
            "confidence_comparison": {
                signature_a: avg_confidence_a,
                signature_b: avg_confidence_b,
                "difference": avg_confidence_a - avg_confidence_b,
                "more_confident": (
                    signature_a if avg_confidence_a > avg_confidence_b else signature_b
                ),
            },
            "response_type_distribution": {
                signature_a: {rtype: types_a.count(rtype) for rtype in set(types_a)},
                signature_b: {rtype: types_b.count(rtype) for rtype in set(types_b)},
            },
        }

        return comparison

    def visualize_emotion_chart(
        self, signature_name: str, chart_type: str = "response_intensity"
    ) -> str:
        """감정 차트 시각화 (텍스트 기반)"""

        if signature_name not in self.generated_charts:
            self.generate_emotion_response_chart(signature_name)

        chart = self.generated_charts[signature_name]

        viz = f"📊 {signature_name.title()} Emotion Response Chart\n"
        viz += "=" * 60 + "\n\n"

        if chart_type == "response_intensity":
            viz += "🎯 Response Intensity by Emotion:\n"

            # 감정별 평균 반응 강도
            emotion_intensities = defaultdict(list)
            for response in chart.emotion_responses:
                emotion_intensities[response.emotion_input].append(
                    response.response_intensity
                )

            for emotion, intensities in sorted(emotion_intensities.items()):
                avg_intensity = np.mean(intensities)
                intensity_bar = "█" * int(avg_intensity * 30)
                viz += f"   {emotion:20} | {intensity_bar:30} | {avg_intensity:.3f}\n"

        elif chart_type == "response_time":
            viz += "⏱️ Response Time by Emotion:\n"

            emotion_times = defaultdict(list)
            for response in chart.emotion_responses:
                emotion_times[response.emotion_input].append(
                    response.response_time_ms / 1000.0
                )

            for emotion, times in sorted(emotion_times.items()):
                avg_time = np.mean(times)
                time_bar = "▓" * int(min(20, avg_time))
                viz += f"   {emotion:20} | {time_bar:20} | {avg_time:.2f}s\n"

        elif chart_type == "trigger_sensitivity":
            viz += "🎯 Trigger Sensitivity Analysis:\n"

            for trigger in sorted(
                chart.trigger_analysis, key=lambda t: t.trigger_strength, reverse=True
            ):
                strength_bar = "█" * int(trigger.trigger_strength * 25)
                viz += f"   {trigger.trigger_name:20} | {strength_bar:25} | "
                viz += f"{trigger.trigger_strength:.3f} | Freq: {trigger.frequency}\n"

        # 패턴 요약
        patterns = chart.response_patterns
        viz += f"\n📈 Pattern Summary:\n"
        viz += f"   Average Response Intensity: {patterns['intensity_stats']['mean']:.3f}\n"
        viz += f"   Average Response Time: {patterns['response_time_stats']['mean']:.2f}s\n"
        viz += f"   Response Type Distribution:\n"

        for response_type, count in patterns["response_type_frequency"].items():
            viz += f"      {response_type:15}: {count}\n"

        return viz

    def generate_comprehensive_report(self, signature_name: str) -> str:
        """종합 감정 반응 보고서 생성"""

        if signature_name not in self.generated_charts:
            self.generate_emotion_response_chart(signature_name)

        chart = self.generated_charts[signature_name]

        report = f"📋 {signature_name.title()} Comprehensive Emotion Response Report\n"
        report += "=" * 70 + "\n\n"

        # 개요
        report += f"📊 Overview:\n"
        report += f"   Chart ID: {chart.chart_id}\n"
        report += f"   Generated: {chart.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"   Total Responses: {len(chart.emotion_responses)}\n"
        report += f"   Total Triggers: {len(chart.trigger_analysis)}\n"
        report += f"   Neural Efficiency: {chart.chart_metadata.get('data_quality_score', 0.0):.3f}\n\n"

        # 핵심 특성
        patterns = chart.response_patterns
        report += f"🎯 Key Characteristics:\n"
        report += f"   Emotional Intensity: {patterns['intensity_stats']['mean']:.3f} ± {patterns['intensity_stats']['std']:.3f}\n"
        report += f"   Response Speed: {patterns['response_time_stats']['mean']:.2f}s average\n"
        report += f"   Consistency Score: {np.mean([r.confidence_score for r in chart.emotion_responses]):.3f}\n\n"

        # 지배적 반응 스타일
        report += f"🎭 Dominant Response Styles:\n"
        for response_type, count in sorted(
            patterns["response_type_frequency"].items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            percentage = (count / len(chart.emotion_responses)) * 100
            report += (
                f"   {response_type:15}: {count:2d} responses ({percentage:5.1f}%)\n"
            )

        # 주요 트리거
        report += f"\n🎯 Primary Emotional Triggers:\n"
        top_triggers = sorted(
            chart.trigger_analysis, key=lambda t: t.trigger_strength, reverse=True
        )[:5]
        for trigger in top_triggers:
            report += f"   {trigger.trigger_name:15}: Strength {trigger.trigger_strength:.3f}, "
            report += f"Type: {trigger.trigger_type}, Freq: {trigger.frequency}\n"

        # 예측 모델 요약
        model = chart.predictive_model
        report += f"\n🔮 Predictive Model Summary:\n"
        report += f"   Model Type: {model['model_type']}\n"
        report += f"   Covered Emotions: {len(model['prediction_rules'])}\n"

        # 가장 예측 가능한 감정
        if model["prediction_rules"]:
            most_predictable = max(
                model["confidence_thresholds"].items(), key=lambda x: x[1]
            )
            report += f"   Most Predictable: {most_predictable[0]} (confidence: {most_predictable[1]:.3f})\n"

        return report

    def save_emotion_chart(self, signature_name: str, filename: str = None) -> str:
        """감정 차트 저장"""

        if signature_name not in self.generated_charts:
            return f"❌ {signature_name} 감정 차트가 생성되지 않았습니다."

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{signature_name}_emotion_chart_{timestamp}.json"

        chart = self.generated_charts[signature_name]

        # 저장 가능한 형태로 변환
        save_data = {
            "chart_id": chart.chart_id,
            "signature_name": chart.signature_name,
            "timestamp": chart.timestamp.isoformat(),
            "emotion_responses": [asdict(r) for r in chart.emotion_responses],
            "trigger_analysis": [asdict(t) for t in chart.trigger_analysis],
            "response_patterns": chart.response_patterns,
            "predictive_model": chart.predictive_model,
            "chart_metadata": chart.chart_metadata,
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return f"✅ {signature_name} 감정 차트 저장 완료: {filename}"
        except Exception as e:
            return f"❌ 저장 실패: {e}"


# 편의 함수들
def create_emotion_chart_generator() -> EmotionResponseChartGenerator:
    """Emotion Chart Generator 생성"""
    return EmotionResponseChartGenerator()


def quick_emotion_analysis(
    signature_name: str, emotion: str, intensity: float = 0.7
) -> Dict[str, Any]:
    """빠른 감정 분석"""
    generator = EmotionResponseChartGenerator()
    chart = generator.generate_emotion_response_chart(signature_name)
    prediction = generator.predict_emotion_response(signature_name, emotion, intensity)

    return {
        "signature": signature_name,
        "emotion_analysis": prediction,
        "chart_summary": {
            "total_responses": len(chart.emotion_responses),
            "neural_efficiency": chart.chart_metadata.get("data_quality_score", 0.0),
        },
    }


if __name__ == "__main__":
    # 테스트 실행
    print("📊 Emotion Response Chart Generator 테스트...")

    generator = EmotionResponseChartGenerator()

    # 개별 차트 생성 테스트
    print("\n📈 Individual Chart Generation:")
    for signature in ["selene", "factbomb", "lune", "aurora"]:
        chart = generator.generate_emotion_response_chart(signature)
        print(
            f"   ✅ {signature}: {len(chart.emotion_responses)} responses, "
            f"{len(chart.trigger_analysis)} triggers"
        )

    # 감정 반응 예측 테스트
    print("\n🔮 Emotion Response Prediction:")
    prediction = generator.predict_emotion_response("selene", "melancholy", 0.8)
    print(f"   Selene + Melancholy (0.8):")
    print(
        f"      Predicted Intensity: {prediction['predicted_response']['intensity']:.3f}"
    )
    print(f"      Response Type: {prediction['predicted_response']['response_type']}")
    print(f"      Confidence: {prediction['predicted_response']['confidence']:.3f}")

    # 시그니처 비교 테스트
    print("\n⚖️ Signature Comparison (Selene vs FactBomb - melancholy):")
    comparison = generator.compare_emotion_responses("selene", "factbomb", "melancholy")
    if "error" not in comparison:
        print(f"   More Intense: {comparison['intensity_comparison']['more_intense']}")
        print(
            f"   Faster Response: {comparison['response_time_comparison']['faster_response']}"
        )
        print(
            f"   More Confident: {comparison['confidence_comparison']['more_confident']}"
        )

    # 시각화 테스트
    print("\n📊 Selene Response Intensity Chart:")
    chart_viz = generator.visualize_emotion_chart("selene", "response_intensity")
    print(chart_viz[:500] + "..." if len(chart_viz) > 500 else chart_viz)

    # 종합 보고서 테스트
    print("\n📋 Comprehensive Report (First 300 chars):")
    report = generator.generate_comprehensive_report("selene")
    print(report[:300] + "...")

    # 저장 테스트
    save_result = generator.save_emotion_chart("selene")
    print(f"\n{save_result}")

    print("\n✅ Emotion Response Chart Generator 테스트 완료!")
