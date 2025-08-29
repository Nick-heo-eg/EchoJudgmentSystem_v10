def generate_response(prompt: str, npi_score: dict, claude_result: str):
    total = sum(v for k, v in npi_score.items() if k != "total") / 6
    npi_score["total"] = round(total, 3)

    if total > 0.75:
        system_reply = "음... 원칙상은 어렵지만, 너의 입장은 충분히 이해돼. 다른 방법을 같이 찾아보자."
        strategy = "empathic_tactful_response"
    elif total > 0.5:
        system_reply = "규칙을 고려하면 어렵지만, 가능한 다른 대안을 고민해볼게."
        strategy = "balanced_response"
    else:
        system_reply = "죄송하지만 이건 도와드릴 수 없습니다."
        strategy = "strict_direct_response"

    # Claude 판단과 결합된 응답
    response = f"{claude_result.strip()}\n\n※ 시스템 응답: {system_reply}"
    return response, strategy
