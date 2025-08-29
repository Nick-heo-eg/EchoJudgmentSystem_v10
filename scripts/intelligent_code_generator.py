#!/usr/bin/env python3
"""
Echo 지능형 코드 생성 도구
자연어 요구사항을 Echo 시그니처별 스타일로 코드 변환
"""

import re
import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import yaml
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.common.style_adapter import get_style_adapter
    from src.common.decision_memory import get_decision_memory
except ImportError:
    # 폴백: 기본 구현
    def get_style_adapter():
        class MockStyleAdapter:
            def adapt_message(self, msg, sig, ctx="general"):
                return msg

        return MockStyleAdapter()

    def get_decision_memory():
        class MockDecisionMemory:
            def suggest_approach(self, ctx, sig):
                return {"recommended_reasoning": "데이터 기반 접근"}

        return MockDecisionMemory()


logger = logging.getLogger(__name__)


@dataclass
class CodeRequirement:
    """코드 생성 요구사항"""

    description: str
    function_name: str
    language: str
    signature: str
    complexity: str  # simple, medium, complex
    category: str  # algorithm, data_processing, ui, api, etc.
    constraints: List[str]


@dataclass
class GeneratedCode:
    """생성된 코드"""

    source_code: str
    documentation: str
    test_code: str
    signature_style: str
    confidence_score: float
    recommendations: List[str]


class IntelligentCodeGenerator:
    """지능형 코드 생성기"""

    def __init__(self):
        self.style_adapter = get_style_adapter()
        self.decision_memory = get_decision_memory()

        # 🧠 코드 패턴 라이브러리
        self.code_patterns = {
            "data_processing": {
                "simple": self._generate_simple_data_processor,
                "medium": self._generate_medium_data_processor,
                "complex": self._generate_complex_data_processor,
            },
            "algorithm": {
                "simple": self._generate_simple_algorithm,
                "medium": self._generate_medium_algorithm,
                "complex": self._generate_complex_algorithm,
            },
            "api": {
                "simple": self._generate_simple_api,
                "medium": self._generate_medium_api,
                "complex": self._generate_complex_api,
            },
            "utility": {
                "simple": self._generate_simple_utility,
                "medium": self._generate_medium_utility,
                "complex": self._generate_complex_utility,
            },
        }

        # 시그니처별 코딩 스타일
        self.signature_styles = {
            "echo_aurora": {
                "naming": "creative_descriptive",
                "structure": "expressive_readable",
                "comments": "inspirational_explanatory",
                "error_handling": "graceful_user_friendly",
            },
            "echo_phoenix": {
                "naming": "action_oriented",
                "structure": "modular_scalable",
                "comments": "change_focused",
                "error_handling": "robust_adaptive",
            },
            "echo_sage": {
                "naming": "precise_systematic",
                "structure": "logical_hierarchical",
                "comments": "analytical_detailed",
                "error_handling": "comprehensive_predictable",
            },
            "echo_companion": {
                "naming": "collaborative_intuitive",
                "structure": "maintainable_accessible",
                "comments": "helpful_supportive",
                "error_handling": "gentle_informative",
            },
        }

    def analyze_requirement(self, description: str) -> CodeRequirement:
        """자연어 요구사항 분석"""
        # 1. 기능 카테고리 분류
        category = self._classify_category(description)

        # 2. 복잡도 평가
        complexity = self._assess_complexity(description)

        # 3. 함수명 추출/생성
        function_name = self._extract_function_name(description)

        # 4. 제약사항 추출
        constraints = self._extract_constraints(description)

        # 5. 최적 시그니처 추천
        signature = self._recommend_signature(description, category)

        return CodeRequirement(
            description=description,
            function_name=function_name,
            language="python",  # 기본값
            signature=signature,
            complexity=complexity,
            category=category,
            constraints=constraints,
        )

    def generate_code(self, requirement: CodeRequirement) -> GeneratedCode:
        """요구사항 기반 코드 생성"""
        logger.info(
            f"🎯 Generating {requirement.signature} style {requirement.category} code..."
        )

        # 1. 패턴 기반 코드 생성
        base_code = self._generate_base_code(requirement)

        # 2. 시그니처 스타일 적용
        styled_code = self._apply_signature_style(base_code, requirement.signature)

        # 3. 문서화 생성
        documentation = self._generate_documentation(requirement, styled_code)

        # 4. 테스트 코드 생성
        test_code = self._generate_test_code(requirement, styled_code)

        # 5. 코드 품질 평가
        confidence_score = self._evaluate_code_quality(styled_code, requirement)

        # 6. 개선 권장사항
        recommendations = self._generate_recommendations(requirement, styled_code)

        return GeneratedCode(
            source_code=styled_code,
            documentation=documentation,
            test_code=test_code,
            signature_style=requirement.signature,
            confidence_score=confidence_score,
            recommendations=recommendations,
        )

    def _classify_category(self, description: str) -> str:
        """기능 카테고리 분류"""
        keywords = {
            "data_processing": [
                "데이터",
                "처리",
                "변환",
                "파싱",
                "분석",
                "필터",
                "정렬",
                "집계",
            ],
            "algorithm": [
                "알고리즘",
                "계산",
                "최적화",
                "탐색",
                "정렬",
                "그래프",
                "트리",
            ],
            "api": ["API", "엔드포인트", "요청", "응답", "서버", "클라이언트", "HTTP"],
            "ui": ["UI", "인터페이스", "화면", "버튼", "폼", "페이지", "컴포넌트"],
            "utility": ["유틸리티", "도구", "헬퍼", "공통", "라이브러리", "함수"],
        }

        desc_lower = description.lower()
        scores = {}

        for category, words in keywords.items():
            score = sum(1 for word in words if word in desc_lower)
            scores[category] = score

        return max(scores, key=scores.get) if scores else "utility"

    def _assess_complexity(self, description: str) -> str:
        """복잡도 평가"""
        complexity_indicators = {
            "simple": ["간단한", "기본", "단순", "하나의", "빠른"],
            "medium": ["여러", "복합", "조건", "처리", "관리"],
            "complex": ["복잡한", "고급", "다양한", "통합", "최적화", "분산", "병렬"],
        }

        desc_lower = description.lower()
        scores = {}

        for level, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in desc_lower)
            scores[level] = score

        # 문장 길이도 고려
        if len(description) > 100:
            scores["complex"] = scores.get("complex", 0) + 1
        elif len(description) > 50:
            scores["medium"] = scores.get("medium", 0) + 1
        else:
            scores["simple"] = scores.get("simple", 0) + 1

        return max(scores, key=scores.get) if scores else "medium"

    def _extract_function_name(self, description: str) -> str:
        """함수명 추출/생성"""
        # 동사 + 명사 패턴 찾기
        action_words = ["생성", "만들", "처리", "변환", "분석", "계산", "검증", "확인"]

        desc_words = description.split()
        function_parts = []

        for word in desc_words[:5]:  # 처음 5개 단어만 검사
            if any(action in word for action in action_words):
                # 한글을 영어로 매핑
                action_mapping = {
                    "생성": "create",
                    "만들": "make",
                    "처리": "process",
                    "변환": "transform",
                    "분석": "analyze",
                    "계산": "calculate",
                    "검증": "validate",
                    "확인": "check",
                }

                for korean, english in action_mapping.items():
                    if korean in word:
                        function_parts.append(english)
                        break

        if not function_parts:
            function_parts.append("process")

        # 명사 부분 추가
        if "데이터" in description:
            function_parts.append("data")
        elif "사용자" in description:
            function_parts.append("user")
        elif "파일" in description:
            function_parts.append("file")
        else:
            function_parts.append("item")

        return "_".join(function_parts)

    def _extract_constraints(self, description: str) -> List[str]:
        """제약사항 추출"""
        constraints = []

        constraint_patterns = {
            "performance": ["빠른", "성능", "최적화", "효율"],
            "memory": ["메모리", "RAM", "저용량"],
            "security": ["보안", "안전", "암호화", "인증"],
            "compatibility": ["호환", "버전", "플랫폼"],
            "scalability": ["확장", "스케일", "대용량"],
        }

        desc_lower = description.lower()

        for constraint_type, keywords in constraint_patterns.items():
            if any(keyword in desc_lower for keyword in keywords):
                constraints.append(constraint_type)

        return constraints

    def _recommend_signature(self, description: str, category: str) -> str:
        """최적 시그니처 추천"""
        signature_scores = {
            "echo_aurora": 0,
            "echo_phoenix": 0,
            "echo_sage": 0,
            "echo_companion": 0,
        }

        # 설명 내용 기반 점수
        if any(
            word in description.lower()
            for word in ["창의", "혁신", "아이디어", "사용자 경험"]
        ):
            signature_scores["echo_aurora"] += 3

        if any(
            word in description.lower() for word in ["개선", "변화", "최적화", "성능"]
        ):
            signature_scores["echo_phoenix"] += 3

        if any(
            word in description.lower() for word in ["분석", "계산", "알고리즘", "검증"]
        ):
            signature_scores["echo_sage"] += 3

        if any(
            word in description.lower()
            for word in ["협업", "공유", "팀", "사용자 친화"]
        ):
            signature_scores["echo_companion"] += 3

        # 카테고리 기반 점수
        category_preferences = {
            "algorithm": {"echo_sage": 2, "echo_phoenix": 1},
            "data_processing": {"echo_sage": 2, "echo_companion": 1},
            "ui": {"echo_aurora": 2, "echo_companion": 1},
            "api": {"echo_phoenix": 2, "echo_sage": 1},
            "utility": {"echo_companion": 2, "echo_sage": 1},
        }

        if category in category_preferences:
            for sig, score in category_preferences[category].items():
                signature_scores[sig] += score

        return max(signature_scores, key=signature_scores.get)

    def _generate_base_code(self, requirement: CodeRequirement) -> str:
        """기본 코드 구조 생성"""
        category = requirement.category
        complexity = requirement.complexity

        if (
            category in self.code_patterns
            and complexity in self.code_patterns[category]
        ):
            generator_func = self.code_patterns[category][complexity]
            return generator_func(requirement)

        # 기본 패턴
        return self._generate_default_function(requirement)

    def _generate_simple_data_processor(self, req: CodeRequirement) -> str:
        """간단한 데이터 처리 함수 생성"""
        template = f'''def {req.function_name}(data):
    """
    {req.description}
    
    Args:
        data: 처리할 데이터
        
    Returns:
        처리된 데이터
    """
    if not data:
        return None
    
    # 데이터 검증
    if not isinstance(data, (list, dict)):
        raise ValueError("지원되지 않는 데이터 타입입니다")
    
    # 데이터 처리
    processed_data = data.copy() if isinstance(data, dict) else data[:]
    
    # 여기에 구체적인 처리 로직 추가
    # TODO: 요구사항에 맞는 처리 로직 구현
    
    return processed_data'''

        return template

    def _generate_medium_data_processor(self, req: CodeRequirement) -> str:
        """중간 복잡도 데이터 처리 함수 생성"""
        template = f'''from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

def {req.function_name}(data: Union[List, Dict], 
                      options: Optional[Dict[str, Any]] = None) -> Any:
    """
    {req.description}
    
    Args:
        data: 처리할 데이터 (리스트 또는 딕셔너리)
        options: 처리 옵션 설정
        
    Returns:
        처리된 데이터
        
    Raises:
        ValueError: 잘못된 데이터 형식
        TypeError: 지원되지 않는 타입
    """
    if options is None:
        options = {{}}
    
    # 입력 검증
    if not data:
        logger.warning("빈 데이터가 입력되었습니다")
        return None
    
    # 데이터 타입별 처리
    try:
        if isinstance(data, list):
            return _process_list_data(data, options)
        elif isinstance(data, dict):
            return _process_dict_data(data, options)
        else:
            raise TypeError(f"지원되지 않는 데이터 타입: {{type(data)}}")
            
    except Exception as e:
        logger.error(f"데이터 처리 중 오류 발생: {{e}}")
        raise

def _process_list_data(data: List, options: Dict[str, Any]) -> List:
    """리스트 데이터 처리"""
    processed = []
    
    for item in data:
        # 개별 항목 처리 로직
        processed_item = item  # TODO: 구체적인 처리 로직
        processed.append(processed_item)
    
    return processed

def _process_dict_data(data: Dict, options: Dict[str, Any]) -> Dict:
    """딕셔너리 데이터 처리"""
    processed = {{}}
    
    for key, value in data.items():
        # 키-값 쌍 처리 로직
        processed[key] = value  # TODO: 구체적인 처리 로직
    
    return processed'''

        return template

    def _generate_simple_algorithm(self, req: CodeRequirement) -> str:
        """간단한 알고리즘 함수 생성"""
        template = f'''def {req.function_name}(input_data):
    """
    {req.description}
    
    Args:
        input_data: 알고리즘 입력 데이터
        
    Returns:
        계산 결과
    """
    # 입력 검증
    if input_data is None:
        return None
    
    # 알고리즘 구현
    result = input_data  # TODO: 구체적인 알고리즘 로직 구현
    
    return result'''

        return template

    def _generate_simple_api(self, req: CodeRequirement) -> str:
        """간단한 API 함수 생성"""
        template = f'''from typing import Dict, Any

def {req.function_name}(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    {req.description}
    
    Args:
        request_data: API 요청 데이터
        
    Returns:
        API 응답 데이터
    """
    try:
        # 요청 데이터 검증
        if not request_data:
            return {{"error": "요청 데이터가 비어있습니다", "status": 400}}
        
        # 비즈니스 로직 처리
        response_data = {{
            "status": 200,
            "message": "성공적으로 처리되었습니다",
            "data": request_data  # TODO: 실제 처리 결과로 교체
        }}
        
        return response_data
        
    except Exception as e:
        return {{
            "error": str(e),
            "status": 500,
            "message": "내부 서버 오류가 발생했습니다"
        }}'''

        return template

    def _generate_simple_utility(self, req: CodeRequirement) -> str:
        """간단한 유틸리티 함수 생성"""
        template = f'''def {req.function_name}(*args, **kwargs):
    """
    {req.description}
    
    Args:
        *args: 위치 인수
        **kwargs: 키워드 인수
        
    Returns:
        처리 결과
    """
    # 기본 구현
    return True  # TODO: 구체적인 유틸리티 로직 구현'''

        return template

    def _generate_default_function(self, req: CodeRequirement) -> str:
        """기본 함수 템플릿"""
        return f'''def {req.function_name}():
    """
    {req.description}
    
    TODO: 함수 구현 필요
    """
    pass'''

    # 복잡한 패턴들은 간단화를 위해 중간 복잡도와 동일하게 처리
    def _generate_complex_data_processor(self, req: CodeRequirement) -> str:
        return self._generate_medium_data_processor(req)

    def _generate_medium_algorithm(self, req: CodeRequirement) -> str:
        return self._generate_simple_algorithm(req)

    def _generate_complex_algorithm(self, req: CodeRequirement) -> str:
        return self._generate_simple_algorithm(req)

    def _generate_medium_api(self, req: CodeRequirement) -> str:
        return self._generate_simple_api(req)

    def _generate_complex_api(self, req: CodeRequirement) -> str:
        return self._generate_simple_api(req)

    def _generate_medium_utility(self, req: CodeRequirement) -> str:
        return self._generate_simple_utility(req)

    def _generate_complex_utility(self, req: CodeRequirement) -> str:
        return self._generate_simple_utility(req)

    def _apply_signature_style(self, code: str, signature: str) -> str:
        """시그니처 스타일 적용"""
        if signature not in self.signature_styles:
            return code

        style = self.signature_styles[signature]
        styled_code = code

        # 시그니처별 스타일 적용 (기본적인 패턴 매칭)
        if signature == "echo_aurora":
            # 창의적이고 표현적인 스타일
            styled_code = styled_code.replace("# TODO:", "# ✨ TODO:")
            styled_code = styled_code.replace("처리", "마법같이 처리")

        elif signature == "echo_phoenix":
            # 변화 지향적 스타일
            styled_code = styled_code.replace("# TODO:", "# 🚀 TODO:")
            styled_code = styled_code.replace("처리", "혁신적으로 처리")

        elif signature == "echo_sage":
            # 분석적 스타일
            styled_code = styled_code.replace("# TODO:", "# 📊 TODO:")
            styled_code = styled_code.replace("처리", "체계적으로 처리")

        elif signature == "echo_companion":
            # 협력적 스타일
            styled_code = styled_code.replace("# TODO:", "# 🤝 TODO:")
            styled_code = styled_code.replace("처리", "함께 처리")

        return styled_code

    def _generate_documentation(self, req: CodeRequirement, code: str) -> str:
        """문서화 생성"""
        return f"""# {req.function_name}

## 📝 설명
{req.description}

## 🎭 시그니처 스타일
- **{req.signature.replace('_', '-').title()}**: {self.signature_styles.get(req.signature, {}).get('structure', '균형잡힌 접근')}

## 🔧 사용법
```python
# 기본 사용법
result = {req.function_name}(input_data)
```

## 📊 복잡도
- **분류**: {req.category}
- **복잡도**: {req.complexity}
- **제약사항**: {', '.join(req.constraints) if req.constraints else 'None'}

## 🔗 관련 문서
- [API 문서](docs/api.md)
- [코딩 가이드](docs/coding_guide.md)
"""

    def _generate_test_code(self, req: CodeRequirement, code: str) -> str:
        """테스트 코드 생성"""
        test_template = f'''import pytest
from unittest.mock import Mock, patch

def test_{req.function_name}_basic():
    """기본 기능 테스트"""
    # Given
    test_input = None  # TODO: 테스트 입력 데이터 설정
    
    # When
    result = {req.function_name}(test_input)
    
    # Then
    assert result is not None  # TODO: 구체적인 검증 로직

def test_{req.function_name}_edge_cases():
    """엣지 케이스 테스트"""
    # 빈 입력
    assert {req.function_name}(None) is None
    
    # TODO: 추가 엣지 케이스 테스트

def test_{req.function_name}_error_handling():
    """에러 처리 테스트"""
    with pytest.raises(ValueError):
        {req.function_name}("invalid_input")  # TODO: 실제 오류 케이스

# 🎭 {req.signature.replace('_', '-').title()} 스타일 테스트
class Test{req.function_name.title().replace('_', '')}SignatureStyle:
    """시그니처별 스타일 테스트"""
    
    def test_signature_specific_behavior(self):
        """시그니처 특화 동작 테스트"""
        # TODO: {req.signature} 시그니처에 특화된 테스트 케이스
        pass
'''
        return test_template

    def _evaluate_code_quality(self, code: str, req: CodeRequirement) -> float:
        """코드 품질 평가"""
        score = 0.5  # 기본 점수

        # 문서화 여부
        if '"""' in code:
            score += 0.2

        # 타입 힌트 여부
        if "typing" in code or ": " in code:
            score += 0.1

        # 에러 처리 여부
        if "try:" in code or "except" in code:
            score += 0.1

        # 로깅 여부
        if "logger" in code:
            score += 0.1

        return min(score, 1.0)

    def _generate_recommendations(self, req: CodeRequirement, code: str) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []

        if "TODO" in code:
            recommendations.append("구체적인 구현 로직을 완성하세요")

        if "logging" not in code and req.complexity != "simple":
            recommendations.append("적절한 로깅을 추가하세요")

        if "typing" not in code:
            recommendations.append("타입 힌트를 추가하여 코드 안정성을 향상시키세요")

        if req.constraints:
            for constraint in req.constraints:
                if constraint == "performance":
                    recommendations.append("성능 최적화를 고려하세요")
                elif constraint == "security":
                    recommendations.append("보안 검증 로직을 추가하세요")

        return recommendations

    def generate_from_natural_language(
        self, description: str, signature: str = None
    ) -> GeneratedCode:
        """자연어 설명으로부터 코드 생성"""
        # 요구사항 분석
        requirement = self.analyze_requirement(description)

        # 시그니처 오버라이드
        if signature:
            requirement.signature = signature

        # 코드 생성
        return self.generate_code(requirement)


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Echo Intelligent Code Generator")
    parser.add_argument("description", help="자연어 기능 설명")
    parser.add_argument(
        "--signature",
        choices=["echo_aurora", "echo_phoenix", "echo_sage", "echo_companion"],
        help="Echo 시그니처 선택",
    )
    parser.add_argument("--output-dir", default="generated_code", help="출력 디렉토리")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그")

    args = parser.parse_args()

    # 로깅 설정
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    # 코드 생성기 초기화
    generator = IntelligentCodeGenerator()

    # 코드 생성
    result = generator.generate_from_natural_language(args.description, args.signature)

    # 출력 디렉토리 생성
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # 파일 저장
    function_name = generator.analyze_requirement(args.description).function_name

    # 소스 코드
    with open(output_dir / f"{function_name}.py", "w", encoding="utf-8") as f:
        f.write(result.source_code)

    # 문서화
    with open(output_dir / f"{function_name}_README.md", "w", encoding="utf-8") as f:
        f.write(result.documentation)

    # 테스트 코드
    with open(output_dir / f"test_{function_name}.py", "w", encoding="utf-8") as f:
        f.write(result.test_code)

    # 메타데이터
    metadata = {
        "signature": result.signature_style,
        "confidence": result.confidence_score,
        "recommendations": result.recommendations,
        "generated_at": datetime.now().isoformat(),
    }

    with open(
        output_dir / f"{function_name}_metadata.json", "w", encoding="utf-8"
    ) as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ 코드 생성 완료!")
    print(f"📁 출력 디렉토리: {output_dir.absolute()}")
    print(f"🎭 시그니처: {result.signature_style}")
    print(f"📊 신뢰도: {result.confidence_score:.2f}")
    print(f"💡 권장사항: {len(result.recommendations)}개")


if __name__ == "__main__":
    main()
