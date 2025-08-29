import os, requests

NOTION_KEY = os.getenv("NOTION_API_KEY")
BASE_URL = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {NOTION_KEY}",
    "Notion-Version": "2022-06-28",
}

def query_database(db_id: str, query: dict) -> dict:
    url = f"{BASE_URL}/databases/{db_id}/query"
    r = requests.post(url, headers=HEADERS, json=query)
    return r.json()

def mcp_notion(payload: dict) -> dict:
    if not NOTION_KEY:
        return {"status":"error","error":"NO_NOTION_API_KEY"}
    return {"status":"ok","data":query_database(payload.get("db_id"), payload.get("query", {}))}
