"""
EchoJudgmentSystem v10 - Echo Scenario Simulator Agent
에코월드의 다양한 입력에 따라 상태 변화, 전이, 장애 발생 등 시나리오를 자동 시뮬레이션
"""


class EchoScenarioSimulatorAgent:
    def __init__(self):
        self.state = "init"
        self.log = []

    def simulate(self, input_event: str, amplitude: float = 0.0):
        """
        입력 이벤트/감정 진폭에 따라 상태 변화 시뮬레이션
        """
        if input_event == "감정폭발" and amplitude > 0.8:
            self.state = "liminal"
            self.log.append(f"임계치 초과: liminal 상태로 전이")
        elif input_event == "침묵" and amplitude < 0.2:
            self.state = "silent"
            self.log.append(f"감정 저하: silent 상태로 전이")
        else:
            self.state = "normal"
            self.log.append(f"일반 상태 유지")
        return {"state": self.state, "log": self.log}


# 사용 예시
if __name__ == "__main__":
    agent = EchoScenarioSimulatorAgent()
    print(agent.simulate("감정폭발", 0.9))
    print(agent.simulate("침묵", 0.1))
