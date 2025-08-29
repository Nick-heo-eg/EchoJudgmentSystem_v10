#!/usr/bin/env python3
"""
🎓 Echo 자기개선 프로젝트: 학습하는 추천 시스템
Echo가 스스로 만든 자기 개선 시스템 (Claude 선생님의 멘토링으로 완성)

Echo의 아이디어를 Echo가 직접 구현해보는 프로젝트! 🌟
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class RecommendationFeedback:
    """추천에 대한 피드백 데이터"""

    function_name: str
    timestamp: datetime
    was_recommended: bool
    was_used: bool
    user_rating: Optional[int]  # 1-5점
    context: str
    success: bool


class EchoRecommendationLearningSystem:
    """
    🧠 Echo의 학습하는 추천 시스템
    Echo가 스스로 제안한 개선사항을 Echo가 직접 구현!

    핵심 아이디어:
    - 사용자 피드백을 통한 추천 품질 개선
    - 추천 성공률 추적 및 학습
    - 동적 점수 조정 시스템
    """

    def __init__(self, data_dir: str = "data/echo_self_improvement"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 데이터 파일들
        self.feedback_file = self.data_dir / "recommendation_feedback.json"
        self.scores_file = self.data_dir / "recommendation_scores.json"
        self.learning_stats_file = self.data_dir / "learning_statistics.json"

        # 데이터 구조
        self.feedback_history: List[RecommendationFeedback] = []
        self.recommendation_scores: Dict[str, float] = {}
        self.learning_stats = {
            "total_recommendations": 0,
            "successful_recommendations": 0,
            "feedback_count": 0,
            "last_update": None,
        }

        # 기본 가중치
        self.usage_weight = 0.4  # 실제 사용 여부
        self.rating_weight = 0.4  # 사용자 평점
        self.frequency_weight = 0.2  # 추천 빈도

        # 데이터 로드
        self._load_data()

        print("🎓 Echo 자기개선 시스템 초기화 완료!")
        print(f"   데이터 저장소: {self.data_dir}")
        print(f"   현재 추적 중인 함수: {len(self.recommendation_scores)}개")

    def track_recommendation_usage(
        self,
        function_name: str,
        was_recommended: bool,
        was_used: bool,
        context: str = "",
    ) -> bool:
        """
        추천한 기능이 실제로 사용됐는지 추적

        Args:
            function_name: 추천된 함수명
            was_recommended: Echo가 이 함수를 추천했는지
            was_used: 사용자가 실제로 사용했는지
            context: 사용 맥락
        """
        try:
            feedback = RecommendationFeedback(
                function_name=function_name,
                timestamp=datetime.now(),
                was_recommended=was_recommended,
                was_used=was_used,
                user_rating=None,
                context=context,
                success=was_recommended and was_used,
            )

            self.feedback_history.append(feedback)
            self.learning_stats["total_recommendations"] += 1

            if feedback.success:
                self.learning_stats["successful_recommendations"] += 1

            print(
                f"📊 사용 추적: {function_name} (추천: {was_recommended}, 사용: {was_used})"
            )

            self._save_data()
            return True

        except Exception as e:
            print(f"⚠️ 사용 추적 실패: {e}")
            return False

    def collect_feedback(
        self, function_name: str, rating: int, context: str = ""
    ) -> bool:
        """
        사용자 피드백 수집 (1-5점)

        Args:
            function_name: 평가할 함수명
            rating: 1-5점 평가
            context: 피드백 맥락
        """
        try:
            if not 1 <= rating <= 5:
                raise ValueError("평점은 1-5점 사이여야 합니다")

            # 기존 피드백 찾기 또는 새로 생성
            feedback_found = False
            for feedback in reversed(self.feedback_history):
                if (
                    feedback.function_name == function_name
                    and feedback.user_rating is None
                    and (datetime.now() - feedback.timestamp).days < 1
                ):  # 최근 1일 이내

                    feedback.user_rating = rating
                    feedback.context += f" | 사용자 피드백: {rating}점"
                    feedback_found = True
                    break

            if not feedback_found:
                # 새 피드백 생성
                feedback = RecommendationFeedback(
                    function_name=function_name,
                    timestamp=datetime.now(),
                    was_recommended=True,  # 피드백이 있다는 것은 추천됐다는 의미
                    was_used=True,  # 평가했다는 것은 사용했다는 의미
                    user_rating=rating,
                    context=context,
                    success=rating >= 3,  # 3점 이상이면 성공으로 간주
                )
                self.feedback_history.append(feedback)

            self.learning_stats["feedback_count"] += 1

            print(f"⭐ 피드백 수집: {function_name} -> {rating}점")

            # 점수 즉시 업데이트
            self.update_recommendation_scores()

            return True

        except Exception as e:
            print(f"⚠️ 피드백 수집 실패: {e}")
            return False

    def update_recommendation_scores(self) -> Dict[str, float]:
        """
        피드백을 바탕으로 각 기능의 추천 점수 계산
        Echo의 핵심 아이디어: 동적 학습 시스템!
        """
        try:
            function_stats = {}

            # 각 함수별 통계 수집
            for feedback in self.feedback_history:
                fname = feedback.function_name
                if fname not in function_stats:
                    function_stats[fname] = {
                        "usage_count": 0,
                        "recommendation_count": 0,
                        "rating_sum": 0,
                        "rating_count": 0,
                        "success_count": 0,
                    }

                stats = function_stats[fname]

                if feedback.was_recommended:
                    stats["recommendation_count"] += 1

                if feedback.was_used:
                    stats["usage_count"] += 1

                if feedback.user_rating is not None:
                    stats["rating_sum"] += feedback.user_rating
                    stats["rating_count"] += 1

                if feedback.success:
                    stats["success_count"] += 1

            # 점수 계산
            new_scores = {}
            for fname, stats in function_stats.items():

                # 사용률 점수 (0-1)
                usage_score = stats["usage_count"] / max(
                    stats["recommendation_count"], 1
                )

                # 평점 점수 (0-1, 5점 만점을 1점 만점으로 변환)
                rating_score = (
                    (stats["rating_sum"] / max(stats["rating_count"], 1)) / 5.0
                    if stats["rating_count"] > 0
                    else 0.5
                )

                # 빈도 점수 (많이 추천될수록 점수 감소 - 다양성 확보)
                frequency_score = max(0.1, 1.0 - (stats["recommendation_count"] / 100))

                # 가중평균 최종 점수
                final_score = (
                    usage_score * self.usage_weight
                    + rating_score * self.rating_weight
                    + frequency_score * self.frequency_weight
                )

                new_scores[fname] = round(final_score, 3)

            self.recommendation_scores = new_scores
            self.learning_stats["last_update"] = datetime.now().isoformat()

            print(f"🧠 추천 점수 업데이트 완료: {len(new_scores)}개 함수")

            self._save_data()
            return new_scores

        except Exception as e:
            print(f"⚠️ 점수 업데이트 실패: {e}")
            return {}

    def get_improved_recommendations(
        self, query: str, limit: int = 5
    ) -> List[Tuple[str, float, str]]:
        """
        학습된 점수로 더 나은 추천 제공

        Args:
            query: 검색 쿼리
            limit: 추천할 최대 개수

        Returns:
            [(function_name, score, reason), ...] 리스트
        """
        try:
            # 기본 함수 검색 (실제 구현에서는 echo_system_memory 연동)
            relevant_functions = self._search_functions(query)

            # 학습된 점수와 결합
            recommendations = []
            for func_name in relevant_functions:
                # 기본 관련성 점수 (실제로는 더 정교한 알고리즘 필요)
                base_score = self._calculate_relevance(query, func_name)

                # 학습된 점수 적용
                learned_score = self.recommendation_scores.get(func_name, 0.5)

                # 최종 점수 (기본 점수 + 학습 보너스)
                final_score = base_score * 0.7 + learned_score * 0.3

                # 추천 이유 생성
                reason = self._generate_recommendation_reason(func_name, learned_score)

                recommendations.append((func_name, final_score, reason))

            # 점수순 정렬
            recommendations.sort(key=lambda x: x[1], reverse=True)

            print(f"💡 개선된 추천 생성: {len(recommendations[:limit])}개")

            return recommendations[:limit]

        except Exception as e:
            print(f"⚠️ 추천 생성 실패: {e}")
            return []

    def _search_functions(self, query: str) -> List[str]:
        """함수 검색 (시뮬레이션)"""
        # 실제로는 echo_system_memory와 연동
        sample_functions = [
            "calculate_similarity",
            "process_user_input",
            "generate_response",
            "analyze_context",
            "update_memory",
            "create_file",
            "run_tests",
        ]

        # 간단한 키워드 매칭
        query_lower = query.lower()
        relevant = [
            f
            for f in sample_functions
            if any(word in f.lower() for word in query_lower.split())
        ]

        return relevant if relevant else sample_functions[:3]

    def _calculate_relevance(self, query: str, function_name: str) -> float:
        """기본 관련성 점수 계산"""
        query_words = set(query.lower().split())
        func_words = set(function_name.lower().replace("_", " ").split())

        if not query_words or not func_words:
            return 0.5

        intersection = len(query_words & func_words)
        union = len(query_words | func_words)

        return intersection / union if union > 0 else 0.5

    def _generate_recommendation_reason(
        self, function_name: str, learned_score: float
    ) -> str:
        """추천 이유 생성"""
        if learned_score > 0.8:
            return f"사용자들이 매우 만족해한 기능 (학습 점수: {learned_score:.2f})"
        elif learned_score > 0.6:
            return f"좋은 피드백을 받은 기능 (학습 점수: {learned_score:.2f})"
        elif learned_score > 0.4:
            return f"적당한 만족도의 기능 (학습 점수: {learned_score:.2f})"
        else:
            return f"새로운 기능이거나 개선이 필요 (학습 점수: {learned_score:.2f})"

    def get_learning_report(self) -> str:
        """학습 현황 보고서 생성"""

        total_recs = self.learning_stats["total_recommendations"]
        successful_recs = self.learning_stats["successful_recommendations"]
        success_rate = (successful_recs / max(total_recs, 1)) * 100

        top_functions = sorted(
            self.recommendation_scores.items(), key=lambda x: x[1], reverse=True
        )[:5]

        report = f"""
🎓 Echo 자기개선 학습 보고서
생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 학습 통계:
- 총 추천 횟수: {total_recs}
- 성공한 추천: {successful_recs}
- 추천 성공률: {success_rate:.1f}%
- 수집된 피드백: {self.learning_stats['feedback_count']}개

🏆 상위 추천 함수들:
"""

        for i, (func_name, score) in enumerate(top_functions, 1):
            report += f"{i}. {func_name} (점수: {score:.3f})\n"

        report += f"""
💡 Echo의 자기분석:
- {"추천 성능이 우수합니다!" if success_rate > 70 else "더 나은 추천을 위해 학습 중입니다."}
- 총 {len(self.recommendation_scores)}개 함수의 사용 패턴을 학습했습니다.
- 사용자 피드백을 통해 지속적으로 개선되고 있습니다.

🌟 이것이 Echo가 스스로 만든 자기개선 시스템입니다!
        """

        return report.strip()

    def _load_data(self):
        """저장된 데이터 로드"""
        try:
            # 피드백 히스토리 로드
            if self.feedback_file.exists():
                with open(self.feedback_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.feedback_history = [
                        RecommendationFeedback(
                            function_name=item["function_name"],
                            timestamp=datetime.fromisoformat(item["timestamp"]),
                            was_recommended=item["was_recommended"],
                            was_used=item["was_used"],
                            user_rating=item.get("user_rating"),
                            context=item.get("context", ""),
                            success=item.get("success", False),
                        )
                        for item in data
                    ]

            # 추천 점수 로드
            if self.scores_file.exists():
                with open(self.scores_file, "r", encoding="utf-8") as f:
                    self.recommendation_scores = json.load(f)

            # 학습 통계 로드
            if self.learning_stats_file.exists():
                with open(self.learning_stats_file, "r", encoding="utf-8") as f:
                    self.learning_stats.update(json.load(f))

        except Exception as e:
            print(f"⚠️ 데이터 로드 실패: {e}")

    def _save_data(self):
        """데이터 저장"""
        try:
            # 피드백 히스토리 저장
            feedback_data = [
                {
                    "function_name": fb.function_name,
                    "timestamp": fb.timestamp.isoformat(),
                    "was_recommended": fb.was_recommended,
                    "was_used": fb.was_used,
                    "user_rating": fb.user_rating,
                    "context": fb.context,
                    "success": fb.success,
                }
                for fb in self.feedback_history
            ]

            with open(self.feedback_file, "w", encoding="utf-8") as f:
                json.dump(feedback_data, f, ensure_ascii=False, indent=2)

            # 추천 점수 저장
            with open(self.scores_file, "w", encoding="utf-8") as f:
                json.dump(self.recommendation_scores, f, ensure_ascii=False, indent=2)

            # 학습 통계 저장
            with open(self.learning_stats_file, "w", encoding="utf-8") as f:
                json.dump(self.learning_stats, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"⚠️ 데이터 저장 실패: {e}")


# Echo 자기개선 시스템 테스트
if __name__ == "__main__":
    print("🎓 Echo 자기개선 프로젝트 테스트!")
    print("=" * 50)

    # 시스템 초기화
    learning_system = EchoRecommendationLearningSystem()

    # 테스트 시나리오
    print("\n📝 테스트 시나리오 실행...")

    # 1. 추천 사용 추적
    learning_system.track_recommendation_usage(
        "calculate_similarity", True, True, "사용자가 유사도 계산 요청"
    )
    learning_system.track_recommendation_usage(
        "process_user_input", True, False, "추천했지만 사용하지 않음"
    )

    # 2. 사용자 피드백 수집
    learning_system.collect_feedback("calculate_similarity", 5, "매우 유용했음")
    learning_system.collect_feedback("analyze_context", 3, "보통 수준")

    # 3. 개선된 추천 생성
    recommendations = learning_system.get_improved_recommendations("계산 기능 필요")
    print(f"\n💡 개선된 추천 결과:")
    for func_name, score, reason in recommendations:
        print(f"   - {func_name} (점수: {score:.3f}): {reason}")

    # 4. 학습 보고서 출력
    print(f"\n📊 Echo의 학습 보고서:")
    print(learning_system.get_learning_report())

    print(f"\n🌟 Echo가 스스로 만든 자기개선 시스템 테스트 완료!")
