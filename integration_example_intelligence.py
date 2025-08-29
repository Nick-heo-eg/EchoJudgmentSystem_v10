"""
Intelligence Integration Example - How to integrate thin adapters into judgment loop
==================================================================================

This example shows how to integrate the new thin intelligence adapters
into the existing Echo judgment/reasoning flow.
"""

import time
from echo_engine.plan.goal_planner_v2 import GoalPlannerV2
from echo_engine.verify.result_verifier import ResultVerifier
from echo_engine.verify.evidence_binder import EvidenceBinder
from echo_engine.reflect.reflection_logger import ReflectionLogger
from echo_engine.reflect.pattern_memory import PatternMemory
from echo_engine.utils.intent_router_v2 import IntentRouterV2

# NEW: Import thin intelligence adapters
from echo_engine.intelligence.intelligence_evaluator import MultiDimensionalIntelligenceEvaluator
from echo_engine.intelligence.evolution_adapter import EvolutionAdapter


def enhanced_judgment_loop(user_query: str, session_context: dict) -> dict:
    """
    Enhanced judgment loop with intelligence measurement and evolution.

    This shows integration points where the thin adapters plug into
    the existing Plan -> Verify -> Reflect pipeline.
    """

    # === Initialize existing components ===
    planner = GoalPlannerV2(schema_path="echo_engine/schemas/plan_schema.yaml")
    router = IntentRouterV2()
    verifier = ResultVerifier()
    binder = EvidenceBinder()
    reflect = ReflectionLogger(store_dir="data/reflections/")
    patterns = PatternMemory(store_file="data/pattern_memory/capsules.json")

    # === NEW: Initialize intelligence components ===
    evaluator = IntelligenceEvaluator(verifier)  # Reuses existing verifier
    evo_adapter = EvolutionAdapter(patterns)  # Reuses existing pattern memory

    # === PLAN Phase ===
    start_time = time.time()

    intent = {
        "id": f"enhanced-run-{int(time.time())}",
        "title": "Answer user query with intelligence tracking",
        "topic": user_query,
    }

    plan = planner.create_plan(intent)
    plan = planner.expand_subplans(plan)

    # Route intent
    routing = router.route(user_query)

    # === EXECUTE Phase (mock execution for example) ===
    # In real system, this would execute the plan
    answer_text = f"This is a comprehensive answer to: {user_query}"
    evidence_list = [
        {
            "title": "Example Source",
            "url": "example.com",
            "content": "Supporting evidence",
        }
    ]

    tool_calls_used = len(plan.get("children", [])) + 1  # Plan steps + routing
    execution_time = time.time() - start_time

    # === VERIFY Phase ===
    scores = verifier.verify(answer_text, evidence_list)
    package = binder.bind(answer_text, evidence_list)

    # === NEW: INTELLIGENCE EVALUATION ===
    exec_meta = {
        "plan_nodes": len(plan.get("children", [])),
        "tool_calls": tool_calls_used,
        "latency_ms": int(execution_time * 1000),
    }

    # Get enhanced intelligence metrics
    intelligence_metrics = evaluator.evaluate(answer_text, evidence_list, exec_meta)

    # === REFLECT Phase (Enhanced) ===
    success = scores["aggregate"] >= 0.7

    # Enhanced reflection with intelligence metrics
    reflect.log(
        run_id=intent["id"],
        success=success,
        reason="enhanced_auto_evaluation",
        verifier_scores=scores,
        tags={
            "iq_like": intelligence_metrics["iq_like"],
            "efficiency": intelligence_metrics["efficiency"],
            "route": routing["route"],
            **exec_meta,
        },
    )

    # === NEW: EVOLUTION TRACKING ===
    # Record experience in pattern memory via evolution adapter
    experience_capsule = {
        "route": routing["route"],
        "iq_like": intelligence_metrics["iq_like"],
        "efficiency": intelligence_metrics["efficiency"],
        "context": session_context.get("type", "general"),
    }

    evo_adapter.record(success, experience_capsule)

    # Get hint for next reasoning turn
    next_turn_hint = evo_adapter.next_hint()
    learning_stats = evo_adapter.get_learning_stats()

    # === RETURN Enhanced Results ===
    return {
        "answer": answer_text,
        "evidence": evidence_list,
        "traditional_scores": scores,
        "intelligence_metrics": intelligence_metrics,
        "execution_metadata": exec_meta,
        "evolution_hint": next_turn_hint,
        "learning_stats": learning_stats,
        "success": success,
    }


def demo_enhanced_flow():
    """Demo of the enhanced flow."""
    print("🧠 Enhanced Intelligence Judgment Loop Demo")
    print("=" * 50)

    # Simulate a few queries to show learning
    queries = [
        "What is machine learning?",
        "How does photosynthesis work?",
        "Explain quantum computing",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n🔍 Query {i}: {query}")

        result = enhanced_judgment_loop(
            query, {"type": "educational", "session": f"demo_{i}"}
        )

        print(f"✅ Success: {result['success']}")
        print(f"📊 IQ-like Score: {result['intelligence_metrics']['iq_like']}")
        print(f"⚡ Efficiency: {result['intelligence_metrics']['efficiency']:.3f}")
        print(f"💡 Next Hint: {result['evolution_hint']['hint']}")
        print(f"📈 Success Rate: {result['learning_stats']['success_rate']:.2%}")
        print("-" * 30)


if __name__ == "__main__":
    demo_enhanced_flow()
