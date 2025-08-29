# echo_engine/flow_visualizer.py
"""
📊 Flow Visualizer
- 시드 기반 판단 흐름, 감정-전략 흐름을 시각화하거나 .flow.yaml 포맷으로 변환
- ASCII 시각화, Streamlit 연동, YAML 내보내기 등 제공
"""

import yaml
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from echo_engine.seed_kernel import InitialState, EchoSeedKernel


class FlowVisualizer:
    def __init__(self):
        self.visualization_cache = {}

    def render_judgment_flow(self, state: InitialState, style: str = "detailed") -> str:
        """ASCII 방식으로 판단 흐름 시각화 출력"""

        if style == "simple":
            return self._render_simple_flow(state)
        elif style == "detailed":
            return self._render_detailed_flow(state)
        elif style == "compact":
            return self._render_compact_flow(state)
        else:
            return self._render_detailed_flow(state)

    def _render_simple_flow(self, state: InitialState) -> str:
        """간단한 ASCII 흐름"""
        return f"""
[{state.identity_trace.seed_id}] {state.emotion_rhythm.primary_emotion} → {state.initial_strategy}
"""

    def _render_detailed_flow(self, state: InitialState) -> str:
        """상세한 ASCII 판단 흐름 시각화"""
        rhythm_display = " → ".join(state.emotion_rhythm.rhythm_pattern)

        return f"""
    ╭─────────────────────────────────────────────────────────╮
    │ 🌱 SEED FLOW VISUALIZATION                              │
    ├─────────────────────────────────────────────────────────┤
    │ ID: {state.identity_trace.seed_id:<45} │
    │                                                         │
    │ 🎭 Emotion Layer:                                       │
    │    ├─ Primary: {state.emotion_rhythm.primary_emotion:<35} │
    │    ├─ Rhythm: {rhythm_display:<36} │
    │    └─ Volatility: {state.emotion_rhythm.volatility_threshold:<30.2f} │
    │                                                         │
    │ 🎯 Strategy Layer:                                      │
    │    └─ Strategy: {state.initial_strategy:<35} │
    │                                                         │
    │ 🧠 Meta Layer:                                          │
    │    ├─ Sensitivity: {state.meta_sensitivity:<30.2f} │
    │    ├─ Evolution Potential: {state.evolution_potential:<20.2f} │
    │    └─ Signature: {state.signature_alignment or 'None':<32} │
    │                                                         │
    │ ⏰ Identity:                                             │
    │    └─ Created: {state.identity_trace.creation_timestamp:<33} │
    ╰─────────────────────────────────────────────────────────╯
"""

    def _render_compact_flow(self, state: InitialState) -> str:
        """압축된 한 줄 형태"""
        return (
            f"[{state.identity_trace.seed_id}] "
            f"{state.emotion_rhythm.primary_emotion}({state.meta_sensitivity:.2f}) → "
            f"{state.initial_strategy}({state.evolution_potential:.2f}) | "
            f"{''.join(state.emotion_rhythm.rhythm_pattern[:3])}"
        )

    def render_multi_seed_flow(
        self, states: List[InitialState], style: str = "compact"
    ) -> str:
        """여러 시드의 흐름을 한번에 시각화"""
        if not states:
            return "No seeds to visualize."

        if style == "compact":
            flows = [self._render_compact_flow(state) for state in states]
            return "\n".join(flows)
        else:
            header = f"""
╭─────────────────────────────────────────────────────────╮
│ 🌱 MULTI-SEED FLOW VISUALIZATION ({len(states)} seeds)      │
╰─────────────────────────────────────────────────────────╯
"""
            flows = [self.render_judgment_flow(state, style) for state in states]
            return header + "\n".join(flows)

    def export_flow_yaml_from_seed(self, state: InitialState) -> Dict[str, Any]:
        """flow.yaml 호환 포맷 변환"""
        return {
            "seed_id": state.identity_trace.seed_id,
            "flow": {
                "emotion": {
                    "primary": state.emotion_rhythm.primary_emotion,
                    "rhythm": state.emotion_rhythm.rhythm_pattern,
                    "volatility": state.emotion_rhythm.volatility_threshold,
                },
                "strategy": state.initial_strategy,
                "meta": {
                    "sensitivity": state.meta_sensitivity,
                    "evolution_potential": state.evolution_potential,
                    "signature_alignment": state.signature_alignment,
                },
                "identity": {
                    "seed_id": state.identity_trace.seed_id,
                    "creation_timestamp": state.identity_trace.creation_timestamp,
                },
            },
            "export_timestamp": datetime.now().isoformat(),
        }

    def export_multi_seed_yaml(self, states: List[InitialState]) -> Dict[str, Any]:
        """여러 시드를 flow.yaml 포맷으로 내보내기"""
        flows = []
        for state in states:
            flows.append(self.export_flow_yaml_from_seed(state))

        return {
            "multi_seed_flow": {
                "total_seeds": len(states),
                "export_timestamp": datetime.now().isoformat(),
                "flows": flows,
            }
        }

    def generate_flow_statistics(self, states: List[InitialState]) -> Dict[str, Any]:
        """흐름 통계 생성"""
        if not states:
            return {"error": "No states provided"}

        # Emotion distribution
        emotions = [state.emotion_rhythm.primary_emotion for state in states]
        emotion_dist = {emotion: emotions.count(emotion) for emotion in set(emotions)}

        # Strategy distribution
        strategies = [state.initial_strategy for state in states]
        strategy_dist = {
            strategy: strategies.count(strategy) for strategy in set(strategies)
        }

        # Sensitivity statistics
        sensitivities = [state.meta_sensitivity for state in states]
        sensitivity_stats = {
            "mean": sum(sensitivities) / len(sensitivities),
            "min": min(sensitivities),
            "max": max(sensitivities),
            "range": max(sensitivities) - min(sensitivities),
        }

        # Evolution potential statistics
        potentials = [state.evolution_potential for state in states]
        potential_stats = {
            "mean": sum(potentials) / len(potentials),
            "min": min(potentials),
            "max": max(potentials),
            "range": max(potentials) - min(potentials),
        }

        # Signature alignment
        signatures = [
            state.signature_alignment for state in states if state.signature_alignment
        ]
        signature_dist = (
            {sig: signatures.count(sig) for sig in set(signatures)}
            if signatures
            else {}
        )
        unaligned_count = len([s for s in states if not s.signature_alignment])

        return {
            "total_seeds": len(states),
            "emotion_distribution": emotion_dist,
            "strategy_distribution": strategy_dist,
            "sensitivity_statistics": {
                k: round(v, 3) for k, v in sensitivity_stats.items()
            },
            "evolution_potential_statistics": {
                k: round(v, 3) for k, v in potential_stats.items()
            },
            "signature_distribution": signature_dist,
            "unaligned_seeds": unaligned_count,
            "alignment_rate": (
                round((len(signatures) / len(states)) * 100, 1) if states else 0.0
            ),
        }

    def create_flow_timeline(self, kernel: EchoSeedKernel) -> List[Dict[str, Any]]:
        """시드 생성 및 진화 타임라인 생성"""
        timeline = []

        # Add seed creations
        for state_id, state in kernel.seed_registry.items():
            timeline.append(
                {
                    "timestamp": state.identity_trace.creation_timestamp,
                    "event_type": "seed_creation",
                    "seed_id": state_id,
                    "emotion": state.emotion_rhythm.primary_emotion,
                    "strategy": state.initial_strategy,
                    "details": {
                        "meta_sensitivity": state.meta_sensitivity,
                        "evolution_potential": state.evolution_potential,
                        "signature_alignment": state.signature_alignment,
                    },
                }
            )

        # Add evolutions
        for evolution in kernel.evolution_history:
            timeline.append(
                {
                    "timestamp": evolution.get("timestamp", ""),
                    "event_type": "seed_evolution",
                    "seed_id": evolution.get("seed_id"),
                    "trigger": evolution.get("trigger"),
                    "changes": evolution.get("changes", {}),
                    "details": evolution,
                }
            )

        # Sort by timestamp
        timeline.sort(key=lambda x: x.get("timestamp", ""))

        return timeline

    def render_ascii_timeline(
        self, timeline: List[Dict[str, Any]], max_events: int = 20
    ) -> str:
        """ASCII 타임라인 렌더링"""
        if not timeline:
            return "No timeline events to display."

        display_timeline = (
            timeline[-max_events:] if len(timeline) > max_events else timeline
        )

        ascii_timeline = """
╭─────────────────────────────────────────────────────────╮
│ 📅 SEED TIMELINE                                        │
├─────────────────────────────────────────────────────────┤
"""

        for i, event in enumerate(display_timeline):
            event_type = event.get("event_type", "unknown")
            seed_id = event.get("seed_id", "unknown")
            timestamp = event.get("timestamp", "")[:19]  # Truncate timestamp

            if event_type == "seed_creation":
                emotion = event.get("emotion", "")
                strategy = event.get("strategy", "")
                ascii_timeline += f"│ 🌱 {timestamp} | {seed_id:<12} | Created: {emotion} → {strategy:<10} │\n"
            elif event_type == "seed_evolution":
                trigger = event.get("trigger", "unknown")
                ascii_timeline += (
                    f"│ 🔄 {timestamp} | {seed_id:<12} | Evolved: {trigger:<15} │\n"
                )
            else:
                ascii_timeline += (
                    f"│ ❓ {timestamp} | {seed_id:<12} | {event_type:<20} │\n"
                )

        if len(timeline) > max_events:
            ascii_timeline += f"│ ... ({len(timeline) - max_events} more events)                                 │\n"

        ascii_timeline += "╰─────────────────────────────────────────────────────────╯"

        return ascii_timeline

    def streamlit_visualize_judgment(self, state: InitialState):
        """Streamlit 시각화 (확장용)"""
        try:
            import streamlit as st
            import plotly.graph_objects as go
            import plotly.express as px

            st.subheader(f"🌱 시드 흐름 시각화 - {state.identity_trace.seed_id}")

            # ASCII 표시
            st.text(self.render_judgment_flow(state))

            # Metrics display
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Meta Sensitivity", f"{state.meta_sensitivity:.2f}")
            with col2:
                st.metric("Evolution Potential", f"{state.evolution_potential:.2f}")
            with col3:
                st.metric(
                    "Volatility", f"{state.emotion_rhythm.volatility_threshold:.2f}"
                )

            # Rhythm visualization
            if state.emotion_rhythm.rhythm_pattern:
                st.subheader("🎵 Emotion Rhythm")
                rhythm_text = " → ".join(state.emotion_rhythm.rhythm_pattern)
                st.write(rhythm_text)

                # Simple bar chart of rhythm intensity (placeholder)
                rhythm_data = [
                    {"Step": i + 1, "Intensity": 0.5 + (i * 0.1)}
                    for i in range(len(state.emotion_rhythm.rhythm_pattern))
                ]

                if rhythm_data:
                    fig = px.bar(
                        rhythm_data,
                        x="Step",
                        y="Intensity",
                        title="Rhythm Intensity Pattern",
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # YAML export
            with st.expander("📄 YAML Export"):
                yaml_data = self.export_flow_yaml_from_seed(state)
                st.code(yaml.dump(yaml_data, default_flow_style=False), language="yaml")

        except ImportError:
            st.error("Streamlit not available for visualization")

    def streamlit_visualize_multi_seeds(self, states: List[InitialState]):
        """Multiple seeds Streamlit visualization"""
        try:
            import streamlit as st
            import pandas as pd
            import plotly.express as px

            if not states:
                st.warning("No seeds to visualize")
                return

            st.subheader(f"🌱 Multi-Seed Visualization ({len(states)} seeds)")

            # Statistics
            stats = self.generate_flow_statistics(states)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Seeds", stats["total_seeds"])
            with col2:
                st.metric("Alignment Rate", f"{stats['alignment_rate']:.1f}%")
            with col3:
                avg_sensitivity = stats["sensitivity_statistics"]["mean"]
                st.metric("Avg Sensitivity", f"{avg_sensitivity:.2f}")

            # Distribution charts
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("😊 Emotion Distribution")
                if stats["emotion_distribution"]:
                    emotion_df = pd.DataFrame(
                        list(stats["emotion_distribution"].items()),
                        columns=["Emotion", "Count"],
                    )
                    fig1 = px.pie(emotion_df, values="Count", names="Emotion")
                    st.plotly_chart(fig1, use_container_width=True)

            with col2:
                st.subheader("🎯 Strategy Distribution")
                if stats["strategy_distribution"]:
                    strategy_df = pd.DataFrame(
                        list(stats["strategy_distribution"].items()),
                        columns=["Strategy", "Count"],
                    )
                    fig2 = px.pie(strategy_df, values="Count", names="Strategy")
                    st.plotly_chart(fig2, use_container_width=True)

            # Detailed seed table
            st.subheader("📋 Seed Details")
            seed_data = []
            for state in states:
                seed_data.append(
                    {
                        "Seed ID": state.identity_trace.seed_id,
                        "Emotion": state.emotion_rhythm.primary_emotion,
                        "Strategy": state.initial_strategy,
                        "Sensitivity": f"{state.meta_sensitivity:.2f}",
                        "Evolution Potential": f"{state.evolution_potential:.2f}",
                        "Signature": state.signature_alignment or "None",
                    }
                )

            seed_df = pd.DataFrame(seed_data)
            st.dataframe(seed_df, use_container_width=True)

        except ImportError:
            st.error("Required libraries not available for visualization")


# Convenience functions
def render_judgment_flow(state: InitialState, style: str = "detailed") -> str:
    """ASCII 방식으로 판단 흐름 시각화 출력 (편의 함수)"""
    visualizer = FlowVisualizer()
    return visualizer.render_judgment_flow(state, style)


def export_flow_yaml_from_seed(state: InitialState) -> Dict[str, Any]:
    """flow.yaml 호환 포맷 변환 (편의 함수)"""
    visualizer = FlowVisualizer()
    return visualizer.export_flow_yaml_from_seed(state)


def streamlit_visualize_judgment(state: InitialState):
    """Streamlit 시각화 (편의 함수)"""
    visualizer = FlowVisualizer()
    return visualizer.streamlit_visualize_judgment(state)


def generate_flow_timeline(kernel: EchoSeedKernel) -> List[Dict[str, Any]]:
    """시드 생성 및 진화 타임라인 생성 (편의 함수)"""
    visualizer = FlowVisualizer()
    return visualizer.create_flow_timeline(kernel)


if __name__ == "__main__":
    # Test code
    from echo_engine.seed_kernel import EchoSeedKernel

    print("📊 Flow Visualizer 테스트")

    # Create test kernel and generate seeds
    kernel = EchoSeedKernel()
    test_seeds = []

    for i in range(3):
        seed = kernel.generate_initial_state(
            primary_emotion=["joy", "curiosity", "sadness"][i],
            strategy=["empathetic", "analytical", "protective"][i],
        )
        test_seeds.append(seed)

    visualizer = FlowVisualizer()

    print("🎭 Single Seed Visualization:")
    print(visualizer.render_judgment_flow(test_seeds[0], "detailed"))

    print("\n🌱 Multi-Seed Compact View:")
    print(visualizer.render_multi_seed_flow(test_seeds, "compact"))

    print("\n📊 Flow Statistics:")
    stats = visualizer.generate_flow_statistics(test_seeds)
    print(f"Total seeds: {stats['total_seeds']}")
    print(f"Emotions: {stats['emotion_distribution']}")
    print(f"Strategies: {stats['strategy_distribution']}")

    print("\n📅 Timeline:")
    timeline = visualizer.create_flow_timeline(kernel)
    print(visualizer.render_ascii_timeline(timeline))

    print("\n📄 YAML Export:")
    yaml_export = visualizer.export_flow_yaml_from_seed(test_seeds[0])
    print(yaml.dump(yaml_export, default_flow_style=False)[:200] + "...")

    print("✅ Flow Visualizer 테스트 완료")
