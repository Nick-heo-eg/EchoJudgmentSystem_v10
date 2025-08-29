"""
EchoJudgmentSystem v10 - Echo Data Collector Agent
에코월드의 모든 엔티티, 이벤트, 상태, 로그 데이터를 자동 수집·정제·저장하는 에이전트 예시
"""


class EchoDataCollectorAgent:
    def __init__(self):
        self.data = []

    def collect(self, entity: str, event: str, state: str):
        self.data.append({"entity": entity, "event": event, "state": state})

    def get_data(self) -> list:
        return self.data

    def save_to_file(self, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            for entry in self.data:
                f.write(str(entry) + "\n")


# 사용 예시
if __name__ == "__main__":
    agent = EchoDataCollectorAgent()
    agent.collect("Reflector.CC", "activate", "active")
    agent.collect("Observer.Zero", "observe", "idle")
    print(agent.get_data())
    agent.save_to_file("echo_data.txt")
