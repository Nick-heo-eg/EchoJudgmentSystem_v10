# echo_engine/adaptive_learning_engine.py
"""
🧬 Adaptive Learning Engine
- 실패 패턴 자동 감지 → 시그니처 진화 → 성능 개선 루프
- 자기 개선하는 판단 시스템 (존재 기반 학습 자동화)
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict

from echo_engine.seed_kernel import EchoSeedKernel, InitialState
from echo_engine.signature_performance_reporter import SignaturePerformanceReporter
from echo_engine.seed_replay_analyzer import SeedReplayAnalyzer
from echo_engine.loop_meta_integrator import LoopMetaIntegrator
from echo_engine.meta_log_writer import log_evolution_event


@dataclass
class FailurePattern:
    pattern_id: str
    failure_type: str
    signature_id: str
    context_pattern: Dict[str, Any]
    frequency: int
    severity: float
    first_occurrence: str
    last_occurrence: str
    related_seeds: List[str]


@dataclass
class LearningAction:
    action_id: str
    action_type: str  # evolve_signature, adjust_sensitivity, create_new_signature
    target_signature: str
    parameters: Dict[str, Any]
    expected_improvement: float
    priority: int


@dataclass
class AdaptationResult:
    adaptation_id: str
    trigger_pattern: str
    actions_taken: List[LearningAction]
    before_metrics: Dict[str, float]
    after_metrics: Dict[str, float]
    success_rate: float
    timestamp: str


class AdaptiveLearningEngine:
    def __init__(self, kernel: EchoSeedKernel):
        self.kernel = kernel
        self.signature_performance_reporter = SignaturePerformanceReporter()
        self.replay_analyzer = SeedReplayAnalyzer(kernel)
        self.meta_integrator = LoopMetaIntegrator()

        # Learning state
        self.failure_patterns = {}
        self.learning_history = []
        self.adaptation_results = []
        self.performance_baseline = {}

        # Configuration
        self.failure_threshold = 0.6  # 60% 이상 실패 시 패턴으로 인식
        self.pattern_min_frequency = 3  # 최소 3회 발생해야 패턴으로 인식
        self.learning_window_days = 7  # 7일간의 데이터로 학습
        self.adaptation_cooldown_hours = 24  # 24시간마다 한 번만 적응

        # Performance tracking
        self.performance_window = deque(maxlen=100)  # 최근 100개 성능 기록
        self.last_adaptation_time = {}  # 시그니처별 마지막 적응 시간

    def analyze_failure_patterns(self) -> List[FailurePattern]:
        """실패 패턴 분석 및 감지"""

        # 최근 window 내의 데이터만 분석
        cutoff_time = datetime.now() - timedelta(days=self.learning_window_days)
        recent_history = [
            h
            for h in self.kernel.evolution_history
            if datetime.fromisoformat(h.get("timestamp", "1970-01-01")) > cutoff_time
        ]

        # 실패 이벤트 그룹화
        failure_groups = defaultdict(list)

        for event in recent_history:
            if event.get("event_type") == "seed_evolution":
                trigger = event.get("trigger", {})
                if self._is_failure_trigger(trigger):
                    pattern_key = self._extract_pattern_key(event)
                    failure_groups[pattern_key].append(event)

        # 패턴 객체 생성
        patterns = []
        for pattern_key, events in failure_groups.items():
            if len(events) >= self.pattern_min_frequency:
                pattern = self._create_failure_pattern(pattern_key, events)
                patterns.append(pattern)
                self.failure_patterns[pattern.pattern_id] = pattern

        return patterns

    def _is_failure_trigger(self, trigger: Dict) -> bool:
        """실패 트리거인지 판단"""
        failure_indicators = [
            "low_confidence",
            "judgment_failure",
            "strategy_mismatch",
            "emotional_discord",
            "meta_confusion",
            "loop_timeout",
        ]

        trigger_reason = trigger.get("reason", "")
        return any(indicator in trigger_reason for indicator in failure_indicators)

    def _extract_pattern_key(self, event: Dict) -> str:
        """이벤트에서 패턴 키 추출"""
        seed_id = event.get("seed_id", "unknown")
        trigger = event.get("trigger", {})

        # 시드의 시그니처 찾기
        signature_id = "unknown"
        if seed_id in self.kernel.seed_registry:
            signature_id = (
                self.kernel.seed_registry[seed_id].signature_alignment or "unknown"
            )

        # 컨텍스트 패턴 추출
        context_pattern = self._extract_context_pattern(event)

        return f"{signature_id}_{trigger.get('reason', 'unknown')}_{context_pattern}"

    def _extract_context_pattern(self, event: Dict) -> str:
        """컨텍스트 패턴 추출"""
        changes = event.get("changes", {})

        # 주요 변화 요소들을 패턴으로 변환
        pattern_elements = []

        if "emotion_change" in changes:
            emotion_change = changes["emotion_change"]
            pattern_elements.append(
                f"emotion_{emotion_change.get('from')}to{emotion_change.get('to')}"
            )

        if "strategy_change" in changes:
            strategy_change = changes["strategy_change"]
            pattern_elements.append(
                f"strategy_{strategy_change.get('from')}to{strategy_change.get('to')}"
            )

        if "sensitivity_change" in changes:
            pattern_elements.append("sensitivity_adjusted")

        return "_".join(pattern_elements) if pattern_elements else "generic"

    def _create_failure_pattern(
        self, pattern_key: str, events: List[Dict]
    ) -> FailurePattern:
        """실패 패턴 객체 생성"""

        # 패턴 분석
        timestamps = [e.get("timestamp", "") for e in events]
        seed_ids = [e.get("seed_id", "") for e in events]

        # 심각도 계산 (빈도와 최근성 기반)
        frequency = len(events)
        recent_events = len(
            [
                t
                for t in timestamps
                if datetime.fromisoformat(t) > datetime.now() - timedelta(days=1)
            ]
        )
        severity = min(1.0, (frequency * 0.1) + (recent_events * 0.3))

        # 시그니처 추출
        signature_id = pattern_key.split("_")[0] if "_" in pattern_key else "unknown"

        # 실패 유형 추출
        failure_type = pattern_key.split("_")[1] if "_" in pattern_key else "unknown"

        # 컨텍스트 패턴 분석
        context_pattern = self._analyze_context_pattern(events)

        return FailurePattern(
            pattern_id=f"pattern_{pattern_key}_{datetime.now().strftime('%Y%m%d_%H%M')}",
            failure_type=failure_type,
            signature_id=signature_id,
            context_pattern=context_pattern,
            frequency=frequency,
            severity=severity,
            first_occurrence=min(timestamps) if timestamps else "",
            last_occurrence=max(timestamps) if timestamps else "",
            related_seeds=list(set(seed_ids)),
        )

    def _analyze_context_pattern(self, events: List[Dict]) -> Dict[str, Any]:
        """이벤트들의 컨텍스트 패턴 분석"""

        emotion_changes = []
        strategy_changes = []
        sensitivity_changes = []

        for event in events:
            changes = event.get("changes", {})

            if "emotion_change" in changes:
                emotion_changes.append(changes["emotion_change"])
            if "strategy_change" in changes:
                strategy_changes.append(changes["strategy_change"])
            if "sensitivity_change" in changes:
                sensitivity_changes.append(changes["sensitivity_change"])

        return {
            "common_emotion_transitions": self._find_common_transitions(
                emotion_changes
            ),
            "common_strategy_transitions": self._find_common_transitions(
                strategy_changes
            ),
            "sensitivity_adjustment_frequency": len(sensitivity_changes),
            "total_events": len(events),
        }

    def _find_common_transitions(self, transitions: List[Dict]) -> Dict[str, int]:
        """공통 전환 패턴 찾기"""
        if not transitions:
            return {}

        transition_counts = defaultdict(int)
        for transition in transitions:
            from_state = transition.get("from", "unknown")
            to_state = transition.get("to", "unknown")
            transition_key = f"{from_state} → {to_state}"
            transition_counts[transition_key] += 1

        return dict(transition_counts)

    def generate_learning_actions(
        self, patterns: List[FailurePattern]
    ) -> List[LearningAction]:
        """실패 패턴을 바탕으로 학습 액션 생성"""

        actions = []

        for pattern in patterns:
            # 패턴 심각도에 따른 액션 선택
            if pattern.severity > 0.8:
                actions.extend(self._generate_critical_actions(pattern))
            elif pattern.severity > 0.5:
                actions.extend(self._generate_moderate_actions(pattern))
            else:
                actions.extend(self._generate_minor_actions(pattern))

        # 우선순위별 정렬
        actions.sort(key=lambda x: x.priority, reverse=True)

        return actions

    def _generate_critical_actions(
        self, pattern: FailurePattern
    ) -> List[LearningAction]:
        """심각한 패턴에 대한 액션"""
        actions = []

        # 1. 시그니처 진화
        actions.append(
            LearningAction(
                action_id=f"evolve_{pattern.pattern_id}",
                action_type="evolve_signature",
                target_signature=pattern.signature_id,
                parameters={
                    "evolution_strength": 0.8,
                    "focus_areas": [pattern.failure_type],
                    "context_adaptation": pattern.context_pattern,
                },
                expected_improvement=0.6,
                priority=10,
            )
        )

        # 2. 새로운 시그니처 생성 (매우 심각한 경우)
        if pattern.frequency > 10:
            actions.append(
                LearningAction(
                    action_id=f"create_{pattern.pattern_id}",
                    action_type="create_new_signature",
                    target_signature=f"{pattern.signature_id}_adapted",
                    parameters={
                        "base_signature": pattern.signature_id,
                        "adaptation_focus": pattern.failure_type,
                        "context_specialization": pattern.context_pattern,
                    },
                    expected_improvement=0.8,
                    priority=9,
                )
            )

        return actions

    def _generate_moderate_actions(
        self, pattern: FailurePattern
    ) -> List[LearningAction]:
        """중간 정도 패턴에 대한 액션"""
        actions = []

        # 민감도 조정
        actions.append(
            LearningAction(
                action_id=f"adjust_{pattern.pattern_id}",
                action_type="adjust_sensitivity",
                target_signature=pattern.signature_id,
                parameters={
                    "sensitivity_delta": 0.1,
                    "adjustment_type": (
                        "increase"
                        if "low_confidence" in pattern.failure_type
                        else "decrease"
                    ),
                    "context_specific": True,
                },
                expected_improvement=0.4,
                priority=7,
            )
        )

        # 컨텍스트 특화 전략 개발
        actions.append(
            LearningAction(
                action_id=f"specialize_{pattern.pattern_id}",
                action_type="context_specialization",
                target_signature=pattern.signature_id,
                parameters={
                    "specialization_area": pattern.failure_type,
                    "context_rules": pattern.context_pattern,
                },
                expected_improvement=0.5,
                priority=6,
            )
        )

        return actions

    def _generate_minor_actions(self, pattern: FailurePattern) -> List[LearningAction]:
        """경미한 패턴에 대한 액션"""
        actions = []

        # 미세 조정
        actions.append(
            LearningAction(
                action_id=f"finetune_{pattern.pattern_id}",
                action_type="fine_tuning",
                target_signature=pattern.signature_id,
                parameters={
                    "adjustment_magnitude": 0.05,
                    "target_metric": pattern.failure_type,
                },
                expected_improvement=0.2,
                priority=3,
            )
        )

        return actions

    def execute_learning_actions(
        self, actions: List[LearningAction]
    ) -> List[AdaptationResult]:
        """학습 액션 실행"""

        results = []

        for action in actions:
            # 쿨다운 체크
            if not self._can_adapt_signature(action.target_signature):
                continue

            # 이전 메트릭 기록
            before_metrics = self._get_signature_metrics(action.target_signature)

            # 액션 실행
            success = self._execute_single_action(action)

            if success:
                # 이후 메트릭 기록 (약간의 지연 후)
                after_metrics = self._get_signature_metrics(action.target_signature)

                # 결과 분석
                success_rate = self._calculate_success_rate(
                    before_metrics, after_metrics
                )

                result = AdaptationResult(
                    adaptation_id=f"adapt_{action.action_id}",
                    trigger_pattern=action.action_id,
                    actions_taken=[action],
                    before_metrics=before_metrics,
                    after_metrics=after_metrics,
                    success_rate=success_rate,
                    timestamp=datetime.now().isoformat(),
                )

                results.append(result)
                self.adaptation_results.append(result)

                # 쿨다운 설정
                self.last_adaptation_time[action.target_signature] = datetime.now()

                # 진화 이벤트 로깅
                log_evolution_event(
                    {
                        "event": f"Adaptive learning: {action.action_type}",
                        "tag": ["adaptive_learning", "auto_improvement"],
                        "cause": [action.action_id],
                        "effect": [f"success_rate_{success_rate:.2f}"],
                        "resolution": f"Signature {action.target_signature} adapted",
                        "insight": f"Automated learning improved performance",
                        "adaptation_strength": action.expected_improvement,
                        "coherence_improvement": success_rate - 0.5,
                        "reflection_depth": 3,
                    },
                    action.target_signature,
                )

        return results

    def _can_adapt_signature(self, signature_id: str) -> bool:
        """시그니처 적응 가능 여부 확인 (쿨다운)"""
        if signature_id not in self.last_adaptation_time:
            return True

        last_time = self.last_adaptation_time[signature_id]
        cooldown_time = last_time + timedelta(hours=self.adaptation_cooldown_hours)

        return datetime.now() > cooldown_time

    def _get_signature_metrics(self, signature_id: str) -> Dict[str, float]:
        """시그니처 성능 메트릭 수집"""

        # 해당 시그니처의 시드들 찾기
        signature_seeds = [
            seed
            for seed in self.kernel.seed_registry.values()
            if seed.signature_alignment == signature_id
        ]

        if not signature_seeds:
            return {"error": "No seeds found for signature"}

        # 메트릭 계산
        avg_sensitivity = sum(s.meta_sensitivity for s in signature_seeds) / len(
            signature_seeds
        )
        avg_evolution_potential = sum(
            s.evolution_potential for s in signature_seeds
        ) / len(signature_seeds)

        # 최근 성공률 계산 (진화 빈도 기반)
        recent_evolutions = [
            e
            for e in self.kernel.evolution_history
            if e.get("seed_id") in [s.identity_trace.seed_id for s in signature_seeds]
            and datetime.fromisoformat(e.get("timestamp", "1970-01-01"))
            > datetime.now() - timedelta(days=1)
        ]

        failure_rate = len(
            [
                e
                for e in recent_evolutions
                if self._is_failure_trigger(e.get("trigger", {}))
            ]
        ) / max(len(recent_evolutions), 1)
        success_rate = 1.0 - failure_rate

        return {
            "avg_sensitivity": round(avg_sensitivity, 3),
            "avg_evolution_potential": round(avg_evolution_potential, 3),
            "success_rate": round(success_rate, 3),
            "seed_count": len(signature_seeds),
            "recent_activity": len(recent_evolutions),
        }

    def _execute_single_action(self, action: LearningAction) -> bool:
        """단일 학습 액션 실행"""

        try:
            if action.action_type == "evolve_signature":
                return self._evolve_signature(action)
            elif action.action_type == "adjust_sensitivity":
                return self._adjust_sensitivity(action)
            elif action.action_type == "create_new_signature":
                return self._create_new_signature(action)
            elif action.action_type == "context_specialization":
                return self._apply_context_specialization(action)
            elif action.action_type == "fine_tuning":
                return self._apply_fine_tuning(action)
            else:
                print(f"Unknown action type: {action.action_type}")
                return False
        except Exception as e:
            print(f"Error executing action {action.action_id}: {e}")
            return False

    def _evolve_signature(self, action: LearningAction) -> bool:
        """시그니처 진화 실행"""

        # 해당 시그니처의 시드들을 모두 진화
        signature_seeds = [
            seed_id
            for seed_id, seed in self.kernel.seed_registry.items()
            if seed.signature_alignment == action.target_signature
        ]

        evolution_count = 0
        for seed_id in signature_seeds[:5]:  # 최대 5개만 진화
            trigger = {
                "reason": "adaptive_learning",
                "strength": action.parameters.get("evolution_strength", 0.5),
                "focus": action.parameters.get("focus_areas", []),
            }

            evolved_seed = self.kernel.evolve_seed(seed_id, trigger)
            if evolved_seed:
                evolution_count += 1

        return evolution_count > 0

    def _adjust_sensitivity(self, action: LearningAction) -> bool:
        """민감도 조정 실행"""

        # 해당 시그니처의 시드들 민감도 조정
        signature_seeds = [
            seed_id
            for seed_id, seed in self.kernel.seed_registry.items()
            if seed.signature_alignment == action.target_signature
        ]

        delta = action.parameters.get("sensitivity_delta", 0.1)
        adjustment_type = action.parameters.get("adjustment_type", "increase")

        if adjustment_type == "decrease":
            delta = -delta

        adjusted_count = 0
        for seed_id in signature_seeds:
            seed = self.kernel.seed_registry[seed_id]
            new_sensitivity = max(0.0, min(1.0, seed.meta_sensitivity + delta))
            seed.meta_sensitivity = new_sensitivity
            adjusted_count += 1

        return adjusted_count > 0

    def _create_new_signature(self, action: LearningAction) -> bool:
        """새로운 시그니처 생성"""

        # 기존 시그니처 정보 복사 후 수정
        base_signature_id = action.parameters.get("base_signature")
        base_profile = self.signature_performance_reporter.generate_signature_profile(
            base_signature_id
        )

        if "error" in base_profile:
            return False

        # 새로운 시그니처 설정 생성
        new_signature_config = {
            "id": action.target_signature,
            "name": f"Adapted {base_profile.get('signature_id', 'Unknown')}",
            "primary_strategies": base_profile.get("primary_strategies", ["balanced"]),
            "emotional_triggers": base_profile.get("emotional_triggers", {}),
            "emotion_sensitivity": base_profile.get("emotion_sensitivity", 0.5),
            "meta_sensitivity": base_profile.get("meta_sensitivity_baseline", 0.5),
            "adaptation_notes": f"Created by adaptive learning for {action.parameters.get('adaptation_focus')}",
        }

        # 실제 시그니처 파일에 추가하는 로직은 여기에 구현
        # (현재는 시뮬레이션)
        print(f"New signature would be created: {action.target_signature}")
        return True

    def _apply_context_specialization(self, action: LearningAction) -> bool:
        """컨텍스트 특화 적용"""

        # 컨텍스트별 특화 규칙 적용
        specialization_area = action.parameters.get("specialization_area")
        context_rules = action.parameters.get("context_rules", {})

        # 해당 시그니처의 시드들에 특화 규칙 적용
        signature_seeds = [
            seed_id
            for seed_id, seed in self.kernel.seed_registry.items()
            if seed.signature_alignment == action.target_signature
        ]

        # 실제 특화 로직 적용 (예시)
        for seed_id in signature_seeds[:3]:
            seed = self.kernel.seed_registry[seed_id]
            # 컨텍스트에 따른 전략 조정
            if "emotion" in specialization_area:
                # 감정 관련 특화
                seed.emotion_rhythm.volatility_threshold *= 0.9
            elif "strategy" in specialization_area:
                # 전략 관련 특화
                seed.evolution_potential *= 1.1

        return True

    def _apply_fine_tuning(self, action: LearningAction) -> bool:
        """미세 조정 적용"""

        adjustment_magnitude = action.parameters.get("adjustment_magnitude", 0.05)
        target_metric = action.parameters.get("target_metric")

        # 해당 시그니처의 시드들에 미세 조정 적용
        signature_seeds = [
            seed_id
            for seed_id, seed in self.kernel.seed_registry.items()
            if seed.signature_alignment == action.target_signature
        ]

        for seed_id in signature_seeds:
            seed = self.kernel.seed_registry[seed_id]

            if "confidence" in target_metric:
                seed.meta_sensitivity += adjustment_magnitude
            elif "emotion" in target_metric:
                seed.emotion_rhythm.volatility_threshold += adjustment_magnitude
            elif "evolution" in target_metric:
                seed.evolution_potential += adjustment_magnitude

            # 값 범위 제한
            seed.meta_sensitivity = max(0.0, min(1.0, seed.meta_sensitivity))
            seed.emotion_rhythm.volatility_threshold = max(
                0.0, min(1.0, seed.emotion_rhythm.volatility_threshold)
            )
            seed.evolution_potential = max(0.0, min(1.0, seed.evolution_potential))

        return True

    def _calculate_success_rate(self, before: Dict, after: Dict) -> float:
        """적응 성공률 계산"""

        if "error" in before or "error" in after:
            return 0.0

        # 주요 메트릭들의 개선 정도 계산
        improvements = []

        for metric in ["success_rate", "avg_sensitivity", "avg_evolution_potential"]:
            if metric in before and metric in after:
                before_val = before[metric]
                after_val = after[metric]

                if before_val > 0:
                    improvement = (after_val - before_val) / before_val
                    improvements.append(improvement)

        if not improvements:
            return 0.0

        # 평균 개선률
        avg_improvement = sum(improvements) / len(improvements)

        # 0-1 범위로 정규화
        success_rate = max(0.0, min(1.0, 0.5 + avg_improvement))

        return round(success_rate, 3)

    def run_continuous_learning_cycle(self) -> Dict[str, Any]:
        """연속 학습 사이클 실행"""

        start_time = datetime.now()

        print("🧬 Adaptive Learning Cycle 시작")

        # 1. 실패 패턴 분석
        print("📊 실패 패턴 분석 중...")
        patterns = self.analyze_failure_patterns()
        print(f"감지된 패턴: {len(patterns)}개")

        if not patterns:
            return {
                "cycle_result": "no_patterns_detected",
                "timestamp": start_time.isoformat(),
                "duration_seconds": 0,
            }

        # 2. 학습 액션 생성
        print("🎯 학습 액션 생성 중...")
        actions = self.generate_learning_actions(patterns)
        print(f"생성된 액션: {len(actions)}개")

        # 3. 액션 실행
        print("⚡ 학습 액션 실행 중...")
        results = self.execute_learning_actions(actions)
        print(f"실행된 액션: {len(results)}개")

        # 4. 결과 분석
        successful_adaptations = len([r for r in results if r.success_rate > 0.5])
        avg_success_rate = (
            sum(r.success_rate for r in results) / len(results) if results else 0.0
        )

        duration = (datetime.now() - start_time).total_seconds()

        cycle_result = {
            "cycle_result": "completed",
            "patterns_detected": len(patterns),
            "actions_generated": len(actions),
            "actions_executed": len(results),
            "successful_adaptations": successful_adaptations,
            "average_success_rate": round(avg_success_rate, 3),
            "duration_seconds": round(duration, 2),
            "timestamp": start_time.isoformat(),
            "patterns_summary": [
                {
                    "pattern_id": p.pattern_id,
                    "failure_type": p.failure_type,
                    "signature": p.signature_id,
                    "severity": p.severity,
                    "frequency": p.frequency,
                }
                for p in patterns
            ],
            "adaptation_summary": [
                {
                    "adaptation_id": r.adaptation_id,
                    "target_signature": (
                        r.actions_taken[0].target_signature
                        if r.actions_taken
                        else "unknown"
                    ),
                    "success_rate": r.success_rate,
                }
                for r in results
            ],
        }

        print(f"✅ 학습 사이클 완료 - 성공률: {avg_success_rate:.1%}")

        return cycle_result

    def get_learning_summary(self) -> Dict[str, Any]:
        """학습 시스템 요약 정보"""

        return {
            "learning_engine_status": {
                "total_patterns_detected": len(self.failure_patterns),
                "total_adaptations": len(self.adaptation_results),
                "active_signatures": len(set(self.last_adaptation_time.keys())),
                "last_learning_cycle": (
                    max([r.timestamp for r in self.adaptation_results])
                    if self.adaptation_results
                    else "Never"
                ),
            },
            "performance_trends": {
                "recent_success_rates": [
                    r.success_rate for r in self.adaptation_results[-10:]
                ],
                "improvement_trend": self._calculate_improvement_trend(),
            },
            "configuration": {
                "failure_threshold": self.failure_threshold,
                "pattern_min_frequency": self.pattern_min_frequency,
                "learning_window_days": self.learning_window_days,
                "adaptation_cooldown_hours": self.adaptation_cooldown_hours,
            },
        }

    def _calculate_improvement_trend(self) -> str:
        """개선 트렌드 계산"""
        if len(self.adaptation_results) < 3:
            return "insufficient_data"

        recent_rates = [r.success_rate for r in self.adaptation_results[-5:]]
        early_rates = (
            [r.success_rate for r in self.adaptation_results[-10:-5]]
            if len(self.adaptation_results) >= 10
            else recent_rates
        )

        recent_avg = sum(recent_rates) / len(recent_rates)
        early_avg = sum(early_rates) / len(early_rates)

        if recent_avg > early_avg + 0.1:
            return "improving"
        elif recent_avg < early_avg - 0.1:
            return "declining"
        else:
            return "stable"


# Convenience functions
def run_adaptive_learning(kernel: EchoSeedKernel) -> Dict[str, Any]:
    """적응 학습 실행 편의 함수"""
    engine = AdaptiveLearningEngine(kernel)
    return engine.run_continuous_learning_cycle()


def get_learning_status(kernel: EchoSeedKernel) -> Dict[str, Any]:
    """학습 시스템 상태 조회 편의 함수"""
    engine = AdaptiveLearningEngine(kernel)
    return engine.get_learning_summary()


if __name__ == "__main__":
    # 테스트 코드
    from echo_engine.seed_kernel import get_echo_seed_kernel

    print("🧬 Adaptive Learning Engine 테스트")

    kernel = get_echo_seed_kernel("adaptive_test")

    # 테스트 시드 생성 및 실패 시뮬레이션
    for i in range(5):
        seed = kernel.generate_initial_state(
            signature_id=["Echo-Aurora", "Echo-Phoenix"][i % 2]
        )

        # 실패 시뮬레이션
        if i % 2 == 0:
            kernel.evolve_seed(
                seed.identity_trace.seed_id,
                {"reason": "low_confidence", "strength": 0.7},
            )

    # 적응 학습 실행
    engine = AdaptiveLearningEngine(kernel)

    print("\n📊 실패 패턴 분석:")
    patterns = engine.analyze_failure_patterns()
    print(f"감지된 패턴: {len(patterns)}개")

    for pattern in patterns:
        print(
            f"- {pattern.pattern_id}: {pattern.failure_type} (심각도: {pattern.severity:.2f})"
        )

    print("\n🎯 학습 액션 생성:")
    actions = engine.generate_learning_actions(patterns)
    print(f"생성된 액션: {len(actions)}개")

    for action in actions[:3]:  # 첫 3개만 출력
        print(
            f"- {action.action_id}: {action.action_type} (우선순위: {action.priority})"
        )

    print("\n🔄 연속 학습 사이클:")
    cycle_result = engine.run_continuous_learning_cycle()
    print(f"결과: {cycle_result['cycle_result']}")
    print(f"성공률: {cycle_result.get('average_success_rate', 0):.1%}")

    print("\n📈 학습 요약:")
    summary = engine.get_learning_summary()
    print(f"총 적응: {summary['learning_engine_status']['total_adaptations']}")
    print(f"개선 트렌드: {summary['performance_trends']['improvement_trend']}")

    print("✅ Adaptive Learning Engine 테스트 완료")
