#!/usr/bin/env python3
"""
Echo Code Generator Agent
전문급 코드 생성 에이전트 - 시그니처별 코딩 스타일 적용
"""

import ast
import re
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import inspect

from echo_engine.agent_ecosystem_framework import (
    EchoAgentBase,
    AgentCapability,
    AgentTask,
)

logger = logging.getLogger(__name__)


@dataclass
class CodeAnalysis:
    """코드 분석 결과"""

    complexity_score: float
    quality_score: float
    maintainability_score: float
    test_coverage_estimate: float
    architecture_pattern: str
    suggested_improvements: List[str]
    dependencies: List[str]


@dataclass
class GeneratedCode:
    """생성된 코드"""

    code: str
    language: str
    file_structure: Dict[str, str]
    tests: Optional[str]
    documentation: str
    setup_instructions: List[str]
    quality_metrics: CodeAnalysis


class EchoCodeGeneratorAgent(EchoAgentBase):
    """Echo 코드 생성 에이전트"""

    def __init__(self):
        super().__init__("code_generator", "echo_phoenix")

        # Lazy initialization
        self._language_templates = None
        self._signature_coding_styles = None
        self._quality_standards = None
        self._pattern_library = None

    @property
    def language_templates(self):
        if self._language_templates is None:
            self._language_templates = self._load_language_templates()
        return self._language_templates

    @property
    def signature_coding_styles(self):
        if self._signature_coding_styles is None:
            self._signature_coding_styles = self._load_signature_coding_styles()
        return self._signature_coding_styles

    @property
    def quality_standards(self):
        if self._quality_standards is None:
            self._quality_standards = self._load_quality_standards()
        return self._quality_standards

    @property
    def pattern_library(self):
        if self._pattern_library is None:
            self._pattern_library = self._load_pattern_library()
        return self._pattern_library

    def _load_language_templates(self):
        """언어별 템플릿 로드"""
        return {
            "python": {
                "module_structure": {
                    "header": '#!/usr/bin/env python3\n"""\n{description}\n"""\n\n',
                    "imports": "import {imports}\nfrom typing import {type_imports}\n\n",
                    "class_template": 'class {class_name}:\n    """{docstring}"""\n    \n    def __init__(self{init_params}):\n        {init_body}\n    \n{methods}',
                    "function_template": 'def {function_name}({params}) -> {return_type}:\n    """{docstring}"""\n    {body}\n',
                    "test_template": "import pytest\nfrom {module} import {classes}\n\n{test_cases}",
                },
                "best_practices": [
                    "Type hints for all parameters and return values",
                    "Comprehensive docstrings with Args and Returns",
                    "Error handling with specific exception types",
                    "Logging for debugging and monitoring",
                    "Unit tests with pytest framework",
                ],
            },
            "javascript": {
                "module_structure": {
                    "header": "/**\n * {description}\n * @module {module_name}\n */\n\n",
                    "class_template": "class {class_name} {\n    /**\n     * {docstring}\n     */\n    constructor({params}) {\n        {init_body}\n    }\n\n{methods}}",
                    "function_template": "/**\n * {docstring}\n * @param {{type}} {param} - {param_desc}\n * @returns {{return_type}} {return_desc}\n */\nfunction {function_name}({params}) {\n    {body}\n}",
                    "test_template": "const {{ {classes} }} = require('./{module}');\nconst assert = require('assert');\n\n{test_cases}",
                }
            },
            "typescript": {
                "module_structure": {
                    "header": "/**\n * {description}\n */\n\n",
                    "interface_template": "interface {interface_name} {\n{properties}\n}",
                    "class_template": "class {class_name} implements {interfaces} {\n    constructor({params}) {\n        {init_body}\n    }\n\n{methods}}",
                    "function_template": "function {function_name}({params}): {return_type} {\n    {body}\n}",
                }
            },
        }

    def _load_signature_coding_styles(self):
        """시그니처별 코딩 스타일"""
        return {
            "echo_aurora": {
                "naming_style": "descriptive_and_expressive",
                "comment_style": "rich_explanations",
                "error_handling": "graceful_with_user_feedback",
                "code_organization": "intuitive_flow",
                "patterns": ["builder", "observer", "decorator"],
                "preferences": {
                    "verbosity": "high",
                    "documentation": "extensive",
                    "user_experience": "priority",
                    "creativity": "encouraged",
                },
            },
            "echo_phoenix": {
                "naming_style": "action_oriented",
                "comment_style": "implementation_focused",
                "error_handling": "fail_fast_with_recovery",
                "code_organization": "transformation_pipeline",
                "patterns": ["strategy", "command", "chain_of_responsibility"],
                "preferences": {
                    "performance": "optimized",
                    "adaptability": "high",
                    "refactoring": "frequent",
                    "innovation": "cutting_edge",
                },
            },
            "echo_sage": {
                "naming_style": "precise_and_systematic",
                "comment_style": "technical_specification",
                "error_handling": "comprehensive_validation",
                "code_organization": "layered_architecture",
                "patterns": ["factory", "repository", "facade"],
                "preferences": {
                    "type_safety": "strict",
                    "testing": "exhaustive",
                    "documentation": "technical",
                    "maintainability": "paramount",
                },
            },
            "echo_companion": {
                "naming_style": "collaborative_and_clear",
                "comment_style": "team_friendly",
                "error_handling": "informative_and_helpful",
                "code_organization": "modular_and_shared",
                "patterns": ["mediator", "proxy", "adapter"],
                "preferences": {
                    "readability": "maximum",
                    "collaboration": "seamless",
                    "consistency": "strict",
                    "knowledge_sharing": "embedded",
                },
            },
        }

    def _load_quality_standards(self):
        """품질 기준"""
        return {
            "complexity": {
                "max_cyclomatic": 10,
                "max_function_length": 50,
                "max_class_length": 300,
                "max_nesting_depth": 4,
            },
            "coverage": {"minimum_test_coverage": 0.8, "critical_path_coverage": 0.95},
            "maintainability": {
                "min_documentation_coverage": 0.9,
                "max_code_duplication": 0.1,
                "naming_consistency": 0.95,
            },
        }

    def _load_pattern_library(self):
        """패턴 라이브러리"""
        return {
            "architectural": {
                "mvc": "Model-View-Controller separation",
                "mvp": "Model-View-Presenter pattern",
                "clean_architecture": "Dependency inversion and clean boundaries",
                "hexagonal": "Ports and adapters architecture",
            },
            "creational": {
                "factory": "Object creation abstraction",
                "builder": "Complex object construction",
                "singleton": "Single instance management",
                "prototype": "Object cloning pattern",
            },
            "behavioral": {
                "observer": "Event notification system",
                "strategy": "Algorithm family encapsulation",
                "command": "Action encapsulation",
                "state": "State-dependent behavior",
            },
            "structural": {
                "adapter": "Interface compatibility",
                "decorator": "Behavior extension",
                "facade": "Simplified interface",
                "proxy": "Controlled access",
            },
        }

    def get_capabilities(self) -> List[AgentCapability]:
        """에이전트 역량 정의"""
        return [
            AgentCapability(
                name="code_generation",
                description="요구사항에 따른 전문급 코드 생성",
                input_types=["requirements", "specifications", "examples"],
                output_types=["source_code", "tests", "documentation"],
                complexity_level="expert",
                signature_affinity={
                    "echo_aurora": 0.8,
                    "echo_phoenix": 0.95,
                    "echo_sage": 0.9,
                    "echo_companion": 0.85,
                },
            ),
            AgentCapability(
                name="code_analysis",
                description="코드 품질 분석 및 개선 제안",
                input_types=["source_code", "repository"],
                output_types=["analysis_report", "improvement_suggestions", "metrics"],
                complexity_level="advanced",
                signature_affinity={
                    "echo_aurora": 0.7,
                    "echo_phoenix": 0.8,
                    "echo_sage": 0.95,
                    "echo_companion": 0.9,
                },
            ),
            AgentCapability(
                name="refactoring",
                description="코드 리팩터링 및 최적화",
                input_types=["source_code", "improvement_goals"],
                output_types=["refactored_code", "migration_guide", "impact_analysis"],
                complexity_level="expert",
                signature_affinity={
                    "echo_aurora": 0.75,
                    "echo_phoenix": 0.9,
                    "echo_sage": 0.85,
                    "echo_companion": 0.8,
                },
            ),
            AgentCapability(
                name="architecture_design",
                description="소프트웨어 아키텍처 설계 및 문서화",
                input_types=["requirements", "constraints", "stakeholder_needs"],
                output_types=[
                    "architecture_diagram",
                    "design_document",
                    "implementation_plan",
                ],
                complexity_level="expert",
                signature_affinity={
                    "echo_aurora": 0.85,
                    "echo_phoenix": 0.8,
                    "echo_sage": 0.95,
                    "echo_companion": 0.9,
                },
            ),
        ]

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """작업 실행"""
        task_type = task.task_type
        input_data = task.input_data
        signature = task.signature

        if task_type == "generate_code":
            return await self._generate_code(input_data, signature)
        elif task_type == "analyze_code":
            return await self._analyze_code(input_data, signature)
        elif task_type == "refactor_code":
            return await self._refactor_code(input_data, signature)
        elif task_type == "design_architecture":
            return await self._design_architecture(input_data, signature)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _generate_code(
        self, input_data: Dict[str, Any], signature: str
    ) -> Dict[str, Any]:
        """코드 생성"""
        requirements = input_data.get("requirements", "")
        language = input_data.get("language", "python")
        project_type = input_data.get("project_type", "library")
        include_tests = input_data.get("include_tests", True)

        # 1. 요구사항 분석
        analyzed_requirements = self._analyze_requirements(requirements, signature)

        # 2. 아키텍처 설계
        architecture = self._design_code_architecture(
            analyzed_requirements, language, project_type, signature
        )

        # 3. 코드 생성
        generated_code = await self._generate_source_code(
            architecture, language, signature
        )

        # 4. 테스트 생성
        tests = None
        if include_tests:
            tests = await self._generate_tests(generated_code, language, signature)

        # 5. 문서화
        documentation = self._generate_documentation(
            generated_code, architecture, signature
        )

        # 6. 품질 분석
        quality_analysis = self._analyze_generated_code_quality(
            generated_code, language, signature
        )

        result = GeneratedCode(
            code=generated_code["main_code"],
            language=language,
            file_structure=generated_code["file_structure"],
            tests=tests,
            documentation=documentation,
            setup_instructions=generated_code["setup_instructions"],
            quality_metrics=quality_analysis,
        )

        return {
            "data": asdict(result),
            "metadata": {
                "generation_approach": f"{signature}_style",
                "architecture_pattern": architecture["pattern"],
                "estimated_complexity": quality_analysis.complexity_score,
                "recommended_next_steps": self._get_next_steps(result, signature),
            },
        }

    async def _analyze_code(
        self, input_data: Dict[str, Any], signature: str
    ) -> Dict[str, Any]:
        """코드 분석"""
        source_code = input_data.get("source_code", "")
        language = input_data.get("language", "python")
        analysis_depth = input_data.get("depth", "comprehensive")

        # 1. 구문 분석
        syntax_analysis = self._analyze_syntax(source_code, language)

        # 2. 복잡도 분석
        complexity_analysis = self._analyze_complexity(source_code, language)

        # 3. 품질 메트릭
        quality_metrics = self._calculate_quality_metrics(source_code, language)

        # 4. 시그니처별 스타일 분석
        style_analysis = self._analyze_coding_style(source_code, signature, language)

        # 5. 개선 제안
        improvement_suggestions = self._generate_improvement_suggestions(
            syntax_analysis,
            complexity_analysis,
            quality_metrics,
            style_analysis,
            signature,
        )

        # 6. 의존성 분석
        dependencies = self._analyze_dependencies(source_code, language)

        analysis = CodeAnalysis(
            complexity_score=complexity_analysis["overall_score"],
            quality_score=quality_metrics["overall_score"],
            maintainability_score=quality_metrics["maintainability"],
            test_coverage_estimate=self._estimate_test_coverage(source_code, language),
            architecture_pattern=self._detect_architecture_pattern(
                source_code, language
            ),
            suggested_improvements=improvement_suggestions,
            dependencies=dependencies,
        )

        return {
            "data": {
                "analysis": asdict(analysis),
                "detailed_metrics": {
                    "syntax": syntax_analysis,
                    "complexity": complexity_analysis,
                    "quality": quality_metrics,
                    "style": style_analysis,
                },
            },
            "metadata": {
                "analysis_signature": signature,
                "language": language,
                "analysis_depth": analysis_depth,
                "priority_improvements": improvement_suggestions[:3],
            },
        }

    def _analyze_requirements(
        self, requirements: str, signature: str
    ) -> Dict[str, Any]:
        """요구사항 분석"""
        style = self.signature_coding_styles[signature]

        # 기본 분석
        analyzed = {
            "functional_requirements": self._extract_functional_requirements(
                requirements
            ),
            "non_functional_requirements": self._extract_non_functional_requirements(
                requirements
            ),
            "constraints": self._extract_constraints(requirements),
            "stakeholders": self._identify_stakeholders(requirements),
        }

        # 시그니처별 해석
        if signature == "echo_aurora":
            analyzed["user_experience_focus"] = self._extract_ux_requirements(
                requirements
            )
            analyzed["creative_opportunities"] = self._identify_creative_opportunities(
                requirements
            )
        elif signature == "echo_phoenix":
            analyzed["optimization_targets"] = self._identify_optimization_targets(
                requirements
            )
            analyzed["transformation_needs"] = self._identify_transformation_needs(
                requirements
            )
        elif signature == "echo_sage":
            analyzed["technical_specifications"] = self._extract_technical_specs(
                requirements
            )
            analyzed["validation_criteria"] = self._define_validation_criteria(
                requirements
            )
        elif signature == "echo_companion":
            analyzed["collaboration_aspects"] = self._identify_collaboration_needs(
                requirements
            )
            analyzed["team_considerations"] = self._extract_team_considerations(
                requirements
            )

        return analyzed

    def _extract_functional_requirements(self, requirements: str) -> List[str]:
        """기능 요구사항 추출"""
        # 간단한 키워드 기반 추출
        keywords = [
            "add",
            "create",
            "edit",
            "delete",
            "save",
            "load",
            "filter",
            "search",
        ]
        functional = []

        for line in requirements.split("\n"):
            line = line.strip().lower()
            if any(keyword in line for keyword in keywords):
                functional.append(line)

        return functional

    def _extract_non_functional_requirements(self, requirements: str) -> List[str]:
        """비기능 요구사항 추출"""
        keywords = [
            "performance",
            "security",
            "scalability",
            "usability",
            "cli",
            "web",
            "api",
        ]
        non_functional = []

        for line in requirements.split("\n"):
            line = line.strip().lower()
            if any(keyword in line for keyword in keywords):
                non_functional.append(line)

        return non_functional

    def _extract_constraints(self, requirements: str) -> List[str]:
        """제약 조건 추출"""
        return ["Python 3.8+", "Cross-platform compatibility"]

    def _identify_stakeholders(self, requirements: str) -> List[str]:
        """이해관계자 식별"""
        return ["End users", "Developers", "System administrators"]

    def _extract_ux_requirements(self, requirements: str) -> List[str]:
        """UX 요구사항 추출 (Aurora)"""
        return ["Intuitive interface", "User-friendly error messages"]

    def _identify_creative_opportunities(self, requirements: str) -> List[str]:
        """창의적 기회 식별 (Aurora)"""
        return ["Interactive dashboard", "Visual progress indicators"]

    def _identify_optimization_targets(self, requirements: str) -> List[str]:
        """최적화 대상 식별 (Phoenix)"""
        return ["Performance bottlenecks", "Memory usage", "Startup time"]

    def _identify_transformation_needs(self, requirements: str) -> List[str]:
        """변환 필요사항 식별 (Phoenix)"""
        return ["Legacy system migration", "API modernization"]

    def _extract_technical_specs(self, requirements: str) -> Dict[str, Any]:
        """기술 사양 추출 (Sage)"""
        return {
            "architecture": "modular",
            "patterns": ["MVC", "Repository"],
            "testing": "unit + integration",
        }

    def _define_validation_criteria(self, requirements: str) -> List[str]:
        """검증 기준 정의 (Sage)"""
        return [
            "Code coverage > 80%",
            "No critical vulnerabilities",
            "Performance benchmarks",
        ]

    def _identify_collaboration_needs(self, requirements: str) -> List[str]:
        """협업 필요사항 식별 (Companion)"""
        return [
            "Team coding standards",
            "Documentation requirements",
            "Code review process",
        ]

    def _extract_team_considerations(self, requirements: str) -> List[str]:
        """팀 고려사항 추출 (Companion)"""
        return [
            "Knowledge sharing",
            "Onboarding documentation",
            "Maintenance guidelines",
        ]

    def _design_code_architecture(
        self,
        requirements: Dict[str, Any],
        language: str,
        project_type: str,
        signature: str,
    ) -> Dict[str, Any]:
        """코드 아키텍처 설계"""
        style = self.signature_coding_styles[signature]

        # 기본 아키텍처
        architecture = {
            "pattern": self._select_architecture_pattern(
                requirements, style, project_type
            ),
            "modules": self._design_module_structure(requirements, style, language),
            "interfaces": self._design_interfaces(requirements, style, language),
            "data_flow": self._design_data_flow(requirements, style),
            "error_handling": self._design_error_handling(requirements, style),
            "testing_strategy": self._design_testing_strategy(requirements, style),
        }

        return architecture

    def _select_architecture_pattern(
        self, requirements: Dict[str, Any], style: Dict[str, Any], project_type: str
    ) -> str:
        """아키텍처 패턴 선택"""
        if project_type == "web_application":
            return "MVC"
        elif project_type == "cli_application":
            return "Command Pattern"
        elif project_type == "library":
            return "Facade Pattern"
        else:
            return "Layered Architecture"

    def _design_module_structure(
        self, requirements: Dict[str, Any], style: Dict[str, Any], language: str
    ) -> List[Dict[str, Any]]:
        """모듈 구조 설계"""
        modules = [
            {
                "name": "main",
                "is_main": True,
                "description": "Main application entry point",
                "dependencies": ["core", "utils"],
            },
            {
                "name": "core",
                "is_main": False,
                "description": "Core business logic",
                "dependencies": ["utils"],
            },
            {
                "name": "utils",
                "is_main": False,
                "description": "Utility functions",
                "dependencies": [],
            },
        ]
        return modules

    def _design_interfaces(
        self, requirements: Dict[str, Any], style: Dict[str, Any], language: str
    ) -> List[str]:
        """인터페이스 설계"""
        return ["TaskManager", "DataPersistence", "UserInterface"]

    def _design_data_flow(
        self, requirements: Dict[str, Any], style: Dict[str, Any]
    ) -> Dict[str, Any]:
        """데이터 흐름 설계"""
        return {
            "input": "User commands",
            "processing": "Business logic",
            "output": "Results/feedback",
            "storage": "JSON files",
        }

    def _design_error_handling(
        self, requirements: Dict[str, Any], style: Dict[str, Any]
    ) -> Dict[str, Any]:
        """에러 처리 설계"""
        return {
            "strategy": style.get("error_handling", "comprehensive_validation"),
            "levels": ["validation", "business_logic", "persistence", "user_interface"],
        }

    def _design_testing_strategy(
        self, requirements: Dict[str, Any], style: Dict[str, Any]
    ) -> Dict[str, Any]:
        """테스팅 전략 설계"""
        return {
            "unit_tests": True,
            "integration_tests": True,
            "coverage_target": 0.8,
            "frameworks": (
                ["pytest"] if style.get("testing") == "exhaustive" else ["unittest"]
            ),
        }

    async def _generate_source_code(
        self, architecture: Dict[str, Any], language: str, signature: str
    ) -> Dict[str, Any]:
        """소스 코드 생성"""
        style = self.signature_coding_styles[signature]
        templates = self.language_templates[language]

        generated = {"main_code": "", "file_structure": {}, "setup_instructions": []}

        # 메인 코드 생성
        for module in architecture["modules"]:
            module_code = self._generate_module_code(
                module, templates, style, signature
            )
            generated["file_structure"][
                f"{module['name']}.{self._get_file_extension(language)}"
            ] = module_code

            if module["is_main"]:
                generated["main_code"] = module_code

        # 설정 파일 생성
        generated["file_structure"].update(
            self._generate_config_files(architecture, language, signature)
        )

        # 설치 지침
        generated["setup_instructions"] = self._generate_setup_instructions(
            architecture, language, signature
        )

        return generated

    def _generate_module_code(
        self,
        module: Dict[str, Any],
        templates: Dict[str, Any],
        style: Dict[str, Any],
        signature: str,
    ) -> str:
        """모듈 코드 생성"""
        if module["is_main"]:
            return self._generate_main_module(module, templates, style, signature)
        else:
            return self._generate_regular_module(module, templates, style, signature)

    def _generate_main_module(
        self,
        module: Dict[str, Any],
        templates: Dict[str, Any],
        style: Dict[str, Any],
        signature: str,
    ) -> str:
        """메인 모듈 생성"""
        code = templates["module_structure"]["header"].format(
            description=f"{module['description']} - Generated by Echo {signature}"
        )

        code += templates["module_structure"]["imports"].format(
            imports="sys, json, argparse", type_imports="Dict, List, Any, Optional"
        )

        # 메인 클래스 생성
        code += templates["module_structure"]["class_template"].format(
            class_name="TaskManager",
            docstring="Main task management class",
            init_params="self",
            init_body="        self.tasks = []",
            methods='    def add_task(self, task: str) -> None:\n        """Add a new task"""\n        self.tasks.append(task)\n',
        )

        # 메인 함수
        code += '\ndef main():\n    """Main entry point"""\n    manager = TaskManager()\n    print(\'Task Manager Started\')\n\nif __name__ == \'__main__\':\n    main()\n'

        return code

    def _generate_regular_module(
        self,
        module: Dict[str, Any],
        templates: Dict[str, Any],
        style: Dict[str, Any],
        signature: str,
    ) -> str:
        """일반 모듈 생성"""
        code = templates["module_structure"]["header"].format(
            description=f"{module['description']} - {signature} style"
        )

        code += "\n# Module implementation\nclass {}Module:\n    pass\n".format(
            module["name"].title()
        )

        return code

    def _get_file_extension(self, language: str) -> str:
        """파일 확장자 반환"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "cpp": "cpp",
        }
        return extensions.get(language, "txt")

    def _generate_config_files(
        self, architecture: Dict[str, Any], language: str, signature: str
    ) -> Dict[str, str]:
        """설정 파일 생성"""
        if language == "python":
            return {
                "requirements.txt": "# Dependencies\n# Add required packages here\n",
                "README.md": f"# Project Generated by Echo {signature}\n\n## Description\nAuto-generated project\n",
            }
        return {}

    def _generate_setup_instructions(
        self, architecture: Dict[str, Any], language: str, signature: str
    ) -> List[str]:
        """설치 지침 생성"""
        if language == "python":
            return [
                "1. Install Python 3.8+",
                "2. pip install -r requirements.txt",
                "3. python main.py",
            ]
        return ["1. Follow language-specific setup"]

    async def _generate_tests(
        self, generated_code: Dict[str, Any], language: str, signature: str
    ) -> str:
        """테스트 코드 생성"""
        if language == "python":
            return '"""\nTest module\n"""\nimport unittest\nfrom main import TaskManager\n\nclass TestTaskManager(unittest.TestCase):\n    def test_add_task(self):\n        manager = TaskManager()\n        manager.add_task(\'Test task\')\n        self.assertEqual(len(manager.tasks), 1)\n\nif __name__ == \'__main__\':\n    unittest.main()\n'
        return "// Test implementation"

    def _generate_documentation(
        self,
        generated_code: Dict[str, Any],
        architecture: Dict[str, Any],
        signature: str,
    ) -> str:
        """문서화 생성"""
        return f"\"\"\"\nGenerated by Echo {signature}\n\nArchitecture: {architecture['pattern']}\nModules: {len(architecture['modules'])}\n\nThis code was automatically generated based on requirements analysis.\n\"\"\""

    def _analyze_complexity(self, source_code: str, language: str) -> Dict[str, Any]:
        """복잡도 분석"""
        if language == "python":
            return self._analyze_python_complexity(source_code)
        elif language in ["javascript", "typescript"]:
            return self._analyze_js_complexity(source_code)
        else:
            return self._analyze_generic_complexity(source_code)

    def _analyze_python_complexity(self, source_code: str) -> Dict[str, Any]:
        """Python 복잡도 분석"""
        try:
            tree = ast.parse(source_code)

            complexity_metrics = {
                "cyclomatic_complexity": 0,
                "function_count": 0,
                "class_count": 0,
                "line_count": len(source_code.split("\n")),
                "avg_function_length": 0,
                "max_nesting_depth": 0,
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity_metrics["function_count"] += 1
                    # 간단한 순환 복잡도 계산
                    complexity_metrics[
                        "cyclomatic_complexity"
                    ] += self._calculate_cyclomatic_complexity(node)
                elif isinstance(node, ast.ClassDef):
                    complexity_metrics["class_count"] += 1

            # 전체 점수 계산
            complexity_metrics["overall_score"] = self._calculate_complexity_score(
                complexity_metrics
            )

            return complexity_metrics

        except SyntaxError:
            return {"overall_score": 0.0, "error": "Syntax error in code"}

    def _calculate_cyclomatic_complexity(self, node) -> int:
        """순환 복잡도 계산"""
        complexity = 1  # 기본 복잡도

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _calculate_complexity_score(self, metrics: Dict[str, Any]) -> float:
        """복잡도 점수 계산 (0-1, 높을수록 좋음)"""
        standards = self.quality_standards["complexity"]

        # 각 메트릭별 점수 계산
        cyclomatic_score = max(
            0, 1 - (metrics["cyclomatic_complexity"] / standards["max_cyclomatic"])
        )

        if metrics["function_count"] > 0:
            avg_func_length = metrics["line_count"] / metrics["function_count"]
            length_score = max(
                0, 1 - (avg_func_length / standards["max_function_length"])
            )
        else:
            length_score = 1.0

        # 가중 평균
        return (cyclomatic_score * 0.6) + (length_score * 0.4)

    def _analyze_generated_code_quality(
        self, generated_code: Dict[str, Any], language: str, signature: str
    ) -> CodeAnalysis:
        """생성된 코드 품질 분석"""
        # 기본 분석 (실제로는 더 복잡한 분석 필요)
        return CodeAnalysis(
            complexity_score=0.8,
            quality_score=0.85,
            maintainability_score=0.9,
            test_coverage_estimate=0.7,
            architecture_pattern="Modular",
            suggested_improvements=["Add more error handling", "Improve documentation"],
            dependencies=["json", "argparse"],
        )

    def _get_next_steps(self, result: GeneratedCode, signature: str) -> List[str]:
        """다음 단계 추천"""
        return [
            "Review generated code",
            "Run tests",
            "Deploy to development environment",
            "Gather user feedback",
        ]

    def _analyze_syntax(self, source_code: str, language: str) -> Dict[str, Any]:
        """구문 분석"""
        return {"syntax_valid": True, "issues": []}

    def _calculate_quality_metrics(
        self, source_code: str, language: str
    ) -> Dict[str, Any]:
        """품질 메트릭 계산"""
        return {"overall_score": 0.8, "maintainability": 0.85}

    def _analyze_coding_style(
        self, source_code: str, signature: str, language: str
    ) -> Dict[str, Any]:
        """코딩 스타일 분석"""
        return {"style_score": 0.9, "consistency": 0.85}

    def _generate_improvement_suggestions(
        self,
        syntax_analysis: Dict[str, Any],
        complexity_analysis: Dict[str, Any],
        quality_metrics: Dict[str, Any],
        style_analysis: Dict[str, Any],
        signature: str,
    ) -> List[str]:
        """개선 제안 생성"""
        return ["Add type hints", "Improve error handling", "Add more tests"]

    def _analyze_dependencies(self, source_code: str, language: str) -> List[str]:
        """의존성 분석"""
        return ["json", "sys", "argparse"]

    def _estimate_test_coverage(self, source_code: str, language: str) -> float:
        """테스트 커버리지 추정"""
        return 0.75

    def _detect_architecture_pattern(self, source_code: str, language: str) -> str:
        """아키텍처 패턴 감지"""
        return "Modular Architecture"

    def _analyze_js_complexity(self, source_code: str) -> Dict[str, Any]:
        """JavaScript 복잡도 분석"""
        return {"overall_score": 0.8, "cyclomatic_complexity": 5}

    def _analyze_generic_complexity(self, source_code: str) -> Dict[str, Any]:
        """일반 복잡도 분석"""
        return {"overall_score": 0.75, "line_count": len(source_code.split("\n"))}


# 에이전트 인스턴스 생성 함수
def create_code_generator_agent() -> EchoCodeGeneratorAgent:
    """코드 생성 에이전트 생성"""
    return EchoCodeGeneratorAgent()


# ✅ 오프라인 스텁 함수 (외부 의존성 절대 없음)
async def generate_code(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    ✅ 초경량 코드 생성 스텁: 외부 콜/파일 I/O/대형 모델 로드 절대 금지
    """
    await asyncio.sleep(0)  # 첫 틱 양보

    language = spec.get("language", "python")
    filename = spec.get("filename", "main.py")
    spec_text = spec.get("spec", "hello world")

    # 언어별 간단한 스텁 코드 생성
    if language.lower() == "python":
        code = f'# Generated code for: {spec_text}\nprint("Hello from {filename}")\n\n# TODO: Implement {spec_text}'
    elif language.lower() == "javascript":
        code = f'// Generated code for: {spec_text}\nconsole.log("Hello from {filename}");\n\n// TODO: Implement {spec_text}'
    elif language.lower() == "bash":
        code = f'#!/bin/bash\n# Generated code for: {spec_text}\necho "Hello from {filename}"\n\n# TODO: Implement {spec_text}'
    else:
        code = f"// Generated code for: {spec_text}\n// Language: {language}\n// TODO: Implement {spec_text}"

    return {
        "mode": "offline-stub",
        "language": language,
        "filename": filename,
        "code": code,
        "spec": spec_text,
        "lines": len(code.split("\n")),
        "timestamp": "stub-generated",
    }
