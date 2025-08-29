"""
EchoJudgmentSystem v10 - Code-to-Architecture Agent
코드 입력 시 시스템 아키텍처/의존성 구조를 자동 생성하는 에이전트 예시
"""


class CodeToArchitectureAgent:
    def __init__(self):
        pass

    def generate_architecture(self, code: str) -> str:
        """
        코드에서 함수/클래스/모듈 구조를 추출해 계층 구조 다이어그램 텍스트 생성
        """
        # 예시: 함수/클래스명 추출
        import re

        funcs = re.findall(r"def ([a-zA-Z_][a-zA-Z0-9_]*)", code)
        classes = re.findall(r"class ([a-zA-Z_][a-zA-Z0-9_]*)", code)
        diagram = "# 시스템 아키텍처\n"
        for cls in classes:
            diagram += f"[Class] {cls}\n"
        for func in funcs:
            diagram += f"  └─ [Function] {func}\n"
        return diagram


# 사용 예시
if __name__ == "__main__":
    sample_code = """
class Foo:
    def bar(self):
        pass

def baz():
    pass
"""
    agent = CodeToArchitectureAgent()
    print(agent.generate_architecture(sample_code))
