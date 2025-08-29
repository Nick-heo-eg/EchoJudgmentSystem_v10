
#!/usr/bin/env python3
import asyncio, time, argparse, json, os, sys
from datetime import datetime
from typing import List, Tuple
import aiohttp
import tracemalloc
import cProfile, pstats, io

from .utils import ensure_dir, save_json, percentile

DEFAULT_STEPS = [(20, 200), (50, 1000)]  # (concurrency, total_requests)

def parse_steps(s: str) -> List[Tuple[int,int]]:
    steps = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        if "x" not in part:
            raise ValueError(f"Invalid step '{part}', use like '50x1000'")
        c, r = part.split("x", 1)
        steps.append((int(c), int(r)))
    return steps

async def bench_step(session: aiohttp.ClientSession, url: str, payload: dict, concurrency: int, total: int):
    sem = asyncio.Semaphore(concurrency)
    latencies = []
    errors = 0
    start = time.perf_counter()

    async def one():
        nonlocal errors
        async with sem:
            t0 = time.perf_counter()
            try:
                async with session.post(url, json=payload) as resp:
                    _ = await resp.read()
                    if resp.status >= 400:
                        errors += 1
            except Exception:
                errors += 1
            finally:
                lat = (time.perf_counter() - t0) * 1000.0  # ms
                latencies.append(lat)

    tasks = [asyncio.create_task(one()) for _ in range(total)]
    await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - start
    rps = total / elapsed if elapsed > 0 else 0.0
    p50 = percentile(latencies, 0.50)
    p95 = percentile(latencies, 0.95)

    return {
        "concurrency": concurrency,
        "total_requests": total,
        "elapsed_sec": elapsed,
        "rps": rps,
        "p50_ms": p50,
        "p95_ms": p95,
        "errors": errors,
    }

async def main():
    ap = argparse.ArgumentParser(description="Agent Hub bench curve")
    ap.add_argument("--base-url", default="http://localhost:8014", help="Base URL of Agent Hub")
    ap.add_argument("--endpoint", default="/echo", help="Endpoint path to test (POST)")
    ap.add_argument("--steps", default="", help="Comma-separated steps like '20x200,50x1000'")
    ap.add_argument("--text", default="성능 측정 테스트입니다. 시스템 상태를 점검합니다.", help="Text payload")
    ap.add_argument("--tag", default="", help="Run tag (e.g., PR-123 or nightly)")
    ap.add_argument("--artifacts-dir", default="artifacts/bench", help="Artifacts output root")
    ap.add_argument("--profile", action="store_true", help="Enable cProfile + tracemalloc snapshot")
    args = ap.parse_args()

    url = args.base_url.rstrip("/") + "/" + args.endpoint.lstrip("/")
    payload = {"text": args.text, "context": {}}

    steps = parse_steps(args.steps) if args.steps else DEFAULT_STEPS

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_id = (args.tag + "-" if args.tag else "") + ts
    out_dir = os.path.join(args.artifacts_dir, run_id)
    ensure_dir(out_dir)

    prof = None
    if args.profile:
        tracemalloc.start()
        prof = cProfile.Profile()
        prof.enable()

    results = []
    async with aiohttp.ClientSession() as session:
        for (c, r) in steps:
            res = await bench_step(session, url, payload, c, r)
            print(json.dumps(res, ensure_ascii=False))
            results.append(res)

    meta = {
        "base_url": args.base_url,
        "endpoint": args.endpoint,
        "tag": args.tag,
        "run_id": run_id,
        "timestamp": ts,
        "steps": steps,
    }
    save_json({"meta": meta, "results": results}, os.path.join(out_dir, "results.json"))

    # also write CSV
    csv_path = os.path.join(out_dir, "results.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("concurrency,total_requests,elapsed_sec,rps,p50_ms,p95_ms,errors\n")
        for r in results:
            f.write(f"{r['concurrency']},{r['total_requests']},{r['elapsed_sec']:.6f},{r['rps']:.3f},{r['p50_ms']:.3f},{r['p95_ms']:.3f},{r['errors']}\n")

    if args.profile and prof:
        prof.disable()
        s = io.StringIO()
        ps = pstats.Stats(prof, stream=s).sort_stats("cumulative")
        ps.print_stats(40)
        with open(os.path.join(out_dir, "cpu_profile.txt"), "w", encoding="utf-8") as f:
            f.write(s.getvalue())

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        with open(os.path.join(out_dir, "mem_profile.txt"), "w", encoding="utf-8") as f:
            f.write(f"current_bytes={current}\npeak_bytes={peak}\n")

    print(f"[bench] results saved to: {out_dir}")

if __name__ == "__main__":
    asyncio.run(main())
