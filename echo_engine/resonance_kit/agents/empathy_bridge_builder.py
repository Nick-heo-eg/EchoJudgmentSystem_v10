"""
Empathy Bridge Builder: 감정적 공명 브리지 구축 (Simple Mock Version)
- 사용자 감정 상태 분석
- 감정적 안전감 평가
- 공감적 응답 패턴 제안
"""

from typing import Dict, List, Any


class EmpathyBridgeBuilder:
    """감정적 공명 브리지 구축기 (Mock Version)"""

    def __init__(self, config: Dict[str, Any], session, metrics):
        self.config = config
        self.session = session
        self.metrics = metrics

    def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """감정적 공명 브리지 분석 실행"""
        user_turns = [turn for turn in transcript if turn.get("role") == "user"]
        combined_text = " ".join([turn.get("text", "") for turn in user_turns])

        # Analyze emotional needs
        empathy_indicators = {
            "understanding": ["이해", "알아", "맞아", "그래"],
            "support": ["도와", "함께", "지지", "응원"],
            "validation": ["맞다", "인정", "좋아", "훌륭"],
            "connection": ["공감", "느껴", "연결", "소통"],
        }

        need_scores = {}
        for need_type, indicators in empathy_indicators.items():
            score = sum(1 for indicator in indicators if indicator in combined_text)
            need_scores[need_type] = min(1.0, score / 5)

        # Calculate emotional safety
        safety_indicators = ["편안", "안심", "믿어", "신뢰"]
        unsafe_indicators = ["불안", "걱정", "두려", "조심"]

        safety_count = sum(
            1 for indicator in safety_indicators if indicator in combined_text
        )
        unsafe_count = sum(
            1 for indicator in unsafe_indicators if indicator in combined_text
        )

        safety_score = max(0.3, min(1.0, (safety_count + 1) / max(1, unsafe_count + 1)))

        # Calculate overall empathy resonance
        empathy_score = (sum(need_scores.values()) + safety_score) / 5

        # Update metrics
        self.metrics.update_metric("empathy_resonance", empathy_score)
        self.metrics.update_metric("emotional_safety", safety_score)

        return {
            "metrics": {
                "empathy_resonance": empathy_score,
                "emotional_safety": safety_score,
            },
            "need_analysis": need_scores,
            "safety_assessment": (
                "safe"
                if safety_score > 0.7
                else ("moderate" if safety_score > 0.4 else "needs_attention")
            ),
            "notes": f"Empathy resonance: {empathy_score:.2f}, safety: {safety_score:.2f}",
        }
