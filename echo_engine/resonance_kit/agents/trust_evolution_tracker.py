"""
Trust Evolution Tracker: 신뢰 관계 진화 추적 (Simple Mock Version)
- 신뢰 관련 키워드 분석
- 신뢰 충격 감지
- 신뢰 회복 패턴 분석
"""

from typing import Dict, List, Any


class TrustEvolutionTracker:
    """신뢰 진화 추적기 (Mock Version)"""

    def __init__(self, config: Dict[str, Any], session, metrics):
        self.config = config
        self.session = session
        self.metrics = metrics

    def run(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """신뢰 진화 추적 실행"""
        user_turns = [turn for turn in transcript if turn.get("role") == "user"]
        combined_text = " ".join([turn.get("text", "") for turn in user_turns])

        # Trust building indicators
        trust_building = ["믿어", "신뢰", "의지", "확신", "안심", "맡겨"]
        trust_breaking = ["의심", "불신", "실망", "배신", "틀렸", "잘못"]

        building_count = sum(
            1 for indicator in trust_building if indicator in combined_text
        )
        breaking_count = sum(
            1 for indicator in trust_breaking if indicator in combined_text
        )

        # Calculate trust level
        if building_count + breaking_count == 0:
            trust_score = 0.6  # neutral baseline
        else:
            trust_balance = (building_count - breaking_count) / (
                building_count + breaking_count
            )
            trust_score = max(0.1, min(1.0, 0.6 + trust_balance * 0.4))

        # Detect trust shock
        shock_indicators = ["실망", "배신", "화가", "짜증"]
        shock_count = sum(
            1 for indicator in shock_indicators if indicator in combined_text
        )
        trust_shock_detected = shock_count > 0

        # Calculate trust stability
        stability_score = max(0.3, 1.0 - (breaking_count / max(1, len(user_turns))))

        # Calculate trust delta (change)
        trust_delta = (building_count - breaking_count) / max(1, len(user_turns))

        # Update metrics
        self.metrics.update_metric("trust", trust_score)
        self.metrics.update_metric("trust_delta", trust_delta)
        self.metrics.update_metric("trust_stability", stability_score)

        return {
            "metrics": {
                "trust": trust_score,
                "trust_delta": trust_delta,
                "trust_stability": stability_score,
            },
            "trust_analysis": {
                "level": (
                    "high"
                    if trust_score > 0.7
                    else ("moderate" if trust_score > 0.4 else "low")
                ),
                "direction": (
                    "improving"
                    if trust_delta > 0.1
                    else ("declining" if trust_delta < -0.1 else "stable")
                ),
                "shock_detected": trust_shock_detected,
                "recovery_needed": trust_shock_detected and trust_score < 0.5,
            },
            "notes": f"Trust level: {trust_score:.2f}, delta: {trust_delta:.2f}, stability: {stability_score:.2f}",
        }
