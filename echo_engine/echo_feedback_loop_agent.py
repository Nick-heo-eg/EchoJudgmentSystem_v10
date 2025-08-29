"""
EchoJudgmentSystem v10 - Echo Feedback Loop Agent
에코월드 내 반복 패턴, 루프, 피드백 구조를 자동 감지·분석하는 에이전트 예시
"""


class EchoFeedbackLoopAgent:
    def __init__(self):
        self.history = []

    def add_event(self, event: str):
        self.history.append(event)

    def detect_loop(self) -> dict:
        """
        반복되는 이벤트/패턴 자동 감지
        """
        loop_events = set([e for e in self.history if self.history.count(e) > 1])
        return {"loops": list(loop_events), "total_events": len(self.history)}


# 사용 예시
if __name__ == "__main__":
    agent = EchoFeedbackLoopAgent()
    agent.add_event("activate")
    agent.add_event("observe")
    agent.add_event("activate")
    print(agent.detect_loop())
