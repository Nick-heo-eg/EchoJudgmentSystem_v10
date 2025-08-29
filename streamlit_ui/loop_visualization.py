# loop_visualization.py - 8대 루프 실행 시각화 모듈
# Streamlit Visualization for 8-Loop System

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys
import os

# Add echo_engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from echo_engine.loop_executor import LoopExecutor, get_available_loops
from echo_engine.signature_loop_bridge import (
    SignatureLoopBridge,
    analyze_signature_loop_compatibility,
)
from echo_engine.loop_meta_integrator import (
    LoopMetaIntegrator,
    execute_integrated_judgment,
    get_system_performance,
)


class LoopVisualizationApp:
    def __init__(self):
        self.loop_executor = LoopExecutor()
        self.signature_bridge = SignatureLoopBridge()
        self.meta_integrator = LoopMetaIntegrator()

        # Initialize session state
        if "execution_history" not in st.session_state:
            st.session_state.execution_history = []
        if "loop_stats" not in st.session_state:
            st.session_state.loop_stats = {}

    def run(self):
        """Main Streamlit app"""
        st.set_page_config(
            page_title="EchoJudgment v10 - 8대 루프 시각화",
            page_icon="🔄",
            layout="wide",
        )

        st.title("🔄 EchoJudgment v10 - 8대 루프 시스템")
        st.markdown("**8-Loop Execution & Visualization Dashboard**")

        # Sidebar
        self.render_sidebar()

        # Main content
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "🚀 루프 실행",
                "📊 성능 대시보드",
                "🧬 시그니처 분석",
                "📈 실행 히스토리",
                "⚙️ 시스템 설정",
            ]
        )

        with tab1:
            self.render_loop_execution()

        with tab2:
            self.render_performance_dashboard()

        with tab3:
            self.render_signature_analysis()

        with tab4:
            self.render_execution_history()

        with tab5:
            self.render_system_settings()

    def render_sidebar(self):
        """Sidebar with quick stats and controls"""
        st.sidebar.header("🎛️ 제어판")

        # Available loops
        available_loops = get_available_loops()
        st.sidebar.subheader("📋 사용 가능한 루프")
        for loop_id in available_loops:
            st.sidebar.text(f"• {loop_id}")

        # Quick stats
        if st.session_state.execution_history:
            st.sidebar.subheader("📊 빠른 통계")
            total_executions = len(st.session_state.execution_history)
            recent_success_rate = sum(
                1
                for r in st.session_state.execution_history[-10:]
                if r.get("loop_result", {}).get("success", False)
            ) / min(10, total_executions)

            st.sidebar.metric("총 실행 횟수", total_executions)
            st.sidebar.metric("최근 성공률", f"{recent_success_rate:.1%}")

        # System actions
        st.sidebar.subheader("🔧 시스템 액션")
        if st.sidebar.button("🔄 히스토리 새로고침"):
            st.rerun()

        if st.sidebar.button("🗑️ 히스토리 초기화"):
            st.session_state.execution_history = []
            st.session_state.loop_stats = {}
            st.success("히스토리가 초기화되었습니다!")
            st.rerun()

    def render_loop_execution(self):
        """Loop execution interface"""
        st.header("🚀 루프 실행 인터페이스")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Input form
            with st.form("loop_execution_form"):
                st.subheader("📝 입력")

                input_text = st.text_area(
                    "판단할 텍스트를 입력하세요:",
                    placeholder="복잡한 상황에서의 감정적 결정이 필요합니다...",
                    height=100,
                )

                signature_id = st.selectbox(
                    "시그니처 선택:",
                    ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"],
                    help="판단에 사용할 시그니처를 선택하세요",
                )

                # Advanced options
                with st.expander("🔧 고급 옵션"):
                    manual_loop = st.selectbox(
                        "수동 루프 선택 (선택사항):",
                        ["자동 선택"] + get_available_loops(),
                    )

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        complexity = st.slider("복잡도", 0.0, 1.0, 0.5)
                    with col_b:
                        uncertainty = st.slider("불확실성", 0.0, 1.0, 0.5)
                    with col_c:
                        emotional_intensity = st.slider("감정 강도", 0.0, 1.0, 0.5)

                    learning_enabled = st.checkbox("강화학습 활성화", value=True)

                submitted = st.form_submit_button("🎯 판단 실행", type="primary")

        with col2:
            # Real-time loop selection preview
            if input_text and signature_id:
                st.subheader("🎯 루프 선택 미리보기")

                context = {
                    "complexity": complexity,
                    "uncertainty": uncertainty,
                    "emotional_intensity": emotional_intensity,
                }

                predicted_loop = self.signature_bridge.determine_optimal_loop(
                    signature_id, context
                )

                st.info(f"**예상 루프:** {predicted_loop}")

                # Loop phases preview
                loop_config = self.loop_executor.get_loop_by_id(predicted_loop)
                if loop_config:
                    st.write("**실행 단계:**")
                    phases = loop_config.get("phases", [])
                    for i, phase in enumerate(phases, 1):
                        st.write(f"{i}. {phase}")

        # Execute loop
        if submitted and input_text:
            with st.spinner("🔄 루프 실행 중..."):
                try:
                    context = {
                        "complexity": complexity,
                        "uncertainty": uncertainty,
                        "emotional_intensity": emotional_intensity,
                    }

                    if manual_loop != "자동 선택":
                        # Manual loop execution
                        loop_result = self.loop_executor.execute_loop(
                            manual_loop, context, signature_id=signature_id
                        )
                        result = {
                            "input_text": input_text,
                            "signature_id": signature_id,
                            "selected_loop": manual_loop,
                            "selection_method": "manual",
                            "loop_result": loop_result,
                            "context": context,
                            "timestamp": datetime.now().isoformat(),
                        }
                    else:
                        # Integrated execution
                        result = execute_integrated_judgment(
                            input_text, signature_id, context
                        )

                    # Store in session state
                    st.session_state.execution_history.append(result)

                    # Display results
                    self.display_execution_result(result)

                except Exception as e:
                    st.error(f"실행 중 오류 발생: {str(e)}")

    def display_execution_result(self, result: Dict):
        """Display execution result"""
        st.success("✅ 루프 실행 완료!")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "선택된 루프",
                result.get("selected_loop", "Unknown"),
                delta=result.get("selection_method", ""),
            )

        with col2:
            success = result.get("loop_result", {}).get("success", False)
            st.metric("실행 성공", "✅ 성공" if success else "❌ 실패")

        with col3:
            exec_time = result.get("loop_result", {}).get("execution_time", 0.0)
            st.metric("실행 시간", f"{exec_time:.2f}초")

        # Detailed results
        with st.expander("📋 상세 결과"):
            st.json(result.get("loop_result", {}).get("output", {}))

        # Execution timeline
        if result.get("loop_result", {}).get("phases_executed"):
            st.subheader("🔄 실행 단계")
            phases = result["loop_result"]["phases_executed"]

            # Create timeline visualization
            fig = go.Figure()

            for i, phase in enumerate(phases):
                fig.add_trace(
                    go.Scatter(
                        x=[i, i + 1],
                        y=[0, 0],
                        mode="lines+markers+text",
                        text=[phase, ""],
                        textposition="top center",
                        line=dict(width=4, color="royalblue"),
                        marker=dict(size=10, color="lightblue"),
                    )
                )

            fig.update_layout(
                title="루프 실행 단계",
                showlegend=False,
                height=200,
                xaxis=dict(showticklabels=False),
                yaxis=dict(showticklabels=False),
            )

            st.plotly_chart(fig, use_container_width=True)

    def render_performance_dashboard(self):
        """Performance dashboard"""
        st.header("📊 성능 대시보드")

        if not st.session_state.execution_history:
            st.info("실행 히스토리가 없습니다. 먼저 루프를 실행해보세요!")
            return

        # Performance metrics
        performance = get_system_performance()

        if performance.get("message"):
            st.warning(performance["message"])
            return

        # Overall metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("총 실행 횟수", performance.get("total_executions", 0))

        with col2:
            success_rate = performance.get("overall_success_rate", 0)
            st.metric("전체 성공률", f"{success_rate:.1%}")

        with col3:
            confidence = performance.get("overall_confidence", 0)
            st.metric("평균 신뢰도", f"{confidence:.2f}")

        with col4:
            recent_count = performance.get("recent_executions", 0)
            st.metric("최근 실행", recent_count)

        # Loop performance chart
        st.subheader("🔄 루프별 성능")

        loop_perf = performance.get("loop_performance", {})
        if loop_perf:
            loop_data = []
            for loop_id, stats in loop_perf.items():
                loop_data.append(
                    {
                        "Loop": loop_id,
                        "실행 횟수": stats["count"],
                        "성공률": stats["success_rate"],
                        "평균 신뢰도": stats["avg_confidence"],
                    }
                )

            df_loops = pd.DataFrame(loop_data)

            col1, col2 = st.columns(2)

            with col1:
                fig1 = px.bar(
                    df_loops,
                    x="Loop",
                    y="성공률",
                    title="루프별 성공률",
                    color="성공률",
                    color_continuous_scale="RdYlGn",
                )
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                fig2 = px.scatter(
                    df_loops,
                    x="실행 횟수",
                    y="평균 신뢰도",
                    text="Loop",
                    title="실행 횟수 vs 신뢰도",
                    size="성공률",
                )
                fig2.update_traces(textposition="top center")
                st.plotly_chart(fig2, use_container_width=True)

        # Signature performance
        st.subheader("🧬 시그니처별 성능")

        sig_perf = performance.get("signature_performance", {})
        if sig_perf:
            sig_data = []
            for sig_id, stats in sig_perf.items():
                sig_data.append(
                    {
                        "Signature": sig_id,
                        "실행 횟수": stats["count"],
                        "성공률": stats["success_rate"],
                        "평균 신뢰도": stats["avg_confidence"],
                    }
                )

            df_sigs = pd.DataFrame(sig_data)

            fig3 = px.bar(
                df_sigs,
                x="Signature",
                y=["성공률", "평균 신뢰도"],
                title="시그니처별 성능 비교",
                barmode="group",
            )
            st.plotly_chart(fig3, use_container_width=True)

    def render_signature_analysis(self):
        """Signature analysis interface"""
        st.header("🧬 시그니처 분석")

        signature_id = st.selectbox(
            "분석할 시그니처:",
            ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"],
        )

        if st.button("🔍 호환성 분석 실행"):
            with st.spinner("분석 중..."):
                compatibility = analyze_signature_loop_compatibility(signature_id)

                st.subheader(f"🎯 {signature_id} 루프 호환성 분석")

                # Recommended loops
                st.success(
                    f"**추천 루프:** {', '.join(compatibility['recommended_loops'])}"
                )

                # Compatibility matrix
                comp_data = []
                for loop_id, data in compatibility["loop_compatibility"].items():
                    comp_data.append(
                        {
                            "Loop": loop_id,
                            "민감도": data["sensitivity"],
                            "설명": data["description"],
                            "단계": len(data["phases"]),
                        }
                    )

                df_comp = pd.DataFrame(comp_data)

                # Visualization
                col1, col2 = st.columns(2)

                with col1:
                    fig1 = px.bar(
                        df_comp,
                        x="Loop",
                        y="민감도",
                        title="루프별 민감도",
                        color="민감도",
                        color_continuous_scale="viridis",
                    )
                    st.plotly_chart(fig1, use_container_width=True)

                with col2:
                    fig2 = px.scatter(
                        df_comp,
                        x="단계",
                        y="민감도",
                        text="Loop",
                        title="단계 수 vs 민감도",
                    )
                    fig2.update_traces(textposition="top center")
                    st.plotly_chart(fig2, use_container_width=True)

                # Detailed table
                st.subheader("📋 상세 호환성 테이블")
                st.dataframe(df_comp, use_container_width=True)

    def render_execution_history(self):
        """Execution history visualization"""
        st.header("📈 실행 히스토리")

        if not st.session_state.execution_history:
            st.info("실행 히스토리가 없습니다.")
            return

        # History table
        history_data = []
        for i, record in enumerate(st.session_state.execution_history):
            history_data.append(
                {
                    "ID": i + 1,
                    "시간": record.get("timestamp", "")[:19],
                    "시그니처": record.get("signature_id", ""),
                    "루프": record.get("selected_loop", ""),
                    "선택방법": record.get("selection_method", ""),
                    "성공": (
                        "✅" if record.get("loop_result", {}).get("success") else "❌"
                    ),
                    "실행시간": f"{record.get('loop_result', {}).get('execution_time', 0):.2f}s",
                }
            )

        df_history = pd.DataFrame(history_data)

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            sig_filter = st.multiselect(
                "시그니처 필터:",
                df_history["시그니처"].unique(),
                default=df_history["시그니처"].unique(),
            )

        with col2:
            loop_filter = st.multiselect(
                "루프 필터:",
                df_history["루프"].unique(),
                default=df_history["루프"].unique(),
            )

        with col3:
            success_filter = st.selectbox("성공 여부:", ["전체", "성공만", "실패만"])

        # Apply filters
        filtered_df = df_history[
            (df_history["시그니처"].isin(sig_filter))
            & (df_history["루프"].isin(loop_filter))
        ]

        if success_filter == "성공만":
            filtered_df = filtered_df[filtered_df["성공"] == "✅"]
        elif success_filter == "실패만":
            filtered_df = filtered_df[filtered_df["성공"] == "❌"]

        # Display table
        st.dataframe(filtered_df, use_container_width=True)

        # Timeline chart
        if len(filtered_df) > 1:
            st.subheader("📊 시간별 성공률")

            # Convert execution time to numeric
            filtered_df["실행시간_숫자"] = (
                filtered_df["실행시간"].str.replace("s", "").astype(float)
            )
            filtered_df["성공_숫자"] = (filtered_df["성공"] == "✅").astype(int)

            fig = px.line(
                filtered_df,
                x="ID",
                y="성공_숫자",
                title="실행 순서별 성공 여부",
                markers=True,
            )
            fig.update_yaxis(ticktext=["실패", "성공"], tickvals=[0, 1])
            st.plotly_chart(fig, use_container_width=True)

    def render_system_settings(self):
        """System settings interface"""
        st.header("⚙️ 시스템 설정")

        # Loop configuration
        st.subheader("🔄 루프 설정")

        available_loops = get_available_loops()
        st.write(f"사용 가능한 루프: {len(available_loops)}개")

        for loop_id in available_loops:
            with st.expander(f"🔧 {loop_id} 설정"):
                loop_config = self.loop_executor.get_loop_by_id(loop_id)
                if loop_config:
                    st.write(f"**설명:** {loop_config.get('description', 'N/A')}")
                    st.write(f"**단계:** {', '.join(loop_config.get('phases', []))}")

        # System diagnostics
        st.subheader("🔍 시스템 진단")

        if st.button("🧪 시스템 테스트 실행"):
            with st.spinner("테스트 중..."):
                test_results = self._run_system_diagnostics()

                for component, result in test_results.items():
                    if result["status"] == "ok":
                        st.success(f"✅ {component}: {result['message']}")
                    else:
                        st.error(f"❌ {component}: {result['message']}")

        # Export/Import
        st.subheader("📤 데이터 관리")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 히스토리 내보내기"):
                if st.session_state.execution_history:
                    export_data = {
                        "export_time": datetime.now().isoformat(),
                        "total_records": len(st.session_state.execution_history),
                        "history": st.session_state.execution_history,
                    }

                    st.download_button(
                        "💾 JSON 파일 다운로드",
                        data=json.dumps(export_data, ensure_ascii=False, indent=2),
                        file_name=f"echo_loop_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                    )
                else:
                    st.warning("내보낼 히스토리가 없습니다.")

        with col2:
            uploaded_file = st.file_uploader("📁 히스토리 가져오기", type="json")
            if uploaded_file:
                try:
                    import_data = json.load(uploaded_file)
                    if "history" in import_data:
                        st.session_state.execution_history = import_data["history"]
                        st.success(
                            f"✅ {len(import_data['history'])}개 기록을 가져왔습니다!"
                        )
                        st.rerun()
                except Exception as e:
                    st.error(f"파일 가져오기 실패: {e}")

    def _run_system_diagnostics(self) -> Dict:
        """Run system diagnostics"""
        results = {}

        try:
            # Test loop executor
            test_context = {"complexity": 0.5, "uncertainty": 0.5}
            test_result = self.loop_executor.execute_loop("JUDGE", test_context)
            results["LoopExecutor"] = {
                "status": "ok" if test_result.success else "error",
                "message": (
                    "루프 실행기 정상 작동"
                    if test_result.success
                    else f"오류: {test_result.error_message}"
                ),
            }
        except Exception as e:
            results["LoopExecutor"] = {"status": "error", "message": str(e)}

        try:
            # Test signature bridge
            test_loop = self.signature_bridge.determine_optimal_loop(
                "Echo-Aurora", test_context
            )
            results["SignatureBridge"] = {
                "status": "ok",
                "message": f"시그니처 브리지 정상 작동 (추천 루프: {test_loop})",
            }
        except Exception as e:
            results["SignatureBridge"] = {"status": "error", "message": str(e)}

        try:
            # Test meta integrator
            performance = get_system_performance()
            results["MetaIntegrator"] = {
                "status": "ok",
                "message": "메타 통합기 정상 작동",
            }
        except Exception as e:
            results["MetaIntegrator"] = {"status": "error", "message": str(e)}

        return results


def main():
    """Main function to run the Streamlit app"""
    app = LoopVisualizationApp()
    app.run()


if __name__ == "__main__":
    main()
