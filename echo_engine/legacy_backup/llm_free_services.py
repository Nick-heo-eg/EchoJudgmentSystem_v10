#!/usr/bin/env python3
"""
🚀 Echo System - LLM-Free Practical Services
실제 사람들이 유용하게 쓸 수 있는 LLM 없는 서비스들

핵심 철학:
- 복잡한 AI 없이도 구조화된 사고로 실용적 결과 제공
- 패턴 기반 분석과 템플릿 시스템 활용
- 투명하고 예측 가능한 로직
"""

import json
import yaml
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import csv


@dataclass
class DecisionContext:
    """의사결정 컨텍스트"""

    situation: str
    options: List[Dict[str, Any]]
    constraints: List[str]
    timeline: str
    priority_weights: Dict[str, float]


@dataclass
class AnalysisResult:
    """분석 결과"""

    recommended_option: str
    confidence_score: float
    reasoning_steps: List[str]
    risk_assessment: Dict[str, Any]
    alternative_scenarios: List[Dict[str, Any]]


class PracticalDecisionMaker:
    """🎯 실용적 의사결정 도우미 (LLM-Free)"""

    def __init__(self):
        self.decision_templates = self._load_decision_templates()
        self.scoring_algorithms = self._init_scoring_algorithms()

    def _load_decision_templates(self) -> Dict[str, Any]:
        """의사결정 템플릿 로드"""
        return {
            "career_change": {
                "factors": [
                    "salary",
                    "growth_potential",
                    "work_life_balance",
                    "job_security",
                    "location",
                ],
                "weights": {
                    "salary": 0.25,
                    "growth_potential": 0.3,
                    "work_life_balance": 0.2,
                    "job_security": 0.15,
                    "location": 0.1,
                },
                "risk_categories": ["financial", "professional", "personal", "market"],
            },
            "investment": {
                "factors": [
                    "expected_return",
                    "risk_level",
                    "liquidity",
                    "diversification",
                    "time_horizon",
                ],
                "weights": {
                    "expected_return": 0.3,
                    "risk_level": 0.25,
                    "liquidity": 0.15,
                    "diversification": 0.15,
                    "time_horizon": 0.15,
                },
                "risk_categories": ["market", "credit", "inflation", "liquidity"],
            },
            "housing": {
                "factors": ["price", "location", "size", "condition", "future_value"],
                "weights": {
                    "price": 0.25,
                    "location": 0.3,
                    "size": 0.2,
                    "condition": 0.15,
                    "future_value": 0.1,
                },
                "risk_categories": ["financial", "market", "maintenance", "location"],
            },
            "education": {
                "factors": [
                    "cost",
                    "reputation",
                    "program_quality",
                    "career_prospects",
                    "location",
                ],
                "weights": {
                    "cost": 0.2,
                    "reputation": 0.25,
                    "program_quality": 0.3,
                    "career_prospects": 0.2,
                    "location": 0.05,
                },
                "risk_categories": [
                    "financial",
                    "opportunity_cost",
                    "market_demand",
                    "personal",
                ],
            },
        }

    def _init_scoring_algorithms(self) -> Dict[str, Any]:
        """점수 계산 알고리즘 초기화"""
        return {
            "weighted_sum": self._weighted_sum_scoring,
            "topsis": self._topsis_scoring,
            "risk_adjusted": self._risk_adjusted_scoring,
        }

    def analyze_decision(
        self, context: DecisionContext, method: str = "weighted_sum"
    ) -> AnalysisResult:
        """의사결정 분석 실행"""

        # 템플릿 매칭
        template = self._match_template(context.situation)

        # 옵션별 점수 계산
        scores = []
        for option in context.options:
            score = self.scoring_algorithms[method](
                option, template, context.priority_weights
            )
            scores.append((option["name"], score, option))

        # 정렬 (점수 높은 순)
        scores.sort(key=lambda x: x[1], reverse=True)

        # 리스크 평가
        risk_assessment = self._assess_risks(scores[0][2], template)

        # 대안 시나리오
        alternative_scenarios = self._generate_alternatives(scores, context)

        # 추론 단계 생성
        reasoning_steps = self._generate_reasoning(scores, template, context)

        return AnalysisResult(
            recommended_option=scores[0][0],
            confidence_score=self._calculate_confidence(scores),
            reasoning_steps=reasoning_steps,
            risk_assessment=risk_assessment,
            alternative_scenarios=alternative_scenarios,
        )

    def _match_template(self, situation: str) -> Dict[str, Any]:
        """상황에 맞는 템플릿 매칭"""
        situation_lower = situation.lower()

        # 키워드 기반 매칭
        if any(
            keyword in situation_lower
            for keyword in ["job", "career", "직업", "커리어"]
        ):
            return self.decision_templates["career_change"]
        elif any(
            keyword in situation_lower
            for keyword in ["invest", "투자", "stock", "fund"]
        ):
            return self.decision_templates["investment"]
        elif any(
            keyword in situation_lower for keyword in ["house", "home", "집", "부동산"]
        ):
            return self.decision_templates["housing"]
        elif any(
            keyword in situation_lower
            for keyword in ["school", "university", "교육", "학교"]
        ):
            return self.decision_templates["education"]
        else:
            # 기본 템플릿
            return {
                "factors": ["cost", "benefit", "risk", "feasibility", "timeline"],
                "weights": {
                    "cost": 0.2,
                    "benefit": 0.3,
                    "risk": 0.2,
                    "feasibility": 0.2,
                    "timeline": 0.1,
                },
                "risk_categories": [
                    "financial",
                    "operational",
                    "strategic",
                    "external",
                ],
            }

    def _weighted_sum_scoring(
        self,
        option: Dict[str, Any],
        template: Dict[str, Any],
        user_weights: Dict[str, float],
    ) -> float:
        """가중합 점수 계산"""
        score = 0.0
        total_weight = 0.0

        # 사용자 가중치와 템플릿 가중치 결합
        combined_weights = {**template["weights"], **user_weights}

        for factor, weight in combined_weights.items():
            if factor in option:
                # 0-10 스케일로 정규화
                normalized_value = min(10, max(0, float(option.get(factor, 5))))
                score += normalized_value * weight
                total_weight += weight

        return score / total_weight if total_weight > 0 else 0.0

    def _topsis_scoring(
        self,
        option: Dict[str, Any],
        template: Dict[str, Any],
        user_weights: Dict[str, float],
    ) -> float:
        """TOPSIS 방법 기반 점수 계산"""
        # 간단한 TOPSIS 구현
        score = self._weighted_sum_scoring(option, template, user_weights)

        # 정규화 및 이상적/비이상적 해와의 거리 계산 (단순화)
        ideal_distance = abs(10.0 - score)
        anti_ideal_distance = abs(0.0 - score)

        if ideal_distance + anti_ideal_distance == 0:
            return 1.0

        return anti_ideal_distance / (ideal_distance + anti_ideal_distance)

    def _risk_adjusted_scoring(
        self,
        option: Dict[str, Any],
        template: Dict[str, Any],
        user_weights: Dict[str, float],
    ) -> float:
        """리스크 조정 점수 계산"""
        base_score = self._weighted_sum_scoring(option, template, user_weights)

        # 리스크 팩터 계산
        risk_factor = option.get("risk_level", 5) / 10.0  # 0-1 스케일

        # 리스크 조정 (높은 리스크는 점수 감소)
        risk_adjustment = 1.0 - (risk_factor * 0.3)

        return base_score * risk_adjustment

    def _assess_risks(
        self, option: Dict[str, Any], template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """리스크 평가"""
        risks = {}

        for risk_category in template.get("risk_categories", []):
            # 옵션의 특성을 기반으로 리스크 점수 계산
            risk_score = self._calculate_risk_score(option, risk_category)
            risks[risk_category] = {
                "score": risk_score,
                "level": self._get_risk_level(risk_score),
                "mitigation": self._get_risk_mitigation(risk_category, risk_score),
            }

        return risks

    def _calculate_risk_score(
        self, option: Dict[str, Any], risk_category: str
    ) -> float:
        """리스크 점수 계산"""
        # 간단한 휴리스틱 기반 리스크 계산
        base_risk = option.get("risk_level", 5) / 10.0

        # 카테고리별 조정
        category_multipliers = {
            "financial": 1.2,
            "market": 1.1,
            "operational": 0.9,
            "strategic": 1.0,
            "personal": 0.8,
            "external": 1.3,
        }

        multiplier = category_multipliers.get(risk_category, 1.0)
        return min(1.0, base_risk * multiplier)

    def _get_risk_level(self, score: float) -> str:
        """리스크 레벨 결정"""
        if score < 0.3:
            return "Low"
        elif score < 0.7:
            return "Medium"
        else:
            return "High"

    def _get_risk_mitigation(self, category: str, score: float) -> str:
        """리스크 완화 방안"""
        mitigations = {
            "financial": "비상 자금 확보, 보험 가입 검토",
            "market": "시장 동향 모니터링, 분산 전략",
            "operational": "프로세스 표준화, 백업 계획",
            "strategic": "단계적 실행, 성과 지표 설정",
            "personal": "스킬 업그레이드, 네트워킹",
            "external": "규제 변화 추적, 대안 준비",
        }

        base_mitigation = mitigations.get(category, "정기적 검토 및 모니터링")

        if score > 0.7:
            return f"⚠️ 고위험: {base_mitigation} + 전문가 상담"
        elif score > 0.4:
            return f"⚡ 중위험: {base_mitigation}"
        else:
            return f"✅ 저위험: {base_mitigation}"

    def _generate_alternatives(
        self, scores: List[Tuple], context: DecisionContext
    ) -> List[Dict[str, Any]]:
        """대안 시나리오 생성"""
        alternatives = []

        # 상위 3개 옵션 기반 시나리오
        for i, (name, score, option) in enumerate(scores[:3]):
            scenario = {
                "rank": i + 1,
                "option": name,
                "score": round(score, 3),
                "scenario": self._generate_scenario_description(option, context),
                "pros": self._extract_pros(option),
                "cons": self._extract_cons(option),
            }
            alternatives.append(scenario)

        return alternatives

    def _generate_scenario_description(
        self, option: Dict[str, Any], context: DecisionContext
    ) -> str:
        """시나리오 설명 생성"""
        return f"{option['name']}을(를) 선택할 경우, {context.timeline} 내에 예상되는 결과를 고려한 시나리오"

    def _extract_pros(self, option: Dict[str, Any]) -> List[str]:
        """장점 추출"""
        pros = []

        # 높은 점수 요소들을 장점으로 추출
        for key, value in option.items():
            if isinstance(value, (int, float)) and value > 7:
                pros.append(f"{key}: {value}/10 (우수)")

        if not pros:
            pros.append("전반적으로 균형잡힌 선택")

        return pros

    def _extract_cons(self, option: Dict[str, Any]) -> List[str]:
        """단점 추출"""
        cons = []

        # 낮은 점수 요소들을 단점으로 추출
        for key, value in option.items():
            if isinstance(value, (int, float)) and value < 4:
                cons.append(f"{key}: {value}/10 (개선 필요)")

        if not cons:
            cons.append("특별한 단점 없음")

        return cons

    def _generate_reasoning(
        self, scores: List[Tuple], template: Dict[str, Any], context: DecisionContext
    ) -> List[str]:
        """추론 단계 생성"""
        steps = []

        # 1. 분석 방법 설명
        steps.append(
            f"📊 {len(context.options)}개 옵션을 {len(template['factors'])}개 요소로 분석"
        )

        # 2. 주요 결정 요인
        top_factors = sorted(
            template["weights"].items(), key=lambda x: x[1], reverse=True
        )[:3]
        factor_names = [f[0] for f in top_factors]
        steps.append(f"🎯 주요 결정 요인: {', '.join(factor_names)}")

        # 3. 최고 점수 옵션
        best_option, best_score, _ = scores[0]
        steps.append(f"⭐ 최고 점수: {best_option} ({best_score:.2f}/10)")

        # 4. 점수 차이 분석
        if len(scores) > 1:
            second_score = scores[1][1]
            score_gap = best_score - second_score
            if score_gap < 0.5:
                steps.append("⚠️ 상위 옵션들 간 점수 차이가 작아 신중한 검토 필요")
            else:
                steps.append(f"✅ 명확한 우위 (차이: {score_gap:.2f}점)")

        # 5. 제약 사항 고려
        if context.constraints:
            steps.append(f"📋 제약 사항 {len(context.constraints)}개 항목 검토 완료")

        return steps

    def _calculate_confidence(self, scores: List[Tuple]) -> float:
        """신뢰도 계산"""
        if len(scores) < 2:
            return 0.5

        best_score = scores[0][1]
        second_score = scores[1][1]

        # 점수 차이가 클수록 신뢰도 높음
        score_gap = best_score - second_score

        # 0.8-1.0 범위로 정규화
        confidence = 0.8 + min(0.2, score_gap / 5.0)

        return round(confidence, 3)


class ProductivityTracker:
    """📈 생산성 추적기 (LLM-Free)"""

    def __init__(self, data_dir: str = "productivity_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.daily_file = self.data_dir / "daily_logs.json"
        self.goals_file = self.data_dir / "goals.json"

    def log_activity(
        self, activity: str, duration_minutes: int, category: str = "work"
    ) -> Dict[str, Any]:
        """활동 로깅"""
        timestamp = datetime.now()

        activity_log = {
            "timestamp": timestamp.isoformat(),
            "date": timestamp.date().isoformat(),
            "activity": activity,
            "duration_minutes": duration_minutes,
            "category": category,
            "productivity_score": self._calculate_productivity_score(
                activity, duration_minutes, category
            ),
        }

        # 일일 로그에 추가
        daily_logs = self._load_daily_logs()
        daily_logs.append(activity_log)
        self._save_daily_logs(daily_logs)

        return {
            "logged": True,
            "activity": activity,
            "duration": duration_minutes,
            "productivity_score": activity_log["productivity_score"],
            "daily_total": self._get_daily_total(timestamp.date()),
        }

    def _calculate_productivity_score(
        self, activity: str, duration: int, category: str
    ) -> float:
        """생산성 점수 계산"""
        # 카테고리별 기본 점수
        category_scores = {
            "deep_work": 1.0,
            "meetings": 0.7,
            "admin": 0.5,
            "learning": 0.9,
            "break": 0.3,
            "communication": 0.6,
        }

        base_score = category_scores.get(category, 0.5)

        # 지속 시간 보너스 (25-90분이 최적)
        if 25 <= duration <= 90:
            duration_multiplier = 1.2
        elif duration < 15:
            duration_multiplier = 0.7
        elif duration > 180:
            duration_multiplier = 0.8
        else:
            duration_multiplier = 1.0

        # 키워드 기반 조정
        activity_lower = activity.lower()
        if any(
            keyword in activity_lower
            for keyword in ["focus", "coding", "writing", "analysis"]
        ):
            keyword_bonus = 0.2
        elif any(
            keyword in activity_lower
            for keyword in ["interrupt", "distraction", "social media"]
        ):
            keyword_bonus = -0.3
        else:
            keyword_bonus = 0.0

        score = base_score * duration_multiplier + keyword_bonus
        return max(0.0, min(1.0, score))

    def get_daily_summary(self, date: str = None) -> Dict[str, Any]:
        """일일 요약"""
        if date is None:
            date = datetime.now().date().isoformat()

        daily_logs = self._load_daily_logs()
        day_logs = [log for log in daily_logs if log["date"] == date]

        if not day_logs:
            return {"date": date, "no_data": True}

        # 통계 계산
        total_time = sum(log["duration_minutes"] for log in day_logs)
        avg_productivity = sum(log["productivity_score"] for log in day_logs) / len(
            day_logs
        )

        # 카테고리별 분석
        category_stats = {}
        for log in day_logs:
            cat = log["category"]
            if cat not in category_stats:
                category_stats[cat] = {"count": 0, "time": 0, "avg_score": 0}
            category_stats[cat]["count"] += 1
            category_stats[cat]["time"] += log["duration_minutes"]
            category_stats[cat]["avg_score"] += log["productivity_score"]

        for cat_stat in category_stats.values():
            cat_stat["avg_score"] /= cat_stat["count"]

        return {
            "date": date,
            "total_activities": len(day_logs),
            "total_time_minutes": total_time,
            "average_productivity": round(avg_productivity, 3),
            "category_breakdown": category_stats,
            "recommendations": self._generate_productivity_recommendations(
                day_logs, avg_productivity
            ),
        }

    def _generate_productivity_recommendations(
        self, day_logs: List[Dict], avg_productivity: float
    ) -> List[str]:
        """생산성 개선 추천"""
        recommendations = []

        # 생산성 점수 기반 추천
        if avg_productivity < 0.5:
            recommendations.append("🔍 집중 시간을 늘리고 방해 요소를 최소화하세요")
        elif avg_productivity > 0.8:
            recommendations.append("🎉 높은 생산성! 현재 패턴을 유지하세요")

        # 활동 시간 분석
        total_time = sum(log["duration_minutes"] for log in day_logs)
        if total_time > 600:  # 10시간 이상
            recommendations.append("⚠️ 과도한 작업 시간. 적절한 휴식을 취하세요")
        elif total_time < 180:  # 3시간 미만
            recommendations.append("📈 더 많은 활동 로깅으로 패턴을 파악해보세요")

        # 활동 다양성
        categories = set(log["category"] for log in day_logs)
        if len(categories) < 2:
            recommendations.append("🎯 다양한 종류의 활동을 균형있게 배분해보세요")

        return recommendations[:3]  # 최대 3개 추천

    def _load_daily_logs(self) -> List[Dict[str, Any]]:
        """일일 로그 로드"""
        if self.daily_file.exists():
            with open(self.daily_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_daily_logs(self, logs: List[Dict[str, Any]]):
        """일일 로그 저장"""
        with open(self.daily_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def _get_daily_total(self, date) -> int:
        """해당 날짜 총 시간"""
        daily_logs = self._load_daily_logs()
        date_str = date.isoformat()
        return sum(
            log["duration_minutes"] for log in daily_logs if log["date"] == date_str
        )


class FinancialTracker:
    """💰 가계부 & 투자 추적기 (LLM-Free)"""

    def __init__(self, data_dir: str = "financial_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.transactions_file = self.data_dir / "transactions.json"
        self.budgets_file = self.data_dir / "budgets.json"

    def add_transaction(
        self,
        amount: float,
        category: str,
        description: str,
        transaction_type: str = "expense",
    ) -> Dict[str, Any]:
        """거래 추가"""
        timestamp = datetime.now()

        transaction = {
            "id": hashlib.md5(f"{timestamp}{amount}{description}".encode()).hexdigest()[
                :8
            ],
            "timestamp": timestamp.isoformat(),
            "date": timestamp.date().isoformat(),
            "amount": amount,
            "category": category,
            "description": description,
            "type": transaction_type,  # expense, income, investment
            "tags": self._extract_tags(description),
        }

        # 거래 내역에 추가
        transactions = self._load_transactions()
        transactions.append(transaction)
        self._save_transactions(transactions)

        # 분석 결과 반환
        return {
            "transaction_id": transaction["id"],
            "amount": amount,
            "category": category,
            "monthly_category_total": self._get_monthly_category_total(
                category, timestamp
            ),
            "daily_total": self._get_daily_total(timestamp.date()),
            "budget_status": self._check_budget_status(category, timestamp),
        }

    def _extract_tags(self, description: str) -> List[str]:
        """설명에서 태그 추출"""
        tags = []
        description_lower = description.lower()

        # 자동 태그 매핑
        tag_keywords = {
            "essential": [
                "food",
                "grocery",
                "rent",
                "utility",
                "음식",
                "마트",
                "월세",
                "공과금",
            ],
            "entertainment": ["movie", "game", "restaurant", "영화", "게임", "맛집"],
            "transport": [
                "taxi",
                "bus",
                "subway",
                "gas",
                "택시",
                "버스",
                "지하철",
                "기름",
            ],
            "shopping": [
                "shopping",
                "clothes",
                "electronics",
                "쇼핑",
                "옷",
                "전자제품",
            ],
            "health": ["hospital", "pharmacy", "gym", "병원", "약국", "헬스장"],
            "subscription": ["netflix", "spotify", "subscription", "넷플릭스", "구독"],
        }

        for tag, keywords in tag_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                tags.append(tag)

        return tags

    def get_monthly_summary(
        self, year: int = None, month: int = None
    ) -> Dict[str, Any]:
        """월간 요약"""
        if year is None or month is None:
            now = datetime.now()
            year, month = now.year, now.month

        transactions = self._load_transactions()

        # 해당 월 거래 필터링
        month_transactions = [
            t for t in transactions if t["date"].startswith(f"{year:04d}-{month:02d}")
        ]

        if not month_transactions:
            return {"year": year, "month": month, "no_data": True}

        # 수입/지출 분석
        income = sum(t["amount"] for t in month_transactions if t["type"] == "income")
        expenses = sum(
            t["amount"] for t in month_transactions if t["type"] == "expense"
        )
        investments = sum(
            t["amount"] for t in month_transactions if t["type"] == "investment"
        )

        # 카테고리별 분석
        category_breakdown = {}
        for transaction in month_transactions:
            cat = transaction["category"]
            if cat not in category_breakdown:
                category_breakdown[cat] = {"amount": 0, "count": 0, "percentage": 0}
            category_breakdown[cat]["amount"] += transaction["amount"]
            category_breakdown[cat]["count"] += 1

        # 백분율 계산
        total_expenses = max(expenses, 1)  # 0으로 나누기 방지
        for cat_data in category_breakdown.values():
            cat_data["percentage"] = round(
                (cat_data["amount"] / total_expenses) * 100, 1
            )

        # 트렌드 분석 (전월 대비)
        prev_month_data = self._get_previous_month_data(year, month)
        trend_analysis = self._calculate_trends(
            {"income": income, "expenses": expenses}, prev_month_data
        )

        return {
            "year": year,
            "month": month,
            "summary": {
                "total_income": income,
                "total_expenses": expenses,
                "total_investments": investments,
                "net_savings": income - expenses - investments,
                "savings_rate": round(
                    ((income - expenses - investments) / max(income, 1)) * 100, 1
                ),
            },
            "category_breakdown": category_breakdown,
            "trend_analysis": trend_analysis,
            "recommendations": self._generate_financial_recommendations(
                income, expenses, category_breakdown
            ),
        }

    def _get_previous_month_data(self, year: int, month: int) -> Dict[str, float]:
        """전월 데이터 가져오기"""
        prev_month = month - 1
        prev_year = year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1

        transactions = self._load_transactions()
        prev_transactions = [
            t
            for t in transactions
            if t["date"].startswith(f"{prev_year:04d}-{prev_month:02d}")
        ]

        income = sum(t["amount"] for t in prev_transactions if t["type"] == "income")
        expenses = sum(t["amount"] for t in prev_transactions if t["type"] == "expense")

        return {"income": income, "expenses": expenses}

    def _calculate_trends(
        self, current: Dict[str, float], previous: Dict[str, float]
    ) -> Dict[str, Any]:
        """트렌드 계산"""
        trends = {}

        for key in ["income", "expenses"]:
            current_val = current.get(key, 0)
            prev_val = previous.get(key, 0)

            if prev_val > 0:
                change_percent = round(((current_val - prev_val) / prev_val) * 100, 1)
                trends[key] = {
                    "change_percent": change_percent,
                    "change_amount": current_val - prev_val,
                    "trend": (
                        "증가"
                        if change_percent > 0
                        else "감소" if change_percent < 0 else "변화없음"
                    ),
                }
            else:
                trends[key] = {
                    "change_percent": 0,
                    "change_amount": 0,
                    "trend": "데이터없음",
                }

        return trends

    def _generate_financial_recommendations(
        self, income: float, expenses: float, categories: Dict
    ) -> List[str]:
        """재정 관리 추천"""
        recommendations = []

        # 저축률 분석
        savings_rate = ((income - expenses) / max(income, 1)) * 100 if income > 0 else 0

        if savings_rate < 10:
            recommendations.append("💰 저축률이 낮습니다. 불필요한 지출을 줄여보세요")
        elif savings_rate > 30:
            recommendations.append("🎉 훌륭한 저축률! 투자를 고려해보세요")

        # 카테고리별 분석
        if categories:
            max_category = max(categories.items(), key=lambda x: x[1]["amount"])
            if max_category[1]["percentage"] > 40:
                recommendations.append(
                    f"⚠️ {max_category[0]} 지출이 {max_category[1]['percentage']}%로 높습니다"
                )

        # 지출 대비 수입 분석
        if expenses > income:
            recommendations.append("🚨 지출이 수입을 초과했습니다. 긴급 점검 필요")

        return recommendations[:3]

    def _get_monthly_category_total(self, category: str, timestamp: datetime) -> float:
        """월간 카테고리 총액"""
        transactions = self._load_transactions()
        month_str = timestamp.strftime("%Y-%m")

        return sum(
            t["amount"]
            for t in transactions
            if t["category"] == category and t["date"].startswith(month_str)
        )

    def _get_daily_total(self, date) -> float:
        """일일 총액"""
        transactions = self._load_transactions()
        date_str = date.isoformat()

        return sum(
            t["amount"]
            for t in transactions
            if t["date"] == date_str and t["type"] == "expense"
        )

    def _check_budget_status(
        self, category: str, timestamp: datetime
    ) -> Dict[str, Any]:
        """예산 상태 확인"""
        # 간단한 예산 체크 (실제로는 budgets.json에서 로드)
        monthly_total = self._get_monthly_category_total(category, timestamp)

        # 기본 예산 (카테고리별)
        default_budgets = {
            "food": 500000,
            "transport": 200000,
            "entertainment": 300000,
            "shopping": 400000,
            "utility": 200000,
        }

        budget_limit = default_budgets.get(category, 1000000)
        usage_rate = (monthly_total / budget_limit) * 100

        if usage_rate > 90:
            status = "over_budget"
        elif usage_rate > 70:
            status = "warning"
        else:
            status = "safe"

        return {
            "budget_limit": budget_limit,
            "used_amount": monthly_total,
            "usage_rate": round(usage_rate, 1),
            "status": status,
            "remaining": budget_limit - monthly_total,
        }

    def _load_transactions(self) -> List[Dict[str, Any]]:
        """거래 내역 로드"""
        if self.transactions_file.exists():
            with open(self.transactions_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_transactions(self, transactions: List[Dict[str, Any]]):
        """거래 내역 저장"""
        with open(self.transactions_file, "w", encoding="utf-8") as f:
            json.dump(transactions, f, indent=2, ensure_ascii=False)


class HealthTracker:
    """🏃‍♂️ 건강 추적기 (LLM-Free)"""

    def __init__(self, data_dir: str = "health_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.records_file = self.data_dir / "health_records.json"

    def log_health_data(
        self, data_type: str, value: float, unit: str = "", notes: str = ""
    ) -> Dict[str, Any]:
        """건강 데이터 로깅"""
        timestamp = datetime.now()

        health_record = {
            "id": hashlib.md5(f"{timestamp}{data_type}{value}".encode()).hexdigest()[
                :8
            ],
            "timestamp": timestamp.isoformat(),
            "date": timestamp.date().isoformat(),
            "type": data_type,
            "value": value,
            "unit": unit,
            "notes": notes,
            "health_score": self._calculate_health_score(data_type, value),
        }

        # 건강 기록에 추가
        records = self._load_health_records()
        records.append(health_record)
        self._save_health_records(records)

        # 분석 결과 반환
        return {
            "record_id": health_record["id"],
            "type": data_type,
            "value": value,
            "health_score": health_record["health_score"],
            "trend": self._analyze_trend(data_type, records),
            "recommendations": self._get_health_recommendations(
                data_type, value, health_record["health_score"]
            ),
        }

    def _calculate_health_score(self, data_type: str, value: float) -> float:
        """건강 점수 계산 (0-1 스케일)"""
        # 데이터 타입별 최적 범위 정의
        optimal_ranges = {
            "weight": (50, 90),  # kg
            "blood_pressure_systolic": (90, 140),  # mmHg
            "blood_pressure_diastolic": (60, 90),  # mmHg
            "heart_rate": (60, 100),  # bpm
            "steps": (8000, 15000),  # daily steps
            "sleep_hours": (7, 9),  # hours
            "water_intake": (2000, 3000),  # ml
            "exercise_minutes": (30, 120),  # minutes
        }

        if data_type not in optimal_ranges:
            return 0.5  # 기본 점수

        min_val, max_val = optimal_ranges[data_type]

        if min_val <= value <= max_val:
            # 최적 범위 내: 0.8-1.0 점수
            return 0.8 + 0.2 * (
                1 - abs(value - (min_val + max_val) / 2) / ((max_val - min_val) / 2)
            )
        else:
            # 최적 범위 밖: 거리에 따라 점수 감소
            if value < min_val:
                distance = min_val - value
                penalty = distance / min_val
            else:
                distance = value - max_val
                penalty = distance / max_val

            return max(0.1, 0.8 - penalty)

    def _analyze_trend(self, data_type: str, records: List[Dict]) -> Dict[str, Any]:
        """트렌드 분석"""
        # 같은 타입의 최근 7일 데이터
        recent_records = [
            r
            for r in records
            if r["type"] == data_type
            and datetime.fromisoformat(r["timestamp"])
            > datetime.now() - timedelta(days=7)
        ]

        if len(recent_records) < 2:
            return {"trend": "insufficient_data", "change": 0}

        # 시간순 정렬
        recent_records.sort(key=lambda x: x["timestamp"])

        # 처음과 마지막 값 비교
        first_value = recent_records[0]["value"]
        last_value = recent_records[-1]["value"]

        change_percent = (
            ((last_value - first_value) / first_value) * 100 if first_value != 0 else 0
        )

        if abs(change_percent) < 2:
            trend = "stable"
        elif change_percent > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        return {
            "trend": trend,
            "change_percent": round(change_percent, 1),
            "data_points": len(recent_records),
            "period_days": 7,
        }

    def _get_health_recommendations(
        self, data_type: str, value: float, health_score: float
    ) -> List[str]:
        """건강 추천사항"""
        recommendations = []

        # 건강 점수 기반 일반 추천
        if health_score < 0.4:
            recommendations.append("⚠️ 주의 필요한 수치입니다. 전문의 상담을 권합니다")
        elif health_score > 0.8:
            recommendations.append("✅ 건강한 수치입니다. 현재 패턴을 유지하세요")

        # 데이터 타입별 구체적 추천
        type_recommendations = {
            "weight": {
                "low": "체중이 부족합니다. 균형잡힌 식단과 근력 운동을 권합니다",
                "high": "체중 관리가 필요합니다. 유산소 운동과 칼로리 조절을 권합니다",
            },
            "steps": {
                "low": "활동량이 부족합니다. 일일 걸음 수를 점진적으로 늘려보세요",
                "high": "훌륭한 활동량입니다! 부상 방지를 위해 적절한 휴식도 중요합니다",
            },
            "sleep_hours": {
                "low": "수면 시간이 부족합니다. 규칙적인 수면 패턴을 만들어보세요",
                "high": "충분한 수면을 취하고 있습니다. 수면의 질도 함께 고려해보세요",
            },
            "water_intake": {
                "low": "수분 섭취가 부족합니다. 하루 2L 이상 물을 마시세요",
                "high": "적절한 수분 섭취입니다. 과도한 섭취는 피하세요",
            },
        }

        if data_type in type_recommendations:
            if health_score < 0.5:
                recommendations.append(type_recommendations[data_type]["low"])
            elif health_score > 0.8:
                recommendations.append(type_recommendations[data_type]["high"])

        return recommendations[:2]  # 최대 2개 추천

    def get_health_dashboard(self, days: int = 30) -> Dict[str, Any]:
        """건강 대시보드"""
        records = self._load_health_records()

        # 최근 N일 데이터 필터링
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_records = [
            r for r in records if datetime.fromisoformat(r["timestamp"]) > cutoff_date
        ]

        if not recent_records:
            return {"no_data": True, "period_days": days}

        # 데이터 타입별 최신값과 평균
        type_summary = {}
        for record in recent_records:
            data_type = record["type"]
            if data_type not in type_summary:
                type_summary[data_type] = {
                    "values": [],
                    "health_scores": [],
                    "latest_value": None,
                    "latest_date": None,
                }

            type_summary[data_type]["values"].append(record["value"])
            type_summary[data_type]["health_scores"].append(record["health_score"])

            # 최신값 업데이트
            if (
                type_summary[data_type]["latest_date"] is None
                or record["timestamp"] > type_summary[data_type]["latest_date"]
            ):
                type_summary[data_type]["latest_value"] = record["value"]
                type_summary[data_type]["latest_date"] = record["timestamp"]

        # 통계 계산
        for data_type, summary in type_summary.items():
            summary["average"] = round(
                sum(summary["values"]) / len(summary["values"]), 2
            )
            summary["average_health_score"] = round(
                sum(summary["health_scores"]) / len(summary["health_scores"]), 3
            )
            summary["data_points"] = len(summary["values"])

        # 전체 건강 점수
        all_health_scores = [r["health_score"] for r in recent_records]
        overall_health_score = sum(all_health_scores) / len(all_health_scores)

        return {
            "period_days": days,
            "total_records": len(recent_records),
            "overall_health_score": round(overall_health_score, 3),
            "health_level": self._get_health_level(overall_health_score),
            "data_types": type_summary,
            "general_recommendations": self._get_general_health_recommendations(
                overall_health_score, type_summary
            ),
        }

    def _get_health_level(self, score: float) -> str:
        """건강 레벨 판정"""
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        else:
            return "Needs Attention"

    def _get_general_health_recommendations(
        self, overall_score: float, type_summary: Dict
    ) -> List[str]:
        """일반 건강 추천사항"""
        recommendations = []

        # 전체 점수 기반
        if overall_score < 0.5:
            recommendations.append(
                "🏥 전반적인 건강 관리가 필요합니다. 생활 습관 개선을 권합니다"
            )
        elif overall_score > 0.8:
            recommendations.append(
                "🌟 건강 상태가 우수합니다! 현재 생활 패턴을 유지하세요"
            )

        # 데이터 기록 빈도
        total_types = len(type_summary)
        if total_types < 3:
            recommendations.append("📊 더 다양한 건강 지표를 추적해보세요")

        # 가장 낮은 점수 영역 찾기
        if type_summary:
            lowest_type = min(
                type_summary.items(), key=lambda x: x[1]["average_health_score"]
            )
            if lowest_type[1]["average_health_score"] < 0.4:
                recommendations.append(
                    f"⚠️ {lowest_type[0]} 관리에 특별한 주의가 필요합니다"
                )

        return recommendations[:3]

    def _load_health_records(self) -> List[Dict[str, Any]]:
        """건강 기록 로드"""
        if self.records_file.exists():
            with open(self.records_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_health_records(self, records: List[Dict[str, Any]]):
        """건강 기록 저장"""
        with open(self.records_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)


# 통합 서비스 클래스
class EchoLLMFreeServices:
    """🚀 Echo LLM-Free Services Hub"""

    def __init__(self):
        self.decision_maker = PracticalDecisionMaker()
        self.productivity_tracker = ProductivityTracker()
        self.financial_tracker = FinancialTracker()
        self.health_tracker = HealthTracker()

        print("🚀 Echo LLM-Free Services 초기화 완료!")
        print("   📊 의사결정 도우미")
        print("   📈 생산성 추적기")
        print("   💰 가계부 & 투자 추적기")
        print("   🏃‍♂️ 건강 추적기")

    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 확인"""
        return {
            "services": [
                {
                    "name": "의사결정 도우미",
                    "status": "active",
                    "description": "다기준 의사결정 분석",
                },
                {
                    "name": "생산성 추적기",
                    "status": "active",
                    "description": "활동 로깅 및 생산성 분석",
                },
                {
                    "name": "가계부",
                    "status": "active",
                    "description": "지출 관리 및 예산 추적",
                },
                {
                    "name": "건강 추적기",
                    "status": "active",
                    "description": "건강 지표 모니터링",
                },
            ],
            "total_services": 4,
            "llm_dependency": False,
            "data_storage": "local_files",
            "initialized_at": datetime.now().isoformat(),
        }
