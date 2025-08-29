# signature_loop_bridge.py - 시그니처⨯페르소나⨯루프 연계 모듈
# Signature-Persona-Loop Integration Bridge

import yaml
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from .loop_executor import LoopExecutor, execute_loop


@dataclass
class SignatureLoopMapping:
    signature_id: str
    preferred_loops: List[str]
    loop_sensitivity: Dict[str, float]
    fallback_loop: str
    meta_response: Dict[str, str]


class SignatureLoopBridge:
    def __init__(
        self,
        signature_yaml_path: str = "data/signature.yaml",
        persona_yaml_path: str = "data/persona.yaml",
    ):
        self.signature_yaml_path = signature_yaml_path
        self.persona_yaml_path = persona_yaml_path
        self.signatures = self._load_signatures()
        self.personas = self._load_personas()
        self.loop_executor = LoopExecutor()

    def _load_signatures(self) -> Dict:
        """Load signature configurations"""
        try:
            with open(self.signature_yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {"signatures": []}

    def _load_personas(self) -> Dict:
        """Load persona configurations"""
        try:
            with open(self.persona_yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {"personas": []}

    def get_signature_by_id(self, signature_id: str) -> Optional[Dict]:
        """Get signature configuration by ID"""
        for signature in self.signatures.get("signatures", []):
            if signature.get("id") == signature_id:
                return signature
        return None

    def get_persona_by_signature(self, signature_id: str) -> Optional[Dict]:
        """Get persona configuration for a signature"""
        for persona in self.personas.get("personas", []):
            if persona.get("signature_profile") == signature_id:
                return persona
        return None

    def determine_optimal_loop(self, signature_id: str, context: Dict) -> str:
        """Determine optimal loop based on signature and context"""
        signature = self.get_signature_by_id(signature_id)
        if not signature:
            return "JUDGE"  # Default fallback

        # Check context for specific triggers
        complexity = context.get("complexity", 0.5)
        uncertainty = context.get("uncertainty", 0.5)
        failure_detected = context.get("failure_detected", False)
        emotional_intensity = context.get("emotional_intensity", 0.5)

        # Determine loop based on signature preferences and context
        if failure_detected:
            return "RISE"
        elif complexity > 0.7:
            return "FIST"
        elif emotional_intensity > 0.6:
            return "FLOW"
        elif uncertainty > 0.8:
            return "QUANTUM"
        elif context.get("meta_cognition_needed", False):
            return "META"
        else:
            # Use signature-specific preferences
            primary_strategies = signature.get("primary_strategies", [])
            if "analytical" in primary_strategies:
                return "FIST"
            elif "empathetic" in primary_strategies:
                return "FLOW"
            elif "transformative" in primary_strategies:
                return "RISE"
            else:
                return "JUDGE"

    def get_loop_sensitivity(self, signature_id: str, loop_id: str) -> float:
        """Get loop sensitivity for a signature"""
        signature = self.get_signature_by_id(signature_id)
        if not signature:
            return 0.5  # Default sensitivity

        # Map signature characteristics to loop sensitivity
        emotion_sensitivity = signature.get("emotion_sensitivity", 0.5)
        meta_sensitivity = signature.get("meta_sensitivity", 0.5)

        sensitivity_map = {
            "FIST": meta_sensitivity * 0.8,
            "RISE": emotion_sensitivity * 0.7,
            "DIR": meta_sensitivity * 0.6,
            "PIR": emotion_sensitivity * 0.9,
            "META": meta_sensitivity,
            "FLOW": emotion_sensitivity,
            "QUANTUM": meta_sensitivity * 0.5,
            "JUDGE": (emotion_sensitivity + meta_sensitivity) / 2,
        }

        return sensitivity_map.get(loop_id, 0.5)

    def execute_signature_based_judgment(
        self, input_text: str, signature_id: str, context: Dict = None
    ) -> Dict:
        """Execute judgment using signature-based loop selection"""
        if context is None:
            context = {}

        # Add input analysis to context
        context.update(
            {
                "input_text": input_text,
                "complexity": self._analyze_complexity(input_text),
                "uncertainty": self._analyze_uncertainty(input_text),
                "emotional_intensity": self._analyze_emotional_intensity(input_text),
            }
        )

        # Determine optimal loop
        optimal_loop = self.determine_optimal_loop(signature_id, context)

        # Get signature and persona info
        signature = self.get_signature_by_id(signature_id)
        persona = self.get_persona_by_signature(signature_id)

        # Execute the loop
        loop_result = execute_loop(optimal_loop, context, signature_id=signature_id)

        # Compile final result
        result = {
            "input_text": input_text,
            "signature_id": signature_id,
            "signature_name": (
                signature.get("name", "Unknown") if signature else "Unknown"
            ),
            "persona": persona.get("name", "Default") if persona else "Default",
            "selected_loop": optimal_loop,
            "loop_sensitivity": self.get_loop_sensitivity(signature_id, optimal_loop),
            "loop_result": {
                "success": loop_result.success,
                "phases_executed": loop_result.phases_executed,
                "execution_time": loop_result.execution_time,
                "output": loop_result.output,
                "error": loop_result.error_message,
            },
            "context": context,
            "timestamp": (
                loop_result.output.get("timestamp") if loop_result.output else None
            ),
        }

        return result

    def run_multi_loop_analysis(
        self, input_text: str, signature_id: str, loop_ids: List[str]
    ) -> Dict:
        """Run multiple loops and compare results"""
        context = {
            "input_text": input_text,
            "complexity": self._analyze_complexity(input_text),
            "uncertainty": self._analyze_uncertainty(input_text),
            "emotional_intensity": self._analyze_emotional_intensity(input_text),
        }

        results = {}
        for loop_id in loop_ids:
            loop_result = execute_loop(loop_id, context, signature_id=signature_id)
            sensitivity = self.get_loop_sensitivity(signature_id, loop_id)

            results[loop_id] = {
                "sensitivity": sensitivity,
                "result": loop_result,
                "weighted_score": sensitivity * (1.0 if loop_result.success else 0.0),
            }

        # Find best performing loop
        best_loop = max(results.keys(), key=lambda x: results[x]["weighted_score"])

        return {
            "input_text": input_text,
            "signature_id": signature_id,
            "multi_loop_results": results,
            "recommended_loop": best_loop,
            "best_score": results[best_loop]["weighted_score"],
        }

    def _analyze_complexity(self, text: str) -> float:
        """Analyze text complexity (simple heuristic)"""
        word_count = len(text.split())
        question_marks = text.count("?")
        complex_words = len([w for w in text.split() if len(w) > 6])

        complexity = min(
            1.0, (word_count * 0.01) + (question_marks * 0.1) + (complex_words * 0.02)
        )
        return complexity

    def _analyze_uncertainty(self, text: str) -> float:
        """Analyze uncertainty level in text"""
        uncertainty_indicators = [
            "maybe",
            "perhaps",
            "might",
            "could",
            "uncertain",
            "unclear",
            "어쩌면",
            "아마도",
            "불확실",
        ]
        uncertainty_count = sum(
            1
            for indicator in uncertainty_indicators
            if indicator.lower() in text.lower()
        )

        uncertainty = min(1.0, uncertainty_count * 0.2)
        return uncertainty

    def _analyze_emotional_intensity(self, text: str) -> float:
        """Analyze emotional intensity in text"""
        emotional_words = [
            "느낌",
            "감정",
            "기분",
            "마음",
            "사랑",
            "화나",
            "슬픈",
            "기쁜",
            "불안",
            "걱정",
        ]
        emotional_punctuation = text.count("!") + text.count("...") * 0.5
        emotional_word_count = sum(1 for word in emotional_words if word in text)

        intensity = min(
            1.0, (emotional_word_count * 0.15) + (emotional_punctuation * 0.1)
        )
        return intensity


# Convenience functions
def execute_signature_judgment(
    input_text: str, signature_id: str, context: Dict = None
) -> Dict:
    """Execute judgment using signature-based approach"""
    bridge = SignatureLoopBridge()
    return bridge.execute_signature_based_judgment(input_text, signature_id, context)


def analyze_signature_loop_compatibility(signature_id: str) -> Dict:
    """Analyze how well a signature works with different loops"""
    bridge = SignatureLoopBridge()
    available_loops = bridge.loop_executor.loops_config.get("loops", [])

    compatibility = {}
    for loop in available_loops:
        loop_id = loop["id"]
        sensitivity = bridge.get_loop_sensitivity(signature_id, loop_id)
        compatibility[loop_id] = {
            "sensitivity": sensitivity,
            "description": loop.get("description", ""),
            "phases": loop.get("phases", []),
        }

    return {
        "signature_id": signature_id,
        "loop_compatibility": compatibility,
        "recommended_loops": sorted(
            compatibility.keys(),
            key=lambda x: compatibility[x]["sensitivity"],
            reverse=True,
        )[:3],
    }


if __name__ == "__main__":
    # Test signature-loop integration
    test_input = "이 복잡한 상황에서 어떤 전략이 가장 효과적일까요? 감정적으로도 어려운 결정이네요."
    test_signature = "Echo-Aurora"

    result = execute_signature_judgment(test_input, test_signature)
    print(f"Selected Loop: {result['selected_loop']}")
    print(f"Success: {result['loop_result']['success']}")
    print(f"Sensitivity: {result['loop_sensitivity']:.2f}")

    # Test compatibility analysis
    compatibility = analyze_signature_loop_compatibility(test_signature)
    print(
        f"Recommended loops for {test_signature}: {compatibility['recommended_loops']}"
    )
