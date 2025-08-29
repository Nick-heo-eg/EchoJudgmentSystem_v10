"""
EchoJudgmentSystem v10 - Natural Language Structurer Agent
긴 자연어 명령/요구사항을 자동으로 구조화하는 에이전트 예시
"""


class NaturalLanguageStructurerAgent:
    def __init__(self):
        pass

    def structure(self, text: str) -> dict:
        """
        자연어 명령에서 핵심 요구사항, 기능, 제약조건, 우선순위 추출
        """
        # 예시: 단순 키워드 기반 구조화
        result = {"요구사항": [], "기능": [], "제약조건": [], "우선순위": []}
        if "빠르게" in text:
            result["우선순위"].append("속도")
        if "보안" in text:
            result["제약조건"].append("보안 강화")
        if "테스트" in text:
            result["기능"].append("테스트 자동화")
        result["요구사항"].append(text)
        return result


# 사용 예시
if __name__ == "__main__":
    nl_text = "빠르게 동작하고, 보안이 강화된 테스트 자동화 시스템을 만들어줘"
    agent = NaturalLanguageStructurerAgent()
    print(agent.structure(nl_text))
