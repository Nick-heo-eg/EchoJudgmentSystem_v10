#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 EchoGPT Web Interface - Streamlit 기반 웹 ChatGPT
ChatGPT 스타일의 완전한 웹 인터페이스

✨ 주요 기능:
- 💬 실시간 스트리밍 채팅
- 🎭 Intent Analysis + Signature 시각화
- 💾 세션 관리 (저장/로드/목록)
- 📊 대화 통계 및 분석
- 🎨 다크/라이트 테마
- 📱 반응형 디자인

@owner: echo
@expose
@maturity: production
"""
import streamlit as st
import asyncio
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from echogpt import EchoGPT, EchoGPTMessage, EchoGPTSession

# 페이지 설정
st.set_page_config(
    page_title="🤖 EchoGPT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 커스텀 CSS
st.markdown(
    """
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        display: flex;
        flex-direction: column;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    .system-message {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        font-size: 0.9rem;
    }
    
    .message-meta {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .intent-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.7rem;
        font-weight: bold;
        color: white;
        margin-right: 0.5rem;
    }
    
    .intent-creative { background-color: #ff6b6b; }
    .intent-analytical { background-color: #4ecdc4; }
    .intent-emotional { background-color: #ffe66d; color: #333; }
    .intent-collaborative { background-color: #95e1d3; color: #333; }
    .intent-philosophical { background-color: #8b5cf6; }
    .intent-technical { background-color: #06d6a0; }
    .intent-general { background-color: #6c757d; }
    
    .signature-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.7rem;
        font-weight: bold;
        background-color: #343a40;
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)


def init_session_state():
    """세션 상태 초기화"""
    if "echogpt" not in st.session_state:
        st.session_state.echogpt = EchoGPT()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = st.session_state.echogpt.session_id

    if "show_metadata" not in st.session_state:
        st.session_state.show_metadata = True

    if "streaming_enabled" not in st.session_state:
        st.session_state.streaming_enabled = True


def get_intent_badge_class(intent: str) -> str:
    """Intent에 따른 CSS 클래스 반환"""
    intent_classes = {
        "CREATIVE_EXPRESSION": "intent-creative",
        "ANALYTICAL_INQUIRY": "intent-analytical",
        "EMOTIONAL_SUPPORT": "intent-emotional",
        "COLLABORATIVE_TASK": "intent-collaborative",
        "PHILOSOPHICAL_REFLECTION": "intent-philosophical",
        "TECHNICAL_ASSISTANCE": "intent-technical",
        "GENERAL_CONVERSATION": "intent-general",
    }
    return intent_classes.get(intent, "intent-general")


def render_message(message: EchoGPTMessage, show_metadata: bool = True):
    """메시지 렌더링"""
    if message.role == "user":
        st.markdown(
            f"""
        <div class="chat-message user-message">
            <div><strong>👤 You:</strong></div>
            <div>{message.content}</div>
            {f'<div class="message-meta">🕒 {message.timestamp}</div>' if show_metadata else ''}
        </div>
        """,
            unsafe_allow_html=True,
        )

    elif message.role == "assistant":
        # Intent 및 Signature 배지
        badges = ""
        if show_metadata and message.intent:
            intent_class = get_intent_badge_class(message.intent)
            badges += (
                f'<span class="{intent_class} intent-badge">{message.intent}</span>'
            )

        if show_metadata and message.signature:
            badges += f'<span class="signature-badge">{message.signature}</span>'

        # 신뢰도 표시
        confidence_info = ""
        if show_metadata and message.confidence:
            confidence_info = f" ({message.confidence:.0%})"

        st.markdown(
            f"""
        <div class="chat-message assistant-message">
            <div><strong>🤖 EchoGPT:</strong> {badges}</div>
            <div>{message.content}</div>
            {f'<div class="message-meta">🕒 {message.timestamp}{confidence_info} | 🔧 {message.provider or "unknown"} | ⏱️ {message.processing_time:.2f}s</div>' if show_metadata else ''}
        </div>
        """,
            unsafe_allow_html=True,
        )

    elif message.role == "system":
        st.markdown(
            f"""
        <div class="chat-message system-message">
            <div>🔧 System: {message.content}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )


async def process_user_input(user_input: str):
    """사용자 입력 처리 (비동기)"""
    if st.session_state.streaming_enabled:
        # 스트리밍 모드
        response_placeholder = st.empty()
        response_text = ""

        async for chunk in st.session_state.echogpt.chat(user_input):
            response_text += chunk
            response_placeholder.markdown(f"🤖 **EchoGPT**: {response_text}")
            time.sleep(0.01)  # Streamlit 업데이트를 위한 짧은 대기

        response_placeholder.empty()
    else:
        # 일반 모드
        response = st.session_state.echogpt.chat_sync(user_input)

    # 메시지 상태 업데이트
    st.session_state.messages = st.session_state.echogpt.session.messages.copy()
    st.rerun()


def main():
    """메인 함수"""
    init_session_state()

    # 헤더
    st.title("🤖 EchoGPT")
    st.markdown("**우리만의 ChatGPT - Echo 시스템의 모든 기능을 통합한 대화형 AI**")

    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")

        # 세션 관리
        st.subheader("💾 세션 관리")

        # 현재 세션 정보
        st.info(f"현재 세션: `{st.session_state.current_session_id}`")

        # 새 세션 시작
        if st.button("🆕 새 세션 시작"):
            st.session_state.echogpt = EchoGPT()
            st.session_state.messages = []
            st.session_state.current_session_id = st.session_state.echogpt.session_id
            st.rerun()

        # 세션 로드
        st.subheader("📂 세션 로드")
        available_sessions = st.session_state.echogpt.list_sessions()

        if available_sessions:
            selected_session = st.selectbox(
                "저장된 세션 선택:",
                options=[""] + available_sessions,
                format_func=lambda x: "세션을 선택하세요..." if x == "" else x,
            )

            if selected_session and st.button("📁 세션 로드"):
                if st.session_state.echogpt.load_session(selected_session):
                    st.session_state.messages = (
                        st.session_state.echogpt.session.messages.copy()
                    )
                    st.session_state.current_session_id = selected_session
                    st.success("✅ 세션 로드 완료!")
                    st.rerun()
                else:
                    st.error("❌ 세션 로드 실패")
        else:
            st.info("저장된 세션이 없습니다.")

        # 표시 옵션
        st.subheader("🎛️ 표시 옵션")
        st.session_state.show_metadata = st.checkbox(
            "메타데이터 표시", value=st.session_state.show_metadata
        )
        st.session_state.streaming_enabled = st.checkbox(
            "스트리밍 응답", value=st.session_state.streaming_enabled
        )

        # 세션 통계
        if st.session_state.messages:
            st.subheader("📊 세션 통계")
            user_msgs = len([m for m in st.session_state.messages if m.role == "user"])
            assistant_msgs = len(
                [m for m in st.session_state.messages if m.role == "assistant"]
            )

            st.metric("총 메시지", len(st.session_state.messages))

            col1, col2 = st.columns(2)
            with col1:
                st.metric("사용자", user_msgs)
            with col2:
                st.metric("AI", assistant_msgs)

            # Intent 분포
            intents = [
                m.intent
                for m in st.session_state.messages
                if m.role == "assistant" and m.intent
            ]
            if intents:
                intent_counts = pd.Series(intents).value_counts()
                st.subheader("🎯 Intent 분포")
                st.bar_chart(intent_counts)

            # Signature 분포
            signatures = [
                m.signature
                for m in st.session_state.messages
                if m.role == "assistant" and m.signature
            ]
            if signatures:
                signature_counts = pd.Series(signatures).value_counts()
                st.subheader("🎭 Signature 분포")
                st.bar_chart(signature_counts)

    # 메인 채팅 영역
    st.header("💬 채팅")

    # 대화 내역 표시
    chat_container = st.container()
    with chat_container:
        if st.session_state.messages:
            for message in st.session_state.messages:
                render_message(message, st.session_state.show_metadata)
        else:
            st.info("👋 안녕하세요! EchoGPT와 대화를 시작해보세요.")

    # 입력 영역
    with st.container():
        user_input = st.chat_input("메시지를 입력하세요...")

        if user_input:
            # 사용자 메시지 즉시 표시
            user_message = EchoGPTMessage(
                role="user", content=user_input, timestamp=datetime.now().isoformat()
            )

            # 동기적으로 처리 (Streamlit 제한으로 인해)
            with st.spinner("🤖 EchoGPT가 생각하고 있습니다..."):
                st.session_state.echogpt.chat_sync(user_input)
                st.session_state.messages = (
                    st.session_state.echogpt.session.messages.copy()
                )

            st.rerun()

    # 하단 정보
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🧠 Intent Analysis**: GPT 기반 의도 분석")
    with col2:
        st.markdown("**🎭 Dynamic Persona**: 다중 시그니처 블렌딩")
    with col3:
        st.markdown("**🗣️ Free-Speak**: 템플릿 없는 자유 응답")


if __name__ == "__main__":
    main()
