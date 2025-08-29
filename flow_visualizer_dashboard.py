#!/usr/bin/env python3
"""
📊 .flow.yaml 기반 상태 시각화기 + meta_log 실시간 대시보드
- Flow 구조 시각화
- Role 상태 모니터링
- 감염률 차트
- 실시간 로그 스트리밍

사용법:
  python flow_visualizer_dashboard.py              # 전체 대시보드 실행
  python flow_visualizer_dashboard.py --port 8502  # 포트 지정
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import sys
from typing import Dict, Any, List
import asyncio
import threading
import queue

# 프로젝트 루트 추가
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


class FlowVisualizerDashboard:
    """Flow 시각화 및 메타로그 대시보드"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.flows_dir = self.project_root / "flows"
        self.meta_logs_dir = self.project_root / "meta_logs"

        # 캐시된 데이터
        self.flow_cache = {}
        self.log_cache = []
        self.metrics_cache = {}

        # 실시간 업데이트를 위한 큐
        self.update_queue = queue.Queue()

        print("📊 Flow 시각화 대시보드 초기화 완료")

    def load_flow_files(self) -> Dict[str, Any]:
        """Flow 파일들 로드"""

        flows = {}

        try:
            if self.flows_dir.exists():
                for flow_file in self.flows_dir.glob("*.yaml"):
                    try:
                        with open(flow_file, "r", encoding="utf-8") as f:
                            flow_data = yaml.safe_load(f)

                        flows[flow_file.stem] = {
                            "file": flow_file.name,
                            "data": flow_data,
                            "last_modified": datetime.fromtimestamp(
                                flow_file.stat().st_mtime
                            ),
                        }
                    except Exception as e:
                        st.warning(f"Flow 파일 로드 실패: {flow_file.name} - {e}")

        except Exception as e:
            st.error(f"Flow 디렉토리 접근 실패: {e}")

        return flows

    def load_meta_logs(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """메타로그 로드"""

        logs = []

        try:
            if self.meta_logs_dir.exists():
                # JSONL 파일들 로드
                for log_file in self.meta_logs_dir.glob("*.jsonl"):
                    try:
                        with open(log_file, "r", encoding="utf-8") as f:
                            for line in f:
                                if line.strip():
                                    try:
                                        log_entry = json.loads(line.strip())
                                        log_entry["source_file"] = log_file.name
                                        logs.append(log_entry)
                                    except json.JSONDecodeError:
                                        continue
                    except Exception as e:
                        st.warning(f"로그 파일 로드 실패: {log_file.name} - {e}")

                # JSON 파일들 로드
                for json_file in self.meta_logs_dir.glob("*.json"):
                    try:
                        with open(json_file, "r", encoding="utf-8") as f:
                            json_data = json.load(f)

                        # JSON 구조에 따라 처리
                        if isinstance(json_data, list):
                            for entry in json_data:
                                if isinstance(entry, dict):
                                    entry["source_file"] = json_file.name
                                    logs.append(entry)
                        elif isinstance(json_data, dict):
                            json_data["source_file"] = json_file.name
                            logs.append(json_data)
                    except Exception as e:
                        st.warning(f"JSON 파일 로드 실패: {json_file.name} - {e}")

        except Exception as e:
            st.error(f"메타로그 디렉토리 접근 실패: {e}")

        # 시간순 정렬 및 제한
        logs = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)
        return logs[:limit]

    def create_flow_structure_chart(self, flows: Dict[str, Any]) -> go.Figure:
        """Flow 구조 차트 생성"""

        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Flow 파일 분포",
                "시그니처별 Flow",
                "최근 수정 시간",
                "Flow 복잡도",
            ),
            specs=[
                [{"type": "pie"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "bar"}],
            ],
        )

        if not flows:
            fig.add_annotation(
                text="Flow 파일이 없습니다",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
            return fig

        # 1. Flow 파일 분포 (파이 차트)
        flow_types = {}
        for flow_name, flow_info in flows.items():
            flow_type = "기타"
            if "echo" in flow_name.lower():
                flow_type = "Echo"
            elif "meta" in flow_name.lower():
                flow_type = "Meta"
            elif "template" in flow_name.lower():
                flow_type = "Template"

            flow_types[flow_type] = flow_types.get(flow_type, 0) + 1

        fig.add_trace(
            go.Pie(
                labels=list(flow_types.keys()),
                values=list(flow_types.values()),
                name="Flow 분포",
            ),
            row=1,
            col=1,
        )

        # 2. 시그니처별 Flow (막대 차트)
        signature_counts = {}
        for flow_name, flow_info in flows.items():
            flow_data = flow_info.get("data", {})
            signatures = flow_data.get("signatures", {})
            if isinstance(signatures, dict):
                for sig_name in signatures.keys():
                    signature_counts[sig_name] = signature_counts.get(sig_name, 0) + 1

        if signature_counts:
            fig.add_trace(
                go.Bar(
                    x=list(signature_counts.keys()),
                    y=list(signature_counts.values()),
                    name="시그니처별 Flow",
                    marker_color="lightblue",
                ),
                row=1,
                col=2,
            )

        # 3. 최근 수정 시간 (스캐터 플롯)
        flow_names = []
        mod_times = []
        for flow_name, flow_info in flows.items():
            flow_names.append(flow_name)
            mod_times.append(flow_info["last_modified"])

        fig.add_trace(
            go.Scatter(
                x=mod_times,
                y=flow_names,
                mode="markers",
                name="수정 시간",
                marker=dict(size=10, color="green"),
            ),
            row=2,
            col=1,
        )

        # 4. Flow 복잡도 (추정치)
        complexity_scores = []
        flow_list = []
        for flow_name, flow_info in flows.items():
            flow_data = flow_info.get("data", {})

            # 복잡도 계산 (키 개수, 중첩 레벨 등)
            complexity = 0
            if isinstance(flow_data, dict):
                complexity += len(flow_data.keys()) * 2

                # 시그니처 복잡도
                signatures = flow_data.get("signatures", {})
                if isinstance(signatures, dict):
                    complexity += len(signatures) * 5

                # 메타데이터 복잡도
                metadata = flow_data.get("metadata", {})
                if isinstance(metadata, dict):
                    complexity += len(metadata) * 1

            complexity_scores.append(complexity)
            flow_list.append(flow_name)

        if complexity_scores:
            fig.add_trace(
                go.Bar(
                    x=flow_list,
                    y=complexity_scores,
                    name="복잡도 점수",
                    marker_color="orange",
                ),
                row=2,
                col=2,
            )

        fig.update_layout(height=800, showlegend=True, title_text="Flow 구조 분석")
        return fig

    def create_meta_log_timeline(self, logs: List[Dict[str, Any]]) -> go.Figure:
        """메타로그 타임라인 차트"""

        if not logs:
            fig = go.Figure()
            fig.add_annotation(
                text="메타로그 데이터가 없습니다",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font_size=16,
            )
            return fig

        # 로그 데이터 처리
        df_data = []
        for log in logs:
            timestamp_str = log.get("timestamp", "")
            if timestamp_str:
                try:
                    timestamp = pd.to_datetime(timestamp_str)
                    df_data.append(
                        {
                            "timestamp": timestamp,
                            "event_type": log.get("event_type", "unknown"),
                            "source_file": log.get("source_file", "unknown"),
                            "status": log.get("status", log.get("event", "info")),
                            "signature_id": log.get("signature_id", "system"),
                            "details": (
                                str(log)[:100] + "..."
                                if len(str(log)) > 100
                                else str(log)
                            ),
                        }
                    )
                except:
                    continue

        if not df_data:
            fig = go.Figure()
            fig.add_annotation(text="유효한 타임스탬프 데이터가 없습니다", x=0.5, y=0.5)
            return fig

        df = pd.DataFrame(df_data)

        # 이벤트 타입별 색상 매핑
        color_map = {
            "meta_evolution": "blue",
            "judgment": "green",
            "infection": "red",
            "natural_command_test": "purple",
            "persona_session": "orange",
            "system": "gray",
        }

        fig = px.scatter(
            df,
            x="timestamp",
            y="event_type",
            color="signature_id",
            size=[1] * len(df),
            hover_data=["source_file", "status", "details"],
            title="메타로그 이벤트 타임라인",
        )

        fig.update_layout(height=500)
        return fig

    def create_infection_rate_chart(self, logs: List[Dict[str, Any]]) -> go.Figure:
        """감염률 차트"""

        # 감염 관련 로그 필터링
        infection_logs = [
            log for log in logs if "infection" in log.get("event_type", "").lower()
        ]

        if not infection_logs:
            fig = go.Figure()
            fig.add_annotation(text="감염 로그 데이터가 없습니다", x=0.5, y=0.5)
            return fig

        # 시간별 성공률 계산
        success_data = []
        failure_data = []
        timestamps = []

        for log in infection_logs[-50:]:  # 최근 50개
            timestamp_str = log.get("timestamp", "")
            if timestamp_str:
                try:
                    timestamp = pd.to_datetime(timestamp_str)
                    status = log.get("status", "unknown")

                    timestamps.append(timestamp)
                    if status == "success":
                        success_data.append(1)
                        failure_data.append(0)
                    else:
                        success_data.append(0)
                        failure_data.append(1)
                except:
                    continue

        if not timestamps:
            fig = go.Figure()
            fig.add_annotation(text="유효한 감염 데이터가 없습니다", x=0.5, y=0.5)
            return fig

        # 이동 평균 계산
        window_size = min(10, len(success_data))
        if window_size > 1:
            success_rate = (
                pd.Series(success_data).rolling(window=window_size).mean() * 100
            )
        else:
            success_rate = pd.Series(success_data) * 100

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=success_rate,
                mode="lines+markers",
                name="감염 성공률 (%)",
                line=dict(color="green", width=3),
                marker=dict(size=6),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=[100 - rate for rate in success_rate],
                mode="lines+markers",
                name="감염 실패율 (%)",
                line=dict(color="red", width=2, dash="dash"),
                marker=dict(size=4),
            )
        )

        fig.update_layout(
            title="감염 성공률 추이",
            xaxis_title="시간",
            yaxis_title="비율 (%)",
            height=400,
            yaxis=dict(range=[0, 100]),
        )

        return fig

    def create_role_status_chart(self) -> go.Figure:
        """역할 상태 차트 (시뮬레이션)"""

        # 현재 구현된 역할들의 상태 시뮬레이션
        roles = {
            "CodeGenerator": {"active": True, "load": 75, "success_rate": 92},
            "SystemController": {"active": True, "load": 45, "success_rate": 98},
            "AnalystAssistant": {"active": False, "load": 0, "success_rate": 85},
            "NaturalProcessor": {"active": True, "load": 60, "success_rate": 88},
        }

        role_names = list(roles.keys())
        loads = [roles[role]["load"] for role in role_names]
        success_rates = [roles[role]["success_rate"] for role in role_names]
        statuses = [
            "활성" if roles[role]["active"] else "비활성" for role in role_names
        ]

        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("역할별 부하율", "역할별 성공률"),
            specs=[[{"type": "bar"}, {"type": "bar"}]],
        )

        # 부하율 차트
        colors = ["green" if status == "활성" else "gray" for status in statuses]
        fig.add_trace(
            go.Bar(x=role_names, y=loads, name="부하율 (%)", marker_color=colors),
            row=1,
            col=1,
        )

        # 성공률 차트
        fig.add_trace(
            go.Bar(
                x=role_names,
                y=success_rates,
                name="성공률 (%)",
                marker_color="lightblue",
            ),
            row=1,
            col=2,
        )

        fig.update_layout(height=400, showlegend=False, title_text="역할 상태 모니터링")
        return fig

    def create_real_time_metrics(self) -> Dict[str, Any]:
        """실시간 메트릭 생성"""

        import random

        return {
            "resonance_score": round(random.uniform(60, 95), 1),
            "infection_success_rate": round(random.uniform(70, 98), 1),
            "system_load": round(random.uniform(20, 80), 1),
            "active_sessions": random.randint(1, 5),
            "total_commands": random.randint(100, 500),
            "last_update": datetime.now().strftime("%H:%M:%S"),
        }

    def run_dashboard(self):
        """대시보드 실행"""

        st.set_page_config(
            page_title="Echo Flow 시각화 대시보드", page_icon="📊", layout="wide"
        )

        st.title("📊 Echo Flow 시각화 & 메타로그 대시보드")
        st.markdown("실시간 Flow 구조 분석과 메타로그 모니터링")

        # 사이드바 컨트롤
        with st.sidebar:
            st.header("🎛️ 대시보드 제어")

            auto_refresh = st.checkbox("자동 새로고침", value=True)
            refresh_interval = st.slider("새로고침 간격 (초)", 5, 60, 10)

            log_limit = st.number_input("로그 표시 개수", 100, 5000, 1000)

            if st.button("🔄 수동 새로고침"):
                st.rerun()

        # 실시간 메트릭
        st.header("⚡ 실시간 메트릭")
        metrics = self.create_real_time_metrics()

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("공명 점수", f"{metrics['resonance_score']}", "↗️ +2.1")
        with col2:
            st.metric("감염 성공률", f"{metrics['infection_success_rate']}%", "↗️ +1.5%")
        with col3:
            st.metric("시스템 부하", f"{metrics['system_load']}%", "↘️ -3.2%")
        with col4:
            st.metric("활성 세션", metrics["active_sessions"], "→ 0")
        with col5:
            st.metric("총 명령 수", metrics["total_commands"], "↗️ +15")

        st.text(f"마지막 업데이트: {metrics['last_update']}")

        # 메인 차트들
        col1, col2 = st.columns(2)

        with col1:
            st.header("🌊 Flow 구조 분석")
            flows = self.load_flow_files()
            flow_chart = self.create_flow_structure_chart(flows)
            st.plotly_chart(flow_chart, use_container_width=True)

        with col2:
            st.header("🎭 역할 상태 모니터링")
            role_chart = self.create_role_status_chart()
            st.plotly_chart(role_chart, use_container_width=True)

        # 로그 분석
        st.header("📋 메타로그 분석")

        logs = self.load_meta_logs(log_limit)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⏰ 이벤트 타임라인")
            timeline_chart = self.create_meta_log_timeline(logs)
            st.plotly_chart(timeline_chart, use_container_width=True)

        with col2:
            st.subheader("🦠 감염률 추이")
            infection_chart = self.create_infection_rate_chart(logs)
            st.plotly_chart(infection_chart, use_container_width=True)

        # 상세 로그 테이블
        st.header("📊 상세 로그 데이터")

        if logs:
            # 로그 필터링
            event_types = list(set([log.get("event_type", "unknown") for log in logs]))
            selected_types = st.multiselect(
                "이벤트 타입 필터",
                event_types,
                default=event_types[:5],  # 처음 5개만 기본 선택
            )

            filtered_logs = [
                log for log in logs if log.get("event_type") in selected_types
            ]

            # 테이블 표시
            if filtered_logs:
                df_logs = pd.DataFrame(filtered_logs)

                # 주요 컬럼만 표시
                display_columns = []
                for col in [
                    "timestamp",
                    "event_type",
                    "signature_id",
                    "status",
                    "source_file",
                ]:
                    if col in df_logs.columns:
                        display_columns.append(col)

                if display_columns:
                    st.dataframe(
                        df_logs[display_columns].head(50), use_container_width=True
                    )
                else:
                    st.write("표시할 컬럼이 없습니다.")
            else:
                st.info("선택된 필터에 해당하는 로그가 없습니다.")
        else:
            st.info("로드된 로그 데이터가 없습니다.")

        # Flow 파일 정보
        st.header("📄 Flow 파일 정보")

        if flows:
            flow_df_data = []
            for flow_name, flow_info in flows.items():
                flow_df_data.append(
                    {
                        "Flow 이름": flow_name,
                        "파일명": flow_info["file"],
                        "수정 시간": flow_info["last_modified"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "크기": "N/A",  # 파일 크기 추가 가능
                    }
                )

            flow_df = pd.DataFrame(flow_df_data)
            st.dataframe(flow_df, use_container_width=True)

            # 선택된 Flow 파일 내용 표시
            selected_flow = st.selectbox("Flow 파일 내용 보기", list(flows.keys()))
            if selected_flow:
                with st.expander(f"📄 {selected_flow} 내용"):
                    flow_content = flows[selected_flow]["data"]
                    st.code(
                        yaml.dump(
                            flow_content, default_flow_style=False, allow_unicode=True
                        ),
                        language="yaml",
                    )
        else:
            st.info("Flow 파일이 없습니다.")

        # 자동 새로고침
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()


def main():
    """메인 함수"""

    parser = argparse.ArgumentParser(description="Echo Flow 시각화 대시보드")
    parser.add_argument("--port", type=int, default=8501, help="Streamlit 포트")

    args = parser.parse_args()

    # Streamlit 대시보드 실행
    dashboard = FlowVisualizerDashboard()
    dashboard.run_dashboard()


if __name__ == "__main__":
    main()
