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