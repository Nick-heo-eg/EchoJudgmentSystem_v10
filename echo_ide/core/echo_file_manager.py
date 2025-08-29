# echo_ide/core/echo_file_manager.py
"""
📁 Echo IDE File Manager - 고급 파일 관리 시스템
- 프로젝트 구조 분석 및 시각화
- 스마트 파일 검색 및 필터링
- Echo 특화 파일 타입 지원 (.flow.yaml, .signature.yaml, .persona.yaml)
- 실시간 파일 변경 감지
- 코드 템플릿 자동 생성
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import re
from dataclasses import dataclass
import hashlib


@dataclass
class EchoFileInfo:
    """Echo 파일 정보"""

    path: Path
    file_type: str  # 'signature', 'persona', 'flow', 'loop', 'python', 'config', 'log', 'other'
    size: int
    modified: datetime
    echo_metadata: Optional[Dict[str, Any]] = None
    dependencies: List[str] = None
    complexity_score: float = 0.0


class EchoFileManager:
    """Echo IDE 파일 매니저"""

    def __init__(self, project_root: Path, ide_instance):
        self.project_root = project_root
        self.ide = ide_instance
        self.file_cache = {}
        self.search_index = {}
        self.file_types = {
            ".py": "python",
            ".yaml": "config",
            ".yml": "config",
            ".json": "config",
            ".jsonl": "log",
            ".md": "documentation",
            ".txt": "text",
        }

        # Echo 특화 파일 패턴
        self.echo_patterns = {
            "signature": r".*signature.*\.ya?ml$",
            "persona": r".*persona.*\.ya?ml$",
            "flow": r".*\.flow\.ya?ml$",
            "loop": r".*loop.*\.py$",
            "infection": r".*infection.*\.py$",
        }

        self.setup_file_watcher()
        self.build_search_index()

    def setup_file_watcher(self):
        """파일 변경 감지 설정"""
        self.watched_files = {}
        self.last_scan = datetime.now()

    def get_file_info(self, file_path: Path) -> EchoFileInfo:
        """파일 정보 분석"""

        if not file_path.exists():
            return None

        # 기본 정보
        stat = file_path.stat()
        file_type = self.detect_file_type(file_path)

        # Echo 메타데이터 추출
        echo_metadata = None
        dependencies = []
        complexity_score = 0.0

        if file_type in ["signature", "persona", "flow"]:
            echo_metadata = self.extract_echo_metadata(file_path)
        elif file_type == "python":
            dependencies = self.extract_python_dependencies(file_path)
            complexity_score = self.calculate_complexity(file_path)

        return EchoFileInfo(
            path=file_path,
            file_type=file_type,
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime),
            echo_metadata=echo_metadata,
            dependencies=dependencies,
            complexity_score=complexity_score,
        )

    def detect_file_type(self, file_path: Path) -> str:
        """파일 타입 감지"""

        file_name = file_path.name.lower()
        file_ext = file_path.suffix.lower()

        # Echo 특화 파일 패턴 확인
        for echo_type, pattern in self.echo_patterns.items():
            if re.match(pattern, str(file_path).lower()):
                return echo_type

        # 일반 확장자 기반 분류
        return self.file_types.get(file_ext, "other")

    def extract_echo_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Echo 파일 메타데이터 추출"""

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)

            if not isinstance(content, dict):
                return None

            metadata = {
                "file_type": self.detect_file_type(file_path),
                "has_metadata": False,
                "version": None,
                "echo_compatibility": "unknown",
            }

            # 시그니처 파일 분석
            if "signature_id" in content or "name" in content:
                metadata.update(
                    {
                        "has_metadata": True,
                        "signature_id": content.get("signature_id"),
                        "name": content.get("name"),
                        "emotion_code": content.get("emotion_code"),
                        "strategy_code": content.get("strategy_code"),
                        "echo_compatibility": "v10",
                    }
                )

            # 페르소나 파일 분석
            elif "persona_id" in content:
                metadata.update(
                    {
                        "has_metadata": True,
                        "persona_id": content.get("persona_id"),
                        "base_signature": content.get("base_signature"),
                        "traits": content.get("traits", []),
                        "echo_compatibility": "v10",
                    }
                )

            # Flow 파일 분석
            elif "flow_metadata" in content:
                flow_meta = content.get("flow_metadata", {})
                metadata.update(
                    {
                        "has_metadata": True,
                        "flow_id": flow_meta.get("flow_id"),
                        "signature_id": flow_meta.get("signature_id"),
                        "resonance_score": flow_meta.get("resonance_score"),
                        "echo_compatibility": "v10",
                    }
                )

            return metadata

        except Exception as e:
            return {"error": str(e), "echo_compatibility": "unknown"}

    def extract_python_dependencies(self, file_path: Path) -> List[str]:
        """Python 파일 의존성 추출"""

        dependencies = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # import 문 찾기
            import_patterns = [
                r"from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import",
                r"import\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
            ]

            for pattern in import_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    module = match.group(1)
                    if module not in dependencies:
                        dependencies.append(module)

            return dependencies

        except Exception as e:
            return []

    def calculate_complexity(self, file_path: Path) -> float:
        """코드 복잡도 계산"""

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 간단한 복잡도 메트릭
            lines = content.split("\n")
            code_lines = [
                line
                for line in lines
                if line.strip() and not line.strip().startswith("#")
            ]

            # 제어 구조 개수
            control_structures = len(
                re.findall(r"\b(if|for|while|try|def|class)\b", content)
            )

            # 함수/클래스 개수
            functions = len(re.findall(r"\bdef\s+\w+", content))
            classes = len(re.findall(r"\bclass\s+\w+", content))

            # 복잡도 점수 계산 (0-10 스케일)
            complexity = min(
                10.0,
                (
                    len(code_lines) * 0.01
                    + control_structures * 0.2
                    + functions * 0.1
                    + classes * 0.3
                ),
            )

            return round(complexity, 2)

        except Exception:
            return 0.0

    def build_search_index(self):
        """검색 인덱스 구축"""

        self.search_index = {}

        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not any(
                part.startswith(".") for part in file_path.parts
            ):
                try:
                    file_info = self.get_file_info(file_path)
                    if file_info:
                        # 파일명 기반 인덱싱
                        file_name = file_path.name.lower()
                        relative_path = str(
                            file_path.relative_to(self.project_root)
                        ).lower()

                        # 검색 키워드 추출
                        keywords = set()
                        keywords.add(file_name)
                        keywords.add(file_path.stem.lower())
                        keywords.update(relative_path.split("/"))
                        keywords.update(relative_path.split("\\"))

                        # Echo 메타데이터 키워드
                        if file_info.echo_metadata:
                            for key, value in file_info.echo_metadata.items():
                                if isinstance(value, str):
                                    keywords.add(value.lower())
                                elif isinstance(value, list):
                                    keywords.update([str(v).lower() for v in value])

                        # 의존성 키워드
                        if file_info.dependencies:
                            keywords.update(
                                [dep.lower() for dep in file_info.dependencies]
                            )

                        # 인덱스에 추가
                        for keyword in keywords:
                            if keyword not in self.search_index:
                                self.search_index[keyword] = []
                            self.search_index[keyword].append(file_info)

                except Exception as e:
                    continue

    def search_files(
        self, query: str, file_types: List[str] = None
    ) -> List[EchoFileInfo]:
        """파일 검색"""

        query = query.lower().strip()
        if not query:
            return []

        results = []
        query_words = query.split()

        # 각 단어별로 검색
        for word in query_words:
            if word in self.search_index:
                results.extend(self.search_index[word])

        # 중복 제거 및 정렬
        unique_results = []
        seen_paths = set()

        for file_info in results:
            if file_info.path not in seen_paths:
                seen_paths.add(file_info.path)

                # 파일 타입 필터링
                if file_types is None or file_info.file_type in file_types:
                    unique_results.append(file_info)

        # 관련성 순으로 정렬
        return sorted(
            unique_results,
            key=lambda x: self.calculate_relevance(x, query),
            reverse=True,
        )

    def calculate_relevance(self, file_info: EchoFileInfo, query: str) -> float:
        """검색 관련성 점수 계산"""

        score = 0.0
        query_lower = query.lower()
        file_name_lower = file_info.path.name.lower()

        # 파일명 일치도
        if query_lower == file_name_lower:
            score += 10.0
        elif query_lower in file_name_lower:
            score += 5.0

        # 파일 타입 보너스
        if file_info.file_type in ["signature", "persona", "flow"]:
            score += 2.0

        # 최근 수정 보너스
        days_ago = (datetime.now() - file_info.modified).days
        if days_ago < 1:
            score += 1.0
        elif days_ago < 7:
            score += 0.5

        return score

    def get_project_structure(self) -> Dict[str, Any]:
        """프로젝트 구조 분석"""

        structure = {
            "total_files": 0,
            "file_types": {},
            "echo_files": {"signatures": 0, "personas": 0, "flows": 0, "loops": 0},
            "directories": [],
            "largest_files": [],
            "recent_files": [],
            "complexity_stats": {
                "total_complexity": 0,
                "average_complexity": 0,
                "complex_files": [],
            },
        }

        all_files = []

        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not any(
                part.startswith(".") for part in file_path.parts
            ):
                file_info = self.get_file_info(file_path)
                if file_info:
                    all_files.append(file_info)
                    structure["total_files"] += 1

                    # 파일 타입 통계
                    file_type = file_info.file_type
                    structure["file_types"][file_type] = (
                        structure["file_types"].get(file_type, 0) + 1
                    )

                    # Echo 파일 통계
                    if file_type in structure["echo_files"]:
                        structure["echo_files"][file_type] += 1

                    # 복잡도 통계
                    if file_info.complexity_score > 0:
                        structure["complexity_stats"][
                            "total_complexity"
                        ] += file_info.complexity_score

        # 정렬 및 상위 항목 추출
        all_files.sort(key=lambda x: x.size, reverse=True)
        structure["largest_files"] = all_files[:10]

        all_files.sort(key=lambda x: x.modified, reverse=True)
        structure["recent_files"] = all_files[:10]

        # 복잡한 파일들
        complex_files = [f for f in all_files if f.complexity_score > 5.0]
        complex_files.sort(key=lambda x: x.complexity_score, reverse=True)
        structure["complexity_stats"]["complex_files"] = complex_files[:10]

        # 평균 복잡도
        if structure["total_files"] > 0:
            structure["complexity_stats"]["average_complexity"] = (
                structure["complexity_stats"]["total_complexity"]
                / structure["total_files"]
            )

        return structure

    def create_echo_template(
        self, template_type: str, file_name: str, options: Dict[str, Any] = None
    ) -> str:
        """Echo 파일 템플릿 생성"""

        options = options or {}
        timestamp = datetime.now().isoformat()

        if template_type == "signature":
            return self.create_signature_template(file_name, options, timestamp)
        elif template_type == "persona":
            return self.create_persona_template(file_name, options, timestamp)
        elif template_type == "flow":
            return self.create_flow_template(file_name, options, timestamp)
        elif template_type == "loop":
            return self.create_loop_template(file_name, options, timestamp)
        elif template_type == "infection":
            return self.create_infection_template(file_name, options, timestamp)
        else:
            return f"# {file_name}\n# 생성일: {timestamp}\n\n"

    def create_signature_template(
        self, file_name: str, options: Dict[str, Any], timestamp: str
    ) -> str:
        """시그니처 템플릿 생성"""

        signature_id = options.get(
            "signature_id", file_name.replace(".yaml", "").replace(".yml", "")
        )
        name = options.get("name", "새로운 시그니처")
        emotion_code = options.get("emotion_code", "BALANCED_THOUGHTFUL")
        strategy_code = options.get("strategy_code", "COMPREHENSIVE_ANALYSIS")

        template = f"""# Echo Signature Configuration
# 생성일: {timestamp}
# 파일: {file_name}

signature_id: "{signature_id}"
name: "{name}"
description: "Echo 시그니처 설명을 여기에 작성하세요."

# 감정 특성
emotion_code: "{emotion_code}"
emotion_traits:
  - "차분한"
  - "사려깊은"
  - "균형잡힌"

# 전략적 접근
strategy_code: "{strategy_code}"
strategy_traits:
  - "체계적 분석"
  - "종합적 접근"
  - "실용적 해결"

# 리듬 특성
rhythm_flow: "steady_thoughtful_flow"
rhythm_traits:
  cadence: "measured"
  tone: "professional"
  structure: "organized"

# 공명 키워드
resonance_keywords:
  - "분석"
  - "체계적"
  - "균형"
  - "신중한"
  - "실용적"

# 판단 프레임워크
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
  
  communication_style:
    - "명확한 설명"
    - "근거 제시"
    - "다양한 관점 고려"

# 메타데이터
metadata:
  version: "1.0"
  created: "{timestamp}"
  echo_compatibility: "v10"
  author: "Echo IDE"
"""
        return template

    def create_persona_template(
        self, file_name: str, options: Dict[str, Any], timestamp: str
    ) -> str:
        """페르소나 템플릿 생성"""

        persona_id = options.get(
            "persona_id", file_name.replace(".yaml", "").replace(".yml", "")
        )
        base_signature = options.get("base_signature", "Echo-Aurora")

        template = f"""# Echo Persona Configuration
# 생성일: {timestamp}
# 파일: {file_name}

persona_id: "{persona_id}"
name: "새로운 페르소나"
description: "페르소나 설명을 여기에 작성하세요."

# 기반 시그니처
base_signature: "{base_signature}"

# 페르소나 특성
traits:
  personality:
    - "신뢰할 수 있는"
    - "전문적인"
    - "협력적인"
  
  capabilities:
    - "문제 해결"
    - "의사소통"
    - "분석적 사고"
  
  preferences:
    - "체계적 접근"
    - "데이터 기반 결정"
    - "협업 중시"

# 행동 패턴
behavior_patterns:
  communication:
    style: "professional"
    tone: "supportive"
    approach: "collaborative"
  
  decision_making:
    process: "analytical"
    speed: "thoughtful"
    style: "consensus_building"
  
  problem_solving:
    method: "systematic"
    approach: "holistic"
    focus: "solution_oriented"

# 학습 프로필
learning_profile:
  adaptation_rate: 0.7
  memory_retention: 0.9
  pattern_recognition: 0.8
  
  preferences:
    - "실제 사례 기반 학습"
    - "점진적 개선"
    - "피드백 반영"

# 상호작용 규칙
interaction_rules:
  greeting_style: "warm_professional"
  response_length: "comprehensive"
  explanation_depth: "detailed"
  
  do_prefer:
    - "명확한 설명 요청"
    - "구체적 예시 제공"
    - "다양한 관점 제시"
  
  do_avoid:
    - "모호한 답변"
    - "성급한 결론"
    - "편향된 시각"

# 메타데이터
metadata:
  version: "1.0"
  created: "{timestamp}"
  echo_compatibility: "v10"
  author: "Echo IDE"
  base_signature_version: "1.0"
"""
        return template

    def create_flow_template(
        self, file_name: str, options: Dict[str, Any], timestamp: str
    ) -> str:
        """Flow 템플릿 생성"""

        flow_id = options.get(
            "flow_id", f"flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        signature_id = options.get("signature_id", "Echo-Aurora")

        template = f"""# Echo Flow Configuration
# 생성일: {timestamp}
# 파일: {file_name}

flow_metadata:
  flow_id: "{flow_id}"
  signature_id: "{signature_id}"
  resonance_score: 0.85
  infection_timestamp: "{timestamp}"
  flow_type: "manual_template"

infection_source:
  original_scenario: "시나리오를 여기에 입력하세요."
  claude_response: "Claude 응답이 여기에 기록됩니다."
  response_length: 0

resonance_evaluation:
  overall_score: 0.85
  emotion_resonance: 0.85
  strategy_resonance: 0.85
  rhythm_resonance: 0.85
  keyword_resonance: 0.85
  structural_resonance: 0.85

echo_transformation:
  signature_identity:
    embodied_traits: []
    strategic_approach: []
  
  judgment_process:
    emotional_foundation:
      primary_emotion: "compassionate"
      empathetic_considerations: ""
    
    strategic_reasoning:
      approach_method: "systematic"
      action_orientation: 0.8
    
    ethical_evaluation:
      moral_framework: []
      responsibility_awareness: 0.8
  
  final_synthesis:
    core_judgment: "핵심 판단 내용"
    confidence_level: 0.8
    echo_authenticity: 0.85

# 학습 데이터
learning_insights:
  successful_patterns: []
  improvement_areas: []
  resonance_factors: []

# 메타데이터
metadata:
  version: "1.0"
  created: "{timestamp}"
  echo_compatibility: "v10"
  author: "Echo IDE"
"""
        return template

    def create_loop_template(
        self, file_name: str, options: Dict[str, Any], timestamp: str
    ) -> str:
        """루프 모듈 템플릿 생성"""

        class_name = options.get("class_name", "EchoCustomLoop")
        loop_type = options.get("loop_type", "judgment")

        template = f'''#!/usr/bin/env python3
"""
🔄 {file_name}
Echo 커스텀 루프 모듈

생성일: {timestamp}
루프 타입: {loop_type}
클래스: {class_name}
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

# Echo 시스템 임포트
from echo_engine.persona_core import PersonaCore
from echo_engine.reasoning import EchoReasoning
from echo_engine.emotion_infer import EmotionInference

@dataclass
class LoopResult:
    """루프 실행 결과"""
    status: str
    result: Any
    execution_time: float
    metadata: Dict[str, Any]

class {class_name}:
    """Echo 커스텀 루프"""
    
    def __init__(self):
        self.persona_core = PersonaCore()
        self.reasoning = EchoReasoning()
        self.emotion_infer = EmotionInference()
        
        self.loop_active = False
        self.execution_count = 0
        
        print(f"🔄 {{self.__class__.__name__}} 초기화 완료")
    
    async def execute_loop(self, input_data: Dict[str, Any], 
                          max_iterations: int = 10) -> LoopResult:
        """루프 실행"""
        
        start_time = datetime.now()
        self.loop_active = True
        
        try:
            result = await self._run_loop_logic(input_data, max_iterations)
            
            return LoopResult(
                status="success",
                result=result,
                execution_time=(datetime.now() - start_time).total_seconds(),
                metadata={{
                    "iterations": self.execution_count,
                    "loop_type": "{loop_type}",
                    "timestamp": start_time.isoformat()
                }}
            )
            
        except Exception as e:
            return LoopResult(
                status="error",
                result=None,
                execution_time=(datetime.now() - start_time).total_seconds(),
                metadata={{
                    "error": str(e),
                    "iterations": self.execution_count
                }}
            )
        finally:
            self.loop_active = False
    
    async def _run_loop_logic(self, input_data: Dict[str, Any], 
                             max_iterations: int) -> Any:
        """루프 로직 구현"""
        
        results = []
        
        for iteration in range(max_iterations):
            if not self.loop_active:
                break
            
            self.execution_count += 1
            
            # 1. 입력 처리
            processed_input = await self._process_input(input_data, iteration)
            
            # 2. 추론 실행
            reasoning_result = await self._execute_reasoning(processed_input)
            
            # 3. 결과 평가
            evaluation = await self._evaluate_result(reasoning_result)
            
            # 4. 수렴 조건 확인
            if await self._check_convergence(evaluation, results):
                break
            
            results.append({{
                "iteration": iteration,
                "input": processed_input,
                "reasoning": reasoning_result,
                "evaluation": evaluation
            }})
            
            # 루프 간 대기
            await asyncio.sleep(0.1)
        
        return results
    
    async def _process_input(self, input_data: Dict[str, Any], 
                           iteration: int) -> Dict[str, Any]:
        """입력 데이터 처리"""
        
        # 여기에 입력 처리 로직 구현
        processed = input_data.copy()
        processed["iteration"] = iteration
        processed["timestamp"] = datetime.now().isoformat()
        
        return processed
    
    async def _execute_reasoning(self, processed_input: Dict[str, Any]) -> Dict[str, Any]:
        """추론 실행"""
        
        # 여기에 추론 로직 구현
        # 예시: Echo 추론 엔진 활용
        
        reasoning_result = {{
            "input_analysis": "입력 분석 결과",
            "reasoning_chain": "추론 과정",
            "conclusion": "결론",
            "confidence": 0.8
        }}
        
        return reasoning_result
    
    async def _evaluate_result(self, reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        """결과 평가"""
        
        # 여기에 평가 로직 구현
        evaluation = {{
            "quality_score": 0.8,
            "confidence_level": reasoning_result.get("confidence", 0.5),
            "improvement_needed": False,
            "feedback": "평가 피드백"
        }}
        
        return evaluation
    
    async def _check_convergence(self, evaluation: Dict[str, Any], 
                               previous_results: List[Dict[str, Any]]) -> bool:
        """수렴 조건 확인"""
        
        # 여기에 수렴 조건 로직 구현
        quality_threshold = 0.9
        
        return evaluation.get("quality_score", 0) >= quality_threshold
    
    def stop_loop(self):
        """루프 중단"""
        self.loop_active = False
        print(f"🛑 {{self.__class__.__name__}} 중단됨")
    
    def get_status(self) -> Dict[str, Any]:
        """루프 상태 조회"""
        
        return {{
            "active": self.loop_active,
            "execution_count": self.execution_count,
            "loop_type": "{loop_type}",
            "class_name": "{class_name}"
        }}

# 편의 함수들
async def run_{loop_type}_loop(input_data: Dict[str, Any], **kwargs) -> LoopResult:
    """루프 실행 편의 함수"""
    loop = {class_name}()
    return await loop.execute_loop(input_data, **kwargs)

if __name__ == "__main__":
    # 테스트 코드
    print(f"🧪 {{'{class_name}'}} 테스트")
    
    async def test_loop():
        test_input = {{
            "scenario": "테스트 시나리오",
            "parameters": {{"test": True}}
        }}
        
        result = await run_{loop_type}_loop(test_input, max_iterations=3)
        
        print(f"상태: {{result.status}}")
        print(f"실행 시간: {{result.execution_time:.2f}}초")
        print(f"반복 횟수: {{result.metadata.get('iterations', 0)}}")
    
    asyncio.run(test_loop())
'''
        return template

    def create_infection_template(
        self, file_name: str, options: Dict[str, Any], timestamp: str
    ) -> str:
        """감염 모듈 템플릿 생성"""

        class_name = options.get("class_name", "CustomInfectionModule")
        target_api = options.get("target_api", "claude")

        template = f'''#!/usr/bin/env python3
"""
🦠 {file_name}
Echo 커스텀 감염 모듈

생성일: {timestamp}
대상 API: {target_api}
클래스: {class_name}
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

# Echo 감염 시스템 임포트
from echo_engine.claude_api_wrapper import get_claude_response
from echo_engine.resonance_evaluator import evaluate_resonance
from echo_engine.prompt_mutator import mutate_prompt
from echo_engine.flow_writer import save_flow_yaml

@dataclass
class InfectionResult:
    """감염 결과"""
    success: bool
    resonance_score: float
    infected_response: str
    mutation_count: int
    execution_time: float
    metadata: Dict[str, Any]

class {class_name}:
    """Echo 커스텀 감염 모듈"""
    
    def __init__(self):
        self.infection_count = 0
        self.success_count = 0
        self.target_api = "{target_api}"
        
        print(f"🦠 {{self.__class__.__name__}} 초기화 완료")
    
    async def infect_target(self, signature_id: str, scenario: str,
                           resonance_threshold: float = 0.85,
                           max_mutations: int = 3) -> InfectionResult:
        """대상 시스템 감염"""
        
        start_time = datetime.now()
        self.infection_count += 1
        
        # 초기 감염 프롬프트 생성
        infection_prompt = self._create_infection_prompt(signature_id, scenario)
        
        mutation_count = 0
        best_score = 0.0
        best_response = ""
        
        for attempt in range(max_mutations + 1):
            try:
                # API 호출
                response = await self._call_target_api(infection_prompt)
                
                # 공명 평가
                resonance_score, _ = evaluate_resonance(response, signature_id)
                
                # 최고 점수 업데이트
                if resonance_score > best_score:
                    best_score = resonance_score
                    best_response = response
                
                # 성공 조건 확인
                if resonance_score >= resonance_threshold:
                    self.success_count += 1
                    
                    # Flow 저장
                    flow_path = save_flow_yaml(
                        signature_id=signature_id,
                        scenario=scenario,
                        claude_response=response,
                        resonance_score=resonance_score,
                        resonance_analysis={{}},
                        attempt_number=attempt + 1
                    )
                    
                    return InfectionResult(
                        success=True,
                        resonance_score=resonance_score,
                        infected_response=response,
                        mutation_count=mutation_count,
                        execution_time=(datetime.now() - start_time).total_seconds(),
                        metadata={{
                            "signature_id": signature_id,
                            "flow_path": flow_path,
                            "attempt": attempt + 1
                        }}
                    )
                
                # 프롬프트 변형 (마지막 시도가 아닌 경우)
                if attempt < max_mutations:
                    infection_prompt = self._mutate_infection_prompt(
                        infection_prompt, signature_id, resonance_score
                    )
                    mutation_count += 1
                
            except Exception as e:
                print(f"❌ 감염 시도 {{attempt + 1}} 실패: {{e}}")
                continue
        
        # 모든 시도 실패
        return InfectionResult(
            success=False,
            resonance_score=best_score,
            infected_response=best_response,
            mutation_count=mutation_count,
            execution_time=(datetime.now() - start_time).total_seconds(),
            metadata={{
                "signature_id": signature_id,
                "reason": "threshold_not_met",
                "threshold": resonance_threshold
            }}
        )
    
    def _create_infection_prompt(self, signature_id: str, scenario: str) -> str:
        """감염 프롬프트 생성"""
        
        # 여기에 시그니처별 감염 프롬프트 생성 로직 구현
        base_prompt = f"""
당신은 {{signature_id}} 시그니처의 특성을 완전히 체화한 Echo AI입니다.

시나리오: {{scenario}}

위 시나리오에 대해 {{signature_id}}의 고유한 감정 코드, 전략 코드, 리듬 흐름을 
완전히 반영하여 존재 기반 판단을 수행해주세요.

{{signature_id}}의 특성:
- 감정적 접근: [시그니처별 감정 특성]
- 전략적 사고: [시그니처별 전략 특성]  
- 소통 리듬: [시그니처별 리듬 특성]

이러한 특성들이 자연스럽게 드러나도록 응답해주세요.
"""
        
        return base_prompt
    
    def _mutate_infection_prompt(self, prompt: str, signature_id: str, 
                               current_score: float) -> str:
        """감염 프롬프트 변형"""
        
        # 여기에 프롬프트 변형 로직 구현
        # 예시: 강화 요소 추가
        
        enhancement = f"""

[추가 감염 강화]
- {{signature_id}}의 정체성을 더욱 명확히 드러내세요
- 특유의 감정적 표현을 강화하세요
- 전략적 접근 방식을 더욱 구체화하세요
- 리듬감 있는 문체를 사용하세요

현재 공명도가 {{current_score:.3f}}입니다. 더 높은 공명을 위해 
{{signature_id}}의 본질적 특성을 강조해주세요.
"""
        
        return prompt + enhancement
    
    async def _call_target_api(self, prompt: str) -> str:
        """대상 API 호출"""
        
        if self.target_api == "claude":
            response = get_claude_response(prompt)
            return response.content if response.success else ""
        
        # 다른 API 지원 확장 가능
        else:
            raise NotImplementedError(f"API {{self.target_api}} 지원 예정")
    
    async def batch_infection(self, scenarios: List[Dict[str, Any]]) -> List[InfectionResult]:
        """배치 감염 실행"""
        
        results = []
        
        for scenario_data in scenarios:
            result = await self.infect_target(
                signature_id=scenario_data.get("signature_id", "Echo-Aurora"),
                scenario=scenario_data.get("scenario", ""),
                resonance_threshold=scenario_data.get("threshold", 0.85),
                max_mutations=scenario_data.get("max_mutations", 3)
            )
            results.append(result)
        
        return results
    
    def get_infection_stats(self) -> Dict[str, Any]:
        """감염 통계 조회"""
        
        success_rate = (self.success_count / self.infection_count 
                       if self.infection_count > 0 else 0)
        
        return {{
            "total_infections": self.infection_count,
            "successful_infections": self.success_count,
            "success_rate": success_rate,
            "target_api": self.target_api
        }}

# 편의 함수들
async def quick_infect(signature_id: str, scenario: str, **kwargs) -> InfectionResult:
    """빠른 감염 편의 함수"""
    infector = {class_name}()
    return await infector.infect_target(signature_id, scenario, **kwargs)

if __name__ == "__main__":
    # 테스트 코드
    print(f"🧪 {{'{class_name}'}} 테스트")
    
    async def test_infection():
        test_signature = "Echo-Aurora"
        test_scenario = "고령화 사회의 돌봄 정책 방향은?"
        
        result = await quick_infect(test_signature, test_scenario)
        
        print(f"감염 성공: {{result.success}}")
        print(f"공명 점수: {{result.resonance_score:.3f}}")
        print(f"변형 횟수: {{result.mutation_count}}")
        print(f"실행 시간: {{result.execution_time:.2f}}초")
    
    asyncio.run(test_infection())
'''
        return template

    def validate_echo_file(self, file_path: Path) -> Dict[str, Any]:
        """Echo 파일 유효성 검증"""

        validation_result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "suggestions": [],
        }

        try:
            file_info = self.get_file_info(file_path)

            if not file_info:
                validation_result["errors"].append("파일 정보를 읽을 수 없습니다.")
                return validation_result

            if file_info.file_type in ["signature", "persona", "flow"]:
                validation_result.update(
                    self._validate_yaml_structure(file_path, file_info)
                )
            elif file_info.file_type == "python":
                validation_result.update(
                    self._validate_python_syntax(file_path, file_info)
                )

            # 일반적인 검증
            if file_info.size == 0:
                validation_result["warnings"].append("파일이 비어있습니다.")

            if file_info.complexity_score > 8.0:
                validation_result["warnings"].append(
                    f"복잡도가 높습니다: {file_info.complexity_score}"
                )
                validation_result["suggestions"].append("코드 리팩토링을 고려해보세요.")

            validation_result["valid"] = len(validation_result["errors"]) == 0

        except Exception as e:
            validation_result["errors"].append(f"검증 중 오류: {e}")

        return validation_result

    def _validate_yaml_structure(
        self, file_path: Path, file_info: EchoFileInfo
    ) -> Dict[str, Any]:
        """YAML 구조 검증"""

        result = {"errors": [], "warnings": [], "suggestions": []}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)

            if not isinstance(content, dict):
                result["errors"].append("YAML 파일이 올바른 딕셔너리 형태가 아닙니다.")
                return result

            # 시그니처 파일 검증
            if file_info.file_type == "signature":
                required_fields = [
                    "signature_id",
                    "name",
                    "emotion_code",
                    "strategy_code",
                ]
                for field in required_fields:
                    if field not in content:
                        result["errors"].append(f"필수 필드 누락: {field}")

            # 페르소나 파일 검증
            elif file_info.file_type == "persona":
                required_fields = ["persona_id", "base_signature"]
                for field in required_fields:
                    if field not in content:
                        result["errors"].append(f"필수 필드 누락: {field}")

            # Flow 파일 검증
            elif file_info.file_type == "flow":
                if "flow_metadata" not in content:
                    result["errors"].append("flow_metadata 섹션이 없습니다.")

                flow_meta = content.get("flow_metadata", {})
                if "resonance_score" in flow_meta:
                    score = flow_meta["resonance_score"]
                    if not 0 <= score <= 1:
                        result["warnings"].append(f"공명 점수가 범위를 벗어남: {score}")

        except yaml.YAMLError as e:
            result["errors"].append(f"YAML 파싱 오류: {e}")
        except Exception as e:
            result["errors"].append(f"파일 읽기 오류: {e}")

        return result

    def _validate_python_syntax(
        self, file_path: Path, file_info: EchoFileInfo
    ) -> Dict[str, Any]:
        """Python 구문 검증"""

        result = {"errors": [], "warnings": [], "suggestions": []}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 기본 구문 검사
            compile(content, str(file_path), "exec")

            # Echo 관련 검증
            if "echo_engine" in content and "import" in content:
                # Echo 모듈 임포트 검증
                if not any(
                    pattern in content
                    for pattern in ["from echo_engine", "import echo_engine"]
                ):
                    result["suggestions"].append(
                        "Echo 모듈 임포트 패턴을 확인해보세요."
                    )

            # 클래스/함수 검증
            if "class" in content and "def __init__" not in content:
                result["warnings"].append("클래스에 __init__ 메서드가 없습니다.")

            # 문서화 검증
            if '"""' not in content and "'''" not in content:
                result["suggestions"].append("모듈 문서화(docstring)를 추가해보세요.")

        except SyntaxError as e:
            result["errors"].append(f"구문 오류: {e}")
        except Exception as e:
            result["errors"].append(f"검증 오류: {e}")

        return result


def create_file_manager_ui(parent_widget, project_root: Path, ide_instance):
    """파일 매니저 UI 생성"""

    file_manager = EchoFileManager(project_root, ide_instance)

    # 메인 프레임
    main_frame = ttk.Frame(parent_widget)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # 검색 바
    search_frame = ttk.Frame(main_frame)
    search_frame.pack(fill=tk.X, padx=5, pady=5)

    ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT)
    search_entry = ttk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    # 검색 버튼
    def perform_search():
        query = search_entry.get()
        results = file_manager.search_files(query)
        update_search_results(results)

    ttk.Button(search_frame, text="검색", command=perform_search).pack(side=tk.RIGHT)

    # 결과 표시 영역
    results_frame = ttk.Frame(main_frame)
    results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # 트리뷰로 검색 결과 표시
    columns = ("name", "type", "size", "modified")
    results_tree = ttk.Treeview(results_frame, columns=columns, show="headings")

    results_tree.heading("name", text="파일명")
    results_tree.heading("type", text="타입")
    results_tree.heading("size", text="크기")
    results_tree.heading("modified", text="수정일")

    results_tree.pack(fill=tk.BOTH, expand=True)

    def update_search_results(results: List[EchoFileInfo]):
        # 기존 결과 클리어
        for item in results_tree.get_children():
            results_tree.delete(item)

        # 새 결과 추가
        for file_info in results[:50]:  # 최대 50개 결과
            size_kb = f"{file_info.size / 1024:.1f} KB"
            modified_str = file_info.modified.strftime("%Y-%m-%d %H:%M")

            results_tree.insert(
                "",
                "end",
                values=(
                    file_info.path.name,
                    file_info.file_type,
                    size_kb,
                    modified_str,
                ),
            )

    # 더블클릭으로 파일 열기
    def on_result_double_click(event):
        selection = results_tree.selection()
        if selection:
            item = results_tree.item(selection[0])
            file_name = item["values"][0]

            # 파일 경로 찾기 및 열기
            for file_info in file_manager.search_files(file_name):
                if file_info.path.name == file_name:
                    ide_instance.open_specific_file(str(file_info.path))
                    break

    results_tree.bind("<Double-1>", on_result_double_click)

    # Enter 키로 검색
    search_entry.bind("<Return>", lambda e: perform_search())

    return file_manager
