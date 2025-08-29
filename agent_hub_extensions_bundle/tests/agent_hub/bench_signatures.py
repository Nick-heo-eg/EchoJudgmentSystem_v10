
#!/usr/bin/env python3
import asyncio, time, argparse, json, os
from datetime import datetime
from typing import List, Tuple
import aiohttp

def parse_steps(s: str) -> List[tuple[int,int]]:
    steps = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        c, r = part.split("x", 1)
        steps.append((int(c), int(r)))
    return steps

async def bench_once(session, url, payload, concurrency, total):
    sem = asyncio.Semaphore(concurrency)
    latencies = []
    errors = 0
    t0 = time.perf_counter()
    async def one():
        nonlocal errors
        async with sem:
            t1 = time.perf_counter()
            try:
                async with session.post(url, json=payload) as resp:
                    _ = await resp.read()
                    if resp.status >= 400:
                        errors += 1
            except Exception:
                errors += 1
            latencies.append((time.perf_counter() - t1) * 1000.0)
    await asyncio.gather(*[asyncio.create_task(one()) for _ in range(total)])
    elapsed = time.perf_counter() - t0
    rps = total / elapsed if elapsed > 0 else 0.0
    latencies.sort()
    def pct(p):
        i = (len(latencies)-1) * p
        f = int(i)
        c = min(f+1, len(latencies)-1)
        if f==c: return latencies[f]
        return latencies[f]*(c-i) + latencies[c]*(i-f)
    return {
        "concurrency": concurrency,
        "total_requests": total,
        "elapsed_sec": elapsed,
        "rps": rps,
        "p50_ms": pct(0.50),
        "p95_ms": pct(0.95),
        "errors": errors,
    }

async def run_signature(base_url, endpoint, signature, steps, text, out_dir):
    url = base_url.rstrip("/") + "/" + endpoint.lstrip("/")
    payload = {"text": text, "context": {"signature": signature}}
    results = []
    async with aiohttp.ClientSession() as session:
        for (c, r) in steps:
            res = await bench_once(session, url, payload, c, r)
            results.append(res)
    meta = {"base_url": base_url, "endpoint": endpoint, "signature": signature, "steps": steps}
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"signature_{signature}.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "results": results}, f, ensure_ascii=False, indent=2)
    return {"signature": signature, "meta": meta, "results": results}

async def main():
    ap = argparse.ArgumentParser(description="Benchmark multiple Echo signatures")
    ap.add_argument("--base-url", default="http://localhost:8014")
    ap.add_argument("--endpoint", default="/echo")
    ap.add_argument("--signatures", default="Aurora,Selene,Heo")
    ap.add_argument("--steps", default="20x200,50x1000")
    ap.add_argument("--text", default="벤치마크용 텍스트입니다.")
    ap.add_argument("--tag", default="sigbench")
    ap.add_argument("--out-root", default="artifacts/bench")
    args = ap.parse_args()

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_id = f"{args.tag}-{ts}"
    out_dir = os.path.join(args.out_root, run_id)
    os.makedirs(out_dir, exist_ok=True)

    steps = parse_steps(args.steps)
    sigs = [s.strip() for s in args.signatures.split(",") if s.strip()]

    combined = {"meta": {"run_id": run_id, "signatures": sigs, "steps": steps}, "results": {}}
    for s in sigs:
        one = await run_signature(args.base_url, args.endpoint, s, steps, args.text, out_dir)
        combined["results"][s] = one["results"]

    with open(os.path.join(out_dir, "combined.json"), "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print(json.dumps({"out_dir": out_dir}, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
