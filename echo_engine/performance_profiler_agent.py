"""
EchoJudgmentSystem v10 - Performance Profiler Agent
코드의 성능 병목 구간을 자동 분석하고 최적화 방안을 제안하는 에이전트 예시
"""


class PerformanceProfilerAgent:
    def __init__(self):
        pass

    def profile(self, code: str) -> list[str]:
        """
        코드 내 성능 병목(예: 반복문, 불필요한 연산 등) 분석
        """
        issues = []
        if "for " in code and "range(" in code:
            issues.append("반복문 사용: 대용량 데이터 처리 시 최적화 필요")
        if "time.sleep(" in code:
            issues.append("time.sleep() 사용: 불필요한 대기 발생 가능")
        if "print(" in code:
            issues.append("print() 다량 사용: I/O 병목 가능성")
        return issues


# 사용 예시
if __name__ == "__main__":
    code = "for i in range(100000):\n    print(i)\n    time.sleep(1)"
    agent = PerformanceProfilerAgent()
    print(agent.profile(code))
