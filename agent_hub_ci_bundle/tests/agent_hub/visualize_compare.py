
#!/usr/bin/env python3
import argparse, os, json
from typing import Dict, List
import matplotlib.pyplot as plt

def load(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def plot_compare(combined_json: str, out_dir: str):
    data = load(combined_json)
    steps = data["meta"]["steps"]
    sigs = data["meta"]["signatures"]
    results = data["results"]  # dict sig -> list rows

    xs = [c for (c, _) in steps]

    # RPS compare
    plt.figure()
    for s in sigs:
        rps = [row["rps"] for row in results[s]]
        plt.plot(xs, rps, marker="o", label=s)
    plt.title("RPS vs Concurrency (by Signature)")
    plt.xlabel("Concurrency")
    plt.ylabel("RPS")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(os.path.join(out_dir, "sig_rps_curve.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # p50 compare
    plt.figure()
    for s in sigs:
        p50 = [row["p50_ms"] for row in results[s]]
        plt.plot(xs, p50, marker="o", label=f"{s} p50")
    plt.title("p50 vs Concurrency (by Signature)")
    plt.xlabel("Concurrency")
    plt.ylabel("Latency (ms)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.savefig(os.path.join(out_dir, "sig_p50_curve.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # p95 compare
    plt.figure()
    for s in sigs:
        p95 = [row["p95_ms"] for row in results[s]]
        plt.plot(xs, p95, marker="o", label=f"{s} p95")
    plt.title("p95 vs Concurrency (by Signature)")
    plt.xlabel("Concurrency")
    plt.ylabel("Latency (ms)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.savefig(os.path.join(out_dir, "sig_p95_curve.png"), dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Saved comparison plots into: {out_dir}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("combined_json", help="artifacts/bench/<run>/combined.json")
    ap.add_argument("--out-dir", default="", help="Output dir (default = same folder as input)")
    args = ap.parse_args()
    out = args.out_dir or os.path.dirname(os.path.abspath(args.combined_json))
    plot_compare(args.combined_json, out)
