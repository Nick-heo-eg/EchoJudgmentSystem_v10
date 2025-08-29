import json
import os

# 기본 전략 리스트
STRATEGIES = [
    "risk_avoidance",
    "creative_initiative",
    "efficiency_focus",
    "user_centric",
    "logical_neutral",
]

# 가중치 파일 경로
WEIGHT_FILE = "strategy_weights.json"


def load_weights():
    if os.path.exists(WEIGHT_FILE):
        with open(WEIGHT_FILE, "r") as f:
            return json.load(f)
    else:
        # 기본 가중치 1.0
        return {strategy: 1.0 for strategy in STRATEGIES}


def save_weights(weights):
    with open(WEIGHT_FILE, "w") as f:
        json.dump(weights, f, indent=2)


def update_weight(strategy: str, delta: float):
    weights = load_weights()
    if strategy in weights:
        weights[strategy] += delta
        weights[strategy] = max(0.1, round(weights[strategy], 3))  # 최소값 제한
        save_weights(weights)


def weighted_strategy(strategies: list) -> str:
    """
    입력된 전략 리스트 중 가중치 기반으로 하나 선택
    """
    import random

    weights = load_weights()
    filtered = [(s, weights.get(s, 1.0)) for s in strategies]
    total = sum(w for _, w in filtered)
    probs = [w / total for _, w in filtered]
    options = [s for s, _ in filtered]
    return random.choices(options, probs)[0]
