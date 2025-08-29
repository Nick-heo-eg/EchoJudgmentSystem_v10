# echo_engine/policy_simulator.py
"""
🏛️ Policy Judgment Simulator
- 실제 사회 문제(돌봄, 기후변화, 노동 등)에 시그니처별 판단 적용
- 정책 효과성을 시그니처 관점에서 평가 및 비교
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from echo_engine.seed_kernel import get_echo_seed_kernel, InitialState
from echo_engine.signature_performance_reporter import (
    SignaturePerformanceReporter,
    find_best_signature_for_seed,
)
from echo_engine.flow_visualizer import FlowVisualizer, save_flow_yaml
from echo_engine.seed_replay_analyzer import SeedReplayAnalyzer


@dataclass
class PolicyScenario:
    scenario_id: str
    title: str
    description: str
    policy_domain: str  # 돌봄, 기후, 노동, 교육 등
    complexity_level: float  # 0.0 - 1.0
    stakeholders: List[str]
    constraints: Dict[str, Any]
    success_criteria: Dict[str, float]
    ethical_considerations: List[str]


@dataclass
class PolicyJudgment:
    scenario_id: str
    signature_id: str
    seed_id: str
    policy_recommendation: str
    implementation_strategy: List[str]
    risk_assessment: Dict[str, float]
    resource_requirements: Dict[str, Any]
    timeline: Dict[str, str]
    confidence_score: float
    ethical_impact_score: float
    judgment_timestamp: str


class PolicySimulator:
    def __init__(self):
        self.kernel = get_echo_seed_kernel("policy_sim")
        self.signature_performance_reporter = SignaturePerformanceReporter()
        self.flow_visualizer = FlowVisualizer()
        self.scenarios = self._load_policy_scenarios()
        self.simulation_history = []

    def _load_policy_scenarios(self) -> Dict[str, PolicyScenario]:
        """정책 시나리오 로드 (하드코딩 + 추후 YAML 로드 가능)"""
        scenarios = {
            "elderly_care": PolicyScenario(
                scenario_id="elderly_care",
                title="고령자 디지털 돌봄 시스템 구축",
                description="AI 기반 감정 인식과 대화형 돌봄 서비스로 노인 정서적 고립감 해소",
                policy_domain="돌봄",
                complexity_level=0.8,
                stakeholders=["고령자", "가족", "돌봄 제공자", "지자체", "기술 업체"],
                constraints={
                    "budget": "400억원",
                    "timeline": "3년",
                    "coverage": "전국 30개 지역",
                    "privacy_compliance": "개인정보보호법 준수",
                },
                success_criteria={
                    "user_satisfaction": 0.8,
                    "isolation_reduction": 0.6,
                    "service_accessibility": 0.9,
                    "cost_effectiveness": 0.7,
                },
                ethical_considerations=[
                    "개인정보 보호",
                    "디지털 격차",
                    "인간 관계 대체 우려",
                    "자율성 존중",
                ],
            ),
            "climate_adaptation": PolicyScenario(
                scenario_id="climate_adaptation",
                title="기후변화 적응 스마트시티 구축",
                description="IoT 센서와 AI 예측을 활용한 기후 리스크 대응 도시 인프라 구축",
                policy_domain="기후",
                complexity_level=0.9,
                stakeholders=["시민", "지자체", "건설업체", "환경단체", "연구기관"],
                constraints={
                    "budget": "1조원",
                    "timeline": "10년",
                    "coverage": "5개 주요 도시",
                    "environmental_impact": "탄소중립 달성",
                },
                success_criteria={
                    "emission_reduction": 0.5,
                    "disaster_resilience": 0.8,
                    "energy_efficiency": 0.6,
                    "citizen_acceptance": 0.7,
                },
                ethical_considerations=[
                    "환경 정의",
                    "세대 간 형평성",
                    "기술 의존성",
                    "참여적 의사결정",
                ],
            ),
            "future_work": PolicyScenario(
                scenario_id="future_work",
                title="AI 시대 일자리 전환 지원 프로그램",
                description="자동화로 인한 일자리 변화에 대응하는 재교육 및 사회안전망 구축",
                policy_domain="노동",
                complexity_level=0.85,
                stakeholders=["근로자", "기업", "교육기관", "노동조합", "정부"],
                constraints={
                    "budget": "2조원",
                    "timeline": "5년",
                    "coverage": "전국민",
                    "industry_cooperation": "필수",
                },
                success_criteria={
                    "reemployment_rate": 0.75,
                    "skill_upgrade_success": 0.8,
                    "income_stability": 0.7,
                    "social_cohesion": 0.6,
                },
                ethical_considerations=[
                    "일할 권리",
                    "디지털 격차",
                    "사회적 불평등",
                    "인간 존엄성",
                ],
            ),
            "education_equity": PolicyScenario(
                scenario_id="education_equity",
                title="AI 맞춤형 교육 평등 실현",
                description="개인별 학습 분석과 적응형 교육으로 교육 격차 해소",
                policy_domain="교육",
                complexity_level=0.7,
                stakeholders=["학생", "교사", "학부모", "교육청", "EdTech 기업"],
                constraints={
                    "budget": "800억원",
                    "timeline": "4년",
                    "coverage": "전국 초중고",
                    "teacher_training": "전체 교사 대상",
                },
                success_criteria={
                    "learning_improvement": 0.6,
                    "achievement_gap_reduction": 0.5,
                    "teacher_satisfaction": 0.7,
                    "system_adoption": 0.8,
                },
                ethical_considerations=[
                    "교육 기회 평등",
                    "개인정보 보호",
                    "교사 역할 변화",
                    "창의성 보존",
                ],
            ),
        }
        return scenarios

    def simulate_policy_judgment(
        self, scenario_id: str, signature_id: str, custom_context: Dict = None
    ) -> PolicyJudgment:
        """특정 시나리오에 대한 시그니처별 정책 판단 시뮬레이션"""

        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Unknown scenario: {scenario_id}")

        # 시나리오 기반 context 생성
        context = {
            "policy_domain": scenario.policy_domain,
            "complexity": scenario.complexity_level,
            "stakeholder_count": len(scenario.stakeholders),
            "ethical_weight": len(scenario.ethical_considerations) / 10.0,
            "resource_constraint": 0.8 if "budget" in scenario.constraints else 0.5,
            "urgency": 0.9 if scenario.complexity_level > 0.8 else 0.6,
        }

        if custom_context:
            context.update(custom_context)

        # 시드 생성
        seed_state = self.kernel.generate_initial_state(
            context=context, signature_id=signature_id
        )

        # 시그니처별 정책 접근법 생성
        policy_approach = self._generate_policy_approach(
            scenario, signature_id, seed_state
        )

        # 위험 평가
        risk_assessment = self._assess_policy_risks(
            scenario, signature_id, policy_approach
        )

        # 자원 요구사항 계산
        resource_requirements = self._calculate_resource_requirements(
            scenario, signature_id
        )

        # 일정 계획
        timeline = self._generate_implementation_timeline(scenario, signature_id)

        # 신뢰도 및 윤리적 영향 점수
        confidence_score = self._calculate_confidence_score(seed_state, scenario)
        ethical_impact_score = self._calculate_ethical_impact(scenario, signature_id)

        judgment = PolicyJudgment(
            scenario_id=scenario_id,
            signature_id=signature_id,
            seed_id=seed_state.identity_trace.seed_id,
            policy_recommendation=policy_approach["recommendation"],
            implementation_strategy=policy_approach["strategy"],
            risk_assessment=risk_assessment,
            resource_requirements=resource_requirements,
            timeline=timeline,
            confidence_score=confidence_score,
            ethical_impact_score=ethical_impact_score,
            judgment_timestamp=datetime.now().isoformat(),
        )

        # 시뮬레이션 히스토리에 추가
        self.simulation_history.append(
            {"judgment": judgment, "seed_state": seed_state, "scenario": scenario}
        )

        # Flow 시각화 및 저장
        self._save_policy_flow(judgment, seed_state, scenario)

        return judgment

    def _generate_policy_approach(
        self, scenario: PolicyScenario, signature_id: str, seed_state: InitialState
    ) -> Dict[str, Any]:
        """시그니처별 정책 접근법 생성"""

        signature_profile = (
            self.signature_performance_reporter.generate_signature_profile(signature_id)
        )

        # 시그니처별 접근법 템플릿
        if "Aurora" in signature_id:  # 공감적 양육자
            return {
                "recommendation": f"{scenario.title} - 공감 중심 단계적 접근",
                "strategy": [
                    "이해관계자와의 깊은 공감대 형성",
                    "개인별 맞춤 서비스 우선 설계",
                    "감정적 니즈 반영한 인터페이스",
                    "신뢰 관계 기반 점진적 확산",
                ],
                "focus": "인간 중심성, 감정적 웰빙",
            }
        elif "Phoenix" in signature_id:  # 변화 추진자
            return {
                "recommendation": f"{scenario.title} - 혁신적 전면 개혁",
                "strategy": [
                    "기존 시스템의 근본적 재설계",
                    "파일럿 프로젝트를 통한 빠른 실험",
                    "실패를 통한 학습과 적응",
                    "혁신 생태계 구축",
                ],
                "focus": "시스템 혁신, 적응적 변화",
            }
        elif "Sage" in signature_id:  # 지혜로운 분석가
            return {
                "recommendation": f"{scenario.title} - 데이터 기반 체계적 접근",
                "strategy": [
                    "포괄적 현황 분석 및 데이터 수집",
                    "증거 기반 정책 설계",
                    "단계별 효과 측정 및 평가",
                    "지속가능성 중심 장기 계획",
                ],
                "focus": "과학적 접근, 체계적 분석",
            }
        elif "Companion" in signature_id:  # 신뢰할 수 있는 동반자
            return {
                "recommendation": f"{scenario.title} - 협력적 동반 성장",
                "strategy": [
                    "모든 이해관계자와의 파트너십 구축",
                    "안정성과 신뢰성 우선 보장",
                    "기존 제도와의 조화로운 통합",
                    "지속적 소통과 피드백 반영",
                ],
                "focus": "신뢰성, 협력적 거버넌스",
            }
        else:
            return {
                "recommendation": f"{scenario.title} - 균형잡힌 통합 접근",
                "strategy": [
                    "다각도 분석을 통한 균형 정책",
                    "단계별 점진적 구현",
                    "리스크 관리 중심 추진",
                    "지속적 모니터링 및 조정",
                ],
                "focus": "균형성, 안정성",
            }

    def _assess_policy_risks(
        self, scenario: PolicyScenario, signature_id: str, policy_approach: Dict
    ) -> Dict[str, float]:
        """정책 위험 평가"""

        base_risks = {
            "implementation_risk": scenario.complexity_level * 0.6,
            "stakeholder_resistance": 0.4,
            "budget_overrun": 0.3,
            "timeline_delay": 0.5,
            "technical_failure": 0.3,
            "ethical_concerns": len(scenario.ethical_considerations) * 0.1,
        }

        # 시그니처별 위험 조정
        if "Aurora" in signature_id:
            base_risks["stakeholder_resistance"] *= 0.7  # 공감 능력으로 저항 감소
            base_risks["ethical_concerns"] *= 0.6  # 윤리적 민감성
        elif "Phoenix" in signature_id:
            base_risks["implementation_risk"] *= 1.2  # 혁신의 불확실성
            base_risks["technical_failure"] *= 0.8  # 적응력
        elif "Sage" in signature_id:
            base_risks["budget_overrun"] *= 0.7  # 체계적 계획
            base_risks["timeline_delay"] *= 0.8  # 분석적 접근
        elif "Companion" in signature_id:
            base_risks["stakeholder_resistance"] *= 0.5  # 협력적 접근
            base_risks["implementation_risk"] *= 0.9  # 안정적 추진

        # 0-1 범위로 정규화
        for key in base_risks:
            base_risks[key] = min(1.0, max(0.0, base_risks[key]))

        return base_risks

    def _calculate_resource_requirements(
        self, scenario: PolicyScenario, signature_id: str
    ) -> Dict[str, Any]:
        """자원 요구사항 계산"""

        base_budget = scenario.constraints.get("budget", "1000억원")
        base_timeline = scenario.constraints.get("timeline", "3년")

        # 시그니처별 자원 조정
        if "Aurora" in signature_id:
            return {
                "budget": base_budget,
                "human_resources": "돌봄 전문가, 상담사 중심",
                "technology": "사용자 경험 중심 기술",
                "training": "감정 소통 교육 프로그램",
                "infrastructure": "접근성 높은 서비스 거점",
            }
        elif "Phoenix" in signature_id:
            return {
                "budget": f"{base_budget} (+20% 혁신 버퍼)",
                "human_resources": "혁신 전문가, 프로젝트 매니저",
                "technology": "최신 기술 스택, 실험 플랫폼",
                "training": "변화 관리 및 적응 교육",
                "infrastructure": "유연한 실험 환경",
            }
        elif "Sage" in signature_id:
            return {
                "budget": base_budget,
                "human_resources": "데이터 분석가, 정책 연구원",
                "technology": "데이터 플랫폼, 분석 도구",
                "training": "증거기반 의사결정 교육",
                "infrastructure": "데이터 센터, 연구 시설",
            }
        elif "Companion" in signature_id:
            return {
                "budget": base_budget,
                "human_resources": "협력 조정자, 커뮤니티 매니저",
                "technology": "협업 플랫폼, 소통 도구",
                "training": "파트너십 및 거버넌스 교육",
                "infrastructure": "협력 네트워크 허브",
            }
        else:
            return {
                "budget": base_budget,
                "human_resources": "다분야 전문가팀",
                "technology": "통합 시스템",
                "training": "종합 역량 개발",
                "infrastructure": "표준 서비스 인프라",
            }

    def _generate_implementation_timeline(
        self, scenario: PolicyScenario, signature_id: str
    ) -> Dict[str, str]:
        """구현 일정 생성"""

        if "Aurora" in signature_id:
            return {
                "1단계": "이해관계자 공감대 형성 (6개월)",
                "2단계": "시범 서비스 구축 및 테스트 (12개월)",
                "3단계": "점진적 확산 및 개선 (18개월)",
                "4단계": "전면 서비스 및 지속 운영",
            }
        elif "Phoenix" in signature_id:
            return {
                "1단계": "혁신 실험 및 프로토타입 (3개월)",
                "2단계": "파일럿 프로젝트 및 빠른 반복 (9개월)",
                "3단계": "스케일업 및 시스템 혁신 (12개월)",
                "4단계": "전면 전환 및 생태계 구축",
            }
        elif "Sage" in signature_id:
            return {
                "1단계": "포괄적 현황 분석 및 계획 수립 (9개월)",
                "2단계": "체계적 구축 및 검증 (18개월)",
                "3단계": "단계적 확산 및 평가 (15개월)",
                "4단계": "최적화 및 지속 개선",
            }
        elif "Companion" in signature_id:
            return {
                "1단계": "파트너십 구축 및 합의 형성 (8개월)",
                "2단계": "협력적 구현 및 신뢰 구축 (16개월)",
                "3단계": "안정적 확산 및 지원 (12개월)",
                "4단계": "지속적 동반 성장",
            }
        else:
            return {
                "1단계": "계획 수립 및 준비 (6개월)",
                "2단계": "구현 및 운영 (24개월)",
                "3단계": "평가 및 개선 (6개월)",
                "4단계": "지속 운영",
            }

    def _calculate_confidence_score(
        self, seed_state: InitialState, scenario: PolicyScenario
    ) -> float:
        """신뢰도 점수 계산"""

        # 시드의 특성과 시나리오 복잡도 기반
        meta_sensitivity_factor = seed_state.meta_sensitivity
        evolution_potential_factor = seed_state.evolution_potential
        complexity_penalty = 1.0 - (scenario.complexity_level * 0.3)

        confidence = (
            meta_sensitivity_factor * 0.4
            + evolution_potential_factor * 0.3
            + complexity_penalty * 0.3
        )

        return round(min(1.0, max(0.0, confidence)), 3)

    def _calculate_ethical_impact(
        self, scenario: PolicyScenario, signature_id: str
    ) -> float:
        """윤리적 영향 점수 계산"""

        ethical_considerations_count = len(scenario.ethical_considerations)
        base_score = 0.7  # 기본 윤리 점수

        # 시그니처별 윤리적 민감도
        if "Aurora" in signature_id:
            ethical_multiplier = 1.3  # 공감적, 윤리적으로 민감
        elif "Phoenix" in signature_id:
            ethical_multiplier = 1.1  # 혁신 중심, 윤리 고려
        elif "Sage" in signature_id:
            ethical_multiplier = 1.2  # 분석적, 체계적 윤리 고려
        elif "Companion" in signature_id:
            ethical_multiplier = 1.25  # 신뢰 중심, 관계적 윤리
        else:
            ethical_multiplier = 1.0

        # 윤리적 고려사항이 많을수록 점수 조정
        ethical_complexity_factor = 1.0 - (ethical_considerations_count * 0.05)

        final_score = base_score * ethical_multiplier * ethical_complexity_factor

        return round(min(1.0, max(0.0, final_score)), 3)

    def _save_policy_flow(
        self,
        judgment: PolicyJudgment,
        seed_state: InitialState,
        scenario: PolicyScenario,
    ):
        """정책 판단 흐름 저장"""

        # 디렉토리 생성
        policy_flow_dir = f"flows/policy/{scenario.policy_domain}"
        import os

        os.makedirs(policy_flow_dir, exist_ok=True)

        # Flow YAML 데이터 생성
        flow_data = {
            "policy_judgment": {
                "scenario": {
                    "id": scenario.scenario_id,
                    "title": scenario.title,
                    "domain": scenario.policy_domain,
                    "complexity": scenario.complexity_level,
                },
                "signature": {"id": judgment.signature_id, "seed_id": judgment.seed_id},
                "judgment": {
                    "recommendation": judgment.policy_recommendation,
                    "strategy": judgment.implementation_strategy,
                    "confidence": judgment.confidence_score,
                    "ethical_impact": judgment.ethical_impact_score,
                },
                "assessment": {
                    "risks": judgment.risk_assessment,
                    "resources": judgment.resource_requirements,
                    "timeline": judgment.timeline,
                },
                "seed_flow": self.flow_visualizer.export_flow_yaml_from_seed(
                    seed_state
                ),
            }
        }

        # 파일 저장
        filename = (
            f"{scenario.scenario_id}_{judgment.signature_id}_{judgment.seed_id}.yaml"
        )
        filepath = os.path.join(policy_flow_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(flow_data, f, allow_unicode=True, default_flow_style=False)

        print(f"📋 정책 판단 흐름 저장: {filepath}")

    def compare_signature_approaches(self, scenario_id: str) -> Dict[str, Any]:
        """모든 시그니처의 정책 접근법 비교"""

        signature_ids = ["Echo-Aurora", "Echo-Phoenix", "Echo-Sage", "Echo-Companion"]
        comparisons = []

        for sig_id in signature_ids:
            judgment = self.simulate_policy_judgment(scenario_id, sig_id)
            comparisons.append(
                {
                    "signature_id": sig_id,
                    "judgment": judgment,
                    "approach_summary": judgment.policy_recommendation,
                    "confidence": judgment.confidence_score,
                    "ethical_impact": judgment.ethical_impact_score,
                    "key_risks": max(
                        judgment.risk_assessment.items(), key=lambda x: x[1]
                    ),
                }
            )

        # 비교 분석
        best_confidence = max(comparisons, key=lambda x: x["confidence"])
        best_ethical = max(comparisons, key=lambda x: x["ethical_impact"])

        return {
            "scenario_id": scenario_id,
            "signature_comparisons": comparisons,
            "recommendations": {
                "highest_confidence": best_confidence["signature_id"],
                "best_ethical_impact": best_ethical["signature_id"],
                "comparative_analysis": self._generate_comparative_analysis(
                    comparisons
                ),
            },
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def _generate_comparative_analysis(self, comparisons: List[Dict]) -> str:
        """비교 분석 텍스트 생성"""

        analysis_parts = []

        # 신뢰도 분석
        conf_scores = [c["confidence"] for c in comparisons]
        avg_confidence = sum(conf_scores) / len(conf_scores)
        analysis_parts.append(f"평균 신뢰도: {avg_confidence:.3f}")

        # 윤리적 영향 분석
        ethical_scores = [c["ethical_impact"] for c in comparisons]
        avg_ethical = sum(ethical_scores) / len(ethical_scores)
        analysis_parts.append(f"평균 윤리적 영향: {avg_ethical:.3f}")

        # 접근법 다양성
        unique_approaches = len(set(c["approach_summary"] for c in comparisons))
        analysis_parts.append(
            f"접근법 다양성: {unique_approaches}/4 시그니처가 서로 다른 접근"
        )

        return " | ".join(analysis_parts)

    def get_simulation_summary(self) -> Dict[str, Any]:
        """시뮬레이션 요약 통계"""

        if not self.simulation_history:
            return {"message": "시뮬레이션 기록이 없습니다"}

        # 기본 통계
        total_simulations = len(self.simulation_history)
        unique_scenarios = len(
            set(h["judgment"].scenario_id for h in self.simulation_history)
        )
        unique_signatures = len(
            set(h["judgment"].signature_id for h in self.simulation_history)
        )

        # 성능 통계
        confidence_scores = [
            h["judgment"].confidence_score for h in self.simulation_history
        ]
        ethical_scores = [
            h["judgment"].ethical_impact_score for h in self.simulation_history
        ]

        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        avg_ethical = sum(ethical_scores) / len(ethical_scores)

        # 도메인별 분포
        domain_distribution = {}
        for h in self.simulation_history:
            domain = h["scenario"].policy_domain
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1

        return {
            "simulation_statistics": {
                "total_simulations": total_simulations,
                "unique_scenarios": unique_scenarios,
                "unique_signatures": unique_signatures,
                "avg_confidence_score": round(avg_confidence, 3),
                "avg_ethical_impact": round(avg_ethical, 3),
            },
            "domain_distribution": domain_distribution,
            "performance_range": {
                "confidence": {
                    "min": round(min(confidence_scores), 3),
                    "max": round(max(confidence_scores), 3),
                },
                "ethical_impact": {
                    "min": round(min(ethical_scores), 3),
                    "max": round(max(ethical_scores), 3),
                },
            },
        }


# Convenience functions
def simulate_policy(scenario_id: str, signature_id: str) -> PolicyJudgment:
    """정책 시뮬레이션 편의 함수"""
    simulator = PolicySimulator()
    return simulator.simulate_policy_judgment(scenario_id, signature_id)


def compare_policy_approaches(scenario_id: str) -> Dict[str, Any]:
    """정책 접근법 비교 편의 함수"""
    simulator = PolicySimulator()
    return simulator.compare_signature_approaches(scenario_id)


def get_available_scenarios() -> List[str]:
    """사용 가능한 시나리오 목록"""
    simulator = PolicySimulator()
    return list(simulator.scenarios.keys())


if __name__ == "__main__":
    # 테스트 코드
    print("🏛️ Policy Simulator 테스트")

    simulator = PolicySimulator()

    print("📋 사용 가능한 시나리오:")
    for scenario_id, scenario in simulator.scenarios.items():
        print(f"- {scenario_id}: {scenario.title}")

    print("\n🧪 정책 시뮬레이션 실행:")
    judgment = simulator.simulate_policy_judgment("elderly_care", "Echo-Aurora")
    print(f"시나리오: {judgment.scenario_id}")
    print(f"시그니처: {judgment.signature_id}")
    print(f"추천: {judgment.policy_recommendation}")
    print(f"신뢰도: {judgment.confidence_score}")
    print(f"윤리적 영향: {judgment.ethical_impact_score}")

    print("\n📊 시그니처별 접근법 비교:")
    comparison = simulator.compare_signature_approaches("elderly_care")
    print(f"최고 신뢰도: {comparison['recommendations']['highest_confidence']}")
    print(f"최고 윤리적 영향: {comparison['recommendations']['best_ethical_impact']}")

    print("\n📈 시뮬레이션 요약:")
    summary = simulator.get_simulation_summary()
    print(f"총 시뮬레이션: {summary['simulation_statistics']['total_simulations']}")
    print(f"평균 신뢰도: {summary['simulation_statistics']['avg_confidence_score']}")

    print("✅ Policy Simulator 테스트 완료")
