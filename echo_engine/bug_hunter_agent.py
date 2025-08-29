"""
EchoJudgmentSystem v10 - Bug Hunter Kit
코드 자동 진단 및 버그 리포트 에이전트 예시
"""

import ast


class BugHunterAgent:
    def __init__(self):
        pass

    def analyze_code(self, code: str) -> list[dict]:
        """
        코드 내 버그, 에러, 취약점 탐지 (간단한 AST 기반)
        """
        issues = []
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            issues.append(
                {
                    "type": "SyntaxError",
                    "message": str(e),
                    "lineno": getattr(e, "lineno", None),
                }
            )
            return issues
        # 예시: print 사용, eval 사용 등 위험 패턴 탐지
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if getattr(node.func, "id", None) == "eval":
                    issues.append(
                        {
                            "type": "SecurityWarning",
                            "message": "eval() 사용은 보안상 위험합니다.",
                            "lineno": node.lineno,
                        }
                    )
                if getattr(node.func, "id", None) == "exec":
                    issues.append(
                        {
                            "type": "SecurityWarning",
                            "message": "exec() 사용은 보안상 위험합니다.",
                            "lineno": node.lineno,
                        }
                    )
        return issues

    def report(self, code: str) -> str:
        """
        진단 결과를 리포트 형태로 반환
        """
        issues = self.analyze_code(code)
        if not issues:
            return "✅ 버그/취약점 없음. 코드가 안전합니다."
        report_lines = ["❌ 버그/취약점 발견:"]
        for issue in issues:
            line = f"- [{issue['type']}] Line {issue.get('lineno', '?')}: {issue['message']}"
            report_lines.append(line)
        return "\n".join(report_lines)


# 사용 예시
if __name__ == "__main__":
    sample_code = """
def foo():
    eval('print(123)')
    print('hello')
"""
    agent = BugHunterAgent()
    print(agent.report(sample_code))
