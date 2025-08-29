# echo_engine/signature_performance_reporter.py
"""
📊 Signature Performance Reporter
- 축적된 .flow.yaml 분석으로 시그니처별 강약점 리포트
- 최적 시그니처 조합 추천 및 성능 비교 분석
"""

import os
import yaml
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from pathlib import Path

from echo_engine.signature_mapper import SignaturePerformanceReporter as SignatureMapper
from echo_engine.seed_replay_analyzer import SeedReplayAnalyzer
from echo_engine.flow_visualizer import FlowVisualizer


@dataclass
class SignatureMetrics:
    signature_id: str
    total_executions: int
    success_rate: float
    avg_confidence: float
    avg_execution_time: float
    common_contexts: List[str]
    strength_areas: List[str]
    weakness_areas: List[str]
    evolution_frequency: float
    last_activity: str


@dataclass
class SignatureComparison:
    signature_a: str
    signature_b: str
    performance_difference: float
    complementary_score: float
    context_overlap: float
    recommended_combination: bool
    reasoning: str


@dataclass
class PerformanceReport:
    report_id: str
    generation_timestamp: str
    analysis_period: str
    signature_metrics: List[SignatureMetrics]
    signature_comparisons: List[SignatureComparison]
    recommendations: Dict[str, Any]
    insights: List[str]
    data_sources: Dict[str, int]


class SignaturePerformanceReporter:
    def __init__(self, flow_data_path: str = "flows/"):
        self.flow_data_path = Path(flow_data_path)
        self.signature_mapper = SignatureMapper()
        self.flow_visualizer = FlowVisualizer()

        # Data storage
        self.flow_data = []
        self.policy_data = []
        self.loop_execution_data = []
        self.signature_profiles = {}

        # Configuration
        self.analysis_window_days = 30
        self.min_executions_for_analysis = 5

    def collect_performance_data(self) -> Dict[str, int]:
        """성능 데이터 수집"""

        data_sources = {
            "flow_files": 0,
            "policy_files": 0,
            "loop_execution_files": 0,
            "signature_profiles": 0,
        }

        print("📊 성능 데이터 수집 중...")

        # 1. Flow YAML 파일들 수집
        self._collect_flow_files(data_sources)

        # 2. Policy 시뮬레이션 결과 수집
        self._collect_policy_files(data_sources)

        # 3. Loop 실행 데이터 수집
        self._collect_loop_execution_files(data_sources)

        # 4. 시그니처 프로파일 로드
        self._load_signature_profiles(data_sources)

        print(f"✅ 데이터 수집 완료: {sum(data_sources.values())}개 파일")

        return data_sources

    def _collect_flow_files(self, data_sources: Dict[str, int]):
        """Flow YAML 파일 수집"""

        flow_pattern = "**/*.yaml"

        for flow_file in self.flow_data_path.rglob(flow_pattern):
            if flow_file.is_file() and "policy" not in str(flow_file):
                try:
                    with open(flow_file, "r", encoding="utf-8") as f:
                        flow_data = yaml.safe_load(f)

                    # 데이터 구조 정규화
                    normalized_data = self._normalize_flow_data(
                        flow_data, str(flow_file)
                    )
                    if normalized_data:
                        self.flow_data.append(normalized_data)
                        data_sources["flow_files"] += 1

                except Exception as e:
                    print(f"Warning: 파일 로드 실패 {flow_file}: {e}")

    def _collect_policy_files(self, data_sources: Dict[str, int]):
        """Policy 시뮬레이션 파일 수집"""

        policy_path = self.flow_data_path / "policy"

        if policy_path.exists():
            for policy_file in policy_path.rglob("*.yaml"):
                try:
                    with open(policy_file, "r", encoding="utf-8") as f:
                        policy_data = yaml.safe_load(f)

                    normalized_data = self._normalize_policy_data(
                        policy_data, str(policy_file)
                    )
                    if normalized_data:
                        self.policy_data.append(normalized_data)
                        data_sources["policy_files"] += 1

                except Exception as e:
                    print(f"Warning: 정책 파일 로드 실패 {policy_file}: {e}")

    def _collect_loop_execution_files(self, data_sources: Dict[str, int]):
        """Loop 실행 데이터 수집"""

        # meta_logs에서 루프 실행 기록 수집
        meta_logs_path = Path("meta_logs")

        if meta_logs_path.exists():
            for log_file in meta_logs_path.glob("*.json*"):
                try:
                    if log_file.suffix == ".jsonl":
                        with open(log_file, "r", encoding="utf-8") as f:
                            for line in f:
                                log_entry = json.loads(line.strip())
                                normalized_data = self._normalize_loop_data(
                                    log_entry, str(log_file)
                                )
                                if normalized_data:
                                    self.loop_execution_data.append(normalized_data)
                                    data_sources["loop_execution_files"] += 1
                    elif log_file.suffix == ".json":
                        with open(log_file, "r", encoding="utf-8") as f:
                            log_data = json.load(f)
                            normalized_data = self._normalize_loop_data(
                                log_data, str(log_file)
                            )
                            if normalized_data:
                                self.loop_execution_data.append(normalized_data)
                                data_sources["loop_execution_files"] += 1

                except Exception as e:
                    print(f"Warning: 로그 파일 로드 실패 {log_file}: {e}")

    def _load_signature_profiles(self, data_sources: Dict[str, int]):
        """시그니처 프로파일 로드"""

        available_signatures = self.signature_mapper.get_available_signatures()

        for signature_id in available_signatures:
            profile = self.signature_mapper.generate_signature_profile(signature_id)
            if "error" not in profile:
                self.signature_profiles[signature_id] = profile
                data_sources["signature_profiles"] += 1

    def _normalize_flow_data(self, flow_data: Dict, file_path: str) -> Optional[Dict]:
        """Flow 데이터 정규화"""

        try:
            # 기본 flow 구조 파싱
            if "seed_id" in flow_data and "flow" in flow_data:
                return {
                    "type": "flow",
                    "seed_id": flow_data["seed_id"],
                    "signature_id": flow_data["flow"]
                    .get("meta", {})
                    .get("signature_alignment"),
                    "emotion": flow_data["flow"].get("emotion", {}).get("primary"),
                    "strategy": flow_data["flow"].get("strategy"),
                    "sensitivity": flow_data["flow"].get("meta", {}).get("sensitivity"),
                    "evolution_potential": flow_data["flow"]
                    .get("meta", {})
                    .get("evolution_potential"),
                    "timestamp": flow_data.get("export_timestamp"),
                    "file_path": file_path,
                }

            # Multi-seed flow 구조 파싱
            elif "multi_seed_flow" in flow_data:
                multi_flow = flow_data["multi_seed_flow"]
                results = []
                for flow in multi_flow.get("flows", []):
                    normalized = self._normalize_flow_data(flow, file_path)
                    if normalized:
                        results.append(normalized)
                return results[0] if len(results) == 1 else results

            return None

        except Exception as e:
            print(f"Flow 데이터 정규화 실패: {e}")
            return None

    def _normalize_policy_data(
        self, policy_data: Dict, file_path: str
    ) -> Optional[Dict]:
        """Policy 데이터 정규화"""

        try:
            if "policy_judgment" in policy_data:
                pj = policy_data["policy_judgment"]

                return {
                    "type": "policy",
                    "scenario_id": pj.get("scenario", {}).get("id"),
                    "scenario_domain": pj.get("scenario", {}).get("domain"),
                    "signature_id": pj.get("signature", {}).get("id"),
                    "seed_id": pj.get("signature", {}).get("seed_id"),
                    "confidence": pj.get("judgment", {}).get("confidence"),
                    "ethical_impact": pj.get("judgment", {}).get("ethical_impact"),
                    "complexity": pj.get("scenario", {}).get("complexity"),
                    "timestamp": policy_data.get("export_timestamp"),
                    "file_path": file_path,
                }

            return None

        except Exception as e:
            print(f"Policy 데이터 정규화 실패: {e}")
            return None

    def _normalize_loop_data(self, log_data: Dict, file_path: str) -> Optional[Dict]:
        """Loop 실행 데이터 정규화"""

        try:
            # 루프 실행 로그인지 확인
            if "loop_execution" in log_data:
                loop_exec = log_data["loop_execution"]

                return {
                    "type": "loop",
                    "signature_id": loop_exec.get("signature_id"),
                    "selected_loop": loop_exec.get("selected_loop"),
                    "success": loop_exec.get("loop_result", {}).get("success"),
                    "execution_time": loop_exec.get("loop_result", {}).get(
                        "execution_time"
                    ),
                    "confidence": loop_exec.get("metrics", {}).get("confidence_score"),
                    "timestamp": log_data.get("timestamp"),
                    "file_path": file_path,
                }

            # 기타 메타 로그 구조들...
            elif "judgment_mode" in log_data:
                return {
                    "type": "judgment",
                    "signature_id": log_data.get("signature_id"),
                    "confidence": log_data.get("confidence"),
                    "success": log_data.get("confidence", 0) > 0.5,
                    "processing_time": log_data.get("processing_time"),
                    "timestamp": log_data.get("timestamp"),
                    "file_path": file_path,
                }

            return None

        except Exception as e:
            print(f"Loop 데이터 정규화 실패: {e}")
            return None

    def analyze_signature_performance(self) -> List[SignatureMetrics]:
        """시그니처별 성능 분석"""

        print("📈 시그니처 성능 분석 중...")

        signature_metrics = []

        # 시그니처별 데이터 그룹화
        signature_data = defaultdict(list)

        # 모든 데이터 소스에서 시그니처별로 그룹화
        all_data = self.flow_data + self.policy_data + self.loop_execution_data

        for data in all_data:
            signature_id = data.get("signature_id")
            if signature_id:
                signature_data[signature_id].append(data)

        # 각 시그니처별 메트릭 계산
        for signature_id, data_list in signature_data.items():
            if len(data_list) >= self.min_executions_for_analysis:
                metrics = self._calculate_signature_metrics(signature_id, data_list)
                signature_metrics.append(metrics)

        return signature_metrics

    def _calculate_signature_metrics(
        self, signature_id: str, data_list: List[Dict]
    ) -> SignatureMetrics:
        """개별 시그니처 메트릭 계산"""

        # 기본 통계
        total_executions = len(data_list)

        # 성공률 계산
        success_data = [d for d in data_list if "success" in d]
        success_rate = (
            sum(d["success"] for d in success_data) / len(success_data)
            if success_data
            else 0.0
        )

        # 평균 신뢰도
        confidence_data = [
            d["confidence"] for d in data_list if d.get("confidence") is not None
        ]
        avg_confidence = (
            sum(confidence_data) / len(confidence_data) if confidence_data else 0.0
        )

        # 평균 실행 시간
        time_data = []
        for d in data_list:
            time_val = d.get("execution_time") or d.get("processing_time")
            if time_val is not None:
                time_data.append(float(time_val))

        avg_execution_time = sum(time_data) / len(time_data) if time_data else 0.0

        # 공통 컨텍스트 분석
        common_contexts = self._analyze_common_contexts(data_list)

        # 강점/약점 영역 분석
        strength_areas, weakness_areas = self._analyze_strength_weakness(
            signature_id, data_list
        )

        # 진화 빈도 (flow 데이터에서)
        flow_data = [d for d in data_list if d.get("type") == "flow"]
        evolution_potential_data = [
            d.get("evolution_potential", 0)
            for d in flow_data
            if d.get("evolution_potential")
        ]
        evolution_frequency = (
            sum(evolution_potential_data) / len(evolution_potential_data)
            if evolution_potential_data
            else 0.0
        )

        # 마지막 활동
        timestamps = [d.get("timestamp") for d in data_list if d.get("timestamp")]
        last_activity = max(timestamps) if timestamps else "Unknown"

        return SignatureMetrics(
            signature_id=signature_id,
            total_executions=total_executions,
            success_rate=round(success_rate, 3),
            avg_confidence=round(avg_confidence, 3),
            avg_execution_time=round(avg_execution_time, 3),
            common_contexts=common_contexts,
            strength_areas=strength_areas,
            weakness_areas=weakness_areas,
            evolution_frequency=round(evolution_frequency, 3),
            last_activity=last_activity,
        )

    def _analyze_common_contexts(self, data_list: List[Dict]) -> List[str]:
        """공통 컨텍스트 분석"""

        contexts = []

        # 정책 도메인
        policy_domains = [
            d.get("scenario_domain") for d in data_list if d.get("scenario_domain")
        ]
        if policy_domains:
            most_common_domain = Counter(policy_domains).most_common(1)[0][0]
            contexts.append(f"정책도메인:{most_common_domain}")

        # 감정 패턴
        emotions = [d.get("emotion") for d in data_list if d.get("emotion")]
        if emotions:
            most_common_emotion = Counter(emotions).most_common(1)[0][0]
            contexts.append(f"주감정:{most_common_emotion}")

        # 전략 패턴
        strategies = [d.get("strategy") for d in data_list if d.get("strategy")]
        if strategies:
            most_common_strategy = Counter(strategies).most_common(1)[0][0]
            contexts.append(f"주전략:{most_common_strategy}")

        # 루프 패턴
        loops = [d.get("selected_loop") for d in data_list if d.get("selected_loop")]
        if loops:
            most_common_loop = Counter(loops).most_common(1)[0][0]
            contexts.append(f"주루프:{most_common_loop}")

        return contexts[:5]  # 최대 5개까지

    def _analyze_strength_weakness(
        self, signature_id: str, data_list: List[Dict]
    ) -> Tuple[List[str], List[str]]:
        """강점/약점 영역 분석"""

        strengths = []
        weaknesses = []

        # 신뢰도 기반 분석
        confidence_data = [
            d["confidence"] for d in data_list if d.get("confidence") is not None
        ]
        if confidence_data:
            avg_confidence = sum(confidence_data) / len(confidence_data)
            if avg_confidence > 0.8:
                strengths.append("높은 신뢰도")
            elif avg_confidence < 0.5:
                weaknesses.append("낮은 신뢰도")

        # 성공률 기반 분석
        success_data = [d for d in data_list if "success" in d]
        if success_data:
            success_rate = sum(d["success"] for d in success_data) / len(success_data)
            if success_rate > 0.8:
                strengths.append("높은 성공률")
            elif success_rate < 0.6:
                weaknesses.append("높은 실패율")

        # 실행 시간 분석
        time_data = []
        for d in data_list:
            time_val = d.get("execution_time") or d.get("processing_time")
            if time_val is not None:
                time_data.append(float(time_val))

        if time_data:
            avg_time = sum(time_data) / len(time_data)
            if avg_time < 1.0:
                strengths.append("빠른 실행")
            elif avg_time > 5.0:
                weaknesses.append("느린 실행")

        # 컨텍스트별 특화 분석
        policy_data = [d for d in data_list if d.get("type") == "policy"]
        if policy_data:
            ethical_scores = [d.get("ethical_impact", 0) for d in policy_data]
            if ethical_scores:
                avg_ethical = sum(ethical_scores) / len(ethical_scores)
                if avg_ethical > 0.8:
                    strengths.append("높은 윤리적 판단")
                elif avg_ethical < 0.5:
                    weaknesses.append("윤리적 고려 부족")

        # 시그니처 고유 특성 반영
        if signature_id in self.signature_profiles:
            profile = self.signature_profiles[signature_id]
            primary_strategies = profile.get("primary_strategies", [])

            if "empathetic" in primary_strategies:
                # Aurora 특성 검증
                emotion_data = [d.get("emotion") for d in data_list if d.get("emotion")]
                if emotion_data and "joy" in emotion_data:
                    strengths.append("감정적 공감 우수")

            elif "analytical" in primary_strategies:
                # Sage 특성 검증
                complexity_data = [
                    d.get("complexity", 0) for d in data_list if d.get("complexity")
                ]
                if complexity_data:
                    avg_complexity = sum(complexity_data) / len(complexity_data)
                    if avg_complexity > 0.7:
                        strengths.append("복잡한 문제 처리 우수")

        return strengths[:5], weaknesses[:5]  # 각각 최대 5개

    def compare_signatures(
        self, signature_metrics: List[SignatureMetrics]
    ) -> List[SignatureComparison]:
        """시그니처 간 비교 분석"""

        print("🔍 시그니처 비교 분석 중...")

        comparisons = []

        # 모든 시그니처 쌍에 대해 비교
        for i, sig_a in enumerate(signature_metrics):
            for sig_b in signature_metrics[i + 1 :]:
                comparison = self._compare_signature_pair(sig_a, sig_b)
                comparisons.append(comparison)

        return comparisons

    def _compare_signature_pair(
        self, sig_a: SignatureMetrics, sig_b: SignatureMetrics
    ) -> SignatureComparison:
        """두 시그니처 간 비교"""

        # 성능 차이 계산 (종합 점수)
        score_a = (
            sig_a.success_rate * 0.4
            + sig_a.avg_confidence * 0.3
            + (1.0 - min(sig_a.avg_execution_time / 10.0, 1.0)) * 0.3
        )
        score_b = (
            sig_b.success_rate * 0.4
            + sig_b.avg_confidence * 0.3
            + (1.0 - min(sig_b.avg_execution_time / 10.0, 1.0)) * 0.3
        )

        performance_difference = score_a - score_b

        # 상호보완성 점수
        complementary_score = self._calculate_complementary_score(sig_a, sig_b)

        # 컨텍스트 중복도
        context_overlap = self._calculate_context_overlap(sig_a, sig_b)

        # 조합 추천 여부
        recommended_combination = (
            abs(performance_difference) < 0.3  # 성능이 비슷하고
            and complementary_score > 0.6  # 상호보완적이며
            and context_overlap < 0.8  # 컨텍스트 중복이 적음
        )

        # 추천 근거
        reasoning = self._generate_comparison_reasoning(
            sig_a, sig_b, performance_difference, complementary_score, context_overlap
        )

        return SignatureComparison(
            signature_a=sig_a.signature_id,
            signature_b=sig_b.signature_id,
            performance_difference=round(performance_difference, 3),
            complementary_score=round(complementary_score, 3),
            context_overlap=round(context_overlap, 3),
            recommended_combination=recommended_combination,
            reasoning=reasoning,
        )

    def _calculate_complementary_score(
        self, sig_a: SignatureMetrics, sig_b: SignatureMetrics
    ) -> float:
        """상호보완성 점수 계산"""

        complementary_factors = []

        # 강점/약점 상호보완
        a_strengths = set(sig_a.strength_areas)
        a_weaknesses = set(sig_a.weakness_areas)
        b_strengths = set(sig_b.strength_areas)
        b_weaknesses = set(sig_b.weakness_areas)

        # A의 약점을 B가 보완
        a_weakness_covered = len(a_weaknesses & b_strengths) / max(len(a_weaknesses), 1)
        # B의 약점을 A가 보완
        b_weakness_covered = len(b_weaknesses & a_strengths) / max(len(b_weaknesses), 1)

        complementary_factors.append((a_weakness_covered + b_weakness_covered) / 2)

        # 성능 특성 보완
        if sig_a.avg_execution_time > 3.0 and sig_b.avg_execution_time < 2.0:
            complementary_factors.append(0.8)  # 속도 보완
        elif sig_b.avg_execution_time > 3.0 and sig_a.avg_execution_time < 2.0:
            complementary_factors.append(0.8)

        if abs(sig_a.avg_confidence - sig_b.avg_confidence) > 0.3:
            complementary_factors.append(0.6)  # 신뢰도 다양성

        # 진화 패턴 보완
        if abs(sig_a.evolution_frequency - sig_b.evolution_frequency) > 0.3:
            complementary_factors.append(0.5)  # 진화 특성 다양성

        return (
            sum(complementary_factors) / len(complementary_factors)
            if complementary_factors
            else 0.0
        )

    def _calculate_context_overlap(
        self, sig_a: SignatureMetrics, sig_b: SignatureMetrics
    ) -> float:
        """컨텍스트 중복도 계산"""

        contexts_a = set(sig_a.common_contexts)
        contexts_b = set(sig_b.common_contexts)

        if not contexts_a and not contexts_b:
            return 0.0

        overlap = len(contexts_a & contexts_b)
        total_unique = len(contexts_a | contexts_b)

        return overlap / total_unique if total_unique > 0 else 0.0

    def _generate_comparison_reasoning(
        self,
        sig_a: SignatureMetrics,
        sig_b: SignatureMetrics,
        perf_diff: float,
        comp_score: float,
        overlap: float,
    ) -> str:
        """비교 분석 근거 생성"""

        reasoning_parts = []

        # 성능 차이 분석
        if abs(perf_diff) < 0.1:
            reasoning_parts.append("성능이 거의 동등함")
        elif perf_diff > 0.3:
            reasoning_parts.append(f"{sig_a.signature_id}가 종합 성능 우수")
        elif perf_diff < -0.3:
            reasoning_parts.append(f"{sig_b.signature_id}가 종합 성능 우수")

        # 상호보완성 분석
        if comp_score > 0.7:
            reasoning_parts.append("높은 상호보완성")
        elif comp_score < 0.3:
            reasoning_parts.append("상호보완성 낮음")

        # 컨텍스트 중복 분석
        if overlap > 0.8:
            reasoning_parts.append("컨텍스트 중복 높음")
        elif overlap < 0.3:
            reasoning_parts.append("서로 다른 영역 특화")

        # 특별한 패턴 감지
        if sig_a.avg_execution_time < 1.0 and sig_b.avg_execution_time > 3.0:
            reasoning_parts.append(
                f"{sig_a.signature_id}는 속도, {sig_b.signature_id}는 신중함"
            )

        return " | ".join(reasoning_parts) if reasoning_parts else "추가 분석 필요"

    def generate_recommendations(
        self,
        signature_metrics: List[SignatureMetrics],
        comparisons: List[SignatureComparison],
    ) -> Dict[str, Any]:
        """추천 사항 생성"""

        print("💡 추천 사항 생성 중...")

        recommendations = {}

        # 1. 최고 성능 시그니처
        best_overall = max(
            signature_metrics,
            key=lambda x: x.success_rate * 0.5 + x.avg_confidence * 0.5,
        )
        recommendations["best_overall_signature"] = {
            "signature_id": best_overall.signature_id,
            "success_rate": best_overall.success_rate,
            "avg_confidence": best_overall.avg_confidence,
            "reasoning": f"성공률 {best_overall.success_rate:.1%}, 신뢰도 {best_overall.avg_confidence:.2f}",
        }

        # 2. 특화 영역별 최적 시그니처
        recommendations["specialized_recommendations"] = (
            self._generate_specialized_recommendations(signature_metrics)
        )

        # 3. 추천 시그니처 조합
        recommended_combinations = [c for c in comparisons if c.recommended_combination]
        recommendations["recommended_combinations"] = [
            {
                "signatures": [c.signature_a, c.signature_b],
                "complementary_score": c.complementary_score,
                "reasoning": c.reasoning,
            }
            for c in recommended_combinations[:3]  # 상위 3개
        ]

        # 4. 개선이 필요한 시그니처
        improvement_needed = [
            s
            for s in signature_metrics
            if s.success_rate < 0.6 or s.avg_confidence < 0.5
        ]
        recommendations["improvement_needed"] = [
            {
                "signature_id": s.signature_id,
                "issues": s.weakness_areas,
                "suggested_actions": self._suggest_improvement_actions(s),
            }
            for s in improvement_needed
        ]

        # 5. 시나리오별 추천
        recommendations["scenario_recommendations"] = (
            self._generate_scenario_recommendations(signature_metrics)
        )

        return recommendations

    def _generate_specialized_recommendations(
        self, signature_metrics: List[SignatureMetrics]
    ) -> Dict[str, str]:
        """특화 영역별 추천"""

        specialized = {}

        # 속도 최적화
        fastest = min(signature_metrics, key=lambda x: x.avg_execution_time)
        specialized["fastest_execution"] = fastest.signature_id

        # 높은 신뢰도
        most_confident = max(signature_metrics, key=lambda x: x.avg_confidence)
        specialized["highest_confidence"] = most_confident.signature_id

        # 진화 활발
        most_evolving = max(signature_metrics, key=lambda x: x.evolution_frequency)
        specialized["most_adaptive"] = most_evolving.signature_id

        # 복잡한 문제 처리 (정책 데이터 기반)
        policy_specialists = [
            s for s in signature_metrics if "정책도메인" in " ".join(s.common_contexts)
        ]
        if policy_specialists:
            best_policy = max(policy_specialists, key=lambda x: x.avg_confidence)
            specialized["policy_specialist"] = best_policy.signature_id

        return specialized

    def _suggest_improvement_actions(
        self, signature_metrics: SignatureMetrics
    ) -> List[str]:
        """개선 액션 제안"""

        actions = []

        if signature_metrics.success_rate < 0.6:
            actions.append("판단 알고리즘 재조정 필요")

        if signature_metrics.avg_confidence < 0.5:
            actions.append("메타 민감도 증가 고려")

        if signature_metrics.avg_execution_time > 5.0:
            actions.append("실행 효율성 최적화 필요")

        if signature_metrics.evolution_frequency > 0.8:
            actions.append("과도한 진화 패턴 조정 필요")

        if "낮은 신뢰도" in signature_metrics.weakness_areas:
            actions.append("신뢰도 향상을 위한 컨텍스트 특화")

        return actions[:3]  # 최대 3개

    def _generate_scenario_recommendations(
        self, signature_metrics: List[SignatureMetrics]
    ) -> Dict[str, str]:
        """시나리오별 추천"""

        scenario_recs = {}

        # 정책 시나리오
        policy_candidates = [
            s
            for s in signature_metrics
            if any("정책" in ctx for ctx in s.common_contexts)
        ]
        if policy_candidates:
            best_policy = max(policy_candidates, key=lambda x: x.avg_confidence)
            scenario_recs["policy_scenarios"] = best_policy.signature_id

        # 감정적 시나리오
        emotional_candidates = [
            s
            for s in signature_metrics
            if any(
                "joy" in ctx or "empathetic" in " ".join(s.strength_areas)
                for ctx in s.common_contexts
            )
        ]
        if emotional_candidates:
            best_emotional = max(emotional_candidates, key=lambda x: x.success_rate)
            scenario_recs["emotional_scenarios"] = best_emotional.signature_id

        # 분석적 시나리오
        analytical_candidates = [
            s
            for s in signature_metrics
            if any(
                "analytical" in " ".join(s.strength_areas) for ctx in s.common_contexts
            )
        ]
        if analytical_candidates:
            best_analytical = max(analytical_candidates, key=lambda x: x.avg_confidence)
            scenario_recs["analytical_scenarios"] = best_analytical.signature_id

        return scenario_recs

    def generate_insights(
        self,
        signature_metrics: List[SignatureMetrics],
        comparisons: List[SignatureComparison],
    ) -> List[str]:
        """통찰 생성"""

        insights = []

        # 전체 성능 트렌드
        avg_success_rate = sum(s.success_rate for s in signature_metrics) / len(
            signature_metrics
        )
        if avg_success_rate > 0.8:
            insights.append(
                f"전체 시그니처 성능이 우수함 (평균 성공률 {avg_success_rate:.1%})"
            )
        elif avg_success_rate < 0.6:
            insights.append(
                f"시그니처 성능 개선이 필요함 (평균 성공률 {avg_success_rate:.1%})"
            )

        # 성능 분산 분석
        success_rates = [s.success_rate for s in signature_metrics]
        performance_variance = np.var(success_rates)
        if performance_variance > 0.1:
            insights.append("시그니처 간 성능 차이가 큼 - 특화 영역 활용 고려")
        else:
            insights.append("시그니처 간 성능이 균등함 - 안정적인 시스템")

        # 실행 시간 분석
        execution_times = [s.avg_execution_time for s in signature_metrics]
        if max(execution_times) > 5.0:
            slowest = max(signature_metrics, key=lambda x: x.avg_execution_time)
            insights.append(f"{slowest.signature_id}의 실행 시간 최적화 필요")

        # 상호보완성 분석
        high_complementary = [c for c in comparisons if c.complementary_score > 0.7]
        if high_complementary:
            insights.append(
                f"시그니처 조합 활용 가능: {len(high_complementary)}개 조합 발견"
            )

        # 특화 패턴
        specialized_contexts = set()
        for s in signature_metrics:
            specialized_contexts.update(s.common_contexts)

        if len(specialized_contexts) > 10:
            insights.append("다양한 컨텍스트에서 활용됨 - 범용성 높음")

        # 진화 패턴
        high_evolution = [s for s in signature_metrics if s.evolution_frequency > 0.7]
        if high_evolution:
            insights.append(f"{len(high_evolution)}개 시그니처가 활발한 진화 패턴 보임")

        return insights[:5]  # 최대 5개

    def generate_performance_report(self) -> PerformanceReport:
        """종합 성능 리포트 생성"""

        print("📋 성능 리포트 생성 중...")

        # 데이터 수집
        data_sources = self.collect_performance_data()

        # 시그니처 성능 분석
        signature_metrics = self.analyze_signature_performance()

        # 시그니처 비교
        comparisons = self.compare_signatures(signature_metrics)

        # 추천 사항 생성
        recommendations = self.generate_recommendations(signature_metrics, comparisons)

        # 통찰 생성
        insights = self.generate_insights(signature_metrics, comparisons)

        # 분석 기간
        cutoff_date = datetime.now() - timedelta(days=self.analysis_window_days)
        analysis_period = f"{cutoff_date.strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}"

        report = PerformanceReport(
            report_id=f"perf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            generation_timestamp=datetime.now().isoformat(),
            analysis_period=analysis_period,
            signature_metrics=signature_metrics,
            signature_comparisons=comparisons,
            recommendations=recommendations,
            insights=insights,
            data_sources=data_sources,
        )

        return report

    def save_report(
        self, report: PerformanceReport, output_path: str = "reports/"
    ) -> str:
        """리포트 저장"""

        os.makedirs(output_path, exist_ok=True)

        # JSON 형태로 저장
        report_data = asdict(report)

        filename = f"{report.report_id}.json"
        filepath = os.path.join(output_path, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        print(f"📊 성능 리포트 저장: {filepath}")

        # 요약 텍스트 파일도 생성
        self._save_report_summary(report, output_path)

        return filepath

    def _save_report_summary(self, report: PerformanceReport, output_path: str):
        """리포트 요약 텍스트 저장"""

        summary_filename = f"{report.report_id}_summary.txt"
        summary_filepath = os.path.join(output_path, summary_filename)

        with open(summary_filepath, "w", encoding="utf-8") as f:
            f.write(f"📊 EchoJudgment 시그니처 성능 리포트\n")
            f.write(f"=" * 50 + "\n\n")

            f.write(f"🗓️ 생성일시: {report.generation_timestamp}\n")
            f.write(f"📅 분석기간: {report.analysis_period}\n")
            f.write(f"📁 데이터소스: {sum(report.data_sources.values())}개 파일\n\n")

            f.write(f"📈 시그니처 성능 요약\n")
            f.write(f"-" * 30 + "\n")

            for metrics in report.signature_metrics:
                f.write(f"🔸 {metrics.signature_id}\n")
                f.write(f"   성공률: {metrics.success_rate:.1%}\n")
                f.write(f"   신뢰도: {metrics.avg_confidence:.2f}\n")
                f.write(f"   실행횟수: {metrics.total_executions}\n")
                f.write(f"   강점: {', '.join(metrics.strength_areas[:3])}\n")
                f.write(f"   약점: {', '.join(metrics.weakness_areas[:3])}\n\n")

            f.write(f"💡 주요 추천사항\n")
            f.write(f"-" * 30 + "\n")

            best = report.recommendations.get("best_overall_signature", {})
            f.write(f"🏆 최고 성능: {best.get('signature_id', 'N/A')}\n")
            f.write(f"   {best.get('reasoning', '')}\n\n")

            f.write(f"🔍 주요 통찰\n")
            f.write(f"-" * 30 + "\n")
            for i, insight in enumerate(report.insights, 1):
                f.write(f"{i}. {insight}\n")

        print(f"📄 리포트 요약 저장: {summary_filepath}")


# Convenience functions
def generate_signature_report(flow_data_path: str = "flows/") -> PerformanceReport:
    """시그니처 성능 리포트 생성 편의 함수"""
    reporter = SignaturePerformanceReporter(flow_data_path)
    return reporter.generate_performance_report()


def analyze_signature_performance_quick(signature_id: str) -> Dict[str, Any]:
    """특정 시그니처 빠른 성능 분석"""
    reporter = SignaturePerformanceReporter()
    data_sources = reporter.collect_performance_data()

    all_data = reporter.flow_data + reporter.policy_data + reporter.loop_execution_data
    signature_data = [d for d in all_data if d.get("signature_id") == signature_id]

    if signature_data:
        metrics = reporter._calculate_signature_metrics(signature_id, signature_data)
        return asdict(metrics)
    else:
        return {"error": f"No data found for signature {signature_id}"}


if __name__ == "__main__":
    # 테스트 코드
    print("📊 Signature Performance Reporter 테스트")

    reporter = SignaturePerformanceReporter()

    print("\n📁 데이터 수집:")
    data_sources = reporter.collect_performance_data()
    print(f"수집된 파일: {data_sources}")

    if sum(data_sources.values()) > 0:
        print("\n📈 성능 분석:")
        signature_metrics = reporter.analyze_signature_performance()
        print(f"분석된 시그니처: {len(signature_metrics)}개")

        for metrics in signature_metrics:
            print(
                f"- {metrics.signature_id}: 성공률 {metrics.success_rate:.1%}, 신뢰도 {metrics.avg_confidence:.2f}"
            )

        if len(signature_metrics) > 1:
            print("\n🔍 시그니처 비교:")
            comparisons = reporter.compare_signatures(signature_metrics)
            print(f"비교 분석: {len(comparisons)}개 조합")

            for comp in comparisons[:3]:  # 첫 3개만 출력
                print(
                    f"- {comp.signature_a} vs {comp.signature_b}: 상호보완성 {comp.complementary_score:.2f}"
                )

        print("\n📋 종합 리포트 생성:")
        report = reporter.generate_performance_report()
        print(f"리포트 ID: {report.report_id}")
        print(f"통찰: {len(report.insights)}개")

        # 리포트 저장
        report_path = reporter.save_report(report)
        print(f"리포트 저장: {report_path}")

    else:
        print("분석할 데이터가 없습니다. 먼저 시스템을 실행하여 데이터를 생성해주세요.")

    print("✅ Signature Performance Reporter 테스트 완료")
