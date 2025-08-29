"""
EchoJudgmentSystem v10 - Code Refactor Agent
입력된 Python 코드를 더 깔끔하고 효율적으로 리팩터링하는 에이전트 예시
"""


class CodeRefactorAgent:
    def __init__(self):
        pass

    def refactor(self, code: str) -> str:
        """
        불필요한 pass만 제거하는 최소 리팩터링
        """
        lines = code.split("\n")
        cleaned = [line for line in lines if line.strip() != "pass"]
        return "\n".join(cleaned)


# 사용 예시
if __name__ == "__main__":
    sample_code = """
def myFunction():
    pass
    print('hello')
"""
    agent = CodeRefactorAgent()
    print(agent.refactor(sample_code))
