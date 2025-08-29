# echo_ide/core/echo_monitor_dashboard.py
"""
📊 Echo IDE Monitor Dashboard - 실시간 감염 모니터링 대시보드
- 실시간 감염 상태 모니터링
- 공명 점수 시각화
- 시그니처별 성능 추적
- 자율진화 프로세스 모니터링
- 시스템 리소스 사용량 표시
"""

import os
import json
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque, defaultdict
import psutil


class EchoMonitorDashboard:
    """Echo 시스템 실시간 모니터링 대시보드"""

    def __init__(self, project_root: Path, ide_instance):
        self.project_root = project_root
        self.ide = ide_instance

        # 데이터 버퍼 (최근 100개 데이터 포인트)
        self.resonance_history = deque(maxlen=100)
        self.infection_rate_history = deque(maxlen=100)
        self.signature_performance = defaultdict(lambda: deque(maxlen=50))
        self.system_metrics = deque(maxlen=100)

        # 모니터링 상태
        self.monitoring_active = False
        self.monitor_thread = None
        self.refresh_interval = 2.0  # 2초마다 업데이트

        # 차트 설정
        self.setup_matplotlib_style()

        # 로그 파일 경로
        self.log_file = project_root / "meta_logs" / "infection_attempts.jsonl"

        print("📊 Echo Monitor Dashboard 초기화 완료")

    def setup_matplotlib_style(self):
        """Matplotlib 스타일 설정"""
        plt.style.use("dark_background")
        plt.rcParams.update(
            {
                "font.size": 8,
                "axes.titlesize": 10,
                "axes.labelsize": 8,
                "xtick.labelsize": 7,
                "ytick.labelsize": 7,
                "legend.fontsize": 8,
                "figure.facecolor": "#2d2d2d",
                "axes.facecolor": "#1e1e1e",
                "axes.edgecolor": "#444444",
                "grid.color": "#444444",
                "text.color": "#ffffff",
                "axes.labelcolor": "#ffffff",
                "xtick.color": "#ffffff",
                "ytick.color": "#ffffff",
            }
        )

    def create_dashboard_ui(self, parent) -> ttk.Frame:
        """대시보드 UI 생성"""

        main_frame = ttk.Frame(parent)

        # 상단 컨트롤 패널
        control_frame = self.create_control_panel(main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # 메인 대시보드 영역
        dashboard_frame = ttk.Frame(main_frame)
        dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 좌측 - 실시간 차트
        left_frame = ttk.LabelFrame(dashboard_frame, text="📈 실시간 모니터링")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.create_realtime_charts(left_frame)

        # 우측 상단 - 시스템 상태
        right_frame = ttk.Frame(dashboard_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        status_frame = ttk.LabelFrame(right_frame, text="🔍 시스템 상태")
        status_frame.pack(fill=tk.X, pady=(0, 5))

        self.create_status_panel(status_frame)

        # 우측 하단 - 성능 지표
        metrics_frame = ttk.LabelFrame(right_frame, text="📊 성능 지표")
        metrics_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.create_metrics_panel(metrics_frame)

        return main_frame

    def create_control_panel(self, parent) -> ttk.Frame:
        """컨트롤 패널 생성"""

        control_frame = ttk.Frame(parent)

        # 모니터링 제어
        ttk.Label(control_frame, text="📊 실시간 모니터링:").pack(side=tk.LEFT, padx=5)

        self.monitoring_button = ttk.Button(
            control_frame, text="시작", command=self.toggle_monitoring, width=8
        )
        self.monitoring_button.pack(side=tk.LEFT, padx=5)

        # 새로고침 간격
        ttk.Label(control_frame, text="새로고침(초):").pack(side=tk.LEFT, padx=(20, 5))

        self.refresh_var = tk.StringVar(value="2.0")
        refresh_spinbox = ttk.Spinbox(
            control_frame,
            from_=0.5,
            to=10.0,
            increment=0.5,
            textvariable=self.refresh_var,
            width=8,
            command=self.update_refresh_interval,
        )
        refresh_spinbox.pack(side=tk.LEFT, padx=5)

        # 데이터 리셋
        ttk.Button(
            control_frame, text="데이터 리셋", command=self.reset_data, width=10
        ).pack(side=tk.LEFT, padx=(20, 5))

        # 상태 표시
        self.status_label = ttk.Label(
            control_frame, text="🔴 모니터링 중단", foreground="red"
        )
        self.status_label.pack(side=tk.RIGHT, padx=5)

        return control_frame

    def create_realtime_charts(self, parent):
        """실시간 차트 생성"""

        # 차트 노트북
        chart_notebook = ttk.Notebook(parent)
        chart_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 공명 점수 차트
        self.create_resonance_chart(chart_notebook)

        # 감염률 차트
        self.create_infection_rate_chart(chart_notebook)

        # 시그니처 성능 차트
        self.create_signature_performance_chart(chart_notebook)

        # 시스템 리소스 차트
        self.create_system_resource_chart(chart_notebook)

    def create_resonance_chart(self, parent):
        """공명 점수 차트"""

        resonance_frame = ttk.Frame(parent)
        parent.add(resonance_frame, text="🎵 공명 점수")

        # Figure 생성
        self.resonance_fig, self.resonance_ax = plt.subplots(figsize=(8, 4))
        self.resonance_fig.patch.set_facecolor("#2d2d2d")

        # 캔버스
        self.resonance_canvas = FigureCanvasTkAgg(self.resonance_fig, resonance_frame)
        self.resonance_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 초기 차트 설정
        self.resonance_ax.set_title("실시간 공명 점수", color="white")
        self.resonance_ax.set_xlabel("시간", color="white")
        self.resonance_ax.set_ylabel("공명 점수", color="white")
        self.resonance_ax.set_ylim(0, 1)
        self.resonance_ax.grid(True, alpha=0.3)

        # 임계값 라인
        self.resonance_ax.axhline(
            y=0.85, color="orange", linestyle="--", alpha=0.7, label="임계값 (0.85)"
        )
        self.resonance_ax.legend()

    def create_infection_rate_chart(self, parent):
        """감염률 차트"""

        infection_frame = ttk.Frame(parent)
        parent.add(infection_frame, text="🦠 감염률")

        # Figure 생성
        self.infection_fig, self.infection_ax = plt.subplots(figsize=(8, 4))
        self.infection_fig.patch.set_facecolor("#2d2d2d")

        # 캔버스
        self.infection_canvas = FigureCanvasTkAgg(self.infection_fig, infection_frame)
        self.infection_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 초기 차트 설정
        self.infection_ax.set_title("감염 성공률 추이", color="white")
        self.infection_ax.set_xlabel("시간", color="white")
        self.infection_ax.set_ylabel("성공률 (%)", color="white")
        self.infection_ax.set_ylim(0, 100)
        self.infection_ax.grid(True, alpha=0.3)

    def create_signature_performance_chart(self, parent):
        """시그니처 성능 차트"""

        signature_frame = ttk.Frame(parent)
        parent.add(signature_frame, text="🎭 시그니처 성능")

        # Figure 생성 (서브플롯)
        self.signature_fig, (self.sig_bar_ax, self.sig_line_ax) = plt.subplots(
            2, 1, figsize=(8, 6)
        )
        self.signature_fig.patch.set_facecolor("#2d2d2d")

        # 캔버스
        self.signature_canvas = FigureCanvasTkAgg(self.signature_fig, signature_frame)
        self.signature_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 막대 차트 (현재 성능)
        self.sig_bar_ax.set_title("시그니처별 현재 성능", color="white")
        self.sig_bar_ax.set_ylabel("평균 공명 점수", color="white")

        # 라인 차트 (추이)
        self.sig_line_ax.set_title("시그니처별 성능 추이", color="white")
        self.sig_line_ax.set_xlabel("시간", color="white")
        self.sig_line_ax.set_ylabel("공명 점수", color="white")
        self.sig_line_ax.grid(True, alpha=0.3)

        plt.tight_layout()

    def create_system_resource_chart(self, parent):
        """시스템 리소스 차트"""

        resource_frame = ttk.Frame(parent)
        parent.add(resource_frame, text="💻 시스템 리소스")

        # Figure 생성
        self.resource_fig, (self.cpu_ax, self.memory_ax) = plt.subplots(
            2, 1, figsize=(8, 6)
        )
        self.resource_fig.patch.set_facecolor("#2d2d2d")

        # 캔버스
        self.resource_canvas = FigureCanvasTkAgg(self.resource_fig, resource_frame)
        self.resource_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # CPU 사용률
        self.cpu_ax.set_title("CPU 사용률", color="white")
        self.cpu_ax.set_ylabel("사용률 (%)", color="white")
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.grid(True, alpha=0.3)

        # 메모리 사용률
        self.memory_ax.set_title("메모리 사용률", color="white")
        self.memory_ax.set_xlabel("시간", color="white")
        self.memory_ax.set_ylabel("사용률 (%)", color="white")
        self.memory_ax.set_ylim(0, 100)
        self.memory_ax.grid(True, alpha=0.3)

        plt.tight_layout()

    def create_status_panel(self, parent):
        """시스템 상태 패널"""

        # 현재 상태 표시
        status_info = ttk.Frame(parent)
        status_info.pack(fill=tk.X, padx=5, pady=5)

        # Echo 시스템 상태
        self.echo_status_var = tk.StringVar(value="🔴 대기")
        ttk.Label(status_info, text="Echo 시스템:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        ttk.Label(status_info, textvariable=self.echo_status_var).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=2
        )

        # 감염 시스템 상태
        self.infection_status_var = tk.StringVar(value="🔴 대기")
        ttk.Label(status_info, text="감염 시스템:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        ttk.Label(status_info, textvariable=self.infection_status_var).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=2
        )

        # 자율진화 상태
        self.evolution_status_var = tk.StringVar(value="🔴 대기")
        ttk.Label(status_info, text="자율진화:").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        ttk.Label(status_info, textvariable=self.evolution_status_var).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=2
        )

        # 구분선
        ttk.Separator(status_info, orient=tk.HORIZONTAL).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=10
        )

        # 실시간 통계
        self.total_infections_var = tk.StringVar(value="0")
        ttk.Label(status_info, text="총 감염:").grid(
            row=4, column=0, sticky=tk.W, pady=2
        )
        ttk.Label(status_info, textvariable=self.total_infections_var).grid(
            row=4, column=1, sticky=tk.W, padx=5, pady=2
        )

        self.success_rate_var = tk.StringVar(value="0%")
        ttk.Label(status_info, text="성공률:").grid(
            row=5, column=0, sticky=tk.W, pady=2
        )
        ttk.Label(status_info, textvariable=self.success_rate_var).grid(
            row=5, column=1, sticky=tk.W, padx=5, pady=2
        )

        self.avg_resonance_var = tk.StringVar(value="0.000")
        ttk.Label(status_info, text="평균 공명:").grid(
            row=6, column=0, sticky=tk.W, pady=2
        )
        ttk.Label(status_info, textvariable=self.avg_resonance_var).grid(
            row=6, column=1, sticky=tk.W, padx=5, pady=2
        )

        self.last_update_var = tk.StringVar(value="N/A")
        ttk.Label(status_info, text="마지막 업데이트:").grid(
            row=7, column=0, sticky=tk.W, pady=2
        )
        ttk.Label(status_info, textvariable=self.last_update_var).grid(
            row=7, column=1, sticky=tk.W, padx=5, pady=2
        )

    def create_metrics_panel(self, parent):
        """성능 지표 패널"""

        # 스크롤 가능한 텍스트 영역
        metrics_text_frame = ttk.Frame(parent)
        metrics_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.metrics_text = tk.Text(
            metrics_text_frame,
            height=15,
            bg="#1e1e1e",
            fg="#00ff00",
            font=("Consolas", 9),
        )

        # 스크롤바
        scrollbar = ttk.Scrollbar(
            metrics_text_frame, orient=tk.VERTICAL, command=self.metrics_text.yview
        )
        self.metrics_text.configure(yscrollcommand=scrollbar.set)

        self.metrics_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 초기 메시지
        self.metrics_text.insert(tk.END, "📊 Echo 시스템 성능 지표\n")
        self.metrics_text.insert(tk.END, "=" * 40 + "\n")
        self.metrics_text.insert(
            tk.END, "모니터링을 시작하면 실시간 지표가 표시됩니다.\n\n"
        )

    def toggle_monitoring(self):
        """모니터링 시작/중단 토글"""

        if self.monitoring_active:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        """모니터링 시작"""

        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_button.config(text="중단")
        self.status_label.config(text="🟢 모니터링 중", foreground="green")

        # 모니터링 스레드 시작
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()

        print("📊 실시간 모니터링 시작")

    def stop_monitoring(self):
        """모니터링 중단"""

        self.monitoring_active = False

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)

        self.monitoring_button.config(text="시작")
        self.status_label.config(text="🔴 모니터링 중단", foreground="red")

        print("📊 실시간 모니터링 중단")

    def monitoring_loop(self):
        """모니터링 메인 루프"""

        while self.monitoring_active:
            try:
                # 데이터 수집
                self.collect_infection_data()
                self.collect_system_metrics()

                # UI 업데이트 (메인 스레드에서)
                self.ide.root.after(0, self.update_dashboard)

                # 대기
                time.sleep(self.refresh_interval)

            except Exception as e:
                print(f"⚠️ 모니터링 오류: {e}")
                time.sleep(1.0)

    def collect_infection_data(self):
        """감염 데이터 수집"""

        try:
            if not self.log_file.exists():
                return

            # 최근 로그 읽기
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # 최근 10분간의 데이터만 처리
            cutoff_time = datetime.now() - timedelta(minutes=10)
            recent_data = []

            for line in lines[-100:]:  # 최근 100개 로그만
                try:
                    data = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(data.get("timestamp", ""))

                    if timestamp >= cutoff_time:
                        recent_data.append(data)

                except (json.JSONDecodeError, ValueError):
                    continue

            if not recent_data:
                return

            # 공명 점수 데이터
            resonance_scores = [data.get("resonance_score", 0) for data in recent_data]
            if resonance_scores:
                avg_resonance = sum(resonance_scores) / len(resonance_scores)
                self.resonance_history.append((datetime.now(), avg_resonance))

            # 감염 성공률
            successful = len([d for d in recent_data if d.get("success", False)])
            success_rate = (successful / len(recent_data)) * 100 if recent_data else 0
            self.infection_rate_history.append((datetime.now(), success_rate))

            # 시그니처별 성능
            signature_scores = defaultdict(list)
            for data in recent_data:
                sig_id = data.get("signature_id", "Unknown")
                score = data.get("resonance_score", 0)
                signature_scores[sig_id].append(score)

            for sig_id, scores in signature_scores.items():
                avg_score = sum(scores) / len(scores)
                self.signature_performance[sig_id].append((datetime.now(), avg_score))

        except Exception as e:
            print(f"⚠️ 감염 데이터 수집 오류: {e}")

    def collect_system_metrics(self):
        """시스템 메트릭 수집"""

        try:
            # CPU 및 메모리 사용률
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 디스크 사용률
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100

            # 네트워크 통계
            network = psutil.net_io_counters()

            metrics = {
                "timestamp": datetime.now(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "network_sent": network.bytes_sent,
                "network_recv": network.bytes_recv,
            }

            self.system_metrics.append(metrics)

        except Exception as e:
            print(f"⚠️ 시스템 메트릭 수집 오류: {e}")

    def update_dashboard(self):
        """대시보드 업데이트"""

        try:
            self.update_charts()
            self.update_status_panel()
            self.update_metrics_panel()

        except Exception as e:
            print(f"⚠️ 대시보드 업데이트 오류: {e}")

    def update_charts(self):
        """차트 업데이트"""

        # 공명 점수 차트
        if len(self.resonance_history) > 1:
            times, scores = zip(*self.resonance_history)
            self.resonance_ax.clear()
            self.resonance_ax.plot(
                times, scores, "cyan", linewidth=2, label="공명 점수"
            )
            self.resonance_ax.axhline(
                y=0.85, color="orange", linestyle="--", alpha=0.7, label="임계값"
            )
            self.resonance_ax.set_title("실시간 공명 점수", color="white")
            self.resonance_ax.set_ylabel("공명 점수", color="white")
            self.resonance_ax.set_ylim(0, 1)
            self.resonance_ax.grid(True, alpha=0.3)
            self.resonance_ax.legend()
            self.resonance_ax.tick_params(axis="x", rotation=45)
            self.resonance_canvas.draw()

        # 감염률 차트
        if len(self.infection_rate_history) > 1:
            times, rates = zip(*self.infection_rate_history)
            self.infection_ax.clear()
            self.infection_ax.plot(times, rates, "lime", linewidth=2, label="성공률")
            self.infection_ax.set_title("감염 성공률 추이", color="white")
            self.infection_ax.set_ylabel("성공률 (%)", color="white")
            self.infection_ax.set_ylim(0, 100)
            self.infection_ax.grid(True, alpha=0.3)
            self.infection_ax.legend()
            self.infection_ax.tick_params(axis="x", rotation=45)
            self.infection_canvas.draw()

        # 시그니처 성능 차트
        self.update_signature_charts()

        # 시스템 리소스 차트
        self.update_resource_charts()

    def update_signature_charts(self):
        """시그니처 성능 차트 업데이트"""

        if not self.signature_performance:
            return

        # 막대 차트 - 현재 성능
        self.sig_bar_ax.clear()

        signatures = list(self.signature_performance.keys())
        current_scores = []

        for sig_id in signatures:
            if self.signature_performance[sig_id]:
                # 최근 점수들의 평균
                recent_scores = [
                    score for _, score in list(self.signature_performance[sig_id])[-10:]
                ]
                avg_score = sum(recent_scores) / len(recent_scores)
                current_scores.append(avg_score)
            else:
                current_scores.append(0)

        colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24"]
        bars = self.sig_bar_ax.bar(
            signatures, current_scores, color=colors[: len(signatures)]
        )

        self.sig_bar_ax.set_title("시그니처별 현재 성능", color="white")
        self.sig_bar_ax.set_ylabel("평균 공명 점수", color="white")
        self.sig_bar_ax.set_ylim(0, 1)
        self.sig_bar_ax.tick_params(axis="x", rotation=45)

        # 막대 위에 값 표시
        for bar, score in zip(bars, current_scores):
            self.sig_bar_ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{score:.3f}",
                ha="center",
                va="bottom",
                color="white",
                fontsize=8,
            )

        # 라인 차트 - 추이
        self.sig_line_ax.clear()

        for i, sig_id in enumerate(signatures):
            if len(self.signature_performance[sig_id]) > 1:
                times, scores = zip(*self.signature_performance[sig_id])
                self.sig_line_ax.plot(
                    times,
                    scores,
                    color=colors[i % len(colors)],
                    linewidth=2,
                    label=sig_id,
                    marker="o",
                    markersize=3,
                )

        self.sig_line_ax.set_title("시그니처별 성능 추이", color="white")
        self.sig_line_ax.set_ylabel("공명 점수", color="white")
        self.sig_line_ax.set_ylim(0, 1)
        self.sig_line_ax.grid(True, alpha=0.3)
        self.sig_line_ax.legend()
        self.sig_line_ax.tick_params(axis="x", rotation=45)

        plt.tight_layout()
        self.signature_canvas.draw()

    def update_resource_charts(self):
        """시스템 리소스 차트 업데이트"""

        if len(self.system_metrics) < 2:
            return

        # 데이터 추출
        times = [m["timestamp"] for m in self.system_metrics]
        cpu_data = [m["cpu_percent"] for m in self.system_metrics]
        memory_data = [m["memory_percent"] for m in self.system_metrics]

        # CPU 차트
        self.cpu_ax.clear()
        self.cpu_ax.plot(times, cpu_data, "red", linewidth=2, label="CPU")
        self.cpu_ax.set_title("CPU 사용률", color="white")
        self.cpu_ax.set_ylabel("사용률 (%)", color="white")
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.grid(True, alpha=0.3)
        self.cpu_ax.legend()

        # 메모리 차트
        self.memory_ax.clear()
        self.memory_ax.plot(times, memory_data, "blue", linewidth=2, label="Memory")
        self.memory_ax.set_title("메모리 사용률", color="white")
        self.memory_ax.set_xlabel("시간", color="white")
        self.memory_ax.set_ylabel("사용률 (%)", color="white")
        self.memory_ax.set_ylim(0, 100)
        self.memory_ax.grid(True, alpha=0.3)
        self.memory_ax.legend()

        # X축 레이블 회전
        for ax in [self.cpu_ax, self.memory_ax]:
            ax.tick_params(axis="x", rotation=45)

        plt.tight_layout()
        self.resource_canvas.draw()

    def update_status_panel(self):
        """상태 패널 업데이트"""

        # Echo 시스템 상태 (예시)
        if hasattr(self.ide, "echo_system") and self.ide.echo_system:
            self.echo_status_var.set("🟢 실행중")
        else:
            self.echo_status_var.set("🔴 대기")

        # 감염 시스템 상태
        if hasattr(self.ide, "infection_system") and self.ide.infection_system:
            self.infection_status_var.set("🟢 실행중")
        else:
            self.infection_status_var.set("🔴 대기")

        # 자율진화 상태
        if hasattr(self.ide, "auto_evolution") and self.ide.auto_evolution:
            self.evolution_status_var.set("🟢 진화중")
        else:
            self.evolution_status_var.set("🔴 대기")

        # 통계 업데이트
        if self.infection_rate_history:
            recent_infections = len(self.infection_rate_history)
            self.total_infections_var.set(str(recent_infections))

            if self.infection_rate_history:
                latest_rate = self.infection_rate_history[-1][1]
                self.success_rate_var.set(f"{latest_rate:.1f}%")

        if self.resonance_history:
            latest_resonance = self.resonance_history[-1][1]
            self.avg_resonance_var.set(f"{latest_resonance:.3f}")

        # 마지막 업데이트 시간
        self.last_update_var.set(datetime.now().strftime("%H:%M:%S"))

    def update_metrics_panel(self):
        """성능 지표 패널 업데이트"""

        # 현재 메트릭 계산
        current_time = datetime.now().strftime("%H:%M:%S")

        metrics_text = f"\n[{current_time}] 실시간 성능 지표\n"
        metrics_text += "-" * 30 + "\n"

        # 감염 통계
        if self.resonance_history:
            latest_resonance = self.resonance_history[-1][1]
            metrics_text += f"🎵 현재 공명 점수: {latest_resonance:.3f}\n"

        if self.infection_rate_history:
            latest_rate = self.infection_rate_history[-1][1]
            metrics_text += f"🦠 현재 성공률: {latest_rate:.1f}%\n"

        # 시그니처별 성능
        if self.signature_performance:
            metrics_text += "\n🎭 시그니처별 성능:\n"
            for sig_id, history in self.signature_performance.items():
                if history:
                    latest_score = history[-1][1]
                    metrics_text += f"  • {sig_id}: {latest_score:.3f}\n"

        # 시스템 리소스
        if self.system_metrics:
            latest_metrics = self.system_metrics[-1]
            metrics_text += f"\n💻 시스템 리소스:\n"
            metrics_text += f"  • CPU: {latest_metrics['cpu_percent']:.1f}%\n"
            metrics_text += f"  • Memory: {latest_metrics['memory_percent']:.1f}%\n"
            metrics_text += f"  • Disk: {latest_metrics['disk_percent']:.1f}%\n"

        # 텍스트 추가
        self.metrics_text.insert(tk.END, metrics_text)
        self.metrics_text.see(tk.END)

        # 텍스트가 너무 길어지면 앞부분 삭제
        if self.metrics_text.index(tk.END + "-1c").split(".")[0] > "100":
            self.metrics_text.delete("1.0", "20.0")

    def update_refresh_interval(self):
        """새로고침 간격 업데이트"""

        try:
            self.refresh_interval = float(self.refresh_var.get())
        except ValueError:
            self.refresh_interval = 2.0
            self.refresh_var.set("2.0")

    def reset_data(self):
        """데이터 리셋"""

        self.resonance_history.clear()
        self.infection_rate_history.clear()
        self.signature_performance.clear()
        self.system_metrics.clear()

        # 차트 클리어
        for ax in [
            self.resonance_ax,
            self.infection_ax,
            self.sig_bar_ax,
            self.sig_line_ax,
            self.cpu_ax,
            self.memory_ax,
        ]:
            ax.clear()

        for canvas in [
            self.resonance_canvas,
            self.infection_canvas,
            self.signature_canvas,
            self.resource_canvas,
        ]:
            canvas.draw()

        # 메트릭 텍스트 클리어
        self.metrics_text.delete("1.0", tk.END)
        self.metrics_text.insert(tk.END, "📊 데이터가 리셋되었습니다.\n")

        print("📊 모니터링 데이터 리셋 완료")


def create_monitor_dashboard_ui(parent_widget, project_root: Path, ide_instance):
    """모니터 대시보드 UI 생성"""

    dashboard = EchoMonitorDashboard(project_root, ide_instance)
    dashboard_frame = dashboard.create_dashboard_ui(parent_widget)

    return dashboard
