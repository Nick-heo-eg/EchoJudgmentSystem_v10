"""
EchoJudgmentSystem v10 - Echo Health Monitor Agent
에코월드 전체의 상태를 실시간 모니터링하고 이상 징후를 자동 감지·알림
"""


class EchoHealthMonitorAgent:
    def __init__(self):
        self.status = {}
        self.alerts = []

    def update_status(self, entity: str, state: str, amplitude: float = 0.0):
        """
        엔티티 상태/감정 진폭 업데이트
        """
        self.status[entity] = {"state": state, "amplitude": amplitude}
        if amplitude > 0.9:
            self.alerts.append(f"[ALERT] {entity} 감정 진폭 임계치 초과: {amplitude}")
        if state == "looped":
            self.alerts.append(f"[ALERT] {entity} 루프 고착 상태 감지")

    def get_status(self) -> dict:
        return self.status

    def get_alerts(self) -> list:
        return self.alerts


# 사용 예시
if __name__ == "__main__":
    agent = EchoHealthMonitorAgent()
    agent.update_status("Reflector.CC", "active", 0.5)
    agent.update_status("Observer.Zero", "looped", 0.2)
    agent.update_status("Silencer.Veil", "silent", 0.95)
    print(agent.get_status())
    print(agent.get_alerts())
