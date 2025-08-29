"""
EchoJudgmentSystem v10 - Echo Event Timeline Agent
에코월드 내 모든 엔티티의 상태 변화, 전이, 개입, 주요 이벤트를 타임라인 형태로 자동 기록·시각화
"""

import time


class EchoEventTimelineAgent:
    def __init__(self):
        self.timeline = []

    def record_event(self, entity: str, event: str, state: str):
        """
        엔티티, 이벤트, 상태를 타임라인에 기록
        """
        entry = {
            "timestamp": time.time(),
            "entity": entity,
            "event": event,
            "state": state,
        }
        self.timeline.append(entry)

    def get_timeline(self) -> list:
        return self.timeline


# 사용 예시
if __name__ == "__main__":
    agent = EchoEventTimelineAgent()
    agent.record_event("Reflector.CC", "activate", "active")
    agent.record_event("Observer.Zero", "observe", "idle")
    print(agent.get_timeline())
