# echo_engine/seed_replay_analyzer.py
"""
🔁 Seed Replay Analyzer
- seed_kernel에서 생성된 진화 이력을 바탕으로 감정/전략 흐름 분석
- 변동성 드리프트, 전략 변화율, 감정 패턴 통계 등 제공
"""

import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime
from echo_engine.seed_kernel import EchoSeedKernel, InitialState


class SeedReplayAnalyzer:
    def __init__(self, kernel: EchoSeedKernel):
        self.kernel = kernel
        self.analysis_cache = {}

    def analyze_evolution_trends(self) -> Dict[str, Any]:
        """진화 기록 기반 감정, 전략 트렌드 분석"""
        emotion_changes = []
        strategy_changes = []
        evolution_triggers = []
        evolution_timeline = []

        for event in self.kernel.evolution_history:
            if event.get("event_type") == "seed_evolution":
                changes = event.get("changes", {})

                # Extract emotion changes
                emotion_change = changes.get("emotion_change", {})
                if emotion_change:
                    emotion_changes.append(
                        {
                            "from": emotion_change.get("from"),
                            "to": emotion_change.get("to"),
                            "timestamp": event.get("timestamp"),
                            "seed_id": event.get("seed_id"),
                        }
                    )

                # Extract strategy changes
                strategy_change = changes.get("strategy_change", {})
                if strategy_change:
                    strategy_changes.append(
                        {
                            "from": strategy_change.get("from"),
                            "to": strategy_change.get("to"),
                            "timestamp": event.get("timestamp"),
                            "seed_id": event.get("seed_id"),
                        }
                    )

                # Extract evolution triggers
                trigger = event.get("trigger", "unknown")
                evolution_triggers.append(trigger)

                # Timeline entry
                evolution_timeline.append(
                    {
                        "timestamp": event.get("timestamp"),
                        "seed_id": event.get("seed_id"),
                        "trigger": trigger,
                        "changes": changes,
                    }
                )

        # Analyze patterns
        emotion_transition_patterns = self._analyze_transition_patterns(emotion_changes)
        strategy_transition_patterns = self._analyze_transition_patterns(
            strategy_changes
        )
        trigger_frequency = Counter(evolution_triggers)

        return {
            "emotion_transitions": emotion_changes,
            "strategy_transitions": strategy_changes,
            "evolution_count": len(self.kernel.evolution_history),
            "emotion_patterns": emotion_transition_patterns,
            "strategy_patterns": strategy_transition_patterns,
            "trigger_frequency": dict(trigger_frequency),
            "evolution_timeline": evolution_timeline,
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def _analyze_transition_patterns(self, transitions: List[Dict]) -> Dict[str, Any]:
        """Extract patterns from transition data"""
        if not transitions:
            return {"patterns": {}, "most_common": None, "stability_score": 1.0}

        # Count transition types
        pattern_counts = defaultdict(int)
        for transition in transitions:
            from_state = transition.get("from", "unknown")
            to_state = transition.get("to", "unknown")
            pattern = f"{from_state} → {to_state}"
            pattern_counts[pattern] += 1

        # Calculate stability (how often states stay the same)
        same_state_transitions = sum(
            1 for t in transitions if t.get("from") == t.get("to")
        )
        stability_score = (
            same_state_transitions / len(transitions) if transitions else 1.0
        )

        # Most common transition
        most_common = (
            max(pattern_counts.items(), key=lambda x: x[1]) if pattern_counts else None
        )

        return {
            "patterns": dict(pattern_counts),
            "most_common": most_common,
            "stability_score": round(stability_score, 3),
            "total_transitions": len(transitions),
            "unique_patterns": len(pattern_counts),
        }

    def detect_emotion_volatility_drift(self) -> Dict[str, Any]:
        """감정 리듬 변동성 평균 드리프트 추정"""
        volatility_data = []
        emotion_distribution = defaultdict(int)
        sensitivity_data = []

        for state_id, state in self.kernel.seed_registry.items():
            volatility = state.emotion_rhythm.volatility_threshold
            volatility_data.append(volatility)

            # Track emotion distribution
            emotion_distribution[state.emotion_rhythm.primary_emotion] += 1

            # Track sensitivity
            sensitivity_data.append(state.meta_sensitivity)

        if not volatility_data:
            return {"error": "No seed data available for analysis", "drift_score": 0.0}

        # Calculate drift statistics
        mean_volatility = np.mean(volatility_data)
        std_volatility = np.std(volatility_data)
        baseline_volatility = 0.5  # Assumed neutral baseline

        # Drift is the absolute deviation from baseline
        total_drift = sum(abs(v - baseline_volatility) for v in volatility_data)
        avg_drift = total_drift / len(volatility_data)

        # Volatility trend analysis
        volatility_trend = "stable"
        if mean_volatility > baseline_volatility + std_volatility:
            volatility_trend = "increasing"
        elif mean_volatility < baseline_volatility - std_volatility:
            volatility_trend = "decreasing"

        # Sensitivity analysis
        mean_sensitivity = np.mean(sensitivity_data) if sensitivity_data else 0.0
        sensitivity_std = np.std(sensitivity_data) if len(sensitivity_data) > 1 else 0.0

        return {
            "drift_score": round(avg_drift, 3),
            "mean_volatility": round(mean_volatility, 3),
            "std_volatility": round(std_volatility, 3),
            "baseline_volatility": baseline_volatility,
            "volatility_trend": volatility_trend,
            "emotion_distribution": dict(emotion_distribution),
            "sensitivity_stats": {
                "mean": round(mean_sensitivity, 3),
                "std": round(sensitivity_std, 3),
                "min": round(min(sensitivity_data), 3) if sensitivity_data else 0.0,
                "max": round(max(sensitivity_data), 3) if sensitivity_data else 0.0,
            },
            "total_seeds_analyzed": len(volatility_data),
        }

    def generate_seed_flow_log(self) -> List[Dict[str, Any]]:
        """시드별 생성/진화 로그 추출"""
        logs = []

        for state_id, state in self.kernel.seed_registry.items():
            # Basic seed information
            log_entry = {
                "seed_id": state_id,
                "primary_emotion": state.emotion_rhythm.primary_emotion,
                "strategy": state.initial_strategy,
                "meta_sensitivity": round(state.meta_sensitivity, 3),
                "evolution_potential": round(state.evolution_potential, 3),
                "volatility_threshold": round(
                    state.emotion_rhythm.volatility_threshold, 3
                ),
                "rhythm_pattern": state.emotion_rhythm.rhythm_pattern,
                "signature_alignment": state.signature_alignment,
                "creation_timestamp": state.identity_trace.creation_timestamp,
            }

            # Add evolution history for this seed
            seed_evolutions = [
                event
                for event in self.kernel.evolution_history
                if event.get("seed_id") == state_id
            ]

            log_entry["evolution_count"] = len(seed_evolutions)
            log_entry["last_evolution"] = (
                seed_evolutions[-1] if seed_evolutions else None
            )

            # Calculate seed lifespan and activity
            if seed_evolutions:
                first_evolution = min(
                    seed_evolutions, key=lambda x: x.get("timestamp", "")
                )
                last_evolution = max(
                    seed_evolutions, key=lambda x: x.get("timestamp", "")
                )
                log_entry["first_evolution"] = first_evolution.get("timestamp")
                log_entry["last_evolution_time"] = last_evolution.get("timestamp")

            logs.append(log_entry)

        # Sort by creation timestamp
        logs.sort(key=lambda x: x.get("creation_timestamp", ""))

        return logs

    def analyze_seed_performance_patterns(self) -> Dict[str, Any]:
        """시드별 성능 패턴 분석"""
        performance_data = {
            "high_performers": [],
            "low_performers": [],
            "stable_seeds": [],
            "volatile_seeds": [],
        }

        evolution_frequency = {}
        sensitivity_performance = {}

        for state_id, state in self.kernel.seed_registry.items():
            # Count evolutions for this seed
            seed_evolutions = [
                event
                for event in self.kernel.evolution_history
                if event.get("seed_id") == state_id
            ]

            evolution_count = len(seed_evolutions)
            evolution_frequency[state_id] = evolution_count

            # Performance classification
            if state.evolution_potential > 0.7:
                performance_data["high_performers"].append(
                    {
                        "seed_id": state_id,
                        "evolution_potential": state.evolution_potential,
                        "evolution_count": evolution_count,
                    }
                )
            elif state.evolution_potential < 0.3:
                performance_data["low_performers"].append(
                    {
                        "seed_id": state_id,
                        "evolution_potential": state.evolution_potential,
                        "evolution_count": evolution_count,
                    }
                )

            # Stability classification
            if state.emotion_rhythm.volatility_threshold < 0.3:
                performance_data["stable_seeds"].append(
                    {
                        "seed_id": state_id,
                        "volatility": state.emotion_rhythm.volatility_threshold,
                        "evolution_count": evolution_count,
                    }
                )
            elif state.emotion_rhythm.volatility_threshold > 0.7:
                performance_data["volatile_seeds"].append(
                    {
                        "seed_id": state_id,
                        "volatility": state.emotion_rhythm.volatility_threshold,
                        "evolution_count": evolution_count,
                    }
                )

            # Sensitivity-performance correlation
            sensitivity_performance[state_id] = {
                "meta_sensitivity": state.meta_sensitivity,
                "evolution_potential": state.evolution_potential,
                "evolution_count": evolution_count,
            }

        # Calculate correlations
        if len(sensitivity_performance) > 1:
            sensitivities = [
                data["meta_sensitivity"] for data in sensitivity_performance.values()
            ]
            potentials = [
                data["evolution_potential"] for data in sensitivity_performance.values()
            ]

            # Simple correlation calculation
            correlation = (
                np.corrcoef(sensitivities, potentials)[0, 1]
                if len(sensitivities) > 1
                else 0.0
            )
        else:
            correlation = 0.0

        return {
            "performance_categories": performance_data,
            "evolution_frequency": evolution_frequency,
            "sensitivity_performance_correlation": round(correlation, 3),
            "total_seeds": len(self.kernel.seed_registry),
            "analysis_summary": {
                "high_performers_count": len(performance_data["high_performers"]),
                "low_performers_count": len(performance_data["low_performers"]),
                "stable_seeds_count": len(performance_data["stable_seeds"]),
                "volatile_seeds_count": len(performance_data["volatile_seeds"]),
            },
        }

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """종합 분석 보고서 생성"""
        evolution_trends = self.analyze_evolution_trends()
        volatility_analysis = self.detect_emotion_volatility_drift()
        performance_patterns = self.analyze_seed_performance_patterns()
        flow_logs = self.generate_seed_flow_log()

        # Summary statistics
        total_seeds = len(self.kernel.seed_registry)
        total_evolutions = len(self.kernel.evolution_history)
        avg_evolutions_per_seed = total_evolutions / max(total_seeds, 1)

        # Key insights
        insights = []

        if volatility_analysis.get("volatility_trend") == "increasing":
            insights.append("시드들의 감정 변동성이 증가 추세입니다")

        if evolution_trends.get("evolution_count", 0) > total_seeds * 2:
            insights.append("시드 진화가 활발하게 일어나고 있습니다")

        if performance_patterns.get("sensitivity_performance_correlation", 0) > 0.5:
            insights.append(
                "메타 민감도와 진화 잠재력 간에 강한 양의 상관관계가 있습니다"
            )

        return {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_seeds": total_seeds,
                "total_evolutions": total_evolutions,
                "avg_evolutions_per_seed": round(avg_evolutions_per_seed, 2),
            },
            "evolution_trends": evolution_trends,
            "volatility_analysis": volatility_analysis,
            "performance_patterns": performance_patterns,
            "key_insights": insights,
            "flow_logs": flow_logs[:10],  # First 10 for summary
            "total_flow_logs": len(flow_logs),
        }


# Convenience functions
def analyze_evolution_trends(kernel: EchoSeedKernel) -> Dict[str, Any]:
    """진화 기록 기반 감정, 전략 트렌드 분석 (편의 함수)"""
    analyzer = SeedReplayAnalyzer(kernel)
    return analyzer.analyze_evolution_trends()


def detect_emotion_volatility_drift(kernel: EchoSeedKernel) -> Dict[str, Any]:
    """감정 리듬 변동성 평균 드리프트 추정 (편의 함수)"""
    analyzer = SeedReplayAnalyzer(kernel)
    return analyzer.detect_emotion_volatility_drift()


def generate_seed_flow_log(kernel: EchoSeedKernel) -> List[Dict[str, Any]]:
    """시드별 생성/진화 로그 추출 (편의 함수)"""
    analyzer = SeedReplayAnalyzer(kernel)
    return analyzer.generate_seed_flow_log()


def generate_comprehensive_seed_report(kernel: EchoSeedKernel) -> Dict[str, Any]:
    """종합 시드 분석 보고서 생성 (편의 함수)"""
    analyzer = SeedReplayAnalyzer(kernel)
    return analyzer.generate_comprehensive_report()


if __name__ == "__main__":
    # Test code
    print("🔁 Seed Replay Analyzer 테스트")

    # Create test kernel with some data
    kernel = EchoSeedKernel()

    # Generate test seeds
    for i in range(5):
        seed = kernel.generate_initial_state(
            primary_emotion=["joy", "sadness", "anger", "curiosity", "neutral"][i],
            strategy=["empathetic", "analytical", "protective", "creative", "balanced"][
                i
            ],
        )

        # Simulate some evolution
        if i % 2 == 0:
            kernel.evolve_seed(seed.identity_trace.seed_id, "low_confidence")

    # Run analysis
    analyzer = SeedReplayAnalyzer(kernel)

    print("🔄 Evolution Trends:")
    trends = analyzer.analyze_evolution_trends()
    print(f"Total evolutions: {trends['evolution_count']}")
    print(f"Emotion patterns: {len(trends['emotion_patterns']['patterns'])}")

    print("\n📊 Volatility Analysis:")
    volatility = analyzer.detect_emotion_volatility_drift()
    print(f"Drift score: {volatility['drift_score']}")
    print(f"Trend: {volatility['volatility_trend']}")

    print("\n📈 Performance Patterns:")
    performance = analyzer.analyze_seed_performance_patterns()
    print(
        f"High performers: {performance['analysis_summary']['high_performers_count']}"
    )
    print(f"Correlation: {performance['sensitivity_performance_correlation']}")

    print("\n📋 Flow Log:")
    flow_log = analyzer.generate_seed_flow_log()
    print(f"Total seeds logged: {len(flow_log)}")

    print("\n📊 Comprehensive Report:")
    report = analyzer.generate_comprehensive_report()
    print(f"Key insights: {len(report['key_insights'])}")
    for insight in report["key_insights"]:
        print(f"- {insight}")

    print("✅ Seed Replay Analyzer 테스트 완료")
