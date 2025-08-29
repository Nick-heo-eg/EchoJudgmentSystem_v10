"""
EchoJudgmentSystem v10 - Multi-Agent Orchestrator
여러 Agent를 자동으로 조합·연계해 복합 문제를 처리하는 오케스트레이션 에이전트 예시
"""


class MultiAgentOrchestrator:
    def __init__(self, agents: dict):
        self.agents = agents

    def orchestrate(self, code: str) -> dict:
        """
        버그 진단 → 테스트 생성 → 문서화 등 복합 처리
        """
        results = {}
        if "bug_hunter" in self.agents:
            results["bugs"] = self.agents["bug_hunter"].analyze_code(code)
        if "testcase_writer" in self.agents:
            results["testcase"] = self.agents["testcase_writer"].generate_testcase(code)
        if "code_explainer" in self.agents:
            results["explanation"] = self.agents["code_explainer"].explain(code)
        return results


# 사용 예시
if __name__ == "__main__":
    from bug_hunter_agent import BugHunterAgent
    from testcase_writer_agent import TestcaseWriterAgent
    from code_explainer_agent import CodeExplainerAgent

    agents = {
        "bug_hunter": BugHunterAgent(),
        "testcase_writer": TestcaseWriterAgent(),
        "code_explainer": CodeExplainerAgent(),
    }
    orchestrator = MultiAgentOrchestrator(agents)
    code = "def foo():\n    print('hello')"
    print(orchestrator.orchestrate(code))
