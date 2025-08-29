"""
판단 결과 시각화 모듈
LLM-Free 판단 시스템 결과를 시각화합니다.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
import json

# 상위 디렉토리 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from echo_engine.llm_free.llm_free_judge import quick_judgment, FallbackJudge
from echo_engine.llm_free.pattern_based_reasoner import PatternBasedReasoner
from api.llm_runner import generate_response


def create_judgment_interface():
    """판단 시스템 인터페이스 생성"""
    st.title("🧠 EchoJudgmentSystem - 판단 결과 시각화")

    # 사이드바 설정
    st.sidebar.title("⚙️ 판단 설정")

    # 판단 모드 선택
    judge_mode = st.sidebar.selectbox(
        "판단 모드",
        ["fallback", "claude"],
        index=0,
        help="fallback: LLM-Free 판단, claude: Claude AI 판단",
    )

    # 입력 섹션
    st.header("📝 입력")

    col1, col2 = st.columns([3, 1])

    with col1:
        input_text = st.text_area(
            "판단할 텍스트를 입력하세요:",
            height=100,
            placeholder="예: 오늘 회의에서 제안이 잘 받아들여졌어요!",
        )

    with col2:
        context = st.text_area(
            "추가 맥락 (선택사항):", height=100, placeholder="예: 업무 상황"
        )

    # 판단 실행 버튼
    if st.button("🎯 판단 실행", type="primary"):
        if input_text.strip():
            execute_judgment(input_text, context, judge_mode)
        else:
            st.error("텍스트를 입력해주세요!")

    # 예시 버튼들
    st.subheader("💡 예시 테스트")

    example_cases = [
        "오늘 승진 소식을 들었어요! 너무 기뻐요!",
        "회의에서 논리적으로 분석해서 발표했어요.",
        "친구와 갈등이 있어서 마음이 아파요.",
        "새로운 창의적 아이디어가 생각났어요!",
        "스트레스가 너무 심해서 걱정이에요.",
    ]

    cols = st.columns(len(example_cases))
    for i, example in enumerate(example_cases):
        with cols[i]:
            if st.button(f"예시 {i+1}", key=f"example_{i}"):
                st.session_state.example_input = example
                st.rerun()

    # 예시 입력이 선택된 경우
    if hasattr(st.session_state, "example_input"):
        execute_judgment(st.session_state.example_input, "", judge_mode)
        del st.session_state.example_input


def execute_judgment(input_text: str, context: str, judge_mode: str):
    """판단 실행 및 결과 시각화"""
    st.header("🎯 판단 결과")

    with st.spinner("판단 실행 중..."):
        try:
            # 판단 실행
            if judge_mode == "fallback":
                result = quick_judgment(input_text, context)
                judgment_data = {
                    "judgment": result.judgment,
                    "confidence": result.confidence,
                    "emotion_detected": result.emotion_detected,
                    "strategy_suggested": result.strategy_suggested,
                    "reasoning": " → ".join(result.reasoning_trace),
                    "processing_time": result.processing_time,
                    "fallback_used": True,
                }
            else:
                # Claude 모드 (API 통합)
                input_data = {
                    "text": input_text,
                    "context": context,
                    "judge_mode": judge_mode,
                }
                judgment_data = generate_response(input_data)

            # 결과 표시
            display_judgment_results(judgment_data, input_text, context)

        except Exception as e:
            st.error(f"판단 실행 중 오류 발생: {e}")
            st.exception(e)


def display_judgment_results(judgment_data: dict, input_text: str, context: str):
    """판단 결과 표시"""

    # 기본 정보 표시
    st.subheader("📊 판단 요약")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("신뢰도", f"{judgment_data['confidence']:.3f}")

    with col2:
        st.metric("감정", judgment_data["emotion_detected"])

    with col3:
        st.metric("전략", judgment_data["strategy_suggested"])

    with col4:
        st.metric("처리시간", f"{judgment_data['processing_time']:.3f}초")

    # 판단 결과 표시
    st.subheader("💭 판단 결과")
    st.info(judgment_data["judgment"])

    # 추론 과정 표시
    if "reasoning" in judgment_data and judgment_data["reasoning"]:
        st.subheader("🔍 추론 과정")
        st.text(judgment_data["reasoning"])

    # 시각화 섹션
    st.subheader("📈 시각화")

    # 탭으로 구분
    tab1, tab2, tab3, tab4 = st.tabs(
        ["감정 분석", "전략 분석", "성능 분석", "상세 정보"]
    )

    with tab1:
        display_emotion_analysis(judgment_data)

    with tab2:
        display_strategy_analysis(judgment_data)

    with tab3:
        display_performance_analysis(judgment_data)

    with tab4:
        display_detailed_info(judgment_data, input_text, context)


def display_emotion_analysis(judgment_data: dict):
    """감정 분석 시각화"""
    st.subheader("😊 감정 분석")

    # 감정별 색상 매핑
    emotion_colors = {
        "joy": "#FFD700",
        "sadness": "#4169E1",
        "anger": "#FF6347",
        "fear": "#800080",
        "surprise": "#FFA500",
        "neutral": "#808080",
    }

    detected_emotion = judgment_data["emotion_detected"]
    confidence = judgment_data["confidence"]

    # 감정 게이지 차트
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=confidence,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": f"감정: {detected_emotion}"},
            delta={"reference": 0.5},
            gauge={
                "axis": {"range": [None, 1]},
                "bar": {"color": emotion_colors.get(detected_emotion, "#808080")},
                "steps": [
                    {"range": [0, 0.3], "color": "lightgray"},
                    {"range": [0.3, 0.7], "color": "yellow"},
                    {"range": [0.7, 1], "color": "green"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 0.9,
                },
            },
        )
    )

    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

    # 감정 설명
    emotion_descriptions = {
        "joy": "😊 기쁨: 긍정적이고 즐거운 상태",
        "sadness": "😢 슬픔: 우울하고 침울한 상태",
        "anger": "😠 분노: 화가 나고 짜증나는 상태",
        "fear": "😨 두려움: 걱정되고 불안한 상태",
        "surprise": "😲 놀라움: 예상치 못한 상황에 대한 반응",
        "neutral": "😐 중립: 특별한 감정이 없는 평온한 상태",
    }

    st.info(emotion_descriptions.get(detected_emotion, "알 수 없는 감정"))


def display_strategy_analysis(judgment_data: dict):
    """전략 분석 시각화"""
    st.subheader("🎯 전략 분석")

    strategy = judgment_data["strategy_suggested"]
    confidence = judgment_data["confidence"]

    # 전략별 설명
    strategy_descriptions = {
        "logical": {
            "title": "논리적 접근",
            "description": "데이터와 사실에 기반한 체계적 분석",
            "color": "#1f77b4",
            "icon": "🧠",
        },
        "empathetic": {
            "title": "공감적 접근",
            "description": "감정과 관계를 중시하는 따뜻한 소통",
            "color": "#ff7f0e",
            "icon": "❤️",
        },
        "creative": {
            "title": "창의적 접근",
            "description": "새로운 아이디어와 혁신적 해결책",
            "color": "#2ca02c",
            "icon": "💡",
        },
        "cautious": {
            "title": "신중한 접근",
            "description": "안전하고 단계적인 진행",
            "color": "#d62728",
            "icon": "🛡️",
        },
        "balanced": {
            "title": "균형잡힌 접근",
            "description": "다양한 관점을 종합한 절충안",
            "color": "#9467bd",
            "icon": "⚖️",
        },
    }

    strategy_info = strategy_descriptions.get(
        strategy,
        {
            "title": "알 수 없는 전략",
            "description": "분류되지 않은 접근 방식",
            "color": "#808080",
            "icon": "❓",
        },
    )

    # 전략 시각화
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(
            f"""
        <div style="text-align: center; padding: 20px; background-color: {strategy_info['color']}20; border-radius: 10px;">
            <h1 style="color: {strategy_info['color']};">{strategy_info['icon']}</h1>
            <h3>{strategy_info['title']}</h3>
            <p>신뢰도: {confidence:.3f}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        **{strategy_info['title']}**
        
        {strategy_info['description']}
        
        **적용 상황:**
        - 이 전략은 현재 상황에서 {confidence:.1%} 신뢰도로 권장됩니다.
        - 감정 상태와 문맥을 고려한 최적의 접근 방식입니다.
        """
        )


def display_performance_analysis(judgment_data: dict):
    """성능 분석 시각화"""
    st.subheader("⚡ 성능 분석")

    processing_time = judgment_data["processing_time"]
    confidence = judgment_data["confidence"]

    # 성능 메트릭
    col1, col2 = st.columns(2)

    with col1:
        # 처리 시간 시각화
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=processing_time * 1000,  # 밀리초로 변환
                title={"text": "처리 시간 (ms)"},
                gauge={
                    "axis": {"range": [None, 1000]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 100], "color": "lightgreen"},
                        {"range": [100, 500], "color": "yellow"},
                        {"range": [500, 1000], "color": "lightcoral"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 1000,
                    },
                },
            )
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # 신뢰도 시각화
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=confidence,
                title={"text": "신뢰도"},
                gauge={
                    "axis": {"range": [None, 1]},
                    "bar": {"color": "darkgreen"},
                    "steps": [
                        {"range": [0, 0.3], "color": "lightcoral"},
                        {"range": [0.3, 0.7], "color": "yellow"},
                        {"range": [0.7, 1], "color": "lightgreen"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 0.9,
                    },
                },
            )
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    # 성능 분석 요약
    st.subheader("📊 성능 요약")

    performance_level = (
        "우수"
        if processing_time < 0.1
        else "보통" if processing_time < 0.5 else "개선 필요"
    )
    confidence_level = (
        "높음" if confidence > 0.7 else "보통" if confidence > 0.4 else "낮음"
    )

    st.markdown(
        f"""
    **처리 성능:** {performance_level} ({processing_time:.3f}초)
    **판단 신뢰도:** {confidence_level} ({confidence:.3f})
    
    **분석:**
    - 처리 시간이 {'빠름' if processing_time < 0.1 else '적절함' if processing_time < 0.5 else '느림'}
    - 판단 신뢰도가 {'높음' if confidence > 0.7 else '보통' if confidence > 0.4 else '낮음'}
    - {'실시간 사용에 적합' if processing_time < 0.5 and confidence > 0.5 else '성능 최적화 권장'}
    """
    )


def display_detailed_info(judgment_data: dict, input_text: str, context: str):
    """상세 정보 표시"""
    st.subheader("🔍 상세 정보")

    # 입력 정보
    st.markdown("**입력 정보:**")
    st.text(f"텍스트: {input_text}")
    if context:
        st.text(f"맥락: {context}")

    # 판단 정보
    st.markdown("**판단 정보:**")
    st.json(judgment_data)

    # 시스템 정보
    st.markdown("**시스템 정보:**")
    st.text(f"판단 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.text(
        f"모드: {'LLM-Free' if judgment_data.get('fallback_used', False) else 'Claude AI'}"
    )

    # 다운로드 버튼
    result_data = {
        "input": {"text": input_text, "context": context},
        "output": judgment_data,
        "timestamp": datetime.now().isoformat(),
    }

    st.download_button(
        label="📥 결과 다운로드 (JSON)",
        data=json.dumps(result_data, ensure_ascii=False, indent=2),
        file_name=f"judgment_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
    )


def main():
    """메인 함수"""
    st.set_page_config(
        page_title="EchoJudgmentSystem 판단 시각화",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # CSS 스타일
    st.markdown(
        """
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    create_judgment_interface()


if __name__ == "__main__":
    main()
