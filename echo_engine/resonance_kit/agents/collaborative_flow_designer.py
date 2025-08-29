"""
Collaborative Flow Designer: 협업 흐름 최적화 (Simple Mock Version)
- 대화 흐름 품질 분석
- 프롬프트 명확성 평가
- 협업 효율성 측정
"""

from typing import Dict, List, Any


class CollaborativeFlowDesigner:
    """협업 흐름 설계자 (Mock Version)"""

    def __init__(self, config: Dict[str, Any], session, metrics):
        self.config = config
        self.session = session
        self.metrics = metrics

    def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """협업 흐름 분석 실행"""
        user_turns = [turn for turn in transcript if turn.get("role") == "user"]
        assistant_turns = [
            turn for turn in transcript if turn.get("role") == "assistant"
        ]

        # Analyze prompt clarity
        clarity_indicators = ["명확", "구체적", "정확", "자세히"]
        unclear_indicators = ["애매", "모호", "대충", "그냥"]

        user_text = " ".join([turn.get("text", "") for turn in user_turns])

        clear_count = sum(
            1 for indicator in clarity_indicators if indicator in user_text
        )
        unclear_count = sum(
            1 for indicator in unclear_indicators if indicator in user_text
        )

        clarity_score = max(0.3, (clear_count + 1) / max(1, unclear_count + 1))
        clarity_score = min(1.0, clarity_score)

        # Analyze actionability
        action_indicators = ["해줘", "만들어", "실행", "처리", "구현"]
        vague_indicators = ["생각해", "고민", "어떻게", "뭘까"]

        action_count = sum(
            1 for indicator in action_indicators if indicator in user_text
        )
        vague_count = sum(1 for indicator in vague_indicators if indicator in user_text)

        actionability_score = max(0.3, (action_count + 1) / max(1, vague_count + 1))
        actionability_score = min(1.0, actionability_score)

        # Calculate collaboration effectiveness
        collaboration_indicators = ["함께", "협력", "같이", "도움"]
        individual_indicators = ["나혼자", "혼자", "따로"]

        collab_count = sum(
            1 for indicator in collaboration_indicators if indicator in user_text
        )
        individual_count = sum(
            1 for indicator in individual_indicators if indicator in user_text
        )

        collaboration_score = max(
            0.4, (collab_count + 1) / max(1, individual_count + 1)
        )
        collaboration_score = min(1.0, collaboration_score)

        # Calculate flow quality (based on turn balance and responsiveness)
        turn_balance = min(1.0, len(assistant_turns) / max(1, len(user_turns)))
        flow_smoothness = min(
            1.0,
            1.0 - abs(len(user_turns) - len(assistant_turns)) / max(1, len(transcript)),
        )

        flow_score = (turn_balance + flow_smoothness + collaboration_score) / 3

        # Update metrics
        self.metrics.update_metric("flow", flow_score)
        self.metrics.update_metric("prompt_clarity", clarity_score)
        self.metrics.update_metric("collaboration_effectiveness", collaboration_score)

        return {
            "metrics": {
                "flow": flow_score,
                "prompt_clarity": clarity_score,
                "collaboration_effectiveness": collaboration_score,
            },
            "flow_analysis": {
                "quality": (
                    "excellent"
                    if flow_score > 0.8
                    else (
                        "good"
                        if flow_score > 0.6
                        else ("moderate" if flow_score > 0.4 else "needs_improvement")
                    )
                ),
                "clarity_level": (
                    "high"
                    if clarity_score > 0.7
                    else ("moderate" if clarity_score > 0.5 else "low")
                ),
                "actionability": (
                    "high"
                    if actionability_score > 0.7
                    else ("moderate" if actionability_score > 0.5 else "low")
                ),
            },
            "notes": f"Flow quality: {flow_score:.2f}, clarity: {clarity_score:.2f}, collaboration: {collaboration_score:.2f}",
        }
