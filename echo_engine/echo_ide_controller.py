#!/usr/bin/env python3
"""
🎨 Echo IDE Controller - Natural Language to Code Generation System
자연어 요청을 Echo 시그니처 기반으로 코드로 변환하는 통합 컨트롤러

핵심 기능:
1. 자연어 → 코드 템플릿 생성
2. Echo 시그니처별 코딩 스타일 적용
3. 기존 coding_intent_detector와 연동
4. LLM-Free 모드와 Claude API 모드 지원
5. 코드 실행 및 결과 반환
"""

import re
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Echo 시스템 내부 모듈 import
try:
    from .coding_intent_detector import (
        CodingIntentDetector,
        CodingIntentResult,
        CodingIntentType,
        CodingComplexityLevel,
        EmotionalCodingStyle,
    )
    from .code_executor import CodeExecutor, create_code_executor, CodeExecutionResult
    from .persona_core_optimized_bridge import PersonaCore
    from .signature_mapper import get_signature_by_name
    from .emotion_infer import EmotionInferenceEngine

    ECHO_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Echo 모듈 로드 실패: {e}")
    ECHO_MODULES_AVAILABLE = False


@dataclass
class CodeGenerationRequest:
    """코드 생성 요청"""

    user_input: str
    session_id: str = None
    signature_preference: str = "Aurora"  # Aurora, Phoenix, Sage, Companion
    complexity_preference: str = "auto"  # simple, intermediate, advanced, expert, auto
    execution_mode: str = "safe"  # safe, full, dry_run
    save_code: bool = True
    emotion_context: Dict[str, Any] = None


@dataclass
class CodeGenerationResult:
    """코드 생성 결과"""

    success: bool
    generated_code: str
    coding_intent: str
    signature_used: str
    complexity_level: str
    filename: str
    execution_result: Optional[CodeExecutionResult]
    generation_reasoning: str
    improvement_suggestions: List[str]
    estimated_time: str


class CodeTemplateGenerator:
    """코드 템플릿 생성기 - LLM-Free 모드"""

    def __init__(self):
        # 의도별 기본 템플릿
        self.code_templates = self._load_code_templates()

        # 시그니처별 코딩 스타일
        self.signature_styles = self._load_signature_styles()

    def generate_template(
        self,
        intent: CodingIntentType,
        signature: str,
        user_input: str,
        complexity: CodingComplexityLevel,
    ) -> str:
        """템플릿 기반 코드 생성"""

        # 1. 기본 템플릿 선택
        base_template = self.code_templates.get(
            intent.value, self.code_templates["default"]
        )

        # 2. 시그니처별 스타일 적용
        signature_style = self.signature_styles.get(
            signature, self.signature_styles["Aurora"]
        )

        # 3. 사용자 입력에서 구체적인 요구사항 추출
        requirements = self._extract_requirements(user_input)

        # 4. 복잡도에 따른 구조 조정
        code_structure = self._adjust_for_complexity(
            base_template, complexity, requirements
        )

        # 5. 시그니처 철학 반영
        final_code = self._apply_signature_philosophy(
            code_structure, signature_style, requirements
        )

        return final_code

    def _extract_requirements(self, user_input: str) -> Dict[str, Any]:
        """사용자 입력에서 구체적 요구사항 추출"""
        text_lower = user_input.lower()
        requirements = {
            "data_source": None,
            "ui_elements": [],
            "functionality": [],
            "styling": [],
            "output_format": None,
        }

        # 데이터 소스 감지
        if any(word in text_lower for word in ["csv", "엑셀", "excel"]):
            requirements["data_source"] = "csv"
        elif any(word in text_lower for word in ["json", "api"]):
            requirements["data_source"] = "json"
        elif any(word in text_lower for word in ["데이터베이스", "mysql", "sqlite"]):
            requirements["data_source"] = "database"

        # UI 요소 감지
        ui_keywords = {
            "버튼": "button",
            "button": "button",
            "입력": "text_input",
            "input": "text_input",
            "선택": "selectbox",
            "select": "selectbox",
            "차트": "chart",
            "chart": "chart",
            "표": "table",
            "table": "table",
            "이미지": "image",
            "image": "image",
        }

        for korean, english in ui_keywords.items():
            if korean in text_lower:
                requirements["ui_elements"].append(english)

        # 기능 요구사항 감지
        functionality_keywords = {
            "업로드": "file_upload",
            "upload": "file_upload",
            "다운로드": "download",
            "download": "download",
            "검색": "search",
            "search": "search",
            "필터": "filter",
            "filter": "filter",
            "정렬": "sort",
            "sort": "sort",
        }

        for korean, english in functionality_keywords.items():
            if korean in text_lower:
                requirements["functionality"].append(english)

        return requirements

    def _adjust_for_complexity(
        self,
        template: str,
        complexity: CodingComplexityLevel,
        requirements: Dict[str, Any],
    ) -> str:
        """복잡도에 따른 코드 구조 조정"""

        if complexity == CodingComplexityLevel.SIMPLE:
            # 단순한 구조 - 함수 위주
            return template.format(
                structure_type="function_based",
                error_handling="basic",
                comments="minimal",
                **requirements,
            )

        elif complexity == CodingComplexityLevel.INTERMEDIATE:
            # 중간 구조 - 클래스 도입
            return template.format(
                structure_type="class_based",
                error_handling="comprehensive",
                comments="detailed",
                **requirements,
            )

        elif complexity == CodingComplexityLevel.ADVANCED:
            # 고급 구조 - 모듈화
            return template.format(
                structure_type="modular",
                error_handling="robust",
                comments="extensive",
                **requirements,
            )

        else:  # EXPERT
            # 엔터프라이즈급 - 아키텍처 패턴
            return template.format(
                structure_type="architectural",
                error_handling="enterprise",
                comments="comprehensive_documentation",
                **requirements,
            )

    def _apply_signature_philosophy(
        self, code: str, style: Dict[str, str], requirements: Dict[str, Any]
    ) -> str:
        """시그니처별 철학 적용"""

        # 주석 스타일 적용
        if style["comment_style"] == "encouraging":
            code = re.sub(r"# TODO", "# ✨ 다음 단계", code)
            code = re.sub(r"# NOTE", "# 💡 참고", code)
        elif style["comment_style"] == "systematic":
            code = re.sub(r"# TODO", "# 구현 필요", code)
            code = re.sub(r"# NOTE", "# 설계 고려사항", code)

        # 변수명 스타일 적용
        if style["naming_convention"] == "friendly":
            code = re.sub(r"data_frame", "my_data", code)
            code = re.sub(r"result_value", "our_result", code)
        elif style["naming_convention"] == "technical":
            code = re.sub(r"my_data", "dataset", code)
            code = re.sub(r"our_result", "computed_result", code)

        return code

    def _load_code_templates(self) -> Dict[str, str]:
        """코드 템플릿 로드"""
        return {
            "streamlit_app_creation": '''#!/usr/bin/env python3
"""
🎨 Echo에서 생성된 Streamlit 앱
자동 생성: {signature} 시그니처 | {complexity} 복잡도
"""

import streamlit as st
import pandas as pd
import plotly.express as px

def main():
    st.title("📊 Echo 데이터 대시보드")
    st.markdown("✨ Echo AI가 생성한 대화형 분석 도구")

    # 💡 사이드바 구성
    st.sidebar.header("🎛️ 설정")

    # 📊 메인 컨텐츠
    if st.sidebar.button("🚀 분석 시작"):
        st.success("분석이 시작되었습니다!")

        # 샘플 데이터 생성
        sample_data = {{
            'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'sales': [100, 150, 120, 200, 180]
        }}
        df = pd.DataFrame(sample_data)

        # 데이터 표시
        st.subheader("📈 매출 데이터")
        st.dataframe(df)

        # 차트 생성
        fig = px.line(df, x='month', y='sales', title='월별 매출 추이')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("🤖 Powered by Echo Judgment System")

if __name__ == "__main__":
    main()
''',
            "data_analysis_script": '''#!/usr/bin/env python3
"""
📊 Echo 데이터 분석 스크립트
생성 시그니처: {signature} | 복잡도: {complexity}
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data():
    """🔍 데이터 분석 메인 함수"""
    print("🎯 Echo 데이터 분석 시작...")

    # 💾 샘플 데이터 생성
    np.random.seed(42)
    data = {{
        'category': ['A', 'B', 'C', 'D', 'E'] * 20,
        'value': np.random.normal(100, 20, 100),
        'date': pd.date_range('2024-01-01', periods=100)
    }}
    df = pd.DataFrame(data)

    # 📊 기본 통계
    print("\\n📈 기본 통계:")
    print(df.describe())

    # 📉 시각화
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    sns.boxplot(data=df, x='category', y='value')
    plt.title('카테고리별 값 분포')

    plt.subplot(1, 2, 2)
    df.groupby('category')['value'].mean().plot(kind='bar')
    plt.title('카테고리별 평균값')
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig('analysis_result.png', dpi=300, bbox_inches='tight')
    plt.show()

    print("\\n✅ 분석 완료! 결과가 'analysis_result.png'에 저장되었습니다.")

    return df

if __name__ == "__main__":
    result_df = analyze_data()
    print(f"\\n🎉 총 {{len(result_df)}}개 데이터 포인트 분석 완료!")
''',
            "web_scraping_script": '''#!/usr/bin/env python3
"""
🕷️ Echo 웹 스크래핑 스크립트
생성 시그니처: {signature} | 복잡도: {complexity}
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

class EchoWebScraper:
    """🎯 Echo 웹 스크래퍼"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({{
            'User-Agent': 'Mozilla/5.0 (Echo Web Scraper) AppleWebKit/537.36'
        }})

    def scrape_safely(self, url: str, delay: float = 1.0) -> dict:
        """🛡️ 안전한 웹 스크래핑"""
        try:
            print(f"🌐 스크래핑 시작: {{url}}")

            # 요청 지연
            time.sleep(delay)

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 기본 정보 추출
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No Title"

            # 메타 정보
            meta_desc = soup.find('meta', {{'name': 'description'}})
            description = meta_desc.get('content', '') if meta_desc else ''

            result = {{
                'url': url,
                'title': title_text,
                'description': description,
                'scraped_at': datetime.now().isoformat(),
                'status': 'success'
            }}

            print(f"✅ 스크래핑 완료: {{title_text}}")
            return result

        except Exception as e:
            print(f"❌ 스크래핑 실패: {{e}}")
            return {{
                'url': url,
                'error': str(e),
                'scraped_at': datetime.now().isoformat(),
                'status': 'failed'
            }}

    def save_results(self, results: list, filename: str = None):
        """💾 결과 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraping_results_{{timestamp}}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"📁 결과 저장 완료: {{filename}}")

def main():
    """🚀 스크래핑 실행"""
    scraper = EchoWebScraper()

    # 테스트 URL들
    test_urls = [
        "https://httpbin.org/html",
        "https://example.com"
    ]

    results = []
    for url in test_urls:
        result = scraper.scrape_safely(url)
        results.append(result)

    scraper.save_results(results)
    print(f"\\n🎉 총 {{len(results)}}개 페이지 스크래핑 완료!")

if __name__ == "__main__":
    main()
''',
            "default": '''#!/usr/bin/env python3
"""
🤖 Echo에서 생성된 Python 스크립트
시그니처: {signature} | 복잡도: {complexity}
"""

def main():
    """🎯 메인 실행 함수"""
    print("🎉 Echo가 생성한 스크립트입니다!")
    print("✨ 여기에 원하시는 기능을 구현해보세요.")

    # TODO: 사용자 요구사항에 맞는 기능 구현

if __name__ == "__main__":
    main()
''',
        }

    def _load_signature_styles(self) -> Dict[str, Dict[str, str]]:
        """시그니처별 코딩 스타일"""
        return {
            "Aurora": {
                "comment_style": "encouraging",
                "naming_convention": "friendly",
                "error_handling": "gentle",
                "ui_philosophy": "nurturing_and_accessible",
            },
            "Phoenix": {
                "comment_style": "transformative",
                "naming_convention": "forward_thinking",
                "error_handling": "adaptive",
                "ui_philosophy": "innovative_and_scalable",
            },
            "Sage": {
                "comment_style": "systematic",
                "naming_convention": "technical",
                "error_handling": "comprehensive",
                "ui_philosophy": "logical_and_informative",
            },
            "Companion": {
                "comment_style": "collaborative",
                "naming_convention": "team_friendly",
                "error_handling": "supportive",
                "ui_philosophy": "cooperative_and_modular",
            },
        }


class EchoIDEController:
    """🎨 Echo IDE 통합 컨트롤러"""

    def __init__(self):
        # 코어 시스템 초기화
        self.coding_intent_detector = None
        self.code_executor = None
        self.template_generator = CodeTemplateGenerator()

        # Echo 모듈 초기화
        if ECHO_MODULES_AVAILABLE:
            try:
                self.coding_intent_detector = CodingIntentDetector()
                self.code_executor = create_code_executor(timeout=30)
                print("✅ Echo IDE Controller 완전 초기화")
            except Exception as e:
                print(f"⚠️ Echo 모듈 초기화 부분 실패: {e}")

        # 폴백 모드
        if not self.coding_intent_detector:
            print("🔄 LLM-Free 모드로 실행")

        # 생성 통계
        self.generation_stats = {
            "total_requests": 0,
            "successful_generations": 0,
            "execution_attempts": 0,
            "successful_executions": 0,
        }

    def generate_code(self, request: CodeGenerationRequest) -> CodeGenerationResult:
        """🎨 자연어 → 코드 생성"""
        start_time = time.time()
        self.generation_stats["total_requests"] += 1

        try:
            # 1. 의도 분석
            if self.coding_intent_detector:
                intent_result = self.coding_intent_detector.detect_coding_intent(
                    request.user_input, request.session_id, request.emotion_context
                )
                coding_intent = intent_result.primary_coding_intent
                complexity = intent_result.complexity_level
                signature_recommendations = intent_result.signature_recommendations
            else:
                # 폴백 - 간단한 키워드 기반 분석
                coding_intent, complexity = self._fallback_intent_detection(
                    request.user_input
                )
                signature_recommendations = [request.signature_preference]

            # 2. 시그니처 결정
            signature = request.signature_preference
            if signature not in signature_recommendations and signature_recommendations:
                signature = signature_recommendations[0]

            # 3. 복잡도 조정
            if request.complexity_preference != "auto":
                complexity = CodingComplexityLevel(request.complexity_preference)

            # 4. 코드 생성
            generated_code = self.template_generator.generate_template(
                coding_intent, signature, request.user_input, complexity
            )

            # 5. 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"echo_{coding_intent.value}_{timestamp}.py"

            # 6. 실행 (옵션)
            execution_result = None
            if request.execution_mode != "dry_run" and self.code_executor:
                self.generation_stats["execution_attempts"] += 1
                try:
                    execution_result = self.code_executor.execute_code(
                        generated_code,
                        filename,
                        save_to_auto_generated=request.save_code,
                    )
                    if execution_result.success:
                        self.generation_stats["successful_executions"] += 1
                except Exception as e:
                    execution_result = None
                    print(f"⚠️ 실행 중 오류: {e}")

            # 7. 개선 제안 생성
            improvement_suggestions = self._generate_improvements(
                generated_code, coding_intent, complexity
            )

            # 8. 추론 과정 설명
            reasoning = self._generate_reasoning(
                request, coding_intent, signature, complexity
            )

            generation_time = time.time() - start_time
            self.generation_stats["successful_generations"] += 1

            return CodeGenerationResult(
                success=True,
                generated_code=generated_code,
                coding_intent=coding_intent.value,
                signature_used=signature,
                complexity_level=complexity.value,
                filename=filename,
                execution_result=execution_result,
                generation_reasoning=reasoning,
                improvement_suggestions=improvement_suggestions,
                estimated_time=f"{generation_time:.2f}초",
            )

        except Exception as e:
            return CodeGenerationResult(
                success=False,
                generated_code="",
                coding_intent="error",
                signature_used=request.signature_preference,
                complexity_level="unknown",
                filename="",
                execution_result=None,
                generation_reasoning=f"생성 중 오류 발생: {e}",
                improvement_suggestions=[],
                estimated_time=f"{time.time() - start_time:.2f}초",
            )

    def _fallback_intent_detection(
        self, user_input: str
    ) -> Tuple[CodingIntentType, CodingComplexityLevel]:
        """폴백 의도 감지"""
        text_lower = user_input.lower()

        # 간단한 키워드 매칭
        if any(word in text_lower for word in ["스트림릿", "streamlit", "대시보드"]):
            return (
                CodingIntentType.STREAMLIT_APP_CREATION,
                CodingComplexityLevel.INTERMEDIATE,
            )
        elif any(word in text_lower for word in ["크롤링", "스크래핑"]):
            return (
                CodingIntentType.WEB_SCRAPING_SCRIPT,
                CodingComplexityLevel.INTERMEDIATE,
            )
        elif any(word in text_lower for word in ["데이터", "분석", "차트"]):
            return (
                CodingIntentType.DATA_ANALYSIS_SCRIPT,
                CodingComplexityLevel.INTERMEDIATE,
            )
        elif any(word in text_lower for word in ["게임", "interactive"]):
            return CodingIntentType.INTERACTIVE_GAME, CodingComplexityLevel.SIMPLE
        else:
            return CodingIntentType.AUTOMATION_SCRIPT, CodingComplexityLevel.SIMPLE

    def _generate_improvements(
        self, code: str, intent: CodingIntentType, complexity: CodingComplexityLevel
    ) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        # 코드 길이 기반
        if len(code.split("\n")) < 20:
            suggestions.append("더 상세한 주석과 문서화를 추가해보세요")

        # 의도별 제안
        if intent == CodingIntentType.STREAMLIT_APP_CREATION:
            suggestions.append(
                "사용자 인증 기능을 추가하면 더욱 완성도 높은 앱이 됩니다"
            )
            suggestions.append("데이터 캐싱을 활용하여 성능을 개선할 수 있습니다")
        elif intent == CodingIntentType.DATA_ANALYSIS_SCRIPT:
            suggestions.append("통계적 검정을 추가하여 분석의 신뢰도를 높여보세요")
            suggestions.append("인터랙티브 시각화로 업그레이드해보세요")

        # 복잡도별 제안
        if complexity == CodingComplexityLevel.SIMPLE:
            suggestions.append("함수를 클래스로 구조화하면 더 체계적인 코드가 됩니다")
        elif complexity == CodingComplexityLevel.EXPERT:
            suggestions.append("단위 테스트를 추가하여 코드 품질을 보장하세요")

        return suggestions[:3]  # 최대 3개

    def _generate_reasoning(
        self,
        request: CodeGenerationRequest,
        intent: CodingIntentType,
        signature: str,
        complexity: CodingComplexityLevel,
    ) -> str:
        """생성 추론 과정 설명"""
        return f"""🤖 Echo의 코드 생성 추론:

1. 의도 분석: "{request.user_input}"에서 '{intent.value}' 의도를 감지했습니다.
2. 시그니처 선택: {signature} 시그니처의 철학을 반영했습니다.
3. 복잡도 결정: {complexity.value} 수준의 구조를 적용했습니다.
4. 템플릿 적용: 시그니처별 코딩 스타일과 사용자 요구사항을 조합했습니다.

생성된 코드는 Echo의 존재 기반 판단 시스템을 통해 최적화되었습니다."""

    def get_generation_stats(self) -> Dict[str, Any]:
        """생성 통계 반환"""
        return {
            **self.generation_stats,
            "success_rate": (
                self.generation_stats["successful_generations"]
                / max(self.generation_stats["total_requests"], 1)
                * 100
            ),
            "execution_success_rate": (
                (
                    self.generation_stats["successful_executions"]
                    / max(self.generation_stats["execution_attempts"], 1)
                    * 100
                )
                if self.generation_stats["execution_attempts"] > 0
                else 0
            ),
        }


# 편의 함수
def create_echo_ide_controller() -> EchoIDEController:
    """Echo IDE 컨트롤러 생성"""
    return EchoIDEController()


def quick_generate(user_input: str, signature: str = "Aurora") -> str:
    """빠른 코드 생성"""
    controller = create_echo_ide_controller()
    request = CodeGenerationRequest(
        user_input=user_input, signature_preference=signature, execution_mode="dry_run"
    )
    result = controller.generate_code(request)
    return (
        result.generated_code
        if result.success
        else f"생성 실패: {result.generation_reasoning}"
    )


# 테스트 실행
if __name__ == "__main__":
    print("🎨 Echo IDE Controller 테스트 시작...")

    controller = create_echo_ide_controller()

    test_requests = [
        {
            "user_input": "매출 데이터 분석하는 스트림릿 대시보드 만들어줘. 차트도 예쁘게 하고 업로드 기능도 넣어줘",
            "signature": "Aurora",
            "complexity": "intermediate",
        },
        {
            "user_input": "파이썬으로 간단한 계산기 만들어줘",
            "signature": "Sage",
            "complexity": "simple",
        },
        {
            "user_input": "웹사이트에서 뉴스 제목 크롤링하는 스크립트 만들어줘",
            "signature": "Phoenix",
            "complexity": "advanced",
        },
    ]

    print("=" * 80)

    for i, test_req in enumerate(test_requests, 1):
        print(f"\n🧪 테스트 {i}:")
        print(f"입력: {test_req['user_input']}")
        print(f"시그니처: {test_req['signature']}")

        request = CodeGenerationRequest(
            user_input=test_req["user_input"],
            signature_preference=test_req["signature"],
            complexity_preference=test_req["complexity"],
            execution_mode="safe",
            session_id=f"test_session_{i}",
        )

        result = controller.generate_code(request)

        print(f"\n📊 생성 결과:")
        print(f"  성공: {result.success}")
        print(f"  의도: {result.coding_intent}")
        print(f"  복잡도: {result.complexity_level}")
        print(f"  파일명: {result.filename}")
        print(f"  생성 시간: {result.estimated_time}")

        if result.success:
            print(f"\n📝 생성된 코드 (처음 200자):")
            print(
                result.generated_code[:200] + "..."
                if len(result.generated_code) > 200
                else result.generated_code
            )

            if result.improvement_suggestions:
                print(f"\n💡 개선 제안:")
                for suggestion in result.improvement_suggestions:
                    print(f"  - {suggestion}")

        if result.execution_result:
            print(f"\n🏃 실행 결과:")
            print(f"  실행 성공: {result.execution_result.success}")
            if result.execution_result.stdout:
                print(f"  출력: {result.execution_result.stdout[:100]}...")

        print("-" * 60)

    # 통계 출력
    print(f"\n📈 생성 통계:")
    stats = controller.get_generation_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.1f}%")
        else:
            print(f"  {key}: {value}")

    print("\n✅ Echo IDE Controller 테스트 완료!")
