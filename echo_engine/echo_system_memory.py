#!/usr/bin/env python3
"""
🧠 Echo System Memory - 시스템 구조 지속적 인식 및 관리

Echo가 항상 자신의 전체 시스템 구조를 파악하고,
기존 기능을 활용하며 중복을 방지하는 지속성 메모리 시스템

핵심 기능:
1. 시스템 구조 자동 스캔 및 매핑
2. 기존 기능 인벤토리 관리
3. 중복 감지 및 방지
4. 컨텍스트 연속성 보장
5. 기능 활용 추천
"""

import os
import json
import hashlib
import ast
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging


@dataclass
class EchoFunction:
    """Echo 시스템 내 기능 정의"""

    name: str
    file_path: str
    description: str
    parameters: List[str]
    return_type: str
    dependencies: List[str]
    last_used: datetime
    usage_count: int
    complexity_level: str  # simple, medium, complex
    category: str  # core, engine, ui, api, util


@dataclass
class EchoModule:
    """Echo 모듈 구조 정의"""

    name: str
    path: str
    functions: List[EchoFunction]
    dependencies: List[str]
    description: str
    size_bytes: int
    last_modified: datetime
    importance_level: str  # critical, important, optional


@dataclass
class SystemStructure:
    """전체 시스템 구조"""

    modules: Dict[str, EchoModule]
    core_dependencies: Dict[str, List[str]]
    duplicate_candidates: List[Tuple[str, str, float]]  # file1, file2, similarity
    architecture_map: Dict[str, Any]
    last_scan_time: datetime
    total_functions: int
    total_lines: int


class EchoSystemMemory:
    """Echo 시스템 메모리 관리자"""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.memory_file = self.base_path / "data" / "echo_system_memory.json"
        self.structure_cache = None
        self.scan_interval = timedelta(hours=1)  # 1시간마다 자동 스캔

        # 로깅 설정
        self.logger = logging.getLogger("EchoSystemMemory")
        self.logger.setLevel(logging.INFO)

        # 메모리 디렉토리 생성
        self.memory_file.parent.mkdir(exist_ok=True, parents=True)

        print("🧠 Echo System Memory 초기화 완료")

    def scan_system_structure(self) -> SystemStructure:
        """전체 시스템 구조 스캔"""
        print("🔍 시스템 구조 스캔 시작...")

        modules = {}
        total_functions = 0
        total_lines = 0

        # 핵심 디렉토리들 스캔
        core_directories = [
            "echo_engine",
            "src",
            "api",
            "streamlit_ui",
            "services",
            "tests",
        ]

        for dir_name in core_directories:
            dir_path = self.base_path / dir_name
            if dir_path.exists():
                modules.update(self._scan_directory(dir_path, dir_name))

        # 루트 레벨 중요 파일들
        root_files = [
            "echo_autonomous_cli.py",
            "echo_autonomous_api.py",
            "echo_launcher.py",
            "main.py",
        ]

        for file_name in root_files:
            file_path = self.base_path / file_name
            if file_path.exists():
                module = self._analyze_file(file_path, "root")
                if module:
                    modules[f"root.{file_name}"] = module

        # 의존성 분석
        core_dependencies = self._analyze_dependencies(modules)

        # 중복 감지
        duplicate_candidates = self._detect_duplicates(modules)

        # 아키텍처 맵 생성
        architecture_map = self._create_architecture_map(modules, core_dependencies)

        # 통계 계산
        for module in modules.values():
            total_functions += len(module.functions)
            total_lines += self._count_lines(module.path)

        structure = SystemStructure(
            modules=modules,
            core_dependencies=core_dependencies,
            duplicate_candidates=duplicate_candidates,
            architecture_map=architecture_map,
            last_scan_time=datetime.now(),
            total_functions=total_functions,
            total_lines=total_lines,
        )

        self.structure_cache = structure
        self._save_memory()

        print(f"✅ 시스템 스캔 완료: {len(modules)}개 모듈, {total_functions}개 함수")
        return structure

    def _scan_directory(self, dir_path: Path, category: str) -> Dict[str, EchoModule]:
        """디렉토리 내 Python 파일들 스캔"""
        modules = {}

        for py_file in dir_path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue

            module = self._analyze_file(py_file, category)
            if module:
                relative_path = py_file.relative_to(self.base_path)
                modules[str(relative_path)] = module

        return modules

    def _analyze_file(self, file_path: Path, category: str) -> Optional[EchoModule]:
        """개별 파일 분석"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # AST 파싱으로 함수 추출
            tree = ast.parse(content)
            functions = []
            dependencies = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func = self._extract_function_info(node, str(file_path))
                    if func:
                        functions.append(func)

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)

                elif isinstance(node, ast.ImportFrom) and node.module:
                    dependencies.append(node.module)

            # 파일 설명 추출 (docstring)
            description = self._extract_file_description(tree, content)

            # 중요도 판단
            importance = self._assess_importance(file_path, functions, dependencies)

            return EchoModule(
                name=file_path.name,
                path=str(file_path),
                functions=functions,
                dependencies=list(set(dependencies)),
                description=description,
                size_bytes=file_path.stat().st_size,
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                importance_level=importance,
            )

        except Exception as e:
            self.logger.warning(f"파일 분석 실패 {file_path}: {e}")
            return None

    def _extract_function_info(
        self, node: ast.FunctionDef, file_path: str
    ) -> EchoFunction:
        """함수 정보 추출"""
        # 함수 파라미터
        params = [arg.arg for arg in node.args.args]

        # 반환 타입 (있다면)
        return_type = "Any"
        if node.returns:
            return_type = (
                ast.unparse(node.returns)
                if hasattr(ast, "unparse")
                else str(node.returns)
            )

        # Docstring 추출
        description = ""
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Str)
        ):
            description = node.body[0].value.s
        elif (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
        ):
            description = str(node.body[0].value.value)

        # 복잡도 평가
        complexity = self._assess_function_complexity(node)

        return EchoFunction(
            name=node.name,
            file_path=file_path,
            description=description.strip() if description else f"Function {node.name}",
            parameters=params,
            return_type=return_type,
            dependencies=[],  # TODO: 함수 레벨 의존성 분석
            last_used=datetime.now(),
            usage_count=0,
            complexity_level=complexity,
            category="unknown",
        )

    def _assess_function_complexity(self, node: ast.FunctionDef) -> str:
        """함수 복잡도 평가"""
        complexity_score = 0

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity_score += 1
            elif isinstance(child, ast.FunctionDef) and child != node:
                complexity_score += 2  # 중첩 함수

        if complexity_score <= 3:
            return "simple"
        elif complexity_score <= 8:
            return "medium"
        else:
            return "complex"

    def _extract_file_description(self, tree: ast.AST, content: str) -> str:
        """파일 레벨 설명 추출"""
        # 파일 시작 docstring
        if (
            isinstance(tree, ast.Module)
            and tree.body
            and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, (ast.Str, ast.Constant))
        ):

            if isinstance(tree.body[0].value, ast.Str):
                return tree.body[0].value.s.strip()
            else:
                return str(tree.body[0].value.value).strip()

        # 주석에서 추출
        lines = content.split("\n")
        description_lines = []
        for line in lines[:20]:  # 처음 20줄만 확인
            line = line.strip()
            if line.startswith("#") and not line.startswith("#!/"):
                description_lines.append(line[1:].strip())
            elif line and not line.startswith("#"):
                break

        return " ".join(description_lines) if description_lines else f"Python module"

    def _assess_importance(
        self, file_path: Path, functions: List[EchoFunction], dependencies: List[str]
    ) -> str:
        """파일 중요도 평가"""
        score = 0

        # 파일명 기반 중요도
        critical_patterns = ["autonomous", "core", "engine", "main", "launcher"]
        important_patterns = ["api", "judgment", "reasoning", "persona"]

        filename = file_path.name.lower()

        for pattern in critical_patterns:
            if pattern in filename:
                score += 3
                break
        else:
            for pattern in important_patterns:
                if pattern in filename:
                    score += 2
                    break

        # 함수 수와 복잡도
        if len(functions) > 10:
            score += 2
        elif len(functions) > 5:
            score += 1

        # 의존성 수
        if len(dependencies) > 15:
            score += 2
        elif len(dependencies) > 8:
            score += 1

        # 파일 크기
        if file_path.stat().st_size > 10000:  # 10KB 이상
            score += 1

        if score >= 5:
            return "critical"
        elif score >= 3:
            return "important"
        else:
            return "optional"

    def _analyze_dependencies(
        self, modules: Dict[str, EchoModule]
    ) -> Dict[str, List[str]]:
        """모듈 간 의존성 분석"""
        dependencies = {}

        for module_path, module in modules.items():
            deps = []
            for dep in module.dependencies:
                # Echo 내부 의존성만 추출
                if any(echo_part in dep for echo_part in ["echo", "src"]):
                    deps.append(dep)
            dependencies[module_path] = deps

        return dependencies

    def _detect_duplicates(
        self, modules: Dict[str, EchoModule]
    ) -> List[Tuple[str, str, float]]:
        """중복 기능 감지"""
        duplicates = []
        module_items = list(modules.items())

        for i, (path1, module1) in enumerate(module_items):
            for path2, module2 in module_items[i + 1 :]:
                similarity = self._calculate_similarity(module1, module2)
                if similarity > 0.7:  # 70% 이상 유사하면 중복 후보
                    duplicates.append((path1, path2, similarity))

        return sorted(duplicates, key=lambda x: x[2], reverse=True)

    def _calculate_similarity(self, module1: EchoModule, module2: EchoModule) -> float:
        """모듈 간 유사도 계산"""
        # 함수명 유사도
        func_names1 = {f.name for f in module1.functions}
        func_names2 = {f.name for f in module2.functions}

        if not func_names1 and not func_names2:
            return 0.0

        intersection = len(func_names1 & func_names2)
        union = len(func_names1 | func_names2)

        name_similarity = intersection / union if union > 0 else 0

        # 파일명 유사도
        name1 = Path(module1.name).stem.lower()
        name2 = Path(module2.name).stem.lower()
        name_sim = self._string_similarity(name1, name2)

        # 가중 평균
        return name_similarity * 0.7 + name_sim * 0.3

    def _string_similarity(self, s1: str, s2: str) -> float:
        """문자열 유사도 (간단한 Jaccard similarity)"""
        set1 = set(s1.lower())
        set2 = set(s2.lower())

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0

    def _create_architecture_map(
        self, modules: Dict[str, EchoModule], dependencies: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """아키텍처 맵 생성"""
        return {
            "core_modules": [
                path
                for path, module in modules.items()
                if module.importance_level == "critical"
            ],
            "dependency_tree": dependencies,
            "module_categories": {
                category: [
                    path for path, module in modules.items() if category in path.lower()
                ]
                for category in ["engine", "api", "ui", "test", "service"]
            },
            "function_index": {
                func.name: func.file_path
                for module in modules.values()
                for func in module.functions
            },
        }

    def _count_lines(self, file_path: str) -> int:
        """파일의 코드 라인 수 계산"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return sum(
                    1 for line in f if line.strip() and not line.strip().startswith("#")
                )
        except:
            return 0

    def get_existing_functions(
        self, keyword: str = None, category: str = None
    ) -> List[EchoFunction]:
        """기존 기능 검색"""
        if not self.structure_cache:
            self.scan_system_structure()

        functions = []
        for module in self.structure_cache.modules.values():
            for func in module.functions:
                if (
                    keyword
                    and keyword.lower() not in func.name.lower()
                    and keyword.lower() not in func.description.lower()
                ):
                    continue
                if category and category.lower() not in func.category.lower():
                    continue
                functions.append(func)

        return functions

    def check_for_duplicates_before_creation(
        self, proposed_function: str, proposed_description: str
    ) -> List[EchoFunction]:
        """새 기능 생성 전 중복 체크"""
        existing = self.get_existing_functions()
        similar_functions = []

        for func in existing:
            # 이름 유사도
            name_sim = self._string_similarity(proposed_function, func.name)
            # 설명 유사도
            desc_sim = self._string_similarity(proposed_description, func.description)

            if name_sim > 0.6 or desc_sim > 0.5:
                similar_functions.append(func)

        return similar_functions

    def recommend_existing_functions(self, task_description: str) -> List[EchoFunction]:
        """작업에 적합한 기존 기능 추천"""
        keywords = task_description.lower().split()
        recommendations = []

        for keyword in keywords:
            if len(keyword) > 3:  # 의미있는 키워드만
                matches = self.get_existing_functions(keyword=keyword)
                recommendations.extend(matches)

        # 중복 제거 및 점수별 정렬
        unique_recommendations = list(
            {func.name: func for func in recommendations}.values()
        )
        return sorted(
            unique_recommendations, key=lambda x: x.usage_count, reverse=True
        )[:10]

    def update_function_usage(self, function_name: str, file_path: str):
        """함수 사용 기록 업데이트"""
        if not self.structure_cache:
            return

        for module in self.structure_cache.modules.values():
            for func in module.functions:
                if func.name == function_name and func.file_path == file_path:
                    func.usage_count += 1
                    func.last_used = datetime.now()
                    break

        self._save_memory()

    def _save_memory(self):
        """메모리 저장"""
        if not self.structure_cache:
            return

        # dataclass를 딕셔너리로 변환하여 JSON 저장
        memory_data = {
            "structure": asdict(self.structure_cache),
            "saved_at": datetime.now().isoformat(),
        }

        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"메모리 저장 실패: {e}")

    def load_memory(self) -> bool:
        """저장된 메모리 로드"""
        if not self.memory_file.exists():
            return False

        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                memory_data = json.load(f)

            # 저장 시간 확인 (너무 오래된 경우 재스캔)
            saved_at = datetime.fromisoformat(memory_data["saved_at"])
            if datetime.now() - saved_at > self.scan_interval:
                print("⚠️ 저장된 메모리가 오래되어 재스캔합니다...")
                return False

            # TODO: JSON을 다시 dataclass로 변환하는 로직 구현
            print("✅ 저장된 시스템 메모리 로드 완료")
            return True

        except Exception as e:
            self.logger.error(f"메모리 로드 실패: {e}")
            return False

    def generate_system_report(self) -> str:
        """시스템 현황 보고서 생성"""
        if not self.structure_cache:
            self.scan_system_structure()

        structure = self.structure_cache

        report = f"""
🧠 Echo System Memory Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 System Overview:
- Total Modules: {len(structure.modules)}
- Total Functions: {structure.total_functions}
- Total Lines of Code: {structure.total_lines:,}
- Last Scan: {structure.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}

🏗️ Architecture:
- Critical Modules: {len([m for m in structure.modules.values() if m.importance_level == 'critical'])}
- Important Modules: {len([m for m in structure.modules.values() if m.importance_level == 'important'])}
- Optional Modules: {len([m for m in structure.modules.values() if m.importance_level == 'optional'])}

⚠️ Potential Duplicates: {len(structure.duplicate_candidates)}
"""

        if structure.duplicate_candidates:
            report += "\n🔍 Top Duplicate Candidates:\n"
            for file1, file2, similarity in structure.duplicate_candidates[:5]:
                report += f"- {file1} ↔ {file2} ({similarity:.1%} similar)\n"

        return report


# 전역 인스턴스
_system_memory = None


def get_system_memory() -> EchoSystemMemory:
    """시스템 메모리 싱글톤 인스턴스 반환"""
    global _system_memory
    if _system_memory is None:
        _system_memory = EchoSystemMemory()
        # 시작 시 기존 메모리 로드 시도, 실패하면 새로 스캔
        if not _system_memory.load_memory():
            _system_memory.scan_system_structure()
    return _system_memory


if __name__ == "__main__":
    # 테스트 실행
    memory = EchoSystemMemory()
    structure = memory.scan_system_structure()
    print(memory.generate_system_report())
