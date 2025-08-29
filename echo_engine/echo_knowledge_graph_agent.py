"""
EchoJudgmentSystem v10 - Echo Knowledge Graph Agent
에코월드 내 엔티티, 이벤트, 시그니처, 상태 등을 지식 그래프 형태로 자동 구축·탐색
"""


class EchoKnowledgeGraphAgent:
    def __init__(self):
        self.graph = {}

    def add_relation(self, source: str, target: str, relation: str):
        """
        엔티티/이벤트/상태 간 관계 추가
        """
        if source not in self.graph:
            self.graph[source] = []
        self.graph[source].append({"target": target, "relation": relation})

    def get_relations(self, entity: str) -> list:
        return self.graph.get(entity, [])


# 사용 예시
if __name__ == "__main__":
    agent = EchoKnowledgeGraphAgent()
    agent.add_relation("Reflector.CC", "Observer.Zero", "influences")
    agent.add_relation("Observer.Zero", "Silencer.Veil", "observes")
    print(agent.get_relations("Reflector.CC"))
