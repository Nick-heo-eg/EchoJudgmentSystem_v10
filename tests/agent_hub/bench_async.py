#!/usr/bin/env python3
import asyncio, json, time, statistics, sys
try:
    import aiohttp
except ImportError:
    print("aiohttp가 필요합니다. 먼저 설치하세요: pip install aiohttp", file=sys.stderr)
    sys.exit(1)

BASE = "http://localhost:8014"
CONCURRENCY = int(sys.argv[1]) if len(sys.argv) > 1 else 20
TOTAL = int(sys.argv[2]) if len(sys.argv) > 2 else 200

payload = {
    "text": "빠른 테스트입니다. 요약과 키워드만.",
    "context": {"tasks": ["summarize","keywords"], "lang":"ko", "trace_id":"bench-echo"}
}

async def worker(session, latencies):
    start = time.perf_counter()
    async with session.post(f"{BASE}/echo", json=payload) as r:
        await r.text()
    latencies.append(time.perf_counter() - start)

async def run():
    latencies = []
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [asyncio.create_task(worker(session, latencies)) for _ in range(TOTAL)]
        start = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start

    p50 = statistics.median(latencies)
    p95 = sorted(latencies)[int(0.95*len(latencies))-1]
    print(json.dumps({
        "total_requests": TOTAL,
        "concurrency": CONCURRENCY,
        "elapsed_s": round(elapsed, 3),
        "rps": round(TOTAL/elapsed, 1),
        "latency_p50_s": round(p50, 4),
        "latency_p95_s": round(p95, 4)
    }, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(run())