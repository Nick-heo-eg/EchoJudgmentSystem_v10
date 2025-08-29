# streamlit_ui/components/res_viewer.py

import streamlit as st
import pandas as pd
from meta_log import load_judgment_logs
from datetime import datetime


def render_res_viewer():
    st.header("📈 감정 ⨯ 전략 리듬 분석")
    logs = load_judgment_logs(limit=300)

    if not logs:
        st.warning("판단 로그가 없습니다.")
        return

    df = pd.DataFrame(logs)
    df["logged_at"] = pd.to_datetime(df["logged_at"])

    with st.expander("🧠 전략 분포"):
        st.bar_chart(df["final_decision"].value_counts())

    with st.expander("💓 감정 분포"):
        st.bar_chart(df["emotion"].value_counts())

    with st.expander("⏱ 시간 흐름에 따른 감정 변화"):
        emotion_trend = df.groupby(pd.Grouper(key="logged_at", freq="1min"))[
            "emotion"
        ].agg(lambda x: x.value_counts().index[0])
        st.line_chart(emotion_trend)

    with st.expander("⏱ 시간 흐름에 따른 전략 변화"):
        strategy_trend = df.groupby(pd.Grouper(key="logged_at", freq="1min"))[
            "final_decision"
        ].agg(lambda x: x.value_counts().index[0])
        st.line_chart(strategy_trend)
