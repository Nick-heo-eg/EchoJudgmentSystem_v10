#!/usr/bin/env python3
"""
📝 Feedback Collector - 사용자 피드백 수집기
공명 응답에 대한 사용자 만족도와 피드백을 체계적으로 수집하여 학습 데이터로 활용

핵심 기능:
- 다양한 피드백 형태 지원 (👍/👎, 1-5점, 선택지, 자유텍스트)
- 실시간 피드백 분석 및 분류
- meta_logs/feedback_logs.jsonl 구조화된 저장
- 피드백 품질 검증 및 필터링
- 시그니처별/감정별 만족도 통계
- 개선 포인트 자동 추출
"""

import json
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import re


class FeedbackType(Enum):
    """피드백 유형"""

    THUMBS = "thumbs"  # 👍/👎
    RATING = "rating"  # 1-5점
    CHOICE = "choice"  # 선택지
    TEXT = "text"  # 자유텍스트
    COMBINED = "combined"  # 복합


class SatisfactionLevel(Enum):
    """만족도 레벨"""

    VERY_DISSATISFIED = 1
    DISSATISFIED = 2
    NEUTRAL = 3
    SATISFIED = 4
    VERY_SATISFIED = 5


@dataclass
class FeedbackEntry:
    """피드백 엔트리"""

    feedback_id: str
    response_id: str
    user_id: str
    session_id: str
    signature: str
    emotion: str
    response_text: str
    feedback_type: str
    feedback_value: Any
    satisfaction_score: float
    feedback_categories: List[str]
    feedback_text: Optional[str]
    timestamp: str
    context_metadata: Dict[str, Any]


@dataclass
class FeedbackAnalysis:
    """피드백 분석 결과"""

    total_feedback_count: int
    average_satisfaction: float
    satisfaction_distribution: Dict[str, int]
    signature_performance: Dict[str, float]
    emotion_performance: Dict[str, float]
    common_issues: List[str]
    improvement_suggestions: List[str]
    analysis_timestamp: str


class FeedbackCollector:
    """사용자 피드백 수집기"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.feedback_dir = self.data_dir / "meta_logs"
        self.feedback_dir.mkdir(exist_ok=True)

        self.feedback_log_path = self.feedback_dir / "feedback_logs.jsonl"
        self.analysis_cache_path = self.feedback_dir / "feedback_analysis_cache.json"

        # 피드백 설정
        self.feedback_categories = self._init_feedback_categories()
        self.satisfaction_thresholds = self._init_satisfaction_thresholds()

        # 캐시된 데이터
        self.recent_feedback = self._load_recent_feedback()
        self.analysis_cache = self._load_analysis_cache()

        print("📝 Feedback Collector 초기화 완료")
        print(f"   📊 최근 피드백: {len(self.recent_feedback)}개")
        print(f"   📁 로그 위치: {self.feedback_log_path}")

    def collect_thumbs_feedback(
        self,
        response_id: str,
        user_id: str,
        is_positive: bool,
        context: Dict[str, Any] = None,
    ) -> str:
        """👍/👎 피드백 수집"""
        feedback_value = "👍" if is_positive else "👎"
        satisfaction_score = 4.0 if is_positive else 2.0

        feedback_id = self._collect_feedback(
            response_id=response_id,
            user_id=user_id,
            feedback_type=FeedbackType.THUMBS.value,
            feedback_value=feedback_value,
            satisfaction_score=satisfaction_score,
            context=context or {},
        )

        print(f"👍 Thumbs 피드백 수집: {feedback_value} (ID: {feedback_id[:8]})")
        return feedback_id

    def collect_rating_feedback(
        self,
        response_id: str,
        user_id: str,
        rating: int,
        context: Dict[str, Any] = None,
    ) -> str:
        """1-5점 평점 피드백 수집"""
        if rating < 1 or rating > 5:
            raise ValueError("평점은 1-5 사이여야 합니다")

        satisfaction_score = float(rating)

        feedback_id = self._collect_feedback(
            response_id=response_id,
            user_id=user_id,
            feedback_type=FeedbackType.RATING.value,
            feedback_value=rating,
            satisfaction_score=satisfaction_score,
            context=context or {},
        )

        print(f"⭐ 평점 피드백 수집: {rating}/5 (ID: {feedback_id[:8]})")
        return feedback_id

    def collect_choice_feedback(
        self,
        response_id: str,
        user_id: str,
        selected_choices: List[str],
        feedback_text: str = "",
        context: Dict[str, Any] = None,
    ) -> str:
        """선택지 기반 피드백 수집"""
        # 선택지별 만족도 매핑
        choice_satisfaction_mapping = {
            "공감됨": 4.5,
            "도움됨": 4.0,
            "적절함": 3.5,
            "보통": 3.0,
            "너무 딱딱함": 2.5,
            "시그니처 안 맞음": 2.0,
            "부적절함": 1.5,
            "이해 안됨": 1.0,
        }

        # 평균 만족도 계산
        satisfaction_scores = [
            choice_satisfaction_mapping.get(choice, 3.0) for choice in selected_choices
        ]
        satisfaction_score = (
            statistics.mean(satisfaction_scores) if satisfaction_scores else 3.0
        )

        feedback_id = self._collect_feedback(
            response_id=response_id,
            user_id=user_id,
            feedback_type=FeedbackType.CHOICE.value,
            feedback_value=selected_choices,
            satisfaction_score=satisfaction_score,
            feedback_categories=selected_choices,
            feedback_text=feedback_text,
            context=context or {},
        )

        print(
            f"✅ 선택지 피드백 수집: {', '.join(selected_choices)} (ID: {feedback_id[:8]})"
        )
        return feedback_id

    def collect_text_feedback(
        self,
        response_id: str,
        user_id: str,
        feedback_text: str,
        context: Dict[str, Any] = None,
    ) -> str:
        """자유 텍스트 피드백 수집"""
        # 텍스트 감정 분석을 통한 만족도 추정
        satisfaction_score = self._analyze_text_sentiment(feedback_text)

        # 텍스트에서 카테고리 추출
        categories = self._extract_categories_from_text(feedback_text)

        feedback_id = self._collect_feedback(
            response_id=response_id,
            user_id=user_id,
            feedback_type=FeedbackType.TEXT.value,
            feedback_value=feedback_text,
            satisfaction_score=satisfaction_score,
            feedback_categories=categories,
            feedback_text=feedback_text,
            context=context or {},
        )

        print(f"💬 텍스트 피드백 수집: {len(feedback_text)}자 (ID: {feedback_id[:8]})")
        return feedback_id

    def collect_combined_feedback(
        self,
        response_id: str,
        user_id: str,
        rating: Optional[int] = None,
        choices: Optional[List[str]] = None,
        text: Optional[str] = None,
        context: Dict[str, Any] = None,
    ) -> str:
        """복합 피드백 수집"""
        feedback_components = {}
        satisfaction_scores = []
        all_categories = []

        # 평점 처리
        if rating is not None:
            feedback_components["rating"] = rating
            satisfaction_scores.append(float(rating))

        # 선택지 처리
        if choices:
            feedback_components["choices"] = choices
            choice_satisfaction_mapping = {
                "공감됨": 4.5,
                "도움됨": 4.0,
                "적절함": 3.5,
                "보통": 3.0,
                "너무 딱딱함": 2.5,
                "시그니처 안 맞음": 2.0,
                "부적절함": 1.5,
                "이해 안됨": 1.0,
            }
            choice_scores = [
                choice_satisfaction_mapping.get(choice, 3.0) for choice in choices
            ]
            if choice_scores:
                satisfaction_scores.append(statistics.mean(choice_scores))
            all_categories.extend(choices)

        # 텍스트 처리
        if text:
            feedback_components["text"] = text
            text_satisfaction = self._analyze_text_sentiment(text)
            satisfaction_scores.append(text_satisfaction)
            text_categories = self._extract_categories_from_text(text)
            all_categories.extend(text_categories)

        # 전체 만족도 계산
        final_satisfaction = (
            statistics.mean(satisfaction_scores) if satisfaction_scores else 3.0
        )

        feedback_id = self._collect_feedback(
            response_id=response_id,
            user_id=user_id,
            feedback_type=FeedbackType.COMBINED.value,
            feedback_value=feedback_components,
            satisfaction_score=final_satisfaction,
            feedback_categories=list(set(all_categories)),
            feedback_text=text,
            context=context or {},
        )

        print(
            f"🔄 복합 피드백 수집: {len(feedback_components)}개 요소 (ID: {feedback_id[:8]})"
        )
        return feedback_id

    def _collect_feedback(
        self,
        response_id: str,
        user_id: str,
        feedback_type: str,
        feedback_value: Any,
        satisfaction_score: float,
        feedback_categories: List[str] = None,
        feedback_text: str = None,
        context: Dict[str, Any] = None,
    ) -> str:
        """내부 피드백 수집 메서드"""

        # 피드백 ID 생성
        feedback_id = f"fb_{int(time.time() * 1000)}_{user_id[:4]}"

        # 컨텍스트에서 메타데이터 추출
        context = context or {}
        signature = context.get("signature", "unknown")
        emotion = context.get("emotion", "unknown")
        response_text = context.get("response_text", "")
        session_id = context.get("session_id", "unknown")

        # 피드백 엔트리 생성
        feedback_entry = FeedbackEntry(
            feedback_id=feedback_id,
            response_id=response_id,
            user_id=user_id,
            session_id=session_id,
            signature=signature,
            emotion=emotion,
            response_text=response_text[:200],  # 처음 200자만 저장
            feedback_type=feedback_type,
            feedback_value=feedback_value,
            satisfaction_score=satisfaction_score,
            feedback_categories=feedback_categories or [],
            feedback_text=feedback_text,
            timestamp=datetime.now().isoformat(),
            context_metadata=context,
        )

        # JSONL 파일에 저장
        self._save_feedback_to_log(feedback_entry)

        # 최근 피드백 캐시 업데이트
        self.recent_feedback.append(asdict(feedback_entry))
        self._maintain_recent_feedback_cache()

        # 실시간 분석 업데이트
        self._update_analysis_cache(feedback_entry)

        return feedback_id

    def _save_feedback_to_log(self, feedback_entry: FeedbackEntry):
        """피드백을 JSONL 로그에 저장"""
        try:
            with open(self.feedback_log_path, "a", encoding="utf-8") as f:
                json.dump(asdict(feedback_entry), f, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            print(f"❌ 피드백 로그 저장 실패: {e}")

    def _analyze_text_sentiment(self, text: str) -> float:
        """텍스트 감정 분석을 통한 만족도 추정"""
        if not text:
            return 3.0

        text_lower = text.lower()

        # 긍정 키워드
        positive_keywords = [
            "좋",
            "만족",
            "훌륭",
            "완벽",
            "도움",
            "공감",
            "이해",
            "적절",
            "정확",
            "감사",
            "고마워",
            "최고",
            "멋진",
            "훌륭한",
            "좋아",
            "마음에 들어",
        ]

        # 부정 키워드
        negative_keywords = [
            "나쁘",
            "실망",
            "부족",
            "틀렸",
            "이상",
            "불만",
            "안 좋",
            "별로",
            "못",
            "엉망",
            "문제",
            "잘못",
            "이해 안",
            "도움 안",
            "공감 안",
            "부적절",
        ]

        positive_count = sum(
            1 for keyword in positive_keywords if keyword in text_lower
        )
        negative_count = sum(
            1 for keyword in negative_keywords if keyword in text_lower
        )

        # 감정 스코어 계산
        if positive_count > negative_count:
            if positive_count >= 3:
                return 4.5  # 매우 만족
            elif positive_count >= 2:
                return 4.0  # 만족
            else:
                return 3.5  # 약간 만족
        elif negative_count > positive_count:
            if negative_count >= 3:
                return 1.5  # 매우 불만족
            elif negative_count >= 2:
                return 2.0  # 불만족
            else:
                return 2.5  # 약간 불만족
        else:
            return 3.0  # 보통

    def _extract_categories_from_text(self, text: str) -> List[str]:
        """텍스트에서 피드백 카테고리 추출"""
        if not text:
            return []

        text_lower = text.lower()
        categories = []

        category_keywords = {
            "공감됨": ["공감", "이해", "마음", "느낌"],
            "도움됨": ["도움", "유용", "좋았", "해결"],
            "너무 딱딱함": ["딱딱", "차가운", "무미건조", "기계적"],
            "시그니처 안 맞음": ["안 맞", "다른", "어색", "이상한"],
            "부적절함": ["부적절", "적절하지", "맞지 않", "틀렸"],
            "이해 안됨": ["이해 안", "모르겠", "헷갈", "애매"],
        }

        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)

        return categories

    def _maintain_recent_feedback_cache(self):
        """최근 피드백 캐시 유지 (최대 1000개)"""
        if len(self.recent_feedback) > 1000:
            self.recent_feedback = self.recent_feedback[-1000:]

    def _update_analysis_cache(self, feedback_entry: FeedbackEntry):
        """실시간 분석 캐시 업데이트"""
        # 기본 통계 업데이트
        if "total_count" not in self.analysis_cache:
            self.analysis_cache["total_count"] = 0
        if "satisfaction_sum" not in self.analysis_cache:
            self.analysis_cache["satisfaction_sum"] = 0.0

        self.analysis_cache["total_count"] += 1
        self.analysis_cache["satisfaction_sum"] += feedback_entry.satisfaction_score
        self.analysis_cache["average_satisfaction"] = (
            self.analysis_cache["satisfaction_sum"] / self.analysis_cache["total_count"]
        )

        # 시그니처별 통계
        if "signature_stats" not in self.analysis_cache:
            self.analysis_cache["signature_stats"] = {}

        sig_stats = self.analysis_cache["signature_stats"]
        if feedback_entry.signature not in sig_stats:
            sig_stats[feedback_entry.signature] = {"count": 0, "satisfaction_sum": 0.0}

        sig_stats[feedback_entry.signature]["count"] += 1
        sig_stats[feedback_entry.signature][
            "satisfaction_sum"
        ] += feedback_entry.satisfaction_score
        sig_stats[feedback_entry.signature]["average"] = (
            sig_stats[feedback_entry.signature]["satisfaction_sum"]
            / sig_stats[feedback_entry.signature]["count"]
        )

        # 캐시 저장
        self._save_analysis_cache()

    def analyze_feedback(self, days: int = 7) -> FeedbackAnalysis:
        """피드백 분석 실행"""
        print(f"📊 최근 {days}일 피드백 분석 시작...")

        # 기간 필터링
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_feedback = [
            fb
            for fb in self.recent_feedback
            if datetime.fromisoformat(fb["timestamp"]) > cutoff_date
        ]

        if not recent_feedback:
            print("⚠️ 분석할 피드백이 없습니다.")
            return FeedbackAnalysis(
                total_feedback_count=0,
                average_satisfaction=0.0,
                satisfaction_distribution={},
                signature_performance={},
                emotion_performance={},
                common_issues=[],
                improvement_suggestions=[],
                analysis_timestamp=datetime.now().isoformat(),
            )

        # 기본 통계
        total_count = len(recent_feedback)
        satisfactions = [fb["satisfaction_score"] for fb in recent_feedback]
        average_satisfaction = statistics.mean(satisfactions)

        # 만족도 분포
        satisfaction_distribution = {
            "매우 불만족 (1-2)": len([s for s in satisfactions if s < 2.5]),
            "보통 (2.5-3.5)": len([s for s in satisfactions if 2.5 <= s < 3.5]),
            "만족 (3.5-4.5)": len([s for s in satisfactions if 3.5 <= s < 4.5]),
            "매우 만족 (4.5-5)": len([s for s in satisfactions if s >= 4.5]),
        }

        # 시그니처별 성능
        signature_performance = {}
        signature_groups = {}
        for fb in recent_feedback:
            sig = fb["signature"]
            if sig not in signature_groups:
                signature_groups[sig] = []
            signature_groups[sig].append(fb["satisfaction_score"])

        for sig, scores in signature_groups.items():
            signature_performance[sig] = statistics.mean(scores)

        # 감정별 성능
        emotion_performance = {}
        emotion_groups = {}
        for fb in recent_feedback:
            emotion = fb["emotion"]
            if emotion not in emotion_groups:
                emotion_groups[emotion] = []
            emotion_groups[emotion].append(fb["satisfaction_score"])

        for emotion, scores in emotion_groups.items():
            emotion_performance[emotion] = statistics.mean(scores)

        # 공통 이슈 추출
        common_issues = self._extract_common_issues(recent_feedback)

        # 개선 제안 생성
        improvement_suggestions = self._generate_improvement_suggestions(
            average_satisfaction,
            signature_performance,
            emotion_performance,
            common_issues,
        )

        analysis = FeedbackAnalysis(
            total_feedback_count=total_count,
            average_satisfaction=average_satisfaction,
            satisfaction_distribution=satisfaction_distribution,
            signature_performance=signature_performance,
            emotion_performance=emotion_performance,
            common_issues=common_issues,
            improvement_suggestions=improvement_suggestions,
            analysis_timestamp=datetime.now().isoformat(),
        )

        print(f"✅ 피드백 분석 완료: 평균 만족도 {average_satisfaction:.2f}/5.0")

        return analysis

    def _extract_common_issues(self, feedback_list: List[Dict]) -> List[str]:
        """공통 이슈 추출"""
        issues = []

        # 낮은 만족도 피드백에서 카테고리 추출
        low_satisfaction_feedback = [
            fb for fb in feedback_list if fb["satisfaction_score"] < 3.0
        ]

        if low_satisfaction_feedback:
            category_counts = {}
            for fb in low_satisfaction_feedback:
                for category in fb.get("feedback_categories", []):
                    category_counts[category] = category_counts.get(category, 0) + 1

            # 상위 3개 이슈
            sorted_issues = sorted(
                category_counts.items(), key=lambda x: x[1], reverse=True
            )
            issues = [issue for issue, count in sorted_issues[:3] if count > 1]

        return issues

    def _generate_improvement_suggestions(
        self,
        avg_satisfaction: float,
        signature_perf: Dict[str, float],
        emotion_perf: Dict[str, float],
        common_issues: List[str],
    ) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        # 전체 만족도 기반 제안
        if avg_satisfaction < 3.0:
            suggestions.append("전체적인 응답 품질 개선이 필요합니다.")
        elif avg_satisfaction < 3.5:
            suggestions.append("사용자 공감 능력 강화가 필요합니다.")

        # 저성능 시그니처 개선 제안
        low_performing_sigs = [
            sig for sig, score in signature_perf.items() if score < 3.0
        ]
        if low_performing_sigs:
            suggestions.append(
                f"다음 시그니처들의 응답 개선 필요: {', '.join(low_performing_sigs)}"
            )

        # 감정별 개선 제안
        low_performing_emotions = [
            emotion for emotion, score in emotion_perf.items() if score < 3.0
        ]
        if low_performing_emotions:
            suggestions.append(
                f"다음 감정들에 대한 응답 개선 필요: {', '.join(low_performing_emotions)}"
            )

        # 공통 이슈 기반 제안
        if "너무 딱딱함" in common_issues:
            suggestions.append("응답의 친근함과 따뜻함을 높여야 합니다.")
        if "시그니처 안 맞음" in common_issues:
            suggestions.append("시그니처별 특성을 더 명확하게 반영해야 합니다.")
        if "이해 안됨" in common_issues:
            suggestions.append("응답의 명확성과 이해도를 개선해야 합니다.")

        return suggestions

    def get_feedback_statistics(
        self, signature: str = None, emotion: str = None
    ) -> Dict[str, Any]:
        """피드백 통계 조회"""
        filtered_feedback = self.recent_feedback

        # 필터링
        if signature:
            filtered_feedback = [
                fb for fb in filtered_feedback if fb["signature"] == signature
            ]
        if emotion:
            filtered_feedback = [
                fb for fb in filtered_feedback if fb["emotion"] == emotion
            ]

        if not filtered_feedback:
            return {"message": "해당 조건의 피드백이 없습니다."}

        satisfactions = [fb["satisfaction_score"] for fb in filtered_feedback]

        return {
            "count": len(filtered_feedback),
            "average_satisfaction": statistics.mean(satisfactions),
            "min_satisfaction": min(satisfactions),
            "max_satisfaction": max(satisfactions),
            "median_satisfaction": statistics.median(satisfactions),
            "satisfaction_std": (
                statistics.stdev(satisfactions) if len(satisfactions) > 1 else 0.0
            ),
        }

    def _init_feedback_categories(self) -> List[str]:
        """피드백 카테고리 초기화"""
        return [
            "공감됨",
            "도움됨",
            "적절함",
            "보통",
            "너무 딱딱함",
            "시그니처 안 맞음",
            "부적절함",
            "이해 안됨",
        ]

    def _init_satisfaction_thresholds(self) -> Dict[str, float]:
        """만족도 임계값 초기화"""
        return {
            "very_dissatisfied": 2.0,
            "dissatisfied": 3.0,
            "neutral": 3.5,
            "satisfied": 4.0,
            "very_satisfied": 4.5,
        }

    def _load_recent_feedback(self) -> List[Dict[str, Any]]:
        """최근 피드백 로딩"""
        recent_feedback = []

        try:
            if self.feedback_log_path.exists():
                with open(self.feedback_log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            feedback = json.loads(line)
                            recent_feedback.append(feedback)

                # 최근 1000개만 유지
                recent_feedback = recent_feedback[-1000:]
        except Exception as e:
            print(f"⚠️ 최근 피드백 로딩 실패: {e}")

        return recent_feedback

    def _load_analysis_cache(self) -> Dict[str, Any]:
        """분석 캐시 로딩"""
        try:
            if self.analysis_cache_path.exists():
                with open(self.analysis_cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ 분석 캐시 로딩 실패: {e}")

        return {}

    def _save_analysis_cache(self):
        """분석 캐시 저장"""
        try:
            with open(self.analysis_cache_path, "w", encoding="utf-8") as f:
                json.dump(self.analysis_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 분석 캐시 저장 실패: {e}")


def main():
    """CLI 테스트 인터페이스"""
    print("📝 Feedback Collector 테스트")
    print("=" * 50)

    collector = FeedbackCollector()

    # 테스트 컨텍스트
    test_context = {
        "signature": "Selene",
        "emotion": "sadness",
        "response_text": "🌙 Selene: 마음이 아프시는군요... 함께 있어드릴게요.",
        "session_id": "test_session",
    }

    # 다양한 피드백 유형 테스트
    print("\n🧪 다양한 피드백 유형 테스트:")

    # 1. Thumbs 피드백
    feedback_id1 = collector.collect_thumbs_feedback(
        response_id="resp_001",
        user_id="user_001",
        is_positive=True,
        context=test_context,
    )

    # 2. 평점 피드백
    feedback_id2 = collector.collect_rating_feedback(
        response_id="resp_002", user_id="user_002", rating=4, context=test_context
    )

    # 3. 선택지 피드백
    feedback_id3 = collector.collect_choice_feedback(
        response_id="resp_003",
        user_id="user_003",
        selected_choices=["공감됨", "도움됨"],
        feedback_text="정말 위로가 되었습니다.",
        context=test_context,
    )

    # 4. 텍스트 피드백
    feedback_id4 = collector.collect_text_feedback(
        response_id="resp_004",
        user_id="user_004",
        feedback_text="응답이 너무 차갑게 느껴져요. 좀 더 따뜻했으면 좋겠어요.",
        context=test_context,
    )

    # 5. 복합 피드백
    feedback_id5 = collector.collect_combined_feedback(
        response_id="resp_005",
        user_id="user_005",
        rating=3,
        choices=["보통", "적절함"],
        text="괜찮지만 더 개인화되었으면 좋겠어요.",
        context=test_context,
    )

    print(f"\n📊 수집된 피드백 수: {len(collector.recent_feedback)}")

    # 피드백 분석
    print("\n📈 피드백 분석 수행...")
    analysis = collector.analyze_feedback(days=1)

    print(f"\n📊 분석 결과:")
    print(f"   총 피드백: {analysis.total_feedback_count}개")
    print(f"   평균 만족도: {analysis.average_satisfaction:.2f}/5.0")
    print(f"   만족도 분포: {analysis.satisfaction_distribution}")

    if analysis.common_issues:
        print(f"   공통 이슈: {', '.join(analysis.common_issues)}")

    if analysis.improvement_suggestions:
        print(f"   개선 제안:")
        for suggestion in analysis.improvement_suggestions:
            print(f"     - {suggestion}")

    # 통계 조회 테스트
    print("\n📈 통계 조회 테스트:")
    stats = collector.get_feedback_statistics(signature="Selene")
    print(f"   Selene 시그니처 통계: {stats}")

    print("\n✅ Feedback Collector 테스트 완료!")


if __name__ == "__main__":
    main()
