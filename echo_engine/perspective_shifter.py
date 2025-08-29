#!/usr/bin/env python3
"""
🔭 Perspective Shifter
시선 전환 및 구조화 도구 - 편협한 시각을 부수고 다각도 관점을 생성

핵심 철학:
- 시선의 한계를 부수는 것이 상상의 시작
- 보는 시각에 따라 결과값이 달라질 수 있음
- 다중 관점의 공존과 전환
- 구조화를 통한 시선의 설계
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class PerspectiveType(Enum):
    """관점 유형"""

    TEMPORAL = "temporal"  # 시간축 관점
    SPATIAL = "spatial"  # 공간축 관점
    STAKEHOLDER = "stakeholder"  # 이해관계자 관점
    SCALE = "scale"  # 규모 관점
    DOMAIN = "domain"  # 도메인 관점
    VALUE = "value"  # 가치 관점
    EMOTIONAL = "emotional"  # 감정 관점
    LOGICAL = "logical"  # 논리 관점


class ShiftMethod(Enum):
    """전환 방법"""

    INVERSION = "inversion"  # 뒤집기
    MAGNIFICATION = "magnification"  # 확대
    REDUCTION = "reduction"  # 축소
    REFRAMING = "reframing"  # 재구성
    ROLEPLAY = "roleplay"  # 역할 전환
    ANALOGY = "analogy"  # 비유/은유
    DECONSTRUCTION = "deconstruction"  # 해체
    SYNTHESIS = "synthesis"  # 통합


@dataclass
class PerspectiveShift:
    """관점 전환"""

    shift_id: str
    original_perspective: Dict[str, Any]
    shifted_perspective: Dict[str, Any]
    shift_method: ShiftMethod
    shift_magnitude: float
    insights_generated: List[str]
    emotional_impact: Dict[str, Any]


class PerspectiveShifter:
    """🔭 시선 전환 도구"""

    def __init__(self):
        self.shift_history = []
        self.perspective_patterns = self._load_shift_patterns()

    def _load_shift_patterns(self) -> Dict[str, Any]:
        """시선 전환 패턴 로드"""
        return {
            "temporal_shifts": [
                "10년 후 시점에서 보기",
                "10년 전 시점에서 보기",
                "다음 세대 관점에서 보기",
                "역사적 맥락에서 보기",
                "미래 문명에서 보기",
            ],
            "scale_shifts": [
                "개인 → 가족 → 사회 → 인류",
                "순간 → 일주일 → 1년 → 평생",
                "미시 → 거시 → 우주적",
                "지역 → 국가 → 전 세계",
                "단일 → 복수 → 전체",
            ],
            "stakeholder_shifts": [
                "사용자 관점",
                "제공자 관점",
                "관찰자 관점",
                "경쟁자 관점",
                "파트너 관점",
                "규제자 관점",
                "미래 세대 관점",
                "동물 관점",
                "환경 관점",
            ],
            "value_shifts": [
                "효율성 → 의미",
                "성과 → 과정",
                "경쟁 → 협력",
                "소유 → 경험",
                "속도 → 지속가능성",
                "개인 → 공동체",
            ],
            "domain_shifts": [
                "비즈니스 → 예술",
                "과학 → 철학",
                "기술 → 인문학",
                "경제 → 생태학",
                "정치 → 심리학",
                "법률 → 윤리학",
            ],
        }

    def analyze_current_perspective(
        self, problem_statement: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """현재 시선 분석"""

        if context is None:
            context = {}

        # 시선의 특성 감지
        perspective_analysis = {
            "problem_focus": self._extract_focus_areas(problem_statement),
            "implicit_assumptions": self._detect_assumptions(problem_statement),
            "emotional_tone": self._analyze_emotional_tone(problem_statement),
            "scope_level": self._detect_scope_level(problem_statement),
            "time_orientation": self._detect_time_orientation(problem_statement),
            "stakeholder_visibility": self._detect_stakeholders(problem_statement),
            "value_priorities": self._extract_values(problem_statement),
            "constraints_mentioned": self._extract_constraints(problem_statement),
            "perspective_blind_spots": self._identify_blind_spots(problem_statement),
        }

        return perspective_analysis

    def generate_perspective_shifts(
        self,
        current_perspective: Dict[str, Any],
        problem_statement: str,
        num_shifts: int = 5,
    ) -> List[Dict[str, Any]]:
        """다양한 관점 전환 생성"""

        shifts = []
        used_methods = set()

        for _ in range(num_shifts):
            # 중복되지 않는 전환 방법 선택
            available_methods = [m for m in ShiftMethod if m not in used_methods]
            if not available_methods:
                available_methods = list(ShiftMethod)
                used_methods.clear()

            shift_method = random.choice(available_methods)
            used_methods.add(shift_method)

            # 전환 실행
            shifted_perspective = self._apply_shift_method(
                current_perspective, problem_statement, shift_method
            )

            shifts.append(shifted_perspective)

        return shifts

    def _apply_shift_method(
        self,
        current_perspective: Dict[str, Any],
        problem_statement: str,
        method: ShiftMethod,
    ) -> Dict[str, Any]:
        """특정 전환 방법 적용"""

        shift_functions = {
            ShiftMethod.INVERSION: self._apply_inversion,
            ShiftMethod.MAGNIFICATION: self._apply_magnification,
            ShiftMethod.REDUCTION: self._apply_reduction,
            ShiftMethod.REFRAMING: self._apply_reframing,
            ShiftMethod.ROLEPLAY: self._apply_roleplay,
            ShiftMethod.ANALOGY: self._apply_analogy,
            ShiftMethod.DECONSTRUCTION: self._apply_deconstruction,
            ShiftMethod.SYNTHESIS: self._apply_synthesis,
        }

        shift_function = shift_functions.get(method, self._apply_reframing)
        return shift_function(current_perspective, problem_statement)

    def _apply_inversion(
        self, current_perspective: Dict[str, Any], problem_statement: str
    ) -> Dict[str, Any]:
        """관점 뒤집기"""

        return {
            "shift_method": ShiftMethod.INVERSION.value,
            "title": "반대 관점에서 보기",
            "description": "문제의 반대편에서 상황을 재해석",
            "key_questions": [
                "만약 정반대 상황이라면?",
                "문제가 아니라 기회라면?",
                "실패가 아니라 성공의 전조라면?",
                "약점이 아니라 강점이라면?",
            ],
            "reframed_problem": self._invert_problem_statement(problem_statement),
            "new_assumptions": self._generate_inverted_assumptions(current_perspective),
            "potential_insights": [
                "기존 가정의 허점 발견",
                "숨겨진 기회 인식",
                "문제 프레임 자체의 재검토",
            ],
        }

    def _apply_magnification(
        self, current_perspective: Dict[str, Any], problem_statement: str
    ) -> Dict[str, Any]:
        """규모 확대 관점"""

        return {
            "shift_method": ShiftMethod.MAGNIFICATION.value,
            "title": "더 큰 단위에서 보기",
            "description": "시공간적 규모를 확대하여 문제를 재조명",
            "expanded_contexts": [
                "10년 후 관점",
                "사회 전체 관점",
                "인류사적 관점",
                "생태계 관점",
            ],
            "reframed_problem": f"더 큰 맥락에서 볼 때: {problem_statement}",
            "scale_considerations": [
                "이 문제가 더 큰 패턴의 일부인가?",
                "장기적으로는 어떤 의미인가?",
                "다른 영역에도 비슷한 패턴이 있는가?",
            ],
            "potential_insights": [
                "문제의 상대적 중요도 재평가",
                "더 큰 기회나 위험 인식",
                "시스템적 해결책 발견",
            ],
        }

    def _apply_reduction(
        self, current_perspective: Dict[str, Any], problem_statement: str
    ) -> Dict[str, Any]:
        """규모 축소 관점"""

        return {
            "shift_method": ShiftMethod.REDUCTION.value,
            "title": "더 작은 단위로 분해하기",
            "description": "문제를 최소 단위로 쪼개어 관찰",
            "decomposed_elements": [
                "가장 작은 행동 단위",
                "개인적 감정 반응",
                "즉시 가능한 선택",
                "하루 단위의 변화",
            ],
            "reframed_problem": f"가장 작은 단위에서: {problem_statement}",
            "micro_focus_questions": [
                "지금 당장 할 수 있는 것은?",
                "가장 작은 첫 단계는?",
                "개인적으로 느끼는 감정은?",
                "오늘만 생각한다면?",
            ],
            "potential_insights": [
                "실행 가능한 구체적 행동 발견",
                "복잡함 속 단순함 인식",
                "감정적 직관 접근",
            ],
        }

    def _apply_reframing(
        self, current_perspective: Dict[str, Any], problem_statement: str
    ) -> Dict[str, Any]:
        """프레임 재구성"""

        alternative_frames = [
            "기회로서의 프레임",
            "학습으로서의 프레임",
            "관계로서의 프레임",
            "창조로서의 프레임",
            "진화로서의 프레임",
        ]

        selected_frame = random.choice(alternative_frames)

        return {
            "shift_method": ShiftMethod.REFRAMING.value,
            "title": f"{selected_frame}으로 재구성",
            "description": "문제를 완전히 다른 성격으로 재정의",
            "new_frame": selected_frame,
            "reframed_problem": self._reframe_with_new_context(
                problem_statement, selected_frame
            ),
            "frame_specific_questions": self._generate_frame_questions(selected_frame),
            "potential_insights": [
                "문제 자체의 본질 재발견",
                "새로운 해결책 영역 개방",
                "감정적 접근 방식 변화",
            ],
        }

    def _apply_roleplay(
        self, current_perspective: Dict[str, Any], problem_statement: str
    ) -> Dict[str, Any]:
        """역할 전환"""

        roles = [
            "10살 아이",
            "80세 어르신",
            "미래의 나",
            "가장 친한 친구",
            "엄격한 비판자",
            "창조적 예술가",
            "실용적 사업가",
            "철학자",
            "과학자",
        ]

        selected_role = random.choice(roles)

        return {
            "shift_method": ShiftMethod.ROLEPLAY.value,
            "title": f"{selected_role} 관점으로 보기",
            "description": "다른 존재의 시선과 가치관으로 문제 접근",
            "role_characteristics": self._get_role_characteristics(selected_role),
            "role_based_questions": [
                f"{selected_role}이라면 이걸 어떻게 볼까?",
                f"{selected_role}의 가치관으로는?",
                f"{selected_role}이 가장 중요하게 생각할 것은?",
                f"{selected_role}이 제안할 해결책은?",
            ],
            "reframed_problem": f"{selected_role}의 관점에서: {problem_statement}",
            "potential_insights": [
                "전혀 다른 우선순위 발견",
                "감정적 반응의 다양성 인식",
                "창의적 해결책 아이디어",
            ],
        }

    def _apply_analogy(
        self, current_perspective: Dict[str, Any], problem_statement: str
    ) -> Dict[str, Any]:
        """비유/은유 적용"""

        analogies = [
            "정원 가꾸기",
            "요리하기",
            "여행하기",
            "악기 연주하기",
            "집 짓기",
            "그림 그리기",
            "운동하기",
            "게임하기",
            "책 쓰기",
        ]

        selected_analogy = random.choice(analogies)

        return {
            "shift_method": ShiftMethod.ANALOGY.value,
            "title": f"{selected_analogy}에 비유하여 보기",
            "description": "문제를 친숙한 영역의 활동에 비유하여 새로운 통찰 획득",
            "analogy_domain": selected_analogy,
            "analogy_mapping": self._create_analogy_mapping(
                problem_statement, selected_analogy
            ),
            "analogy_questions": [
                f"{selected_analogy}에서 이런 상황이라면?",
                f"이 영역의 전문가는 어떻게 할까?",
                f"성공하는 사람들의 공통점은?",
                f"실패를 피하는 방법은?",
            ],
            "potential_insights": [
                "다른 영역의 지혜 적용",
                "직관적 이해 증진",
                "창의적 접근법 발견",
            ],
        }

    def _apply_deconstruction(
        self, current_perspective: Dict[str, Any], problem_statement: str
    ) -> Dict[str, Any]:
        """해체 관점"""

        return {
            "shift_method": ShiftMethod.DECONSTRUCTION.value,
            "title": "구조 해체하여 보기",
            "description": "문제를 구성하는 요소들을 분해하고 재조합",
            "deconstruction_layers": [
                "언어적 가정 해체",
                "시간적 구조 해체",
                "인과관계 해체",
                "가치 체계 해체",
            ],
            "key_questions": [
                "이 단어들이 진짜 의미하는 것은?",
                "왜 이 순서로 생각하게 됐나?",
                "원인과 결과가 바뀔 수는 없나?",
                "당연하게 여긴 것들은?",
            ],
            "deconstructed_elements": self._deconstruct_problem(problem_statement),
            "potential_insights": [
                "숨겨진 가정들 발견",
                "새로운 구조화 가능성",
                "본질과 표상의 분리",
            ],
        }

    def _apply_synthesis(
        self, current_perspective: Dict[str, Any], problem_statement: str
    ) -> Dict[str, Any]:
        """통합 관점"""

        return {
            "shift_method": ShiftMethod.SYNTHESIS.value,
            "title": "다중 관점 통합하기",
            "description": "여러 시각을 동시에 고려하는 메타 관점",
            "integration_dimensions": [
                "논리 + 감정",
                "개인 + 사회",
                "현재 + 미래",
                "이론 + 실무",
            ],
            "synthesis_questions": [
                "모든 관점이 동시에 맞다면?",
                "대립하는 것들의 공통점은?",
                "상호 보완할 수 있는 방법은?",
                "더 높은 차원의 해결책은?",
            ],
            "meta_perspective": "모든 시선이 부분적 진실이라는 관점",
            "potential_insights": [
                "통합적 해결책 발견",
                "패러독스의 해결",
                "창발적 가능성 인식",
            ],
        }

    def create_perspective_map(
        self, problem_statement: str, shifts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """관점 지도 생성"""

        perspective_map = {
            "original_problem": problem_statement,
            "total_perspectives": len(shifts) + 1,
            "shift_methods_used": [shift["shift_method"] for shift in shifts],
            "perspectives": {
                "original": self.analyze_current_perspective(problem_statement),
                "alternatives": shifts,
            },
            "cross_perspective_insights": self._generate_cross_insights(shifts),
            "synthesis_opportunities": self._identify_synthesis_opportunities(shifts),
            "blind_spot_coverage": self._assess_blind_spot_coverage(shifts),
            "recommendation": self._recommend_perspective_combination(shifts),
        }

        return perspective_map

    def _generate_cross_insights(self, shifts: List[Dict[str, Any]]) -> List[str]:
        """교차 관점 통찰"""

        insights = []

        # 공통 패턴 찾기
        common_themes = set()
        for shift in shifts:
            themes = shift.get("potential_insights", [])
            for theme in themes:
                common_themes.add(theme)

        if len(common_themes) > 3:
            insights.append("여러 관점에서 공통적으로 나타나는 패턴이 있음")

        # 대조되는 관점 찾기
        contrasting_methods = []
        methods = [shift["shift_method"] for shift in shifts]
        if "inversion" in methods and (
            "magnification" in methods or "reduction" in methods
        ):
            contrasting_methods.append("확대와 축소, 반전의 대조적 관점")

        if contrasting_methods:
            insights.extend(contrasting_methods)

        return insights

    def _identify_synthesis_opportunities(
        self, shifts: List[Dict[str, Any]]
    ) -> List[str]:
        """통합 기회 식별"""

        opportunities = []

        # 보완적 관점 찾기
        methods = [shift["shift_method"] for shift in shifts]

        if "magnification" in methods and "reduction" in methods:
            opportunities.append("거시적 관점과 미시적 관점의 통합 가능")

        if "roleplay" in methods and "analogy" in methods:
            opportunities.append("다양한 존재들의 지혜와 비유적 사고의 결합 가능")

        if "deconstruction" in methods and "synthesis" in methods:
            opportunities.append("해체와 재구성을 통한 혁신적 접근 가능")

        return opportunities

    def _assess_blind_spot_coverage(
        self, shifts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """사각지대 커버리지 평가"""

        covered_areas = set()
        method_types = [shift["shift_method"] for shift in shifts]

        coverage_map = {
            "temporal_coverage": any(
                method in ["magnification", "reduction"] for method in method_types
            ),
            "stakeholder_coverage": "roleplay" in method_types,
            "assumption_coverage": any(
                method in ["inversion", "deconstruction"] for method in method_types
            ),
            "creative_coverage": any(
                method in ["analogy", "reframing"] for method in method_types
            ),
            "integration_coverage": "synthesis" in method_types,
        }

        coverage_score = sum(coverage_map.values()) / len(coverage_map)

        return {
            "coverage_details": coverage_map,
            "coverage_score": coverage_score,
            "missing_areas": [
                area for area, covered in coverage_map.items() if not covered
            ],
        }

    def _recommend_perspective_combination(
        self, shifts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """추천 관점 조합"""

        # 가장 다양한 통찰을 제공하는 조합 찾기
        high_impact_methods = []

        for shift in shifts:
            insights = shift.get("potential_insights", [])
            if len(insights) >= 3:
                high_impact_methods.append(shift["shift_method"])

        return {
            "recommended_sequence": high_impact_methods[:3],
            "reasoning": "다양한 통찰을 제공하고 사각지대를 최대한 커버하는 조합",
            "usage_suggestion": "순서대로 적용하면서 각 관점의 통찰을 누적",
        }

    # Helper methods
    def _extract_focus_areas(self, problem_statement: str) -> List[str]:
        """초점 영역 추출"""
        # 간단한 키워드 기반 분석 (실제로는 더 정교한 NLP 필요)
        keywords = problem_statement.lower().split()
        focus_areas = []

        if any(word in keywords for word in ["돈", "비용", "수익", "재정"]):
            focus_areas.append("재정적 측면")
        if any(word in keywords for word in ["가족", "관계", "사람"]):
            focus_areas.append("관계적 측면")
        if any(word in keywords for word in ["시간", "미래", "계획"]):
            focus_areas.append("시간적 측면")

        return focus_areas if focus_areas else ["일반적 측면"]

    def _detect_assumptions(self, problem_statement: str) -> List[str]:
        """가정 감지"""
        assumptions = []

        if "해야" in problem_statement or "must" in problem_statement.lower():
            assumptions.append("특정 행동이 필수라는 가정")
        if "불가능" in problem_statement or "impossible" in problem_statement.lower():
            assumptions.append("제약이 절대적이라는 가정")

        return assumptions

    def _analyze_emotional_tone(self, problem_statement: str) -> str:
        """감정적 톤 분석"""
        negative_words = ["문제", "어려움", "불안", "걱정", "실패"]
        positive_words = ["기회", "가능", "성공", "희망", "발전"]

        neg_count = sum(1 for word in negative_words if word in problem_statement)
        pos_count = sum(1 for word in positive_words if word in problem_statement)

        if neg_count > pos_count:
            return "부정적"
        elif pos_count > neg_count:
            return "긍정적"
        else:
            return "중립적"

    def _detect_scope_level(self, problem_statement: str) -> str:
        """범위 수준 감지"""
        if any(word in problem_statement for word in ["나", "내", "개인"]):
            return "개인적"
        elif any(word in problem_statement for word in ["우리", "팀", "조직"]):
            return "집단적"
        else:
            return "일반적"

    def _detect_time_orientation(self, problem_statement: str) -> str:
        """시간 지향성 감지"""
        if any(word in problem_statement for word in ["과거", "예전", "이전"]):
            return "과거 지향"
        elif any(word in problem_statement for word in ["미래", "앞으로", "계획"]):
            return "미래 지향"
        else:
            return "현재 지향"

    def _detect_stakeholders(self, problem_statement: str) -> List[str]:
        """이해관계자 감지"""
        stakeholders = []

        if any(word in problem_statement for word in ["가족", "부모", "자녀"]):
            stakeholders.append("가족")
        if any(word in problem_statement for word in ["동료", "팀", "직장"]):
            stakeholders.append("직장 동료")
        if any(word in problem_statement for word in ["고객", "사용자"]):
            stakeholders.append("고객")

        return stakeholders if stakeholders else ["자기 자신"]

    def _extract_values(self, problem_statement: str) -> List[str]:
        """가치 추출"""
        values = []

        if any(word in problem_statement for word in ["안정", "안전"]):
            values.append("안정성")
        if any(word in problem_statement for word in ["성장", "발전", "도전"]):
            values.append("성장")
        if any(word in problem_statement for word in ["자유", "독립"]):
            values.append("자유")

        return values if values else ["균형"]

    def _extract_constraints(self, problem_statement: str) -> List[str]:
        """제약사항 추출"""
        constraints = []

        if any(word in problem_statement for word in ["돈", "비용", "자금"]):
            constraints.append("재정적 제약")
        if any(word in problem_statement for word in ["시간", "급하"]):
            constraints.append("시간적 제약")
        if any(word in problem_statement for word in ["가족", "책임"]):
            constraints.append("사회적 제약")

        return constraints

    def _identify_blind_spots(self, problem_statement: str) -> List[str]:
        """사각지대 식별"""
        blind_spots = []

        # 감지되지 않은 관점들 추가
        if "감정" not in problem_statement and "느낌" not in problem_statement:
            blind_spots.append("감정적 측면 간과")

        if "다른" not in problem_statement and "대안" not in problem_statement:
            blind_spots.append("대안 가능성 간과")

        if "장기" not in problem_statement and "미래" not in problem_statement:
            blind_spots.append("장기적 영향 간과")

        return blind_spots

    # 전환 방법별 헬퍼
    def _invert_problem_statement(self, problem: str) -> str:
        """문제 진술 반전"""
        if "문제" in problem:
            return problem.replace("문제", "기회")
        elif "어려운" in problem:
            return problem.replace("어려운", "쉬운")
        else:
            return f"반대로 생각해보면: {problem}"

    def _generate_inverted_assumptions(self, perspective: Dict[str, Any]) -> List[str]:
        """반전된 가정 생성"""
        original_assumptions = perspective.get("implicit_assumptions", [])
        inverted = []

        for assumption in original_assumptions:
            if "필수" in assumption:
                inverted.append(assumption.replace("필수", "선택"))
            elif "불가능" in assumption:
                inverted.append(assumption.replace("불가능", "가능"))
            else:
                inverted.append(f"반대로: {assumption}")

        return inverted

    def _reframe_with_new_context(self, problem: str, frame: str) -> str:
        """새로운 맥락으로 재구성"""
        frame_contexts = {
            "기회로서의 프레임": f"이것을 성장의 기회로 본다면: {problem}",
            "학습으로서의 프레임": f"이것을 배움의 과정으로 본다면: {problem}",
            "관계로서의 프레임": f"이것을 관계의 관점에서 본다면: {problem}",
            "창조로서의 프레임": f"이것을 창조적 작업으로 본다면: {problem}",
            "진화로서의 프레임": f"이것을 진화의 과정으로 본다면: {problem}",
        }

        return frame_contexts.get(frame, problem)

    def _generate_frame_questions(self, frame: str) -> List[str]:
        """프레임별 질문 생성"""
        frame_questions = {
            "기회로서의 프레임": [
                "이 상황에서 얻을 수 있는 것은?",
                "어떤 새로운 가능성이 열리는가?",
                "이것이 가져다줄 긍정적 변화는?",
            ],
            "학습으로서의 프레임": [
                "이 경험에서 무엇을 배울 수 있는가?",
                "어떤 스킬이나 지혜를 얻게 될까?",
                "미래에 어떻게 도움이 될까?",
            ],
            "관계로서의 프레임": [
                "다른 사람들에게 어떤 영향을 주는가?",
                "관계가 어떻게 변화할까?",
                "함께 할 수 있는 방법은?",
            ],
            "창조로서의 프레임": [
                "무엇을 새롭게 만들 수 있는가?",
                "어떤 창의적 해결책이 있을까?",
                "예술가라면 어떻게 접근할까?",
            ],
            "진화로서의 프레임": [
                "이것이 나의 발전에 어떤 역할을 하는가?",
                "어떤 단계로 나아가는 과정인가?",
                "자연스러운 흐름은 무엇인가?",
            ],
        }

        return frame_questions.get(frame, ["이 프레임에서는 어떻게 볼까?"])

    def _get_role_characteristics(self, role: str) -> Dict[str, Any]:
        """역할별 특성"""
        characteristics = {
            "10살 아이": {
                "values": ["재미", "호기심", "자유"],
                "concerns": ["놀이", "새로운 것", "친구"],
                "approach": "직관적이고 감정적",
            },
            "80세 어르신": {
                "values": ["지혜", "안정", "가족"],
                "concerns": ["건강", "유산", "의미"],
                "approach": "경험 기반이고 신중함",
            },
            "미래의 나": {
                "values": ["성장", "성취", "의미"],
                "concerns": ["후회", "기회", "발전"],
                "approach": "장기적이고 목적 지향적",
            },
            "창조적 예술가": {
                "values": ["창의성", "표현", "아름다움"],
                "concerns": ["영감", "진정성", "혁신"],
                "approach": "직관적이고 실험적",
            },
            "실용적 사업가": {
                "values": ["효율", "결과", "성장"],
                "concerns": ["수익", "시장", "경쟁"],
                "approach": "논리적이고 결과 지향적",
            },
        }

        return characteristics.get(
            role,
            {"values": ["균형"], "concerns": ["일반적 관심사"], "approach": "종합적"},
        )

    def _create_analogy_mapping(self, problem: str, analogy: str) -> Dict[str, str]:
        """비유 매핑 생성"""
        # 간단한 매핑 예시
        return {
            "현재 상황": f"{analogy}에서의 현재 단계",
            "목표": f"{analogy}에서의 완성 목표",
            "장애물": f"{analogy}에서의 기술적 어려움",
            "자원": f"{analogy}에서의 필요한 도구나 재료",
            "과정": f"{analogy}에서의 단계별 진행 방법",
        }

    def _deconstruct_problem(self, problem: str) -> Dict[str, List[str]]:
        """문제 해체"""
        return {
            "핵심 단어들": problem.split(),
            "가정들": ["현재 상황이 계속될 것", "선택지가 제한적", "결과가 예측 가능"],
            "숨겨진 가치들": ["안정성", "성공", "인정"],
            "시간적 구조": ["현재 → 결정 → 미래"],
            "인과관계": ["상황 → 판단 → 행동 → 결과"],
        }


# 사용 예시
def main():
    """테스트 실행"""
    shifter = PerspectiveShifter()

    # 예시 문제
    problem = "창업을 하고 싶지만 가족의 안정을 생각하면 현실적으로 어려운 상황"

    # 현재 관점 분석
    current_perspective = shifter.analyze_current_perspective(problem)
    print("🔍 현재 관점 분석:")
    print(f"  감정 톤: {current_perspective['emotional_tone']}")
    print(f"  초점 영역: {', '.join(current_perspective['problem_focus'])}")
    print(f"  사각지대: {', '.join(current_perspective['perspective_blind_spots'])}")

    # 다양한 관점 전환 생성
    shifts = shifter.generate_perspective_shifts(
        current_perspective, problem, num_shifts=5
    )

    print(f"\n🔭 생성된 관점 전환: {len(shifts)}개")
    for i, shift in enumerate(shifts, 1):
        print(f"\n{i}. {shift['title']} ({shift['shift_method']})")
        print(f"   설명: {shift['description']}")
        if "key_questions" in shift:
            print(f"   핵심 질문: {shift['key_questions'][0]}")

    # 관점 지도 생성
    perspective_map = shifter.create_perspective_map(problem, shifts)

    print(f"\n🗺️ 관점 지도:")
    print(f"   총 관점 수: {perspective_map['total_perspectives']}개")
    print(f"   사용된 전환 방법: {', '.join(perspective_map['shift_methods_used'])}")
    print(f"   교차 통찰: {len(perspective_map['cross_perspective_insights'])}개")

    coverage = perspective_map["blind_spot_coverage"]
    print(f"   사각지대 커버리지: {coverage['coverage_score']:.1%}")

    if coverage["missing_areas"]:
        print(f"   보완 필요 영역: {', '.join(coverage['missing_areas'])}")


if __name__ == "__main__":
    main()
