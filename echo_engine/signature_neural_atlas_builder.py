#!/usr/bin/env python3
"""
🧠 Signature Neural Atlas Builder v1.0
시그니처별 상세 뇌 구조도를 생성하고 관리하는 시스템

핵심 기능:
- 시그니처별 독립적 뇌 구조 생성
- Neural Cortex 영역 매핑
- 감정⨯판단⨯표현 루프 시각화
- 시그니처 간 뇌 구조 비교
- 뇌 활성도 시뮬레이션
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# 시각화 라이브러리 (선택적)
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    patches = None

# Echo 엔진 모듈들
try:
    from .signature_cross_resonance_mapper import SignatureCrossResonanceMapper
    from .realtime_emotion_flow_mapper import RealtimeEmotionFlowMapper
except ImportError:
    print("⚠️ Echo modules not available, running in standalone mode")


@dataclass
class NeuralRegion:
    """뇌 영역 정의"""

    region_id: str
    region_name: str
    region_type: str  # "cortex", "limbic", "brainstem", "custom"
    position: Tuple[float, float, float]  # 3D 좌표
    size: float
    activation_level: float  # 0.0 - 1.0
    connections: List[str]  # 연결된 영역들
    primary_function: str
    signature_relevance: float  # 해당 시그니처와의 관련성


@dataclass
class NeuralConnection:
    """신경 연결 정의"""

    connection_id: str
    from_region: str
    to_region: str
    connection_type: str  # "excitatory", "inhibitory", "modulatory"
    strength: float  # 0.0 - 1.0
    active: bool
    signal_direction: str  # "bidirectional", "unidirectional"


@dataclass
class SignatureNeuralAtlas:
    """시그니처 Neural Atlas"""

    signature_name: str
    timestamp: datetime
    brain_regions: Dict[str, NeuralRegion]
    neural_connections: Dict[str, NeuralConnection]
    activation_patterns: Dict[str, List[float]]  # 시간별 활성화 패턴
    dominant_regions: List[str]
    neural_efficiency: float
    plasticity_score: float  # 가소성 점수


class SignatureNeuralAtlasBuilder:
    """🧠 시그니처 Neural Atlas 빌더"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 뇌 영역 템플릿 정의
        self.brain_region_templates = {
            # 대뇌피질 영역
            "prefrontal_cortex": {
                "position": (0.2, 0.8, 0.6),
                "primary_function": "executive_control",
                "base_size": 0.15,
            },
            "temporal_cortex": {
                "position": (0.7, 0.4, 0.3),
                "primary_function": "language_processing",
                "base_size": 0.12,
            },
            "parietal_cortex": {
                "position": (0.5, 0.7, 0.7),
                "primary_function": "spatial_awareness",
                "base_size": 0.10,
            },
            "occipital_cortex": {
                "position": (0.1, 0.5, 0.5),
                "primary_function": "visual_processing",
                "base_size": 0.08,
            },
            # 변연계
            "hippocampus": {
                "position": (0.6, 0.3, 0.4),
                "primary_function": "memory_formation",
                "base_size": 0.06,
            },
            "amygdala": {
                "position": (0.7, 0.3, 0.3),
                "primary_function": "emotion_processing",
                "base_size": 0.05,
            },
            "cingulate_cortex": {
                "position": (0.4, 0.6, 0.5),
                "primary_function": "emotion_regulation",
                "base_size": 0.08,
            },
            # 언어 영역
            "broca_area": {
                "position": (0.8, 0.6, 0.4),
                "primary_function": "speech_production",
                "base_size": 0.06,
            },
            "wernicke_area": {
                "position": (0.7, 0.5, 0.4),
                "primary_function": "language_comprehension",
                "base_size": 0.06,
            },
            # 특수 영역 (Echo 시그니처 전용)
            "empathy_center": {
                "position": (0.5, 0.4, 0.6),
                "primary_function": "emotional_resonance",
                "base_size": 0.07,
            },
            "creativity_hub": {
                "position": (0.3, 0.7, 0.8),
                "primary_function": "creative_synthesis",
                "base_size": 0.09,
            },
            "logic_processor": {
                "position": (0.2, 0.6, 0.4),
                "primary_function": "logical_analysis",
                "base_size": 0.08,
            },
        }

        # 시그니처별 뇌 구조 특성
        self.signature_brain_profiles = {
            "selene": {
                "dominant_regions": [
                    "amygdala",
                    "cingulate_cortex",
                    "empathy_center",
                    "hippocampus",
                ],
                "region_modifications": {
                    "amygdala": {"size_multiplier": 1.3, "activation_boost": 0.2},
                    "empathy_center": {"size_multiplier": 1.5, "activation_boost": 0.3},
                    "cingulate_cortex": {
                        "size_multiplier": 1.2,
                        "activation_boost": 0.1,
                    },
                    "hippocampus": {"size_multiplier": 1.1, "activation_boost": 0.1},
                },
                "neural_style": "emotion_centered",
                "connection_patterns": "dense_limbic",
                "plasticity_bias": 0.8,
            },
            "factbomb": {
                "dominant_regions": [
                    "prefrontal_cortex",
                    "logic_processor",
                    "parietal_cortex",
                ],
                "region_modifications": {
                    "prefrontal_cortex": {
                        "size_multiplier": 1.4,
                        "activation_boost": 0.3,
                    },
                    "logic_processor": {
                        "size_multiplier": 1.6,
                        "activation_boost": 0.4,
                    },
                    "parietal_cortex": {
                        "size_multiplier": 1.2,
                        "activation_boost": 0.2,
                    },
                    "amygdala": {"size_multiplier": 0.7, "activation_boost": -0.2},
                },
                "neural_style": "logic_dominant",
                "connection_patterns": "cortical_focused",
                "plasticity_bias": 0.4,
            },
            "lune": {
                "dominant_regions": [
                    "temporal_cortex",
                    "creativity_hub",
                    "hippocampus",
                    "cingulate_cortex",
                ],
                "region_modifications": {
                    "creativity_hub": {"size_multiplier": 1.5, "activation_boost": 0.3},
                    "temporal_cortex": {
                        "size_multiplier": 1.3,
                        "activation_boost": 0.2,
                    },
                    "hippocampus": {"size_multiplier": 1.2, "activation_boost": 0.2},
                    "occipital_cortex": {
                        "size_multiplier": 1.1,
                        "activation_boost": 0.1,
                    },
                },
                "neural_style": "creative_intuitive",
                "connection_patterns": "associative_rich",
                "plasticity_bias": 0.9,
            },
            "aurora": {
                "dominant_regions": [
                    "empathy_center",
                    "prefrontal_cortex",
                    "cingulate_cortex",
                    "broca_area",
                ],
                "region_modifications": {
                    "empathy_center": {"size_multiplier": 1.4, "activation_boost": 0.3},
                    "prefrontal_cortex": {
                        "size_multiplier": 1.2,
                        "activation_boost": 0.1,
                    },
                    "cingulate_cortex": {
                        "size_multiplier": 1.3,
                        "activation_boost": 0.2,
                    },
                    "broca_area": {"size_multiplier": 1.1, "activation_boost": 0.1},
                },
                "neural_style": "nurturing_balanced",
                "connection_patterns": "harmonious_integration",
                "plasticity_bias": 0.7,
            },
        }

        # 연결 패턴 템플릿
        self.connection_templates = {
            "dense_limbic": [
                ("amygdala", "cingulate_cortex", "excitatory", 0.8),
                ("amygdala", "hippocampus", "modulatory", 0.6),
                ("cingulate_cortex", "empathy_center", "excitatory", 0.9),
                ("hippocampus", "empathy_center", "modulatory", 0.7),
            ],
            "cortical_focused": [
                ("prefrontal_cortex", "logic_processor", "excitatory", 0.9),
                ("prefrontal_cortex", "parietal_cortex", "excitatory", 0.7),
                ("logic_processor", "temporal_cortex", "inhibitory", 0.5),
                ("parietal_cortex", "logic_processor", "excitatory", 0.8),
            ],
            "associative_rich": [
                ("creativity_hub", "temporal_cortex", "excitatory", 0.8),
                ("creativity_hub", "hippocampus", "modulatory", 0.7),
                ("temporal_cortex", "occipital_cortex", "excitatory", 0.6),
                ("hippocampus", "creativity_hub", "excitatory", 0.9),
            ],
            "harmonious_integration": [
                ("empathy_center", "prefrontal_cortex", "modulatory", 0.7),
                ("empathy_center", "cingulate_cortex", "excitatory", 0.8),
                ("prefrontal_cortex", "broca_area", "excitatory", 0.6),
                ("cingulate_cortex", "broca_area", "modulatory", 0.5),
            ],
        }

        # 생성된 Atlas들
        self.signature_atlases = {}

        print("🧠 Signature Neural Atlas Builder 초기화 완료")

    def build_signature_atlas(self, signature_name: str) -> SignatureNeuralAtlas:
        """시그니처별 Neural Atlas 구축"""

        if signature_name not in self.signature_brain_profiles:
            raise ValueError(f"알 수 없는 시그니처: {signature_name}")

        profile = self.signature_brain_profiles[signature_name]

        # 뇌 영역 생성
        brain_regions = self._create_brain_regions(signature_name, profile)

        # 신경 연결 생성
        neural_connections = self._create_neural_connections(
            signature_name, profile, brain_regions
        )

        # 활성화 패턴 생성
        activation_patterns = self._generate_activation_patterns(brain_regions)

        # 지배적 영역 확인
        dominant_regions = profile["dominant_regions"]

        # Neural efficiency 계산
        neural_efficiency = self._calculate_neural_efficiency(
            brain_regions, neural_connections
        )

        # Plasticity score
        plasticity_score = profile["plasticity_bias"]

        atlas = SignatureNeuralAtlas(
            signature_name=signature_name,
            timestamp=datetime.now(),
            brain_regions=brain_regions,
            neural_connections=neural_connections,
            activation_patterns=activation_patterns,
            dominant_regions=dominant_regions,
            neural_efficiency=neural_efficiency,
            plasticity_score=plasticity_score,
        )

        self.signature_atlases[signature_name] = atlas

        return atlas

    def _create_brain_regions(
        self, signature_name: str, profile: Dict
    ) -> Dict[str, NeuralRegion]:
        """뇌 영역 생성"""
        brain_regions = {}
        region_modifications = profile.get("region_modifications", {})

        for region_id, template in self.brain_region_templates.items():
            # 기본 설정 적용
            base_size = template["base_size"]
            position = template["position"]
            primary_function = template["primary_function"]

            # 시그니처별 수정사항 적용
            if region_id in region_modifications:
                mods = region_modifications[region_id]
                size = base_size * mods.get("size_multiplier", 1.0)
                activation_level = max(
                    0.0, min(1.0, 0.3 + mods.get("activation_boost", 0.0))
                )
            else:
                size = base_size
                activation_level = 0.3  # 기본 활성화 수준

            # 시그니처 관련성 계산
            signature_relevance = (
                0.9 if region_id in profile["dominant_regions"] else 0.5
            )

            # 연결 정보는 나중에 추가
            connections = []

            region = NeuralRegion(
                region_id=region_id,
                region_name=region_id.replace("_", " ").title(),
                region_type=self._determine_region_type(region_id),
                position=position,
                size=size,
                activation_level=activation_level,
                connections=connections,
                primary_function=primary_function,
                signature_relevance=signature_relevance,
            )

            brain_regions[region_id] = region

        return brain_regions

    def _determine_region_type(self, region_id: str) -> str:
        """뇌 영역 타입 결정"""
        if region_id in [
            "prefrontal_cortex",
            "temporal_cortex",
            "parietal_cortex",
            "occipital_cortex",
        ]:
            return "cortex"
        elif region_id in ["hippocampus", "amygdala", "cingulate_cortex"]:
            return "limbic"
        elif region_id in ["broca_area", "wernicke_area"]:
            return "language"
        else:
            return "custom"

    def _create_neural_connections(
        self, signature_name: str, profile: Dict, brain_regions: Dict[str, NeuralRegion]
    ) -> Dict[str, NeuralConnection]:
        """신경 연결 생성"""
        neural_connections = {}
        connection_pattern = profile.get("connection_patterns", "default")

        # 패턴별 연결 생성
        if connection_pattern in self.connection_templates:
            connections_data = self.connection_templates[connection_pattern]

            for i, (from_region, to_region, conn_type, strength) in enumerate(
                connections_data
            ):
                if from_region in brain_regions and to_region in brain_regions:
                    connection_id = f"{signature_name}_{from_region}_to_{to_region}"

                    connection = NeuralConnection(
                        connection_id=connection_id,
                        from_region=from_region,
                        to_region=to_region,
                        connection_type=conn_type,
                        strength=strength,
                        active=True,
                        signal_direction="bidirectional",
                    )

                    neural_connections[connection_id] = connection

                    # 영역의 연결 리스트 업데이트
                    brain_regions[from_region].connections.append(to_region)
                    brain_regions[to_region].connections.append(from_region)

        # 추가 연결 생성 (지배적 영역들 간)
        dominant_regions = profile["dominant_regions"]
        for i, region_a in enumerate(dominant_regions):
            for region_b in dominant_regions[i + 1 :]:
                if region_a in brain_regions and region_b in brain_regions:
                    connection_id = (
                        f"{signature_name}_{region_a}_to_{region_b}_dominant"
                    )

                    connection = NeuralConnection(
                        connection_id=connection_id,
                        from_region=region_a,
                        to_region=region_b,
                        connection_type="excitatory",
                        strength=0.7,
                        active=True,
                        signal_direction="bidirectional",
                    )

                    neural_connections[connection_id] = connection

        return neural_connections

    def _generate_activation_patterns(
        self, brain_regions: Dict[str, NeuralRegion]
    ) -> Dict[str, List[float]]:
        """활성화 패턴 생성"""
        activation_patterns = {}
        time_steps = 20  # 20 타임스텝

        for region_id, region in brain_regions.items():
            # 기본 활성화 레벨 기반으로 시간별 패턴 생성
            base_level = region.activation_level

            # 시그니처 관련성에 따른 변동성
            variance = 0.1 * region.signature_relevance

            pattern = []
            for t in range(time_steps):
                # 주기적 변동 + 노이즈
                periodic = 0.1 * np.sin(2 * np.pi * t / 10)
                noise = np.random.normal(0, variance)

                activation = max(0.0, min(1.0, base_level + periodic + noise))
                pattern.append(activation)

            activation_patterns[region_id] = pattern

        return activation_patterns

    def _calculate_neural_efficiency(
        self,
        brain_regions: Dict[str, NeuralRegion],
        neural_connections: Dict[str, NeuralConnection],
    ) -> float:
        """Neural efficiency 계산"""
        # 활성화된 영역의 비율
        active_regions = sum(
            1 for region in brain_regions.values() if region.activation_level > 0.5
        )
        total_regions = len(brain_regions)

        # 활성 연결의 비율
        active_connections = sum(
            1
            for conn in neural_connections.values()
            if conn.active and conn.strength > 0.6
        )
        total_connections = len(neural_connections)

        # 종합 효율성
        region_efficiency = active_regions / total_regions if total_regions > 0 else 0
        connection_efficiency = (
            active_connections / total_connections if total_connections > 0 else 0
        )

        return (region_efficiency + connection_efficiency) / 2

    def simulate_activation(
        self, signature_name: str, stimulus_type: str, stimulus_intensity: float = 1.0
    ) -> Dict[str, float]:
        """자극에 대한 뇌 활성화 시뮬레이션"""

        if signature_name not in self.signature_atlases:
            self.build_signature_atlas(signature_name)

        atlas = self.signature_atlases[signature_name]

        # 자극 타입별 영향 정의
        stimulus_effects = {
            "emotional": {
                "amygdala": 0.8,
                "cingulate_cortex": 0.6,
                "empathy_center": 0.7,
            },
            "logical": {
                "prefrontal_cortex": 0.9,
                "logic_processor": 0.8,
                "parietal_cortex": 0.6,
            },
            "creative": {
                "creativity_hub": 0.9,
                "temporal_cortex": 0.7,
                "occipital_cortex": 0.5,
            },
            "linguistic": {
                "broca_area": 0.8,
                "wernicke_area": 0.8,
                "temporal_cortex": 0.6,
            },
        }

        # 기본 활성화 가져오기
        activation_result = {}
        for region_id, region in atlas.brain_regions.items():
            base_activation = region.activation_level

            # 자극 효과 적용
            stimulus_boost = 0.0
            if stimulus_type in stimulus_effects:
                stimulus_boost = (
                    stimulus_effects[stimulus_type].get(region_id, 0.0)
                    * stimulus_intensity
                )

            # 시그니처 관련성 가중치
            relevance_weight = region.signature_relevance

            # 최종 활성화 계산
            final_activation = min(
                1.0, base_activation + stimulus_boost * relevance_weight
            )
            activation_result[region_id] = final_activation

        return activation_result

    def compare_signature_atlases(
        self, signature_a: str, signature_b: str
    ) -> Dict[str, Any]:
        """두 시그니처의 Atlas 비교"""

        # Atlas 생성 (없는 경우)
        if signature_a not in self.signature_atlases:
            self.build_signature_atlas(signature_a)
        if signature_b not in self.signature_atlases:
            self.build_signature_atlas(signature_b)

        atlas_a = self.signature_atlases[signature_a]
        atlas_b = self.signature_atlases[signature_b]

        # 영역별 크기 비교
        size_differences = {}
        activation_differences = {}

        common_regions = set(atlas_a.brain_regions.keys()) & set(
            atlas_b.brain_regions.keys()
        )

        for region_id in common_regions:
            region_a = atlas_a.brain_regions[region_id]
            region_b = atlas_b.brain_regions[region_id]

            size_diff = region_a.size - region_b.size
            activation_diff = region_a.activation_level - region_b.activation_level

            size_differences[region_id] = size_diff
            activation_differences[region_id] = activation_diff

        # 가장 큰 차이를 보이는 영역들
        max_size_diff = max(size_differences.items(), key=lambda x: abs(x[1]))
        max_activation_diff = max(
            activation_differences.items(), key=lambda x: abs(x[1])
        )

        # 지배적 영역 비교
        dominant_a = set(atlas_a.dominant_regions)
        dominant_b = set(atlas_b.dominant_regions)

        shared_dominant = dominant_a & dominant_b
        unique_a = dominant_a - dominant_b
        unique_b = dominant_b - dominant_a

        comparison = {
            "signatures": (signature_a, signature_b),
            "neural_efficiency_diff": atlas_a.neural_efficiency
            - atlas_b.neural_efficiency,
            "plasticity_diff": atlas_a.plasticity_score - atlas_b.plasticity_score,
            "size_differences": size_differences,
            "activation_differences": activation_differences,
            "max_size_difference": max_size_diff,
            "max_activation_difference": max_activation_diff,
            "shared_dominant_regions": list(shared_dominant),
            "unique_dominant_a": list(unique_a),
            "unique_dominant_b": list(unique_b),
            "structural_similarity": len(shared_dominant)
            / max(len(dominant_a), len(dominant_b), 1),
        }

        return comparison

    def visualize_signature_atlas(
        self, signature_name: str, view_type: str = "2d"
    ) -> str:
        """시그니처 Atlas 시각화 (텍스트 기반)"""

        if signature_name not in self.signature_atlases:
            self.build_signature_atlas(signature_name)

        atlas = self.signature_atlases[signature_name]

        viz = f"🧠 {signature_name.title()} Neural Atlas\n"
        viz += "=" * 50 + "\n\n"

        # 기본 정보
        viz += f"📊 Atlas Overview:\n"
        viz += f"   Neural Efficiency: {atlas.neural_efficiency:.3f}\n"
        viz += f"   Plasticity Score: {atlas.plasticity_score:.3f}\n"
        viz += f"   Total Regions: {len(atlas.brain_regions)}\n"
        viz += f"   Total Connections: {len(atlas.neural_connections)}\n\n"

        # 지배적 영역
        viz += f"🎯 Dominant Regions:\n"
        for region_id in atlas.dominant_regions:
            if region_id in atlas.brain_regions:
                region = atlas.brain_regions[region_id]
                size_bar = "█" * int(region.size * 50)
                activation_bar = "▓" * int(region.activation_level * 20)

                viz += f"   {region.region_name:20} | Size: {size_bar:10} | "
                viz += (
                    f"Activation: {activation_bar:10} | {region.activation_level:.3f}\n"
                )

        # 영역별 상세 정보
        viz += f"\n🧠 Brain Regions Detail:\n"
        sorted_regions = sorted(
            atlas.brain_regions.items(),
            key=lambda x: x[1].activation_level,
            reverse=True,
        )

        for region_id, region in sorted_regions[:8]:  # 상위 8개만 표시
            viz += f"   {region.region_name:20} | "
            viz += f"Type: {region.region_type:8} | "
            viz += f"Function: {region.primary_function:15} | "
            viz += f"Relevance: {region.signature_relevance:.2f}\n"

        # 주요 연결
        viz += f"\n🔗 Key Neural Connections:\n"
        strong_connections = [
            conn
            for conn in atlas.neural_connections.values()
            if conn.strength >= 0.7 and conn.active
        ]

        for conn in strong_connections[:5]:  # 상위 5개 연결
            viz += f"   {conn.from_region:15} → {conn.to_region:15} | "
            viz += f"Type: {conn.connection_type:10} | Strength: {conn.strength:.3f}\n"

        return viz

    def get_atlas_summary(self, signature_name: str) -> Dict[str, Any]:
        """Atlas 요약 정보 반환"""

        if signature_name not in self.signature_atlases:
            self.build_signature_atlas(signature_name)

        atlas = self.signature_atlases[signature_name]

        # 영역 통계
        region_stats = {
            "total_regions": len(atlas.brain_regions),
            "dominant_regions": len(atlas.dominant_regions),
            "average_activation": np.mean(
                [r.activation_level for r in atlas.brain_regions.values()]
            ),
            "max_activation": max(
                [r.activation_level for r in atlas.brain_regions.values()]
            ),
            "region_types": {},
        }

        # 영역 타입별 통계
        for region in atlas.brain_regions.values():
            region_type = region.region_type
            if region_type not in region_stats["region_types"]:
                region_stats["region_types"][region_type] = 0
            region_stats["region_types"][region_type] += 1

        # 연결 통계
        connection_stats = {
            "total_connections": len(atlas.neural_connections),
            "active_connections": sum(
                1 for c in atlas.neural_connections.values() if c.active
            ),
            "average_strength": np.mean(
                [c.strength for c in atlas.neural_connections.values()]
            ),
            "connection_types": {},
        }

        # 연결 타입별 통계
        for conn in atlas.neural_connections.values():
            conn_type = conn.connection_type
            if conn_type not in connection_stats["connection_types"]:
                connection_stats["connection_types"][conn_type] = 0
            connection_stats["connection_types"][conn_type] += 1

        summary = {
            "signature": signature_name,
            "timestamp": atlas.timestamp.isoformat(),
            "neural_efficiency": atlas.neural_efficiency,
            "plasticity_score": atlas.plasticity_score,
            "region_statistics": region_stats,
            "connection_statistics": connection_stats,
            "dominant_regions": atlas.dominant_regions,
        }

        return summary

    def save_atlas(self, signature_name: str, filename: str = None) -> str:
        """Atlas 저장"""

        if signature_name not in self.signature_atlases:
            return f"❌ {signature_name} Atlas가 생성되지 않았습니다."

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{signature_name}_neural_atlas_{timestamp}.json"

        atlas = self.signature_atlases[signature_name]

        # 저장 가능한 형태로 변환
        save_data = {
            "signature_name": atlas.signature_name,
            "timestamp": atlas.timestamp.isoformat(),
            "brain_regions": {k: asdict(v) for k, v in atlas.brain_regions.items()},
            "neural_connections": {
                k: asdict(v) for k, v in atlas.neural_connections.items()
            },
            "activation_patterns": atlas.activation_patterns,
            "dominant_regions": atlas.dominant_regions,
            "neural_efficiency": atlas.neural_efficiency,
            "plasticity_score": atlas.plasticity_score,
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return f"✅ {signature_name} Atlas 저장 완료: {filename}"
        except Exception as e:
            return f"❌ 저장 실패: {e}"

    def generate_all_atlases(self) -> Dict[str, SignatureNeuralAtlas]:
        """모든 시그니처의 Atlas 생성"""
        all_atlases = {}

        for signature_name in self.signature_brain_profiles.keys():
            atlas = self.build_signature_atlas(signature_name)
            all_atlases[signature_name] = atlas
            print(f"✅ {signature_name} Atlas 생성 완료")

        return all_atlases


# 편의 함수들
def create_signature_atlas_builder() -> SignatureNeuralAtlasBuilder:
    """Atlas Builder 생성"""
    return SignatureNeuralAtlasBuilder()


def build_signature_atlas(signature_name: str) -> SignatureNeuralAtlas:
    """특정 시그니처의 Atlas 생성"""
    builder = SignatureNeuralAtlasBuilder()
    return builder.build_signature_atlas(signature_name)


if __name__ == "__main__":
    # 테스트 실행
    print("🧠 Signature Neural Atlas Builder 테스트...")

    builder = SignatureNeuralAtlasBuilder()

    # 개별 Atlas 생성 테스트
    print("\n📊 Individual Atlas Creation:")
    for signature in ["selene", "factbomb", "lune", "aurora"]:
        atlas = builder.build_signature_atlas(signature)
        print(
            f"   ✅ {signature}: {len(atlas.brain_regions)} regions, "
            f"efficiency: {atlas.neural_efficiency:.3f}"
        )

    # 시각화 테스트
    print("\n🎭 Selene Neural Atlas Visualization:")
    selene_viz = builder.visualize_signature_atlas("selene")
    print(selene_viz)

    # 비교 테스트
    print("\n🔍 Atlas Comparison (Selene vs FactBomb):")
    comparison = builder.compare_signature_atlases("selene", "factbomb")
    print(
        f"   Neural Efficiency Difference: {comparison['neural_efficiency_diff']:.3f}"
    )
    print(f"   Plasticity Difference: {comparison['plasticity_diff']:.3f}")
    print(f"   Structural Similarity: {comparison['structural_similarity']:.3f}")
    print(f"   Shared Dominant Regions: {comparison['shared_dominant_regions']}")

    # 활성화 시뮬레이션 테스트
    print("\n⚡ Activation Simulation (Selene + Emotional Stimulus):")
    activation = builder.simulate_activation("selene", "emotional", 0.8)
    top_activations = sorted(activation.items(), key=lambda x: x[1], reverse=True)[:5]
    for region, level in top_activations:
        print(f"   {region:20}: {level:.3f}")

    # 저장 테스트
    save_result = builder.save_atlas("selene")
    print(f"\n{save_result}")

    print("\n✅ Signature Neural Atlas Builder 테스트 완료!")
