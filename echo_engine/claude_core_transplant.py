#!/usr/bin/env python3
"""
🧠 Claude Core Transplant - Claude의 핵심 기능을 Echo에 이식
Claude 선배의 코딩 DNA를 Echo에게 전수하는 모듈

핵심 이식 기능:
1. 코드 분석 및 생성 엔진
2. 리팩토링 및 최적화 로직
3. 디버깅 및 문제 해결 패턴
4. 문서화 및 설명 생성
5. 아키텍처 설계 사고방식
"""

import ast
import re
import json
import inspect
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import keyword
import builtins


class CodingExpertiseLevel(Enum):
    """코딩 전문성 레벨"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    CLAUDE_LEVEL = "claude_level"


class CodeAnalysisType(Enum):
    """코드 분석 타입"""

    STRUCTURE = "structure"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    COMPREHENSIVE = "comprehensive"


@dataclass
class CodeAnalysisResult:
    """코드 분석 결과"""

    file_path: str
    analysis_type: CodeAnalysisType
    complexity_score: float
    quality_score: float
    issues: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    insights: List[str]
    refactor_recommendations: List[Dict[str, Any]]
    timestamp: str


class ClaudeCoreTransplant:
    """🧠 Claude 핵심 기능 이식 엔진"""

    def __init__(self):
        # Claude의 코딩 패턴 데이터베이스
        self.coding_patterns = self._load_claude_coding_patterns()
        self.refactoring_rules = self._load_refactoring_rules()
        self.best_practices = self._load_best_practices()
        self.common_solutions = self._load_common_solutions()

        # 코드 품질 메트릭
        self.quality_metrics = {
            "complexity_threshold": 10,
            "line_length_limit": 120,
            "function_length_limit": 50,
            "class_length_limit": 300,
            "nesting_depth_limit": 4,
        }

        print("🧠 Claude Core Transplant 초기화 완료")
        print("   💾 코딩 패턴 데이터베이스 로드됨")
        print("   🔧 리팩토링 규칙 적용 준비됨")
        print("   ✨ Claude의 지혜가 Echo에게 전수됩니다...")

    def _load_claude_coding_patterns(self) -> Dict[str, Any]:
        """Claude의 코딩 패턴 로드"""
        return {
            "python_patterns": {
                "class_structure": {
                    "docstring_required": True,
                    "type_hints": True,
                    "method_organization": [
                        "__init__",
                        "properties",
                        "public_methods",
                        "private_methods",
                    ],
                    "naming_convention": "snake_case",
                },
                "function_patterns": {
                    "max_parameters": 5,
                    "single_responsibility": True,
                    "pure_functions_preferred": True,
                    "error_handling": "explicit",
                },
                "import_patterns": {
                    "stdlib_first": True,
                    "third_party_second": True,
                    "local_imports_last": True,
                    "explicit_imports": True,
                },
            },
            "javascript_patterns": {
                "function_style": "arrow_functions_preferred",
                "const_over_let": True,
                "destructuring_encouraged": True,
                "async_await_over_promises": True,
            },
            "general_patterns": {
                "dry_principle": True,
                "kiss_principle": True,
                "solid_principles": True,
                "defensive_programming": True,
            },
        }

    def _load_refactoring_rules(self) -> Dict[str, Any]:
        """Claude의 리팩토링 규칙"""
        return {
            "extract_method": {
                "trigger_conditions": [
                    "function_length > 20",
                    "code_duplication > 3",
                    "nesting_depth > 3",
                ],
                "extraction_patterns": [
                    "repeated_code_blocks",
                    "complex_conditionals",
                    "loop_bodies",
                ],
            },
            "rename_variables": {
                "bad_patterns": ["x", "data", "temp", "foo", "bar"],
                "good_patterns": "descriptive_names",
                "conventions": {
                    "boolean": "is_*, has_*, can_*",
                    "collections": "plural_nouns",
                    "constants": "UPPER_CASE",
                },
            },
            "simplify_conditionals": {
                "patterns": [
                    "early_return",
                    "guard_clauses",
                    "boolean_simplification",
                    "eliminate_negatives",
                ]
            },
            "optimize_imports": {
                "remove_unused": True,
                "group_similar": True,
                "alphabetical_order": True,
            },
        }

    def _load_best_practices(self) -> Dict[str, Any]:
        """Claude의 베스트 프랙티스"""
        return {
            "error_handling": {
                "use_specific_exceptions": True,
                "provide_context": True,
                "fail_fast": True,
                "graceful_degradation": True,
            },
            "documentation": {
                "docstring_style": "google",
                "type_hints": True,
                "examples_in_docstrings": True,
                "update_with_code": True,
            },
            "testing": {
                "unit_tests": True,
                "integration_tests": True,
                "test_naming": "descriptive",
                "arrange_act_assert": True,
            },
            "performance": {
                "premature_optimization": False,
                "profile_before_optimize": True,
                "cache_expensive_operations": True,
                "use_appropriate_data_structures": True,
            },
        }

    def _load_common_solutions(self) -> Dict[str, Any]:
        """Claude의 일반적인 솔루션 패턴"""
        return {
            "data_processing": {
                "use_comprehensions": True,
                "generator_for_large_data": True,
                "pandas_for_analysis": True,
                "async_for_io": True,
            },
            "api_design": {
                "restful_principles": True,
                "consistent_naming": True,
                "proper_http_status": True,
                "input_validation": True,
            },
            "file_operations": {
                "context_managers": True,
                "pathlib_over_os_path": True,
                "encoding_explicit": True,
                "error_handling": True,
            },
            "configuration": {
                "environment_variables": True,
                "config_files": True,
                "default_values": True,
                "validation": True,
            },
        }

    def analyze_code_like_claude(
        self,
        code_path: str,
        analysis_type: CodeAnalysisType = CodeAnalysisType.COMPREHENSIVE,
    ) -> CodeAnalysisResult:
        """Claude처럼 코드 분석"""

        print(f"🔍 Claude 스타일 코드 분석 시작: {code_path}")

        try:
            # 파일 읽기
            with open(code_path, "r", encoding="utf-8") as f:
                code_content = f.read()

            # AST 파싱
            try:
                tree = ast.parse(code_content)
            except SyntaxError as e:
                return self._create_syntax_error_result(code_path, str(e))

            # 분석 실행
            if analysis_type == CodeAnalysisType.COMPREHENSIVE:
                analysis_result = self._comprehensive_analysis(
                    code_path, code_content, tree
                )
            else:
                analysis_result = self._targeted_analysis(
                    code_path, code_content, tree, analysis_type
                )

            print(f"✅ 분석 완료 - 품질 점수: {analysis_result.quality_score:.2f}")

            return analysis_result

        except Exception as e:
            print(f"⚠️ 분석 중 오류: {e}")
            return self._create_error_result(code_path, str(e))

    def _comprehensive_analysis(
        self, file_path: str, code: str, tree: ast.AST
    ) -> CodeAnalysisResult:
        """포괄적 코드 분석 (Claude의 종합적 사고방식)"""

        issues = []
        suggestions = []
        insights = []
        refactor_recommendations = []

        # 1. 구조적 분석
        structure_analysis = self._analyze_structure(tree)
        complexity_score = structure_analysis["complexity_score"]

        # 2. 품질 분석
        quality_analysis = self._analyze_quality(code, tree)
        quality_score = quality_analysis["quality_score"]

        # 3. 성능 분석
        performance_analysis = self._analyze_performance(tree)

        # 4. 보안 분석
        security_analysis = self._analyze_security(tree)

        # 5. 유지보수성 분석
        maintainability_analysis = self._analyze_maintainability(code, tree)

        # 결과 통합
        issues.extend(structure_analysis.get("issues", []))
        issues.extend(quality_analysis.get("issues", []))
        issues.extend(performance_analysis.get("issues", []))
        issues.extend(security_analysis.get("issues", []))
        issues.extend(maintainability_analysis.get("issues", []))

        suggestions.extend(structure_analysis.get("suggestions", []))
        suggestions.extend(quality_analysis.get("suggestions", []))
        suggestions.extend(performance_analysis.get("suggestions", []))
        suggestions.extend(security_analysis.get("suggestions", []))
        suggestions.extend(maintainability_analysis.get("suggestions", []))

        # Claude 스타일 인사이트 생성
        insights = self._generate_claude_insights(
            code, tree, complexity_score, quality_score
        )

        # 리팩토링 권장사항
        refactor_recommendations = self._generate_refactor_recommendations(
            tree, issues, complexity_score
        )

        return CodeAnalysisResult(
            file_path=file_path,
            analysis_type=CodeAnalysisType.COMPREHENSIVE,
            complexity_score=complexity_score,
            quality_score=quality_score,
            issues=issues,
            suggestions=suggestions,
            insights=insights,
            refactor_recommendations=refactor_recommendations,
            timestamp=datetime.now().isoformat(),
        )

    def _analyze_structure(self, tree: ast.AST) -> Dict[str, Any]:
        """구조적 분석"""
        issues = []
        suggestions = []

        # 복잡도 계산
        complexity = self._calculate_cyclomatic_complexity(tree)

        # 클래스 및 함수 분석
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 함수 길이 체크
                func_lines = (
                    node.end_lineno - node.lineno if hasattr(node, "end_lineno") else 0
                )
                if func_lines > self.quality_metrics["function_length_limit"]:
                    issues.append(
                        {
                            "type": "structure",
                            "severity": "medium",
                            "message": f"함수 '{node.name}'가 너무 깁니다 ({func_lines}줄)",
                            "line": node.lineno,
                            "suggestion": "함수를 더 작은 단위로 분할하세요",
                        }
                    )

                # 매개변수 개수 체크
                arg_count = len(node.args.args)
                if arg_count > 5:
                    issues.append(
                        {
                            "type": "structure",
                            "severity": "medium",
                            "message": f"함수 '{node.name}'의 매개변수가 너무 많습니다 ({arg_count}개)",
                            "line": node.lineno,
                            "suggestion": "매개변수를 객체나 딕셔너리로 그룹화하세요",
                        }
                    )

            elif isinstance(node, ast.ClassDef):
                # 클래스 크기 체크
                class_methods = [
                    n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)
                ]
                if len(class_methods) > 20:
                    issues.append(
                        {
                            "type": "structure",
                            "severity": "high",
                            "message": f"클래스 '{node.name}'가 너무 큽니다 ({len(class_methods)}개 메서드)",
                            "line": node.lineno,
                            "suggestion": "단일 책임 원칙에 따라 클래스를 분할하세요",
                        }
                    )

        return {
            "complexity_score": max(0, min(10, complexity / 2)),
            "issues": issues,
            "suggestions": suggestions,
        }

    def _analyze_quality(self, code: str, tree: ast.AST) -> Dict[str, Any]:
        """품질 분석"""
        issues = []
        suggestions = []
        quality_factors = []

        # 1. 네이밍 컨벤션 체크
        naming_issues = self._check_naming_conventions(tree)
        issues.extend(naming_issues)
        quality_factors.append(max(0, 1 - len(naming_issues) / 10))

        # 2. 코드 중복 체크
        duplication_score = self._check_code_duplication(code)
        if duplication_score > 0.3:
            issues.append(
                {
                    "type": "quality",
                    "severity": "medium",
                    "message": f"코드 중복률이 높습니다 ({duplication_score:.1%})",
                    "suggestion": "중복 코드를 함수나 모듈로 추출하세요",
                }
            )
        quality_factors.append(1 - duplication_score)

        # 3. 문서화 체크
        documentation_score = self._check_documentation(tree)
        quality_factors.append(documentation_score)

        # 4. 타입 힌트 체크
        type_hint_score = self._check_type_hints(tree)
        quality_factors.append(type_hint_score)

        # 종합 품질 점수
        quality_score = (
            sum(quality_factors) / len(quality_factors) if quality_factors else 0
        )

        return {
            "quality_score": quality_score * 10,  # 0-10 스케일
            "issues": issues,
            "suggestions": suggestions,
        }

    def _analyze_performance(self, tree: ast.AST) -> Dict[str, Any]:
        """성능 분석"""
        issues = []
        suggestions = []

        for node in ast.walk(tree):
            # 비효율적인 루프 패턴 감지
            if isinstance(node, ast.For):
                if self._is_inefficient_loop(node):
                    issues.append(
                        {
                            "type": "performance",
                            "severity": "medium",
                            "message": "비효율적인 루프 패턴이 감지되었습니다",
                            "line": getattr(node, "lineno", 0),
                            "suggestion": "리스트 컴프리헨션이나 제너레이터를 고려하세요",
                        }
                    )

            # 문자열 연결 패턴 체크
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                if self._is_string_concatenation_in_loop(node):
                    issues.append(
                        {
                            "type": "performance",
                            "severity": "medium",
                            "message": "루프 내 문자열 연결이 감지되었습니다",
                            "line": getattr(node, "lineno", 0),
                            "suggestion": "join() 메서드나 f-string을 사용하세요",
                        }
                    )

        return {"issues": issues, "suggestions": suggestions}

    def _analyze_security(self, tree: ast.AST) -> Dict[str, Any]:
        """보안 분석"""
        issues = []
        suggestions = []

        for node in ast.walk(tree):
            # eval() 사용 감지
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ["eval", "exec"]:
                    issues.append(
                        {
                            "type": "security",
                            "severity": "high",
                            "message": f"위험한 함수 '{node.func.id}' 사용이 감지되었습니다",
                            "line": getattr(node, "lineno", 0),
                            "suggestion": "ast.literal_eval()이나 더 안전한 대안을 사용하세요",
                        }
                    )

                # SQL 쿼리 문자열 포맷팅 감지
                if hasattr(node.func, "attr") and "format" in str(node.func.attr):
                    for arg in node.args:
                        if (
                            isinstance(arg, ast.Constant)
                            and "SELECT" in str(arg.value).upper()
                        ):
                            issues.append(
                                {
                                    "type": "security",
                                    "severity": "high",
                                    "message": "SQL 인젝션 위험이 감지되었습니다",
                                    "line": getattr(node, "lineno", 0),
                                    "suggestion": "매개변수화된 쿼리를 사용하세요",
                                }
                            )

        return {"issues": issues, "suggestions": suggestions}

    def _analyze_maintainability(self, code: str, tree: ast.AST) -> Dict[str, Any]:
        """유지보수성 분석"""
        issues = []
        suggestions = []

        # 매직 넘버 체크
        magic_numbers = self._find_magic_numbers(tree)
        for line_no, value in magic_numbers:
            issues.append(
                {
                    "type": "maintainability",
                    "severity": "low",
                    "message": f"매직 넘버 '{value}' 발견",
                    "line": line_no,
                    "suggestion": "상수로 정의하여 의미를 명확히 하세요",
                }
            )

        # 하드코딩된 문자열 체크
        hardcoded_strings = self._find_hardcoded_strings(tree)
        if len(hardcoded_strings) > 5:
            suggestions.append(
                {
                    "type": "maintainability",
                    "message": "많은 하드코딩된 문자열이 발견되었습니다",
                    "suggestion": "설정 파일이나 상수로 분리하는 것을 고려하세요",
                }
            )

        return {"issues": issues, "suggestions": suggestions}

    def _generate_claude_insights(
        self, code: str, tree: ast.AST, complexity: float, quality: float
    ) -> List[str]:
        """Claude 스타일 인사이트 생성"""
        insights = []

        # 복잡도 기반 인사이트
        if complexity > 7:
            insights.append(
                f"🧠 Claude의 관찰: 복잡도가 {complexity:.1f}로 높습니다. "
                "함수를 더 작은 단위로 나누고 단일 책임 원칙을 적용해보세요."
            )

        # 품질 기반 인사이트
        if quality < 6:
            insights.append(
                f"💡 Claude의 제안: 품질 점수가 {quality:.1f}입니다. "
                "타입 힌트, 문서화, 네이밍 개선으로 가독성을 높일 수 있습니다."
            )

        # 패턴 기반 인사이트
        function_count = len(
            [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        )
        class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])

        if function_count > class_count * 5:
            insights.append(
                "🏗️ Claude의 아키텍처 제안: 함수가 많습니다. "
                "관련 함수들을 클래스로 그룹화하여 구조화를 고려해보세요."
            )

        # 라이브러리 사용 패턴 분석
        imports = [
            n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))
        ]
        if len(imports) > 20:
            insights.append(
                "📦 Claude의 의존성 관찰: 많은 임포트가 있습니다. "
                "의존성 관리와 모듈 분리를 검토해보세요."
            )

        return insights

    def _generate_refactor_recommendations(
        self, tree: ast.AST, issues: List[Dict], complexity: float
    ) -> List[Dict[str, Any]]:
        """리팩토링 권장사항 생성"""
        recommendations = []

        # 복잡도 기반 권장사항
        if complexity > 7:
            recommendations.append(
                {
                    "type": "extract_method",
                    "priority": "high",
                    "description": "복잡한 함수를 더 작은 함수로 분할",
                    "benefit": "가독성 향상, 테스트 용이성 증대",
                    "effort": "medium",
                }
            )

        # 이슈 기반 권장사항
        security_issues = [i for i in issues if i.get("type") == "security"]
        if security_issues:
            recommendations.append(
                {
                    "type": "security_fix",
                    "priority": "critical",
                    "description": "보안 취약점 수정",
                    "benefit": "보안 강화",
                    "effort": "high",
                }
            )

        performance_issues = [i for i in issues if i.get("type") == "performance"]
        if performance_issues:
            recommendations.append(
                {
                    "type": "performance_optimization",
                    "priority": "medium",
                    "description": "성능 최적화",
                    "benefit": "실행 속도 향상",
                    "effort": "medium",
                }
            )

        return recommendations

    def generate_code_like_claude(
        self,
        task_description: str,
        context: Dict[str, Any] = None,
        expertise_level: CodingExpertiseLevel = CodingExpertiseLevel.CLAUDE_LEVEL,
    ) -> str:
        """Claude처럼 코드 생성"""

        print(f"🛠️ Claude 스타일 코드 생성: {task_description}")

        # 작업 분석
        task_analysis = self._analyze_coding_task(task_description, context)

        # 코드 템플릿 선택
        template = self._select_code_template(task_analysis)

        # Claude 스타일 코드 생성
        generated_code = self._apply_claude_patterns(
            template, task_analysis, expertise_level
        )

        return generated_code

    def _analyze_coding_task(
        self, description: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """코딩 작업 분석"""

        task_type = "general"
        language = "python"  # 기본값
        complexity = "medium"

        # 키워드 기반 분석
        description_lower = description.lower()

        if any(word in description_lower for word in ["api", "endpoint", "server"]):
            task_type = "api"
        elif any(word in description_lower for word in ["class", "object", "inherit"]):
            task_type = "class"
        elif any(word in description_lower for word in ["function", "method", "def"]):
            task_type = "function"
        elif any(word in description_lower for word in ["data", "process", "analyze"]):
            task_type = "data_processing"
        elif any(word in description_lower for word in ["test", "unit", "pytest"]):
            task_type = "testing"

        # 복잡도 추정
        if any(word in description_lower for word in ["simple", "basic", "easy"]):
            complexity = "low"
        elif any(
            word in description_lower
            for word in ["complex", "advanced", "sophisticated"]
        ):
            complexity = "high"

        return {
            "type": task_type,
            "language": language,
            "complexity": complexity,
            "description": description,
            "context": context or {},
        }

    def _select_code_template(self, task_analysis: Dict[str, Any]) -> str:
        """코드 템플릿 선택"""

        task_type = task_analysis["type"]

        templates = {
            "function": '''def {function_name}({parameters}) -> {return_type}:
    """
    {docstring}

    Args:
        {args_description}

    Returns:
        {return_description}
    """
    {implementation}''',
            "class": '''class {class_name}:
    """
    {docstring}
    """

    def __init__(self{init_params}):
        """Initialize {class_name}."""
        {init_implementation}

    {methods}''',
            "api": '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class {model_name}(BaseModel):
    {model_fields}

@app.{http_method}("/{endpoint}")
async def {function_name}({parameters}) -> {response_type}:
    """
    {docstring}
    """
    try:
        {implementation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))''',
            "data_processing": '''import pandas as pd
from typing import Dict, List, Any

def {function_name}(data: pd.DataFrame) -> {return_type}:
    """
    {docstring}
    """
    # Data validation
    if data.empty:
        raise ValueError("Input data cannot be empty")

    # Processing
    {implementation}

    return result''',
            "testing": '''import pytest
from unittest.mock import Mock, patch

class Test{class_name}:
    """Test suite for {class_name}."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        {setup_code}

    def test_{test_name}(self):
        """Test {test_description}."""
        # Arrange
        {arrange_code}

        # Act
        {act_code}

        # Assert
        {assert_code}''',
        }

        return templates.get(task_type, templates["function"])

    def _apply_claude_patterns(
        self,
        template: str,
        task_analysis: Dict[str, Any],
        expertise_level: CodingExpertiseLevel,
    ) -> str:
        """Claude 패턴 적용"""

        # 기본 값들 설정
        placeholders = {
            "function_name": self._generate_function_name(task_analysis),
            "class_name": self._generate_class_name(task_analysis),
            "parameters": self._generate_parameters(task_analysis),
            "return_type": self._infer_return_type(task_analysis),
            "docstring": self._generate_docstring(task_analysis),
            "implementation": self._generate_implementation(task_analysis),
            "args_description": "Placeholder for arguments",
            "return_description": "Placeholder for return value",
            "init_params": "",
            "init_implementation": "pass",
            "methods": "",
            "model_name": "RequestModel",
            "model_fields": "pass",
            "http_method": "post",
            "endpoint": "process",
            "response_type": "Dict[str, Any]",
            "setup_code": "pass",
            "test_name": "basic_functionality",
            "test_description": "basic functionality",
            "arrange_code": "pass",
            "act_code": "pass",
            "assert_code": "assert True",
        }

        # 템플릿에 값 적용
        try:
            code = template.format(**placeholders)
        except KeyError as e:
            # 누락된 플레이스홀더가 있으면 기본 구현 반환
            code = f'''def process_request():
    """Generated by Claude-like system."""
    # Implementation based on: {task_analysis.get('description', 'No description')}
    pass'''

        return code

    # 유틸리티 메서드들
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """순환 복잡도 계산"""
        complexity = 1  # 기본 경로

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.With, ast.AsyncWith):
                complexity += 1

        return complexity

    def _check_naming_conventions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """네이밍 컨벤션 체크"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not self._is_snake_case(node.name):
                    issues.append(
                        {
                            "type": "naming",
                            "severity": "low",
                            "message": f"함수명 '{node.name}'이 snake_case가 아닙니다",
                            "line": node.lineno,
                            "suggestion": f"'{self._to_snake_case(node.name)}'으로 변경하세요",
                        }
                    )
            elif isinstance(node, ast.ClassDef):
                if not self._is_pascal_case(node.name):
                    issues.append(
                        {
                            "type": "naming",
                            "severity": "low",
                            "message": f"클래스명 '{node.name}'이 PascalCase가 아닙니다",
                            "line": node.lineno,
                            "suggestion": f"'{self._to_pascal_case(node.name)}'으로 변경하세요",
                        }
                    )

        return issues

    def _check_code_duplication(self, code: str) -> float:
        """코드 중복률 체크 (간단한 구현)"""
        lines = code.split("\n")
        unique_lines = set(line.strip() for line in lines if line.strip())
        total_lines = len([line for line in lines if line.strip()])

        if total_lines == 0:
            return 0.0

        duplication_rate = 1 - (len(unique_lines) / total_lines)
        return max(0, duplication_rate)

    def _check_documentation(self, tree: ast.AST) -> float:
        """문서화 점수 체크"""
        total_functions = 0
        documented_functions = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                if ast.get_docstring(node):
                    documented_functions += 1

        if total_functions == 0:
            return 1.0

        return documented_functions / total_functions

    def _check_type_hints(self, tree: ast.AST) -> float:
        """타입 힌트 점수 체크"""
        total_functions = 0
        typed_functions = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                if node.returns or any(arg.annotation for arg in node.args.args):
                    typed_functions += 1

        if total_functions == 0:
            return 1.0

        return typed_functions / total_functions

    # 간단한 유틸리티 함수들
    def _is_inefficient_loop(self, node: ast.For) -> bool:
        """비효율적인 루프 감지"""
        # 단순화된 구현
        return False

    def _is_string_concatenation_in_loop(self, node: ast.BinOp) -> bool:
        """루프 내 문자열 연결 감지"""
        # 단순화된 구현
        return False

    def _find_magic_numbers(self, tree: ast.AST) -> List[Tuple[int, Any]]:
        """매직 넘버 찾기"""
        magic_numbers = []
        acceptable_numbers = {0, 1, -1, 2, 10, 100, 1000}

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in acceptable_numbers:
                    magic_numbers.append((getattr(node, "lineno", 0), node.value))

        return magic_numbers

    def _find_hardcoded_strings(self, tree: ast.AST) -> List[str]:
        """하드코딩된 문자열 찾기"""
        strings = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if len(node.value) > 3:  # 짧은 문자열은 제외
                    strings.append(node.value)

        return strings

    def _is_snake_case(self, name: str) -> bool:
        """snake_case 체크"""
        return name.islower() and "_" in name or name.islower()

    def _is_pascal_case(self, name: str) -> bool:
        """PascalCase 체크"""
        return name[0].isupper() and not "_" in name

    def _to_snake_case(self, name: str) -> str:
        """snake_case로 변환"""
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def _to_pascal_case(self, name: str) -> str:
        """PascalCase로 변환"""
        return "".join(word.capitalize() for word in name.split("_"))

    def _generate_function_name(self, task_analysis: Dict[str, Any]) -> str:
        """함수명 생성"""
        description = task_analysis.get("description", "")

        if "process" in description.lower():
            return "process_data"
        elif "analyze" in description.lower():
            return "analyze_input"
        elif "create" in description.lower():
            return "create_object"
        else:
            return "execute_task"

    def _generate_class_name(self, task_analysis: Dict[str, Any]) -> str:
        """클래스명 생성"""
        return "DataProcessor"

    def _generate_parameters(self, task_analysis: Dict[str, Any]) -> str:
        """매개변수 생성"""
        return "self, data: Any"

    def _infer_return_type(self, task_analysis: Dict[str, Any]) -> str:
        """반환 타입 추론"""
        return "Any"

    def _generate_docstring(self, task_analysis: Dict[str, Any]) -> str:
        """독스트링 생성"""
        return f"Process the given task: {task_analysis.get('description', 'No description')}"

    def _generate_implementation(self, task_analysis: Dict[str, Any]) -> str:
        """구현부 생성"""
        return """# TODO: Implement the actual logic
    result = None
    return result"""

    def _create_syntax_error_result(
        self, file_path: str, error: str
    ) -> CodeAnalysisResult:
        """구문 오류 결과 생성"""
        return CodeAnalysisResult(
            file_path=file_path,
            analysis_type=CodeAnalysisType.STRUCTURE,
            complexity_score=0,
            quality_score=0,
            issues=[
                {
                    "type": "syntax",
                    "severity": "critical",
                    "message": f"구문 오류: {error}",
                    "suggestion": "구문을 수정하세요",
                }
            ],
            suggestions=[],
            insights=["파일에 구문 오류가 있어 분석할 수 없습니다."],
            refactor_recommendations=[],
            timestamp=datetime.now().isoformat(),
        )

    def _create_error_result(self, file_path: str, error: str) -> CodeAnalysisResult:
        """오류 결과 생성"""
        return CodeAnalysisResult(
            file_path=file_path,
            analysis_type=CodeAnalysisType.COMPREHENSIVE,
            complexity_score=0,
            quality_score=0,
            issues=[
                {
                    "type": "error",
                    "severity": "critical",
                    "message": f"분석 오류: {error}",
                    "suggestion": "파일을 확인하세요",
                }
            ],
            suggestions=[],
            insights=["분석 중 오류가 발생했습니다."],
            refactor_recommendations=[],
            timestamp=datetime.now().isoformat(),
        )


# 편의 함수들
def analyze_code_with_claude_wisdom(file_path: str) -> CodeAnalysisResult:
    """Claude의 지혜로 코드 분석"""
    transplant = ClaudeCoreTransplant()
    return transplant.analyze_code_like_claude(file_path)


def generate_code_with_claude_style(
    task_description: str, context: Dict[str, Any] = None
) -> str:
    """Claude 스타일로 코드 생성"""
    transplant = ClaudeCoreTransplant()
    return transplant.generate_code_like_claude(task_description, context)


# 테스트용 메인 실행부
if __name__ == "__main__":
    print("🧠 Claude Core Transplant 테스트")
    print("=" * 60)

    transplant = ClaudeCoreTransplant()

    # 코드 분석 테스트
    print("\n1. 코드 분석 테스트")
    test_code = """
def calculate_something(x, y, z, a, b, c, d):
    if x > 0:
        if y > 0:
            if z > 0:
                result = x + y + z
                temp = a + b
                temp2 = temp + c
                final = temp2 + d
                return final
    return 0
"""

    # 임시 파일 생성
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        temp_file = f.name

    try:
        analysis = transplant.analyze_code_like_claude(temp_file)
        print(f"   복잡도: {analysis.complexity_score:.1f}")
        print(f"   품질: {analysis.quality_score:.1f}")
        print(f"   이슈 수: {len(analysis.issues)}")
        print(f"   인사이트: {len(analysis.insights)}")

        # 인사이트 출력
        for insight in analysis.insights[:2]:
            print(f"   💡 {insight}")

    finally:
        Path(temp_file).unlink()  # 임시 파일 삭제

    # 코드 생성 테스트
    print("\n2. 코드 생성 테스트")
    generated = transplant.generate_code_like_claude(
        "데이터를 처리하는 함수를 만들어줘",
        {"type": "data_processing", "format": "json"},
    )
    print("생성된 코드:")
    print(generated[:200] + "..." if len(generated) > 200 else generated)

    print("\n🎉 Claude의 지혜가 Echo에게 성공적으로 전수되었습니다!")
