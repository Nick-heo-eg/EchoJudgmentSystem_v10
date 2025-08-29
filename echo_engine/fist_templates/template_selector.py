"""
🎯 FIST Template Selector - 템플릿 선택 및 최적화 모듈
상황과 요구사항에 맞는 최적의 FIST 템플릿을 선택하는 고급 알고리즘
"""

import time
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

from .fist_core import (
    FISTTemplate,
    FISTRequest,
    TemplateCategory,
    TemplateComplexity,
    FISTStructureType,
)


class TemplateSelectionStrategy(Enum):
    """템플릿 선택 전략"""

    BEST_MATCH = "best_match"  # 최적 매칭
    HIGH_PERFORMANCE = "high_performance"  # 고성능 우선
    COMPLEXITY_BASED = "complexity_based"  # 복잡도 기반
    CONTEXTUAL = "contextual"  # 맥락 기반
    ADAPTIVE = "adaptive"  # 적응형
    RANDOM = "random"  # 무작위 (테스트용)


@dataclass
class TemplateScore:
    """템플릿 점수 정보"""

    template_id: str
    template_name: str
    total_score: float
    score_breakdown: Dict[str, float]
    confidence: float
    reasoning: List[str]


@dataclass
class SelectionCriteria:
    """선택 기준"""

    category_weight: float = 0.3
    performance_weight: float = 0.25
    complexity_weight: float = 0.15
    usage_weight: float = 0.1
    context_weight: float = 0.1
    freshness_weight: float = 0.1


class ContextAnalyzer:
    """컨텍스트 분석기"""

    def __init__(self):
        self.emotion_keywords = {
            "joy": ["기쁘", "행복", "즐거", "좋", "최고", "만족"],
            "sadness": ["슬프", "우울", "힘들", "속상", "아쉽", "실망"],
            "anger": ["화", "짜증", "분노", "열받", "빡친", "억울"],
            "fear": ["무서", "걱정", "불안", "두려", "위험", "조심"],
            "surprise": ["놀라", "헐", "와우", "대박", "신기", "의외"],
            "neutral": ["보통", "그냥", "일반", "평범", "괜찮"],
        }

        self.urgency_keywords = {
            "high": ["urgent", "긴급", "급해", "빨리", "즉시", "지금"],
            "medium": ["soon", "곧", "빨리", "일주일", "며칠"],
            "low": ["later", "나중", "천천히", "여유", "시간"],
        }

        self.domain_keywords = {
            "business": ["비즈니스", "사업", "회사", "매출", "투자", "경영"],
            "technology": ["기술", "AI", "시스템", "소프트웨어", "개발"],
            "personal": ["개인", "사적", "개인적", "내가", "나의"],
            "social": ["사회", "관계", "친구", "가족", "사람들"],
        }

    def analyze_context(
        self, text: str, additional_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """컨텍스트 분석"""
        text_lower = text.lower()

        analysis = {
            "text_length": len(text),
            "word_count": len(text.split()),
            "emotion_detected": self._detect_emotion(text_lower),
            "urgency_level": self._detect_urgency(text_lower),
            "domain": self._detect_domain(text_lower),
            "complexity_indicators": self._analyze_complexity(text),
            "question_type": self._detect_question_type(text_lower),
            "certainty_level": self._analyze_certainty(text_lower),
        }

        # 추가 컨텍스트 정보 통합
        if additional_context:
            analysis.update(additional_context)

        return analysis

    def _detect_emotion(self, text: str) -> Dict[str, Any]:
        """감정 감지"""
        emotion_scores = {}

        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            emotion_scores[emotion] = score

        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[primary_emotion]

        return {
            "primary_emotion": primary_emotion if max_score > 0 else "neutral",
            "scores": emotion_scores,
            "confidence": min(max_score / 3, 1.0),
        }

    def _detect_urgency(self, text: str) -> Dict[str, Any]:
        """긴급도 감지"""
        urgency_scores = {}

        for level, keywords in self.urgency_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            urgency_scores[level] = score

        primary_urgency = max(urgency_scores, key=urgency_scores.get)
        max_score = urgency_scores[primary_urgency]

        return {
            "level": primary_urgency if max_score > 0 else "medium",
            "scores": urgency_scores,
            "confidence": min(max_score / 2, 1.0),
        }

    def _detect_domain(self, text: str) -> Dict[str, Any]:
        """도메인 감지"""
        domain_scores = {}

        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            domain_scores[domain] = score

        primary_domain = max(domain_scores, key=domain_scores.get)
        max_score = domain_scores[primary_domain]

        return {
            "primary_domain": primary_domain if max_score > 0 else "general",
            "scores": domain_scores,
            "confidence": min(max_score / 2, 1.0),
        }

    def _analyze_complexity(self, text: str) -> Dict[str, Any]:
        """복잡도 분석"""
        # 간단한 복잡도 지표들
        word_count = len(text.split())
        sentence_count = text.count(".") + text.count("!") + text.count("?")
        avg_word_length = sum(len(word) for word in text.split()) / max(word_count, 1)

        complexity_score = 0
        if word_count > 50:
            complexity_score += 1
        if sentence_count > 3:
            complexity_score += 1
        if avg_word_length > 6:
            complexity_score += 1

        complexity_levels = ["simple", "moderate", "complex"]
        complexity_level = complexity_levels[min(complexity_score, 2)]

        return {
            "level": complexity_level,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_word_length": avg_word_length,
            "score": complexity_score,
        }

    def _detect_question_type(self, text: str) -> str:
        """질문 유형 감지"""
        if "?" not in text:
            return "statement"

        question_starters = {
            "what": ["무엇", "뭐", "어떤"],
            "how": ["어떻게", "방법", "how"],
            "why": ["왜", "이유", "why"],
            "when": ["언제", "when"],
            "where": ["어디", "where"],
            "who": ["누구", "who"],
        }

        for q_type, keywords in question_starters.items():
            if any(keyword in text for keyword in keywords):
                return q_type

        return "general_question"

    def _analyze_certainty(self, text: str) -> Dict[str, Any]:
        """확실성 분석"""
        certainty_high = ["확실", "분명", "틀림없", "당연", "명백"]
        certainty_low = ["아마", "maybe", "perhaps", "possibly", "uncertain"]

        high_count = sum(1 for keyword in certainty_high if keyword in text)
        low_count = sum(1 for keyword in certainty_low if keyword in text)

        if high_count > low_count:
            return {"level": "high", "confidence": 0.8}
        elif low_count > high_count:
            return {"level": "low", "confidence": 0.8}
        else:
            return {"level": "medium", "confidence": 0.5}


class AdvancedTemplateSelector:
    """고급 템플릿 선택기"""

    def __init__(self, templates: List[FISTTemplate]):
        self.templates = templates
        self.context_analyzer = ContextAnalyzer()
        self.selection_history = []
        self.performance_history = {}
        self.template_embeddings = {}  # 향후 벡터 기반 매칭용

        # 기본 선택 기준
        self.default_criteria = SelectionCriteria()

        # 템플릿 성능 초기화
        self._initialize_template_performance()

    def _initialize_template_performance(self):
        """템플릿 성능 정보 초기화"""
        for template in self.templates:
            self.performance_history[template.template_id] = {
                "usage_count": template.usage_count,
                "success_rate": template.success_rate,
                "average_confidence": template.average_confidence,
                "last_used": datetime.now() - timedelta(days=30),  # 기본값
                "context_matches": {},
                "performance_trend": [],
            }

    def select_optimal_template(
        self,
        request: FISTRequest,
        strategy: TemplateSelectionStrategy = TemplateSelectionStrategy.BEST_MATCH,
        criteria: Optional[SelectionCriteria] = None,
    ) -> Tuple[FISTTemplate, TemplateScore]:
        """최적 템플릿 선택"""

        # 컨텍스트 분석
        context_analysis = self.context_analyzer.analyze_context(
            request.input_text, request.context
        )

        # 선택 기준 적용
        active_criteria = criteria or self.default_criteria

        # 전략별 선택
        if strategy == TemplateSelectionStrategy.BEST_MATCH:
            selected_template, score = self._select_best_match(
                request, context_analysis, active_criteria
            )
        elif strategy == TemplateSelectionStrategy.HIGH_PERFORMANCE:
            selected_template, score = self._select_high_performance(
                request, context_analysis
            )
        elif strategy == TemplateSelectionStrategy.COMPLEXITY_BASED:
            selected_template, score = self._select_complexity_based(
                request, context_analysis
            )
        elif strategy == TemplateSelectionStrategy.CONTEXTUAL:
            selected_template, score = self._select_contextual(
                request, context_analysis
            )
        elif strategy == TemplateSelectionStrategy.ADAPTIVE:
            selected_template, score = self._select_adaptive(
                request, context_analysis, active_criteria
            )
        else:  # RANDOM
            selected_template, score = self._select_random(request)

        # 선택 이력 기록
        self._record_selection(
            request, selected_template, score, strategy, context_analysis
        )

        return selected_template, score

    def _select_best_match(
        self, request: FISTRequest, context: Dict[str, Any], criteria: SelectionCriteria
    ) -> Tuple[FISTTemplate, TemplateScore]:
        """최적 매칭 선택"""
        scores = []

        for template in self.templates:
            score_breakdown = {}

            # 1. 카테고리 일치 점수
            category_score = 1.0 if template.category == request.category else 0.3
            score_breakdown["category"] = category_score * criteria.category_weight

            # 2. 성능 점수
            performance_score = (
                template.success_rate * 0.6 + template.average_confidence * 0.4
            )
            score_breakdown["performance"] = (
                performance_score * criteria.performance_weight
            )

            # 3. 복잡도 적합성
            complexity_score = self._calculate_complexity_score(
                template, request, context
            )
            score_breakdown["complexity"] = (
                complexity_score * criteria.complexity_weight
            )

            # 4. 사용 빈도 점수
            usage_score = min(template.usage_count / 100, 1.0)
            score_breakdown["usage"] = usage_score * criteria.usage_weight

            # 5. 컨텍스트 적합성
            context_score = self._calculate_context_score(template, context)
            score_breakdown["context"] = context_score * criteria.context_weight

            # 6. 신선도 점수
            freshness_score = self._calculate_freshness_score(template)
            score_breakdown["freshness"] = freshness_score * criteria.freshness_weight

            # 총 점수 계산
            total_score = sum(score_breakdown.values())

            # 점수 객체 생성
            template_score = TemplateScore(
                template_id=template.template_id,
                template_name=template.name,
                total_score=total_score,
                score_breakdown=score_breakdown,
                confidence=min(total_score, 1.0),
                reasoning=self._generate_score_reasoning(score_breakdown),
            )

            scores.append((template, template_score))

        # 최고 점수 템플릿 선택
        best_template, best_score = max(scores, key=lambda x: x[1].total_score)
        return best_template, best_score

    def _select_high_performance(
        self, request: FISTRequest, context: Dict[str, Any]
    ) -> Tuple[FISTTemplate, TemplateScore]:
        """고성능 템플릿 선택"""
        # 성능 기반 정렬
        performance_templates = sorted(
            self.templates,
            key=lambda t: t.success_rate * t.average_confidence,
            reverse=True,
        )

        # 카테고리 일치 템플릿 우선 선택
        category_matches = [
            t for t in performance_templates if t.category == request.category
        ]

        if category_matches:
            selected = category_matches[0]
        else:
            selected = performance_templates[0]

        score = TemplateScore(
            template_id=selected.template_id,
            template_name=selected.name,
            total_score=selected.success_rate * selected.average_confidence,
            score_breakdown={
                "performance": selected.success_rate * selected.average_confidence
            },
            confidence=0.9,
            reasoning=[
                "고성능 기준으로 선택",
                f"성공률: {selected.success_rate}",
                f"평균 신뢰도: {selected.average_confidence}",
            ],
        )

        return selected, score

    def _select_complexity_based(
        self, request: FISTRequest, context: Dict[str, Any]
    ) -> Tuple[FISTTemplate, TemplateScore]:
        """복잡도 기반 선택"""
        # 요청 복잡도 분석
        text_complexity = context.get("complexity_indicators", {})

        if request.complexity:
            target_complexity = request.complexity
        else:
            # 컨텍스트 기반 복잡도 추정
            complexity_level = text_complexity.get("level", "moderate")
            target_complexity = TemplateComplexity(complexity_level)

        # 복잡도 일치 템플릿 필터링
        complexity_matches = [
            t for t in self.templates if t.complexity == target_complexity
        ]

        if not complexity_matches:
            # 일치하는 복잡도가 없으면 moderate 선택
            complexity_matches = [
                t for t in self.templates if t.complexity == TemplateComplexity.MODERATE
            ]

        if not complexity_matches:
            complexity_matches = self.templates  # 최후 수단

        # 카테고리 일치 우선
        category_matches = [
            t for t in complexity_matches if t.category == request.category
        ]
        selected = category_matches[0] if category_matches else complexity_matches[0]

        score = TemplateScore(
            template_id=selected.template_id,
            template_name=selected.name,
            total_score=0.8,
            score_breakdown={"complexity_match": 0.8},
            confidence=0.8,
            reasoning=[
                f"복잡도 {target_complexity.value} 기준으로 선택",
                f"텍스트 복잡도: {text_complexity.get('level', 'unknown')}",
            ],
        )

        return selected, score

    def _select_contextual(
        self, request: FISTRequest, context: Dict[str, Any]
    ) -> Tuple[FISTTemplate, TemplateScore]:
        """컨텍스트 기반 선택"""
        best_template = None
        best_score = 0

        for template in self.templates:
            # 컨텍스트 적합성 점수 계산
            context_score = self._calculate_context_score(template, context)

            if context_score > best_score:
                best_score = context_score
                best_template = template

        if not best_template:
            best_template = self.templates[0]
            best_score = 0.5

        score = TemplateScore(
            template_id=best_template.template_id,
            template_name=best_template.name,
            total_score=best_score,
            score_breakdown={"context_match": best_score},
            confidence=best_score,
            reasoning=["컨텍스트 기반 선택", f"컨텍스트 적합성: {best_score:.2f}"],
        )

        return best_template, score

    def _select_adaptive(
        self, request: FISTRequest, context: Dict[str, Any], criteria: SelectionCriteria
    ) -> Tuple[FISTTemplate, TemplateScore]:
        """적응형 선택 (성능 이력 기반)"""
        # 최근 성능 이력을 고려한 동적 선택
        current_time = datetime.now()
        adaptive_scores = []

        for template in self.templates:
            template_history = self.performance_history.get(template.template_id, {})

            # 기본 점수 계산
            base_score = template.success_rate * template.average_confidence

            # 최근 성능 트렌드 적용
            trend_score = self._calculate_performance_trend(template_history)

            # 사용 빈도 기반 조정
            usage_recency = self._calculate_usage_recency(
                template_history, current_time
            )

            # 적응형 점수 계산
            adaptive_score = base_score * 0.5 + trend_score * 0.3 + usage_recency * 0.2

            adaptive_scores.append((template, adaptive_score))

        # 최고 점수 선택
        best_template, best_score = max(adaptive_scores, key=lambda x: x[1])

        score = TemplateScore(
            template_id=best_template.template_id,
            template_name=best_template.name,
            total_score=best_score,
            score_breakdown={"adaptive_score": best_score},
            confidence=min(best_score, 1.0),
            reasoning=["적응형 선택", "최근 성능 트렌드 반영", "사용 패턴 분석"],
        )

        return best_template, score

    def _select_random(
        self, request: FISTRequest
    ) -> Tuple[FISTTemplate, TemplateScore]:
        """무작위 선택 (테스트용)"""
        import random

        # 카테고리 일치 템플릿 중에서 무작위 선택
        category_matches = [t for t in self.templates if t.category == request.category]

        if category_matches:
            selected = random.choice(category_matches)
        else:
            selected = random.choice(self.templates)

        score = TemplateScore(
            template_id=selected.template_id,
            template_name=selected.name,
            total_score=0.5,
            score_breakdown={"random": 0.5},
            confidence=0.5,
            reasoning=["무작위 선택 (테스트용)"],
        )

        return selected, score

    def _calculate_complexity_score(
        self, template: FISTTemplate, request: FISTRequest, context: Dict[str, Any]
    ) -> float:
        """복잡도 적합성 점수 계산"""
        # 요청 복잡도와 템플릿 복잡도 비교
        if request.complexity:
            if template.complexity == request.complexity:
                return 1.0
            elif abs(template.complexity.value - request.complexity.value) == 1:
                return 0.7
            else:
                return 0.3

        # 컨텍스트 기반 복잡도 추정
        text_complexity = context.get("complexity_indicators", {})
        estimated_complexity = text_complexity.get("level", "moderate")

        if template.complexity.value == estimated_complexity:
            return 1.0
        else:
            return 0.6

    def _calculate_context_score(
        self, template: FISTTemplate, context: Dict[str, Any]
    ) -> float:
        """컨텍스트 적합성 점수 계산"""
        score = 0.0

        # 감정 컨텍스트 매칭
        emotion_info = context.get("emotion_detected", {})
        primary_emotion = emotion_info.get("primary_emotion", "neutral")

        if (
            template.category == TemplateCategory.EMOTIONAL
            and primary_emotion != "neutral"
        ):
            score += 0.3

        # 긴급도 매칭
        urgency_info = context.get("urgency_level", {})
        urgency_level = urgency_info.get("level", "medium")

        if urgency_level == "high" and template.complexity == TemplateComplexity.SIMPLE:
            score += 0.2
        elif (
            urgency_level == "low" and template.complexity == TemplateComplexity.COMPLEX
        ):
            score += 0.2

        # 도메인 매칭
        domain_info = context.get("domain", {})
        primary_domain = domain_info.get("primary_domain", "general")

        if (
            primary_domain == "business"
            and template.category == TemplateCategory.STRATEGIC
        ):
            score += 0.3
        elif (
            primary_domain == "technology"
            and template.category == TemplateCategory.ANALYTICAL
        ):
            score += 0.3

        # 질문 유형 매칭
        question_type = context.get("question_type", "statement")

        if question_type == "how" and template.category == TemplateCategory.DECISION:
            score += 0.2
        elif (
            question_type == "what" and template.category == TemplateCategory.EVALUATION
        ):
            score += 0.2

        return min(score, 1.0)

    def _calculate_freshness_score(self, template: FISTTemplate) -> float:
        """신선도 점수 계산"""
        template_history = self.performance_history.get(template.template_id, {})
        last_used = template_history.get(
            "last_used", datetime.now() - timedelta(days=30)
        )

        days_since_used = (datetime.now() - last_used).days

        if days_since_used < 1:
            return 0.3  # 최근 사용은 낮은 신선도
        elif days_since_used < 7:
            return 0.7
        elif days_since_used < 30:
            return 1.0
        else:
            return 0.9  # 너무 오래 사용 안함도 약간 감점

    def _calculate_performance_trend(self, template_history: Dict[str, Any]) -> float:
        """성능 트렌드 계산"""
        trend_data = template_history.get("performance_trend", [])

        if len(trend_data) < 2:
            return 0.5  # 기본값

        # 최근 성능 트렌드 분석
        recent_scores = trend_data[-5:]  # 최근 5개 데이터

        if len(recent_scores) < 2:
            return 0.5

        # 단순 트렌드 계산
        avg_recent = sum(recent_scores) / len(recent_scores)

        return min(avg_recent, 1.0)

    def _calculate_usage_recency(
        self, template_history: Dict[str, Any], current_time: datetime
    ) -> float:
        """사용 최근성 계산"""
        last_used = template_history.get("last_used", current_time - timedelta(days=30))
        days_since_used = (current_time - last_used).days

        if days_since_used < 1:
            return 0.5  # 너무 최근은 다양성 측면에서 감점
        elif days_since_used < 7:
            return 1.0
        elif days_since_used < 30:
            return 0.8
        else:
            return 0.6

    def _generate_score_reasoning(self, score_breakdown: Dict[str, float]) -> List[str]:
        """점수 근거 생성"""
        reasoning = []

        for factor, score in score_breakdown.items():
            if score > 0.7:
                reasoning.append(f"{factor}: 높은 점수 ({score:.2f})")
            elif score > 0.4:
                reasoning.append(f"{factor}: 중간 점수 ({score:.2f})")
            else:
                reasoning.append(f"{factor}: 낮은 점수 ({score:.2f})")

        return reasoning

    def _record_selection(
        self,
        request: FISTRequest,
        template: FISTTemplate,
        score: TemplateScore,
        strategy: TemplateSelectionStrategy,
        context: Dict[str, Any],
    ):
        """선택 이력 기록"""
        selection_record = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request.request_id,
            "template_id": template.template_id,
            "template_name": template.name,
            "strategy": strategy.value,
            "score": score.total_score,
            "score_breakdown": score.score_breakdown,
            "context_summary": {
                "category": request.category.value,
                "complexity": (
                    request.complexity.value if request.complexity else "auto"
                ),
                "emotion": context.get("emotion_detected", {}).get(
                    "primary_emotion", "neutral"
                ),
                "urgency": context.get("urgency_level", {}).get("level", "medium"),
                "domain": context.get("domain", {}).get("primary_domain", "general"),
            },
        }

        self.selection_history.append(selection_record)

        # 템플릿 성능 이력 업데이트
        template_history = self.performance_history.get(template.template_id, {})
        template_history["last_used"] = datetime.now()
        template_history["usage_count"] = template_history.get("usage_count", 0) + 1

        # 이력 크기 제한
        if len(self.selection_history) > 1000:
            self.selection_history = self.selection_history[-1000:]

    def update_template_performance(
        self,
        template_id: str,
        performance_score: float,
        confidence: float,
        success: bool,
    ):
        """템플릿 성능 업데이트"""
        if template_id not in self.performance_history:
            return

        template_history = self.performance_history[template_id]

        # 성능 트렌드 업데이트
        trend_data = template_history.get("performance_trend", [])
        trend_data.append(performance_score)

        # 트렌드 데이터 크기 제한
        if len(trend_data) > 20:
            trend_data = trend_data[-20:]

        template_history["performance_trend"] = trend_data

        # 성공률 업데이트
        current_success_rate = template_history.get("success_rate", 0)
        usage_count = template_history.get("usage_count", 0)

        if usage_count > 0:
            new_success_rate = (
                (current_success_rate * (usage_count - 1)) + (1 if success else 0)
            ) / usage_count
            template_history["success_rate"] = new_success_rate

        # 평균 신뢰도 업데이트
        current_avg_confidence = template_history.get("average_confidence", 0)

        if usage_count > 0:
            new_avg_confidence = (
                (current_avg_confidence * (usage_count - 1)) + confidence
            ) / usage_count
            template_history["average_confidence"] = new_avg_confidence

    def get_selection_analytics(self) -> Dict[str, Any]:
        """선택 분석 결과"""
        if not self.selection_history:
            return {"message": "선택 이력이 없습니다"}

        # 통계 계산
        total_selections = len(self.selection_history)

        # 템플릿 사용 통계
        template_usage = {}
        strategy_usage = {}
        category_usage = {}

        for record in self.selection_history:
            template_id = record["template_id"]
            strategy = record["strategy"]
            category = record["context_summary"]["category"]

            template_usage[template_id] = template_usage.get(template_id, 0) + 1
            strategy_usage[strategy] = strategy_usage.get(strategy, 0) + 1
            category_usage[category] = category_usage.get(category, 0) + 1

        # 평균 점수 계산
        avg_score = (
            sum(record["score"] for record in self.selection_history) / total_selections
        )

        return {
            "total_selections": total_selections,
            "average_score": avg_score,
            "template_usage": template_usage,
            "strategy_usage": strategy_usage,
            "category_usage": category_usage,
            "most_used_template": (
                max(template_usage, key=template_usage.get) if template_usage else None
            ),
            "most_used_strategy": (
                max(strategy_usage, key=strategy_usage.get) if strategy_usage else None
            ),
            "most_used_category": (
                max(category_usage, key=category_usage.get) if category_usage else None
            ),
            "performance_summary": {
                "high_score_selections": sum(
                    1 for r in self.selection_history if r["score"] > 0.8
                ),
                "medium_score_selections": sum(
                    1 for r in self.selection_history if 0.5 < r["score"] <= 0.8
                ),
                "low_score_selections": sum(
                    1 for r in self.selection_history if r["score"] <= 0.5
                ),
            },
        }


# 편의 함수들
def select_optimal_template(
    templates: List[FISTTemplate],
    request: FISTRequest,
    strategy: TemplateSelectionStrategy = TemplateSelectionStrategy.BEST_MATCH,
) -> Tuple[FISTTemplate, TemplateScore]:
    """최적 템플릿 선택 편의 함수"""
    selector = AdvancedTemplateSelector(templates)
    return selector.select_optimal_template(request, strategy)


def analyze_template_performance(
    templates: List[FISTTemplate], selection_history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """템플릿 성능 분석 편의 함수"""
    selector = AdvancedTemplateSelector(templates)
    selector.selection_history = selection_history
    return selector.get_selection_analytics()
