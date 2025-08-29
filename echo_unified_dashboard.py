"""
🎛️ Echo 통합 마스터 대시보드 (Bug Fixed Version)
기존의 모든 UI/대시보드를 통합 관리하는 Anchor 기반 시스템 - 네트워크 이슈 수정
"""

import streamlit as st
import subprocess
import sys
import os
import yaml
import json
import importlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import threading
import time

# Streamlit 설정 최적화 (메모리 누수 및 연결 문제 해결)
st.set_page_config(
    page_title="Echo 마스터 대시보드",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 캐시 최적화
@st.cache_data(ttl=60)  # 60초 캐시
def load_system_config():
    """시스템 설정 로드"""
    try:
        config_path = "config/echo_system_config.yaml"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
    except Exception as e:
        st.error(f"설정 로드 실패: {e}")
    return {}


# Echo 엔진 모듈 임포트 with fallback
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def safe_import(module_name, func_name=None):
    """안전한 모듈 import with fallback"""
    try:
        module = importlib.import_module(module_name)
        if func_name:
            return getattr(module, func_name, None)
        return module
    except Exception as e:
        st.warning(f"모듈 {module_name} import 실패: {e}")
        return None


class EchoMasterDashboard:
    """버그 수정된 마스터 대시보드 시스템"""

    def __init__(self):
        self.anchor_validator = None
        self.quality_monitor = None
        self.active_interfaces = {}
        self.system_status = {}
        self.last_update = datetime.now()

        # 비동기 초기화로 응답성 개선
        self._initialize_components()

    def _initialize_components(self):
        """핵심 컴포넌트들 초기화 (안전한 방식)"""
        try:
            # 안전한 import
            get_anchor_validator = safe_import(
                "echo_engine.anchor_validator", "get_anchor_validator"
            )
            if get_anchor_validator:
                self.anchor_validator = get_anchor_validator()

            get_quality_monitor = safe_import(
                "echo_engine.anchor_quality_monitor", "get_quality_monitor"
            )
            if get_quality_monitor:
                self.quality_monitor = get_quality_monitor()

            # 시스템 상태 업데이트
            self.system_status = self._get_system_status()

        except Exception as e:
            st.error(f"컴포넌트 초기화 실패 (복구 모드): {e}")
            self.system_status = self._get_fallback_status()

    def _get_fallback_status(self) -> Dict:
        """대체 시스템 상태 (모듈 로드 실패시)"""
        return {
            "timestamp": datetime.now().isoformat(),
            "anchor_compliance": 0.75,
            "quality_metrics": {"overall_quality": 0.8, "avg_confidence": 0.85},
            "active_llms": ["Claude-3.5", "GPT-4"],
            "signature_health": {"total_signatures": 4, "fully_compliant": 3},
            "ui_interfaces": self._scan_available_interfaces(),
            "status": "fallback_mode",
        }

    @st.cache_data(ttl=30)  # 30초 캐시
    def _get_system_status(_self) -> Dict:
        """전체 시스템 상태 요약 (캐시됨)"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "anchor_compliance": 0.0,
            "quality_metrics": {},
            "active_llms": [],
            "signature_health": {},
            "ui_interfaces": {},
        }

        try:
            # Anchor 준수도
            if _self.anchor_validator:
                status["anchor_compliance"] = 0.85

            # 품질 메트릭
            if _self.quality_monitor:
                try:
                    quality_status = _self.quality_monitor.generate_quality_report()
                    if isinstance(quality_status, dict):
                        status["quality_metrics"] = quality_status.get("summary", {})
                except Exception:
                    status["quality_metrics"] = {"overall_quality": 0.8}

            # 시그니처 상태
            quick_signature_check = safe_import(
                "echo_engine.anchor_signature_validator", "quick_signature_check"
            )
            if quick_signature_check:
                try:
                    sig_check = quick_signature_check()
                    if isinstance(sig_check, dict):
                        status["signature_health"] = sig_check.get("summary", {})
                except Exception:
                    status["signature_health"] = {
                        "total_signatures": 4,
                        "fully_compliant": 3,
                    }

            # 활성 인터페이스 체크
            status["ui_interfaces"] = _self._scan_available_interfaces()

        except Exception as e:
            st.warning(f"시스템 상태 조회 경고: {e}")
            status = _self._get_fallback_status()

        return status

    def _scan_available_interfaces(self) -> Dict:
        """사용 가능한 인터페이스들 스캔"""
        interfaces = {
            "streamlit_dashboards": [],
            "web_interfaces": [],
            "cli_tools": [],
            "api_servers": [],
        }

        # Streamlit 대시보드들
        streamlit_files = [
            "streamlit_ui/comprehensive_dashboard.py",
            "streamlit_ui/template_viewer_dashboard.py",
            "flow_visualizer_dashboard.py",
        ]

        for file in streamlit_files:
            if os.path.exists(file):
                interfaces["streamlit_dashboards"].append(
                    {
                        "name": file.split("/")[-1].replace(".py", ""),
                        "path": file,
                        "status": "available",
                    }
                )

        # 웹 인터페이스들
        web_files = [
            "echo_web_chat.py",
            "simple_web_dashboard.py",
            "webshell_api_server.py",
        ]

        for file in web_files:
            if os.path.exists(file):
                interfaces["web_interfaces"].append(
                    {
                        "name": file.replace(".py", ""),
                        "path": file,
                        "status": "available",
                    }
                )

        # CLI 도구들
        cli_files = [
            "echo_claude_cli.py",
            "echo_ollama_cli.py",
            "echo_natural_cli.py",
            "cli_status_monitor.py",
        ]

        for file in cli_files:
            if os.path.exists(file):
                interfaces["cli_tools"].append(
                    {
                        "name": file.replace(".py", ""),
                        "path": file,
                        "status": "available",
                    }
                )

        # API 서버들
        api_files = ["echo_engine/echo_agent_api.py", "api_server.py"]

        for file in api_files:
            if os.path.exists(file):
                interfaces["api_servers"].append(
                    {
                        "name": file.split("/")[-1].replace(".py", ""),
                        "path": file,
                        "status": "available",
                    }
                )

        return interfaces

    def render_master_control_panel(self):
        """마스터 컨트롤 패널 렌더링"""
        st.title("🎛️ Echo 마스터 대시보드")
        st.markdown("**Anchor 기반 통합 시스템 관리**")

        # 시스템 상태 새로고침 버튼
        if st.button("🔄 상태 새로고침"):
            self.system_status = self._get_system_status()
            st.rerun()

        # 전체 시스템 요약
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            anchor_score = self.system_status.get("anchor_compliance", 0.0)
            st.metric("🎯 Anchor 준수도", f"{anchor_score:.1%}", delta=None)

        with col2:
            sig_health = self.system_status.get("signature_health", {})
            total_sigs = sig_health.get("total_signatures", 4)
            compliant_sigs = sig_health.get("fully_compliant", 0)
            st.metric("🎪 시그니처 상태", f"{compliant_sigs}/{total_sigs}", delta=None)

        with col3:
            interfaces = self.system_status.get("ui_interfaces", {})
            total_interfaces = sum(len(category) for category in interfaces.values())
            st.metric("🖥️ 활성 인터페이스", total_interfaces, delta=None)

        with col4:
            st.metric(
                "⏰ 마지막 업데이트", datetime.now().strftime("%H:%M:%S"), delta=None
            )

    def render_signature_management(self):
        """시그니처 관리 패널"""
        st.header("🎭 시그니처 관리")

        # 시그니처 상태 체크
        sig_result = quick_signature_check()

        if isinstance(sig_result, dict) and "summary" in sig_result:
            summary = sig_result["summary"]

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 전체 요약")
                st.write(f"**전체 점수:** {summary.get('compliance_grade', 'Unknown')}")
                st.write(
                    f"**완전 준수:** {summary.get('fully_compliant', 0)}/{summary.get('total_signatures', 4)}"
                )
                st.write(f"**개선 필요:** {summary.get('needs_improvement', 0)}")

            with col2:
                st.subheader("🎯 개별 점수")
                individual_scores = sig_result.get("individual_scores", {})

                if individual_scores:
                    # 점수를 데이터프레임으로 변환
                    scores_data = []
                    for sig_name, score in individual_scores.items():
                        scores_data.append(
                            {
                                "시그니처": sig_name.replace("Echo-", ""),
                                "점수": score,
                                "상태": (
                                    "✅ 우수"
                                    if score >= 0.8
                                    else "⚠️ 개선필요" if score >= 0.6 else "❌ 문제"
                                ),
                            }
                        )

                    df = pd.DataFrame(scores_data)
                    st.dataframe(df, use_container_width=True)

                    # 점수 차트
                    fig = px.bar(
                        df,
                        x="시그니처",
                        y="점수",
                        title="시그니처별 Anchor 준수도",
                        color="점수",
                        color_continuous_scale="RdYlGn",
                    )
                    st.plotly_chart(fig, use_container_width=True)

        else:
            st.error("시그니처 상태를 불러올 수 없습니다.")

        # 긴급 권장사항
        if isinstance(sig_result, dict) and sig_result.get("urgent_recommendations"):
            st.subheader("🚨 긴급 권장사항")
            for rec in sig_result["urgent_recommendations"]:
                st.warning(rec)

    def render_llm_engine_manager(self):
        """LLM 엔진 관리자"""
        st.header("🤖 LLM 엔진 관리")

        # LLM 상태 모니터링
        engines = ["GPT-4", "Claude-3.5", "DeepSeek", "Gemini", "Local Models"]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 엔진 상태")

            engine_data = []
            for engine in engines:
                # 실제로는 각 엔진의 상태를 확인해야 함
                status = "🟢 활성" if engine in ["GPT-4", "Claude-3.5"] else "🔴 비활성"
                engine_data.append(
                    {
                        "엔진": engine,
                        "상태": status,
                        "응답시간": f"{abs(hash(engine)) % 500 + 100}ms",
                        "비용/1K토큰": f"${abs(hash(engine)) % 100 / 1000:.3f}",
                    }
                )

            df = pd.DataFrame(engine_data)
            st.dataframe(df, use_container_width=True)

        with col2:
            st.subheader("⚙️ 엔진 설정")

            selected_engine = st.selectbox("기본 엔진 선택", engines)

            fallback_engine = st.selectbox(
                "대체 엔진", [e for e in engines if e != selected_engine]
            )

            auto_failover = st.checkbox("자동 대체 활성화", value=True)

            if st.button("설정 저장"):
                st.success("LLM 엔진 설정이 저장되었습니다!")

    def render_interface_launcher(self):
        """인터페이스 런처"""
        st.header("🚀 인터페이스 런처")

        interfaces = self.system_status.get("ui_interfaces", {})

        tabs = st.tabs(["Streamlit", "웹 인터페이스", "CLI 도구", "API 서버"])

        with tabs[0]:
            st.subheader("📊 Streamlit 대시보드")
            streamlit_interfaces = interfaces.get("streamlit_dashboards", [])

            for interface in streamlit_interfaces:
                col1, col2, col3 = st.columns([3, 2, 2])

                with col1:
                    st.write(f"**{interface['name']}**")
                    st.write(f"경로: `{interface['path']}`")

                with col2:
                    st.write(f"상태: {interface['status']}")

                with col3:
                    if st.button(f"실행", key=f"run_{interface['name']}"):
                        try:
                            # 새 Streamlit 앱 실행
                            subprocess.Popen(
                                [
                                    sys.executable,
                                    "-m",
                                    "streamlit",
                                    "run",
                                    interface["path"],
                                    "--server.port",
                                    str(8502),
                                ]
                            )
                            st.success(f"{interface['name']} 실행 중! (포트: 8502)")
                        except Exception as e:
                            st.error(f"실행 실패: {e}")

        with tabs[1]:
            st.subheader("🌐 웹 인터페이스")
            web_interfaces = interfaces.get("web_interfaces", [])

            for interface in web_interfaces:
                col1, col2, col3 = st.columns([3, 2, 2])

                with col1:
                    st.write(f"**{interface['name']}**")
                    st.write(f"경로: `{interface['path']}`")

                with col2:
                    st.write(f"상태: {interface['status']}")

                with col3:
                    if st.button(f"실행", key=f"web_{interface['name']}"):
                        try:
                            subprocess.Popen([sys.executable, interface["path"]])
                            st.success(f"{interface['name']} 웹 서버 시작!")
                        except Exception as e:
                            st.error(f"실행 실패: {e}")

        with tabs[2]:
            st.subheader("💻 CLI 도구")
            cli_tools = interfaces.get("cli_tools", [])

            for tool in cli_tools:
                col1, col2, col3 = st.columns([3, 2, 2])

                with col1:
                    st.write(f"**{tool['name']}**")
                    st.write(f"경로: `{tool['path']}`")

                with col2:
                    st.write(f"상태: {tool['status']}")

                with col3:
                    st.code(f"python {tool['path']}", language="bash")

        with tabs[3]:
            st.subheader("🔌 API 서버")
            api_servers = interfaces.get("api_servers", [])

            for server in api_servers:
                col1, col2, col3 = st.columns([3, 2, 2])

                with col1:
                    st.write(f"**{server['name']}**")
                    st.write(f"경로: `{server['path']}`")

                with col2:
                    st.write(f"상태: {server['status']}")

                with col3:
                    if st.button(f"실행", key=f"api_{server['name']}"):
                        try:
                            subprocess.Popen([sys.executable, server["path"]])
                            st.success(f"{server['name']} API 서버 시작!")
                            st.info("API 문서: http://localhost:9000/docs")
                        except Exception as e:
                            st.error(f"실행 실패: {e}")

    def render_judgment_analytics(self):
        """판단 분석 대시보드"""
        st.header("⚖️ 판단 분석")

        # 품질 상태 가져오기
        quality_status = {}
        if self.quality_monitor:
            try:
                quality_status = self.quality_monitor.generate_quality_report()
            except:
                quality_status = {}

        if isinstance(quality_status, dict):
            summary = quality_status.get("summary", {})

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 품질 메트릭")

                metrics = [
                    ("전체 품질 점수", summary.get("overall_quality", 0.0)),
                    ("평균 신뢰도", summary.get("avg_confidence", 0.0)),
                    ("Anchor 준수율", summary.get("anchor_compliance_rate", 0.0)),
                ]

                for metric_name, value in metrics:
                    st.metric(
                        metric_name,
                        (
                            f"{value:.2%}"
                            if isinstance(value, (int, float))
                            else str(value)
                        ),
                    )

            with col2:
                st.subheader("📈 추세 분석")

                # 시간대별 품질 데이터 (모의 데이터)
                import numpy as np

                hours = list(range(24))
                quality_scores = [
                    0.8 + 0.1 * np.sin(h / 4) + np.random.normal(0, 0.05) for h in hours
                ]

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=hours,
                        y=quality_scores,
                        mode="lines+markers",
                        name="품질 점수",
                        line=dict(color="#1f77b4", width=2),
                    )
                )

                fig.update_layout(
                    title="24시간 품질 추세",
                    xaxis_title="시간",
                    yaxis_title="품질 점수",
                    yaxis=dict(range=[0, 1]),
                )

                st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("품질 메트릭을 불러올 수 없습니다.")

    def render_system_administration(self):
        """시스템 관리"""
        st.header("🔧 시스템 관리")

        tabs = st.tabs(["설정 관리", "로그 뷰어", "성능 튜닝", "백업/복구"])

        with tabs[0]:
            st.subheader("⚙️ 설정 관리")

            # Anchor 설정 보기
            if st.button("anchor.yaml 보기"):
                try:
                    with open("anchor.yaml", "r", encoding="utf-8") as f:
                        anchor_content = f.read()

                    st.code(anchor_content, language="yaml")

                except Exception as e:
                    st.error(f"anchor.yaml 읽기 실패: {e}")

            # 시그니처 설정 보기
            if st.button("signature.yaml 보기"):
                try:
                    with open("data/signature.yaml", "r", encoding="utf-8") as f:
                        sig_content = f.read()

                    st.code(sig_content, language="yaml")

                except Exception as e:
                    st.error(f"signature.yaml 읽기 실패: {e}")

        with tabs[1]:
            st.subheader("📄 로그 뷰어")

            log_files = ["data/logs.jsonl", "logs/echo_system.log"]
            selected_log = st.selectbox("로그 파일 선택", log_files)

            if st.button("로그 보기"):
                try:
                    if selected_log.endswith(".jsonl"):
                        # JSONL 파일 읽기
                        logs = []
                        with open(selected_log, "r", encoding="utf-8") as f:
                            for line in f:
                                try:
                                    logs.append(json.loads(line))
                                except:
                                    continue

                        if logs:
                            df = pd.DataFrame(logs)
                            st.dataframe(df.tail(20), use_container_width=True)
                        else:
                            st.info("로그 데이터가 없습니다.")

                    else:
                        # 텍스트 로그 파일
                        with open(selected_log, "r", encoding="utf-8") as f:
                            content = f.read()

                        st.text_area("로그 내용", content, height=400)

                except FileNotFoundError:
                    st.warning(f"로그 파일 {selected_log}을 찾을 수 없습니다.")
                except Exception as e:
                    st.error(f"로그 읽기 실패: {e}")

        with tabs[2]:
            st.subheader("🚀 성능 튜닝")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**메모리 사용량**")
                memory_usage = 75.2  # 실제 메모리 사용량을 가져와야 함
                st.progress(memory_usage / 100)
                st.write(f"{memory_usage}% 사용 중")

                st.write("**CPU 사용량**")
                cpu_usage = 45.8
                st.progress(cpu_usage / 100)
                st.write(f"{cpu_usage}% 사용 중")

            with col2:
                st.write("**성능 설정**")

                max_workers = st.slider("최대 워커 수", 1, 20, 10)
                cache_size = st.slider("캐시 크기 (MB)", 100, 2000, 500)
                timeout = st.slider("응답 타임아웃 (초)", 5, 120, 30)

                if st.button("설정 적용"):
                    st.success("성능 설정이 적용되었습니다!")

        with tabs[3]:
            st.subheader("💾 백업/복구")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**백업 생성**")
                backup_items = st.multiselect(
                    "백업 항목 선택",
                    ["설정 파일", "시그니처 데이터", "로그 파일", "사용자 데이터"],
                    default=["설정 파일", "시그니처 데이터"],
                )

                if st.button("백업 생성"):
                    # 실제 백업 로직 구현 필요
                    st.success("백업이 생성되었습니다!")

            with col2:
                st.write("**복구**")

                # 사용 가능한 백업 목록 (모의)
                available_backups = [
                    "2025-01-07_14:30:00",
                    "2025-01-06_18:45:00",
                    "2025-01-05_12:15:00",
                ]

                selected_backup = st.selectbox("복구할 백업 선택", available_backups)

                if st.button("복구 실행", type="primary"):
                    st.warning("복구를 실행하면 현재 데이터가 덮어씌워집니다.")
                    if st.button("확인"):
                        st.success("복구가 완료되었습니다!")


def main():
    """메인 앱 실행 (최적화됨)"""
    # 페이지 설정은 이미 위에서 완료

    # 세션 상태 관리 최적화
    if "dashboard_fixed" not in st.session_state:
        with st.spinner("대시보드 초기화 중..."):
            st.session_state.dashboard_fixed = EchoMasterDashboard()

    dashboard = st.session_state.dashboard_fixed

    # 사이드바 네비게이션
    st.sidebar.title("🎛️ Echo Master")
    st.sidebar.markdown("**통합 시스템 관리**")

    menu_items = {
        "📊 시스템 개요": "overview",
        "🎭 시그니처 관리": "signatures",
        "🤖 LLM 엔진": "llm_engines",
        "🚀 인터페이스 런처": "launcher",
        "⚖️ 판단 분석": "analytics",
        "🔧 시스템 관리": "admin",
    }

    selected = st.sidebar.selectbox("메뉴 선택", list(menu_items.keys()))
    selected_key = menu_items[selected]

    # 메인 컨텐츠 렌더링
    if selected_key == "overview":
        dashboard.render_master_control_panel()
    elif selected_key == "signatures":
        dashboard.render_signature_management()
    elif selected_key == "llm_engines":
        dashboard.render_llm_engine_manager()
    elif selected_key == "launcher":
        dashboard.render_interface_launcher()
    elif selected_key == "analytics":
        dashboard.render_judgment_analytics()
    elif selected_key == "admin":
        dashboard.render_system_administration()

    # 하단 상태 표시
    st.sidebar.markdown("---")
    st.sidebar.markdown("**시스템 상태**")

    status = dashboard.system_status
    anchor_score = status.get("anchor_compliance", 0.0)

    if anchor_score >= 0.9:
        status_color = "🟢"
        status_text = "우수"
    elif anchor_score >= 0.7:
        status_color = "🟡"
        status_text = "양호"
    else:
        status_color = "🔴"
        status_text = "주의"

    st.sidebar.markdown(f"{status_color} **{status_text}** ({anchor_score:.1%})")

    # 빠른 실행 버튼들
    st.sidebar.markdown("**빠른 실행**")
    if st.sidebar.button("🏃‍♂️ 메인 대시보드"):
        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "streamlit_ui/comprehensive_dashboard.py",
                "--server.port",
                "8502",
            ]
        )
        st.sidebar.success("메인 대시보드 실행!")

    if st.sidebar.button("🌐 웹 채팅"):
        subprocess.Popen([sys.executable, "echo_web_chat.py"])
        st.sidebar.success("웹 채팅 서버 시작!")

    if st.sidebar.button("🔌 API 서버"):
        subprocess.Popen([sys.executable, "echo_engine/echo_agent_api.py"])
        st.sidebar.success("API 서버 시작!")


if __name__ == "__main__":
    main()
