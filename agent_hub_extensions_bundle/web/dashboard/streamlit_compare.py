
import os, glob, json
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Agent Hub — Signature Bench Compare", layout="wide")
st.title("Agent Hub — Signature Comparison Dashboard")

root = st.text_input("Artifacts root", "artifacts/bench")
runs = sorted(glob.glob(os.path.join(root, "*", "combined.json")))
if not runs:
    st.info("No combined signature runs found (expected artifacts/bench/*/combined.json)")
    st.stop()

path = st.selectbox("Select combined.json", runs, index=len(runs)-1)
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

st.subheader("Meta")
st.json(data.get("meta", {}))

steps = data["meta"]["steps"]
xs = [c for (c, _) in steps]
results = data["results"]
sigs = list(results.keys())

st.subheader("RPS vs Concurrency")
fig1 = plt.figure()
for s in sigs:
    ys = [row["rps"] for row in results[s]]
    plt.plot(xs, ys, marker="o", label=s)
plt.xlabel("Concurrency")
plt.ylabel("RPS")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
st.pyplot(fig1)

st.subheader("Latency (p50/p95) vs Concurrency")
fig2 = plt.figure()
for s in sigs:
    p50 = [row["p50_ms"] for row in results[s]]
    p95 = [row["p95_ms"] for row in results[s]]
    plt.plot(xs, p50, marker="o", label=f"{s} p50")
    plt.plot(xs, p95, marker="o", label=f"{s} p95")
plt.xlabel("Concurrency")
plt.ylabel("Latency (ms)")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
st.pyplot(fig2)

st.caption("Tip: Run `python tests/agent_hub/bench_signatures.py --signatures Aurora,Selene,Heo --steps 20x200,50x1000,100x2000` to generate more data.")
