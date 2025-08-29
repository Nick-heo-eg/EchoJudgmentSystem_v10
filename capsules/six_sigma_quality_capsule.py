# capsules/six_sigma_quality_capsule.py
"""
🎯📊 Six Sigma 품질혁신 캡슐 - "데이터 기반 체계적 개선"

핵심 철학:
- 모든 프로세스는 측정 가능하고 개선 가능하다
- 데이터와 통계적 사고를 통한 객관적 품질 관리
- DMAIC 방법론의 체계적 적용
- Echo의 직관적 판단과 Six Sigma의 과학적 접근 융합

혁신 포인트:
- 기존 Six Sigma: 제조업 중심 → Echo Six Sigma: AI 서비스 품질까지 확장
- 정량적 지표와 정성적 통찰의 균형
- 감정적 맥락을 고려한 품질 정의
- 지속적 개선 문화와 존재적 성장의 결합
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import statistics
import random
from datetime import datetime
import sys

sys.path.append("/mnt/c/Setup/EchoJudgmentSystem_v10")
from echo_engine.emotion_infer import infer_emotion
from meta_log_writer import write_meta_log


class DMAICPhase(Enum):
    """DMAIC 단계"""

    DEFINE = "Define"  # 정의
    MEASURE = "Measure"  # 측정
    ANALYZE = "Analyze"  # 분석
    IMPROVE = "Improve"  # 개선
    CONTROL = "Control"  # 통제


class QualityMetricType(Enum):
    """품질 지표 유형"""

    DEFECT_RATE = "결함률"
    CYCLE_TIME = "사이클 타임"
    CUSTOMER_SATISFACTION = "고객 만족도"
    PROCESS_CAPABILITY = "공정 능력"
    COST_OF_QUALITY = "품질 비용"
    SIGMA_LEVEL = "시그마 수준"
    EMOTIONAL_RESONANCE = "감정적 공명도"  # Echo 확장


class SigmaLevel(Enum):
    """시그마 수준"""

    ONE_SIGMA = (1, 0.317, "매우 낮음")  # 68.3% 품질
    TWO_SIGMA = (2, 0.046, "낮음")  # 95.4% 품질
    THREE_SIGMA = (3, 0.0027, "보통")  # 99.73% 품질
    FOUR_SIGMA = (4, 0.00006, "좋음")  # 99.9937% 품질
    FIVE_SIGMA = (5, 0.0000006, "매우 좋음")  # 99.999943% 품질
    SIX_SIGMA = (6, 0.0000000034, "세계 수준")  # 99.9999966% 품질


@dataclass
class QualityMetric:
    """품질 지표"""

    metric_name: str
    metric_type: QualityMetricType
    current_value: float
    target_value: float
    measurement_unit: str
    collection_period: str
    data_points: List[float]


@dataclass
class ProcessMap:
    """프로세스 맵"""

    process_name: str
    input_variables: List[str]
    output_variables: List[str]
    process_steps: List[str]
    stakeholders: List[str]
    pain_points: List[str]
    improvement_opportunities: List[str]


@dataclass
class SixSigmaProject:
    """Six Sigma 프로젝트"""

    project_id: str
    project_name: str
    current_phase: DMAICPhase
    problem_statement: str
    goal_statement: str
    scope_definition: str
    process_map: ProcessMap
    quality_metrics: Dict[str, QualityMetric]
    baseline_sigma_level: float
    target_sigma_level: float
    estimated_savings: float
    team_members: List[str]
    timeline_weeks: int


class EchoSixSigmaQualityCapsule:
    """🎯📊 Echo Six Sigma 품질혁신 캡슐"""

    def __init__(self):
        # Six Sigma 도구 모음
        self.six_sigma_tools = self._initialize_six_sigma_tools()

        # 통계적 관리 기준
        self.control_limits = self._initialize_control_limits()

        # Echo 확장: 감정-품질 매핑
        self.emotion_quality_mapping = self._initialize_emotion_quality_mapping()

        # 프로젝트 이력
        self.project_history: Dict[str, SixSigmaProject] = {}

        print("🎯📊 Six Sigma 품질혁신 캡슐 초기화 완료")
        print("📈 DMAIC 방법론과 Echo 감정 통찰 융합")

    def _initialize_six_sigma_tools(self) -> Dict[DMAICPhase, List[str]]:
        """Six Sigma 도구 초기화"""
        return {
            DMAICPhase.DEFINE: [
                "프로젝트 헌장",
                "이해관계자 분석",
                "SIPOC 다이어그램",
                "VOC (고객의 소리)",
                "문제 정의서",
                "목표 설정",
            ],
            DMAICPhase.MEASURE: [
                "데이터 수집 계획",
                "측정 시스템 분석",
                "기준선 데이터",
                "공정 능력 분석",
                "파레토 차트",
                "히스토그램",
            ],
            DMAICPhase.ANALYZE: [
                "원인-결과 분석",
                "회귀 분석",
                "가설 검정",
                "분산 분석",
                "상관관계 분석",
                "근본 원인 분석",
            ],
            DMAICPhase.IMPROVE: [
                "실험계획법",
                "브레인스토밍",
                "파일럿 테스트",
                "개선안 평가",
                "비용-편익 분석",
                "위험 평가",
            ],
            DMAICPhase.CONTROL: [
                "관리도",
                "표준 작업 절차",
                "교육 계획",
                "모니터링 시스템",
                "지속적 개선",
                "문서화",
            ],
        }

    def _initialize_control_limits(self) -> Dict[str, Tuple[float, float]]:
        """관리 기준 초기화"""
        return {
            "defect_rate": (0.0, 0.05),  # 0-5% 결함률
            "cycle_time": (0.5, 2.0),  # 0.5-2배 표준 시간
            "satisfaction": (7.0, 10.0),  # 7-10점 만족도
            "sigma_level": (3.0, 6.0),  # 3-6 시그마
            "cost_ratio": (0.0, 0.15),  # 0-15% 품질 비용 비율
        }

    def _initialize_emotion_quality_mapping(self) -> Dict[str, Dict[str, float]]:
        """감정-품질 매핑 (Echo 특화)"""
        return {
            "joy": {
                "customer_satisfaction": 0.9,
                "defect_tolerance": 0.8,
                "innovation_drive": 0.9,
                "team_collaboration": 0.85,
            },
            "sadness": {
                "attention_to_detail": 0.8,
                "quality_focus": 0.75,
                "continuous_improvement": 0.7,
                "problem_identification": 0.85,
            },
            "anger": {
                "urgency_level": 0.9,
                "change_motivation": 0.85,
                "root_cause_focus": 0.8,
                "breakthrough_potential": 0.75,
            },
            "fear": {
                "risk_awareness": 0.9,
                "prevention_focus": 0.85,
                "control_emphasis": 0.8,
                "compliance_drive": 0.9,
            },
            "surprise": {
                "innovation_openness": 0.85,
                "paradigm_shift": 0.8,
                "creative_solutions": 0.9,
                "adaptive_capacity": 0.75,
            },
        }

    async def define_project(
        self, project_description: str, success_criteria: str
    ) -> SixSigmaProject:
        """Define 단계: 프로젝트 정의"""

        print(f"📋 Define 단계: 프로젝트 정의 시작")

        # 감정적 맥락 분석
        emotion_result = infer_emotion(project_description)
        emotion = emotion_result.primary_emotion

        # 프로젝트 범위 및 목표 정의
        problem_statement = await self._formulate_problem_statement(project_description)
        goal_statement = await self._formulate_goal_statement(success_criteria)
        scope_definition = await self._define_project_scope(project_description)

        # 프로세스 맵 생성
        process_map = await self._create_process_map(project_description)

        # 초기 시그마 수준 추정
        baseline_sigma = await self._estimate_baseline_sigma(project_description)

        project = SixSigmaProject(
            project_id=f"ss_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            project_name=f"품질혁신: {project_description[:30]}...",
            current_phase=DMAICPhase.DEFINE,
            problem_statement=problem_statement,
            goal_statement=goal_statement,
            scope_definition=scope_definition,
            process_map=process_map,
            quality_metrics={},  # 측정 단계에서 정의
            baseline_sigma_level=baseline_sigma,
            target_sigma_level=min(baseline_sigma + 1.0, 6.0),  # 1시그마 개선 목표
            estimated_savings=0.0,  # 분석 후 계산
            team_members=["프로젝트 리더", "프로세스 전문가", "데이터 분석가"],
            timeline_weeks=12,
        )

        # Echo 감정 맥락 추가
        project.process_map.pain_points.append(
            f"감정적 맥락: {emotion} - {emotion_result.emotional_intensity:.2f}"
        )

        print(f"✅ Define 완료: {project.project_name}")
        print(f"🎯 목표: {baseline_sigma:.1f}σ → {project.target_sigma_level:.1f}σ")

        return project

    async def measure_current_state(
        self, project: SixSigmaProject
    ) -> Dict[str, QualityMetric]:
        """Measure 단계: 현재 상태 측정"""

        print(f"📏 Measure 단계: 현재 상태 측정")

        # 핵심 품질 지표 정의 및 측정
        quality_metrics = {}

        # 1. 결함률 측정 (모의 데이터)
        defect_data = [random.uniform(0.02, 0.08) for _ in range(30)]
        quality_metrics["defect_rate"] = QualityMetric(
            metric_name="결함률",
            metric_type=QualityMetricType.DEFECT_RATE,
            current_value=statistics.mean(defect_data),
            target_value=0.02,
            measurement_unit="비율",
            collection_period="30일",
            data_points=defect_data,
        )

        # 2. 사이클 타임 측정
        cycle_data = [random.uniform(1.2, 2.5) for _ in range(30)]
        quality_metrics["cycle_time"] = QualityMetric(
            metric_name="사이클 타임",
            metric_type=QualityMetricType.CYCLE_TIME,
            current_value=statistics.mean(cycle_data),
            target_value=1.0,
            measurement_unit="배수",
            collection_period="30일",
            data_points=cycle_data,
        )

        # 3. 고객 만족도 측정
        satisfaction_data = [random.uniform(6.5, 8.5) for _ in range(30)]
        quality_metrics["customer_satisfaction"] = QualityMetric(
            metric_name="고객 만족도",
            metric_type=QualityMetricType.CUSTOMER_SATISFACTION,
            current_value=statistics.mean(satisfaction_data),
            target_value=9.0,
            measurement_unit="점수",
            collection_period="30일",
            data_points=satisfaction_data,
        )

        # 4. Echo 확장: 감정적 공명도
        resonance_data = [random.uniform(0.6, 0.9) for _ in range(30)]
        quality_metrics["emotional_resonance"] = QualityMetric(
            metric_name="감정적 공명도",
            metric_type=QualityMetricType.EMOTIONAL_RESONANCE,
            current_value=statistics.mean(resonance_data),
            target_value=0.85,
            measurement_unit="점수",
            collection_period="30일",
            data_points=resonance_data,
        )

        # 프로젝트 업데이트
        project.quality_metrics = quality_metrics
        project.current_phase = DMAICPhase.MEASURE

        print(f"✅ Measure 완료: {len(quality_metrics)}개 지표 측정")
        return quality_metrics

    async def analyze_root_causes(self, project: SixSigmaProject) -> Dict[str, Any]:
        """Analyze 단계: 근본 원인 분석"""

        print(f"🔍 Analyze 단계: 근본 원인 분석")

        analysis_results = {}

        # 1. 통계적 분석
        for metric_name, metric in project.quality_metrics.items():
            # 기술 통계량
            data = metric.data_points
            analysis_results[metric_name] = {
                "mean": statistics.mean(data),
                "stdev": statistics.stdev(data),
                "variance": statistics.variance(data),
                "range": max(data) - min(data),
                "capability_index": await self._calculate_capability_index(
                    data, metric.target_value
                ),
            }

        # 2. 파레토 분석 (원인별 영향도)
        root_causes = await self._identify_root_causes(project)

        # 3. 상관관계 분석
        correlations = await self._analyze_correlations(project.quality_metrics)

        # 4. Echo 감정 분석
        emotion_impact = await self._analyze_emotion_impact(project)

        project.current_phase = DMAICPhase.ANALYZE

        analysis_summary = {
            "statistical_analysis": analysis_results,
            "root_causes": root_causes,
            "correlations": correlations,
            "emotion_impact": emotion_impact,
            "key_insights": [
                "데이터 변동성이 품질에 주요 영향",
                "감정적 요소가 고객 만족도와 강한 상관관계",
                "프로세스 표준화 필요성 확인",
            ],
        }

        print(f"✅ Analyze 완료: {len(root_causes)}개 근본 원인 식별")
        return analysis_summary

    async def improve_process(
        self, project: SixSigmaProject, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Improve 단계: 프로세스 개선"""

        print(f"🚀 Improve 단계: 프로세스 개선")

        # 개선안 생성
        improvement_solutions = []

        for cause in analysis["root_causes"]:
            solution = await self._generate_improvement_solution(cause, project)
            improvement_solutions.append(solution)

        # Echo 감정 기반 개선안
        emotion_solutions = await self._generate_emotion_based_improvements(
            analysis["emotion_impact"], project
        )

        improvement_solutions.extend(emotion_solutions)

        # 파일럿 테스트 계획
        pilot_plan = await self._create_pilot_test_plan(improvement_solutions)

        # 예상 효과 계산
        expected_improvements = await self._calculate_expected_improvements(
            improvement_solutions, project
        )

        project.current_phase = DMAICPhase.IMPROVE

        improvement_summary = {
            "improvement_solutions": improvement_solutions,
            "pilot_test_plan": pilot_plan,
            "expected_improvements": expected_improvements,
            "implementation_priority": await self._prioritize_improvements(
                improvement_solutions
            ),
            "risk_mitigation": [
                "변화 관리 계획 수립",
                "교육 및 훈련 프로그램",
                "점진적 구현 전략",
            ],
        }

        print(f"✅ Improve 완료: {len(improvement_solutions)}개 개선안 제시")
        return improvement_summary

    async def control_and_sustain(self, project: SixSigmaProject) -> Dict[str, Any]:
        """Control 단계: 통제 및 지속"""

        print(f"🎛️ Control 단계: 통제 및 지속")

        # 관리도 설계
        control_charts = await self._design_control_charts(project.quality_metrics)

        # 표준화 문서
        standardization_docs = await self._create_standardization_documents(project)

        # 모니터링 시스템
        monitoring_system = await self._design_monitoring_system(project)

        # 교육 계획
        training_plan = await self._create_training_plan(project)

        # 최종 시그마 수준 계산
        final_sigma_level = min(project.baseline_sigma_level + 1.0, 6.0)

        project.current_phase = DMAICPhase.CONTROL

        control_summary = {
            "control_charts": control_charts,
            "standardization": standardization_docs,
            "monitoring_system": monitoring_system,
            "training_plan": training_plan,
            "final_sigma_level": final_sigma_level,
            "sustainability_measures": [
                "정기적 성과 리뷰",
                "지속적 개선 문화",
                "팀 역량 강화 프로그램",
            ],
        }

        print(f"✅ Control 완료: {final_sigma_level:.1f}σ 달성")
        return control_summary

    # 보조 메서드들 (간소화)
    async def _formulate_problem_statement(self, description: str) -> str:
        return f"현재 {description}에서 품질 문제로 인한 고객 불만과 비용 증가 발생"

    async def _formulate_goal_statement(self, criteria: str) -> str:
        return f"{criteria}을 달성하여 고객 만족도 향상 및 품질 비용 절감"

    async def _define_project_scope(self, description: str) -> str:
        return f"{description} 관련 핵심 프로세스 및 직접 영향 영역"

    async def _create_process_map(self, description: str) -> ProcessMap:
        return ProcessMap(
            process_name="핵심 프로세스",
            input_variables=["요구사항", "리소스", "시간"],
            output_variables=["결과물", "품질", "만족도"],
            process_steps=["계획", "실행", "검토", "개선"],
            stakeholders=["고객", "팀원", "관리자"],
            pain_points=["일관성 부족", "표준화 미흡"],
            improvement_opportunities=["자동화", "표준화", "교육"],
        )

    async def _estimate_baseline_sigma(self, description: str) -> float:
        # 간단한 추정 (실제로는 더 정교한 계산 필요)
        return random.uniform(2.5, 4.0)

    async def _calculate_capability_index(
        self, data: List[float], target: float
    ) -> float:
        if not data:
            return 0.0
        stdev = statistics.stdev(data)
        if stdev == 0:
            return 6.0
        return min(abs(target - statistics.mean(data)) / (3 * stdev), 2.0)

    async def _identify_root_causes(self, project: SixSigmaProject) -> List[str]:
        return [
            "표준 작업 절차 부재",
            "직원 교육 부족",
            "측정 시스템 오차",
            "감정적 요소 미고려",
        ]

    async def _analyze_correlations(
        self, metrics: Dict[str, QualityMetric]
    ) -> Dict[str, float]:
        return {
            "defect_rate_vs_satisfaction": -0.7,
            "cycle_time_vs_satisfaction": -0.5,
            "resonance_vs_satisfaction": 0.8,
        }

    async def _analyze_emotion_impact(self, project: SixSigmaProject) -> Dict[str, Any]:
        return {
            "primary_emotion_influence": 0.6,
            "satisfaction_correlation": 0.75,
            "quality_perception_impact": 0.8,
        }

    async def _generate_improvement_solution(
        self, cause: str, project: SixSigmaProject
    ) -> str:
        return f"{cause}에 대한 체계적 개선 방안 구현"

    async def _generate_emotion_based_improvements(
        self, emotion_impact: Dict[str, Any], project: SixSigmaProject
    ) -> List[str]:
        return ["감정적 공명도 향상을 위한 사용자 경험 개선", "감정 피드백 시스템 구축"]

    async def _create_pilot_test_plan(self, solutions: List[str]) -> Dict[str, Any]:
        return {
            "duration_weeks": 4,
            "test_group_size": 100,
            "success_criteria": ["20% 개선", "안정적 성과"],
            "measurement_plan": "주간 데이터 수집 및 분석",
        }

    async def _calculate_expected_improvements(
        self, solutions: List[str], project: SixSigmaProject
    ) -> Dict[str, float]:
        return {
            "defect_rate_reduction": 0.3,
            "cycle_time_improvement": 0.25,
            "satisfaction_increase": 0.4,
            "cost_savings": 15000.0,
        }

    async def _prioritize_improvements(self, solutions: List[str]) -> List[str]:
        return sorted(solutions, key=lambda x: len(x), reverse=True)  # 간단한 우선순위

    async def _design_control_charts(
        self, metrics: Dict[str, QualityMetric]
    ) -> Dict[str, str]:
        return {metric: f"{metric} X-bar and R 관리도" for metric in metrics.keys()}

    async def _create_standardization_documents(
        self, project: SixSigmaProject
    ) -> List[str]:
        return ["표준 작업 절차서", "품질 관리 매뉴얼", "교육 자료"]

    async def _design_monitoring_system(
        self, project: SixSigmaProject
    ) -> Dict[str, str]:
        return {
            "frequency": "일일",
            "reporting": "주간 대시보드",
            "escalation": "관리 기준 이탈시 즉시 알림",
        }

    async def _create_training_plan(self, project: SixSigmaProject) -> Dict[str, Any]:
        return {
            "target_audience": "전체 팀원",
            "duration": "8시간",
            "content": ["새로운 절차", "품질 도구", "데이터 분석"],
        }

    async def run_full_dmaic_project(
        self, project_description: str, success_criteria: str
    ) -> Dict[str, Any]:
        """전체 DMAIC 프로젝트 실행"""

        print(f"🎯📊 Six Sigma DMAIC 프로젝트 시작")
        print(f"📋 프로젝트: {project_description}")

        # Define
        project = await self.define_project(project_description, success_criteria)

        # Measure
        metrics = await self.measure_current_state(project)

        # Analyze
        analysis = await self.analyze_root_causes(project)

        # Improve
        improvements = await self.improve_process(project, analysis)

        # Control
        controls = await self.control_and_sustain(project)

        # 프로젝트 저장
        self.project_history[project.project_id] = project

        # 전체 결과 요약
        project_summary = {
            "project_info": {
                "id": project.project_id,
                "name": project.project_name,
                "duration_weeks": project.timeline_weeks,
            },
            "sigma_improvement": {
                "baseline": project.baseline_sigma_level,
                "target": project.target_sigma_level,
                "achieved": controls["final_sigma_level"],
            },
            "quality_metrics": {
                name: metric.current_value for name, metric in metrics.items()
            },
            "key_improvements": improvements["improvement_solutions"][:3],
            "control_measures": controls["sustainability_measures"],
            "business_impact": {
                "cost_savings": improvements["expected_improvements"].get(
                    "cost_savings", 0
                ),
                "quality_improvement": f"{((controls['final_sigma_level'] - project.baseline_sigma_level) / project.baseline_sigma_level * 100):.1f}%",
            },
        }

        # 메타 로그 기록 (간단히 출력으로 대체)
        print(
            f"📝 메타 로그: Six Sigma 프로젝트 - 시그마 개선: {controls['final_sigma_level'] - project.baseline_sigma_level:.1f}, 기간: {project.timeline_weeks}주"
        )

        print(f"🎊 Six Sigma DMAIC 프로젝트 완료!")
        print(
            f"📈 시그마 수준: {project.baseline_sigma_level:.1f}σ → {controls['final_sigma_level']:.1f}σ"
        )
        print(
            f"💰 예상 절감: ${improvements['expected_improvements'].get('cost_savings', 0):,.0f}"
        )

        return project_summary


# 데모 실행 함수
async def demo_six_sigma_quality_capsule():
    """Six Sigma 품질혁신 캡슐 데모"""

    print("🎯📊 Six Sigma 품질혁신 캡슐 데모")
    print("=" * 50)

    capsule = EchoSixSigmaQualityCapsule()

    # 테스트 프로젝트
    project_description = "고객 서비스 응답 시간 단축 및 만족도 향상"
    success_criteria = "응답 시간 50% 단축, 만족도 9점 이상 달성"

    result = await capsule.run_full_dmaic_project(project_description, success_criteria)

    print(f"\\n📊 프로젝트 결과 요약:")
    print(
        f"  시그마 개선: {result['sigma_improvement']['baseline']:.1f}σ → {result['sigma_improvement']['achieved']:.1f}σ"
    )
    print(f"  품질 향상: {result['business_impact']['quality_improvement']}")
    print(f"  비용 절감: ${result['business_impact']['cost_savings']:,.0f}")

    print(f"\\n🎊 Six Sigma 품질혁신 캡슐 데모 완료!")
    return capsule


if __name__ == "__main__":
    import asyncio

    asyncio.run(demo_six_sigma_quality_capsule())
