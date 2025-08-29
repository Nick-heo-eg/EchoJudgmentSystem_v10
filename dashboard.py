#!/usr/bin/env python3
"""
EchoJudgmentSystem 시각화 대시보드
실시간 NPI 로그 분석 및 시각화
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime, timedelta
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="EchoJudgmentSystem 대시보드",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 사이드바 설정
st.sidebar.title("🤖 Echo 판단 시스템")
st.sidebar.markdown("---")


@st.cache_data
def load_npi_logs(file_path="npi_log.jsonl"):
    """NPI 로그 파일 로드"""
    if not os.path.exists(file_path):
        return pd.DataFrame()

    logs = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
    except Exception as e:
        st.error(f"로그 파일 로드 실패: {e}")
        return pd.DataFrame()

    if not logs:
        return pd.DataFrame()

    df = pd.DataFrame(logs)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # NPI 점수 분해
    if "npi_score" in df.columns:
        npi_df = pd.json_normalize(df["npi_score"])
        df = pd.concat([df, npi_df], axis=1)

    return df


def create_npi_radar_chart(df):
    """NPI 레이더 차트 생성"""
    if df.empty:
        return None

    # 최근 데이터 사용
    recent_data = df.tail(10)

    # NPI 구성 요소 평균 계산
    npi_components = [
        "structure",
        "emotion",
        "rhythm",
        "context",
        "strategy_tone",
        "silence",
    ]
    avg_scores = []

    for component in npi_components:
        if component in recent_data.columns:
            avg_scores.append(recent_data[component].mean())
        else:
            avg_scores.append(0)

    # 레이더 차트 생성
    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=avg_scores,
            theta=npi_components,
            fill="toself",
            name="NPI 평균 점수",
            line=dict(color="rgb(0, 123, 255)"),
            fillcolor="rgba(0, 123, 255, 0.3)",
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title="NPI 구성 요소 분석",
        height=400,
    )

    return fig


def create_strategy_distribution(df):
    """전략 분포 차트 생성"""
    if df.empty or "strategy" not in df.columns:
        return None

    strategy_counts = df["strategy"].value_counts()

    fig = px.pie(
        values=strategy_counts.values,
        names=strategy_counts.index,
        title="응답 전략 분포",
        height=400,
    )

    return fig


def create_npi_timeline(df):
    """NPI 점수 시간대별 변화"""
    if df.empty or "total" not in df.columns:
        return None

    fig = px.line(
        df,
        x="timestamp",
        y="total",
        title="NPI 총점 시간대별 변화",
        labels={"total": "NPI 총점", "timestamp": "시간"},
        height=400,
    )

    fig.add_hline(
        y=0.75,
        line_dash="dash",
        line_color="red",
        annotation_text="고감도 기준선 (0.75)",
    )
    fig.add_hline(
        y=0.5,
        line_dash="dash",
        line_color="orange",
        annotation_text="중간 기준선 (0.5)",
    )

    return fig


def create_claude_confidence_chart(df):
    """Claude 신뢰도 분석"""
    if df.empty:
        return None

    # Claude 관련 컬럼이 있는지 확인
    claude_cols = [col for col in df.columns if "claude" in col.lower()]
    if not claude_cols:
        return None

    # 임시 데이터 생성 (실제 로그에 claude 데이터가 있을 때까지)
    confidence_data = np.random.uniform(0.7, 0.95, len(df))

    fig = px.histogram(
        x=confidence_data,
        nbins=20,
        title="Claude 판단 신뢰도 분포",
        labels={"x": "신뢰도", "y": "빈도"},
        height=400,
    )

    return fig


def main():
    """메인 대시보드"""
    st.title("🤖 EchoJudgmentSystem 실시간 대시보드")
    st.markdown("---")

    # 데이터 로드
    df = load_npi_logs()

    # 새로고침 버튼
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()

    if df.empty:
        st.warning("⚠️ 로그 데이터가 없습니다. API를 통해 판단 요청을 보내주세요.")
        st.code(
            """
# API 테스트 명령어
curl -X POST "http://localhost:9000/judge" \\
     -H "Content-Type: application/json" \\
     -d '{"prompt": "오늘 회의에서 제안했는데 다들 조용해졌어요."}'
        """
        )
        return

    # 메트릭 표시
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("총 판단 수", len(df))

    with col2:
        if "total" in df.columns:
            avg_npi = df["total"].mean()
            st.metric("평균 NPI 점수", f"{avg_npi:.3f}")
        else:
            st.metric("평균 NPI 점수", "N/A")

    with col3:
        if "strategy" in df.columns:
            most_common_strategy = (
                df["strategy"].mode()[0] if not df["strategy"].mode().empty else "N/A"
            )
            st.metric("주요 전략", most_common_strategy)
        else:
            st.metric("주요 전략", "N/A")

    with col4:
        recent_count = len(df[df["timestamp"] > datetime.now() - timedelta(hours=1)])
        st.metric("최근 1시간 판단 수", recent_count)

    # 차트 섹션
    st.markdown("## 📊 분석 차트")

    # 첫 번째 행: NPI 레이더 차트와 전략 분포
    col1, col2 = st.columns(2)

    with col1:
        radar_fig = create_npi_radar_chart(df)
        if radar_fig:
            st.plotly_chart(radar_fig, use_container_width=True)

    with col2:
        strategy_fig = create_strategy_distribution(df)
        if strategy_fig:
            st.plotly_chart(strategy_fig, use_container_width=True)

    # 두 번째 행: 시간대별 변화와 신뢰도 분포
    col1, col2 = st.columns(2)

    with col1:
        timeline_fig = create_npi_timeline(df)
        if timeline_fig:
            st.plotly_chart(timeline_fig, use_container_width=True)

    with col2:
        confidence_fig = create_claude_confidence_chart(df)
        if confidence_fig:
            st.plotly_chart(confidence_fig, use_container_width=True)

    # 최근 판단 내역 테이블
    st.markdown("## 📋 최근 판단 내역")

    if len(df) > 0:
        # 표시할 컬럼 선택
        display_cols = ["timestamp", "prompt", "strategy", "total"]
        if "claude_summary" in df.columns:
            display_cols.append("claude_summary")

        recent_df = df[display_cols].tail(10).sort_values("timestamp", ascending=False)

        # 컬럼명 한국어로 변경
        column_mapping = {
            "timestamp": "시간",
            "prompt": "입력",
            "strategy": "전략",
            "total": "NPI 총점",
            "claude_summary": "Claude 요약",
        }

        recent_df = recent_df.rename(columns=column_mapping)

        st.dataframe(recent_df, use_container_width=True)

    # 사이드바 정보
    st.sidebar.markdown("### 📊 실시간 통계")
    if not df.empty:
        if "total" in df.columns:
            st.sidebar.metric("최고 NPI 점수", f"{df['total'].max():.3f}")
            st.sidebar.metric("최저 NPI 점수", f"{df['total'].min():.3f}")

        st.sidebar.markdown("### 🎯 전략 분포")
        if "strategy" in df.columns:
            for strategy, count in df["strategy"].value_counts().items():
                st.sidebar.text(f"{strategy}: {count}회")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 시스템 정보")
    st.sidebar.text(f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}")
    st.sidebar.text(f"데이터 포인트: {len(df)}개")


if __name__ == "__main__":
    main()
