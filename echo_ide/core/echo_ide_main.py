#!/usr/bin/env python3
"""
🛠️ Echo IDE - EchoJudgmentSystem v10 통합 개발 환경
- 시그니처/페르소나/루프 통합 관리
- 실시간 감염 모니터링 및 제어
- 자동 코드 생성 및 AI 어시스턴트
- 파일 탐색 및 편집 인터페이스
"""

import os
import sys
import json
import asyncio
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess

# Echo 시스템 모듈 임포트
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from echo_engine.echo_infection_main import EchoInfectionSystem
    from echo_engine.logging.meta_infection_logger import MetaInfectionLogger
    from echo_engine.echo_signature_loader import get_all_signatures
    from echo_foundation_doctrine import EchoDoctrine
    from echo_auto import EchoAutoEvolution
except ImportError as e:
    print(f"⚠️ Echo 모듈 임포트 실패: {e}")


class EchoIDE:
    """Echo 통합 개발 환경"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧬 Echo IDE - EchoJudgmentSystem v10")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e1e")

        # 시스템 상태
        self.echo_system = None
        self.infection_system = None
        self.auto_evolution = None
        self.logger = None
        self.current_file = None
        self.project_root = Path(__file__).parent.parent.parent

        # AI 어시스턴트 초기화
        self.ai_assistant = None

        # UI 구성요소
        self.setup_ui()
        self.setup_system_integration()

        # 이벤트 바인딩
        self.setup_events()

        print("🛠️ Echo IDE 초기화 완료")

    def setup_ui(self):
        """UI 구성 요소 설정"""

        # 메인 메뉴
        self.setup_menu()

        # 툴바
        self.setup_toolbar()

        # 메인 판넬 (3분할)
        self.setup_main_panels()

        # 상태바
        self.setup_statusbar()

        # 상태 변수 초기화
        self.status_var = tk.StringVar(value="Echo IDE 준비 완료")

        # 스타일 적용
        self.apply_dark_theme()

    def setup_menu(self):
        """메뉴바 설정"""

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(
            label="새 파일", command=self.new_file, accelerator="Ctrl+N"
        )
        file_menu.add_command(
            label="열기", command=self.open_file, accelerator="Ctrl+O"
        )
        file_menu.add_command(
            label="저장", command=self.save_file, accelerator="Ctrl+S"
        )
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.quit_ide)

        # Echo 메뉴
        echo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Echo", menu=echo_menu)
        echo_menu.add_command(label="시스템 시작", command=self.start_echo_system)
        echo_menu.add_command(label="감염 루프 실행", command=self.run_infection_loop)
        echo_menu.add_command(label="자율진화 시작", command=self.start_auto_evolution)
        echo_menu.add_separator()
        echo_menu.add_command(label="시그니처 관리", command=self.manage_signatures)
        echo_menu.add_command(label="페르소나 관리", command=self.manage_personas)

        # 도구 메뉴
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도구", menu=tools_menu)
        tools_menu.add_command(label="터미널", command=self.open_terminal)
        tools_menu.add_command(label="로그 뷰어", command=self.open_log_viewer)
        tools_menu.add_command(
            label="성능 모니터", command=self.open_performance_monitor
        )

        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="Echo IDE 가이드", command=self.show_help)
        help_menu.add_command(label="정보", command=self.show_about)

    def setup_toolbar(self):
        """툴바 설정"""

        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        # 파일 버튼들
        ttk.Button(self.toolbar, text="📁", command=self.open_file, width=3).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(self.toolbar, text="💾", command=self.save_file, width=3).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=5
        )

        # Echo 시스템 버튼들
        ttk.Button(
            self.toolbar, text="🧬", command=self.start_echo_system, width=3
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            self.toolbar, text="🦠", command=self.run_infection_loop, width=3
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            self.toolbar, text="🔄", command=self.start_auto_evolution, width=3
        ).pack(side=tk.LEFT, padx=2)

        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=5
        )

        # 실행 버튼들
        ttk.Button(self.toolbar, text="▶️", command=self.run_current_file, width=3).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(self.toolbar, text="⏹️", command=self.stop_execution, width=3).pack(
            side=tk.LEFT, padx=2
        )

        # 우측 정렬 - 시스템 상태
        self.system_status = ttk.Label(self.toolbar, text="🔴 시스템 대기중")
        self.system_status.pack(side=tk.RIGHT, padx=10)

    def setup_main_panels(self):
        """메인 패널 3분할 구성"""

        # 메인 컨테이너
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 좌측 패널 - 파일 탐색기 & 시그니처 관리
        self.left_panel = ttk.Notebook(main_frame, width=300)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        self.setup_file_explorer()
        self.setup_signature_manager()
        self.setup_echo_monitor()

        # 중앙 패널 - 코드 편집기
        self.center_panel = ttk.Frame(main_frame)
        self.center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.setup_code_editor()

        # 우측 패널 - 출력 & 로그
        self.right_panel = ttk.Notebook(main_frame, width=400)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        self.setup_output_panel()
        self.setup_log_panel()
        self.setup_ai_assistant()

    def setup_file_explorer(self):
        """파일 탐색기 설정"""

        explorer_frame = ttk.Frame(self.left_panel)
        self.left_panel.add(explorer_frame, text="📁 파일")

        # 프로젝트 트리
        self.file_tree = ttk.Treeview(explorer_frame)
        self.file_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 스크롤바
        tree_scroll = ttk.Scrollbar(
            explorer_frame, orient=tk.VERTICAL, command=self.file_tree.yview
        )
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.configure(yscrollcommand=tree_scroll.set)

        # 트리 이벤트
        self.file_tree.bind("<Double-1>", self.on_file_double_click)

        # 프로젝트 루트 로딩
        self.load_project_tree()

    def setup_signature_manager(self):
        """시그니처 관리 패널"""

        sig_frame = ttk.Frame(self.left_panel)
        self.left_panel.add(sig_frame, text="🎭 시그니처")

        # 시그니처 목록
        self.signature_list = tk.Listbox(sig_frame, bg="#2d2d2d", fg="#ffffff")
        self.signature_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 시그니처 버튼들
        sig_buttons = ttk.Frame(sig_frame)
        sig_buttons.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(sig_buttons, text="편집", command=self.edit_signature).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(sig_buttons, text="테스트", command=self.test_signature).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(sig_buttons, text="새로고침", command=self.refresh_signatures).pack(
            side=tk.LEFT, padx=2
        )

        # 시그니처 로딩
        self.load_signatures()

    def setup_echo_monitor(self):
        """Echo 시스템 모니터"""

        monitor_frame = ttk.Frame(self.left_panel)
        self.left_panel.add(monitor_frame, text="📊 모니터")

        # 시스템 상태
        status_frame = ttk.LabelFrame(monitor_frame, text="시스템 상태")
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        self.echo_status_label = ttk.Label(status_frame, text="Echo System: 🔴 대기")
        self.echo_status_label.pack(anchor=tk.W, padx=5, pady=2)

        self.infection_status_label = ttk.Label(
            status_frame, text="Infection Loop: 🔴 대기"
        )
        self.infection_status_label.pack(anchor=tk.W, padx=5, pady=2)

        self.evolution_status_label = ttk.Label(
            status_frame, text="Auto Evolution: 🔴 대기"
        )
        self.evolution_status_label.pack(anchor=tk.W, padx=5, pady=2)

        # 감염 통계
        stats_frame = ttk.LabelFrame(monitor_frame, text="감염 통계")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)

        self.infection_stats = scrolledtext.ScrolledText(
            stats_frame, height=10, bg="#2d2d2d", fg="#ffffff"
        )
        self.infection_stats.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 새로고침 버튼
        ttk.Button(
            monitor_frame, text="📈 통계 새로고침", command=self.refresh_stats
        ).pack(pady=5)

    def setup_code_editor(self):
        """코드 편집기 설정"""

        # 편집기 프레임
        editor_frame = ttk.LabelFrame(self.center_panel, text="📝 코드 편집기")
        editor_frame.pack(fill=tk.BOTH, expand=True)

        # 탭 노트북
        self.editor_notebook = ttk.Notebook(editor_frame)
        self.editor_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 기본 편집 탭 추가
        self.add_editor_tab("새 파일", "")

    def setup_output_panel(self):
        """출력 패널 설정"""

        output_frame = ttk.Frame(self.right_panel)
        self.right_panel.add(output_frame, text="📤 출력")

        self.output_text = scrolledtext.ScrolledText(
            output_frame, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 출력 제어 버튼
        output_controls = ttk.Frame(output_frame)
        output_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(output_controls, text="지우기", command=self.clear_output).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(output_controls, text="저장", command=self.save_output).pack(
            side=tk.LEFT, padx=2
        )

    def setup_log_panel(self):
        """로그 패널 설정"""

        log_frame = ttk.Frame(self.right_panel)
        self.right_panel.add(log_frame, text="📋 로그")

        self.log_text = scrolledtext.ScrolledText(
            log_frame, bg="#1e1e1e", fg="#ffffff", font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 로그 제어
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(log_controls, text="새로고침", command=self.refresh_logs).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(
            log_controls, text="자동갱신", command=self.toggle_auto_refresh
        ).pack(side=tk.LEFT, padx=2)

        self.auto_refresh_logs = False

    def setup_ai_assistant(self):
        """AI 어시스턴트 패널"""

        try:
            from .echo_ai_assistant import create_ai_assistant_ui

            # 전체 AI 어시스턴트 UI 생성
            ai_frame = create_ai_assistant_ui(self.right_panel, self.project_root, self)
            self.right_panel.add(ai_frame, text="🤖 AI 도우미")

            # AI 어시스턴트 인스턴스 저장
            self.ai_assistant = ai_frame.master if hasattr(ai_frame, "master") else None

            print("🤖 AI 어시스턴트 완전 통합 완료")

        except ImportError as e:
            print(f"⚠️ AI 어시스턴트 모듈 임포트 실패: {e}")
            self.setup_basic_ai_assistant()
        except Exception as e:
            print(f"❌ AI 어시스턴트 설정 오류: {e}")
            self.setup_basic_ai_assistant()

    def setup_basic_ai_assistant(self):
        """AI 어시스턴트 기본 패널 (폴백)"""

        ai_frame = ttk.Frame(self.right_panel)
        self.right_panel.add(ai_frame, text="🤖 AI 도우미")

        # 대화 영역
        self.ai_chat = scrolledtext.ScrolledText(
            ai_frame, bg="#1a1a2e", fg="#e94560", font=("맑은 고딕", 10)
        )
        self.ai_chat.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 입력 영역
        input_frame = ttk.Frame(ai_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.ai_input = ttk.Entry(input_frame, font=("맑은 고딕", 10))
        self.ai_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(input_frame, text="전송", command=self.send_to_ai).pack(
            side=tk.RIGHT
        )

        # Enter 키 바인딩
        self.ai_input.bind("<Return>", lambda e: self.send_to_ai())

        # 초기 메시지
        self.ai_chat.insert(
            tk.END,
            "🤖 기본 AI 어시스턴트가 활성화되었습니다.\n전체 기능을 사용하려면 의존성을 설치해주세요.\n\n",
        )

    def setup_statusbar(self):
        """상태바 설정"""

        self.statusbar = ttk.Frame(self.root)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 상태 정보들
        self.status_left = ttk.Label(self.statusbar, text="준비됨")
        self.status_left.pack(side=tk.LEFT, padx=5)

        self.status_right = ttk.Label(
            self.statusbar,
            text=f"Echo IDE v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        )
        self.status_right.pack(side=tk.RIGHT, padx=5)

    def apply_dark_theme(self):
        """다크 테마 적용"""

        style = ttk.Style()
        style.theme_use("clam")

        # 다크 테마 색상
        style.configure("TFrame", background="#2d2d2d")
        style.configure("TLabel", background="#2d2d2d", foreground="#ffffff")
        style.configure("TButton", background="#404040", foreground="#ffffff")
        style.configure("TNotebook", background="#2d2d2d")
        style.configure("TNotebook.Tab", background="#404040", foreground="#ffffff")

    def setup_system_integration(self):
        """Echo 시스템 통합 설정"""

        try:
            self.logger = MetaInfectionLogger()
            self.log("✅ Meta Infection Logger 초기화 완료")
        except Exception as e:
            self.log(f"⚠️ Logger 초기화 실패: {e}")

    def setup_events(self):
        """이벤트 바인딩 설정"""

        # 키보드 단축키
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<F5>", lambda e: self.run_current_file())

        # 창 닫기 이벤트
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message: str):
        """로그 출력"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)

        print(message)  # 콘솔에도 출력

    def output(self, message: str):
        """출력 패널에 메시지 출력"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        output_message = f"[{timestamp}] {message}\n"

        self.output_text.insert(tk.END, output_message)
        self.output_text.see(tk.END)

    # 파일 관리 메서드들
    def new_file(self):
        """새 파일 생성"""
        self.add_editor_tab("새 파일", "")
        self.log("📄 새 파일 생성")

    def open_file(self):
        """파일 열기"""
        file_path = filedialog.askopenfilename(
            title="파일 열기",
            initialdir=self.project_root,
            filetypes=[
                ("Python files", "*.py"),
                ("YAML files", "*.yaml *.yml"),
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                file_name = Path(file_path).name
                self.add_editor_tab(file_name, content, file_path)
                self.current_file = file_path
                self.log(f"📂 파일 열기: {file_name}")

            except Exception as e:
                messagebox.showerror("오류", f"파일을 열 수 없습니다: {e}")

    def save_file(self):
        """파일 저장"""
        current_tab = self.editor_notebook.select()
        if not current_tab:
            return

        # 현재 탭의 텍스트 위젯 찾기
        tab_frame = self.editor_notebook.nametowidget(current_tab)
        text_widget = None

        for child in tab_frame.winfo_children():
            if isinstance(child, scrolledtext.ScrolledText):
                text_widget = child
                break

        if not text_widget:
            return

        content = text_widget.get("1.0", tk.END + "-1c")

        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(content)
                self.log(f"💾 파일 저장: {Path(self.current_file).name}")
            except Exception as e:
                messagebox.showerror("오류", f"파일을 저장할 수 없습니다: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        """다른 이름으로 저장"""
        file_path = filedialog.asksaveasfilename(
            title="다른 이름으로 저장",
            initialdir=self.project_root,
            defaultextension=".py",
            filetypes=[
                ("Python files", "*.py"),
                ("YAML files", "*.yaml"),
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            current_tab = self.editor_notebook.select()
            tab_frame = self.editor_notebook.nametowidget(current_tab)

            for child in tab_frame.winfo_children():
                if isinstance(child, scrolledtext.ScrolledText):
                    content = child.get("1.0", tk.END + "-1c")

                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)

                        self.current_file = file_path
                        self.log(f"💾 파일 저장: {Path(file_path).name}")

                        # 탭 제목 업데이트
                        tab_id = self.editor_notebook.index(current_tab)
                        self.editor_notebook.tab(tab_id, text=Path(file_path).name)

                    except Exception as e:
                        messagebox.showerror("오류", f"파일을 저장할 수 없습니다: {e}")
                    break

    def add_editor_tab(self, title: str, content: str, file_path: str = None):
        """편집기 탭 추가"""

        tab_frame = ttk.Frame(self.editor_notebook)

        # 텍스트 편집기
        text_editor = scrolledtext.ScrolledText(
            tab_frame,
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Consolas", 11),
            insertbackground="#ffffff",
            selectbackground="#264f78",
        )
        text_editor.pack(fill=tk.BOTH, expand=True)

        # 내용 설정
        text_editor.insert("1.0", content)

        # 탭 추가
        self.editor_notebook.add(tab_frame, text=title)
        self.editor_notebook.select(tab_frame)

        if file_path:
            text_editor.file_path = file_path

    # Echo 시스템 통합 메서드들
    def start_echo_system(self):
        """Echo 시스템 시작"""

        def start_system():
            try:
                self.echo_system = EchoDoctrine()
                self.infection_system = EchoInfectionSystem()

                self.update_status("echo", "🟢 실행중")
                self.log("🧬 Echo 시스템 시작 완료")
                self.output("Echo Foundation Doctrine 시스템이 시작되었습니다.")

            except Exception as e:
                self.log(f"❌ Echo 시스템 시작 실패: {e}")
                self.update_status("echo", "🔴 오류")

        threading.Thread(target=start_system, daemon=True).start()

    def run_infection_loop(self):
        """감염 루프 실행"""

        if not self.infection_system:
            messagebox.showwarning("경고", "먼저 Echo 시스템을 시작해주세요.")
            return

        # 감염 다이얼로그 표시
        self.show_infection_dialog()

    def start_auto_evolution(self):
        """자율진화 시작"""

        def start_evolution():
            try:
                self.auto_evolution = EchoAutoEvolution()
                self.update_status("evolution", "🟢 진화중")
                self.log("🔄 자율진화 시작")

                # 별도 스레드에서 실행
                threading.Thread(
                    target=self.auto_evolution.start_auto_evolution, daemon=True
                ).start()

            except Exception as e:
                self.log(f"❌ 자율진화 시작 실패: {e}")
                self.update_status("evolution", "🔴 오류")

        threading.Thread(target=start_evolution, daemon=True).start()

    def update_status(self, component: str, status: str):
        """상태 업데이트"""

        if component == "echo":
            self.echo_status_label.config(text=f"Echo System: {status}")
        elif component == "infection":
            self.infection_status_label.config(text=f"Infection Loop: {status}")
        elif component == "evolution":
            self.evolution_status_label.config(text=f"Auto Evolution: {status}")

    def show_infection_dialog(self):
        """감염 실행 다이얼로그"""

        dialog = tk.Toplevel(self.root)
        dialog.title("🦠 감염 루프 실행")
        dialog.geometry("500x400")
        dialog.configure(bg="#2d2d2d")

        # 시그니처 선택
        ttk.Label(dialog, text="시그니처 선택:").pack(pady=5)

        signature_var = tk.StringVar(value="Echo-Aurora")
        signature_combo = ttk.Combobox(
            dialog,
            textvariable=signature_var,
            values=["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"],
        )
        signature_combo.pack(pady=5)

        # 시나리오 입력
        ttk.Label(dialog, text="시나리오:").pack(pady=5)
        scenario_text = scrolledtext.ScrolledText(
            dialog, height=8, bg="#1e1e1e", fg="#ffffff"
        )
        scenario_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 설정
        settings_frame = ttk.Frame(dialog)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(settings_frame, text="최대 시도:").pack(side=tk.LEFT)
        attempts_var = tk.StringVar(value="3")
        ttk.Entry(settings_frame, textvariable=attempts_var, width=5).pack(
            side=tk.LEFT, padx=5
        )

        ttk.Label(settings_frame, text="임계값:").pack(side=tk.LEFT, padx=(10, 0))
        threshold_var = tk.StringVar(value="0.85")
        ttk.Entry(settings_frame, textvariable=threshold_var, width=8).pack(
            side=tk.LEFT, padx=5
        )

        # 버튼
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        def run_infection():
            signature = signature_var.get()
            scenario = scenario_text.get("1.0", tk.END).strip()
            max_attempts = int(attempts_var.get())
            threshold = float(threshold_var.get())

            if not scenario:
                messagebox.showwarning("경고", "시나리오를 입력해주세요.")
                return

            dialog.destroy()

            # 백그라운드에서 감염 실행
            def execute_infection():
                try:
                    self.update_status("infection", "🟡 실행중")
                    self.log(f"🦠 감염 시작: {signature}")

                    result = self.infection_system.run_single_infection(
                        signature_id=signature,
                        scenario=scenario,
                        max_attempts=max_attempts,
                        threshold=threshold,
                    )

                    if result["success"]:
                        self.log(f"✅ 감염 성공: {result['final_resonance_score']:.3f}")
                        self.output(
                            f"감염 성공! 공명 점수: {result['final_resonance_score']:.3f}"
                        )
                    else:
                        self.log(f"❌ 감염 실패: {result['error_message']}")
                        self.output(f"감염 실패: {result['error_message']}")

                    self.update_status("infection", "🟢 완료")

                except Exception as e:
                    self.log(f"❌ 감염 실행 오류: {e}")
                    self.update_status("infection", "🔴 오류")

            threading.Thread(target=execute_infection, daemon=True).start()

        ttk.Button(button_frame, text="실행", command=run_infection).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(button_frame, text="취소", command=dialog.destroy).pack(
            side=tk.RIGHT
        )

    # 기타 UI 메서드들
    def load_project_tree(self):
        """프로젝트 트리 로딩"""

        def insert_path(parent, path):
            for item in sorted(path.iterdir()):
                if item.name.startswith("."):
                    continue

                if item.is_dir():
                    folder_id = self.file_tree.insert(
                        parent, "end", text=f"📁 {item.name}", values=[str(item)]
                    )
                    try:
                        insert_path(folder_id, item)
                    except PermissionError:
                        pass
                else:
                    icon = "🐍" if item.suffix == ".py" else "📄"
                    self.file_tree.insert(
                        parent, "end", text=f"{icon} {item.name}", values=[str(item)]
                    )

        root_id = self.file_tree.insert(
            "",
            "end",
            text=f"🗂️ {self.project_root.name}",
            values=[str(self.project_root)],
        )
        insert_path(root_id, self.project_root)

        self.file_tree.item(root_id, open=True)

    def on_file_double_click(self, event):
        """파일 더블클릭 이벤트"""

        selection = self.file_tree.selection()
        if not selection:
            return

        item = self.file_tree.item(selection[0])
        file_path = item["values"][0] if item["values"] else None

        if file_path and Path(file_path).is_file():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                file_name = Path(file_path).name
                self.add_editor_tab(file_name, content, file_path)
                self.current_file = file_path

            except Exception as e:
                messagebox.showerror("오류", f"파일을 열 수 없습니다: {e}")

    def load_signatures(self):
        """시그니처 목록 로딩"""

        try:
            signatures = get_all_signatures()
            self.signature_list.delete(0, tk.END)

            for sig_id, name in signatures.items():
                self.signature_list.insert(tk.END, f"{sig_id}: {name}")

        except Exception as e:
            self.log(f"⚠️ 시그니처 로딩 실패: {e}")

    def refresh_signatures(self):
        """시그니처 새로고침"""
        self.load_signatures()
        self.log("🔄 시그니처 목록 새로고침")

    def refresh_stats(self):
        """통계 새로고침"""

        if not self.logger:
            return

        try:
            analytics = self.logger.get_infection_analytics(days=7)

            stats_text = f"""
📊 최근 7일 감염 통계:
━━━━━━━━━━━━━━━━━━━━
• 총 시도: {analytics['total_attempts']}
• 성공한 감염: {analytics['successful_infections']}
• 성공률: {analytics.get('success_rate', 0):.1%}

🏆 시그니처 순위:
"""

            for i, ranking in enumerate(analytics.get("signature_rankings", [])[:3], 1):
                stats_text += f"{i}. {ranking['signature_id']}: {ranking.get('success_rate', 0):.1%}\n"

            self.infection_stats.delete("1.0", tk.END)
            self.infection_stats.insert("1.0", stats_text)

        except Exception as e:
            self.log(f"⚠️ 통계 새로고침 실패: {e}")

    def refresh_logs(self):
        """로그 새로고침"""

        try:
            log_file = self.project_root / "meta_logs" / "infection_attempts.jsonl"

            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                recent_logs = lines[-50:]  # 최근 50개 로그

                self.log_text.delete("1.0", tk.END)

                for line in recent_logs:
                    try:
                        log_data = json.loads(line.strip())
                        timestamp = log_data.get("timestamp", "").split("T")[1][:8]
                        signature = log_data.get("signature_id", "Unknown")
                        score = log_data.get("resonance_score", 0)
                        success = "✅" if log_data.get("success", False) else "❌"

                        log_entry = (
                            f"[{timestamp}] {success} {signature}: {score:.3f}\n"
                        )
                        self.log_text.insert(tk.END, log_entry)

                    except json.JSONDecodeError:
                        continue

                self.log_text.see(tk.END)

        except Exception as e:
            self.log(f"⚠️ 로그 새로고침 실패: {e}")

    def send_to_ai(self):
        """AI 어시스턴트에 메시지 전송 (기본 모드용)"""

        if not hasattr(self, "ai_input") or not hasattr(self, "ai_chat"):
            return

        message = self.ai_input.get().strip()
        if not message:
            return

        # 사용자 메시지 표시
        self.ai_chat.insert(tk.END, f"👤 사용자: {message}\n")

        # AI 응답 (간단한 예시)
        ai_response = self.get_ai_response(message)
        self.ai_chat.insert(tk.END, f"🤖 Echo AI: {ai_response}\n\n")

        self.ai_chat.see(tk.END)
        self.ai_input.delete(0, tk.END)

    def update_status(self, message: str):
        """IDE 상태 메시지 업데이트"""
        if hasattr(self, "status_var"):
            self.status_var.set(message)
        print(f"IDE 상태: {message}")

    def get_ai_response(self, message: str) -> str:
        """AI 응답 생성 (간단한 규칙 기반)"""

        message_lower = message.lower()

        if "시그니처" in message:
            return "Echo 시스템에는 4개의 시그니처가 있습니다: Aurora(공감적 양육자), Phoenix(변화 추진자), Sage(지혜로운 분석가), Companion(신뢰할 수 있는 동반자). 어떤 시그니처에 대해 알고 싶으신가요?"

        elif "감염" in message:
            return "감염 루프는 Claude API를 통해 외부 AI를 Echo 시그니처 특성으로 감염시키는 기능입니다. Echo 메뉴에서 '감염 루프 실행'을 선택하여 시작할 수 있습니다."

        elif "자율진화" in message:
            return "자율진화 모드는 시스템이 자동으로 시나리오를 생성하고 감염을 실행하며 학습하는 기능입니다. 실시간으로 성능을 모니터링하고 개선합니다."

        elif "도움" in message or "help" in message_lower:
            return """Echo IDE 주요 기능:
• 파일 관리: 프로젝트 파일 편집 및 관리
• Echo 시스템: 통합 판단 시스템 실행
• 감염 루프: Claude API 감염 실행
• 자율진화: 자동 학습 및 최적화
• 모니터링: 실시간 시스템 상태 확인

무엇을 도와드릴까요?"""

        else:
            return f"'{message}'에 대한 질문을 이해했습니다. Echo 시스템의 특정 기능에 대해 더 자세히 질문해 주시면 도움을 드릴 수 있습니다."

    def run_current_file(self):
        """현재 파일 실행"""

        if not self.current_file:
            messagebox.showwarning("경고", "실행할 파일이 선택되지 않았습니다.")
            return

        if not self.current_file.endswith(".py"):
            messagebox.showwarning("경고", "Python 파일만 실행할 수 있습니다.")
            return

        def run_file():
            try:
                self.output(f"▶️ 실행 시작: {Path(self.current_file).name}")

                result = subprocess.run(
                    [sys.executable, self.current_file],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )

                if result.stdout:
                    self.output(f"📤 출력:\n{result.stdout}")

                if result.stderr:
                    self.output(f"❌ 오류:\n{result.stderr}")

                self.output(f"✅ 실행 완료 (종료 코드: {result.returncode})")

            except Exception as e:
                self.output(f"❌ 실행 오류: {e}")

        threading.Thread(target=run_file, daemon=True).start()

    def stop_execution(self):
        """실행 중단"""
        self.output("⏹️ 실행 중단 요청")

    def clear_output(self):
        """출력 지우기"""
        self.output_text.delete("1.0", tk.END)

    def save_output(self):
        """출력 저장"""
        content = self.output_text.get("1.0", tk.END)

        file_path = filedialog.asksaveasfilename(
            title="출력 저장",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.log(f"💾 출력 저장: {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("오류", f"출력을 저장할 수 없습니다: {e}")

    def toggle_auto_refresh(self):
        """자동 새로고침 토글"""
        self.auto_refresh_logs = not self.auto_refresh_logs

        if self.auto_refresh_logs:
            self.log("🔄 자동 로그 새로고침 활성화")
            self.auto_refresh_loop()
        else:
            self.log("⏸️ 자동 로그 새로고침 비활성화")

    def auto_refresh_loop(self):
        """자동 새로고침 루프"""
        if self.auto_refresh_logs:
            self.refresh_logs()
            self.refresh_stats()
            self.root.after(5000, self.auto_refresh_loop)  # 5초마다 새로고침

    # 메뉴 핸들러들
    def manage_signatures(self):
        """시그니처 관리 창"""
        messagebox.showinfo("정보", "시그니처 관리 기능은 개발 중입니다.")

    def manage_personas(self):
        """페르소나 관리 창"""
        messagebox.showinfo("정보", "페르소나 관리 기능은 개발 중입니다.")

    def open_terminal(self):
        """터미널 열기"""
        try:
            if os.name == "nt":  # Windows
                subprocess.Popen(["cmd"], cwd=self.project_root)
            else:  # Unix/Linux/Mac
                subprocess.Popen(["gnome-terminal"], cwd=self.project_root)
        except Exception as e:
            messagebox.showerror("오류", f"터미널을 열 수 없습니다: {e}")

    def open_log_viewer(self):
        """로그 뷰어 열기"""
        self.right_panel.select(1)  # 로그 탭 선택
        self.refresh_logs()

    def open_performance_monitor(self):
        """성능 모니터 열기"""
        self.left_panel.select(2)  # 모니터 탭 선택
        self.refresh_stats()

    def show_help(self):
        """도움말 표시"""
        help_text = """
🛠️ Echo IDE 사용 가이드

📁 파일 관리:
• Ctrl+N: 새 파일
• Ctrl+O: 파일 열기  
• Ctrl+S: 파일 저장
• F5: 현재 파일 실행

🧬 Echo 시스템:
• Echo 메뉴에서 시스템 시작
• 감염 루프로 Claude API 활용
• 자율진화로 자동 최적화

🎭 시그니처 관리:
• 좌측 패널에서 시그니처 확인
• 편집 및 테스트 기능 제공

📊 모니터링:
• 실시간 시스템 상태 확인
• 감염 통계 및 성능 분석
• 자동 로그 새로고침

🤖 AI 어시스턴트:
• 우측 패널에서 질문 입력
• Echo 시스템 관련 도움말 제공
"""

        messagebox.showinfo("Echo IDE 도움말", help_text)

    def show_about(self):
        """정보 표시"""
        about_text = """
🧬 Echo IDE v1.0

EchoJudgmentSystem v10 통합 개발 환경

주요 기능:
• 통합 파일 관리 및 편집
• Echo 시스템 실시간 제어
• Claude API 감염 루프 실행
• 자율진화 모니터링
• AI 어시스턴트 지원

개발: Echo Development Team
버전: 1.0.0
날짜: 2025년 1월
"""

        messagebox.showinfo("Echo IDE 정보", about_text)

    def quit_ide(self):
        """IDE 종료"""
        self.on_closing()

    def on_closing(self):
        """창 닫기 처리"""

        if messagebox.askokcancel("종료", "Echo IDE를 종료하시겠습니까?"):
            # 실행중인 작업들 정리
            if self.auto_evolution:
                try:
                    self.auto_evolution.evolution_active = False
                except:
                    pass

            self.log("👋 Echo IDE 종료")
            self.root.destroy()

    def run(self):
        """IDE 실행"""
        self.log("🚀 Echo IDE 시작")
        self.root.mainloop()


def main():
    """메인 실행 함수"""

    # 환경 검사
    project_root = Path(__file__).parent.parent.parent
    if not project_root.exists():
        print("❌ 프로젝트 루트 디렉토리를 찾을 수 없습니다.")
        return 1

    # Echo IDE 시작
    try:
        ide = EchoIDE()
        ide.run()
        return 0
    except Exception as e:
        print(f"❌ Echo IDE 시작 실패: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
