"""
EchoJudgmentSystem v10 - Security Auditor Agent
코드와 설정의 보안 취약점을 자동 진단하고 개선 방안을 제안하는 에이전트 예시
"""


class SecurityAuditorAgent:
    def __init__(self):
        pass

    def audit(self, code: str) -> list[str]:
        """
        코드 내 보안 취약점(예: eval, exec, 하드코딩된 비밀번호 등) 진단
        """
        issues = []
        if "eval(" in code:
            issues.append("eval() 사용은 보안상 위험합니다.")
        if "exec(" in code:
            issues.append("exec() 사용은 보안상 위험합니다.")
        if "password =" in code or "passwd =" in code:
            issues.append("비밀번호 하드코딩은 위험합니다.")
        return issues


# 사용 예시
if __name__ == "__main__":
    code = "eval('print(123)')\npassword = '1234'"
    agent = SecurityAuditorAgent()
    print(agent.audit(code))
