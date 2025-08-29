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