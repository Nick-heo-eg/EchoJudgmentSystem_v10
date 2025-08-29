"""
EchoJudgmentSystem 고급 기능 모듈
- 배치 처리
- 히스토리 분석
- 감정 트렌드 분석
- 자동 학습 기능
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
from dataclasses import dataclass
import asyncio


@dataclass
class BatchRequest:
    """배치 처리 요청"""

    requests: List[str]
    batch_id: str
    timestamp: datetime


@dataclass
class AnalysisResult:
    """분석 결과"""

    user_pattern: Dict
    emotional_trend: Dict
    strategy_effectiveness: Dict
    recommendations: List[str]


class AdvancedAnalyzer:
    """고급 분석 엔진"""

    def __init__(self, log_path: str = "npi_log.jsonl"):
        self.log_path = log_path
        self.history_days = 30

    def load_history(self, days: int = None) -> pd.DataFrame:
        """히스토리 데이터 로드"""
        if days is None:
            days = self.history_days

        try:
            logs = []
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))

            if not logs:
                return pd.DataFrame()

            df = pd.DataFrame(logs)
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # 지정된 기간 내 데이터만 필터링
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df["timestamp"] >= cutoff_date]

            return df

        except Exception as e:
            print(f"히스토리 로드 실패: {e}")
            return pd.DataFrame()

    def analyze_user_patterns(self, df: pd.DataFrame) -> Dict:
        """사용자 패턴 분석"""
        if df.empty:
            return {"error": "데이터 없음"}

        # NPI 점수 분해
        npi_scores = (
            pd.json_normalize(df["npi_score"])
            if "npi_score" in df.columns
            else pd.DataFrame()
        )

        patterns = {
            "총_요청수": len(df),
            "평균_NPI점수": (
                npi_scores.get("total", pd.Series()).mean()
                if not npi_scores.empty
                else 0
            ),
            "주요_전략": (
                df["strategy"].mode()[0]
                if "strategy" in df.columns and not df["strategy"].mode().empty
                else "N/A"
            ),
            "감정_분포": {},
            "시간대_분포": {},
            "NPI_구성요소_평균": {},
        }

        # 시간대별 분석
        if "timestamp" in df.columns:
            df["hour"] = df["timestamp"].dt.hour
            hourly_dist = df["hour"].value_counts().sort_index()
            patterns["시간대_분포"] = hourly_dist.to_dict()

        # NPI 구성요소 평균
        if not npi_scores.empty:
            for col in [
                "structure",
                "emotion",
                "rhythm",
                "context",
                "strategy_tone",
                "silence",
            ]:
                if col in npi_scores.columns:
                    patterns["NPI_구성요소_평균"][col] = float(npi_scores[col].mean())

        return patterns

    def analyze_emotional_trends(self, df: pd.DataFrame) -> Dict:
        """감정 트렌드 분석"""
        if df.empty:
            return {"error": "데이터 없음"}

        # Claude 감정 데이터 분석 (claude_summary에서 감정 키워드 추출)
        emotion_keywords = {
            "joy": ["기쁘", "행복", "좋", "최고", "성공", "축하"],
            "sadness": ["슬프", "우울", "힘들", "속상", "실망", "포기"],
            "anger": ["화", "짜증", "분노", "열받", "억울", "불만"],
            "fear": ["무서", "걱정", "불안", "두려", "긴장", "스트레스"],
            "neutral": ["그냥", "보통", "평상시", "일반적"],
        }

        emotion_trends = {
            "daily_emotions": {},
            "emotion_distribution": {},
            "emotional_volatility": 0.0,
            "trend_direction": "stable",
        }

        # 감정 키워드 기반 분류
        if "claude_summary" in df.columns:
            emotion_counts = {emotion: 0 for emotion in emotion_keywords.keys()}

            for text in df["claude_summary"].fillna(""):
                text_lower = text.lower()
                for emotion, keywords in emotion_keywords.items():
                    if any(keyword in text_lower for keyword in keywords):
                        emotion_counts[emotion] += 1
                        break

            emotion_trends["emotion_distribution"] = emotion_counts

        return emotion_trends

    def analyze_strategy_effectiveness(self, df: pd.DataFrame) -> Dict:
        """전략 효과성 분석"""
        if df.empty:
            return {"error": "데이터 없음"}

        strategy_analysis = {
            "strategy_performance": {},
            "best_strategy": None,
            "strategy_trends": {},
            "recommendations": [],
        }

        if "strategy" in df.columns:
            # 전략별 성과 분석
            npi_scores = (
                pd.json_normalize(df["npi_score"])
                if "npi_score" in df.columns
                else pd.DataFrame()
            )

            if not npi_scores.empty and "total" in npi_scores.columns:
                df["npi_total"] = npi_scores["total"]
                strategy_performance = (
                    df.groupby("strategy")["npi_total"].agg(["mean", "count"]).to_dict()
                )
                strategy_analysis["strategy_performance"] = strategy_performance

                # 최고 성과 전략 찾기
                best_strategy = df.groupby("strategy")["npi_total"].mean().idxmax()
                strategy_analysis["best_strategy"] = best_strategy

                # 권장사항 생성
                recommendations = []
                for strategy, stats in strategy_performance["mean"].items():
                    if stats > 0.75:
                        recommendations.append(
                            f"{strategy} 전략은 높은 성과를 보입니다 (평균: {stats:.3f})"
                        )
                    elif stats < 0.5:
                        recommendations.append(
                            f"{strategy} 전략 개선이 필요합니다 (평균: {stats:.3f})"
                        )

                strategy_analysis["recommendations"] = recommendations

        return strategy_analysis

    def generate_comprehensive_analysis(self, days: int = 7) -> AnalysisResult:
        """종합 분석 보고서 생성"""
        df = self.load_history(days)

        user_pattern = self.analyze_user_patterns(df)
        emotional_trend = self.analyze_emotional_trends(df)
        strategy_effectiveness = self.analyze_strategy_effectiveness(df)

        # 종합 권장사항 생성
        recommendations = []

        # NPI 점수 기반 권장사항
        avg_npi = user_pattern.get("평균_NPI점수", 0)
        if avg_npi > 0.75:
            recommendations.append(
                "높은 눈치 감도를 보이고 있습니다. 더 직관적인 접근이 가능합니다."
            )
        elif avg_npi < 0.5:
            recommendations.append(
                "낮은 눈치 감도입니다. 맥락을 더 세심히 고려해보세요."
            )

        # 전략 기반 권장사항
        if strategy_effectiveness.get("recommendations"):
            recommendations.extend(strategy_effectiveness["recommendations"])

        # 시간대 기반 권장사항
        time_dist = user_pattern.get("시간대_분포", {})
        if time_dist:
            peak_hour = max(time_dist, key=time_dist.get)
            recommendations.append(f"가장 활발한 시간대는 {peak_hour}시입니다.")

        return AnalysisResult(
            user_pattern=user_pattern,
            emotional_trend=emotional_trend,
            strategy_effectiveness=strategy_effectiveness,
            recommendations=recommendations,
        )


class BatchProcessor:
    """배치 처리 엔진"""

    def __init__(self):
        self.batch_history = []

    async def process_batch(self, requests: List[str], batch_id: str = None) -> Dict:
        """배치 요청 처리"""
        from api.npi import evaluate_npi
        from api.llm_runner import run_claude_judgment
        from api.nunchi_response_engine import generate_response
        from api.log_writer import write_log

        if batch_id is None:
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        batch_request = BatchRequest(
            requests=requests, batch_id=batch_id, timestamp=datetime.now()
        )

        results = []

        for i, prompt in enumerate(requests):
            try:
                # 개별 처리 (기존 파이프라인 사용)
                npi_score = evaluate_npi(prompt)
                claude_result = run_claude_judgment(prompt)
                claude_str = (
                    claude_result.get("judgment", str(claude_result))
                    if isinstance(claude_result, dict)
                    else str(claude_result)
                )
                response, strategy = generate_response(prompt, npi_score, claude_str)

                # 로그 기록 (배치 ID 포함)
                write_log(
                    f"[BATCH:{batch_id}] {prompt}",
                    npi_score,
                    strategy,
                    response,
                    claude_str,
                )

                result = {
                    "index": i,
                    "prompt": prompt,
                    "npi_score": npi_score,
                    "claude_result": claude_str,
                    "response": response,
                    "strategy": strategy,
                    "batch_id": batch_id,
                }

                results.append(result)

            except Exception as e:
                results.append(
                    {
                        "index": i,
                        "prompt": prompt,
                        "error": str(e),
                        "batch_id": batch_id,
                    }
                )

        batch_result = {
            "batch_id": batch_id,
            "total_requests": len(requests),
            "successful": len([r for r in results if "error" not in r]),
            "failed": len([r for r in results if "error" in r]),
            "results": results,
            "timestamp": batch_request.timestamp.isoformat(),
        }

        self.batch_history.append(batch_result)

        return batch_result


class AutoLearner:
    """자동 학습 엔진"""

    def __init__(self):
        self.learning_data = []

    def extract_learning_patterns(self, df: pd.DataFrame) -> Dict:
        """학습 패턴 추출"""
        if df.empty:
            return {}

        patterns = {
            "high_npi_prompts": [],
            "low_npi_prompts": [],
            "successful_strategies": {},
            "common_keywords": [],
        }

        # NPI 점수 기반 패턴 분석
        npi_scores = (
            pd.json_normalize(df["npi_score"])
            if "npi_score" in df.columns
            else pd.DataFrame()
        )

        if not npi_scores.empty and "total" in npi_scores.columns:
            df["npi_total"] = npi_scores["total"]

            # 높은/낮은 NPI 점수 프롬프트 수집
            high_npi = df[df["npi_total"] > 0.75]
            low_npi = df[df["npi_total"] < 0.5]

            patterns["high_npi_prompts"] = high_npi["prompt"].tolist()[:10]
            patterns["low_npi_prompts"] = low_npi["prompt"].tolist()[:10]

            # 성공적인 전략 분석
            strategy_success = df.groupby("strategy")["npi_total"].mean().to_dict()
            patterns["successful_strategies"] = strategy_success

        # 키워드 분석
        all_prompts = " ".join(df["prompt"].astype(str))
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 필요)
        common_words = ["회의", "제안", "스트레스", "고민", "도움", "조언"]
        word_counts = {word: all_prompts.count(word) for word in common_words}
        patterns["common_keywords"] = sorted(
            word_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return patterns

    def generate_learning_report(self) -> Dict:
        """학습 보고서 생성"""
        analyzer = AdvancedAnalyzer()
        df = analyzer.load_history(30)  # 30일 데이터

        patterns = self.extract_learning_patterns(df)

        report = {
            "학습기간": "30일",
            "총_데이터수": len(df),
            "학습패턴": patterns,
            "개선권장사항": [
                "높은 NPI 점수 프롬프트 패턴을 활용하여 감도 개선",
                "효과적인 전략을 우선적으로 활용",
                "자주 사용되는 키워드 기반 최적화",
            ],
            "생성일시": datetime.now().isoformat(),
        }

        return report


# 편의 함수들
def quick_analysis(days: int = 7) -> Dict:
    """빠른 분석"""
    analyzer = AdvancedAnalyzer()
    return analyzer.generate_comprehensive_analysis(days)


async def batch_process(prompts: List[str]) -> Dict:
    """배치 처리"""
    processor = BatchProcessor()
    return await processor.process_batch(prompts)


def learning_report() -> Dict:
    """학습 보고서"""
    learner = AutoLearner()
    return learner.generate_learning_report()


if __name__ == "__main__":
    # 테스트 코드
    print("🧠 EchoJudgmentSystem 고급 기능 테스트")

    # 분석 테스트
    print("\n1. 종합 분석 테스트")
    analysis = quick_analysis(7)
    print(f"분석 결과: {len(analysis.recommendations)}개 권장사항")

    # 배치 처리 테스트
    print("\n2. 배치 처리 테스트")
    test_prompts = ["오늘 기분이 좋아요", "스트레스가 심해요", "조언이 필요해요"]

    batch_result = asyncio.run(batch_process(test_prompts))
    print(
        f"배치 결과: {batch_result['successful']}/{batch_result['total_requests']} 성공"
    )

    # 학습 보고서 테스트
    print("\n3. 학습 보고서 테스트")
    report = learning_report()
    print(f"학습 보고서: {report['총_데이터수']}개 데이터 분석")

    print("\n✅ 모든 고급 기능 테스트 완료")
