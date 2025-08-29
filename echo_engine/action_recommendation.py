# echo_engine/action_recommendation.py


def recommend_action(world_state: dict) -> str:
    """
    세계 상태를 기반으로 추천 행동 출력
    """
    mood = world_state["state"]["mood"]
    creativity = world_state["state"]["innovation_potential"]
    risk = world_state["state"]["risk_factor"]

    if mood == "unstable":
        if risk > 0.5:
            return "⚠️ 위험 요소를 줄이고 안정성을 확보하세요."
        else:
            return "🧩 혼란 속에서 새로운 가능성을 탐색해보세요."

    if mood == "open":
        if creativity > 0.8:
            return "🎯 창의적인 아이디어를 구체적으로 실행해보세요."
        elif creativity > 0.5:
            return "📝 실험적인 접근을 작게 시도해보세요."
        else:
            return "📊 효율성을 우선으로 계획을 정비해보세요."

    return "🤔 추가 정보가 필요합니다. 전략을 재설정해보세요."
