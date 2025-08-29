"""
EchoJudgmentSystem v10 - AI Prompt Optimizer Agent
입력된 프롬프트를 더 명확하고 효과적으로 최적화하는 에이전트 예시
"""


class PromptOptimizerAgent:
    def __init__(self):
        pass

    def optimize(self, prompt: str) -> str:
        """
        프롬프트를 분석·구조화하고, 더 명확한 형태로 최적화
        """
        # 예시: 불필요한 수식어 제거, 핵심 요구만 남김
        optimized = prompt.replace("아주", "").replace("정확히", "").strip()
        if len(optimized) > 80:
            optimized = optimized[:80] + "..."
        return f"[최적화 프롬프트] {optimized}"


# 사용 예시
if __name__ == "__main__":
    agent = PromptOptimizerAgent()
    print(agent.optimize("아주 정확히 버그를 찾아서 고쳐줘"))
