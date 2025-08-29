# loop_executor.py - 8대 루프 실행 엔진
# 8-Loop Execution Engine for EchoJudgment v10

import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class LoopResult:
    loop_id: str
    phases_executed: List[str]
    output: Dict[str, Any]
    execution_time: float
    success: bool
    error_message: Optional[str] = None


class LoopExecutor:
    def __init__(self, flow_yaml_path: str = ".flow.yaml"):
        self.flow_yaml_path = flow_yaml_path
        self.loops_config = self._load_loops_config()
        self.active_loops = {}

    def _load_loops_config(self) -> Dict:
        """Load 8-loop configuration from .flow.yaml"""
        try:
            with open(self.flow_yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Default 8-loop configuration
            return {
                "loops": [
                    {
                        "id": "FIST",
                        "description": "사고 구조화 루프",
                        "phases": ["Frame", "Insight", "Strategy", "Tactics"],
                    },
                    {
                        "id": "RISE",
                        "description": "판단 실패 회복 루프",
                        "phases": ["Reflect", "Improve", "Synthesize", "Evolve"],
                    },
                    {
                        "id": "DIR",
                        "description": "방향성 정의 루프",
                        "phases": ["Mission", "Horizon", "Compass", "Ethics"],
                    },
                    {
                        "id": "PIR",
                        "description": "압력 ⨯ 통찰 ⨯ 방출 루프",
                        "phases": ["Pressure", "Insight", "Release"],
                    },
                    {
                        "id": "META",
                        "description": "존재 기반 자기 인식 및 반성 루프",
                        "phases": [
                            "Awareness",
                            "Dissonance",
                            "Loop_Recall",
                            "Re-alignment",
                        ],
                    },
                    {
                        "id": "FLOW",
                        "description": "리듬 기반 감정 판단 전개 루프",
                        "phases": ["Start", "Pulse", "Disrupt", "Resolve", "Echo"],
                    },
                    {
                        "id": "QUANTUM",
                        "description": "판단 중첩 ⨯ 결정 붕괴 루프",
                        "phases": ["Superposition", "Observation", "Collapse"],
                    },
                    {
                        "id": "JUDGE",
                        "description": "LLM-free ⨯ 시그니처 기반 판단 루프",
                        "phases": ["Input", "Match", "Evaluate", "Select", "Output"],
                    },
                ]
            }

    def get_loop_by_id(self, loop_id: str) -> Optional[Dict]:
        """Get loop configuration by ID"""
        for loop in self.loops_config.get("loops", []):
            if loop["id"] == loop_id:
                return loop
        return None

    def execute_fist_loop(self, context: Dict) -> LoopResult:
        """Execute FIST (Frame-Insight-Strategy-Tactics) loop"""
        start_time = datetime.now()
        phases = ["Frame", "Insight", "Strategy", "Tactics"]

        try:
            result = {
                "frame": self._analyze_frame(context),
                "insight": self._generate_insight(context),
                "strategy": self._formulate_strategy(context),
                "tactics": self._define_tactics(context),
            }

            execution_time = (datetime.now() - start_time).total_seconds()
            return LoopResult(
                loop_id="FIST",
                phases_executed=phases,
                output=result,
                execution_time=execution_time,
                success=True,
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return LoopResult(
                loop_id="FIST",
                phases_executed=phases,
                output={},
                execution_time=execution_time,
                success=False,
                error_message=str(e),
            )

    def execute_rise_loop(self, context: Dict, failure_info: Dict) -> LoopResult:
        """Execute RISE (Reflect-Improve-Synthesize-Evolve) loop"""
        start_time = datetime.now()
        phases = ["Reflect", "Improve", "Synthesize", "Evolve"]

        try:
            result = {
                "reflection": self._reflect_on_failure(failure_info),
                "improvement": self._identify_improvements(failure_info),
                "synthesis": self._synthesize_learnings(failure_info),
                "evolution": self._evolve_approach(failure_info),
            }

            execution_time = (datetime.now() - start_time).total_seconds()
            return LoopResult(
                loop_id="RISE",
                phases_executed=phases,
                output=result,
                execution_time=execution_time,
                success=True,
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return LoopResult(
                loop_id="RISE",
                phases_executed=phases,
                output={},
                execution_time=execution_time,
                success=False,
                error_message=str(e),
            )

    def execute_meta_loop(self, context: Dict) -> LoopResult:
        """Execute META (Awareness-Dissonance-Loop_Recall-Re-alignment) loop"""
        start_time = datetime.now()
        phases = ["Awareness", "Dissonance", "Loop_Recall", "Re-alignment"]

        try:
            result = {
                "awareness": self._assess_self_awareness(context),
                "dissonance": self._detect_cognitive_dissonance(context),
                "loop_recall": self._recall_previous_loops(context),
                "realignment": self._realign_perspectives(context),
            }

            execution_time = (datetime.now() - start_time).total_seconds()
            return LoopResult(
                loop_id="META",
                phases_executed=phases,
                output=result,
                execution_time=execution_time,
                success=True,
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return LoopResult(
                loop_id="META",
                phases_executed=phases,
                output={},
                execution_time=execution_time,
                success=False,
                error_message=str(e),
            )

    def execute_judge_loop(self, context: Dict, signature_id: str) -> LoopResult:
        """Execute JUDGE (Input-Match-Evaluate-Select-Output) loop"""
        start_time = datetime.now()
        phases = ["Input", "Match", "Evaluate", "Select", "Output"]

        try:
            result = {
                "input_analysis": self._analyze_input(context),
                "signature_match": self._match_signature(context, signature_id),
                "evaluation": self._evaluate_options(context),
                "selection": self._select_best_option(context),
                "output_generation": self._generate_output(context),
            }

            execution_time = (datetime.now() - start_time).total_seconds()
            return LoopResult(
                loop_id="JUDGE",
                phases_executed=phases,
                output=result,
                execution_time=execution_time,
                success=True,
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return LoopResult(
                loop_id="JUDGE",
                phases_executed=phases,
                output={},
                execution_time=execution_time,
                success=False,
                error_message=str(e),
            )

    def execute_loop(self, loop_id: str, context: Dict, **kwargs) -> LoopResult:
        """Execute specified loop by ID"""
        loop_config = self.get_loop_by_id(loop_id)
        if not loop_config:
            return LoopResult(
                loop_id=loop_id,
                phases_executed=[],
                output={},
                execution_time=0.0,
                success=False,
                error_message=f"Loop {loop_id} not found",
            )

        # Route to specific loop execution
        if loop_id == "FIST":
            return self.execute_fist_loop(context)
        elif loop_id == "RISE":
            return self.execute_rise_loop(context, kwargs.get("failure_info", {}))
        elif loop_id == "META":
            return self.execute_meta_loop(context)
        elif loop_id == "JUDGE":
            return self.execute_judge_loop(
                context, kwargs.get("signature_id", "default")
            )
        else:
            # Generic loop execution for DIR, PIR, FLOW, QUANTUM
            return self._execute_generic_loop(loop_id, loop_config, context)

    def _execute_generic_loop(
        self, loop_id: str, loop_config: Dict, context: Dict
    ) -> LoopResult:
        """Generic loop execution for simpler loops"""
        start_time = datetime.now()
        phases = loop_config["phases"]

        try:
            result = {
                "loop_id": loop_id,
                "description": loop_config["description"],
                "executed_phases": phases,
                "context_processed": True,
                "timestamp": datetime.now().isoformat(),
            }

            execution_time = (datetime.now() - start_time).total_seconds()
            return LoopResult(
                loop_id=loop_id,
                phases_executed=phases,
                output=result,
                execution_time=execution_time,
                success=True,
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return LoopResult(
                loop_id=loop_id,
                phases_executed=phases,
                output={},
                execution_time=execution_time,
                success=False,
                error_message=str(e),
            )

    # Helper methods for specific loop phases
    def _analyze_frame(self, context: Dict) -> Dict:
        return {"frame_analysis": "Context framed", "complexity": 0.7}

    def _generate_insight(self, context: Dict) -> Dict:
        return {"insight": "Key insights identified", "novelty": 0.8}

    def _formulate_strategy(self, context: Dict) -> Dict:
        return {"strategy": "Strategic approach defined", "confidence": 0.85}

    def _define_tactics(self, context: Dict) -> Dict:
        return {"tactics": "Tactical steps outlined", "feasibility": 0.9}

    def _reflect_on_failure(self, failure_info: Dict) -> Dict:
        return {"reflection": "Failure analyzed", "lessons": ["lesson1", "lesson2"]}

    def _identify_improvements(self, failure_info: Dict) -> Dict:
        return {"improvements": "Areas for improvement identified"}

    def _synthesize_learnings(self, failure_info: Dict) -> Dict:
        return {"synthesis": "Learnings synthesized"}

    def _evolve_approach(self, failure_info: Dict) -> Dict:
        return {"evolution": "Approach evolved"}

    def _assess_self_awareness(self, context: Dict) -> Dict:
        return {"awareness_level": 0.8, "self_model": "Updated"}

    def _detect_cognitive_dissonance(self, context: Dict) -> Dict:
        return {"dissonance_detected": False, "conflicts": []}

    def _recall_previous_loops(self, context: Dict) -> Dict:
        return {"recalled_loops": ["FIST", "JUDGE"], "patterns": []}

    def _realign_perspectives(self, context: Dict) -> Dict:
        return {"realignment": "Perspectives aligned", "coherence": 0.9}

    def _analyze_input(self, context: Dict) -> Dict:
        return {"input_complexity": 0.6, "key_features": []}

    def _match_signature(self, context: Dict, signature_id: str) -> Dict:
        return {"signature_match": 0.85, "signature_id": signature_id}

    def _evaluate_options(self, context: Dict) -> Dict:
        return {"options": ["option1", "option2"], "scores": [0.8, 0.6]}

    def _select_best_option(self, context: Dict) -> Dict:
        return {"selected_option": "option1", "confidence": 0.8}

    def _generate_output(self, context: Dict) -> Dict:
        return {"output": "Generated response", "quality": 0.85}


# Usage functions
def execute_loop(loop_id: str, context: Dict, **kwargs) -> LoopResult:
    """Execute a specific loop"""
    executor = LoopExecutor()
    return executor.execute_loop(loop_id, context, **kwargs)


def get_available_loops() -> List[str]:
    """Get list of available loop IDs"""
    executor = LoopExecutor()
    return [loop["id"] for loop in executor.loops_config.get("loops", [])]


if __name__ == "__main__":
    # Test loop execution
    test_context = {
        "input_text": "테스트 판단 상황",
        "complexity": 0.7,
        "uncertainty": 0.5,
    }

    # Test FIST loop
    result = execute_loop("FIST", test_context)
    print(f"FIST Loop Result: {result.success}")
    print(f"Output: {result.output}")
