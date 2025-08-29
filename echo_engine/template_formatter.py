# template_formatter.py

"""
📦 TemplateFormatter
전략 프레임 (frame), 감정 (emotion), 전술 (tactics)을 기반으로
공명 문장을 생성하는 포맷터 모듈.
"""


class TemplateFormatter:
    def __init__(self):
        # 필요 시 템플릿 DB or YAML 로딩 구조 추가 가능
        # 프레임 이름과 메서드 매핑
        self.frame_method_map = {
            "위로": self._format_consolation,
            "격려": self._format_encouragement,
            "도전": self._format_challenge,
            "반성": self._format_reflection,
            "전환": self._format_transition,
            "희망": self.format_hope,
            "감사": self.format_gratitude,
            "혼란": self.format_confusion,
            "후회": self.format_regret,
        }

    def format(self, frame: str, tactics: str, emotion: str) -> str:
        """
        전략 프레임, 전술, 감정 기반 공명 문장 생성
        """
        method = self.frame_method_map.get(frame)
        if method:
            return method(emotion, tactics)
        else:
            return f"{emotion}한 상황이지만, {tactics} 하며 조금씩 바꿔볼 수 있어요."

    def format_template(self, frame: str, tactics: str, emotion: str) -> str:
        """format과 동일한 기능 (호환성을 위한 별칭)"""
        return self.format(frame, tactics, emotion)

    # 기존 format 함수의 각 분기를 별도 메서드로 분리
    def _format_consolation(self, emotion: str, tactics: str) -> str:
        return f"{emotion}한 마음이 느껴지네요. {tactics} 해보면 조금 나아질 수 있어요."

    def _format_encouragement(self, emotion: str, tactics: str) -> str:
        return f"{emotion}한 순간일수록, {tactics} 같은 행동이 큰 힘이 돼요."

    def _format_challenge(self, emotion: str, tactics: str) -> str:
        return f"{emotion}한 지금, {tactics}을 통해 한 걸음 내딛어보는 건 어때요?"

    def _format_reflection(self, emotion: str, tactics: str) -> str:
        return f"{emotion}했던 경험도 결국 {tactics}로 이어진다면 가치 있어요."

    def _format_transition(self, emotion: str, tactics: str) -> str:
        return f"{emotion}했던 흐름에서 {tactics}로 바뀌는 순간이 올 수 있어요."

    def format_hope(self, emotion: str, tactics: str) -> str:
        """
        희망 프레임: 감정 + 전술 기반 자연문 생성
        """
        return f"{emotion}한 마음이 조금씩 피어오르네요. {tactics}을(를) 시도해보면 더 밝은 내일이 기다릴 거예요."

    def format_gratitude(self, emotion: str, tactics: str) -> str:
        """
        감사 프레임: 감정 + 전술 기반 자연문 생성
        """
        return f"{emotion}한 순간에 감사함이 스며들어요. {tactics}을(를) 통해 마음이 한결 따뜻해질 거예요."

    def format_confusion(self, emotion: str, tactics: str) -> str:
        """
        혼란 프레임: 감정 + 전술 기반 자연문 생성
        """
        return f"{emotion}한 마음이 복잡할 수 있지만, {tactics}을(를) 천천히 해보면 조금씩 정리가 될 거예요."

    def format_regret(self, emotion: str, tactics: str) -> str:
        """
        후회 프레임: 감정 + 전술 기반 자연문 생성
        """
        return f"{emotion}한 마음이 남아있지만, {tactics}을(를) 통해 조금씩 자신을 다독여줄 수 있어요."
