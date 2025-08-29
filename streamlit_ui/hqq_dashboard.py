#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 HQ-Q Dashboard - 질문 레이어별 시각화 보드
L1(핵심) → L2(증거) → L3(검증) 실시간 모니터링

# @owner: echo
# @expose
# @maturity: production
"""

import streamlit as st
import asyncio
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# 상위 디렉토리의 모듈들 import
sys.path.append(str(Path(__file__).parent.parent))

from hqq_pipeline_engine import HQPipelineEngine, EvidenceData, VerificationResult
from self_questioning_echo import HQQuestionEngine, Q

# 페이지 설정
st.set_page_config(
    page_title="🔥 HQ-Q Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 커스텀 CSS
st.markdown(
    """
<style>
    .question-card {
        border: 2px solid #e1e5e9;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f8f9fa;
    }
    
    .layer1-card {
        border-color: #007bff;
        background-color: #e3f2fd;
    }
    
    .layer2-card {
        border-color: #28a745;
        background-color: #e8f5e9;
    }
    
    .layer3-card {
        border-color: #ffc107;
        background-color: #fff8e1;
    }
    
    .status-good {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    
    .metric-box {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# 세션 상태 초기화
if "hqq_engine" not in st.session_state:
    st.session_state.hqq_engine = HQQuestionEngine()
if "pipeline_engine" not in st.session_state:
    st.session_state.pipeline_engine = HQPipelineEngine()
if "current_questions" not in st.session_state:
    st.session_state.current_questions = []
if "evidence_data" not in st.session_state:
    st.session_state.evidence_data = {}
if "verification_results" not in st.session_state:
    st.session_state.verification_results = []
if "pipeline_history" not in st.session_state:
    st.session_state.pipeline_history = []


def load_pipeline_history():
    """기존 파이프라인 결과 파일들 로드"""
    history = []

    # hqq_pipeline_results_*.json 파일들 찾기
    result_files = list(Path(".").glob("hqq_pipeline_results_*.json"))

    for file_path in sorted(
        result_files, key=lambda x: x.stat().st_mtime, reverse=True
    )[:10]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                history.append(
                    {
                        "file": file_path.name,
                        "timestamp": data.get("timestamp", ""),
                        "task": data.get("task", ""),
                        "status": data.get("summary", {}).get(
                            "overall_status", "UNKNOWN"
                        ),
                        "success_rate": data.get("summary", {}).get("success_rate", 0),
                        "data": data,
                    }
                )
        except Exception as e:
            st.sidebar.error(f"파일 로드 실패: {file_path.name} - {e}")

    return history


def display_question_card(
    question: Q,
    layer_name: str,
    evidence: EvidenceData = None,
    verification: VerificationResult = None,
):
    """질문 카드 표시"""

    # 레이어별 색상 설정
    if question.layer == 1:
        card_class = "layer1-card"
        layer_icon = "🎯"
        layer_color = "#007bff"
    elif question.layer == 2:
        card_class = "layer2-card"
        layer_icon = "🔍"
        layer_color = "#28a745"
    else:
        card_class = "layer3-card"
        layer_icon = "✅"
        layer_color = "#ffc107"

    # 상태 결정
    if evidence and evidence.confidence > 0.8:
        status_class = "status-good"
        status_text = "완료"
        status_icon = "✅"
    elif evidence and evidence.confidence > 0.5:
        status_class = "status-warning"
        status_text = "부분"
        status_icon = "⚠️"
    elif evidence:
        status_class = "status-error"
        status_text = "실패"
        status_icon = "❌"
    else:
        status_class = "status-warning"
        status_text = "대기"
        status_icon = "⏳"

    # 카드 HTML
    card_html = f"""
    <div class="question-card {card_class}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1;">
                <h4 style="margin: 0; color: {layer_color};">
                    {layer_icon} Layer {question.layer}: {layer_name}
                </h4>
                <p style="margin: 5px 0; font-size: 16px;">{question.text}</p>
                <div style="font-size: 12px; color: #666;">
                    가중치: {question.weight:.2f} | 태그: {', '.join(question.tags)} | 카테고리: {question.category}
                </div>
            </div>
            <div style="text-align: center; min-width: 80px;">
                <div style="font-size: 24px;">{status_icon}</div>
                <div class="{status_class}">{status_text}</div>
            </div>
        </div>
    """

    # 증거 데이터 표시
    if evidence:
        card_html += f"""
        <hr style="margin: 10px 0;">
        <div style="background-color: rgba(255,255,255,0.7); padding: 10px; border-radius: 5px;">
            <strong>📊 수집된 증거:</strong><br>
            <div style="font-size: 14px; margin-top: 5px;">
                타입: {evidence.evidence_type} | 신뢰도: {evidence.confidence:.2f}<br>
                결과: {evidence.processed_data[:100]}...
            </div>
        </div>
        """

    # 검증 결과 표시
    if verification:
        verification_icon = "✅" if verification.passed else "❌"
        verification_color = "#28a745" if verification.passed else "#dc3545"

        card_html += f"""
        <hr style="margin: 10px 0;">
        <div style="background-color: rgba(255,255,255,0.7); padding: 10px; border-radius: 5px;">
            <strong style="color: {verification_color};">{verification_icon} 검증 결과:</strong><br>
            <div style="font-size: 14px; margin-top: 5px;">
                기준: {verification.criteria}<br>
                실제: {verification.actual_result}<br>
                기대: {verification.expected_result}<br>
                결과: <span style="color: {verification_color};">{'통과' if verification.passed else '실패'}</span>
            </div>
        </div>
        """

    card_html += "</div>"

    st.markdown(card_html, unsafe_allow_html=True)


def create_pipeline_metrics_chart(pipeline_result: dict):
    """파이프라인 메트릭 차트 생성"""

    if not pipeline_result or "summary" not in pipeline_result:
        return None

    summary = pipeline_result["summary"]

    # 메트릭 데이터
    metrics = {
        "검증 성공률": summary.get("success_rate", 0),
        "증거 신뢰도": summary.get("evidence_confidence", 0) * 100,
        "실행 성공률": summary.get("execution_success_rate", 0),
    }

    # 방사형 차트 생성
    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=list(metrics.values()),
            theta=list(metrics.keys()),
            fill="toself",
            name="현재 성과",
            line_color="#667eea",
            fillcolor="rgba(102, 126, 234, 0.3)",
        )
    )

    # 목표 기준선 (80%)
    fig.add_trace(
        go.Scatterpolar(
            r=[80, 80, 80],
            theta=list(metrics.keys()),
            fill="toself",
            name="목표 기준",
            line_color="#28a745",
            fillcolor="rgba(40, 167, 69, 0.1)",
            line_dash="dash",
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="📊 파이프라인 성과 지표",
        height=400,
    )

    return fig


def create_evidence_confidence_chart(evidence_data: dict):
    """증거 신뢰도 차트 생성"""
    if not evidence_data:
        return None

    # 증거 타입별 신뢰도 데이터
    evidence_types = {}
    for ev in evidence_data.values():
        ev_type = ev.evidence_type
        if ev_type not in evidence_types:
            evidence_types[ev_type] = []
        evidence_types[ev_type].append(ev.confidence)

    # 평균 신뢰도 계산
    avg_confidence = {
        ev_type: sum(confidences) / len(confidences)
        for ev_type, confidences in evidence_types.items()
    }

    # 막대 차트 생성
    fig = px.bar(
        x=list(avg_confidence.keys()),
        y=list(avg_confidence.values()),
        title="🔍 증거 타입별 평균 신뢰도",
        labels={"x": "증거 타입", "y": "평균 신뢰도"},
        color=list(avg_confidence.values()),
        color_continuous_scale="Viridis",
    )

    fig.update_layout(height=400)
    fig.update_traces(texttemplate="%{y:.2f}", textposition="outside")

    return fig


def create_timeline_chart(pipeline_history: list):
    """파이프라인 실행 타임라인 차트"""
    if not pipeline_history:
        return None

    df_data = []
    for item in pipeline_history:
        try:
            timestamp = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
            df_data.append(
                {
                    "시간": timestamp,
                    "작업": (
                        item["task"][:30] + "..."
                        if len(item["task"]) > 30
                        else item["task"]
                    ),
                    "성공률": item["success_rate"],
                    "상태": item["status"],
                }
            )
        except:
            continue

    if not df_data:
        return None

    df = pd.DataFrame(df_data)

    # 상태별 색상 매핑
    color_map = {"SUCCESS": "#28a745", "PARTIAL": "#ffc107", "FAILED": "#dc3545"}

    fig = px.scatter(
        df,
        x="시간",
        y="성공률",
        color="상태",
        hover_data=["작업"],
        title="📈 파이프라인 실행 히스토리",
        color_discrete_map=color_map,
    )

    fig.update_layout(height=400)

    return fig


# 메인 UI
def main():
    """메인 UI 함수"""

    # 타이틀
    st.title("🔥 HQ-Q Dashboard")
    st.markdown("**질문 → 증거 → 검증 실시간 모니터링**")

    # 사이드바
    st.sidebar.title("🎛️ 제어판")

    # 파이프라인 히스토리 로드
    if st.sidebar.button("📂 히스토리 새로고침"):
        st.session_state.pipeline_history = load_pipeline_history()
        st.rerun()

    # 새 작업 입력
    st.sidebar.markdown("### 🚀 새 작업 실행")
    task_input = st.sidebar.text_input(
        "작업 설명", placeholder="예: 시스템 성능을 2배 빠르게 최적화해줘"
    )

    if st.sidebar.button("▶️ HQ-Q 파이프라인 실행"):
        if task_input:
            with st.spinner("HQ-Q 파이프라인 실행 중..."):
                # 비동기 실행을 위한 wrapper
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        st.session_state.pipeline_engine.execute_full_pipeline(
                            task_input, interactive=False
                        )
                    )

                    # 결과를 세션에 저장
                    st.session_state.current_result = result
                    st.session_state.pipeline_history = load_pipeline_history()

                    st.success(
                        f"✅ 파이프라인 실행 완료! 상태: {result['summary']['overall_status']}"
                    )
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ 실행 실패: {e}")
        else:
            st.sidebar.error("작업을 입력해주세요!")

    # 기존 결과 선택
    if st.session_state.pipeline_history:
        st.sidebar.markdown("### 📋 기존 결과")
        selected_history = st.sidebar.selectbox(
            "히스토리 선택",
            options=range(len(st.session_state.pipeline_history)),
            format_func=lambda x: f"{st.session_state.pipeline_history[x]['task'][:20]}... ({st.session_state.pipeline_history[x]['status']})",
        )

        if st.sidebar.button("📊 선택된 결과 보기"):
            st.session_state.current_result = st.session_state.pipeline_history[
                selected_history
            ]["data"]
            st.rerun()

    # 메인 대시보드
    if "current_result" in st.session_state and st.session_state.current_result:
        display_main_dashboard(st.session_state.current_result)
    else:
        display_welcome_screen()


def display_welcome_screen():
    """환영 화면 (외부 버전의 간결성 반영)"""

    # 외부 버전 스타일의 간단한 인터페이스 추가
    st.markdown("### 🚀 빠른 시작")

    col1, col2 = st.columns([2, 1])

    with col1:
        # 외부 버전처럼 메인 화면에서 바로 실행 가능
        quick_task = st.text_input(
            "작업을 입력하세요", placeholder="예: 시스템 성능을 2배 빠르게 최적화해줘"
        )

        if st.button("🔥 즉시 HQ-Q 파이프라인 실행", key="quick_run"):
            if quick_task:
                with st.spinner("HQ-Q 파이프라인 실행 중..."):
                    try:
                        import asyncio

                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(
                            st.session_state.pipeline_engine.execute_full_pipeline(
                                quick_task, interactive=False
                            )
                        )

                        st.session_state.current_result = result
                        st.success(
                            f"✅ 완료! 상태: {result['summary']['overall_status']}"
                        )
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ 실행 실패: {e}")
            else:
                st.error("작업을 입력해주세요!")

    with col2:
        # 외부 버전처럼 3-Layer 구조를 간단히 표시
        st.markdown(
            """
        **🎯 Layer 1**: 핵심 (5W1H)  
        **🔍 Layer 2**: 증거·제약  
        **✅ Layer 3**: 대안·검증
        """
        )

    # 기존의 상세 설명은 아래에 접이식으로
    with st.expander("📖 HQ-Q Pipeline 상세 설명"):
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown(
                """
            <div style="text-align: center; padding: 30px;">
                <h3>🔥 HQ-Q Pipeline Dashboard</h3>
                <p style="font-size: 16px; color: #666;">
                    High-Quality Question 엔진의 3단계 실행 과정을 실시간으로 모니터링합니다.
                </p>
                
                <div style="margin: 20px 0;">
                    <div style="display: flex; justify-content: space-around; margin: 15px 0;">
                        <div style="text-align: center;">
                            <div style="font-size: 36px;">🎯</div>
                            <h5>Layer 1: 핵심 질문</h5>
                            <p style="font-size: 12px;">5W1H 기반 작업 정의</p>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 36px;">🔍</div>
                            <h5>Layer 2: 증거 수집</h5>
                            <p style="font-size: 12px;">자동 데이터 수집 및 검증</p>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 36px;">✅</div>
                            <h5>Layer 3: 검증</h5>
                            <p style="font-size: 12px;">성공/실패 기준 자동 검증</p>
                        </div>
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )


def display_main_dashboard(result: dict):
    """메인 대시보드 표시"""

    # 상단 메트릭
    summary = result.get("summary", {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status = summary.get("overall_status", "UNKNOWN")
        status_color = (
            "🟢" if status == "SUCCESS" else "🟡" if status == "PARTIAL" else "🔴"
        )
        st.metric("전체 상태", f"{status_color} {status}")

    with col2:
        success_rate = summary.get("success_rate", 0)
        st.metric("검증 성공률", f"{success_rate:.1f}%")

    with col3:
        confidence = summary.get("evidence_confidence", 0)
        st.metric("증거 신뢰도", f"{confidence:.2f}")

    with col4:
        exec_rate = summary.get("execution_success_rate", 0)
        st.metric("실행 성공률", f"{exec_rate:.1f}%")

    # 탭 구성
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📋 질문 레이어", "📊 메트릭", "🔍 증거 상세", "✅ 검증 결과", "📈 히스토리"]
    )

    with tab1:
        display_question_layers(result)

    with tab2:
        display_metrics_tab(result)

    with tab3:
        display_evidence_tab(result)

    with tab4:
        display_verification_tab(result)

    with tab5:
        display_history_tab()


def display_question_layers(result: dict):
    """질문 레이어 탭"""
    st.markdown("### 🎯 HQ-Q 3-Layer 질문 구조")

    # 질문 데이터 추출
    questions = (
        result.get("pipeline_stages", {}).get("hqq_generation", {}).get("questions", [])
    )
    evidence_summary = (
        result.get("pipeline_stages", {})
        .get("evidence_collection", {})
        .get("evidence_summary", {})
    )
    verification_results = (
        result.get("pipeline_stages", {}).get("verification", {}).get("results", [])
    )

    # 질문을 Q 객체로 변환
    hq_questions = []
    for q_dict in questions:
        hq_questions.append(
            Q(
                text=q_dict["text"],
                layer=q_dict["layer"],
                tags=q_dict["tags"],
                weight=q_dict["weight"],
                pre_action=q_dict.get("pre_action"),
                category=q_dict["category"],
            )
        )

    # 레이어별 분류
    l1_questions = [q for q in hq_questions if q.layer == 1]
    l2_questions = [q for q in hq_questions if q.layer == 2]
    l3_questions = [q for q in hq_questions if q.layer == 3]

    # Layer 1 표시
    if l1_questions:
        st.markdown("#### 🎯 Layer 1: 핵심 질문 (5W1H)")
        for q in l1_questions:
            display_question_card(q, "핵심 정의")

    # Layer 2 표시
    if l2_questions:
        st.markdown("#### 🔍 Layer 2: 증거 & 제약 질문")
        for q in l2_questions:
            # 해당 질문의 증거 데이터 찾기
            evidence = None
            for ev_q, ev_data in evidence_summary.items():
                if q.text in ev_q:
                    evidence = EvidenceData(
                        question=ev_q,
                        evidence_type=ev_data["type"],
                        raw_data=None,
                        processed_data=ev_data["summary"],
                        timestamp="",
                        confidence=ev_data["confidence"],
                    )
                    break

            display_question_card(q, "증거 수집", evidence=evidence)

    # Layer 3 표시
    if l3_questions:
        st.markdown("#### ✅ Layer 3: 대안 & 검증 질문")
        for q in l3_questions:
            # 해당 질문의 검증 결과 찾기
            verification = None
            for v_result in verification_results:
                if q.text in v_result.get("question", ""):
                    verification = VerificationResult(
                        question=v_result["question"],
                        criteria=v_result["criteria"],
                        actual_result=v_result["actual_result"],
                        expected_result=v_result["expected_result"],
                        passed=v_result["passed"],
                        details=v_result["details"],
                        timestamp=v_result["timestamp"],
                    )
                    break

            display_question_card(q, "검증", verification=verification)


def display_metrics_tab(result: dict):
    """메트릭 탭"""
    st.markdown("### 📊 파이프라인 성과 분석")

    # 메트릭 차트
    metrics_chart = create_pipeline_metrics_chart(result)
    if metrics_chart:
        st.plotly_chart(metrics_chart, use_container_width=True)

    # 증거 신뢰도 차트
    evidence_summary = (
        result.get("pipeline_stages", {})
        .get("evidence_collection", {})
        .get("evidence_summary", {})
    )
    if evidence_summary:
        # EvidenceData 객체들 생성
        evidence_data = {}
        for q, ev_data in evidence_summary.items():
            evidence_data[q] = EvidenceData(
                question=q,
                evidence_type=ev_data["type"],
                raw_data=None,
                processed_data=ev_data["summary"],
                timestamp="",
                confidence=ev_data["confidence"],
            )

        confidence_chart = create_evidence_confidence_chart(evidence_data)
        if confidence_chart:
            st.plotly_chart(confidence_chart, use_container_width=True)

    # 상세 메트릭 테이블
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📋 단계별 실행 통계")
        stages = result.get("pipeline_stages", {})

        stage_data = []
        for stage_name, stage_data_dict in stages.items():
            if isinstance(stage_data_dict, dict):
                total = stage_data_dict.get(
                    "total_items",
                    stage_data_dict.get(
                        "total_questions", stage_data_dict.get("total_evidence", 0)
                    ),
                )
                completed = stage_data_dict.get(
                    "completed", stage_data_dict.get("passed", 0)
                )

                stage_data.append(
                    {
                        "단계": stage_name.replace("_", " ").title(),
                        "총 항목": total,
                        "완료": completed,
                        "성공률": (
                            f"{(completed/total*100):.1f}%" if total > 0 else "N/A"
                        ),
                    }
                )

        if stage_data:
            st.dataframe(pd.DataFrame(stage_data), use_container_width=True)

    with col2:
        st.markdown("#### 💡 권장사항")
        recommendations = result.get("summary", {}).get("recommendations", [])
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")

        st.markdown("#### 🎯 다음 액션")
        next_actions = result.get("summary", {}).get("next_actions", [])
        for i, action in enumerate(next_actions, 1):
            st.write(f"{i}. {action}")


def display_evidence_tab(result: dict):
    """증거 상세 탭"""
    st.markdown("### 🔍 수집된 증거 상세 분석")

    evidence_summary = (
        result.get("pipeline_stages", {})
        .get("evidence_collection", {})
        .get("evidence_summary", {})
    )

    if not evidence_summary:
        st.info("수집된 증거가 없습니다.")
        return

    for question, ev_data in evidence_summary.items():
        with st.expander(f"📋 {question[:60]}..."):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**증거 타입:** {ev_data['type']}")
                st.markdown(f"**신뢰도:** {ev_data['confidence']:.2f}")
                st.markdown(f"**요약:**")
                st.code(ev_data["summary"], language="text")

            with col2:
                # 신뢰도 게이지
                fig = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=ev_data["confidence"],
                        domain={"x": [0, 1], "y": [0, 1]},
                        title={"text": "신뢰도"},
                        gauge={
                            "axis": {"range": [None, 1]},
                            "bar": {"color": "darkblue"},
                            "steps": [
                                {"range": [0, 0.5], "color": "lightgray"},
                                {"range": [0.5, 0.8], "color": "yellow"},
                                {"range": [0.8, 1], "color": "green"},
                            ],
                            "threshold": {
                                "line": {"color": "red", "width": 4},
                                "thickness": 0.75,
                                "value": 0.9,
                            },
                        },
                    )
                )

                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)


def display_verification_tab(result: dict):
    """검증 결과 탭"""
    st.markdown("### ✅ 검증 결과 상세")

    verification_results = (
        result.get("pipeline_stages", {}).get("verification", {}).get("results", [])
    )

    if not verification_results:
        st.info("검증 결과가 없습니다.")
        return

    # 검증 통계
    total_verifications = len(verification_results)
    passed_verifications = sum(
        1 for v in verification_results if v.get("passed", False)
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 검증", total_verifications)
    with col2:
        st.metric("성공", passed_verifications, delta=None)
    with col3:
        st.metric("실패", total_verifications - passed_verifications, delta=None)

    # 검증 결과 상세
    for i, v_result in enumerate(verification_results, 1):
        status_icon = "✅" if v_result.get("passed", False) else "❌"
        status_color = "green" if v_result.get("passed", False) else "red"

        with st.expander(
            f"{status_icon} 검증 {i}: {v_result.get('criteria', 'Unknown')}"
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**질문:** {v_result.get('question', 'N/A')}")
                st.markdown(f"**검증 기준:** {v_result.get('criteria', 'N/A')}")
                st.markdown(f"**실제 결과:** {v_result.get('actual_result', 'N/A')}")
                st.markdown(f"**기대 결과:** {v_result.get('expected_result', 'N/A')}")

            with col2:
                st.markdown(
                    f"**상태:** :{status_color}[{'통과' if v_result.get('passed', False) else '실패'}]"
                )
                st.markdown(f"**상세 설명:**")
                st.info(v_result.get("details", "N/A"))


def display_history_tab():
    """히스토리 탭"""
    st.markdown("### 📈 파이프라인 실행 히스토리")

    if not st.session_state.pipeline_history:
        st.session_state.pipeline_history = load_pipeline_history()

    if not st.session_state.pipeline_history:
        st.info("실행 히스토리가 없습니다.")
        return

    # 타임라인 차트
    timeline_chart = create_timeline_chart(st.session_state.pipeline_history)
    if timeline_chart:
        st.plotly_chart(timeline_chart, use_container_width=True)

    # 히스토리 테이블
    st.markdown("#### 📋 실행 기록 목록")

    history_data = []
    for item in st.session_state.pipeline_history:
        history_data.append(
            {
                "시간": item["timestamp"][:19].replace("T", " "),
                "작업": (
                    item["task"][:50] + "..."
                    if len(item["task"]) > 50
                    else item["task"]
                ),
                "상태": item["status"],
                "성공률": f"{item['success_rate']:.1f}%",
                "파일": item["file"],
            }
        )

    if history_data:
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main()
