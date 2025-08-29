# loop_meta_integrator.py - 루프 실행과 메타 로깅/강화학습 통합 모듈 (v2.0 Optimized)
# Loop Execution + Meta Logging + Reinforcement Learning Integration

import asyncio
from collections import deque
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from functools import lru_cache

try:
    import orjson as json
except ImportError:
    import json

from .loop_executor import LoopExecutor, LoopResult
from .signature_loop_bridge import SignatureLoopBridge
from echo_engine.meta_log_writer import get_meta_log_writer, log_evolution_event
from .qtable_rl import QLearningAgent
from .reinforcement_engine import ReinforcementEngine

# --- Shared Instances for Optimization ---
@lru_cache(maxsize=1)
def get_shared_loop_executor():
    return LoopExecutor()

@lru_cache(maxsize=1)
def get_shared_signature_bridge():
    return SignatureLoopBridge()

@lru_cache(maxsize=1)
def get_shared_q_agent():
    return QLearningAgent()

@lru_cache(maxsize=1)
def get_shared_reinforcement_engine():
    return ReinforcementEngine()

# -----------------------------------------

@dataclass
class LoopExecutionMetrics:
    loop_id: str
    signature_id: str
    execution_time: float
    success_rate: float
    confidence_score: float
    adaptation_score: float
    learning_feedback: Dict[str, Any]


class LoopMetaIntegrator:
    def __init__(self):
        self.loop_executor = get_shared_loop_executor()
        self.signature_bridge = get_shared_signature_bridge()
        self.meta_logger = get_meta_log_writer()
        self.q_agent = get_shared_q_agent()
        self.reinforcement_engine = get_shared_reinforcement_engine()
        self.execution_history = deque(maxlen=100)
        self._previous_state = None
        self._previous_action = None

    async def execute_integrated_loop(
        self,
        input_text: str,
        signature_id: str,
        context: Dict = None,
        learning_enabled: bool = True,
    ) -> Dict:
        """통합된 루프 실행 (메타 로깅 + 강화학습 포함) - 비동기 최적화"""
        start_time = datetime.now()
        context = context or {}

        # 1. 시그니처 기반 루프 선택 (비동기 가정)
        optimal_loop = await self.signature_bridge.determine_optimal_loop_async(
            signature_id, context
        )

        # 2. Q-Learning 기반 루프 추천
        selected_loop = optimal_loop
        selection_method = "signature_based"
        if learning_enabled:
            state = self._encode_state(input_text, signature_id, context)
            q_recommended_loop = self.q_agent.get_best_action(state)
            if q_recommended_loop and self.q_agent.get_q_value(state, q_recommended_loop) > 0.7:
                selected_loop = q_recommended_loop
                selection_method = "q_learning"

        # 3. 루프 실행 (비동기)
        loop_result = await self.loop_executor.execute_loop_async(
            selected_loop, context, signature_id=signature_id
        )

        # 4. 실행 메트릭 계산
        execution_time = (datetime.now() - start_time).total_seconds()
        metrics = self._calculate_metrics(
            selected_loop, signature_id, loop_result, execution_time
        )

        # 5. 메타 로깅 (비동기 I/O)
        await self._log_meta_data(input_text, selected_loop, selection_method, metrics, loop_result, context, execution_time)

        # 6. 강화학습 피드백 (비동기)
        if learning_enabled:
            await self._process_reinforcement_learning(state, selected_loop, loop_result, metrics, input_text, signature_id)

        # 7. 진화 이벤트 감지 및 로깅
        if self._should_trigger_evolution(metrics, loop_result):
            self._log_evolution_event(selected_loop, signature_id, metrics, loop_result)

        # 8. 실행 히스토리 업데이트
        self._update_execution_history(input_text, signature_id, selected_loop, selection_method, loop_result, metrics, context)

        # 9. 최종 결과 구성
        return self._build_final_result(input_text, signature_id, selected_loop, selection_method, loop_result, metrics, context, learning_enabled)

    async def _log_meta_data(self, input_text, loop_id, selection_method, metrics, loop_result, context, exec_time):
        """메타 데이터 비동기 로깅"""
        judgment_data = {
            "judgment_mode": f"loop_{loop_id}",
            "judgment": loop_result.output,
            "confidence": metrics.confidence_score,
            "emotion_detected": context.get("emotional_intensity", 0.5),
            "strategy_suggested": loop_id,
            "reasoning": f"Loop: {loop_id} → Phases: {' → '.join(loop_result.phases_executed)}",
            "processing_time": exec_time, "fallback_used": not loop_result.success,
            "loop_id": loop_id, "selection_method": selection_method,
        }
        meta_info = {"loop_execution": asdict(metrics), "signature_id": metrics.signature_id, "context": context}
        
        # orjson은 bytes를 반환하므로 디코딩 필요
        context_str = json.dumps(context)
        if isinstance(context_str, bytes):
            context_str = context_str.decode('utf-8')

        await self.meta_logger.log_judgment_async(input_text, judgment_data, context=context_str, meta_info=meta_info)

    async def _process_reinforcement_learning(self, state, action, loop_result, metrics, input_text, signature_id):
        """강화학습 피드백 처리"""
        reward = self._calculate_reward(loop_result, metrics)
        if self._previous_state and self._previous_action:
            self.q_agent.update_q_table(self._previous_state, self._previous_action, reward, state)
        self._previous_state, self._previous_action = state, action

        feedback_data = {"input_text": input_text, "loop_used": action, "success": loop_result.success,
                         "confidence": metrics.confidence_score, "signature_id": signature_id}
        await self.reinforcement_engine.process_feedback_async(feedback_data)

    def _log_evolution_event(self, loop_id, signature_id, metrics, loop_result):
        """진화 이벤트 로깅"""
        evolution_data = {
            "event": f"Loop adaptation triggered for {loop_id}",
            "tag": ["loop_evolution", "performance_optimization"],
            "cause": ["low_confidence", "execution_failure"] if not loop_result.success else ["optimization_opportunity"],
            "effect": ["loop_weight_adjustment", "signature_sensitivity_update"],
            "resolution": f"Adaptive learning for {signature_id}",
            "insight": f"Loop {loop_id} requires optimization",
            "adaptation_strength": 1.0 - metrics.confidence_score,
            "coherence_improvement": metrics.adaptation_score,
            "reflection_depth": len(loop_result.phases_executed),
        }
        log_evolution_event(evolution_data, signature_id)

    def _update_execution_history(self, input_text, signature_id, loop_id, selection_method, loop_result, metrics, context):
        """실행 히스토리 업데이트 (deque 사용)"""
        execution_record = {
            "timestamp": datetime.now().isoformat(), "input_text": input_text, "signature_id": signature_id,
            "selected_loop": loop_id, "selection_method": selection_method, "loop_result": loop_result,
            "metrics": metrics, "context": context,
        }
        self.execution_history.append(execution_record)

    def _build_final_result(self, input_text, signature_id, loop_id, selection_method, loop_result, metrics, context, learning_enabled):
        """최종 결과 객체 생성"""
        return {
            "input_text": input_text, "signature_id": signature_id, "selected_loop": loop_id,
            "selection_method": selection_method,
            "loop_result": {
                "success": loop_result.success, "phases_executed": loop_result.phases_executed,
                "output": loop_result.output, "execution_time": loop_result.execution_time,
                "error": loop_result.error_message,
            },
            "metrics": asdict(metrics), "context": context, "learning_applied": learning_enabled,
            "timestamp": datetime.now().isoformat(),
        }

    def _encode_state(self, input_text: str, signature_id: str, context: Dict) -> str:
        """상태를 Q-Learning용 문자열로 인코딩"""
        complexity = context.get("complexity", 0.5)
        uncertainty = context.get("uncertainty", 0.5)
        emotional_intensity = context.get("emotional_intensity", 0.5)
        complexity_level = "high" if complexity > 0.7 else "medium" if complexity > 0.3 else "low"
        uncertainty_level = "high" if uncertainty > 0.7 else "medium" if uncertainty > 0.3 else "low"
        emotion_level = "high" if emotional_intensity > 0.6 else "medium" if emotional_intensity > 0.3 else "low"
        return f"{signature_id}_{complexity_level}_{uncertainty_level}_{emotion_level}"

    def _calculate_metrics(self, loop_id: str, signature_id: str, loop_result: LoopResult, execution_time: float) -> LoopExecutionMetrics:
        """실행 메트릭 계산"""
        success_rate = 1.0 if loop_result.success else 0.0
        time_penalty = min(0.3, execution_time / 10.0)
        confidence_score = max(0.0, min(1.0, success_rate - time_penalty))
        loop_sensitivity = self.signature_bridge.get_loop_sensitivity(signature_id, loop_id)
        adaptation_score = loop_sensitivity * success_rate
        learning_feedback = {
            "execution_successful": loop_result.success, "phases_completed": len(loop_result.phases_executed),
            "time_efficiency": 1.0 - time_penalty, "signature_compatibility": loop_sensitivity,
        }
        return LoopExecutionMetrics(loop_id, signature_id, execution_time, success_rate, confidence_score, adaptation_score, learning_feedback)

    def _calculate_reward(self, loop_result: LoopResult, metrics: LoopExecutionMetrics) -> float:
        """강화학습용 보상 계산"""
        base_reward = 1.0 if loop_result.success else -0.5
        time_bonus = max(-0.3, min(0.3, (5.0 - loop_result.execution_time) / 10.0))
        confidence_bonus = metrics.confidence_score * 0.5
        adaptation_bonus = metrics.adaptation_score * 0.3
        total_reward = base_reward + time_bonus + confidence_bonus + adaptation_bonus
        return max(-1.0, min(1.0, total_reward))

    def _should_trigger_evolution(self, metrics: LoopExecutionMetrics, loop_result: LoopResult) -> bool:
        """진화 이벤트 트리거 조건 확인"""
        return not loop_result.success or metrics.confidence_score < 0.6 or metrics.adaptation_score < 0.5 or metrics.execution_time > 10.0

    def get_performance_summary(self) -> Dict:
        """성능 요약 통계"""
        if not self.execution_history:
            return {"message": "No execution history available"}
        
        recent_executions = list(self.execution_history)[-20:]
        loop_stats, signature_stats = {}, {}

        for record in recent_executions:
            loop_id, sig_id = record["selected_loop"], record["signature_id"]
            metrics = record["metrics"]
            loop_stats.setdefault(loop_id, {"count": 0, "success_rate": 0, "avg_confidence": 0})
            signature_stats.setdefault(sig_id, {"count": 0, "success_rate": 0, "avg_confidence": 0})
            
            loop_stats[loop_id]["count"] += 1
            loop_stats[loop_id]["success_rate"] += metrics.success_rate
            loop_stats[loop_id]["avg_confidence"] += metrics.confidence_score
            signature_stats[sig_id]["count"] += 1
            signature_stats[sig_id]["success_rate"] += metrics.success_rate
            signature_stats[sig_id]["avg_confidence"] += metrics.confidence_score

        for stats in (loop_stats, signature_stats):
            for key in stats:
                count = stats[key]["count"]
                stats[key]["success_rate"] /= count
                stats[key]["avg_confidence"] /= count
        
        return {
            "total_executions": len(self.execution_history), "recent_executions": len(recent_executions),
            "loop_performance": loop_stats, "signature_performance": signature_stats,
            "overall_success_rate": sum(r["metrics"].success_rate for r in recent_executions) / len(recent_executions),
            "overall_confidence": sum(r["metrics"].confidence_score for r in recent_executions) / len(recent_executions),
        }

# --- Global Integrator Instance ---
_integrator_instance = None
_integrator_lock = asyncio.Lock()

async def get_integrator() -> LoopMetaIntegrator:
    global _integrator_instance
    if _integrator_instance is None:
        async with _integrator_lock:
            if _integrator_instance is None:
                _integrator_instance = LoopMetaIntegrator()
    return _integrator_instance

async def execute_integrated_judgment(input_text: str, signature_id: str, context: Dict = None) -> Dict:
    integrator = await get_integrator()
    return await integrator.execute_integrated_loop(input_text, signature_id, context)

async def get_system_performance() -> Dict:
    integrator = await get_integrator()
    return integrator.get_performance_summary()

async def main_test():
    print("🔗 Loop Meta Integrator 테스트 (v2.0 Optimized)")
    test_input = "복잡한 상황에서의 감정적 결정이 필요합니다. 어떻게 접근해야 할까요?"
    test_signature = "Echo-Aurora"
    test_context = {"complexity": 0.8, "uncertainty": 0.6, "emotional_intensity": 0.7}

    result = await execute_integrated_judgment(test_input, test_signature, test_context)

    print(f"Selected Loop: {result['selected_loop']}")
    print(f"Selection Method: {result['selection_method']}")
    print(f"Success: {result['loop_result']['success']}")
    print(f"Confidence: {result['metrics']['confidence_score']:.2f}")
    print(f"Adaptation Score: {result['metrics']['adaptation_score']:.2f}")

    performance = await get_system_performance()
    print(f"System Performance: {performance}")
    print("✅ Loop Meta Integrator 테스트 완료")

if __name__ == "__main__":
    asyncio.run(main_test())
