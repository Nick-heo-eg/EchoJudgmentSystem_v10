"""
EchoJudgmentSystem v10 - Dependency Updater Agent
프로젝트의 패키지/라이브러리 의존성을 최신 버전으로 자동 업데이트하는 에이전트 예시
"""


class DependencyUpdaterAgent:
    def __init__(self):
        pass

    def update_dependencies(self, requirements: str) -> str:
        """
        requirements.txt 내용 입력 → 최신 버전으로 업데이트된 내용 반환
        """
        # 예시: 모든 패키지 버전을 'latest'로 변경
        lines = requirements.split("\n")
        updated = []
        for line in lines:
            if "==" in line:
                pkg = line.split("==")[0]
                updated.append(f"{pkg}==latest")
            elif line.strip():
                updated.append(f"{line.strip()}==latest")
        return "\n".join(updated)


# 사용 예시
if __name__ == "__main__":
    reqs = "numpy==1.21.0\npandas==1.3.0"
    agent = DependencyUpdaterAgent()
    print(agent.update_dependencies(reqs))
