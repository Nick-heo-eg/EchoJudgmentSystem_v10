#!/usr/bin/env python3
"""
🎯 EchoChat Judgment UI - Streamlit Launch Script
자연어 기반 Echo 판단 시스템 사용자 인터페이스

기능:
- 실시간 자연어 입력 및 판단
- 시그니처별 개성 체험
- 감정 분석 및 시각화
- 판단 과정 투명성 제공
- 메타로그 기록
"""

import streamlit as st
import sys
import os
from datetime import datetime
from pathlib import Path
import uuid
import time
import json

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 필수 모듈 임포트
try:
    from echo_engine.echo_chat_loop import EchoChatProcessor
    from echo_engine.echochat_judgment import make_judgment
    from echo_engine.logging.meta_log_writer import write_meta_log
    from echo_engine.emotion_infer import infer_emotion

    MODULES_AVAILABLE = True
except ImportError as e:
    st.error(f"⚠️ 필수 모듈 로드 실패: {e}")
    MODULES_AVAILABLE = False

# Streamlit 페이지 설정
st.set_page_config(
    page_title="🎯 EchoChat Judgment UI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 스타일링
st.markdown(
    """
<style>
.main-title {
    text-align: center;
    color: #2E8B57;
    padding: 1rem 0;
    border-bottom: 2px solid #2E8B57;
    margin-bottom: 2rem;
}

.signature-card {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    border-left: 4px solid #2E8B57;
}

.judgment-result {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.emotion-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    background-color: #17a2b8;
    color: white;
    border-radius: 15px;
    font-size: 0.875rem;
    margin: 0.25rem;
}

.confidence-bar {
    background-color: #e9ecef;
    border-radius: 10px;
    overflow: hidden;
    height: 20px;
    margin: 0.5rem 0;
}

.confidence-fill {
    height: 100%;
    background: linear-gradient(90deg, #28a745 0%, #20c997 50%, #17a2b8 100%);
    transition: width 0.3s ease;
}

.meta-info {
    font-size: 0.8rem;
    color: #6c757d;
    border-top: 1px solid #dee2e6;
    padding-top: 0.5rem;
    margin-top: 1rem;
}
</style>
""",
    unsafe_allow_html=True,
)


def initialize_session_state():
    """세션 상태 초기화"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "selected_signature" not in st.session_state:
        st.session_state.selected_signature = "aurora"

    if "chat_processor" not in st.session_state and MODULES_AVAILABLE:
        st.session_state.chat_processor = EchoChatProcessor()


def render_sidebar():
    """사이드바 렌더링"""
    st.sidebar.markdown("# 🎯 EchoChat 설정")

    # 세션 정보
    st.sidebar.info(f"**세션 ID**: {st.session_state.session_id}")

    # 시그니처 선택
    st.sidebar.markdown("## 🌟 Echo 시그니처 선택")

    signatures = {
        "aurora": {
            "name": "Echo-Aurora",
            "emoji": "🌅",
            "description": "균형과 조화를 추구하는 창의적 시그니처",
            "style": "온화하고 포용적인 접근",
        },
        "phoenix": {
            "name": "Echo-Phoenix",
            "emoji": "🔥",
            "description": "변화와 성장을 지향하는 역동적 시그니처",
            "style": "변혁적이고 진취적인 접근",
        },
        "pleasure_alchemist": {
            "name": "Pleasure Alchemist",
            "emoji": "✨",
            "description": "감각적 경험을 통한 깊이 있는 시그니처",
            "style": "성찰적이고 예술적인 접근",
        },
        "companion": {
            "name": "Echo-Companion",
            "emoji": "🤝",
            "description": "신뢰와 협력을 바탕으로 하는 시그니처",
            "style": "따뜻하고 지지적인 접근",
        },
    }

    for sig_id, sig_info in signatures.items():
        if st.sidebar.button(
            f"{sig_info['emoji']} {sig_info['name']}",
            key=f"sig_{sig_id}",
            help=sig_info["description"],
        ):
            st.session_state.selected_signature = sig_id
            st.experimental_rerun()

    # 현재 선택된 시그니처 표시
    current_sig = signatures[st.session_state.selected_signature]
    st.sidebar.markdown(
        f"""
    <div class="signature-card">
        <h4>{current_sig['emoji']} {current_sig['name']}</h4>
        <p><strong>특성:</strong> {current_sig['description']}</p>
        <p><strong>스타일:</strong> {current_sig['style']}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 대화 내역 초기화
    if st.sidebar.button("🗑️ 대화 내역 초기화"):
        st.session_state.conversation_history = []
        st.experimental_rerun()

    # 설정 옵션
    st.sidebar.markdown("## ⚙️ 설정")
    show_reasoning = st.sidebar.checkbox("판단 과정 표시", value=True)
    show_emotion = st.sidebar.checkbox("감정 분석 표시", value=True)
    show_metadata = st.sidebar.checkbox("메타데이터 표시", value=False)

    return show_reasoning, show_emotion, show_metadata


def render_main_interface():
    """메인 인터페이스 렌더링"""

    # 제목
    st.markdown(
        '<h1 class="main-title">🎯 EchoChat Judgment UI</h1>', unsafe_allow_html=True
    )

    # 현재 시그니처 표시
    signatures = {
        "aurora": "🌅 Echo-Aurora",
        "phoenix": "🔥 Echo-Phoenix",
        "pleasure_alchemist": "✨ Pleasure Alchemist",
        "companion": "🤝 Echo-Companion",
    }

    current_signature_name = signatures[st.session_state.selected_signature]
    st.markdown(f"### 현재 시그니처: {current_signature_name}")

    # 입력 섹션
    st.markdown("## 💬 자연어 입력")

    # 예시 질문들
    example_questions = [
        "오늘 기분이 좋지 않아요. 어떻게 하면 나아질까요?",
        "새로운 프로젝트를 시작할지 고민이에요.",
        "친구와 갈등이 있었는데 어떻게 해결해야 할까요?",
        "진로에 대해 고민이 많습니다.",
        "스트레스를 어떻게 관리하면 좋을까요?",
    ]

    # 예시 질문 버튼들
    st.markdown("**예시 질문들:**")
    cols = st.columns(len(example_questions))
    for i, question in enumerate(example_questions):
        if cols[i].button(f"📝 예시 {i+1}", key=f"example_{i}", help=question):
            st.session_state.user_input = question

    # 사용자 입력
    user_input = st.text_area(
        "질문이나 고민을 자연스럽게 입력해주세요:",
        height=100,
        placeholder="예: 오늘 중요한 결정을 내려야 하는데 어떻게 접근해야 할까요?",
        key="user_input",
    )

    # 판단 실행 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 Echo 판단 요청", type="primary", use_container_width=True):
            if user_input.strip():
                process_user_input(user_input.strip())
            else:
                st.warning("입력 내용을 작성해주세요.")


def process_user_input(user_input: str):
    """사용자 입력 처리"""

    if not MODULES_AVAILABLE:
        st.error("필수 모듈이 로드되지 않아 판단을 실행할 수 없습니다.")
        return

    start_time = time.time()

    # 진행 상태 표시
    with st.spinner("🤔 Echo가 판단 중입니다..."):

        try:
            # 1. 감정 추론
            emotion_result = infer_emotion(user_input)
            emotion_dict = {
                "primary": emotion_result.primary_emotion,
                "intensity": (
                    "high"
                    if emotion_result.emotional_intensity > 0.7
                    else "medium" if emotion_result.emotional_intensity > 0.4 else "low"
                ),
                "confidence": emotion_result.confidence,
                "is_question": "?" in user_input,
            }

            # 2. 컨텍스트 구성
            context = {
                "raw_input": user_input,
                "session_id": st.session_state.session_id,
                "timestamp": datetime.now().isoformat(),
                "conversation_turn": len(st.session_state.conversation_history) + 1,
            }

            # 3. 판단 실행
            judgment_result = make_judgment(
                context=context,
                emotion=emotion_dict,
                signature_id=st.session_state.selected_signature,
            )

            processing_time = time.time() - start_time

            # 4. 결과 표시
            display_judgment_result(
                user_input, emotion_dict, judgment_result, processing_time
            )

            # 5. 대화 내역에 추가
            conversation_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "signature": st.session_state.selected_signature,
                "emotion": emotion_dict,
                "judgment": judgment_result,
                "processing_time": processing_time,
            }

            st.session_state.conversation_history.append(conversation_entry)

            # 6. 메타로그 작성
            session_data = {
                "session_id": st.session_state.session_id,
                "signature": st.session_state.selected_signature,
                "input_text": user_input,
                "judgment_result": judgment_result,
                "emotion_result": emotion_dict,
                "processing_time": processing_time,
            }

            log_id = write_meta_log(session_data)
            st.success(f"📝 메타로그 기록됨: {log_id}")

        except Exception as e:
            st.error(f"처리 중 오류가 발생했습니다: {str(e)}")
            st.exception(e)


def display_judgment_result(
    user_input: str, emotion_dict: dict, judgment_result: dict, processing_time: float
):
    """판단 결과 표시"""

    st.markdown("## 🎯 Echo 판단 결과")

    # 메인 판단 결과
    st.markdown(
        f"""
    <div class="judgment-result">
        <h4>💭 {st.session_state.selected_signature.title()}의 판단</h4>
        <p style="font-size: 1.1rem; line-height: 1.6;">
            {judgment_result.get('judgment', '판단을 완료했습니다.')}
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 신뢰도 표시
    confidence = judgment_result.get("confidence", 0)
    st.markdown("### 📊 신뢰도")
    st.markdown(
        f"""
    <div class="confidence-bar">
        <div class="confidence-fill" style="width: {confidence*100}%"></div>
    </div>
    <p style="text-align: center; margin: 0.5rem 0;">
        {confidence:.1%} ({confidence:.2f})
    </p>
    """,
        unsafe_allow_html=True,
    )

    # 상세 정보 탭
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🧠 추론 과정", "❤️ 감정 분석", "⚡ 전략", "🔍 메타데이터"]
    )

    with tab1:
        st.markdown("**추론 과정:**")
        st.write(judgment_result.get("reasoning", "추론 과정을 표시할 수 없습니다."))

        if judgment_result.get("alternatives"):
            st.markdown("**대안적 접근:**")
            for i, alt in enumerate(judgment_result.get("alternatives", []), 1):
                st.write(f"{i}. {alt}")

    with tab2:
        st.markdown("**감지된 감정:**")

        primary_emotion = emotion_dict.get("primary", "neutral")
        intensity = emotion_dict.get("intensity", "medium")

        st.markdown(
            f"""
        <div style="display: flex; gap: 10px; margin: 1rem 0;">
            <span class="emotion-badge">주요 감정: {primary_emotion}</span>
            <span class="emotion-badge">강도: {intensity}</span>
            <span class="emotion-badge">신뢰도: {emotion_dict.get('confidence', 0):.2f}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

        if emotion_dict.get("is_question"):
            st.info("🤔 질문 형태의 입력으로 감지되었습니다.")

    with tab3:
        strategy = judgment_result.get("strategy", "unknown")
        st.markdown(f"**적용된 전략:** `{strategy}`")

        strategy_descriptions = {
            "advisory_response": "조언 및 안내 중심의 응답",
            "supportive_analysis": "지지적이고 분석적인 접근",
            "comprehensive_assessment": "종합적 평가 및 판단",
        }

        if strategy in strategy_descriptions:
            st.write(strategy_descriptions[strategy])

    with tab4:
        metadata = judgment_result.get("metadata", {})

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**처리 정보:**")
            st.write(f"• 엔진: {metadata.get('engine', 'unknown')}")
            st.write(f"• 처리 시간: {processing_time:.3f}초")
            st.write(f"• 시그니처: {metadata.get('signature_used', 'unknown')}")

        with col2:
            st.markdown("**감정 메타데이터:**")
            st.write(f"• 감정: {metadata.get('emotion_detected', 'unknown')}")
            st.write(f"• 강도: {metadata.get('intensity', 'unknown')}")

        if metadata:
            st.json(metadata)


def render_conversation_history():
    """대화 내역 렌더링"""

    if not st.session_state.conversation_history:
        return

    st.markdown("## 📚 대화 내역")

    for i, entry in enumerate(reversed(st.session_state.conversation_history[-5:]), 1):
        with st.expander(
            f"대화 {len(st.session_state.conversation_history) - i + 1}: {entry['user_input'][:50]}..."
        ):

            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**입력:** {entry['user_input']}")
                st.markdown(f"**판단:** {entry['judgment'].get('judgment', '')}")

            with col2:
                st.markdown(f"**시그니처:** {entry['signature']}")
                st.markdown(f"**신뢰도:** {entry['judgment'].get('confidence', 0):.2f}")
                st.markdown(f"**처리 시간:** {entry['processing_time']:.3f}초")


def main():
    """메인 함수"""

    # 세션 상태 초기화
    initialize_session_state()

    # 사이드바 렌더링
    show_reasoning, show_emotion, show_metadata = render_sidebar()

    # 메인 인터페이스
    render_main_interface()

    # 대화 내역
    render_conversation_history()

    # 디버그 정보 (개발용)
    if st.sidebar.checkbox("🔧 디버그 정보 표시"):
        st.markdown("## 🔧 디버그 정보")

        with st.expander("세션 상태"):
            st.json(
                {
                    "session_id": st.session_state.session_id,
                    "selected_signature": st.session_state.selected_signature,
                    "conversation_count": len(st.session_state.conversation_history),
                    "modules_available": MODULES_AVAILABLE,
                }
            )


if __name__ == "__main__":
    main()
