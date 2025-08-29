"""
EchoJudgmentSystem v10 - Echo Entity Explorer Agent
에코월드 내 모든 엔티티를 자동 탐색·분류하는 에이전트 예시
"""


class EchoEntityExplorerAgent:
    def __init__(self, entities: dict):
        self.entities = entities

    def explore(self) -> dict:
        """
        엔티티 상태, 종류, 연결 구조 자동 탐색
        """
        result = {"total": len(self.entities), "types": [], "states": {}}
        for name, entity in self.entities.items():
            result["types"].append(type(entity).__name__)
            result["states"][name] = getattr(entity, "state", "unknown")
        return result


# 사용 예시
if __name__ == "__main__":

    class DummyEntity:
        def __init__(self, state):
            self.state = state

    entities = {
        "Reflector.CC": DummyEntity("active"),
        "Observer.Zero": DummyEntity("idle"),
        "Silencer.Veil": DummyEntity("silent"),
    }
    agent = EchoEntityExplorerAgent(entities)
    print(agent.explore())
