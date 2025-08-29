#!/usr/bin/env python3
"""
🔍 Echo Structure Analyzer - 지능형 구조 분석 및 중복 방지 시스템

Echo가 새로운 요청을 받을 때마다:
1. 기존 기능을 먼저 검색하여 재사용 가능한지 확인
2. 중복 생성을 방지하고 기존 코드 활용 제안
3. 시스템 전체 구조를 고려한 최적 배치 결정
4. 지속적인 컨텍스트 유지
"""

from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import json
import re
from pathlib import Path

from .echo_system_memory import get_system_memory, EchoFunction, EchoModule


class EchoStructureAnalyzer:
    """Echo 구조 분석 및 중복 방지 시스템"""

    def __init__(self):
        self.system_memory = get_system_memory()
        self.analysis_cache = {}
        print("🔍 Echo Structure Analyzer 초기화 완료")

    def analyze_new_request(self, user_request: str, signature: str) -> Dict[str, Any]:
        """새 요청 분석 - 기존 기능 활용 가능성 체크"""

        analysis_result = {
            "request": user_request,
            "signature": signature,
            "timestamp": datetime.now().isoformat(),
            "existing_functions": [],
            "similar_implementations": [],
            "recommended_approach": "",
            "duplicate_risk": "low",
            "suggested_file_location": "",
            "context_continuity": {},
        }

        # 1. 기존 기능 검색
        print(f"🔍 '{user_request}' 요청에 대한 기존 기능 검색 중...")
        existing_functions = self._find_existing_functions(user_request)
        analysis_result["existing_functions"] = [
            {
                "name": func.name,
                "file_path": func.file_path,
                "description": func.description,
                "usage_count": func.usage_count,
                "last_used": func.last_used.isoformat() if func.last_used else None,
                "relevance_score": self._calculate_relevance(user_request, func),
            }
            for func in existing_functions[:5]  # 상위 5개만
        ]

        # 2. 유사한 구현 찾기
        similar_implementations = self._find_similar_implementations(user_request)
        analysis_result["similar_implementations"] = similar_implementations

        # 3. 중복 위험도 평가
        duplicate_risk = self._assess_duplicate_risk(user_request, existing_functions)
        analysis_result["duplicate_risk"] = duplicate_risk

        # 4. 최적 접근법 추천
        recommended_approach = self._recommend_approach(
            user_request, existing_functions, similar_implementations, signature
        )
        analysis_result["recommended_approach"] = recommended_approach

        # 5. 파일 위치 제안
        suggested_location = self._suggest_file_location(user_request, signature)
        analysis_result["suggested_file_location"] = suggested_location

        # 6. 컨텍스트 연속성 분석
        context_continuity = self._analyze_context_continuity(user_request)
        analysis_result["context_continuity"] = context_continuity

        return analysis_result

    def _find_existing_functions(self, request: str) -> List[EchoFunction]:
        """요청과 관련된 기존 기능 찾기"""
        # 요청에서 키워드 추출
        keywords = self._extract_keywords(request)

        all_matches = []
        for keyword in keywords:
            matches = self.system_memory.get_existing_functions(keyword=keyword)
            all_matches.extend(matches)

        # 중복 제거 및 관련성 점수로 정렬
        unique_functions = {}
        for func in all_matches:
            if func.name not in unique_functions:
                unique_functions[func.name] = func

        sorted_functions = sorted(
            unique_functions.values(),
            key=lambda f: self._calculate_relevance(request, f),
            reverse=True,
        )

        return sorted_functions[:10]

    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 의미있는 키워드 추출"""
        # 한글, 영어 키워드 추출
        korean_keywords = re.findall(r"[가-힣]+", text)
        english_keywords = re.findall(r"[a-zA-Z]{3,}", text.lower())

        # 프로그래밍 관련 키워드 우선순위
        programming_keywords = {
            "계산기": ["calculator", "calc", "math"],
            "게임": ["game", "play", "interactive"],
            "웹": ["web", "html", "server", "api"],
            "데이터": ["data", "json", "csv", "parse"],
            "파일": ["file", "read", "write", "io"],
            "알고리즘": ["algorithm", "sort", "search", "tree"],
            "인터페이스": ["ui", "interface", "gui", "cli"],
            "네트워크": ["network", "http", "request", "client"],
            "데이터베이스": ["database", "db", "sql", "query"],
        }

        enhanced_keywords = []
        for korean in korean_keywords:
            enhanced_keywords.append(korean)
            if korean in programming_keywords:
                enhanced_keywords.extend(programming_keywords[korean])

        enhanced_keywords.extend(english_keywords)

        # 중복 제거 및 길이 필터
        return list(set([kw for kw in enhanced_keywords if len(kw) >= 3]))

    def _calculate_relevance(self, request: str, function: EchoFunction) -> float:
        """요청과 함수의 관련성 점수 계산"""
        score = 0.0

        request_lower = request.lower()
        func_name_lower = function.name.lower()
        func_desc_lower = function.description.lower()

        # 이름 매칭
        if any(
            keyword in func_name_lower for keyword in self._extract_keywords(request)
        ):
            score += 3.0

        # 설명 매칭
        desc_keywords = self._extract_keywords(function.description)
        request_keywords = self._extract_keywords(request)
        common_keywords = set(desc_keywords) & set(request_keywords)
        score += len(common_keywords) * 1.5

        # 사용 횟수 (인기도)
        score += min(function.usage_count * 0.1, 1.0)

        # 최근 사용 (신선도)
        if function.last_used:
            days_since_use = (datetime.now() - function.last_used).days
            score += max(0, (30 - days_since_use) / 30)  # 30일 기준

        return score

    def _find_similar_implementations(self, request: str) -> List[Dict[str, Any]]:
        """유사한 구현 패턴 찾기"""
        similar_patterns = []

        # 요청 패턴 분석
        request_lower = request.lower()

        patterns = {
            "crud_operations": [
                "생성",
                "조회",
                "수정",
                "삭제",
                "create",
                "read",
                "update",
                "delete",
            ],
            "data_processing": [
                "변환",
                "파싱",
                "처리",
                "분석",
                "parse",
                "process",
                "analyze",
            ],
            "ui_components": [
                "화면",
                "인터페이스",
                "ui",
                "gui",
                "interface",
                "display",
            ],
            "api_endpoints": ["api", "endpoint", "서버", "server", "route"],
            "algorithms": ["정렬", "검색", "알고리즘", "sort", "search", "algorithm"],
        }

        for pattern_name, keywords in patterns.items():
            if any(keyword in request_lower for keyword in keywords):
                # 해당 패턴의 기존 구현 찾기
                pattern_functions = []
                for keyword in keywords:
                    functions = self.system_memory.get_existing_functions(
                        keyword=keyword
                    )
                    pattern_functions.extend(functions[:3])

                if pattern_functions:
                    similar_patterns.append(
                        {
                            "pattern": pattern_name,
                            "examples": [
                                {
                                    "name": func.name,
                                    "file_path": func.file_path,
                                    "description": func.description[:100],
                                }
                                for func in pattern_functions[:3]
                            ],
                        }
                    )

        return similar_patterns

    def _assess_duplicate_risk(
        self, request: str, existing_functions: List[EchoFunction]
    ) -> str:
        """중복 생성 위험도 평가"""
        if not existing_functions:
            return "low"

        # 높은 관련성 점수를 가진 함수가 있는지 확인
        max_relevance = max(
            self._calculate_relevance(request, func) for func in existing_functions
        )

        if max_relevance > 4.0:
            return "high"  # 매우 유사한 기능이 이미 존재
        elif max_relevance > 2.0:
            return "medium"  # 관련된 기능이 존재
        else:
            return "low"  # 새로운 기능

    def _recommend_approach(
        self,
        request: str,
        existing_functions: List[EchoFunction],
        similar_implementations: List[Dict],
        signature: str,
    ) -> str:
        """최적 접근법 추천"""

        if not existing_functions:
            return f"🆕 새로운 기능을 {signature} 스타일로 구현하는 것을 추천합니다."

        top_function = existing_functions[0]
        relevance = self._calculate_relevance(request, top_function)

        if relevance > 4.0:
            return f"♻️ 기존 함수 '{top_function.name}'을 재사용하거나 확장하는 것을 추천합니다. (파일: {top_function.file_path})"

        elif relevance > 2.0:
            return f"🔧 기존 함수 '{top_function.name}'을 참고하여 유사한 패턴으로 구현하는 것을 추천합니다."

        elif similar_implementations:
            pattern = similar_implementations[0]["pattern"]
            return f"📋 {pattern} 패턴을 따라 구현하는 것을 추천합니다."

        else:
            return (
                f"🆕 새로운 접근법으로 {signature} 스타일의 독창적인 구현을 추천합니다."
            )

    def _suggest_file_location(self, request: str, signature: str) -> str:
        """최적 파일 위치 제안"""
        request_lower = request.lower()

        # 카테고리별 위치 매핑
        location_mapping = {
            "api": "echo_engine/echo_api_extensions.py",
            "server": "echo_engine/echo_server_utils.py",
            "ui": "streamlit_ui/components/",
            "web": "echo_engine/echo_web_utils.py",
            "data": "echo_engine/echo_data_processing.py",
            "algorithm": "echo_engine/echo_algorithms.py",
            "game": "echo_engine/echo_interactive_games.py",
            "file": "echo_engine/echo_file_operations.py",
            "math": "echo_engine/echo_math_utils.py",
            "network": "echo_engine/echo_network_utils.py",
        }

        for category, location in location_mapping.items():
            if category in request_lower:
                return location

        # 기본 위치
        return f"echo_generated_{signature.lower()}_script.py"

    def _analyze_context_continuity(self, request: str) -> Dict[str, Any]:
        """컨텍스트 연속성 분석"""
        context = {
            "related_sessions": [],
            "ongoing_projects": [],
            "suggested_connections": [],
        }

        # TODO: 과거 세션 기록과 비교하여 연속성 분석
        # TODO: 진행 중인 프로젝트와의 연관성 분석
        # TODO: 추천 연결 고리 제안

        return context

    def generate_pre_implementation_report(self, analysis: Dict[str, Any]) -> str:
        """구현 전 분석 보고서 생성"""

        report = f"""
🔍 Echo 구조 분석 보고서
요청: "{analysis['request']}"
시그니처: {analysis['signature']}
분석 시각: {analysis['timestamp']}

"""

        # 기존 기능 분석
        if analysis["existing_functions"]:
            report += "♻️ 활용 가능한 기존 기능:\n"
            for func in analysis["existing_functions"][:3]:
                report += (
                    f"- {func['name']} (관련도: {func['relevance_score']:.1f}/5.0)\n"
                )
                report += f"  위치: {func['file_path']}\n"
                report += f"  설명: {func['description'][:80]}...\n\n"

        # 중복 위험도
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        risk_text = {"low": "낮음", "medium": "보통", "high": "높음"}
        report += f"{risk_emoji[analysis['duplicate_risk']]} 중복 위험도: {risk_text[analysis['duplicate_risk']]}\n\n"

        # 추천 접근법
        report += f"💡 추천 접근법:\n{analysis['recommended_approach']}\n\n"

        # 제안 위치
        report += f"📁 제안 파일 위치: {analysis['suggested_file_location']}\n\n"

        # 유사 구현 패턴
        if analysis["similar_implementations"]:
            report += "📋 참고할 수 있는 유사 패턴:\n"
            for pattern in analysis["similar_implementations"][:2]:
                report += f"- {pattern['pattern']} 패턴\n"
                for example in pattern["examples"][:2]:
                    report += f"  예시: {example['name']} ({example['file_path']})\n"

        return report

    def update_implementation_feedback(
        self,
        request: str,
        chosen_approach: str,
        created_files: List[str],
        success: bool,
    ):
        """구현 결과 피드백 업데이트"""

        feedback = {
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "chosen_approach": chosen_approach,
            "created_files": created_files,
            "success": success,
        }

        # 사용된 기능들의 usage_count 업데이트
        if success and created_files:
            for file_path in created_files:
                # 파일에서 사용된 함수들 추적하여 usage_count 증가
                # TODO: 실제 사용된 함수 분석 후 업데이트
                pass

        # 피드백 로그 저장
        feedback_file = (
            Path(__file__).parent.parent / "data" / "implementation_feedback.jsonl"
        )
        feedback_file.parent.mkdir(exist_ok=True, parents=True)

        try:
            with open(feedback_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(feedback, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️ 피드백 저장 실패: {e}")


# 전역 인스턴스
_structure_analyzer = None


def get_structure_analyzer() -> EchoStructureAnalyzer:
    """구조 분석기 싱글톤 인스턴스 반환"""
    global _structure_analyzer
    if _structure_analyzer is None:
        _structure_analyzer = EchoStructureAnalyzer()
    return _structure_analyzer
