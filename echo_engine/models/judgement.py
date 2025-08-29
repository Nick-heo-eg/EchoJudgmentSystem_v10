from typing import Optional, Dict, Any
from datetime import datetime


class InputContext:
    def __init__(
        self,
        text: str,
        source: Optional[str] = "user",
        timestamp: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        self.text = text
        self.source = source or "user"
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.context = context or {}

        # 예기치 않은 필드 확장 대응
        for key, value in kwargs.items():
            setattr(self, key, value)


class JudgmentResult:
    def __init__(
        self,
        input_text: str = "",
        strategy: str = "",
        emotion: str = "",
        reasoning: str = "",
        judgment: str = "",
        confidence: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        self.input_text = input_text
        self.strategy = strategy
        self.emotion = emotion
        self.reasoning = reasoning
        self.judgment = judgment or reasoning  # reasoning이 없을 때 대체
        self.confidence = confidence
        self.metadata = metadata or {}

        # 추가 필드 유연 처리
        for key, value in kwargs.items():
            setattr(self, key, value)


class MergedJudgmentResult:
    def __init__(
        self,
        input_text: str,
        echo_strategy: str,
        claude_strategy: Optional[str],
        echo_reasoning: str,
        claude_reasoning: Optional[str],
        agreement: bool,
        final_decision: str,
        **kwargs,
    ):
        self.input_text = input_text
        self.echo_strategy = echo_strategy
        self.claude_strategy = claude_strategy
        self.echo_reasoning = echo_reasoning
        self.claude_reasoning = claude_reasoning
        self.agreement = agreement
        self.final_decision = final_decision

        # 확장 필드 처리
        for key, value in kwargs.items():
            setattr(self, key, value)
