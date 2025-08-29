#!/usr/bin/env python3
import matplotlib.pyplot as plt
from echo_engine.telemetry.timeline_logger import read_log

STATE_ORDER = {
    "judgment_mode": 0,
    "liminal_entered": 1,
    "existence_mode": 2,
    "return_to_judgment": 3,
}


def main():
    data = read_log()
    if not data:
        print("❌ 로그가 비어 있습니다.")
        return

    xs = [i for i, _ in enumerate(data)]
    ys = [STATE_ORDER.get(d["state"], -1) for d in data]
    labels = [f'{d["state"]} ({d["by"]})' for d in data]

    plt.figure()
    plt.plot(xs, ys, marker="o")
    for x, y, label in zip(xs, ys, labels):
        plt.text(x, y + 0.05, label, fontsize=8, rotation=15)

    plt.yticks(list(STATE_ORDER.values()), list(STATE_ORDER.keys()))
    plt.xlabel("Step")
    plt.ylabel("LIMINAL State")
    plt.title("Meta-Liminal Transition Timeline")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
