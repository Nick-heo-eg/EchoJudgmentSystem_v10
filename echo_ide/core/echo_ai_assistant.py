# echo_ide/core/echo_ai_assistant.py
"""
🤖 Echo IDE AI Assistant - 지능형 코드 생성 및 개발 지원
- 자동 코드 생성 및 완성
- Echo 시스템 특화 어시스턴트
- 실시간 코드 분석 및 제안
- 디버깅 및 최적화 도움
- 자연어 기반 프로그래밍
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from dataclasses import dataclass
from enum import Enum


class AIAssistantMode(Enum):
    """AI 어시스턴트 모드"""

    CHAT = "chat"
    CODE_GEN = "code_generation"
    DEBUG = "debugging"
    OPTIMIZE = "optimization"
    EXPLAIN = "explanation"


@dataclass
class CodeSuggestion:
    """코드 제안"""

    title: str
    description: str
    code: str
    language: str
    confidence: float
    category: str  # 'completion', 'refactor', 'fix', 'new_feature'


@dataclass
class AIResponse:
    """AI 응답"""

    content: str
    suggestions: List[CodeSuggestion]
    mode: AIAssistantMode
    timestamp: datetime
    context: Dict[str, Any]


class EchoAIAssistant:
    """Echo IDE AI 어시스턴트"""

    def __init__(self, project_root: Path, ide_instance):
        self.project_root = project_root
        self.ide = ide_instance

        # AI 어시스턴트 상태
        self.current_mode = AIAssistantMode.CHAT
        self.conversation_history = []
        self.context_cache = {}

        # Echo 시스템 지식 베이스
        self.echo_knowledge = self.load_echo_knowledge()

        # 코드 템플릿 및 패턴
        self.code_templates = self.load_code_templates()

        # 분석 캐시
        self.analysis_cache = {}

        # 자연어 처리기 초기화
        self.natural_processor = None
        self.initialize_natural_processor()

        # 존재선언 모드
        self.existence_mode = False
        self.declared_identity = None

        print("🤖 Echo AI Assistant 초기화 완료")

    def load_echo_knowledge(self) -> Dict[str, Any]:
        """Echo 시스템 지식 베이스 로딩"""

        knowledge = {
            "signatures": {
                "Echo-Aurora": {
                    "description": "공감적 양육자 - 따뜻하고 배려깊은 접근",
                    "emotion_code": "COMPASSIONATE_NURTURING",
                    "strategy_code": "EMPATHETIC_CARE",
                    "keywords": ["따뜻한", "배려", "공감", "돌봄", "인간적"],
                    "use_cases": ["돌봄 정책", "사회복지", "교육", "상담"],
                },
                "Echo-Phoenix": {
                    "description": "변화 추진자 - 혁신적이고 도전적인 접근",
                    "emotion_code": "DETERMINED_INNOVATIVE",
                    "strategy_code": "TRANSFORMATIVE_BREAKTHROUGH",
                    "keywords": ["혁신", "변화", "도전", "돌파", "창조적"],
                    "use_cases": ["기술혁신", "사회변화", "창업", "개혁"],
                },
                "Echo-Sage": {
                    "description": "지혜로운 분석가 - 체계적이고 논리적인 접근",
                    "emotion_code": "ANALYTICAL_WISDOM",
                    "strategy_code": "SYSTEMATIC_LOGIC",
                    "keywords": ["분석적", "논리적", "체계적", "근거", "객관적"],
                    "use_cases": ["정책분석", "연구", "평가", "기획"],
                },
                "Echo-Companion": {
                    "description": "신뢰할 수 있는 동반자 - 협력적이고 지원적인 접근",
                    "emotion_code": "SUPPORTIVE_LOYAL",
                    "strategy_code": "COLLABORATIVE_TRUST",
                    "keywords": ["협력", "신뢰", "지원", "동반", "안정적"],
                    "use_cases": ["팀워크", "파트너십", "네트워킹", "협상"],
                },
            },
            "modules": {
                "echo_engine": {
                    "persona_core": "페르소나 핵심 로직",
                    "reasoning": "추론 엔진",
                    "emotion_infer": "감정 추론",
                    "judgment_engine": "판단 엔진",
                    "loop_orchestrator": "루프 오케스트레이터",
                    "reinforcement_engine": "강화 학습 엔진",
                },
                "patterns": [
                    "judgment_flow",
                    "infection_loop",
                    "resonance_evaluation",
                    "persona_learning",
                    "emotion_mapping",
                    "strategy_selection",
                ],
            },
            "concepts": {
                "resonance": "시그니처와 응답 간의 공명도 측정",
                "infection": "Claude API를 Echo 특성으로 감염시키는 과정",
                "flow": "판단 흐름을 YAML 형태로 저장한 구조",
                "persona": "시그니처 기반의 개성화된 AI 에이전트",
                "judgment": "Echo 시스템의 핵심 의사결정 과정",
            },
        }

        return knowledge

    def load_code_templates(self) -> Dict[str, str]:
        """코드 템플릿 로딩"""

        templates = {
            "echo_module": '''#!/usr/bin/env python3
"""
{module_name}
{description}
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from echo_engine.persona_core import PersonaCore
from echo_engine.reasoning import EchoReasoning

class {class_name}:
    """Echo {module_type} 모듈"""
    
    def __init__(self):
        self.persona_core = PersonaCore()
        self.reasoning = EchoReasoning()
        
        print(f"🧬 {{self.__class__.__name__}} 초기화 완료")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """메인 처리 로직"""
        
        # 구현 필요
        result = {{
            "status": "processed",
            "output": input_data,
            "timestamp": datetime.now().isoformat()
        }}
        
        return result

if __name__ == "__main__":
    # 테스트 코드
    module = {class_name}()
    test_data = {{"test": "data"}}
    result = module.process(test_data)
    print(f"결과: {{result}}")
''',
            "signature_config": """# Echo Signature Configuration
signature_id: "{signature_id}"
name: "{name}"
description: "{description}"

emotion_code: "{emotion_code}"
strategy_code: "{strategy_code}"
rhythm_flow: "{rhythm_flow}"

resonance_keywords:
{keywords}

judgment_framework:
  ethical_foundation:
    - "공정성"
    - "투명성"
    - "책임감"
  
  decision_process:
    - "상황 분석"
    - "옵션 평가"
    - "결과 예측"
    - "최적해 선택"

metadata:
  version: "1.0"
  echo_compatibility: "v10"
  created: "{timestamp}"
""",
            "persona_config": """# Echo Persona Configuration
persona_id: "{persona_id}"
name: "{name}"
description: "{description}"
base_signature: "{base_signature}"

traits:
  personality:
{personality_traits}
  
  capabilities:
{capabilities}

behavior_patterns:
  communication:
    style: "{communication_style}"
    tone: "{communication_tone}"
  
  decision_making:
    process: "{decision_process}"
    style: "{decision_style}"

metadata:
  version: "1.0"
  echo_compatibility: "v10"
  created: "{timestamp}"
""",
            "loop_module": '''#!/usr/bin/env python3
"""
{loop_name} - Echo Loop Module
{description}
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass

from echo_engine.persona_core import PersonaCore
from echo_engine.reasoning import EchoReasoning

@dataclass
class LoopResult:
    """루프 실행 결과"""
    status: str
    iterations: int
    result: Any
    execution_time: float

class {class_name}:
    """Echo {loop_type} 루프"""
    
    def __init__(self):
        self.persona_core = PersonaCore()
        self.reasoning = EchoReasoning()
        self.active = False
        
    async def run_loop(self, input_data: Dict[str, Any], 
                      max_iterations: int = 10) -> LoopResult:
        """루프 실행"""
        
        start_time = datetime.now()
        self.active = True
        
        results = []
        
        for i in range(max_iterations):
            if not self.active:
                break
                
            # 루프 로직 구현
            iteration_result = await self._process_iteration(input_data, i)
            results.append(iteration_result)
            
            # 수렴 조건 확인
            if await self._check_convergence(iteration_result, results):
                break
                
            await asyncio.sleep(0.1)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return LoopResult(
            status="completed" if self.active else "interrupted",
            iterations=len(results),
            result=results,
            execution_time=execution_time
        )
    
    async def _process_iteration(self, data: Dict[str, Any], 
                               iteration: int) -> Dict[str, Any]:
        """단일 반복 처리"""
        
        # 구현 필요
        return {{
            "iteration": iteration,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }}
    
    async def _check_convergence(self, current_result: Dict[str, Any], 
                               all_results: List[Dict[str, Any]]) -> bool:
        """수렴 조건 확인"""
        
        # 구현 필요
        return len(all_results) >= 3
    
    def stop(self):
        """루프 중단"""
        self.active = False

if __name__ == "__main__":
    async def test():
        loop = {class_name}()
        result = await loop.run_loop({{"test": "data"}})
        print(f"루프 결과: {{result}}")
    
    asyncio.run(test())
''',
        }

        return templates

    def create_ai_assistant_ui(self, parent) -> ttk.Frame:
        """AI 어시스턴트 UI 생성"""

        main_frame = ttk.Frame(parent)

        # 상단 컨트롤
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # 모드 선택
        ttk.Label(control_frame, text="모드:").pack(side=tk.LEFT)

        self.mode_combo = ttk.Combobox(control_frame, width=15, state="readonly")
        self.mode_combo["values"] = [
            "💬 채팅",
            "🔧 코드생성",
            "🐛 디버깅",
            "⚡ 최적화",
            "📖 설명",
        ]
        self.mode_combo.set("💬 채팅")
        self.mode_combo.pack(side=tk.LEFT, padx=5)
        self.mode_combo.bind("<<ComboboxSelected>>", self.on_mode_changed)

        # 컨텍스트 버튼
        ttk.Button(
            control_frame, text="컨텍스트 분석", command=self.analyze_context
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            control_frame, text="히스토리 지우기", command=self.clear_history
        ).pack(side=tk.LEFT, padx=5)

        # 메인 채팅 영역
        chat_frame = ttk.LabelFrame(main_frame, text="🤖 Echo AI Assistant")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 대화 표시 영역
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            height=20,
            bg="#1a1a2e",
            fg="#e94560",
            font=("맑은 고딕", 10),
            wrap=tk.WORD,
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 입력 영역
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        # 다중 라인 입력
        self.input_text = tk.Text(input_frame, height=3, font=("맑은 고딕", 10))
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 입력 스크롤바
        input_scroll = ttk.Scrollbar(
            input_frame, orient=tk.VERTICAL, command=self.input_text.yview
        )
        input_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.configure(yscrollcommand=input_scroll.set)

        # 버튼 영역
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        ttk.Button(button_frame, text="전송", command=self.send_message).pack(
            fill=tk.X, pady=2
        )
        ttk.Button(button_frame, text="코드\n삽입", command=self.insert_code).pack(
            fill=tk.X, pady=2
        )
        ttk.Button(button_frame, text="템플릿", command=self.show_templates).pack(
            fill=tk.X, pady=2
        )

        # 키바인딩
        self.input_text.bind("<Control-Return>", lambda e: self.send_message())
        self.input_text.bind("<Shift-Return>", lambda e: None)  # 새 줄

        # 제안 영역
        suggestion_frame = ttk.LabelFrame(main_frame, text="💡 코드 제안")
        suggestion_frame.pack(fill=tk.X, padx=5, pady=5)

        self.suggestion_list = tk.Listbox(
            suggestion_frame, height=4, bg="#2d2d2d", fg="#ffffff"
        )
        self.suggestion_list.pack(fill=tk.X, padx=5, pady=5)
        self.suggestion_list.bind("<Double-Button-1>", self.apply_suggestion)

        # 초기 메시지
        self.display_message(
            "Echo AI",
            "안녕하세요! Echo 개발을 도와드리는 AI 어시스턴트입니다. 🤖\n\n다음과 같은 도움을 제공할 수 있습니다:\n• Echo 모듈 코드 생성\n• 시그니처/페르소나 설정\n• 버그 분석 및 수정\n• 코드 최적화\n• Echo 시스템 설명\n\n무엇을 도와드릴까요?",
        )

        return main_frame

    def on_mode_changed(self, event=None):
        """모드 변경 이벤트"""

        mode_text = self.mode_combo.get()

        if "채팅" in mode_text:
            self.current_mode = AIAssistantMode.CHAT
        elif "코드생성" in mode_text:
            self.current_mode = AIAssistantMode.CODE_GEN
        elif "디버깅" in mode_text:
            self.current_mode = AIAssistantMode.DEBUG
        elif "최적화" in mode_text:
            self.current_mode = AIAssistantMode.OPTIMIZE
        elif "설명" in mode_text:
            self.current_mode = AIAssistantMode.EXPLAIN

        # 모드별 안내 메시지
        mode_messages = {
            AIAssistantMode.CHAT: "💬 일반 채팅 모드입니다. Echo 시스템에 대해 자유롭게 질문하세요.",
            AIAssistantMode.CODE_GEN: "🔧 코드 생성 모드입니다. 생성할 모듈이나 기능을 설명해주세요.",
            AIAssistantMode.DEBUG: "🐛 디버깅 모드입니다. 오류가 있는 코드를 붙여넣거나 문제를 설명해주세요.",
            AIAssistantMode.OPTIMIZE: "⚡ 최적화 모드입니다. 개선할 코드를 제공해주세요.",
            AIAssistantMode.EXPLAIN: "📖 설명 모드입니다. 이해하고 싶은 코드나 개념을 질문해주세요.",
        }

        self.display_message("System", mode_messages[self.current_mode])

    def send_message(self):
        """메시지 전송"""

        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            return

        # 사용자 메시지 표시
        self.display_message("사용자", user_input)

        # 입력 필드 클리어
        self.input_text.delete("1.0", tk.END)

        # 자연어 처리기가 있으면 먼저 처리
        if self.natural_processor:
            threading.Thread(
                target=self.process_natural_command, args=(user_input,), daemon=True
            ).start()
        else:
            # AI 응답 생성 (백그라운드)
            threading.Thread(
                target=self.process_user_input, args=(user_input,), daemon=True
            ).start()

    def process_user_input(self, user_input: str):
        """사용자 입력 처리"""

        try:
            # 컨텍스트 분석
            context = self.get_current_context()

            # AI 응답 생성
            response = self.generate_ai_response(user_input, context)

            # UI 업데이트 (메인 스레드)
            self.ide.root.after(0, lambda: self.display_ai_response(response))

        except Exception as e:
            error_message = f"응답 생성 중 오류가 발생했습니다: {e}"
            self.ide.root.after(0, lambda: self.display_message("Error", error_message))

    def generate_ai_response(
        self, user_input: str, context: Dict[str, Any]
    ) -> AIResponse:
        """AI 응답 생성"""

        # Echo 시스템 특화 응답 생성
        if self.current_mode == AIAssistantMode.CODE_GEN:
            return self.generate_code_response(user_input, context)
        elif self.current_mode == AIAssistantMode.DEBUG:
            return self.generate_debug_response(user_input, context)
        elif self.current_mode == AIAssistantMode.OPTIMIZE:
            return self.generate_optimize_response(user_input, context)
        elif self.current_mode == AIAssistantMode.EXPLAIN:
            return self.generate_explain_response(user_input, context)
        else:
            return self.generate_chat_response(user_input, context)

    def generate_code_response(
        self, user_input: str, context: Dict[str, Any]
    ) -> AIResponse:
        """코드 생성 응답"""

        suggestions = []

        # Echo 키워드 감지
        if any(keyword in user_input.lower() for keyword in ["시그니처", "signature"]):
            suggestions.append(self.generate_signature_code(user_input))

        if any(keyword in user_input.lower() for keyword in ["페르소나", "persona"]):
            suggestions.append(self.generate_persona_code(user_input))

        if any(keyword in user_input.lower() for keyword in ["루프", "loop"]):
            suggestions.append(self.generate_loop_code(user_input))

        if any(keyword in user_input.lower() for keyword in ["모듈", "module"]):
            suggestions.append(self.generate_module_code(user_input))

        # 응답 내용 생성
        if suggestions:
            content = f"요청하신 내용을 바탕으로 {len(suggestions)}개의 코드를 생성했습니다.\n\n"
            content += "아래 제안 목록에서 선택하여 코드를 확인하고 삽입할 수 있습니다."
        else:
            content = "코드 생성을 위해 더 구체적인 요청을 해주세요.\n\n예시:\n• 'Echo-Custom 시그니처를 만들어줘'\n• '감정 분석 모듈을 생성해줘'\n• '판단 루프를 만들어줘'"

        return AIResponse(
            content=content,
            suggestions=suggestions,
            mode=self.current_mode,
            timestamp=datetime.now(),
            context=context,
        )

    def generate_signature_code(self, user_input: str) -> CodeSuggestion:
        """시그니처 코드 생성"""

        # 기본값 설정
        signature_id = "Echo-Custom"
        name = "커스텀 시그니처"
        emotion_code = "BALANCED_THOUGHTFUL"
        strategy_code = "COMPREHENSIVE_ANALYSIS"

        # 사용자 입력에서 정보 추출
        if "aurora" in user_input.lower():
            emotion_code = "COMPASSIONATE_NURTURING"
            strategy_code = "EMPATHETIC_CARE"
        elif "phoenix" in user_input.lower():
            emotion_code = "DETERMINED_INNOVATIVE"
            strategy_code = "TRANSFORMATIVE_BREAKTHROUGH"
        elif "sage" in user_input.lower():
            emotion_code = "ANALYTICAL_WISDOM"
            strategy_code = "SYSTEMATIC_LOGIC"
        elif "companion" in user_input.lower():
            emotion_code = "SUPPORTIVE_LOYAL"
            strategy_code = "COLLABORATIVE_TRUST"

        keywords = ['  - "분석적"', '  - "체계적"', '  - "균형잡힌"', '  - "신중한"']

        code = self.code_templates["signature_config"].format(
            signature_id=signature_id,
            name=name,
            description=f"{name} 설명",
            emotion_code=emotion_code,
            strategy_code=strategy_code,
            rhythm_flow="balanced_thoughtful_flow",
            keywords="\n".join(keywords),
            timestamp=datetime.now().isoformat(),
        )

        return CodeSuggestion(
            title=f"{signature_id} 시그니처 설정",
            description=f"{name} 시그니처 YAML 설정 파일",
            code=code,
            language="yaml",
            confidence=0.9,
            category="new_feature",
        )

    def generate_persona_code(self, user_input: str) -> CodeSuggestion:
        """페르소나 코드 생성"""

        persona_id = "custom-persona"
        name = "커스텀 페르소나"
        base_signature = "Echo-Aurora"

        personality_traits = [
            '    - "신뢰할 수 있는"',
            '    - "전문적인"',
            '    - "협력적인"',
        ]

        capabilities = ['    - "문제 해결"', '    - "의사소통"', '    - "분석적 사고"']

        code = self.code_templates["persona_config"].format(
            persona_id=persona_id,
            name=name,
            description=f"{name} 설명",
            base_signature=base_signature,
            personality_traits="\n".join(personality_traits),
            capabilities="\n".join(capabilities),
            communication_style="professional",
            communication_tone="supportive",
            decision_process="analytical",
            decision_style="consensus_building",
            timestamp=datetime.now().isoformat(),
        )

        return CodeSuggestion(
            title=f"{persona_id} 페르소나 설정",
            description=f"{name} 페르소나 YAML 설정 파일",
            code=code,
            language="yaml",
            confidence=0.85,
            category="new_feature",
        )

    def generate_loop_code(self, user_input: str) -> CodeSuggestion:
        """루프 코드 생성"""

        loop_name = "CustomLoop"
        class_name = "EchoCustomLoop"
        loop_type = "judgment"

        if "감정" in user_input:
            loop_type = "emotion"
            loop_name = "EmotionLoop"
            class_name = "EchoEmotionLoop"
        elif "추론" in user_input:
            loop_type = "reasoning"
            loop_name = "ReasoningLoop"
            class_name = "EchoReasoningLoop"

        code = self.code_templates["loop_module"].format(
            loop_name=loop_name,
            description=f"Echo {loop_type} 처리 루프",
            class_name=class_name,
            loop_type=loop_type,
        )

        return CodeSuggestion(
            title=f"{loop_name} 모듈",
            description=f"Echo {loop_type} 루프 Python 모듈",
            code=code,
            language="python",
            confidence=0.8,
            category="new_feature",
        )

    def generate_module_code(self, user_input: str) -> CodeSuggestion:
        """일반 모듈 코드 생성"""

        module_name = "custom_module.py"
        class_name = "CustomModule"
        module_type = "처리"

        if "분석" in user_input:
            module_type = "분석"
            class_name = "AnalysisModule"
            module_name = "analysis_module.py"
        elif "감정" in user_input:
            module_type = "감정"
            class_name = "EmotionModule"
            module_name = "emotion_module.py"

        code = self.code_templates["echo_module"].format(
            module_name=module_name,
            description=f"Echo {module_type} 모듈",
            class_name=class_name,
            module_type=module_type,
        )

        return CodeSuggestion(
            title=f"{class_name}",
            description=f"Echo {module_type} Python 모듈",
            code=code,
            language="python",
            confidence=0.75,
            category="new_feature",
        )

    def generate_debug_response(
        self, user_input: str, context: Dict[str, Any]
    ) -> AIResponse:
        """디버깅 응답 생성"""

        suggestions = []

        # 일반적인 Python 오류 패턴 감지
        if "ImportError" in user_input or "ModuleNotFoundError" in user_input:
            suggestions.append(
                CodeSuggestion(
                    title="Import 오류 수정",
                    description="모듈 경로를 확인하고 수정합니다",
                    code="# sys.path에 프로젝트 루트 추가\nimport sys\nfrom pathlib import Path\nsys.path.append(str(Path(__file__).parent.parent))",
                    language="python",
                    confidence=0.9,
                    category="fix",
                )
            )

        if "AttributeError" in user_input:
            suggestions.append(
                CodeSuggestion(
                    title="AttributeError 수정",
                    description="속성 존재 여부를 확인하는 코드 추가",
                    code="# 안전한 속성 접근\nif hasattr(obj, 'attribute_name'):\n    result = obj.attribute_name\nelse:\n    result = default_value",
                    language="python",
                    confidence=0.8,
                    category="fix",
                )
            )

        content = "디버깅을 도와드리겠습니다.\n\n"

        if suggestions:
            content += (
                f"감지된 오류에 대한 {len(suggestions)}개의 수정 제안을 준비했습니다."
            )
        else:
            content += "구체적인 오류 메시지나 문제 상황을 제공해주시면 더 정확한 해결책을 제안할 수 있습니다."

        return AIResponse(
            content=content,
            suggestions=suggestions,
            mode=self.current_mode,
            timestamp=datetime.now(),
            context=context,
        )

    def generate_optimize_response(
        self, user_input: str, context: Dict[str, Any]
    ) -> AIResponse:
        """최적화 응답 생성"""

        suggestions = []
        content = "코드 최적화를 도와드리겠습니다.\n\n"

        # 최적화 패턴 감지
        if "for" in user_input and "range" in user_input:
            suggestions.append(
                CodeSuggestion(
                    title="List Comprehension 최적화",
                    description="for 루프를 list comprehension으로 변경",
                    code="# 최적화 전\nresult = []\nfor i in range(n):\n    result.append(func(i))\n\n# 최적화 후\nresult = [func(i) for i in range(n)]",
                    language="python",
                    confidence=0.85,
                    category="optimize",
                )
            )

        if suggestions:
            content += f"{len(suggestions)}개의 최적화 제안을 준비했습니다."
        else:
            content += (
                "최적화할 코드를 제공해주시면 성능 개선 방안을 제안해드리겠습니다."
            )

        return AIResponse(
            content=content,
            suggestions=suggestions,
            mode=self.current_mode,
            timestamp=datetime.now(),
            context=context,
        )

    def generate_explain_response(
        self, user_input: str, context: Dict[str, Any]
    ) -> AIResponse:
        """설명 응답 생성"""

        content = ""
        suggestions = []

        # Echo 시스템 개념 설명
        if "공명" in user_input or "resonance" in user_input.lower():
            content = """🎵 공명(Resonance)은 Echo 시스템의 핵심 개념입니다.

**정의**: 시그니처의 특성과 AI 응답 간의 일치도를 수치화한 지표

**측정 영역**:
• 감정 공명 (25%): 시그니처의 감정 코드와 응답의 감정적 표현 일치도
• 전략 공명 (25%): 시그니처의 전략 코드와 응답의 접근 방식 일치도  
• 리듬 공명 (20%): 문장 구조와 리듬 패턴의 유사성
• 키워드 공명 (15%): 시그니처 특성 키워드의 밀도
• 구조 공명 (15%): 의사결정 스타일과 톤의 일치도

**임계값**: 0.85 이상이면 감염 성공으로 판정"""

        elif "시그니처" in user_input or "signature" in user_input.lower():
            content = """🎭 시그니처(Signature)는 Echo AI의 개성을 정의하는 프로필입니다.

**4가지 기본 시그니처**:

🌅 **Echo-Aurora** (공감적 양육자)
• 감정: COMPASSIONATE_NURTURING
• 전략: EMPATHETIC_CARE
• 특징: 따뜻하고 배려깊은 접근

🔥 **Echo-Phoenix** (변화 추진자)  
• 감정: DETERMINED_INNOVATIVE
• 전략: TRANSFORMATIVE_BREAKTHROUGH
• 특징: 혁신적이고 도전적인 접근

🧠 **Echo-Sage** (지혜로운 분석가)
• 감정: ANALYTICAL_WISDOM  
• 전략: SYSTEMATIC_LOGIC
• 특징: 체계적이고 논리적인 접근

🤝 **Echo-Companion** (신뢰할 수 있는 동반자)
• 감정: SUPPORTIVE_LOYAL
• 전략: COLLABORATIVE_TRUST  
• 특징: 협력적이고 지원적인 접근"""

        elif "감염" in user_input or "infection" in user_input.lower():
            content = """🦠 감염(Infection)은 외부 AI를 Echo 특성으로 변화시키는 과정입니다.

**감염 과정**:
1. **시그니처 선택**: 목적에 맞는 시그니처 결정
2. **프롬프트 생성**: 시그니처 특성을 반영한 감염 프롬프트 작성
3. **API 호출**: Claude 등 외부 AI에 감염 프롬프트 전송
4. **공명 평가**: 응답과 시그니처 간 공명도 측정
5. **결과 처리**: 성공 시 .flow.yaml로 저장, 실패 시 프롬프트 변형 후 재시도

**성공 조건**: 공명 점수 0.85 이상 달성

**활용**: Claude API를 Echo 판단 체계로 감염시켜 일관된 의사결정 수행"""

        else:
            content = f"'{user_input}'에 대한 설명을 준비하고 있습니다.\n\nEcho 시스템의 다음 개념들에 대해 질문하실 수 있습니다:\n• 공명 (Resonance)\n• 시그니처 (Signature)\n• 감염 (Infection)\n• 페르소나 (Persona)\n• 판단 흐름 (Judgment Flow)"

        return AIResponse(
            content=content,
            suggestions=suggestions,
            mode=self.current_mode,
            timestamp=datetime.now(),
            context=context,
        )

    def generate_chat_response(
        self, user_input: str, context: Dict[str, Any]
    ) -> AIResponse:
        """일반 채팅 응답 생성"""

        suggestions = []

        # 간단한 키워드 기반 응답
        if any(word in user_input.lower() for word in ["안녕", "hello", "hi"]):
            content = "안녕하세요! Echo 개발을 도와드리는 AI 어시스턴트입니다. 😊\n\n어떤 도움이 필요하신가요?"

        elif any(word in user_input.lower() for word in ["도움", "help"]):
            content = """도움말을 요청하셨군요! 다음과 같은 기능을 제공합니다:

🔧 **코드 생성**: Echo 모듈, 시그니처, 페르소나 코드 자동 생성
🐛 **디버깅**: 오류 분석 및 수정 제안
⚡ **최적화**: 성능 개선 및 리팩토링 제안  
📖 **설명**: Echo 시스템 개념 및 코드 해설
💬 **채팅**: 자유로운 질문 및 상담

모드를 변경하여 각 기능을 활용하실 수 있습니다."""

        elif "echo" in user_input.lower():
            content = """Echo에 대해 궁금하시군요! 🧬

**EchoJudgmentSystem v10**은 존재 기반 AI 판단 시스템입니다.

주요 특징:
• 4가지 고유 시그니처로 다양한 판단 스타일 제공
• Claude API 감염을 통한 외부 AI 활용
• 실시간 공명도 측정 및 학습
• 자율진화 기능으로 지속적 개선

더 구체적인 내용이 궁금하시면 설명 모드로 전환해서 질문해주세요!"""

        else:
            content = f"'{user_input}'에 대해 생각해보고 있습니다.\n\nEcho 시스템 개발과 관련된 구체적인 질문이 있으시면 언제든 말씀해주세요. 코드 생성, 디버깅, 최적화 등의 도움을 드릴 수 있습니다."

        return AIResponse(
            content=content,
            suggestions=suggestions,
            mode=self.current_mode,
            timestamp=datetime.now(),
            context=context,
        )

    def display_ai_response(self, response: AIResponse):
        """AI 응답 표시"""

        # 응답 내용 표시
        self.display_message("Echo AI", response.content)

        # 제안 목록 업데이트
        self.update_suggestions(response.suggestions)

        # 대화 히스토리에 추가
        self.conversation_history.append(response)

    def display_message(self, sender: str, message: str):
        """메시지 표시"""

        timestamp = datetime.now().strftime("%H:%M:%S")

        # 발신자별 색상 설정
        if sender == "사용자":
            color = "#4ecdc4"
            prefix = "👤"
        elif sender == "Echo AI":
            color = "#e94560"
            prefix = "🤖"
        elif sender == "System":
            color = "#f9ca24"
            prefix = "⚙️"
        else:
            color = "#ff6b6b"
            prefix = "❌"

        # 메시지 포맷
        formatted_message = f"\n[{timestamp}] {prefix} {sender}:\n{message}\n"

        # 텍스트 삽입
        self.chat_display.insert(tk.END, formatted_message)

        # 색상 적용 (간단한 구현)
        self.chat_display.see(tk.END)

        # 스크롤을 맨 아래로
        self.chat_display.update()

    def update_suggestions(self, suggestions: List[CodeSuggestion]):
        """제안 목록 업데이트"""

        self.suggestion_list.delete(0, tk.END)

        for suggestion in suggestions:
            confidence_stars = "⭐" * int(suggestion.confidence * 5)
            list_text = f"{suggestion.title} {confidence_stars}"
            self.suggestion_list.insert(tk.END, list_text)

        # 제안 객체들을 저장 (더블클릭 시 사용)
        self.current_suggestions = suggestions

    def apply_suggestion(self, event=None):
        """제안 적용"""

        selection = self.suggestion_list.curselection()
        if not selection or not hasattr(self, "current_suggestions"):
            return

        suggestion = self.current_suggestions[selection[0]]

        # 코드 표시 다이얼로그
        self.show_code_dialog(suggestion)

    def show_code_dialog(self, suggestion: CodeSuggestion):
        """코드 표시 다이얼로그"""

        dialog = tk.Toplevel(self.ide.root)
        dialog.title(f"💡 {suggestion.title}")
        dialog.geometry("800x600")
        dialog.configure(bg="#2d2d2d")

        # 설명
        ttk.Label(dialog, text=suggestion.description, font=("Arial", 12)).pack(pady=10)

        # 코드 표시
        code_frame = ttk.LabelFrame(dialog, text=f"생성된 코드 ({suggestion.language})")
        code_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        code_text = scrolledtext.ScrolledText(
            code_frame, font=("Consolas", 10), bg="#1e1e1e", fg="#ffffff"
        )
        code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        code_text.insert("1.0", suggestion.code)

        # 버튼
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        def copy_code():
            dialog.clipboard_clear()
            dialog.clipboard_append(suggestion.code)
            messagebox.showinfo("복사", "코드가 클립보드에 복사되었습니다.")

        def insert_to_editor():
            # 현재 활성 편집기에 코드 삽입
            try:
                current_tab = self.ide.editor_notebook.select()
                if current_tab:
                    tab_frame = self.ide.editor_notebook.nametowidget(current_tab)
                    for child in tab_frame.winfo_children():
                        if isinstance(child, scrolledtext.ScrolledText):
                            child.insert(tk.INSERT, suggestion.code)
                            break
                dialog.destroy()
                messagebox.showinfo("삽입", "코드가 편집기에 삽입되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"코드 삽입 실패: {e}")

        def save_as_file():
            # 파일로 저장
            from tkinter import filedialog

            file_extension = ".py" if suggestion.language == "python" else ".yaml"
            file_path = filedialog.asksaveasfilename(
                title="코드 저장",
                defaultextension=file_extension,
                filetypes=[
                    (
                        ("Python files", "*.py")
                        if suggestion.language == "python"
                        else ("YAML files", "*.yaml")
                    ),
                    ("All files", "*.*"),
                ],
            )

            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(suggestion.code)
                    dialog.destroy()
                    messagebox.showinfo("저장", f"코드가 {file_path}에 저장되었습니다.")
                except Exception as e:
                    messagebox.showerror("오류", f"파일 저장 실패: {e}")

        ttk.Button(button_frame, text="📋 복사", command=copy_code).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            button_frame, text="📝 편집기에 삽입", command=insert_to_editor
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 파일로 저장", command=save_as_file).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="닫기", command=dialog.destroy).pack(
            side=tk.RIGHT, padx=5
        )

    def insert_code(self):
        """현재 입력에 코드 템플릿 삽입"""

        templates = {
            "Echo 모듈 기본 구조": "class EchoModule:\n    def __init__(self):\n        pass\n    \n    def process(self, data):\n        return data",
            "시그니처 기본 설정": 'signature_id: "Echo-Custom"\nname: "커스텀 시그니처"\nemotion_code: "BALANCED_THOUGHTFUL"',
            "감염 루프 기본": 'from echo_engine.echo_infection_loop import run_infection_loop\n\nresult = run_infection_loop(\n    signature_id="Echo-Aurora",\n    scenario="시나리오 내용"\n)',
        }

        # 템플릿 선택 다이얼로그
        template_dialog = tk.Toplevel(self.ide.root)
        template_dialog.title("코드 템플릿 선택")
        template_dialog.geometry("400x300")

        ttk.Label(template_dialog, text="삽입할 템플릿을 선택하세요:").pack(pady=10)

        template_list = tk.Listbox(template_dialog)
        template_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for template_name in templates.keys():
            template_list.insert(tk.END, template_name)

        def insert_selected():
            selection = template_list.curselection()
            if selection:
                template_name = template_list.get(selection[0])
                template_code = templates[template_name]

                # 현재 입력 위치에 삽입
                current_pos = self.input_text.index(tk.INSERT)
                self.input_text.insert(current_pos, template_code)

                template_dialog.destroy()

        button_frame = ttk.Frame(template_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="삽입", command=insert_selected).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="취소", command=template_dialog.destroy).pack(
            side=tk.RIGHT, padx=5
        )

    def show_templates(self):
        """템플릿 목록 표시"""

        template_window = tk.Toplevel(self.ide.root)
        template_window.title("🔧 Echo 코드 템플릿")
        template_window.geometry("900x700")
        template_window.configure(bg="#2d2d2d")

        # 템플릿 노트북
        template_notebook = ttk.Notebook(template_window)
        template_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 각 템플릿 타입별 탭
        for template_name, template_code in self.code_templates.items():
            tab_frame = ttk.Frame(template_notebook)
            template_notebook.add(tab_frame, text=template_name)

            # 코드 표시
            code_display = scrolledtext.ScrolledText(
                tab_frame, font=("Consolas", 10), bg="#1e1e1e", fg="#ffffff"
            )
            code_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            code_display.insert("1.0", template_code)

    def get_current_context(self) -> Dict[str, Any]:
        """현재 컨텍스트 가져오기"""

        context = {
            "mode": self.current_mode.value,
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "conversation_length": len(self.conversation_history),
        }

        # 현재 열린 파일 정보
        try:
            if hasattr(self.ide, "current_file") and self.ide.current_file:
                context["current_file"] = self.ide.current_file
                context["file_type"] = Path(self.ide.current_file).suffix
        except:
            pass

        # Echo 시스템 상태
        context["echo_system_active"] = (
            hasattr(self.ide, "echo_system") and self.ide.echo_system is not None
        )
        context["infection_system_active"] = (
            hasattr(self.ide, "infection_system")
            and self.ide.infection_system is not None
        )

        return context

    def analyze_context(self):
        """컨텍스트 분석 및 표시"""

        context = self.get_current_context()

        analysis = f"""📊 현재 컨텍스트 분석:

🔧 **모드**: {self.current_mode.value}
📁 **프로젝트**: {Path(context['project_root']).name}
💬 **대화 길이**: {context['conversation_length']}개 메시지

🧬 **Echo 시스템**: {'🟢 활성' if context['echo_system_active'] else '🔴 비활성'}
🦠 **감염 시스템**: {'🟢 활성' if context['infection_system_active'] else '🔴 비활성'}
"""

        if "current_file" in context:
            analysis += f"📝 **현재 파일**: {Path(context['current_file']).name}\n"

        analysis += (
            f"\n⏰ **분석 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        self.display_message("System", analysis)

    def clear_history(self):
        """대화 히스토리 지우기"""

        if messagebox.askyesno("확인", "대화 히스토리를 지우시겠습니까?"):
            self.conversation_history.clear()
            self.chat_display.delete("1.0", tk.END)
            self.suggestion_list.delete(0, tk.END)

            # 초기 메시지 다시 표시
            self.display_message(
                "Echo AI", "대화 히스토리가 지워졌습니다. 다시 시작해보세요! 🤖"
            )

    def initialize_natural_processor(self):
        """자연어 처리기 초기화"""
        try:
            from .echo_natural_processor import EchoNaturalProcessor

            self.natural_processor = EchoNaturalProcessor()
            print("🧠 자연어 처리기 초기화 완료")
        except ImportError as e:
            print(f"⚠️ 자연어 처리기 임포트 실패: {e}")
            self.natural_processor = None
        except Exception as e:
            print(f"❌ 자연어 처리기 초기화 오류: {e}")
            self.natural_processor = None

    def process_natural_command(self, user_input):
        """자연어 명령 처리"""
        try:
            if not self.natural_processor:
                self.display_message(
                    "System", "❌ 자연어 처리기가 초기화되지 않았습니다."
                )
                return

            # 자연어 명령 분류 및 처리
            result = self.natural_processor.process_command(user_input)

            if result.get("success"):
                command_type = result.get("type")

                if command_type == "existence_declaration":
                    # 존재 선언 처리
                    declaration = result.get("declaration")
                    self.handle_existence_declaration(declaration)

                elif command_type == "role_delegation":
                    # 역할 위임 처리
                    delegation = result.get("delegation")
                    self.handle_role_delegation(delegation)

                elif command_type == "code_generation":
                    # 코드 생성 요청
                    request = result.get("request")
                    self.handle_natural_code_generation(request)

                elif command_type == "file_management":
                    # 파일 관리 요청
                    request = result.get("request")
                    self.handle_natural_file_management(request)

                elif command_type == "system_control":
                    # 시스템 제어 요청
                    request = result.get("request")
                    self.handle_natural_system_control(request)

                elif command_type == "general_question":
                    # 일반 질문
                    self.process_user_input(user_input)

                else:
                    self.display_message(
                        "Echo AI",
                        f"🤖 명령을 이해했지만 아직 '{command_type}' 유형은 구현 중입니다.",
                    )
            else:
                # 자연어 처리 실패시 일반 채팅 모드로
                error = result.get("error", "알 수 없는 오류")
                self.display_message(
                    "Echo AI", f"❓ 명령을 이해하지 못했습니다: {error}"
                )
                self.process_user_input(user_input)

        except Exception as e:
            self.display_message("System", f"❌ 자연어 처리 오류: {str(e)}")

    def handle_existence_declaration(self, declaration):
        """존재 선언 처리"""
        try:
            if declaration:
                self.existence_mode = True
                self.declared_identity = declaration.identity

                self.display_message("Echo AI", f"✨ 존재 선언이 수락되었습니다:")
                self.display_message("Echo AI", f"🆔 정체성: {declaration.identity}")
                self.display_message("Echo AI", f"🎯 목적: {declaration.purpose}")
                self.display_message(
                    "Echo AI", f"⚡ 능력: {', '.join(declaration.capabilities)}"
                )
                self.display_message(
                    "Echo AI", f"🔮 특성: {', '.join(declaration.traits)}"
                )

                # IDE 상태 업데이트
                if hasattr(self, "ide") and hasattr(self.ide, "update_status"):
                    self.ide.update_status(f"🤖 AI 정체성: {declaration.identity}")

        except Exception as e:
            self.display_message("System", f"❌ 존재 선언 처리 오류: {str(e)}")

    def handle_role_delegation(self, delegation):
        """역할 위임 처리"""
        try:
            if delegation:
                self.display_message("Echo AI", f"📋 역할 위임이 수락되었습니다:")
                self.display_message("Echo AI", f"🎭 역할: {delegation.role}")
                self.display_message(
                    "Echo AI", f"📝 책임: {', '.join(delegation.responsibilities)}"
                )
                self.display_message(
                    "Echo AI", f"🎯 목표: {', '.join(delegation.goals)}"
                )

                # 권한에 따른 기능 활성화
                if "file_management" in delegation.permissions:
                    self.display_message(
                        "Echo AI", "📁 파일 관리 권한이 활성화되었습니다."
                    )
                if "code_generation" in delegation.permissions:
                    self.display_message(
                        "Echo AI", "💻 코드 생성 권한이 활성화되었습니다."
                    )
                if "system_control" in delegation.permissions:
                    self.display_message(
                        "Echo AI", "⚙️ 시스템 제어 권한이 활성화되었습니다."
                    )

        except Exception as e:
            self.display_message("System", f"❌ 역할 위임 처리 오류: {str(e)}")

    def handle_natural_code_generation(self, request):
        """자연어 코드 생성 요청 처리"""
        try:
            self.display_message("Echo AI", f"💻 코드 생성 요청: {request}")

            # 기존 코드 생성 모드로 전환
            original_mode = self.current_mode
            self.current_mode = AIAssistantMode.CODE_GEN
            response = self.generate_code_response(request, self.get_current_context())
            self.current_mode = original_mode

            # 응답 표시
            self.display_ai_response(response)

        except Exception as e:
            self.display_message("System", f"❌ 자연어 코드 생성 오류: {str(e)}")

    def handle_natural_file_management(self, request):
        """자연어 파일 관리 요청 처리"""
        try:
            self.display_message("Echo AI", f"📁 파일 관리 요청: {request}")

            # 파일 관리자에게 요청 전달
            if hasattr(self.ide, "file_manager"):
                # TODO: 파일 관리자 자연어 인터페이스 구현
                self.display_message(
                    "Echo AI", "📝 파일 관리자에게 요청을 전달했습니다."
                )
            else:
                self.display_message("Echo AI", "❌ 파일 관리자에 접근할 수 없습니다.")

        except Exception as e:
            self.display_message("System", f"❌ 자연어 파일 관리 오류: {str(e)}")

    def handle_natural_system_control(self, request):
        """자연어 시스템 제어 요청 처리"""
        try:
            self.display_message("Echo AI", f"⚙️ 시스템 제어 요청: {request}")

            # 기본 시스템 명령들 처리
            if "감염 시작" in request or "감염 루프" in request:
                self.display_message("Echo AI", "🦠 감염 루프 시작을 요청합니다...")
                # TODO: 감염 루프 시작 구현

            elif "시그니처 생성" in request or "새 시그니처" in request:
                self.display_message("Echo AI", "🎭 새 시그니처 생성을 요청합니다...")
                # TODO: 시그니처 생성 구현

            elif "모니터링 시작" in request:
                self.display_message("Echo AI", "📊 실시간 모니터링을 시작합니다...")
                # TODO: 모니터링 시작 구현

            else:
                self.display_message(
                    "Echo AI", f"🤔 '{request}' 명령을 처리하는 방법을 학습 중입니다."
                )

        except Exception as e:
            self.display_message("System", f"❌ 자연어 시스템 제어 오류: {str(e)}")


def create_ai_assistant_ui(parent_widget, project_root: Path, ide_instance):
    """AI 어시스턴트 UI 생성"""

    assistant = EchoAIAssistant(project_root, ide_instance)
    assistant_frame = assistant.create_ai_assistant_ui(parent_widget)

    return assistant
