import re
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
# from echo_engine.intent_infer import (

#!/usr/bin/env python3
"""
🎯 Coding Intent Detector - Enhanced
세밀한 코딩 의도 분류 및 감정 기반 코딩 스타일 추론

핵심 기능:
1. 자연어에서 구체적인 코딩 의도 추출 (15가지 유형)
2. KoSimCSE 감정 분석과 연동한 코딩 스타일 결정
3. 기존 intent_infer.py와 연계하여 확장된 의도 분류
4. 시그니처별 코딩 접근법 매핑
"""


# 기존 intent_infer.py와 연계
try:
    from echo_engine.intent_infer import (
        DetailedIntentType,
        EnhancedIntentInferenceEngine,
        IntentInferenceResult,
    )

    INTENT_ENGINE_AVAILABLE = True
except ImportError:
    print("⚠️ Intent Inference Engine not available")
    INTENT_ENGINE_AVAILABLE = False


class CodingIntentType(Enum):
    """세밀한 코딩 의도 분류"""

    # 웹 개발
    STREAMLIT_APP_CREATION = "streamlit_app_creation"
    FLASK_API_CREATION = "flask_api_creation"
    HTML_PAGE_CREATION = "html_page_creation"
    REACT_APP_CREATION = "react_app_creation"

    # 데이터 처리
    DATA_ANALYSIS_SCRIPT = "data_analysis_script"
    FILE_PROCESSOR_CREATION = "file_processor_creation"
    CSV_HANDLER_CREATION = "csv_handler_creation"
    JSON_PROCESSOR_CREATION = "json_processor_creation"

    # 자동화 및 스크립팅
    AUTOMATION_SCRIPT = "automation_script"
    BATCH_PROCESSING = "batch_processing"
    WEB_SCRAPING_SCRIPT = "web_scraping_script"

    # 게임 및 인터랙티브
    INTERACTIVE_GAME = "interactive_game_creation"
    VISUALIZATION_TOOL = "visualization_tool"
    DASHBOARD_CREATION = "dashboard_creation"

    # 고급 알고리즘
    ALGORITHM_IMPLEMENTATION = "algorithm_implementation"


class CodingComplexityLevel(Enum):
    """코딩 복잡도 레벨"""

    SIMPLE = "simple"  # 기본 스크립트, 단순 함수
    INTERMEDIATE = "intermediate"  # 클래스, 모듈화된 코드
    ADVANCED = "advanced"  # 복잡한 로직, 다중 파일
    EXPERT = "expert"  # 아키텍처, 프레임워크 수준


@dataclass
class CodingIntentResult:
    """코딩 의도 분석 결과"""

    primary_coding_intent: CodingIntentType
    confidence: float
    complexity_level: CodingComplexityLevel
    suggested_language: str
    estimated_files: int
    required_libraries: List[str]
    emotional_context: Dict[str, Any]
    signature_recommendations: List[str]
    implementation_approach: str


@dataclass
class EmotionalCodingStyle:
    """감정 기반 코딩 스타일"""

    ui_elements: List[str]
    code_philosophy: str
    comment_style: str
    naming_convention: str
    error_handling_tone: str


class CodingIntentDetector:
    """🎯 코딩 의도 감지 엔진"""

    def __init__(self):
        # 기존 의도 추론 엔진 연계
        if INTENT_ENGINE_AVAILABLE:
            self.base_intent_engine = EnhancedIntentInferenceEngine()
        else:
            self.base_intent_engine = None

        # 코딩 의도 패턴 데이터베이스
        self.coding_intent_patterns = self._load_coding_patterns()

        # 감정-코딩스타일 매핑
        self.emotion_coding_mapping = self._build_emotion_coding_mapping()

        # 시그니처별 코딩 철학
        self.signature_coding_philosophy = self._build_signature_philosophy()

        # 복잡도 평가 지표
        self.complexity_indicators = self._build_complexity_indicators()

        print("🎯 Coding Intent Detector 초기화 완료")

    def detect_coding_intent(
        self,
        user_input: str,
        session_id: str = None,
        emotion_context: Dict[str, Any] = None,
    ) -> CodingIntentResult:
        """코딩 의도 종합 감지"""

        # 1. 기본 의도 분석 (기존 시스템 활용)
        base_intent_result = None
        if self.base_intent_engine and session_id:
            base_intent_result = self.base_intent_engine.infer_intent_and_rhythm(
                user_input, session_id, emotion_context
            )

        # 2. 구체적인 코딩 의도 분류
        coding_intent, confidence = self._classify_coding_intent(user_input)

        # 3. 복잡도 평가
        complexity_level = self._assess_coding_complexity(user_input)

        # 4. 언어 및 라이브러리 추천
        language, libraries = self._recommend_tech_stack(user_input, coding_intent)

        # 5. 파일 수 추정
        estimated_files = self._estimate_file_count(user_input, complexity_level)

        # 6. 감정 기반 코딩 스타일 결정
        emotional_context = emotion_context or {}

        # 7. 시그니처 추천
        signature_recommendations = self._recommend_signatures(
            coding_intent, emotional_context, complexity_level
        )

        # 8. 구현 접근법 결정
        implementation_approach = self._determine_implementation_approach(
            coding_intent, complexity_level, emotional_context
        )

        return CodingIntentResult(
            primary_coding_intent=coding_intent,
            confidence=confidence,
            complexity_level=complexity_level,
            suggested_language=language,
            estimated_files=estimated_files,
            required_libraries=libraries,
            emotional_context=emotional_context,
            signature_recommendations=signature_recommendations,
            implementation_approach=implementation_approach,
        )

    def _classify_coding_intent(self, text: str) -> Tuple[CodingIntentType, float]:
        """구체적인 코딩 의도 분류"""
        text_lower = text.lower()
        intent_scores = {}

        # 패턴 매칭을 통한 의도 점수 계산
        for intent_type, patterns in self.coding_intent_patterns.items():
            score = 0.0

            for pattern_info in patterns:
                if isinstance(pattern_info, dict):
                    # 가중치가 있는 키워드
                    for keyword, weight in pattern_info.items():
                        if keyword in text_lower:
                            score += weight
                else:
                    # 단순 키워드
                    if pattern_info in text_lower:
                        score += 1.0

            if score > 0:
                intent_scores[intent_type] = score

        # 컨텍스트 기반 보정
        intent_scores = self._apply_contextual_scoring(intent_scores, text_lower)

        if not intent_scores:
            return CodingIntentType.AUTOMATION_SCRIPT, 0.3

        # 최고 점수 의도 선택
        best_intent_str = max(intent_scores.items(), key=lambda x: x[1])[0]
        best_intent = CodingIntentType(best_intent_str)

        # 신뢰도 계산 (정규화)
        total_score = sum(intent_scores.values())
        confidence = (
            intent_scores[best_intent_str] / total_score if total_score > 0 else 0.3
        )

        return best_intent, min(confidence, 1.0)

    def _apply_contextual_scoring(
        self, scores: Dict[str, float], text: str
    ) -> Dict[str, float]:
        """컨텍스트 기반 점수 보정"""

        # 스트림릿 관련 강화
        if "streamlit" in text or "대시보드" in text or "시각화" in text:
            if "streamlit_app_creation" in scores:
                scores["streamlit_app_creation"] *= 1.5
            if "dashboard_creation" in scores:
                scores["dashboard_creation"] *= 1.3

        # 데이터 분석 관련
        if any(word in text for word in ["데이터", "분석", "차트", "그래프"]):
            if "data_analysis_script" in scores:
                scores["data_analysis_script"] *= 1.4
            if "visualization_tool" in scores:
                scores["visualization_tool"] *= 1.3

        # 웹 크롤링 관련
        if any(word in text for word in ["크롤링", "스크래핑", "웹사이트", "수집"]):
            if "web_scraping_script" in scores:
                scores["web_scraping_script"] *= 2.0

        # 게임 관련
        if any(word in text for word in ["게임", "퍼즐", "인터랙티브", "플레이"]):
            if "interactive_game" in scores:
                scores["interactive_game"] *= 1.8

        return scores

    def _assess_coding_complexity(self, text: str) -> CodingComplexityLevel:
        """코딩 복잡도 평가"""
        text_lower = text.lower()
        complexity_score = 0

        # 복잡도 지표별 점수 계산
        for indicator, score in self.complexity_indicators.items():
            if indicator in text_lower:
                complexity_score += score

        # 추가 휴리스틱
        # 다중 기능 요구사항
        feature_count = len(
            [word for word in ["기능", "특징", "옵션", "설정"] if word in text_lower]
        )
        complexity_score += feature_count * 2

        # 통합 요구사항
        integration_words = ["연동", "통합", "api", "데이터베이스", "서버"]
        integration_count = len(
            [word for word in integration_words if word in text_lower]
        )
        complexity_score += integration_count * 3

        # 복잡도 레벨 결정
        if complexity_score >= 15:
            return CodingComplexityLevel.EXPERT
        elif complexity_score >= 10:
            return CodingComplexityLevel.ADVANCED
        elif complexity_score >= 5:
            return CodingComplexityLevel.INTERMEDIATE
        else:
            return CodingComplexityLevel.SIMPLE

    def _recommend_tech_stack(
        self, text: str, coding_intent: CodingIntentType
    ) -> Tuple[str, List[str]]:
        """기술 스택 추천"""
        text_lower = text.lower()

        # 의도별 기본 기술 스택
        tech_stack_mapping = {
            CodingIntentType.STREAMLIT_APP_CREATION: (
                "python",
                ["streamlit", "pandas", "plotly"],
            ),
            CodingIntentType.FLASK_API_CREATION: (
                "python",
                ["flask", "flask-restful", "requests"],
            ),
            CodingIntentType.HTML_PAGE_CREATION: ("html", ["bootstrap", "jquery"]),
            CodingIntentType.DATA_ANALYSIS_SCRIPT: (
                "python",
                ["pandas", "numpy", "matplotlib"],
            ),
            CodingIntentType.WEB_SCRAPING_SCRIPT: (
                "python",
                ["requests", "beautifulsoup4", "selenium"],
            ),
            CodingIntentType.INTERACTIVE_GAME: ("html", ["javascript", "css3"]),
            CodingIntentType.VISUALIZATION_TOOL: (
                "python",
                ["plotly", "bokeh", "seaborn"],
            ),
            CodingIntentType.ALGORITHM_IMPLEMENTATION: ("python", ["numpy", "scipy"]),
        }

        base_language, base_libraries = tech_stack_mapping.get(
            coding_intent, ("python", ["requests"])
        )

        # 텍스트 기반 라이브러리 추가
        additional_libraries = []

        library_keywords = {
            "mysql": ["mysql", "데이터베이스", "db"],
            "sqlite3": ["sqlite", "로컬db"],
            "opencv-python": ["이미지", "컴퓨터비전", "opencv"],
            "tensorflow": ["머신러닝", "딥러닝", "ai"],
            "discord.py": ["디스코드", "봇"],
            "psutil": ["시스템", "모니터링"],
            "schedule": ["스케줄", "자동화", "정기실행"],
        }

        for library, keywords in library_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                additional_libraries.append(library)

        return base_language, base_libraries + additional_libraries

    def _estimate_file_count(self, text: str, complexity: CodingComplexityLevel) -> int:
        """생성될 파일 수 추정"""
        text_lower = text.lower()

        base_files = {
            CodingComplexityLevel.SIMPLE: 1,
            CodingComplexityLevel.INTERMEDIATE: 2,
            CodingComplexityLevel.ADVANCED: 4,
            CodingComplexityLevel.EXPERT: 7,
        }

        file_count = base_files[complexity]

        # 추가 파일 요인
        if "css" in text_lower or "스타일" in text_lower:
            file_count += 1
        if "config" in text_lower or "설정" in text_lower:
            file_count += 1
        if "test" in text_lower or "테스트" in text_lower:
            file_count += 1
        if "api" in text_lower:
            file_count += 2

        return min(file_count, 10)  # 최대 10개 파일

    def _recommend_signatures(
        self,
        coding_intent: CodingIntentType,
        emotional_context: Dict[str, Any],
        complexity: CodingComplexityLevel,
    ) -> List[str]:
        """시그니처 추천"""

        recommendations = []
        primary_emotion = emotional_context.get("primary_emotion", "neutral")

        # 의도별 기본 시그니처 매핑
        intent_signature_mapping = {
            CodingIntentType.STREAMLIT_APP_CREATION: ["Aurora", "Companion"],
            CodingIntentType.DATA_ANALYSIS_SCRIPT: ["Sage", "Phoenix"],
            CodingIntentType.WEB_SCRAPING_SCRIPT: ["Phoenix", "Sage"],
            CodingIntentType.INTERACTIVE_GAME: ["Aurora", "Phoenix"],
            CodingIntentType.ALGORITHM_IMPLEMENTATION: ["Sage", "Phoenix"],
        }

        base_signatures = intent_signature_mapping.get(
            coding_intent, ["Aurora", "Sage"]
        )
        recommendations.extend(base_signatures)

        # 감정별 추가 추천
        emotion_signature_mapping = {
            "joy": ["Aurora", "Companion"],
            "curiosity": ["Sage", "Phoenix"],
            "anticipation": ["Phoenix", "Aurora"],
            "focus": ["Sage", "Companion"],
            "creativity": ["Phoenix", "Aurora"],
        }

        if primary_emotion in emotion_signature_mapping:
            emotion_signatures = emotion_signature_mapping[primary_emotion]
            for sig in emotion_signatures:
                if sig not in recommendations:
                    recommendations.append(sig)

        # 복잡도별 조정
        if complexity in [CodingComplexityLevel.ADVANCED, CodingComplexityLevel.EXPERT]:
            if "Sage" not in recommendations:
                recommendations.append("Sage")

        return recommendations[:3]  # 최대 3개 추천

    def _determine_implementation_approach(
        self,
        coding_intent: CodingIntentType,
        complexity: CodingComplexityLevel,
        emotional_context: Dict[str, Any],
    ) -> str:
        """구현 접근법 결정"""

        primary_emotion = emotional_context.get("primary_emotion", "neutral")

        # 기본 접근법
        base_approaches = {
            CodingIntentType.STREAMLIT_APP_CREATION: "사용자 친화적 UI 우선, 단계별 구현",
            CodingIntentType.DATA_ANALYSIS_SCRIPT: "데이터 무결성 중심, 시각화 강화",
            CodingIntentType.WEB_SCRAPING_SCRIPT: "견고한 에러 처리, 효율적 데이터 수집",
            CodingIntentType.INTERACTIVE_GAME: "재미있는 UX, 부드러운 애니메이션",
            CodingIntentType.ALGORITHM_IMPLEMENTATION: "최적화된 성능, 명확한 로직",
        }

        base_approach = base_approaches.get(coding_intent, "체계적이고 모듈화된 구현")

        # 감정별 접근법 조정
        emotional_adjustments = {
            "joy": " + 밝고 긍정적인 사용자 경험",
            "curiosity": " + 학습하기 쉬운 구조와 상세한 설명",
            "anticipation": " + 확장 가능한 아키텍처",
            "focus": " + 핵심 기능 중심의 간결한 구현",
            "anxiety": " + 안정적이고 신뢰할 수 있는 코드",
        }

        if primary_emotion in emotional_adjustments:
            base_approach += emotional_adjustments[primary_emotion]

        # 복잡도별 조정
        if complexity == CodingComplexityLevel.EXPERT:
            base_approach += " + 엔터프라이즈급 아키텍처 고려"
        elif complexity == CodingComplexityLevel.SIMPLE:
            base_approach += " + 초보자도 이해하기 쉬운 코드"

        return base_approach

    def get_emotional_coding_style(
        self, emotion: str, signature: str
    ) -> EmotionalCodingStyle:
        """감정과 시그니처 기반 코딩 스타일 반환"""

        # 기본 감정별 스타일
        emotion_base_style = self.emotion_coding_mapping.get(
            emotion,
            {
                "ui_elements": ["clean", "simple"],
                "code_philosophy": "straightforward_and_functional",
                "comment_style": "practical_explanations",
                "naming_convention": "descriptive_names",
                "error_handling_tone": "informative_messages",
            },
        )

        # 시그니처별 철학 반영
        signature_philosophy = self.signature_coding_philosophy.get(
            signature,
            {
                "ui_focus": "balanced",
                "code_style": "standard_practices",
                "comment_approach": "necessary_comments",
            },
        )

        # 통합된 스타일 생성
        return EmotionalCodingStyle(
            ui_elements=emotion_base_style["ui_elements"],
            code_philosophy=f"{emotion_base_style['code_philosophy']} + {signature_philosophy['code_style']}",
            comment_style=f"{emotion_base_style['comment_style']} + {signature_philosophy['comment_approach']}",
            naming_convention=emotion_base_style["naming_convention"],
            error_handling_tone=emotion_base_style["error_handling_tone"],
        )

    def _load_coding_patterns(self) -> Dict[str, List]:
        """코딩 의도 패턴 로드"""
        return {
            "streamlit_app_creation": [
                {"스트림릿": 2.0, "streamlit": 2.0, "대시보드": 1.5, "dashboard": 1.5},
                {"웹앱": 1.0, "web app": 1.0, "시각화": 1.5, "차트": 1.0},
            ],
            "flask_api_creation": [
                {"flask": 2.0, "api": 2.0, "서버": 1.5, "endpoint": 1.5},
                {"rest": 1.0, "웹서비스": 1.0},
            ],
            "html_page_creation": [
                {"html": 2.0, "웹페이지": 2.0, "webpage": 2.0, "사이트": 1.5},
                {"css": 1.0, "스타일": 1.0},
            ],
            "data_analysis_script": [
                {"데이터분석": 2.0, "data analysis": 2.0, "분석": 1.5, "데이터": 1.0},
                {"pandas": 1.5, "csv": 1.0, "excel": 1.0},
            ],
            "file_processor_creation": [
                {"파일처리": 2.0, "file processing": 2.0, "파일": 1.5},
                {"읽기": 1.0, "쓰기": 1.0, "변환": 1.5},
            ],
            "web_scraping_script": [
                {"크롤링": 2.5, "스크래핑": 2.5, "scraping": 2.0, "웹크롤러": 2.0},
                {"수집": 1.5, "웹사이트": 1.0, "beautifulsoup": 2.0},
            ],
            "automation_script": [
                {"자동화": 2.0, "automation": 2.0, "스케줄": 1.5, "정기실행": 1.5},
                {"반복": 1.0, "batch": 1.0},
            ],
            "interactive_game": [
                {"게임": 2.0, "game": 2.0, "퍼즐": 1.5, "인터랙티브": 2.0},
                {"플레이": 1.0, "interactive": 2.0},
            ],
            "visualization_tool": [
                {"시각화": 2.0, "visualization": 2.0, "차트": 1.5, "그래프": 1.5},
                {"plotly": 1.5, "matplotlib": 1.5},
            ],
            "algorithm_implementation": [
                {"알고리즘": 2.0, "algorithm": 2.0, "자료구조": 1.5, "구현": 1.0},
                {"트리": 1.5, "검색": 1.0, "정렬": 1.0},
            ],
        }

    def _build_emotion_coding_mapping(self) -> Dict[str, Dict[str, Any]]:
        """감정-코딩스타일 매핑 구축"""
        return {
            "joy": {
                "ui_elements": ["colorful", "animated", "cheerful", "bright"],
                "code_philosophy": "expressive_and_lively",
                "comment_style": "encouraging_and_positive",
                "naming_convention": "friendly_descriptive_names",
                "error_handling_tone": "gentle_and_helpful",
            },
            "anticipation": {
                "ui_elements": ["progressive", "interactive", "engaging", "modern"],
                "code_philosophy": "feature_rich_and_extensible",
                "comment_style": "future_focused_explanations",
                "naming_convention": "forward_thinking_names",
                "error_handling_tone": "constructive_guidance",
            },
            "curiosity": {
                "ui_elements": [
                    "exploratory",
                    "detailed",
                    "informative",
                    "educational",
                ],
                "code_philosophy": "well_documented_and_educational",
                "comment_style": "learning_focused_detailed_explanations",
                "naming_convention": "self_explaining_names",
                "error_handling_tone": "educational_error_messages",
            },
            "focus": {
                "ui_elements": ["clean", "minimal", "efficient", "purposeful"],
                "code_philosophy": "lean_and_efficient",
                "comment_style": "concise_essential_comments",
                "naming_convention": "precise_technical_names",
                "error_handling_tone": "direct_and_clear",
            },
            "anxiety": {
                "ui_elements": ["stable", "predictable", "secure", "reliable"],
                "code_philosophy": "robust_and_defensive",
                "comment_style": "reassuring_detailed_explanations",
                "naming_convention": "clear_unambiguous_names",
                "error_handling_tone": "supportive_and_informative",
            },
        }

    def _build_signature_philosophy(self) -> Dict[str, Dict[str, str]]:
        """시그니처별 코딩 철학 구축"""
        return {
            "Aurora": {
                "ui_focus": "user_experience_and_accessibility",
                "code_style": "readable_and_nurturing",
                "comment_approach": "guiding_and_explanatory",
            },
            "Phoenix": {
                "ui_focus": "innovation_and_scalability",
                "code_style": "modern_and_transformative",
                "comment_approach": "future_possibilities_focused",
            },
            "Sage": {
                "ui_focus": "information_and_logic",
                "code_style": "systematic_and_principled",
                "comment_approach": "theoretical_and_educational",
            },
            "Companion": {
                "ui_focus": "collaboration_and_teamwork",
                "code_style": "modular_and_cooperative",
                "comment_approach": "team_friendly_documentation",
            },
        }

    def _build_complexity_indicators(self) -> Dict[str, int]:
        """복잡도 지표 구축"""
        return {
            # 고복잡도 지표 (3-5점)
            "아키텍처": 5,
            "시스템": 4,
            "프레임워크": 4,
            "마이크로서비스": 5,
            "데이터베이스": 3,
            "orm": 3,
            "멀티스레드": 4,
            "비동기": 4,
            "머신러닝": 5,
            "딥러닝": 5,
            "ai": 4,
            "알고리즘": 3,
            "보안": 4,
            "인증": 3,
            "암호화": 4,
            # 중복잡도 지표 (2-3점)
            "api": 2,
            "rest": 2,
            "클래스": 2,
            "상속": 3,
            "디자인패턴": 3,
            "싱글톤": 3,
            "팩토리": 3,
            "테스트": 2,
            "유닛테스트": 2,
            "통합테스트": 3,
            "로깅": 2,
            "모니터링": 2,
            "배포": 3,
            # 저복잡도 지표 (1-2점)
            "함수": 1,
            "변수": 1,
            "반복문": 1,
            "조건문": 1,
            "파일읽기": 1,
            "파일쓰기": 1,
            "json": 1,
            "csv": 1,
            "출력": 1,
            "입력": 1,
            "계산": 1,
        }


# 편의 함수
def create_coding_intent_detector() -> CodingIntentDetector:
    """코딩 의도 감지기 생성"""
    return CodingIntentDetector()


# 테스트 실행
if __name__ == "__main__":
    print("🎯 Coding Intent Detector 테스트 시작...")

    detector = create_coding_intent_detector()

    test_cases = [
        {
            "input": "스트림릿으로 매출 데이터 분석 대시보드 만들어줘. 차트도 예쁘게 하고 파일 업로드 기능도 넣어줘",
            "emotion": {"primary_emotion": "anticipation", "emotion_intensity": 0.8},
        },
        {
            "input": "파이썬으로 네이버 뉴스 크롤링하는 스크립트 만들어줘. JSON으로 저장하고 에러 처리도 잘 해줘",
            "emotion": {"primary_emotion": "focus", "emotion_intensity": 0.7},
        },
        {
            "input": "간단한 퍼즐 게임 만들어줘. HTML과 자바스크립트로 브라우저에서 플레이할 수 있게",
            "emotion": {"primary_emotion": "joy", "emotion_intensity": 0.9},
        },
        {
            "input": "이진 검색 트리 알고리즘 구현해줘. 삽입, 삭제, 검색 기능 모두 포함해서",
            "emotion": {"primary_emotion": "curiosity", "emotion_intensity": 0.6},
        },
    ]

    print("=" * 80)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔧 테스트 {i}:")
        print(f"입력: {test_case['input']}")

        result = detector.detect_coding_intent(
            test_case["input"],
            session_id=f"test_session_{i}",
            emotion_context=test_case["emotion"],
        )

        print(f"\n📊 분석 결과:")
        print(f"  🎯 코딩 의도: {result.primary_coding_intent.value}")
        print(f"  🎚️ 신뢰도: {result.confidence:.2f}")
        print(f"  📈 복잡도: {result.complexity_level.value}")
        print(f"  💻 추천 언어: {result.suggested_language}")
        print(f"  📁 예상 파일 수: {result.estimated_files}")
        print(f"  📦 필요 라이브러리: {', '.join(result.required_libraries)}")
        print(f"  🎭 추천 시그니처: {', '.join(result.signature_recommendations)}")
        print(f"  🛠️ 구현 접근법: {result.implementation_approach}")

        # 감정 기반 코딩 스타일 예시
        if result.signature_recommendations:
            style = detector.get_emotional_coding_style(
                test_case["emotion"]["primary_emotion"],
                result.signature_recommendations[0],
            )
            print(f"  💡 코딩 스타일: {style.code_philosophy}")

        print("-" * 60)

    print("\n✅ Coding Intent Detector 테스트 완료!")
