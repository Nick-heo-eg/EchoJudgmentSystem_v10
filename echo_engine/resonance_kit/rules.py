"""
Rules Engine: 동적 에이전트 라우팅 및 실행 규칙 관리
- 메트릭 기반 조건 평가
- 동적 에이전트 재실행 및 시그니처 변경 추천
- 무한 루프 방지 및 안전성 체크
"""

from typing import Dict, List, Any, Callable, Optional
import operator as op
from datetime import datetime


class Router:
    """동적 라우팅 규칙 엔진"""

    def __init__(self, routing_config: Dict[str, Any]):
        self.rules = routing_config.get("rules", [])

        # 연산자 매핑
        self.operators: Dict[str, Callable[[float, float], bool]] = {
            "<": op.lt,
            "<=": op.le,
            ">": op.gt,
            ">=": op.ge,
            "==": op.eq,
            "!=": op.ne,
        }

        # 실행 히스토리 (무한 루프 방지)
        self.execution_history: List[Dict[str, Any]] = []
        self.max_history = 20

        # 액션별 기본 파라미터
        self.default_action_params = {
            "repeat_agent": {
                "max_repeats": 2,
                "improvement_threshold": 0.05,
                "timeout_seconds": 30,
            },
            "escalate_signature_rewrite": {
                "style": "supportive-adjust",
                "intensity": "medium",
                "preserve_context": True,
            },
            "suggest_signature_switch": {
                "preferred_category": "empathetic",
                "switch_confidence": 0.7,
                "reason": "metrics below threshold",
            },
        }

    def decide(self, metrics: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """라우팅 결정"""
        for rule in self.rules:
            condition = rule.get("when", {})
            action_config = rule.get("then", {})

            if self._evaluate_condition(condition, metrics):
                # 안전성 체크
                if self._is_action_safe(action_config, metrics):
                    enhanced_action = self._enhance_action_params(
                        action_config, metrics
                    )
                    self._update_execution_history(enhanced_action, metrics)
                    return enhanced_action

        return None

    def _evaluate_condition(
        self, condition: Dict[str, Any], metrics: Dict[str, float]
    ) -> bool:
        """조건 평가"""
        if not condition:
            return False

        metric_name = condition.get("metric")
        op_str = condition.get("op")
        threshold_value = condition.get("value")

        if not all([metric_name, op_str, threshold_value is not None]):
            return False

        # 메트릭 값 가져오기
        current_value = metrics.get(metric_name)
        if current_value is None:
            return False

        # 연산자 함수 가져오기
        op_func = self.operators.get(op_str)
        if not op_func:
            return False

        # 조건 평가
        try:
            result = op_func(current_value, threshold_value)
            return bool(result)
        except (TypeError, ValueError):
            return False

    def _is_action_safe(
        self, action_config: Dict[str, Any], metrics: Dict[str, float]
    ) -> bool:
        """액션 안전성 체크 (무한 루프 방지)"""
        action = action_config.get("action")

        # 최근 동일 액션 실행 횟수 체크
        recent_actions = [entry["action"] for entry in self.execution_history[-5:]]
        same_action_count = recent_actions.count(action)

        # 액션별 최대 반복 제한
        max_repeats = {
            "repeat_agent": 3,
            "escalate_signature_rewrite": 2,
            "suggest_signature_switch": 1,
            "skip_agent": 5,
        }

        if same_action_count >= max_repeats.get(action, 2):
            return False

        # repeat_agent의 경우 개선도 체크
        if action == "repeat_agent":
            return self._is_repeat_worthwhile(action_config, metrics)

        return True

    def _is_repeat_worthwhile(
        self, action_config: Dict[str, Any], metrics: Dict[str, float]
    ) -> bool:
        """에이전트 반복 실행이 가치있는지 판단"""
        target_agent = action_config.get("params", {}).get("agent")

        # 해당 에이전트의 최근 성과 히스토리 확인
        agent_history = [
            entry
            for entry in self.execution_history
            if entry.get("target_agent") == target_agent
        ]

        if len(agent_history) >= 2:
            # 최근 실행에서 개선이 있었는지 확인
            recent_improvement = self._calculate_recent_improvement(
                agent_history, metrics
            )
            if recent_improvement < 0.05:  # 5% 미만 개선은 반복 가치 낮음
                return False

        return True

    def _calculate_recent_improvement(
        self, agent_history: List[Dict], current_metrics: Dict[str, float]
    ) -> float:
        """최근 개선도 계산"""
        if len(agent_history) < 1:
            return 0.0

        # 마지막 실행 시점의 메트릭과 현재 메트릭 비교
        last_execution = agent_history[-1]
        previous_metrics = last_execution.get("metrics_snapshot", {})

        # 주요 메트릭들의 개선도 계산
        key_metrics = ["resonance", "trust", "flow", "empathy_resonance"]
        improvements = []

        for metric in key_metrics:
            prev_val = previous_metrics.get(metric, 0.0)
            curr_val = current_metrics.get(metric, 0.0)
            if prev_val > 0:
                improvement = (curr_val - prev_val) / prev_val
                improvements.append(improvement)

        return sum(improvements) / len(improvements) if improvements else 0.0

    def _update_execution_history(
        self, action_config: Dict[str, Any], metrics: Dict[str, float]
    ):
        """실행 히스토리 업데이트"""
        history_entry = {
            "action": action_config.get("action"),
            "target_agent": action_config.get("params", {}).get("agent"),
            "metrics_snapshot": metrics.copy(),
            "timestamp": self._get_timestamp(),
        }

        self.execution_history.append(history_entry)

        # 히스토리 크기 제한
        if len(self.execution_history) > self.max_history:
            self.execution_history = self.execution_history[-self.max_history :]

    def _enhance_action_params(
        self, action_config: Dict[str, Any], metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """액션 파라미터 보강"""
        action = action_config.get("action")
        params = action_config.get("params", {}).copy()

        # 기본 파라미터 적용
        default_params = self.default_action_params.get(action, {})
        for key, value in default_params.items():
            if key not in params:
                params[key] = value

        # 상황별 파라미터 동적 조정
        if action == "repeat_agent":
            params = self._enhance_repeat_agent_params(params, metrics)
        elif action == "escalate_signature_rewrite":
            params = self._enhance_escalate_params(params, metrics)
        elif action == "suggest_signature_switch":
            params = self._enhance_switch_params(params, metrics)

        return {
            "action": action,
            "params": params,
            "routing_context": {
                "trigger_metrics": {
                    k: v for k, v in metrics.items() if v < 0.5
                },  # 문제 메트릭만
                "execution_count": len(self.execution_history),
            },
        }

    def _enhance_repeat_agent_params(
        self, params: Dict[str, Any], metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """repeat_agent 파라미터 보강"""
        # 메트릭 상태에 따른 반복 강도 조정
        resonance = metrics.get("resonance", 0.0)
        empathy = metrics.get("empathy_resonance", 0.0)
        trust = metrics.get("trust", 0.0)

        # 가장 문제가 되는 영역 식별
        if resonance < 0.3:
            params["focus_area"] = "resonance_building"
            params["intensity"] = "high"
        elif empathy < 0.4:
            params["focus_area"] = "empathy_strengthening"
            params["intensity"] = "medium"
        elif trust < 0.4:
            params["focus_area"] = "trust_recovery"
            params["intensity"] = "gentle"

        # 반복 횟수 동적 조정
        avg_score = (resonance + empathy + trust) / 3
        if avg_score < 0.3:
            params["max_repeats"] = 3
        elif avg_score < 0.5:
            params["max_repeats"] = 2
        else:
            params["max_repeats"] = 1

        return params

    def _enhance_escalate_params(
        self, params: Dict[str, Any], metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """escalate_signature_rewrite 파라미터 보강"""
        trust = metrics.get("trust", 0.0)
        emotional_safety = metrics.get("emotional_safety", 0.0)
        resonance = metrics.get("resonance", 0.0)

        # 상황에 따른 스타일 결정
        if emotional_safety < 0.3:
            params["style"] = "whisper-comfort"  # 매우 부드럽고 안전한 접근
        elif trust < 0.3:
            params["style"] = "gentle-rebuild"  # 신뢰 재구축 중심
        elif resonance < 0.3:
            params["style"] = "warm-reconnect"  # 따뜻한 재연결
        else:
            params["style"] = "supportive-adjust"  # 지지적 조정

        # 에스컬레이션 강도 조정
        avg_problem_severity = 1.0 - ((trust + emotional_safety + resonance) / 3)
        if avg_problem_severity > 0.7:
            params["intensity"] = "high"
        elif avg_problem_severity > 0.5:
            params["intensity"] = "medium"
        else:
            params["intensity"] = "low"

        return params

    def _enhance_switch_params(
        self, params: Dict[str, Any], metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """suggest_signature_switch 파라미터 보강"""
        # 현재 상황에 가장 적합한 시그니처 타입 제안
        empathy_need = 1.0 - metrics.get("empathy_resonance", 0.5)
        trust_need = 1.0 - metrics.get("trust", 0.5)
        flow_need = 1.0 - metrics.get("flow", 0.5)

        # 필요도에 따른 시그니처 카테고리 우선순위
        if empathy_need > 0.6:
            params["preferred_category"] = "empathetic"  # Selene, Aurora, Companion
            params["reason"] = "high empathy support needed"
        elif trust_need > 0.6:
            params["preferred_category"] = "trustworthy"  # Heo, Sage
            params["reason"] = "trust rebuilding required"
        elif flow_need > 0.6:
            params["preferred_category"] = "flow_enhancer"  # Aurora, Lune
            params["reason"] = "collaboration flow improvement needed"

        # 스위치 확신도 계산
        problem_severity = max(empathy_need, trust_need, flow_need)
        params["switch_confidence"] = min(1.0, problem_severity * 1.2)

        return params

    def _get_timestamp(self) -> str:
        """타임스탬프 생성"""
        return datetime.now().isoformat()

    def get_execution_summary(self) -> Dict[str, Any]:
        """실행 요약 정보"""
        if not self.execution_history:
            return {"total_executions": 0, "action_counts": {}, "recent_actions": []}

        # 액션별 실행 횟수
        action_counts = {}
        for entry in self.execution_history:
            action = entry.get("action")
            action_counts[action] = action_counts.get(action, 0) + 1

        # 최근 액션들
        recent_actions = [
            {
                "action": entry.get("action"),
                "target_agent": entry.get("target_agent"),
                "timestamp": entry.get("timestamp"),
            }
            for entry in self.execution_history[-5:]
        ]

        return {
            "total_executions": len(self.execution_history),
            "action_counts": action_counts,
            "recent_actions": recent_actions,
            "most_common_action": (
                max(action_counts.items(), key=lambda x: x[1])[0]
                if action_counts
                else None
            ),
        }

    def reset_history(self):
        """실행 히스토리 리셋"""
        self.execution_history = []

    def add_custom_rule(self, condition: Dict[str, Any], action: Dict[str, Any]):
        """커스텀 규칙 추가"""
        new_rule = {"when": condition, "then": action}
        self.rules.append(new_rule)

    def get_applicable_rules(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """현재 메트릭에 적용 가능한 모든 규칙 반환"""
        applicable = []

        for i, rule in enumerate(self.rules):
            if self._evaluate_condition(rule.get("when", {}), metrics):
                applicable.append(
                    {
                        "rule_index": i,
                        "condition": rule.get("when"),
                        "action": rule.get("then"),
                        "would_execute": self._is_action_safe(
                            rule.get("then", {}), metrics
                        ),
                    }
                )

        return applicable
