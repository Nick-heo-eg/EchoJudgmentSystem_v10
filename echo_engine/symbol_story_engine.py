# echo_engine/symbol_story_engine.py


def generate_story(seed: str, strategy: str, emotion: str, action: str) -> str:
    """
    전략⨯감정⨯행동⨯심볼 시드를 기반으로 상징적 이야기 생성
    """
    # 전략 설명 사전
    strategy_desc = {
        "creative_initiative": "당신은 새로운 가능성에 과감히 뛰어드는 개척자였습니다.",
        "risk_avoidance": "당신은 위험을 피하며 신중하게 길을 모색했습니다.",
        "efficiency_focus": "당신은 자원을 아끼며 효율적으로 문제를 해결했습니다.",
        "user_centric": "당신은 타인의 입장을 먼저 생각하며 결정을 내렸습니다.",
        "logical_neutral": "당신은 감정보다 논리를 우선으로 삼아 판단했습니다.",
    }

    # 감정 설명 사전
    emotion_desc = {
        "curious": "호기심이 당신을 이끌었습니다.",
        "anxious": "불안함이 선택의 배경에 깔려 있었습니다.",
        "confident": "자신감 넘치는 마음으로 움직였습니다.",
        "empathetic": "공감이 당신의 결정을 부드럽게 감싸고 있었습니다.",
        "neutral": "감정보다는 균형 잡힌 시각이 드러났습니다.",
    }

    # 이야기 생성
    story = f"""
    🧬 상징 시드: `{seed}`

    {strategy_desc.get(strategy, "")}
    {emotion_desc.get(emotion, "")}

    결국 당신은 이렇게 행동했습니다: **{action}**

    이 선택은 세계에 또 다른 가능성을 열었습니다.
    """

    return story.strip()


# echo_engine/symbol_story_engine.py


def generate_story(seed: dict, strategy: str, emotion: str, action: str) -> str:
    """
    상징 시드 + 전략 + 감정 + 행동을 바탕으로 간단한 이야기 생성
    """
    symbol_combo = seed["world_seed"]
    mood = seed["attributes"]

    template = f"""
    어느 날, 상징 `{symbol_combo}` 로 정의된 세계가 생성되었다.
    이 세계는 창의도 {mood['creativity']:.2f}, 위험도 {mood['tension']:.2f}의 균형 위에 있었다.

    전략 `{strategy}` 와 감정 `{emotion}` 이 교차한 이곳에서,
    시스템은 다음과 같은 행동을 제안했다:

    👉 **"{action}"**

    이는 이 세계에 어떤 영향을 줄까?
    """

    return template.strip()
