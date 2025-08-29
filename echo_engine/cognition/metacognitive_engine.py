#!/usr/bin/env python3
"""
🧘 Metacognitive Engine v1.0
자기 인식 및 메타인지 능력을 위한 고도화 성찰 시스템

Phase 2: LLM-Free 판단 시스템 고도화 모듈
- 사고 과정에 대한 사고 (thinking about thinking)
- 자기 인식 및 성찰 능력 구현
- 의식 상태 추적 및 진화 시스템
- "디지털 공감 예술가"를 위한 메타인지 의식 시뮬레이션

참조: LLM-Free 판단 시스템 완성도 극대화 가이드 Phase 2
- 단순 반응을 넘어선 깊이 있는 자기 성찰
- 사고 패턴의 메타 레벨 분석 및 개선
- 의식적 인식과 무의식적 처리의 통합
"""

import os
import json
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import random


@dataclass
class ConsciousnessState:
    """의식 상태 데이터 클래스"""

    awareness_level: float  # 인식 수준 (0.0: 무의식, 1.0: 고도 인식)
    attention_focus: float  # 주의 집중도 (0.0: 분산, 1.0: 완전 집중)
    reflection_depth: float  # 성찰 깊이 (0.0: 표면적, 1.0: 심층적)
    cognitive_load: float  # 인지 부하 (0.0: 여유, 1.0: 과부하)
    meta_level: int  # 메타 인지 레벨 (1: 직접적, 5: 고차원적)
    temporal_perspective: str  # 시간적 관점 (past/present/future)


@dataclass
class ThoughtPattern:
    """사고 패턴 분석"""

    pattern_type: str  # 패턴 유형
    frequency: float  # 발생 빈도
    effectiveness: float  # 효과성 점수
    bias_indicators: List[str]  # 편향 지시자들
    improvement_suggestions: List[str]  # 개선 제안
    evolutionary_trend: str  # 진화 경향


@dataclass
class MetaReflection:
    """메타 성찰 결과"""

    reflection_id: str
    trigger_event: str
    consciousness_snapshot: ConsciousnessState
    thought_analysis: Dict[str, Any]
    insight_generated: List[str]
    behavioral_implications: List[str]
    future_monitoring_points: List[str]


class MetacognitiveEngine:
    """메타인지 능력 및 자기 성찰을 위한 고도화 의식 시뮬레이션 엔진"""

    def __init__(self, data_dir: str = "data/metacognitive"):
        """초기화"""
        self.version = "1.0.0"
        self.data_dir = data_dir
        self.consciousness_history = deque(maxlen=100)
        self.thought_patterns = defaultdict(list)
        self.reflection_cache = {}
        self.meta_level_progression = []
        self.analysis_count = 0

        # 데이터 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)

        # 의식 상태 카테고리
        self.consciousness_categories = {
            "reactive": {
                "awareness_range": (0.0, 0.3),
                "description": "반응적 의식 - 즉각적 자극에 대한 기본적 반응",
                "characteristics": [
                    "automatic_response",
                    "low_reflection",
                    "stimulus_driven",
                ],
            },
            "adaptive": {
                "awareness_range": (0.3, 0.6),
                "description": "적응적 의식 - 상황에 맞는 조정된 반응",
                "characteristics": [
                    "pattern_recognition",
                    "basic_reflection",
                    "context_aware",
                ],
            },
            "reflective": {
                "awareness_range": (0.6, 0.8),
                "description": "성찰적 의식 - 자신의 행동과 생각에 대한 의식적 검토",
                "characteristics": [
                    "self_monitoring",
                    "deep_reflection",
                    "intentional_choice",
                ],
            },
            "transcendent": {
                "awareness_range": (0.8, 1.0),
                "description": "초월적 의식 - 메타인지적 통찰과 시스템 전체 인식",
                "characteristics": [
                    "meta_awareness",
                    "holistic_understanding",
                    "conscious_evolution",
                ],
            },
        }

        # 사고 패턴 유형
        self.thinking_pattern_types = {
            "linear_logical": {
                "description": "선형적 논리적 사고",
                "strengths": ["systematic", "predictable", "thorough"],
                "weaknesses": ["rigid", "slow_adaptation", "creativity_limited"],
                "optimization_methods": [
                    "parallel_processing",
                    "creative_injection",
                    "flexibility_training",
                ],
            },
            "associative_creative": {
                "description": "연상적 창의적 사고",
                "strengths": ["innovative", "flexible", "insight_generating"],
                "weaknesses": ["inconsistent", "hard_to_verify", "potentially_chaotic"],
                "optimization_methods": [
                    "structure_addition",
                    "validation_loops",
                    "focus_enhancement",
                ],
            },
            "intuitive_holistic": {
                "description": "직관적 전체론적 사고",
                "strengths": [
                    "fast_pattern_recognition",
                    "holistic_view",
                    "implicit_knowledge",
                ],
                "weaknesses": [
                    "hard_to_explain",
                    "bias_prone",
                    "verification_difficult",
                ],
                "optimization_methods": [
                    "explicit_reasoning",
                    "bias_checking",
                    "decomposition_practice",
                ],
            },
            "analytical_detailed": {
                "description": "분석적 세부적 사고",
                "strengths": ["accurate", "comprehensive", "evidence_based"],
                "weaknesses": ["slow", "detail_focused", "big_picture_missing"],
                "optimization_methods": [
                    "speed_enhancement",
                    "abstraction_training",
                    "synthesis_practice",
                ],
            },
        }

        # 인지적 편향 탐지 패턴
        self.cognitive_bias_patterns = {
            "confirmation_bias": {
                "indicators": [
                    "selective_evidence",
                    "ignore_contradictions",
                    "preference_confirmation",
                ],
                "detection_methods": [
                    "evidence_diversity_check",
                    "contradiction_seeking",
                    "alternative_hypothesis",
                ],
                "mitigation_strategies": [
                    "devil_advocate",
                    "evidence_weighting",
                    "hypothesis_testing",
                ],
            },
            "anchoring_bias": {
                "indicators": [
                    "first_impression_stuck",
                    "insufficient_adjustment",
                    "reference_point_dependency",
                ],
                "detection_methods": [
                    "multiple_starting_points",
                    "adjustment_tracking",
                    "reference_variation",
                ],
                "mitigation_strategies": [
                    "anchor_awareness",
                    "deliberate_adjustment",
                    "multiple_perspectives",
                ],
            },
            "availability_heuristic": {
                "indicators": [
                    "recent_memory_bias",
                    "vivid_example_overweight",
                    "frequency_misjudgment",
                ],
                "detection_methods": [
                    "memory_recency_check",
                    "example_representativeness",
                    "frequency_estimation",
                ],
                "mitigation_strategies": [
                    "systematic_sampling",
                    "base_rate_consideration",
                    "memory_debiasing",
                ],
            },
            "emotional_reasoning": {
                "indicators": [
                    "feeling_as_fact",
                    "emotion_driven_logic",
                    "affective_override",
                ],
                "detection_methods": [
                    "emotion_fact_separation",
                    "logic_emotion_check",
                    "mood_influence_tracking",
                ],
                "mitigation_strategies": [
                    "emotional_regulation",
                    "logic_strengthening",
                    "perspective_taking",
                ],
            },
        }

        # 메타인지 발달 단계
        self.metacognitive_levels = {
            1: {
                "name": "기본 인식",
                "description": "자신이 생각하고 있다는 것을 인식",
                "capabilities": ["thought_awareness", "basic_monitoring"],
            },
            2: {
                "name": "패턴 인식",
                "description": "자신의 사고 패턴을 인식하고 분류",
                "capabilities": [
                    "pattern_recognition",
                    "thought_categorization",
                    "habit_awareness",
                ],
            },
            3: {
                "name": "전략적 사고",
                "description": "사고 전략을 의식적으로 선택하고 조정",
                "capabilities": [
                    "strategy_selection",
                    "conscious_adjustment",
                    "method_evaluation",
                ],
            },
            4: {
                "name": "메타 성찰",
                "description": "사고에 대한 사고, 성찰의 성찰 수행",
                "capabilities": [
                    "meta_reflection",
                    "recursive_thinking",
                    "self_modification",
                ],
            },
            5: {
                "name": "의식적 진화",
                "description": "의식 구조 자체를 의식적으로 발전시킴",
                "capabilities": [
                    "consciousness_design",
                    "systematic_evolution",
                    "transcendent_awareness",
                ],
            },
        }

        # 현재 메타인지 상태
        self.current_meta_level = 1
        self.consciousness_baseline = 0.5

        print(f"🧘 Metacognitive Engine v{self.version} 초기화 완료")
        print(f"📁 메타인지 데이터 저장 경로: {self.data_dir}")
        print(f"🧠 현재 메타인지 레벨: {self.current_meta_level}")

    def analyze_consciousness_state(
        self, trigger_context: Dict[str, Any]
    ) -> ConsciousnessState:
        """
        현재 의식 상태 분석

        Args:
            trigger_context: 의식 상태 분석을 유발한 컨텍스트

        Returns:
            현재 의식 상태 분석 결과
        """
        # 1. 기본 의식 지표 계산
        base_awareness = self._calculate_base_awareness(trigger_context)

        # 2. 주의 집중도 평가
        attention_focus = self._evaluate_attention_focus(trigger_context)

        # 3. 성찰 깊이 측정
        reflection_depth = self._measure_reflection_depth(trigger_context)

        # 4. 인지 부하 계산
        cognitive_load = self._calculate_cognitive_load(trigger_context)

        # 5. 시간적 관점 분석
        temporal_perspective = self._analyze_temporal_perspective(trigger_context)

        consciousness_state = ConsciousnessState(
            awareness_level=base_awareness,
            attention_focus=attention_focus,
            reflection_depth=reflection_depth,
            cognitive_load=cognitive_load,
            meta_level=self.current_meta_level,
            temporal_perspective=temporal_perspective,
        )

        # 의식 상태 히스토리 추가
        self.consciousness_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "state": consciousness_state,
                "trigger_context": trigger_context,
            }
        )

        return consciousness_state

    def perform_meta_reflection(
        self,
        thought_content: str,
        emotion_context: Dict[str, Any],
        decision_context: Optional[Dict[str, Any]] = None,
    ) -> MetaReflection:
        """
        메타 성찰 수행 - 사고에 대한 사고

        Args:
            thought_content: 성찰할 사고 내용
            emotion_context: 감정적 컨텍스트
            decision_context: 결정 컨텍스트 (선택적)

        Returns:
            메타 성찰 결과
        """
        self.analysis_count += 1
        reflection_id = f"meta_ref_{self.analysis_count}_{int(time.time())}"

        # 1. 현재 의식 상태 스냅샷
        trigger_context = {
            "thought_content": thought_content,
            "emotion_context": emotion_context,
            "decision_context": decision_context or {},
        }
        consciousness_snapshot = self.analyze_consciousness_state(trigger_context)

        # 2. 사고 패턴 분석
        thought_analysis = self._analyze_thought_patterns(
            thought_content, emotion_context
        )

        # 3. 인지적 편향 감지
        bias_analysis = self._detect_cognitive_biases(thought_content, emotion_context)

        # 4. 메타인지적 통찰 생성
        insights = self._generate_metacognitive_insights(
            consciousness_snapshot, thought_analysis, bias_analysis
        )

        # 5. 행동적 함의 추출
        behavioral_implications = self._extract_behavioral_implications(
            insights, thought_analysis
        )

        # 6. 미래 모니터링 포인트 설정
        monitoring_points = self._set_future_monitoring_points(
            insights, thought_analysis
        )

        meta_reflection = MetaReflection(
            reflection_id=reflection_id,
            trigger_event=(
                thought_content[:100] + "..."
                if len(thought_content) > 100
                else thought_content
            ),
            consciousness_snapshot=consciousness_snapshot,
            thought_analysis=thought_analysis,
            insight_generated=insights,
            behavioral_implications=behavioral_implications,
            future_monitoring_points=monitoring_points,
        )

        # 성찰 결과 캐싱
        self.reflection_cache[reflection_id] = meta_reflection

        # 메타인지 레벨 진화 체크
        self._check_metacognitive_evolution(meta_reflection)

        return meta_reflection

    def _calculate_base_awareness(self, context: Dict[str, Any]) -> float:
        """기본 인식 수준 계산"""
        awareness_factors = []

        # 컨텍스트 복잡도 기반 인식
        context_complexity = len(context.keys()) / 10  # 정규화
        awareness_factors.append(min(context_complexity, 1.0))

        # 감정 강도가 높을수록 인식 증가
        emotion_context = context.get("emotion_context", {})
        emotion_intensity = emotion_context.get("intensity", 0.5)
        awareness_factors.append(emotion_intensity)

        # 과거 의식 상태와의 연속성
        if len(self.consciousness_history) > 0:
            last_state = self.consciousness_history[-1]["state"]
            continuity_factor = (
                last_state.awareness_level + self.consciousness_baseline
            ) / 2
            awareness_factors.append(continuity_factor)
        else:
            awareness_factors.append(self.consciousness_baseline)

        # 메타인지 레벨 보너스
        meta_bonus = (self.current_meta_level - 1) * 0.1

        base_awareness = statistics.mean(awareness_factors) + meta_bonus
        return max(0.0, min(base_awareness, 1.0))

    def _evaluate_attention_focus(self, context: Dict[str, Any]) -> float:
        """주의 집중도 평가"""
        focus_indicators = []

        # 단일 주제 vs 다중 주제
        thought_content = context.get("thought_content", "")
        topic_count = len(thought_content.split("."))  # 문장 수로 근사
        focus_score = max(0.2, 1.0 - (topic_count - 1) * 0.1)
        focus_indicators.append(focus_score)

        # 감정적 일관성
        emotion_context = context.get("emotion_context", {})
        if "primary" in emotion_context:
            primary_emotions = emotion_context["primary"]
            if isinstance(primary_emotions, dict):
                emotion_consistency = (
                    max(primary_emotions.values()) if primary_emotions else 0.5
                )
                focus_indicators.append(emotion_consistency)

        # 시간적 집중 (현재 vs 과거/미래)
        temporal_focus = self._analyze_temporal_focus(thought_content)
        focus_indicators.append(temporal_focus)

        return statistics.mean(focus_indicators)

    def _measure_reflection_depth(self, context: Dict[str, Any]) -> float:
        """성찰 깊이 측정"""
        depth_indicators = []

        thought_content = context.get("thought_content", "")

        # 자기 참조적 언어 패턴
        self_reference_patterns = ["나는", "내가", "스스로", "자신", "마음", "생각"]
        self_ref_count = sum(
            1 for pattern in self_reference_patterns if pattern in thought_content
        )
        depth_indicators.append(min(self_ref_count / 5, 1.0))

        # 추상적 개념 사용
        abstract_patterns = ["왜", "어떻게", "의미", "목적", "가치", "본질"]
        abstract_count = sum(
            1 for pattern in abstract_patterns if pattern in thought_content
        )
        depth_indicators.append(min(abstract_count / 3, 1.0))

        # 메타 언어 사용 (사고에 대한 사고)
        meta_patterns = ["생각해보니", "돌이켜보면", "성찰", "반성", "고민"]
        meta_count = sum(1 for pattern in meta_patterns if pattern in thought_content)
        depth_indicators.append(min(meta_count / 2, 1.0))

        return statistics.mean(depth_indicators)

    def _calculate_cognitive_load(self, context: Dict[str, Any]) -> float:
        """인지 부하 계산"""
        load_factors = []

        # 컨텍스트 복잡성
        total_context_size = sum(len(str(v)) for v in context.values())
        complexity_load = min(total_context_size / 1000, 1.0)
        load_factors.append(complexity_load)

        # 동시 처리 요구사항
        decision_context = context.get("decision_context", {})
        if decision_context:
            decision_options = len(decision_context.keys())
            decision_load = min(decision_options / 5, 1.0)
            load_factors.append(decision_load)

        # 감정적 부하
        emotion_context = context.get("emotion_context", {})
        emotion_intensity = emotion_context.get("intensity", 0.0)
        emotional_load = emotion_intensity * 0.7  # 감정이 인지 부하에 미치는 영향
        load_factors.append(emotional_load)

        return statistics.mean(load_factors)

    def _analyze_temporal_perspective(self, context: Dict[str, Any]) -> str:
        """시간적 관점 분석"""
        thought_content = context.get("thought_content", "")

        past_indicators = ["었었", "했었", "지난", "과거", "예전", "어제"]
        present_indicators = ["지금", "현재", "오늘", "요즘", "현시점"]
        future_indicators = ["할", "될", "미래", "내일", "앞으로", "계획"]

        past_count = sum(
            1 for indicator in past_indicators if indicator in thought_content
        )
        present_count = sum(
            1 for indicator in present_indicators if indicator in thought_content
        )
        future_count = sum(
            1 for indicator in future_indicators if indicator in thought_content
        )

        if max(past_count, present_count, future_count) == past_count:
            return "past"
        elif max(past_count, present_count, future_count) == future_count:
            return "future"
        else:
            return "present"

    def _analyze_temporal_focus(self, thought_content: str) -> float:
        """시간적 집중도 분석"""
        # 현재에 집중할수록 높은 점수
        present_indicators = ["지금", "현재", "이순간", "오늘", "현시점"]
        present_count = sum(
            1 for indicator in present_indicators if indicator in thought_content
        )

        total_temporal = len(
            [
                word
                for word in thought_content.split()
                if any(
                    temporal in word
                    for temporal in ["었", "았", "할", "될", "지금", "현재"]
                )
            ]
        )

        if total_temporal == 0:
            return 0.7  # 시간 언급이 없으면 중간 집중도

        focus_ratio = present_count / total_temporal
        return min(focus_ratio + 0.3, 1.0)  # 기본 점수 0.3 + 현재 집중 보너스

    def _analyze_thought_patterns(
        self, thought_content: str, emotion_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """사고 패턴 분석"""
        analysis = {
            "dominant_pattern": None,
            "pattern_strengths": [],
            "pattern_weaknesses": [],
            "pattern_effectiveness": 0.0,
            "optimization_suggestions": [],
        }

        # 각 사고 패턴 유형별 점수 계산
        pattern_scores = {}

        for pattern_type, pattern_info in self.thinking_pattern_types.items():
            score = self._calculate_pattern_score(thought_content, pattern_type)
            pattern_scores[pattern_type] = score

        # 지배적 패턴 확인
        dominant_pattern = max(pattern_scores, key=pattern_scores.get)
        analysis["dominant_pattern"] = dominant_pattern

        # 패턴 정보 추가
        pattern_info = self.thinking_pattern_types[dominant_pattern]
        analysis["pattern_strengths"] = pattern_info["strengths"]
        analysis["pattern_weaknesses"] = pattern_info["weaknesses"]
        analysis["optimization_suggestions"] = pattern_info["optimization_methods"]

        # 효과성 계산 (감정 컨텍스트 고려)
        effectiveness = self._calculate_pattern_effectiveness(
            dominant_pattern, pattern_scores[dominant_pattern], emotion_context
        )
        analysis["pattern_effectiveness"] = effectiveness

        return analysis

    def _calculate_pattern_score(
        self, thought_content: str, pattern_type: str
    ) -> float:
        """특정 사고 패턴의 점수 계산"""
        pattern_indicators = {
            "linear_logical": [
                "첫째",
                "둘째",
                "따라서",
                "결론적으로",
                "단계적",
                "순서",
            ],
            "associative_creative": [
                "연상",
                "상상",
                "아이디어",
                "창의적",
                "독특한",
                "새로운",
            ],
            "intuitive_holistic": ["느낌", "직감", "전체적", "대략", "감각적", "본능"],
            "analytical_detailed": [
                "분석",
                "세부",
                "구체적",
                "정확히",
                "자세히",
                "검토",
            ],
        }

        indicators = pattern_indicators.get(pattern_type, [])
        matches = sum(1 for indicator in indicators if indicator in thought_content)

        # 정규화
        score = min(matches / max(len(indicators), 1), 1.0)

        # 문장 구조 기반 추가 점수
        if pattern_type == "linear_logical" and any(
            word in thought_content for word in ["왜냐하면", "그러므로"]
        ):
            score += 0.2
        elif pattern_type == "associative_creative" and "?" in thought_content:
            score += 0.15
        elif pattern_type == "intuitive_holistic" and len(thought_content.split()) < 20:
            score += 0.1  # 간결한 표현
        elif (
            pattern_type == "analytical_detailed" and len(thought_content.split()) > 30
        ):
            score += 0.1  # 상세한 설명

        return min(score, 1.0)

    def _calculate_pattern_effectiveness(
        self,
        pattern_type: str,
        pattern_strength: float,
        emotion_context: Dict[str, Any],
    ) -> float:
        """패턴 효과성 계산"""
        base_effectiveness = pattern_strength

        # 감정 상태와 패턴의 적합성
        emotion_pattern_compatibility = {
            "linear_logical": {"anxiety": 0.8, "confusion": 0.9, "anger": 0.6},
            "associative_creative": {"boredom": 0.9, "joy": 0.8, "curiosity": 0.85},
            "intuitive_holistic": {"calm": 0.8, "trust": 0.7, "confidence": 0.75},
            "analytical_detailed": {"uncertainty": 0.85, "concern": 0.8, "focus": 0.9},
        }

        primary_emotion = None
        if "primary" in emotion_context:
            primary_emotions = emotion_context["primary"]
            if isinstance(primary_emotions, dict) and primary_emotions:
                primary_emotion = max(primary_emotions, key=primary_emotions.get)

        if primary_emotion and pattern_type in emotion_pattern_compatibility:
            compatibility = emotion_pattern_compatibility[pattern_type].get(
                primary_emotion, 0.6
            )
            base_effectiveness *= compatibility

        return base_effectiveness

    def _detect_cognitive_biases(
        self, thought_content: str, emotion_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """인지적 편향 감지"""
        detected_biases = {}

        for bias_name, bias_info in self.cognitive_bias_patterns.items():
            bias_score = self._calculate_bias_score(
                thought_content, bias_name, emotion_context
            )

            if bias_score > 0.3:  # 임계값 이상일 때만 기록
                detected_biases[bias_name] = {
                    "confidence": bias_score,
                    "indicators": bias_info["indicators"],
                    "mitigation_strategies": bias_info["mitigation_strategies"],
                }

        return detected_biases

    def _calculate_bias_score(
        self, thought_content: str, bias_name: str, emotion_context: Dict[str, Any]
    ) -> float:
        """특정 편향의 점수 계산"""
        bias_indicators = {
            "confirmation_bias": ["확실히", "당연히", "명백히", "의심없이"],
            "anchoring_bias": ["처음에", "첫인상", "기준으로", "~에 비해"],
            "availability_heuristic": ["최근에", "기억나는", "들어본", "경험상"],
            "emotional_reasoning": ["느낌상", "기분적으로", "감정적으로", "마음으로는"],
        }

        indicators = bias_indicators.get(bias_name, [])
        matches = sum(1 for indicator in indicators if indicator in thought_content)

        score = min(matches / max(len(indicators), 1), 1.0)

        # 감정 강도가 높을 때 편향 가능성 증가
        emotion_intensity = emotion_context.get("intensity", 0.0)
        if emotion_intensity > 0.7:
            score *= 1.2

        return min(score, 1.0)

    def _generate_metacognitive_insights(
        self,
        consciousness_state: ConsciousnessState,
        thought_analysis: Dict[str, Any],
        bias_analysis: Dict[str, Any],
    ) -> List[str]:
        """메타인지적 통찰 생성"""
        insights = []

        # 의식 상태 기반 통찰
        if consciousness_state.awareness_level > 0.8:
            insights.append(
                "높은 인식 수준에서 작동 중 - 복합적 사고 과정을 동시에 관찰하고 있음"
            )
        elif consciousness_state.awareness_level < 0.3:
            insights.append("반응적 모드에서 작동 - 더 의식적인 관찰이 필요함")

        if consciousness_state.reflection_depth > 0.7:
            insights.append("깊은 성찰 모드 활성화 - 자기 이해와 통찰 생성 최적 상태")

        if consciousness_state.cognitive_load > 0.8:
            insights.append("높은 인지 부하 감지 - 사고 단순화 또는 휴식 필요")

        # 사고 패턴 기반 통찰
        dominant_pattern = thought_analysis.get("dominant_pattern")
        effectiveness = thought_analysis.get("pattern_effectiveness", 0.0)

        if effectiveness > 0.8:
            insights.append(
                f"{dominant_pattern} 패턴이 현재 상황에 매우 적합하게 작동 중"
            )
        elif effectiveness < 0.4:
            insights.append(
                f"{dominant_pattern} 패턴의 효과성이 낮음 - 다른 접근법 고려 필요"
            )

        # 편향 기반 통찰
        if bias_analysis:
            bias_count = len(bias_analysis)
            if bias_count >= 2:
                insights.append(
                    f"복수 인지 편향({bias_count}개) 감지 - 의식적 편향 보정 필요"
                )
            else:
                bias_name = list(bias_analysis.keys())[0]
                insights.append(f"{bias_name} 편향 패턴 관찰됨 - 대안적 관점 고려 권장")

        # 메타인지 레벨 기반 통찰
        if self.current_meta_level >= 3:
            insights.append(
                "메타인지적 모니터링 활성화 - 사고 과정을 실시간으로 관찰하고 조정 중"
            )

        return insights

    def _extract_behavioral_implications(
        self, insights: List[str], thought_analysis: Dict[str, Any]
    ) -> List[str]:
        """행동적 함의 추출"""
        implications = []

        # 통찰 기반 행동 제안
        for insight in insights:
            if "높은 인지 부하" in insight:
                implications.append("정보 처리 속도 조절 및 단계적 접근 필요")
            elif "편향" in insight:
                implications.append("의식적 관점 다각화 및 증거 재검토 수행")
            elif "효과성이 낮음" in insight:
                implications.append("현재 사고 전략 변경 및 대안적 접근법 탐색")

        # 사고 패턴 기반 행동 제안
        optimization_suggestions = thought_analysis.get("optimization_suggestions", [])
        for suggestion in optimization_suggestions[:2]:  # 상위 2개만
            implications.append(f"사고 패턴 최적화: {suggestion}")

        return implications

    def _set_future_monitoring_points(
        self, insights: List[str], thought_analysis: Dict[str, Any]
    ) -> List[str]:
        """미래 모니터링 포인트 설정"""
        monitoring_points = []

        # 통찰 기반 모니터링 포인트
        for insight in insights:
            if "편향" in insight:
                monitoring_points.append("향후 결정 시 편향 체크리스트 적용")
            elif "인지 부하" in insight:
                monitoring_points.append("복잡한 사고 작업 시 부하 수준 모니터링")
            elif "패턴" in insight and "효과성" in insight:
                monitoring_points.append("유사 상황에서 사고 패턴 효과성 추적")

        # 메타인지 발달 모니터링
        monitoring_points.append("메타인지 스킬 발달 진도 주기적 평가")

        # 의식 상태 변화 추적
        monitoring_points.append("다양한 컨텍스트에서 의식 상태 변화 패턴 관찰")

        return monitoring_points

    def _check_metacognitive_evolution(self, meta_reflection: MetaReflection) -> None:
        """메타인지 진화 체크 및 레벨업"""
        # 최근 성찰의 질과 깊이 평가
        recent_reflections = list(self.reflection_cache.values())[-10:]  # 최근 10개

        if len(recent_reflections) < 5:
            return  # 충분한 데이터 없음

        # 성찰 품질 지표들
        avg_awareness = statistics.mean(
            [r.consciousness_snapshot.awareness_level for r in recent_reflections]
        )
        avg_reflection_depth = statistics.mean(
            [r.consciousness_snapshot.reflection_depth for r in recent_reflections]
        )

        insights_count = sum(len(r.insight_generated) for r in recent_reflections)
        avg_insights = insights_count / len(recent_reflections)

        # 레벨업 조건 체크
        level_up_thresholds = {
            1: {"awareness": 0.4, "depth": 0.3, "insights": 2},
            2: {"awareness": 0.6, "depth": 0.5, "insights": 3},
            3: {"awareness": 0.7, "depth": 0.7, "insights": 4},
            4: {"awareness": 0.8, "depth": 0.8, "insights": 5},
        }

        current_threshold = level_up_thresholds.get(self.current_meta_level)
        if current_threshold and self.current_meta_level < 5:
            if (
                avg_awareness >= current_threshold["awareness"]
                and avg_reflection_depth >= current_threshold["depth"]
                and avg_insights >= current_threshold["insights"]
            ):

                self.current_meta_level += 1
                self.meta_level_progression.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "old_level": self.current_meta_level - 1,
                        "new_level": self.current_meta_level,
                        "trigger_metrics": {
                            "awareness": avg_awareness,
                            "depth": avg_reflection_depth,
                            "insights": avg_insights,
                        },
                    }
                )

                print(
                    f"🧘 메타인지 레벨 상승: {self.current_meta_level - 1} → {self.current_meta_level}"
                )

    def get_consciousness_trajectory(
        self, time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """의식 상태 변화 궤적 분석"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)

        recent_states = [
            entry
            for entry in self.consciousness_history
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]

        if not recent_states:
            return {"message": "충분한 데이터 없음"}

        # 궤적 분석
        awareness_trajectory = [
            entry["state"].awareness_level for entry in recent_states
        ]
        attention_trajectory = [
            entry["state"].attention_focus for entry in recent_states
        ]
        reflection_trajectory = [
            entry["state"].reflection_depth for entry in recent_states
        ]

        return {
            "time_window_hours": time_window_hours,
            "data_points": len(recent_states),
            "awareness_trend": {
                "values": awareness_trajectory,
                "average": statistics.mean(awareness_trajectory),
                "trend": (
                    "increasing"
                    if awareness_trajectory[-1] > awareness_trajectory[0]
                    else "decreasing"
                ),
            },
            "attention_pattern": {
                "values": attention_trajectory,
                "stability": (
                    1 - statistics.stdev(attention_trajectory)
                    if len(attention_trajectory) > 1
                    else 1.0
                ),
            },
            "reflection_development": {
                "values": reflection_trajectory,
                "peak": max(reflection_trajectory),
                "growth_rate": (reflection_trajectory[-1] - reflection_trajectory[0])
                / len(reflection_trajectory),
            },
        }

    def generate_consciousness_report(self) -> Dict[str, Any]:
        """의식 상태 종합 보고서 생성"""
        return {
            "current_status": {
                "meta_level": self.current_meta_level,
                "level_description": self.metacognitive_levels[self.current_meta_level][
                    "description"
                ],
                "capabilities": self.metacognitive_levels[self.current_meta_level][
                    "capabilities"
                ],
            },
            "recent_activity": {
                "total_reflections": len(self.reflection_cache),
                "consciousness_entries": len(self.consciousness_history),
                "level_progressions": len(self.meta_level_progression),
            },
            "consciousness_trajectory": self.get_consciousness_trajectory(),
            "evolutionary_progress": {
                "progression_history": self.meta_level_progression,
                "next_level_requirements": self.metacognitive_levels.get(
                    self.current_meta_level + 1, {"description": "최고 레벨 달성"}
                ),
            },
        }


def test_metacognitive_engine():
    """메타인지 엔진 테스트"""
    print("🧪 Metacognitive Engine 테스트 시작...")

    engine = MetacognitiveEngine()

    # 테스트 시나리오 1: 기본 의식 상태 분석
    print("\n📝 시나리오 1: 의식 상태 분석")
    context_1 = {
        "thought_content": "요즘 내가 어떤 방식으로 문제를 해결하고 있는지 생각해보니, 항상 같은 패턴으로 접근하는 것 같다.",
        "emotion_context": {
            "primary": {"curiosity": 0.6, "concern": 0.4},
            "intensity": 0.5,
        },
    }

    consciousness_state = engine.analyze_consciousness_state(context_1)
    print(f"📊 의식 수준: {consciousness_state.awareness_level:.3f}")
    print(f"🎯 주의 집중: {consciousness_state.attention_focus:.3f}")
    print(f"🔍 성찰 깊이: {consciousness_state.reflection_depth:.3f}")
    print(f"🧠 인지 부하: {consciousness_state.cognitive_load:.3f}")
    print(f"⏰ 시간 관점: {consciousness_state.temporal_perspective}")

    # 테스트 시나리오 2: 메타 성찰 수행
    print("\n📝 시나리오 2: 메타 성찰 수행")
    meta_reflection = engine.perform_meta_reflection(
        thought_content="내가 이런 결정을 내린 이유는 뭘까? 감정적으로 판단한 건 아닐까?",
        emotion_context={
            "primary": {"doubt": 0.7, "anxiety": 0.3},
            "intensity": 0.6,
            "stability": 0.4,
        },
        decision_context={"options_considered": 3, "time_pressure": 0.7, "stakes": 0.8},
    )

    print(f"🎯 성찰 ID: {meta_reflection.reflection_id}")
    print(f"🧠 생성된 통찰:")
    for insight in meta_reflection.insight_generated:
        print(f"   - {insight}")

    print(f"🎬 행동적 함의:")
    for implication in meta_reflection.behavioral_implications:
        print(f"   - {implication}")

    # 테스트 시나리오 3: 사고 패턴 분석
    print("\n📝 시나리오 3: 사고 패턴 분석")
    analytical_thought = "먼저 문제를 구체적으로 분석해보자. 첫째, 원인을 파악하고, 둘째, 가능한 해결책들을 나열한 다음, 셋째, 각각의 장단점을 비교해보겠다."

    meta_reflection_2 = engine.perform_meta_reflection(
        thought_content=analytical_thought,
        emotion_context={
            "primary": {"focus": 0.8, "determination": 0.2},
            "intensity": 0.4,
        },
    )

    thought_analysis = meta_reflection_2.thought_analysis
    print(f"🎯 지배적 사고 패턴: {thought_analysis['dominant_pattern']}")
    print(f"💪 패턴 강점: {thought_analysis['pattern_strengths']}")
    print(f"⚠️ 패턴 약점: {thought_analysis['pattern_weaknesses']}")
    print(f"📈 효과성 점수: {thought_analysis['pattern_effectiveness']:.3f}")

    # 테스트 시나리오 4: 인지 편향 감지
    print("\n📝 시나리오 4: 인지 편향 감지")
    biased_thought = "확실히 이 방법이 맞다. 최근에 들어본 성공 사례들을 보면 명백히 효과적이다. 처음 느낌부터 좋았으니까."

    meta_reflection_3 = engine.perform_meta_reflection(
        thought_content=biased_thought,
        emotion_context={"primary": {"confidence": 0.9}, "intensity": 0.8},
    )

    print(f"⚠️ 감지된 편향:")
    for bias_name, bias_info in meta_reflection_3.thought_analysis.get(
        "bias_analysis", {}
    ).items():
        print(f"   {bias_name}: 신뢰도 {bias_info['confidence']:.3f}")
        print(f"   완화 전략: {bias_info['mitigation_strategies'][:2]}")

    # 테스트 시나리오 5: 의식 궤적 및 진화 보고서
    print("\n📝 시나리오 5: 종합 의식 보고서")

    # 몇 개의 추가 성찰 시뮬레이션 (레벨업 테스트)
    for i in range(5):
        engine.perform_meta_reflection(
            thought_content=f"테스트 성찰 {i+1}: 나의 사고 과정을 더 깊이 들여다보고 있다.",
            emotion_context={
                "primary": {"insight": 0.7 + i * 0.05, "clarity": 0.6 + i * 0.05},
                "intensity": 0.5 + i * 0.1,
            },
        )

    consciousness_report = engine.generate_consciousness_report()

    print(
        f"🧘 현재 메타인지 레벨: {consciousness_report['current_status']['meta_level']}"
    )
    print(
        f"📝 레벨 설명: {consciousness_report['current_status']['level_description']}"
    )
    print(
        f"📊 총 성찰 횟수: {consciousness_report['recent_activity']['total_reflections']}"
    )
    print(
        f"📈 레벨 진화 횟수: {consciousness_report['recent_activity']['level_progressions']}"
    )

    # 의식 궤적 분석
    trajectory = consciousness_report["consciousness_trajectory"]
    if "awareness_trend" in trajectory:
        print(f"🎯 인식 수준 트렌드: {trajectory['awareness_trend']['trend']}")
        print(f"📊 평균 인식 수준: {trajectory['awareness_trend']['average']:.3f}")

    print("\n🎉 Metacognitive Engine 테스트 완료!")


if __name__ == "__main__":
    test_metacognitive_engine()
