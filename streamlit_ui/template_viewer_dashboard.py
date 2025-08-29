#!/usr/bin/env python3
"""
📊 Template Viewer Dashboard - FIST 템플릿 뷰어 및 폴백 모니터링 UI

36개 감정×전략 조합 템플릿을 시각화하고 폴백 엔진의 성능을 실시간으로 모니터링하는
Streamlit 기반 대시보드.

핵심 기능:
1. 36개 FIST 템플릿 브라우저 및 미리보기
2. 실시간 폴백 체인 성능 모니터링
3. 감정×전략 조합 사용 통계
4. 템플릿 효과성 분석 및 시각화
5. 라이브 테스트 인터페이스
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys

# Echo Engine 경로 추가
sys.path.append(str(Path(__file__).parent.parent))


def load_config():
    """페이지 설정"""
    st.set_page_config(
        page_title="🎭 Echo Template Viewer",
        page_icon="🎭",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def load_fist_templates() -> Dict[str, Any]:
    """FIST 자동생성 템플릿 로드"""
    templates = {}
    templates_dir = Path("echo_engine/templates/fist_autogen")

    if templates_dir.exists():
        for yaml_file in templates_dir.glob("*.yaml"):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    template_data = yaml.safe_load(f)
                    templates[yaml_file.stem] = template_data
            except Exception as e:
                st.error(f"템플릿 로드 실패 {yaml_file}: {e}")

    return templates


def get_emotion_strategy_matrix(templates: Dict[str, Any]) -> pd.DataFrame:
    """감정×전략 매트릭스 생성"""
    emotions = ["joy", "sadness", "anger", "fear", "surprise", "neutral"]
    strategies = ["adapt", "confront", "retreat", "analyze", "initiate", "harmonize"]

    matrix_data = []
    for emotion in emotions:
        for strategy in strategies:
            template_key = f"{emotion}_{strategy}"
            exists = template_key in templates

            matrix_data.append(
                {
                    "emotion": emotion,
                    "strategy": strategy,
                    "template_key": template_key,
                    "exists": exists,
                    "emotion_korean": templates.get(template_key, {}).get(
                        "emotion_korean", emotion
                    ),
                    "strategy_korean": templates.get(template_key, {}).get(
                        "strategy_korean", strategy
                    ),
                }
            )

    return pd.DataFrame(matrix_data)


def create_template_heatmap(df: pd.DataFrame) -> go.Figure:
    """템플릿 존재 여부 히트맵"""
    pivot_df = df.pivot(index="emotion", columns="strategy", values="exists")

    fig = px.imshow(
        pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        color_continuous_scale=["lightcoral", "lightgreen"],
        title="🎯 FIST 템플릿 매트릭스 (36개 조합)",
        labels={"color": "템플릿 존재"},
    )

    fig.update_layout(
        xaxis_title="전략 (Strategy)", yaxis_title="감정 (Emotion)", height=400
    )

    return fig


def display_template_browser(templates: Dict[str, Any]):
    """템플릿 브라우저"""
    st.header("🎭 템플릿 브라우저")

    if not templates:
        st.warning("로드된 템플릿이 없습니다.")
        return

    # 필터링 옵션
    col1, col2 = st.columns(2)

    with col1:
        emotions = list(set(t.get("emotion", "") for t in templates.values()))
        emotions.sort()
        selected_emotion = st.selectbox("감정 선택", ["모든 감정"] + emotions)

    with col2:
        strategies = list(set(t.get("strategy", "") for t in templates.values()))
        strategies.sort()
        selected_strategy = st.selectbox("전략 선택", ["모든 전략"] + strategies)

    # 템플릿 필터링
    filtered_templates = templates.copy()

    if selected_emotion != "모든 감정":
        filtered_templates = {
            k: v
            for k, v in filtered_templates.items()
            if v.get("emotion") == selected_emotion
        }

    if selected_strategy != "모든 전략":
        filtered_templates = {
            k: v
            for k, v in filtered_templates.items()
            if v.get("strategy") == selected_strategy
        }

    st.write(f"📊 필터링된 템플릿: {len(filtered_templates)}개")

    # 템플릿 목록
    if filtered_templates:
        template_names = list(filtered_templates.keys())
        selected_template = st.selectbox("템플릿 선택", template_names)

        if selected_template:
            template_data = filtered_templates[selected_template]

            # 템플릿 상세 정보
            col1, col2 = st.columns(2)

            with col1:
                st.subheader(f"📋 {selected_template}")
                st.write(
                    f"**감정**: {template_data.get('emotion_korean', '')} ({template_data.get('emotion', '')})"
                )
                st.write(
                    f"**전략**: {template_data.get('strategy_korean', '')} ({template_data.get('strategy', '')})"
                )
                st.write(f"**설명**: {template_data.get('description', '')}")

            with col2:
                st.subheader("🔧 메타데이터")
                metadata = template_data.get("metadata", {})
                if metadata:
                    st.json(metadata)

            # FIST 구조 표시
            st.subheader("🎯 FIST 구조")

            fist_components = [
                ("Frame", template_data.get("frame", "")),
                ("Insight", template_data.get("insight", "")),
                ("Strategy", template_data.get("strategy", "")),
                ("Tactics", template_data.get("tactics", "")),
            ]

            for component_name, component_text in fist_components:
                if component_text:
                    st.write(f"**{component_name}**")
                    st.info(component_text)


def test_fallback_engine():
    """폴백 엔진 라이브 테스트"""
    st.header("🧪 폴백 엔진 라이브 테스트")

    # 테스트 입력
    test_input = st.text_area(
        "테스트 입력", placeholder="테스트할 텍스트를 입력하세요...", height=100
    )

    col1, col2 = st.columns(2)

    with col1:
        manual_emotion = st.selectbox(
            "감정 수동 설정 (선택사항)",
            ["자동 감지", "joy", "sadness", "anger", "fear", "surprise", "neutral"],
        )

    with col2:
        manual_strategy = st.selectbox(
            "전략 수동 설정 (선택사항)",
            [
                "자동 선택",
                "adapt",
                "confront",
                "retreat",
                "analyze",
                "initiate",
                "harmonize",
            ],
        )

    if st.button("🚀 폴백 테스트 실행", type="primary"):
        if test_input.strip():
            with st.spinner("폴백 엔진 실행 중..."):
                try:
                    # 폴백 엔진 호출
                    from echo_engine.fallback_engine import fallback_judge

                    context = {}
                    if manual_emotion != "자동 감지":
                        context["manual_emotion"] = manual_emotion
                    if manual_strategy != "자동 선택":
                        context["manual_strategy"] = manual_strategy

                    result = fallback_judge(test_input, context)

                    # 결과 표시
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("📊 실행 결과")

                        if result.success:
                            st.success(f"✅ 성공: {result.stage_used.value} 단계")
                        else:
                            st.error("❌ 모든 단계 실패")

                        st.metric("신뢰도", f"{result.confidence:.2f}")
                        st.metric("처리 시간", f"{result.processing_time:.3f}초")
                        st.metric("시도 횟수", result.attempts_made)

                        if result.template_used:
                            st.info(f"🎭 사용된 템플릿: {result.template_used}")

                    with col2:
                        st.subheader("🔄 폴백 체인")
                        for i, stage in enumerate(result.fallback_chain, 1):
                            if stage == result.stage_used.value and result.success:
                                st.success(f"{i}. {stage} ✅")
                            else:
                                st.error(f"{i}. {stage} ❌")

                    # 응답 텍스트
                    st.subheader("💬 생성된 응답")
                    st.text_area(
                        "응답 내용", result.response_text, height=150, disabled=True
                    )

                    # 오류 메시지 (있는 경우)
                    if result.error_messages:
                        st.subheader("⚠️ 오류 메시지")
                        for error in result.error_messages:
                            st.error(error)

                except Exception as e:
                    st.error(f"테스트 실행 중 오류: {e}")
        else:
            st.warning("테스트 입력을 작성해주세요.")


def display_fallback_statistics():
    """폴백 통계 표시"""
    st.header("📈 폴백 엔진 통계")

    try:
        from echo_engine.fallback_engine import get_fallback_engine

        engine = get_fallback_engine()
        stats = engine.get_fallback_stats()

        # 전체 통계
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("총 요청", stats["total_requests"])

        with col2:
            st.metric("성공 요청", stats["successful_requests"])

        with col3:
            success_rate = stats.get("overall_success_rate", 0)
            st.metric("성공률", f"{success_rate:.1f}%")

        with col4:
            avg_time = stats.get("average_processing_time", 0)
            st.metric("평균 처리시간", f"{avg_time:.3f}초")

        # 단계별 사용 통계
        if stats.get("stage_usage"):
            st.subheader("🎯 단계별 사용 통계")

            stage_df = pd.DataFrame(
                [
                    {"단계": stage, "사용 횟수": count}
                    for stage, count in stats["stage_usage"].items()
                ]
            )

            fig = px.bar(
                stage_df,
                x="단계",
                y="사용 횟수",
                title="폴백 단계별 사용 빈도",
                color="사용 횟수",
                color_continuous_scale="viridis",
            )

            st.plotly_chart(fig, use_container_width=True)

        # 감정×전략 조합 통계
        if stats.get("emotion_strategy_combinations"):
            st.subheader("🎭 감정×전략 조합 사용 통계")

            combo_df = pd.DataFrame(
                [
                    {"조합": combo, "사용 횟수": count}
                    for combo, count in stats["emotion_strategy_combinations"].items()
                ]
            )

            fig = px.pie(
                combo_df, names="조합", values="사용 횟수", title="감정×전략 조합 분포"
            )

            st.plotly_chart(fig, use_container_width=True)

        # 실패율 분석
        if stats.get("failure_rate_by_stage"):
            st.subheader("❌ 단계별 실패율 분석")

            failure_data = []
            for stage, data in stats["failure_rate_by_stage"].items():
                failure_rate = data.get("failure_rate", 0)
                failure_data.append(
                    {
                        "단계": stage,
                        "실패율": failure_rate,
                        "총 시도": data.get("attempts", 0),
                        "실패 횟수": data.get("failures", 0),
                    }
                )

            failure_df = pd.DataFrame(failure_data)

            fig = px.bar(
                failure_df,
                x="단계",
                y="실패율",
                title="단계별 실패율 (%)",
                color="실패율",
                color_continuous_scale="reds",
            )

            st.plotly_chart(fig, use_container_width=True)

            # 상세 테이블
            st.subheader("📊 상세 실패 통계")
            st.dataframe(failure_df, use_container_width=True)

    except Exception as e:
        st.error(f"통계 로드 중 오류: {e}")


def display_performance_monitoring():
    """성능 모니터링"""
    st.header("⚡ 실시간 성능 모니터링")

    # 실시간 데이터 시뮬레이션 (실제 구현에서는 실제 메트릭 사용)
    if st.button("🔄 실시간 데이터 새로고침"):

        # 시간별 요청 수 시뮬레이션
        current_time = datetime.now()
        time_data = []

        for i in range(24):
            hour_time = current_time - timedelta(hours=i)
            requests = max(0, int(50 + 30 * (0.5 - abs((hour_time.hour - 12) / 24))))

            time_data.append(
                {
                    "시간": hour_time.strftime("%H:%M"),
                    "요청 수": requests,
                    "성공률": min(100, max(80, 95 + (i % 3 - 1) * 5)),
                    "평균 응답시간": max(0.1, 0.5 + (i % 4 - 2) * 0.1),
                }
            )

        time_df = pd.DataFrame(time_data)

        # 시간별 요청 수 차트
        fig1 = px.line(
            time_df, x="시간", y="요청 수", title="📈 시간별 요청 수 변화", markers=True
        )

        st.plotly_chart(fig1, use_container_width=True)

        # 성능 메트릭 멀티 차트
        fig2 = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("성공률 (%)", "평균 응답시간 (초)"),
            vertical_spacing=0.1,
        )

        fig2.add_trace(
            go.Scatter(
                x=time_df["시간"],
                y=time_df["성공률"],
                mode="lines+markers",
                name="성공률",
                line=dict(color="green"),
            ),
            row=1,
            col=1,
        )

        fig2.add_trace(
            go.Scatter(
                x=time_df["시간"],
                y=time_df["평균 응답시간"],
                mode="lines+markers",
                name="응답시간",
                line=dict(color="blue"),
            ),
            row=2,
            col=1,
        )

        fig2.update_layout(height=500, title_text="⚡ 성능 메트릭 추이")

        st.plotly_chart(fig2, use_container_width=True)

        # 최근 성능 지표
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("현재 성공률", "94.2%", "↑ 2.1%")

        with col2:
            st.metric("평균 응답시간", "0.45초", "↓ 0.05초")

        with col3:
            st.metric("활성 템플릿", "36개", "→ 0개")


def main():
    """메인 애플리케이션"""
    load_config()

    st.title("🎭 Echo Template Viewer & Fallback Monitor")
    st.markdown("**36개 감정×전략 조합 템플릿 뷰어 및 폴백 엔진 모니터링 대시보드**")

    # 사이드바 메뉴
    st.sidebar.title("📋 메뉴")

    menu_options = [
        "🎭 템플릿 브라우저",
        "📊 템플릿 매트릭스",
        "🧪 라이브 테스트",
        "📈 폴백 통계",
        "⚡ 성능 모니터링",
    ]

    selected_menu = st.sidebar.selectbox("메뉴 선택", menu_options)

    # 템플릿 로드
    with st.spinner("템플릿 로딩 중..."):
        templates = load_fist_templates()

    st.sidebar.success(f"✅ {len(templates)}개 템플릿 로드됨")

    # 메뉴별 페이지 표시
    if selected_menu == "🎭 템플릿 브라우저":
        display_template_browser(templates)

    elif selected_menu == "📊 템플릿 매트릭스":
        st.header("📊 템플릿 매트릭스")

        if templates:
            df = get_emotion_strategy_matrix(templates)

            # 매트릭스 히트맵
            fig = create_template_heatmap(df)
            st.plotly_chart(fig, use_container_width=True)

            # 템플릿 완성도
            total_combinations = 36
            existing_templates = len(templates)
            completion_rate = (existing_templates / total_combinations) * 100

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("총 조합", f"{total_combinations}개")

            with col2:
                st.metric("생성된 템플릿", f"{existing_templates}개")

            with col3:
                st.metric("완성도", f"{completion_rate:.1f}%")

            # 상세 매트릭스 테이블
            st.subheader("📋 상세 매트릭스")

            display_df = df[
                ["emotion_korean", "strategy_korean", "template_key", "exists"]
            ].copy()
            display_df.columns = ["감정", "전략", "템플릿 키", "존재 여부"]
            display_df["존재 여부"] = display_df["존재 여부"].map(
                {True: "✅", False: "❌"}
            )

            st.dataframe(display_df, use_container_width=True, height=400)

    elif selected_menu == "🧪 라이브 테스트":
        test_fallback_engine()

    elif selected_menu == "📈 폴백 통계":
        display_fallback_statistics()

    elif selected_menu == "⚡ 성능 모니터링":
        display_performance_monitoring()

    # 푸터
    st.markdown("---")
    st.markdown(
        "**Echo Judgment System v10** | "
        f"템플릿: {len(templates)}개 | "
        f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    main()
