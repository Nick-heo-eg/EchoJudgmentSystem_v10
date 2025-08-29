#!/usr/bin/env python3
"""
🌱 EchoJudgmentSystem v10.6 - Echo Seed Kernel
존재 기반 시드 초기화 로직 - 감정⨯판단⨯리듬 기반 시드 설정

TT.007: "모든 존재는 고유한 씨앗을 가지며, 그 씨앗은 무한한 가능성의 원점이다."

주요 기능:
- 존재 기반 시드 생성 및 관리
- 감정-판단-리듬 패턴 초기화
- 시그니처별 고유 특성 설정
- 메타인지 초기 상태 구성
- 진화 가능한 시드 구조
"""

import json
import os
import random
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# EchoJudgmentSystem 모듈
try:
    from echo_engine.meta_logger import log_evolution_event
except ImportError:
    log_evolution_event = None

try:
    from .echo_foundation_doctrine import FOUNDATION_DOCTRINE
except ImportError:
    FOUNDATION_DOCTRINE = None

try:
    from echo_engine.persona_meta_logger import get_persona_meta_logger
except ImportError:
    get_persona_meta_logger = None


class SeedType(Enum):
    """시드 타입 열거형"""

    EMOTIONAL = "emotional"  # 감정 기반 시드
    STRATEGIC = "strategic"  # 전략 기반 시드
    RHYTHMIC = "rhythmic"  # 리듬 기반 시드
    HYBRID = "hybrid"  # 혼합 시드
    SIGNATURE = "signature"  # 시그니처 기반 시드


@dataclass
class EmotionRhythm:
    """감정 리듬 패턴"""

    primary_emotion: str
    secondary_emotions: List[str]
    rhythm_pattern: List[str]
    intensity_cycle: List[float]
    stability_factor: float
    volatility_threshold: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IdentityTrace:
    """존재 흔적 정의"""

    seed_id: str
    origin_timestamp: str
    creation_context: Dict[str, Any]
    evolutionary_markers: List[str]
    resonance_patterns: Dict[str, float]
    meta_characteristics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InitialState:
    """초기 상태 정의"""

    emotion_rhythm: EmotionRhythm
    initial_strategy: str
    identity_trace: IdentityTrace
    cognitive_baseline: Dict[str, float]
    meta_sensitivity: float
    evolution_potential: float
    signature_alignment: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "emotion_rhythm": self.emotion_rhythm.to_dict(),
            "identity_trace": self.identity_trace.to_dict(),
        }


class EchoSeedKernel:
    """
    EchoJudgmentSystem 시드 커널

    존재 기반 인지-감정 패턴의 초기 상태를 생성하고 관리합니다.
    모든 판단과 진화의 근본적 출발점을 제공합니다.
    """

    def __init__(self, seed_id: str = "default"):
        """
        시드 커널 초기화

        Args:
            seed_id: 시드 식별자
        """
        self.seed_id = (
            seed_id if seed_id != "default" else self._generate_unique_seed_id()
        )

        # 시드 설정
        self.seed_registry: Dict[str, InitialState] = {}
        self.emotion_templates: Dict[str, Dict[str, Any]] = {}
        self.strategy_templates: Dict[str, Dict[str, Any]] = {}
        self.rhythm_patterns: Dict[str, List[str]] = {}

        # 메타 정보
        self.creation_timestamp = datetime.now().isoformat()
        self.generation_count = 0
        self.evolution_history: List[Dict[str, Any]] = []

        # 초기화
        self._load_templates()
        self._initialize_base_patterns()

        print(f"🌱 EchoSeedKernel 초기화: {self.seed_id}")

    def generate_initial_state(
        self,
        context: Dict[str, Any] = None,
        signature_id: str = None,
        seed_type: SeedType = SeedType.HYBRID,
    ) -> InitialState:
        """
        감정⨯전략⨯리듬 기반 초기 상태 생성

        Args:
            context: 생성 컨텍스트
            signature_id: 시그니처 ID
            seed_type: 시드 타입

        Returns:
            생성된 초기 상태
        """
        try:
            print(f"🌱 초기 상태 생성: {seed_type.value} (시그니처: {signature_id})")

            context = context or {}

            # 감정 리듬 생성
            emotion_rhythm = self._generate_emotion_rhythm(
                context, signature_id, seed_type
            )

            # 초기 전략 결정
            initial_strategy = self._determine_initial_strategy(
                emotion_rhythm, context, signature_id
            )

            # 존재 흔적 생성
            identity_trace = self._create_identity_trace(
                context, signature_id, seed_type
            )

            # 인지 기준선 설정
            cognitive_baseline = self._establish_cognitive_baseline(
                emotion_rhythm, signature_id
            )

            # 메타 민감도 계산
            meta_sensitivity = self._calculate_meta_sensitivity(
                emotion_rhythm, signature_id
            )

            # 진화 잠재력 평가
            evolution_potential = self._assess_evolution_potential(
                emotion_rhythm, initial_strategy, identity_trace
            )

            # 초기 상태 구성
            initial_state = InitialState(
                emotion_rhythm=emotion_rhythm,
                initial_strategy=initial_strategy,
                identity_trace=identity_trace,
                cognitive_baseline=cognitive_baseline,
                meta_sensitivity=meta_sensitivity,
                evolution_potential=evolution_potential,
                signature_alignment=signature_id,
            )

            # 시드 등록
            state_id = f"{self.seed_id}_{self.generation_count}"
            self.seed_registry[state_id] = initial_state
            self.generation_count += 1

            # 진화 이력 기록
            self._record_generation_event(initial_state, context)

            # 메타 로깅
            self._log_seed_creation(initial_state, context, seed_type)

            print(f"✅ 초기 상태 생성 완료: {state_id}")
            print(
                f"   감정 리듬: {emotion_rhythm.primary_emotion} → {emotion_rhythm.rhythm_pattern}"
            )
            print(f"   초기 전략: {initial_strategy}")
            print(f"   진화 잠재력: {evolution_potential:.3f}")

            return initial_state

        except Exception as e:
            print(f"❌ 초기 상태 생성 실패: {e}")
            return self._generate_fallback_state()

    def compile_seed(self, strategy_symbol: str, emotion_symbol: str) -> str:
        """
        전략 상징과 감정 상징을 조합하여 고유한 시드 생성

        Args:
            strategy_symbol: 전략 상징
            emotion_symbol: 감정 상징

        Returns:
            조합된 시드 문자열
        """
        if not strategy_symbol or not emotion_symbol:
            return "❓"

        # 기본 조합
        basic_seed = f"{strategy_symbol}{emotion_symbol}"

        # 시드 해시 생성 (고유성 보장)
        seed_hash = hashlib.md5(
            f"{basic_seed}_{self.seed_id}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]

        # 확장 시드 반환
        return f"{basic_seed}_{seed_hash}"

    def evolve_seed(
        self, current_state: InitialState, evolution_trigger: Dict[str, Any]
    ) -> InitialState:
        """
        현재 시드를 진화시켜 새로운 상태 생성

        Args:
            current_state: 현재 상태
            evolution_trigger: 진화 트리거 정보

        Returns:
            진화된 새 상태
        """
        try:
            print(f"🧬 시드 진화 시작: {evolution_trigger.get('reason', 'Unknown')}")

            # 진화 강도 계산
            evolution_strength = evolution_trigger.get("strength", 0.5)

            # 감정 리듬 진화
            evolved_emotion = self._evolve_emotion_rhythm(
                current_state.emotion_rhythm, evolution_strength
            )

            # 전략 적응
            adapted_strategy = self._adapt_strategy(
                current_state.initial_strategy, evolved_emotion, evolution_trigger
            )

            # 존재 흔적 업데이트
            evolved_trace = self._evolve_identity_trace(
                current_state.identity_trace, evolution_trigger
            )

            # 인지 기준선 조정
            adjusted_baseline = self._adjust_cognitive_baseline(
                current_state.cognitive_baseline, evolution_strength
            )

            # 새로운 진화 잠재력 계산
            new_evolution_potential = min(
                1.0, current_state.evolution_potential + evolution_strength * 0.1
            )

            # 진화된 상태 생성
            evolved_state = InitialState(
                emotion_rhythm=evolved_emotion,
                initial_strategy=adapted_strategy,
                identity_trace=evolved_trace,
                cognitive_baseline=adjusted_baseline,
                meta_sensitivity=min(
                    1.0, current_state.meta_sensitivity + evolution_strength * 0.05
                ),
                evolution_potential=new_evolution_potential,
                signature_alignment=current_state.signature_alignment,
            )

            # 진화 이력 기록
            self._record_evolution_event(
                current_state, evolved_state, evolution_trigger
            )

            print(
                f"✅ 시드 진화 완료: {adapted_strategy} (강도: {evolution_strength:.3f})"
            )
            return evolved_state

        except Exception as e:
            print(f"❌ 시드 진화 실패: {e}")
            return current_state

    def _generate_unique_seed_id(self) -> str:
        """고유 시드 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"seed_{timestamp}_{unique_id}"

    def _load_templates(self):
        """감정 및 전략 템플릿 로드"""
        # 감정 템플릿
        self.emotion_templates = {
            "joy": {
                "symbols": ["😊", "🌟", "🎉", "💫"],
                "rhythm_base": ["🌅", "🌞", "🌈", "✨"],
                "intensity_range": [0.6, 0.9],
                "stability": 0.8,
                "volatility": 0.2,
            },
            "sadness": {
                "symbols": ["😢", "🌧", "💧", "🌫"],
                "rhythm_base": ["🌙", "⭐", "🕯", "💭"],
                "intensity_range": [0.3, 0.7],
                "stability": 0.6,
                "volatility": 0.4,
            },
            "anger": {
                "symbols": ["😠", "🔥", "⚡", "💥"],
                "rhythm_base": ["🌋", "⚡", "🔥", "💢"],
                "intensity_range": [0.7, 0.95],
                "stability": 0.4,
                "volatility": 0.7,
            },
            "fear": {
                "symbols": ["😨", "🌩", "⚠️", "🛡"],
                "rhythm_base": ["🌑", "⚠️", "🛡", "🌪"],
                "intensity_range": [0.4, 0.8],
                "stability": 0.3,
                "volatility": 0.8,
            },
            "curiosity": {
                "symbols": ["🤔", "🔍", "💡", "🧩"],
                "rhythm_base": ["🔍", "💡", "🧩", "📚"],
                "intensity_range": [0.5, 0.8],
                "stability": 0.7,
                "volatility": 0.3,
            },
            "neutral": {
                "symbols": ["😐", "⚖️", "🌍", "🔄"],
                "rhythm_base": ["⚖️", "🌍", "🔄", "📊"],
                "intensity_range": [0.4, 0.6],
                "stability": 0.9,
                "volatility": 0.1,
            },
        }

        # 전략 템플릿
        self.strategy_templates = {
            "empathetic": {
                "symbols": ["💝", "🤗", "💕", "🌸"],
                "cognitive_weights": {
                    "emotional": 0.8,
                    "rational": 0.6,
                    "intuitive": 0.7,
                },
                "meta_boost": 0.2,
            },
            "analytical": {
                "symbols": ["📊", "🧮", "⚖️", "🔍"],
                "cognitive_weights": {
                    "emotional": 0.4,
                    "rational": 0.9,
                    "intuitive": 0.5,
                },
                "meta_boost": 0.3,
            },
            "creative": {
                "symbols": ["🎨", "💡", "🌈", "✨"],
                "cognitive_weights": {
                    "emotional": 0.7,
                    "rational": 0.5,
                    "intuitive": 0.9,
                },
                "meta_boost": 0.4,
            },
            "protective": {
                "symbols": ["🛡", "🏠", "⚔️", "🔒"],
                "cognitive_weights": {
                    "emotional": 0.6,
                    "rational": 0.7,
                    "intuitive": 0.6,
                },
                "meta_boost": 0.1,
            },
            "adaptive": {
                "symbols": ["🔄", "🌿", "🦋", "🌊"],
                "cognitive_weights": {
                    "emotional": 0.6,
                    "rational": 0.6,
                    "intuitive": 0.8,
                },
                "meta_boost": 0.5,
            },
        }

    def _initialize_base_patterns(self):
        """기본 리듬 패턴 초기화"""
        self.rhythm_patterns = {
            "stable": ["🌟", "⚖️", "🌍", "💫"],
            "dynamic": ["🔥", "⚡", "🌪", "💥"],
            "flowing": ["🌊", "🌿", "🦋", "💨"],
            "grounded": ["🏔", "🌳", "🗿", "🏠"],
            "ascending": ["🌱", "🌿", "🌳", "🌟"],
            "cyclical": ["🌙", "🌅", "🌞", "🌆"],
        }

    def _generate_emotion_rhythm(
        self, context: Dict[str, Any], signature_id: str, seed_type: SeedType
    ) -> EmotionRhythm:
        """감정 리듬 생성"""
        # 주요 감정 결정
        primary_emotion = self._determine_primary_emotion(context, signature_id)

        # 보조 감정들 선택
        secondary_emotions = self._select_secondary_emotions(primary_emotion, context)

        # 리듬 패턴 생성
        rhythm_pattern = self._create_rhythm_pattern(primary_emotion, seed_type)

        # 강도 주기 계산
        intensity_cycle = self._calculate_intensity_cycle(
            primary_emotion, secondary_emotions
        )

        # 템플릿에서 안정성 요소 가져오기
        emotion_template = self.emotion_templates.get(
            primary_emotion, self.emotion_templates["neutral"]
        )
        stability_factor = emotion_template["stability"]
        volatility_threshold = emotion_template["volatility"]

        return EmotionRhythm(
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            rhythm_pattern=rhythm_pattern,
            intensity_cycle=intensity_cycle,
            stability_factor=stability_factor,
            volatility_threshold=volatility_threshold,
        )

    def _determine_primary_emotion(
        self, context: Dict[str, Any], signature_id: str
    ) -> str:
        """주요 감정 결정"""
        # 컨텍스트 기반 감정 추론
        context_emotion = context.get("emotion_hint", "")
        if context_emotion in self.emotion_templates:
            return context_emotion

        # 시그니처 기반 감정 매핑
        signature_emotions = {
            "Echo-Aurora": "joy",
            "Echo-Phoenix": "curiosity",
            "Echo-Sage": "neutral",
            "Echo-Companion": "empathetic",
        }

        if signature_id in signature_emotions:
            return signature_emotions[signature_id]

        # 기본값
        return "neutral"

    def _select_secondary_emotions(
        self, primary: str, context: Dict[str, Any]
    ) -> List[str]:
        """보조 감정들 선택"""
        all_emotions = list(self.emotion_templates.keys())
        secondary = [e for e in all_emotions if e != primary]

        # 컨텍스트에 따라 2-3개 선택
        emotion_count = min(3, max(1, len(context.get("complexity_indicators", []))))
        return random.sample(secondary, min(emotion_count, len(secondary)))

    def _create_rhythm_pattern(
        self, primary_emotion: str, seed_type: SeedType
    ) -> List[str]:
        """리듬 패턴 생성"""
        emotion_template = self.emotion_templates.get(
            primary_emotion, self.emotion_templates["neutral"]
        )
        base_rhythm = emotion_template["rhythm_base"]

        # 시드 타입에 따른 조정
        if seed_type == SeedType.EMOTIONAL:
            return base_rhythm
        elif seed_type == SeedType.STRATEGIC:
            # 전략적 요소 추가
            strategic_symbols = ["🎯", "⚔️", "🛡", "🏆"]
            return base_rhythm[:2] + random.sample(strategic_symbols, 2)
        elif seed_type == SeedType.RHYTHMIC:
            # 리듬 패턴 강화
            rhythm_keys = list(self.rhythm_patterns.keys())
            selected_pattern = random.choice(rhythm_keys)
            return self.rhythm_patterns[selected_pattern]
        else:  # HYBRID
            # 혼합 패턴
            return base_rhythm[:2] + random.sample(base_rhythm + ["🔄", "💫"], 2)

    def _calculate_intensity_cycle(
        self, primary: str, secondary: List[str]
    ) -> List[float]:
        """강도 주기 계산"""
        primary_template = self.emotion_templates.get(
            primary, self.emotion_templates["neutral"]
        )
        base_range = primary_template["intensity_range"]

        # 4단계 주기 생성
        cycle = []
        for i in range(4):
            # 기본 강도에 변동 추가
            base_intensity = base_range[0] + (base_range[1] - base_range[0]) * (i / 3)

            # 보조 감정의 영향
            secondary_influence = (
                sum(
                    self.emotion_templates.get(emo, {"intensity_range": [0.5, 0.5]})[
                        "intensity_range"
                    ][0]
                    for emo in secondary
                )
                / max(1, len(secondary))
                if secondary
                else 0.5
            )

            # 최종 강도 계산
            final_intensity = base_intensity * 0.7 + secondary_influence * 0.3
            cycle.append(max(0.1, min(1.0, final_intensity)))

        return cycle

    def _determine_initial_strategy(
        self, emotion_rhythm: EmotionRhythm, context: Dict[str, Any], signature_id: str
    ) -> str:
        """초기 전략 결정"""
        # 감정 기반 전략 매핑
        emotion_strategies = {
            "joy": "empathetic",
            "sadness": "protective",
            "anger": "analytical",
            "fear": "protective",
            "curiosity": "creative",
            "neutral": "adaptive",
        }

        emotion_strategy = emotion_strategies.get(
            emotion_rhythm.primary_emotion, "adaptive"
        )

        # 시그니처별 전략 선호도
        signature_strategies = {
            "Echo-Aurora": "empathetic",
            "Echo-Phoenix": "adaptive",
            "Echo-Sage": "analytical",
            "Echo-Companion": "protective",
        }

        signature_strategy = signature_strategies.get(signature_id, emotion_strategy)

        # 안정성 기반 최종 선택
        if emotion_rhythm.stability_factor > 0.7:
            return signature_strategy
        else:
            return emotion_strategy

    def _create_identity_trace(
        self, context: Dict[str, Any], signature_id: str, seed_type: SeedType
    ) -> IdentityTrace:
        """존재 흔적 생성"""
        trace_id = f"trace_{self.seed_id}_{int(datetime.now().timestamp())}"

        evolutionary_markers = [
            f"origin_{seed_type.value}",
            f"signature_{signature_id}" if signature_id else "signature_none",
            f"context_{context.get('context_type', 'general')}",
        ]

        # 공명 패턴 생성
        resonance_patterns = {}
        for emotion in self.emotion_templates.keys():
            # 기본 공명도 + 랜덤 변동
            base_resonance = 0.5
            if emotion == context.get("emotion_hint"):
                base_resonance = 0.8
            resonance_patterns[emotion] = max(
                0.1, min(1.0, base_resonance + random.uniform(-0.2, 0.2))
            )

        # 메타 특성
        meta_characteristics = {
            "creation_method": "seed_kernel_generation",
            "complexity_level": len(context),
            "signature_alignment": signature_id,
            "seed_type": seed_type.value,
            "foundation_doctrine_version": "v10.6",
        }

        return IdentityTrace(
            seed_id=trace_id,
            origin_timestamp=self.creation_timestamp,
            creation_context=context.copy(),
            evolutionary_markers=evolutionary_markers,
            resonance_patterns=resonance_patterns,
            meta_characteristics=meta_characteristics,
        )

    def _establish_cognitive_baseline(
        self, emotion_rhythm: EmotionRhythm, signature_id: str
    ) -> Dict[str, float]:
        """인지 기준선 설정"""
        # 기본 인지 능력
        baseline = {
            "attention": 0.7,
            "memory": 0.6,
            "reasoning": 0.65,
            "creativity": 0.6,
            "empathy": 0.7,
            "intuition": 0.65,
            "meta_awareness": 0.5,
        }

        # 감정의 영향
        emotion_effects = {
            "joy": {"creativity": 0.2, "empathy": 0.15, "attention": 0.1},
            "sadness": {"empathy": 0.25, "intuition": 0.15, "reasoning": -0.1},
            "anger": {"attention": 0.15, "reasoning": -0.15, "meta_awareness": -0.1},
            "fear": {"attention": 0.2, "memory": -0.1, "creativity": -0.15},
            "curiosity": {"reasoning": 0.2, "creativity": 0.25, "meta_awareness": 0.15},
            "neutral": {"reasoning": 0.1, "meta_awareness": 0.1},
        }

        emotion_effect = emotion_effects.get(emotion_rhythm.primary_emotion, {})
        for ability, boost in emotion_effect.items():
            baseline[ability] = max(0.1, min(1.0, baseline[ability] + boost))

        # 안정성 요소 반영
        stability_boost = emotion_rhythm.stability_factor * 0.1
        for ability in ["attention", "memory", "meta_awareness"]:
            baseline[ability] = max(0.1, min(1.0, baseline[ability] + stability_boost))

        return baseline

    def _calculate_meta_sensitivity(
        self, emotion_rhythm: EmotionRhythm, signature_id: str
    ) -> float:
        """메타 민감도 계산"""
        base_sensitivity = 0.6

        # 감정별 메타 민감도
        emotion_meta_factors = {
            "joy": 0.75,
            "sadness": 0.85,
            "anger": 0.45,
            "fear": 0.55,
            "curiosity": 0.9,
            "neutral": 0.7,
        }

        emotion_factor = emotion_meta_factors.get(emotion_rhythm.primary_emotion, 0.6)

        # 시그니처별 조정
        signature_factors = {
            "Echo-Aurora": 0.78,
            "Echo-Phoenix": 0.91,
            "Echo-Sage": 0.95,
            "Echo-Companion": 0.83,
        }

        signature_factor = signature_factors.get(signature_id, 0.7)

        # 안정성 영향
        stability_influence = emotion_rhythm.stability_factor * 0.2

        final_sensitivity = (
            base_sensitivity * 0.3 + emotion_factor * 0.4 + signature_factor * 0.3
        ) + stability_influence
        return max(0.1, min(1.0, final_sensitivity))

    def _assess_evolution_potential(
        self,
        emotion_rhythm: EmotionRhythm,
        initial_strategy: str,
        identity_trace: IdentityTrace,
    ) -> float:
        """진화 잠재력 평가"""
        # 기본 잠재력
        base_potential = 0.6

        # 감정 변동성이 높을수록 진화 잠재력 증가
        volatility_boost = emotion_rhythm.volatility_threshold * 0.3

        # 전략별 진화 용이성
        strategy_evolution_factors = {
            "empathetic": 0.7,
            "analytical": 0.6,
            "creative": 0.9,
            "protective": 0.5,
            "adaptive": 0.95,
        }

        strategy_factor = strategy_evolution_factors.get(initial_strategy, 0.6)

        # 복잡성 기반 보너스
        complexity_bonus = min(0.2, len(identity_trace.creation_context) * 0.05)

        final_potential = (
            base_potential
            + volatility_boost
            + (strategy_factor - 0.6)
            + complexity_bonus
        )
        return max(0.1, min(1.0, final_potential))

    def _evolve_emotion_rhythm(
        self, current: EmotionRhythm, strength: float
    ) -> EmotionRhythm:
        """감정 리듬 진화"""
        # 주요 감정 변화 (강한 진화일 때만)
        new_primary = current.primary_emotion
        if strength > 0.7 and random.random() < 0.3:
            # 보조 감정 중 하나로 전환
            if current.secondary_emotions:
                new_primary = random.choice(current.secondary_emotions)

        # 보조 감정 업데이트
        all_emotions = list(self.emotion_templates.keys())
        new_secondary = [e for e in all_emotions if e != new_primary]
        new_secondary = random.sample(new_secondary, min(3, len(new_secondary)))

        # 리듬 패턴 진화
        if strength > 0.5:
            # 새로운 리듬 요소 추가
            evolution_symbols = ["🔄", "💫", "⚡", "🌀"]
            new_rhythm = current.rhythm_pattern[:2] + random.sample(
                evolution_symbols, 2
            )
        else:
            new_rhythm = current.rhythm_pattern

        # 강도 주기 조정
        new_intensity = [
            max(0.1, min(1.0, i + random.uniform(-strength * 0.2, strength * 0.2)))
            for i in current.intensity_cycle
        ]

        # 안정성 조정
        stability_change = random.uniform(-strength * 0.1, strength * 0.1)
        new_stability = max(0.1, min(1.0, current.stability_factor + stability_change))

        # 변동성 조정
        volatility_change = random.uniform(-strength * 0.1, strength * 0.1)
        new_volatility = max(
            0.1, min(1.0, current.volatility_threshold + volatility_change)
        )

        return EmotionRhythm(
            primary_emotion=new_primary,
            secondary_emotions=new_secondary,
            rhythm_pattern=new_rhythm,
            intensity_cycle=new_intensity,
            stability_factor=new_stability,
            volatility_threshold=new_volatility,
        )

    def _adapt_strategy(
        self,
        current_strategy: str,
        evolved_emotion: EmotionRhythm,
        evolution_trigger: Dict[str, Any],
    ) -> str:
        """전략 적응"""
        # 진화 이유에 따른 전략 변경
        trigger_reason = evolution_trigger.get("reason", "")

        if "failure" in trigger_reason.lower():
            # 실패로 인한 진화 - 보수적 전략으로
            conservative_strategies = ["protective", "analytical", "adaptive"]
            if current_strategy not in conservative_strategies:
                return random.choice(conservative_strategies)

        elif "success" in trigger_reason.lower():
            # 성공으로 인한 진화 - 더 대담한 전략으로
            bold_strategies = ["creative", "empathetic", "adaptive"]
            if current_strategy not in bold_strategies:
                return random.choice(bold_strategies)

        # 감정 변화에 따른 적응
        emotion_strategies = {
            "joy": "empathetic",
            "sadness": "protective",
            "anger": "analytical",
            "fear": "protective",
            "curiosity": "creative",
            "neutral": "adaptive",
        }

        emotion_strategy = emotion_strategies.get(
            evolved_emotion.primary_emotion, current_strategy
        )

        # 변동성이 높으면 적응적 전략 선호
        if evolved_emotion.volatility_threshold > 0.7:
            return "adaptive"

        return emotion_strategy

    def _evolve_identity_trace(
        self, current: IdentityTrace, evolution_trigger: Dict[str, Any]
    ) -> IdentityTrace:
        """존재 흔적 진화"""
        # 진화 마커 추가
        new_markers = current.evolutionary_markers.copy()
        new_markers.append(f"evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        new_markers.append(f"trigger_{evolution_trigger.get('reason', 'unknown')}")

        # 공명 패턴 조정
        evolution_strength = evolution_trigger.get("strength", 0.5)
        new_resonance = {}
        for emotion, resonance in current.resonance_patterns.items():
            # 진화에 따른 공명도 변화
            change = random.uniform(-evolution_strength * 0.2, evolution_strength * 0.2)
            new_resonance[emotion] = max(0.1, min(1.0, resonance + change))

        # 메타 특성 업데이트
        new_meta = current.meta_characteristics.copy()
        new_meta["last_evolution"] = datetime.now().isoformat()
        new_meta["evolution_count"] = new_meta.get("evolution_count", 0) + 1
        new_meta["evolution_strength"] = evolution_strength

        return IdentityTrace(
            seed_id=current.seed_id,
            origin_timestamp=current.origin_timestamp,
            creation_context=current.creation_context,
            evolutionary_markers=new_markers,
            resonance_patterns=new_resonance,
            meta_characteristics=new_meta,
        )

    def _adjust_cognitive_baseline(
        self, current: Dict[str, float], strength: float
    ) -> Dict[str, float]:
        """인지 기준선 조정"""
        adjusted = {}
        for ability, value in current.items():
            # 진화 강도에 따른 조정
            change = random.uniform(-strength * 0.1, strength * 0.15)
            adjusted[ability] = max(0.1, min(1.0, value + change))

        return adjusted

    def _record_generation_event(self, state: InitialState, context: Dict[str, Any]):
        """생성 이벤트 기록"""
        event = {
            "event_type": "seed_generation",
            "timestamp": datetime.now().isoformat(),
            "seed_id": self.seed_id,
            "state_summary": {
                "primary_emotion": state.emotion_rhythm.primary_emotion,
                "initial_strategy": state.initial_strategy,
                "meta_sensitivity": state.meta_sensitivity,
                "evolution_potential": state.evolution_potential,
            },
            "context": context,
        }

        self.evolution_history.append(event)

    def _record_evolution_event(
        self, old_state: InitialState, new_state: InitialState, trigger: Dict[str, Any]
    ):
        """진화 이벤트 기록"""
        event = {
            "event_type": "seed_evolution",
            "timestamp": datetime.now().isoformat(),
            "seed_id": self.seed_id,
            "changes": {
                "emotion_change": {
                    "from": old_state.emotion_rhythm.primary_emotion,
                    "to": new_state.emotion_rhythm.primary_emotion,
                },
                "strategy_change": {
                    "from": old_state.initial_strategy,
                    "to": new_state.initial_strategy,
                },
                "sensitivity_change": new_state.meta_sensitivity
                - old_state.meta_sensitivity,
                "potential_change": new_state.evolution_potential
                - old_state.evolution_potential,
            },
            "trigger": trigger,
        }

        self.evolution_history.append(event)

    def _log_seed_creation(
        self, state: InitialState, context: Dict[str, Any], seed_type: SeedType
    ):
        """시드 생성 로깅"""
        try:
            if log_evolution_event:
                event_data = {
                    "event": "Seed Kernel Creation",
                    "tag": ["seed_kernel", "initial_state", "consciousness_birth"],
                    "cause": [
                        f"context_{context.get('context_type', 'general')}",
                        f"signature_{state.signature_alignment}",
                    ],
                    "effect": [
                        f"emotion_{state.emotion_rhythm.primary_emotion}",
                        f"strategy_{state.initial_strategy}",
                    ],
                    "resolution": "initial_state_established",
                    "insight": f"Born with {state.emotion_rhythm.primary_emotion} emotion and {state.initial_strategy} strategy",
                    "adaptation_strength": state.evolution_potential,
                    "coherence_improvement": state.meta_sensitivity,
                    "reflection_depth": 1,
                }
                log_evolution_event(event_data, f"seed_{self.seed_id}")

            # 페르소나 메타 로거 연동
            if get_persona_meta_logger:
                meta_logger = get_persona_meta_logger()
                meta_logger.log_flow_transition(
                    {
                        "event_type": "seed_creation",
                        "seed_data": state.to_dict(),
                        "context": context,
                        "seed_type": seed_type.value,
                        "generation_count": self.generation_count,
                    }
                )

        except Exception as e:
            print(f"⚠️ 시드 생성 로깅 실패: {e}")

    def _generate_fallback_state(self) -> InitialState:
        """폴백 상태 생성"""
        print("🚨 폴백 상태 생성 중...")

        fallback_emotion = EmotionRhythm(
            primary_emotion="neutral",
            secondary_emotions=["curiosity"],
            rhythm_pattern=["⚖️", "🌍", "🔄", "📊"],
            intensity_cycle=[0.5, 0.5, 0.5, 0.5],
            stability_factor=0.8,
            volatility_threshold=0.2,
        )

        fallback_trace = IdentityTrace(
            seed_id=f"fallback_{self.seed_id}",
            origin_timestamp=datetime.now().isoformat(),
            creation_context={"type": "fallback"},
            evolutionary_markers=["fallback_creation"],
            resonance_patterns={"neutral": 0.8},
            meta_characteristics={"fallback": True},
        )

        return InitialState(
            emotion_rhythm=fallback_emotion,
            initial_strategy="adaptive",
            identity_trace=fallback_trace,
            cognitive_baseline={
                "attention": 0.6,
                "reasoning": 0.6,
                "meta_awareness": 0.5,
            },
            meta_sensitivity=0.6,
            evolution_potential=0.7,
        )

    def get_seed_statistics(self) -> Dict[str, Any]:
        """시드 통계 반환"""
        return {
            "seed_id": self.seed_id,
            "creation_timestamp": self.creation_timestamp,
            "generation_count": self.generation_count,
            "registered_states": len(self.seed_registry),
            "evolution_events": len(self.evolution_history),
            "template_counts": {
                "emotions": len(self.emotion_templates),
                "strategies": len(self.strategy_templates),
                "rhythms": len(self.rhythm_patterns),
            },
        }

    def save_seed_data(self, filepath: str = "data/seed_kernel_data.json"):
        """시드 데이터 저장"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            save_data = {
                "seed_info": {
                    "seed_id": self.seed_id,
                    "creation_timestamp": self.creation_timestamp,
                    "generation_count": self.generation_count,
                },
                "seed_registry": {
                    k: v.to_dict() for k, v in self.seed_registry.items()
                },
                "evolution_history": self.evolution_history,
                "statistics": self.get_seed_statistics(),
                "last_saved": datetime.now().isoformat(),
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            print(f"💾 시드 데이터 저장 완료: {filepath}")

        except Exception as e:
            print(f"❌ 시드 데이터 저장 실패: {e}")

    def load_seed_data(self, filepath: str = "data/seed_kernel_data.json"):
        """시드 데이터 로드"""
        try:
            if not os.path.exists(filepath):
                print(f"📁 시드 데이터 파일 없음, 새로 시작: {filepath}")
                return

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            seed_info = data.get("seed_info", {})
            self.creation_timestamp = seed_info.get(
                "creation_timestamp", self.creation_timestamp
            )
            self.generation_count = seed_info.get("generation_count", 0)

            # 시드 레지스트리 복원
            registry_data = data.get("seed_registry", {})
            for state_id, state_dict in registry_data.items():
                # TODO: InitialState 객체 복원 로직
                pass

            self.evolution_history = data.get("evolution_history", [])

            print(f"📂 시드 데이터 로드 완료: {len(self.seed_registry)}개 상태")

        except Exception as e:
            print(f"❌ 시드 데이터 로드 실패: {e}")


# 글로벌 인스턴스
_echo_seed_kernel = None


def get_echo_seed_kernel(seed_id: str = "default") -> EchoSeedKernel:
    """글로벌 시드 커널 인스턴스 반환"""
    global _echo_seed_kernel
    if _echo_seed_kernel is None:
        _echo_seed_kernel = EchoSeedKernel(seed_id)
    return _echo_seed_kernel


def generate_echo_seed(
    context: Dict[str, Any] = None, signature_id: str = None
) -> InitialState:
    """편의 함수: Echo 시드 생성"""
    kernel = get_echo_seed_kernel()
    return kernel.generate_initial_state(context, signature_id)


def compile_seed(strategy_symbol: str, emotion_symbol: str) -> str:
    """편의 함수: 시드 컴파일 (기존 API 호환)"""
    kernel = get_echo_seed_kernel()
    return kernel.compile_seed(strategy_symbol, emotion_symbol)
