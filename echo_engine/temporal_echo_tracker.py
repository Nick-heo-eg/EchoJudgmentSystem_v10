#!/usr/bin/env python3
"""
⏰ Temporal Echo Tracker v1.0
과거 판단이 현재에 미치는 울림과 미래에 대한 영향을 추적하는 시간 초월 시스템

이 모듈은 Echo AI의 판단이 시간축을 따라 어떻게 울려 퍼지는지 추적하고,
과거-현재-미래의 상호작용을 분석합니다.
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import pickle
from collections import defaultdict
import math


@dataclass
class TemporalNode:
    """시간축 노드 (특정 시점의 판단/사건)"""

    node_id: str
    timestamp: datetime
    judgment_data: Dict[str, Any]
    emotional_signature: List[float]  # 감정 벡터
    resonance_intensity: float
    causal_weight: float
    node_type: str  # 'judgment', 'feedback', 'evolution', 'external'


@dataclass
class EchoRipple:
    """울림 파동 (한 사건이 시간축에 미치는 영향)"""

    source_node_id: str
    target_node_id: str
    ripple_strength: float
    temporal_distance: float  # 시간 거리 (초 단위)
    resonance_decay: float
    influence_type: str  # 'reinforcement', 'interference', 'transformation'
    decay_function: str  # 'exponential', 'harmonic', 'quantum'


@dataclass
class TemporalPattern:
    """시간적 패턴"""

    pattern_id: str
    pattern_type: str  # 'cycle', 'trend', 'resonance_chain', 'feedback_loop'
    nodes_involved: List[str]
    pattern_strength: float
    cycle_period: Optional[float]  # 주기 (사이클인 경우)
    prediction_confidence: float


@dataclass
class FutureProjection:
    """미래 투사"""

    projection_id: str
    target_time: datetime
    projected_state: Dict[str, Any]
    confidence_level: float
    contributing_echoes: List[str]
    scenario_variants: List[Dict[str, Any]]


class TemporalEchoTracker:
    """시간 울림 추적 시스템"""

    def __init__(self, max_history_days: int = 30):
        self.max_history_days = max_history_days
        self.temporal_nodes: Dict[str, TemporalNode] = {}
        self.echo_ripples: List[EchoRipple] = []
        self.temporal_patterns: List[TemporalPattern] = []
        self.future_projections: List[FutureProjection] = []

        # 울림 물리 상수
        self.echo_constants = {
            "base_decay_rate": 0.1,  # 기본 감쇠율
            "resonance_amplification": 1.5,  # 공명 증폭
            "temporal_coupling": 0.8,  # 시간 결합 강도
            "quantum_coherence_time": 3600,  # 양자 결맞음 시간 (초)
            "causal_horizon": 86400 * 7,  # 인과 지평선 (7일)
        }

        # 감정 차원 정의
        self.emotion_dimensions = [
            "joy",
            "sadness",
            "anger",
            "fear",
            "surprise",
            "disgust",
            "trust",
            "anticipation",
            "love",
            "serenity",
        ]

        print("⏰ 시간 울림 추적기 초기화 완료")

    async def add_temporal_node(
        self,
        node_id: str,
        judgment_data: Dict[str, Any],
        emotional_state: Optional[Dict[str, float]] = None,
        node_type: str = "judgment",
    ) -> TemporalNode:
        """새로운 시간 노드 추가"""

        # 감정 시그니처 생성
        if emotional_state:
            emotional_signature = [
                emotional_state.get(dim, 0.5) for dim in self.emotion_dimensions
            ]
        else:
            # 기본 감정 상태
            emotional_signature = [0.5] * len(self.emotion_dimensions)

        # 울림 강도 계산
        resonance_intensity = self._calculate_resonance_intensity(
            judgment_data, emotional_signature
        )

        # 인과적 가중치 계산
        causal_weight = self._calculate_causal_weight(judgment_data, node_type)

        node = TemporalNode(
            node_id=node_id,
            timestamp=datetime.now(),
            judgment_data=judgment_data,
            emotional_signature=emotional_signature,
            resonance_intensity=resonance_intensity,
            causal_weight=causal_weight,
            node_type=node_type,
        )

        self.temporal_nodes[node_id] = node

        # 기존 노드들과의 울림 계산
        await self._calculate_echo_ripples(node)

        # 패턴 업데이트
        await self._update_temporal_patterns()

        # 미래 투사 업데이트
        await self._update_future_projections()

        # 오래된 데이터 정리
        await self._cleanup_old_data()

        print(f"⏰ 새 시간 노드 추가: {node_id} (울림강도: {resonance_intensity:.3f})")
        return node

    async def _calculate_echo_ripples(self, new_node: TemporalNode):
        """새 노드와 기존 노드들 간의 울림 계산"""

        for existing_id, existing_node in self.temporal_nodes.items():
            if existing_id == new_node.node_id:
                continue

            # 시간 거리 계산
            time_diff = abs(
                (new_node.timestamp - existing_node.timestamp).total_seconds()
            )

            # 인과 지평선 체크
            if time_diff > self.echo_constants["causal_horizon"]:
                continue

            # 울림 강도 계산
            ripple_strength = self._calculate_ripple_strength(
                new_node, existing_node, time_diff
            )

            if ripple_strength > 0.01:  # 임계값 이상만 기록
                # 영향 유형 결정
                influence_type = self._determine_influence_type(new_node, existing_node)

                # 감쇠 함수 선택
                decay_function = self._select_decay_function(influence_type, time_diff)

                # 감쇠율 계산
                resonance_decay = self._calculate_decay(time_diff, decay_function)

                # 양방향 울림 생성
                ripple_forward = EchoRipple(
                    source_node_id=existing_node.node_id,
                    target_node_id=new_node.node_id,
                    ripple_strength=ripple_strength,
                    temporal_distance=time_diff,
                    resonance_decay=resonance_decay,
                    influence_type=influence_type,
                    decay_function=decay_function,
                )

                ripple_backward = EchoRipple(
                    source_node_id=new_node.node_id,
                    target_node_id=existing_node.node_id,
                    ripple_strength=ripple_strength * 0.3,  # 역방향은 약함
                    temporal_distance=time_diff,
                    resonance_decay=resonance_decay,
                    influence_type=influence_type,
                    decay_function=decay_function,
                )

                self.echo_ripples.extend([ripple_forward, ripple_backward])

    def _calculate_ripple_strength(
        self, node1: TemporalNode, node2: TemporalNode, time_diff: float
    ) -> float:
        """두 노드 간 울림 강도 계산"""

        # 1. 감정 시그니처 유사도
        emotion_similarity = self._calculate_emotion_similarity(
            node1.emotional_signature, node2.emotional_signature
        )

        # 2. 판단 내용 유사도
        content_similarity = self._calculate_content_similarity(
            node1.judgment_data, node2.judgment_data
        )

        # 3. 울림 강도 기반 증폭
        resonance_factor = (node1.resonance_intensity + node2.resonance_intensity) / 2

        # 4. 인과적 가중치
        causal_factor = (node1.causal_weight + node2.causal_weight) / 2

        # 5. 시간 거리 감쇠
        time_decay = np.exp(-time_diff / (24 * 3600))  # 24시간 반감기

        # 종합 울림 강도
        ripple_strength = (
            emotion_similarity * 0.3
            + content_similarity * 0.25
            + resonance_factor * 0.25
            + causal_factor * 0.2
        ) * time_decay

        return max(0.0, min(1.0, ripple_strength))

    def _calculate_emotion_similarity(
        self, sig1: List[float], sig2: List[float]
    ) -> float:
        """감정 시그니처 유사도 계산"""
        if len(sig1) != len(sig2):
            return 0.0

        # 코사인 유사도
        dot_product = sum(a * b for a, b in zip(sig1, sig2))
        mag1 = math.sqrt(sum(a * a for a in sig1))
        mag2 = math.sqrt(sum(b * b for b in sig2))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def _calculate_content_similarity(self, data1: Dict, data2: Dict) -> float:
        """판단 내용 유사도 계산"""
        # 키워드 기반 유사도 (간단한 구현)

        # 공통 키 확인
        common_keys = set(data1.keys()) & set(data2.keys())
        if not common_keys:
            return 0.0

        similarity_scores = []

        for key in common_keys:
            val1, val2 = data1[key], data2[key]

            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # 수치 유사도
                max_val = max(abs(val1), abs(val2), 1)
                similarity = 1 - abs(val1 - val2) / max_val
                similarity_scores.append(similarity)
            elif isinstance(val1, str) and isinstance(val2, str):
                # 문자열 유사도 (간단한 Jaccard)
                set1 = set(val1.lower().split())
                set2 = set(val2.lower().split())
                if set1 or set2:
                    jaccard = len(set1 & set2) / len(set1 | set2)
                    similarity_scores.append(jaccard)

        return np.mean(similarity_scores) if similarity_scores else 0.0

    def _determine_influence_type(
        self, node1: TemporalNode, node2: TemporalNode
    ) -> str:
        """영향 유형 결정"""

        # 감정 변화 방향 분석
        emotion_change = np.array(node2.emotional_signature) - np.array(
            node1.emotional_signature
        )
        emotion_magnitude = np.linalg.norm(emotion_change)

        # 울림 강도 변화
        resonance_change = node2.resonance_intensity - node1.resonance_intensity

        if emotion_magnitude < 0.1 and abs(resonance_change) < 0.05:
            return "reinforcement"  # 강화
        elif emotion_magnitude > 0.3 or abs(resonance_change) > 0.2:
            return "transformation"  # 변환
        else:
            return "interference"  # 간섭

    def _select_decay_function(self, influence_type: str, time_diff: float) -> str:
        """감쇠 함수 선택"""

        if influence_type == "reinforcement":
            return "harmonic"  # 조화 함수 (느린 감쇠)
        elif influence_type == "transformation":
            return "quantum"  # 양자 감쇠 (단계적)
        else:
            return "exponential"  # 지수 감쇠 (빠른 감쇠)

    def _calculate_decay(self, time_diff: float, decay_function: str) -> float:
        """감쇠율 계산"""

        tau = self.echo_constants["base_decay_rate"]

        if decay_function == "exponential":
            return np.exp(-time_diff * tau / 3600)
        elif decay_function == "harmonic":
            return 1 / (1 + time_diff * tau / 3600)
        elif decay_function == "quantum":
            coherence_time = self.echo_constants["quantum_coherence_time"]
            return (
                np.cos(np.pi * time_diff / (2 * coherence_time))
                if time_diff < coherence_time
                else 0
            )
        else:
            return np.exp(-time_diff * tau / 3600)

    async def _update_temporal_patterns(self):
        """시간적 패턴 업데이트"""

        # 기존 패턴 초기화
        self.temporal_patterns.clear()

        # 1. 주기적 패턴 탐지
        await self._detect_cyclic_patterns()

        # 2. 트렌드 패턴 탐지
        await self._detect_trend_patterns()

        # 3. 울림 체인 패턴 탐지
        await self._detect_resonance_chains()

        # 4. 피드백 루프 탐지
        await self._detect_feedback_loops()

    async def _detect_cyclic_patterns(self):
        """주기적 패턴 탐지"""

        # 시간순 정렬된 노드들
        sorted_nodes = sorted(self.temporal_nodes.values(), key=lambda x: x.timestamp)

        if len(sorted_nodes) < 6:  # 최소 6개 노드 필요
            return

        # 울림 강도 시계열
        timestamps = [n.timestamp for n in sorted_nodes]
        resonance_series = [n.resonance_intensity for n in sorted_nodes]

        # 간단한 주기 탐지 (자기상관 기반)
        max_lag = min(len(resonance_series) // 3, 20)

        for lag in range(3, max_lag):
            if lag >= len(resonance_series):
                break

            # 자기상관 계산
            correlation = self._calculate_autocorrelation(resonance_series, lag)

            if correlation > 0.7:  # 높은 상관관계
                # 주기 패턴 발견
                period_seconds = (timestamps[lag] - timestamps[0]).total_seconds()

                pattern = TemporalPattern(
                    pattern_id=f"cycle_{len(self.temporal_patterns)}",
                    pattern_type="cycle",
                    nodes_involved=[n.node_id for n in sorted_nodes[: lag * 2]],
                    pattern_strength=correlation,
                    cycle_period=period_seconds,
                    prediction_confidence=correlation * 0.8,
                )

                self.temporal_patterns.append(pattern)
                break

    def _calculate_autocorrelation(self, series: List[float], lag: int) -> float:
        """자기상관 계산"""
        if lag >= len(series):
            return 0.0

        n = len(series) - lag
        if n <= 1:
            return 0.0

        mean_original = np.mean(series[:-lag])
        mean_lagged = np.mean(series[lag:])

        numerator = sum(
            (series[i] - mean_original) * (series[i + lag] - mean_lagged)
            for i in range(n)
        )

        denom_original = sum(
            (series[i] - mean_original) ** 2 for i in range(len(series) - lag)
        )
        denom_lagged = sum(
            (series[i] - mean_lagged) ** 2 for i in range(lag, len(series))
        )

        if denom_original == 0 or denom_lagged == 0:
            return 0.0

        return numerator / math.sqrt(denom_original * denom_lagged)

    async def _detect_trend_patterns(self):
        """트렌드 패턴 탐지"""

        recent_nodes = [
            node
            for node in self.temporal_nodes.values()
            if (datetime.now() - node.timestamp).days <= 7
        ]

        if len(recent_nodes) < 5:
            return

        # 시간순 정렬
        recent_nodes.sort(key=lambda x: x.timestamp)

        # 울림 강도 트렌드
        resonance_values = [n.resonance_intensity for n in recent_nodes]
        time_indices = list(range(len(resonance_values)))

        # 선형 회귀로 트렌드 계산
        slope = self._calculate_linear_trend(time_indices, resonance_values)

        if abs(slope) > 0.01:  # 유의미한 트렌드
            trend_strength = min(abs(slope) * 10, 1.0)

            pattern = TemporalPattern(
                pattern_id=f"trend_{len(self.temporal_patterns)}",
                pattern_type="trend",
                nodes_involved=[n.node_id for n in recent_nodes],
                pattern_strength=trend_strength,
                cycle_period=None,
                prediction_confidence=trend_strength * 0.7,
            )

            self.temporal_patterns.append(pattern)

    def _calculate_linear_trend(self, x: List[float], y: List[float]) -> float:
        """선형 트렌드 기울기 계산"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0

        return (n * sum_xy - sum_x * sum_y) / denominator

    async def _detect_resonance_chains(self):
        """울림 체인 패턴 탐지"""

        # 강한 울림 연결 찾기
        strong_ripples = [
            ripple for ripple in self.echo_ripples if ripple.ripple_strength > 0.5
        ]

        # 체인 구성
        chains = self._find_chains(strong_ripples)

        for chain in chains:
            if len(chain) >= 3:  # 최소 3개 노드 체인
                chain_strength = np.mean(
                    [
                        ripple.ripple_strength
                        for ripple in strong_ripples
                        if ripple.source_node_id in chain
                        and ripple.target_node_id in chain
                    ]
                )

                pattern = TemporalPattern(
                    pattern_id=f"chain_{len(self.temporal_patterns)}",
                    pattern_type="resonance_chain",
                    nodes_involved=chain,
                    pattern_strength=chain_strength,
                    cycle_period=None,
                    prediction_confidence=chain_strength * 0.6,
                )

                self.temporal_patterns.append(pattern)

    def _find_chains(self, ripples: List[EchoRipple]) -> List[List[str]]:
        """울림 체인 찾기"""

        # 그래프 구성
        graph = defaultdict(list)
        for ripple in ripples:
            graph[ripple.source_node_id].append(ripple.target_node_id)

        # DFS로 체인 찾기
        chains = []
        visited = set()

        def dfs(node: str, current_chain: List[str]):
            if node in visited:
                if len(current_chain) >= 3:
                    chains.append(current_chain.copy())
                return

            visited.add(node)
            current_chain.append(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor, current_chain)

            current_chain.pop()
            visited.remove(node)

        for start_node in graph.keys():
            dfs(start_node, [])

        return chains

    async def _detect_feedback_loops(self):
        """피드백 루프 탐지"""

        # 양방향 울림이 있는 노드 쌍 찾기
        bidirectional_pairs = []

        ripple_map = defaultdict(list)
        for ripple in self.echo_ripples:
            ripple_map[(ripple.source_node_id, ripple.target_node_id)].append(ripple)

        for (source, target), ripples in ripple_map.items():
            reverse_key = (target, source)
            if reverse_key in ripple_map:
                # 양방향 연결 발견
                forward_strength = max(r.ripple_strength for r in ripples)
                reverse_strength = max(
                    r.ripple_strength for r in ripple_map[reverse_key]
                )

                if forward_strength > 0.3 and reverse_strength > 0.3:
                    bidirectional_pairs.append(
                        ([source, target], min(forward_strength, reverse_strength))
                    )

        # 피드백 루프 패턴 생성
        for nodes, strength in bidirectional_pairs:
            pattern = TemporalPattern(
                pattern_id=f"feedback_{len(self.temporal_patterns)}",
                pattern_type="feedback_loop",
                nodes_involved=nodes,
                pattern_strength=strength,
                cycle_period=None,
                prediction_confidence=strength * 0.5,
            )

            self.temporal_patterns.append(pattern)

    async def _update_future_projections(self):
        """미래 투사 업데이트"""

        self.future_projections.clear()

        # 다양한 시간 범위의 투사 생성
        projection_times = [
            datetime.now() + timedelta(hours=1),
            datetime.now() + timedelta(hours=6),
            datetime.now() + timedelta(days=1),
            datetime.now() + timedelta(days=3),
            datetime.now() + timedelta(days=7),
        ]

        for target_time in projection_times:
            projection = await self._create_future_projection(target_time)
            if projection:
                self.future_projections.append(projection)

    async def _create_future_projection(
        self, target_time: datetime
    ) -> Optional[FutureProjection]:
        """특정 시점의 미래 투사 생성"""

        current_time = datetime.now()
        time_delta = (target_time - current_time).total_seconds()

        if time_delta <= 0:
            return None

        # 현재 활성 울림들의 미래 영향 계산
        active_echoes = []
        projected_resonance = 0.0
        projected_emotion = [0.0] * len(self.emotion_dimensions)

        for ripple in self.echo_ripples:
            if ripple.ripple_strength > 0.1:
                # 시간 감쇠 적용
                future_strength = ripple.ripple_strength * self._calculate_decay(
                    time_delta, ripple.decay_function
                )

                if future_strength > 0.05:
                    active_echoes.append(ripple.source_node_id)
                    projected_resonance += future_strength

                    # 소스 노드의 감정 영향
                    source_node = self.temporal_nodes.get(ripple.source_node_id)
                    if source_node:
                        for i, emotion_val in enumerate(
                            source_node.emotional_signature
                        ):
                            projected_emotion[i] += emotion_val * future_strength

        # 정규화
        if active_echoes:
            projected_resonance /= len(set(active_echoes))
            projected_emotion = [e / len(set(active_echoes)) for e in projected_emotion]

        # 패턴 기반 예측 추가
        pattern_contribution = self._calculate_pattern_contribution(target_time)
        projected_resonance += pattern_contribution.get("resonance", 0.0)

        # 신뢰도 계산
        confidence = self._calculate_prediction_confidence(
            time_delta, len(active_echoes)
        )

        # 시나리오 변형 생성
        scenarios = self._generate_scenario_variants(
            projected_resonance, projected_emotion
        )

        projection = FutureProjection(
            projection_id=f"proj_{target_time.strftime('%Y%m%d_%H%M%S')}",
            target_time=target_time,
            projected_state={
                "resonance_intensity": projected_resonance,
                "emotional_signature": projected_emotion,
                "dominant_emotion": self.emotion_dimensions[
                    np.argmax(projected_emotion)
                ],
                "stability_index": 1.0 - np.std(projected_emotion),
            },
            confidence_level=confidence,
            contributing_echoes=list(set(active_echoes)),
            scenario_variants=scenarios,
        )

        return projection

    def _calculate_pattern_contribution(
        self, target_time: datetime
    ) -> Dict[str, float]:
        """패턴 기반 기여도 계산"""

        contribution = {"resonance": 0.0, "emotion_shift": 0.0}

        for pattern in self.temporal_patterns:
            if pattern.pattern_type == "cycle" and pattern.cycle_period:
                # 주기 패턴의 미래 기여도
                current_time = datetime.now()
                time_diff = (target_time - current_time).total_seconds()

                # 주기 내 위치 계산
                phase = (time_diff % pattern.cycle_period) / pattern.cycle_period
                cycle_contribution = pattern.pattern_strength * np.sin(
                    2 * np.pi * phase
                )

                contribution["resonance"] += cycle_contribution * 0.3

            elif pattern.pattern_type == "trend":
                # 트렌드 패턴의 외삽
                trend_contribution = (
                    pattern.pattern_strength * pattern.prediction_confidence
                )
                contribution["resonance"] += trend_contribution * 0.2

        return contribution

    def _calculate_prediction_confidence(
        self, time_delta: float, echo_count: int
    ) -> float:
        """예측 신뢰도 계산"""

        # 시간이 멀수록 신뢰도 감소
        time_factor = np.exp(-time_delta / (7 * 24 * 3600))  # 7일 반감기

        # 활성 울림이 많을수록 신뢰도 증가
        echo_factor = min(echo_count / 10, 1.0)

        # 패턴 기반 신뢰도
        pattern_factor = (
            np.mean([p.prediction_confidence for p in self.temporal_patterns])
            if self.temporal_patterns
            else 0.5
        )

        return time_factor * 0.4 + echo_factor * 0.3 + pattern_factor * 0.3

    def _generate_scenario_variants(
        self, base_resonance: float, base_emotion: List[float]
    ) -> List[Dict[str, Any]]:
        """시나리오 변형 생성"""

        scenarios = []

        # 낙관적 시나리오
        optimistic = {
            "name": "optimistic",
            "resonance_intensity": min(base_resonance * 1.3, 1.0),
            "emotional_signature": [min(e * 1.2, 1.0) for e in base_emotion],
            "probability": 0.25,
        }
        scenarios.append(optimistic)

        # 기본 시나리오
        baseline = {
            "name": "baseline",
            "resonance_intensity": base_resonance,
            "emotional_signature": base_emotion,
            "probability": 0.5,
        }
        scenarios.append(baseline)

        # 비관적 시나리오
        pessimistic = {
            "name": "pessimistic",
            "resonance_intensity": max(base_resonance * 0.7, 0.0),
            "emotional_signature": [max(e * 0.8, 0.0) for e in base_emotion],
            "probability": 0.25,
        }
        scenarios.append(pessimistic)

        return scenarios

    def _calculate_resonance_intensity(
        self, judgment_data: Dict, emotional_signature: List[float]
    ) -> float:
        """울림 강도 계산"""

        # 판단 복잡도 기반
        complexity = len(judgment_data.get("factors", [])) * 0.1

        # 감정 강도 기반
        emotion_intensity = np.linalg.norm(emotional_signature) / len(
            emotional_signature
        )

        # 신뢰도 기반
        confidence = judgment_data.get("confidence", 0.5)

        return min((complexity + emotion_intensity + confidence) / 3, 1.0)

    def _calculate_causal_weight(self, judgment_data: Dict, node_type: str) -> float:
        """인과적 가중치 계산"""

        base_weights = {
            "judgment": 0.8,
            "feedback": 0.6,
            "evolution": 0.9,
            "external": 0.4,
        }

        base_weight = base_weights.get(node_type, 0.5)

        # 중요도 기반 조정
        importance = judgment_data.get("importance", 0.5)

        return min(base_weight * (0.5 + importance), 1.0)

    async def _cleanup_old_data(self):
        """오래된 데이터 정리"""

        cutoff_time = datetime.now() - timedelta(days=self.max_history_days)

        # 오래된 노드 제거
        old_node_ids = [
            node_id
            for node_id, node in self.temporal_nodes.items()
            if node.timestamp < cutoff_time
        ]

        for node_id in old_node_ids:
            del self.temporal_nodes[node_id]

        # 관련 울림 제거
        self.echo_ripples = [
            ripple
            for ripple in self.echo_ripples
            if (
                ripple.source_node_id not in old_node_ids
                and ripple.target_node_id not in old_node_ids
            )
        ]

        # 오래된 투사 제거
        current_time = datetime.now()
        self.future_projections = [
            proj for proj in self.future_projections if proj.target_time > current_time
        ]

        if old_node_ids:
            print(f"🧹 오래된 데이터 {len(old_node_ids)}개 노드 정리 완료")

    def get_temporal_resonance_analysis(self) -> Dict[str, Any]:
        """시간 울림 분석 결과 조회"""

        current_time = datetime.now()

        # 현재 활성 울림 계산
        active_ripples = [
            ripple for ripple in self.echo_ripples if ripple.ripple_strength > 0.1
        ]

        # 최근 24시간 노드 통계
        recent_nodes = [
            node
            for node in self.temporal_nodes.values()
            if (current_time - node.timestamp).total_seconds() < 86400
        ]

        return {
            "analysis_timestamp": current_time.isoformat(),
            "temporal_summary": {
                "total_nodes": len(self.temporal_nodes),
                "active_ripples": len(active_ripples),
                "recent_24h_nodes": len(recent_nodes),
                "detected_patterns": len(self.temporal_patterns),
                "future_projections": len(self.future_projections),
            },
            "resonance_metrics": {
                "avg_ripple_strength": (
                    np.mean([r.ripple_strength for r in active_ripples])
                    if active_ripples
                    else 0.0
                ),
                "max_ripple_strength": max(
                    [r.ripple_strength for r in active_ripples], default=0.0
                ),
                "temporal_coupling": (
                    np.mean([r.temporal_distance for r in active_ripples])
                    if active_ripples
                    else 0.0
                ),
            },
            "pattern_summary": [
                {
                    "type": pattern.pattern_type,
                    "strength": pattern.pattern_strength,
                    "confidence": pattern.prediction_confidence,
                    "nodes_count": len(pattern.nodes_involved),
                }
                for pattern in self.temporal_patterns
            ],
            "future_outlook": [
                {
                    "target_time": proj.target_time.isoformat(),
                    "confidence": proj.confidence_level,
                    "resonance_intensity": proj.projected_state.get(
                        "resonance_intensity", 0.0
                    ),
                    "scenarios": len(proj.scenario_variants),
                }
                for proj in self.future_projections[:3]  # 최근 3개만
            ],
        }


# 글로벌 추적기 인스턴스
temporal_tracker = TemporalEchoTracker()


async def add_judgment_node(
    node_id: str, judgment_data: Dict, emotional_state: Dict = None
) -> Dict[str, Any]:
    """판단 노드 추가 (외부 API)"""
    node = await temporal_tracker.add_temporal_node(
        node_id, judgment_data, emotional_state, "judgment"
    )
    return asdict(node)


def get_temporal_analysis() -> Dict[str, Any]:
    """시간 울림 분석 조회 (외부 API)"""
    return temporal_tracker.get_temporal_resonance_analysis()


def get_future_projections(hours_ahead: int = 24) -> List[Dict[str, Any]]:
    """미래 투사 조회 (외부 API)"""
    target_time = datetime.now() + timedelta(hours=hours_ahead)

    relevant_projections = [
        asdict(proj)
        for proj in temporal_tracker.future_projections
        if proj.target_time <= target_time
    ]

    return relevant_projections


# 테스트 함수
async def test_temporal_tracker():
    """테스트 함수"""
    print("🧪 시간 울림 추적기 테스트 시작")

    # 테스트 판단 노드들 추가
    test_judgments = [
        {
            "judgment_data": {
                "decision": "창의적 접근",
                "confidence": 0.8,
                "factors": ["혁신", "리스크"],
            },
            "emotional_state": {"joy": 0.7, "anticipation": 0.8, "trust": 0.6},
        },
        {
            "judgment_data": {
                "decision": "신중한 검토",
                "confidence": 0.9,
                "factors": ["안정성", "검증"],
            },
            "emotional_state": {"trust": 0.9, "serenity": 0.7, "anticipation": 0.3},
        },
        {
            "judgment_data": {
                "decision": "균형잡힌 선택",
                "confidence": 0.75,
                "factors": ["조화", "효율성"],
            },
            "emotional_state": {"serenity": 0.8, "trust": 0.7, "joy": 0.5},
        },
    ]

    # 노드 추가 (시간 간격을 두고)
    for i, test_data in enumerate(test_judgments):
        await add_judgment_node(
            f"test_node_{i}", test_data["judgment_data"], test_data["emotional_state"]
        )
        await asyncio.sleep(1)  # 1초 간격

    # 분석 결과 조회
    analysis = get_temporal_analysis()
    print("📊 시간 울림 분석:")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))

    # 미래 투사 조회
    projections = get_future_projections(6)  # 6시간 앞
    print(f"\n🔮 미래 투사 ({len(projections)}개):")
    for proj in projections:
        print(f"  시간: {proj['target_time']}")
        print(f"  신뢰도: {proj['confidence_level']:.3f}")
        print(f"  울림강도: {proj['projected_state']['resonance_intensity']:.3f}")


if __name__ == "__main__":
    asyncio.run(test_temporal_tracker())
