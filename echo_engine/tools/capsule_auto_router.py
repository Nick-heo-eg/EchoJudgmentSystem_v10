"""
🎯 Capsule Auto Router
검색 없는 즉시 캡슐 라우팅 시스템 - "몇 글자만 치면 바로 추천"
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

from .capsule_models import CapsuleSpec, ExecutionContext, CapsuleType


@dataclass
class ContextSignal:
    """상황 신호 추출 결과"""

    emotions: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    urgency: float = 0.0
    complexity: float = 0.0
    capsule_hints: List[str] = field(default_factory=list)


@dataclass
class RouteRecommendation:
    """라우팅 추천 결과"""

    capsule_names: List[str]
    confidence_score: float
    reasoning: str
    auto_selected: bool = False
    context_match_score: float = 0.0


class ContextAnalyzer:
    """상황 분석기 - 텍스트에서 캡슐 힌트 추출"""

    def __init__(self):
        # 감정 키워드 매핑
        self.emotion_patterns = {
            "anxiety": ["불안", "anxiety", "걱정", "nervous", "stress", "overwhelm"],
            "sadness": ["슬프", "sad", "우울", "lonely", "외로", "depressed"],
            "frustration": ["답답", "frustrat", "막막", "stuck", "block", "화나"],
            "excitement": ["신나", "excit", "기대", "설레", "thrill", "eager"],
            "confusion": ["헷갈", "confus", "모르겠", "unclear", "복잡", "어려워"],
            "joy": ["기쁘", "happy", "joy", "좋아", "만족", "pleased"],
        }

        # 캡슐 타입 키워드 매핑
        self.capsule_hints = {
            "aurora-empathy": [
                "위로",
                "comfort",
                "공감",
                "empathy",
                "따뜻",
                "도움",
                "help",
                "외로",
                "lonely",
                "슬프",
                "sad",
                "힘들",
            ],
            "phoenix-transformation": [
                "변화",
                "change",
                "혁신",
                "innovation",
                "돌파",
                "breakthrough",
                "막힘",
                "stuck",
                "탈출",
                "transform",
                "새로운",
            ],
            "sage-analysis": [
                "분석",
                "analyz",
                "체계",
                "systematic",
                "논리",
                "logic",
                "복잡",
                "complex",
                "해결",
                "solve",
                "지혜",
                "wisdom",
            ],
            "hybrid-creative": [
                "창의",
                "creativ",
                "예술",
                "art",
                "상상",
                "imagin",
                "영감",
                "inspir",
                "아이디어",
                "idea",
                "만들",
            ],
        }

        # 우선순위 키워드
        self.urgency_patterns = [
            "급해",
            "urgent",
            "빨리",
            "immediately",
            "지금",
            "now",
            "데드라인",
            "deadline",
            "마감",
            "asap",
        ]

        # 복잡도 키워드
        self.complexity_patterns = [
            "복잡",
            "complex",
            "어려운",
            "difficult",
            "다면적",
            "multi",
            "종합적",
            "comprehensive",
            "통합",
            "integrated",
        ]

    def analyze_context(
        self, text: str, emotion: Optional[str] = None
    ) -> ContextSignal:
        """컨텍스트 분석 - 캡슐 힌트 추출"""
        if not text:
            text = ""

        text_lower = text.lower()
        signal = ContextSignal()

        # 1. 감정 신호 추출
        for emotion_key, patterns in self.emotion_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    signal.emotions.append(emotion_key)
                    break

        # 명시적 감정이 있으면 추가
        if emotion and emotion not in signal.emotions:
            signal.emotions.append(emotion)

        # 2. 캡슐 힌트 추출
        for capsule_name, patterns in self.capsule_hints.items():
            match_count = 0
            for pattern in patterns:
                if pattern in text_lower:
                    match_count += 1

            if match_count > 0:
                # 매칭된 패턴 수에 비례한 점수
                signal.capsule_hints.append((capsule_name, match_count))

        # 점수순 정렬
        signal.capsule_hints = [
            name
            for name, _ in sorted(
                signal.capsule_hints, key=lambda x: x[1], reverse=True
            )
        ]

        # 3. 긴급도 계산
        urgency_matches = sum(
            1 for pattern in self.urgency_patterns if pattern in text_lower
        )
        signal.urgency = min(1.0, urgency_matches * 0.3)

        # 4. 복잡도 계산
        complexity_matches = sum(
            1 for pattern in self.complexity_patterns if pattern in text_lower
        )
        signal.complexity = min(1.0, complexity_matches * 0.3)

        # 5. 키워드 추출 (단순 토큰화)
        keywords = re.findall(r"\b\w{3,}\b", text_lower)
        signal.keywords = list(set(keywords))[:10]  # 최대 10개

        return signal


class CapsuleCache:
    """캡슐 매칭 캐시 - 빠른 추천을 위한 전처리된 인덱스"""

    def __init__(self):
        self.usage_history: Dict[str, int] = {}  # 사용 빈도
        self.success_history: Dict[str, float] = {}  # 성공률
        self.last_used: Dict[str, datetime] = {}  # 마지막 사용 시간
        self.context_patterns: Dict[str, List[str]] = defaultdict(list)  # 컨텍스트 패턴

        # 캐시 파일 경로
        self.cache_path = Path("data/capsule_cache.json")
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_cache()

    def _load_cache(self):
        """캐시 로드"""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.usage_history = data.get("usage_history", {})
                    self.success_history = data.get("success_history", {})
                    self.context_patterns = defaultdict(
                        list, data.get("context_patterns", {})
                    )

                    # 날짜 문자열을 datetime으로 변환
                    last_used_str = data.get("last_used", {})
                    self.last_used = {}
                    for k, v in last_used_str.items():
                        try:
                            self.last_used[k] = datetime.fromisoformat(v)
                        except:
                            pass
            except Exception:
                pass  # 캐시 로드 실패해도 계속 진행

    def _save_cache(self):
        """캐시 저장"""
        try:
            # datetime을 문자열로 변환
            last_used_str = {k: v.isoformat() for k, v in self.last_used.items()}

            data = {
                "usage_history": self.usage_history,
                "success_history": self.success_history,
                "context_patterns": dict(self.context_patterns),
                "last_used": last_used_str,
            }
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # 캐시 저장 실패해도 계속 진행

    def record_usage(
        self, capsule_name: str, context_keywords: List[str], success: bool = True
    ):
        """사용 기록 업데이트"""
        # 사용 빈도 증가
        self.usage_history[capsule_name] = self.usage_history.get(capsule_name, 0) + 1

        # 성공률 업데이트 (지수이동평균)
        current_success = self.success_history.get(capsule_name, 0.5)
        alpha = 0.1
        self.success_history[capsule_name] = (1 - alpha) * current_success + alpha * (
            1.0 if success else 0.0
        )

        # 마지막 사용 시간
        self.last_used[capsule_name] = datetime.now()

        # 컨텍스트 패턴 학습
        for keyword in context_keywords[:5]:  # 최대 5개만
            if keyword not in self.context_patterns[capsule_name]:
                self.context_patterns[capsule_name].append(keyword)
                # 최대 20개까지만 저장
                if len(self.context_patterns[capsule_name]) > 20:
                    self.context_patterns[capsule_name] = self.context_patterns[
                        capsule_name
                    ][-20:]

        self._save_cache()

    def get_popularity_score(self, capsule_name: str) -> float:
        """인기도 점수 (사용빈도 + 성공률 + 최근성)"""
        usage = self.usage_history.get(capsule_name, 0)
        success = self.success_history.get(capsule_name, 0.5)

        # 최근성 (30일 기준)
        recency = 0.0
        if capsule_name in self.last_used:
            days_ago = (datetime.now() - self.last_used[capsule_name]).days
            recency = max(0.0, 1.0 - days_ago / 30)

        # 가중 평균
        return 0.4 * min(1.0, usage / 10) + 0.4 * success + 0.2 * recency

    def get_context_match_score(self, capsule_name: str, keywords: List[str]) -> float:
        """컨텍스트 매칭 점수"""
        if capsule_name not in self.context_patterns or not keywords:
            return 0.0

        capsule_patterns = self.context_patterns[capsule_name]
        matches = sum(1 for keyword in keywords if keyword in capsule_patterns)

        return matches / len(keywords) if keywords else 0.0


class CapsuleAutoRouter:
    """캡슐 자동 라우터 - 검색 없는 즉시 추천"""

    def __init__(self, registry_path: str = "data/capsule_registry.json"):
        self.registry_path = registry_path
        self._engine = None  # 지연 로드
        self.analyzer = ContextAnalyzer()
        self.cache = CapsuleCache()

    @property
    def engine(self):
        """CapsuleEngine 지연 로드"""
        if self._engine is None:
            from .capsule_cli import CapsuleEngine

            self._engine = CapsuleEngine(self.registry_path)
        return self._engine

    def auto_route(
        self, context: ExecutionContext, limit: int = 3
    ) -> RouteRecommendation:
        """자동 라우팅 - 즉시 캡슐 추천"""

        # 1. 컨텍스트 분석
        signal = self.analyzer.analyze_context(context.text, context.emotion)

        # 2. 사용 가능한 캡슐 목록
        all_capsules = self.engine.registry.list_capsules()

        if not all_capsules:
            return RouteRecommendation(
                capsule_names=[],
                confidence_score=0.0,
                reasoning="등록된 캡슐이 없습니다",
            )

        # 3. 각 캡슐 점수 계산
        scored_capsules = []

        for capsule in all_capsules:
            score = self._calculate_capsule_score(capsule, signal, context)
            if score > 0:
                scored_capsules.append((capsule.name, score))

        # 4. 점수순 정렬 및 상위 N개 선택
        scored_capsules.sort(key=lambda x: x[1], reverse=True)
        top_capsules = scored_capsules[:limit]

        if not top_capsules:
            # Fallback - 인기순으로 추천
            fallback = self._get_fallback_recommendations(limit)
            return RouteRecommendation(
                capsule_names=fallback,
                confidence_score=0.3,
                reasoning="컨텍스트 매칭 실패, 인기 캡슐로 대체 추천",
            )

        # 5. 결과 구성
        capsule_names = [name for name, _ in top_capsules]
        max_score = top_capsules[0][1]

        # 자동 선택 여부 (신뢰도 0.8 이상이면 첫 번째 자동 선택)
        auto_selected = max_score >= 0.8

        reasoning_parts = []
        if signal.emotions:
            reasoning_parts.append(f"감정: {', '.join(signal.emotions)}")
        if signal.capsule_hints:
            reasoning_parts.append(f"힌트: {', '.join(signal.capsule_hints[:2])}")
        if signal.urgency > 0.3:
            reasoning_parts.append(f"긴급도: {signal.urgency:.1f}")

        reasoning = " | ".join(reasoning_parts) if reasoning_parts else "기본 매칭"

        return RouteRecommendation(
            capsule_names=capsule_names,
            confidence_score=max_score,
            reasoning=reasoning,
            auto_selected=auto_selected,
            context_match_score=max_score,
        )

    def _calculate_capsule_score(
        self, capsule: CapsuleSpec, signal: ContextSignal, context: ExecutionContext
    ) -> float:
        """캡슐 점수 계산 (다차원 매칭)"""
        score = 0.0

        # 1. 캡슐 힌트 매칭 (가장 중요)
        if capsule.name in signal.capsule_hints:
            hint_position = signal.capsule_hints.index(capsule.name)
            score += 0.5 * (1.0 - hint_position * 0.2)  # 순위에 따라 점수 차등

        # 2. 감정 매칭
        emotion_score = self._calculate_emotion_score(capsule, signal.emotions)
        score += 0.2 * emotion_score

        # 3. 인기도/성공률
        popularity = self.cache.get_popularity_score(capsule.name)
        score += 0.15 * popularity

        # 4. 컨텍스트 매칭 (학습된 패턴)
        context_match = self.cache.get_context_match_score(
            capsule.name, signal.keywords
        )
        score += 0.1 * context_match

        # 5. 강도 매칭
        if context.intensity > 0.7 and any(
            "intensity>" in rule.condition for rule in capsule.rules
        ):
            score += 0.05

        return min(1.0, score)

    def _calculate_emotion_score(
        self, capsule: CapsuleSpec, emotions: List[str]
    ) -> float:
        """감정 매칭 점수"""
        if not emotions:
            return 0.5  # 중립

        # 캡슐 타입별 감정 친화도
        emotion_affinity = {
            CapsuleType.EMOTION: {
                "sadness": 0.9,
                "anxiety": 0.8,
                "joy": 0.7,
                "excitement": 0.6,
            },
            CapsuleType.SIGNATURE: {
                "frustration": 0.9,
                "excitement": 0.8,
                "confusion": 0.6,
            },
            CapsuleType.COGNITIVE: {
                "confusion": 0.9,
                "frustration": 0.7,
                "anxiety": 0.6,
            },
            CapsuleType.HYBRID: {
                "excitement": 0.9,
                "joy": 0.8,
                "frustration": 0.6,
                "confusion": 0.5,
            },
        }

        affinity_map = emotion_affinity.get(capsule.type, {})

        if not affinity_map:
            return 0.5

        max_affinity = 0.0
        for emotion in emotions:
            affinity = affinity_map.get(emotion, 0.3)  # 기본 친화도
            max_affinity = max(max_affinity, affinity)

        return max_affinity

    def _get_fallback_recommendations(self, limit: int) -> List[str]:
        """대체 추천 - 인기/성공률 기반"""
        all_capsules = self.engine.registry.list_capsules()

        popularity_scores = []
        for capsule in all_capsules:
            popularity = self.cache.get_popularity_score(capsule.name)
            popularity_scores.append((capsule.name, popularity))

        popularity_scores.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in popularity_scores[:limit]]

    def record_selection(
        self, capsule_name: str, context: ExecutionContext, success: bool = True
    ):
        """캡슐 선택 기록 - 학습 데이터 축적"""
        signal = self.analyzer.analyze_context(context.text, context.emotion)
        self.cache.record_usage(capsule_name, signal.keywords, success)

    def get_hotlist(self, limit: int = 5) -> List[Tuple[str, float]]:
        """인기 캡슐 목록 (즐겨찾기용)"""
        all_capsules = self.engine.registry.list_capsules()

        hotlist = []
        for capsule in all_capsules:
            popularity = self.cache.get_popularity_score(capsule.name)
            if popularity > 0.1:  # 최소 임계값
                hotlist.append((capsule.name, popularity))

        hotlist.sort(key=lambda x: x[1], reverse=True)
        return hotlist[:limit]

    def warm_up_cache(self):
        """캐시 웜업 - 초기 인기도 설정"""
        all_capsules = self.engine.registry.list_capsules()

        for capsule in all_capsules:
            if capsule.name not in self.cache.usage_history:
                # 캡슐 이름 기반 초기 인기도 설정
                initial_popularity = 1
                if "aurora" in capsule.name.lower():
                    initial_popularity = 3
                elif "phoenix" in capsule.name.lower():
                    initial_popularity = 2
                elif "sage" in capsule.name.lower():
                    initial_popularity = 2

                self.cache.usage_history[capsule.name] = initial_popularity
                self.cache.success_history[capsule.name] = 0.7  # 초기 성공률

        self.cache._save_cache()
