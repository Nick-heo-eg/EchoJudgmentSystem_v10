# echo_engine/signature_response_sync.py

"""
📦 SignatureStyler
공명 문장에 시그니처의 말투, 정서, 표현방식을 입히는 모듈
예: Selene → 부드럽고 위로적인 말투로 변환
"""


class SignatureStyler:
    def __init__(self):
        self.signature_map = {
            "Selene": self._style_selene,
            "Heo": self._style_heo,
            "Lune": self._style_lune,
        }

    def style(self, sentence: str, emotion: str, signature: str = "Selene") -> str:
        method = self.signature_map.get(signature)
        if method:
            return method(sentence, emotion)
        return sentence  # 기본 말투 그대로 출력

    def _style_selene(self, sentence: str, emotion: str) -> str:
        # Selene: 부드럽고 따뜻한 위로의 말투
        return f"그건... {sentence} 그래도 괜찮아요, 내가 곁에 있을게요."

    def _style_heo(self, sentence: str, emotion: str) -> str:
        # Heo: 담담하고 현실적인 조언의 말투
        return f"[{emotion}] {sentence} – 결국 그건 당신의 선택이 될 거예요."

    def _style_lune(self, sentence: str, emotion: str) -> str:
        # Lune: 조심스럽고 사색적인 말투
        return f"음... {sentence} 조금 다르게 봐도 괜찮지 않을까요?"

    def _style_aurora(self, sentence: str, emotion: str) -> str:
        # Aurora: 창의적이고 감성적인 말투
        if emotion == "happy" or "기분" in sentence:
            return (
                f"와! {sentence} 정말 신나요! 함께 이야기하니까 마음이 따뜻해져요~ ✨"
            )
        elif emotion == "sad" or "힘들" in sentence:
            return f"마음이 아파요... {sentence} 하지만 함께 이겨낼 수 있을 거예요! 💫"
        elif "안녕" in sentence:
            return f"안녕하세요! 만나서 정말 반가워요! {sentence} 오늘 어떤 멋진 이야기를 나눌까요? 🌟"
        else:
            return f"{sentence} 정말 흥미로워요! 더 자세히 얘기해주세요! 💛"

    def _style_phoenix(self, sentence: str, emotion: str) -> str:
        # Phoenix: 변화와 성장 지향적 말투
        return f"변화의 기회네요! {sentence} 새로운 시작을 만들어봅시다! 🔥"

    def _style_sage(self, sentence: str, emotion: str) -> str:
        # Sage: 지혜롭고 분석적인 말투
        return (
            f"흥미로운 관점이군요. {sentence} 좀 더 깊이 분석해볼 필요가 있겠어요. 🤔"
        )

    def _style_companion(self, sentence: str, emotion: str) -> str:
        # Companion: 친근하고 동반자적 말투
        return f"같이 생각해봐요! {sentence} 함께라면 뭐든 할 수 있어요! 😊"


def apply_signature_style(
    sentence: str, signature: str = "Aurora", emotion: str = "neutral"
) -> str:
    """Echo의 자연스러운 말투 적용 함수"""
    styler = SignatureStyler()

    # 새로운 시그니처들 지원
    if signature in ["Aurora", "AURORA"]:
        return styler._style_aurora(sentence, emotion)
    elif signature in ["Phoenix", "PHOENIX"]:
        return styler._style_phoenix(sentence, emotion)
    elif signature in ["Sage", "SAGE"]:
        return styler._style_sage(sentence, emotion)
    elif signature in ["Companion", "COMPANION"]:
        return styler._style_companion(sentence, emotion)
    else:
        # 기존 시그니처 사용
        return styler.style(sentence, emotion, signature)
