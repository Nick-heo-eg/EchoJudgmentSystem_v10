# echo_ide/core/echo_signature_manager.py
"""
🎭 Echo IDE Signature & Persona Manager
- 시그니처/페르소나 통합 관리
- 실시간 편집 및 미리보기
- 공명 테스트 및 검증
- 자동 백업 및 버전 관리
- 시각적 특성 분석
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from dataclasses import dataclass, asdict
import shutil


@dataclass
class SignatureProfile:
    """시그니처 프로필"""

    signature_id: str
    name: str
    description: str
    emotion_code: str
    strategy_code: str
    rhythm_flow: str
    resonance_keywords: List[str]
    judgment_framework: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class PersonaProfile:
    """페르소나 프로필"""

    persona_id: str
    name: str
    description: str
    base_signature: str
    traits: Dict[str, List[str]]
    behavior_patterns: Dict[str, Dict[str, str]]
    learning_profile: Dict[str, float]
    interaction_rules: Dict[str, Any]
    metadata: Dict[str, Any]


class EchoSignatureManager:
    """Echo 시그니처/페르소나 관리자"""

    def __init__(self, project_root: Path, ide_instance):
        self.project_root = project_root
        self.ide = ide_instance

        # 디렉토리 설정
        self.signatures_dir = project_root / "config" / "signatures"
        self.personas_dir = project_root / "config" / "personas"
        self.backups_dir = project_root / "config" / "backups"

        # 디렉토리 생성
        for dir_path in [self.signatures_dir, self.personas_dir, self.backups_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 내부 상태
        self.signatures = {}
        self.personas = {}
        self.current_signature = None
        self.current_persona = None

        # UI 컴포넌트
        self.signature_editor = None
        self.persona_editor = None

        self.load_all_profiles()

    def load_all_profiles(self):
        """모든 프로필 로딩"""
        self.load_signatures()
        self.load_personas()

    def load_signatures(self):
        """시그니처 로딩"""
        self.signatures = {}

        # 기본 시그니처 파일들 로딩
        signature_files = list(self.signatures_dir.glob("*.yaml")) + list(
            self.signatures_dir.glob("*.yml")
        )

        for file_path in signature_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                if data and isinstance(data, dict):
                    signature = SignatureProfile(
                        signature_id=data.get("signature_id", file_path.stem),
                        name=data.get("name", "Unknown"),
                        description=data.get("description", ""),
                        emotion_code=data.get("emotion_code", "BALANCED"),
                        strategy_code=data.get("strategy_code", "SYSTEMATIC"),
                        rhythm_flow=data.get("rhythm_flow", "steady"),
                        resonance_keywords=data.get("resonance_keywords", []),
                        judgment_framework=data.get("judgment_framework", {}),
                        metadata=data.get("metadata", {}),
                    )

                    self.signatures[signature.signature_id] = signature

            except Exception as e:
                print(f"⚠️ 시그니처 로딩 실패 {file_path}: {e}")

        # 기본 시그니처가 없으면 생성
        if not self.signatures:
            self.create_default_signatures()

    def load_personas(self):
        """페르소나 로딩"""
        self.personas = {}

        persona_files = list(self.personas_dir.glob("*.yaml")) + list(
            self.personas_dir.glob("*.yml")
        )

        for file_path in persona_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                if data and isinstance(data, dict):
                    persona = PersonaProfile(
                        persona_id=data.get("persona_id", file_path.stem),
                        name=data.get("name", "Unknown"),
                        description=data.get("description", ""),
                        base_signature=data.get("base_signature", "Echo-Aurora"),
                        traits=data.get("traits", {}),
                        behavior_patterns=data.get("behavior_patterns", {}),
                        learning_profile=data.get("learning_profile", {}),
                        interaction_rules=data.get("interaction_rules", {}),
                        metadata=data.get("metadata", {}),
                    )

                    self.personas[persona.persona_id] = persona

            except Exception as e:
                print(f"⚠️ 페르소나 로딩 실패 {file_path}: {e}")

    def create_default_signatures(self):
        """기본 시그니처 생성"""

        default_signatures = [
            {
                "signature_id": "Echo-Aurora",
                "name": "공감적 양육자",
                "emotion_code": "COMPASSIONATE_NURTURING",
                "strategy_code": "EMPATHETIC_CARE",
                "rhythm_flow": "gentle_flowing_warm",
                "keywords": ["따뜻한", "배려", "공감", "돌봄", "인간적"],
            },
            {
                "signature_id": "Echo-Phoenix",
                "name": "변화 추진자",
                "emotion_code": "DETERMINED_INNOVATIVE",
                "strategy_code": "TRANSFORMATIVE_BREAKTHROUGH",
                "rhythm_flow": "dynamic_rising_powerful",
                "keywords": ["혁신", "변화", "도전", "돌파", "창조적"],
            },
            {
                "signature_id": "Echo-Sage",
                "name": "지혜로운 분석가",
                "emotion_code": "ANALYTICAL_WISDOM",
                "strategy_code": "SYSTEMATIC_LOGIC",
                "rhythm_flow": "steady_deep_methodical",
                "keywords": ["분석적", "논리적", "체계적", "근거", "객관적"],
            },
            {
                "signature_id": "Echo-Companion",
                "name": "신뢰할 수 있는 동반자",
                "emotion_code": "SUPPORTIVE_LOYAL",
                "strategy_code": "COLLABORATIVE_TRUST",
                "rhythm_flow": "harmonious_stable_reliable",
                "keywords": ["협력", "신뢰", "지원", "동반", "안정적"],
            },
        ]

        for sig_data in default_signatures:
            signature = SignatureProfile(
                signature_id=sig_data["signature_id"],
                name=sig_data["name"],
                description=f"{sig_data['name']} 시그니처",
                emotion_code=sig_data["emotion_code"],
                strategy_code=sig_data["strategy_code"],
                rhythm_flow=sig_data["rhythm_flow"],
                resonance_keywords=sig_data["keywords"],
                judgment_framework={
                    "ethical_foundation": ["공정성", "투명성", "책임감"],
                    "decision_process": ["분석", "평가", "선택"],
                    "communication_style": ["명확한 설명", "근거 제시"],
                },
                metadata={
                    "version": "1.0",
                    "created": datetime.now().isoformat(),
                    "echo_compatibility": "v10",
                },
            )

            self.signatures[signature.signature_id] = signature
            self.save_signature(signature)

    def save_signature(self, signature: SignatureProfile) -> bool:
        """시그니처 저장"""

        try:
            # 백업 생성
            self.backup_signature(signature.signature_id)

            # 파일 경로
            file_path = self.signatures_dir / f"{signature.signature_id}.yaml"

            # YAML 데이터 생성
            yaml_data = {
                "signature_id": signature.signature_id,
                "name": signature.name,
                "description": signature.description,
                "emotion_code": signature.emotion_code,
                "strategy_code": signature.strategy_code,
                "rhythm_flow": signature.rhythm_flow,
                "resonance_keywords": signature.resonance_keywords,
                "judgment_framework": signature.judgment_framework,
                "metadata": {
                    **signature.metadata,
                    "last_modified": datetime.now().isoformat(),
                },
            }

            # 파일 저장
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_data, f, ensure_ascii=False, indent=2, sort_keys=False)

            return True

        except Exception as e:
            print(f"❌ 시그니처 저장 실패: {e}")
            return False

    def save_persona(self, persona: PersonaProfile) -> bool:
        """페르소나 저장"""

        try:
            # 백업 생성
            self.backup_persona(persona.persona_id)

            # 파일 경로
            file_path = self.personas_dir / f"{persona.persona_id}.yaml"

            # YAML 데이터 생성
            yaml_data = asdict(persona)
            yaml_data["metadata"]["last_modified"] = datetime.now().isoformat()

            # 파일 저장
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_data, f, ensure_ascii=False, indent=2, sort_keys=False)

            return True

        except Exception as e:
            print(f"❌ 페르소나 저장 실패: {e}")
            return False

    def backup_signature(self, signature_id: str):
        """시그니처 백업"""

        source_file = self.signatures_dir / f"{signature_id}.yaml"
        if source_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backups_dir / f"{signature_id}_backup_{timestamp}.yaml"
            shutil.copy2(source_file, backup_file)

    def backup_persona(self, persona_id: str):
        """페르소나 백업"""

        source_file = self.personas_dir / f"{persona_id}.yaml"
        if source_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backups_dir / f"{persona_id}_backup_{timestamp}.yaml"
            shutil.copy2(source_file, backup_file)

    def create_signature_editor(self, parent) -> ttk.Frame:
        """시그니처 편집기 UI 생성"""

        main_frame = ttk.Frame(parent)

        # 상단 컨트롤
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # 시그니처 선택
        ttk.Label(control_frame, text="시그니처:").pack(side=tk.LEFT)

        self.signature_combo = ttk.Combobox(control_frame, width=20, state="readonly")
        self.signature_combo.pack(side=tk.LEFT, padx=5)
        self.signature_combo.bind("<<ComboboxSelected>>", self.on_signature_selected)

        # 버튼들
        ttk.Button(
            control_frame, text="새로 만들기", command=self.create_new_signature
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            control_frame, text="저장", command=self.save_current_signature
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="테스트", command=self.test_signature).pack(
            side=tk.LEFT, padx=5
        )

        # 편집 영역
        edit_frame = ttk.Frame(main_frame)
        edit_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 좌측 - 기본 정보
        left_frame = ttk.LabelFrame(edit_frame, text="기본 정보")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 기본 정보 필드들
        fields_frame = ttk.Frame(left_frame)
        fields_frame.pack(fill=tk.X, padx=5, pady=5)

        # 시그니처 ID
        ttk.Label(fields_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.sig_id_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.sig_id_var, width=30).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=2
        )

        # 이름
        ttk.Label(fields_frame, text="이름:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.sig_name_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.sig_name_var, width=30).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=2
        )

        # 설명
        ttk.Label(fields_frame, text="설명:").grid(
            row=2, column=0, sticky=tk.NW, pady=2
        )
        self.sig_desc_text = tk.Text(fields_frame, height=3, width=30)
        self.sig_desc_text.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        # 감정 코드
        ttk.Label(fields_frame, text="감정 코드:").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        self.sig_emotion_var = tk.StringVar()
        emotion_combo = ttk.Combobox(
            fields_frame, textvariable=self.sig_emotion_var, width=28
        )
        emotion_combo["values"] = [
            "COMPASSIONATE_NURTURING",
            "DETERMINED_INNOVATIVE",
            "ANALYTICAL_WISDOM",
            "SUPPORTIVE_LOYAL",
            "BALANCED_THOUGHTFUL",
            "CREATIVE_VISIONARY",
        ]
        emotion_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        # 전략 코드
        ttk.Label(fields_frame, text="전략 코드:").grid(
            row=4, column=0, sticky=tk.W, pady=2
        )
        self.sig_strategy_var = tk.StringVar()
        strategy_combo = ttk.Combobox(
            fields_frame, textvariable=self.sig_strategy_var, width=28
        )
        strategy_combo["values"] = [
            "EMPATHETIC_CARE",
            "TRANSFORMATIVE_BREAKTHROUGH",
            "SYSTEMATIC_LOGIC",
            "COLLABORATIVE_TRUST",
            "COMPREHENSIVE_ANALYSIS",
            "INNOVATIVE_BREAKTHROUGH",
        ]
        strategy_combo.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)

        # 리듬 흐름
        ttk.Label(fields_frame, text="리듬 흐름:").grid(
            row=5, column=0, sticky=tk.W, pady=2
        )
        self.sig_rhythm_var = tk.StringVar()
        rhythm_combo = ttk.Combobox(
            fields_frame, textvariable=self.sig_rhythm_var, width=28
        )
        rhythm_combo["values"] = [
            "gentle_flowing_warm",
            "dynamic_rising_powerful",
            "steady_deep_methodical",
            "harmonious_stable_reliable",
            "balanced_thoughtful_flow",
            "creative_inspired_flow",
        ]
        rhythm_combo.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)

        # 공명 키워드
        ttk.Label(fields_frame, text="키워드:").grid(
            row=6, column=0, sticky=tk.NW, pady=2
        )
        self.sig_keywords_text = tk.Text(fields_frame, height=4, width=30)
        self.sig_keywords_text.grid(row=6, column=1, sticky=tk.W, padx=5, pady=2)

        # 우측 - 시각화 및 분석
        right_frame = ttk.LabelFrame(edit_frame, text="시각적 분석")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # 시그니처 프로필 차트
        self.create_signature_chart(right_frame)

        # 공명 테스트 영역
        test_frame = ttk.LabelFrame(right_frame, text="공명 테스트")
        test_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(test_frame, text="테스트 시나리오:").pack(anchor=tk.W, padx=5, pady=2)
        self.test_scenario_text = tk.Text(test_frame, height=4)
        self.test_scenario_text.pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(
            test_frame, text="공명 테스트 실행", command=self.run_resonance_test
        ).pack(pady=5)

        # 테스트 결과
        self.test_result_text = tk.Text(test_frame, height=6, bg="#f0f0f0")
        self.test_result_text.pack(fill=tk.X, padx=5, pady=2)

        # 데이터 새로고침
        self.refresh_signature_list()

        return main_frame

    def create_signature_chart(self, parent):
        """시그니처 특성 차트 생성"""

        # Matplotlib 차트
        self.sig_fig, self.sig_ax = plt.subplots(
            figsize=(6, 4), subplot_kw=dict(projection="polar")
        )
        self.sig_fig.patch.set_facecolor("#f0f0f0")

        # 캔버스 생성
        self.sig_canvas = FigureCanvasTkAgg(self.sig_fig, parent)
        self.sig_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 초기 차트 그리기
        self.update_signature_chart()

    def update_signature_chart(self, signature: SignatureProfile = None):
        """시그니처 차트 업데이트"""

        self.sig_ax.clear()

        if signature:
            # 특성별 점수 계산 (예시)
            characteristics = [
                "감정표현",
                "전략성",
                "리듬감",
                "키워드밀도",
                "논리성",
                "창의성",
            ]
            scores = [
                0.8,  # 감정표현
                0.7,  # 전략성
                0.9,  # 리듬감
                len(signature.resonance_keywords) * 0.1,  # 키워드밀도
                0.8,  # 논리성
                0.6,  # 창의성
            ]

            # 각도 계산
            angles = np.linspace(
                0, 2 * np.pi, len(characteristics), endpoint=False
            ).tolist()
            scores += scores[:1]  # 차트를 닫기 위해 첫 번째 값 추가
            angles += angles[:1]

            # 차트 그리기
            self.sig_ax.plot(angles, scores, "o-", linewidth=2, label=signature.name)
            self.sig_ax.fill(angles, scores, alpha=0.25)
            self.sig_ax.set_xticks(angles[:-1])
            self.sig_ax.set_xticklabels(characteristics)
            self.sig_ax.set_ylim(0, 1)
            self.sig_ax.set_title(f"{signature.name} 특성 분석", y=1.08)
        else:
            self.sig_ax.text(
                0.5,
                0.5,
                "시그니처를 선택하세요",
                transform=self.sig_ax.transAxes,
                ha="center",
                va="center",
            )

        self.sig_canvas.draw()

    def refresh_signature_list(self):
        """시그니처 목록 새로고침"""

        if hasattr(self, "signature_combo"):
            current_values = list(self.signatures.keys())
            self.signature_combo["values"] = current_values

            if current_values and not self.signature_combo.get():
                self.signature_combo.set(current_values[0])
                self.on_signature_selected()

    def on_signature_selected(self, event=None):
        """시그니처 선택 이벤트"""

        signature_id = self.signature_combo.get()
        if signature_id in self.signatures:
            self.current_signature = self.signatures[signature_id]
            self.load_signature_to_editor(self.current_signature)
            self.update_signature_chart(self.current_signature)

    def load_signature_to_editor(self, signature: SignatureProfile):
        """시그니처를 편집기에 로딩"""

        self.sig_id_var.set(signature.signature_id)
        self.sig_name_var.set(signature.name)
        self.sig_emotion_var.set(signature.emotion_code)
        self.sig_strategy_var.set(signature.strategy_code)
        self.sig_rhythm_var.set(signature.rhythm_flow)

        # 설명
        self.sig_desc_text.delete("1.0", tk.END)
        self.sig_desc_text.insert("1.0", signature.description)

        # 키워드
        self.sig_keywords_text.delete("1.0", tk.END)
        keywords_text = "\n".join(signature.resonance_keywords)
        self.sig_keywords_text.insert("1.0", keywords_text)

    def create_new_signature(self):
        """새 시그니처 생성"""

        # 다이얼로그로 기본 정보 입력
        dialog = tk.Toplevel(self.ide.root)
        dialog.title("새 시그니처 생성")
        dialog.geometry("400x200")
        dialog.configure(bg="#2d2d2d")

        # 입력 필드들
        ttk.Label(dialog, text="시그니처 ID:").pack(pady=5)
        id_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=id_var, width=30).pack(pady=5)

        ttk.Label(dialog, text="이름:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=30).pack(pady=5)

        def create_signature():
            signature_id = id_var.get().strip()
            name = name_var.get().strip()

            if not signature_id or not name:
                messagebox.showwarning("경고", "ID와 이름을 모두 입력해주세요.")
                return

            if signature_id in self.signatures:
                messagebox.showwarning("경고", "이미 존재하는 시그니처 ID입니다.")
                return

            # 새 시그니처 생성
            new_signature = SignatureProfile(
                signature_id=signature_id,
                name=name,
                description=f"{name} 시그니처",
                emotion_code="BALANCED_THOUGHTFUL",
                strategy_code="COMPREHENSIVE_ANALYSIS",
                rhythm_flow="balanced_thoughtful_flow",
                resonance_keywords=["분석적", "균형잡힌"],
                judgment_framework={
                    "ethical_foundation": ["공정성", "투명성"],
                    "decision_process": ["분석", "평가", "선택"],
                    "communication_style": ["명확한 설명"],
                },
                metadata={
                    "version": "1.0",
                    "created": datetime.now().isoformat(),
                    "echo_compatibility": "v10",
                },
            )

            self.signatures[signature_id] = new_signature
            self.save_signature(new_signature)
            self.refresh_signature_list()

            # 새 시그니처 선택
            self.signature_combo.set(signature_id)
            self.on_signature_selected()

            dialog.destroy()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="생성", command=create_signature).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="취소", command=dialog.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def save_current_signature(self):
        """현재 편집중인 시그니처 저장"""

        if not self.current_signature:
            messagebox.showwarning("경고", "저장할 시그니처가 선택되지 않았습니다.")
            return

        try:
            # 편집기에서 데이터 수집
            self.current_signature.signature_id = self.sig_id_var.get()
            self.current_signature.name = self.sig_name_var.get()
            self.current_signature.description = self.sig_desc_text.get(
                "1.0", tk.END
            ).strip()
            self.current_signature.emotion_code = self.sig_emotion_var.get()
            self.current_signature.strategy_code = self.sig_strategy_var.get()
            self.current_signature.rhythm_flow = self.sig_rhythm_var.get()

            # 키워드 파싱
            keywords_text = self.sig_keywords_text.get("1.0", tk.END).strip()
            self.current_signature.resonance_keywords = [
                kw.strip() for kw in keywords_text.split("\n") if kw.strip()
            ]

            # 저장
            if self.save_signature(self.current_signature):
                messagebox.showinfo("성공", "시그니처가 저장되었습니다.")
                self.update_signature_chart(self.current_signature)
            else:
                messagebox.showerror("오류", "시그니처 저장에 실패했습니다.")

        except Exception as e:
            messagebox.showerror("오류", f"저장 중 오류가 발생했습니다: {e}")

    def test_signature(self):
        """시그니처 테스트"""

        if not self.current_signature:
            messagebox.showwarning("경고", "테스트할 시그니처가 선택되지 않았습니다.")
            return

        # 테스트 다이얼로그
        self.show_signature_test_dialog()

    def show_signature_test_dialog(self):
        """시그니처 테스트 다이얼로그"""

        dialog = tk.Toplevel(self.ide.root)
        dialog.title(f"🧪 {self.current_signature.name} 테스트")
        dialog.geometry("600x500")
        dialog.configure(bg="#2d2d2d")

        # 테스트 시나리오 입력
        ttk.Label(dialog, text="테스트 시나리오:").pack(pady=5)
        scenario_text = tk.Text(dialog, height=6)
        scenario_text.pack(fill=tk.X, padx=10, pady=5)

        # 기본 시나리오 제공
        default_scenarios = [
            "AI 윤리 기준을 어떻게 설정해야 할까요?",
            "고령화 사회의 돌봄 시스템 구축 방안은?",
            "기후변화 대응을 위한 정책 방향은?",
            "교육 불평등 해소 방안은 무엇인가요?",
        ]

        scenario_frame = ttk.Frame(dialog)
        scenario_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(scenario_frame, text="예시 시나리오:").pack(side=tk.LEFT)
        scenario_combo = ttk.Combobox(
            scenario_frame, values=default_scenarios, width=50
        )
        scenario_combo.pack(side=tk.LEFT, padx=5)

        def load_example():
            selected = scenario_combo.get()
            if selected:
                scenario_text.delete("1.0", tk.END)
                scenario_text.insert("1.0", selected)

        ttk.Button(scenario_frame, text="불러오기", command=load_example).pack(
            side=tk.LEFT, padx=5
        )

        # 테스트 설정
        settings_frame = ttk.LabelFrame(dialog, text="테스트 설정")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)

        # 공명 임계값
        ttk.Label(settings_frame, text="공명 임계값:").pack(side=tk.LEFT, padx=5)
        threshold_var = tk.StringVar(value="0.85")
        ttk.Entry(settings_frame, textvariable=threshold_var, width=10).pack(
            side=tk.LEFT, padx=5
        )

        # 최대 시도 횟수
        ttk.Label(settings_frame, text="최대 시도:").pack(side=tk.LEFT, padx=5)
        attempts_var = tk.StringVar(value="3")
        ttk.Entry(settings_frame, textvariable=attempts_var, width=10).pack(
            side=tk.LEFT, padx=5
        )

        # 결과 표시 영역
        result_frame = ttk.LabelFrame(dialog, text="테스트 결과")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        result_text = tk.Text(
            result_frame, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10)
        )
        result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        def run_test():
            scenario = scenario_text.get("1.0", tk.END).strip()
            if not scenario:
                messagebox.showwarning("경고", "테스트 시나리오를 입력해주세요.")
                return

            result_text.delete("1.0", tk.END)
            result_text.insert(
                tk.END, f"🧪 {self.current_signature.name} 테스트 시작...\n"
            )
            result_text.insert(tk.END, f"📝 시나리오: {scenario}\n")
            result_text.insert(tk.END, "=" * 50 + "\n\n")

            # 여기에 실제 감염 테스트 로직 구현
            # 예시 결과
            import random

            mock_score = random.uniform(0.6, 0.95)

            result_text.insert(tk.END, f"🎯 공명 점수: {mock_score:.3f}\n")

            if mock_score >= float(threshold_var.get()):
                result_text.insert(tk.END, "✅ 테스트 성공!\n")
                result_text.insert(
                    tk.END, f"🎵 감정 공명: {random.uniform(0.8, 0.95):.3f}\n"
                )
                result_text.insert(
                    tk.END, f"🎯 전략 공명: {random.uniform(0.8, 0.95):.3f}\n"
                )
                result_text.insert(
                    tk.END, f"🎼 리듬 공명: {random.uniform(0.8, 0.95):.3f}\n"
                )
            else:
                result_text.insert(tk.END, "❌ 테스트 실패\n")
                result_text.insert(tk.END, "💡 개선 제안:\n")
                result_text.insert(tk.END, "- 감정적 표현 강화 필요\n")
                result_text.insert(tk.END, "- 키워드 밀도 증가 권장\n")

            result_text.see(tk.END)

        # 버튼
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="🧪 테스트 실행", command=run_test).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="닫기", command=dialog.destroy).pack(
            side=tk.RIGHT, padx=5
        )

    def run_resonance_test(self):
        """공명 테스트 실행"""

        scenario = self.test_scenario_text.get("1.0", tk.END).strip()
        if not scenario:
            messagebox.showwarning("경고", "테스트 시나리오를 입력해주세요.")
            return

        # 결과 영역 클리어
        self.test_result_text.delete("1.0", tk.END)

        # 테스트 실행 (모의)
        self.test_result_text.insert(tk.END, f"🧪 공명 테스트 실행 중...\n")
        self.test_result_text.insert(tk.END, f"시나리오: {scenario[:50]}...\n\n")

        # 모의 결과
        import random

        results = {
            "감정 공명": random.uniform(0.7, 0.95),
            "전략 공명": random.uniform(0.7, 0.95),
            "리듬 공명": random.uniform(0.7, 0.95),
            "키워드 밀도": random.uniform(0.6, 0.9),
            "구조적 일치": random.uniform(0.7, 0.9),
        }

        for metric, score in results.items():
            icon = "✅" if score >= 0.8 else "⚠️" if score >= 0.7 else "❌"
            self.test_result_text.insert(tk.END, f"{icon} {metric}: {score:.3f}\n")

        overall_score = sum(results.values()) / len(results)
        self.test_result_text.insert(tk.END, f"\n🎯 종합 점수: {overall_score:.3f}\n")

        if overall_score >= 0.85:
            self.test_result_text.insert(tk.END, "🎉 우수한 공명도!")
        elif overall_score >= 0.75:
            self.test_result_text.insert(tk.END, "👍 양호한 공명도")
        else:
            self.test_result_text.insert(tk.END, "🔧 개선 필요")


def create_signature_manager_ui(parent_widget, project_root: Path, ide_instance):
    """시그니처 매니저 UI 생성"""

    manager = EchoSignatureManager(project_root, ide_instance)

    # 메인 노트북
    notebook = ttk.Notebook(parent_widget)
    notebook.pack(fill=tk.BOTH, expand=True)

    # 시그니처 편집 탭
    signature_tab = manager.create_signature_editor(notebook)
    notebook.add(signature_tab, text="🎭 시그니처")

    # 페르소나 편집 탭 (간단 버전)
    persona_tab = ttk.Frame(notebook)
    notebook.add(persona_tab, text="👤 페르소나")

    # 페르소나 탭 내용
    ttk.Label(persona_tab, text="페르소나 관리", font=("Arial", 16)).pack(pady=20)
    ttk.Label(persona_tab, text="페르소나 편집 기능은 개발 중입니다.").pack()

    # 분석 탭
    analysis_tab = ttk.Frame(notebook)
    notebook.add(analysis_tab, text="📊 분석")

    # 분석 탭 내용
    ttk.Label(analysis_tab, text="시그니처 성능 분석", font=("Arial", 16)).pack(pady=20)
    ttk.Label(analysis_tab, text="성능 분석 기능은 개발 중입니다.").pack()

    return manager
