"""
EchoJudgmentSystem v10 - Testcase Writer Agent
입력된 함수 코드에 대해 pytest 스타일의 테스트케이스를 자동 생성하는 에이전트 예시
"""

import re


class TestcaseWriterAgent:
    def __init__(self):
        pass

    def generate_testcase(self, func_code: str, function_name: str = None) -> str:
        """
        함수 코드 입력 → pytest 스타일 테스트케이스 자동 생성
        """
        # 함수명 추출
        if not function_name:
            match = re.search(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)", func_code)
            function_name = match.group(1) if match else "auto_func"
        # 예시: 덧셈 함수에 대한 테스트케이스
        if "return a + b" in func_code:
            test_code = f"def test_{function_name}():\n    assert {function_name}(2, 3) == 5\n    assert {function_name}(-1, 1) == 0\n    assert {function_name}(0, 0) == 0"
        elif "return a * b" in func_code:
            test_code = f"def test_{function_name}():\n    assert {function_name}(2, 3) == 6\n    assert {function_name}(0, 10) == 0\n    assert {function_name}(1, 1) == 1"
        else:
            test_code = f"def test_{function_name}():\n    # TODO: 테스트케이스 자동 생성 (함수 동작 분석 필요)\n    pass"
        return test_code


# 사용 예시
if __name__ == "__main__":
    func_code = """
def add_numbers(a, b):
    return a + b
"""
    agent = TestcaseWriterAgent()
    print(agent.generate_testcase(func_code, "add_numbers"))
    func_code2 = """
def multiply_numbers(a, b):
    return a * b
"""
    print(agent.generate_testcase(func_code2, "multiply_numbers"))
