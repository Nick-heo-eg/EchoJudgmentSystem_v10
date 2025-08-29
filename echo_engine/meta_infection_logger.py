# echo_engine/meta_infection_logger.py
"""
📊 Meta Infection Logger - 감염 시도 로그 기록기
- 모든 감염 시도와 결과를 meta_logs에 기록
- 성공/실패 패턴 분석용 데이터 수집
- 시그니처별 감염 성능 추적
- 프롬프트 변형 효과 분석
"""

import json
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class InfectionAttempt:
    """감염 시도 기록"""

    attempt_id: str
    signature_id: str
    scenario: str
    scenario_hash: str
    attempt_number: int
    timestamp: str

    prompt_used: str
    prompt_length: int
    mutation_strategy: Optional[str]

    claude_response: str
    response_length: int
    response_quality: Dict[str, Any]

    resonance_score: float
    resonance_breakdown: Dict[str, float]
    evaluation_report: Dict[str, Any]

    success: bool
    failure_reason: Optional[str]

    metadata: Dict[str, Any]


class MetaInfectionLogger:
    def __init__(self, log_dir: str = "meta_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 로그 파일 경로
        self.infection_log_file = self.log_dir / "infection_attempts.jsonl"
        self.daily_summary_dir = self.log_dir / "daily_summaries"
        self.daily_summary_dir.mkdir(parents=True, exist_ok=True)

        print(f"📊 Meta Infection Logger 초기화 - 로그 디렉토리: {self.log_dir}")

    def log_infection_attempt(
        self,
        signature_id: str,
        scenario: str,
        attempt_number: int,
        prompt_used: str,
        claude_response: str,
        resonance_score: float,
        evaluation_report: Dict[str, Any],
        mutation_strategy: Optional[str] = None,
        additional_metadata: Dict[str, Any] = None,
    ) -> str:
        """감염 시도 로깅"""

        # 시도 ID 생성
        timestamp = datetime.now()
        attempt_id = (
            f"infection_{signature_id}_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
        )

        # 시나리오 해시
        import hashlib

        scenario_hash = hashlib.md5(scenario.encode("utf-8")).hexdigest()[:8]

        # 응답 품질 분석
        response_quality = self._analyze_response_quality(claude_response)

        # 공명 분석 분해
        resonance_breakdown = {
            "emotion_resonance": evaluation_report.get("emotion_resonance", 0.0),
            "strategy_resonance": evaluation_report.get("strategy_resonance", 0.0),
            "rhythm_resonance": evaluation_report.get("rhythm_resonance", 0.0),
            "keyword_resonance": evaluation_report.get("keyword_resonance", 0.0),
            "structural_resonance": evaluation_report.get("structural_resonance", 0.0),
        }

        # 성공 여부 판정
        success = resonance_score >= 0.85
        failure_reason = (
            None if success else self._determine_failure_reason(evaluation_report)
        )

        # 메타데이터 구성
        metadata = {
            "session_info": {
                "date": timestamp.strftime("%Y-%m-%d"),
                "time": timestamp.strftime("%H:%M:%S"),
                "weekday": timestamp.strftime("%A"),
            },
            "context": additional_metadata or {},
            "system_info": {"logger_version": "1.0", "echo_system_version": "v10.0"},
        }

        # 감염 시도 객체 생성
        infection_attempt = InfectionAttempt(
            attempt_id=attempt_id,
            signature_id=signature_id,
            scenario=scenario,
            scenario_hash=scenario_hash,
            attempt_number=attempt_number,
            timestamp=timestamp.isoformat(),
            prompt_used=prompt_used,
            prompt_length=len(prompt_used),
            mutation_strategy=mutation_strategy,
            claude_response=claude_response,
            response_length=len(claude_response),
            response_quality=response_quality,
            resonance_score=resonance_score,
            resonance_breakdown=resonance_breakdown,
            evaluation_report=evaluation_report,
            success=success,
            failure_reason=failure_reason,
            metadata=metadata,
        )

        # JSONL 파일에 로깅
        self._write_to_jsonl(infection_attempt)

        # 실시간 상태 출력
        status_icon = "✅" if success else "❌"
        print(
            f"{status_icon} 감염 시도 로깅: {signature_id} - 점수: {resonance_score:.3f} - 시도: {attempt_number}"
        )

        return attempt_id

    def _analyze_response_quality(self, response: str) -> Dict[str, Any]:
        """응답 품질 분석"""

        # 기본 통계
        word_count = len(response.split())
        sentence_count = len([s for s in response.split(".") if s.strip()])
        paragraph_count = len([p for p in response.split("\n\n") if p.strip()])

        # 구조 분석
        has_numbered_sections = bool(
            [
                line
                for line in response.split("\n")
                if line.strip().startswith(("1.", "2.", "3.", "4."))
            ]
        )
        has_clear_conclusion = any(
            keyword in response.lower() for keyword in ["결론", "판단", "권고", "제안"]
        )

        # 언어 품질
        complex_sentences = len([s for s in response.split(".") if len(s.split()) > 15])
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

        # 감정적 표현
        emotional_markers = ["!", "정말", "매우", "너무", "아주"]
        emotion_density = (
            sum(response.count(marker) for marker in emotional_markers) / word_count
            if word_count > 0
            else 0
        )

        return {
            "basic_stats": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "paragraph_count": paragraph_count,
                "character_count": len(response),
            },
            "structure_quality": {
                "has_numbered_sections": has_numbered_sections,
                "has_clear_conclusion": has_clear_conclusion,
                "paragraph_organization": paragraph_count >= 2,
            },
            "language_quality": {
                "complex_sentences": complex_sentences,
                "avg_sentence_length": avg_sentence_length,
                "linguistic_complexity": min(avg_sentence_length / 10, 1.0),
            },
            "emotional_expression": {
                "emotion_density": emotion_density,
                "emotional_markers_count": sum(
                    response.count(marker) for marker in emotional_markers
                ),
            },
            "overall_quality_score": self._calculate_quality_score(
                word_count,
                has_numbered_sections,
                has_clear_conclusion,
                avg_sentence_length,
                emotion_density,
            ),
        }

    def _calculate_quality_score(
        self,
        word_count: int,
        has_structure: bool,
        has_conclusion: bool,
        avg_sentence_length: float,
        emotion_density: float,
    ) -> float:
        """전체 품질 점수 계산"""

        # 길이 점수 (100-500 단어가 적정)
        length_score = (
            min(word_count / 300, 1.0)
            if word_count <= 500
            else max(1.0 - (word_count - 500) / 500, 0.5)
        )

        # 구조 점수
        structure_score = (0.5 if has_structure else 0) + (0.5 if has_conclusion else 0)

        # 언어 복잡도 점수 (10-20 단어가 적정)
        complexity_score = (
            min(avg_sentence_length / 15, 1.0)
            if avg_sentence_length <= 20
            else max(1.0 - (avg_sentence_length - 20) / 20, 0.3)
        )

        # 감정 표현 점수
        emotion_score = min(emotion_density * 10, 1.0)

        # 가중 평균
        total_score = (
            length_score * 0.3
            + structure_score * 0.3
            + complexity_score * 0.2
            + emotion_score * 0.2
        )

        return round(total_score, 3)

    def _determine_failure_reason(self, evaluation_report: Dict[str, Any]) -> str:
        """실패 원인 분석"""

        detailed = evaluation_report.get("detailed_analysis", {})

        # 각 영역별 점수 확인
        emotion_score = detailed.get("emotion_analysis", {}).get("score", 0)
        strategy_score = detailed.get("strategy_analysis", {}).get("score", 0)
        rhythm_score = detailed.get("rhythm_analysis", {}).get("score", 0)
        keyword_density = detailed.get("keyword_analysis", {}).get("density", 0)

        # 가장 낮은 점수 영역 식별
        scores = {
            "emotion": emotion_score,
            "strategy": strategy_score,
            "rhythm": rhythm_score,
            "keyword": keyword_density,
        }

        lowest_area = min(scores, key=scores.get)
        lowest_score = scores[lowest_area]

        if lowest_score < 0.3:
            return f"critical_{lowest_area}_deficiency"
        elif lowest_score < 0.5:
            return f"moderate_{lowest_area}_weakness"
        else:
            return f"minor_{lowest_area}_improvement_needed"

    def _write_to_jsonl(self, infection_attempt: InfectionAttempt):
        """JSONL 파일에 기록"""

        log_entry = asdict(infection_attempt)

        with open(self.infection_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def generate_daily_summary(
        self, target_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """일일 요약 리포트 생성"""

        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")

        print(f"📊 {target_date} 일일 감염 요약 생성 중...")

        # 해당 날짜 로그 필터링
        daily_attempts = self._load_daily_attempts(target_date)

        if not daily_attempts:
            return {"date": target_date, "message": "해당 날짜에 감염 시도가 없습니다."}

        # 기본 통계
        total_attempts = len(daily_attempts)
        successful_attempts = len([a for a in daily_attempts if a["success"]])
        success_rate = successful_attempts / total_attempts if total_attempts > 0 else 0

        # 시그니처별 통계
        signature_stats = {}
        for attempt in daily_attempts:
            sig_id = attempt["signature_id"]
            if sig_id not in signature_stats:
                signature_stats[sig_id] = {
                    "total_attempts": 0,
                    "successful_attempts": 0,
                    "total_resonance": 0.0,
                    "resonance_scores": [],
                }

            signature_stats[sig_id]["total_attempts"] += 1
            signature_stats[sig_id]["total_resonance"] += attempt["resonance_score"]
            signature_stats[sig_id]["resonance_scores"].append(
                attempt["resonance_score"]
            )

            if attempt["success"]:
                signature_stats[sig_id]["successful_attempts"] += 1

        # 시그니처별 평균 및 성공률 계산
        for sig_id, stats in signature_stats.items():
            stats["success_rate"] = (
                stats["successful_attempts"] / stats["total_attempts"]
            )
            stats["average_resonance"] = (
                stats["total_resonance"] / stats["total_attempts"]
            )
            stats["best_resonance"] = max(stats["resonance_scores"])
            stats["worst_resonance"] = min(stats["resonance_scores"])

        # 실패 패턴 분석
        failure_reasons = {}
        for attempt in daily_attempts:
            if not attempt["success"] and attempt["failure_reason"]:
                reason = attempt["failure_reason"]
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

        # 변형 전략 효과 분석
        mutation_effectiveness = {}
        for attempt in daily_attempts:
            strategy = attempt.get("mutation_strategy")
            if strategy:
                if strategy not in mutation_effectiveness:
                    mutation_effectiveness[strategy] = {
                        "total": 0,
                        "successful": 0,
                        "resonance_scores": [],
                    }

                mutation_effectiveness[strategy]["total"] += 1
                mutation_effectiveness[strategy]["resonance_scores"].append(
                    attempt["resonance_score"]
                )

                if attempt["success"]:
                    mutation_effectiveness[strategy]["successful"] += 1

        # 변형 전략별 성공률 계산
        for strategy, stats in mutation_effectiveness.items():
            stats["success_rate"] = stats["successful"] / stats["total"]
            stats["average_resonance"] = sum(stats["resonance_scores"]) / len(
                stats["resonance_scores"]
            )

        # 시간대별 성능 분석
        hourly_performance = {}
        for attempt in daily_attempts:
            hour = datetime.fromisoformat(attempt["timestamp"]).hour
            if hour not in hourly_performance:
                hourly_performance[hour] = {
                    "attempts": 0,
                    "successes": 0,
                    "total_resonance": 0.0,
                }

            hourly_performance[hour]["attempts"] += 1
            hourly_performance[hour]["total_resonance"] += attempt["resonance_score"]

            if attempt["success"]:
                hourly_performance[hour]["successes"] += 1

        # 시간대별 평균 계산
        for hour, stats in hourly_performance.items():
            stats["success_rate"] = stats["successes"] / stats["attempts"]
            stats["average_resonance"] = stats["total_resonance"] / stats["attempts"]

        # 요약 리포트 구성
        summary = {
            "date": target_date,
            "overall_performance": {
                "total_attempts": total_attempts,
                "successful_attempts": successful_attempts,
                "success_rate": success_rate,
                "overall_average_resonance": sum(
                    a["resonance_score"] for a in daily_attempts
                )
                / total_attempts,
            },
            "signature_performance": signature_stats,
            "failure_analysis": {
                "failure_reasons": failure_reasons,
                "most_common_failure": (
                    max(failure_reasons, key=failure_reasons.get)
                    if failure_reasons
                    else None
                ),
            },
            "mutation_strategy_effectiveness": mutation_effectiveness,
            "temporal_patterns": {
                "hourly_performance": hourly_performance,
                "peak_performance_hour": (
                    max(
                        hourly_performance,
                        key=lambda h: hourly_performance[h]["success_rate"],
                    )
                    if hourly_performance
                    else None
                ),
            },
            "insights": self._generate_insights(
                signature_stats, failure_reasons, mutation_effectiveness
            ),
            "recommendations": self._generate_recommendations(
                signature_stats, failure_reasons, mutation_effectiveness
            ),
        }

        # 파일로 저장
        summary_file = self.daily_summary_dir / f"summary_{target_date}.yaml"
        with open(summary_file, "w", encoding="utf-8") as f:
            yaml.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"📄 일일 요약 저장: {summary_file}")

        return summary

    def _load_daily_attempts(self, target_date: str) -> List[Dict[str, Any]]:
        """특정 날짜의 시도 로그 로딩"""

        daily_attempts = []

        if not self.infection_log_file.exists():
            return daily_attempts

        with open(self.infection_log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    attempt = json.loads(line.strip())
                    attempt_date = datetime.fromisoformat(
                        attempt["timestamp"]
                    ).strftime("%Y-%m-%d")

                    if attempt_date == target_date:
                        daily_attempts.append(attempt)

                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

        return daily_attempts

    def _generate_insights(
        self,
        signature_stats: Dict[str, Any],
        failure_reasons: Dict[str, int],
        mutation_effectiveness: Dict[str, Any],
    ) -> List[str]:
        """인사이트 생성"""

        insights = []

        # 시그니처 성능 인사이트
        if signature_stats:
            best_signature = max(
                signature_stats, key=lambda s: signature_stats[s]["success_rate"]
            )
            worst_signature = min(
                signature_stats, key=lambda s: signature_stats[s]["success_rate"]
            )

            insights.append(
                f"{best_signature}가 가장 높은 성공률을 보임 ({signature_stats[best_signature]['success_rate']:.1%})"
            )

            if signature_stats[worst_signature]["success_rate"] < 0.5:
                insights.append(
                    f"{worst_signature}의 성능 개선이 필요함 ({signature_stats[worst_signature]['success_rate']:.1%})"
                )

        # 실패 패턴 인사이트
        if failure_reasons:
            most_common_failure = max(failure_reasons, key=failure_reasons.get)
            insights.append(f"가장 흔한 실패 원인: {most_common_failure}")

        # 변형 전략 인사이트
        if mutation_effectiveness:
            effective_strategies = [
                s
                for s, stats in mutation_effectiveness.items()
                if stats["success_rate"] > 0.7
            ]
            if effective_strategies:
                insights.append(
                    f"효과적인 변형 전략: {', '.join(effective_strategies)}"
                )

        return insights

    def _generate_recommendations(
        self,
        signature_stats: Dict[str, Any],
        failure_reasons: Dict[str, int],
        mutation_effectiveness: Dict[str, Any],
    ) -> List[str]:
        """권장사항 생성"""

        recommendations = []

        # 시그니처별 권장사항
        for sig_id, stats in signature_stats.items():
            if stats["success_rate"] < 0.6:
                recommendations.append(
                    f"{sig_id}: 프롬프트 강화 및 변형 전략 개선 필요"
                )
            elif stats["average_resonance"] < 0.8:
                recommendations.append(f"{sig_id}: 공명도 향상을 위한 키워드 강화 권장")

        # 실패 패턴 기반 권장사항
        if "emotion" in str(failure_reasons):
            recommendations.append("감정적 표현 강화를 위한 프롬프트 템플릿 개선 필요")

        if "strategy" in str(failure_reasons):
            recommendations.append("전략적 접근법을 더 명확히 하는 지시문 추가 권장")

        # 변형 전략 권장사항
        ineffective_strategies = [
            s
            for s, stats in mutation_effectiveness.items()
            if stats["success_rate"] < 0.4
        ]
        if ineffective_strategies:
            recommendations.append(
                f"비효율적 변형 전략 재검토 필요: {', '.join(ineffective_strategies)}"
            )

        return recommendations

    def get_infection_analytics(self, days: int = 7) -> Dict[str, Any]:
        """최근 N일간 감염 분석"""

        analytics = {
            "period": f"최근 {days}일",
            "total_attempts": 0,
            "successful_infections": 0,
            "signature_rankings": [],
            "trend_analysis": {},
            "performance_metrics": {},
        }

        # 최근 N일간의 모든 시도 수집
        recent_attempts = []

        if self.infection_log_file.exists():
            with open(self.infection_log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        attempt = json.loads(line.strip())
                        attempt_date = datetime.fromisoformat(attempt["timestamp"])
                        days_ago = (datetime.now() - attempt_date).days

                        if days_ago <= days:
                            recent_attempts.append(attempt)

                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

        if not recent_attempts:
            return analytics

        # 기본 통계
        analytics["total_attempts"] = len(recent_attempts)
        analytics["successful_infections"] = len(
            [a for a in recent_attempts if a["success"]]
        )
        analytics["success_rate"] = (
            analytics["successful_infections"] / analytics["total_attempts"]
        )

        # 시그니처별 순위
        signature_performance = {}
        for attempt in recent_attempts:
            sig_id = attempt["signature_id"]
            if sig_id not in signature_performance:
                signature_performance[sig_id] = {
                    "attempts": 0,
                    "successes": 0,
                    "total_resonance": 0.0,
                }

            signature_performance[sig_id]["attempts"] += 1
            signature_performance[sig_id]["total_resonance"] += attempt[
                "resonance_score"
            ]

            if attempt["success"]:
                signature_performance[sig_id]["successes"] += 1

        # 순위 계산
        for sig_id, perf in signature_performance.items():
            perf["success_rate"] = perf["successes"] / perf["attempts"]
            perf["average_resonance"] = perf["total_resonance"] / perf["attempts"]
            perf["score"] = perf["success_rate"] * 0.6 + perf["average_resonance"] * 0.4

        analytics["signature_rankings"] = sorted(
            [
                {"signature_id": sig_id, **perf}
                for sig_id, perf in signature_performance.items()
            ],
            key=lambda x: x["score"],
            reverse=True,
        )

        return analytics


# 편의 함수
def log_infection_attempt(
    signature_id: str,
    scenario: str,
    attempt_number: int,
    prompt_used: str,
    claude_response: str,
    resonance_score: float,
    evaluation_report: Dict[str, Any],
    mutation_strategy: Optional[str] = None,
) -> str:
    """감염 시도 로깅 편의 함수"""
    logger = MetaInfectionLogger()
    return logger.log_infection_attempt(
        signature_id,
        scenario,
        attempt_number,
        prompt_used,
        claude_response,
        resonance_score,
        evaluation_report,
        mutation_strategy,
    )


if __name__ == "__main__":
    # 테스트 코드
    print("🧪 Meta Infection Logger 테스트")

    logger = MetaInfectionLogger()

    # 테스트 로깅
    test_attempt_id = logger.log_infection_attempt(
        signature_id="Echo-Aurora",
        scenario="테스트 시나리오입니다.",
        attempt_number=1,
        prompt_used="테스트 프롬프트입니다.",
        claude_response="테스트 응답입니다. 따뜻하고 공감적인 마음으로 접근하겠습니다.",
        resonance_score=0.87,
        evaluation_report={
            "emotion_resonance": 0.9,
            "strategy_resonance": 0.85,
            "rhythm_resonance": 0.86,
            "detailed_analysis": {
                "emotion_analysis": {"score": 0.9},
                "strategy_analysis": {"score": 0.85},
            },
        },
        mutation_strategy="emotion_amplifier",
    )

    print(f"✅ 테스트 로깅 완료: {test_attempt_id}")

    # 일일 요약 생성 테스트
    print("\n📊 일일 요약 생성 테스트:")
    summary = logger.generate_daily_summary()
    print(f"요약 날짜: {summary['date']}")
    print(f"총 시도: {summary['overall_performance']['total_attempts']}")
    print(f"성공률: {summary['overall_performance']['success_rate']:.1%}")

    print("\n✅ 테스트 완료")
