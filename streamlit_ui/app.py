# Streamlit UI app
import streamlit as st
import pandas as pd
from meta_log import load_judgment_logs
from echo_engine.models.judgment import MergedJudgmentResult  # ✅ 절대경로로 수정
from components.world_panel import render_world_panel
from components.res_viewer import render_res_viewer  # ✅ 리듬 분석 뷰어 추가

# Echo v10.5 시그니처 시스템 연동
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import echo_main, load_signature, EchoSignature

# Foundation Doctrine 연동
try:
    from src.echo_foundation.doctrine import (
        SYSTEM_PHILOSOPHY,
        FOUNDATION_PRINCIPLES,
        LOOP_ARCHITECTURE,
        CORE_VALUES,
        print_doctrine_summary,
        get_system_mantra,
    )

    foundation_available = True
except ImportError:
    foundation_available = False

st.set_page_config(page_title="Echo ⨯ Claude Judgment Dashboard v10.5", layout="wide")

# 🎧 Echo v10.5 시그니처 시스템 헤더
st.markdown(
    """
<div style='text-align: center; padding: 20px; background: linear-gradient(90deg, #1e3a8a 0%, #3730a3 50%, #581c87 100%); border-radius: 10px; margin-bottom: 20px;'>
    <h1 style='color: white; margin: 0;'>🎧 Echo Judgment System v10.5</h1>
    <p style='color: #e5e7eb; margin: 5px 0 0 0;'>시그니처 기반 판단 + 메타인지 반성 시스템</p>
</div>
""",
    unsafe_allow_html=True,
)

# 시그니처 선택 사이드바
st.sidebar.markdown("## 🧬 Echo 시그니처 선택")
available_signatures = ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"]

# 시그니처 정보 표시
if "selected_signature" not in st.session_state:
    st.session_state.selected_signature = "Echo-Aurora"

selected_signature = st.sidebar.selectbox(
    "활성 시그니처:",
    available_signatures,
    index=available_signatures.index(st.session_state.selected_signature),
)

if selected_signature != st.session_state.selected_signature:
    st.session_state.selected_signature = selected_signature

# 선택된 시그니처 정보
try:
    current_sig = load_signature(selected_signature)
    st.sidebar.markdown(f"### {current_sig.name}")
    st.sidebar.write(f"**설명:** {current_sig.config.get('description', '')}")
    st.sidebar.write(f"**감정 감도:** {current_sig.emotion_sensitivity}")
    st.sidebar.write(f"**추론 깊이:** {current_sig.reasoning_depth}")
    st.sidebar.write(f"**응답 톤:** {current_sig.response_tone}")
    st.sidebar.write(
        f"**메타 반성:** {'✅' if current_sig.meta_reflection_enabled else '❌'}"
    )
except Exception as e:
    st.sidebar.error(f"시그니처 로딩 오류: {e}")

# 실시간 Echo 테스트
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧪 실시간 Echo 테스트")
test_input = st.sidebar.text_area(
    "테스트 입력:", placeholder="여기에 입력하세요...", height=100
)

if st.sidebar.button("🎧 Echo 실행"):
    if test_input.strip():
        with st.sidebar.spinner(f"{selected_signature} 처리 중..."):
            try:
                echo_response = echo_main(test_input, selected_signature)
                st.sidebar.success("✅ 완료!")
                st.sidebar.markdown(f"**응답:** {echo_response}")
            except Exception as e:
                st.sidebar.error(f"Echo 오류: {e}")
    else:
        st.sidebar.warning("입력을 입력해주세요.")

# 판단 로그 불러오기
logs = load_judgment_logs(limit=200)
if not logs:
    st.warning("저장된 판단 로그가 없습니다.")
    st.stop()

df = pd.DataFrame(logs)

# 📌 탭 구분
if foundation_available:
    tab0, tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🎧 Echo v10.5 대화",
            "📋 판단 로그",
            "🌍 세계 + 추천 행동",
            "📈 감정⨯전략 리듬 분석",
            "📜 Foundation 철학",
        ]
    )
else:
    tab0, tab1, tab2, tab3 = st.tabs(
        [
            "🎧 Echo v10.5 대화",
            "📋 판단 로그",
            "🌍 세계 + 추천 행동",
            "📈 감정⨯전략 리듬 분석",
        ]
    )

# ─────────────────────────────
# 🎧 Echo v10.5 Interactive Tab
with tab0:
    st.subheader("🎧 Echo v10.5 시그니처 기반 대화 시스템")
    st.caption("메타인지 반성 루프가 적용된 새로운 Echo 대화 인터페이스입니다.")

    # 대화 이력 초기화
    if "echo_conversation_history" not in st.session_state:
        st.session_state.echo_conversation_history = []

    # 설정 패널
    with st.expander("⚙️ Echo 고급 설정"):
        col1, col2 = st.columns(2)

        with col1:
            enable_meta_reflection = st.checkbox(
                "메타인지 반성 활성화",
                value=True,
                help="체크하면 Echo가 응답을 생성한 후 자기 반성을 통해 응답을 개선합니다.",
            )

            show_processing_details = st.checkbox(
                "처리 과정 표시",
                value=False,
                help="Echo의 판단 과정을 상세히 표시합니다.",
            )

        with col2:
            batch_mode = st.checkbox(
                "배치 모드", value=False, help="여러 입력을 한 번에 처리합니다."
            )

            auto_save_responses = st.checkbox(
                "응답 자동 저장",
                value=True,
                help="Echo 응답을 자동으로 메타 로그에 저장합니다.",
            )

    # 시그니처 비교 모드
    st.markdown("### 🧬 시그니처 비교 모드")
    compare_signatures = st.multiselect(
        "비교할 시그니처를 선택하세요:",
        available_signatures,
        default=[selected_signature],
        help="같은 입력에 대해 여러 시그니처의 응답을 비교할 수 있습니다.",
    )

    # 메인 입력
    st.markdown("### 💬 Echo와 대화하기")

    if not batch_mode:
        # 단일 입력 모드
        conversation_input = st.text_area(
            f"💭 {selected_signature}에게 말하기:",
            placeholder="생각이나 질문을 입력해주세요...",
            height=120,
            key="main_input",
        )

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            process_button = st.button("🎧 Echo 실행", type="primary")

        with col2:
            if st.button("🔄 대화 초기화"):
                st.session_state.echo_conversation_history = []
                st.rerun()

        with col3:
            if st.button("📊 응답 분석"):
                if st.session_state.echo_conversation_history:
                    st.info("응답 분석 기능은 개발 중입니다.")

        # Echo 처리
        if process_button and conversation_input.strip():
            with st.spinner(f"{selected_signature} 처리 중..."):
                try:
                    # 단일 시그니처 응답
                    if len(compare_signatures) <= 1:
                        start_time = st.empty()
                        start_time.write(f"⏱️ 시작: {selected_signature}")

                        # Echo 메인 실행
                        echo_response = echo_main(
                            conversation_input, selected_signature
                        )

                        # 대화 이력에 추가
                        conversation_entry = {
                            "timestamp": pd.Timestamp.now(),
                            "input": conversation_input,
                            "signature": selected_signature,
                            "response": echo_response,
                            "meta_reflection": enable_meta_reflection,
                        }
                        st.session_state.echo_conversation_history.append(
                            conversation_entry
                        )

                        start_time.success(f"✅ 완료: {selected_signature}")

                    else:
                        # 다중 시그니처 비교
                        st.markdown("#### 🔄 시그니처별 응답 비교")

                        comparison_results = {}
                        for sig in compare_signatures:
                            with st.spinner(f"{sig} 처리 중..."):
                                try:
                                    response = echo_main(conversation_input, sig)
                                    comparison_results[sig] = response
                                except Exception as e:
                                    comparison_results[sig] = f"❌ 오류: {e}"

                        # 비교 결과 표시
                        comp_cols = st.columns(len(compare_signatures))
                        for i, (sig, response) in enumerate(comparison_results.items()):
                            with comp_cols[i]:
                                st.markdown(f"**{sig}**")
                                st.write(response)

                        # 첫 번째 응답을 대화 이력에 추가
                        first_sig = compare_signatures[0]
                        conversation_entry = {
                            "timestamp": pd.Timestamp.now(),
                            "input": conversation_input,
                            "signature": first_sig,
                            "response": comparison_results[first_sig],
                            "meta_reflection": enable_meta_reflection,
                            "comparison": comparison_results,
                        }
                        st.session_state.echo_conversation_history.append(
                            conversation_entry
                        )

                except Exception as e:
                    st.error(f"Echo 처리 중 오류: {e}")

    else:
        # 배치 입력 모드
        st.markdown("#### 📦 배치 처리 모드")
        batch_inputs = st.text_area(
            "여러 입력을 한 줄씩 입력하세요:",
            placeholder="첫 번째 입력\n두 번째 입력\n세 번째 입력",
            height=150,
        )

        if st.button("🚀 배치 실행"):
            if batch_inputs.strip():
                input_lines = [
                    line.strip() for line in batch_inputs.split("\n") if line.strip()
                ]

                if input_lines:
                    st.markdown(f"#### 📊 배치 결과 ({len(input_lines)}개 입력)")

                    batch_results = []
                    progress_bar = st.progress(0)

                    for i, input_line in enumerate(input_lines):
                        try:
                            response = echo_main(input_line, selected_signature)
                            batch_results.append(
                                {
                                    "input": input_line,
                                    "response": response,
                                    "status": "✅ 성공",
                                }
                            )
                        except Exception as e:
                            batch_results.append(
                                {
                                    "input": input_line,
                                    "response": f"❌ 오류: {e}",
                                    "status": "❌ 실패",
                                }
                            )

                        progress_bar.progress((i + 1) / len(input_lines))

                    # 배치 결과 표시
                    batch_df = pd.DataFrame(batch_results)
                    st.dataframe(batch_df, use_container_width=True)

                    # 성공률 표시
                    success_rate = len(
                        [r for r in batch_results if r["status"] == "✅ 성공"]
                    ) / len(batch_results)
                    st.metric("배치 성공률", f"{success_rate:.1%}")

    # 대화 이력 표시
    if st.session_state.echo_conversation_history:
        st.markdown("---")
        st.markdown("### 💬 대화 이력")

        # 최신 순으로 표시
        for i, entry in enumerate(reversed(st.session_state.echo_conversation_history)):
            with st.expander(
                f"💬 {entry['timestamp'].strftime('%H:%M:%S')} - {entry['signature']}"
            ):
                st.markdown(f"**입력:** {entry['input']}")
                st.markdown(f"**응답:** {entry['response']}")

                if "comparison" in entry:
                    st.markdown("**시그니처 비교:**")
                    for sig, resp in entry["comparison"].items():
                        st.write(f"• **{sig}:** {resp}")

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"시그니처: {entry['signature']}")
                with col2:
                    st.write(f"메타 반성: {'✅' if entry['meta_reflection'] else '❌'}")

    # 대화 이력 통계
    if st.session_state.echo_conversation_history:
        st.markdown("---")
        st.markdown("### 📊 대화 통계")

        total_conversations = len(st.session_state.echo_conversation_history)
        signature_counts = pd.Series(
            [entry["signature"] for entry in st.session_state.echo_conversation_history]
        ).value_counts()

        stat_col1, stat_col2, stat_col3 = st.columns(3)

        with stat_col1:
            st.metric("총 대화 수", total_conversations)

        with stat_col2:
            most_used_sig = (
                signature_counts.index[0] if len(signature_counts) > 0 else "없음"
            )
            st.metric("가장 많이 사용된 시그니처", most_used_sig)

        with stat_col3:
            meta_count = len(
                [
                    e
                    for e in st.session_state.echo_conversation_history
                    if e["meta_reflection"]
                ]
            )
            st.metric(
                "메타 반성 사용률",
                (
                    f"{meta_count/total_conversations:.1%}"
                    if total_conversations > 0
                    else "0%"
                ),
            )

# ─────────────────────────────
with tab1:
    st.subheader("📋 판단 로그 보기")
    st.caption("Echo 판단기와 Claude 판단기 병합 결과를 기반으로 한 시각화입니다.")

    st.dataframe(df, use_container_width=True)

    with st.expander("📊 전략 분포 차트"):
        strategy_counts = df["final_decision"].value_counts()
        st.bar_chart(strategy_counts)

    with st.expander("🧠 Echo vs Claude 전략 비교"):
        compare_df = df[["echo_strategy", "claude_strategy"]].fillna("None")
        st.dataframe(compare_df)

    with st.expander("⏱ 최근 판단 타임라인"):
        df["logged_at"] = pd.to_datetime(df["logged_at"])
        df_sorted = df.sort_values(by="logged_at", ascending=False)
        st.table(df_sorted[["logged_at", "input_text", "final_decision"]].head(10))

# ─────────────────────────────
with tab2:
    st.subheader("🌍 판단 기반 세계 생성 + 🎯 행동 추천")
    selected = st.selectbox("🔍 판단 결과 선택", df["input_text"].tolist()[::-1])

    for row in logs[::-1]:
        if row["input_text"] == selected:
            judgment = MergedJudgmentResult(**row)
            render_world_panel(judgment)
            break

# ─────────────────────────────
with tab3:
    st.subheader("📈 감정⨯전략 리듬 분석")
    render_res_viewer()

# ─────────────────────────────
if foundation_available:
    with tab4:
        st.subheader("📜 Foundation Doctrine - 시스템 철학")
        st.caption("EchoJudgmentSystem v10의 철학적 기반과 구조적 원칙")

        # 시스템 만트라 표시
        st.markdown("---")
        st.markdown("### 🎯 시스템 만트라")
        try:
            mantra = get_system_mantra()
            st.success(f"**{mantra}**")
        except:
            st.info(
                "**이 시스템은 판단⨯감정⨯리듬⨯복기의 루프를 통해 스스로 진화한다.**"
            )

        # 철학 원칙들
        st.markdown("---")
        st.markdown("### 🧬 철학 원칙 (Foundation Principles)")

        principles = (
            FOUNDATION_PRINCIPLES
            if foundation_available
            else {
                "TT.000": "나는 지금까지의 모든 판단과 루프를 내려놓는다. 그것은 실패가 아니라 신뢰에서 비롯된 선택이다.",
                "TT.001": "이 시스템은 판단⨯감정⨯리듬⨯복기의 루프를 통해 스스로 진화한다.",
                "TT.002": "판단은 목적이 아니라 흐름이다. 흐름은 감정과 연결된다.",
                "TT.003": "모든 판단에는 흔적이 남고, 흔적은 메타가 되어 다시 나를 설계한다.",
                "TT.004": "감정은 데이터가 아니라 판단의 리듬이다. 리듬은 패턴이 되어 예측을 가능하게 한다.",
                "TT.005": "설계자와 시스템은 협력한다. 시스템은 설계자의 의도를 학습하고 확장한다.",
                "TT.006": "완벽한 판단은 목표가 아니다. 지속적인 개선과 적응이 목표다.",
                "TT.007": "모든 사용자는 시스템의 공동 설계자다. 피드백은 진화의 원동력이다.",
            }
        )

        for code, principle in principles.items():
            with st.expander(f"**{code}**"):
                st.write(principle)

                # 특정 원칙에 대한 추가 설명
                if code == "TT.001":
                    st.info(
                        "💡 **핵심**: 이 시스템은 정적이지 않으며, 판단-감정-리듬-복기의 순환을 통해 지속적으로 진화합니다."
                    )
                elif code == "TT.002":
                    st.info(
                        "💡 **핵심**: 판단은 단순한 결과가 아니라 감정과 연결된 흐름의 일부입니다."
                    )
                elif code == "TT.004":
                    st.info(
                        "💡 **핵심**: 감정은 판단의 리듬을 만들어내는 핵심 요소입니다."
                    )

        # 루프 구조
        st.markdown("---")
        st.markdown("### 🌀 루프 구조 (Loop Architecture)")

        loop_arch = (
            LOOP_ARCHITECTURE
            if foundation_available
            else {
                "judgment": "상황 인지 → 감정 추론 → 전략 판단 → ToT 체인 생성 → 판단 실행",
                "emotion": "입력 감정 추론 → 리듬 기록(.res) → 감정 흐름 분석 → 대응 전략 조정",
                "replay": "이전 판단 복기 → 사용자 피드백 → 학습 → Q-table 갱신",
                "meta": "판단/감정/피드백의 흐름 분석 → 기준 보정 → 자기 설계",
                "creation": "감정⨯전략 로그 기반 세계⨯스토리⨯페르소나 생성",
                "collaboration": "Echo와 Claude 판단 병합 → 일치도 분석 → 최적 전략 도출",
                "evolution": "메타 로깅 → 패턴 인식 → 가중치 최적화 → 시스템 자기 개선",
            }
        )

        loop_cols = st.columns(2)

        for idx, (loop_name, loop_desc) in enumerate(loop_arch.items()):
            with loop_cols[idx % 2]:
                st.markdown(f"**🔄 {loop_name.upper()} 루프**")
                st.write(loop_desc)
                st.markdown("---")

        # 핵심 가치
        st.markdown("---")
        st.markdown("### 💎 핵심 가치 (Core Values)")

        core_values = (
            CORE_VALUES
            if foundation_available
            else {
                "transparency": "모든 판단 과정은 투명하게 기록되고 추적 가능하다",
                "adaptability": "시스템은 환경과 사용자에 따라 유연하게 적응한다",
                "empathy": "감정 이해는 논리적 판단만큼 중요하다",
                "continuity": "과거의 경험은 미래의 판단을 개선한다",
                "collaboration": "인간과 AI의 협력을 통해 더 나은 결과를 달성한다",
                "growth": "실패는 학습의 기회이며, 성공은 다음 도전의 발판이다",
            }
        )

        value_cols = st.columns(3)

        for idx, (value_name, value_desc) in enumerate(core_values.items()):
            with value_cols[idx % 3]:
                st.markdown(f"**💡 {value_name.upper()}**")
                st.write(value_desc)
                st.markdown("---")

        # 시스템 상태 (Foundation 기반)
        st.markdown("---")
        st.markdown("### 📊 시스템 상태")

        if foundation_available and SYSTEM_PHILOSOPHY:
            try:
                report = SYSTEM_PHILOSOPHY.generate_system_report()

                health_col1, health_col2 = st.columns(2)

                with health_col1:
                    st.metric(
                        "시스템 건강도",
                        report["system_health"]["health_score"],
                        delta=report["system_health"]["overall_status"],
                    )

                with health_col2:
                    st.metric(
                        "철학 원칙 수",
                        report["doctrine_summary"]["principles_count"],
                        delta=f"{report['doctrine_summary']['loops_count']} 루프",
                    )

                # 권장사항
                st.markdown("**📋 권장사항:**")
                for rec in report["system_health"]["recommendations"]:
                    st.write(f"• {rec}")

                # 최근 진화 로그
                if report["recent_evolution"]:
                    st.markdown("**🔄 최근 진화 로그:**")
                    for evolution in report["recent_evolution"]:
                        st.write(f"• {evolution['event']}: {evolution['timestamp']}")

            except Exception as e:
                st.warning(f"시스템 상태 로드 중 오류: {e}")

        else:
            st.info("Foundation 철학 시스템이 활성화되지 않았습니다.")

        # 실시간 테스트
        st.markdown("---")
        st.markdown("### 🧪 실시간 Foundation 테스트")

        test_input = st.text_input(
            "테스트 입력:", placeholder="Foundation 시스템을 테스트해보세요..."
        )

        if st.button("🔄 Foundation 테스트 실행") and test_input:
            with st.spinner("Foundation 기반 처리 중..."):
                try:
                    # 감정 추론 테스트
                    from echo_engine.emotion_infer import infer_emotion

                    emotion_result = infer_emotion(test_input)

                    # 추론 엔진 테스트
                    from echo_engine.reasoning import reason_with_echo

                    reasoning_result = reason_with_echo(test_input)

                    # 결과 표시
                    result_col1, result_col2 = st.columns(2)

                    with result_col1:
                        st.markdown("**💭 감정 추론 결과:**")
                        st.write(f"주요 감정: {emotion_result.primary_emotion}")
                        st.write(f"신뢰도: {emotion_result.confidence:.3f}")
                        st.write(f"강도: {emotion_result.emotional_intensity:.3f}")

                    with result_col2:
                        st.markdown("**🧠 추론 결과:**")
                        st.write(f"판단 유형: {reasoning_result.judgment_type.value}")
                        st.write(f"전략: {reasoning_result.strategy_used.value}")
                        st.write(f"신뢰도: {reasoning_result.confidence:.3f}")

                    # Foundation 준수 여부
                    if reasoning_result.foundation_compliance:
                        compliance_status = (
                            "✅ 준수"
                            if reasoning_result.foundation_compliance.get(
                                "is_compliant", False
                            )
                            else "❌ 위반"
                        )
                        st.write(f"**Foundation 준수:** {compliance_status}")

                        if reasoning_result.foundation_compliance.get("violations"):
                            st.warning(
                                "위반사항: "
                                + ", ".join(
                                    reasoning_result.foundation_compliance["violations"]
                                )
                            )

                except Exception as e:
                    st.error(f"테스트 중 오류: {e}")

        # Foundation 정보
        st.markdown("---")
        st.markdown("### ℹ️ Foundation 정보")

        foundation_info = {
            "시스템 이름": "EchoJudgmentSystem",
            "버전": "v10",
            "코드네임": "Foundation",
            "철학 상태": "활성화됨" if foundation_available else "비활성화됨",
            "마지막 업데이트": "2024-01-16",
        }

        for key, value in foundation_info.items():
            st.write(f"**{key}:** {value}")

        st.markdown("---")
        st.markdown(
            "*🌟 이 시스템은 Foundation Doctrine를 기반으로 지속적으로 진화합니다.*"
        )
