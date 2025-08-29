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