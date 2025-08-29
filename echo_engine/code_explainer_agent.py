"""
EchoJudgmentSystem v10 - Code Explainer Agent
입력된 Python 코드에 대해 한글 설명 및 주석을 자동 추가하는 에이전트 예시
"""


class CodeExplainerAgent:
    def __init__(self):
        pass

    def explain(self, code: str) -> str:
        """
        코드 동작을 한글로 설명하고, 각 라인에 주석 추가
        """
        lines = code.split("\n")
        explained = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("def "):
                func_name = stripped.split("(")[0][4:]
                explained.append(f"{line}  # 함수 정의: {func_name} 함수")
            elif "return a + b" in stripped:
                explained.append(f"{line}  # 두 수를 더해서 반환")
            elif "return a * b" in stripped:
                explained.append(f"{line}  # 두 수를 곱해서 반환")
            elif stripped.startswith("print("):
                explained.append(f"{line}  # 결과 출력")
            else:
                explained.append(line)
        # 전체 코드 설명 추가
        description = """# 이 코드는 입력값에 따라 연산을 수행하는 함수 예시입니다."""
        return description + "\n" + "\n".join(explained)


# 사용 예시
if __name__ == "__main__":
    sample_code = """
def add_numbers(a, b):
    return a + b
"""
    agent = CodeExplainerAgent()
    print(agent.explain(sample_code))
