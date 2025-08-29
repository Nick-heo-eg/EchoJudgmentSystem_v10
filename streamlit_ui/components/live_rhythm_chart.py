#!/usr/bin/env python3
"""
📈 Live Rhythm Chart - EchoJudgmentSystem v10 실시간 리듬 시각화

실시간으로 감정×전략 리듬을 추적하고 시각화하는 고급 차트 컴포넌트
WebSocket 또는 polling을 통한 실시간 업데이트 지원
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import time
import os
from typing import Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass


@dataclass
class RhythmDataPoint:
    """리듬 데이터 포인트"""

    timestamp: datetime
    emotion: str
    strategy: str
    confidence: float
    judgment: str
    session_id: str


class LiveRhythmChart:
    """실시간 리듬 차트 관리자"""

    def __init__(self, max_data_points: int = 100):
        self.max_data_points = max_data_points
        self.data_buffer = []
        self.emotion_colors = {
            "joy": "#FFD700",
            "sadness": "#4169E1",
            "anger": "#DC143C",
            "fear": "#8B008B",
            "surprise": "#FF4500",
            "neutral": "#708090",
        }
        self.strategy_colors = {
            "logical": "#20B2AA",
            "empathetic": "#FF69B4",
            "creative": "#32CD32",
            "cautious": "#DAA520",
        }

    def add_data_point(
        self,
        emotion: str,
        strategy: str,
        confidence: float,
        judgment: str,
        session_id: str = "default",
    ):
        """새로운 데이터 포인트 추가"""
        data_point = RhythmDataPoint(
            timestamp=datetime.now(),
            emotion=emotion,
            strategy=strategy,
            confidence=confidence,
            judgment=judgment,
            session_id=session_id,
        )

        self.data_buffer.append(data_point)

        # 최대 데이터 포인트 수 제한
        if len(self.data_buffer) > self.max_data_points:
            self.data_buffer.pop(0)

    def load_from_res_logs(self, res_logs_dir: str = "res_logs"):
        """res_logs에서 데이터 로드"""
        if not os.path.exists(res_logs_dir):
            return

        # res_logs 파일들 읽기
        for filename in sorted(os.listdir(res_logs_dir)):
            if filename.endswith(".json"):
                filepath = os.path.join(res_logs_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # 데이터 포인트 생성
                    emotion = data.get("emotion", "neutral")
                    strategy = data.get("strategy_symbol", "cautious")
                    confidence = 0.8  # 기본값
                    judgment = data.get("final_decision", "N/A")
                    timestamp_str = data.get("timestamp", datetime.now().isoformat())

                    # 타임스탬프 파싱
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )

                    data_point = RhythmDataPoint(
                        timestamp=timestamp,
                        emotion=emotion,
                        strategy=strategy,
                        confidence=confidence,
                        judgment=judgment,
                        session_id="loaded",
                    )

                    self.data_buffer.append(data_point)

                except Exception as e:
                    st.error(f"로그 파일 읽기 오류: {filename} - {e}")

        # 시간순 정렬
        self.data_buffer.sort(key=lambda x: x.timestamp)

        # 최대 데이터 포인트 수 제한
        if len(self.data_buffer) > self.max_data_points:
            self.data_buffer = self.data_buffer[-self.max_data_points :]

    def create_emotion_timeline(self) -> go.Figure:
        """감정 타임라인 차트 생성"""
        if not self.data_buffer:
            return go.Figure().add_annotation(
                text="데이터 없음",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
            )

        df = pd.DataFrame(
            [
                {
                    "timestamp": dp.timestamp,
                    "emotion": dp.emotion,
                    "confidence": dp.confidence,
                    "judgment": (
                        dp.judgment[:30] + "..."
                        if len(dp.judgment) > 30
                        else dp.judgment
                    ),
                }
                for dp in self.data_buffer
            ]
        )

        fig = go.Figure()

        # 감정별 scatter plot
        for emotion in df["emotion"].unique():
            emotion_data = df[df["emotion"] == emotion]
            fig.add_trace(
                go.Scatter(
                    x=emotion_data["timestamp"],
                    y=emotion_data["confidence"],
                    mode="markers+lines",
                    name=emotion,
                    marker=dict(
                        color=self.emotion_colors.get(emotion, "#888888"),
                        size=10,
                        line=dict(width=1, color="white"),
                    ),
                    hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        + "시간: %{x}<br>"
                        + "신뢰도: %{y:.2f}<br>"
                        + "판단: %{customdata}<br>"
                        + "<extra></extra>"
                    ),
                    customdata=emotion_data["judgment"],
                )
            )

        fig.update_layout(
            title="🎭 감정 상태 시간별 변화",
            xaxis_title="시간",
            yaxis_title="신뢰도",
            hovermode="closest",
            showlegend=True,
            height=400,
        )

        return fig

    def create_strategy_heatmap(self) -> go.Figure:
        """전략×감정 히트맵 생성"""
        if not self.data_buffer:
            return go.Figure().add_annotation(
                text="데이터 없음",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
            )

        # 전략×감정 매트릭스 생성
        strategy_emotion_matrix = {}
        for dp in self.data_buffer:
            if dp.strategy not in strategy_emotion_matrix:
                strategy_emotion_matrix[dp.strategy] = {}
            if dp.emotion not in strategy_emotion_matrix[dp.strategy]:
                strategy_emotion_matrix[dp.strategy][dp.emotion] = 0
            strategy_emotion_matrix[dp.strategy][dp.emotion] += 1

        # 데이터프레임 변환
        strategies = list(strategy_emotion_matrix.keys())
        emotions = list(set(dp.emotion for dp in self.data_buffer))

        matrix_data = []
        for strategy in strategies:
            row = []
            for emotion in emotions:
                count = strategy_emotion_matrix.get(strategy, {}).get(emotion, 0)
                row.append(count)
            matrix_data.append(row)

        fig = go.Figure(
            data=go.Heatmap(
                z=matrix_data,
                x=emotions,
                y=strategies,
                colorscale="Viridis",
                hovertemplate=(
                    "전략: %{y}<br>"
                    + "감정: %{x}<br>"
                    + "빈도: %{z}<br>"
                    + "<extra></extra>"
                ),
            )
        )

        fig.update_layout(
            title="🎯 전략×감정 상관관계 히트맵",
            xaxis_title="감정",
            yaxis_title="전략",
            height=300,
        )

        return fig

    def create_rhythm_flow(self) -> go.Figure:
        """리듬 플로우 차트 생성"""
        if not self.data_buffer:
            return go.Figure().add_annotation(
                text="데이터 없음",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
            )

        # 시간 윈도우별 데이터 집계
        df = pd.DataFrame(
            [
                {
                    "timestamp": dp.timestamp,
                    "emotion": dp.emotion,
                    "strategy": dp.strategy,
                    "confidence": dp.confidence,
                }
                for dp in self.data_buffer
            ]
        )

        # 5분 간격으로 그룹화
        df["time_window"] = df["timestamp"].dt.floor("5min")

        # 각 시간 윈도우별 주요 감정/전략 계산
        flow_data = []
        for window in df["time_window"].unique():
            window_data = df[df["time_window"] == window]

            # 가장 빈번한 감정/전략
            top_emotion = (
                window_data["emotion"].mode().iloc[0]
                if not window_data.empty
                else "neutral"
            )
            top_strategy = (
                window_data["strategy"].mode().iloc[0]
                if not window_data.empty
                else "cautious"
            )
            avg_confidence = window_data["confidence"].mean()

            flow_data.append(
                {
                    "time_window": window,
                    "emotion": top_emotion,
                    "strategy": top_strategy,
                    "confidence": avg_confidence,
                    "data_points": len(window_data),
                }
            )

        flow_df = pd.DataFrame(flow_data)

        if flow_df.empty:
            return go.Figure().add_annotation(
                text="데이터 부족",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
            )

        # 서브플롯 생성
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("감정 플로우", "전략 플로우"),
            vertical_spacing=0.1,
        )

        # 감정 플로우
        fig.add_trace(
            go.Scatter(
                x=flow_df["time_window"],
                y=flow_df["emotion"],
                mode="lines+markers",
                name="감정 플로우",
                line=dict(width=3),
                marker=dict(size=8),
            ),
            row=1,
            col=1,
        )

        # 전략 플로우
        fig.add_trace(
            go.Scatter(
                x=flow_df["time_window"],
                y=flow_df["strategy"],
                mode="lines+markers",
                name="전략 플로우",
                line=dict(width=3),
                marker=dict(size=8),
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            title="🌊 시간 흐름에 따른 감정×전략 리듬", showlegend=False, height=600
        )

        return fig

    def create_confidence_distribution(self) -> go.Figure:
        """신뢰도 분포 차트 생성"""
        if not self.data_buffer:
            return go.Figure().add_annotation(
                text="데이터 없음",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
            )

        confidences = [dp.confidence for dp in self.data_buffer]

        fig = go.Figure(
            data=[
                go.Histogram(
                    x=confidences,
                    nbinsx=20,
                    marker=dict(
                        color="rgba(0,123,255,0.7)",
                        line=dict(color="rgba(0,123,255,1)", width=1),
                    ),
                    name="신뢰도 분포",
                )
            ]
        )

        fig.update_layout(
            title="📊 판단 신뢰도 분포",
            xaxis_title="신뢰도",
            yaxis_title="빈도",
            height=300,
        )

        return fig

    def get_rhythm_stats(self) -> Dict:
        """리듬 통계 생성"""
        if not self.data_buffer:
            return {
                "total_data_points": 0,
                "time_span": "N/A",
                "most_common_emotion": "N/A",
                "most_common_strategy": "N/A",
                "average_confidence": 0.0,
            }

        emotions = [dp.emotion for dp in self.data_buffer]
        strategies = [dp.strategy for dp in self.data_buffer]
        confidences = [dp.confidence for dp in self.data_buffer]

        # 시간 범위 계산
        timestamps = [dp.timestamp for dp in self.data_buffer]
        time_span = max(timestamps) - min(timestamps)

        return {
            "total_data_points": len(self.data_buffer),
            "time_span": str(time_span),
            "most_common_emotion": max(set(emotions), key=emotions.count),
            "most_common_strategy": max(set(strategies), key=strategies.count),
            "average_confidence": np.mean(confidences),
            "emotion_diversity": len(set(emotions)),
            "strategy_diversity": len(set(strategies)),
            "confidence_std": np.std(confidences),
        }


def render_live_rhythm_chart():
    """Streamlit에서 실시간 리듬 차트 렌더링"""
    st.header("📈 실시간 감정×전략 리듬 분석")

    # 리듬 차트 인스턴스 생성
    if "rhythm_chart" not in st.session_state:
        st.session_state.rhythm_chart = LiveRhythmChart()

    chart = st.session_state.rhythm_chart

    # 데이터 로드 버튼
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("📁 res_logs 데이터 로드"):
            chart.load_from_res_logs()
            st.success(f"✅ {len(chart.data_buffer)}개 데이터 포인트 로드됨")

    with col2:
        if st.button("🔄 새로고침"):
            st.rerun()

    with col3:
        if st.button("🗑️ 데이터 초기화"):
            chart.data_buffer = []
            st.success("✅ 데이터 초기화 완료")

    # 통계 정보
    stats = chart.get_rhythm_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("데이터 포인트", stats["total_data_points"])
    with col2:
        st.metric("주요 감정", stats["most_common_emotion"])
    with col3:
        st.metric("주요 전략", stats["most_common_strategy"])
    with col4:
        st.metric("평균 신뢰도", f"{stats['average_confidence']:.2f}")

    # 차트 렌더링
    if len(chart.data_buffer) > 0:
        # 감정 타임라인
        emotion_fig = chart.create_emotion_timeline()
        st.plotly_chart(emotion_fig, use_container_width=True)

        # 2열 레이아웃
        col1, col2 = st.columns(2)

        with col1:
            # 전략×감정 히트맵
            heatmap_fig = chart.create_strategy_heatmap()
            st.plotly_chart(heatmap_fig, use_container_width=True)

        with col2:
            # 신뢰도 분포
            confidence_fig = chart.create_confidence_distribution()
            st.plotly_chart(confidence_fig, use_container_width=True)

        # 리듬 플로우
        flow_fig = chart.create_rhythm_flow()
        st.plotly_chart(flow_fig, use_container_width=True)

        # 상세 통계
        with st.expander("📊 상세 통계"):
            st.json(stats)

    else:
        st.info("📈 데이터를 로드하거나 새로운 판단을 실행하여 리듬 차트를 확인하세요.")
        st.markdown(
            """
        **리듬 차트 사용법:**
        1. 📁 'res_logs 데이터 로드' 버튼 클릭
        2. 또는 `auto_launcher.py`를 실행하여 새로운 데이터 생성
        3. 🔄 '새로고침' 버튼으로 최신 데이터 확인
        """
        )


# 테스트 함수
def test_live_rhythm_chart():
    """테스트용 샘플 데이터 생성"""
    chart = LiveRhythmChart()

    # 샘플 데이터 생성
    import random

    emotions = ["joy", "sadness", "anger", "fear", "surprise", "neutral"]
    strategies = ["logical", "empathetic", "creative", "cautious"]

    for i in range(50):
        chart.add_data_point(
            emotion=random.choice(emotions),
            strategy=random.choice(strategies),
            confidence=random.uniform(0.5, 1.0),
            judgment=f"테스트 판단 {i+1}",
            session_id="test",
        )

    return chart


if __name__ == "__main__":
    # 테스트 실행
    test_chart = test_live_rhythm_chart()
    print(f"✅ 테스트 차트 생성 완료: {len(test_chart.data_buffer)}개 데이터 포인트")

    stats = test_chart.get_rhythm_stats()
    print("📊 통계 정보:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
