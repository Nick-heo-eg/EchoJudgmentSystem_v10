#!/usr/bin/env python3
import sys, json, time
from typing import Any, Dict
try:
    import yaml, requests
except ImportError as e:
    print("필요 패키지 설치: pip install pyyaml requests", file=sys.stderr)
    sys.exit(1)

def has_any_keys(obj: Dict[str, Any], keys):
    return any(k in obj for k in keys)

def main(cfg_path: str):
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    base = cfg.get("base", "http://localhost:8014")
    scenarios = cfg.get("scenarios", [])

    results = []
    failed = 0

    for sc in scenarios:
        name = sc["name"]
        method = sc["method"].upper()
        url = base + sc["path"]
        json_body = sc.get("json")
        expect = sc.get("expect", {})
        status_expect = expect.get("status", 200)
        keys_any = expect.get("json_keys_any", [])

        t0 = time.time()
        try:
            resp = requests.request(method, url, json=json_body, timeout=15)
            elapsed = time.time() - t0
        except Exception as e:
            failed += 1
            results.append({"name": name, "ok": False, "error": str(e)})
            continue

        ok = (resp.status_code == status_expect)
        body = {}
        try:
            body = resp.json()
        except Exception:
            pass

        if ok and keys_any:
            ok = has_any_keys(body if isinstance(body, dict) else {}, keys_any)

        results.append({
            "name": name,
            "status": resp.status_code,
            "ok": ok,
            "elapsed_ms": int(elapsed*1000),
            "body_sample": body if isinstance(body, dict) else resp.text[:200]
        })
        if not ok:
            failed += 1

    print(json.dumps({"failed": failed, "results": results}, ensure_ascii=False, indent=2))
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python run_regression.py regression.yaml", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])