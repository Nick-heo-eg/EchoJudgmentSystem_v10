
#!/usr/bin/env python3
import os, sys, json, urllib.request

def main():
    if len(sys.argv) < 2:
        print("usage: slack_notify.py summary.json [title]", file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else "Agent Hub Bench Summary"
    with open(path, "r", encoding="utf-8") as f:
        summary = json.load(f)
    ok = summary.get("ok", False)
    failures = summary.get("failures", [])
    notes = summary.get("notes", [])
    meta = summary.get("meta", {})

    lines = [f"*{title}*",
             f"Run: `{meta.get('timestamp','?')}` Endpoint: `{meta.get('endpoint','?')}`",
             "Status: " + ("✅ OK" if ok else "❌ REGRESSION DETECTED"),
             "Notes:"] + [f"- {n}" for n in notes]
    if failures:
        lines += ["Failures:"] + [f"• {f}" for f in failures]

    payload = {"text": "\n".join(lines)}
    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        print("SLACK_WEBHOOK_URL not set in env; printing message instead:\n" + payload["text"])
        return
    req = urllib.request.Request(webhook, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        print("Slack response:", resp.status)

if __name__ == "__main__":
    main()
