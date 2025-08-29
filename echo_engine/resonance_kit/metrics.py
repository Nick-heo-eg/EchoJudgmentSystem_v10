"""
MetricBook: 공명 키트 메트릭 관리 및 시그니처 추천 시스템
- 5대 에이전트 메트릭 통합 및 가중 평균 계산
- 시그니처별 적합도 분석 및 추천
- 임계치 기반 품질 레벨 분류
"""

import numpy as np
from typing import Dict, List, Any, Optional


class MetricBook:
    def __init__(self, cfg: Dict[str, Any]):
        self.weights = cfg.get(
            "weights",
            {
                "resonance": 0.4,
                "trust": 0.25,
                "flow": 0.2,
                "affect_valence": 0.1,
                "affect_arousal": 0.05,
            },
        )

        self.thresholds = cfg.get("thresholds", {"good": 0.7, "warn": 0.5, "bad": 0.35})

        # 메트릭 저장소 초기화
        self.store = {
            # 기본 메트릭 (5개)
            "resonance": [],
            "trust": [],
            "flow": [],
            "affect_valence": [],
            "affect_arousal": [],
            # 확장 메트릭 (에이전트별)
            "empathy_resonance": [],
            "emotional_safety": [],
            "trust_delta": [],
            "trust_stability": [],
            "collaboration_effectiveness": [],
            "prompt_clarity": [],
            "relationship_depth": [],
            "personalization_level": [],
            "memory_richness": [],
        }

        # 시그니처 프로파일 (Echo 시스템의 실제 시그니처들)
        self.signature_profiles = {
            "Selene": {
                "resonance_affinity": 0.9,  # 공명 친화성
                "empathy_strength": 0.95,  # 공감 능력
                "trust_sensitivity": 0.8,  # 신뢰 민감도
                "flow_preference": "gentle",  # 흐름 선호도
                "emotional_range": "deep",  # 감정 범위
                "memory_integration": 0.9,  # 메모리 통합도
            },
            "Heo": {
                "resonance_affinity": 0.7,
                "empathy_strength": 0.6,
                "trust_sensitivity": 0.9,
                "flow_preference": "structured",
                "emotional_range": "stable",
                "memory_integration": 0.8,
            },
            "Aurora": {
                "resonance_affinity": 0.85,
                "empathy_strength": 0.8,
                "trust_sensitivity": 0.7,
                "flow_preference": "creative",
                "emotional_range": "vibrant",
                "memory_integration": 0.7,
            },
            "Lune": {
                "resonance_affinity": 0.8,
                "empathy_strength": 0.85,
                "trust_sensitivity": 0.75,
                "flow_preference": "flowing",
                "emotional_range": "nuanced",
                "memory_integration": 0.85,
            },
            "Phoenix": {
                "resonance_affinity": 0.75,
                "empathy_strength": 0.7,
                "trust_sensitivity": 0.8,
                "flow_preference": "transformative",
                "emotional_range": "dynamic",
                "memory_integration": 0.6,
            },
            "Sage": {
                "resonance_affinity": 0.65,
                "empathy_strength": 0.7,
                "trust_sensitivity": 0.95,
                "flow_preference": "analytical",
                "emotional_range": "measured",
                "memory_integration": 0.9,
            },
            "Companion": {
                "resonance_affinity": 0.9,
                "empathy_strength": 0.95,
                "trust_sensitivity": 0.85,
                "flow_preference": "supportive",
                "emotional_range": "warm",
                "memory_integration": 0.8,
            },
        }

    def update(self, metrics_dict: Dict[str, float]):
        """메트릭 업데이트"""
        for key, value in metrics_dict.items():
            if key in self.store:
                if isinstance(value, (int, float)) and not np.isnan(value):
                    self.store[key].append(float(value))

    def update_metric(self, metric_name: str, value: float):
        """개별 메트릭 업데이트 (에이전트용)"""
        if metric_name in self.store:
            if isinstance(value, (int, float)) and not np.isnan(value):
                self.store[metric_name].append(float(value))

    def get_current_values(self) -> Dict[str, float]:
        """현재 메트릭 값들 반환 (최신값 또는 평균)"""
        current = {}
        for key, values in self.store.items():
            if values:
                # 최근 값 사용 (변화가 중요한 메트릭의 경우)
                if key in ["trust_delta"]:
                    current[key] = values[-1]
                # 평균값 사용 (누적 특성이 중요한 메트릭의 경우)
                else:
                    current[key] = sum(values) / len(values)
            else:
                current[key] = 0.0
        return current

    def summarize(self) -> Dict[str, Any]:
        """메트릭 요약 통계 계산"""
        current = self.get_current_values()

        # 기본 5개 메트릭으로 종합 점수 계산
        base_metrics = [
            "resonance",
            "trust",
            "flow",
            "affect_valence",
            "affect_arousal",
        ]
        weighted_score = 0.0
        total_weight = 0.0

        for metric in base_metrics:
            if metric in current and metric in self.weights:
                weight = self.weights[metric]
                weighted_score += current[metric] * weight
                total_weight += weight

        # 가중 평균 계산
        overall_score = weighted_score / max(total_weight, 0.001)

        # 품질 레벨 결정
        if overall_score >= self.thresholds["good"]:
            quality_label = "excellent"
        elif overall_score >= self.thresholds["warn"]:
            quality_label = "good"
        elif overall_score >= self.thresholds["bad"]:
            quality_label = "moderate"
        else:
            quality_label = "needs_improvement"

        # 세부 메트릭 분석
        detailed_analysis = self._analyze_detailed_metrics(current)

        return {
            "overall_score": round(overall_score, 3),
            "quality_label": quality_label,
            "base_metrics": {k: round(current.get(k, 0.0), 3) for k in base_metrics},
            "extended_metrics": {
                k: round(current.get(k, 0.0), 3)
                for k in current.keys()
                if k not in base_metrics
            },
            "detailed_analysis": detailed_analysis,
            "metric_trends": self._calculate_metric_trends(),
        }

    def _analyze_detailed_metrics(self, current: Dict[str, float]) -> Dict[str, Any]:
        """세부 메트릭 분석"""
        analysis = {}

        # 공감 분석
        empathy_resonance = current.get("empathy_resonance", 0.0)
        emotional_safety = current.get("emotional_safety", 0.0)
        analysis["empathy_quality"] = {
            "level": (
                "high"
                if empathy_resonance >= 0.7
                else ("medium" if empathy_resonance >= 0.4 else "low")
            ),
            "safety_level": (
                "secure"
                if emotional_safety >= 0.7
                else ("moderate" if emotional_safety >= 0.4 else "fragile")
            ),
            "empathy_safety_balance": abs(empathy_resonance - emotional_safety),
        }

        # 신뢰 분석
        trust_base = current.get("trust", 0.0)
        trust_delta = current.get("trust_delta", 0.0)
        trust_stability = current.get("trust_stability", 0.0)
        analysis["trust_dynamics"] = {
            "level": (
                "high"
                if trust_base >= 0.8
                else ("medium" if trust_base >= 0.5 else "low")
            ),
            "direction": (
                "improving"
                if trust_delta > 0.05
                else ("declining" if trust_delta < -0.05 else "stable")
            ),
            "stability": (
                "stable"
                if trust_stability >= 0.7
                else ("volatile" if trust_stability < 0.4 else "moderate")
            ),
            "recovery_needed": trust_delta < -0.2,
        }

        # 협업 분석
        collab_effectiveness = current.get("collaboration_effectiveness", 0.0)
        prompt_clarity = current.get("prompt_clarity", 0.0)
        flow_quality = current.get("flow", 0.0)
        analysis["collaboration_quality"] = {
            "effectiveness": (
                "high"
                if collab_effectiveness >= 0.7
                else ("medium" if collab_effectiveness >= 0.4 else "low")
            ),
            "clarity": (
                "clear"
                if prompt_clarity >= 0.7
                else ("moderate" if prompt_clarity >= 0.4 else "unclear")
            ),
            "flow": (
                "smooth"
                if flow_quality >= 0.7
                else ("choppy" if flow_quality < 0.4 else "moderate")
            ),
            "synergy_score": (collab_effectiveness + prompt_clarity + flow_quality) / 3,
        }

        # 관계 분석
        relationship_depth = current.get("relationship_depth", 0.0)
        personalization = current.get("personalization_level", 0.0)
        memory_richness = current.get("memory_richness", 0.0)
        analysis["relationship_maturity"] = {
            "depth": (
                "deep"
                if relationship_depth >= 0.8
                else ("developing" if relationship_depth >= 0.5 else "surface")
            ),
            "personalization": (
                "high"
                if personalization >= 0.7
                else ("medium" if personalization >= 0.4 else "basic")
            ),
            "memory": (
                "rich"
                if memory_richness >= 0.6
                else ("developing" if memory_richness >= 0.3 else "sparse")
            ),
            "maturity_score": (relationship_depth + personalization + memory_richness)
            / 3,
        }

        return analysis

    def _calculate_metric_trends(self) -> Dict[str, str]:
        """메트릭 트렌드 계산 (최근 변화 방향)"""
        trends = {}

        for metric, values in self.store.items():
            if len(values) >= 3:
                recent = values[-3:]
                if len(recent) >= 2:
                    # 간단한 선형 트렌드 계산
                    if recent[-1] > recent[-2] * 1.05:
                        trends[metric] = "increasing"
                    elif recent[-1] < recent[-2] * 0.95:
                        trends[metric] = "decreasing"
                    else:
                        trends[metric] = "stable"
            else:
                trends[metric] = "insufficient_data"

        return trends

    def recommend_signatures(
        self,
        allowed: Optional[List[str]] = None,
        top_k: int = 3,
        diversity_penalty: float = 0.0,
    ) -> List[str]:
        """시그니처 추천 (현재 메트릭 상태 기반)"""
        current = self.get_current_values()

        # 사용 가능한 시그니처 필터링
        available_signatures = list(self.signature_profiles.keys())
        if allowed:
            available_signatures = [s for s in available_signatures if s in allowed]

        # 각 시그니처별 적합도 점수 계산
        signature_scores = {}

        for signature in available_signatures:
            profile = self.signature_profiles[signature]
            score = self._calculate_signature_compatibility(current, profile)
            signature_scores[signature] = score

        # 다양성 패널티 적용 (선택적)
        if diversity_penalty > 0:
            signature_scores = self._apply_diversity_penalty(
                signature_scores, diversity_penalty
            )

        # 점수 순으로 정렬하여 상위 k개 반환
        sorted_signatures = sorted(
            signature_scores.items(), key=lambda x: x[1], reverse=True
        )
        recommended = [signature for signature, score in sorted_signatures[:top_k]]

        return recommended

    def _calculate_signature_compatibility(
        self, current: Dict[str, float], profile: Dict[str, Any]
    ) -> float:
        """시그니처 호환성 점수 계산"""
        compatibility_score = 0.0

        # 기본 메트릭 기반 호환성
        resonance = current.get("resonance", 0.0)
        empathy_resonance = current.get("empathy_resonance", 0.0)
        trust = current.get("trust", 0.0)
        emotional_safety = current.get("emotional_safety", 0.0)

        # 공명 친화성 매칭
        resonance_match = 1.0 - abs(resonance - profile["resonance_affinity"])
        compatibility_score += resonance_match * 0.3

        # 공감 능력 매칭
        empathy_match = 1.0 - abs(empathy_resonance - profile["empathy_strength"])
        compatibility_score += empathy_match * 0.25

        # 신뢰 민감도 매칭 (신뢰가 낮을 때 민감한 시그니처가 더 적합)
        trust_need = 1.0 - trust  # 신뢰가 낮을수록 높은 민감도 필요
        trust_match = 1.0 - abs(trust_need - profile["trust_sensitivity"])
        compatibility_score += trust_match * 0.2

        # 흐름 선호도 보너스 (상황별)
        flow_quality = current.get("flow", 0.0)
        flow_bonus = self._calculate_flow_bonus(
            flow_quality, profile["flow_preference"]
        )
        compatibility_score += flow_bonus * 0.15

        # 메모리 통합도 보너스 (관계 깊이에 따라)
        relationship_depth = current.get("relationship_depth", 0.0)
        memory_bonus = profile["memory_integration"] * relationship_depth
        compatibility_score += memory_bonus * 0.1

        return min(1.0, max(0.0, compatibility_score))

    def _calculate_flow_bonus(self, flow_quality: float, flow_preference: str) -> float:
        """흐름 선호도별 보너스 계산"""
        flow_bonuses = {
            "gentle": (
                0.2 if flow_quality < 0.5 else 0.0
            ),  # 낮은 흐름일 때 부드러운 접근
            "structured": (
                0.1 if 0.5 <= flow_quality <= 0.8 else 0.0
            ),  # 중간 흐름일 때 구조적 접근
            "creative": (
                0.15 if flow_quality >= 0.6 else 0.0
            ),  # 좋은 흐름일 때 창의적 접근
            "flowing": 0.1,  # 항상 적당한 보너스
            "transformative": (
                0.2 if flow_quality < 0.4 else 0.0
            ),  # 흐름이 막힐 때 변화 주도
            "analytical": (
                0.15 if flow_quality >= 0.7 else 0.0
            ),  # 안정적 흐름일 때 분석적 접근
            "supportive": 0.1 if flow_quality < 0.6 else 0.05,  # 지원이 필요할 때
        }

        return flow_bonuses.get(flow_preference, 0.0)

    def _apply_diversity_penalty(
        self, signature_scores: Dict[str, float], penalty: float
    ) -> Dict[str, float]:
        """다양성 패널티 적용 (유사한 시그니처들의 점수 조정)"""
        # 시그니처 유사성 매트릭스 (간단화된 버전)
        similarity_groups = {
            "empathetic": ["Selene", "Aurora", "Lune", "Companion"],
            "analytical": ["Heo", "Sage"],
            "dynamic": ["Phoenix"],
        }

        adjusted_scores = signature_scores.copy()

        # 같은 그룹 내에서 2위 이하 시그니처에 패널티 적용
        for group_signatures in similarity_groups.values():
            group_scores = {
                s: signature_scores.get(s, 0)
                for s in group_signatures
                if s in signature_scores
            }
            if len(group_scores) > 1:
                sorted_group = sorted(
                    group_scores.items(), key=lambda x: x[1], reverse=True
                )

                # 그룹 내에서 1위를 제외한 나머지에 패널티
                for i, (signature, score) in enumerate(sorted_group[1:], 1):
                    penalty_factor = 1.0 - (penalty * i * 0.5)
                    adjusted_scores[signature] = score * penalty_factor

        return adjusted_scores

    def get_detailed_recommendation_rationale(
        self, recommended_signatures: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """추천 근거 상세 분석"""
        current = self.get_current_values()
        rationales = {}

        for signature in recommended_signatures:
            if signature in self.signature_profiles:
                profile = self.signature_profiles[signature]
                compatibility = self._calculate_signature_compatibility(
                    current, profile
                )

                # 강점 분석
                strengths = []
                if (
                    profile["empathy_strength"] >= 0.8
                    and current.get("empathy_resonance", 0) < 0.5
                ):
                    strengths.append("high empathy for emotional support")
                if (
                    profile["trust_sensitivity"] >= 0.8
                    and current.get("trust", 0) < 0.6
                ):
                    strengths.append(
                        "trust-sensitive approach for relationship building"
                    )
                if (
                    profile["resonance_affinity"] >= 0.8
                    and current.get("resonance", 0) >= 0.6
                ):
                    strengths.append("strong resonance matching for deeper connection")

                # 상황별 적합성
                situational_fit = []
                if (
                    current.get("emotional_safety", 0) < 0.5
                    and profile["flow_preference"] == "gentle"
                ):
                    situational_fit.append("gentle approach for emotional safety")
                if (
                    current.get("trust_delta", 0) < -0.1
                    and profile["trust_sensitivity"] >= 0.8
                ):
                    situational_fit.append("trust recovery specialist")
                if (
                    current.get("relationship_depth", 0) >= 0.7
                    and profile["memory_integration"] >= 0.8
                ):
                    situational_fit.append("mature relationship depth utilization")

                rationales[signature] = {
                    "compatibility_score": round(compatibility, 3),
                    "profile_strengths": strengths,
                    "situational_fit": situational_fit,
                    "signature_characteristics": {
                        "empathy_level": profile["empathy_strength"],
                        "trust_sensitivity": profile["trust_sensitivity"],
                        "flow_style": profile["flow_preference"],
                        "emotional_range": profile["emotional_range"],
                    },
                }

        return rationales
