
import os
import glob
import json
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Agent Hub Bench Dashboard", layout="wide")
st.title("Agent Hub — Bench Dashboard")

root = st.text_input("Artifacts root", "artifacts/bench")
matches = sorted(glob.glob(os.path.join(root, "*", "results.json")))
if not matches:
    st.info("No runs found under artifacts/bench/*/results.json")
    st.stop()

run_path = st.selectbox("Select run", matches, index=len(matches)-1)
with open(run_path, "r", encoding="utf-8") as f:
    data = json.load(f)

st.subheader("Meta")
st.json(data["meta"])

rows = data["results"]
xs = [r["concurrency"] for r in rows]
rps = [r["rps"] for r in rows]
p50 = [r["p50_ms"] for r in rows]
p95 = [r["p95_ms"] for r in rows]

st.subheader("RPS vs Concurrency")
fig1 = plt.figure()
plt.plot(xs, rps, marker="o")
plt.xlabel("Concurrency")
plt.ylabel("RPS")
plt.grid(True, linestyle="--", alpha=0.5)
st.pyplot(fig1)

st.subheader("Latency vs Concurrency")
fig2 = plt.figure()
plt.plot(xs, p50, marker="o", label="p50 (ms)")
plt.plot(xs, p95, marker="o", label="p95 (ms)")
plt.xlabel("Concurrency")
plt.ylabel("Latency (ms)")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
st.pyplot(fig2)

st.caption("Tip: Run `python tests/agent_hub/bench_curve.py --profile --steps 20x200,50x1000,100x2000` to generate more data.")
