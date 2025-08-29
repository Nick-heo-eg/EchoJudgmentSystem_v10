#!/usr/bin/env python3
"""
🧠 Echo IDE TokenWise - 토큰 효율적인 통합 개발 환경
VS Code + Claude Code 사용 시 토큰 소비를 최적화하는 지능형 IDE 어시스턴트

핵심 기능:
1. 🎯 스마트 컨텍스트 분석 및 압축
2. 🔄 인텔리전트 배치 처리
3. 📊 실시간 토큰 사용량 모니터링
4. 🧬 Echo 철학 기반 코드 분석
5. 💡 토큰 효율적인 제안 시스템
"""

import asyncio
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import difflib

from .token_optimizer import (
    TokenOptimizer,
    get_token_optimizer,
    optimize_for_claude_code,
)


class EchoIDETokenWise:
    """🧠 Echo IDE TokenWise - 토큰 효율적 통합 개발 환경"""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.token_optimizer = get_token_optimizer()

        # IDE 상태
        self.current_context = ""
        self.active_files = {}
        self.recent_queries = []
        self.batch_queue = []

        # 토큰 효율화 설정
        self.max_context_size = 8000  # 최대 컨텍스트 크기
        self.batch_size = 5  # 배치 처리 크기
        self.smart_filtering = True

        print("🧠 Echo IDE TokenWise 초기화")
        print(f"   작업공간: {self.workspace_path}")
        print("   토큰 최적화 엔진 연동 완료")

    async def analyze_code_efficiently(
        self, file_path: str, analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """🎯 토큰 효율적인 코드 분석"""
        print(f"🔍 효율적 코드 분석: {file_path} ({analysis_type})")

        try:
            # 파일 읽기
            full_path = self.workspace_path / file_path
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 토큰 최적화 적용
            optimized_content, optimization_result = optimize_for_claude_code(
                content, f"code_analysis_{analysis_type}"
            )

            # 분석 타입별 특화 처리
            if analysis_type == "security":
                analysis_result = await self._analyze_security(
                    optimized_content, file_path
                )
            elif analysis_type == "performance":
                analysis_result = await self._analyze_performance(
                    optimized_content, file_path
                )
            elif analysis_type == "architecture":
                analysis_result = await self._analyze_architecture(
                    optimized_content, file_path
                )
            else:
                analysis_result = await self._analyze_general(
                    optimized_content, file_path
                )

            # 토큰 사용량 추적
            estimated_tokens = len(optimized_content.split()) * 1.3
            self.token_optimizer.track_token_usage(
                input_tokens=int(estimated_tokens),
                output_tokens=int(len(str(analysis_result)) * 0.3),
                request_type=f"code_analysis_{analysis_type}",
                context_compressed=optimization_result.compression_ratio < 0.9,
            )

            return {
                "file_path": file_path,
                "analysis_type": analysis_type,
                "optimization_applied": optimization_result.optimization_methods,
                "token_savings": optimization_result.estimated_token_savings,
                "analysis_result": analysis_result,
                "processing_efficiency": {
                    "original_size": optimization_result.original_size,
                    "processed_size": optimization_result.optimized_size,
                    "compression_ratio": optimization_result.compression_ratio,
                },
            }

        except Exception as e:
            print(f"❌ 코드 분석 실패: {e}")
            return {"error": str(e)}

    async def _analyze_security(self, content: str, file_path: str) -> Dict[str, Any]:
        """🔒 보안 분석 (토큰 효율적)"""
        # 보안 관련 패턴 추출
        security_patterns = [
            r'password\s*=\s*["\'].*["\']',
            r'api_key\s*=\s*["\'].*["\']',
            r"exec\s*\(",
            r"eval\s*\(",
            r"__import__\s*\(",
            r'open\s*\(["\'].*["\'].*["\']w',
            r"subprocess\.",
            r"os\.system",
            r"input\s*\(",
        ]

        vulnerabilities = []
        for i, line in enumerate(content.split("\n"), 1):
            for pattern in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(
                        {
                            "line": i,
                            "pattern": pattern,
                            "content": line.strip(),
                            "severity": self._assess_security_severity(pattern),
                        }
                    )

        return {
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities[:10],  # 상위 10개만
            "security_score": max(0, 100 - len(vulnerabilities) * 10),
            "recommendations": self._generate_security_recommendations(
                vulnerabilities[:5]
            ),
        }

    async def _analyze_performance(
        self, content: str, file_path: str
    ) -> Dict[str, Any]:
        """⚡ 성능 분석 (토큰 효율적)"""
        performance_issues = []

        # 성능 이슈 패턴
        perf_patterns = [
            (r"for.*in.*range\(len\(", "Use enumerate() instead of range(len())"),
            (
                r"\.append\(.*\)\s*$",
                "Consider list comprehension for better performance",
            ),
            (r"while\s+True:", "Infinite loop detected"),
            (r"time\.sleep\(", "Blocking sleep call found"),
            (r"print\(", "Print statements in production code"),
            (
                r"len\(.*\)\s*==\s*0",
                "Use 'not sequence' instead of 'len(sequence) == 0'",
            ),
        ]

        for i, line in enumerate(content.split("\n"), 1):
            for pattern, message in perf_patterns:
                if re.search(pattern, line):
                    performance_issues.append(
                        {"line": i, "issue": message, "content": line.strip()}
                    )

        return {
            "performance_issues": len(performance_issues),
            "issues": performance_issues[:8],  # 상위 8개만
            "performance_score": max(0, 100 - len(performance_issues) * 8),
            "optimization_suggestions": self._generate_performance_suggestions(
                performance_issues[:3]
            ),
        }

    async def _analyze_architecture(
        self, content: str, file_path: str
    ) -> Dict[str, Any]:
        """🏗️ 아키텍처 분석 (토큰 효율적)"""
        # 함수 및 클래스 추출
        functions = re.findall(r"def\s+(\w+)\s*\(", content)
        classes = re.findall(r"class\s+(\w+)", content)
        imports = re.findall(r"(?:from\s+\w+\s+)?import\s+(\w+)", content)

        # 복잡도 계산 (간단한 버전)
        lines = content.split("\n")
        complexity_indicators = sum(
            1
            for line in lines
            if any(
                keyword in line for keyword in ["if", "for", "while", "try", "except"]
            )
        )

        return {
            "architecture_summary": {
                "functions_count": len(functions),
                "classes_count": len(classes),
                "imports_count": len(imports),
                "total_lines": len(lines),
                "complexity_score": min(100, complexity_indicators * 2),
            },
            "structure": {
                "functions": functions[:10],  # 상위 10개
                "classes": classes[:5],  # 상위 5개
                "imports": imports[:15],  # 상위 15개
            },
            "recommendations": self._generate_architecture_recommendations(
                len(functions), len(classes), complexity_indicators
            ),
        }

    async def _analyze_general(self, content: str, file_path: str) -> Dict[str, Any]:
        """📊 일반 분석 (토큰 효율적)"""
        lines = content.split("\n")

        return {
            "general_stats": {
                "total_lines": len(lines),
                "non_empty_lines": len([l for l in lines if l.strip()]),
                "comment_lines": len([l for l in lines if l.strip().startswith("#")]),
                "file_size": len(content),
                "estimated_complexity": len(
                    re.findall(r"def|class|if|for|while", content)
                ),
            },
            "code_quality": {
                "documentation_ratio": len(
                    [l for l in lines if '"""' in l or "'''" in l]
                )
                / max(len(lines), 1),
                "comment_ratio": len([l for l in lines if l.strip().startswith("#")])
                / max(len(lines), 1),
                "avg_line_length": sum(len(l) for l in lines) / max(len(lines), 1),
            },
        }

    def _assess_security_severity(self, pattern: str) -> str:
        """보안 심각도 평가"""
        high_severity = ["exec", "eval", "__import__", "subprocess", "os.system"]
        medium_severity = ["password", "api_key"]

        for high_risk in high_severity:
            if high_risk in pattern:
                return "HIGH"

        for medium_risk in medium_severity:
            if medium_risk in pattern:
                return "MEDIUM"

        return "LOW"

    def _generate_security_recommendations(
        self, vulnerabilities: List[Dict]
    ) -> List[str]:
        """보안 권장사항 생성"""
        recommendations = []

        for vuln in vulnerabilities:
            if "password" in vuln["pattern"]:
                recommendations.append(
                    "환경변수나 설정파일을 사용하여 비밀번호를 저장하세요"
                )
            elif "exec" in vuln["pattern"] or "eval" in vuln["pattern"]:
                recommendations.append("exec/eval 사용을 피하고 안전한 대안을 찾으세요")
            elif "subprocess" in vuln["pattern"]:
                recommendations.append("subprocess 사용 시 입력값 검증을 철저히 하세요")

        return list(set(recommendations))  # 중복 제거

    def _generate_performance_suggestions(self, issues: List[Dict]) -> List[str]:
        """성능 최적화 제안"""
        suggestions = []

        for issue in issues:
            if "enumerate" in issue["issue"]:
                suggestions.append("range(len()) 대신 enumerate() 사용을 고려하세요")
            elif "list comprehension" in issue["issue"]:
                suggestions.append(
                    "반복적인 append 대신 리스트 컴프리헨션 사용을 고려하세요"
                )
            elif "sleep" in issue["issue"]:
                suggestions.append("블로킹 sleep 대신 비동기 대안을 고려하세요")

        return list(set(suggestions))

    def _generate_architecture_recommendations(
        self, func_count: int, class_count: int, complexity: int
    ) -> List[str]:
        """아키텍처 권장사항"""
        recommendations = []

        if func_count > 20:
            recommendations.append("함수가 많습니다. 모듈 분리를 고려하세요")

        if class_count == 0 and func_count > 10:
            recommendations.append("클래스 기반 구조 도입을 고려하세요")

        if complexity > 50:
            recommendations.append("코드 복잡도가 높습니다. 리팩토링을 고려하세요")

        return recommendations

    async def batch_process_files(
        self, file_paths: List[str], analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """📦 배치 파일 처리 (토큰 효율성 극대화)"""
        print(f"📦 배치 처리 시작: {len(file_paths)}개 파일")

        # 파일들을 배치로 그룹화
        batches = [
            file_paths[i : i + self.batch_size]
            for i in range(0, len(file_paths), self.batch_size)
        ]

        all_results = []
        total_token_savings = 0

        for batch_num, batch in enumerate(batches, 1):
            print(f"📋 배치 {batch_num}/{len(batches)} 처리 중...")

            batch_results = []
            for file_path in batch:
                result = await self.analyze_code_efficiently(file_path, analysis_type)
                batch_results.append(result)
                total_token_savings += result.get("token_savings", 0)

            all_results.extend(batch_results)

            # 배치 간 짧은 대기 (API 레이트 리밋 고려)
            if batch_num < len(batches):
                await asyncio.sleep(0.5)

        return {
            "batch_processing_complete": True,
            "total_files_processed": len(file_paths),
            "total_batches": len(batches),
            "total_token_savings": total_token_savings,
            "results": all_results,
            "processing_summary": self._summarize_batch_results(all_results),
        }

    def _summarize_batch_results(self, results: List[Dict]) -> Dict[str, Any]:
        """배치 결과 요약"""
        successful = [r for r in results if "error" not in r]
        failed = [r for r in results if "error" in r]

        total_savings = sum(r.get("token_savings", 0) for r in successful)

        return {
            "success_rate": len(successful) / len(results) if results else 0,
            "successful_analyses": len(successful),
            "failed_analyses": len(failed),
            "total_token_savings": total_savings,
            "average_compression_ratio": sum(
                r.get("processing_efficiency", {}).get("compression_ratio", 1.0)
                for r in successful
            )
            / max(len(successful), 1),
        }

    def get_token_efficiency_report(self) -> Dict[str, Any]:
        """📊 토큰 효율성 보고서"""
        stats = self.token_optimizer.get_optimization_stats()
        suggestions = self.token_optimizer.suggest_optimizations()

        return {
            "echo_ide_tokenwise_report": True,
            "optimization_stats": stats,
            "efficiency_suggestions": suggestions,
            "workspace_context": {
                "active_files": len(self.active_files),
                "recent_queries": len(self.recent_queries),
                "batch_queue_size": len(self.batch_queue),
            },
            "token_saving_tips": [
                "🎯 반복적인 코드 분석은 캐시를 활용합니다",
                "📦 여러 파일을 한 번에 배치 처리하면 토큰을 절약할 수 있습니다",
                "🔄 비슷한 분석 요청은 자동으로 최적화됩니다",
                "💡 Echo IDE의 스마트 컨텍스트 압축을 활용하세요",
                "📊 정기적으로 토큰 사용 패턴을 확인하세요",
            ],
            "timestamp": datetime.now().isoformat(),
        }

    async def smart_context_analysis(
        self, query: str, context_files: List[str] = None
    ) -> Dict[str, Any]:
        """🧠 스마트 컨텍스트 분석"""
        print(f"🧠 스마트 컨텍스트 분석: {query[:50]}...")

        # 쿼리 타입 분류
        query_type = self._classify_query(query)

        # 관련 파일들 자동 선택
        if context_files is None:
            context_files = await self._select_relevant_files(query, query_type)

        # 컨텍스트 구성 및 최적화
        combined_context = ""
        optimization_results = []

        for file_path in context_files[:5]:  # 최대 5개 파일로 제한
            try:
                full_path = self.workspace_path / file_path
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 쿼리 타입에 맞는 최적화 적용
                optimized_content, opt_result = optimize_for_claude_code(
                    content, query_type
                )
                combined_context += f"\n--- {file_path} ---\n{optimized_content}\n"
                optimization_results.append(opt_result)

            except Exception as e:
                print(f"⚠️ 파일 읽기 실패 {file_path}: {e}")

        # 전체 컨텍스트 크기 제한
        if len(combined_context) > self.max_context_size:
            combined_context = (
                combined_context[: self.max_context_size]
                + "\n[...컨텍스트 크기 제한으로 생략...]"
            )

        return {
            "query": query,
            "query_type": query_type,
            "context_files": context_files,
            "optimized_context": combined_context,
            "optimization_summary": {
                "total_files": len(optimization_results),
                "total_token_savings": sum(
                    r.estimated_token_savings for r in optimization_results
                ),
                "average_compression": sum(
                    r.compression_ratio for r in optimization_results
                )
                / max(len(optimization_results), 1),
            },
        }

    def _classify_query(self, query: str) -> str:
        """쿼리 타입 분류"""
        query_lower = query.lower()

        if any(
            word in query_lower for word in ["bug", "error", "debug", "fix", "issue"]
        ):
            return "debugging"
        elif any(
            word in query_lower for word in ["refactor", "improve", "optimize", "clean"]
        ):
            return "refactoring"
        elif any(
            word in query_lower
            for word in ["security", "vulnerability", "safe", "secure"]
        ):
            return "security"
        elif any(
            word in query_lower for word in ["performance", "speed", "fast", "slow"]
        ):
            return "performance"
        elif any(
            word in query_lower for word in ["architecture", "design", "structure"]
        ):
            return "architecture"
        else:
            return "general"

    async def _select_relevant_files(self, query: str, query_type: str) -> List[str]:
        """관련 파일 자동 선택"""
        # 간단한 관련도 기반 파일 선택
        all_files = list(self.workspace_path.rglob("*.py"))

        # 쿼리 키워드와 파일명 매칭
        query_keywords = query.lower().split()
        relevant_files = []

        for file_path in all_files:
            relative_path = file_path.relative_to(self.workspace_path)
            file_name = file_path.name.lower()

            # 파일명과 쿼리 키워드 매칭
            relevance_score = sum(
                1 for keyword in query_keywords if keyword in file_name
            )

            if relevance_score > 0:
                relevant_files.append((str(relative_path), relevance_score))

        # 관련도 순으로 정렬
        relevant_files.sort(key=lambda x: x[1], reverse=True)

        return [file_path for file_path, score in relevant_files[:10]]


# 편의 함수들
async def analyze_with_echo_ide(
    file_path: str, analysis_type: str = "general", workspace: str = "."
) -> Dict[str, Any]:
    """Echo IDE TokenWise 분석 편의 함수"""
    ide = EchoIDETokenWise(workspace)
    return await ide.analyze_code_efficiently(file_path, analysis_type)


async def batch_analyze_with_echo_ide(
    file_paths: List[str], analysis_type: str = "general", workspace: str = "."
) -> Dict[str, Any]:
    """Echo IDE TokenWise 배치 분석 편의 함수"""
    ide = EchoIDETokenWise(workspace)
    return await ide.batch_process_files(file_paths, analysis_type)


if __name__ == "__main__":
    # 테스트
    print("🧪 Echo IDE TokenWise 테스트")

    async def test_echo_ide():
        ide = EchoIDETokenWise(".")

        # 단일 파일 분석 테스트
        test_file = "echo_engine/token_optimizer.py"
        if Path(test_file).exists():
            result = await ide.analyze_code_efficiently(test_file, "security")
            print(f"\n📊 분석 결과:")
            print(f"   파일: {result['file_path']}")
            print(f"   토큰 절약: {result['token_savings']}개")
            print(
                f"   압축률: {result['processing_efficiency']['compression_ratio']:.1%}"
            )

        # 효율성 보고서
        report = ide.get_token_efficiency_report()
        print(f"\n📈 효율성 보고서:")
        print(f"   활성 파일: {report['workspace_context']['active_files']}")
        print(f"   최적화 제안: {len(report['efficiency_suggestions'])}개")

        print("\n✅ Echo IDE TokenWise 테스트 완료")

    asyncio.run(test_echo_ide())
