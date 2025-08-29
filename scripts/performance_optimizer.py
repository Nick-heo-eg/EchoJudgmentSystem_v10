#!/usr/bin/env python3
"""
Echo 성능 최적화 자동화 시스템
코드 성능 병목점 자동 감지 및 최적화 제안
"""

import ast
import time
import cProfile
import pstats
import io
import re
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import memory_profiler
except ImportError:
    memory_profiler = None

try:
    import line_profiler
except ImportError:
    line_profiler = None
import sys
import os

logger = logging.getLogger(__name__)


@dataclass
class PerformanceIssue:
    """성능 이슈"""

    severity: str  # critical, high, medium, low
    category: str  # cpu, memory, io, algorithm, database
    description: str
    file_path: str
    line_number: int
    function_name: str
    current_performance: str
    suggested_optimization: str
    estimated_improvement: str
    confidence: float


@dataclass
class ProfileResult:
    """프로파일링 결과"""

    total_time: float
    function_stats: Dict[str, Dict]
    memory_usage: Dict[str, float]
    hotspots: List[Dict]
    bottlenecks: List[PerformanceIssue]


class PerformanceOptimizer:
    """성능 최적화 분석기"""

    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.performance_issues: List[PerformanceIssue] = []

        # 🎯 성능 패턴 라이브러리
        self.optimization_patterns = {
            "loop_inefficiency": {
                "patterns": [
                    r"for\s+\w+\s+in\s+range\(len\(",  # for i in range(len(list))
                    r"for\s+\w+\s+in\s+\w+:\s*if\s+",  # 필터링이 없는 루프
                ],
                "optimizations": [
                    "enumerate() 사용으로 인덱스 접근 최적화",
                    "list comprehension 또는 filter() 사용 고려",
                ],
            },
            "string_concatenation": {
                "patterns": [
                    r"\w+\s*\+=\s*[\"'].*[\"']",  # str += "text"
                    r"\w+\s*=\s*\w+\s*\+\s*[\"']",  # str = str + "text"
                ],
                "optimizations": [
                    "join() 메서드 사용으로 문자열 연결 최적화",
                    "f-string 또는 format() 사용 고려",
                ],
            },
            "database_queries": {
                "patterns": [
                    r"for\s+\w+\s+in\s+\w+:.*\.query\(",  # N+1 쿼리 문제
                    r"\.execute\(.*\+.*\)",  # 동적 쿼리 생성
                ],
                "optimizations": [
                    "bulk 쿼리 또는 join 사용으로 N+1 문제 해결",
                    "prepared statement 사용으로 쿼리 최적화",
                ],
            },
            "file_operations": {
                "patterns": [
                    r"open\(.*\)\.read\(\)",  # with문 없는 파일 읽기
                    r"for\s+line\s+in\s+open\(",  # 파일 전체 로드
                ],
                "optimizations": [
                    "with문 사용으로 리소스 관리 최적화",
                    "readline() 또는 chunk 단위 읽기로 메모리 사용량 최적화",
                ],
            },
            "algorithm_complexity": {
                "patterns": [
                    r"for\s+.*:\s*for\s+.*:",  # 중첩 루프
                    r"\.sort\(\).*for\s+",  # 정렬 후 반복
                ],
                "optimizations": [
                    "알고리즘 복잡도 개선 (O(n²) → O(n log n))",
                    "적절한 자료구조 사용 (set, dict, heap 등)",
                ],
            },
        }

        # 메모리 최적화 패턴
        self.memory_patterns = {
            "large_data_structures": [
                r"list\(range\(\d{4,}\)\)",  # 큰 리스트 생성
                r"\[\w+\s+for\s+\w+\s+in\s+\w+\s+if\s+.*\]",  # 큰 list comprehension
            ],
            "generator_opportunities": [
                r"return\s+\[.*for.*\]",  # 리스트 반환 대신 제너레이터
                r"sum\(\[.*for.*\]\)",  # sum에 리스트 대신 제너레이터
            ],
        }

    def analyze_project_performance(self) -> Dict[str, Any]:
        """프로젝트 전체 성능 분석"""
        logger.info("🔍 Starting comprehensive performance analysis...")

        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_dir.absolute()),
            "analyzed_files": 0,
            "performance_issues": [],
            "profile_results": {},
            "optimization_summary": {
                "total_issues": 0,
                "critical_issues": 0,
                "estimated_improvement": 0,
            },
        }

        # 1. 정적 코드 분석
        self._analyze_source_files()
        analysis_result["analyzed_files"] = len(list(self.project_dir.rglob("*.py")))

        # 2. 동적 프로파일링 (주요 모듈만)
        main_modules = self._find_main_modules()
        for module_path in main_modules:
            profile_result = self._profile_module(module_path)
            if profile_result:
                analysis_result["profile_results"][str(module_path)] = asdict(
                    profile_result
                )

        # 3. 결과 집계
        analysis_result["performance_issues"] = [
            asdict(issue) for issue in self.performance_issues
        ]
        analysis_result["optimization_summary"] = self._calculate_optimization_summary()

        logger.info(
            f"📊 Performance analysis completed: {len(self.performance_issues)} issues found"
        )
        return analysis_result

    def _analyze_source_files(self):
        """소스 파일 정적 분석"""
        python_files = list(self.project_dir.rglob("*.py"))

        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue

            try:
                self._analyze_python_file(file_path)
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")

    def _should_skip_file(self, file_path: Path) -> bool:
        """파일 스킵 여부 판단"""
        skip_dirs = {
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
            ".pytest_cache",
        }
        skip_patterns = {"test_", "_test", "conftest"}

        # 디렉토리 체크
        for part in file_path.parts:
            if part in skip_dirs:
                return True

        # 테스트 파일 스킵
        for pattern in skip_patterns:
            if pattern in file_path.name:
                return True

        return False

    def _analyze_python_file(self, file_path: Path):
        """Python 파일 성능 분석"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\\n")

            # 1. 패턴 기반 분석
            self._check_optimization_patterns(file_path, content, lines)

            # 2. AST 기반 복잡도 분석
            self._analyze_complexity(file_path, content)

            # 3. 메모리 사용 패턴 분석
            self._analyze_memory_patterns(file_path, content, lines)

        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")

    def _check_optimization_patterns(
        self, file_path: Path, content: str, lines: List[str]
    ):
        """최적화 패턴 검사"""
        for category, pattern_data in self.optimization_patterns.items():
            patterns = pattern_data["patterns"]
            optimizations = pattern_data["optimizations"]

            for i, pattern in enumerate(patterns):
                for match in re.finditer(pattern, content, re.MULTILINE):
                    line_num = content[: match.start()].count("\\n") + 1

                    # 함수명 추출
                    function_name = self._extract_function_name(lines, line_num)

                    # 심각도 결정
                    severity = self._determine_severity(category, pattern)

                    self.performance_issues.append(
                        PerformanceIssue(
                            severity=severity,
                            category=self._map_category(category),
                            description=f"{category.replace('_', ' ').title()} 최적화 기회 발견",
                            file_path=str(file_path.relative_to(self.project_dir)),
                            line_number=line_num,
                            function_name=function_name,
                            current_performance="현재 구현의 성능 특성 분석 필요",
                            suggested_optimization=optimizations[
                                min(i, len(optimizations) - 1)
                            ],
                            estimated_improvement=self._estimate_improvement(category),
                            confidence=0.7,
                        )
                    )

    def _analyze_complexity(self, file_path: Path, content: str):
        """복잡도 분석"""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_cyclomatic_complexity(node)

                    if complexity > 10:  # 높은 복잡도
                        self.performance_issues.append(
                            PerformanceIssue(
                                severity="medium" if complexity <= 15 else "high",
                                category="algorithm",
                                description=f"높은 순환 복잡도 (McCabe: {complexity})",
                                file_path=str(file_path.relative_to(self.project_dir)),
                                line_number=node.lineno,
                                function_name=node.name,
                                current_performance=f"순환 복잡도: {complexity}",
                                suggested_optimization="함수 분해 및 알고리즘 단순화",
                                estimated_improvement="가독성 및 유지보수성 30% 향상",
                                confidence=0.8,
                            )
                        )

        except SyntaxError:
            pass
        except Exception as e:
            logger.warning(f"Complexity analysis failed for {file_path}: {e}")

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """순환 복잡도 계산"""
        complexity = 1  # 기본 복잡도

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1

        return complexity

    def _analyze_memory_patterns(self, file_path: Path, content: str, lines: List[str]):
        """메모리 사용 패턴 분석"""
        for pattern_type, patterns in self.memory_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    line_num = content[: match.start()].count("\\n") + 1
                    function_name = self._extract_function_name(lines, line_num)

                    self.performance_issues.append(
                        PerformanceIssue(
                            severity="medium",
                            category="memory",
                            description=f"메모리 최적화 기회: {pattern_type.replace('_', ' ')}",
                            file_path=str(file_path.relative_to(self.project_dir)),
                            line_number=line_num,
                            function_name=function_name,
                            current_performance="메모리 사용량 분석 필요",
                            suggested_optimization=self._get_memory_optimization(
                                pattern_type
                            ),
                            estimated_improvement="메모리 사용량 20-50% 감소",
                            confidence=0.6,
                        )
                    )

    def _extract_function_name(self, lines: List[str], line_num: int) -> str:
        """라인 번호 기준으로 함수명 추출"""
        for i in range(max(0, line_num - 10), min(len(lines), line_num + 1)):
            line = lines[i].strip()
            if line.startswith("def ") or line.startswith("async def "):
                match = re.match(r"(async )?def\\s+(\\w+)", line)
                if match:
                    return match.group(2)
        return "unknown"

    def _determine_severity(self, category: str, pattern: str) -> str:
        """심각도 결정"""
        severity_map = {
            "database_queries": "high",
            "loop_inefficiency": "medium",
            "algorithm_complexity": "high",
            "string_concatenation": "low",
            "file_operations": "medium",
        }
        return severity_map.get(category, "low")

    def _map_category(self, category: str) -> str:
        """카테고리 매핑"""
        category_map = {
            "loop_inefficiency": "cpu",
            "string_concatenation": "cpu",
            "database_queries": "database",
            "file_operations": "io",
            "algorithm_complexity": "algorithm",
        }
        return category_map.get(category, "cpu")

    def _estimate_improvement(self, category: str) -> str:
        """개선 효과 추정"""
        improvement_map = {
            "loop_inefficiency": "실행 시간 20-40% 감소",
            "string_concatenation": "메모리 사용량 30-60% 감소",
            "database_queries": "쿼리 시간 50-90% 감소",
            "file_operations": "I/O 성능 20-50% 향상",
            "algorithm_complexity": "확장성 및 성능 대폭 개선",
        }
        return improvement_map.get(category, "성능 향상 기대")

    def _get_memory_optimization(self, pattern_type: str) -> str:
        """메모리 최적화 제안"""
        optimization_map = {
            "large_data_structures": "generator 또는 iterator 사용으로 메모리 사용량 최적화",
            "generator_opportunities": "list 대신 generator expression 사용",
        }
        return optimization_map.get(pattern_type, "메모리 사용 패턴 최적화")

    def _find_main_modules(self) -> List[Path]:
        """주요 모듈 찾기"""
        main_modules = []

        # main.py, app.py 등 메인 엔트리 포인트
        for pattern in ["main.py", "app.py", "run.py", "server.py"]:
            main_file = self.project_dir / pattern
            if main_file.exists():
                main_modules.append(main_file)

        # __main__.py 모듈
        for main_file in self.project_dir.rglob("__main__.py"):
            main_modules.append(main_file)

        return main_modules[:3]  # 최대 3개만

    def _profile_module(self, module_path: Path) -> Optional[ProfileResult]:
        """모듈 프로파일링"""
        try:
            logger.info(f"📊 Profiling module: {module_path}")

            # cProfile 실행
            pr = cProfile.Profile()

            # 모듈 동적 임포트 및 실행
            spec = self._import_and_run_module(module_path, pr)

            if not spec:
                return None

            # 통계 수집
            s = io.StringIO()
            stats = pstats.Stats(pr, stream=s)
            stats.sort_stats("cumulative").print_stats(20)

            # 결과 파싱
            function_stats = self._parse_profile_stats(stats)
            hotspots = self._identify_hotspots(function_stats)

            return ProfileResult(
                total_time=sum(
                    stat.get("cumtime", 0) for stat in function_stats.values()
                ),
                function_stats=function_stats,
                memory_usage={},  # 메모리 프로파일링은 선택적
                hotspots=hotspots,
                bottlenecks=[],
            )

        except Exception as e:
            logger.warning(f"Profiling failed for {module_path}: {e}")
            return None

    def _import_and_run_module(
        self, module_path: Path, profiler: cProfile.Profile
    ) -> bool:
        """모듈 임포트 및 실행"""
        try:
            # 모듈 경로를 Python 경로에 추가
            module_dir = module_path.parent
            if str(module_dir) not in sys.path:
                sys.path.insert(0, str(module_dir))

            # 프로파일링 시작
            profiler.enable()

            # 간단한 임포트 테스트만 수행 (실제 실행은 위험할 수 있음)
            module_name = module_path.stem

            # 안전하게 임포트만 테스트
            try:
                __import__(module_name)
                time.sleep(0.1)  # 최소한의 실행 시간
            except Exception:
                pass

            profiler.disable()
            return True

        except Exception as e:
            logger.warning(f"Module execution failed: {e}")
            return False

    def _parse_profile_stats(self, stats: pstats.Stats) -> Dict[str, Dict]:
        """프로파일 통계 파싱"""
        function_stats = {}

        try:
            for func, (cc, nc, tt, ct, callers) in stats.stats.items():
                filename, line_num, func_name = func

                function_stats[f"{filename}:{func_name}"] = {
                    "call_count": cc,
                    "total_time": tt,
                    "cumtime": ct,
                    "filename": filename,
                    "line_number": line_num,
                    "function_name": func_name,
                }
        except Exception as e:
            logger.warning(f"Failed to parse profile stats: {e}")

        return function_stats

    def _identify_hotspots(self, function_stats: Dict[str, Dict]) -> List[Dict]:
        """성능 핫스팟 식별"""
        hotspots = []

        # 실행 시간 기준 상위 함수들
        sorted_functions = sorted(
            function_stats.items(), key=lambda x: x[1].get("cumtime", 0), reverse=True
        )

        for func_name, stats in sorted_functions[:10]:
            if stats.get("cumtime", 0) > 0.01:  # 10ms 이상
                hotspots.append(
                    {
                        "function": func_name,
                        "cumulative_time": stats.get("cumtime", 0),
                        "call_count": stats.get("call_count", 0),
                        "avg_time": stats.get("cumtime", 0)
                        / max(stats.get("call_count", 1), 1),
                    }
                )

        return hotspots

    def _calculate_optimization_summary(self) -> Dict[str, Any]:
        """최적화 요약 계산"""
        summary = {
            "total_issues": len(self.performance_issues),
            "critical_issues": sum(
                1 for issue in self.performance_issues if issue.severity == "critical"
            ),
            "high_issues": sum(
                1 for issue in self.performance_issues if issue.severity == "high"
            ),
            "medium_issues": sum(
                1 for issue in self.performance_issues if issue.severity == "medium"
            ),
            "low_issues": sum(
                1 for issue in self.performance_issues if issue.severity == "low"
            ),
            "category_breakdown": {},
        }

        # 카테고리별 분류
        for issue in self.performance_issues:
            category = issue.category
            if category not in summary["category_breakdown"]:
                summary["category_breakdown"][category] = 0
            summary["category_breakdown"][category] += 1

        return summary

    def generate_optimization_report(self, output_path: str) -> Dict[str, Any]:
        """최적화 리포트 생성"""
        analysis_result = self.analyze_project_performance()

        # JSON 리포트 저장
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)

        # HTML 리포트 생성
        html_path = output_path.replace(".json", ".html")
        self._generate_html_report(analysis_result, html_path)

        logger.info(f"📊 Optimization report generated: {output_path}")
        return analysis_result

    def _generate_html_report(self, data: Dict[str, Any], html_path: str):
        """HTML 리포트 생성"""
        summary = data["optimization_summary"]
        issues = data["performance_issues"]

        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Echo Performance Optimization Report</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0; padding: 20px; background: #f8f9fa; 
        }}
        .container {{ 
            max-width: 1200px; margin: 0 auto; background: white;
            border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .summary {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; margin-bottom: 30px; 
        }}
        .summary-card {{ 
            background: #e8f4fd; border-radius: 8px; padding: 20px; text-align: center;
        }}
        .issue-list {{ margin-top: 20px; }}
        .issue-item {{ 
            border: 1px solid #e1e8ed; border-radius: 8px; padding: 15px; 
            margin-bottom: 15px; background: #fafbfc;
        }}
        .severity-critical {{ border-left: 4px solid #dc3545; }}
        .severity-high {{ border-left: 4px solid #fd7e14; }}
        .severity-medium {{ border-left: 4px solid #ffc107; }}
        .severity-low {{ border-left: 4px solid #28a745; }}
        .issue-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .issue-details {{ margin-top: 10px; font-size: 0.9em; color: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Performance Optimization Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>총 이슈</h3>
                <h2>{summary['total_issues']}</h2>
            </div>
            <div class="summary-card">
                <h3>Critical</h3>
                <h2 style="color: #dc3545;">{summary['critical_issues']}</h2>
            </div>
            <div class="summary-card">
                <h3>High</h3>
                <h2 style="color: #fd7e14;">{summary['high_issues']}</h2>
            </div>
            <div class="summary-card">
                <h3>Medium</h3>
                <h2 style="color: #ffc107;">{summary['medium_issues']}</h2>
            </div>
            <div class="summary-card">
                <h3>Low</h3>
                <h2 style="color: #28a745;">{summary['low_issues']}</h2>
            </div>
        </div>
        
        <div class="issue-list">
            <h3>📋 최적화 기회</h3>
"""

        for issue in issues:
            html_content += f"""
            <div class="issue-item severity-{issue['severity']}">
                <div class="issue-header">
                    <strong>{issue['description']}</strong>
                    <span class="badge">{issue['severity'].upper()}</span>
                </div>
                <div class="issue-details">
                    <p><strong>파일:</strong> {issue['file_path']}:{issue['line_number']}</p>
                    <p><strong>함수:</strong> {issue['function_name']}</p>
                    <p><strong>권장사항:</strong> {issue['suggested_optimization']}</p>
                    <p><strong>예상 개선:</strong> {issue['estimated_improvement']}</p>
                </div>
            </div>
"""

        html_content += """
        </div>
    </div>
</body>
</html>
"""

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Echo Performance Optimizer")
    parser.add_argument(
        "--project-dir", default=".", help="Project directory to analyze"
    )
    parser.add_argument(
        "--output",
        default="performance_optimization_report.json",
        help="Output report file",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # 로깅 설정
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    # 성능 분석 실행
    optimizer = PerformanceOptimizer(args.project_dir)
    results = optimizer.generate_optimization_report(args.output)

    # 결과 요약 출력
    summary = results["optimization_summary"]
    print(f"\\n🚀 Performance Analysis Results:")
    print(f"   📁 Analyzed Files: {results['analyzed_files']}")
    print(f"   🎯 Total Issues: {summary['total_issues']}")
    print(f"   🔥 Critical: {summary['critical_issues']}")
    print(f"   ⚠️  High: {summary['high_issues']}")
    print(f"   📋 Medium: {summary['medium_issues']}")
    print(f"   ℹ️  Low: {summary['low_issues']}")

    # 카테고리별 분류
    if summary["category_breakdown"]:
        print(f"\\n📊 Issues by Category:")
        for category, count in summary["category_breakdown"].items():
            print(f"   {category}: {count}")

    return 0 if summary["total_issues"] == 0 else 1


if __name__ == "__main__":
    exit(main())
