import os, time, random, requests

TAVILY_KEY = os.getenv("TAVILY_API_KEY")
BASE_URL = "https://api.tavily.com/search"
MAX_RETRIES = int(os.getenv("WEBSEARCH_MAX_RETRIES", "3"))
BASE_DELAY  = float(os.getenv("WEBSEARCH_BASE_DELAY", "0.8"))
MAX_DELAY   = float(os.getenv("WEBSEARCH_MAX_DELAY", "6.0"))

def _compose_query(payload: dict) -> str:
    q = (payload.get("query") or payload.get("text") or "").strip()
    q = " ".join(q.split())
    f = payload.get("filters") or {}
    if f.get("site"): q += " site:" + f["site"]
    if f.get("time") in {"past_day","past_week","past_month"}: q += " " + f["time"]
    return q

def _tavily(query: str, max_results: int = 5):
    return requests.post(
        BASE_URL,
        json={"query": query, "max_results": max_results},
        headers={"Authorization": f"Bearer {TAVILY_KEY}"},
        timeout=15,
    )

def _sleep_with_jitter(attempt: int):
    delay = min(MAX_DELAY, BASE_DELAY * (2 ** attempt))
    time.sleep(random.uniform(0, delay))

def _retry_after_seconds(resp):
    ra = resp.headers.get("Retry-After")
    if not ra: return None
    try:
        return max(0.0, float(ra))
    except:
        return None

def mcp_websearch(payload: dict) -> dict:
    if not TAVILY_KEY:
        return {"status":"error","error":"NO_TAVILY_API_KEY"}
    query = _compose_query(payload)
    if not query:
        return {"status":"error","error":"MISSING_QUERY"}

    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            r = _tavily(query)
            if r.status_code == 200:
                data = r.json() or {}
                is_partial = not data or not data.get("results")
                return {"status":"ok" if not is_partial else "partial", "data": data}
            if r.status_code in (429, 500, 502, 503, 504):
                ra = _retry_after_seconds(r)
                if ra is not None:
                    time.sleep(min(ra, MAX_DELAY))
                else:
                    _sleep_with_jitter(attempt)
                continue
            return {"status":"error","error":f"HTTP_{r.status_code}","detail":(r.text or "")[:500]}
        except Exception as e:
            last_err = str(e)
            _sleep_with_jitter(attempt)
    return {"status":"error","error":"REQUEST_FAILED","detail":last_err}
