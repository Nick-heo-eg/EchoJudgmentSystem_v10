#!/usr/bin/env python3
"""
🧭 Loop Router - 판단 흐름 분기 및 경로 결정

입력 및 상황에 따른 최적 판단 흐름을 결정하는 라우팅 엔진.
현재는 legacy adapter 중심이지만, 향후 다양한 AGI 판단 경로로 확장 예정.

핵심 역할:
1. 입력 분석을 통한 판단 복잡도 평가
2. 컨텍스트 기반 최적 판단 경로 선택
3. 다중 판단 경로 가중치 계산
4. 동적 라우팅 규칙 적용
"""

import re
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class RouteType(Enum):
    """판단 경로 타입"""

    LEGACY = "legacy"  # 기존 judgment_loop 사용
    AGI_NATIVE = "agi_native"  # AGI 네이티브 판단 (미래)
    HYBRID = "hybrid"  # 혼합 판단
    META_COGNITIVE = "meta_cognitive"  # 메타인지적 판단
    EMOTIONAL_DEEP = "emotional_deep"  # 감정 심층 분석
    CREATIVE_FLOW = "creative_flow"  # 창의적 사고 흐름


@dataclass
class JudgmentRoute:
    """판단 경로 정의"""

    route_type: RouteType
    weight: float
    confidence: float
    reasoning: str
    parameters: Dict[str, Any]
    estimated_time: float


class LoopRouter:
    """🧭 판단 루프 라우터"""

    def __init__(self):
        self.version = "1.0.0"
        self.routing_stats = {
            "total_routes": 0,
            "route_distribution": {},
            "successful_routes": 0,
            "routing_time_total": 0.0,
        }

        # 라우팅 규칙 설정
        self.routing_rules = self._initialize_routing_rules()

        print("🧭 Loop Router v1.0 초기화 완료")

    def route_judgment(
        self, user_input: str, context: Dict[str, Any]
    ) -> List[JudgmentRoute]:
        """🎯 메인 라우팅 함수"""
        self.routing_stats["total_routes"] += 1

        # 1. 입력 분석
        input_analysis = self._analyze_input(user_input)

        # 2. 컨텍스트 분석
        context_analysis = self._analyze_context(context)

        # 3. 라우팅 규칙 적용
        candidate_routes = self._apply_routing_rules(input_analysis, context_analysis)

        # 4. 경로 가중치 계산
        weighted_routes = self._calculate_route_weights(
            candidate_routes, input_analysis, context_analysis
        )

        # 5. 최적 경로 선택 (현재는 상위 1개, 향후 다중 경로 지원)
        selected_routes = self._select_optimal_routes(weighted_routes, max_routes=1)

        # 6. 통계 업데이트
        for route in selected_routes:
            route_name = route.route_type.value
            self.routing_stats["route_distribution"][route_name] = (
                self.routing_stats["route_distribution"].get(route_name, 0) + 1
            )

        print(f"🧭 라우팅 결과: {[r.route_type.value for r in selected_routes]}")
        return selected_routes

    def _analyze_input(self, user_input: str) -> Dict[str, Any]:
        """사용자 입력 분석"""
        text_lower = user_input.lower()

        analysis = {
            "length": len(user_input),
            "complexity": self._calculate_text_complexity(user_input),
            "emotional_intensity": self._detect_emotional_intensity(text_lower),
            "question_markers": self._count_question_markers(user_input),
            "emotional_keywords": self._extract_emotional_keywords(text_lower),
            "creativity_indicators": self._detect_creativity_indicators(text_lower),
            "urgency_level": self._assess_urgency(text_lower),
        }

        return analysis

    def _analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """컨텍스트 분석"""
        analysis = {
            "context_richness": len(context),
            "has_history": bool(context.get("conversation_history")),
            "has_emotion_context": bool(context.get("emotion_context")),
            "has_meta_info": bool(context.get("meta_info")),
            "session_continuity": bool(context.get("session_id")),
            "specialized_context": self._detect_specialized_context(context),
        }

        return analysis

    def _calculate_text_complexity(self, text: str) -> float:
        """텍스트 복잡도 계산"""
        factors = []

        # 길이 기반 복잡도
        length_complexity = min(1.0, len(text) / 200.0)
        factors.append(length_complexity)

        # 문장 구조 복잡도
        sentence_count = len([s for s in text.split(".") if s.strip()])
        structure_complexity = min(1.0, sentence_count / 5.0)
        factors.append(structure_complexity)

        # 어휘 다양성
        words = text.split()
        unique_words = len(set(words))
        vocab_complexity = min(1.0, unique_words / max(len(words), 1))
        factors.append(vocab_complexity)

        return sum(factors) / len(factors)

    def _detect_emotional_intensity(self, text: str) -> float:
        """감정 강도 탐지"""
        high_intensity_markers = [
            "진짜",
            "정말",
            "너무",
            "완전",
            "엄청",
            "매우",
            "정말로",
            "!",
            "!!",
            "!!!",
            "ㅠㅠ",
            "ㅜㅜ",
            "ㅎㅎ",
            "ㅋㅋ",
        ]

        intensity_score = 0.0
        for marker in high_intensity_markers:
            intensity_score += text.count(marker) * 0.1

        return min(1.0, intensity_score)

    def _count_question_markers(self, text: str) -> int:
        """질문 마커 개수"""
        return (
            text.count("?") + text.count("뭐") + text.count("어떻") + text.count("왜")
        )

    def _extract_emotional_keywords(self, text: str) -> List[str]:
        """감정 키워드 추출"""
        emotion_patterns = {
            "joy": ["기쁘", "좋", "행복", "즐거", "만족", "신나", "재미"],
            "sadness": ["슬프", "우울", "힘들", "속상", "아쉽", "외로", "허무"],
            "anger": ["화", "짜증", "빡", "분노", "열받", "억울", "답답"],
            "anxiety": ["불안", "걱정", "두려", "초조", "긴장", "무서", "스트레스"],
            "curiosity": ["궁금", "흥미", "알고싶", "배우고싶", "신기", "놀라"],
        }

        found_emotions = []
        for emotion, patterns in emotion_patterns.items():
            if any(pattern in text for pattern in patterns):
                found_emotions.append(emotion)

        return found_emotions

    def _detect_creativity_indicators(self, text: str) -> List[str]:
        """창의성 지표 탐지"""
        creativity_markers = [
            "창의",
            "아이디어",
            "상상",
            "새로운",
            "독특",
            "혁신",
            "발명",
            "예술",
            "디자인",
            "만들",
            "그려",
            "써",
        ]

        found_markers = []
        for marker in creativity_markers:
            if marker in text:
                found_markers.append(marker)

        return found_markers

    def _assess_urgency(self, text: str) -> float:
        """긴급도 평가"""
        urgency_markers = [
            "급해",
            "빨리",
            "당장",
            "지금",
            "즉시",
            "긴급",
            "어서",
            "시급",
            "바로",
            "먼저",
        ]

        urgency_score = 0.0
        for marker in urgency_markers:
            if marker in text:
                urgency_score += 0.2

        return min(1.0, urgency_score)

    def _detect_specialized_context(self, context: Dict[str, Any]) -> List[str]:
        """특화된 컨텍스트 탐지"""
        specialized = []

        if context.get("coding_context"):
            specialized.append("coding")
        if context.get("creative_context"):
            specialized.append("creative")
        if context.get("emotional_support_context"):
            specialized.append("emotional_support")
        if context.get("analytical_context"):
            specialized.append("analytical")

        return specialized

    def _initialize_routing_rules(self) -> List[Dict[str, Any]]:
        """라우팅 규칙 초기화"""
        return [
            {
                "name": "high_emotional_intensity",
                "condition": lambda inp, ctx: inp["emotional_intensity"] > 0.7,
                "target_route": RouteType.EMOTIONAL_DEEP,
                "weight_bonus": 0.3,
            },
            {
                "name": "creative_request",
                "condition": lambda inp, ctx: len(inp["creativity_indicators"]) > 2,
                "target_route": RouteType.CREATIVE_FLOW,
                "weight_bonus": 0.2,
            },
            {
                "name": "complex_analysis",
                "condition": lambda inp, ctx: inp["complexity"] > 0.8
                and inp["question_markers"] > 2,
                "target_route": RouteType.META_COGNITIVE,
                "weight_bonus": 0.25,
            },
            {
                "name": "standard_interaction",
                "condition": lambda inp, ctx: True,  # 항상 적용 (기본)
                "target_route": RouteType.LEGACY,
                "weight_bonus": 0.0,
            },
        ]

    def _apply_routing_rules(
        self, input_analysis: Dict[str, Any], context_analysis: Dict[str, Any]
    ) -> List[Tuple[RouteType, float]]:
        """라우팅 규칙 적용"""
        candidate_routes = []

        for rule in self.routing_rules:
            try:
                if rule["condition"](input_analysis, context_analysis):
                    candidate_routes.append(
                        (rule["target_route"], rule["weight_bonus"])
                    )
            except Exception as e:
                print(f"⚠️ 라우팅 규칙 '{rule['name']}' 적용 오류: {e}")

        return candidate_routes

    def _calculate_route_weights(
        self,
        candidate_routes: List[Tuple[RouteType, float]],
        input_analysis: Dict[str, Any],
        context_analysis: Dict[str, Any],
    ) -> List[JudgmentRoute]:
        """경로 가중치 계산"""
        weighted_routes = []

        for route_type, base_weight in candidate_routes:
            # 기본 가중치 계산
            weight = 0.5 + base_weight

            # 컨텍스트 기반 가중치 조정
            if context_analysis["context_richness"] > 5:
                weight += 0.1

            if context_analysis["has_history"]:
                weight += 0.05

            # 입력 기반 가중치 조정
            if input_analysis["complexity"] > 0.6:
                weight += 0.1

            if input_analysis["emotional_intensity"] > 0.5:
                weight += 0.05

            # 경로별 특화 조정
            if route_type == RouteType.LEGACY:
                # 레거시는 항상 안정적인 선택
                weight += 0.2
                confidence = 0.8
                estimated_time = 0.5
            elif route_type == RouteType.AGI_NATIVE:
                # AGI 네이티브는 아직 실험적
                confidence = 0.6
                estimated_time = 1.0
            else:
                # 기타 경로들
                confidence = 0.7
                estimated_time = 0.8

            weighted_route = JudgmentRoute(
                route_type=route_type,
                weight=min(1.0, weight),
                confidence=confidence,
                reasoning=f"규칙 기반 선택: {route_type.value}",
                parameters={
                    "input_analysis": input_analysis,
                    "context_analysis": context_analysis,
                },
                estimated_time=estimated_time,
            )

            weighted_routes.append(weighted_route)

        return weighted_routes

    def _select_optimal_routes(
        self, weighted_routes: List[JudgmentRoute], max_routes: int = 1
    ) -> List[JudgmentRoute]:
        """최적 경로 선택"""
        if not weighted_routes:
            # 폴백: 레거시 경로
            return [
                JudgmentRoute(
                    route_type=RouteType.LEGACY,
                    weight=1.0,
                    confidence=0.8,
                    reasoning="폴백 경로",
                    parameters={},
                    estimated_time=0.5,
                )
            ]

        # 가중치 기준 정렬
        sorted_routes = sorted(
            weighted_routes, key=lambda r: r.weight * r.confidence, reverse=True
        )

        return sorted_routes[:max_routes]

    def get_routing_stats(self) -> Dict[str, Any]:
        """라우팅 통계 반환"""
        stats = self.routing_stats.copy()

        if stats["total_routes"] > 0:
            stats["success_rate"] = stats["successful_routes"] / stats["total_routes"]
            stats["average_routing_time"] = (
                stats["routing_time_total"] / stats["total_routes"]
            )

        return stats


# 글로벌 라우터 인스턴스
_global_router = None


def get_router() -> LoopRouter:
    """글로벌 라우터 인스턴스 반환"""
    global _global_router
    if _global_router is None:
        _global_router = LoopRouter()
    return _global_router


def route_judgment(user_input: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """🧭 판단 라우팅 - 메인 진입점"""
    router = get_router()
    routes = router.route_judgment(user_input, context)

    # JudgmentRoute 객체를 딕셔너리로 변환 (호환성)
    return [
        {
            "type": route.route_type.value,
            "weight": route.weight,
            "confidence": route.confidence,
            "reasoning": route.reasoning,
            "parameters": route.parameters,
            "estimated_time": route.estimated_time,
        }
        for route in routes
    ]


if __name__ == "__main__":
    # 라우터 테스트
    print("🧪 Loop Router 테스트")

    test_cases = [
        {"input": "안녕하세요!", "context": {}, "expected": "legacy"},
        {
            "input": "너무 슬퍼서 죽을 것 같아요 ㅠㅠ",
            "context": {},
            "expected": "emotional_deep",
        },
        {
            "input": "새로운 아이디어를 생각해내고 싶어요. 창의적인 방법이 있을까요?",
            "context": {},
            "expected": "creative_flow",
        },
        {
            "input": "이 복잡한 문제를 어떻게 분석해야 할까요? 여러 관점에서 살펴봐야 할 것 같은데...",
            "context": {"context_richness": 10},
            "expected": "meta_cognitive",
        },
    ]

    router = get_router()

    for i, case in enumerate(test_cases, 1):
        print(f"\n🎯 테스트 {i}: {case['input'][:50]}...")
        routes = route_judgment(case["input"], case["context"])

        if routes:
            primary_route = routes[0]
            print(f"  선택된 경로: {primary_route['type']}")
            print(f"  가중치: {primary_route['weight']:.2f}")
            print(f"  신뢰도: {primary_route['confidence']:.2f}")
            print(
                f"  예상과 일치: {'✅' if primary_route['type'] == case['expected'] else '❌'}"
            )
        else:
            print("  ❌ 경로 선택 실패")

    # 통계 출력
    stats = router.get_routing_stats()
    print(f"\n📊 라우터 통계:")
    print(f"  총 라우팅: {stats['total_routes']}")
    print(f"  경로 분포: {stats['route_distribution']}")
