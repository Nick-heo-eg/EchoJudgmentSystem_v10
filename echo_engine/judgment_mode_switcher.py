#!/usr/bin/env python3
"""
🎛️ EchoJudgmentSystem v10.5 - Judgment Mode Switcher
지능형 판단 모드 전환 시스템

이 모듈은 다음 기능을 제공합니다:
- 동적 모드 전환 (llm_free/claude/hybrid)
- 컨텍스트 기반 모드 선택
- 성능 기반 자동 전환
- 실시간 모드 모니터링 및 최적화
"""

import time
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque

# 공통 모듈 임포트
try:
    from .shared_judgment_logic import JudgmentMode, SharedJudgmentResult
except ImportError:
    from shared_judgment_logic import JudgmentMode, SharedJudgmentResult


class SwitchingTrigger(Enum):
    """모드 전환 트리거"""

    MANUAL = "manual"  # 수동 전환
    CONFIDENCE_BASED = "confidence"  # 신뢰도 기반
    PERFORMANCE_BASED = "performance"  # 성능 기반
    CONTEXT_BASED = "context"  # 컨텍스트 기반
    ERROR_RECOVERY = "error_recovery"  # 오류 복구
    LOAD_BALANCING = "load_balancing"  # 부하 분산
    COST_OPTIMIZATION = "cost_optimization"  # 비용 최적화


class SwitchingStrategy(Enum):
    """전환 전략"""

    CONSERVATIVE = "conservative"  # 보수적 (안정성 우선)
    AGGRESSIVE = "aggressive"  # 적극적 (성능 우선)
    BALANCED = "balanced"  # 균형 (안정성 + 성능)
    ADAPTIVE = "adaptive"  # 적응적 (학습 기반)


@dataclass
class ModePerformanceMetrics:
    """모드별 성능 지표"""

    mode: JudgmentMode
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    average_confidence: float = 0.0
    error_rate: float = 0.0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    recent_response_times: deque = field(default_factory=lambda: deque(maxlen=10))
    recent_confidences: deque = field(default_factory=lambda: deque(maxlen=10))


@dataclass
class SwitchingRule:
    """전환 규칙"""

    trigger: SwitchingTrigger
    condition: Dict[str, Any]
    target_mode: JudgmentMode
    priority: int = 5  # 1=highest, 10=lowest
    enabled: bool = True
    description: str = ""


@dataclass
class SwitchingDecision:
    """전환 결정"""

    from_mode: JudgmentMode
    to_mode: JudgmentMode
    trigger: SwitchingTrigger
    reason: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class JudgmentModeSwitcher:
    """지능형 판단 모드 전환기"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        모드 전환기 초기화

        Args:
            config: 전환기 설정
        """
        self.config = config or self._load_default_config()

        # 현재 모드
        self.current_mode = JudgmentMode(self.config.get("default_mode", "hybrid"))

        # 성능 지표 추적
        self.performance_metrics = {
            mode: ModePerformanceMetrics(mode) for mode in JudgmentMode
        }

        # 전환 규칙
        self.switching_rules = self._initialize_switching_rules()

        # 전환 히스토리
        self.switching_history = deque(maxlen=100)

        # 전환 전략
        self.switching_strategy = SwitchingStrategy(
            self.config.get("switching_strategy", "balanced")
        )

        # 통계
        self.stats = {
            "total_switches": 0,
            "manual_switches": 0,
            "auto_switches": 0,
            "switch_success_rate": 1.0,
            "modes_usage": defaultdict(int),
            "triggers_used": defaultdict(int),
        }

        # 모니터링
        self.monitoring_enabled = self.config.get("enable_monitoring", True)
        self.last_optimization = datetime.now()

        print(f"🎛️ 판단 모드 전환기 초기화 완료 (기본 모드: {self.current_mode.value})")

    def _load_default_config(self) -> Dict[str, Any]:
        """기본 설정 로드"""
        return {
            "default_mode": "hybrid",
            "switching_strategy": "balanced",
            "enable_monitoring": True,
            "confidence_thresholds": {"low": 0.3, "medium": 0.6, "high": 0.8},
            "performance_thresholds": {
                "max_error_rate": 0.15,
                "min_success_rate": 0.8,
                "max_response_time": 5.0,
            },
            "switching_cooldown": 30,  # seconds
            "optimization_interval": 300,  # seconds
            "enable_cost_optimization": False,
            "enable_load_balancing": True,
        }

    def _initialize_switching_rules(self) -> List[SwitchingRule]:
        """전환 규칙 초기화"""
        rules = []

        # 1. 신뢰도 기반 전환 규칙
        rules.append(
            SwitchingRule(
                trigger=SwitchingTrigger.CONFIDENCE_BASED,
                condition={"min_confidence": 0.8},
                target_mode=JudgmentMode.LLM_FREE,
                priority=1,
                description="높은 신뢰도 시 LLM-Free 사용",
            )
        )

        rules.append(
            SwitchingRule(
                trigger=SwitchingTrigger.CONFIDENCE_BASED,
                condition={"max_confidence": 0.3},
                target_mode=JudgmentMode.CLAUDE,
                priority=2,
                description="낮은 신뢰도 시 Claude 사용",
            )
        )

        # 2. 성능 기반 전환 규칙
        rules.append(
            SwitchingRule(
                trigger=SwitchingTrigger.PERFORMANCE_BASED,
                condition={"max_error_rate": 0.15},
                target_mode=JudgmentMode.HYBRID,
                priority=3,
                description="오류율 높을 시 하이브리드 사용",
            )
        )

        # 3. 컨텍스트 기반 전환 규칙
        rules.append(
            SwitchingRule(
                trigger=SwitchingTrigger.CONTEXT_BASED,
                condition={"context_types": ["complex", "creative"]},
                target_mode=JudgmentMode.CLAUDE,
                priority=4,
                description="복잡한 컨텍스트 시 Claude 사용",
            )
        )

        rules.append(
            SwitchingRule(
                trigger=SwitchingTrigger.CONTEXT_BASED,
                condition={"context_types": ["simple", "routine"]},
                target_mode=JudgmentMode.LLM_FREE,
                priority=4,
                description="단순한 컨텍스트 시 LLM-Free 사용",
            )
        )

        # 4. 오류 복구 규칙
        rules.append(
            SwitchingRule(
                trigger=SwitchingTrigger.ERROR_RECOVERY,
                condition={"consecutive_failures": 3},
                target_mode=JudgmentMode.HYBRID,
                priority=1,
                description="연속 실패 시 하이브리드로 복구",
            )
        )

        return rules

    def get_current_mode(self) -> JudgmentMode:
        """현재 모드 반환"""
        return self.current_mode

    def switch_mode(
        self,
        target_mode: JudgmentMode,
        trigger: SwitchingTrigger = SwitchingTrigger.MANUAL,
        reason: str = "Manual switch",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        모드 전환 실행

        Args:
            target_mode: 대상 모드
            trigger: 전환 트리거
            reason: 전환 이유
            metadata: 추가 메타데이터

        Returns:
            전환 성공 여부
        """
        if target_mode == self.current_mode:
            return True  # 이미 해당 모드

        # 쿨다운 체크
        if not self._check_switching_cooldown():
            return False

        # 전환 실행
        previous_mode = self.current_mode

        try:
            # 전환 결정 기록
            decision = SwitchingDecision(
                from_mode=previous_mode,
                to_mode=target_mode,
                trigger=trigger,
                reason=reason,
                confidence=1.0,  # 수동 전환은 100% 신뢰도
                metadata=metadata or {},
            )

            # 모드 변경
            self.current_mode = target_mode

            # 히스토리 업데이트
            self.switching_history.append(decision)

            # 통계 업데이트
            self.stats["total_switches"] += 1
            if trigger == SwitchingTrigger.MANUAL:
                self.stats["manual_switches"] += 1
            else:
                self.stats["auto_switches"] += 1

            self.stats["modes_usage"][target_mode.value] += 1
            self.stats["triggers_used"][trigger.value] += 1

            print(
                f"🎛️ 모드 전환: {previous_mode.value} → {target_mode.value} ({reason})"
            )

            return True

        except Exception as e:
            print(f"❌ 모드 전환 실패: {e}")
            return False

    def auto_switch_mode(self, context: Dict[str, Any]) -> Optional[SwitchingDecision]:
        """
        자동 모드 전환 평가 및 실행

        Args:
            context: 판단 컨텍스트 (텍스트, 신뢰도, 성능 등)

        Returns:
            전환 결정 (전환된 경우) 또는 None
        """
        # 전환 규칙 평가
        best_rule = self._evaluate_switching_rules(context)

        if not best_rule:
            return None

        # 전환 실행
        success = self.switch_mode(
            target_mode=best_rule.target_mode,
            trigger=best_rule.trigger,
            reason=best_rule.description,
            metadata={"rule_priority": best_rule.priority, "context": context},
        )

        if success:
            return self.switching_history[-1]

        return None

    def _evaluate_switching_rules(
        self, context: Dict[str, Any]
    ) -> Optional[SwitchingRule]:
        """전환 규칙 평가"""
        applicable_rules = []

        for rule in self.switching_rules:
            if not rule.enabled:
                continue

            if self._check_rule_condition(rule, context):
                applicable_rules.append(rule)

        if not applicable_rules:
            return None

        # 우선순위 기준으로 정렬 (낮은 숫자가 높은 우선순위)
        applicable_rules.sort(key=lambda r: r.priority)

        return applicable_rules[0]

    def _check_rule_condition(
        self, rule: SwitchingRule, context: Dict[str, Any]
    ) -> bool:
        """규칙 조건 확인"""
        try:
            if rule.trigger == SwitchingTrigger.CONFIDENCE_BASED:
                confidence = context.get("confidence", 0.5)
                if "min_confidence" in rule.condition:
                    return confidence >= rule.condition["min_confidence"]
                if "max_confidence" in rule.condition:
                    return confidence <= rule.condition["max_confidence"]

            elif rule.trigger == SwitchingTrigger.PERFORMANCE_BASED:
                current_metrics = self.performance_metrics[self.current_mode]
                if "max_error_rate" in rule.condition:
                    return (
                        current_metrics.error_rate >= rule.condition["max_error_rate"]
                    )
                if "min_success_rate" in rule.condition:
                    success_rate = current_metrics.successful_requests / max(
                        current_metrics.total_requests, 1
                    )
                    return success_rate <= rule.condition["min_success_rate"]
                if "max_response_time" in rule.condition:
                    return (
                        current_metrics.average_response_time
                        >= rule.condition["max_response_time"]
                    )

            elif rule.trigger == SwitchingTrigger.CONTEXT_BASED:
                context_type = context.get("context_type", "general")
                if "context_types" in rule.condition:
                    return context_type in rule.condition["context_types"]

            elif rule.trigger == SwitchingTrigger.ERROR_RECOVERY:
                if "consecutive_failures" in rule.condition:
                    recent_failures = self._count_recent_failures()
                    return recent_failures >= rule.condition["consecutive_failures"]

            return False

        except Exception as e:
            print(f"⚠️ 규칙 조건 확인 실패: {e}")
            return False

    def record_judgment_result(self, mode: JudgmentMode, result: Dict[str, Any]):
        """판단 결과 기록 및 성능 지표 업데이트"""
        metrics = self.performance_metrics[mode]

        # 기본 통계 업데이트
        metrics.total_requests += 1

        # 성공/실패 판단
        is_success = not result.get("error_occurred", False)
        confidence = result.get("confidence", 0.0)
        processing_time = result.get("processing_time", 0.0)

        if is_success:
            metrics.successful_requests += 1
            metrics.last_success_time = datetime.now()
        else:
            metrics.failed_requests += 1
            metrics.last_failure_time = datetime.now()

        # 오류율 계산
        metrics.error_rate = metrics.failed_requests / metrics.total_requests

        # 평균 응답 시간 업데이트
        metrics.recent_response_times.append(processing_time)
        metrics.average_response_time = sum(metrics.recent_response_times) / len(
            metrics.recent_response_times
        )

        # 평균 신뢰도 업데이트
        metrics.recent_confidences.append(confidence)
        metrics.average_confidence = sum(metrics.recent_confidences) / len(
            metrics.recent_confidences
        )

        # 자동 최적화 체크
        if self.monitoring_enabled:
            self._check_auto_optimization()

    def _check_switching_cooldown(self) -> bool:
        """전환 쿨다운 체크"""
        if not self.switching_history:
            return True

        last_switch = self.switching_history[-1]
        cooldown_seconds = self.config.get("switching_cooldown", 30)

        time_since_last = (datetime.now() - last_switch.timestamp).total_seconds()
        return time_since_last >= cooldown_seconds

    def _count_recent_failures(self, window_minutes: int = 5) -> int:
        """최근 실패 횟수 계산"""
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)

        failure_count = 0
        for metrics in self.performance_metrics.values():
            if metrics.last_failure_time and metrics.last_failure_time > cutoff_time:
                failure_count += 1

        return failure_count

    def _check_auto_optimization(self):
        """자동 최적화 체크"""
        optimization_interval = self.config.get("optimization_interval", 300)

        time_since_last = (datetime.now() - self.last_optimization).total_seconds()

        if time_since_last >= optimization_interval:
            self._optimize_switching_strategy()
            self.last_optimization = datetime.now()

    def _optimize_switching_strategy(self):
        """전환 전략 최적화"""
        print("🔧 전환 전략 최적화 실행")

        # 모드별 성능 분석
        best_mode = None
        best_score = -1

        for mode, metrics in self.performance_metrics.items():
            if metrics.total_requests == 0:
                continue

            # 성능 점수 계산 (성공률 + 신뢰도 - 응답시간 패널티)
            success_rate = metrics.successful_requests / metrics.total_requests
            confidence_score = metrics.average_confidence
            time_penalty = min(
                metrics.average_response_time / 10.0, 0.5
            )  # 최대 0.5 패널티

            score = success_rate * 0.4 + confidence_score * 0.4 - time_penalty * 0.2

            if score > best_score:
                best_score = score
                best_mode = mode

        # 성능이 좋은 모드로 자동 전환 (조건부)
        if (
            best_mode and best_mode != self.current_mode and best_score > 0.7
        ):  # 최소 성능 임계값

            self.switch_mode(
                target_mode=best_mode,
                trigger=SwitchingTrigger.PERFORMANCE_BASED,
                reason=f"성능 최적화 (점수: {best_score:.3f})",
            )

    def get_mode_recommendation(
        self, context: Dict[str, Any]
    ) -> Tuple[JudgmentMode, float, str]:
        """
        모드 추천

        Args:
            context: 판단 컨텍스트

        Returns:
            (추천 모드, 신뢰도, 이유)
        """
        scores = {}

        for mode in JudgmentMode:
            score = self._calculate_mode_score(mode, context)
            scores[mode] = score

        # 최고 점수 모드 선택
        best_mode = max(scores, key=scores.get)
        best_score = scores[best_mode]

        # 추천 이유 생성
        reason = self._generate_recommendation_reason(best_mode, context, scores)

        return best_mode, best_score, reason

    def _calculate_mode_score(
        self, mode: JudgmentMode, context: Dict[str, Any]
    ) -> float:
        """모드별 점수 계산"""
        metrics = self.performance_metrics[mode]

        # 기본 성능 점수
        if metrics.total_requests > 0:
            success_rate = metrics.successful_requests / metrics.total_requests
            confidence_avg = metrics.average_confidence
            time_factor = max(0, 1 - metrics.average_response_time / 10.0)
        else:
            success_rate = 0.5  # 기본값
            confidence_avg = 0.5
            time_factor = 0.8

        base_score = success_rate * 0.4 + confidence_avg * 0.3 + time_factor * 0.3

        # 컨텍스트 적합성 보정
        context_bonus = self._calculate_context_fitness(mode, context)

        # 현재 모드 보너스 (안정성 위해)
        current_mode_bonus = 0.1 if mode == self.current_mode else 0

        final_score = base_score + context_bonus + current_mode_bonus

        return max(0, min(1, final_score))

    def _calculate_context_fitness(
        self, mode: JudgmentMode, context: Dict[str, Any]
    ) -> float:
        """컨텍스트 적합성 계산"""
        context_type = context.get("context_type", "general")
        complexity = context.get("complexity", "medium")
        confidence = context.get("confidence", 0.5)

        # 모드별 적합성 매트릭스
        fitness_matrix = {
            JudgmentMode.LLM_FREE: {
                "simple": 0.3,
                "routine": 0.3,
                "personal": 0.2,
                "low_complexity": 0.2,
                "high_confidence": 0.3,
            },
            JudgmentMode.CLAUDE: {
                "complex": 0.3,
                "creative": 0.3,
                "analytical": 0.2,
                "high_complexity": 0.3,
                "low_confidence": 0.2,
            },
            JudgmentMode.HYBRID: {
                "general": 0.2,
                "medium_complexity": 0.2,
                "medium_confidence": 0.1,
            },
        }

        fitness = fitness_matrix.get(mode, {})
        bonus = 0

        # 컨텍스트 타입 보너스
        bonus += fitness.get(context_type, 0)

        # 복잡도 보너스
        if complexity == "low":
            bonus += fitness.get("low_complexity", 0)
        elif complexity == "high":
            bonus += fitness.get("high_complexity", 0)
        else:
            bonus += fitness.get("medium_complexity", 0)

        # 신뢰도 보너스
        if confidence < 0.4:
            bonus += fitness.get("low_confidence", 0)
        elif confidence > 0.7:
            bonus += fitness.get("high_confidence", 0)
        else:
            bonus += fitness.get("medium_confidence", 0)

        return bonus

    def _generate_recommendation_reason(
        self,
        mode: JudgmentMode,
        context: Dict[str, Any],
        scores: Dict[JudgmentMode, float],
    ) -> str:
        """추천 이유 생성"""
        best_score = scores[mode]
        context_type = context.get("context_type", "general")
        confidence = context.get("confidence", 0.5)

        if mode == JudgmentMode.LLM_FREE:
            return f"LLM-Free 추천 (점수: {best_score:.3f}) - 빠른 응답과 안정성"
        elif mode == JudgmentMode.CLAUDE:
            return f"Claude 추천 (점수: {best_score:.3f}) - 복잡한 분석과 높은 품질"
        else:
            return f"Hybrid 추천 (점수: {best_score:.3f}) - 균형잡힌 성능과 신뢰성"

    def get_switching_stats(self) -> Dict[str, Any]:
        """전환 통계 반환"""
        return {
            "current_mode": self.current_mode.value,
            "switching_strategy": self.switching_strategy.value,
            "total_switches": self.stats["total_switches"],
            "manual_switches": self.stats["manual_switches"],
            "auto_switches": self.stats["auto_switches"],
            "modes_usage": dict(self.stats["modes_usage"]),
            "triggers_used": dict(self.stats["triggers_used"]),
            "performance_metrics": {
                mode.value: {
                    "total_requests": metrics.total_requests,
                    "success_rate": metrics.successful_requests
                    / max(metrics.total_requests, 1),
                    "error_rate": metrics.error_rate,
                    "average_confidence": metrics.average_confidence,
                    "average_response_time": metrics.average_response_time,
                }
                for mode, metrics in self.performance_metrics.items()
            },
            "recent_switches": [
                {
                    "from": decision.from_mode.value,
                    "to": decision.to_mode.value,
                    "trigger": decision.trigger.value,
                    "reason": decision.reason,
                    "timestamp": decision.timestamp.isoformat(),
                }
                for decision in list(self.switching_history)[-5:]  # 최근 5개
            ],
        }

    def export_config(self, file_path: str):
        """설정 내보내기"""
        export_data = {
            "config": self.config,
            "switching_rules": [
                {
                    "trigger": rule.trigger.value,
                    "condition": rule.condition,
                    "target_mode": rule.target_mode.value,
                    "priority": rule.priority,
                    "enabled": rule.enabled,
                    "description": rule.description,
                }
                for rule in self.switching_rules
            ],
            "current_mode": self.current_mode.value,
            "switching_strategy": self.switching_strategy.value,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"📁 모드 전환기 설정 내보내기 완료: {file_path}")


# 편의 함수들
_global_switcher = None


def get_mode_switcher(config: Optional[Dict[str, Any]] = None) -> JudgmentModeSwitcher:
    """전역 모드 전환기 인스턴스 반환 (싱글톤)"""
    global _global_switcher
    if _global_switcher is None:
        _global_switcher = JudgmentModeSwitcher(config)
    return _global_switcher


def switch_judgment_mode(
    target_mode: JudgmentMode, reason: str = "Manual switch"
) -> bool:
    """판단 모드 전환 (편의 함수)"""
    switcher = get_mode_switcher()
    return switcher.switch_mode(target_mode, SwitchingTrigger.MANUAL, reason)


def get_current_judgment_mode() -> JudgmentMode:
    """현재 판단 모드 반환"""
    switcher = get_mode_switcher()
    return switcher.get_current_mode()


def auto_optimize_judgment_mode(context: Dict[str, Any]) -> Optional[SwitchingDecision]:
    """자동 모드 최적화"""
    switcher = get_mode_switcher()
    return switcher.auto_switch_mode(context)


if __name__ == "__main__":
    # 테스트 코드
    print("🎛️ 판단 모드 전환기 테스트")
    print("=" * 50)

    # 전환기 생성
    switcher = JudgmentModeSwitcher()

    # 테스트 시나리오들
    test_scenarios = [
        {
            "name": "높은 신뢰도 상황",
            "context": {
                "confidence": 0.9,
                "context_type": "simple",
                "complexity": "low",
            },
        },
        {
            "name": "낮은 신뢰도 상황",
            "context": {
                "confidence": 0.2,
                "context_type": "complex",
                "complexity": "high",
            },
        },
        {
            "name": "중간 복잡도 상황",
            "context": {
                "confidence": 0.6,
                "context_type": "general",
                "complexity": "medium",
            },
        },
    ]

    for scenario in test_scenarios:
        print(f"\n=== {scenario['name']} ===")
        context = scenario["context"]

        # 모드 추천
        recommended_mode, score, reason = switcher.get_mode_recommendation(context)
        print(f"추천 모드: {recommended_mode.value} (점수: {score:.3f})")
        print(f"이유: {reason}")

        # 자동 전환 시도
        decision = switcher.auto_switch_mode(context)
        if decision:
            print(f"자동 전환: {decision.from_mode.value} → {decision.to_mode.value}")

        # 성능 시뮬레이션
        result = {
            "confidence": context["confidence"],
            "processing_time": 0.5,
            "error_occurred": False,
        }
        switcher.record_judgment_result(switcher.current_mode, result)

    # 최종 통계
    print(f"\n📊 전환 통계:")
    stats = switcher.get_switching_stats()
    print(f"현재 모드: {stats['current_mode']}")
    print(f"총 전환 횟수: {stats['total_switches']}")
    print(f"모드별 사용량: {stats['modes_usage']}")
