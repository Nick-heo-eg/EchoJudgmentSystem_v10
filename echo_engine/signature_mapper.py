# echo_engine/signature_performance_reporter.py

# @owner: nick
# @expose
# @maturity: stable

"""
🔗 Signature Mapper
- Signature ID와 시드 초기 상태(InitialState)를 연결하고, 매핑 정합성 분석
- signature.yaml에 정의된 시그니처 기반으로 emotion, strategy alignment 평가
"""

import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from echo_engine.seed_kernel import InitialState


class SignaturePerformanceReporter:
    def __init__(self, signature_yaml_path: str = "data/signature.yaml"):
        self.signature_yaml_path = signature_yaml_path
        self.signatures = self._load_signatures()

    def _load_signatures(self) -> Dict:
        """Load signature configurations from YAML"""
        try:
            with open(self.signature_yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Default signature profiles if file not found
            return {
                "signatures": [
                    {
                        "id": "Echo-Aurora",
                        "name": "공감적 양육자",
                        "primary_strategies": ["empathetic", "nurturing", "optimistic"],
                        "emotional_triggers": {
                            "joy": 0.8,
                            "hope": 0.9,
                            "compassion": 0.7,
                        },
                        "emotion_sensitivity": 0.92,
                        "meta_sensitivity": 0.78,
                    },
                    {
                        "id": "Echo-Phoenix",
                        "name": "변화 추진자",
                        "primary_strategies": [
                            "transformative",
                            "resilient",
                            "adaptive",
                        ],
                        "emotional_triggers": {
                            "determination": 0.9,
                            "courage": 0.8,
                            "renewal": 0.7,
                        },
                        "emotion_sensitivity": 0.88,
                        "meta_sensitivity": 0.91,
                    },
                    {
                        "id": "Echo-Sage",
                        "name": "지혜로운 분석가",
                        "primary_strategies": ["analytical", "logical", "systematic"],
                        "emotional_triggers": {
                            "curiosity": 0.8,
                            "wisdom": 0.9,
                            "understanding": 0.7,
                        },
                        "emotion_sensitivity": 0.65,
                        "meta_sensitivity": 0.95,
                    },
                    {
                        "id": "Echo-Companion",
                        "name": "신뢰할 수 있는 동반자",
                        "primary_strategies": ["supportive", "loyal", "reliable"],
                        "emotional_triggers": {
                            "trust": 0.9,
                            "stability": 0.8,
                            "care": 0.7,
                        },
                        "emotion_sensitivity": 0.80,
                        "meta_sensitivity": 0.83,
                    },
                ]
            }

    def get_signature_by_id(self, signature_id: str) -> Optional[Dict]:
        """Get signature configuration by ID"""
        for signature in self.signatures.get("signatures", []):
            if signature.get("id") == signature_id:
                return signature
        return None

    def generate_signature_profile(self, signature_id: str) -> Dict[str, Any]:
        """시그니처 고유 특성 추출 (감정, 전략, 리듬 기반)"""
        signature = self.get_signature_by_id(signature_id)

        if not signature:
            return {
                "signature_id": signature_id,
                "preferred_emotion": "neutral",
                "preferred_strategy": "balanced",
                "rhythm_bias": ["🤔"],
                "meta_sensitivity_baseline": 0.5,
                "error": "Unknown signature",
            }

        # Extract primary emotion from emotional triggers
        emotional_triggers = signature.get("emotional_triggers", {})
        preferred_emotion = (
            max(emotional_triggers.keys(), key=lambda x: emotional_triggers[x])
            if emotional_triggers
            else "neutral"
        )

        # Extract primary strategy
        primary_strategies = signature.get("primary_strategies", ["balanced"])
        preferred_strategy = primary_strategies[0] if primary_strategies else "balanced"

        # Generate rhythm bias from signature characteristics
        rhythm_bias = self._generate_rhythm_from_signature(signature)

        return {
            "signature_id": signature_id,
            "preferred_emotion": preferred_emotion,
            "preferred_strategy": preferred_strategy,
            "rhythm_bias": rhythm_bias,
            "meta_sensitivity_baseline": signature.get("meta_sensitivity", 0.5),
            "emotion_sensitivity": signature.get("emotion_sensitivity", 0.5),
            "primary_strategies": primary_strategies,
            "emotional_triggers": emotional_triggers,
        }

    def _generate_rhythm_from_signature(self, signature: Dict) -> List[str]:
        """Generate rhythm pattern from signature characteristics"""
        name = signature.get("name", "")

        if "양육" in name or "empathetic" in signature.get("primary_strategies", []):
            return ["🤗", "💝", "🌸", "🌅"]
        elif "변화" in name or "transformative" in signature.get(
            "primary_strategies", []
        ):
            return ["🔥", "🌪", "⚡", "🌅"]
        elif "분석" in name or "analytical" in signature.get("primary_strategies", []):
            return ["🔍", "📚", "🧮", "⚖️"]
        elif "동반" in name or "supportive" in signature.get("primary_strategies", []):
            return ["🤝", "🛡️", "💙", "🏠"]
        else:
            return ["🤔", "💭", "🎯", "✨"]

    def compare_signature_to_seed(
        self, seed_state: InitialState, signature_id: str
    ) -> Dict[str, Any]:
        """시드 상태와 시그니처 매핑 일치도 평가"""
        profile = self.generate_signature_profile(signature_id)

        if "error" in profile:
            return {
                "signature_id": signature_id,
                "emotion_alignment": 0.0,
                "strategy_alignment": 0.0,
                "sensitivity_gap": 1.0,
                "rhythm_compatibility": 0.0,
                "overall_match_score": 0.0,
                "error": profile["error"],
            }

        # Emotion alignment
        emotion_match = (
            1.0
            if seed_state.emotion_rhythm.primary_emotion == profile["preferred_emotion"]
            else 0.0
        )

        # Strategy alignment
        strategy_match = (
            1.0 if seed_state.initial_strategy == profile["preferred_strategy"] else 0.0
        )

        # Meta sensitivity gap (lower gap = better match)
        sensitivity_gap = abs(
            seed_state.meta_sensitivity - profile["meta_sensitivity_baseline"]
        )
        sensitivity_score = max(0.0, 1.0 - sensitivity_gap)

        # Rhythm compatibility (check overlap between seed rhythm and signature rhythm bias)
        rhythm_overlap = len(
            set(seed_state.emotion_rhythm.rhythm_pattern) & set(profile["rhythm_bias"])
        )
        max_possible_overlap = min(
            len(seed_state.emotion_rhythm.rhythm_pattern), len(profile["rhythm_bias"])
        )
        rhythm_compatibility = rhythm_overlap / max(max_possible_overlap, 1)

        # Overall match score (weighted combination)
        overall_match_score = (
            0.3 * emotion_match
            + 0.3 * strategy_match
            + 0.2 * sensitivity_score
            + 0.2 * rhythm_compatibility
        )

        return {
            "signature_id": signature_id,
            "emotion_alignment": emotion_match,
            "strategy_alignment": strategy_match,
            "sensitivity_gap": sensitivity_gap,
            "sensitivity_score": sensitivity_score,
            "rhythm_compatibility": rhythm_compatibility,
            "overall_match_score": round(overall_match_score, 3),
            "match_details": {
                "seed_emotion": seed_state.emotion_rhythm.primary_emotion,
                "preferred_emotion": profile["preferred_emotion"],
                "seed_strategy": seed_state.initial_strategy,
                "preferred_strategy": profile["preferred_strategy"],
                "seed_sensitivity": seed_state.meta_sensitivity,
                "baseline_sensitivity": profile["meta_sensitivity_baseline"],
                "seed_rhythm": seed_state.emotion_rhythm.rhythm_pattern,
                "signature_rhythm": profile["rhythm_bias"],
            },
        }

    def find_best_signature_for_seed(self, seed_state: InitialState) -> Dict[str, Any]:
        """주어진 시드에 가장 적합한 시그니처 찾기"""
        best_match = None
        best_score = -1.0
        all_comparisons = []

        for signature in self.signatures.get("signatures", []):
            signature_id = signature.get("id", "unknown")
            comparison = self.compare_signature_to_seed(seed_state, signature_id)
            all_comparisons.append(comparison)

            if comparison["overall_match_score"] > best_score:
                best_score = comparison["overall_match_score"]
                best_match = comparison

        return {
            "seed_id": seed_state.identity_trace.seed_id,
            "best_signature": best_match,
            "all_comparisons": all_comparisons,
            "recommendation_confidence": best_score,
        }

    def list_signature_alignment_stats(
        self, seed_states: List[InitialState]
    ) -> List[Dict[str, Any]]:
        """시그니처별 평균 매핑 통계 계산"""
        results = []
        signature_stats = {}

        for seed in seed_states:
            sig_id = seed.signature_alignment or "unknown"
            comparison = self.compare_signature_to_seed(seed, sig_id)

            results.append(
                {
                    "seed_id": seed.identity_trace.seed_id,
                    "signature": sig_id,
                    **comparison,
                }
            )

            # Accumulate stats for each signature
            if sig_id not in signature_stats:
                signature_stats[sig_id] = {
                    "count": 0,
                    "total_emotion_alignment": 0.0,
                    "total_strategy_alignment": 0.0,
                    "total_sensitivity_score": 0.0,
                    "total_rhythm_compatibility": 0.0,
                    "total_overall_score": 0.0,
                }

            stats = signature_stats[sig_id]
            stats["count"] += 1
            stats["total_emotion_alignment"] += comparison["emotion_alignment"]
            stats["total_strategy_alignment"] += comparison["strategy_alignment"]
            stats["total_sensitivity_score"] += comparison.get("sensitivity_score", 0.0)
            stats["total_rhythm_compatibility"] += comparison["rhythm_compatibility"]
            stats["total_overall_score"] += comparison["overall_match_score"]

        # Calculate averages
        signature_averages = {}
        for sig_id, stats in signature_stats.items():
            count = stats["count"]
            signature_averages[sig_id] = {
                "seed_count": count,
                "avg_emotion_alignment": round(
                    stats["total_emotion_alignment"] / count, 3
                ),
                "avg_strategy_alignment": round(
                    stats["total_strategy_alignment"] / count, 3
                ),
                "avg_sensitivity_score": round(
                    stats["total_sensitivity_score"] / count, 3
                ),
                "avg_rhythm_compatibility": round(
                    stats["total_rhythm_compatibility"] / count, 3
                ),
                "avg_overall_score": round(stats["total_overall_score"] / count, 3),
            }

        return {
            "individual_results": results,
            "signature_averages": signature_averages,
            "total_seeds_analyzed": len(seed_states),
        }

    def get_available_signatures(self) -> List[str]:
        """Get list of available signature IDs"""
        return [
            sig.get("id", "unknown") for sig in self.signatures.get("signatures", [])
        ]

    async def register_signature(
        self, signature_name: str, signature_config: Dict[str, Any]
    ) -> bool:
        """새로운 시그니처 등록"""
        try:
            new_signature = {
                "id": signature_name,
                "name": signature_config.get("description", signature_name),
                "judgment_framework": signature_config.get(
                    "judgment_framework", "general"
                ),
                "expertise_domain": signature_config.get("expertise_domain", "general"),
                "complexity_level": signature_config.get("complexity_level", "medium"),
                "primary_strategies": [
                    signature_config.get("strategic_focus", "balanced")
                ],
                "emotion_sensitivity": signature_config.get("emotion_sensitivity", 0.6),
                "response_style": signature_config.get("response_style", "balanced"),
                "judgment_loops": signature_config.get("judgment_loops", []),
            }

            # 기존 시그니처 목록에 추가
            if "signatures" not in self.signatures:
                self.signatures["signatures"] = []

            # 중복 확인 및 업데이트/추가
            existing_index = None
            for i, sig in enumerate(self.signatures["signatures"]):
                if sig.get("id") == signature_name:
                    existing_index = i
                    break

            if existing_index is not None:
                self.signatures["signatures"][existing_index] = new_signature
                print(f"🔄 기존 시그니처 업데이트: {signature_name}")
            else:
                self.signatures["signatures"].append(new_signature)
                print(f"✅ 새 시그니처 등록: {signature_name}")

            return True

        except Exception as e:
            print(f"❌ 시그니처 등록 실패: {e}")
            return False

    def analyze_signature_distribution(
        self, seed_states: List[InitialState]
    ) -> Dict[str, Any]:
        """분석 시드들의 시그니처 분포 및 매칭 품질 분석"""
        signature_distribution = {}
        unaligned_seeds = []

        for seed in seed_states:
            sig_id = seed.signature_alignment
            if sig_id:
                if sig_id not in signature_distribution:
                    signature_distribution[sig_id] = []
                signature_distribution[sig_id].append(seed.identity_trace.seed_id)
            else:
                unaligned_seeds.append(seed.identity_trace.seed_id)

        # Calculate distribution percentages
        total_seeds = len(seed_states)
        distribution_percentages = {}
        for sig_id, seed_ids in signature_distribution.items():
            distribution_percentages[sig_id] = round(
                len(seed_ids) / total_seeds * 100, 1
            )

        return {
            "signature_distribution": signature_distribution,
            "distribution_percentages": distribution_percentages,
            "unaligned_seeds": unaligned_seeds,
            "unaligned_percentage": round(len(unaligned_seeds) / total_seeds * 100, 1),
            "total_seeds": total_seeds,
            "unique_signatures": len(signature_distribution),
        }


# Convenience functions
def generate_signature_profile(signature_id: str) -> Dict[str, Any]:
    """시그니처 고유 특성 추출 (편의 함수)"""
    mapper = SignaturePerformanceReporter()
    return mapper.generate_signature_profile(signature_id)


def compare_signature_to_seed(
    seed_state: InitialState, signature_id: str
) -> Dict[str, Any]:
    """시드 상태와 시그니처 매핑 일치도 평가 (편의 함수)"""
    mapper = SignaturePerformanceReporter()
    return mapper.compare_signature_to_seed(seed_state, signature_id)


def list_signature_alignment_stats(seed_states: List[InitialState]) -> Dict[str, Any]:
    """시그니처별 평균 매핑 통계 계산 (편의 함수)"""
    mapper = SignaturePerformanceReporter()
    return mapper.list_signature_alignment_stats(seed_states)


def find_best_signature_for_seed(seed_state: InitialState) -> Dict[str, Any]:
    """주어진 시드에 가장 적합한 시그니처 찾기 (편의 함수)"""
    mapper = SignaturePerformanceReporter()
    return mapper.find_best_signature_for_seed(seed_state)


if __name__ == "__main__":
    # Test code
    from echo_engine.seed_kernel import EchoSeedKernel

    print("🔗 Signature Mapper 테스트")

    # Create test kernel and generate some seeds
    kernel = EchoSeedKernel()
    test_seeds = []

    for i in range(3):
        seed = kernel.generate_initial_state(
            primary_emotion=["joy", "curiosity", "neutral"][i],
            strategy=["empathetic", "analytical", "supportive"][i],
        )
        test_seeds.append(seed)

    # Test signature mapping
    mapper = SignaturePerformanceReporter()

    print(f"Available signatures: {mapper.get_available_signatures()}")

    # Test individual seed comparison
    for seed in test_seeds:
        best_match = find_best_signature_for_seed(seed)
        print(f"\nSeed {seed.identity_trace.seed_id}:")
        print(f"Best signature: {best_match['best_signature']['signature_id']}")
        print(f"Match score: {best_match['recommendation_confidence']:.3f}")

    # Test alignment stats
    stats = list_signature_alignment_stats(test_seeds)
    print(f"\nAlignment Statistics:")
    print(f"Total seeds analyzed: {stats['total_seeds_analyzed']}")
    for sig_id, avg_stats in stats["signature_averages"].items():
        print(f"{sig_id}: Avg overall score = {avg_stats['avg_overall_score']}")

    print("✅ Signature Mapper 테스트 완료")
