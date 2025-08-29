"""
EchoJudgmentSystem v10 - Emotion Transition Simulator
감정 상태와 임계치 기반 상태 전이 시뮬레이션 에이전트
"""


class EmotionTransitionSimulator:
    def __init__(self, liminal_threshold: float = 0.7):
        self.liminal_threshold = liminal_threshold
        self.state = "judgment"
        self.history = []

    def simulate(self, emotion: str, amplitude: float) -> dict:
        """
        감정(amplitude)와 임계치에 따라 상태 전이 시뮬레이션
        """
        result = {
            "input_emotion": emotion,
            "input_amplitude": amplitude,
            "initial_state": self.state,
            "transition_occurred": False,
            "final_state": self.state,
            "log": [],
        }
        result["log"].append(f"초기 상태: {self.state}")
        if amplitude >= self.liminal_threshold:
            self.state = "liminal"
            result["transition_occurred"] = True
            result["log"].append(
                f"임계치({self.liminal_threshold}) 도달: liminal 상태로 전이"
            )
        else:
            result["log"].append("임계치 미달: 상태 변화 없음")
        result["final_state"] = self.state
        self.history.append(result)
        return result

    def get_history(self) -> list[dict]:
        return self.history


# 사용 예시
if __name__ == "__main__":
    simulator = EmotionTransitionSimulator(liminal_threshold=0.7)
    print(simulator.simulate("confusion", 0.5))
    print(simulator.simulate("hope", 0.8))
    print(simulator.get_history())
