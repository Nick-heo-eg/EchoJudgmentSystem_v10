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