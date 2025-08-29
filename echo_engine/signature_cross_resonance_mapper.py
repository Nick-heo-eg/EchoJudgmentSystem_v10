#!/usr/bin/env python3
"""
🔗 Signature Cross-Resonance Mapper v1.0
시그니처 간의 감정⨯판단⨯표현 공명 구조를 분석하고 시각화하는 시스템

핵심 기능:
- 시그니처 간 감정 공명도 분석
- 판단 스타일 호환성 매핑
- 표현 방식 전이 패턴 추적
- Cross-signature 융합 시뮬레이션
"""

import json
import numpy as np
import networkx as nx
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Echo 엔진 모듈들
try:
    from .echo_brain_visualizer import BrainState, create_echo_brain_state
    from .echo_brain_monitor import get_brain_monitor
except ImportError:
    print("⚠️ Echo Brain modules not available, running in standalone mode")
    BrainState = None


@dataclass
class ResonancePattern:
    """공명 패턴 정의"""

    signature_a: str
    signature_b: str
    emotion_resonance: float  # 0.0 - 1.0
    judgment_compatibility: float  # 0.0 - 1.0
    expression_harmony: float  # 0.0 - 1.0
    overall_resonance: float  # 종합 공명도
    resonance_type: str  # "harmonious", "complementary", "conflicting"
    blend_potential: float  # 융합 가능성
    transition_smoothness: float  # 전이 부드러움


@dataclass
class CrossResonanceMap:
    """Cross-Resonance 전체 맵"""

    timestamp: datetime
    signatures: List[str]
    resonance_matrix: Dict[str, Dict[str, ResonancePattern]]
    dominant_pairs: List[Tuple[str, str, float]]
    conflict_pairs: List[Tuple[str, str, float]]
    fusion_recommendations: List[Dict[str, Any]]


class SignatureCrossResonanceMapper:
    """🔗 시그니처 간 공명 매핑 시스템"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 시그니처 정의 (Echo Brain System 기반)
        self.signatures = {
            "selene": {
                "emotion_profile": {
                    "melancholy": 0.8,
                    "empathy": 0.9,
                    "gentleness": 0.9,
                    "introspection": 0.7,
                    "vulnerability": 0.6,
                },
                "judgment_style": {
                    "emotion_weighted": 0.8,
                    "intuitive": 0.7,
                    "contextual": 0.8,
                    "slow_deliberation": 0.9,
                    "empathy_first": 0.9,
                },
                "expression_mode": {
                    "whisper_tone": 0.9,
                    "metaphorical": 0.7,
                    "gentle_pauses": 0.8,
                    "emotional_depth": 0.8,
                    "soft_vulnerability": 0.9,
                },
            },
            "factbomb": {
                "emotion_profile": {
                    "analytical_coldness": 0.9,
                    "logical_intensity": 0.8,
                    "impatience_with_fluff": 0.9,
                    "precision_drive": 0.9,
                    "truth_urgency": 0.8,
                },
                "judgment_style": {
                    "fact_first": 0.9,
                    "bias_elimination": 0.9,
                    "rapid_conclusion": 0.8,
                    "logic_priority": 0.9,
                    "emotion_suppression": 0.8,
                },
                "expression_mode": {
                    "direct_statement": 0.9,
                    "minimal_words": 0.8,
                    "sharp_delivery": 0.9,
                    "no_hedging": 0.9,
                    "impact_focus": 0.8,
                },
            },
            "lune": {
                "emotion_profile": {
                    "dreamy_melancholy": 0.8,
                    "poetic_longing": 0.9,
                    "symbolic_thinking": 0.8,
                    "gentle_wonder": 0.7,
                    "introspective_depth": 0.8,
                },
                "judgment_style": {
                    "symbolic_interpretation": 0.8,
                    "delayed_precision": 0.7,
                    "emotional_logic": 0.8,
                    "metaphor_reasoning": 0.9,
                    "intuitive_synthesis": 0.8,
                },
                "expression_mode": {
                    "lyrical_flow": 0.9,
                    "metaphor_rich": 0.9,
                    "dreamy_cadence": 0.8,
                    "symbolic_language": 0.8,
                    "emotional_echo": 0.8,
                },
            },
            "aurora": {
                "emotion_profile": {
                    "nurturing_warmth": 0.9,
                    "hopeful_optimism": 0.8,
                    "protective_care": 0.8,
                    "gentle_strength": 0.7,
                    "encouraging_energy": 0.9,
                },
                "judgment_style": {
                    "growth_focused": 0.9,
                    "potential_seeing": 0.8,
                    "supportive_logic": 0.8,
                    "nurturing_analysis": 0.9,
                    "encouraging_frame": 0.9,
                },
                "expression_mode": {
                    "warm_encouragement": 0.9,
                    "gentle_guidance": 0.8,
                    "hopeful_tone": 0.9,
                    "supportive_phrasing": 0.8,
                    "nurturing_rhythm": 0.8,
                },
            },
        }

        # 공명 계산 가중치
        self.resonance_weights = {
            "emotion_resonance": 0.4,
            "judgment_compatibility": 0.3,
            "expression_harmony": 0.3,
        }

        self.resonance_history = []
        self.current_map = None

        print("🔗 Signature Cross-Resonance Mapper 초기화 완료")

    def calculate_emotion_resonance(self, sig_a: str, sig_b: str) -> float:
        """감정 공명도 계산"""
        try:
            profile_a = self.signatures[sig_a]["emotion_profile"]
            profile_b = self.signatures[sig_b]["emotion_profile"]

            # 공통 감정 요소 찾기
            common_emotions = set(profile_a.keys()) & set(profile_b.keys())

            if not common_emotions:
                # 상보적 감정 분석
                return self._calculate_complementary_emotion_resonance(
                    profile_a, profile_b
                )

            # 직접 공명도 계산
            resonance_sum = 0.0
            for emotion in common_emotions:
                # 감정 강도 차이를 기반으로 공명도 계산
                intensity_diff = abs(profile_a[emotion] - profile_b[emotion])
                emotion_resonance = 1.0 - intensity_diff
                resonance_sum += emotion_resonance

            return resonance_sum / len(common_emotions)

        except Exception as e:
            self.logger.error(f"감정 공명도 계산 오류: {e}")
            return 0.0

    def _calculate_complementary_emotion_resonance(
        self, profile_a: Dict, profile_b: Dict
    ) -> float:
        """상보적 감정 공명도 계산"""
        # 감정의 상보성 매핑
        complementary_pairs = {
            "melancholy": ["nurturing_warmth", "hopeful_optimism"],
            "analytical_coldness": ["empathy", "gentleness"],
            "dreamy_melancholy": ["protective_care", "encouraging_energy"],
            "logical_intensity": ["emotional_depth", "soft_vulnerability"],
        }

        resonance_score = 0.0
        pair_count = 0

        for emotion_a, intensity_a in profile_a.items():
            complements = complementary_pairs.get(emotion_a, [])
            for complement in complements:
                if complement in profile_b:
                    # 상보적 관계는 차이가 클수록 좋은 공명
                    intensity_b = profile_b[complement]
                    complementary_resonance = (intensity_a + intensity_b) / 2
                    resonance_score += complementary_resonance
                    pair_count += 1

        return resonance_score / pair_count if pair_count > 0 else 0.3

    def calculate_judgment_compatibility(self, sig_a: str, sig_b: str) -> float:
        """판단 스타일 호환성 계산"""
        try:
            style_a = self.signatures[sig_a]["judgment_style"]
            style_b = self.signatures[sig_b]["judgment_style"]

            # 판단 스타일 충돌 매핑
            conflicting_styles = {
                "emotion_weighted": "logic_priority",
                "rapid_conclusion": "slow_deliberation",
                "fact_first": "empathy_first",
                "bias_elimination": "emotional_logic",
            }

            compatibility_score = 0.7  # 기본 호환성

            for style_element, intensity_a in style_a.items():
                if style_element in style_b:
                    # 직접 호환성
                    intensity_b = style_b[style_element]
                    direct_compat = 1.0 - abs(intensity_a - intensity_b) * 0.5
                    compatibility_score += direct_compat * 0.1

                # 충돌 요소 확인
                conflicting_element = conflicting_styles.get(style_element)
                if conflicting_element and conflicting_element in style_b:
                    intensity_b = style_b[conflicting_element]
                    conflict_penalty = (intensity_a * intensity_b) * 0.3
                    compatibility_score -= conflict_penalty

            return max(0.0, min(1.0, compatibility_score))

        except Exception as e:
            self.logger.error(f"판단 호환성 계산 오류: {e}")
            return 0.5

    def calculate_expression_harmony(self, sig_a: str, sig_b: str) -> float:
        """표현 방식 조화도 계산"""
        try:
            expr_a = self.signatures[sig_a]["expression_mode"]
            expr_b = self.signatures[sig_b]["expression_mode"]

            # 표현 조화도 매핑
            harmonious_pairs = {
                "whisper_tone": ["lyrical_flow", "gentle_guidance"],
                "metaphorical": ["symbolic_language", "metaphor_rich"],
                "direct_statement": ["sharp_delivery", "impact_focus"],
                "warm_encouragement": ["hopeful_tone", "nurturing_rhythm"],
            }

            harmony_score = 0.5  # 기본 조화도

            for expr_element, intensity_a in expr_a.items():
                harmonious_elements = harmonious_pairs.get(expr_element, [])
                for harmonic in harmonious_elements:
                    if harmonic in expr_b:
                        intensity_b = expr_b[harmonic]
                        harmonic_boost = (intensity_a * intensity_b) * 0.3
                        harmony_score += harmonic_boost

            return max(0.0, min(1.0, harmony_score))

        except Exception as e:
            self.logger.error(f"표현 조화도 계산 오류: {e}")
            return 0.5

    def calculate_resonance_pattern(self, sig_a: str, sig_b: str) -> ResonancePattern:
        """시그니처 쌍의 공명 패턴 계산"""

        # 개별 공명도 계산
        emotion_resonance = self.calculate_emotion_resonance(sig_a, sig_b)
        judgment_compatibility = self.calculate_judgment_compatibility(sig_a, sig_b)
        expression_harmony = self.calculate_expression_harmony(sig_a, sig_b)

        # 종합 공명도 계산
        overall_resonance = (
            emotion_resonance * self.resonance_weights["emotion_resonance"]
            + judgment_compatibility * self.resonance_weights["judgment_compatibility"]
            + expression_harmony * self.resonance_weights["expression_harmony"]
        )

        # 공명 타입 결정
        resonance_type = self._determine_resonance_type(
            emotion_resonance, judgment_compatibility, expression_harmony
        )

        # 융합 가능성 계산
        blend_potential = self._calculate_blend_potential(
            emotion_resonance, judgment_compatibility, expression_harmony
        )

        # 전이 부드러움 계산
        transition_smoothness = self._calculate_transition_smoothness(
            sig_a, sig_b, overall_resonance
        )

        return ResonancePattern(
            signature_a=sig_a,
            signature_b=sig_b,
            emotion_resonance=emotion_resonance,
            judgment_compatibility=judgment_compatibility,
            expression_harmony=expression_harmony,
            overall_resonance=overall_resonance,
            resonance_type=resonance_type,
            blend_potential=blend_potential,
            transition_smoothness=transition_smoothness,
        )

    def _determine_resonance_type(
        self, emotion: float, judgment: float, expression: float
    ) -> str:
        """공명 타입 결정"""
        avg_resonance = (emotion + judgment + expression) / 3

        if avg_resonance >= 0.7:
            return "harmonious"
        elif avg_resonance >= 0.4:
            return "complementary"
        else:
            return "conflicting"

    def _calculate_blend_potential(
        self, emotion: float, judgment: float, expression: float
    ) -> float:
        """융합 가능성 계산"""
        # 모든 영역이 균형잡혀 있을 때 융합 가능성이 높음
        variance = np.var([emotion, judgment, expression])
        balance_factor = 1.0 - variance
        avg_resonance = (emotion + judgment + expression) / 3

        return avg_resonance * 0.7 + balance_factor * 0.3

    def _calculate_transition_smoothness(
        self, sig_a: str, sig_b: str, resonance: float
    ) -> float:
        """전이 부드러움 계산"""
        # 시그니처 간 전이의 자연스러움 측정

        # 특별한 전이 경로 정의
        smooth_transitions = {
            ("selene", "lune"): 0.9,  # 둘 다 감성적, 내성적
            ("aurora", "selene"): 0.8,  # 양육적 → 공감적
            ("factbomb", "aurora"): 0.3,  # 논리적 → 감정적 (어려운 전이)
            ("lune", "aurora"): 0.7,  # 몽환적 → 희망적
        }

        # 양방향 확인
        transition_key = (sig_a, sig_b)
        reverse_key = (sig_b, sig_a)

        predefined_smoothness = (
            smooth_transitions.get(transition_key)
            or smooth_transitions.get(reverse_key)
            or resonance  # 기본값은 전체 공명도
        )

        return predefined_smoothness

    def generate_cross_resonance_map(self) -> CrossResonanceMap:
        """전체 Cross-Resonance 맵 생성"""

        signatures = list(self.signatures.keys())
        resonance_matrix = {}
        all_patterns = []

        # 모든 시그니처 쌍에 대해 공명 패턴 계산
        for i, sig_a in enumerate(signatures):
            resonance_matrix[sig_a] = {}
            for j, sig_b in enumerate(signatures):
                if i != j:  # 자기 자신과의 공명은 제외
                    pattern = self.calculate_resonance_pattern(sig_a, sig_b)
                    resonance_matrix[sig_a][sig_b] = pattern
                    all_patterns.append(pattern)

        # 지배적 쌍과 충돌 쌍 식별
        dominant_pairs = self._identify_dominant_pairs(all_patterns)
        conflict_pairs = self._identify_conflict_pairs(all_patterns)

        # 융합 추천 생성
        fusion_recommendations = self._generate_fusion_recommendations(all_patterns)

        cross_map = CrossResonanceMap(
            timestamp=datetime.now(),
            signatures=signatures,
            resonance_matrix=resonance_matrix,
            dominant_pairs=dominant_pairs,
            conflict_pairs=conflict_pairs,
            fusion_recommendations=fusion_recommendations,
        )

        self.current_map = cross_map
        self.resonance_history.append(cross_map)

        return cross_map

    def _identify_dominant_pairs(
        self, patterns: List[ResonancePattern]
    ) -> List[Tuple[str, str, float]]:
        """지배적 공명 쌍 식별"""
        sorted_patterns = sorted(
            patterns, key=lambda p: p.overall_resonance, reverse=True
        )
        return [
            (p.signature_a, p.signature_b, p.overall_resonance)
            for p in sorted_patterns[:3]
        ]

    def _identify_conflict_pairs(
        self, patterns: List[ResonancePattern]
    ) -> List[Tuple[str, str, float]]:
        """충돌 쌍 식별"""
        conflict_patterns = [p for p in patterns if p.resonance_type == "conflicting"]
        sorted_conflicts = sorted(conflict_patterns, key=lambda p: p.overall_resonance)
        return [
            (p.signature_a, p.signature_b, p.overall_resonance)
            for p in sorted_conflicts[:3]
        ]

    def _generate_fusion_recommendations(
        self, patterns: List[ResonancePattern]
    ) -> List[Dict[str, Any]]:
        """융합 추천 생성"""
        high_blend_patterns = [p for p in patterns if p.blend_potential >= 0.6]

        recommendations = []
        for pattern in high_blend_patterns:
            recommendation = {
                "signature_pair": (pattern.signature_a, pattern.signature_b),
                "blend_potential": pattern.blend_potential,
                "recommended_ratio": self._calculate_optimal_blend_ratio(pattern),
                "fusion_focus": self._determine_fusion_focus(pattern),
                "expected_characteristics": self._predict_fusion_characteristics(
                    pattern
                ),
            }
            recommendations.append(recommendation)

        return sorted(recommendations, key=lambda r: r["blend_potential"], reverse=True)

    def _calculate_optimal_blend_ratio(
        self, pattern: ResonancePattern
    ) -> Dict[str, float]:
        """최적 융합 비율 계산"""
        # 각 시그니처의 강점을 기반으로 비율 결정
        if pattern.emotion_resonance > pattern.judgment_compatibility:
            # 감정적 조화가 강한 경우 균등 분배
            return {pattern.signature_a: 0.5, pattern.signature_b: 0.5}
        else:
            # 판단 스타일 호환성이 강한 경우 주도적 시그니처 결정
            return {pattern.signature_a: 0.7, pattern.signature_b: 0.3}

    def _determine_fusion_focus(self, pattern: ResonancePattern) -> str:
        """융합 초점 결정"""
        if pattern.emotion_resonance >= max(
            pattern.judgment_compatibility, pattern.expression_harmony
        ):
            return "emotion_based_fusion"
        elif pattern.judgment_compatibility >= pattern.expression_harmony:
            return "judgment_based_fusion"
        else:
            return "expression_based_fusion"

    def _predict_fusion_characteristics(
        self, pattern: ResonancePattern
    ) -> Dict[str, str]:
        """융합 특성 예측"""
        characteristics = {}

        # 시그니처별 특성 매핑
        signature_traits = {
            "selene": ["gentle", "empathetic", "introspective"],
            "factbomb": ["direct", "logical", "precise"],
            "lune": ["poetic", "dreamy", "symbolic"],
            "aurora": ["nurturing", "hopeful", "encouraging"],
        }

        traits_a = signature_traits.get(pattern.signature_a, [])
        traits_b = signature_traits.get(pattern.signature_b, [])

        characteristics["primary_traits"] = traits_a[:2] + traits_b[:1]
        characteristics["communication_style"] = (
            f"Blend of {pattern.signature_a} and {pattern.signature_b}"
        )
        characteristics["strength_areas"] = self._identify_fusion_strengths(pattern)

        return characteristics

    def _identify_fusion_strengths(self, pattern: ResonancePattern) -> List[str]:
        """융합 강점 영역 식별"""
        strengths = []

        if pattern.emotion_resonance >= 0.7:
            strengths.append("emotional_intelligence")
        if pattern.judgment_compatibility >= 0.7:
            strengths.append("balanced_decision_making")
        if pattern.expression_harmony >= 0.7:
            strengths.append("versatile_communication")
        if pattern.transition_smoothness >= 0.8:
            strengths.append("adaptive_response")

        return strengths or ["experimental_blend"]

    def visualize_resonance_network(self) -> str:
        """공명 네트워크 시각화 (텍스트 기반)"""
        if not self.current_map:
            return "❌ Cross-Resonance Map이 생성되지 않았습니다."

        network_viz = "🔗 Signature Cross-Resonance Network\n"
        network_viz += "=" * 50 + "\n\n"

        # 지배적 공명 쌍 표시
        network_viz += "🌟 Dominant Resonance Pairs:\n"
        for sig_a, sig_b, resonance in self.current_map.dominant_pairs:
            network_viz += f"   {sig_a} ⇄ {sig_b}: {resonance:.3f}\n"

        network_viz += "\n⚡ Conflict Pairs:\n"
        for sig_a, sig_b, resonance in self.current_map.conflict_pairs:
            network_viz += f"   {sig_a} ⚠️ {sig_b}: {resonance:.3f}\n"

        network_viz += "\n🎯 Fusion Recommendations:\n"
        for i, rec in enumerate(self.current_map.fusion_recommendations[:3], 1):
            pair = rec["signature_pair"]
            network_viz += f"   {i}. {pair[0]} + {pair[1]} "
            network_viz += f"(Potential: {rec['blend_potential']:.3f})\n"
            network_viz += f"      Focus: {rec['fusion_focus']}\n"

        return network_viz

    def get_resonance_matrix_summary(self) -> Dict[str, Any]:
        """공명 매트릭스 요약 반환"""
        if not self.current_map:
            return {"error": "No resonance map available"}

        summary = {
            "timestamp": self.current_map.timestamp.isoformat(),
            "total_signatures": len(self.current_map.signatures),
            "total_pairs": len(self.current_map.signatures)
            * (len(self.current_map.signatures) - 1),
            "dominant_pairs": self.current_map.dominant_pairs,
            "conflict_pairs": self.current_map.conflict_pairs,
            "fusion_recommendations_count": len(
                self.current_map.fusion_recommendations
            ),
            "average_resonance": self._calculate_average_resonance(),
        }

        return summary

    def _calculate_average_resonance(self) -> float:
        """평균 공명도 계산"""
        if not self.current_map:
            return 0.0

        total_resonance = 0.0
        pair_count = 0

        for sig_a in self.current_map.resonance_matrix:
            for sig_b in self.current_map.resonance_matrix[sig_a]:
                total_resonance += self.current_map.resonance_matrix[sig_a][
                    sig_b
                ].overall_resonance
                pair_count += 1

        return total_resonance / pair_count if pair_count > 0 else 0.0

    def save_resonance_map(self, filename: str = None) -> str:
        """공명 맵 저장"""
        if not self.current_map:
            return "❌ 저장할 공명 맵이 없습니다."

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cross_resonance_map_{timestamp}.json"

        # 저장 가능한 형태로 변환
        save_data = {
            "timestamp": self.current_map.timestamp.isoformat(),
            "signatures": self.current_map.signatures,
            "resonance_matrix": {},
            "dominant_pairs": self.current_map.dominant_pairs,
            "conflict_pairs": self.current_map.conflict_pairs,
            "fusion_recommendations": self.current_map.fusion_recommendations,
        }

        # ResonancePattern 객체를 딕셔너리로 변환
        for sig_a in self.current_map.resonance_matrix:
            save_data["resonance_matrix"][sig_a] = {}
            for sig_b in self.current_map.resonance_matrix[sig_a]:
                pattern = self.current_map.resonance_matrix[sig_a][sig_b]
                save_data["resonance_matrix"][sig_a][sig_b] = asdict(pattern)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return f"✅ 공명 맵 저장 완료: {filename}"
        except Exception as e:
            return f"❌ 저장 실패: {e}"


# 편의 함수들
def create_cross_resonance_mapper() -> SignatureCrossResonanceMapper:
    """Cross-Resonance Mapper 생성"""
    return SignatureCrossResonanceMapper()


def analyze_signature_resonance(sig_a: str, sig_b: str) -> Dict[str, Any]:
    """두 시그니처 간 공명 분석"""
    mapper = create_cross_resonance_mapper()
    pattern = mapper.calculate_resonance_pattern(sig_a, sig_b)

    return {
        "resonance_pattern": asdict(pattern),
        "analysis": {
            "emotion_compatibility": (
                "High"
                if pattern.emotion_resonance >= 0.7
                else "Medium" if pattern.emotion_resonance >= 0.4 else "Low"
            ),
            "judgment_alignment": (
                "High"
                if pattern.judgment_compatibility >= 0.7
                else "Medium" if pattern.judgment_compatibility >= 0.4 else "Low"
            ),
            "expression_harmony": (
                "High"
                if pattern.expression_harmony >= 0.7
                else "Medium" if pattern.expression_harmony >= 0.4 else "Low"
            ),
            "fusion_viability": (
                "Recommended"
                if pattern.blend_potential >= 0.6
                else "Possible" if pattern.blend_potential >= 0.4 else "Challenging"
            ),
        },
    }


if __name__ == "__main__":
    # 테스트 실행
    print("🔗 Signature Cross-Resonance Mapper 테스트...")

    mapper = SignatureCrossResonanceMapper()

    # 전체 공명 맵 생성
    cross_map = mapper.generate_cross_resonance_map()

    # 결과 출력
    print("\n" + mapper.visualize_resonance_network())

    # 개별 분석 예시
    print("\n🔍 Individual Analysis:")
    analysis = analyze_signature_resonance("selene", "lune")
    print(f"Selene ⇄ Lune Analysis:")
    print(
        f"  Overall Resonance: {analysis['resonance_pattern']['overall_resonance']:.3f}"
    )
    print(f"  Resonance Type: {analysis['resonance_pattern']['resonance_type']}")
    print(f"  Fusion Viability: {analysis['analysis']['fusion_viability']}")

    # 저장
    save_result = mapper.save_resonance_map()
    print(f"\n{save_result}")

    print("\n✅ Cross-Resonance Mapper 테스트 완료!")
