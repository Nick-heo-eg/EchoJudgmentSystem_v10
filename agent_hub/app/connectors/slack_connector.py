import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_KEY = os.getenv("SLACK_BOT_TOKEN")
client = WebClient(token=SLACK_KEY)

def mcp_slack(payload: dict) -> dict:
    if not SLACK_KEY:
        return {"status":"error","error":"NO_SLACK_BOT_TOKEN"}
    try:
        resp = client.chat_postMessage(
            channel=payload.get("channel", "#general"),
            text=payload.get("text", "Hello from Echo Agent Hub"),
        )
        return {"status":"ok","ts":resp["ts"]}
    except SlackApiError as e:
        return {"status":"error","error":str(e)}
