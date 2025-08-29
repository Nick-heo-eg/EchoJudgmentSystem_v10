import json
from datetime import datetime

LOG_PATH = "npi_log.jsonl"


def write_log(prompt, npi_score, strategy, response, claude_result):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "npi_score": npi_score,
        "strategy": strategy,
        "response": response,
        "claude_summary": claude_result,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
